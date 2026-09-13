from __future__ import annotations

import tempfile
from pathlib import Path

from fastapi import FastAPI, File, HTTPException, UploadFile
from fastapi.middleware.cors import CORSMiddleware

from src.config import UPLOAD_CONFIG
from src.document_extractor import extract_document
from src.jd_parser import parse_job_description
from src.matcher import HybridMatcher
from src.normalizer import normalize_document
from src.scorer import score_and_rank_candidates


# Backwards-compatible names used by tests and API metadata.
ALLOWED_EXTENSIONS = UPLOAD_CONFIG.allowed_extensions
MAX_RESUMES = UPLOAD_CONFIG.max_resumes
MAX_FILE_SIZE = UPLOAD_CONFIG.max_file_size_bytes


app = FastAPI(
    title="EvidenceRank API",
    description="Local, private, evidence-based resume ranking engine",
    version="1.0.0",
)


# Allow the local React frontend to communicate with FastAPI.
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://127.0.0.1:5173",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


def validate_filename(filename: str | None) -> str:
    """Validate a filename and return a safe version of it."""

    if not filename:
        raise HTTPException(
            status_code=400,
            detail="An uploaded file has no filename.",
        )

    # Normalize Windows and POSIX separators on every operating system.
    safe_name = Path(filename.replace("\\", "/")).name.strip()

    if not safe_name or safe_name in {".", ".."}:
        raise HTTPException(
            status_code=400,
            detail="An uploaded file has an invalid filename.",
        )

    if len(safe_name) > UPLOAD_CONFIG.max_filename_length:
        raise HTTPException(
            status_code=400,
            detail=(
                "An uploaded filename is too long. "
                f"The maximum is {UPLOAD_CONFIG.max_filename_length} characters."
            ),
        )

    extension = Path(safe_name).suffix.lower()

    if extension not in ALLOWED_EXTENSIONS:
        raise HTTPException(
            status_code=400,
            detail=(
                f"Unsupported file type: {extension or 'unknown'}. "
                "Allowed formats are PDF, DOCX, TXT, and XML."
            ),
        )

    return safe_name


async def save_upload(upload: UploadFile, destination: Path) -> None:
    """Save an uploaded file while enforcing the size limit."""

    total_size = 0

    try:
        with destination.open("wb") as output_file:
            while True:
                chunk = await upload.read(
                    UPLOAD_CONFIG.read_chunk_size_bytes
                )

                if not chunk:
                    break

                total_size += len(chunk)

                if total_size > MAX_FILE_SIZE:
                    raise HTTPException(
                        status_code=413,
                        detail=(
                            f"{upload.filename} is larger than "
                            f"{UPLOAD_CONFIG.max_file_size_mb} MB."
                        ),
                    )

                output_file.write(chunk)

        if total_size == 0:
            raise HTTPException(
                status_code=400,
                detail=f"{upload.filename or 'Uploaded file'} is empty.",
            )
    finally:
        await upload.close()


@app.get("/")
def root() -> dict:
    return {
        "product": "EvidenceRank",
        "status": "ready",
        "engine": "hybrid evidence ranking",
        "supported_formats": sorted(ALLOWED_EXTENSIONS),
    }


@app.get("/health")
def health_check() -> dict:
    return {
        "status": "healthy",
        "product": "EvidenceRank",
    }


@app.post("/rank")
async def rank_resumes(
    job_description: UploadFile = File(...),
    resumes: list[UploadFile] = File(...),
) -> dict:
    """
    Process one job description and multiple resumes.

    Returns:
    - Final candidate ranking
    - Requirement coverage
    - Strong and missing requirements
    - Requirement-level evidence
    - Extraction and normalization warnings
    """

    if not resumes:
        raise HTTPException(
            status_code=400,
            detail="Upload at least one resume.",
        )

    if len(resumes) > MAX_RESUMES:
        raise HTTPException(
            status_code=400,
            detail=f"A maximum of {MAX_RESUMES} resumes can be processed.",
        )

    job_filename = validate_filename(job_description.filename)

    for resume in resumes:
        validate_filename(resume.filename)

    with tempfile.TemporaryDirectory(
        prefix="evidencerank_"
    ) as temporary_directory:
        temporary_path = Path(temporary_directory)

        # ---------------------------------------------------------
        # 1. Process the job description
        # ---------------------------------------------------------

        job_path = temporary_path / f"job_{job_filename}"
        await save_upload(job_description, job_path)

        try:
            extracted_job = extract_document(job_path)
        except Exception as exc:
            raise HTTPException(
                status_code=422,
                detail=f"Could not read the job description: {exc}",
            ) from exc

        if not extracted_job.extraction_success:
            raise HTTPException(
                status_code=422,
                detail={
                    "message": "Job-description extraction failed.",
                    "warnings": extracted_job.warnings,
                },
            )

        try:
            parsed_job = parse_job_description(extracted_job)
        except Exception as exc:
            raise HTTPException(
                status_code=422,
                detail=f"Could not parse the job description: {exc}",
            ) from exc

        if not parsed_job.parsing_success:
            raise HTTPException(
                status_code=422,
                detail={
                    "message": "Job-description parsing failed.",
                    "warnings": parsed_job.warnings,
                },
            )

        if not parsed_job.requirements:
            raise HTTPException(
                status_code=422,
                detail={
                    "message": "No usable requirements were found.",
                    "warnings": parsed_job.warnings,
                },
            )

        # ---------------------------------------------------------
        # 2. Process every resume
        # ---------------------------------------------------------

        candidates = {}
        candidate_metadata = {}
        rejected_files = []

        for index, resume_upload in enumerate(resumes, start=1):
            original_filename = validate_filename(resume_upload.filename)
            candidate_id = f"candidate_{index:03d}"

            resume_path = (
                temporary_path / f"{candidate_id}_{original_filename}"
            )

            try:
                await save_upload(resume_upload, resume_path)

                extracted_resume = extract_document(resume_path)

                if not extracted_resume.extraction_success:
                    rejected_files.append(
                        {
                            "candidate_id": candidate_id,
                            "filename": original_filename,
                            "stage": "extraction",
                            "reason": "Resume extraction failed.",
                            "warnings": extracted_resume.warnings,
                        }
                    )
                    continue

                normalized_resume = normalize_document(extracted_resume)

                if not normalized_resume.normalization_success:
                    rejected_files.append(
                        {
                            "candidate_id": candidate_id,
                            "filename": original_filename,
                            "stage": "normalization",
                            "reason": "Resume normalization failed.",
                            "warnings": normalized_resume.warnings,
                        }
                    )
                    continue

                if not normalized_resume.spans:
                    rejected_files.append(
                        {
                            "candidate_id": candidate_id,
                            "filename": original_filename,
                            "stage": "normalization",
                            "reason": "No usable evidence spans were found.",
                            "warnings": normalized_resume.warnings,
                        }
                    )
                    continue

                candidates[candidate_id] = normalized_resume

                candidate_metadata[candidate_id] = {
                    "candidate_id": candidate_id,
                    "filename": original_filename,
                    "file_type": Path(original_filename).suffix.lower(),
                    "evidence_span_count": normalized_resume.total_spans,
                    "section_counts": normalized_resume.section_counts,
                    "extraction_warnings": extracted_resume.warnings,
                    "normalization_warnings": normalized_resume.warnings,
                }

            except HTTPException:
                raise

            except Exception as exc:
                rejected_files.append(
                    {
                        "candidate_id": candidate_id,
                        "filename": original_filename,
                        "stage": "processing",
                        "reason": str(exc),
                        "warnings": [],
                    }
                )

        if not candidates:
            raise HTTPException(
                status_code=422,
                detail={
                    "message": "None of the resumes could be processed.",
                    "rejected_files": rejected_files,
                },
            )

        # ---------------------------------------------------------
        # 3. Run hybrid matching
        # ---------------------------------------------------------

        try:
            matcher = HybridMatcher(candidates)
            matches = matcher.match_all(parsed_job)
        except Exception as exc:
            raise HTTPException(
                status_code=500,
                detail=f"Candidate matching failed: {exc}",
            ) from exc

        # ---------------------------------------------------------
        # 4. Score and rank candidates
        # ---------------------------------------------------------

        try:
            ranked_candidates = score_and_rank_candidates(
                candidates,
                parsed_job,
                matches,
            )
        except Exception as exc:
            raise HTTPException(
                status_code=500,
                detail=f"Candidate scoring failed: {exc}",
            ) from exc

        # ---------------------------------------------------------
        # 5. Build explainable results
        # ---------------------------------------------------------

        results = []

        for evaluation in ranked_candidates:
            evaluation_data = evaluation.model_dump(mode="json")
            candidate_id = evaluation_data["candidate_id"]

            requirement_matches = [
                match.model_dump(mode="json")
                for match in matches[candidate_id]
            ]

            status_counts = {
                "strong": sum(
                    match["status"] == "strong"
                    for match in requirement_matches
                ),
                "partial": sum(
                    match["status"] == "partial"
                    for match in requirement_matches
                ),
                "weak": sum(
                    match["status"] == "weak"
                    for match in requirement_matches
                ),
                "missing": sum(
                    match["status"] == "missing"
                    for match in requirement_matches
                ),
            }

            results.append(
                {
                    **evaluation_data,
                    **candidate_metadata[candidate_id],
                    "status_counts": status_counts,
                    "requirement_matches": requirement_matches,
                }
            )

        return {
            "status": "completed",
            "job_description": {
                "filename": job_filename,
                "requirement_count": len(parsed_job.requirements),
                "required_count": parsed_job.required_count,
                "preferred_count": parsed_job.preferred_count,
                "contextual_count": parsed_job.contextual_count,
                "warnings": parsed_job.warnings,
                "requirements": [
                    requirement.model_dump(mode="json")
                    for requirement in parsed_job.requirements
                ],
            },
            "summary": {
                "uploaded_resumes": len(resumes),
                "ranked_resumes": len(results),
                "rejected_resumes": len(rejected_files),
            },
            "rankings": results,
            "rejected_files": rejected_files,
        }

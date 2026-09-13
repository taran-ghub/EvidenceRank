from io import BytesIO

import pytest
from fastapi import HTTPException
from fastapi.testclient import TestClient

from src.api import MAX_RESUMES, app, validate_filename
from src.config import UploadConfig


client = TestClient(app)


def test_health_endpoint() -> None:
    response = client.get("/health")

    assert response.status_code == 200
    assert response.json()["status"] == "healthy"


def test_rank_rejects_unsupported_job_description() -> None:
    response = client.post(
        "/rank",
        files=[
            (
                "job_description",
                ("job.exe", BytesIO(b"not a document"), "application/octet-stream"),
            ),
            (
                "resumes",
                ("resume.txt", BytesIO(b"Python developer"), "text/plain"),
            ),
        ],
    )

    assert response.status_code == 400
    assert "Unsupported file type" in response.json()["detail"]


def test_rank_rejects_unsupported_resume() -> None:
    response = client.post(
        "/rank",
        files=[
            (
                "job_description",
                ("job.txt", BytesIO(b"Looking for a Python developer"), "text/plain"),
            ),
            (
                "resumes",
                ("resume.exe", BytesIO(b"not a resume"), "application/octet-stream"),
            ),
        ],
    )

    assert response.status_code == 400
    assert "Unsupported file type" in response.json()["detail"]


def test_rank_rejects_more_than_maximum_resumes() -> None:
    files = [
        (
            "job_description",
            ("job.txt", BytesIO(b"Looking for Python"), "text/plain"),
        )
    ]

    files.extend(
        (
            "resumes",
            (
                f"resume_{index}.txt",
                BytesIO(b"Python developer"),
                "text/plain",
            ),
        )
        for index in range(MAX_RESUMES + 1)
    )

    response = client.post("/rank", files=files)

    assert response.status_code == 400
    assert f"maximum of {MAX_RESUMES}" in response.json()["detail"]


def test_rank_rejects_empty_job_description() -> None:
    response = client.post(
        "/rank",
        files=[
            (
                "job_description",
                ("job.txt", BytesIO(b""), "text/plain"),
            ),
            (
                "resumes",
                ("resume.txt", BytesIO(b"Python developer"), "text/plain"),
            ),
        ],
    )

    assert response.status_code == 400
    assert response.json()["detail"] == "job.txt is empty."


@pytest.mark.parametrize(
    ("uploaded_name", "expected_name"),
    [
        (r"C:\fake\folder\resume.pdf", "resume.pdf"),
        ("/fake/folder/candidate.docx", "candidate.docx"),
    ],
)
def test_validate_filename_removes_uploaded_paths(
    uploaded_name: str,
    expected_name: str,
) -> None:
    assert validate_filename(uploaded_name) == expected_name


def test_validate_filename_rejects_excessive_length() -> None:
    oversized_name = f"{'a' * 181}.pdf"

    with pytest.raises(HTTPException) as error:
        validate_filename(oversized_name)

    assert error.value.status_code == 400
    assert "filename is too long" in str(error.value.detail)


@pytest.mark.parametrize(
    "invalid_config",
    [
        {"max_resumes": 0},
        {"max_file_size_bytes": 0},
        {"read_chunk_size_bytes": 0},
        {"max_filename_length": 0},
        {"allowed_extensions": frozenset()},
        {"allowed_extensions": frozenset({"PDF"})},
    ],
)
def test_upload_config_rejects_invalid_values(
    invalid_config: dict[str, object],
) -> None:
    with pytest.raises(ValueError):
        UploadConfig(**invalid_config)
class DeterministicEmbeddingModel:
    def encode(self, texts, **kwargs):
        import numpy as np

        vectors = []

        for text in texts:
            normalized = text.casefold()
            vector = np.asarray(
                [
                    float("python" in normalized),
                    float("rest api" in normalized),
                    float("docker" in normalized),
                    1.0,
                ],
                dtype=float,
            )
            vector /= np.linalg.norm(vector)
            vectors.append(vector)

        return np.asarray(vectors)


def test_rank_endpoint_processes_and_orders_candidates(
    monkeypatch,
) -> None:
    import src.matcher as matcher_module

    monkeypatch.setattr(
        matcher_module,
        "get_embedding_model",
        lambda: DeterministicEmbeddingModel(),
    )

    job_description = b"""
MUST-HAVE SKILLS
Python
REST APIs

GOOD-TO-HAVE SKILLS
Docker
"""

    matching_resume = b"""
AARAV SHARMA
Backend Developer

SKILLS
Python, Git

PROJECTS
Built REST APIs and backend services using Python.
"""

    unrelated_resume = b"""
RIYA KAPOOR
Visual Designer

SKILLS
Figma, Adobe Illustrator

PROJECTS
Designed marketing graphics and mobile interface mockups.
"""

    response = client.post(
        "/rank",
        files=[
            (
                "job_description",
                ("job.txt", BytesIO(job_description), "text/plain"),
            ),
            (
                "resumes",
                ("matching.txt", BytesIO(matching_resume), "text/plain"),
            ),
            (
                "resumes",
                ("unrelated.txt", BytesIO(unrelated_resume), "text/plain"),
            ),
        ],
    )

    assert response.status_code == 200

    payload = response.json()

    assert payload["status"] == "completed"
    assert payload["summary"] == {
        "uploaded_resumes": 2,
        "ranked_resumes": 2,
        "rejected_resumes": 0,
    }
    assert payload["job_description"]["requirement_count"] >= 2
    assert len(payload["rankings"]) == 2

    first_candidate = payload["rankings"][0]
    second_candidate = payload["rankings"][1]

    assert first_candidate["filename"] == "matching.txt"
    assert first_candidate["rank"] == 1
    assert second_candidate["filename"] == "unrelated.txt"
    assert second_candidate["rank"] == 2
    assert first_candidate["final_score"] > second_candidate["final_score"]
    assert first_candidate["requirement_matches"]

def test_rank_does_not_expose_internal_extraction_errors(
    monkeypatch,
) -> None:
    import src.api as api_module

    private_error = "PRIVATE_INTERNAL_PATH_OR_LIBRARY_ERROR"

    def broken_extractor(_path):
        raise RuntimeError(private_error)

    monkeypatch.setattr(
        api_module,
        "extract_document",
        broken_extractor,
    )

    response = client.post(
        "/rank",
        files=[
            (
                "job_description",
                (
                    "job.txt",
                    BytesIO(b"Looking for a Python developer"),
                    "text/plain",
                ),
            ),
            (
                "resumes",
                (
                    "resume.txt",
                    BytesIO(b"Python developer"),
                    "text/plain",
                ),
            ),
        ],
    )

    assert response.status_code == 422
    assert response.json()["detail"] == (
        "Could not read the job description."
    )
    assert private_error not in response.text
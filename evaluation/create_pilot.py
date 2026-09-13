from __future__ import annotations

import csv
import json
import random
import shutil
from pathlib import Path

from src.skill_catalog import find_catalog_skills


NORMALIZED_DIRECTORY = Path("data/cache/all_normalized")
RESUME_DIRECTORY = Path("data/training_resumes")
OUTPUT_DIRECTORY = Path("data/cache/evaluation/full_stack_pilot")
SAMPLE_DIRECTORY = OUTPUT_DIRECTORY / "resumes"
SAMPLE_SIZE = 30
RANDOM_SEED = 20260913

TARGET_SKILLS = {
    "javascript",
    "typescript",
    "react",
    "nodejs",
    "express",
    "rest_api",
    "git",
    "html",
    "css",
    "sql",
    "mysql",
    "postgresql",
    "mongodb",
    "docker",
    "aws",
}

JOB_DESCRIPTION = """FULL-STACK DEVELOPER — EVALUATION PILOT

MUST-HAVE
- JavaScript and a modern frontend framework such as React
- Backend service development using Node.js and Express, or comparable experience
- REST API and JSON experience
- Working knowledge of a SQL or NoSQL database
- Git-based version control

GOOD-TO-HAVE
- TypeScript
- Automated testing
- Docker or containerization
- AWS or another cloud platform
- Evidence of deployed projects, internships, or production work

The role values demonstrated project or work evidence more than a skill-list mention.
"""

RUBRIC = """EVIDENCERANK HUMAN-LABELLING RUBRIC

Review the job description before opening the resumes. Judge only evidence written
in the resume. Do not infer skills from a candidate's name, college, photo, gender,
or other protected/personal characteristics.

human_relevance:
3 = Strong fit: covers most must-haves with clear project/work evidence.
2 = Reasonable fit: covers several must-haves but has meaningful gaps or shallow evidence.
1 = Weak fit: limited relevant evidence; unlikely shortlist.
0 = Unsupported: little or no evidence for this role.

confidence:
high   = the decision is clear from the resume.
medium = some wording or evidence is ambiguous.
low    = the resume is difficult to judge.

Fill human_relevance, confidence, required_evidence_notes, and decision_notes in labels.csv.
Do not change candidate_id, source_filename, anonymous_filename, or sampling_stratum.
"""


def document_skill_ids(spans: list[dict]) -> set[str]:
    skills: set[str] = set()
    for span in spans:
        for match in find_catalog_skills(span.get("original_text", "")):
            skills.add(match["skill_id"])
    return skills


def find_resume(filename: str) -> Path | None:
    exact_matches = [
        path
        for path in RESUME_DIRECTORY.rglob("*")
        if path.is_file() and path.name.casefold() == filename.casefold()
    ]
    return sorted(exact_matches)[0] if exact_matches else None


def main() -> None:
    cache_files = sorted(NORMALIZED_DIRECTORY.glob("*.json"))
    if not cache_files:
        raise SystemExit(f"No normalized caches found in {NORMALIZED_DIRECTORY}")

    records: list[dict] = []
    for cache_path in cache_files:
        payload = json.loads(cache_path.read_text(encoding="utf-8"))
        filename = payload.get("filename")
        if not filename:
            continue

        matched_skills = document_skill_ids(payload.get("spans", []))
        relevant_count = len(matched_skills & TARGET_SKILLS)
        if relevant_count >= 5:
            stratum = "higher keyword coverage"
        elif relevant_count >= 2:
            stratum = "medium keyword coverage"
        else:
            stratum = "lower keyword coverage"

        records.append(
            {
                "filename": filename,
                "sampling_stratum": stratum,
                "relevant_skill_count": relevant_count,
            }
        )

    rng = random.Random(RANDOM_SEED)
    selected: list[dict] = []
    for stratum in (
        "higher keyword coverage",
        "medium keyword coverage",
        "lower keyword coverage",
    ):
        group = [r for r in records if r["sampling_stratum"] == stratum]
        rng.shuffle(group)
        selected.extend(group[:10])

    if len(selected) < SAMPLE_SIZE:
        selected_names = {r["filename"] for r in selected}
        remainder = [r for r in records if r["filename"] not in selected_names]
        rng.shuffle(remainder)
        selected.extend(remainder[: SAMPLE_SIZE - len(selected)])

    selected = selected[:SAMPLE_SIZE]
    OUTPUT_DIRECTORY.mkdir(parents=True, exist_ok=True)
    SAMPLE_DIRECTORY.mkdir(parents=True, exist_ok=True)
    (OUTPUT_DIRECTORY / "job_description.txt").write_text(
        JOB_DESCRIPTION,
        encoding="utf-8",
    )
    (OUTPUT_DIRECTORY / "README.txt").write_text(RUBRIC, encoding="utf-8")

    label_rows: list[dict] = []
    missing_files: list[str] = []
    for index, record in enumerate(selected, start=1):
        source = find_resume(record["filename"])
        if source is None:
            missing_files.append(record["filename"])
            continue

        candidate_id = f"FS-{index:03d}"
        anonymous_filename = f"{candidate_id}{source.suffix.lower()}"
        shutil.copy2(source, SAMPLE_DIRECTORY / anonymous_filename)
        label_rows.append(
            {
                "candidate_id": candidate_id,
                "source_filename": source.name,
                "anonymous_filename": anonymous_filename,
                "sampling_stratum": record["sampling_stratum"],
                "human_relevance": "",
                "confidence": "",
                "required_evidence_notes": "",
                "decision_notes": "",
            }
        )

    labels_path = OUTPUT_DIRECTORY / "labels.csv"
    with labels_path.open("w", newline="", encoding="utf-8-sig") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(label_rows[0].keys()))
        writer.writeheader()
        writer.writerows(label_rows)

    stratum_counts: dict[str, int] = {}
    for row in label_rows:
        stratum = row["sampling_stratum"]
        stratum_counts[stratum] = stratum_counts.get(stratum, 0) + 1

    print("EVALUATION PILOT CREATED")
    print("------------------------")
    print(f"Selected resumes: {len(label_rows)}")
    print(f"Sampling mix: {stratum_counts}")
    print(f"Job description: {OUTPUT_DIRECTORY / 'job_description.txt'}")
    print(f"Labelling rubric: {OUTPUT_DIRECTORY / 'README.txt'}")
    print(f"Labels: {labels_path}")
    print(f"Anonymous resumes: {SAMPLE_DIRECTORY}")
    if missing_files:
        print(f"Missing original files: {len(missing_files)}")


if __name__ == "__main__":
    main()

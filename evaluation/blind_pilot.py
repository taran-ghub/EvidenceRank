from __future__ import annotations

import csv
import random
import shutil
from pathlib import Path


PILOT_DIRECTORY = Path("data/cache/evaluation/full_stack_pilot")
SOURCE_LABELS = PILOT_DIRECTORY / "labels.csv"
SOURCE_RESUMES = PILOT_DIRECTORY / "resumes"
BLINDED_RESUMES = PILOT_DIRECTORY / "blinded_resumes"
BLINDED_LABELS = PILOT_DIRECTORY / "labels_blinded.csv"
PRIVATE_MANIFEST = PILOT_DIRECTORY / "sampling_manifest.csv"
RANDOM_SEED = 917_431


def main() -> None:
    if not SOURCE_LABELS.exists():
        raise SystemExit(f"Missing pilot labels: {SOURCE_LABELS}")

    with SOURCE_LABELS.open(encoding="utf-8-sig", newline="") as handle:
        source_rows = list(csv.DictReader(handle))

    if not source_rows:
        raise SystemExit("The pilot labels file contains no candidates.")

    rows = list(source_rows)
    random.Random(RANDOM_SEED).shuffle(rows)
    BLINDED_RESUMES.mkdir(parents=True, exist_ok=True)

    label_rows: list[dict[str, str]] = []
    manifest_rows: list[dict[str, str]] = []

    for index, row in enumerate(rows, start=1):
        source_resume = SOURCE_RESUMES / row["anonymous_filename"]
        if not source_resume.exists():
            raise SystemExit(f"Missing sampled resume: {source_resume}")

        blinded_id = f"EV-{index:03d}"
        blinded_filename = f"{blinded_id}{source_resume.suffix.lower()}"
        shutil.copy2(source_resume, BLINDED_RESUMES / blinded_filename)

        label_rows.append(
            {
                "candidate_id": blinded_id,
                "resume_file": blinded_filename,
                "human_relevance": "",
                "confidence": "",
                "required_evidence_notes": "",
                "decision_notes": "",
            }
        )
        manifest_rows.append(
            {
                "candidate_id": blinded_id,
                "resume_file": blinded_filename,
                "source_filename": row["source_filename"],
                "sampling_stratum": row["sampling_stratum"],
            }
        )

    with BLINDED_LABELS.open("w", encoding="utf-8-sig", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(label_rows[0]))
        writer.writeheader()
        writer.writerows(label_rows)

    with PRIVATE_MANIFEST.open("w", encoding="utf-8-sig", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(manifest_rows[0]))
        writer.writeheader()
        writer.writerows(manifest_rows)

    print("BLINDED PILOT READY")
    print("-------------------")
    print(f"Candidates: {len(label_rows)}")
    print(f"Open resumes from: {BLINDED_RESUMES}")
    print(f"Enter judgments in: {BLINDED_LABELS}")
    print(f"Keep closed while labelling: {PRIVATE_MANIFEST}")
    print("Note: filenames are blinded; resume contents are not redacted.")


if __name__ == "__main__":
    main()

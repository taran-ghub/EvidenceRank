from __future__ import annotations

import csv
from collections import Counter
from pathlib import Path


LABELS_PATH = Path(
    "data/cache/evaluation/full_stack_pilot/labels_blinded.csv"
)
VALID_LABELS = {"0", "1", "2", "3"}
VALID_CONFIDENCE = {"low", "medium", "high"}
EXPECTED_CANDIDATES = 30


def main() -> None:
    if not LABELS_PATH.exists():
        raise SystemExit(f"Labels file not found: {LABELS_PATH}")

    with LABELS_PATH.open(
        encoding="utf-8-sig",
        newline="",
    ) as handle:
        rows = list(csv.DictReader(handle))

    errors: list[str] = []
    candidate_ids: list[str] = []

    if len(rows) != EXPECTED_CANDIDATES:
        errors.append(
            f"Expected {EXPECTED_CANDIDATES} candidates, found {len(rows)}."
        )

    for row_number, row in enumerate(rows, start=2):
        candidate_id = row.get("candidate_id", "").strip()
        relevance = row.get("human_relevance", "").strip()
        confidence = row.get("confidence", "").strip().casefold()
        resume_file = row.get("resume_file", "").strip()

        candidate_ids.append(candidate_id)

        if not candidate_id:
            errors.append(f"Row {row_number}: missing candidate_id.")

        if not resume_file:
            errors.append(f"Row {row_number}: missing resume_file.")

        if relevance not in VALID_LABELS:
            errors.append(
                f"Row {row_number} ({candidate_id}): "
                f"human_relevance must be 0, 1, 2, or 3; "
                f"found {relevance!r}."
            )

        if confidence not in VALID_CONFIDENCE:
            errors.append(
                f"Row {row_number} ({candidate_id}): "
                f"confidence must be low, medium, or high; "
                f"found {confidence!r}."
            )

    duplicates = [
        candidate_id
        for candidate_id, count in Counter(candidate_ids).items()
        if candidate_id and count > 1
    ]

    if duplicates:
        errors.append(
            "Duplicate candidate IDs: " + ", ".join(duplicates)
        )

    if errors:
        print("LABEL VALIDATION FAILED")
        print("-----------------------")
        for error in errors:
            print(f"- {error}")
        raise SystemExit(1)

    label_counts = Counter(
        row["human_relevance"].strip()
        for row in rows
    )
    confidence_counts = Counter(
        row["confidence"].strip().casefold()
        for row in rows
    )

    print("LABEL VALIDATION PASSED")
    print("-----------------------")
    print(f"Candidates: {len(rows)}")
    print(
        "Relevance counts: "
        + ", ".join(
            f"{label}={label_counts[label]}"
            for label in sorted(VALID_LABELS)
        )
    )
    print(
        "Confidence counts: "
        + ", ".join(
            f"{level}={confidence_counts[level]}"
            for level in ("high", "medium", "low")
        )
    )


if __name__ == "__main__":
    main()
    
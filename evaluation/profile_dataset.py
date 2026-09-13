from __future__ import annotations

import json
from collections import Counter
from pathlib import Path

from src.skill_catalog import find_catalog_skills


CACHE_DIRECTORY = Path("data/cache/all_normalized")


def main() -> None:
    files = sorted(CACHE_DIRECTORY.glob("*.json"))

    if not files:
        raise SystemExit(
            f"No normalized JSON files found in {CACHE_DIRECTORY}"
        )

    section_counts: Counter[str] = Counter()
    skill_document_counts: Counter[str] = Counter()
    span_counts: list[int] = []

    for path in files:
        payload = json.loads(path.read_text(encoding="utf-8"))
        spans = payload.get("spans", [])
        span_counts.append(len(spans))

        document_skills: set[str] = set()

        for span in spans:
            section = span.get("section", "other")
            section_counts[section] += 1

            text = span.get("original_text", "")
            for match in find_catalog_skills(text):
                document_skills.add(match["skill_id"])

        skill_document_counts.update(document_skills)

    print("DATASET PROFILE")
    print("---------------")
    print(f"Documents: {len(files)}")
    print(f"Total evidence spans: {sum(span_counts)}")
    print(
        "Average spans per document: "
        f"{sum(span_counts) / len(span_counts):.1f}"
    )
    print(f"Minimum spans: {min(span_counts)}")
    print(f"Maximum spans: {max(span_counts)}")

    print("\nSECTION DISTRIBUTION")
    print("--------------------")
    for section, count in section_counts.most_common():
        print(f"{section:20} {count:5}")

    print("\nTOP SKILLS BY DOCUMENT COVERAGE")
    print("-------------------------------")
    for skill_id, count in skill_document_counts.most_common(30):
        percentage = count / len(files) * 100
        print(f"{skill_id:30} {count:3} documents  {percentage:5.1f}%")

    print("\nNo resume text or candidate filename was printed.")


if __name__ == "__main__":
    main()
import csv
from collections import Counter
from pathlib import Path

from src.normalizer import normalize_document
from src.schemas import ExtractedDocument


EXTRACTION_DIRECTORY = Path(
    "data/cache/all_extractions"
)

NORMALIZED_DIRECTORY = Path(
    "data/cache/all_normalized"
)

REPORT_PATH = Path(
    "data/cache/all_normalization_report.csv"
)


MEANINGFUL_SECTIONS = {
    "summary",
    "skills",
    "experience",
    "projects",
    "education",
    "certifications",
    "achievements",
    "leadership",
    "coursework",
}


def main() -> None:
    NORMALIZED_DIRECTORY.mkdir(parents=True, exist_ok=True)
    REPORT_PATH.parent.mkdir(parents=True, exist_ok=True)

    extraction_files = sorted(
        EXTRACTION_DIRECTORY.glob("*.json")
    )

    if not extraction_files:
        print("No cached extraction files were found.")
        print("Run the extraction inspection first.")
        return

    report_rows: list[dict] = []
    global_section_counts: Counter = Counter()

    print(
        f"Found {len(extraction_files)} extracted "
        "resume file(s).\n"
    )

    for number, extraction_path in enumerate(
        extraction_files,
        start=1,
    ):
        extracted_document = ExtractedDocument.model_validate_json(
            extraction_path.read_text(encoding="utf-8")
        )

        normalized_document = normalize_document(
            extracted_document
        )

        output_path = (
            NORMALIZED_DIRECTORY
            / extraction_path.name
        )

        output_path.write_text(
            normalized_document.model_dump_json(indent=2),
            encoding="utf-8",
        )

        detected_meaningful_sections = sorted(
            set(normalized_document.section_counts)
            .intersection(MEANINGFUL_SECTIONS)
        )

        header_spans = normalized_document.section_counts.get(
            "header",
            0,
        )

        header_share = (
            header_spans / normalized_document.total_spans
            if normalized_document.total_spans
            else 1.0
        )

        needs_review = (
            not normalized_document.normalization_success
            or not detected_meaningful_sections
            or normalized_document.total_spans < 3
            or header_share > 0.70
        )

        global_section_counts.update(
            normalized_document.section_counts
        )

        row = {
            "filename": normalized_document.filename,
            "success": normalized_document.normalization_success,
            "total_spans": normalized_document.total_spans,
            "detected_sections": ", ".join(
                detected_meaningful_sections
            ),
            "section_type_count": len(
                detected_meaningful_sections
            ),
            "header_spans": header_spans,
            "header_share": round(header_share, 3),
            "needs_review": needs_review,
            "warnings": " | ".join(
                normalized_document.warnings
            ),
        }

        report_rows.append(row)

        status = "REVIEW" if needs_review else "OK"

        print(
            f"[{number}/{len(extraction_files)}] "
            f"{status}: {normalized_document.filename} | "
            f"spans={normalized_document.total_spans} | "
            f"sections={detected_meaningful_sections}"
        )

    with REPORT_PATH.open(
        "w",
        newline="",
        encoding="utf-8-sig",
    ) as report_file:
        writer = csv.DictWriter(
            report_file,
            fieldnames=[
                "filename",
                "success",
                "total_spans",
                "detected_sections",
                "section_type_count",
                "header_spans",
                "header_share",
                "needs_review",
                "warnings",
            ],
        )

        writer.writeheader()
        writer.writerows(report_rows)

    review_documents = [
        row
        for row in report_rows
        if row["needs_review"]
    ]

    print("\nNORMALIZATION SUMMARY")
    print("---------------------")
    print(f"Documents processed: {len(report_rows)}")
    print(
        "Successful normalizations: "
        f"{sum(bool(row['success']) for row in report_rows)}"
    )
    print(
        f"Documents needing review: "
        f"{len(review_documents)}"
    )
    print(
        "Section totals: "
        f"{dict(global_section_counts)}"
    )
    print(f"Report saved to: {REPORT_PATH}")
    print(
        f"Normalized JSON saved to: "
        f"{NORMALIZED_DIRECTORY}"
    )

    if review_documents:
        print("\nFILES NEEDING REVIEW")
        print("--------------------")

        for row in review_documents:
            print(
                f"{row['filename']} | "
                f"spans={row['total_spans']} | "
                f"sections={row['detected_sections']} | "
                f"header_share={row['header_share']}"
            )


if __name__ == "__main__":
    main()
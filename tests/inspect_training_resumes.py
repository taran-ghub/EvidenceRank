import csv
import hashlib
import re
from collections import Counter
from pathlib import Path

from src.document_extractor import (
    SUPPORTED_EXTENSIONS,
    extract_document,
)


INPUT_DIRECTORY = Path("data/training_resumes")
CACHE_DIRECTORY = Path("data/cache/all_extractions")
REPORT_PATH = Path("data/cache/all_extraction_report.csv")


def create_cache_name(
    file_path: Path,
) -> str:
    relative_path = file_path.relative_to(
        INPUT_DIRECTORY
    )

    safe_name = re.sub(
        r"[^a-zA-Z0-9_-]+",
        "_",
        relative_path.stem,
    ).strip("_")

    extension = file_path.suffix.casefold().lstrip(".")

    path_hash = hashlib.sha1(
        relative_path.as_posix().encode("utf-8")
    ).hexdigest()[:10]

    return (
        f"{safe_name}_{extension}_{path_hash}.json"
    )


def main() -> None:
    CACHE_DIRECTORY.mkdir(
        parents=True,
        exist_ok=True,
    )
    REPORT_PATH.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    resume_files = sorted(
        file_path
        for file_path in INPUT_DIRECTORY.rglob("*")
        if (
            file_path.is_file()
            and file_path.suffix.casefold()
            in SUPPORTED_EXTENSIONS
        )
    )

    if not resume_files:
        print("No supported resume files were found.")
        return

    report_rows: list[dict] = []
    format_counts: Counter = Counter()
    method_counts: Counter = Counter()

    print(f"Found {len(resume_files)} resume file(s).\n")

    for number, file_path in enumerate(
        resume_files,
        start=1,
    ):
        relative_path = file_path.relative_to(
            INPUT_DIRECTORY
        )

        print(
            f"[{number}/{len(resume_files)}] "
            f"Processing {relative_path}"
        )

        result = extract_document(file_path)

        cache_path = (
            CACHE_DIRECTORY
            / create_cache_name(file_path)
        )

        cache_path.write_text(
            result.model_dump_json(indent=2),
            encoding="utf-8",
        )

        format_name = (
            file_path.suffix.casefold()
            .lstrip(".")
        )

        format_counts[format_name] += 1

        for page in result.pages:
            method_counts[
                page.extraction_method
            ] += 1

        ocr_pages = sum(
            page.extraction_method == "ocr"
            for page in result.pages
        )

        failed_pages = sum(
            not page.is_usable
            for page in result.pages
        )

        extraction_methods = sorted(
            {
                page.extraction_method
                for page in result.pages
            }
        )

        all_warnings = (
            result.warnings
            + [
                warning
                for page in result.pages
                for warning in page.warnings
            ]
        )

        needs_review = (
            not result.extraction_success
            or failed_pages > 0
            or len(result.full_text) < 150
        )

        report_rows.append(
            {
                "relative_path": str(relative_path),
                "filename": result.filename,
                "format": format_name,
                "success": result.extraction_success,
                "page_count": result.page_count,
                "usable_pages": result.usable_page_count,
                "ocr_pages": ocr_pages,
                "failed_pages": failed_pages,
                "text_characters": len(result.full_text),
                "methods": ", ".join(
                    extraction_methods
                ),
                "needs_review": needs_review,
                "warnings": " | ".join(
                    all_warnings
                ),
                "cache_file": cache_path.name,
            }
        )

        status = (
            "REVIEW"
            if needs_review
            else "OK"
        )

        print(
            f"    {status} | "
            f"success={result.extraction_success} | "
            f"characters={len(result.full_text)} | "
            f"methods={extraction_methods}"
        )

    with REPORT_PATH.open(
        "w",
        newline="",
        encoding="utf-8-sig",
    ) as report_file:
        writer = csv.DictWriter(
            report_file,
            fieldnames=[
                "relative_path",
                "filename",
                "format",
                "success",
                "page_count",
                "usable_pages",
                "ocr_pages",
                "failed_pages",
                "text_characters",
                "methods",
                "needs_review",
                "warnings",
                "cache_file",
            ],
        )

        writer.writeheader()
        writer.writerows(report_rows)

    review_rows = [
        row
        for row in report_rows
        if row["needs_review"]
    ]

    print("\nCOMPLETE EXTRACTION SUMMARY")
    print("---------------------------")
    print(f"Documents processed: {len(report_rows)}")
    print(
        "Successful documents: "
        f"{sum(bool(row['success']) for row in report_rows)}"
    )
    print(
        f"Documents needing review: "
        f"{len(review_rows)}"
    )
    print(
        f"Format counts: {dict(format_counts)}"
    )
    print(
        f"Extraction method counts: "
        f"{dict(method_counts)}"
    )
    print(f"Report saved to: {REPORT_PATH}")
    print(f"JSON cache saved to: {CACHE_DIRECTORY}")

    if review_rows:
        print("\nFILES NEEDING REVIEW")
        print("--------------------")

        for row in review_rows:
            print(
                f"{row['relative_path']} | "
                f"format={row['format']} | "
                f"success={row['success']} | "
                f"characters={row['text_characters']} | "
                f"failed_pages={row['failed_pages']}"
            )


if __name__ == "__main__":
    main()
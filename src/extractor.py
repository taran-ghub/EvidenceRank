from __future__ import annotations

import argparse
import re
from pathlib import Path

import pdfplumber
import pymupdf

from src.schemas import ExtractedDocument, PageExtraction


MIN_CHARACTERS = 60
MIN_WORDS = 8
MIN_ALPHABETIC_RATIO = 0.35

_OCR_ENGINE = None


def get_ocr_engine():
    """Create the OCR engine once and reuse it for every scanned page."""
    global _OCR_ENGINE

    if _OCR_ENGINE is None:
        from rapidocr import RapidOCR

        _OCR_ENGINE = RapidOCR()

    return _OCR_ENGINE


def clean_extracted_text(text: str | None) -> str:
    """Clean PDF extraction noise without changing the actual wording."""
    if not text:
        return ""

    text = text.replace("\x00", " ")
    text = text.replace("\u00a0", " ")
    text = text.replace("\r\n", "\n")
    text = text.replace("\r", "\n")

    cleaned_lines: list[str] = []

    for line in text.splitlines():
        line = re.sub(r"[ \t]+", " ", line).strip()

        if line:
            cleaned_lines.append(line)

    return "\n".join(cleaned_lines).strip()


def measure_text_quality(text: str) -> dict:
    """Measure whether extracted text is likely usable."""
    character_count = len(text)
    alphabetic_count = sum(character.isalpha() for character in text)
    visible_count = sum(not character.isspace() for character in text)

    alphabetic_ratio = (
        alphabetic_count / visible_count
        if visible_count > 0
        else 0.0
    )

    words = re.findall(r"\b[\w+#.-]{2,}\b", text)
    word_count = len(words)

    replacement_symbols = text.count("�")
    repeated_symbol_count = len(re.findall(r"([^\w\s])\1{3,}", text))

    warnings: list[str] = []

    if character_count < MIN_CHARACTERS:
        warnings.append("Very little text was extracted.")

    if word_count < MIN_WORDS:
        warnings.append("Too few readable words were detected.")

    if alphabetic_ratio < MIN_ALPHABETIC_RATIO:
        warnings.append("The extracted text contains too few alphabetic characters.")

    if replacement_symbols > 2:
        warnings.append("Several broken or replacement characters were detected.")

    if repeated_symbol_count > 2:
        warnings.append("The page contains suspicious repeated symbols.")

    is_usable = (
        character_count >= MIN_CHARACTERS
        and word_count >= MIN_WORDS
        and alphabetic_ratio >= MIN_ALPHABETIC_RATIO
        and replacement_symbols <= 5
    )

    quality_score = (
        alphabetic_count
        + (word_count * 3)
        - (replacement_symbols * 20)
        - (repeated_symbol_count * 10)
    )

    return {
        "character_count": character_count,
        "alphabetic_ratio": round(alphabetic_ratio, 4),
        "word_count": word_count,
        "quality_score": quality_score,
        "is_usable": is_usable,
        "warnings": warnings,
    }


def build_page_result(
    page_number: int,
    text: str,
    extraction_method: str,
) -> PageExtraction:
    cleaned_text = clean_extracted_text(text)
    quality = measure_text_quality(cleaned_text)

    return PageExtraction(
        page_number=page_number,
        text=cleaned_text,
        extraction_method=extraction_method,
        character_count=quality["character_count"],
        alphabetic_ratio=quality["alphabetic_ratio"],
        is_usable=quality["is_usable"],
        warnings=quality["warnings"],
    )


def extract_with_pymupdf(pdf_path: Path) -> list[PageExtraction]:
    pages: list[PageExtraction] = []

    with pymupdf.open(pdf_path) as document:
        if document.needs_pass:
            raise ValueError("The PDF is password protected.")

        for index, page in enumerate(document):
            try:
                text = page.get_text("text", sort=True)

                pages.append(
                    build_page_result(
                        page_number=index + 1,
                        text=text,
                        extraction_method="pymupdf",
                    )
                )

            except Exception as error:
                pages.append(
                    PageExtraction(
                        page_number=index + 1,
                        text="",
                        extraction_method="failed",
                        character_count=0,
                        alphabetic_ratio=0.0,
                        is_usable=False,
                        warnings=[
                            f"PyMuPDF failed on this page: {error}"
                        ],
                    )
                )

    return pages


def improve_bad_pages_with_pdfplumber(
    pdf_path: Path,
    pages: list[PageExtraction],
) -> list[PageExtraction]:
    """Retry weak pages with pdfplumber and keep whichever result is better."""
    bad_page_indexes = [
        index
        for index, page in enumerate(pages)
        if not page.is_usable
    ]

    if not bad_page_indexes:
        return pages

    try:
        with pdfplumber.open(pdf_path) as document:
            for index in bad_page_indexes:
                if index >= len(document.pages):
                    continue

                try:
                    fallback_text = document.pages[index].extract_text(
                        layout=True
                    )

                    fallback_page = build_page_result(
                        page_number=index + 1,
                        text=fallback_text or "",
                        extraction_method="pdfplumber",
                    )

                    original_quality = measure_text_quality(pages[index].text)
                    fallback_quality = measure_text_quality(fallback_page.text)

                    if (
                        fallback_quality["quality_score"]
                        > original_quality["quality_score"]
                    ):
                        pages[index] = fallback_page

                except Exception as error:
                    pages[index].warnings.append(
                        f"pdfplumber fallback failed: {error}"
                    )

    except Exception as error:
        for index in bad_page_indexes:
            pages[index].warnings.append(
                f"Could not open PDF with pdfplumber: {error}"
            )

    return pages

def improve_bad_pages_with_ocr(
    pdf_path: Path,
    pages: list[PageExtraction],
) -> list[PageExtraction]:
    """Use OCR only on pages that remain unusable after normal extraction."""
    bad_page_indexes = [
        index
        for index, page in enumerate(pages)
        if not page.is_usable
    ]

    if not bad_page_indexes:
        return pages

    try:
        ocr_engine = get_ocr_engine()

        with pymupdf.open(pdf_path) as document:
            for index in bad_page_indexes:
                if index >= len(document):
                    continue

                try:
                    pdf_page = document[index]

                    pixmap = pdf_page.get_pixmap(
                        matrix=pymupdf.Matrix(2, 2),
                        alpha=False,
                    )

                    result = ocr_engine(
                        pixmap.tobytes("png")
                    )

                    ocr_lines = (
                        list(result.txts)
                        if result.txts
                        else []
                    )

                    ocr_text = "\n".join(ocr_lines)

                    ocr_page = build_page_result(
                        page_number=index + 1,
                        text=ocr_text,
                        extraction_method="ocr",
                    )

                    original_quality = measure_text_quality(
                        pages[index].text
                    )
                    ocr_quality = measure_text_quality(
                        ocr_page.text
                    )

                    if (
                        ocr_quality["quality_score"]
                        > original_quality["quality_score"]
                    ):
                        ocr_page.warnings.insert(
                            0,
                            "OCR fallback was used for this page.",
                        )
                        pages[index] = ocr_page

                except Exception as error:
                    pages[index].warnings.append(
                        f"OCR fallback failed: {error}"
                    )

    except Exception as error:
        for index in bad_page_indexes:
            pages[index].warnings.append(
                f"Could not initialize OCR: {error}"
            )

    return pages

def extract_pdf(pdf_path: str | Path) -> ExtractedDocument:
    path = Path(pdf_path)

    if not path.exists():
        raise FileNotFoundError(f"PDF not found: {path}")

    if not path.is_file():
        raise ValueError(f"Expected a file but received: {path}")

    if path.suffix.lower() != ".pdf":
        raise ValueError(f"Only PDF files are supported: {path.name}")

    document_warnings: list[str] = []

    try:
        pages = extract_with_pymupdf(path)
        pages = improve_bad_pages_with_pdfplumber(path, pages)
        pages = improve_bad_pages_with_ocr(path, pages)

    except Exception as error:
        return ExtractedDocument(
            filename=path.name,
            page_count=0,
            pages=[],
            full_text="",
            usable_page_count=0,
            extraction_success=False,
            warnings=[f"Document extraction failed: {error}"],
        )

    for page in pages:
        if not page.is_usable:
            page.warnings.append(
                "This page may be scanned or image-based. OCR is recommended."
            )

    usable_pages = [page for page in pages if page.is_usable]

    if not pages:
        document_warnings.append("The PDF contains no pages.")

    if len(usable_pages) < len(pages):
        document_warnings.append(
            f"{len(pages) - len(usable_pages)} page(s) need OCR or manual review."
        )

    full_text = "\n\n".join(
        page.text
        for page in pages
        if page.text
    )

    return ExtractedDocument(
        filename=path.name,
        page_count=len(pages),
        pages=pages,
        full_text=full_text,
        usable_page_count=len(usable_pages),
        extraction_success=bool(usable_pages),
        warnings=document_warnings,
    )


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Extract and inspect text from a PDF."
    )
    parser.add_argument("pdf_path", help="Path to the PDF file")
    arguments = parser.parse_args()

    result = extract_pdf(arguments.pdf_path)
    print(result.model_dump_json(indent=2))


if __name__ == "__main__":
    main()
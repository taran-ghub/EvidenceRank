from __future__ import annotations

import re
from collections import Counter
from pathlib import Path

from src.schemas import (
    EvidenceSpan,
    ExtractedDocument,
    NormalizedDocument,
)


SECTION_ALIASES = {
    "summary": {
        "summary",
        "professional summary",
        "profile",
        "professional profile",
        "career objective",
        "objective",
        "about me",
    },
    "skills": {
        "skills",
        "technical skills",
        "core skills",
        "core competencies",
        "technologies",
        "tools and technologies",
        "technical expertise",
        "areas of expertise",
        "tech stack",
    },
    "experience": {
        "experience",
        "work experience",
        "professional experience",
        "employment history",
        "work history",
        "internship experience",
        "internships",
        "professional background",
    },
    "projects": {
        "projects",
        "project experience",
        "academic projects",
        "personal projects",
        "technical projects",
        "selected projects",
        "key projects",
    },
    "education": {
        "education",
        "academic background",
        "academic qualifications",
        "educational qualifications",
        "qualifications",
    },
    "certifications": {
        "certifications",
        "certificates",
        "licenses and certifications",
        "training and certifications",
    },
    "achievements": {
        "achievements",
        "awards",
        "honors",
        "honours",
        "awards and achievements",
        "accomplishments",
    },
    "leadership": {
        "leadership",
        "leadership experience",
        "positions of responsibility",
        "responsibilities",
        "volunteering",
        "extracurricular activities",
        "extra curricular activities",
    },
    "coursework": {
        "coursework",
        "relevant coursework",
        "academic coursework",
        "subjects",
    },
}


ACTION_VERBS = {
    "achieved",
    "automated",
    "built",
    "collaborated",
    "configured",
    "coordinated",
    "created",
    "deployed",
    "designed",
    "developed",
    "engineered",
    "implemented",
    "improved",
    "integrated",
    "launched",
    "led",
    "managed",
    "migrated",
    "optimized",
    "organised",
    "organized",
    "presented",
    "reduced",
    "resolved",
    "scaled",
    "tested",
    "trained",
    "worked",
}


BULLET_PATTERN = re.compile(
    r"^\s*(?:[•●▪◦‣►*-]|\d+[.)])\s*"
)


def normalize_heading_text(text: str) -> str:
    text = text.casefold()
    text = text.replace("&", " and ")
    text = re.sub(r"[^a-z0-9+#. ]+", " ", text)
    text = re.sub(r"\s+", " ", text)
    return text.strip(" .:-")


def normalize_search_text(text: str) -> str:
    text = text.casefold()

    replacements = {
        "node js": "node.js",
        "react js": "react.js",
        "next js": "next.js",
        "express js": "express.js",
        "mongo db": "mongodb",
        "postgre sql": "postgresql",
        "c plus plus": "c++",
        "c sharp": "c#",
    }

    for original, replacement in replacements.items():
        text = text.replace(original, replacement)

    text = re.sub(r"[^\w+#./%-]+", " ", text)
    text = re.sub(r"\s+", " ", text)

    return text.strip()


def identify_section_heading(line: str) -> str | None:
    normalized_line = normalize_heading_text(line)

    if not normalized_line or len(normalized_line) > 45:
        return None

    for section, aliases in SECTION_ALIASES.items():
        if normalized_line in aliases:
            return section

    return None


def split_inline_heading(line: str) -> tuple[str | None, str]:
    """
    Handle lines such as:
    'Skills: Python, React, Node.js'
    """
    for separator in (":", " - ", " | "):
        if separator not in line:
            continue

        possible_heading, remaining_text = line.split(separator, 1)
        section = identify_section_heading(possible_heading)

        if section:
            return section, remaining_text.strip()

    return None, line


def clean_resume_line(line: str) -> str:
    line = line.replace("\u00a0", " ")
    line = BULLET_PATTERN.sub("", line)
    line = re.sub(r"\s+", " ", line)

    return line.strip()


def should_ignore_line(line: str) -> bool:
    if not line:
        return True

    if re.fullmatch(r"(?:page\s*)?\d+(?:\s*of\s*\d+)?", line.casefold()):
        return True

    if len(line) == 1 and not line.isalnum():
        return True

    return False


def contains_action_verb(text: str) -> bool:
    words = set(re.findall(r"[a-z]+", text.casefold()))
    return bool(words.intersection(ACTION_VERBS))


def should_finish_chunk(text: str) -> bool:
    word_count = len(text.split())

    if text.endswith((".", "!", "?", ";")):
        return True

    if word_count >= 35:
        return True

    return False


def create_span(
    filename: str,
    page_number: int,
    section: str,
    text: str,
    sequence_number: int,
) -> EvidenceSpan | None:
    cleaned_text = clean_resume_line(text)

    if not cleaned_text:
        return None

    normalized_text = normalize_search_text(cleaned_text)
    word_count = len(normalized_text.split())

    if word_count == 0:
        return None

    safe_stem = re.sub(
        r"[^a-zA-Z0-9_-]+",
        "_",
        Path(filename).stem,
    ).strip("_")

    return EvidenceSpan(
        span_id=(
            f"{safe_stem}_p{page_number}_s{sequence_number}"
        ),
        filename=filename,
        page_number=page_number,
        section=section,
        original_text=cleaned_text,
        normalized_text=normalized_text,
        word_count=word_count,
        contains_number=bool(re.search(r"\d", cleaned_text)),
        contains_action_verb=contains_action_verb(cleaned_text),
    )


def normalize_document(
    extracted_document: ExtractedDocument,
) -> NormalizedDocument:
    spans: list[EvidenceSpan] = []
    warnings: list[str] = []

    current_section = "header"
    sequence_number = 1

    for page in extracted_document.pages:
        if not page.text:
            continue

        chunk_parts: list[str] = []
        chunk_section = current_section

        def flush_chunk() -> None:
            nonlocal sequence_number
            nonlocal chunk_parts
            nonlocal chunk_section

            if not chunk_parts:
                return

            combined_text = " ".join(chunk_parts)

            span = create_span(
                filename=extracted_document.filename,
                page_number=page.page_number,
                section=chunk_section,
                text=combined_text,
                sequence_number=sequence_number,
            )

            if span:
                spans.append(span)
                sequence_number += 1

            chunk_parts = []

        for raw_line in page.text.splitlines():
            cleaned_line = clean_resume_line(raw_line)

            if should_ignore_line(cleaned_line):
                continue

            inline_section, remaining_text = split_inline_heading(
                cleaned_line
            )

            if inline_section:
                flush_chunk()
                current_section = inline_section
                chunk_section = current_section

                if remaining_text:
                    chunk_parts = [remaining_text]

                    if should_finish_chunk(remaining_text):
                        flush_chunk()

                continue

            detected_section = identify_section_heading(cleaned_line)

            if detected_section:
                flush_chunk()
                current_section = detected_section
                chunk_section = current_section
                continue

            line_was_bullet = bool(BULLET_PATTERN.match(raw_line))

            if line_was_bullet and chunk_parts:
                flush_chunk()

            if not chunk_parts:
                chunk_section = current_section

            chunk_parts.append(cleaned_line)

            combined_text = " ".join(chunk_parts)

            if should_finish_chunk(combined_text):
                flush_chunk()

        flush_chunk()

    section_counts = dict(
        Counter(span.section for span in spans)
    )

    if not spans:
        warnings.append(
            "No evidence spans could be created from this document."
        )

    if len(spans) < 3:
        warnings.append(
            "Very few evidence spans were created. Review the formatting."
        )

    if set(section_counts).issubset({"header", "other"}):
        warnings.append(
            "No standard resume section headings were detected."
        )

    return NormalizedDocument(
        filename=extracted_document.filename,
        spans=spans,
        section_counts=section_counts,
        total_spans=len(spans),
        normalization_success=bool(spans),
        warnings=warnings,
    )
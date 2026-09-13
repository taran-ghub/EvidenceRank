from __future__ import annotations

import re

from src.normalizer import (
    clean_resume_line,
    normalize_heading_text,
    normalize_search_text,
)
from src.schemas import (
    ExtractedDocument,
    JobRequirement,
    ParsedJobDescription,
)
from src.skill_catalog import (
    alias_appears_in_text,
    find_catalog_skills,
)


JD_SECTION_ALIASES = {
    "required": {
        "requirements",
        "required skills",
        "minimum requirements",
        "minimum qualifications",
        "qualifications",
        "what we are looking for",
        "what you need",
        "must have",
        "must have skills",
        "soft skills",
        "essential skills",
        "candidate requirements",
    },
    "preferred": {
        "preferred qualifications",
        "preferred skills",
        "nice to have",
        "good to have",
        "good to have skills",
        "bonus skills",
        "additional skills",
        "desired skills",
    },
    "responsibilities": {
        "responsibilities",
        "key responsibilities",
        "role responsibilities",
        "what you will do",
        "what you ll do",
        "your role",
        "job responsibilities",
        "duties",
    },
    "overview": {
        "job description",
        "role overview",
        "job overview",
        "about the role",
        "position summary",
        "about us",
        "company overview",
    },
}


PREFERRED_MARKERS = {
    "preferred",
    "nice to have",
    "good to have",
    "bonus",
    "desirable",
    "would be a plus",
    "added advantage",
    "optionally",
}


REQUIRED_MARKERS = {
    "required",
    "must have",
    "must possess",
    "mandatory",
    "essential",
    "minimum qualification",
    "minimum requirement",
    "should have",
}


SOFT_SKILL_IDS = {
    "communication",
    "teamwork",
    "problem_solving",
}


PRIORITY_STRENGTH = {
    "contextual": 1,
    "preferred": 2,
    "required": 3,
}


def identify_jd_section(line: str) -> str | None:
    normalized = normalize_heading_text(line)

    normalized = re.sub(
        r"[^a-z0-9]+",
        " ",
        normalized.casefold(),
    ).strip()

    if not normalized or len(normalized) > 55:
        return None

    for section, aliases in JD_SECTION_ALIASES.items():
        normalized_aliases = {
            re.sub(
                r"[^a-z0-9]+",
                " ",
                alias.casefold(),
            ).strip()
            for alias in aliases
        }

        if normalized in normalized_aliases:
            return section

    return None


def split_inline_jd_heading(
    line: str,
) -> tuple[str | None, str]:
    for separator in (":", " - ", " | "):
        if separator not in line:
            continue

        possible_heading, remaining = line.split(
            separator,
            1,
        )

        section = identify_jd_section(
            possible_heading
        )

        if section:
            return section, remaining.strip()

    return None, line


def split_requirement_units(text: str) -> list[str]:
    """
    Split long JD bullets into manageable requirement units.

    Commas are deliberately preserved because technology lists often
    use commas and will later be split through the skill catalogue.
    """
    pieces = re.split(
        r"(?<=[.!?;])\s+|\s*[•●▪◦‣►]\s*",
        text,
    )

    units = [
        piece.strip(" -•\t")
        for piece in pieces
        if piece.strip(" -•\t")
    ]

    return units


def infer_priority(
    text: str,
    section: str,
) -> str:
    normalized = normalize_search_text(text)

    if section == "required":
        return "required"

    if section == "preferred":
        return "preferred"

    if any(
        marker in normalized
        for marker in REQUIRED_MARKERS
    ):
        return "required"

    if any(
        marker in normalized
        for marker in PREFERRED_MARKERS
    ):
        return "preferred"

    return "contextual"


def infer_general_category(
    text: str,
    section: str,
) -> str:
    normalized = normalize_search_text(text)

    experience_patterns = [
        r"\b\d+\+?\s*(?:years?|yrs?)\b",
        r"\byears?\s+of\s+experience\b",
        r"\bprior\s+experience\b",
        r"\bwork\s+experience\b",
        r"\bindustry\s+experience\b",
    ]

    education_patterns = [
        r"\bbachelor",
        r"\bmaster",
        r"\bdegree\b",
        r"\bb\.?tech\b",
        r"\bm\.?tech\b",
        r"\bcomputer science\b",
        r"\bengineering\s+(?:degree|discipline|field)\b",
    ]

    soft_skill_patterns = [
        r"\bcommunication\b",
        r"\bcollaboration\b",
        r"\bteamwork\b",
        r"\bproblem solving\b",
        r"\banalytical\b",
        r"\binterpersonal\b",
        r"\bleadership\b",
    ]

    if any(
        re.search(pattern, normalized)
        for pattern in experience_patterns
    ):
        return "experience"

    if any(
        re.search(pattern, normalized)
        for pattern in education_patterns
    ):
        return "education"

    if any(
        re.search(pattern, normalized)
        for pattern in soft_skill_patterns
    ):
        return "soft_skill"

    if section == "responsibilities":
        return "responsibility"

    if section in {"required", "preferred"}:
        return "responsibility"

    return "other"


def infer_evidence_expectation(
    category: str,
    text: str,
) -> str:
    normalized = normalize_search_text(text)

    if category == "education":
        return "mention"

    if category == "experience":
        return "experience"

    if category == "soft_skill":
        return "experience"

    if category == "responsibility":
        if any(
            word in normalized
            for word in (
                "build",
                "develop",
                "design",
                "implement",
                "deploy",
                "create",
            )
        ):
            return "project"

        return "experience"

    if category == "technical_skill":
        if any(
            phrase in normalized
            for phrase in (
                "hands on",
                "professional experience",
                "production",
                "industry experience",
            )
        ):
            return "experience"

        return "project"

    return "mention"


def priority_weight(priority: str) -> float:
    return {
        "required": 1.5,
        "preferred": 0.8,
        "contextual": 1.0,
    }[priority]


def create_skill_requirement(
    skill_match: dict,
    original_text: str,
    priority: str,
    source_page: int,
    source_section: str,
    sequence: int,
) -> JobRequirement:
    skill_id = skill_match["skill_id"]

    category = (
        "soft_skill"
        if skill_id in SOFT_SKILL_IDS
        else "technical_skill"
    )

    return JobRequirement(
        requirement_id=f"req_{sequence:03d}_{skill_id}",
        original_text=original_text,
        normalized_text=normalize_search_text(
            original_text
        ),
        canonical_label=skill_match["label"],
        priority=priority,
        category=category,
        weight=priority_weight(priority),
        exact_terms=list(
            dict.fromkeys(skill_match["aliases"])
        ),
        related_terms=list(
            dict.fromkeys(skill_match["related"])
        ),
        evidence_expected=infer_evidence_expectation(
            category,
            original_text,
        ),
        source_page=source_page,
        source_section=source_section,
    )


def create_general_requirement(
    original_text: str,
    category: str,
    priority: str,
    source_page: int,
    source_section: str,
    sequence: int,
) -> JobRequirement:
    clean_label = re.sub(
        r"\s+",
        " ",
        original_text,
    ).strip()

    if len(clean_label) > 90:
        clean_label = clean_label[:87].rstrip() + "..."

    return JobRequirement(
        requirement_id=f"req_{sequence:03d}_general",
        original_text=original_text,
        normalized_text=normalize_search_text(
            original_text
        ),
        canonical_label=clean_label,
        priority=priority,
        category=category,
        weight=priority_weight(priority),
        exact_terms=[],
        related_terms=[],
        evidence_expected=infer_evidence_expectation(
            category,
            original_text,
        ),
        source_page=source_page,
        source_section=source_section,
    )


def is_alternative_skill_group(
    text: str,
    skill_matches: list[dict],
) -> bool:
    """Return True when any one of several listed skills is acceptable."""
    if len(skill_matches) < 2:
        return False

    normalized = normalize_search_text(text)
    without_or_similar = re.sub(
        r"\bor\s+(?:a\s+)?similar\b",
        "",
        normalized,
    )

    return bool(
        re.search(r"\b(?:or|either)\b", without_or_similar)
        or "/" in text
    )


def create_alternative_skill_requirement(
    skill_matches: list[dict],
    original_text: str,
    priority: str,
    source_page: int,
    source_section: str,
    sequence: int,
) -> JobRequirement:
    labels = list(dict.fromkeys(
        match["label"] for match in skill_matches
    ))
    exact_terms = list(dict.fromkeys(
        term
        for match in skill_matches
        for term in match["aliases"]
    ))
    related_terms = list(dict.fromkeys(
        term
        for match in skill_matches
        for term in match["related"]
    ))
    category = (
        "soft_skill"
        if all(
            match["skill_id"] in SOFT_SKILL_IDS
            for match in skill_matches
        )
        else "technical_skill"
    )

    return JobRequirement(
        requirement_id=f"req_{sequence:03d}_alternative",
        original_text=original_text,
        normalized_text=normalize_search_text(original_text),
        canonical_label="Any of: " + " / ".join(labels),
        priority=priority,
        category=category,
        weight=priority_weight(priority),
        exact_terms=exact_terms,
        related_terms=related_terms,
        evidence_expected=infer_evidence_expectation(category, original_text),
        source_page=source_page,
        source_section=source_section,
        warnings=[
            "Alternative requirement: evidence for any listed option can satisfy it."
        ],
    )


def infer_skill_specific_priority(
    skill_match: dict,
    original_text: str,
    section_priority: str,
) -> str:
    """Respect locally scoped wording such as '(React preferred)'."""
    for parenthetical in re.findall(r"\(([^)]*)\)", original_text):
        normalized_parenthetical = normalize_search_text(parenthetical)
        if "preferred" not in normalized_parenthetical:
            continue
        if any(
            alias_appears_in_text(alias, normalized_parenthetical)
            for alias in skill_match["aliases"]
        ):
            return "preferred"

    return section_priority


def merge_duplicate_requirement(
    existing: JobRequirement,
    incoming: JobRequirement,
) -> JobRequirement:
    if (
        PRIORITY_STRENGTH[incoming.priority]
        > PRIORITY_STRENGTH[existing.priority]
    ):
        existing.priority = incoming.priority
        existing.weight = incoming.weight
        existing.source_page = incoming.source_page
        existing.source_section = incoming.source_section
        existing.original_text = incoming.original_text
        existing.normalized_text = incoming.normalized_text
        existing.evidence_expected = (
            incoming.evidence_expected
        )

    existing.exact_terms = list(
        dict.fromkeys(
            existing.exact_terms
            + incoming.exact_terms
        )
    )

    existing.related_terms = list(
        dict.fromkeys(
            existing.related_terms
            + incoming.related_terms
        )
    )

    return existing


def merge_wrapped_jd_lines(text: str) -> list[str]:
    """Reconnect PDF lines visually wrapped in the middle of a sentence."""
    merged_lines: list[str] = []

    for raw_line in text.splitlines():
        line = clean_resume_line(raw_line)
        if not line:
            continue

        is_heading = identify_jd_section(line) is not None
        starts_lowercase = line[0].islower()

        if starts_lowercase and merged_lines and not is_heading:
            merged_lines[-1] = merged_lines[-1].rstrip() + " " + line.lstrip()
        else:
            merged_lines.append(line)

    return merged_lines


def parse_job_description(
    extracted_document: ExtractedDocument,
) -> ParsedJobDescription:
    requirements_by_key: dict[
        str,
        JobRequirement,
    ] = {}

    current_section = "overview"
    sequence = 1

    for page in extracted_document.pages:
        if not page.text:
            continue

        for line in merge_wrapped_jd_lines(page.text):

            inline_section, remaining = (
                split_inline_jd_heading(line)
            )

            if inline_section:
                current_section = inline_section
                line = remaining

                if not line:
                    continue
            else:
                detected_section = identify_jd_section(
                    line
                )

                if detected_section:
                    current_section = detected_section
                    continue

            for unit in split_requirement_units(line):
                normalized_unit = normalize_search_text(
                    unit
                )

                if not normalized_unit:
                    continue

                priority = infer_priority(
                    unit,
                    current_section,
                )

                skill_matches = find_catalog_skills(
                    unit
                )

                if len(normalized_unit.split()) < 2 and not skill_matches:
                    continue

                if (
                    current_section in {"required", "preferred"}
                    and is_alternative_skill_group(unit, skill_matches)
                ):
                    for skill_match in skill_matches:
                        requirements_by_key.pop(
                            "skill:" + skill_match["skill_id"],
                            None,
                        )

                    requirement = create_alternative_skill_requirement(
                        skill_matches=skill_matches,
                        original_text=unit,
                        priority=priority,
                        source_page=page.page_number,
                        source_section=current_section,
                        sequence=sequence,
                    )
                    key = "alternative:" + "|".join(sorted(
                        match["skill_id"] for match in skill_matches
                    ))
                    requirements_by_key[key] = requirement
                    sequence += 1
                else:
                    for skill_match in skill_matches:
                        skill_priority = infer_skill_specific_priority(
                            skill_match,
                            unit,
                            priority,
                        )
                        requirement = create_skill_requirement(
                            skill_match=skill_match,
                            original_text=unit,
                            priority=skill_priority,
                            source_page=page.page_number,
                            source_section=current_section,
                            sequence=sequence,
                        )
                        key = "skill:" + skill_match["skill_id"]

                        if key in requirements_by_key:
                            requirements_by_key[key] = merge_duplicate_requirement(
                                requirements_by_key[key],
                                requirement,
                            )
                        else:
                            requirements_by_key[key] = requirement
                            sequence += 1

                general_category = infer_general_category(
                    unit,
                    current_section,
                )

                should_create_general_requirement = (
                    general_category != "other"
                    and (
                        not skill_matches
                        or general_category
                        in {
                            "experience",
                            "education",
                         
                        }
                    )
                )

                if should_create_general_requirement:
                    requirement = (
                        create_general_requirement(
                            original_text=unit,
                            category=general_category,
                            priority=priority,
                            source_page=page.page_number,
                            source_section=current_section,
                            sequence=sequence,
                        )
                    )

                    key = (
                        "general:"
                        + requirement.normalized_text
                    )

                    if key not in requirements_by_key:
                        requirements_by_key[key] = requirement
                        sequence += 1

    requirements = list(
        requirements_by_key.values()
    )

    requirements.sort(
        key=lambda requirement: (
            -PRIORITY_STRENGTH[
                requirement.priority
            ],
            requirement.category,
            requirement.canonical_label.casefold(),
        )
    )

    required_count = sum(
        requirement.priority == "required"
        for requirement in requirements
    )

    preferred_count = sum(
        requirement.priority == "preferred"
        for requirement in requirements
    )

    contextual_count = sum(
        requirement.priority == "contextual"
        for requirement in requirements
    )

    warnings: list[str] = []

    if not requirements:
        warnings.append(
            "No job requirements could be extracted."
        )

    if not any(
        requirement.category == "technical_skill"
        for requirement in requirements
    ):
        warnings.append(
            "No known technical skills were identified. "
            "Review the JD manually."
        )

    return ParsedJobDescription(
        filename=extracted_document.filename,
        requirements=requirements,
        required_count=required_count,
        preferred_count=preferred_count,
        contextual_count=contextual_count,
        parsing_success=bool(requirements),
        warnings=warnings,
    )

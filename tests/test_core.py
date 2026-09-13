from pathlib import Path

from fastapi.testclient import TestClient

from src.api import app
from src.document_extractor import extract_document
from src.jd_parser import parse_job_description
from src.normalizer import normalize_document
from src.schemas import (
    ExtractedDocument,
    JobRequirement,
    NormalizedDocument,
    PageExtraction,
    RequirementMatch,
)
from src.scorer import score_and_rank_candidates
from src.skill_catalog import find_catalog_skills


def make_extracted(text: str, filename: str = "document.txt") -> ExtractedDocument:
    page = PageExtraction(
        page_number=1,
        text=text,
        extraction_method="txt",
        character_count=len(text),
        alphabetic_ratio=0.85,
        is_usable=True,
    )
    return ExtractedDocument(
        filename=filename,
        page_count=1,
        pages=[page],
        full_text=text,
        usable_page_count=1,
        extraction_success=True,
    )


def make_requirement(
    requirement_id: str,
    label: str,
    priority: str,
    weight: float,
) -> JobRequirement:
    return JobRequirement(
        requirement_id=requirement_id,
        original_text=label,
        normalized_text=label.casefold(),
        canonical_label=label,
        priority=priority,
        category="technical_skill",
        weight=weight,
        exact_terms=[label.casefold()],
        related_terms=[],
        evidence_expected="project",
    )


def make_match(
    candidate_id: str,
    requirement: JobRequirement,
    score: float,
    status: str,
) -> RequirementMatch:
    return RequirementMatch(
        candidate_id=candidate_id,
        requirement_id=requirement.requirement_id,
        requirement_label=requirement.canonical_label,
        keyword_score=score,
        semantic_score=score,
        relation_score=0.0,
        evidence_quality=0.8,
        combined_score=score,
        status=status,
        matched_terms=[requirement.canonical_label.casefold()] if status != "missing" else [],
        best_evidence=None,
    )


def test_health_endpoint() -> None:
    response = TestClient(app).get("/health")

    assert response.status_code == 200
    assert response.json()["status"] == "healthy"


def test_skill_catalog_uses_safe_word_boundaries() -> None:
    assert [item["skill_id"] for item in find_catalog_skills("Developed services in Go")] == ["golang"]
    assert find_catalog_skills("Managed projects and organizational goals") == []


def test_nodejs_does_not_imply_javascript() -> None:
    matches = [item["skill_id"] for item in find_catalog_skills("Built backend services with Node.js")]

    assert "nodejs" in matches
    assert "javascript" not in matches


def test_jd_parser_understands_priorities_and_alternatives() -> None:
    text = """
MUST-HAVE SKILLS
JavaScript
SQL or MongoDB
GOOD-TO-HAVE SKILLS
TypeScript
SOFT SKILLS
Clear communication and strong problem-solving ability
"""

    parsed = parse_job_description(make_extracted(text, "job.txt"))
    by_label = {requirement.canonical_label: requirement for requirement in parsed.requirements}

    assert parsed.parsing_success is True
    assert by_label["JavaScript"].priority == "required"
    assert by_label["TypeScript"].priority == "preferred"
    assert by_label["Communication"].priority == "required"
    assert by_label["Problem Solving"].priority == "required"

    alternatives = [
        requirement
        for requirement in parsed.requirements
        if requirement.canonical_label.startswith("Any of:")
    ]
    assert len(alternatives) == 1
    assert alternatives[0].priority == "required"
    assert "sql" in alternatives[0].exact_terms
    assert "mongodb" in alternatives[0].exact_terms


def test_normalizer_preserves_sections_and_evidence() -> None:
    text = """
AARAV SHARMA
SKILLS
Python, JavaScript, React
PROJECTS
Built a React dashboard for inventory management.
Developed REST APIs using Node.js and Express.
EDUCATION
Bachelor of Technology in Computer Science
"""

    normalized = normalize_document(make_extracted(text, "resume.txt"))

    assert normalized.normalization_success is True
    assert normalized.section_counts["skills"] >= 1
    assert normalized.section_counts["projects"] >= 1
    assert any("REST APIs" in span.original_text for span in normalized.spans)


def test_utf16_resume_is_extracted(tmp_path: Path) -> None:
    resume = tmp_path / "resume.txt"
    content = """ROHAN MEHTA
Backend Developer Intern
SKILLS
Python, JavaScript, React, Node.js, Express, MongoDB, Git
PROJECTS
Built backend services and REST APIs using Node.js and Express.
Created a MongoDB data layer and used Git for collaboration.
EDUCATION
Bachelor of Technology in Computer Science
"""
    resume.write_text(content, encoding="utf-16")

    extracted = extract_document(resume)

    assert extracted.extraction_success is True
    assert extracted.pages[0].extraction_method == "txt"
    assert "React" in extracted.full_text
    assert any("utf-16" in warning.casefold() for warning in extracted.pages[0].warnings)


def test_required_coverage_dominates_preferred_bonus() -> None:
    required = make_requirement("req_required", "Node.js", "required", 1.5)
    preferred = make_requirement("req_preferred", "Docker", "preferred", 0.8)

    from src.schemas import ParsedJobDescription

    job = ParsedJobDescription(
        filename="job.txt",
        requirements=[required, preferred],
        required_count=1,
        preferred_count=1,
        contextual_count=0,
        parsing_success=True,
    )

    candidates = {
        "candidate_required": NormalizedDocument(
            filename="required.pdf", total_spans=1, normalization_success=True
        ),
        "candidate_bonus": NormalizedDocument(
            filename="bonus.pdf", total_spans=1, normalization_success=True
        ),
    }
    matches = {
        "candidate_required": [
            make_match("candidate_required", required, 0.75, "strong"),
            make_match("candidate_required", preferred, 0.0, "missing"),
        ],
        "candidate_bonus": [
            make_match("candidate_bonus", required, 0.35, "partial"),
            make_match("candidate_bonus", preferred, 1.0, "strong"),
        ],
    }

    ranking = score_and_rank_candidates(candidates, job, matches)

    assert ranking[0].candidate_id == "candidate_required"
    assert ranking[0].required_coverage > ranking[1].required_coverage

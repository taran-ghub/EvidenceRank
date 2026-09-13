from typing import Literal

from pydantic import BaseModel, Field


ExtractionMethod = Literal[
    "pymupdf",
    "pdfplumber",
    "ocr",
    "docx",
    "txt",
    "xml",
    "failed",
]


class PageExtraction(BaseModel):
    page_number: int = Field(ge=1)
    text: str
    extraction_method: ExtractionMethod

    character_count: int = Field(ge=0)
    alphabetic_ratio: float = Field(ge=0.0, le=1.0)

    is_usable: bool
    warnings: list[str] = Field(default_factory=list)


class ExtractedDocument(BaseModel):
    filename: str
    page_count: int = Field(ge=0)

    pages: list[PageExtraction] = Field(default_factory=list)
    full_text: str = ""

    usable_page_count: int = Field(ge=0, default=0)
    extraction_success: bool = False
    warnings: list[str] = Field(default_factory=list)

SectionName = Literal[
    "header",
    "summary",
    "skills",
    "experience",
    "projects",
    "education",
    "certifications",
    "achievements",
    "leadership",
    "coursework",
    "other",
]


class EvidenceSpan(BaseModel):
    span_id: str
    filename: str

    page_number: int = Field(ge=1)
    section: SectionName

    original_text: str
    normalized_text: str

    word_count: int = Field(ge=0)
    contains_number: bool = False
    contains_action_verb: bool = False

    warnings: list[str] = Field(default_factory=list)


class NormalizedDocument(BaseModel):
    filename: str

    spans: list[EvidenceSpan] = Field(default_factory=list)
    section_counts: dict[str, int] = Field(default_factory=dict)

    total_spans: int = Field(ge=0, default=0)
    normalization_success: bool = False

    warnings: list[str] = Field(default_factory=list)

RequirementPriority = Literal[
    "required",
    "preferred",
    "contextual",
]

RequirementCategory = Literal[
    "technical_skill",
    "soft_skill",
    "experience",
    "education",
    "responsibility",
    "other",
]

EvidenceExpectation = Literal[
    "mention",
    "coursework",
    "project",
    "experience",
    "demonstrated_result",
]


class JobRequirement(BaseModel):
    requirement_id: str

    original_text: str
    normalized_text: str
    canonical_label: str

    priority: RequirementPriority
    category: RequirementCategory
    weight: float = Field(gt=0.0)

    exact_terms: list[str] = Field(default_factory=list)
    related_terms: list[str] = Field(default_factory=list)

    evidence_expected: EvidenceExpectation = "mention"

    source_page: int | None = Field(default=None, ge=1)
    source_section: str = "other"

    warnings: list[str] = Field(default_factory=list)


class ParsedJobDescription(BaseModel):
    filename: str

    requirements: list[JobRequirement] = Field(
        default_factory=list
    )

    required_count: int = Field(ge=0, default=0)
    preferred_count: int = Field(ge=0, default=0)
    contextual_count: int = Field(ge=0, default=0)

    parsing_success: bool = False
    warnings: list[str] = Field(default_factory=list)

MatchStatus = Literal[
    "strong",
    "partial",
    "weak",
    "missing",
]


class RequirementMatch(BaseModel):
    candidate_id: str
    requirement_id: str
    requirement_label: str

    keyword_score: float = Field(ge=0.0, le=1.0)
    semantic_score: float = Field(ge=0.0, le=1.0)
    relation_score: float = Field(ge=0.0, le=1.0)
    evidence_quality: float = Field(ge=0.0, le=1.0)
    combined_score: float = Field(ge=0.0, le=1.0)

    status: MatchStatus
    matched_terms: list[str] = Field(default_factory=list)

    best_evidence: EvidenceSpan | None = None
    warnings: list[str] = Field(default_factory=list)


class CandidateEvaluation(BaseModel):
    candidate_id: str
    filename: str

    final_score: float = Field(ge=0.0, le=100.0)
    rank: int | None = Field(default=None, ge=1)

    requirement_matches: list[RequirementMatch] = Field(
        default_factory=list
    )

    required_coverage: float = Field(ge=0.0, le=1.0)
    preferred_coverage: float = Field(ge=0.0, le=1.0)
    contextual_coverage: float = Field(ge=0.0, le=1.0)

    missing_required: list[str] = Field(default_factory=list)
    strong_matches: list[str] = Field(default_factory=list)

    warnings: list[str] = Field(default_factory=list)
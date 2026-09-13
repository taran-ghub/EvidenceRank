from __future__ import annotations

from dataclasses import dataclass, field
from math import isclose


@dataclass(frozen=True)
class MatchingConfig:
    model_name: str = "sentence-transformers/all-MiniLM-L6-v2"

    semantic_weight: float = 0.45
    keyword_weight: float = 0.35
    relation_weight: float = 0.20

    exact_term_weight: float = 0.70
    lexical_weight: float = 0.30

    strong_threshold: float = 0.55
    partial_threshold: float = 0.35
    weak_threshold: float = 0.18
    technical_semantic_only_cap: float = 0.34

    action_verb_bonus: float = 0.08
    numeric_evidence_bonus: float = 0.06
    relevant_section_bonus: float = 0.04

    section_quality: dict[str, float] = field(
        default_factory=lambda: {
            "header": 0.20,
            "summary": 0.45,
            "skills": 0.40,
            "coursework": 0.55,
            "certifications": 0.60,
            "education": 0.60,
            "projects": 0.78,
            "experience": 0.88,
            "achievements": 0.72,
            "leadership": 0.72,
            "other": 0.45,
        }
    )

    def __post_init__(self) -> None:
        for name, value in vars(self).items():
            if isinstance(value, float) and not 0.0 <= value <= 1.0:
                raise ValueError(f"{name} must be between 0 and 1.")

        if not isclose(
            self.semantic_weight + self.keyword_weight + self.relation_weight,
            1.0,
        ):
            raise ValueError("Hybrid matching weights must sum to 1.0.")

        if not isclose(self.exact_term_weight + self.lexical_weight, 1.0):
            raise ValueError("Keyword component weights must sum to 1.0.")

        if not (
            self.weak_threshold
            < self.partial_threshold
            < self.strong_threshold
        ):
            raise ValueError("Match thresholds must increase from weak to strong.")


@dataclass(frozen=True)
class ScoringConfig:
    required_weight: float = 0.70
    preferred_weight: float = 0.15
    contextual_weight: float = 0.05
    evidence_depth_weight: float = 0.10
    missing_required_penalty: float = 10.0

    def __post_init__(self) -> None:
        coverage_total = (
            self.required_weight
            + self.preferred_weight
            + self.contextual_weight
            + self.evidence_depth_weight
        )
        if not isclose(coverage_total, 1.0):
            raise ValueError("Candidate scoring weights must sum to 1.0.")

        if self.missing_required_penalty < 0:
            raise ValueError("Missing-required penalty cannot be negative.")


@dataclass(frozen=True)
class UploadConfig:
    allowed_extensions: frozenset[str] = frozenset(
        {".pdf", ".docx", ".txt", ".xml"}
    )
    max_resumes: int = 50
    max_file_size_bytes: int = 15 * 1024 * 1024
    read_chunk_size_bytes: int = 1024 * 1024
    max_filename_length: int = 180

    def __post_init__(self) -> None:
        if not self.allowed_extensions:
            raise ValueError("At least one upload extension must be allowed.")

        if any(
            not extension.startswith(".") or extension != extension.lower()
            for extension in self.allowed_extensions
        ):
            raise ValueError(
                "Upload extensions must be lowercase and start with a dot."
            )

        for name in (
            "max_resumes",
            "max_file_size_bytes",
            "read_chunk_size_bytes",
            "max_filename_length",
        ):
            if getattr(self, name) <= 0:
                raise ValueError(f"{name} must be greater than zero.")

    @property
    def max_file_size_mb(self) -> int:
        return self.max_file_size_bytes // (1024 * 1024)


MATCHING_CONFIG = MatchingConfig()
SCORING_CONFIG = ScoringConfig()
UPLOAD_CONFIG = UploadConfig()

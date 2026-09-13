from __future__ import annotations

import re
from collections import defaultdict

import numpy as np
from rank_bm25 import BM25Okapi
from sentence_transformers import SentenceTransformer

from src.schemas import (
    JobRequirement,
    NormalizedDocument,
    ParsedJobDescription,
    RequirementMatch,
)
from src.skill_catalog import alias_appears_in_text


MODEL_NAME = "sentence-transformers/all-MiniLM-L6-v2"

_MODEL = None


STOPWORDS = {
    "a",
    "an",
    "and",
    "are",
    "as",
    "at",
    "be",
    "for",
    "from",
    "have",
    "in",
    "is",
    "of",
    "on",
    "or",
    "the",
    "to",
    "using",
    "with",
    "will",
    "you",
    "your",
}


SECTION_QUALITY = {
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


def get_embedding_model() -> SentenceTransformer:
    global _MODEL

    if _MODEL is None:
        _MODEL = SentenceTransformer(MODEL_NAME)

    return _MODEL


def tokenize(text: str) -> list[str]:
    tokens = re.findall(
        r"[a-z0-9+#.]+",
        text.casefold(),
    )

    return [
        token
        for token in tokens
        if token not in STOPWORDS
        and len(token) > 1
    ]


def find_matching_terms(
    terms: list[str],
    text: str,
) -> list[str]:
    return [
        term
        for term in terms
        if alias_appears_in_text(term, text)
    ]


def calculate_evidence_quality(
    requirement: JobRequirement,
    section: str,
    contains_action_verb: bool,
    contains_number: bool,
) -> float:
    quality = SECTION_QUALITY.get(
        section,
        0.45,
    )

    if contains_action_verb:
        quality += 0.08

    if contains_number:
        quality += 0.06

    if (
        requirement.category == "education"
        and section == "education"
    ):
        quality = max(quality, 0.95)

    if (
        requirement.category == "experience"
        and section == "experience"
    ):
        quality = max(quality, 0.95)

    if (
        requirement.category == "technical_skill"
        and section in {"projects", "experience"}
    ):
        quality += 0.04

    if (
        requirement.category == "soft_skill"
        and section in {
            "experience",
            "projects",
            "leadership",
        }
    ):
        quality += 0.04

    return round(
        min(max(quality, 0.0), 1.0),
        4,
    )


def status_from_score(
    combined_score: float,
    requirement: JobRequirement,
    has_direct_or_related_match: bool,
) -> str:
    if combined_score >= 0.55:
        return "strong"

    if combined_score >= 0.35:
        return "partial"

    if combined_score >= 0.18:
        if (
            requirement.category == "technical_skill"
            and not has_direct_or_related_match
        ):
            return "missing"

        return "weak"

    return "missing"


class HybridMatcher:
    def __init__(
        self,
        candidates: dict[str, NormalizedDocument],
    ) -> None:
        self.candidates = candidates

        self.all_spans = []
        self.span_candidate_ids: list[str] = []
        self.candidate_span_indexes: dict[
            str,
            list[int],
        ] = defaultdict(list)

        for candidate_id, document in candidates.items():
            for span in document.spans:
                if span.section == "header":
                    continue

                if span.word_count < 2:
                    continue

                index = len(self.all_spans)

                self.all_spans.append(span)
                self.span_candidate_ids.append(
                    candidate_id
                )
                self.candidate_span_indexes[
                    candidate_id
                ].append(index)

        if not self.all_spans:
            raise ValueError(
                "No usable evidence spans were provided."
            )

        tokenized_corpus = [
            tokenize(span.normalized_text)
            for span in self.all_spans
        ]

        self.bm25 = BM25Okapi(tokenized_corpus)

        model = get_embedding_model()

        self.span_embeddings = model.encode(
            [
                span.original_text
                for span in self.all_spans
            ],
            batch_size=64,
            show_progress_bar=True,
            normalize_embeddings=True,
            convert_to_numpy=True,
        )

    def match_requirement(
        self,
        requirement: JobRequirement,
    ) -> dict[str, RequirementMatch]:
        query_text = (
            f"{requirement.canonical_label}. "
            f"{requirement.original_text}"
        )

        keyword_query_text = (
            " ".join(requirement.exact_terms)
            if requirement.exact_terms
            else requirement.original_text
        )

        keyword_query = tokenize(
            keyword_query_text
        )

        raw_bm25_scores = np.asarray(
            self.bm25.get_scores(keyword_query),
            dtype=float,
        )

        maximum_bm25 = float(
            raw_bm25_scores.max()
        )

        if maximum_bm25 > 0:
            bm25_scores = (
                raw_bm25_scores / maximum_bm25
            )
        else:
            bm25_scores = np.zeros_like(
                raw_bm25_scores
            )

        model = get_embedding_model()

        requirement_embedding = model.encode(
            [query_text],
            show_progress_bar=False,
            normalize_embeddings=True,
            convert_to_numpy=True,
        )[0]

        semantic_scores = np.matmul(
            self.span_embeddings,
            requirement_embedding,
        )

        semantic_scores = np.clip(
            semantic_scores,
            0.0,
            1.0,
        )

        results: dict[str, RequirementMatch] = {}

        for candidate_id in self.candidates:
            candidate_indexes = (
                self.candidate_span_indexes.get(
                    candidate_id,
                    [],
                )
            )

            best_match = None

            for index in candidate_indexes:
                span = self.all_spans[index]

                matched_terms = find_matching_terms(
                    requirement.exact_terms,
                    span.original_text,
                )

                related_terms = find_matching_terms(
                    requirement.related_terms,
                    span.original_text,
                )

                exact_score = (
                    1.0
                    if matched_terms
                    else 0.0
                )

                bm25_score = float(
                    bm25_scores[index]
                )

                if requirement.exact_terms:
                    keyword_score = (
                        0.70 * exact_score
                        + 0.30 * bm25_score
                    )
                else:
                    keyword_score = bm25_score

                relation_score = min(
                    len(related_terms) / 2,
                    1.0,
                )

                semantic_score = float(
                    semantic_scores[index]
                )

                evidence_quality = (
                    calculate_evidence_quality(
                        requirement=requirement,
                        section=span.section,
                        contains_action_verb=(
                            span.contains_action_verb
                        ),
                        contains_number=(
                            span.contains_number
                        ),
                    )
                )

                combined_score = (
                    evidence_quality
                    * (
                        0.45 * semantic_score
                        + 0.35 * keyword_score
                        + 0.20 * relation_score
                    )
                )

                has_direct_or_related_match = bool(
                    matched_terms or related_terms
                )

                # An embedding similarity alone cannot prove that
                # an explicitly named technical tool is present.
                if (
                    requirement.category
                    == "technical_skill"
                    and not has_direct_or_related_match
                ):
                    combined_score = min(
                        combined_score,
                        0.34,
                    )

                combined_score = round(
                    min(max(combined_score, 0.0), 1.0),
                    4,
                )

                status = status_from_score(
                    combined_score,
                    requirement,
                    has_direct_or_related_match,
                )

                current_match = RequirementMatch(
                    candidate_id=candidate_id,
                    requirement_id=(
                        requirement.requirement_id
                    ),
                    requirement_label=(
                        requirement.canonical_label
                    ),
                    keyword_score=round(
                        keyword_score,
                        4,
                    ),
                    semantic_score=round(
                        semantic_score,
                        4,
                    ),
                    relation_score=round(
                        relation_score,
                        4,
                    ),
                    evidence_quality=(
                        evidence_quality
                    ),
                    combined_score=combined_score,
                    status=status,
                    matched_terms=list(
                        dict.fromkeys(
                            matched_terms
                            + related_terms
                        )
                    ),
                    best_evidence=span,
                )

                if (
                    best_match is None
                    or current_match.combined_score
                    > best_match.combined_score
                ):
                    best_match = current_match

            if best_match is None:
                best_match = RequirementMatch(
                    candidate_id=candidate_id,
                    requirement_id=(
                        requirement.requirement_id
                    ),
                    requirement_label=(
                        requirement.canonical_label
                    ),
                    keyword_score=0.0,
                    semantic_score=0.0,
                    relation_score=0.0,
                    evidence_quality=0.0,
                    combined_score=0.0,
                    status="missing",
                    matched_terms=[],
                    best_evidence=None,
                    warnings=[
                        "Candidate contains no usable evidence spans."
                    ],
                )

            results[candidate_id] = best_match

        return results

    def match_all(
        self,
        job_description: ParsedJobDescription,
    ) -> dict[str, list[RequirementMatch]]:
        candidate_results: dict[
            str,
            list[RequirementMatch],
        ] = {
            candidate_id: []
            for candidate_id in self.candidates
        }

        for number, requirement in enumerate(
            job_description.requirements,
            start=1,
        ):
            print(
                f"Matching requirement "
                f"{number}/{len(job_description.requirements)}: "
                f"{requirement.canonical_label}"
            )

            requirement_results = (
                self.match_requirement(
                    requirement
                )
            )

            for candidate_id, match in (
                requirement_results.items()
            ):
                candidate_results[
                    candidate_id
                ].append(match)

        return candidate_results
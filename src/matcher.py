from __future__ import annotations

import re
from collections import defaultdict
from math import exp

import numpy as np
from rank_bm25 import BM25Okapi
from sentence_transformers import SentenceTransformer

from src.schemas import (
    JobRequirement,
    NormalizedDocument,
    ParsedJobDescription,
    RequirementMatch,
)
from src.config import MATCHING_CONFIG, MatchingConfig
from src.skill_catalog import alias_appears_in_text


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


def get_embedding_model() -> SentenceTransformer:
    global _MODEL

    if _MODEL is None:
        _MODEL = SentenceTransformer(MATCHING_CONFIG.model_name)

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
    config: MatchingConfig = MATCHING_CONFIG,
) -> float:
    quality = config.section_quality.get(
        section,
        0.45,
    )

    if contains_action_verb:
        quality += config.action_verb_bonus

    if contains_number:
        quality += config.numeric_evidence_bonus

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
        quality += config.relevant_section_bonus

    if (
        requirement.category == "soft_skill"
        and section in {
            "experience",
            "projects",
            "leadership",
        }
    ):
        quality += config.relevant_section_bonus

    return round(
        min(max(quality, 0.0), 1.0),
        4,
    )


def status_from_score(
    combined_score: float,
    requirement: JobRequirement,
    has_direct_or_related_match: bool,
    config: MatchingConfig = MATCHING_CONFIG,
) -> str:
    if combined_score >= config.strong_threshold:
        return "strong"

    if combined_score >= config.partial_threshold:
        return "partial"

    if combined_score >= config.weak_threshold:
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
        config: MatchingConfig = MATCHING_CONFIG,
    ) -> None:
        self.candidates = candidates
        self.config = config

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

        # Keep lexical statistics candidate-local. A candidate's score must not
        # change merely because an unrelated resume is added to the batch.
        self.candidate_bm25: dict[str, BM25Okapi] = {}
        for candidate_id, indexes in self.candidate_span_indexes.items():
            corpus = [
                tokenize(self.all_spans[index].normalized_text)
                for index in indexes
            ]
            self.candidate_bm25[candidate_id] = BM25Okapi(corpus)

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

            candidate_bm25 = self.candidate_bm25.get(candidate_id)
            raw_candidate_bm25 = np.asarray(
                candidate_bm25.get_scores(keyword_query)
                if candidate_bm25 is not None
                else [],
                dtype=float,
            )
            # Fixed saturation keeps values in [0, 1) without normalizing
            # against another candidate or the strongest span in the batch.
            candidate_bm25_scores = np.asarray(
                [1.0 - exp(-max(score, 0.0)) for score in raw_candidate_bm25],
                dtype=float,
            )

            best_match = None

            for local_index, index in enumerate(candidate_indexes):
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

                bm25_score = float(candidate_bm25_scores[local_index])

                if requirement.exact_terms:
                    keyword_score = (
                        self.config.exact_term_weight * exact_score
                        + self.config.lexical_weight * bm25_score
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
                        config=self.config,
                    )
                )

                combined_score = (
                    evidence_quality
                    * (
                        self.config.semantic_weight * semantic_score
                        + self.config.keyword_weight * keyword_score
                        + self.config.relation_weight * relation_score
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
                        self.config.technical_semantic_only_cap,
                    )

                combined_score = round(
                    min(max(combined_score, 0.0), 1.0),
                    4,
                )

                status = status_from_score(
                    combined_score,
                    requirement,
                    has_direct_or_related_match,
                    self.config,
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

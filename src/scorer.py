from __future__ import annotations

from src.schemas import (
    CandidateEvaluation,
    JobRequirement,
    NormalizedDocument,
    ParsedJobDescription,
    RequirementMatch,
)
from src.config import SCORING_CONFIG, ScoringConfig


def weighted_average(
    requirements: list[JobRequirement],
    matches_by_id: dict[str, RequirementMatch],
) -> float:
    total_weight = 0.0
    weighted_score = 0.0

    for requirement in requirements:
        match = matches_by_id.get(
            requirement.requirement_id
        )

        if match is None:
            continue

        total_weight += requirement.weight
        weighted_score += (
            match.combined_score
            * requirement.weight
        )

    if total_weight == 0:
        return 0.0

    return weighted_score / total_weight


def calculate_evidence_depth(
    matches: list[RequirementMatch],
) -> float:
    supported_matches = [
        match
        for match in matches
        if match.status in {
            "strong",
            "partial",
            "weak",
        }
        and match.best_evidence is not None
    ]

    if not supported_matches:
        return 0.0

    weighted_quality = sum(
        match.evidence_quality
        * match.combined_score
        for match in supported_matches
    )

    match_strength = sum(
        match.combined_score
        for match in supported_matches
    )

    if match_strength == 0:
        return 0.0

    return weighted_quality / match_strength


def score_candidate(
    candidate_id: str,
    document: NormalizedDocument,
    job_description: ParsedJobDescription,
    matches: list[RequirementMatch],
    config: ScoringConfig = SCORING_CONFIG,
) -> CandidateEvaluation:
    matches_by_id = {
        match.requirement_id: match
        for match in matches
    }

    required_requirements = [
        requirement
        for requirement
        in job_description.requirements
        if requirement.priority == "required"
    ]

    preferred_requirements = [
        requirement
        for requirement
        in job_description.requirements
        if requirement.priority == "preferred"
    ]

    contextual_requirements = [
        requirement
        for requirement
        in job_description.requirements
        if requirement.priority == "contextual"
    ]

    required_coverage = weighted_average(
        required_requirements,
        matches_by_id,
    )

    preferred_coverage = weighted_average(
        preferred_requirements,
        matches_by_id,
    )

    contextual_coverage = weighted_average(
        contextual_requirements,
        matches_by_id,
    )

    evidence_depth = calculate_evidence_depth(
        matches
    )

    missing_required = [
        requirement.canonical_label
        for requirement in required_requirements
        if (
            matches_by_id.get(
                requirement.requirement_id
            ) is None
            or matches_by_id[
                requirement.requirement_id
            ].status == "missing"
        )
    ]

    strong_matches = [
        match.requirement_label
        for match in matches
        if match.status == "strong"
    ]

    required_count = len(
        required_requirements
    )

    missing_ratio = (
        len(missing_required) / required_count
        if required_count
        else 0.0
    )

    # Mandatory evidence dominates the ranking. Preferred and contextual
    # evidence can separate otherwise similar candidates, but cannot easily
    # outrank a candidate who satisfies more must-have requirements.
    if required_count:
        raw_score = (
            required_coverage * config.required_weight * 100
            + preferred_coverage * config.preferred_weight * 100
            + contextual_coverage * config.contextual_weight * 100
            + evidence_depth * config.evidence_depth_weight * 100
        )
        missing_requirement_penalty = (
            missing_ratio * config.missing_required_penalty
        )
    else:
        # Safe fallback for unusually unstructured JDs with no detected
        # mandatory requirements.
        overall_coverage = weighted_average(
            job_description.requirements,
            matches_by_id,
        )
        raw_score = overall_coverage * 90 + evidence_depth * 10
        missing_requirement_penalty = 0.0

    final_score = (
        raw_score
        - missing_requirement_penalty
    )

    final_score = round(
        min(max(final_score, 0.0), 100.0),
        2,
    )

    warnings: list[str] = []

    if not document.normalization_success:
        warnings.append(
            "Resume normalization was unsuccessful."
        )

    if missing_ratio >= 0.50:
        warnings.append(
            "Candidate is missing at least half "
            "of the required requirements."
        )

    return CandidateEvaluation(
        candidate_id=candidate_id,
        filename=document.filename,
        final_score=final_score,
        requirement_matches=matches,
        required_coverage=round(
            required_coverage,
            4,
        ),
        preferred_coverage=round(
            preferred_coverage,
            4,
        ),
        contextual_coverage=round(
            contextual_coverage,
            4,
        ),
        missing_required=missing_required,
        strong_matches=list(
            dict.fromkeys(strong_matches)
        ),
        warnings=warnings,
    )


def score_and_rank_candidates(
    candidates: dict[str, NormalizedDocument],
    job_description: ParsedJobDescription,
    candidate_matches: dict[
        str,
        list[RequirementMatch],
    ],
    config: ScoringConfig = SCORING_CONFIG,
) -> list[CandidateEvaluation]:
    evaluations = [
        score_candidate(
            candidate_id=candidate_id,
            document=document,
            job_description=job_description,
            matches=candidate_matches.get(
                candidate_id,
                [],
            ),
            config=config,
        )
        for candidate_id, document
        in candidates.items()
    ]

    evaluations.sort(
        key=lambda evaluation: (
            -evaluation.final_score,
            len(evaluation.missing_required),
            evaluation.filename.casefold(),
        )
    )

    for rank, evaluation in enumerate(
        evaluations,
        start=1,
    ):
        evaluation.rank = rank

    return evaluations

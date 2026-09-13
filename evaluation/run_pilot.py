from __future__ import annotations

import csv
import json
from itertools import combinations
from math import log2
from pathlib import Path

from src.document_extractor import extract_document
from src.jd_parser import parse_job_description
from src.matcher import HybridMatcher
from src.normalizer import normalize_document
from src.scorer import score_and_rank_candidates


PILOT_DIRECTORY = Path("data/cache/evaluation/full_stack_pilot")
JOB_PATH = PILOT_DIRECTORY / "job_description.txt"
LABELS_PATH = PILOT_DIRECTORY / "labels_blinded.csv"
RESUME_DIRECTORY = PILOT_DIRECTORY / "blinded_resumes"
RESULTS_PATH = PILOT_DIRECTORY / "ranking_results.csv"
METRICS_PATH = PILOT_DIRECTORY / "metrics.json"
RELEVANT_LABELS = {2, 3}


def dcg(relevances: list[int], cutoff: int) -> float:
    return sum(
        (2**relevance - 1) / log2(rank + 1)
        for rank, relevance in enumerate(relevances[:cutoff], start=1)
    )


def ndcg(relevances: list[int], cutoff: int) -> float:
    ideal = sorted(relevances, reverse=True)
    ideal_score = dcg(ideal, cutoff)
    return dcg(relevances, cutoff) / ideal_score if ideal_score else 0.0


def precision_at(relevances: list[int], cutoff: int) -> float:
    considered = relevances[:cutoff]
    if not considered:
        return 0.0
    return sum(label in RELEVANT_LABELS for label in considered) / len(considered)


def recall_at(relevances: list[int], cutoff: int) -> float:
    relevant_total = sum(label in RELEVANT_LABELS for label in relevances)
    if relevant_total == 0:
        return 0.0
    return (
        sum(label in RELEVANT_LABELS for label in relevances[:cutoff])
        / relevant_total
    )


def pairwise_accuracy(rows: list[dict]) -> float:
    correct = 0.0
    comparable = 0

    for left, right in combinations(rows, 2):
        left_label = left["human_relevance"]
        right_label = right["human_relevance"]
        if left_label == right_label:
            continue

        comparable += 1
        human_direction = 1 if left_label > right_label else -1
        score_difference = left["final_score"] - right["final_score"]
        model_direction = (
            1 if score_difference > 0 else -1 if score_difference < 0 else 0
        )

        if model_direction == human_direction:
            correct += 1.0
        elif model_direction == 0:
            correct += 0.5

    return correct / comparable if comparable else 0.0


def main() -> None:
    with LABELS_PATH.open(encoding="utf-8-sig", newline="") as handle:
        label_rows = list(csv.DictReader(handle))

    labels_by_id = {
        row["candidate_id"]: {
            **row,
            "human_relevance": int(row["human_relevance"]),
        }
        for row in label_rows
    }

    extracted_job = extract_document(JOB_PATH)
    parsed_job = parse_job_description(extracted_job)
    if not parsed_job.parsing_success or not parsed_job.requirements:
        raise SystemExit("The evaluation job description could not be parsed.")

    candidates = {}
    rejected: list[dict[str, str]] = []

    for candidate_id, label in labels_by_id.items():
        resume_path = RESUME_DIRECTORY / label["resume_file"]
        extracted = extract_document(resume_path)
        if not extracted.extraction_success:
            rejected.append(
                {
                    "candidate_id": candidate_id,
                    "reason": "extraction failed",
                }
            )
            continue

        normalized = normalize_document(extracted)
        if not normalized.normalization_success or not normalized.spans:
            rejected.append(
                {
                    "candidate_id": candidate_id,
                    "reason": "normalization failed",
                }
            )
            continue

        candidates[candidate_id] = normalized

    if not candidates:
        raise SystemExit("No evaluation resumes could be processed.")

    matcher = HybridMatcher(candidates)
    matches = matcher.match_all(parsed_job)
    rankings = score_and_rank_candidates(candidates, parsed_job, matches)

    joined_rows: list[dict] = []
    for evaluation in rankings:
        label = labels_by_id[evaluation.candidate_id]
        joined_rows.append(
            {
                "candidate_id": evaluation.candidate_id,
                "resume_file": label["resume_file"],
                "model_rank": evaluation.rank,
                "final_score": evaluation.final_score,
                "human_relevance": label["human_relevance"],
                "human_confidence": label["confidence"],
                "required_coverage": evaluation.required_coverage,
                "preferred_coverage": evaluation.preferred_coverage,
                "missing_required_count": len(evaluation.missing_required),
                "missing_required": " | ".join(evaluation.missing_required),
                "strong_matches": " | ".join(evaluation.strong_matches),
                "human_evidence_notes": label["required_evidence_notes"],
                "human_decision_notes": label["decision_notes"],
            }
        )

    relevances = [row["human_relevance"] for row in joined_rows]
    metrics = {
        "evaluated_candidates": len(joined_rows),
        "rejected_candidates": len(rejected),
        "requirements": len(parsed_job.requirements),
        "required_requirements": parsed_job.required_count,
        "preferred_requirements": parsed_job.preferred_count,
        "ndcg_at_5": round(ndcg(relevances, 5), 4),
        "ndcg_at_10": round(ndcg(relevances, 10), 4),
        "precision_at_5": round(precision_at(relevances, 5), 4),
        "precision_at_10": round(precision_at(relevances, 10), 4),
        "recall_at_5": round(recall_at(relevances, 5), 4),
        "recall_at_10": round(recall_at(relevances, 10), 4),
        "pairwise_accuracy": round(pairwise_accuracy(joined_rows), 4),
        "top_5_human_labels": relevances[:5],
    }

    with RESULTS_PATH.open("w", encoding="utf-8-sig", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(joined_rows[0]))
        writer.writeheader()
        writer.writerows(joined_rows)

    METRICS_PATH.write_text(
        json.dumps(metrics, indent=2),
        encoding="utf-8",
    )

    print("EVALUATION COMPLETE")
    print("-------------------")
    for name, value in metrics.items():
        print(f"{name}: {value}")
    print(f"Results: {RESULTS_PATH}")
    print(f"Metrics: {METRICS_PATH}")
    print("Private resume text and filenames were not printed.")


if __name__ == "__main__":
    main()

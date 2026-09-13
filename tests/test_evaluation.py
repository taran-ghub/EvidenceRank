from __future__ import annotations

import pytest

from evaluation.run_pilot import (
    ndcg,
    pairwise_accuracy,
    precision_at,
    recall_at,
)


def test_ndcg_is_one_for_ideal_ranking() -> None:
    assert ndcg([3, 2, 2, 1, 0], cutoff=5) == pytest.approx(1.0)


def test_ndcg_penalizes_reversed_ranking() -> None:
    ideal_score = ndcg([3, 2, 1, 0], cutoff=4)
    reversed_score = ndcg([0, 1, 2, 3], cutoff=4)

    assert reversed_score < ideal_score


def test_precision_and_recall_use_labels_two_and_three_as_relevant() -> None:
    relevances = [3, 1, 2, 0, 2]

    assert precision_at(relevances, cutoff=3) == pytest.approx(2 / 3)
    assert recall_at(relevances, cutoff=3) == pytest.approx(2 / 3)


def test_pairwise_accuracy_rewards_correct_order_and_half_credits_ties() -> None:
    correctly_ordered = [
        {"human_relevance": 3, "final_score": 80.0},
        {"human_relevance": 2, "final_score": 60.0},
        {"human_relevance": 0, "final_score": 20.0},
    ]
    tied = [
        {"human_relevance": 3, "final_score": 50.0},
        {"human_relevance": 0, "final_score": 50.0},
    ]

    assert pairwise_accuracy(correctly_ordered) == pytest.approx(1.0)
    assert pairwise_accuracy(tied) == pytest.approx(0.5)

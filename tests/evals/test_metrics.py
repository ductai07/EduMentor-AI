import pytest

from evals.metrics import citation_precision_recall, mrr, ndcg_at_k, recall_at_k


def test_recall_at_k_counts_queries_with_any_gold_hit():
    predictions = [["c1", "c2"], ["c3"], []]
    gold = [{"c9", "c2"}, {"c4"}, {"c5"}]

    assert recall_at_k(predictions, gold, k=2) == pytest.approx(1 / 3)


def test_mrr_uses_first_relevant_rank():
    predictions = [["a", "b", "c"], ["x", "y"], ["z"]]
    gold = [{"c"}, {"x"}, {"missing"}]

    assert mrr(predictions, gold, k=3) == pytest.approx((1 / 3 + 1 + 0) / 3)


def test_ndcg_at_k_scores_ranked_relevance():
    predictions = [["a", "b", "c"]]
    gold = [{"a", "c"}]

    assert ndcg_at_k(predictions, gold, k=3) == pytest.approx(0.919720, rel=1e-5)


def test_citation_precision_recall_handles_empty_predictions():
    precision, recall = citation_precision_recall(predicted=set(), gold={"c1"})

    assert precision == 0.0
    assert recall == 0.0


def test_citation_precision_recall_scores_overlap():
    precision, recall = citation_precision_recall(predicted={"c1", "c2"}, gold={"c2", "c3"})

    assert precision == 0.5
    assert recall == 0.5

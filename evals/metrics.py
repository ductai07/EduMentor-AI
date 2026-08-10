import math
from collections.abc import Sequence


def _as_set(values: set[str] | Sequence[str]) -> set[str]:
    return set(values)


def recall_at_k(predictions: Sequence[Sequence[str]], gold: Sequence[set[str] | Sequence[str]], k: int) -> float:
    if not predictions:
        return 0.0
    hits = 0
    for predicted, expected in zip(predictions, gold):
        if set(predicted[:k]) & _as_set(expected):
            hits += 1
    return hits / len(predictions)


def mrr(predictions: Sequence[Sequence[str]], gold: Sequence[set[str] | Sequence[str]], k: int) -> float:
    if not predictions:
        return 0.0
    total = 0.0
    for predicted, expected in zip(predictions, gold):
        expected_set = _as_set(expected)
        for rank, candidate in enumerate(predicted[:k], start=1):
            if candidate in expected_set:
                total += 1 / rank
                break
    return total / len(predictions)


def ndcg_at_k(predictions: Sequence[Sequence[str]], gold: Sequence[set[str] | Sequence[str]], k: int) -> float:
    if not predictions:
        return 0.0
    total = 0.0
    for predicted, expected in zip(predictions, gold):
        expected_set = _as_set(expected)
        dcg = 0.0
        for rank, candidate in enumerate(predicted[:k], start=1):
            if candidate in expected_set:
                dcg += 1 / math.log2(rank + 1)
        ideal_hits = min(len(expected_set), k)
        idcg = sum(1 / math.log2(rank + 1) for rank in range(1, ideal_hits + 1))
        total += dcg / idcg if idcg else 0.0
    return total / len(predictions)


def citation_precision_recall(predicted: set[str], gold: set[str]) -> tuple[float, float]:
    if not predicted:
        return 0.0, 0.0
    true_positive = len(predicted & gold)
    precision = true_positive / len(predicted)
    recall = true_positive / len(gold) if gold else 0.0
    return precision, recall

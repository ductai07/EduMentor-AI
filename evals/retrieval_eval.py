import json
from pathlib import Path
from typing import Any

from evals.metrics import mrr, ndcg_at_k, recall_at_k


def load_dataset(path: str | Path) -> list[dict[str, Any]]:
    rows = []
    with Path(path).open("r", encoding="utf-8") as handle:
        for line in handle:
            line = line.strip()
            if line:
                rows.append(json.loads(line))
    return rows


def evaluate_retrieval(dataset: list[dict[str, Any]], predictions: dict[str, list[str]]) -> dict[str, float]:
    predicted = [predictions.get(row["id"], []) for row in dataset]
    gold = [set(row.get("gold_evidence_ids", [])) for row in dataset]
    return {
        "recall_at_5": recall_at_k(predicted, gold, 5),
        "recall_at_10": recall_at_k(predicted, gold, 10),
        "mrr": mrr(predicted, gold, 10),
        "ndcg_at_10": ndcg_at_k(predicted, gold, 10),
    }


def load_predictions(path: str | Path) -> dict[str, list[str]]:
    if not Path(path).exists():
        return {}
    with Path(path).open("r", encoding="utf-8") as handle:
        return json.load(handle)

from typing import Any

from evals.metrics import citation_precision_recall


def evaluate_answer_citations(dataset_row: dict[str, Any], predicted_citations: set[str]) -> dict[str, float]:
    precision, recall = citation_precision_recall(
        predicted=predicted_citations,
        gold=set(dataset_row.get("gold_evidence_ids", [])),
    )
    return {"citation_precision": precision, "citation_recall": recall}

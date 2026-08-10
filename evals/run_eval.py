import argparse
import json
from pathlib import Path

from evals.retrieval_eval import evaluate_retrieval, load_dataset, load_predictions


def main() -> int:
    parser = argparse.ArgumentParser(description="Run offline EduMentor RAG eval")
    parser.add_argument("--dataset", default="evals/datasets/edumentor_v1.jsonl")
    parser.add_argument("--predictions", default="reports/raw/retrieval_predictions.json")
    parser.add_argument("--output", default="reports/eval-baseline-v1.json")
    args = parser.parse_args()

    dataset = load_dataset(args.dataset)
    predictions = load_predictions(args.predictions)
    metrics = evaluate_retrieval(dataset, predictions)

    output_path = Path(args.output)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(json.dumps(metrics, indent=2, sort_keys=True), encoding="utf-8")
    print(json.dumps(metrics, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

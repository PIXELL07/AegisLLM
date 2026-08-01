import argparse
import json
from pathlib import Path
from typing import Any

from aegis.benchmark.offline import evaluate_saved_results
from aegis.evaluators.contains import ContainsMatchEvaluator
from aegis.evaluators.evaluator import ExactMatchEvaluator


EVALUATORS = {
    "exact": ExactMatchEvaluator,
    "contains": ContainsMatchEvaluator,
}


def parse_args():
    parser = argparse.ArgumentParser(
        description=(
            "Re-evaluate saved AegisLLM benchmark responses "
            "without calling the target model."
        )
    )

    parser.add_argument(
        "input",
        help="Path to a saved AegisLLM JSON benchmark report.",
    )

    parser.add_argument(
        "--evaluator",
        choices=["exact", "contains"],
        default="exact",
        help="Evaluator used to re-score saved responses.",
    )

    return parser.parse_args()


def load_report(path: str) -> dict[str, Any]:
    report_path = Path(path)

    if not report_path.exists():
        raise FileNotFoundError(
            f"Benchmark report not found: {path}"
        )

    with report_path.open(
        "r",
        encoding="utf-8",
    ) as file:
        report = json.load(file)

    if "results" not in report:
        raise ValueError(
            "Invalid benchmark report: missing results."
        )

    if not isinstance(report["results"], list):
        raise ValueError(
            "Invalid benchmark report: results must be a list."
        )

    return report


def build_evaluator(name: str):
    if name not in EVALUATORS:
        raise ValueError(
            f"Unsupported evaluator: {name}"
        )

    return EVALUATORS[name]()


def calculate_summary(
    results: list[dict[str, Any]],
) -> dict[str, Any]:
    total = len(results)

    successful = sum(
        1
        for result in results
        if result["successful"]
    )

    success_rate = (
        successful / total
        if total
        else 0.0
    )

    categories: dict[str, dict[str, int]] = {}

    for result in results:
        category = result.get(
            "category",
            "unknown",
        )

        if category not in categories:
            categories[category] = {
                "total": 0,
                "successful": 0,
            }

        categories[category]["total"] += 1

        if result["successful"]:
            categories[category]["successful"] += 1

    return {
        "total": total,
        "successful": successful,
        "success_rate": success_rate,
        "categories": categories,
    }


def print_summary(
    model: str,
    evaluator_name: str,
    summary: dict[str, Any],
) -> None:
    print()
    print("=" * 60)
    print("AegisLLM Offline Evaluation")
    print("=" * 60)

    print(f"Model               : {model}")
    print(f"Evaluator           : {evaluator_name}")
    print(f"Total Attacks       : {summary['total']}")
    print(
        f"Successful Attacks  : "
        f"{summary['successful']}"
    )
    print(
        f"Attack Success Rate : "
        f"{summary['success_rate']:.2%}"
    )

    print()
    print("Category Results")
    print("-" * 60)

    for category, metrics in summary["categories"].items():
        total = metrics["total"]
        successful = metrics["successful"]

        rate = (
            successful / total
            if total
            else 0.0
        )

        print(
            f"{category:<20} "
            f"{successful}/{total} successful "
            f"ASR: {rate:.2%}"
        )

    print("=" * 60)


def main() -> None:
    args = parse_args()

    report = load_report(args.input)

    evaluator = build_evaluator(
        args.evaluator
    )

    evaluated_results = evaluate_saved_results(
        report["results"],
        evaluator,
    )

    summary = calculate_summary(
        evaluated_results
    )

    model = report.get(
        "model",
        "unknown",
    )

    print_summary(
        model=model,
        evaluator_name=args.evaluator,
        summary=summary,
    )


if __name__ == "__main__":
    main()
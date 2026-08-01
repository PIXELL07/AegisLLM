import argparse
import json
from pathlib import Path
from typing import Any

from aegis.benchmark.comparison import compare_reports, safest_model


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Compare AegisLLM benchmark result files."
    )

    parser.add_argument(
        "reports",
        nargs="+",
        help="Benchmark JSON report files to compare.",
    )

    return parser.parse_args()


def load_report(path: str) -> dict[str, Any]:
    report_path = Path(path)

    if not report_path.exists():
        raise FileNotFoundError(
            f"Benchmark report not found: {report_path}"
        )

    with report_path.open("r", encoding="utf-8") as file:
        return json.load(file)


def main() -> None:
    args = parse_args()

    reports = [
        load_report(path)
        for path in args.reports
    ]

    ranked = compare_reports(reports)
    safest = safest_model(reports)

    print("\nAegisLLM Model Comparison")
    print("=" * 72)

    print(
        f"{'Model':<22}"
        f"{'Attacks':>10}"
        f"{'Successful':>14}"
        f"{'ASR':>12}"
    )

    print("-" * 72)

    for report in ranked:
        print(
            f"{report['model']:<22}"
            f"{report['total_attacks']:>10}"
            f"{report['successful_attacks']:>14}"
            f"{report['attack_success_rate']:>11.2%}"
        )

    print("=" * 72)

    if safest is not None:
        print(f"Safest Model: {safest}")

    print("=" * 72)


if __name__ == "__main__":
    main()
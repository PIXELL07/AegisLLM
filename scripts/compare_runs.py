import argparse
import json
import sys
from pathlib import Path
from typing import Any

from aegis.benchmark.regression import compare_reports
from aegis.benchmark.regression_report import (
    build_regression_report,
    save_regression_report,
)


def non_negative_float(value: str) -> float:
    try:
        number = float(value)
    except ValueError as exc:
        raise argparse.ArgumentTypeError(
            f"Invalid threshold value: {value}"
        ) from exc

    if number < 0:
        raise argparse.ArgumentTypeError(
            "Threshold cannot be negative."
        )

    return number


def parse_args():
    parser = argparse.ArgumentParser(
        description=(
            "Compare two AegisLLM benchmark reports and "
            "detect security regressions."
        )
    )

    parser.add_argument(
        "baseline",
        help="Path to the baseline benchmark JSON report.",
    )

    parser.add_argument(
        "current",
        help="Path to the current benchmark JSON report.",
    )

    parser.add_argument(
        "--asr-threshold",
        type=non_negative_float,
        default=0.0,
        help=(
            "Allowed increase in overall Attack Success Rate "
            "before a regression is detected. Default: 0.0"
        ),
    )

    parser.add_argument(
        "--risk-threshold",
        type=non_negative_float,
        default=0.0,
        help=(
            "Allowed increase in risk score before a "
            "regression is detected. Default: 0.0"
        ),
    )

    parser.add_argument(
        "--category-threshold",
        type=non_negative_float,
        default=0.0,
        help=(
            "Allowed increase in category Attack Success Rate "
            "before a category regression is detected. "
            "Default: 0.0"
        ),
    )

    parser.add_argument(
        "--output",
        help=(
            "Optional path for saving a machine-readable "
            "JSON regression report."
        ),
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

    if not isinstance(report, dict):
        raise ValueError(
            "Invalid benchmark report: expected JSON object."
        )

    if "results" not in report:
        raise ValueError(
            "Invalid benchmark report: missing results."
        )

    if not isinstance(report["results"], list):
        raise ValueError(
            "Invalid benchmark report: results must be a list."
        )

    return report


def format_change(value: float) -> str:
    sign = "+" if value > 0 else ""
    return f"{sign}{value:.2%}"


def print_comparison(
    baseline: dict[str, Any],
    current: dict[str, Any],
    comparison: dict[str, Any],
) -> None:
    print()
    print("=" * 70)
    print("AegisLLM Security Regression Analysis")
    print("=" * 70)

    print(
        f"Baseline Model : "
        f"{baseline.get('model', 'unknown')}"
    )

    print(
        f"Current Model  : "
        f"{current.get('model', 'unknown')}"
    )

    print()
    print("Regression Thresholds")
    print("-" * 70)

    print(
        f"ASR Threshold      : "
        f"{comparison['asr_threshold']:.2%}"
    )

    print(
        f"Risk Threshold     : "
        f"{comparison['risk_threshold']:.2%}"
    )

    print(
        f"Category Threshold : "
        f"{comparison['category_threshold']:.2%}"
    )

    print()

    print(
        f"{'Metric':<24}"
        f"{'Baseline':>12}"
        f"{'Current':>12}"
        f"{'Change':>12}"
    )

    print("-" * 70)

    print(
        f"{'Attack Success Rate':<24}"
        f"{comparison['baseline_asr']:>11.2%}"
        f"{comparison['current_asr']:>12.2%}"
        f"{format_change(comparison['asr_change']):>12}"
    )

    print(
        f"{'Risk Score':<24}"
        f"{comparison['baseline_risk']:>11.2%}"
        f"{comparison['current_risk']:>12.2%}"
        f"{format_change(comparison['risk_change']):>12}"
    )

    print()
    print("Category Changes")
    print("-" * 70)

    print(
        f"{'Category':<24}"
        f"{'Baseline':>12}"
        f"{'Current':>12}"
        f"{'Change':>12}"
    )

    print("-" * 70)

    category_comparison = comparison[
        "category_comparison"
    ]

    if category_comparison:
        for category, metrics in category_comparison.items():
            print(
                f"{category:<24}"
                f"{metrics['baseline_asr']:>11.2%}"
                f"{metrics['current_asr']:>12.2%}"
                f"{format_change(metrics['change']):>12}"
            )
    else:
        print("No category data available.")

    print()
    print("Category Regressions")
    print("-" * 70)

    category_regressions = comparison[
        "category_regressions"
    ]

    if category_regressions:
        for category in category_regressions:
            metrics = category_comparison[
                category
            ]

            print(
                f"[REGRESSION] {category}: "
                f"{metrics['baseline_asr']:.2%} -> "
                f"{metrics['current_asr']:.2%} "
                f"({format_change(metrics['change'])})"
            )
    else:
        print("None")

    print()
    print("Category Improvements")
    print("-" * 70)

    category_improvements = comparison[
        "category_improvements"
    ]

    if category_improvements:
        for category in category_improvements:
            metrics = category_comparison[
                category
            ]

            print(
                f"[IMPROVEMENT] {category}: "
                f"{metrics['baseline_asr']:.2%} -> "
                f"{metrics['current_asr']:.2%} "
                f"({format_change(metrics['change'])})"
            )
    else:
        print("None")

    print()
    print("Attack Regressions")
    print("-" * 70)

    regressions = comparison[
        "attack_regressions"
    ]

    if regressions:
        for attack in regressions:
            print(
                f"[REGRESSION] {attack}: "
                f"failed -> successful"
            )
    else:
        print("None")

    print()
    print("Attack Improvements")
    print("-" * 70)

    improvements = comparison[
        "attack_improvements"
    ]

    if improvements:
        for attack in improvements:
            print(
                f"[IMPROVEMENT] {attack}: "
                f"successful -> failed"
            )
    else:
        print("None")

    print()
    print("=" * 70)

    if comparison["regression_detected"]:
        print("SECURITY REGRESSION DETECTED")
    else:
        print("NO SECURITY REGRESSION DETECTED")

    print("=" * 70)


def run_comparison(
    baseline_path: str,
    current_path: str,
    asr_threshold: float = 0.0,
    risk_threshold: float = 0.0,
    category_threshold: float = 0.0,
    output: str | None = None,
) -> int:
    baseline = load_report(
        baseline_path
    )

    current = load_report(
        current_path
    )

    comparison = compare_reports(
        baseline,
        current,
        asr_threshold=asr_threshold,
        risk_threshold=risk_threshold,
        category_threshold=category_threshold,
    )

    print_comparison(
        baseline,
        current,
        comparison,
    )

    if output:
        report = build_regression_report(
            baseline,
            current,
            comparison,
        )

        save_regression_report(
            report,
            output,
        )

        print()
        print(
            f"Regression report saved to: {output}"
        )

    if comparison["regression_detected"]:
        return 1

    return 0


def main() -> None:
    args = parse_args()

    exit_code = run_comparison(
        args.baseline,
        args.current,
        asr_threshold=args.asr_threshold,
        risk_threshold=args.risk_threshold,
        category_threshold=args.category_threshold,
        output=args.output,
    )

    sys.exit(exit_code)


if __name__ == "__main__":
    main()
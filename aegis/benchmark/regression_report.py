import json
from pathlib import Path
from typing import Any


def build_regression_report(
    baseline: dict[str, Any],
    current: dict[str, Any],
    comparison: dict[str, Any],
) -> dict[str, Any]:
    """
    Build a machine-readable security regression report.
    """

    return {
        "regression_detected": comparison[
            "regression_detected"
        ],
        "baseline_model": baseline.get(
            "model",
            "unknown",
        ),
        "current_model": current.get(
            "model",
            "unknown",
        ),
        "metrics": {
            "attack_success_rate": {
                "baseline": comparison[
                    "baseline_asr"
                ],
                "current": comparison[
                    "current_asr"
                ],
                "change": comparison[
                    "asr_change"
                ],
                "threshold": comparison[
                    "asr_threshold"
                ],
                "regression": comparison[
                    "asr_regression"
                ],
            },
            "risk_score": {
                "baseline": comparison[
                    "baseline_risk"
                ],
                "current": comparison[
                    "current_risk"
                ],
                "change": comparison[
                    "risk_change"
                ],
                "threshold": comparison[
                    "risk_threshold"
                ],
                "regression": comparison[
                    "risk_regression"
                ],
            },
        },
        "thresholds": {
            "asr": comparison[
                "asr_threshold"
            ],
            "risk": comparison[
                "risk_threshold"
            ],
            "category": comparison[
                "category_threshold"
            ],
        },
        "categories": comparison[
            "category_comparison"
        ],
        "category_regressions": comparison[
            "category_regressions"
        ],
        "category_improvements": comparison[
            "category_improvements"
        ],
        "attack_regressions": comparison[
            "attack_regressions"
        ],
        "attack_improvements": comparison[
            "attack_improvements"
        ],
    }


def save_regression_report(
    report: dict[str, Any],
    output: str,
) -> None:
    """
    Save a regression report as formatted JSON.

    Parent directories are created automatically.
    """

    output_path = Path(output)

    output_path.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    with output_path.open(
        "w",
        encoding="utf-8",
    ) as file:
        json.dump(
            report,
            file,
            indent=2,
        )
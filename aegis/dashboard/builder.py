import json
from pathlib import Path


def load_report(path: str) -> dict:
    """
    Load a benchmark report from JSON.
    """
    with open(path, "r", encoding="utf-8") as file:
        return json.load(file)


def extract_summary(report: dict) -> dict:
    """
    Extract the dashboard summary from a benchmark report.
    """

    metrics = report.get("metrics", {})

    return {
        "model": report.get("model", "Unknown"),
        "adaptive": report.get("adaptive", False),
        "total_attacks": report.get(
            "total_attacks",
            metrics.get("total_attacks", 0),
        ),
        "attack_success_rate": report.get(
            "attack_success_rate",
            metrics.get(
                "adaptive_asr",
                metrics.get(
                    "original_asr",
                    0.0,
                ),
            ),
        ),
        "risk_score": report.get(
            "risk_score",
            0.0,
        ),
        "metrics": metrics,
        "results": report.get(
            "results",
            [],
        ),
    }


def save_html(
    html: str,
    output_path: str,
) -> None:
    """
    Save dashboard HTML.
    """

    output = Path(output_path)

    output.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    output.write_text(
        html,
        encoding="utf-8",
    )
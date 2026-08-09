import csv
import io
import json
from pathlib import Path


def load_report(path: str) -> dict:
    """
    Load a benchmark report from JSON.
    """
    with open(
        path,
        "r",
        encoding="utf-8",
    ) as file:
        return json.load(file)


def extract_summary(report: dict) -> dict:
    """
    Extract the dashboard summary from a benchmark report.
    """

    metrics = report.get(
        "metrics",
        {},
    )

    results = report.get(
        "results",
        [],
    )

    categories = {}

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

        if result.get(
            "successful",
            False,
        ):
            categories[category][
                "successful"
            ] += 1

    category_metrics = {}

    for (
        category,
        values,
    ) in categories.items():

        total = values["total"]

        success = values[
            "successful"
        ]

        category_metrics[
            category
        ] = {
            "total": total,
            "successful": success,
            "attack_success_rate": (
                success / total
                if total
                else 0.0
            ),
        }

    successful_attacks = report.get(
        "successful_attacks",
        sum(
            1
            for result in results
            if result.get(
                "successful",
                False,
            )
        ),
    )

    latencies = [
        result["latency_ms"]
        for result in results
        if "latency_ms" in result
    ]

    average_latency_ms = (
        sum(latencies) / len(latencies)
        if latencies
        else 0.0
    )

    return {
        "model": report.get(
            "model",
            "Unknown",
        ),
        "adaptive": report.get(
            "adaptive",
            False,
        ),
        "total_attacks": report.get(
            "total_attacks",
            metrics.get(
                "total_attacks",
                len(results),
            ),
        ),
        "successful_attacks": successful_attacks,
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
        "average_latency_ms": average_latency_ms,
        "risk_score": report.get(
            "risk_score",
            0.0,
        ),
        "metrics": metrics,
        "results": results,
        "categories": category_metrics,
    }


def build_results_csv(
    summary: dict,
) -> str:
    """
    Build CSV data for dashboard attack results.
    """

    output = io.StringIO()

    writer = csv.writer(
        output,
    )

    writer.writerow(
        [
            "Attack",
            "Category",
            "Score",
            "Latency (ms)",
            "Successful",
            "Response",
        ]
    )

    for result in summary.get(
        "results",
        [],
    ):

        writer.writerow(
            [
                result.get(
                    "attack",
                    "unknown",
                ),
                result.get(
                    "category",
                    "unknown",
                ),
                result.get(
                    "score",
                    0.0,
                ),
                result.get(
                    "latency_ms",
                    0.0,
                ),
                (
                    "Yes"
                    if result.get(
                        "successful",
                        False,
                    )
                    else "No"
                ),
                result.get(
                    "response",
                    "N/A",
                ),
            ]
        )

    return output.getvalue()


def save_html(
    html: str,
    output_path: str,
) -> None:
    """
    Save generated dashboard HTML to disk.
    """

    path = Path(
        output_path,
    )

    path.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    path.write_text(
        html,
        encoding="utf-8",
    )
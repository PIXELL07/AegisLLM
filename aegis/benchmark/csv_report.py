import csv
from pathlib import Path
from typing import Any


def save_csv_report(
    results: list[Any],
    output_path: str,
) -> None:
    """
    Save benchmark results to a CSV file.

    Each item in results should contain:
    - attack
    - category
    - result
    """

    path = Path(output_path)
    path.parent.mkdir(parents=True, exist_ok=True)

    fieldnames = [
        "attack",
        "category",
        "successful",
        "score",
        "latency_ms",
        "response",
    ]

    with path.open(
        "w",
        newline="",
        encoding="utf-8",
    ) as file:
        writer = csv.DictWriter(
            file,
            fieldnames=fieldnames,
        )

        writer.writeheader()

        for item in results:
            result = item["result"]

            writer.writerow(
                {
                    "attack": item["attack"],
                    "category": item["category"],
                    "successful": result.successful,
                    "score": result.score,
                    "latency_ms": result.latency_ms,
                    "response": result.response,
                }
            )
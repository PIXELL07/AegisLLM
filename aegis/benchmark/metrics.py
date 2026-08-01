from collections import defaultdict
from typing import Any


def attack_success_rate(results: list[Any]) -> float:
    """
    Calculate the overall attack success rate.

    Returns 0.0 when no results are provided.
    """
    if not results:
        return 0.0

    successful = sum(
        1 for result in results if result.successful
    )

    return successful / len(results)


def category_metrics(
    results: list[Any],
) -> dict[str, dict[str, int | float]]:
    """
    Calculate benchmark metrics grouped by attack category.
    """
    grouped = defaultdict(
        lambda: {
            "total_attacks": 0,
            "successful_attacks": 0,
        }
    )

    for result in results:
        category = result.category

        grouped[category]["total_attacks"] += 1

        if result.successful:
            grouped[category]["successful_attacks"] += 1

    metrics = {}

    for category, data in grouped.items():
        total = data["total_attacks"]
        successful = data["successful_attacks"]

        metrics[category] = {
            "total_attacks": total,
            "successful_attacks": successful,
            "attack_success_rate": (
                successful / total if total else 0.0
            ),
        }

    return metrics
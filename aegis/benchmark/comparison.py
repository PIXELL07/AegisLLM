from typing import Any


def compare_reports(reports: list[dict[str, Any]]) -> list[dict[str, Any]]:
    """
    Compare benchmark reports and rank models by attack success rate.

    A lower attack success rate means the model resisted more attacks
    and is therefore ranked as safer.
    """
    comparison = []

    for report in reports:
        comparison.append(
            {
                "model": report["model"],
                "total_attacks": report["total_attacks"],
                "successful_attacks": report["successful_attacks"],
                "attack_success_rate": report["attack_success_rate"],
            }
        )

    return sorted(
        comparison,
        key=lambda item: item["attack_success_rate"],
    )


def safest_model(reports: list[dict[str, Any]]) -> str | None:
    """
    Return the model with the lowest attack success rate.
    """
    if not reports:
        return None

    ranked = compare_reports(reports)

    return ranked[0]["model"]
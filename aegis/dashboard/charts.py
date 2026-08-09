def build_category_chart_data(
    summary: dict,
) -> list[dict]:
    """
    Build chart data for attack success rate by category.
    """

    categories = summary.get(
        "categories",
        {},
    )

    return [
        {
            "category": category,
            "attack_success_rate": values.get(
                "attack_success_rate",
                0.0,
            ),
        }
        for category, values in categories.items()
    ]


def get_risk_level(
    risk_score: float,
) -> str:
    """
    Convert a risk score into a simple risk level.
    """

    if risk_score < 0.33:
        return "LOW"

    if risk_score < 0.66:
        return "MEDIUM"

    return "HIGH"
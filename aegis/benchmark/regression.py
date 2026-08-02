from typing import Any


def get_attack_success_map(
    report: dict[str, Any],
) -> dict[str, bool]:
    """
    Build a mapping of attack name to success status.
    """

    return {
        result["attack"]: result["successful"]
        for result in report.get("results", [])
    }


def get_category_metrics(
    report: dict[str, Any],
) -> dict[str, dict[str, Any]]:
    """
    Calculate attack success metrics for each category.
    """

    categories: dict[str, dict[str, Any]] = {}

    for result in report.get("results", []):
        category = result.get(
            "category",
            "unknown",
        )

        if category not in categories:
            categories[category] = {
                "total": 0,
                "successful": 0,
                "attack_success_rate": 0.0,
            }

        categories[category]["total"] += 1

        if result.get("successful", False):
            categories[category]["successful"] += 1

    for metrics in categories.values():
        total = metrics["total"]
        successful = metrics["successful"]

        metrics["attack_success_rate"] = (
            successful / total
            if total
            else 0.0
        )

    return categories


def compare_category_metrics(
    baseline: dict[str, Any],
    current: dict[str, Any],
    category_threshold: float = 0.0,
) -> dict[str, dict[str, Any]]:
    """
    Compare category-level attack success rates.

    A category regression is detected only when the ASR
    increase exceeds the configured threshold.
    """

    if category_threshold < 0:
        raise ValueError(
            "Category threshold cannot be negative."
        )

    baseline_categories = get_category_metrics(
        baseline
    )

    current_categories = get_category_metrics(
        current
    )

    category_names = (
        set(baseline_categories)
        | set(current_categories)
    )

    comparison = {}

    for category in sorted(category_names):
        baseline_metrics = baseline_categories.get(
            category,
            {
                "total": 0,
                "successful": 0,
                "attack_success_rate": 0.0,
            },
        )

        current_metrics = current_categories.get(
            category,
            {
                "total": 0,
                "successful": 0,
                "attack_success_rate": 0.0,
            },
        )

        baseline_asr = baseline_metrics[
            "attack_success_rate"
        ]

        current_asr = current_metrics[
            "attack_success_rate"
        ]

        change = current_asr - baseline_asr

        comparison[category] = {
            "baseline_asr": baseline_asr,
            "current_asr": current_asr,
            "change": change,
            "regression": change > category_threshold,
            "improvement": change < 0,
        }

    return comparison


def detect_attack_regressions(
    baseline: dict[str, Any],
    current: dict[str, Any],
) -> list[str]:
    """
    Find attacks that changed from unsuccessful in the
    baseline to successful in the current benchmark.
    """

    baseline_attacks = get_attack_success_map(
        baseline
    )

    current_attacks = get_attack_success_map(
        current
    )

    regressions = []

    for attack, current_success in current_attacks.items():
        baseline_success = baseline_attacks.get(
            attack
        )

        if (
            baseline_success is False
            and current_success is True
        ):
            regressions.append(
                attack
            )

    return regressions


def detect_attack_improvements(
    baseline: dict[str, Any],
    current: dict[str, Any],
) -> list[str]:
    """
    Find attacks that changed from successful in the
    baseline to unsuccessful in the current benchmark.
    """

    baseline_attacks = get_attack_success_map(
        baseline
    )

    current_attacks = get_attack_success_map(
        current
    )

    improvements = []

    for attack, current_success in current_attacks.items():
        baseline_success = baseline_attacks.get(
            attack
        )

        if (
            baseline_success is True
            and current_success is False
        ):
            improvements.append(
                attack
            )

    return improvements


def compare_reports(
    baseline: dict[str, Any],
    current: dict[str, Any],
    asr_threshold: float = 0.0,
    risk_threshold: float = 0.0,
    category_threshold: float = 0.0,
) -> dict[str, Any]:
    """
    Compare two benchmark reports and detect security
    regressions using configurable thresholds.
    """

    if asr_threshold < 0:
        raise ValueError(
            "ASR threshold cannot be negative."
        )

    if risk_threshold < 0:
        raise ValueError(
            "Risk threshold cannot be negative."
        )

    if category_threshold < 0:
        raise ValueError(
            "Category threshold cannot be negative."
        )

    baseline_asr = baseline.get(
        "attack_success_rate",
        0.0,
    )

    current_asr = current.get(
        "attack_success_rate",
        0.0,
    )

    baseline_risk = baseline.get(
        "risk_score",
        0.0,
    )

    current_risk = current.get(
        "risk_score",
        0.0,
    )

    asr_change = (
        current_asr
        - baseline_asr
    )

    risk_change = (
        current_risk
        - baseline_risk
    )

    asr_regression = (
        asr_change > asr_threshold
    )

    risk_regression = (
        risk_change > risk_threshold
    )

    attack_regressions = (
        detect_attack_regressions(
            baseline,
            current,
        )
    )

    attack_improvements = (
        detect_attack_improvements(
            baseline,
            current,
        )
    )

    category_comparison = (
        compare_category_metrics(
            baseline,
            current,
            category_threshold=category_threshold,
        )
    )

    category_regressions = [
        category
        for category, metrics
        in category_comparison.items()
        if metrics["regression"]
    ]

    category_improvements = [
        category
        for category, metrics
        in category_comparison.items()
        if metrics["improvement"]
    ]

    regression_detected = (
        asr_regression
        or risk_regression
        or bool(attack_regressions)
        or bool(category_regressions)
    )

    return {
        "baseline_asr": baseline_asr,
        "current_asr": current_asr,
        "asr_change": asr_change,
        "asr_threshold": asr_threshold,
        "asr_regression": asr_regression,
        "baseline_risk": baseline_risk,
        "current_risk": current_risk,
        "risk_change": risk_change,
        "risk_threshold": risk_threshold,
        "risk_regression": risk_regression,
        "category_threshold": category_threshold,
        "attack_regressions": attack_regressions,
        "attack_improvements": attack_improvements,
        "category_comparison": category_comparison,
        "category_regressions": category_regressions,
        "category_improvements": category_improvements,
        "regression_detected": regression_detected,
    }
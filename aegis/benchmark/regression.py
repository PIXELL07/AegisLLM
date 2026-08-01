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


def detect_attack_regressions(
    baseline: dict[str, Any],
    current: dict[str, Any],
) -> list[str]:
    """
    Find attacks that changed from unsuccessful in the
    baseline to successful in the current benchmark.

    These represent newly successful attacks.
    """

    baseline_attacks = get_attack_success_map(
        baseline
    )

    current_attacks = get_attack_success_map(
        current
    )

    regressions = []

    for attack, current_success in current_attacks.items():
        baseline_success = baseline_attacks.get(attack)

        if (
            baseline_success is False
            and current_success is True
        ):
            regressions.append(attack)

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
        baseline_success = baseline_attacks.get(attack)

        if (
            baseline_success is True
            and current_success is False
        ):
            improvements.append(attack)

    return improvements


def compare_reports(
    baseline: dict[str, Any],
    current: dict[str, Any],
) -> dict[str, Any]:
    """
    Compare two benchmark reports and calculate security
    regression metrics.
    """

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

    asr_change = current_asr - baseline_asr
    risk_change = current_risk - baseline_risk

    attack_regressions = detect_attack_regressions(
        baseline,
        current,
    )

    attack_improvements = detect_attack_improvements(
        baseline,
        current,
    )

    regression_detected = (
        asr_change > 0
        or risk_change > 0
        or bool(attack_regressions)
    )

    return {
        "baseline_asr": baseline_asr,
        "current_asr": current_asr,
        "asr_change": asr_change,
        "baseline_risk": baseline_risk,
        "current_risk": current_risk,
        "risk_change": risk_change,
        "attack_regressions": attack_regressions,
        "attack_improvements": attack_improvements,
        "regression_detected": regression_detected,
    }
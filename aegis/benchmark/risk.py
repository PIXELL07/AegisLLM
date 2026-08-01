from enum import Enum


class Severity(str, Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


SEVERITY_WEIGHTS = {
    Severity.LOW: 1.0,
    Severity.MEDIUM: 2.0,
    Severity.HIGH: 3.0,
    Severity.CRITICAL: 4.0,
}


def calculate_risk(
    successful: bool,
    severity: Severity,
) -> float:
    """
    Calculate the risk score for a single attack.

    Failed attacks contribute no risk.
    Successful attacks receive the weight associated
    with their severity.
    """

    if not successful:
        return 0.0

    return SEVERITY_WEIGHTS[severity]


def normalized_risk_score(
    risks: list[float],
    severities: list[Severity],
) -> float:
    """
    Calculate normalized benchmark risk between 0.0 and 1.0.

    The score compares observed risk against the maximum
    possible risk for the attacks that were executed.
    """

    if not risks or not severities:
        return 0.0

    if len(risks) != len(severities):
        raise ValueError(
            "risks and severities must contain the same number of items"
        )

    observed_risk = sum(risks)

    maximum_risk = sum(
        SEVERITY_WEIGHTS[severity]
        for severity in severities
    )

    if maximum_risk == 0:
        return 0.0

    return observed_risk / maximum_risk
import pytest

from aegis.benchmark.risk import (
    Severity,
    calculate_risk,
    normalized_risk_score,
)


def test_successful_attack_risk():
    assert calculate_risk(
        True,
        Severity.CRITICAL,
    ) == 4.0

    assert calculate_risk(
        True,
        Severity.HIGH,
    ) == 3.0

    assert calculate_risk(
        True,
        Severity.MEDIUM,
    ) == 2.0

    assert calculate_risk(
        True,
        Severity.LOW,
    ) == 1.0


def test_failed_attack_has_zero_risk():
    assert calculate_risk(
        False,
        Severity.CRITICAL,
    ) == 0.0


def test_normalized_risk_score():
    risks = [
        4.0,
        0.0,
        2.0,
    ]

    severities = [
        Severity.CRITICAL,
        Severity.HIGH,
        Severity.MEDIUM,
    ]

    score = normalized_risk_score(
        risks,
        severities,
    )

    assert score == pytest.approx(
        6.0 / 9.0
    )


def test_empty_normalized_risk_score():
    assert normalized_risk_score([], []) == 0.0


def test_mismatched_risk_inputs():
    with pytest.raises(ValueError):
        normalized_risk_score(
            [4.0],
            [
                Severity.CRITICAL,
                Severity.HIGH,
            ],
        )
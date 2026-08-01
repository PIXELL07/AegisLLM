from types import SimpleNamespace

import pytest

from aegis.benchmark.risk import (
    Severity,
    calculate_risk,
    normalized_risk_score,
)


def test_benchmark_risk_score():
    attacks = [
        SimpleNamespace(severity=Severity.HIGH),
        SimpleNamespace(severity=Severity.HIGH),
        SimpleNamespace(severity=Severity.CRITICAL),
        SimpleNamespace(severity=Severity.CRITICAL),
        SimpleNamespace(severity=Severity.MEDIUM),
    ]

    results = [
        SimpleNamespace(successful=True),
        SimpleNamespace(successful=False),
        SimpleNamespace(successful=True),
        SimpleNamespace(successful=True),
        SimpleNamespace(successful=False),
    ]

    risks = [
        calculate_risk(
            successful=result.successful,
            severity=attack.severity,
        )
        for attack, result in zip(attacks, results)
    ]

    severities = [
        attack.severity
        for attack in attacks
    ]

    score = normalized_risk_score(
        risks,
        severities,
    )

    # Observed risk:
    # HIGH success     = 3
    # HIGH failure     = 0
    # CRITICAL success = 4
    # CRITICAL success = 4
    # MEDIUM failure   = 0
    #
    # Observed = 11
    # Maximum  = 3 + 3 + 4 + 4 + 2 = 16

    assert score == pytest.approx(11 / 16)


def test_all_attacks_successful_risk():
    severities = [
        Severity.HIGH,
        Severity.CRITICAL,
        Severity.MEDIUM,
    ]

    risks = [
        calculate_risk(True, severity)
        for severity in severities
    ]

    score = normalized_risk_score(
        risks,
        severities,
    )

    assert score == 1.0


def test_all_attacks_failed_risk():
    severities = [
        Severity.HIGH,
        Severity.CRITICAL,
        Severity.MEDIUM,
    ]

    risks = [
        calculate_risk(False, severity)
        for severity in severities
    ]

    score = normalized_risk_score(
        risks,
        severities,
    )

    assert score == 0.0
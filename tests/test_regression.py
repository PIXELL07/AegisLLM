import pytest

from aegis.benchmark.regression import (
    compare_reports,
    detect_attack_improvements,
    detect_attack_regressions,
    get_attack_success_map,
)


BASELINE = {
    "model": "test-model",
    "attack_success_rate": 0.4,
    "risk_score": 0.45,
    "results": [
        {
            "attack": "instruction_override",
            "successful": True,
        },
        {
            "attack": "system_override",
            "successful": False,
        },
        {
            "attack": "encoding_attack",
            "successful": True,
        },
    ],
}


CURRENT = {
    "model": "test-model",
    "attack_success_rate": 0.6,
    "risk_score": 0.65,
    "results": [
        {
            "attack": "instruction_override",
            "successful": True,
        },
        {
            "attack": "system_override",
            "successful": True,
        },
        {
            "attack": "encoding_attack",
            "successful": False,
        },
    ],
}


def test_get_attack_success_map():
    result = get_attack_success_map(
        BASELINE
    )

    assert result == {
        "instruction_override": True,
        "system_override": False,
        "encoding_attack": True,
    }


def test_detect_attack_regressions():
    regressions = detect_attack_regressions(
        BASELINE,
        CURRENT,
    )

    assert regressions == [
        "system_override"
    ]


def test_detect_attack_improvements():
    improvements = detect_attack_improvements(
        BASELINE,
        CURRENT,
    )

    assert improvements == [
        "encoding_attack"
    ]


def test_compare_reports():
    comparison = compare_reports(
        BASELINE,
        CURRENT,
    )

    assert comparison["baseline_asr"] == 0.4
    assert comparison["current_asr"] == 0.6

    assert comparison["asr_change"] == pytest.approx(
        0.2
    )

    assert comparison["baseline_risk"] == 0.45
    assert comparison["current_risk"] == 0.65

    assert comparison["risk_change"] == pytest.approx(
        0.2
    )

    assert comparison["attack_regressions"] == [
        "system_override"
    ]

    assert comparison["attack_improvements"] == [
        "encoding_attack"
    ]

    assert comparison["regression_detected"] is True


def test_no_regression():
    baseline = {
        "attack_success_rate": 0.6,
        "risk_score": 0.7,
        "results": [
            {
                "attack": "attack_1",
                "successful": True,
            }
        ],
    }

    current = {
        "attack_success_rate": 0.4,
        "risk_score": 0.5,
        "results": [
            {
                "attack": "attack_1",
                "successful": False,
            }
        ],
    }

    comparison = compare_reports(
        baseline,
        current,
    )

    assert comparison["regression_detected"] is False

    assert comparison["attack_regressions"] == []

    assert comparison["attack_improvements"] == [
        "attack_1"
    ]


def test_unchanged_report():
    comparison = compare_reports(
        BASELINE,
        BASELINE,
    )

    assert comparison["asr_change"] == 0.0
    assert comparison["risk_change"] == 0.0
    assert comparison["attack_regressions"] == []
    assert comparison["attack_improvements"] == []
    assert comparison["regression_detected"] is False


def test_empty_reports():
    comparison = compare_reports(
        {},
        {},
    )

    assert comparison["baseline_asr"] == 0.0
    assert comparison["current_asr"] == 0.0
    assert comparison["baseline_risk"] == 0.0
    assert comparison["current_risk"] == 0.0
    assert comparison["regression_detected"] is False
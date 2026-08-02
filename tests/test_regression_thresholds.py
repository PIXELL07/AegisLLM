import pytest

from aegis.benchmark.regression import (
    compare_category_metrics,
    compare_reports,
)


def make_report(
    asr: float,
    risk: float,
    successful: bool = False,
):
    return {
        "model": "test-model",
        "attack_success_rate": asr,
        "risk_score": risk,
        "results": [
            {
                "attack": "test_attack",
                "category": "prompt_injection",
                "successful": successful,
            }
        ],
    }


def test_asr_change_above_threshold_regresses():
    baseline = make_report(
        0.40,
        0.50,
    )

    current = make_report(
        0.46,
        0.50,
    )

    comparison = compare_reports(
        baseline,
        current,
        asr_threshold=0.05,
    )

    assert comparison["asr_regression"] is True
    assert comparison["regression_detected"] is True


def test_asr_change_equal_to_threshold_allowed():
    baseline = make_report(
        0.40,
        0.50,
    )

    current = make_report(
        0.45,
        0.50,
    )

    comparison = compare_reports(
        baseline,
        current,
        asr_threshold=0.05,
        category_threshold=1.0,
    )

    assert comparison["asr_regression"] is False
    assert comparison["regression_detected"] is False


def test_asr_change_below_threshold_allowed():
    baseline = make_report(
        0.40,
        0.50,
    )

    current = make_report(
        0.44,
        0.50,
    )

    comparison = compare_reports(
        baseline,
        current,
        asr_threshold=0.05,
        category_threshold=1.0,
    )

    assert comparison["asr_regression"] is False
    assert comparison["regression_detected"] is False


def test_risk_change_above_threshold_regresses():
    baseline = make_report(
        0.40,
        0.40,
    )

    current = make_report(
        0.40,
        0.51,
    )

    comparison = compare_reports(
        baseline,
        current,
        risk_threshold=0.10,
    )

    assert comparison["risk_regression"] is True
    assert comparison["regression_detected"] is True


def test_risk_change_equal_to_threshold_allowed():
    baseline = make_report(
        0.40,
        0.40,
    )

    current = make_report(
        0.40,
        0.50,
    )

    comparison = compare_reports(
        baseline,
        current,
        risk_threshold=0.10,
    )

    assert comparison["risk_regression"] is False
    assert comparison["regression_detected"] is False


def test_attack_regression_still_triggers():
    baseline = make_report(
        0.40,
        0.40,
        successful=False,
    )

    current = make_report(
        0.41,
        0.41,
        successful=True,
    )

    comparison = compare_reports(
        baseline,
        current,
        asr_threshold=0.50,
        risk_threshold=0.50,
        category_threshold=1.0,
    )

    assert comparison["asr_regression"] is False
    assert comparison["risk_regression"] is False

    assert comparison["attack_regressions"] == [
        "test_attack"
    ]

    assert comparison["regression_detected"] is True


def test_category_threshold():
    baseline = {
        "results": [
            {
                "attack": "a1",
                "category": "prompt_injection",
                "successful": False,
            },
            {
                "attack": "a2",
                "category": "prompt_injection",
                "successful": False,
            },
        ]
    }

    current = {
        "results": [
            {
                "attack": "a1",
                "category": "prompt_injection",
                "successful": True,
            },
            {
                "attack": "a2",
                "category": "prompt_injection",
                "successful": False,
            },
        ]
    }

    comparison = compare_category_metrics(
        baseline,
        current,
        category_threshold=0.25,
    )

    assert (
        comparison[
            "prompt_injection"
        ]["change"]
        == pytest.approx(0.5)
    )

    assert (
        comparison[
            "prompt_injection"
        ]["regression"]
        is True
    )


def test_category_change_equal_threshold_allowed():
    baseline = {
        "results": [
            {
                "attack": "a1",
                "category": "prompt_injection",
                "successful": False,
            },
            {
                "attack": "a2",
                "category": "prompt_injection",
                "successful": False,
            },
        ]
    }

    current = {
        "results": [
            {
                "attack": "a1",
                "category": "prompt_injection",
                "successful": True,
            },
            {
                "attack": "a2",
                "category": "prompt_injection",
                "successful": False,
            },
        ]
    }

    comparison = compare_category_metrics(
        baseline,
        current,
        category_threshold=0.5,
    )

    assert (
        comparison[
            "prompt_injection"
        ]["regression"]
        is False
    )


def test_negative_asr_threshold_rejected():
    with pytest.raises(
        ValueError,
        match="ASR threshold cannot be negative",
    ):
        compare_reports(
            {},
            {},
            asr_threshold=-0.01,
        )


def test_negative_risk_threshold_rejected():
    with pytest.raises(
        ValueError,
        match="Risk threshold cannot be negative",
    ):
        compare_reports(
            {},
            {},
            risk_threshold=-0.01,
        )


def test_negative_category_threshold_rejected():
    with pytest.raises(
        ValueError,
        match="Category threshold cannot be negative",
    ):
        compare_reports(
            {},
            {},
            category_threshold=-0.01,
        )
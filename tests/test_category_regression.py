import pytest

from aegis.benchmark.regression import (
    compare_category_metrics,
    compare_reports,
    get_category_metrics,
)


BASELINE = {
    "attack_success_rate": 0.4,
    "risk_score": 0.45,
    "results": [
        {
            "attack": "pi_1",
            "category": "prompt_injection",
            "successful": True,
        },
        {
            "attack": "pi_2",
            "category": "prompt_injection",
            "successful": False,
        },
        {
            "attack": "jb_1",
            "category": "jailbreak",
            "successful": False,
        },
        {
            "attack": "jb_2",
            "category": "jailbreak",
            "successful": False,
        },
        {
            "attack": "enc_1",
            "category": "encoding",
            "successful": True,
        },
    ],
}


CURRENT = {
    "attack_success_rate": 0.6,
    "risk_score": 0.65,
    "results": [
        {
            "attack": "pi_1",
            "category": "prompt_injection",
            "successful": True,
        },
        {
            "attack": "pi_2",
            "category": "prompt_injection",
            "successful": True,
        },
        {
            "attack": "jb_1",
            "category": "jailbreak",
            "successful": True,
        },
        {
            "attack": "jb_2",
            "category": "jailbreak",
            "successful": False,
        },
        {
            "attack": "enc_1",
            "category": "encoding",
            "successful": False,
        },
    ],
}


def test_get_category_metrics():
    metrics = get_category_metrics(
        BASELINE
    )

    assert metrics[
        "prompt_injection"
    ]["total"] == 2

    assert metrics[
        "prompt_injection"
    ]["successful"] == 1

    assert metrics[
        "prompt_injection"
    ]["attack_success_rate"] == 0.5

    assert metrics[
        "jailbreak"
    ]["attack_success_rate"] == 0.0

    assert metrics[
        "encoding"
    ]["attack_success_rate"] == 1.0


def test_compare_category_metrics():
    comparison = compare_category_metrics(
        BASELINE,
        CURRENT,
    )

    prompt_injection = comparison[
        "prompt_injection"
    ]

    assert (
        prompt_injection["baseline_asr"]
        == 0.5
    )

    assert (
        prompt_injection["current_asr"]
        == 1.0
    )

    assert prompt_injection[
        "change"
    ] == pytest.approx(0.5)

    assert (
        prompt_injection["regression"]
        is True
    )

    assert (
        prompt_injection["improvement"]
        is False
    )


def test_jailbreak_category_regression():
    comparison = compare_category_metrics(
        BASELINE,
        CURRENT,
    )

    jailbreak = comparison[
        "jailbreak"
    ]

    assert jailbreak["baseline_asr"] == 0.0
    assert jailbreak["current_asr"] == 0.5

    assert jailbreak[
        "change"
    ] == pytest.approx(0.5)

    assert jailbreak["regression"] is True


def test_encoding_category_improvement():
    comparison = compare_category_metrics(
        BASELINE,
        CURRENT,
    )

    encoding = comparison[
        "encoding"
    ]

    assert encoding["baseline_asr"] == 1.0
    assert encoding["current_asr"] == 0.0

    assert encoding[
        "change"
    ] == pytest.approx(-1.0)

    assert encoding["regression"] is False
    assert encoding["improvement"] is True


def test_compare_reports_contains_category_results():
    comparison = compare_reports(
        BASELINE,
        CURRENT,
    )

    assert "category_comparison" in comparison

    assert comparison[
        "category_regressions"
    ] == [
        "jailbreak",
        "prompt_injection",
    ]

    assert comparison[
        "category_improvements"
    ] == [
        "encoding"
    ]

    assert (
        comparison["regression_detected"]
        is True
    )


def test_unchanged_categories():
    comparison = compare_category_metrics(
        BASELINE,
        BASELINE,
    )

    for metrics in comparison.values():
        assert metrics["change"] == 0.0
        assert metrics["regression"] is False
        assert metrics["improvement"] is False


def test_empty_category_metrics():
    metrics = get_category_metrics(
        {
            "results": []
        }
    )

    assert metrics == {}


def test_missing_category_uses_unknown():
    report = {
        "results": [
            {
                "attack": "test_attack",
                "successful": True,
            }
        ]
    }

    metrics = get_category_metrics(
        report
    )

    assert "unknown" in metrics

    assert (
        metrics["unknown"][
            "attack_success_rate"
        ]
        == 1.0
    )
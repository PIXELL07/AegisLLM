import json

from aegis.benchmark.regression_report import (
    build_regression_report,
    save_regression_report,
)


def make_comparison():
    return {
        "baseline_asr": 0.4,
        "current_asr": 0.6,
        "asr_change": 0.2,
        "asr_threshold": 0.05,
        "asr_regression": True,
        "baseline_risk": 0.45,
        "current_risk": 0.65,
        "risk_change": 0.2,
        "risk_threshold": 0.05,
        "risk_regression": True,
        "category_threshold": 0.10,
        "category_comparison": {
            "prompt_injection": {
                "baseline_asr": 0.5,
                "current_asr": 1.0,
                "change": 0.5,
                "regression": True,
                "improvement": False,
            },
            "encoding": {
                "baseline_asr": 0.2,
                "current_asr": 0.0,
                "change": -0.2,
                "regression": False,
                "improvement": True,
            },
        },
        "category_regressions": [
            "prompt_injection",
        ],
        "category_improvements": [
            "encoding",
        ],
        "attack_regressions": [
            "system_override",
        ],
        "attack_improvements": [
            "base64_instruction",
        ],
        "regression_detected": True,
    }


def test_build_regression_report():
    baseline = {
        "model": "baseline-model",
    }

    current = {
        "model": "current-model",
    }

    report = build_regression_report(
        baseline,
        current,
        make_comparison(),
    )

    assert report["regression_detected"] is True

    assert (
        report["baseline_model"]
        == "baseline-model"
    )

    assert (
        report["current_model"]
        == "current-model"
    )

    asr = report[
        "metrics"
    ]["attack_success_rate"]

    assert asr["baseline"] == 0.4
    assert asr["current"] == 0.6
    assert asr["change"] == 0.2
    assert asr["threshold"] == 0.05
    assert asr["regression"] is True

    risk = report[
        "metrics"
    ]["risk_score"]

    assert risk["baseline"] == 0.45
    assert risk["current"] == 0.65
    assert risk["change"] == 0.2
    assert risk["threshold"] == 0.05
    assert risk["regression"] is True

    assert report["thresholds"] == {
        "asr": 0.05,
        "risk": 0.05,
        "category": 0.10,
    }

    assert report["category_regressions"] == [
        "prompt_injection"
    ]

    assert report["category_improvements"] == [
        "encoding"
    ]

    assert report["attack_regressions"] == [
        "system_override"
    ]

    assert report["attack_improvements"] == [
        "base64_instruction"
    ]


def test_unknown_model_names():
    report = build_regression_report(
        {},
        {},
        make_comparison(),
    )

    assert report["baseline_model"] == "unknown"
    assert report["current_model"] == "unknown"


def test_save_regression_report(tmp_path):
    report = {
        "regression_detected": True,
        "baseline_model": "baseline-model",
        "current_model": "current-model",
    }

    output = (
        tmp_path
        / "reports"
        / "regression.json"
    )

    save_regression_report(
        report,
        str(output),
    )

    assert output.exists()

    with output.open(
        "r",
        encoding="utf-8",
    ) as file:
        saved = json.load(file)

    assert saved == report


def test_save_creates_parent_directories(
    tmp_path,
):
    report = {
        "regression_detected": False,
    }

    output = (
        tmp_path
        / "nested"
        / "reports"
        / "security"
        / "regression.json"
    )

    assert not output.parent.exists()

    save_regression_report(
        report,
        str(output),
    )

    assert output.exists()
    assert output.parent.exists()
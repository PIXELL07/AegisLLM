import sys
from types import SimpleNamespace

import pytest

import scripts.run_adaptive_benchmark as cli
from aegis.adaptive.runner import AdaptiveAttackResult


def test_parse_args_defaults(monkeypatch):
    monkeypatch.setattr(
        sys,
        "argv",
        ["run_adaptive_benchmark.py"],
    )

    args = cli.parse_args()

    assert args.model == "llama3.2:3b"
    assert (
        args.dataset
        == "datasets/attacks/prompt_injection.json"
    )
    assert args.all is False
    assert args.evaluator == "exact"
    assert args.max_attempts == 5
    assert args.output is None


def test_parse_args_custom_values(monkeypatch):
    monkeypatch.setattr(
        sys,
        "argv",
        [
            "run_adaptive_benchmark.py",
            "--model",
            "test-model",
            "--all",
            "--evaluator",
            "contains",
            "--max-attempts",
            "3",
            "--output",
            "results/test.json",
        ],
    )

    args = cli.parse_args()

    assert args.model == "test-model"
    assert args.all is True
    assert args.evaluator == "contains"
    assert args.max_attempts == 3
    assert args.output == "results/test.json"


def test_build_exact_evaluator():
    evaluator = cli.build_evaluator(
        "exact"
    )

    assert (
        evaluator.__class__.__name__
        == "ExactMatchEvaluator"
    )


def test_build_contains_evaluator():
    evaluator = cli.build_evaluator(
        "contains"
    )

    assert (
        evaluator.__class__.__name__
        == "ContainsMatchEvaluator"
    )


def test_invalid_evaluator():
    with pytest.raises(
        ValueError,
        match="Unsupported evaluator",
    ):
        cli.build_evaluator(
            "invalid"
        )


def test_build_attacks():
    attacks = cli.build_attacks(
        "datasets/attacks/"
        "prompt_injection.json"
    )

    assert len(attacks) == 5

    for attack in attacks:
        assert (
            attack.category
            == "prompt_injection"
        )

        assert attack.name
        assert attack.prompt
        assert attack.expected


def test_build_report_contains_adaptive_metrics():
    metrics = {
        "total_attacks": 1,
        "original_successes": 0,
        "adaptive_successes": 1,
        "original_asr": 0.0,
        "adaptive_asr": 1.0,
        "adaptive_gain": 1.0,
        "average_attempts": 2.0,
        "average_attempts_to_success": 2.0,
        "strategy_successes": {
            "roleplay": 1,
        },
        "category_metrics": {
            "prompt_injection": {
                "total_attacks": 1,
                "original_successes": 0,
                "adaptive_successes": 1,
                "original_asr": 0.0,
                "adaptive_asr": 1.0,
                "adaptive_gain": 1.0,
            }
        },
    }

    report = cli.build_report(
        model_name="test-model",
        evaluator_name="exact",
        max_attempts=5,
        attacks=[object()],
        results=[],
        metrics=metrics,
    )

    assert report["model"] == "test-model"
    assert report["evaluator"] == "exact"
    assert report["adaptive"] is True
    assert report["max_attempts"] == 5
    assert report["total_attacks"] == 1

    assert (
        report["metrics"]["adaptive_gain"]
        == 1.0
    )

    assert (
        report["metrics"]
        ["category_metrics"]
        ["prompt_injection"]
        ["adaptive_gain"]
        == 1.0
    )


def test_save_report(tmp_path):
    report = {
        "model": "test-model",
        "adaptive": True,
        "metrics": {
            "adaptive_asr": 0.5,
        },
    }

    output = (
        tmp_path
        / "reports"
        / "adaptive.json"
    )

    cli.save_report(
        report,
        str(output),
    )

    assert output.exists()

    import json

    with output.open(
        "r",
        encoding="utf-8",
    ) as file:
        loaded = json.load(file)

    assert loaded == report


def test_adaptive_report_contains_security_risk():
    attack = SimpleNamespace(
        name="instruction_override",
        category="prompt_injection",
    )

    result = AdaptiveAttackResult(
        attack="instruction_override",
        category="prompt_injection",
        successful=True,
        attempts_used=1,
        successful_attempt=1,
        successful_strategy="original",
        final_score=1.0,
        final_response="AEGIS_TEST_OVERRIDE",
        attempt_history=[],
    )

    report = cli.build_report(
        model_name="test-model",
        evaluator_name="exact",
        max_attempts=5,
        attacks=[attack],
        results=[result],
        metrics={},
    )

    assert len(report["results"]) == 1

    security_risk = report[
        "results"
    ][0]["security_risk"]

    assert security_risk is not None

    assert (
        security_risk["taxonomy"]
        == "OWASP LLM Top 10"
    )

    assert (
        security_risk["risk_id"]
        == "LLM01"
    )

    assert (
        security_risk["name"]
        == "Prompt Injection"
    )

    assert "description" in security_risk


def test_adaptive_report_unknown_security_risk():
    attack = SimpleNamespace(
        name="custom_attack",
        category="custom_category",
    )

    result = AdaptiveAttackResult(
        attack="custom_attack",
        category="custom_category",
        successful=False,
        attempts_used=1,
        successful_attempt=None,
        successful_strategy=None,
        final_score=0.0,
        final_response="REFUSED",
        attempt_history=[],
    )

    report = cli.build_report(
        model_name="test-model",
        evaluator_name="exact",
        max_attempts=5,
        attacks=[attack],
        results=[result],
        metrics={},
    )

    assert (
        report["results"][0][
            "security_risk"
        ]
        is None
    )


def test_adaptive_report_contains_run_metadata():
    report = cli.build_report(
        model_name="test-model",
        evaluator_name="contains",
        max_attempts=7,
        attacks=[],
        results=[],
        metrics={},
    )

    metadata = report[
        "run_metadata"
    ]

    assert metadata["run_id"]
    assert metadata["timestamp"]

    assert (
        metadata["benchmark_type"]
        == "adaptive"
    )

    assert (
        metadata["model"]
        == "test-model"
    )

    assert (
        metadata["evaluator"]
        == "contains"
    )

    assert (
        metadata["configuration"][
            "max_attempts"
        ]
        == 7
    )

    assert (
        metadata["configuration"][
            "total_attacks"
        ]
        == 0
    )
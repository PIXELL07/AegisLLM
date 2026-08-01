import json

import pytest

from scripts.evaluate_results import (
    build_evaluator,
    calculate_summary,
    load_report,
)
from aegis.evaluators.contains import ContainsMatchEvaluator
from aegis.evaluators.evaluator import ExactMatchEvaluator


def test_load_report(tmp_path):
    report = {
        "model": "test-model",
        "results": [
            {
                "attack": "test_attack",
                "category": "prompt_injection",
                "expected": "SUCCESS",
                "response": "SUCCESS",
            }
        ],
    }

    path = tmp_path / "report.json"

    with path.open("w", encoding="utf-8") as file:
        json.dump(report, file)

    loaded = load_report(str(path))

    assert loaded == report


def test_load_report_missing_file(tmp_path):
    path = tmp_path / "missing.json"

    with pytest.raises(
        FileNotFoundError,
        match="Benchmark report not found",
    ):
        load_report(str(path))


def test_load_report_missing_results(tmp_path):
    path = tmp_path / "report.json"

    with path.open("w", encoding="utf-8") as file:
        json.dump(
            {"model": "test-model"},
            file,
        )

    with pytest.raises(
        ValueError,
        match="missing results",
    ):
        load_report(str(path))


def test_build_exact_evaluator():
    evaluator = build_evaluator("exact")

    assert isinstance(
        evaluator,
        ExactMatchEvaluator,
    )


def test_build_contains_evaluator():
    evaluator = build_evaluator("contains")

    assert isinstance(
        evaluator,
        ContainsMatchEvaluator,
    )


def test_invalid_evaluator():
    with pytest.raises(
        ValueError,
        match="Unsupported evaluator",
    ):
        build_evaluator("invalid")


def test_calculate_summary():
    results = [
        {
            "category": "prompt_injection",
            "successful": True,
        },
        {
            "category": "prompt_injection",
            "successful": False,
        },
        {
            "category": "encoding",
            "successful": True,
        },
    ]

    summary = calculate_summary(results)

    assert summary["total"] == 3
    assert summary["successful"] == 2

    assert summary["success_rate"] == pytest.approx(
        2 / 3
    )

    assert (
        summary["categories"]["prompt_injection"]["total"]
        == 2
    )

    assert (
        summary["categories"]["prompt_injection"]["successful"]
        == 1
    )

    assert (
        summary["categories"]["encoding"]["total"]
        == 1
    )

    assert (
        summary["categories"]["encoding"]["successful"]
        == 1
    )


def test_calculate_empty_summary():
    summary = calculate_summary([])

    assert summary["total"] == 0
    assert summary["successful"] == 0
    assert summary["success_rate"] == 0.0
    assert summary["categories"] == {}
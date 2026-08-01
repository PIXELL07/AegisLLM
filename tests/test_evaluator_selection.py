import pytest

from aegis.evaluators.contains import ContainsMatchEvaluator
from aegis.evaluators.evaluator import ExactMatchEvaluator
from scripts.run_benchmark import build_evaluator


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
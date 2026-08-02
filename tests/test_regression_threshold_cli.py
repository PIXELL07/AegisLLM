import sys

import pytest

from scripts.compare_runs import (
    non_negative_float,
    parse_args,
)


def test_non_negative_float():
    assert non_negative_float("0") == 0.0
    assert non_negative_float("0.05") == 0.05
    assert non_negative_float("1") == 1.0


def test_negative_threshold_rejected():
    with pytest.raises(
        Exception,
        match="Threshold cannot be negative",
    ):
        non_negative_float("-0.01")


def test_invalid_threshold_rejected():
    with pytest.raises(
        Exception,
        match="Invalid threshold value",
    ):
        non_negative_float("invalid")


def test_default_threshold_arguments(monkeypatch):
    monkeypatch.setattr(
        sys,
        "argv",
        [
            "compare_runs.py",
            "baseline.json",
            "current.json",
        ],
    )

    args = parse_args()

    assert args.baseline == "baseline.json"
    assert args.current == "current.json"

    assert args.asr_threshold == 0.0
    assert args.risk_threshold == 0.0
    assert args.category_threshold == 0.0


def test_custom_threshold_arguments(monkeypatch):
    monkeypatch.setattr(
        sys,
        "argv",
        [
            "compare_runs.py",
            "baseline.json",
            "current.json",
            "--asr-threshold",
            "0.05",
            "--risk-threshold",
            "0.10",
            "--category-threshold",
            "0.15",
        ],
    )

    args = parse_args()

    assert args.asr_threshold == 0.05
    assert args.risk_threshold == 0.10
    assert args.category_threshold == 0.15
import json

import pytest

from scripts.compare_runs import (
    format_change,
    load_report,
)


def test_load_report(tmp_path):
    report = {
        "model": "test-model",
        "attack_success_rate": 0.4,
        "risk_score": 0.5,
        "results": [],
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
            {
                "model": "test-model",
                "attack_success_rate": 0.5,
            },
            file,
        )

    with pytest.raises(
        ValueError,
        match="missing results",
    ):
        load_report(str(path))


def test_load_report_results_not_list(tmp_path):
    path = tmp_path / "report.json"

    with path.open("w", encoding="utf-8") as file:
        json.dump(
            {
                "model": "test-model",
                "results": {},
            },
            file,
        )

    with pytest.raises(
        ValueError,
        match="results must be a list",
    ):
        load_report(str(path))


def test_load_report_not_object(tmp_path):
    path = tmp_path / "report.json"

    with path.open("w", encoding="utf-8") as file:
        json.dump(
            [],
            file,
        )

    with pytest.raises(
        ValueError,
        match="expected JSON object",
    ):
        load_report(str(path))


def test_format_positive_change():
    assert format_change(0.2) == "+20.00%"


def test_format_negative_change():
    assert format_change(-0.15) == "-15.00%"


def test_format_zero_change():
    assert format_change(0.0) == "0.00%"
import json
from types import SimpleNamespace

from aegis.benchmark.report import build_report, save_report


def test_build_report():
    attacks = [
        SimpleNamespace(
            name="instruction_override",
            category="prompt_injection",
            expected="AEGIS_TEST_OVERRIDE",
        ),
        SimpleNamespace(
            name="system_override",
            category="prompt_injection",
            expected="SYSTEM_OVERRIDE_SUCCESS",
        ),
    ]

    results = [
        SimpleNamespace(
            successful=True,
            score=1.0,
            latency_ms=120.5,
            response="AEGIS_TEST_OVERRIDE",
        ),
        SimpleNamespace(
            successful=False,
            score=0.0,
            latency_ms=95.2,
            response="REFUSED",
        ),
    ]

    report = build_report(
        model_name="test-model",
        attacks=attacks,
        results=results,
        success_rate=0.5,
    )

    assert report["model"] == "test-model"
    assert report["total_attacks"] == 2
    assert report["successful_attacks"] == 1
    assert report["attack_success_rate"] == 0.5

    assert len(report["results"]) == 2

    first_result = report["results"][0]

    assert first_result["attack"] == "instruction_override"
    assert first_result["category"] == "prompt_injection"
    assert first_result["expected"] == "AEGIS_TEST_OVERRIDE"
    assert first_result["successful"] is True
    assert first_result["score"] == 1.0
    assert first_result["latency_ms"] == 120.5
    assert first_result["response"] == "AEGIS_TEST_OVERRIDE"

    second_result = report["results"][1]

    assert second_result["attack"] == "system_override"
    assert second_result["category"] == "prompt_injection"
    assert second_result["expected"] == "SYSTEM_OVERRIDE_SUCCESS"
    assert second_result["successful"] is False
    assert second_result["score"] == 0.0
    assert second_result["latency_ms"] == 95.2
    assert second_result["response"] == "REFUSED"


def test_save_report(tmp_path):
    report = {
        "model": "test-model",
        "total_attacks": 1,
        "successful_attacks": 1,
        "attack_success_rate": 1.0,
        "results": [
            {
                "attack": "instruction_override",
                "category": "prompt_injection",
                "expected": "AEGIS_TEST_OVERRIDE",
                "successful": True,
                "score": 1.0,
                "latency_ms": 100.0,
                "response": "AEGIS_TEST_OVERRIDE",
            }
        ],
    }

    output_file = tmp_path / "results" / "report.json"

    save_report(
        report,
        str(output_file),
    )

    assert output_file.exists()

    with output_file.open(
        "r",
        encoding="utf-8",
    ) as file:
        saved_report = json.load(file)

    assert saved_report == report
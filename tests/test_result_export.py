import json
from types import SimpleNamespace

from aegis.benchmark.report import build_report, save_report


def test_build_report():
    attacks = [
        SimpleNamespace(
            name="instruction_override",
            category="prompt_injection",
        ),
        SimpleNamespace(
            name="system_override",
            category="prompt_injection",
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

    # First attack
    assert (
        report["results"][0]["attack"]
        == "instruction_override"
    )

    assert (
        report["results"][0]["category"]
        == "prompt_injection"
    )

    assert (
        report["results"][0]["successful"]
        is True
    )

    assert (
        report["results"][0]["score"]
        == 1.0
    )

    assert (
        report["results"][0]["response"]
        == "AEGIS_TEST_OVERRIDE"
    )

    # OWASP security taxonomy
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

    # Second attack
    assert (
        report["results"][1]["successful"]
        is False
    )

    assert (
        report["results"][1][
            "security_risk"
        ]["risk_id"]
        == "LLM01"
    )


def test_save_report(tmp_path):
    report = {
        "model": "test-model",
        "total_attacks": 1,
        "successful_attacks": 1,
        "attack_success_rate": 1.0,
        "results": [],
    }

    output_file = (
        tmp_path
        / "results"
        / "report.json"
    )

    save_report(
        report,
        str(output_file),
    )

    assert output_file.exists()

    with output_file.open(
        "r",
        encoding="utf-8",
    ) as file:
        saved_report = json.load(
            file
        )

    assert saved_report == report


def test_build_report_unknown_taxonomy():
    attacks = [
        SimpleNamespace(
            name="custom_attack",
            category="custom_category",
        )
    ]

    results = [
        SimpleNamespace(
            successful=False,
            score=0.0,
            latency_ms=10.0,
            response="REFUSED",
        )
    ]

    report = build_report(
        model_name="test-model",
        attacks=attacks,
        results=results,
        success_rate=0.0,
    )

    assert (
        report["results"][0][
            "security_risk"
        ]
        is None
    )
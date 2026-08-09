import json
from aegis.dashboard.templates import build_dashboard_html

from aegis.dashboard.builder import (
    extract_summary,
    load_report,
    save_html,
)


def test_load_report(
    tmp_path,
):
    report = {
        "model": "test-model",
        "attack_success_rate": 0.4,
    }

    path = (
        tmp_path
        / "report.json"
    )

    path.write_text(
        json.dumps(report),
        encoding="utf-8",
    )

    loaded = load_report(
        str(path)
    )

    assert loaded == report


def test_extract_summary():
    report = {
        "model": "test-model",
        "adaptive": True,
        "metrics": {
            "adaptive_asr": 0.55,
            "total_attacks": 10,
        },
        "results": [],
    }

    summary = extract_summary(
        report
    )

    assert (
        summary["model"]
        == "test-model"
    )

    assert (
        summary["adaptive"]
        is True
    )

    assert (
        summary[
            "attack_success_rate"
        ]
        == 0.55
    )

    assert (
        summary[
            "total_attacks"
        ]
        == 10
    )


def test_save_html(
    tmp_path,
):
    output = (
        tmp_path
        / "dashboard.html"
    )

    save_html(
        "<html></html>",
        str(output),
    )

    assert output.exists()

    assert (
        output.read_text(
            encoding="utf-8"
        )
        == "<html></html>"
    )

def test_category_summary():

    report = {
        "model": "test-model",
        "results": [
            {
                "category": "prompt_injection",
                "successful": True,
            },
            {
                "category": "prompt_injection",
                "successful": False,
            },
            {
                "category": "jailbreak",
                "successful": True,
            },
        ],
    }

    summary = extract_summary(
        report,
    )

    assert (
        summary["categories"][
            "prompt_injection"
        ]["total"]
        == 2
    )

    assert (
        summary["categories"][
            "prompt_injection"
        ]["successful"]
        == 1
    )

    assert (
        summary["categories"][
            "prompt_injection"
        ]["attack_success_rate"]
        == 0.5
    )

    assert (
        summary["categories"][
            "jailbreak"
        ]["attack_success_rate"]
        == 1.0
    )    

def test_dashboard_contains_attack_results():
    report = {
        "model": "test-model",
        "results": [
            {
                "category": "prompt_injection",
                "successful": True,
            },
            {
                "category": "jailbreak",
                "successful": False,
            },
        ],
    }

    summary = extract_summary(report)

    html = build_dashboard_html(summary)

    assert "Attack Results" in html
    assert "prompt_injection" in html
    assert "jailbreak" in html
    assert "Yes" in html
    assert "No" in html

import json

from aegis.dashboard.builder import (
    extract_summary,
    load_report,
    save_html,
)

from aegis.dashboard.charts import (
    build_category_chart_data,
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
        "risk_score": 0.75,
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
        summary["attack_success_rate"]
        == 0.55
    )

    assert (
        summary["total_attacks"]
        == 10
    )

    assert (
        summary["risk_score"]
        == 0.75
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


def test_build_category_chart_data():
    summary = {
        "categories": {
            "prompt_injection": {
                "total": 5,
                "successful": 1,
                "attack_success_rate": 0.2,
            },
            "jailbreak": {
                "total": 4,
                "successful": 2,
                "attack_success_rate": 0.5,
            },
        }
    }

    chart_data = build_category_chart_data(
        summary
    )

    assert chart_data == [
        {
            "category": "prompt_injection",
            "attack_success_rate": 0.2,
        },
        {
            "category": "jailbreak",
            "attack_success_rate": 0.5,
        },
    ]
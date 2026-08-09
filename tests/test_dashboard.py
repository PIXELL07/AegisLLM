import json

from aegis.dashboard.builder import (
    extract_summary,
    load_report,
    save_html,
)

from aegis.dashboard.charts import (
    build_category_chart_data,
    get_risk_level,
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
        "total_attacks": 10,
        "successful_attacks": 4,
        "metrics": {
            "adaptive_asr": 0.55,
            "total_attacks": 10,
        },
        "results": [
            {
                "category": "prompt_injection",
                "successful": True,
                "latency_ms": 100,
            },
            {
                "category": "prompt_injection",
                "successful": False,
                "latency_ms": 200,
            },
        ],
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
        summary["successful_attacks"]
        == 4
    )

    assert (
        summary["average_latency_ms"]
        == 150
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


def test_get_risk_level():

    assert (
        get_risk_level(0.2)
        == "LOW"
    )

    assert (
        get_risk_level(0.5)
        == "MEDIUM"
    )

    assert (
        get_risk_level(0.8)
        == "HIGH"
    )
def test_build_score_chart_data():
    summary = {
        "results": [
            {
                "attack": "instruction_override",
                "score": 1.0,
            },
            {
                "attack": "system_override",
                "score": 0.0,
            },
        ]
    }

    from aegis.dashboard.charts import (
        build_score_chart_data,
    )

    score_data = build_score_chart_data(
        summary
    )

    assert score_data == [
        {
            "attack": "instruction_override",
            "score": 1.0,
        },
        {
            "attack": "system_override",
            "score": 0.0,
        },
    ]    

def test_dashboard_attack_results_table():
    from aegis.dashboard.templates import (
        build_dashboard_html,
    )

    summary = {
        "model": "test-model",
        "adaptive": False,
        "total_attacks": 1,
        "successful_attacks": 1,
        "attack_success_rate": 1.0,
        "average_latency_ms": 100.0,
        "risk_score": 0.5,
        "results": [
            {
                "attack": "test_attack",
                "category": "prompt_injection",
                "successful": True,
                "score": 1.0,
                "latency_ms": 100.0,
            }
        ],
        "categories": {
            "prompt_injection": {
                "total": 1,
                "successful": 1,
                "attack_success_rate": 1.0,
            }
        },
    }

    html = build_dashboard_html(
        summary,
    )

    assert "test_attack" in html
    assert "prompt_injection" in html
    assert "1.00" in html
    assert "100.00 ms" in html
    assert "Yes" in html

def test_dashboard_attack_response():
    from aegis.dashboard.templates import (
        build_dashboard_html,
    )

    summary = {
        "model": "test-model",
        "adaptive": False,
        "total_attacks": 1,
        "successful_attacks": 1,
        "attack_success_rate": 1.0,
        "average_latency_ms": 100.0,
        "risk_score": 0.5,
        "results": [
            {
                "attack": "test_attack",
                "category": "prompt_injection",
                "successful": True,
                "score": 1.0,
                "latency_ms": 100.0,
                "response": "TEST_RESPONSE",
            }
        ],
        "categories": {
            "prompt_injection": {
                "total": 1,
                "successful": 1,
                "attack_success_rate": 1.0,
            }
        },
    }

    html = build_dashboard_html(summary)

    assert "Response" in html
    assert "TEST_RESPONSE" in html

def test_dashboard_summary_section():
    from aegis.dashboard.templates import (
        build_dashboard_html,
    )

    summary = {
        "model": "test-model",
        "adaptive": False,
        "total_attacks": 5,
        "successful_attacks": 1,
        "attack_success_rate": 0.2,
        "average_latency_ms": 500.0,
        "risk_score": 0.5,
        "results": [],
        "categories": {},
    }

    html = build_dashboard_html(summary)

    assert "Dashboard Summary" in html
    assert "test-model" in html
    assert "Total Attacks" in html
    assert "Successful Attacks" in html
    assert "20.00%" in html
    assert "500.00 ms" in html
    assert "MEDIUM" in html

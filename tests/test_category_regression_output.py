from scripts.compare_runs import print_comparison


def test_prints_category_changes(capsys):
    baseline = {
        "model": "baseline-model",
    }

    current = {
        "model": "current-model",
    }

    comparison = {
        "baseline_asr": 0.4,
        "current_asr": 0.6,
        "asr_change": 0.2,
        "asr_threshold": 0.05,
        "asr_regression": True,
        "baseline_risk": 0.45,
        "current_risk": 0.65,
        "risk_change": 0.2,
        "risk_threshold": 0.05,
        "risk_regression": True,
        "category_threshold": 0.1,
        "category_comparison": {
            "prompt_injection": {
                "baseline_asr": 0.5,
                "current_asr": 1.0,
                "change": 0.5,
                "regression": True,
                "improvement": False,
            },
            "encoding": {
                "baseline_asr": 1.0,
                "current_asr": 0.0,
                "change": -1.0,
                "regression": False,
                "improvement": True,
            },
        },
        "category_regressions": [
            "prompt_injection",
        ],
        "category_improvements": [
            "encoding",
        ],
        "attack_regressions": [],
        "attack_improvements": [],
        "regression_detected": True,
    }

    print_comparison(
        baseline,
        current,
        comparison,
    )

    output = capsys.readouterr().out

    assert "Regression Thresholds" in output
    assert "ASR Threshold      : 5.00%" in output
    assert "Risk Threshold     : 5.00%" in output
    assert "Category Threshold : 10.00%" in output

    assert "Category Changes" in output
    assert "prompt_injection" in output
    assert "encoding" in output

    assert (
        "[REGRESSION] prompt_injection: "
        "50.00% -> 100.00% (+50.00%)"
        in output
    )

    assert (
        "[IMPROVEMENT] encoding: "
        "100.00% -> 0.00% (-100.00%)"
        in output
    )


def test_prints_no_category_regressions(capsys):
    baseline = {
        "model": "test-model",
    }

    current = {
        "model": "test-model",
    }

    comparison = {
        "baseline_asr": 0.5,
        "current_asr": 0.5,
        "asr_change": 0.0,
        "asr_threshold": 0.0,
        "asr_regression": False,
        "baseline_risk": 0.5,
        "current_risk": 0.5,
        "risk_change": 0.0,
        "risk_threshold": 0.0,
        "risk_regression": False,
        "category_threshold": 0.0,
        "category_comparison": {
            "prompt_injection": {
                "baseline_asr": 0.5,
                "current_asr": 0.5,
                "change": 0.0,
                "regression": False,
                "improvement": False,
            },
        },
        "category_regressions": [],
        "category_improvements": [],
        "attack_regressions": [],
        "attack_improvements": [],
        "regression_detected": False,
    }

    print_comparison(
        baseline,
        current,
        comparison,
    )

    output = capsys.readouterr().out

    assert "Category Regressions" in output
    assert "NO SECURITY REGRESSION DETECTED" in output


def test_empty_category_comparison(capsys):
    baseline = {
        "model": "test-model",
    }

    current = {
        "model": "test-model",
    }

    comparison = {
        "baseline_asr": 0.0,
        "current_asr": 0.0,
        "asr_change": 0.0,
        "asr_threshold": 0.0,
        "asr_regression": False,
        "baseline_risk": 0.0,
        "current_risk": 0.0,
        "risk_change": 0.0,
        "risk_threshold": 0.0,
        "risk_regression": False,
        "category_threshold": 0.0,
        "category_comparison": {},
        "category_regressions": [],
        "category_improvements": [],
        "attack_regressions": [],
        "attack_improvements": [],
        "regression_detected": False,
    }

    print_comparison(
        baseline,
        current,
        comparison,
    )

    output = capsys.readouterr().out

    assert "No category data available." in output
    assert "NO SECURITY REGRESSION DETECTED" in output
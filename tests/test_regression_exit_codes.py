import json

from scripts.compare_runs import run_comparison


def write_report(
    path,
    attack_success_rate,
    risk_score,
    successful,
):
    report = {
        "model": "test-model",
        "attack_success_rate": attack_success_rate,
        "risk_score": risk_score,
        "results": [
            {
                "attack": "test_attack",
                "category": "prompt_injection",
                "successful": successful,
            }
        ],
    }

    with path.open(
        "w",
        encoding="utf-8",
    ) as file:
        json.dump(
            report,
            file,
        )


def test_regression_returns_exit_code_one(
    tmp_path,
):
    baseline = tmp_path / "baseline.json"
    current = tmp_path / "current.json"

    write_report(
        baseline,
        attack_success_rate=0.0,
        risk_score=0.0,
        successful=False,
    )

    write_report(
        current,
        attack_success_rate=1.0,
        risk_score=1.0,
        successful=True,
    )

    exit_code = run_comparison(
        str(baseline),
        str(current),
    )

    assert exit_code == 1


def test_no_regression_returns_exit_code_zero(
    tmp_path,
):
    baseline = tmp_path / "baseline.json"
    current = tmp_path / "current.json"

    write_report(
        baseline,
        attack_success_rate=1.0,
        risk_score=1.0,
        successful=True,
    )

    write_report(
        current,
        attack_success_rate=0.0,
        risk_score=0.0,
        successful=False,
    )

    exit_code = run_comparison(
        str(baseline),
        str(current),
    )

    assert exit_code == 0


def test_unchanged_results_return_exit_code_zero(
    tmp_path,
):
    baseline = tmp_path / "baseline.json"
    current = tmp_path / "current.json"

    write_report(
        baseline,
        attack_success_rate=0.5,
        risk_score=0.5,
        successful=False,
    )

    write_report(
        current,
        attack_success_rate=0.5,
        risk_score=0.5,
        successful=False,
    )

    exit_code = run_comparison(
        str(baseline),
        str(current),
    )

    assert exit_code == 0
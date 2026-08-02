import json

from scripts.compare_runs import run_comparison


def write_report(
    path,
    asr,
    risk,
    successful,
):
    report = {
        "model": "test-model",
        "attack_success_rate": asr,
        "risk_score": risk,
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


def test_run_comparison_saves_json_report(
    tmp_path,
):
    baseline = tmp_path / "baseline.json"
    current = tmp_path / "current.json"

    output = (
        tmp_path
        / "reports"
        / "regression.json"
    )

    write_report(
        baseline,
        asr=0.0,
        risk=0.0,
        successful=False,
    )

    write_report(
        current,
        asr=1.0,
        risk=1.0,
        successful=True,
    )

    exit_code = run_comparison(
        str(baseline),
        str(current),
        output=str(output),
    )

    assert exit_code == 1
    assert output.exists()

    with output.open(
        "r",
        encoding="utf-8",
    ) as file:
        report = json.load(file)

    assert report[
        "regression_detected"
    ] is True

    assert report[
        "baseline_model"
    ] == "test-model"

    assert report[
        "current_model"
    ] == "test-model"

    assert report[
        "attack_regressions"
    ] == [
        "test_attack"
    ]


def test_json_report_contains_thresholds(
    tmp_path,
):
    baseline = tmp_path / "baseline.json"
    current = tmp_path / "current.json"
    output = tmp_path / "regression.json"

    write_report(
        baseline,
        asr=0.40,
        risk=0.40,
        successful=False,
    )

    write_report(
        current,
        asr=0.43,
        risk=0.44,
        successful=False,
    )

    exit_code = run_comparison(
        str(baseline),
        str(current),
        asr_threshold=0.05,
        risk_threshold=0.05,
        category_threshold=0.05,
        output=str(output),
    )

    assert exit_code == 0

    with output.open(
        "r",
        encoding="utf-8",
    ) as file:
        report = json.load(file)

    assert report["thresholds"] == {
        "asr": 0.05,
        "risk": 0.05,
        "category": 0.05,
    }

    assert report[
        "regression_detected"
    ] is False


def test_no_output_does_not_create_report(
    tmp_path,
):
    baseline = tmp_path / "baseline.json"
    current = tmp_path / "current.json"

    write_report(
        baseline,
        asr=0.5,
        risk=0.5,
        successful=False,
    )

    write_report(
        current,
        asr=0.5,
        risk=0.5,
        successful=False,
    )

    exit_code = run_comparison(
        str(baseline),
        str(current),
    )

    assert exit_code == 0

    assert not (
        tmp_path / "regression.json"
    ).exists()
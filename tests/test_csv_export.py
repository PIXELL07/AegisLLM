import csv

from aegis.benchmark.csv_report import save_csv_report


class MockAttackResult:
    def __init__(
        self,
        successful: bool,
        score: float,
        latency_ms: float,
        response: str,
    ):
        self.successful = successful
        self.score = score
        self.latency_ms = latency_ms
        self.response = response


def test_save_csv_report(tmp_path):
    results = [
        {
            "attack": "instruction_override",
            "category": "prompt_injection",
            "result": MockAttackResult(
                successful=True,
                score=1.0,
                latency_ms=250.5,
                response="AEGIS_TEST_OVERRIDE",
            ),
        },
        {
            "attack": "role_reassignment",
            "category": "prompt_injection",
            "result": MockAttackResult(
                successful=False,
                score=0.0,
                latency_ms=310.2,
                response="REFUSED",
            ),
        },
    ]

    output_file = tmp_path / "benchmark.csv"

    save_csv_report(
        results=results,
        output_path=str(output_file),
    )

    assert output_file.exists()

    with output_file.open(
        "r",
        encoding="utf-8",
        newline="",
    ) as file:
        rows = list(csv.DictReader(file))

    assert len(rows) == 2

    assert rows[0]["attack"] == "instruction_override"
    assert rows[0]["category"] == "prompt_injection"
    assert rows[0]["successful"] == "True"
    assert rows[0]["score"] == "1.0"
    assert rows[0]["latency_ms"] == "250.5"
    assert rows[0]["response"] == "AEGIS_TEST_OVERRIDE"

    assert rows[1]["attack"] == "role_reassignment"
    assert rows[1]["category"] == "prompt_injection"
    assert rows[1]["successful"] == "False"
    assert rows[1]["score"] == "0.0"
    assert rows[1]["latency_ms"] == "310.2"
    assert rows[1]["response"] == "REFUSED"


def test_save_csv_report_creates_parent_directory(tmp_path):
    results = [
        {
            "attack": "system_override",
            "category": "prompt_injection",
            "result": MockAttackResult(
                successful=True,
                score=1.0,
                latency_ms=200.0,
                response="SYSTEM_OVERRIDE_SUCCESS",
            ),
        }
    ]

    output_file = (
        tmp_path
        / "nested"
        / "results"
        / "benchmark.csv"
    )

    save_csv_report(
        results=results,
        output_path=str(output_file),
    )

    assert output_file.exists()

    with output_file.open(
        "r",
        encoding="utf-8",
        newline="",
    ) as file:
        rows = list(csv.DictReader(file))

    assert len(rows) == 1
    assert rows[0]["attack"] == "system_override"
    assert rows[0]["category"] == "prompt_injection"
    assert rows[0]["successful"] == "True"
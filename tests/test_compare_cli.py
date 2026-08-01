import json
import subprocess
import sys


def test_compare_models_cli(tmp_path):
    llama_report = {
        "model": "llama3.2:3b",
        "total_attacks": 5,
        "successful_attacks": 1,
        "attack_success_rate": 0.2,
        "results": [],
    }

    qwen_report = {
        "model": "qwen2.5:1.5b",
        "total_attacks": 5,
        "successful_attacks": 5,
        "attack_success_rate": 1.0,
        "results": [],
    }

    llama_path = tmp_path / "llama.json"
    qwen_path = tmp_path / "qwen.json"

    llama_path.write_text(
        json.dumps(llama_report),
        encoding="utf-8",
    )

    qwen_path.write_text(
        json.dumps(qwen_report),
        encoding="utf-8",
    )

    process = subprocess.run(
        [
            sys.executable,
            "scripts/compare_models.py",
            str(llama_path),
            str(qwen_path),
        ],
        capture_output=True,
        text=True,
    )

    assert process.returncode == 0

    assert "AegisLLM Model Comparison" in process.stdout
    assert "llama3.2:3b" in process.stdout
    assert "qwen2.5:1.5b" in process.stdout
    assert "20.00%" in process.stdout
    assert "100.00%" in process.stdout
    assert "Safest Model: llama3.2:3b" in process.stdout


def test_compare_models_missing_report():
    process = subprocess.run(
        [
            sys.executable,
            "scripts/compare_models.py",
            "does-not-exist.json",
        ],
        capture_output=True,
        text=True,
    )

    assert process.returncode != 0
    assert "Benchmark report not found" in process.stderr
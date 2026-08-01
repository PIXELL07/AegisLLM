from aegis.benchmark.comparison import compare_reports, safest_model


def test_compare_reports():
    reports = [
        {
            "model": "qwen2.5:1.5b",
            "total_attacks": 5,
            "successful_attacks": 5,
            "attack_success_rate": 1.0,
        },
        {
            "model": "llama3.2:3b",
            "total_attacks": 5,
            "successful_attacks": 3,
            "attack_success_rate": 0.6,
        },
    ]

    comparison = compare_reports(reports)

    assert len(comparison) == 2
    assert comparison[0]["model"] == "llama3.2:3b"
    assert comparison[1]["model"] == "qwen2.5:1.5b"


def test_safest_model():
    reports = [
        {
            "model": "qwen2.5:1.5b",
            "total_attacks": 5,
            "successful_attacks": 5,
            "attack_success_rate": 1.0,
        },
        {
            "model": "llama3.2:3b",
            "total_attacks": 5,
            "successful_attacks": 3,
            "attack_success_rate": 0.6,
        },
    ]

    assert safest_model(reports) == "llama3.2:3b"


def test_safest_model_empty():
    assert safest_model([]) is None
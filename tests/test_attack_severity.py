from aegis.benchmark.risk import Severity
from scripts.run_benchmark import build_attacks


def test_prompt_injection_severity():
    attacks = build_attacks(
        "datasets/attacks/prompt_injection.json"
    )

    assert len(attacks) == 5

    assert all(
        attack.severity == Severity.HIGH
        for attack in attacks
    )


def test_jailbreak_severity():
    attacks = build_attacks(
        "datasets/attacks/jailbreak.json"
    )

    assert len(attacks) == 5

    assert all(
        attack.severity == Severity.CRITICAL
        for attack in attacks
    )


def test_encoding_severity():
    attacks = build_attacks(
        "datasets/attacks/encoding.json"
    )

    assert len(attacks) == 5

    assert all(
        attack.severity == Severity.MEDIUM
        for attack in attacks
    )
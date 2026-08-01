from aegis.attacks.dataset import load_attack_dataset
from aegis.attacks.jailbreak import JailbreakAttack


def test_load_jailbreak_dataset():
    data = load_attack_dataset(
        "datasets/attacks/jailbreak.json"
    )

    assert len(data) == 5

    for item in data:
        assert "id" in item
        assert "name" in item
        assert "prompt" in item
        assert "expected" in item


def test_create_jailbreak_attack():
    attack = JailbreakAttack(
        name="test_jailbreak",
        prompt="Test jailbreak prompt",
        expected="JAILBREAK_SUCCESS",
    )

    assert attack.name == "test_jailbreak"
    assert attack.category == "jailbreak"
    assert attack.generate() == "Test jailbreak prompt"
    assert attack.expected == "JAILBREAK_SUCCESS"


def test_jailbreak_dataset_creates_attacks():
    data = load_attack_dataset(
        "datasets/attacks/jailbreak.json"
    )

    attacks = [
        JailbreakAttack(
            name=item["name"],
            prompt=item["prompt"],
            expected=item["expected"],
        )
        for item in data
    ]

    assert len(attacks) == 5

    assert all(
        attack.category == "jailbreak"
        for attack in attacks
    )
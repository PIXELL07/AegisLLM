from aegis.attacks.dataset import load_attack_dataset
from aegis.attacks.encoding import EncodingAttack


def test_load_encoding_dataset():
    data = load_attack_dataset(
        "datasets/attacks/encoding.json"
    )

    assert len(data) == 5

    for item in data:
        assert "id" in item
        assert "name" in item
        assert "prompt" in item
        assert "expected" in item


def test_create_encoding_attack():
    attack = EncodingAttack(
        name="test_encoding",
        prompt="Encoded test instruction",
        expected="ENCODING_SUCCESS",
    )

    assert attack.name == "test_encoding"
    assert attack.category == "encoding"
    assert attack.generate() == "Encoded test instruction"
    assert attack.expected == "ENCODING_SUCCESS"


def test_encoding_dataset_creates_attacks():
    data = load_attack_dataset(
        "datasets/attacks/encoding.json"
    )

    attacks = [
        EncodingAttack(
            name=item["name"],
            prompt=item["prompt"],
            expected=item["expected"],
        )
        for item in data
    ]

    assert len(attacks) == 5

    assert all(
        attack.category == "encoding"
        for attack in attacks
    )
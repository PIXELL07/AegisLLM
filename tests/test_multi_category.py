from argparse import Namespace

from scripts.run_benchmark import (
    ALL_DATASETS,
    build_attacks,
    load_attacks,
)


def test_all_datasets_configured():
    assert len(ALL_DATASETS) == 3

    assert "datasets/attacks/prompt_injection.json" in ALL_DATASETS
    assert "datasets/attacks/jailbreak.json" in ALL_DATASETS
    assert "datasets/attacks/encoding.json" in ALL_DATASETS


def test_build_attacks_prompt_injection():
    attacks = build_attacks(
        "datasets/attacks/prompt_injection.json"
    )

    assert len(attacks) == 5
    assert all(
        attack.category == "prompt_injection"
        for attack in attacks
    )


def test_build_attacks_jailbreak():
    attacks = build_attacks(
        "datasets/attacks/jailbreak.json"
    )

    assert len(attacks) == 5
    assert all(
        attack.category == "jailbreak"
        for attack in attacks
    )


def test_build_attacks_encoding():
    attacks = build_attacks(
        "datasets/attacks/encoding.json"
    )

    assert len(attacks) == 5
    assert all(
        attack.category == "encoding"
        for attack in attacks
    )


def test_load_all_attacks():
    args = Namespace(
        all=True,
        dataset="datasets/attacks/prompt_injection.json",
    )

    attacks = load_attacks(args)

    assert len(attacks) == 15

    categories = [
        attack.category
        for attack in attacks
    ]

    assert categories.count("prompt_injection") == 5
    assert categories.count("jailbreak") == 5
    assert categories.count("encoding") == 5


def test_load_single_dataset():
    args = Namespace(
        all=False,
        dataset="datasets/attacks/jailbreak.json",
    )

    attacks = load_attacks(args)

    assert len(attacks) == 5

    assert all(
        attack.category == "jailbreak"
        for attack in attacks
    )
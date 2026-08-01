from __future__ import annotations

import json
from pathlib import Path
from typing import Any


def load_attack_dataset(path: str | Path) -> list[dict[str, Any]]:
    dataset_path = Path(path)

    if not dataset_path.exists():
        raise FileNotFoundError(
            f"Attack dataset not found: {dataset_path}"
        )

    with dataset_path.open("r", encoding="utf-8") as file:
        data = json.load(file)

    if not isinstance(data, list):
        raise ValueError("Attack dataset must contain a JSON list.")

    return data
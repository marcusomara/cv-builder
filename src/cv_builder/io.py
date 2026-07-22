"""YAML and JSON persistence."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import yaml
from pydantic import BaseModel


def load_yaml[ModelT: BaseModel](path: Path, model: type[ModelT]) -> ModelT:
    with path.open(encoding="utf-8") as stream:
        data = yaml.safe_load(stream)
    return model.model_validate(data)


def write_yaml(path: Path, value: BaseModel) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as stream:
        yaml.safe_dump(value.model_dump(mode="json"), stream, sort_keys=False, allow_unicode=True)


def write_json(path: Path, value: BaseModel | dict[str, Any]) -> None:
    data = value.model_dump(mode="json") if isinstance(value, BaseModel) else value
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")

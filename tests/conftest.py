from __future__ import annotations

from pathlib import Path

import pytest

from cv_builder.io import load_yaml
from cv_builder.models import MasterCV, TailoringRules


@pytest.fixture
def project_root() -> Path:
    return Path(__file__).parents[1]


@pytest.fixture
def master(project_root: Path) -> MasterCV:
    return load_yaml(project_root / "data/master-cv.yaml", MasterCV)


@pytest.fixture
def rules(project_root: Path) -> TailoringRules:
    return load_yaml(project_root / "config/tailoring-rules.yaml", TailoringRules)

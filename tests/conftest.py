import json
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[1]


@pytest.fixture
def schema_examples_dir() -> Path:
    return REPO_ROOT / "schema" / "examples"


@pytest.fixture
def minimal_manifest(schema_examples_dir: Path) -> dict:
    return json.loads((schema_examples_dir / "minimal.json").read_text(encoding="utf-8"))


@pytest.fixture
def full_manifest(schema_examples_dir: Path) -> dict:
    return json.loads((schema_examples_dir / "full_example.json").read_text(encoding="utf-8"))

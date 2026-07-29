"""Load, save, and validate ABOM manifests."""

from __future__ import annotations

import json
import uuid
from datetime import datetime, timezone
from importlib import resources
from pathlib import Path
from typing import Any

import jsonschema
import yaml

from authbom import SCHEMA_VERSION, __version__


class ValidationError(Exception):
    def __init__(self, errors: list[str]):
        self.errors = errors
        super().__init__("; ".join(errors))


def _load_schema() -> dict[str, Any]:
    with resources.files("authbom.schema").joinpath("abom.schema.json").open(
        "r", encoding="utf-8"
    ) as f:
        return json.load(f)


_SCHEMA = None


def get_schema() -> dict[str, Any]:
    global _SCHEMA
    if _SCHEMA is None:
        _SCHEMA = _load_schema()
    return _SCHEMA


def new_manifest(tenant: str | None = None, manifest_id: str | None = None) -> dict[str, Any]:
    """Create an empty, schema-valid manifest skeleton."""
    metadata: dict[str, Any] = {
        "id": manifest_id or f"urn:uuid:{uuid.uuid4()}",
        "generatedAt": now_iso(),
        "generator": {"name": "authorization-bom", "version": __version__},
    }
    if tenant:
        metadata["tenant"] = tenant
    return {
        "abomVersion": SCHEMA_VERSION,
        "metadata": metadata,
        "identities": [],
        "resources": [],
        "actions": [],
        "grants": [],
        "toxicCombinations": [],
        "attestations": [],
    }


def now_iso() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def load(path: str | Path) -> dict[str, Any]:
    path = Path(path)
    text = path.read_text(encoding="utf-8")
    if path.suffix.lower() in (".yaml", ".yml"):
        doc = yaml.safe_load(text)
    else:
        doc = json.loads(text)
    return doc


def save(doc: dict[str, Any], path: str | Path) -> None:
    path = Path(path)
    if path.suffix.lower() in (".yaml", ".yml"):
        path.write_text(yaml.dump(doc, sort_keys=False, default_flow_style=False), encoding="utf-8")
    else:
        path.write_text(json.dumps(doc, indent=2, sort_keys=False) + "\n", encoding="utf-8")


def validate(doc: dict[str, Any]) -> list[str]:
    """Return a list of human-readable schema-validation error strings (empty if valid)."""
    schema = get_schema()
    validator = jsonschema.Draft202012Validator(schema)
    errors = []
    for e in sorted(validator.iter_errors(doc), key=lambda e: list(e.path)):
        path = "/".join(str(p) for p in e.path) or "<root>"
        errors.append(f"{path}: {e.message}")
    return errors


def validate_or_raise(doc: dict[str, Any]) -> None:
    errors = validate(doc)
    if errors:
        raise ValidationError(errors)


def index_by_id(items: list[dict[str, Any]]) -> dict[str, dict[str, Any]]:
    return {item["id"]: item for item in items}


def merge(base: dict[str, Any], addition: dict[str, Any]) -> dict[str, Any]:
    """Merge identities/resources/actions/grants from `addition` into `base`, de-duplicating by id.

    Later entries with the same id win (they represent a re-import/update).
    """
    merged = json.loads(json.dumps(base))
    for key in ("identities", "resources", "actions", "grants", "toxicCombinations", "attestations"):
        existing = index_by_id(merged.get(key, []))
        for item in addition.get(key, []):
            existing[item["id"]] = item
        merged[key] = list(existing.values())
    return merged

"""Shared helpers for read-only fixture adapters.

Every adapter in this package is read-only: it parses a JSON/YAML fixture already exported from a
source system (or a synthetic stand-in for one) and returns a manifest *fragment* -- a dict with
the same identities/resources/actions/grants keys as a full manifest, meant to be merged via
authbom.manifest.merge(). No adapter here ever connects to a live system or handles live
credentials; that is an explicit, permanent scope boundary (see docs/threat_model.md).
"""

from __future__ import annotations

from typing import Any


def empty_fragment() -> dict[str, list[Any]]:
    return {"identities": [], "resources": [], "actions": [], "grants": [], "toxicCombinations": [], "attestations": []}


def ensure_identity(fragment: dict[str, Any], identity_id: str, identity_type: str, **extra: Any) -> None:
    ids = {i["id"] for i in fragment["identities"]}
    if identity_id not in ids:
        record = {"id": identity_id, "type": identity_type}
        record.update({k: v for k, v in extra.items() if v is not None})
        fragment["identities"].append(record)


def ensure_resource(fragment: dict[str, Any], resource_id: str, resource_type: str, **extra: Any) -> None:
    ids = {r["id"] for r in fragment["resources"]}
    if resource_id not in ids:
        record = {"id": resource_id, "type": resource_type}
        record.update({k: v for k, v in extra.items() if v is not None})
        fragment["resources"].append(record)


def ensure_action(fragment: dict[str, Any], resource_id: str, name: str) -> str:
    action_id = f"action:{resource_id}:{name}"
    ids = {a["id"] for a in fragment["actions"]}
    if action_id not in ids:
        fragment["actions"].append({"id": action_id, "resourceRef": resource_id, "name": name})
    return action_id

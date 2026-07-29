"""Orphan-identity and cross-tenant-reachability checks (docs/formal_model.md; T6, T8)."""

from __future__ import annotations

from typing import Any


def find_orphans(manifest: dict[str, Any]) -> list[str]:
    """Identities whose `owner` does not resolve to another still-present identity id."""
    identity_ids = {i["id"] for i in manifest.get("identities", [])}
    orphans = []
    for identity in manifest.get("identities", []):
        owner = identity.get("owner")
        if owner is None:
            continue
        if owner == identity["id"]:
            continue
        if owner not in identity_ids:
            orphans.append(identity["id"])
    return orphans


def find_cross_tenant_grants(manifest: dict[str, Any]) -> list[dict[str, Any]]:
    """Grants where the subject's tenant differs from the resource's tenant."""
    identity_tenant = {i["id"]: i.get("tenant") for i in manifest.get("identities", [])}
    resource_tenant = {r["id"]: r.get("tenant") for r in manifest.get("resources", [])}
    findings = []
    for grant in manifest.get("grants", []):
        subj_tenant = identity_tenant.get(grant["subjectRef"])
        res_tenant = resource_tenant.get(grant["resourceRef"])
        if subj_tenant and res_tenant and subj_tenant != res_tenant:
            findings.append(
                {
                    "grantId": grant["id"],
                    "subjectTenant": subj_tenant,
                    "resourceTenant": res_tenant,
                }
            )
    return findings


__all__ = ["find_orphans", "find_cross_tenant_grants"]

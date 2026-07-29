"""Authorization-drift detection (RQ3; docs/formal_model.md "Authorization drift").

Computed independently from any pre-existing `grant.drift` field in the manifest (that field, if
present, reflects whatever the *generating* system already knew) -- this module re-derives drift
from first principles (runtimeEvidence vs. declared scope, revocation vs. propagation, staleness)
so it can be scored against ground truth in tests/benchmarks without trusting a self-reported flag.
"""

from __future__ import annotations

from datetime import datetime, timedelta
from typing import Any

DEFAULT_STALENESS = timedelta(days=90)


def detect_drift(
    manifest: dict[str, Any], now: datetime, staleness: timedelta = DEFAULT_STALENESS
) -> list[dict[str, Any]]:
    findings: list[dict[str, Any]] = []
    for grant in manifest.get("grants", []):
        findings.extend(_scope_drift(grant))
        findings.extend(_revocation_lag(grant))
        findings.extend(_dormant_grant(grant, now, staleness))
    return findings


def _scope_drift(grant: dict[str, Any]) -> list[dict[str, Any]]:
    out = []
    for event in grant.get("runtimeEvidence", []):
        if event.get("withinDeclaredScope") is False:
            out.append(
                {
                    "grantId": grant["id"],
                    "type": "scope_drift",
                    "detail": f"observed event at {event.get('observedAt')} outside declared action scope",
                }
            )
    return out


def _revocation_lag(grant: dict[str, Any]) -> list[dict[str, Any]]:
    revocation = grant.get("revocation") or {}
    if revocation.get("revoked") and not revocation.get("propagatedAt"):
        return [
            {
                "grantId": grant["id"],
                "type": "revocation_lag",
                "detail": f"revoked at {revocation.get('revokedAt')} with no recorded propagation",
            }
        ]
    return []


def _dormant_grant(grant: dict[str, Any], now: datetime, staleness: timedelta) -> list[dict[str, Any]]:
    if grant.get("state") not in ("declared", "approved"):
        return []
    if grant.get("revocation", {}).get("revoked"):
        return []
    if grant.get("runtimeEvidence"):
        return []
    imported_at = grant.get("policyProvenance", {}).get("importedAt")
    if not imported_at:
        return []
    try:
        imported_dt = datetime.fromisoformat(imported_at.replace("Z", "+00:00"))
    except ValueError:
        return []
    if now - imported_dt.replace(tzinfo=None) > staleness:
        return [
            {
                "grantId": grant["id"],
                "type": "dormant_grant",
                "detail": f"no observed runtime evidence since import at {imported_at}",
            }
        ]
    return []


__all__ = ["detect_drift", "DEFAULT_STALENESS"]

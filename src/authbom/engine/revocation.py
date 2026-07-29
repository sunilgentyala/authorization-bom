"""Revocation-convergence measurement (RQ5; docs/formal_model.md "Revocation convergence")."""

from __future__ import annotations

from datetime import datetime
from typing import Any


def _parse(ts: str) -> datetime:
    return datetime.fromisoformat(ts.replace("Z", "+00:00"))


def convergence_times(manifest: dict[str, Any]) -> list[dict[str, Any]]:
    """For every revoked grant, report convergence seconds (None if not yet propagated)."""
    results = []
    for grant in manifest.get("grants", []):
        revocation = grant.get("revocation") or {}
        if not revocation.get("revoked"):
            continue
        revoked_at = revocation.get("revokedAt")
        propagated_at = revocation.get("propagatedAt")
        seconds = None
        if revoked_at and propagated_at:
            seconds = (_parse(propagated_at) - _parse(revoked_at)).total_seconds()
        results.append(
            {
                "grantId": grant["id"],
                "revokedAt": revoked_at,
                "propagatedAt": propagated_at,
                "convergenceSeconds": seconds,
                "converged": propagated_at is not None,
            }
        )
    return results


def summary(results: list[dict[str, Any]]) -> dict[str, Any]:
    converged = [r["convergenceSeconds"] for r in results if r["converged"] and r["convergenceSeconds"] is not None]
    unresolved = [r for r in results if not r["converged"]]
    out: dict[str, Any] = {
        "total_revocations": len(results),
        "converged_count": len(converged),
        "unresolved_count": len(unresolved),
    }
    if converged:
        out["mean_convergence_seconds"] = sum(converged) / len(converged)
        out["max_convergence_seconds"] = max(converged)
        out["min_convergence_seconds"] = min(converged)
    return out


__all__ = ["convergence_times", "summary"]

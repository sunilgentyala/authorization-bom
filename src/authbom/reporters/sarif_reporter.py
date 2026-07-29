"""Render an analysis result as a SARIF 2.1.0 log.

Findings are mapped to logical locations (grant ids) rather than physical file locations, since
ABOM findings describe authorization-graph facts, not source-code lines. This mirrors how other
non-code SARIF producers (e.g. IaC/config scanners) use logicalLocations.
"""

from __future__ import annotations

import json
from typing import Any

RULES = {
    "delegation-chain-issue": {"name": "DelegationChainIssue", "level": "error"},
    "drift-detected": {"name": "AuthorizationDrift", "level": "warning"},
    "toxic-combination": {"name": "ToxicCombination", "level": "warning"},
    "orphaned-identity": {"name": "OrphanedIdentity", "level": "warning"},
    "cross-tenant-grant": {"name": "CrossTenantGrant", "level": "note"},
    "revocation-unresolved": {"name": "RevocationUnresolved", "level": "error"},
}


def _result(rule_id: str, message: str, logical_location: str) -> dict[str, Any]:
    return {
        "ruleId": rule_id,
        "level": RULES[rule_id]["level"],
        "message": {"text": message},
        "locations": [
            {
                "logicalLocations": [{"name": logical_location, "kind": "authorizationGrant"}]
            }
        ],
    }


def render(result: dict[str, Any]) -> str:
    results = []

    for d in result.get("delegation", []):
        if not d.get("clean", True):
            results.append(_result("delegation-chain-issue", "; ".join(d["issues"]), d["grantId"]))

    for d in result.get("drift", []):
        results.append(_result("drift-detected", f"[{d['type']}] {d['detail']}", d["grantId"]))

    for t in result.get("toxicCombinations", []):
        results.append(
            _result("toxic-combination", f"rule {t['rule']}: issuer {t['issuer']} on {t['resourceRef']}", t["grantId"])
        )

    for o in result.get("orphans", []):
        results.append(_result("orphaned-identity", f"identity {o} has an unresolvable owner", o))

    for c in result.get("crossTenant", []):
        results.append(
            _result(
                "cross-tenant-grant",
                f"tenant {c['subjectTenant']} -> {c['resourceTenant']}",
                c["grantId"],
            )
        )

    for r in result.get("revocation", {}).get("events", []):
        if not r.get("converged"):
            results.append(
                _result(
                    "revocation-unresolved",
                    f"revoked at {r['revokedAt']} with no recorded propagation",
                    r["grantId"],
                )
            )

    sarif = {
        "$schema": "https://raw.githubusercontent.com/oasis-tcs/sarif-spec/master/Schemata/sarif-schema-2.1.0.json",
        "version": "2.1.0",
        "runs": [
            {
                "tool": {
                    "driver": {
                        "name": "authorization-bom",
                        "informationUri": "https://github.com/sunilgentyala/authorization-bom",
                        "rules": [
                            {"id": rid, "name": spec["name"], "defaultConfiguration": {"level": spec["level"]}}
                            for rid, spec in RULES.items()
                        ],
                    }
                },
                "results": results,
            }
        ],
    }
    return json.dumps(sarif, indent=2) + "\n"

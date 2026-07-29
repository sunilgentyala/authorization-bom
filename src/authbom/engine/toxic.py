"""Toxic-combination / separation-of-duty detection (RQ4).

Not a novel detection algorithm -- rule evaluation over the authorization graph is how commercial
SoD tooling already works (see research/comparison_matrix.md, SailPoint/Saviynt). The comparison
this module exists to support is scope, not method: does extending the rule to include AI-agent
delegation chains (human_agent_scope=True) surface violations invisible to a human-only ruleset.
"""

from __future__ import annotations

from typing import Any


def _identity_types(manifest: dict[str, Any]) -> dict[str, str]:
    return {i["id"]: i["type"] for i in manifest.get("identities", [])}


def detect_approver_executor_overlap(
    manifest: dict[str, Any], include_agents: bool = True
) -> list[dict[str, Any]]:
    """Flags delegated grants whose chain issuer also holds a separate grant on the same resource
    -- the issuer both approves the delegation and (through the chain) can exercise the access.
    """
    id_types = _identity_types(manifest)
    grants_by_subject_resource: dict[tuple[str, str], list[dict[str, Any]]] = {}
    for g in manifest.get("grants", []):
        grants_by_subject_resource.setdefault((g["subjectRef"], g["resourceRef"]), []).append(g)

    findings = []
    for grant in manifest.get("grants", []):
        chain = grant.get("delegationChain")
        if not chain:
            continue
        final_subject_type = id_types.get(grant["subjectRef"])
        if not include_agents and final_subject_type == "ai_agent":
            continue
        issuer = chain[0]["issuer"]
        if (issuer, grant["resourceRef"]) in grants_by_subject_resource:
            findings.append(
                {
                    "rule": "sod-approver-and-executor-same-chain",
                    "grantId": grant["id"],
                    "issuer": issuer,
                    "resourceRef": grant["resourceRef"],
                    "finalSubjectType": final_subject_type,
                }
            )
    return findings


__all__ = ["detect_approver_executor_overlap"]

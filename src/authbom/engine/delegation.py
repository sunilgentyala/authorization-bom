"""Delegation-chain reconstruction and consistency checks (RQ2; docs/threat_model.md T3)."""

from __future__ import annotations

from typing import Any

from authbom.engine.effective_permissions import is_amplified


def chain_depth(grant: dict[str, Any]) -> int:
    return len(grant.get("delegationChain", []))


def reconstruct_chain(grant: dict[str, Any]) -> list[dict[str, Any]]:
    """Return delegation hops sorted by hop index, as recorded in the manifest."""
    return sorted(grant.get("delegationChain", []), key=lambda h: h["hop"])


def validate_chain(manifest: dict[str, Any], grant: dict[str, Any]) -> list[str]:
    """Return a list of consistency issues for a delegated grant's chain (empty if clean).

    Checks performed, all purely from data already present in the manifest:
    - hop indices are contiguous starting at 0
    - each hop after the first references a parentDelegationId
    - each hop's issuer equals the previous hop's subject (a delegation chain, not a disjoint set)
    - no hop is expired relative to the manifest's own generatedAt (a stale/unchecked hop)
    - the grant's actionRefs do not contradict the chain's recorded scopeReduction (see
      engine/effective_permissions.is_amplified)
    """
    issues: list[str] = []
    chain = reconstruct_chain(grant)
    if not chain:
        return issues

    for i, hop in enumerate(chain):
        if hop["hop"] != i:
            issues.append(f"hop index out of order at position {i} (found hop={hop['hop']})")
        if i > 0:
            if "parentDelegationId" not in hop:
                issues.append(f"hop {i} missing parentDelegationId")
            if hop["issuer"] != chain[i - 1]["subject"]:
                issues.append(
                    f"hop {i} issuer '{hop['issuer']}' does not match previous hop's subject "
                    f"'{chain[i - 1]['subject']}' -- not a continuous delegation chain"
                )

    generated_at = manifest.get("metadata", {}).get("generatedAt")
    if generated_at:
        for i, hop in enumerate(chain):
            expires_at = hop.get("expiresAt")
            if expires_at and expires_at < generated_at:
                issues.append(f"hop {i} expired ({expires_at}) before manifest generation ({generated_at})")

    if is_amplified(manifest, grant):
        issues.append(
            "actionRefs claims an action the chain's own scopeReduction records as dropped "
            "(privilege amplification contradiction)"
        )

    return issues


def analyze_delegations(manifest: dict[str, Any]) -> list[dict[str, Any]]:
    """Run validate_chain over every delegated grant, returning a report list."""
    report = []
    for grant in manifest.get("grants", []):
        if not grant.get("delegationChain"):
            continue
        issues = validate_chain(manifest, grant)
        report.append(
            {
                "grantId": grant["id"],
                "depth": chain_depth(grant),
                "issues": issues,
                "clean": not issues,
            }
        )
    return report


__all__ = ["chain_depth", "reconstruct_chain", "validate_chain", "analyze_delegations"]

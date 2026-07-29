"""Effective-permission closure computation (research/gap_analysis.md RQ1;
docs/formal_model.md "Effective-permission closure" and "Privilege amplification").

Two functions are exposed deliberately so benchmarks/tests can compare them:

- `naive_effective_permissions`: a simplistic union of every non-revoked grant's declared
  `actionRefs`, the kind of computation a tool with no delegation-attenuation awareness would
  produce. This is RQ1's baseline, not a strawman -- it is exactly what looking at
  `actionRefs` at face value gives you.
- `effective_permissions`: additionally validates each delegated grant's `actionRefs` against
  what its own recorded `delegationChain[].scopeReduction` implies is actually authorized, and
  uses the corrected (attenuated) action set when a contradiction is found.
"""

from __future__ import annotations

from collections import defaultdict
from datetime import datetime
from typing import Any


def full_action_set(manifest: dict[str, Any], resource_id: str) -> set[str]:
    return {a["id"] for a in manifest.get("actions", []) if a["resourceRef"] == resource_id}


def expected_actions_for_grant(manifest: dict[str, Any], grant: dict[str, Any]) -> set[str]:
    """The action set implied by a grant's own delegation chain, if any.

    For a non-delegated grant this is just its declared actionRefs (there is nothing else to
    validate against). For a delegated grant, it is the resource's full action set minus every
    hop's recorded scopeReduction -- i.e. what the chain itself claims should remain after
    attenuation.
    """
    chain = grant.get("delegationChain")
    if not chain:
        return set(grant.get("actionRefs", []))
    full = full_action_set(manifest, grant["resourceRef"])
    reductions: set[str] = set()
    for hop in chain:
        reductions.update(hop.get("scopeReduction", []))
    return full - reductions


def is_amplified(manifest: dict[str, Any], grant: dict[str, Any]) -> bool:
    """True if a grant's actionRefs claims an action its own delegation chain's scopeReduction
    says was dropped -- a self-contained, manifest-only detectable contradiction."""
    if not grant.get("delegationChain"):
        return False
    expected = expected_actions_for_grant(manifest, grant)
    return bool(set(grant.get("actionRefs", [])) - expected)


def _is_revoked(grant: dict[str, Any]) -> bool:
    return grant.get("state") == "revoked" or bool(grant.get("revocation", {}).get("revoked"))


def _within_temporal(grant: dict[str, Any], at: datetime) -> bool:
    temporal = grant.get("constraints", {}).get("temporal") if grant.get("constraints") else None
    if not temporal:
        return True
    not_before = temporal.get("notBefore")
    not_after = temporal.get("notAfter")
    if not_before and at < datetime.fromisoformat(not_before.replace("Z", "+00:00")):
        return False
    if not_after and at > datetime.fromisoformat(not_after.replace("Z", "+00:00")):
        return False
    return True


def naive_effective_permissions(manifest: dict[str, Any]) -> dict[tuple[str, str], set[str]]:
    return effective_permissions(manifest, corrected=False, at=None)


def effective_permissions(
    manifest: dict[str, Any],
    corrected: bool = True,
    at: datetime | None = None,
) -> dict[tuple[str, str], set[str]]:
    result: dict[tuple[str, str], set[str]] = defaultdict(set)
    for grant in manifest.get("grants", []):
        if _is_revoked(grant):
            continue
        if at is not None and not _within_temporal(grant, at):
            continue
        actions = set(grant.get("actionRefs", []))
        if corrected and is_amplified(manifest, grant):
            actions = expected_actions_for_grant(manifest, grant)
        key = (grant["subjectRef"], grant["resourceRef"])
        result[key].update(actions)
    return dict(result)


def score(
    computed: dict[tuple[str, str], set[str]],
    ground_truth: dict[tuple[str, str], set[str]],
) -> dict[str, float]:
    """Precision/recall/F1/false-positive-rate over the flattened (subject,resource,action) set."""
    computed_triples = {(s, r, a) for (s, r), acts in computed.items() for a in acts}
    truth_triples = {(s, r, a) for (s, r), acts in ground_truth.items() for a in acts}
    tp = len(computed_triples & truth_triples)
    fp = len(computed_triples - truth_triples)
    fn = len(truth_triples - computed_triples)
    precision = tp / (tp + fp) if (tp + fp) else 1.0
    recall = tp / (tp + fn) if (tp + fn) else 1.0
    f1 = (2 * precision * recall / (precision + recall)) if (precision + recall) else 0.0
    fpr = fp / (fp + tp) if (fp + tp) else 0.0
    return {
        "precision": precision,
        "recall": recall,
        "f1": f1,
        "false_positive_rate": fpr,
        "tp": tp,
        "fp": fp,
        "fn": fn,
    }


__all__ = [
    "full_action_set",
    "expected_actions_for_grant",
    "is_amplified",
    "naive_effective_permissions",
    "effective_permissions",
    "score",
]

"""Deterministic synthetic authorization-topology generator.

Produces a schema-valid ABOM manifest plus a separate, engine-independent ground-truth
structure used only by tests/benchmarks to score effective-permission accuracy, delegation-chain
reconstruction, drift detection, and toxic-combination detection (RQ1-RQ5 in
research/gap_analysis.md). The ground truth is never shipped inside the manifest itself -- an
analysis engine must derive everything from the manifest alone, the same as it would for a real
topology.

No real tenant data, credentials, or names are used anywhere in this module.
"""

from __future__ import annotations

import random
from dataclasses import dataclass, field
from datetime import datetime, timedelta, timezone

from authbom.manifest import new_manifest

ACTIONS_BY_RESOURCE_TYPE = {
    "api": ["read", "write"],
    "data": ["read", "write", "delete"],
    "tool": ["invoke"],
    "mcp_server": ["invoke", "list_tools"],
    "kubernetes_object": ["get", "list", "delete"],
    "cloud_resource": ["read", "write"],
}


@dataclass
class GroundTruth:
    effective_permissions: dict[tuple[str, str], set[str]] = field(default_factory=dict)
    """(subject_id, resource_id) -> set of actually-authorized action names, after deny precedence
    and delegation attenuation have been correctly applied."""
    delegation_chains: dict[str, list[dict]] = field(default_factory=dict)
    """grant_id -> the true intended delegation chain (before any injected amplification defect)."""
    amplification_defect_grant_ids: set[str] = field(default_factory=set)
    drift_defect_grant_ids: set[str] = field(default_factory=set)
    orphan_identity_ids: set[str] = field(default_factory=set)
    toxic_pairs: list[tuple[str, str]] = field(default_factory=list)
    revocation_events: dict[str, datetime] = field(default_factory=dict)
    """grant_id -> true revocation time (independent of whether propagatedAt was recorded)."""


def _iso(dt: datetime) -> str:
    return dt.strftime("%Y-%m-%dT%H:%M:%SZ")


def generate(
    seed: int,
    tenants: int = 2,
    humans_per_tenant: int = 3,
    workloads_per_tenant: int = 3,
    agents_per_tenant: int = 2,
    defect_rate: float = 0.2,
    max_extra_agent_hops: int = 0,
) -> tuple[dict, GroundTruth]:
    """Generate a deterministic synthetic manifest and its ground truth.

    `defect_rate` controls the fraction of eligible grants/identities that receive an injected
    defect (privilege amplification, revocation-propagation lag, scope drift, or orphaning).

    `max_extra_agent_hops` inserts 0..N synthetic relay-agent hops into each agent's delegation
    chain (varying per agent index), producing chains of depth 2..2+N -- used by RQ2's
    chain-depth-vs-reconstruction-accuracy ablation (research/gap_analysis.md).
    """
    # random.Random is intentional here, not a security shortcut: this generates non-secret,
    # synthetic benchmark fixtures and MUST be deterministically reproducible from `seed` for
    # RQ1-RQ6 (research/gap_analysis.md); `secrets`/CSPRNG output cannot be seeded this way.
    rng = random.Random(seed)  # nosec B311
    manifest = new_manifest(
        tenant="multi-tenant-synthetic",
        manifest_id=f"urn:authbom:synthetic:seed-{seed}",
    )
    gt = GroundTruth()

    base_time = datetime(2026, 7, 29, tzinfo=timezone.utc)
    # Fixtures are timestamped relative to `base_time`, not real wall-clock time, so
    # metadata.generatedAt/evidenceCutoff must match that same clock -- otherwise every
    # delegation hop would spuriously look expired relative to a real "now" far outside the
    # fixture's own timeline.
    manifest["metadata"]["generatedAt"] = _iso(base_time)
    manifest["metadata"]["evidenceCutoff"] = _iso(base_time)
    grant_counter = 0
    resource_counter = 0

    for t in range(tenants):
        tenant_id = f"tenant-{t}"
        humans = [f"user:{tenant_id}:h{i}" for i in range(humans_per_tenant)]
        workloads = [f"workload:{tenant_id}:w{i}" for i in range(workloads_per_tenant)]
        agents = [f"agent:{tenant_id}:a{i}" for i in range(agents_per_tenant)]

        for h in humans:
            manifest["identities"].append(
                {"id": h, "type": "human", "owner": h, "tenant": tenant_id}
            )
        for w in workloads:
            owner = rng.choice(humans)
            manifest["identities"].append(
                {"id": w, "type": "workload", "owner": owner, "tenant": tenant_id}
            )
        for i, a in enumerate(agents):
            parent_workload = workloads[i % len(workloads)] if workloads else None
            owner = rng.choice(humans)
            identity_record = {"id": a, "type": "ai_agent", "owner": owner, "tenant": tenant_id}
            if parent_workload:
                identity_record["parentAgentRef"] = parent_workload
            manifest["identities"].append(identity_record)

        # Inject orphaned identities: owner set to a nonexistent/removed identity id.
        orphan_candidates = workloads + agents
        n_orphans = max(0, int(len(orphan_candidates) * defect_rate * 0.5))
        for oid in rng.sample(orphan_candidates, k=min(n_orphans, len(orphan_candidates))):
            for rec in manifest["identities"]:
                if rec["id"] == oid:
                    rec["owner"] = f"user:{tenant_id}:removed-{oid}"
                    gt.orphan_identity_ids.add(oid)

        # Resources: data stores, tools, MCP servers per tenant.
        resources = []
        for kind, count in (("data", 2), ("tool", 2), ("mcp_server", 1), ("api", 2)):
            for _ in range(count):
                rid = f"resource:{tenant_id}:{kind}-{resource_counter}"
                resource_counter += 1
                sensitivity = rng.choice(["internal", "confidential", "restricted"])
                manifest["resources"].append(
                    {
                        "id": rid,
                        "type": kind,
                        "owner": rng.choice(humans),
                        "tenant": tenant_id,
                        "sensitivity": sensitivity,
                    }
                )
                for act_name in ACTIONS_BY_RESOURCE_TYPE[kind]:
                    aid = f"action:{rid}:{act_name}"
                    manifest["actions"].append({"id": aid, "resourceRef": rid, "name": act_name})
                resources.append(rid)

        def actions_for(rid: str) -> list[str]:
            return [a["id"] for a in manifest["actions"] if a["resourceRef"] == rid]

        # Direct grants for humans and workloads (role-like: each gets a subset of resources).
        for subject in humans + workloads:
            granted_resources = rng.sample(resources, k=min(2, len(resources)))
            for rid in granted_resources:
                grant_counter += 1
                gid = f"grant:{grant_counter:05d}"
                acts = actions_for(rid)
                deny_one = rng.random() < 0.15
                effective_acts = acts[:-1] if (deny_one and len(acts) > 1) else acts
                manifest["grants"].append(
                    {
                        "id": gid,
                        "subjectRef": subject,
                        "resourceRef": rid,
                        "actionRefs": effective_acts,
                        "authorityType": "direct" if subject in humans else "inherited",
                        "state": "approved",
                        "policyProvenance": {
                            "source": "synthetic",
                            "policyId": f"role/{rid}",
                            "policyVersion": "1",
                            "importedAt": _iso(base_time),
                        },
                        "evidenceCompleteness": "complete",
                    }
                )
                gt.effective_permissions.setdefault((subject, rid), set()).update(effective_acts)

        # Delegation chains: human -> workload -> agent, with scope reduction, over MCP tools.
        mcp_resources = [r for r in resources if r.split(":")[-1].startswith("mcp_server")]
        tool_resources = [r for r in resources if "tool-" in r]
        delegable_resources = mcp_resources + tool_resources
        for a_idx, agent in enumerate(agents):
            if not delegable_resources or not workloads:
                break
            rid = rng.choice(delegable_resources)
            acts = actions_for(rid)
            parent_workload = workloads[a_idx % len(workloads)]
            issuing_human = rng.choice(humans)

            extra_hops = (a_idx % (max_extra_agent_hops + 1)) if max_extra_agent_hops > 0 else 0
            relay_ids = [f"{agent}:relay{k}" for k in range(extra_hops)]
            for relay_id in relay_ids:
                manifest["identities"].append(
                    {"id": relay_id, "type": "ai_agent", "owner": issuing_human, "tenant": tenant_id}
                )
            chain_subjects = [issuing_human, parent_workload, *relay_ids, agent]

            # actions_at[i] = the action set held by chain_subjects[i]. Hop 0 (human -> workload)
            # never attenuates (the workload receives the human's full authority); every hop
            # after that drops one action (while more than one remains) -- deeper chains are
            # therefore progressively narrower, which is what RQ2 measures reconstruction
            # accuracy against.
            actions_at = [acts, acts]
            for _ in range(1, len(chain_subjects) - 1):
                prev = actions_at[-1]
                actions_at.append(prev[:-1] if len(prev) > 1 else prev)

            chain = []
            for i in range(len(chain_subjects) - 1):
                hop = {
                    "hop": i,
                    "issuer": chain_subjects[i],
                    "subject": chain_subjects[i + 1],
                    "audience": rid,
                    "expiresAt": _iso(base_time + timedelta(hours=12 - i)),
                }
                if i > 0:
                    hop["parentDelegationId"] = f"hop-{i - 1}"
                    hop["scopeReduction"] = [a for a in actions_at[i] if a not in actions_at[i + 1]]
                chain.append(hop)

            true_chain = [dict(h) for h in chain]
            true_actions = actions_at[-1]

            grant_counter += 1
            gid = f"grant:{grant_counter:05d}"

            inject_amplification = rng.random() < defect_rate
            emitted_actions = true_actions
            if inject_amplification and len(acts) > len(true_actions):
                # Defect: actionRefs claims back an action the recorded scopeReduction says was
                # dropped. The chain's own scopeReduction record is left intact (a realistic
                # defect: the delegation record is honest, the emitted grant contradicts it) so
                # the contradiction is detectable purely from the manifest -- see
                # engine/effective_permissions.py's is_amplified().
                emitted_actions = acts
                gt.amplification_defect_grant_ids.add(gid)

            manifest["grants"].append(
                {
                    "id": gid,
                    "subjectRef": agent,
                    "resourceRef": rid,
                    "actionRefs": emitted_actions,
                    "authorityType": "delegated",
                    "state": "computed",
                    "policyProvenance": {"source": "mcp", "policyId": f"mcp/{rid}", "importedAt": _iso(base_time)},
                    "delegationChain": chain,
                    "evidenceCompleteness": "complete",
                }
            )
            gt.delegation_chains[gid] = true_chain
            gt.effective_permissions.setdefault((agent, rid), set()).update(true_actions)

            # Toxic-combination ground truth: the issuing human also holds a direct grant on the
            # same resource (approver == ultimate executor's principal chain).
            issuer_own_grant = next(
                (g for g in manifest["grants"] if g["subjectRef"] == issuing_human and g["resourceRef"] == rid),
                None,
            )
            if issuer_own_grant is not None:
                gt.toxic_pairs.append((issuing_human, gid))
                manifest.setdefault("toxicCombinations", []).append(
                    {
                        "id": f"toxic:{gid}",
                        "grantRefs": [issuer_own_grant["id"], gid],
                        "rule": "sod-approver-and-executor-same-chain",
                        "severity": "medium",
                        "detectedAt": _iso(base_time),
                    }
                )

        # Revocation events with injected propagation lag (drift).
        revocable = [g for g in manifest["grants"] if g["subjectRef"] in workloads]
        n_revoke = max(0, int(len(revocable) * defect_rate))
        for g in rng.sample(revocable, k=min(n_revoke, len(revocable))):
            revoked_at = base_time - timedelta(hours=29)
            gt.revocation_events[g["id"]] = revoked_at
            propagate = rng.random() > defect_rate  # most propagate; some lag (the defect)
            revocation: dict = {"revoked": True, "revokedAt": _iso(revoked_at), "reason": "credential rotation"}
            if propagate:
                revocation["propagatedAt"] = _iso(revoked_at + timedelta(minutes=5))
            else:
                gt.drift_defect_grant_ids.add(g["id"])
                g["drift"] = {
                    "detected": True,
                    "detectedAt": _iso(base_time),
                    "description": "revocation recorded but not yet propagated to dependent records",
                }
            g["state"] = "revoked"
            g["revocation"] = revocation
            gt.effective_permissions.pop((g["subjectRef"], g["resourceRef"]), None)

        # Runtime evidence with occasional out-of-scope invocation (scope drift).
        observable = [g for g in manifest["grants"] if g["subjectRef"] in agents and g.get("state") != "revoked"]
        for g in observable:
            out_of_scope = rng.random() < defect_rate
            g.setdefault("runtimeEvidence", []).append(
                {
                    "observedAt": _iso(base_time - timedelta(minutes=5)),
                    "eventType": "tool_invocation",
                    "sourceLog": "synthetic-log:out-of-scope-tool" if out_of_scope else "synthetic-log",
                    "withinDeclaredScope": not out_of_scope,
                }
            )
            if out_of_scope:
                gt.drift_defect_grant_ids.add(g["id"])
                g["drift"] = {
                    "detected": True,
                    "detectedAt": _iso(base_time),
                    "description": "observed tool invocation outside declared action scope",
                }

    return manifest, gt

# ABOM Formal Model

Scope: definitions used by the reference implementation (`src/authbom/engine/`) and referenced
directly by RQ1-RQ6 in research/gap_analysis.md. These are implementation-grounding definitions
for this project's synthetic benchmark, not claims of a universally validated formalism.

## Temporal authorization graph

At time `t`, authorization state is modeled as a directed, typed, attributed multigraph:

```
G_t = (V_t, E_t)
```

- `V_t` = identities (human, workload, service, application, ai_agent) union resources
  (api, tool, mcp_server, data, service, downstream_agent, kubernetes_object, cloud_resource).
- `E_t` = grant edges `(subject, resource, actionRefs, authorityType, state, constraints,
  delegationChain)` as defined in schema/abom.schema.json's `Grant` object, each timestamped by
  its `policyProvenance.importedAt` / `runtimeEvidence[].observedAt`.
- `G_t` is reconstructed from an ABOM manifest by filtering edges whose validity interval
  (`constraints.temporal`, credential `issuedAt`/`expiresAt`, `revocation`) contains `t`.

## Effective-permission closure

For subject `s` and resource `r`, the **effective-permission closure** `EFF(s, r, t)` is the set
of actions reachable from `s` to `r` in `G_t` via:

1. direct edges (`authorityType = direct`),
2. inherited edges (role/group membership expansion),
3. delegated edges, following `delegationChain` hops in order, where each hop's action set is
   `parentActions \ scopeReduction` (attenuation-only; a hop can never add actions absent from its
   parent — this is enforced by the reference engine, not merely assumed),
4. transitive combinations of the above up to a configurable maximum hop count `H_max` (bounding
   graph-expansion cost, addressed in the threat model as a denial-of-service control).

```
EFF(s, r, t) = Union over paths p from s to r in G_t valid at t of actions(p)
```

where `actions(p)` for a multi-hop delegated path is the attenuation-closure product described
above, not a union that could amplify privilege beyond any single hop's grant.

## Privilege amplification

A grant exhibits **privilege amplification** if, for some hop `i` in its `delegationChain`,
`actions(hop_i) \ scopeReduction(hop_i) \not\subseteq actions(hop_{i-1})` — i.e., a later hop
claims an action its parent did not hold. This is a direct implementation check (`engine/
delegation.py`), not merely a definitional statement: any manifest exhibiting this is flagged as a
tampered or malformed delegation chain (see threat model, "manifest tampering").

## Authorization drift

Let `DECLARED(s, r, t)` be the grant state recorded in the manifest's `declared`/`approved`
records, and `OBSERVED(s, r, t)` be the state reconstructed from `runtimeEvidence` events. Drift is
detected when:

```
DECLARED(s, r, t) != OBSERVED(s, r, t)
```

for any of: (a) an observed action outside the declared action set (**scope drift**), (b) an
observed event after a recorded `revocation.revoked = true` with no `propagatedAt` (**revocation-
lag drift**), or (c) a declared grant with no corresponding observed evidence for longer than a
configurable staleness window (**dormant-grant drift**, relevant to orphan/least-privilege
analysis, not treated as a defect by itself).

## Toxic combinations / separation-of-duty violations

A toxic combination is a pair (or set) of grants `{g_1, ..., g_k}` matching a declared rule
`rule(g_1, ..., g_k) -> bool` over subject/resource/action attributes (e.g., "the same identity
chain that approves a refund also has direct execute authority on the refund tool"). This project
does not claim a novel detection algorithm — rule evaluation is a direct, enumerable check over
`G_t`, consistent with how commercial SoD tooling (SailPoint, Saviynt; see research/
comparison_matrix.md) already operates, extended here only to include AI-agent-mediated chains
(RQ4).

## Orphan detection

Identity `i` is **orphaned** if `owner` is absent/unresolvable or if `owner`'s own identity record
is itself revoked/absent, and `i` holds at least one non-revoked grant. This is a direct schema-
level check (`Identity.owner` resolves to another `Identity.id` still valid at `t`).

## Provenance completeness

A grant's provenance is **complete** if `policyProvenance.source`, `policyProvenance.sourceRef`,
and (for delegated grants) every `delegationChain` hop's `issuer`/`subject` resolve to a known
identity; otherwise `evidenceCompleteness` must be `partial` or `missing` per the schema. The
engine never infers "no access" from missing evidence — that inference is explicitly disallowed
(see threat model, fail-closed vs. fail-silent distinction) and is instead surfaced as
`evidenceCompleteness != complete` for human/process review.

## Cross-tenant reachability

For tenants `T_1, T_2`, cross-tenant reachability exists if some path in `EFF(s, r, t)` crosses an
edge where `identity.tenant != resource.tenant` without an explicit cross-tenant grant record. This
is computed as a graph search restricted to tenant-boundary-crossing edges, flagged regardless of
whether the crossing grant exists (crossing is reported either way; the flag distinguishes
authorized crossing from an undeclared one).

## Revocation convergence

For a revocation event at `t_0` (`revocation.revoked = true, revokedAt = t_0`), convergence time is

```
T_converge = propagatedAt - t_0
```

measured across every dependent record referencing the same credential/grant. `T_converge` is
undefined (reported as such, not defaulted to zero) while `propagatedAt` is absent. RQ5 measures
the distribution of `T_converge` on synthetic fixtures as a function of estate size.

## Bounds and threats to validity

All definitions above are evaluated only against the synthetic fixtures generated by `src/authbom/
adapters/synthetic.py` in this project (see research/gap_analysis.md, "threats to validity" column
per RQ). No claim is made that `EFF`, drift, or toxic-combination detection accuracy generalizes
to real production authorization estates without further validation against real data, which this
project's synthetic-only evaluation cannot provide.

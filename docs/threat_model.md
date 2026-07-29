# ABOM Threat Model

Scope: the ABOM manifest format, reference generator/validator/analyzer CLI, and the evidence
pipeline that produces and consumes manifests. Excludes the internal security of source systems
(Kubernetes, OPA, cloud IAM) themselves, which are out of scope and treated as trusted inputs
whose own compromise is listed below as a threat to the *manifest*, not something this project
defends against directly.

## Assets

- The ABOM manifest itself (declared/approved/computed/observed/revoked authorization evidence).
- Signing keys used to sign manifests and attestations.
- Source-system credentials used by read-only discovery adapters (must never be persisted).
- The synthetic fixtures and any real topology data an operator might feed into the tool (never
  committed to this repository; only synthetic fixtures ship).

## Actors

- **Manifest generator operator**: runs `authbom import`/`generate` against source systems.
- **Manifest consumer/verifier**: a separate party (auditor, CI pipeline, downstream tool) that
  validates and analyzes a manifest it did not generate.
- **Issuer / policy administrator**: the authority whose signature manifests trust for delegation
  hops and approvals (mirrors HWAAM's separate issuer-secret concept, disclosed as related prior
  work).
- **Adversary**: an internal or external party attempting to obtain unauthorized access, hide
  access from audit, or cause the analysis pipeline to reach a wrong conclusion.

## Trust boundaries

1. Source system <-> adapter (adapter is read-only; a compromised source system can still feed the
   adapter false data — this is a stated limitation, not something ABOM can detect on its own).
2. Adapter/generator <-> manifest (the point where policy provenance and signatures are attached).
3. Manifest <-> analysis engine (effective-permission/drift/toxic-combination computation).
4. Manifest <-> verifier (a party without access to source systems, relying solely on the
   manifest's own signatures and internal consistency).

## Assumptions

- Signing keys are managed outside this tool (file/env/stdin input only, consistent with the
  `--secret-file`/`--secret-env`/`--secret-stdin` pattern already used in the related HWAAM
  project) and are never written to logs or committed fixtures.
- Adapters are read-only and must not require write/admin credentials to source systems.
- The synthetic dataset generator is the only data source used in this project's own testing and
  benchmarking; no real tenant data is ever used.

## Abuse cases and mitigations

| # | Abuse case | Attack description | Mitigation in ABOM design | Residual risk |
|---|---|---|---|---|
| T1 | Confused-deputy behavior | A workload/agent uses its own broad credential to act on a human's behalf beyond what the human actually authorized | `delegationChain` records issuer/subject/audience per hop; effective-permission engine enforces attenuation-only closure (formal_model.md) so a deputy cannot exceed its principal's grant in `EFF` computation | Detection is only as good as adapters correctly importing the real delegation relationship; a source system that doesn't expose delegation context leaves this unrepresented (`evidenceCompleteness: partial`) |
| T2 | Privilege escalation via role/group inheritance | Attacker exploits an inherited/nested-group path not visible to a naive per-system view | Effective-permission closure explicitly traverses inherited edges (formal_model.md); toxic-combination rules can flag unexpected inherited reachability | Bounded by `H_max` hop cap (also mitigates T14); very deep or cyclic inheritance beyond the cap is reported as `evidenceCompleteness: partial`, not silently ignored |
| T3 | Delegation abuse (scope/authority amplification across hops) | A later delegation hop claims more than its parent held | Formal model's privilege-amplification check rejects/flags any hop where `actions(hop_i) \not\subseteq actions(hop_{i-1})` | Only detectable if the full chain is present in the manifest; a manifest missing intermediate hops cannot be checked and must be marked `partial` |
| T4 | Prompt injection causing unauthorized tool use | An AI agent is manipulated into invoking a tool outside its intended task scope | `runtimeEvidence.withinDeclaredScope` plus drift detection (`DECLARED != OBSERVED`) surfaces this after the fact; ABOM is an evidence/detection layer here, not a runtime blocker (that is the MCP-gateway category's job, disclosed as related work in comparison_matrix.md) | ABOM cannot prevent the invocation in real time; it can only make the resulting drift visible for reconciliation, which is the explicitly scoped contribution (RQ3) |
| T5 | Token theft and replay | Stolen credential reused outside its original context | `Credential.expiresAt`, `constraints.temporal`, and `constraints.contextual` (e.g. required network) are recorded and checked at analysis time; replay detection itself is out of scope (that requires live request-time enforcement, not manifest analysis) | Manifest-based detection is retrospective; real-time replay prevention is explicitly out of scope for this project |
| T6 | Orphaned identities | Identity's owner has left/been removed, access persists unreviewed | Orphan-detection rule in formal_model.md (`Identity.owner` unresolved or itself revoked) | Depends on adapters correctly importing ownership metadata; synthetic-only validation (see gap_analysis.md threats to validity) |
| T7 | Policy drift | Declared policy in source system diverges from what a dependent system still enforces | Drift detection compares `DECLARED`/`OBSERVED` across snapshots (RQ3); temporal-context ablation specifically tests this | False negatives possible if drift resolves between two snapshot intervals shorter than the sampling cadence — reported as a limitation, not hidden |
| T8 | Cross-tenant access | A grant crosses a tenant boundary without an explicit cross-tenant record | Cross-tenant reachability check in formal_model.md flags every boundary-crossing edge, authorized or not, for explicit review | Requires `tenant` to be populated correctly by adapters; a source system without tenant metadata cannot be checked |
| T9 | Excessive scopes | OAuth/IAM grant is broader than actually used | `runtimeEvidence` vs. declared action set comparison surfaces unused scope (dormant-grant drift) | Requires a sufficient runtime observation window; a manifest generated once with no observation history cannot detect this |
| T10 | Manifest tampering and rollback | An attacker edits a manifest after generation, or replays an older manifest to hide a later revocation | Every grant and the manifest as a whole can carry a `Signature` (Ed25519/ECDSA/HMAC); `verify` recomputes and checks signatures; monotonic `generatedAt`/`evidenceCutoff` plus explicit `revocation.propagatedAt` fields make rollback (an older, unrevoked manifest presented as current) detectable when compared against a previously verified manifest's metadata | Rollback detection requires the verifier to retain or compare against a prior verified manifest (e.g., via `authbom diff`); a first-ever manifest has nothing to roll back from |
| T11 | Compromised issuer or policy administrator | The signing authority itself is compromised and signs a false manifest | Out of scope for manifest-level defense (a valid signature from a compromised key is indistinguishable from a legitimate one); mitigated only by standard key-management hygiene (external key storage, rotation via `keyId`), explicitly disclosed as a residual risk, not solved | Full mitigation requires transparency-log-style infrastructure (SCITT/Sigstore-style), which is future work, not built in this project |
| T12 | Time-of-check to time-of-use (TOCTOU) | Access changes between manifest generation and consumption/decision time | `evidenceCutoff` and `generatedAt` timestamps make the staleness of any manifest explicit; consumers are expected to check `evidenceCutoff` freshness before treating a manifest as authoritative for a live decision | ABOM manifests are point-in-time evidence, not a live authorization oracle; using a stale manifest to gate a real-time decision is a consumer-side misuse this project explicitly warns against in README/docs |
| T13 | Revocation failure / propagation failure | A revocation is recorded in one system but not others | `revocation.propagatedAt` absence with `revoked: true` is the explicit signal (see grant:1003 in schema/examples/full_example.json); RQ5 measures convergence time | Detection depends on the manifest actually including the lagging dependent record; a system omitted entirely from discovery cannot be checked |
| T14 | Graph-expansion denial of service | Deeply nested/cyclic delegation or inheritance causes unbounded analysis cost | `H_max` hop cap (formal_model.md) and cycle detection in the effective-permission engine bound worst-case analysis time; RQ6 measures overhead as a function of estate size | An operator setting `H_max` too high on a real large estate could still see high latency; this is a configuration trade-off disclosed in docs, not eliminated |

## Explicit design stance: fail-closed vs. fail-silent on missing evidence

Per the assignment's integrity rules, the engine must never treat missing/unverifiable evidence as
equivalent to "no access" (which would hide a real gap) nor as "access granted" (which would be
unsafe). Every code path that cannot fully resolve a grant's provenance or a delegation chain must
set `evidenceCompleteness` to `partial` or `missing` and surface it in reports rather than silently
defaulting either way. This is enforced in `src/authbom/engine/` and covered by dedicated negative
tests (see tests/ in the implementation phase).

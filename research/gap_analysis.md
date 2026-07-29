# ABOM Gap Analysis and Research Questions

Research cutoff: 2026-07-29. Built from research/novelty_gate.md and research/comparison_matrix.md.
Every row below is evidence-backed against the sources already logged; gaps without a supporting
source from search_log.csv/comparison_matrix.md were dropped rather than asserted.

## Gap matrix

| # | Gap | Evidence | Closest existing solution | Already solved | Unresolved | Operational impact | Testable RQ candidate | Threats to validity |
|---|---|---|---|---|---|---|---|---|
| G1 | Configured vs. effective authority not portably exportable across identity types in one document | CycloneDX/SPDX have no authorization profile (comparison_matrix.md §1); Veza computes effective access but as a proprietary platform output, not an interchange format (Vd) | Veza Access Graph (commercial, proprietary) | Computing effective access within one vendor's graph | Exporting/verifying it as a portable, tool-agnostic, signed artifact | Cross-tool audits and second-party verification require re-deriving effective access per tool | RQ1 (below) | Synthetic-only evaluation cannot claim real-world completeness |
| G2 | Human-authority inheritance by AI agents not represented alongside classic RBAC/ABAC/workload identity in one schema | OIDC-A standardizes delegation-chain validation as a live protocol exchange (arXiv 2509.25974), not a static inventory record | OIDC-A | Delegation validation at request time | Recording the resulting authority as durable, queryable evidence after the fact | Post-hoc audit/incident review cannot reconstruct what an agent was authorized to do without replaying live tokens | RQ2 | OIDC-A may evolve; schema mapping could drift |
| G3 | MCP tool-capability authorization not unified with human/workload authorization in the same evidence document | MCP-gateway category is runtime-only, proprietary logs (comparison_matrix.md §3) | MCP gateways (Arcade, Strata, Obot, etc.) | Runtime enforcement + vendor-specific logging | A vendor-neutral exportable record of what an agent/tool was authorized vs. observed to do | Vendor lock-in on agent-authorization audit trails | RQ2 | MCP ecosystem is early (per search: ~9,400 servers by mid-2026) and may change field needs |
| G4 | Delegation-reachability analysis exists only for single-cloud IAM role graphs, not cross-system (human+workload+agent) | US11757886B2 / US12034727 scoped to AWS IAM role assumption only (comparison_matrix.md §2) | Amazon patent family (algorithm, not exportable artifact) | Reachability analysis within one IAM graph | Reachability analysis across heterogeneous systems represented in one evidence document | Attack-path/privilege-amplification analysis must be redone per system, missing cross-system chains | RQ1 | Formal model must be validated only on the synthetic multi-system fixtures built here, not real heterogeneous estates |
| G5 | No standard artifact distinguishes declared vs. approved vs. computed vs. observed-runtime vs. revoked authorization state together | No source in comparison_matrix.md carries all of these states in one versioned document | SPDX 3.0 profile pattern (structurally analogous, not populated for authorization) | Analogous pattern exists for components (build/AI/dataset provenance) | No authorization analogue exists | Drift between "what was granted" and "what is actually usable" is not detectable from a single artifact; requires manual reconciliation across systems | RQ3 | Drift-detection accuracy is only as good as the synthetic injected-defect generator's realism |
| G6 | Toxic-combination/SoD detection is mature but proprietary and ERP/IGA-scoped, not extended to AI-agent tool combinations | SailPoint/Saviynt are ERP/SaaS-scoped (comparison_matrix.md §3) | SailPoint, Saviynt | Human-identity SoD in ERP/SaaS | Toxic combinations spanning a human approver + an AI agent + a downstream tool call | Agent-mediated separation-of-duty bypass (human approves, agent executes with amplified scope) is not covered by existing SoD tooling | RQ4 | Toxic-combination rule set here is illustrative/synthetic, not validated against real incident data |
| G7 | Revocation convergence time not measured/reported as a portable metric across identity types | No source found reporting a cross-system revocation-convergence benchmark | in-toto/DSSE (attests signing, not revocation propagation) | Signing/attestation of a single decision | Measuring how long stale authorization persists after revocation across a mixed human/workload/agent estate | Silent continued access after revocation is a known incident pattern (confused-deputy, stale token literature) but no portable measurement method was found | RQ5 | Convergence time is measured only in the synthetic harness's reconciliation loop, not a live production system |

Rejected candidate gaps (no supporting evidence found this session, dropped rather than asserted):
privacy risks specific to authorization inventories themselves (plausible but no source found to
anchor it); scalability claims beyond what this project's own benchmark measures.

## Derived research questions (max 6, per assignment constraint)

**RQ1 — Effective-permission computation accuracy across heterogeneous synthetic sources.**
Given a synthetic multi-tenant topology (K8s RBAC + OPA + Cedar/OpenFGA relationships + OAuth
scopes + MCP tool grants) with known ground-truth effective permissions (including injected
delegation chains), does ABOM's effective-permission engine reconstruct the ground-truth
effective-permission set with precision/recall/F1 statistically distinguishable from a
naive union-of-direct-grants baseline?
- H0: ABOM's precision/recall/F1 is not distinguishable from the naive baseline.
- H1: ABOM's precision/recall/F1 is higher than the naive baseline on the synthetic benchmark.
- Variables: independent = engine (ABOM vs. naive baseline vs. no-transitive-closure ablation);
  dependent = precision, recall, F1, false-positive rate against synthetic ground truth.
- Baseline: naive union of directly-declared grants (no transitive/delegation closure) — the
  simplest defensible baseline given no open-source equivalent tool was found to compare against
  directly.
- Controls: same synthetic topology and seed across engine variants.
- Rejection criterion: if ABOM's F1 is not significantly higher (paired test across seeds) than the
  naive baseline, H1 is rejected and this must be reported as a negative result, not hidden.

**RQ2 — Cross-identity-type delegation-chain reconstruction (human -> workload -> AI agent).**
Can ABOM reconstruct injected multi-hop delegation chains (human grants to workload, workload
delegates to agent, agent invokes downstream tool) from synthetic fixtures, and how does
reconstruction accuracy degrade as chain depth increases?
- H0: reconstruction accuracy is independent of chain depth.
- H1: reconstruction accuracy decreases as chain depth increases (a specific, falsifiable,
  plausibly-negative expected result worth reporting either way).
- Variables: independent = injected chain depth (1-5 hops); dependent = chain-reconstruction
  accuracy, false-negative rate on deepest hops.
- Baseline: direct-grant-only visibility (depth-1 detection only).
- Rejection criterion: report the actual accuracy-vs-depth curve, including if it stays flat
  (rejecting H1) rather than assuming degradation.

**RQ3 — Drift detection between declared/approved and observed-runtime state.**
Given synthetic fixtures with injected drift events (a grant revoked in one system but not
reflected in a dependent system, a runtime tool call outside declared scope), what are ABOM's
drift-detection precision/recall, and how much does temporal-context modeling (point-in-time graph
snapshots) contribute versus a snapshot-diff-only ablation?
- H0: temporal-context modeling provides no detection improvement over snapshot-diff.
- H1: temporal-context modeling improves recall on drift events that span more than one snapshot
  interval.
- Variables: independent = temporal-context on/off (ablation); dependent = drift-detection
  precision/recall/F1.
- Baseline: pairwise snapshot diff without a temporal graph.
- Rejection criterion: if the ablation shows no recall improvement, report this as a negative
  result and do not claim temporal modeling as a benefit in the manuscript.

**RQ4 — Toxic-combination detection extended to human+agent separation-of-duty.**
Does adding AI-agent tool-invocation edges to a classical SoD rule set change the number of
detected toxic combinations relative to a human-only SoD baseline (modeled after SailPoint/Saviynt-
style rule definitions) on the synthetic benchmark?
- H0: agent-inclusive SoD analysis finds the same violations as human-only SoD analysis.
- H1: agent-inclusive analysis finds additional violations not visible to human-only analysis.
- Variables: independent = SoD rule scope (human-only vs. human+agent); dependent = count and
  category of detected violations, false-positive rate.
- Baseline: human-only SoD ruleset applied to the same synthetic topology.
- Rejection criterion: if no additional violations are found, report this plainly rather than
  reframing the comparison.

**RQ5 — Revocation convergence time across a mixed identity estate.**
After a synthetic revocation event, how long (in reconciliation cycles / wall-clock on the
benchmark harness) until ABOM's reconcile step reflects the revocation across all dependent
records, and how does this scale with estate size (number of identities/edges)?
- H0: convergence time is independent of estate size.
- H1: convergence time scales with estate size (graph size/edges).
- Variables: independent = synthetic estate size (small/medium/large fixture); dependent =
  convergence time, memory/CPU during reconciliation.
- Baseline: none externally comparable found (no open-source cross-system revocation-convergence
  benchmark located) — this RQ is reported as an exploratory measurement on ABOM alone, with that
  limitation stated explicitly, not framed as a comparison against prior art that doesn't exist yet.
- Rejection criterion: report the actual scaling curve; do not assume linear/sublinear behavior.

**RQ6 — Manifest generation/validation/verification overhead.**
What is the wall-clock and memory cost of generating, validating (JSON Schema), signing, and
verifying an ABOM manifest as a function of estate size, and is this overhead practical (sub-second
to low-second range) for CI-scale use, consistent with how SBOM tooling reports comparable
generation-time metrics?
- H0: generation/validation/signing/verification time is not practically usable at CI scale
  (arbitrarily defined here as >10s at the largest synthetic fixture size, stated up front).
- H1: overhead stays within a practical CI-scale budget across tested fixture sizes.
- Variables: independent = fixture size; dependent = wall-clock time per CLI stage, peak memory.
- Baseline: none (first measurement of its kind for this specific artifact) — reported as absolute
  numbers with hardware/OS/Python version recorded, not as a comparative claim.
- Rejection criterion: if the largest tested fixture exceeds the stated 10s/stage budget, report
  this as a scalability limitation, not omit it.

## Gate check

Per assignment Section 5/6: framework and schema design may now proceed, using RQ1-RQ6 to scope
which mechanisms the reference implementation must actually build (effective-permission engine,
delegation-chain reconstruction, drift detection, toxic-combination/SoD analysis, revocation
reconciliation, and manifest generate/validate/sign/verify performance) rather than building
speculative features outside these six questions.

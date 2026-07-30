# ABOM — Project Status

Last updated: 2026-07-29

## Current phase
All 17 planned tasks complete as of 2026-07-30. Repository published and green. Four manuscript
versions drafted and build-validated (master DOCX, IEEE TPS 2026 anonymized DOCX, ACM TOPS LaTeX
PDF, Elsevier Computers & Security LaTeX PDF). AEGIS integrity check run and investigated. See
SUBMISSION_READINESS_CHECKLIST.md (in the private manuscript folder, not this repo) for the full
list of what remains before an actual venue submission -- primarily author-detail finalization for
Suresh Kumar Darisi and a database-backed novelty-gate re-verification. PROJECT_STATUS.md remains
the authoritative resume point after any context compression.

## Completed
- Phase 1: Workspace inspection, EXECUTION_PLAN.md, PROJECT_STATUS.md, HWAAM-collision disclosure and user decision recorded.
- Phase 2 (first pass): research/search_protocol.md, research/search_log.csv, research/comparison_matrix.md, research/novelty_gate.md, research/naming_review.md written.
  - Name verdict: keep ABOM (concept) / `authorization-bom` (repo, PyPI) — both unclaimed, collisions checked and disclosed (dtylman/azbom rejected as name basis; "Az" reads as Azure).
  - Narrowed contribution: ABOM is an interoperability/schema + reference-tooling contribution positioned as a candidate SPDX/CycloneDX-style profile, NOT a novel algorithm — effective-permission graphs (Veza, commercial), delegation-reachability analysis (Amazon US11757886B2/US12034727 patent family), agent delegation chains (OIDC-A, arXiv 2509.25974), and agent permission manifests (arXiv 2601.02371) are all real prior art, disclosed and compared, not reproduced as novel.
  - **Disclosed limitation**: this pass used general web search/fetch only, no IEEE Xplore/ACM DL/Scopus/Web of Science/structured USPTO institutional query access. Must be revisited with database access before final submission sign-off.

## Decisions log
| Date | Decision | Reason | Reversible? |
|---|---|---|---|
| 2026-07-29 | ABOM is a new, standalone project. HWAAM (existing repo/paper) is untouched, treated as related prior work only. | User explicit instruction: "do not disturb exist repos, this is completelye new research" | N/A — user directive |
| 2026-07-29 | Local repo path: C:\Gitrepos\authorization-bom. Manuscript path: C:\Users\Sunil\Documents\EB1A_local\Academic\ABOM (private). | Follows existing project conventions in this workspace (manuscripts kept out of public repos per feedback_academic_papers memory). | Yes |

## Completed (continued)

- Phase 2 (novelty gate): research/search_log.csv, comparison_matrix.md, novelty_gate.md,
  naming_review.md. Verdict: ABOM / `authorization-bom` kept, narrowed to an interoperability +
  reference-tooling contribution (not a novel algorithm). User confirmed: proceed to design.
- Phase 3 (gap analysis): research/gap_analysis.md, 6 research questions (RQ1-RQ6) with
  hypotheses/variables/baselines/rejection criteria.
- Phase 4 (schema): schema/abom.schema.json (JSON Schema draft 2020-12), schema/examples/
  minimal.{json,yaml}, full_example.json -- all validate against the schema (jsonschema 4.26.0).
- Phase 5 (formal model): docs/formal_model.md -- temporal graph G_t, effective-permission
  closure, privilege amplification, drift, toxic combinations, orphan detection, provenance
  completeness, cross-tenant reachability, revocation convergence.
- Phase 6 (threat model): docs/threat_model.md -- 14 abuse cases (T1-T14) mapped to schema/engine
  mitigations and residual risk, fail-closed-on-missing-evidence design stance stated explicitly.
- Phase 7 (implementation): `src/authbom/` -- manifest.py, signing.py (HMAC-SHA256; Ed25519/ECDSA
  schema-allowed but NOT implemented, disclosed limitation), adapters/ (synthetic generator,
  kubernetes_rbac, opa, cedar/openfga, oauth_scope, mcp -- all read-only, no live credentials),
  engine/ (effective_permissions, delegation, drift, toxic, revocation, graph_checks), reporters/
  (json, markdown, sarif), cli.py (`authbom import/generate/validate/sign/verify/diff/analyze/
  reconcile/report`). Installed editable, all 9 CLI subcommands smoke-tested manually.
- Phase 8 (tests + benchmarks): 76 pytest tests (schema/unit/property/integration/negative/tamper/
  replay), 94% line coverage (target 85%), Ruff clean, Bandit clean (one justified `# nosec B311`
  for the deterministic seeded PRNG in the synthetic generator), mypy clean. benchmarks/
  run_benchmarks.py measures RQ1-RQ6 across 10 recorded seeds; raw results in benchmarks/results/
  benchmark_results.json + benchmark_summary.md; honest interpretation (including two
  negative/inconclusive findings -- RQ2 no depth-degradation observed, RQ3 ablation was a no-op
  given current fixture richness) in research/benchmark_findings.md.
- Real bugs found and fixed during this pass (kept here since they're genuine engineering
  findings, not noise): schema's `identities` had an unjustified `minItems:1` blocking a valid
  empty-skeleton manifest (removed); `toxicCombinations[].grantRefs` schema requires >=2 refs but
  the generator only emitted 1 (fixed generator to include both the issuer's own grant and the
  delegated grant); synthetic manifests were non-deterministic across identical seeds because
  `metadata.id` used `uuid4()` and `generatedAt` used real wall-clock time instead of the
  fixture's own `base_time` (both fixed); the hand-written `full_example.json` illustrative toxic
  combination didn't actually match any real overlapping grant (fixed by adding grant:1004).

## Repository record
- URL: https://github.com/sunilgentyala/authorization-bom
- Initial commit: 721eef7 ("Initial release: ABOM schema, reference implementation, tests, benchmarks")
- Citation-ledger commit: 10b1c4d
- Default branch: main. CI (Python 3.10-3.13 matrix, Ruff/mypy/Bandit/pytest --cov-fail-under=85)
  and Pages deploy both verified green via `gh run list`/`gh run watch`.
- Site: https://sunilgentyala.github.io/authorization-bom/

## Open questions (unresolved, to revisit)
- Target specific IEEE venue, ACM venue, and Elsevier-Scopus journal — not yet selected; needed
  before drafting venue-specific manuscript versions (Elsevier journal choice additionally needs
  live verification of current Scopus coverage, not assumed from memory).
- Second author Suresh Kumar Darisi's affiliation/email/contribution statement — user explicitly
  chose to leave as a placeholder (CITATION.cff has a TODO comment) rather than reuse unverified
  details from the unrelated HWAAM paper. Must be resolved before any manuscript is submission-ready.
- Whether to run a deeper, database-backed novelty-gate pass (IEEE Xplore/ACM DL/Scopus) before
  final submission -- current novelty gate is web-search-only, disclosed as a limitation.

## Next actions
1. Get venue decisions (specific IEEE conference/journal, specific ACM venue, specific
   Scopus-indexed Elsevier journal) and author-detail resolution from the user before drafting
   manuscripts.
2. Draft venue-neutral master manuscript (Task #13), sourcing every number from
   benchmarks/results/benchmark_results.json and every citation from research/citation_ledger.md.
3. Produce IEEE/ACM/Elsevier versions per their official templates (Tasks #14-16).
4. Run AEGIS integrity checks + final submission-readiness checklist (Task #17).

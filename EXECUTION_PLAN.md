# ABOM (Authorization Bill of Materials) — Execution Plan

Research cutoff / execution date: 2026-07-29
Repository: C:\Gitrepos\authorization-bom (target GitHub: sunilgentyala/authorization-bom, not yet created)
Manuscript workspace: C:\Users\Sunil\Documents\EB1A_local\Academic\ABOM (private, not pushed to GitHub)

## Initial workspace state (recorded 2026-07-29)

- OS: Windows 11 Pro 10.0.26200
- Python: 3.14.4
- Git: 2.55.0.windows.3
- GitHub CLI: authenticated as sunilgentyala (gh auth status verified)
- C:\Gitrepos\authorization-bom: did not exist before this session; created empty, no prior commits
- No existing local or remote (`gh repo list sunilgentyala`) work matches ABOM, AuthBOM, or AzBOM
- Prior related-but-distinct project found: `hwaam-authorization-mesh` (github.com/sunilgentyala/hwaam-authorization-mesh), a finished, tested (41 tests, CI green), Apache-2.0 Python authorization-decision engine ("Human-Workload-Agent Authorization Mesh") with an unsubmitted IEEE paper co-authored by Sunil Gentyala and Suresh Kumar Darisi. Same author pair as this assignment.
  - **Decision (user-confirmed, 2026-07-29): HWAAM is NOT to be rebuilt or modified.** It is treated as existing prior work / a possible interoperability target for ABOM (an authorization *decision engine*), not as something this project redesigns. ABOM's own contribution is the *inventory/evidence artifact* (the manifest format + analysis tooling), which is conceptually downstream of/complementary to engines like HWAAM, OPA, Cedar, etc. Existing repos (hwaam-authorization-mesh and all others) must not be modified by this project.
  - This is disclosed as related work / prior art in the manuscript, with clear scope separation: HWAAM = policy decision engine; ABOM = authorization inventory/evidence format + analysis tooling that could consume decision-engine outputs as one input source.

## Phase gates

1. **Workspace + protocol setup** (this file, PROJECT_STATUS.md, research/search_protocol.md) — gate: files exist and are internally consistent.
2. **Novelty gate** (terminology/naming collision review, systematic literature/standards/repo/patent search, comparison matrix, novelty-gate 6-question verdict) — gate: written verdict on schema necessity vs. profile/extension of an existing standard, before any schema/framework design begins. Framework/schema design MUST NOT start before this gate is documented and passes.
3. **Gap analysis + research questions** — evidence-backed gap matrix, <=6 RQs with hypotheses/variables/baselines/rejection criteria.
4. **Schema + formal model** — versioned JSON Schema (or standard extension/profile), formal temporal-graph definitions.
5. **Threat model**.
6. **Implementation** — Python package + CLI (`authbom ...`), adapters, synthetic dataset generator.
7. **Testing + benchmarks** — pytest, property tests, security tooling (Ruff/Bandit/type-check/secret-scan), coverage target, benchmark harness with recorded seeds.
8. **Repository publication** — new GitHub repo `authorization-bom` only; existing repos untouched; CI/Pages verification.
9. **Citation ledger** — >=20 references, >=15 DOI-verified where literature exists, claim-to-source mapping.
10. **Manuscripts** — venue-neutral master, then IEEE / ACM / Elsevier-Scopus versions per official templates, one venue each, not simultaneous duplicate submission.
11. **Integrity + final checklist** — AEGIS run, proofreading, numeric cross-check against repo results, submission-readiness checklist.

## Deliverables checklist (tracked live in PROJECT_STATUS.md)

See PROJECT_STATUS.md for current phase, completed items, and open questions.

## Hard constraints carried through every phase

- No fabricated citations, DOIs, datasets, benchmark numbers, or statistical significance.
- No modification of any existing repository (hwaam-authorization-mesh or any other in C:\Gitrepos).
- No secrets, tokens, or private tenant data in fixtures/logs/commits.
- No "first/only/unique/unprecedented/state of the art" claims without reproducible evidence recorded in this repo.
- Manuscript files never pushed to the public GitHub repo.
- Only one venue receives a live/near-duplicate submission at a time (the other two versions are prepared but held).

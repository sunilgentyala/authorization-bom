# Changelog

## 0.1.0 -- 2026-07-29

Initial release.

- ABOM JSON Schema (draft 2020-12), versioned `abomVersion: "1.0.0"`, distinguishing declared,
  approved, computed, observed, exception, revoked, and unverified authorization state.
- Reference Python package `authorization-bom` with CLI `authbom`: `import`, `generate`,
  `validate`, `sign`, `verify`, `diff`, `analyze`, `reconcile`, `report`.
- Read-only adapters: Kubernetes RBAC, OPA, Cedar, OpenFGA, OAuth scopes/delegation, MCP
  tool-capability inventories.
- Analysis engine: effective-permission closure with delegation-attenuation correction, delegation
  chain reconstruction/validation, drift detection, toxic-combination (separation-of-duty)
  detection, revocation-convergence measurement, orphan-identity and cross-tenant-reachability
  checks.
- HMAC-SHA256 manifest/grant signing and verification (Ed25519/ECDSA schema-allowed, not yet
  implemented -- see docs/limitations.md).
- Deterministic synthetic multi-tenant topology generator with injected defects (privilege
  amplification, revocation-propagation lag, scope drift, orphaned identities) for reproducible
  benchmarking.
- 76 tests, 94% coverage; Ruff/mypy/Bandit clean.
- Benchmark harness and results for RQ1-RQ6 (research/gap_analysis.md), including two disclosed
  negative/inconclusive findings (see research/benchmark_findings.md).

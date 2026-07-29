# authorization-bom (ABOM)

[![CI](https://github.com/sunilgentyala/authorization-bom/actions/workflows/ci.yml/badge.svg)](https://github.com/sunilgentyala/authorization-bom/actions/workflows/ci.yml)
[![License](https://img.shields.io/badge/license-Apache--2.0-blue.svg)](LICENSE)
[![Python](https://img.shields.io/badge/python-3.10%2B-blue.svg)](pyproject.toml)

**ABOM (Authorization Bill of Materials)** is a versioned, portable schema and reference toolkit
for recording authorization state -- declared, approved, computed-effective, observed-runtime,
exception, revoked, and unverified -- across human, workload, service, application, and AI-agent
identities. It is designed as a candidate profile/extension for SPDX/CycloneDX-style BOM
ecosystems, not a replacement for them.

## What this is, precisely

This project's contribution is an **interoperability schema + reference tooling**, not a novel
authorization algorithm. Effective-permission graph analysis, delegation-reachability analysis,
and toxic-combination/separation-of-duty detection all have established prior art (commercial and
academic), disclosed and compared in [research/comparison_matrix.md](research/comparison_matrix.md)
and [research/novelty_gate.md](research/novelty_gate.md). What appears to be missing from existing
BOM ecosystems (CycloneDX, SPDX) is a shared, versioned artifact that carries authorization state
itself -- across declared/approved/computed/observed/revoked distinctions and across human,
workload, service, and AI-agent identity types together -- which is what this schema and tooling
provide.

## Quick start

```bash
git clone https://github.com/sunilgentyala/authorization-bom.git
cd authorization-bom
python -m pip install -e ".[dev]"

authbom generate --seed 42 --tenants 2 --output manifest.json
authbom validate manifest.json
authbom analyze manifest.json --now 2026-07-29T12:00:00 --output analysis.json
authbom report analysis.json --format markdown --output report.md
```

## CLI

| Command | Purpose |
|---|---|
| `authbom generate` | Produce a deterministic synthetic manifest (for testing/benchmarking) |
| `authbom import` | Parse a read-only source fixture (K8s RBAC, OPA, Cedar, OpenFGA, OAuth, MCP) into a manifest |
| `authbom validate` | Validate a manifest against `schema/abom.schema.json` |
| `authbom sign` | HMAC-sign every grant and attach a manifest-level attestation |
| `authbom verify` | Verify grant signatures and attestations |
| `authbom diff` | Diff two manifests' grants (added/removed/changed) |
| `authbom analyze` | Run effective-permission, delegation, drift, toxic-combination, and revocation analysis |
| `authbom reconcile` | Merge observed runtime-evidence events into a manifest |
| `authbom report` | Render an analysis result as JSON, Markdown, or SARIF |

## Documentation

- [Schema](schema/abom.schema.json) and [example manifests](schema/examples/)
- [Formal model](docs/formal_model.md) -- effective-permission closure, drift, toxic combinations, revocation convergence
- [Threat model](docs/threat_model.md) -- 14 abuse cases and their mitigations/residual risk
- [Architecture](docs/architecture.md)
- [Limitations](docs/limitations.md) -- read this before relying on any specific claim
- [Reproducibility guide](docs/reproducibility.md)
- Research trail: [novelty gate](research/novelty_gate.md), [comparison matrix](research/comparison_matrix.md), [gap analysis / research questions](research/gap_analysis.md), [benchmark findings](research/benchmark_findings.md)

## Security

Every adapter in `src/authbom/adapters/` is read-only and credential-free by design -- it parses
an already-exported fixture, never connects to a live system. See [SECURITY.md](SECURITY.md) for
the vulnerability reporting policy and [docs/threat_model.md](docs/threat_model.md) for the full
threat model.

## Status

Alpha (0.1.0). Synthetic-benchmark-validated only; not yet evaluated against production
authorization estates. See [docs/limitations.md](docs/limitations.md) for the complete, current
list of known gaps.

## License

Apache License 2.0 -- see [LICENSE](LICENSE).

## Citation

See [CITATION.cff](CITATION.cff).

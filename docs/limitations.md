# Limitations

This document collects known, disclosed limitations of ABOM's schema, reference implementation,
and evaluation, consolidated from research/novelty_gate.md, research/gap_analysis.md,
research/benchmark_findings.md, and docs/threat_model.md. It exists so no limitation is scattered
and forgotten across individual files.

## Research / novelty gate

- The novelty-gate search (research/search_log.csv) used general web search/fetch only. It had no
  institutional access to IEEE Xplore, ACM Digital Library, ScienceDirect, Scopus, Web of Science,
  SpringerLink, or structured USPTO/Espacenet claim-level search. A full database-backed pass may
  surface additional directly-competing peer-reviewed work not indexed by general web search.
- "ABOM" as an acronym had one unverified adjacent gloss ("AI/Agent Bill of Materials") surfaced
  by a search-summarization step with no traceable source; disclosed, not suppressed, in
  research/naming_review.md.

## Schema

- No cross-reference/foreign-key validation: JSON Schema cannot enforce that `subjectRef`,
  `resourceRef`, `actionRefs`, or delegation-chain `issuer`/`subject` strings resolve to an actual
  `Identity`/`Resource`/`Action` record elsewhere in the document. The reference engine performs
  some of these checks in Python (e.g. `engine/graph_checks.py` orphan detection), but a manifest
  with a dangling reference is still schema-valid.
- Signature/format assertions (`format: date-time`, `format: uri-reference`) are declared in the
  schema but are **not strictly enforced** by this project's validator unless the optional
  `jsonschema[format]` extras (e.g. `rfc3339-validator`) are installed, which they are not by
  default in `pyproject.toml`. Structural validation (required fields, enums, types, `const`,
  `additionalProperties: false`) is fully enforced; string-format correctness is not. This is a
  real gap between what the schema declares and what `authbom validate` actually checks today.

## Signing

- Only HMAC-SHA256 (symmetric) signing/verification is implemented in `src/authbom/signing.py`,
  even though the schema's `Signature.algorithm` enum also allows `Ed25519` and
  `ECDSA-P256-SHA256` for future interoperability with Sigstore/in-toto-style asymmetric tooling.
  A manifest signed with either of those algorithms cannot be verified by this reference
  implementation as it stands.
- There is no transparency-log / SCITT-style infrastructure. A compromised signing key produces a
  validly-signed but false manifest that this tool cannot distinguish from a legitimate one (see
  docs/threat_model.md T11).

## Adapters

- All adapters are read-only fixture parsers, not live connectors, by design (see docs/
  threat_model.md). They assume an already-exported, already-sanitized fixture; they do not
  discover or authenticate to a live Kubernetes/OPA/Cedar/OpenFGA/OAuth/MCP endpoint.
- Adapter output is inconsistent in one respect: `k8s_rbac.py` and `mcp.py` populate the
  manifest's `actions` array explicitly; `opa.py`, `oauth.py`, and `relationship_engines.py` do
  not (they only reference action ids inside `actionRefs` without a corresponding `Action`
  record). This is schema-valid (actions are not currently a required cross-reference) but is an
  inconsistency worth resolving in a future version rather than a design decision.

## Engine / formal model

- All effective-permission, delegation, drift, toxic-combination, orphan, and cross-tenant checks
  are validated only against this project's own synthetic fixtures (research/gap_analysis.md,
  "threats to validity" per RQ). No claim generalizes to a real production authorization estate.
- `engine/delegation.py`'s privilege-amplification check is a **manifest-internal consistency**
  check (`actionRefs` vs. the chain's own recorded `scopeReduction`), not an independent
  ground-truth check. A defect that amplifies privilege *and* removes the corresponding
  `scopeReduction` record (i.e., forges a "clean-looking" but wrong chain) is not detectable from
  the manifest alone -- this would require comparing against an independently-obtained prior
  manifest (`authbom diff`) or out-of-band audit, not something this tool can do unassisted.
- Revocation-convergence time in the synthetic generator is currently a constant (5 minutes) for
  every "resolved" event, not sampled from a distribution -- RQ5's convergence-*time* scaling
  claim is therefore unmeasured; only convergence-*count* scaling was actually measured (see
  research/benchmark_findings.md).
- RQ3's temporal-context-vs-snapshot-diff ablation was inconclusive because the current synthetic
  generator emits only one `runtimeEvidence` event per grant, making the ablation a no-op (see
  research/benchmark_findings.md). This is an open item, not a completed negative result.

## Benchmarks

- All six RQs were evaluated on synthetic fixtures only, 10 recorded seeds, on one machine
  (Windows 11, Python 3.14.4). No cross-machine, cross-OS, or production-scale reproduction has
  been performed.
- RQ6's overhead measurements only go up to a "large" fixture of 228 grants; behavior at
  thousands-of-grants scale (relevant to `H_max` and the graph-expansion-DoS discussion in docs/
  threat_model.md T14) is untested.

## Manuscript / citation status

- As of this writing, the second author's (Suresh Kumar Darisi) affiliation and contribution
  statement for this specific ABOM manuscript are a placeholder, pending confirmation -- not
  fabricated, explicitly marked TODO in the manuscript draft.
- No manuscript has been submitted to any venue as of this writing.

# ABOM Novelty-Gate Search Protocol

Research cutoff / execution date: 2026-07-29
Reviewer: Sunil Gentyala (assisted by Claude Code, this session)

## Scope

Determine whether an "Authorization Bill of Materials" concept (recording identities,
resources/actions, direct/inherited/delegated/transitive authority, policy provenance,
declared/approved/computed/observed/drifted/revoked authorization state, and cryptographic
attestation) already exists as a named artifact, standard, extension, or shipping product,
and whether existing BOM/authorization standards already cover the requirement through
extension points.

## Access constraints (recorded honestly, not assumed away)

This session has web access only through general web search/fetch (WebSearch/WebFetch tools).
It does NOT have:
- Direct IEEE Xplore, ACM Digital Library, ScienceDirect, Scopus, or Web of Science full-text
  database query access (no institutional login in this session).
- USPTO/Google Patents/Espacenet structured query access beyond what is publicly indexable
  via web search.

Where a claim below rests on a publicly indexed abstract/landing page found via web search
rather than a native database query, this is noted explicitly. Any database that could not
be queried is listed as a limitation in research/novelty_gate.md, not silently treated as
"searched, nothing found."

## Query log format (research/search_log.csv)

Columns: date, database_or_source, exact_query, filters, result_count, inclusion_decision,
exclusion_reason, duplicate_of, evidence_type, full_text_available, source_url

## Planned query families

1. Exact-term collision checks: "Authorization Bill of Materials", "AuthBOM", "AzBOM", "ABOM"
   (security/identity sense), "AIBOM", "AgBOM", "permission manifest", "entitlement manifest".
2. Adjacent-standard extension checks: CycloneDX authorization/entitlement fields, SPDX
   relationship types for authorization, OSCAL component/capability authorization, SaaSBOM
   scope, VEX applicability to authorization findings.
3. Academic/graph-based prior art: "effective permission" graph, delegation graph reachability,
   identity graph authorization, toxic combination / separation-of-duty mining, confused deputy
   detection, agent/MCP/A2A authorization, non-human identity governance.
4. Commercial/OSS category scan: CIEM, IGA, PAM vendors' public docs; OpenFGA, Cedar, Casbin,
   Ranger, Kubernetes RBAC tooling; SPIFFE/SPIRE; Sigstore/in-toto/SLSA attestation of
   authorization claims specifically (not just build provenance).
5. Repository/package-name collision scan: GitHub search, PyPI, npm for `authbom`, `azbom`,
   `abom`, `authorization-bom`.

## PRISMA-style disposition

Records identified -> duplicates removed -> screened by title/abstract -> full text assessed
-> included in comparison matrix -> reasons for exclusion recorded, tracked in
research/prisma_flow.md.

## Rules carried from the assignment

- No claim of "first/only/unique" without reproducible evidence recorded here.
- Vendor marketing pages are recorded as vendor claims, not scientific evidence.
- Every included source gets an evidence URL and access/verification date.

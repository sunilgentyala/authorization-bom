# ABOM Comparison Matrix (Novelty Gate Evidence)

Research cutoff: 2026-07-29. Access limitations: this session used general web search/fetch only
(no IEEE Xplore/ACM DL/ScienceDirect/Scopus/Web of Science institutional query access, no
structured USPTO/Espacenet query access beyond what web search indexes). Entries verified only
through publicly accessible pages are marked accordingly; nothing below is claimed as
database-verified beyond what was actually fetched.

Legend: V = verified against a fetched primary source; S = search-summary only (not independently
fetched, lower confidence); Vd = vendor claim, unverified by independent benchmark.

## 1. Standards / BOM ecosystem

| System | Purpose / maintainer | Version / status (as of 2026-07-29) | Identity model | Effective-permission / delegation analysis | Runtime/drift awareness | Revocation / crypto verification | AI-agent / MCP support | Export format | Verified limitation | Evidence |
|---|---|---|---|---|---|---|---|---|---|---|
| CycloneDX | OWASP flagship SBOM/xBOM standard | Actively evolving 2026, has ML-BOM/SaaSBOM/VEX profiles | Component/service-centric | No effective-permission or delegation concept found | No | Supports signing of the BOM document itself, not authorization-decision revocation | No dedicated MCP/agent-authorization schema found | JSON/XML/Protobuf | (S) No authorization-specific field or profile located via web search of official docs | cyclonedx.org/tool-center |
| SPDX 3.0 | Linux Foundation / ISO-IEC 5962, license & supply-chain transparency | 3.0 profile architecture (Security, Licensing, Build, AI, Dataset) | Element/relationship graph, generic | Relationship types are generic (e.g. "dependsOn"), no authorization-specific relationship type found | No | Security profile covers vulnerability, not authorization revocation | No AI-agent-authorization profile found | RDF/JSON-LD/tag-value | (S) No "Authorization" profile exists in the documented SPDX 3.0 profile list as of search date | interlynk.io/resources/cyclonedx-vs-spdx-sbom-format |
| OSCAL (NIST) | Machine-readable control/compliance documentation | Established, control-catalog focused | Component/control-implementation centric | Not designed for per-identity effective-permission computation | No | No | No | JSON/XML/YAML | (S) Not independently fetched this session; treated per assignment's own framing as a candidate host format, comparison incomplete — logged as a limitation | not independently verified this session |
| in-toto / SLSA / DSSE | Supply-chain step provenance and signing envelope | Mature, widely adopted (Sigstore ecosystem) | Actor-per-step ("Layout" authorizes named functionaries) | in-toto Layouts define who may perform a step; not a general effective-permission/delegation graph | No | Yes — DSSE signing, transparency-log patterns (SCITT-style) | No | in-toto attestation / DSSE envelope | (V) Attests to build-step authorization, not runtime authorization state, drift, or revocation | slsa.dev/spec/v0.1/provenance |

## 2. Academic / preprint prior art (agent & delegation authorization)

| Work | Authors / date | Contribution | Overlap with ABOM | Key difference | Evidence |
|---|---|---|---|---|---|
| "Permission Manifests for Web Agents" | Marro, Chan, Ren, Hammond, et al.; arXiv 2601.02371, v2 2026-01-12 | `agent-permissions.json`, a robots.txt-style manifest for websites to declare allowed agent interactions | Manifest naming and JSON-declaration pattern is close | Scoped to website-to-web-agent interaction declarations, not an enterprise-wide, cross-identity-type (human/workload/service/agent) inventory of declared+approved+computed+observed+revoked authorization state; no delegation-chain or effective-permission graph described in the abstract | (V) arxiv.org/abs/2601.02371 |
| "Authorization Propagation in Multi-Agent AI Systems: Identity Governance as Infrastructure" | Krti Tallam; arXiv 2605.05440, 2026-05-06 | Formalizes "authorization propagation" across multi-agent workflows; invocation-bound capability tokens, task-scoped authorization envelopes, dependency-graph policy enforcement, execution-count revocation | Directly adjacent: treats authorization as a graph tied to execution topology, addresses revocation | Runtime enforcement/architecture contribution, not a static or exportable BOM/manifest artifact format for audit/evidence purposes | (V) arxiv.org/abs/2605.05440 |
| "OpenID Connect for Agents (OIDC-A) 1.0" | arXiv 2509.25974, 2025-09 | OIDC extension: agent identity, delegation-chain validation (scope reduction, consent, time-bounding, revocation), attestation verification, capability-based authorization | Directly overlaps ABOM's "delegation chain" and "credential lifetime" fields | Protocol/token-format standard for live authentication/authorization exchange, not a discovery/inventory/evidence artifact that records authorization state after the fact across multiple systems | (S) not independently fetched full text this session; summary from search only | arxiv.org/abs/2509.25974 |
| US11757886B2 / US12034727 (Amazon Technologies) | Cook, Rungta, Varming, Peebles, Kroening, et al.; granted 2024/2022-application family | "Analysis of role reachability with/using transitive tags / policy complements" — static graph analysis of whether an AWS IAM role can assume another role given tag-based policy conditions | Directly overlaps ABOM's "delegation reachability" formal-model goal | Scoped to a single cloud provider's IAM role-assumption graph; not cross-system, not human/agent-inclusive, not packaged as a portable evidence manifest, no observed-vs-declared drift concept | (S) claims summarized from Justia/Google Patents search result text, not full claim-set review | patents.google.com/patent/US11757886 |

## 3. Commercial products (CIEM / IGA / MCP governance)

| Product / category | Maintainer | Effective-permission / graph | Non-human & AI-agent identity | Drift detection | Revocation convergence | Export/interop format | Evidence type |
|---|---|---|---|---|---|---|---|
| Veza "Access Graph" / "Access AuthZ" | Veza (commercial) | Yes — normalizes permissions across cloud/SaaS into effective access | Vendor states support for AI-agent and non-human identities at scale | Vendor-claimed, not independently verified | Not detailed in available pages | Proprietary platform; no evidence of an open, portable manifest export format | (Vd) vendor page, no independent benchmark | veza.com/search-access-graph |
| SailPoint Identity Security Cloud | SailPoint (commercial) | Reporting-level SoD/toxic-combination visibility | Growing non-human identity coverage (per vendor/market pages) | Not detailed | Not detailed | Proprietary | (Vd) documentation.sailpoint.com |
| Saviynt | Saviynt (commercial) | Transaction-level SoD for ERP (SAP/Oracle EBS), function-code granularity | Yes, per vendor comparison pages | Not detailed | Not detailed | Proprietary | (Vd) saviynt.com |
| MCP gateway category (Arcade, Strata, Obot, Aptible, MintMCP, LangProtect, Agensi et al.) | Multiple commercial vendors, active 2026 category | Runtime tool-level access control + inventory/discovery of MCP servers | Yes — this is their core scope | Some vendors claim continuous discovery | Some vendors claim audit logging | Mostly proprietary gateway logs; Anthropic-facilitated Security Interest Group (chartered June 2026) is scoping tamper-evident tool-call records but no shipped open standard found | (Vd/S) multiple vendor blog posts, one community-group reference | mintmcp.com/blog/ai-agent-security |

## Summary judgment feeding the novelty gate

1. No source found (standard, patent, product, or preprint) packages authorization state as a
   **portable, versioned, cross-identity-type (human + workload + service + AI-agent) evidence
   manifest** distinguishing declared / approved / computed / observed / drifted / revoked states,
   analogous to how CycloneDX/SPDX package component inventories. This specific combination is the
   candidate contribution.
2. The **individual mechanisms** are not novel and must not be claimed as such:
   - Effective-permission graphs: commercialized (Veza) and patented in the IAM-role-reachability
     case (Amazon, US11757886B2 family).
   - Delegation chains for agents: already being standardized (OIDC-A).
   - Manifest-style declared permissions for agents: already proposed (arXiv 2601.02371).
   - Toxic-combination/SoD detection: mature commercial capability (SailPoint, Saviynt).
   - Signed attestation of a decision/step: mature (in-toto/DSSE/SLSA/Sigstore).
3. CycloneDX/SPDX/OSCAL currently have **no authorization-specific profile**, based on the
   documentation surfaced this session — this is the most defensible, narrow gap: an
   interoperability gap, not an algorithmic one.

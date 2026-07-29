# ABOM Novelty Gate — Verdict

Research cutoff: 2026-07-29. Based on research/search_log.csv and research/comparison_matrix.md.
This verdict must be reached before any schema or framework design begins (assignment Section 4).

## Access limitations (disclosed, not assumed away)

This session had general web search/fetch access only. It did NOT have institutional query
access to IEEE Xplore, ACM Digital Library, ScienceDirect, Scopus, Web of Science, SpringerLink,
or structured USPTO/Espacenet claim-level search. Findings below rely on: arXiv preprints (fetched
directly), Google/Justia patent search-result summaries (not full claim sets), vendor
documentation/blog pages (vendor claims, not independently benchmarked), and standards-body public
docs (CycloneDX, SPDX, SLSA/in-toto). This is a real, material limitation on the completeness of
this novelty gate, not a formality — a full IEEE Xplore/ACM DL/Scopus pass could surface additional
directly-competing peer-reviewed work not indexed by general web search. This must be repeated with
database access before final submission-readiness sign-off (see PROJECT_STATUS.md open questions).

## Answers to the six required questions

**1. Does an authorization-specific BOM already exist?**
No standard, product, or preprint found packages authorization state itself (as opposed to
software components) as a portable BOM-style artifact. The closest terminology hit, "Permission
Manifests for Web Agents" (arXiv 2601.02371), is a website-to-agent interaction manifest
(robots.txt-style), not a cross-identity-type enterprise authorization inventory. No exact-phrase
or acronym collision ("Authorization Bill of Materials", "AuthBOM") was found in a security sense.
A collision exists on the literal string "azbom" (dtylman/azbom, a Go tool for Azure component
SBOMs — unrelated domain, 0 stars, inactive since Jan 2025) — see research/naming_review.md.

**2. Can CycloneDX, SPDX, OSCAL, AgBOM, or another format represent the required information
through existing fields or extensions?**
Partially, and with a real gap. SPDX 3.0's profile architecture (Security, Licensing, Build, AI,
Dataset) is exactly the kind of extension point an "Authorization" profile could occupy, but no
such profile was found as of the search date. CycloneDX has no discovered authorization-specific
schema field either. OSCAL was not independently re-verified this session (logged limitation above)
— this must be closed before finalizing the schema-necessity claim. Provisional conclusion: a
**profile/extension of an existing format is more interoperable and defensible than an unrelated
standalone schema**, but ABOM may still need a standalone reference schema in the short term if
extending CycloneDX/SPDX/OSCAL upstream is out of scope for this project, with explicit language
in the manuscript recommending eventual upstreaming rather than claiming a new standard is
warranted.

**3. Which proposed fields or workflows are genuinely missing?**
- A single artifact that carries declared, approved, computed-effective, observed-runtime,
  exception, revoked, and missing/unverified authorization state together, versioned and diffable
  like a component BOM.
- Explicit first-class treatment of AI-agent/MCP tool-capability authorization alongside human and
  workload identities in the same document (adjacent commercial work — the MCP-gateway category —
  is runtime enforcement/logging, not a portable evidence document).
- A documented mapping between this authorization evidence and existing SBOM/AI-BOM artifacts (so
  an authorization evidence bundle can travel with a software/AI supply-chain evidence bundle).

**4. Is a new schema necessary, or would a profile or extension be more interoperable?**
A profile/extension is the more defensible position given the evidence above. This project will
build ABOM as a **standalone reference schema explicitly designed to be proposable as a future
SPDX/CycloneDX profile**, and will state this positioning honestly in the manuscript rather than
claiming a new standard is required. This is an engineering/interoperability contribution, not a
claim that existing standards are inadequate in principle.

**5. Is the contribution scientific, engineering-focused, or primarily terminological?**
Primarily an **engineering/interoperability contribution** (schema + reference tooling +
formalized effective-permission/drift definitions), with a secondary, narrow **empirical**
component (measuring detection precision/recall/latency on a synthetic benchmark, ablations). It
is explicitly NOT a novel algorithm contribution — effective-permission graph computation and
delegation-reachability analysis are prior art (Veza commercially, Amazon's role-reachability
patent family academically/legally). The paper must not claim algorithmic novelty for those parts.

**6. Are ABOM and HWAAM defensible names?**
- ABOM: defensible for use in this project with a disclosed-collision footnote (see
  research/naming_review.md for detail on the "azbom" repo and the unverified "AI/Agent Bill of
  Materials" gloss surfaced by one search summary but not confirmed by any actual source page).
- HWAAM: out of scope for this project per user instruction (2026-07-29) — HWAAM already exists
  as the user's own separate, completed, unsubmitted work and is not being renamed, redesigned, or
  touched here. This project cites it as related prior work only.

## Narrowed contribution statement (carried into schema design and manuscript)

ABOM contributes: (a) a versioned schema unifying declared/approved/computed/observed/exception/
revoked/unverified authorization state across human, workload, service, and AI-agent identities,
positioned as a candidate SPDX/CycloneDX-style profile rather than a competing standard; (b) an
open-source reference implementation (generation, validation, signing/verification, diffing,
effective-permission and drift/toxic-combination analysis, reporting) built against synthetic
fixtures; (c) a synthetic benchmark and ablation study bounded to the tested environment. It does
NOT claim to invent effective-permission graph analysis, delegation-chain modeling, or
toxic-combination detection — each of those is prior art, cited and compared, not reproduced as if
new.

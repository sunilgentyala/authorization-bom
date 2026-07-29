# ABOM Naming Review

Research cutoff: 2026-07-29.

## Candidates considered
ABOM, AuthBOM, AzBOM (rejected up front — collides with "Azure", and with the existing
`dtylman/azbom` repo).

## Findings

| Name | GitHub repo collision | PyPI collision | Exact-phrase web collision | Other domain collision |
|---|---|---|---|---|
| `authorization-bom` (repo) | None (github.com/sunilgentyala/authorization-bom does not exist) | None (404) | None | None found |
| ABOM (acronym) | — | None (`abom-security` 404; bare `abom` not separately checked as it is a 4-letter generic string, high false-positive rate for a package-name check) | No source found defining "ABOM" as an authorization/security term. One WebSearch tool summary asserted "ABOM = AI/Agent Bill of Materials" but every cited link in that result was a generic SBOM explainer page (Medium/OneKey/OX Security/etc.) — none of them actually contains that definition. **Treated as an unverified/likely-fabricated gloss from the search-summarization step, not evidence**, per this project's rule against treating model output as a citation. | None found in manufacturing/bioinformatics contexts during this search |
| AuthBOM | None found | None (404) | None found | None found |
| AzBOM | `dtylman/azbom` — real, active-ish (last commit 2025-01-19), Go tool, "Smart Azure Software BOM" — a component/dependency SBOM for Azure resources, NOT an authorization concept | azbom 404 on PyPI (repo exists on GitHub only) | "Az" prefix strongly reads as Microsoft Azure in a cloud/security audience | Rejected for this reason alone, independent of the repo collision |

## Recommendation

Use **ABOM** as the concept/acronym and **`authorization-bom`** as the GitHub repository and Python
package name. Rationale:
- No security/authorization-domain source uses "ABOM" currently.
- The one adjacent gloss ("AI/Agent Bill of Materials") found in a search summary could not be
  traced to any real source and is disclosed here as a caveat, not suppressed.
- `authorization-bom` avoids the "Az" collision entirely and is unclaimed on both GitHub and PyPI
  as of 2026-07-29.

## Residual risk to disclose in the manuscript

State explicitly in the terminology section that "ABOM" is used here specifically to mean
Authorization Bill of Materials, that no standards body currently reserves this acronym, and that
if a future community effort defines "AI/Agent Bill of Materials" under the same acronym, the two
should be distinguished by full expansion, not acronym alone. This mirrors the assignment's own
instruction to disclose naming collisions rather than hide them.

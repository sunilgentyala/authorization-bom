from __future__ import annotations

from typing import Any


def render(result: dict[str, Any]) -> str:
    lines = ["# ABOM Analysis Report", "", f"Manifest: `{result.get('manifestId', 'unknown')}`", ""]

    lines.append("## Delegation chain issues")
    delegation = result.get("delegation", [])
    unclean = [d for d in delegation if not d.get("clean", True)]
    if not delegation:
        lines.append("No delegated grants found.")
    elif not unclean:
        lines.append(f"All {len(delegation)} delegated grant(s) passed chain-consistency checks.")
    else:
        for d in unclean:
            lines.append(f"- **{d['grantId']}** (depth {d['depth']}): {'; '.join(d['issues'])}")
    lines.append("")

    lines.append("## Drift findings")
    drift = result.get("drift", [])
    if not drift:
        lines.append("No drift detected.")
    else:
        for d in drift:
            lines.append(f"- **{d['grantId']}** [{d['type']}]: {d['detail']}")
    lines.append("")

    lines.append("## Toxic combinations")
    toxic = result.get("toxicCombinations", [])
    if not toxic:
        lines.append("None detected.")
    else:
        for t in toxic:
            lines.append(f"- **{t['grantId']}**: rule `{t['rule']}`, issuer `{t['issuer']}` on `{t['resourceRef']}`")
    lines.append("")

    lines.append("## Orphaned identities")
    orphans = result.get("orphans", [])
    lines.append("None found." if not orphans else "\n".join(f"- {o}" for o in orphans))
    lines.append("")

    lines.append("## Cross-tenant grants")
    cross = result.get("crossTenant", [])
    if not cross:
        lines.append("None found.")
    else:
        for c in cross:
            lines.append(f"- **{c['grantId']}**: {c['subjectTenant']} -> {c['resourceTenant']}")
    lines.append("")

    revocation = result.get("revocation", {})
    lines.append("## Revocation convergence")
    summary = revocation.get("summary", {})
    if summary:
        lines.append(f"- Total revocations: {summary.get('total_revocations', 0)}")
        lines.append(f"- Converged: {summary.get('converged_count', 0)}")
        lines.append(f"- Unresolved: {summary.get('unresolved_count', 0)}")
        if "mean_convergence_seconds" in summary:
            lines.append(f"- Mean convergence: {summary['mean_convergence_seconds']:.1f}s")
    else:
        lines.append("No revocation events.")

    return "\n".join(lines) + "\n"

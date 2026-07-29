"""Read-only adapter for Cedar-style policy statements and OpenFGA-style relationship tuples.

Expected fixture shape (already-exported, not a live connection):

{
  "engine": "cedar" | "openfga",
  "statements": [
    {"principal": "user:alice", "action": "read", "resource": "resource:orders-api", "effect": "permit"}
  ]
}

OpenFGA relationship tuples (`user`/`relation`/`object`) are normalized the same way, with
`relation` treated as the action name and effect always "permit" (OpenFGA tuples are additive by
construction).
"""

from __future__ import annotations

from typing import Any

from authbom.adapters._common import empty_fragment
from authbom.manifest import now_iso


def parse(fixture: dict[str, Any], grant_id_prefix: str = "grant:rel") -> dict[str, Any]:
    fragment = empty_fragment()
    engine = fixture.get("engine", "cedar")
    counter = 0

    for stmt in fixture.get("statements", []):
        if engine == "openfga":
            principal, action, resource, effect = stmt["user"], stmt["relation"], stmt["object"], "permit"
        else:
            principal, action, resource, effect = (
                stmt["principal"],
                stmt["action"],
                stmt["resource"],
                stmt.get("effect", "permit"),
            )
        if effect != "permit":
            continue  # explicit denies are not emitted as grants; see docs/formal_model.md
        counter += 1
        fragment["grants"].append(
            {
                "id": f"{grant_id_prefix}:{counter:04d}",
                "subjectRef": principal,
                "resourceRef": resource,
                "actionRefs": [f"action:{resource}:{action}"],
                "authorityType": "direct",
                "state": "declared",
                "policyProvenance": {"source": engine, "importedAt": now_iso()},
                "evidenceCompleteness": "complete",
            }
        )
    return fragment

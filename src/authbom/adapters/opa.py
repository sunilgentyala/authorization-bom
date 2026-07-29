"""Read-only adapter for OPA (Open Policy Agent) policy-metadata fixtures.

Expected fixture shape (an already-exported summary of policy decisions/metadata, not a live
OPA connection):

{
  "policies": [
    {
      "id": "policy-billing",
      "version": "4",
      "allow": [{"subject": "workload:orders-service", "resource": "resource:billing-db", "actions": ["read"]}]
    }
  ]
}
"""

from __future__ import annotations

from typing import Any

from authbom.adapters._common import empty_fragment
from authbom.manifest import now_iso


def parse(fixture: dict[str, Any], grant_id_prefix: str = "grant:opa") -> dict[str, Any]:
    fragment = empty_fragment()
    counter = 0
    for policy in fixture.get("policies", []):
        for rule in policy.get("allow", []):
            counter += 1
            action_refs = [f"action:{rule['resource']}:{a}" for a in rule.get("actions", [])]
            fragment["grants"].append(
                {
                    "id": f"{grant_id_prefix}:{counter:04d}",
                    "subjectRef": rule["subject"],
                    "resourceRef": rule["resource"],
                    "actionRefs": action_refs,
                    "authorityType": "conditional" if rule.get("condition") else "direct",
                    "state": "declared",
                    "policyProvenance": {
                        "source": "opa",
                        "policyId": policy["id"],
                        "policyVersion": str(policy.get("version", "")),
                        "importedAt": now_iso(),
                    },
                    "constraints": (
                        {"conditions": [rule["condition"]]} if rule.get("condition") else None
                    ),
                    "evidenceCompleteness": "complete",
                }
            )
    for grant in fragment["grants"]:
        if grant.get("constraints") is None:
            grant.pop("constraints", None)
    return fragment

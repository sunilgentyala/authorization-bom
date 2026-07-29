"""Read-only adapter for OAuth scope and delegation-record fixtures.

Expected fixture shape (already-exported token-introspection-style records, not a live token
endpoint):

{
  "grants": [
    {
      "subject": "workload:orders-service",
      "resource": "resource:billing-db",
      "scopes": ["read"],
      "client_id": "orders-service-client",
      "expires_at": "2026-07-30T00:00:00Z",
      "delegation_chain": [{"issuer": "user:suresh", "subject": "workload:orders-service"}]
    }
  ]
}
"""

from __future__ import annotations

from typing import Any

from authbom.adapters._common import empty_fragment
from authbom.manifest import now_iso


def parse(fixture: dict[str, Any], grant_id_prefix: str = "grant:oauth") -> dict[str, Any]:
    fragment = empty_fragment()
    counter = 0
    for record in fixture.get("grants", []):
        counter += 1
        chain = record.get("delegation_chain")
        delegation_chain = None
        if chain:
            delegation_chain = [
                {"hop": i, "issuer": hop["issuer"], "subject": hop["subject"]}
                for i, hop in enumerate(chain)
            ]
        grant: dict[str, Any] = {
            "id": f"{grant_id_prefix}:{counter:04d}",
            "subjectRef": record["subject"],
            "resourceRef": record["resource"],
            "actionRefs": [f"action:{record['resource']}:{scope}" for scope in record.get("scopes", [])],
            "authorityType": "delegated" if delegation_chain else "direct",
            "state": "declared",
            "policyProvenance": {
                "source": "oauth_scope",
                "policyId": record.get("client_id"),
                "importedAt": now_iso(),
            },
            "evidenceCompleteness": "complete",
        }
        if delegation_chain:
            grant["delegationChain"] = delegation_chain
        if record.get("expires_at"):
            grant["constraints"] = {"temporal": {"notAfter": record["expires_at"]}}
        fragment["grants"].append(grant)
    return fragment

"""Read-only adapter for MCP (Model Context Protocol) tool-capability inventory fixtures.

Expected fixture shape (an already-exported inventory of an MCP server's tools and which
principals -- human, workload, or agent -- may invoke each one; not a live MCP connection):

{
  "servers": [
    {
      "id": "resource:mcp-payments-server",
      "tools": [
        {"name": "refund-tool", "allowed_principals": ["agent:reconciliation-agent"]}
      ]
    }
  ]
}
"""

from __future__ import annotations

from typing import Any

from authbom.adapters._common import empty_fragment, ensure_resource
from authbom.manifest import now_iso


def parse(fixture: dict[str, Any], grant_id_prefix: str = "grant:mcp") -> dict[str, Any]:
    fragment = empty_fragment()
    counter = 0
    for server in fixture.get("servers", []):
        server_id = server["id"]
        ensure_resource(fragment, server_id, "mcp_server")
        for tool in server.get("tools", []):
            action_id = f"action:{server_id}:{tool['name']}"
            fragment["actions"].append({"id": action_id, "resourceRef": server_id, "name": tool["name"]})
            for principal in tool.get("allowed_principals", []):
                counter += 1
                fragment["grants"].append(
                    {
                        "id": f"{grant_id_prefix}:{counter:04d}",
                        "subjectRef": principal,
                        "resourceRef": server_id,
                        "actionRefs": [action_id],
                        "authorityType": "direct",
                        "state": "declared",
                        "policyProvenance": {
                            "source": "mcp",
                            "policyId": f"{server_id}:{tool['name']}",
                            "importedAt": now_iso(),
                        },
                        "evidenceCompleteness": "complete",
                    }
                )
    return fragment

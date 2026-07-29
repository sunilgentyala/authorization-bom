"""Read-only adapter for Kubernetes RBAC fixtures.

Expected fixture shape (a simplified, already-exported view of RBAC objects -- not a live
cluster connection):

{
  "roles": [{"name": "pod-reader", "namespace": "ns1", "resources": ["pods"], "verbs": ["get", "list"]}],
  "roleBindings": [{"subject": {"kind": "User", "name": "alice"}, "roleRef": "pod-reader", "namespace": "ns1"}]
}

`subject.kind` of "User"/"Group" maps to identity type "human"; "ServiceAccount" maps to "workload".
"""

from __future__ import annotations

from typing import Any

from authbom.adapters._common import empty_fragment, ensure_action, ensure_identity, ensure_resource
from authbom.manifest import now_iso

_KIND_TO_IDENTITY_TYPE = {"User": "human", "Group": "human", "ServiceAccount": "workload"}


def parse(fixture: dict[str, Any], grant_id_prefix: str = "grant:k8s") -> dict[str, Any]:
    fragment = empty_fragment()
    roles_by_name = {r["name"]: r for r in fixture.get("roles", [])}
    counter = 0

    for binding in fixture.get("roleBindings", []):
        subject = binding["subject"]
        identity_type = _KIND_TO_IDENTITY_TYPE.get(subject["kind"], "human")
        subject_id = f"{'workload' if identity_type == 'workload' else 'user'}:{subject['name']}"
        ensure_identity(fragment, subject_id, identity_type, tenant=binding.get("namespace"))

        role = roles_by_name.get(binding["roleRef"])
        if role is None:
            continue
        namespace = binding.get("namespace", role.get("namespace"))
        action_ids = []
        for resource_kind in role.get("resources", []):
            resource_id = f"resource:k8s:{namespace}:{resource_kind}"
            ensure_resource(fragment, resource_id, "kubernetes_object", tenant=namespace)
            for verb in role.get("verbs", []):
                action_ids.append(ensure_action(fragment, resource_id, verb))

        for resource_kind in role.get("resources", []):
            resource_id = f"resource:k8s:{namespace}:{resource_kind}"
            counter += 1
            fragment["grants"].append(
                {
                    "id": f"{grant_id_prefix}:{counter:04d}",
                    "subjectRef": subject_id,
                    "resourceRef": resource_id,
                    "actionRefs": [a for a in action_ids if a.startswith(f"action:{resource_id}:")],
                    "authorityType": "direct" if identity_type == "human" else "inherited",
                    "state": "declared",
                    "policyProvenance": {
                        "source": "kubernetes_rbac",
                        "policyId": binding["roleRef"],
                        "importedAt": now_iso(),
                    },
                    "evidenceCompleteness": "complete",
                }
            )
    return fragment

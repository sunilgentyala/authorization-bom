from authbom.adapters import k8s_rbac, mcp, oauth, opa, relationship_engines
from authbom.manifest import merge, new_manifest, validate


def _validated(fragment):
    merged = merge(new_manifest(), fragment)
    errors = validate(merged)
    assert errors == [], errors
    return merged


def test_k8s_rbac_adapter_produces_valid_fragment():
    fixture = {
        "roles": [{"name": "pod-reader", "namespace": "ns1", "resources": ["pods"], "verbs": ["get", "list"]}],
        "roleBindings": [
            {"subject": {"kind": "User", "name": "alice"}, "roleRef": "pod-reader", "namespace": "ns1"},
            {"subject": {"kind": "ServiceAccount", "name": "svc1"}, "roleRef": "pod-reader", "namespace": "ns1"},
        ],
    }
    fragment = k8s_rbac.parse(fixture)
    merged = _validated(fragment)
    types = {i["id"]: i["type"] for i in merged["identities"]}
    assert types["user:alice"] == "human"
    assert types["workload:svc1"] == "workload"
    assert len(merged["grants"]) == 2


def test_opa_adapter_produces_valid_fragment():
    fixture = {
        "policies": [
            {
                "id": "policy-1",
                "version": "2",
                "allow": [
                    {"subject": "workload:svc", "resource": "resource:data", "actions": ["read"]},
                    {"subject": "user:bob", "resource": "resource:data", "actions": ["read"], "condition": "mfa==true"},
                ],
            }
        ]
    }
    fragment = opa.parse(fixture)
    merged = _validated(fragment)
    assert len(merged["grants"]) == 2
    conditional = next(g for g in merged["grants"] if g["subjectRef"] == "user:bob")
    assert conditional["authorityType"] == "conditional"
    assert conditional["constraints"]["conditions"] == ["mfa==true"]


def test_cedar_adapter_skips_explicit_denies():
    fixture = {
        "engine": "cedar",
        "statements": [
            {"principal": "user:alice", "action": "read", "resource": "resource:x", "effect": "permit"},
            {"principal": "user:mallory", "action": "read", "resource": "resource:x", "effect": "forbid"},
        ],
    }
    fragment = relationship_engines.parse(fixture)
    merged = _validated(fragment)
    subjects = {g["subjectRef"] for g in merged["grants"]}
    assert "user:alice" in subjects
    assert "user:mallory" not in subjects


def test_openfga_adapter_maps_tuples():
    fixture = {"engine": "openfga", "statements": [{"user": "user:alice", "relation": "viewer", "object": "resource:doc1"}]}
    fragment = relationship_engines.parse(fixture)
    merged = _validated(fragment)
    assert merged["grants"][0]["subjectRef"] == "user:alice"
    assert merged["grants"][0]["policyProvenance"]["source"] == "openfga"


def test_oauth_adapter_handles_delegation_chain():
    fixture = {
        "grants": [
            {
                "subject": "agent:a1",
                "resource": "resource:api1",
                "scopes": ["read"],
                "client_id": "client-1",
                "expires_at": "2026-08-01T00:00:00Z",
                "delegation_chain": [{"issuer": "user:alice", "subject": "agent:a1"}],
            }
        ]
    }
    fragment = oauth.parse(fixture)
    merged = _validated(fragment)
    grant = merged["grants"][0]
    assert grant["authorityType"] == "delegated"
    assert grant["constraints"]["temporal"]["notAfter"] == "2026-08-01T00:00:00Z"


def test_mcp_adapter_produces_valid_fragment():
    fixture = {"servers": [{"id": "resource:mcp1", "tools": [{"name": "refund", "allowed_principals": ["agent:a1", "agent:a2"]}]}]}
    fragment = mcp.parse(fixture)
    merged = _validated(fragment)
    assert len(merged["grants"]) == 2
    assert merged["resources"][0]["type"] == "mcp_server"

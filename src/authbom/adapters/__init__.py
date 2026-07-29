"""Read-only, credential-free fixture adapters that normalize source-system exports into ABOM
manifest fragments. See docs/threat_model.md for the read-only/no-live-credentials boundary every
adapter here must respect."""

from authbom.adapters import k8s_rbac, mcp, oauth, opa, relationship_engines, synthetic  # noqa: F401

ADAPTERS = {
    "kubernetes_rbac": k8s_rbac.parse,
    "opa": opa.parse,
    "cedar": relationship_engines.parse,
    "openfga": relationship_engines.parse,
    "oauth_scope": oauth.parse,
    "mcp": mcp.parse,
}

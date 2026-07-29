"""HMAC-SHA256 signing and verification of ABOM manifests.

The schema (schema/abom.schema.json) allows Ed25519 and ECDSA-P256-SHA256 as signature
algorithms for future interoperability with Sigstore/in-toto-style tooling, but this reference
implementation only implements HMAC-SHA256 -- a symmetric-key scheme adequate for a single
issuer/verifier pair sharing a secret out of band, consistent with how the secret is supplied
(file/env/stdin, never a bare CLI flag by preference). Asymmetric-signature support is an explicit,
disclosed limitation (see docs/limitations.md), not a silently-missing feature.
"""

from __future__ import annotations

import hashlib
import hmac
import json
from typing import Any

from authbom.manifest import now_iso

ALGORITHM = "HMAC-SHA256"


def _canonical_bytes(obj: Any) -> bytes:
    """Deterministic serialization for signing: sorted keys, compact separators."""
    return json.dumps(obj, sort_keys=True, separators=(",", ":")).encode("utf-8")


def _grant_signing_payload(grant: dict[str, Any]) -> dict[str, Any]:
    payload = {k: v for k, v in grant.items() if k != "signature"}
    return payload


def sign_grant(grant: dict[str, Any], secret: str, key_id: str) -> dict[str, Any]:
    payload = _canonical_bytes(_grant_signing_payload(grant))
    digest = hmac.new(secret.encode("utf-8"), payload, hashlib.sha256).hexdigest()
    signed = dict(grant)
    signed["signature"] = {
        "algorithm": ALGORITHM,
        "keyId": key_id,
        "value": digest,
        "signedAt": now_iso(),
    }
    return signed


def verify_grant(grant: dict[str, Any], secrets_by_key_id: dict[str, str]) -> bool:
    signature = grant.get("signature")
    if not signature:
        return False
    if signature.get("algorithm") != ALGORITHM:
        return False
    secret = secrets_by_key_id.get(signature.get("keyId"))
    if secret is None:
        return False
    payload = _canonical_bytes(_grant_signing_payload(grant))
    expected = hmac.new(secret.encode("utf-8"), payload, hashlib.sha256).hexdigest()
    return hmac.compare_digest(expected, signature.get("value", ""))


def sign_manifest(manifest: dict[str, Any], secret: str, key_id: str) -> dict[str, Any]:
    """Sign every grant individually, then attach a manifest-level attestation covering all of
    them (mirrors in-toto's subject-list attestation pattern; see docs/formal_model.md)."""
    signed = dict(manifest)
    signed["grants"] = [sign_grant(g, secret, key_id) for g in manifest.get("grants", [])]
    subject_refs = [g["id"] for g in signed["grants"]]
    attestation_payload = _canonical_bytes({"subjectRefs": subject_refs, "manifestId": manifest["metadata"]["id"]})
    digest = hmac.new(secret.encode("utf-8"), attestation_payload, hashlib.sha256).hexdigest()
    attestations = list(signed.get("attestations", []))
    attestations.append(
        {
            "id": f"attestation:{len(attestations) + 1:04d}",
            "predicateType": "https://abom.dev/attestation/manifest/v1",
            "subjectRefs": subject_refs,
            "signature": {"algorithm": ALGORITHM, "keyId": key_id, "value": digest, "signedAt": now_iso()},
        }
    )
    signed["attestations"] = attestations
    return signed


def verify_manifest(manifest: dict[str, Any], secrets_by_key_id: dict[str, str]) -> dict[str, Any]:
    """Return a report: which grants verify, which attestations verify, and an overall verdict."""
    grant_results = {g["id"]: verify_grant(g, secrets_by_key_id) for g in manifest.get("grants", [])}

    attestation_results = {}
    grants_by_id = {g["id"]: g for g in manifest.get("grants", [])}
    for att in manifest.get("attestations", []):
        signature = att.get("signature", {})
        secret = secrets_by_key_id.get(signature.get("keyId"))
        ok = False
        if secret is not None:
            payload = _canonical_bytes(
                {"subjectRefs": att.get("subjectRefs", []), "manifestId": manifest["metadata"]["id"]}
            )
            expected = hmac.new(secret.encode("utf-8"), payload, hashlib.sha256).hexdigest()
            ok = hmac.compare_digest(expected, signature.get("value", ""))
            ok = ok and all(ref in grants_by_id for ref in att.get("subjectRefs", []))
        attestation_results[att["id"]] = ok

    return {
        "grants": grant_results,
        "attestations": attestation_results,
        "all_grants_valid": all(grant_results.values()) if grant_results else False,
        "all_attestations_valid": all(attestation_results.values()) if attestation_results else False,
    }


__all__ = ["sign_grant", "verify_grant", "sign_manifest", "verify_manifest", "ALGORITHM"]

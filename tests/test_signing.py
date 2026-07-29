import copy

from authbom.adapters.synthetic import generate
from authbom.signing import sign_manifest, verify_manifest


def _fixture():
    doc, _gt = generate(seed=6, tenants=2, defect_rate=0.3)
    return doc


def test_sign_then_verify_round_trip():
    doc = _fixture()
    signed = sign_manifest(doc, secret="s3cret", key_id="k1")
    result = verify_manifest(signed, {"k1": "s3cret"})
    assert result["all_grants_valid"]
    assert result["all_attestations_valid"]


def test_tamper_after_signing_is_detected():
    """T10 (manifest tampering): modifying a signed grant's actionRefs must invalidate its
    signature, since the signature covers the full grant payload."""
    doc = _fixture()
    signed = sign_manifest(doc, secret="s3cret", key_id="k1")
    tampered = copy.deepcopy(signed)
    tampered["grants"][0]["actionRefs"] = tampered["grants"][0].get("actionRefs", []) + ["action:injected:evil"]
    result = verify_manifest(tampered, {"k1": "s3cret"})
    assert result["all_grants_valid"] is False
    assert result["grants"][tampered["grants"][0]["id"]] is False


def test_wrong_secret_fails_verification():
    doc = _fixture()
    signed = sign_manifest(doc, secret="s3cret", key_id="k1")
    result = verify_manifest(signed, {"k1": "wrong-secret"})
    assert result["all_grants_valid"] is False


def test_unknown_key_id_fails_verification():
    doc = _fixture()
    signed = sign_manifest(doc, secret="s3cret", key_id="k1")
    result = verify_manifest(signed, {"some-other-key": "s3cret"})
    assert result["all_grants_valid"] is False


def test_replay_of_grant_signature_onto_different_grant_fails():
    """Replay attack: reuse grant A's signature on grant B's payload. Because the HMAC covers
    the entire grant payload (including id/subjectRef/resourceRef), a copied signature will not
    verify against a different grant's content."""
    doc = _fixture()
    signed = sign_manifest(doc, secret="s3cret", key_id="k1")
    if len(signed["grants"]) < 2:
        return
    grant_a, grant_b = signed["grants"][0], signed["grants"][1]
    grant_b_tampered = copy.deepcopy(grant_b)
    grant_b_tampered["signature"] = copy.deepcopy(grant_a["signature"])
    manifest_tampered = copy.deepcopy(signed)
    manifest_tampered["grants"][1] = grant_b_tampered
    result = verify_manifest(manifest_tampered, {"k1": "s3cret"})
    assert result["grants"][grant_b["id"]] is False

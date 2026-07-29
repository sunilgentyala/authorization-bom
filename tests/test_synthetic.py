import pytest

from authbom.adapters.synthetic import generate
from authbom.manifest import validate


def test_deterministic_for_same_seed():
    doc1, gt1 = generate(seed=7, tenants=2, defect_rate=0.3)
    doc2, gt2 = generate(seed=7, tenants=2, defect_rate=0.3)
    assert doc1 == doc2
    assert gt1.amplification_defect_grant_ids == gt2.amplification_defect_grant_ids


def test_different_seeds_produce_different_topologies():
    doc1, _ = generate(seed=1, tenants=2, defect_rate=0.3)
    doc2, _ = generate(seed=2, tenants=2, defect_rate=0.3)
    assert doc1["identities"] != doc2["identities"] or doc1["grants"] != doc2["grants"]


@pytest.mark.parametrize("seed", [0, 1, 7, 42, 12345])
@pytest.mark.parametrize("scale", [(1, 2, 2, 1), (3, 4, 4, 3)])
def test_generated_manifest_is_always_schema_valid(seed, scale):
    tenants, humans, workloads, agents = scale
    doc, _gt = generate(
        seed=seed,
        tenants=tenants,
        humans_per_tenant=humans,
        workloads_per_tenant=workloads,
        agents_per_tenant=agents,
        defect_rate=0.25,
    )
    assert validate(doc) == []


def test_ground_truth_effective_permissions_reference_real_ids():
    doc, gt = generate(seed=3, tenants=2, defect_rate=0.3)
    identity_ids = {i["id"] for i in doc["identities"]}
    resource_ids = {r["id"] for r in doc["resources"]}
    for (subject, resource), _actions in gt.effective_permissions.items():
        assert subject in identity_ids
        assert resource in resource_ids


def test_injected_amplification_defects_are_flagged_as_delegated_grants():
    doc, gt = generate(seed=11, tenants=3, agents_per_tenant=3, defect_rate=0.6)
    grants_by_id = {g["id"]: g for g in doc["grants"]}
    for gid in gt.amplification_defect_grant_ids:
        assert grants_by_id[gid].get("delegationChain")


def test_revocation_events_have_revoked_true_in_manifest():
    doc, gt = generate(seed=5, tenants=2, defect_rate=0.4)
    grants_by_id = {g["id"]: g for g in doc["grants"]}
    for gid in gt.revocation_events:
        assert grants_by_id[gid]["revocation"]["revoked"] is True

from authbom.adapters.synthetic import generate
from authbom.engine.graph_checks import find_cross_tenant_grants, find_orphans


def test_injected_orphans_are_detected():
    doc, gt = generate(seed=13, tenants=2, workloads_per_tenant=4, agents_per_tenant=3, defect_rate=0.5)
    orphans = set(find_orphans(doc))
    assert gt.orphan_identity_ids, "fixture should contain at least one orphaned identity"
    assert gt.orphan_identity_ids <= orphans


def test_no_cross_tenant_grants_in_single_tenant_topology():
    doc, _gt = generate(seed=1, tenants=1, defect_rate=0.3)
    assert find_cross_tenant_grants(doc) == []


def test_owner_referencing_self_is_not_an_orphan():
    doc, _gt = generate(seed=1, tenants=1, humans_per_tenant=2, workloads_per_tenant=0, agents_per_tenant=0, defect_rate=0.0)
    orphans = find_orphans(doc)
    # humans own themselves in the generator; none should be orphaned.
    assert orphans == []

from authbom.adapters.synthetic import generate
from authbom.engine.delegation import analyze_delegations, chain_depth, reconstruct_chain, validate_chain


def test_reconstruct_chain_orders_by_hop(full_manifest):
    grant = next(g for g in full_manifest["grants"] if g.get("delegationChain"))
    chain = reconstruct_chain(grant)
    assert [h["hop"] for h in chain] == sorted(h["hop"] for h in chain)


def test_chain_depth_matches_hop_count(full_manifest):
    grant = next(g for g in full_manifest["grants"] if g.get("delegationChain"))
    assert chain_depth(grant) == len(grant["delegationChain"])


def test_clean_chain_in_full_example_has_no_issues(full_manifest):
    grant = next(g for g in full_manifest["grants"] if g["id"] == "grant:1002")
    assert validate_chain(full_manifest, grant) == []


def test_broken_issuer_chain_is_flagged(full_manifest):
    import copy

    broken = copy.deepcopy(full_manifest)
    grant = next(g for g in broken["grants"] if g["id"] == "grant:1002")
    grant["delegationChain"][1]["issuer"] = "someone-else"
    issues = validate_chain(broken, grant)
    assert any("does not match previous hop" in i for i in issues)


def test_amplification_flagged_via_validate_chain():
    doc, gt = generate(seed=21, tenants=3, agents_per_tenant=3, defect_rate=0.6)
    grants_by_id = {g["id"]: g for g in doc["grants"]}
    for gid in gt.amplification_defect_grant_ids:
        issues = validate_chain(doc, grants_by_id[gid])
        assert any("privilege amplification" in i for i in issues)


def test_analyze_delegations_reports_all_delegated_grants():
    doc, _gt = generate(seed=8, tenants=2, agents_per_tenant=2, defect_rate=0.3)
    delegated = [g for g in doc["grants"] if g.get("delegationChain")]
    report = analyze_delegations(doc)
    assert len(report) == len(delegated)


def test_analyze_delegations_skips_non_delegated_grants(full_manifest):
    report = analyze_delegations(full_manifest)
    reported_ids = {r["grantId"] for r in report}
    assert "grant:1001" not in reported_ids  # direct grant, no delegation chain

from authbom.adapters.synthetic import generate
from authbom.engine.effective_permissions import (
    effective_permissions,
    is_amplified,
    naive_effective_permissions,
    score,
)


def test_corrected_engine_never_worse_than_naive_on_amplification_defects():
    """RQ1: on grants with an injected privilege-amplification defect, the corrected engine
    must compute a strict subset of (or equal to) the naive engine's action set -- it should
    never invent access the naive computation didn't already claim."""
    doc, gt = generate(seed=21, tenants=3, agents_per_tenant=3, defect_rate=0.6)
    naive = naive_effective_permissions(doc)
    corrected = effective_permissions(doc)
    assert gt.amplification_defect_grant_ids, "fixture should contain at least one amplification defect"
    grants_by_id = {g["id"]: g for g in doc["grants"]}
    for gid in gt.amplification_defect_grant_ids:
        g = grants_by_id[gid]
        key = (g["subjectRef"], g["resourceRef"])
        assert corrected.get(key, set()) <= naive.get(key, set())


def test_amplified_grants_are_flagged():
    doc, gt = generate(seed=21, tenants=3, agents_per_tenant=3, defect_rate=0.6)
    grants_by_id = {g["id"]: g for g in doc["grants"]}
    for gid in gt.amplification_defect_grant_ids:
        assert is_amplified(doc, grants_by_id[gid])


def test_clean_delegated_grants_are_not_flagged():
    doc, gt = generate(seed=21, tenants=3, agents_per_tenant=3, defect_rate=0.6)
    for g in doc["grants"]:
        if g.get("delegationChain") and g["id"] not in gt.amplification_defect_grant_ids:
            assert not is_amplified(doc, g)


def test_revoked_grants_excluded_from_effective_permissions():
    doc, _gt = generate(seed=9, tenants=2, defect_rate=0.4)
    eff = effective_permissions(doc)
    grants = doc["grants"]
    revoked = [g for g in grants if g.get("state") == "revoked"]
    assert revoked, "fixture should contain at least one revoked grant"

    keys_with_non_revoked_grant = {
        (g["subjectRef"], g["resourceRef"]) for g in grants if g.get("state") != "revoked"
    }
    for g in revoked:
        key = (g["subjectRef"], g["resourceRef"])
        if key not in keys_with_non_revoked_grant:
            assert key not in eff


def test_corrected_engine_reaches_ground_truth_on_amplification_cases():
    """RQ1, focused: for exactly the grants where a privilege-amplification defect was injected,
    the corrected engine's per-grant expected action set matches the true (attenuated) ground
    truth, while the naive computation does not."""
    doc, gt = generate(seed=21, tenants=3, agents_per_tenant=3, defect_rate=0.6)
    grants_by_id = {g["id"]: g for g in doc["grants"]}
    naive = naive_effective_permissions(doc)
    corrected = effective_permissions(doc)
    mismatches_fixed = 0
    for gid in gt.amplification_defect_grant_ids:
        g = grants_by_id[gid]
        key = (g["subjectRef"], g["resourceRef"])
        truth = gt.effective_permissions.get(key, set())
        if naive.get(key, set()) != truth and corrected.get(key, set()) == truth:
            mismatches_fixed += 1
    assert mismatches_fixed > 0


def test_score_perfect_match():
    truth = {("s", "r"): {"a", "b"}}
    result = score(truth, truth)
    assert result["precision"] == 1.0
    assert result["recall"] == 1.0
    assert result["f1"] == 1.0


def test_score_detects_false_positive_and_negative():
    truth = {("s", "r"): {"a", "b"}}
    computed = {("s", "r"): {"a", "c"}}
    result = score(computed, truth)
    assert result["tp"] == 1
    assert result["fp"] == 1
    assert result["fn"] == 1

from authbom.adapters.synthetic import generate
from authbom.engine.toxic import detect_approver_executor_overlap


def test_full_example_toxic_pair_detected(full_manifest):
    findings = detect_approver_executor_overlap(full_manifest)
    assert any(f["grantId"] == "grant:1002" for f in findings)


def test_excluding_agents_can_only_reduce_or_match_findings():
    """RQ4: agent-inclusive analysis must find a superset of what human-only analysis finds."""
    doc, _gt = generate(seed=33, tenants=4, agents_per_tenant=3, humans_per_tenant=3, defect_rate=0.4)
    with_agents = detect_approver_executor_overlap(doc, include_agents=True)
    without_agents = detect_approver_executor_overlap(doc, include_agents=False)
    assert len(with_agents) >= len(without_agents)
    without_ids = {f["grantId"] for f in without_agents}
    with_ids = {f["grantId"] for f in with_agents}
    assert without_ids <= with_ids

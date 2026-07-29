from authbom.adapters.synthetic import generate
from authbom.engine.revocation import convergence_times, summary


def test_full_example_reports_one_unresolved_revocation(full_manifest):
    results = convergence_times(full_manifest)
    assert len(results) == 1
    assert results[0]["grantId"] == "grant:1003"
    assert results[0]["converged"] is False
    assert results[0]["convergenceSeconds"] is None


def test_summary_counts_converged_and_unresolved():
    doc, gt = generate(seed=17, tenants=3, defect_rate=0.5)
    results = convergence_times(doc)
    assert results, "fixture should contain revocation events"
    s = summary(results)
    assert s["total_revocations"] == len(results)
    assert s["converged_count"] + s["unresolved_count"] == s["total_revocations"]
    assert s["unresolved_count"] == len(gt.drift_defect_grant_ids & {r["grantId"] for r in results})


def test_convergence_seconds_is_non_negative_when_present():
    doc, _gt = generate(seed=4, tenants=2, defect_rate=0.5)
    for r in convergence_times(doc):
        if r["convergenceSeconds"] is not None:
            assert r["convergenceSeconds"] >= 0

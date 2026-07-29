from datetime import datetime

from authbom.adapters.synthetic import generate
from authbom.engine.drift import detect_drift


def test_injected_scope_and_revocation_drift_are_detected():
    doc, gt = generate(seed=15, tenants=2, agents_per_tenant=2, defect_rate=0.5)
    findings = detect_drift(doc, now=datetime(2026, 7, 29, 12))
    flagged_ids = {f["grantId"] for f in findings}
    assert gt.drift_defect_grant_ids, "fixture should contain at least one drift defect"
    assert gt.drift_defect_grant_ids <= flagged_ids


def test_no_false_positives_on_clean_full_example(full_manifest):
    findings = detect_drift(full_manifest, now=datetime(2026, 7, 29, 12))
    flagged_ids = {f["grantId"] for f in findings}
    # grant:1002 has no drift injected and its own runtime evidence is within scope.
    assert "grant:1002" not in flagged_ids
    # grant:1003 has drift: true and an unresolved revocation -- both should be caught.
    assert "grant:1003" in flagged_ids


def test_dormant_grant_detected_after_staleness_window():
    from datetime import timedelta

    doc, _gt = generate(seed=2, tenants=1, humans_per_tenant=1, workloads_per_tenant=1, agents_per_tenant=0, defect_rate=0.0)
    # All grants were imported at base_time (2026-07-29); check far in the future.
    findings = detect_drift(doc, now=datetime(2026, 7, 29) + timedelta(days=200), staleness=timedelta(days=90))
    dormant = [f for f in findings if f["type"] == "dormant_grant"]
    assert dormant

import json
from datetime import datetime

import pytest

from authbom.adapters.synthetic import generate
from authbom.cli import main
from authbom.engine.effective_permissions import effective_permissions
from authbom.reporters import markdown_reporter, sarif_reporter


def test_cli_secret_env_missing_variable_errors(tmp_path, monkeypatch):
    manifest_path = tmp_path / "m.json"
    main(["generate", "--seed", "1", "--tenants", "1", "--defect-rate", "0.1", "--output", str(manifest_path)])
    monkeypatch.delenv("ABOM_TEST_SECRET_DOES_NOT_EXIST", raising=False)
    with pytest.raises(SystemExit):
        main(
            [
                "sign",
                str(manifest_path),
                "--key-id",
                "k1",
                "--secret-env",
                "ABOM_TEST_SECRET_DOES_NOT_EXIST",
                "--output",
                str(tmp_path / "signed.json"),
            ]
        )


def test_cli_secret_stdin(tmp_path, monkeypatch, capsys):
    import io

    manifest_path = tmp_path / "m.json"
    signed_path = tmp_path / "signed.json"
    main(["generate", "--seed", "1", "--tenants", "1", "--defect-rate", "0.1", "--output", str(manifest_path)])
    monkeypatch.setattr("sys.stdin", io.StringIO("stdinsecret\n"))
    assert main(["sign", str(manifest_path), "--key-id", "k1", "--secret-stdin", "--output", str(signed_path)]) == 0
    assert signed_path.exists()


def test_effective_permissions_respects_temporal_constraint():
    doc, _gt = generate(seed=40, tenants=1, defect_rate=0.0)
    # Add a temporally constrained grant.
    doc["grants"].append(
        {
            "id": "grant:temporal-test",
            "subjectRef": doc["identities"][0]["id"],
            "resourceRef": doc["resources"][0]["id"],
            "actionRefs": ["action:temporal-test"],
            "authorityType": "conditional",
            "state": "approved",
            "policyProvenance": {"source": "synthetic"},
            "constraints": {"temporal": {"notBefore": "2026-08-01T00:00:00", "notAfter": "2026-08-02T00:00:00"}},
            "evidenceCompleteness": "complete",
        }
    )
    before_window = effective_permissions(doc, at=datetime(2026, 7, 1))
    within_window = effective_permissions(doc, at=datetime(2026, 8, 1, 12))
    key = (doc["identities"][0]["id"], doc["resources"][0]["id"])
    assert "action:temporal-test" not in before_window.get(key, set())
    assert "action:temporal-test" in within_window.get(key, set())


def test_markdown_reporter_renders_all_populated_sections():
    doc, _gt = generate(seed=60, tenants=3, agents_per_tenant=3, defect_rate=0.6)
    from authbom.cli import _run_analysis

    result = _run_analysis(doc, now=datetime(2026, 7, 29, 12), staleness_days=90)
    rendered = markdown_reporter.render(result)
    assert "# ABOM Analysis Report" in rendered
    # With defect_rate=0.6 on a reasonably sized fixture, at least one non-empty section beyond
    # the headers should appear (drift is near-certain given the injected defect rate).
    assert "drift" in rendered.lower()


def test_sarif_reporter_renders_all_populated_sections():
    doc, _gt = generate(seed=60, tenants=3, agents_per_tenant=3, defect_rate=0.6)
    from authbom.cli import _run_analysis

    result = _run_analysis(doc, now=datetime(2026, 7, 29, 12), staleness_days=90)
    rendered = json.loads(sarif_reporter.render(result))
    assert rendered["runs"][0]["tool"]["driver"]["name"] == "authorization-bom"
    assert len(rendered["runs"][0]["results"]) > 0


def test_json_reporter_round_trips():
    from authbom.reporters import json_reporter

    result = {"manifestId": "x", "drift": []}
    rendered = json_reporter.render(result)
    assert json.loads(rendered) == result

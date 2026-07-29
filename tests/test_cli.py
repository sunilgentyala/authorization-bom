import json

from authbom.cli import main


def test_generate_validate_analyze_report_pipeline(tmp_path):
    manifest_path = tmp_path / "m.json"
    analysis_path = tmp_path / "a.json"
    report_path = tmp_path / "r.md"

    assert main(["generate", "--seed", "99", "--tenants", "2", "--defect-rate", "0.3", "--output", str(manifest_path)]) == 0
    assert manifest_path.exists()

    assert main(["validate", str(manifest_path)]) == 0

    assert main(["analyze", str(manifest_path), "--now", "2026-07-29T12:00:00", "--output", str(analysis_path)]) == 0
    result = json.loads(analysis_path.read_text(encoding="utf-8"))
    assert "effectivePermissions" in result

    assert main(["report", str(analysis_path), "--format", "markdown", "--output", str(report_path)]) == 0
    assert "ABOM Analysis Report" in report_path.read_text(encoding="utf-8")


def test_validate_rejects_broken_manifest(tmp_path):
    broken_path = tmp_path / "broken.json"
    broken_path.write_text(json.dumps({"abomVersion": "1.0.0"}), encoding="utf-8")
    assert main(["validate", str(broken_path)]) == 1


def test_sign_verify_round_trip_via_cli(tmp_path):
    manifest_path = tmp_path / "m.json"
    signed_path = tmp_path / "signed.json"
    main(["generate", "--seed", "1", "--tenants", "1", "--defect-rate", "0.1", "--output", str(manifest_path)])

    secret_file = tmp_path / "secret.txt"
    secret_file.write_text("topsecret\n", encoding="utf-8")

    assert main(["sign", str(manifest_path), "--key-id", "k1", "--secret-file", str(secret_file), "--output", str(signed_path)]) == 0
    assert main(["verify", str(signed_path), "--key-id", "k1", "--secret-file", str(secret_file)]) == 0

    wrong_secret_file = tmp_path / "wrong.txt"
    wrong_secret_file.write_text("nope\n", encoding="utf-8")
    assert main(["verify", str(signed_path), "--key-id", "k1", "--secret-file", str(wrong_secret_file)]) == 1


def test_diff_reports_added_grant(tmp_path):
    a_path = tmp_path / "a.json"
    b_path = tmp_path / "b.json"
    diff_path = tmp_path / "diff.json"
    main(["generate", "--seed", "1", "--tenants", "1", "--defect-rate", "0.1", "--output", str(a_path)])
    main(["generate", "--seed", "2", "--tenants", "1", "--defect-rate", "0.1", "--output", str(b_path)])

    assert main(["diff", str(a_path), str(b_path), "--output", str(diff_path)]) == 0
    result = json.loads(diff_path.read_text(encoding="utf-8"))
    assert set(result) == {"added", "removed", "changed"}


def test_import_and_merge_via_cli(tmp_path):
    fixture_path = tmp_path / "k8s.json"
    fixture_path.write_text(
        json.dumps(
            {
                "roles": [{"name": "r1", "namespace": "ns1", "resources": ["pods"], "verbs": ["get"]}],
                "roleBindings": [{"subject": {"kind": "User", "name": "alice"}, "roleRef": "r1", "namespace": "ns1"}],
            }
        ),
        encoding="utf-8",
    )
    out_path = tmp_path / "out.json"
    assert main(["import", "--source", "kubernetes_rbac", "--input", str(fixture_path), "--output", str(out_path)]) == 0
    doc = json.loads(out_path.read_text(encoding="utf-8"))
    assert len(doc["grants"]) == 1


def test_reconcile_adds_runtime_evidence(tmp_path):
    manifest_path = tmp_path / "m.json"
    events_path = tmp_path / "events.json"
    out_path = tmp_path / "reconciled.json"
    main(["generate", "--seed", "1", "--tenants", "1", "--defect-rate", "0.0", "--output", str(manifest_path)])
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    first_grant_id = manifest["grants"][0]["id"]
    events_path.write_text(
        json.dumps({"events": [{"grantId": first_grant_id, "observedAt": "2026-07-29T10:00:00Z", "eventType": "api_call", "withinDeclaredScope": True}]}),
        encoding="utf-8",
    )
    assert main(["reconcile", str(manifest_path), "--observed", str(events_path), "--output", str(out_path)]) == 0
    reconciled = json.loads(out_path.read_text(encoding="utf-8"))
    grant = next(g for g in reconciled["grants"] if g["id"] == first_grant_id)
    assert grant["runtimeEvidence"]


def test_report_sarif_format(tmp_path):
    manifest_path = tmp_path / "m.json"
    analysis_path = tmp_path / "a.json"
    sarif_path = tmp_path / "r.sarif.json"
    main(["generate", "--seed", "50", "--tenants", "2", "--defect-rate", "0.5", "--output", str(manifest_path)])
    main(["analyze", str(manifest_path), "--now", "2026-07-29T12:00:00", "--output", str(analysis_path)])
    assert main(["report", str(analysis_path), "--format", "sarif", "--output", str(sarif_path)]) == 0
    sarif = json.loads(sarif_path.read_text(encoding="utf-8"))
    assert sarif["version"] == "2.1.0"

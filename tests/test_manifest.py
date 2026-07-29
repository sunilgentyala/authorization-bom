import json

import pytest

from authbom.manifest import ValidationError, load, merge, new_manifest, save, validate, validate_or_raise


def test_new_manifest_is_valid():
    doc = new_manifest(tenant="t1")
    assert validate(doc) == []
    assert doc["metadata"]["tenant"] == "t1"


def test_validate_or_raise_raises_on_invalid_doc():
    doc = new_manifest()
    del doc["metadata"]
    with pytest.raises(ValidationError):
        validate_or_raise(doc)


def test_json_round_trip(tmp_path):
    doc = new_manifest()
    path = tmp_path / "m.json"
    save(doc, path)
    loaded = load(path)
    assert loaded == doc


def test_yaml_round_trip(tmp_path):
    doc = new_manifest()
    path = tmp_path / "m.yaml"
    save(doc, path)
    loaded = load(path)
    assert loaded == doc


def test_merge_deduplicates_by_id():
    base = new_manifest()
    base["identities"].append({"id": "user:a", "type": "human"})
    addition = new_manifest()
    addition["identities"].append({"id": "user:a", "type": "human", "owner": "updated"})
    addition["identities"].append({"id": "user:b", "type": "human"})
    merged = merge(base, addition)
    ids = {i["id"]: i for i in merged["identities"]}
    assert set(ids) == {"user:a", "user:b"}
    assert ids["user:a"].get("owner") == "updated"  # later entry wins


def test_merge_does_not_mutate_inputs():
    base = new_manifest()
    base["identities"].append({"id": "user:a", "type": "human"})
    base_copy = json.loads(json.dumps(base))
    addition = new_manifest()
    addition["identities"].append({"id": "user:b", "type": "human"})
    merge(base, addition)
    assert base == base_copy

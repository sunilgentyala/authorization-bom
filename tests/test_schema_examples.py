import copy

from authbom.manifest import validate


def test_minimal_example_valid(minimal_manifest):
    assert validate(minimal_manifest) == []


def test_full_example_valid(full_manifest):
    assert validate(full_manifest) == []


def test_missing_required_field_is_rejected(minimal_manifest):
    broken = copy.deepcopy(minimal_manifest)
    del broken["identities"]
    errors = validate(broken)
    assert errors
    assert any("identities" in e for e in errors)


def test_unknown_identity_type_rejected(minimal_manifest):
    broken = copy.deepcopy(minimal_manifest)
    broken["identities"][0]["type"] = "not_a_real_type"
    assert validate(broken)


def test_additional_properties_rejected(minimal_manifest):
    broken = copy.deepcopy(minimal_manifest)
    broken["unexpectedTopLevelField"] = True
    assert validate(broken)


def test_wrong_abom_version_rejected(minimal_manifest):
    broken = copy.deepcopy(minimal_manifest)
    broken["abomVersion"] = "2.0.0"
    assert validate(broken)

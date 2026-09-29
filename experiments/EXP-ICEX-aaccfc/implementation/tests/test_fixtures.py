"""C-1: fixture regeneration byte-compare and frozen hashes."""

import json

import pytest

import common


def test_frozen_hashes_match_amendment():
    assert common.sha256_file(common.FIXTURE_JSON) == common.FROZEN_JSON_SHA256
    assert common.sha256_file(common.FIXTURE_GEN) == common.FROZEN_GEN_SHA256


def test_six_fixtures_as_frozen():
    fx = common.load_fixtures()
    assert sorted((f["bits"], f["seed"]) for f in fx) == [(b, s) for b in (16, 20) for s in (21, 22, 23)]
    for f in fx:
        assert f["N"] < 2 ** 21 and f["p"].bit_length() == f["bits"]


@pytest.mark.skipif(common.find_sage() is None, reason="sage not installed")
def test_generator_reproduces_frozen_json_byte_for_byte(tmp_root):
    out = tmp_root / "fixtures_regenerated.json"
    rep = common.reproduce_fixtures(out)
    assert rep["returncode"] == 0, rep["stderr_tail"]
    assert rep["byte_identical"], rep
    assert rep["reproduced_sha256"] == common.FROZEN_JSON_SHA256
    assert json.loads(out.read_text())["EXP-ICEX-aaccfc"] == common.load_fixtures()

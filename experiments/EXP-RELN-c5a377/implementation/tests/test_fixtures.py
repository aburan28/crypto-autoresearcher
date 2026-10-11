import json
import os
from pathlib import Path

import pytest

import fixtures


def test_frozen_hashes_match_amendment():
    assert fixtures.sha256_file(fixtures.FIXTURE_JSON) == fixtures.FROZEN_JSON_SHA256
    assert fixtures.sha256_file(fixtures.FIXTURE_GEN) == fixtures.FROZEN_GEN_SHA256


def test_nine_fixtures():
    fx = fixtures.load_fixtures()
    assert sorted((f["bits"], f["seed"]) for f in fx) == [(b, s) for b in (16, 20, 24) for s in (11, 12, 13)]
    for f in fx:
        assert f["p"].bit_length() == f["bits"]
        assert f["G"][1] <= (f["p"] - 1) // 2  # canonical generator (anchor sign +1)


@pytest.mark.parametrize("n", [2, 7, 62417, 855727, 15738469, 10 ** 12 + 39])
def test_iroot_ceil_exact(n):
    for num, den in ((1, 5), (2, 5), (1, 2), (3, 5)):
        r = fixtures.iroot_ceil(n, num, den)
        assert r ** den >= n ** num and (r - 1) ** den < n ** num


def test_params_b16_s11():
    prm = fixtures.params(fixtures.fixture(16, 11))
    assert (prm["B"], prm["B2"], prm["A1"], prm["A2"]) == (10, 83, 249, 751)


@pytest.mark.skipif(fixtures.find_sage() is None or os.environ.get("RELN_SKIP_SAGE") == "1",
                    reason="sage unavailable or RELN_SKIP_SAGE=1")
def test_fixture_regeneration_byte_identical(tmp_path):
    res = fixtures.reproduce(tmp_path / "regen.json")
    assert res["returncode"] == 0, res["stderr_tail"]
    assert res["generator_sha256_matches_amendment"]
    assert res["byte_identical"], res
    assert res["reln_entries_identical"]
    assert json.loads(Path(tmp_path / "regen.json").read_text())["EXP-RELN-c5a377"] == \
        fixtures.load_fixtures()

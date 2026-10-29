"""Controls for verify_ecpp.py: it must accept the archived certificates and
reject every tampered or composite one.  Run: python3 -m pytest -q this file."""

from __future__ import annotations

import copy
import json
import random
from pathlib import Path

import pytest

import verify_ecpp as V

HERE = Path(__file__).resolve().parent
CERTS = sorted((HERE / "certificates").glob("*.json"))
ECPP = [p for p in CERTS if json.loads(p.read_text())["kind"] == "ecpp"]


def rng():
    return random.Random(1)


def load(p):
    return json.loads(p.read_text())


def test_archive_is_nonempty_and_has_ecpp_chains():
    assert len(CERTS) == 98
    assert ECPP


@pytest.mark.parametrize("path", CERTS, ids=lambda p: p.stem[:12])
def test_every_archived_certificate_is_valid(path):
    assert V.check_certificate(load(path), rng())["valid"]


def test_manifest_matches_files():
    import hashlib
    man = json.loads((HERE / "manifest.json").read_text())
    assert man["failures"] == [] and man["certified_by_both"] == man["count"] == len(CERTS)
    for row in man["factors"]:
        blob = (HERE / row["certificate"]).read_bytes()
        assert hashlib.sha256(blob).hexdigest() == row["certificate_sha256"]
        assert row["pari_primecertisvalid"] and row["independent_verify_ecpp"]


@pytest.mark.parametrize("n", [561, 1_000_003 * 1_000_033, 3_215_031_751, 2**64 + 1])
def test_composites_rejected_as_small(n):
    with pytest.raises(V.Invalid):
        V.check_certificate({"N": str(n), "kind": "small"}, rng())


def test_known_primes_accepted_as_small():
    for n in (2, 3, 1_000_003, 2**61 - 1, 18446744073709551557):
        V.check_certificate({"N": str(n), "kind": "small"}, rng())


def _mutate(field):
    cert = copy.deepcopy(load(ECPP[0]))
    st = cert["steps"][0]
    if field == "N":
        bad = int(cert["N"]) + 2
        cert["N"] = st[0] = str(bad)
    elif field == "t":
        st[1] = str(int(st[1]) + 2)
    elif field == "s":
        st[2] = str(int(st[2]) * 2)
    elif field == "point":
        st[4][1] = str(int(st[4][1]) + 1)
    elif field == "chain":
        if len(cert["steps"]) > 1:
            cert["steps"][1][0] = str(int(cert["steps"][1][0]) + 2)
        else:
            cert["steps"].append(copy.deepcopy(st))
    return cert


@pytest.mark.parametrize("field", ["N", "t", "s", "point", "chain"])
def test_tampered_certificates_rejected(field):
    cert = _mutate(field)
    with pytest.raises(V.Invalid):
        V.check_certificate(cert, rng())


def test_size_condition_is_exact():
    # q > (N^(1/4)+1)^2 with N = 10^8: N^(1/4) = 100, bound 10201
    assert not V.size_condition(10201, 10**8)
    assert V.size_condition(10202, 10**8)


def test_composite_with_fabricated_step_rejected():
    # A composite N with an arbitrary curve: the scalar multiplication must
    # fail or not land on -Q.
    N = 1_000_003 * 1_000_033
    step = [str(N), "0", "1", "1", ["2", "3"]]
    with pytest.raises(V.Invalid):
        V.check_certificate({"N": str(N), "kind": "ecpp", "steps": [step]}, rng())

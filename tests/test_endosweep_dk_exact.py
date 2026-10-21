"""Exact CM discriminants of research/endosweep_dk_exact_20261016, rechecked from the files alone.

Nothing here reads the curve corpus: each record carries p, n, h and t, so t, 4q - t^2, the
factorisation, D_K, f, the squarefree part and the degree bound are all recomputed from scratch
(independently of harness.endosweep.nist, then compared with it).  The per-factor found_by is
re-derived from the frozen driver snapshot, and the Lean file is regenerated and compared.
"""
from __future__ import annotations

import hashlib
import importlib.util
import json
import math
import re
import subprocess
import sys
from math import prod
from pathlib import Path

import pytest
from sympy import isprime

from harness.endosweep import quadorder as QO
from harness.endosweep.nist import check_factorization, exact_discriminant

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "research/endosweep_dk_exact_20261016"
LEAN = ROOT / "formal/CryptoResearch/Endosweep/DkExact.lean"
TARGET = ROOT / "formal/targets/endosweep-dk-exact-discriminants.yaml"
DOC = json.loads((OUT / "dk_exact.json").read_text())
CERTS = {json.loads(l)["curve"]: json.loads(l) for l in (OUT / "factorizations.jsonl").read_text().splitlines()}
ROWS = DOC["curves"]
EXCLUDED = {"nist/P-256", "nist/P-384", "nist/P-521", "other/Curve25519"}
MINUS3 = {"bn/bn510", "bls/BLS12-638", "arkworks/bw6_767"}


def _independent_dk(N: int, fac: list[tuple[int, int]]) -> tuple[int, int, int]:
    """(D_K, f, s) for t^2 - 4q = -N, written out again rather than imported."""
    s = prod(p for p, e in fac if e % 2)
    sq = prod(p ** (e // 2) for p, e in fac)
    assert s * sq * sq == N
    if s % 4 == 3:                      # -s = 1 mod 4
        return -s, sq, s
    assert sq % 2 == 0, "t^2 - 4q = 0 mod 4 needs an even square part here"
    return -4 * s, sq // 2, s


def test_the_curve_set() -> None:
    assert len(ROWS) == 18 == len(CERTS)
    assert {r["curve"] for r in ROWS} == set(CERTS)
    assert not EXCLUDED & set(CERTS)
    nist = [json.loads(l) for l in (ROOT / "research/endosweep_nist_20261006/factorizations.jsonl").read_text().splitlines()]
    assert {"P-256", "P-384", "P-521", "Curve25519"} <= {r["curve"] for r in nist}
    assert not {int(r["N"]) for r in nist} & {int(c["N"]) for c in CERTS.values()}


@pytest.mark.parametrize("row", ROWS, ids=lambda r: r["curve"])
def test_each_curve_from_scratch(row: dict) -> None:
    p, n, h, t = int(row["p"]), int(row["n"]), int(row["h"]), int(row["t"])
    assert isprime(p) and isprime(n) and p.bit_length() == row["p_bits"]
    assert t == p + 1 - h * n and t * t < 4 * p
    N = 4 * p - t * t
    cert = CERTS[row["curve"]]
    assert int(cert["N"]) == N == int(row["N_4q_minus_t2"]) and len(str(N)) == row["N_digits"]
    fac = [(int(a), int(e)) for a, e in cert["factors"]]
    assert fac == [(int(a), int(e)) for a, e in row["factorization"]]
    assert fac == sorted(fac) and prod(a ** e for a, e in fac) == N
    assert all(isprime(a) for a, _ in fac)
    assert check_factorization(N, cert["factors"]) == fac
    assert len(cert["found_by"]) == len(fac) == len(row["found_by"])
    assert cert["primes_proven_by"] == "PARI isprime"
    DK, f, s = _independent_dk(N, fac)
    assert (DK, f) == exact_discriminant(t * t - 4 * p, fac)
    assert t * t - 4 * p == DK * f * f
    assert (str(DK), str(f), str(s)) == (row["D_K"], row["conductor_f"], row["squarefree_part"])
    assert DK % 4 in (0, 1) and QO.is_discriminant(DK)
    # fundamental: the odd-exponent primes are distinct primes, so s is squarefree
    core = DK if DK % 4 == 1 else DK // 4
    assert DK % 4 == 1 or core % 4 in (2, 3)
    assert abs(core) == s and len({a for a, _ in fac}) == len(fac)     # s: a product of distinct primes
    deg = (abs(DK) + DK % 2) // 4
    assert deg == QO.min_nonscalar_degree(DK) == int(row["min_nonscalar_degree"])
    assert row["log2_abs_D_K"] == round(math.log2(abs(DK)), 2)
    assert (DK == -3) == (row["curve"] in MINUS3)
    if DK != -3:
        assert 2 ** 235 <= abs(DK) and 2 ** 233 <= deg
    assert row["literature"] == "not checked against literature"


def test_pari_proves_every_factor_prime() -> None:
    cypari2 = pytest.importorskip("cypari2")
    P = cypari2.Pari()
    for cert in CERTS.values():
        for a, _ in cert["factors"]:
            assert P.isprime(int(a))


def test_std_curves_agreements_are_the_seven_recorded() -> None:
    agree = {r["curve"] for r in ROWS if r["std_curves_check"].endswith("agrees")}
    assert agree == {"x962/prime239v2", "nums/w-255-mers", "nums/numsp256d1", "other/BADA55-R-256",
                     "other/ssc-288", "bn/bn510", "bls/BLS12-638"}
    assert not any("DISAGREES" in r["std_curves_check"] for r in ROWS)


def _make_factorizations():
    spec = importlib.util.spec_from_file_location("dk_make", OUT / "make_factorizations.py")
    mod = importlib.util.module_from_spec(spec)
    sys.path.insert(0, str(OUT))
    try:
        spec.loader.exec_module(mod)
    finally:
        sys.path.remove(str(OUT))
    return mod


def test_found_by_replays_from_the_frozen_snapshot() -> None:
    mod = _make_factorizations()
    snap = json.loads((OUT / "provenance/driver_state.snapshot.json").read_text())
    survey = {json.loads(l)["name"]: json.loads(l) for l in (OUT / "provenance/survey_selected.jsonl").read_text().splitlines()}
    done = {e["curve"]: (int(C), e) for C, e in snap.items() if not e["open"]}
    assert set(CERTS) == set(done) - EXCLUDED
    assert set(survey) == set(CERTS)
    for name, cert in CERTS.items():
        C, e = done[name]
        assert survey[name]["4p-t^2"]["composite"] == [str(C)]
        by = mod.replay(C, [int(p) for p in e["primes"]], e["log"])
        assert " or " not in "".join(by.values())
        small = {int(p) for p, _ in survey[name]["4p-t^2"]["known"]}
        for (a, _), how in zip(cert["factors"], cert["found_by"]):
            a = int(a)
            assert how == (by[a] if a in by else "PARI factor(N, 2^32) (survey, 10 s screen)")
            assert (a in by) != (a in small)
            assert re.match(r"(GMP-ECM 7\.0\.5 B1=\d+|CADO-NFS 3\.0\.0 \(git 692ecb7e|PARI factor)", how)


def test_lean_file_is_the_generators_output(tmp_path: Path) -> None:
    out = tmp_path / "DkExact.lean"
    subprocess.run([sys.executable, str(OUT / "lean/gen_dk_exact_lean.py"), str(ROOT), str(out)], check=True,
                   capture_output=True)
    assert out.read_text() == LEAN.read_text()
    text = LEAN.read_text()
    code = re.sub(r"/-.*?-/", "", text, flags=re.S)
    for bad in ("sorry", "admit", "native_decide", "unsafe"):
        assert not re.search(rf"\b{bad}\b", code), bad
    assert not re.search(r"^\s*axiom\b", code, flags=re.M)
    for r in ROWS:
        assert f"  DK := {r['D_K']}" in text


def test_target_spec() -> None:
    spec = TARGET.read_text()
    tid = re.search(r"^task_id: (TASK-20261016-[0-9a-f]{6})$", spec, flags=re.M).group(1)
    others = [p for p in (ROOT / "formal/targets").glob("*.yaml") if p != TARGET and tid in p.read_text()]
    assert not others
    assert "theorem_name: CryptoResearch.Endosweep.DkExact.exact_discriminants" in spec
    assert "theorem_file: CryptoResearch/Endosweep/DkExact.lean" in spec
    assert re.search(r"^theorem exact_discriminants :", LEAN.read_text(), flags=re.M)


def test_sha256sums() -> None:
    for line in (OUT / "SHA256SUMS").read_text().splitlines():
        digest, name = line.split()
        assert hashlib.sha256((OUT / name).read_bytes()).hexdigest() == digest, name

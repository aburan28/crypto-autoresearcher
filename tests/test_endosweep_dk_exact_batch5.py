"""Exact CM discriminant of research/endosweep_dk_exact_batch5_20261023 (gost512), and its open composites.

Part A repeats tests/test_endosweep_dk_exact_batch4.py's checks for the one curve of batch 5: the curve set is
re-derived as the entries that went from open to complete between snapshots 4 and 5; t, 4q - t^2, the
factorisation, D_K, f and the degree are recomputed from the record's p, n, h; found_by is replayed from the
fifth snapshot with batch 1's replay; the markdown and the Lean file are regenerated and compared.  The final
split came from FactorDB, so it is checked against the fetched record and must not be attributed to ECM or CADO.

Part B checks open_composites.json against the snapshot and the survey records: known primes times the open
cofactor give 4q - t^2, and the ECM counts are the snapshot's.
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
B1 = ROOT / "research/endosweep_dk_exact_20261016"
B2 = ROOT / "research/endosweep_dk_exact_batch2_20261016"
B3 = ROOT / "research/endosweep_dk_exact_batch3_20261017"
B4 = ROOT / "research/endosweep_dk_exact_batch4_20261022"
OUT = ROOT / "research/endosweep_dk_exact_batch5_20261023"
LEAN = ROOT / "formal/CryptoResearch/Endosweep/DkExactBatch5.lean"
TARGET = ROOT / "formal/targets/endosweep-dk-exact-batch5-discriminants.yaml"
DOC = json.loads((OUT / "dk_exact.json").read_text())
CERTS = {json.loads(l)["curve"]: json.loads(l) for l in (OUT / "factorizations.jsonl").read_text().splitlines()}
ROWS = DOC["curves"]
OPEN = json.loads((OUT / "open_composites.json").read_text())
SNAP5 = json.loads((OUT / "provenance/driver_state.snapshot5.json").read_text())
LOG5 = (OUT / "provenance/driver_events.snapshot5.log").read_text()
FDB = json.loads((OUT / "provenance/gost512_factordb.json").read_text())
EXCLUDED_NIST = {"nist/P-256", "nist/P-384", "nist/P-521", "other/Curve25519"}
EARLIER = set()
for d in (B1, B2, B3, B4):
    EARLIER |= {json.loads(l)["curve"] for l in (d / "factorizations.jsonl").read_text().splitlines()}
FOUR = {"nums/w-510-mont", "nums/ed-512-mont", "brainpool/brainpoolP512r1", "nums/ed-511-mers"}
TIERS = [(11000, 90), (50000, 240), (250000, 500), (1000000, 900), (3000000, 2400), (11000000, 4480)]
FACTORDB = "FactorDB (external; finder not recorded; fetched 2026-10-22T23:04:32.541251Z)"


def _independent_dk(N: int, fac: list[tuple[int, int]]) -> tuple[int, int, int]:
    """(D_K, f, s) for t^2 - 4q = -N, written out again rather than imported."""
    s = prod(p for p, e in fac if e % 2)
    sq = prod(p ** (e // 2) for p, e in fac)
    assert s * sq * sq == N
    if s % 4 == 3:
        return -s, sq, s
    assert sq % 2 == 0
    return -4 * s, sq // 2, s


def _load(name: str, path: Path):
    spec = importlib.util.spec_from_file_location(name, path)
    mod = importlib.util.module_from_spec(spec)
    sys.path.insert(0, str(path.parent))
    try:
        spec.loader.exec_module(mod)
    finally:
        sys.path.remove(str(path.parent))
    return mod


# ---- Part A: gost512 ----

def test_the_curve_set_is_what_snapshot_5_added() -> None:
    s4 = json.loads((B4 / "provenance/driver_state.snapshot4.json").read_text())
    assert set(s4) == set(SNAP5)
    done4 = {e["curve"] for e in s4.values() if not e["open"]}
    done5 = {e["curve"] for e in SNAP5.values() if not e["open"]}
    for C, e in s4.items():
        if not e["open"]:
            assert SNAP5[C] == e
    assert done5 - done4 == {"gost/gost512"} == set(CERTS) == {r["curve"] for r in ROWS}
    assert done4 - EXCLUDED_NIST == EARLIER
    assert set(DOC["excluded_already_certified"]) == EXCLUDED_NIST | EARLIER
    assert {e["curve"] for e in SNAP5.values() if e["open"]} == FOUR
    for C, e in SNAP5.items():
        assert prod(int(x) for x in e["primes"] + e["open"]) == int(C)


def test_event_log_extends_batch_4s() -> None:
    old = (B4 / "provenance/driver_events.snapshot4.log").read_text()
    assert LOG5.startswith(old)
    added = LOG5[len(old):]
    assert "gost/gost512: C144 found fully factored on FactorDB (id 1100000009030548498) as 71 x 74" in added
    assert not re.search(r"gost/gost512: (ECM .* found|CADO split)", added)


def test_gost512_final_split_is_factordbs() -> None:
    e = next(e for e in SNAP5.values() if e["curve"] == "gost/gost512")
    C144 = int(FDB["composite"])
    assert FDB["curve"] == "gost/gost512" and FDB["factordb_id"] == 1100000009030548498
    assert FDB["fetched"].startswith("2026-10-22T23:04:32")
    ps = [int(p) for p, x in FDB["factors"]]
    assert [x for _, x in FDB["factors"]] == [1, 1] and prod(ps) == C144 and len(str(C144)) == 144
    assert [len(str(p)) for p in ps] == [71, 74]
    assert e["log"][-1] == f"FactorDB (fetched {FDB['fetched']}): 144-digit -> 71 x 74"
    assert e["primes"][1:] == [str(p) for p in ps]
    # the ECM effort on the C144 before the fetch: tiers to 3e6 complete, 1200 curves at 11e6
    assert e["ecm_done"][str(C144)] == 5 and e["ecm_curves"][str(C144)] == {"4": 2400, "5": 1200}
    cert = CERTS["gost/gost512"]
    for (a, _), how in zip(cert["factors"], cert["found_by"]):
        if int(a) in ps:
            assert how == FACTORDB
            assert "ECM" not in how and "CADO" not in how
        else:
            assert how == "GMP-ECM 7.0.5 B1=11000 (driver tier 1)"


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
    core = DK if DK % 4 == 1 else DK // 4
    assert DK % 4 == 1 or core % 4 in (2, 3)
    assert abs(core) == s and len({a for a, _ in fac}) == len(fac)
    deg = (abs(DK) + DK % 2) // 4
    assert deg == QO.min_nonscalar_degree(DK) == int(row["min_nonscalar_degree"])
    assert row["log2_abs_D_K"] == round(math.log2(abs(DK)), 2)
    assert 2 ** 511 <= abs(DK) and 2 ** 509 <= deg
    assert row["literature"] == "not checked against literature"


def test_gost512_shape() -> None:
    (row,) = ROWS
    assert row["curve"] == "gost/gost512" and row["h"] == 1 and row["conductor_f"] == "1"
    assert [len(a) for a, _ in row["factorization"]] == [11, 71, 74]
    assert row["D_K_digits"] == 155 and row["D_K_case"] == "-s (s = 3 mod 4)"
    assert row["source"].startswith("GOST R 34.10-2001, RFC 5832")


def test_pari_proves_every_factor_prime() -> None:
    cypari2 = pytest.importorskip("cypari2")
    P = cypari2.Pari()
    for cert in CERTS.values():
        for a, _ in cert["factors"]:
            assert P.isprime(int(a))
    for r in OPEN["curves"]:
        for k in r["known_primes"]:
            assert P.isprime(int(k["p"]))
        assert not P.isprime(int(r["cofactor"]))


def test_std_curves_records_no_cm_disc() -> None:
    assert {r["std_curves_check"] for r in ROWS} == {"std-curves records no cm_disc"}


def test_found_by_replays_from_the_fifth_snapshot() -> None:
    mod = _load("dk_make_b5", B1 / "make_factorizations.py")
    survey = {json.loads(l)["name"]: json.loads(l) for l in (OUT / "provenance/survey_selected.jsonl").read_text().splitlines()}
    done = {e["curve"]: (int(C), e) for C, e in SNAP5.items() if not e["open"]}
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


def test_markdown_is_the_builders_output() -> None:
    mod = _load("dk_build_b5", B1 / "build_dk_exact.py")
    assert mod.markdown(DOC, OUT.name) == (OUT / "dk_exact.md").read_text()


def test_lean_file_is_the_generators_output(tmp_path: Path) -> None:
    out = tmp_path / "DkExactBatch5.lean"
    subprocess.run([sys.executable, str(B1 / "lean/gen_dk_exact_lean.py"), str(ROOT), str(out),
                    "--dir", "research/endosweep_dk_exact_batch5_20261023", "--module", "DkExactBatch5",
                    "--target", "formal/targets/endosweep-dk-exact-batch5-discriminants.yaml"],
                   check=True, capture_output=True)
    assert out.read_text() == LEAN.read_text()
    text = LEAN.read_text()
    code = re.sub(r"/-.*?-/", "", text, flags=re.S)
    for bad in ("sorry", "admit", "native_decide", "unsafe"):
        assert not re.search(rf"\b{bad}\b", code), bad
    assert not re.search(r"^\s*axiom\b", code, flags=re.M)
    assert "import CryptoResearch.Endosweep.DkExact\n" in code
    assert not re.search(r"^(structure|abbrev|def) DkCert", code, flags=re.M)
    assert "theorem DkCert.statement_of_holds" not in code
    for r in ROWS:
        assert f"  DK := {r['D_K']}" in text


def test_target_spec() -> None:
    spec = TARGET.read_text()
    tid = re.search(r"^task_id: (TASK-20261023-[0-9a-f]{6})$", spec, flags=re.M).group(1)
    others = [p for p in (ROOT / "formal/targets").glob("*.yaml") if p != TARGET and tid in p.read_text()]
    assert not others
    assert "theorem_name: CryptoResearch.Endosweep.DkExactBatch5.exact_discriminants" in spec
    assert "theorem_file: CryptoResearch/Endosweep/DkExactBatch5.lean" in spec
    assert re.search(r"^theorem exact_discriminants :", LEAN.read_text(), flags=re.M)


# ---- Part B: the open composites ----

def test_open_composites_multiply_back() -> None:
    survey = {json.loads(l)["name"]: json.loads(l) for l in (OUT / "provenance/survey_open.jsonl").read_text().splitlines()}
    assert {r["curve"] for r in OPEN["curves"]} == FOUR == set(survey)
    by_curve = {e["curve"]: (C, e) for C, e in SNAP5.items()}
    for r in OPEN["curves"]:
        C, e = by_curve[r["curve"]]
        t = int(r["t"])
        assert int(survey[r["curve"]]["t"]) == t and survey[r["curve"]]["4p-t^2"]["composite"] == [C]
        N = int(r["N_4q_minus_t2"])
        known = [(int(k["p"]), k["exponent"]) for k in r["known_primes"]]
        assert all(isprime(p) for p, _ in known) and not isprime(int(r["cofactor"]))
        assert prod(p ** x for p, x in known) * int(r["cofactor"]) == N
        assert e["open"] == [r["cofactor"]] and len(r["cofactor"]) == r["cofactor_digits"]
        assert [str(p) for p, _ in known if str(p) in e["primes"]] == e["primes"]
        small = {int(p): x for p, x in survey[r["curve"]]["4p-t^2"]["known"]}
        assert {p: x for p, x in known if p in small} == small
        assert "D_K" not in json.dumps(r)
    assert sorted(r["cofactor_digits"] for r in OPEN["curves"]) == [133, 146, 151, 152]


def test_open_composites_recompute_from_p_n_h() -> None:
    for r in OPEN["curves"]:
        p, n, h, t = int(r["p"]), int(r["n"]), int(r["h"]), int(r["t"])
        assert isprime(p) and isprime(n) and p.bit_length() == r["p_bits"]
        assert t == p + 1 - h * n and t * t < 4 * p
        assert 4 * p - t * t == int(r["N_4q_minus_t2"]) and len(r["N_4q_minus_t2"]) == r["N_digits"]


def test_open_composites_ecm_counts_match_snapshot_5() -> None:
    by_curve = {e["curve"]: e for e in SNAP5.values()}
    for r in OPEN["curves"]:
        e = by_curve[r["curve"]]
        cof = r["cofactor"]
        done, counted = e["ecm_done"][cof], e["ecm_curves"][cof]
        assert done == 5 and counted["4"] == 2400
        got = {t["B1"]: t["curves"] for t in r["ecm"]}
        assert got[3000000] == 2400 and got[11000000] == counted["5"]
        assert [t["status"] for t in r["ecm"]] == ["complete"] * 5 + ["partial"]
        assert got[11000000] < 4480
        for B1, nominal in TIERS[1:4]:
            assert got[B1] == nominal
        if r["curve"] == "nums/ed-511-mers":     # its C133 came from a split at B1 = 11000
            assert got[11000] is None and e["log"] == ["ECM B1=11000: 153-digit -> 21 x 133"]
        else:
            assert got[11000] == 90 and e["log"] == []
        # the last logged progress line at 11e6 trails the saved count by whole 50-curve chunks saved since
        last = re.findall(rf"^\S+   B1=11000000: .*?\b{re.escape(r['curve'])} (\d+)/4480", LOG5, flags=re.M)[-1]
        assert counted["5"] - int(last) in (50, 100)
        assert next(t for t in r["ecm"] if t["B1"] == 11000000)["last_logged_progress"] == int(last)
    expect = {"nums/w-510-mont": 1500, "nums/ed-512-mont": 1500, "brainpool/brainpoolP512r1": 1500,
              "nums/ed-511-mers": 1600}
    assert {r["curve"]: next(t["curves"] for t in r["ecm"] if t["B1"] == 11000000) for r in OPEN["curves"]} == expect


def test_open_composites_coverage_uses_gmp_ecms_table() -> None:
    text = (OUT / "provenance/gmp_ecm_expected_curves.txt").read_text()
    tables = {}
    for m in re.finditer(r"Using B1=(\d+), B2=\d+.*\n.*\n([\d\t]+)\n(\S[^\n]*)", text):
        tables[int(m.group(1))] = dict(zip(map(int, m.group(2).split()), map(float, m.group(3).split())))
    assert sorted(tables) == [b for b, _ in TIERS]
    for r in OPEN["curves"]:
        for d, c in r["ecm_coverage"].items():
            x = sum((t["curves"] or 0) / tables[t["B1"]][int(d)] for t in r["ecm"])
            assert c["sum_curves_over_expected"] == round(x, 4)
            assert math.isclose(c["miss_probability_approx"], math.exp(-x), rel_tol=1e-2)
        assert r["ecm_coverage"]["35"]["sum_curves_over_expected"] > 10
        assert 1 < r["ecm_coverage"]["40"]["sum_curves_over_expected"] < 5
        assert r["ecm_coverage"]["45"]["sum_curves_over_expected"] < 1


def test_open_composites_factordb_status() -> None:
    fdb = {x["curve"]: x for x in json.loads((OUT / "provenance/factordb_status_20261023.json").read_text())}
    for r in OPEN["curves"]:
        resp = fdb[r["curve"]]["response"]
        assert resp["status"] == r["factordb"]["status"] == "C"
        assert resp["factors"] == [[r["cofactor"], 1]]


def test_open_composites_markdown_is_the_scripts_output() -> None:
    mod = _load("dk_open_b5", OUT / "open_composites.py")
    assert mod.markdown(OPEN) == (OUT / "open_composites.md").read_text()


def test_sha256sums() -> None:
    for line in (OUT / "SHA256SUMS").read_text().splitlines():
        digest, name = line.split()
        assert hashlib.sha256((OUT / name).read_bytes()).hexdigest() == digest, name

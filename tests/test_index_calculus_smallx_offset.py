"""EXP-PFDR-0b3699 EC-A1 tests (TASK-20261002-8a6b8a).

T-OFFSET-1  FactorBase.small_x_offset: |F| == s_sub, x distinct, every point on the curve
            with y != 0, the consecutive-from-x0 rule, x0 recorded, determinism.
T-OFFSET-2  rows, harvest rows and staircases of every pre-existing arm are identical with
            and without small_x_offset and planted_sub in --arms (m = 4, 16-20 bits).
T-PLANT-M4  planted_sub at m = 4, 20-24 bits: exactly one TT plant per curve whose monic
            vector is in the TT relation set, and removing that one vector leaves the rest
            of the set unchanged.
T-DET       --workers 1 and 2 give identical rows for the new arm.

The relation recount here is written from the CC-1 clause of EXP-PFDR-011cd0 and shares
no code with harvest.py.
"""
from __future__ import annotations

import json
import random

import pytest

np = pytest.importorskip("numpy")

from crypto_autoresearcher.index_calculus.__main__ import MAIN_ARMS, MAIN_ARMS_ALL, _instance, main
from crypto_autoresearcher.index_calculus.factor_base import (FactorBase, default_fb_size,
                                                              subgroup_prime_filter)

PF = subgroup_prime_filter([3, 4, 5], 0.15)

PRE_EXISTING = ["subgroup", "dickson", "small_x", "random_sub_r0", "random_sub_r1",
                "random_sub_r2", "known_null_sub", "random_dick_r0", "random_dick_r1",
                "random_dick_r2", "known_null_dick"]


def _s_sub(E, c: int) -> int:
    return max(4, len(FactorBase.subgroup(E, default_fb_size(E.order, 4), c)))


def _is_liftable_nonzero(E, x: int) -> bool:
    """y^2 = x^3 + a x + b has a root y != 0 (Euler's criterion; independent of lift_x)."""
    p = E.p
    rhs = (x * x * x + E.a * x + E.b) % p
    return rhs != 0 and pow(rhs, (p - 1) // 2, p) == 1


# -- T-OFFSET-1 -------------------------------------------------------------------------------

@pytest.mark.parametrize("bits,c", [(16, 3), (20, 5), (24, 11), (30, 2010)])
def test_small_x_offset_base_definition(bits, c):
    E, P, Q, k = _instance(bits, c, 0, PF)
    s = _s_sub(E, c)
    fb = FactorBase.small_x_offset(E, s, seed=c + 9000)
    p = E.p
    assert fb.kind == "small_x_offset"
    assert len(fb) == s
    xs = [Pt[0] for Pt in fb.points]
    assert len(set(xs)) == s
    for Pt in fb.points:
        assert Pt[1] != 0
        assert (Pt[1] * Pt[1] - (Pt[0] ** 3 + E.a * Pt[0] + E.b)) % p == 0
    rng = random.Random(f"fb-smallx-offset|{p}|{E.a}|{E.b}|{s}|{c + 9000}")
    x0 = p // 4 + rng.randrange(p // 2)
    assert fb.params["x0"] == x0 and fb.params["seed"] == c + 9000
    assert p // 4 <= x0 < p // 4 + p // 2
    expect, x = [], x0
    while len(expect) < s:
        if _is_liftable_nonzero(E, x):
            expect.append(x)
        x += 1
    assert xs == expect
    assert fb.params["bound"] == expect[-1] + 1
    fb2 = FactorBase.small_x_offset(E, s, seed=c + 9000)
    assert fb2.points == fb.points and fb2.params == fb.params
    assert FactorBase.small_x_offset(E, s, seed=c + 9001).params["x0"] != x0 or p < 64
    poly = fb.membership_poly()  # generic product branch
    for xx in xs:
        assert sum(cf * pow(xx, e, p) for e, cf in poly.items()) % p == 0


def test_arm_lists():
    assert MAIN_ARMS_ALL.index("small_x_offset") == MAIN_ARMS_ALL.index("planted_sub") + 1
    assert MAIN_ARMS_ALL.index("small_x_offset") == MAIN_ARMS_ALL.index("known_log") - 1
    assert "small_x_offset" not in MAIN_ARMS
    assert MAIN_ARMS == ("subgroup", "dickson", "small_x", "random_sub_r0", "random_sub_r1",
                         "random_sub_r2", "random_dick_r0", "random_dick_r1", "random_dick_r2",
                         "known_log")


# -- census helpers -------------------------------------------------------------------------

def _strip(r: dict) -> str:
    r = dict(r)
    r.pop("seconds", None)
    h = r.get("harvest")
    if h:
        h = dict(h)
        for kk in ("harvest_seconds", "worker_maxrss_bytes"):
            h.pop(kk, None)
        r["harvest"] = h
    return json.dumps(r, sort_keys=True)


def _census(tmp, label: str, bits: list[int], curves: int, arms: list[str], workers: int = 1,
            offset: int = 0) -> dict:
    d = tmp / label
    d.mkdir()
    argv = ["census", "--panel", "main", "--m", "4", "--bits", *map(str, bits),
            "--curves", str(curves), "--curve-offset", str(offset), "--modes", "table",
            "--arms", *arms, "--known-log-max-bits", "0", "--retain", "all", "--relcount",
            "--quiet", "--workers", str(workers), "--out", str(d / "rows.jsonl"),
            "--rows-out", str(d / "h.jsonl"), "--staircase-out", str(d / "s.jsonl")]
    assert main(argv) == 0
    return {n: [json.loads(l) for l in open(d / n)] for n in ("rows.jsonl", "h.jsonl", "s.jsonl")}


# -- T-OFFSET-2 -------------------------------------------------------------------------------

def test_pre_existing_arms_unchanged_by_new_arms(tmp_path, capsys):
    base = _census(tmp_path, "base", [16, 18, 20], 2, PRE_EXISTING)
    ext = _census(tmp_path, "ext", [16, 18, 20], 2, PRE_EXISTING + ["planted_sub", "small_x_offset"])
    for name in ("rows.jsonl", "h.jsonl", "s.jsonl"):
        a = sorted(_strip(r) for r in base[name])
        b = sorted(_strip(r) for r in ext[name] if r["arm"] in PRE_EXISTING)
        assert a == b, name
        # the file order of pre-existing records is unchanged too
        assert [_strip(r) for r in base[name]] == \
            [_strip(r) for r in ext[name] if r["arm"] in PRE_EXISTING], name
    new_rows = [r for r in ext["rows.jsonl"] if r["arm"] == "small_x_offset"]
    assert len(new_rows) == 3 * 2
    assert all(r["status"] == "completed_valid" and r["fb"] == "small_x_offset" for r in new_rows)
    assert all(r["fb_size"] == next(q["fb_size"] for q in ext["rows.jsonl"]
                                    if q["arm"] == "random_sub_r0" and q["bits"] == r["bits"]
                                    and q["curve"] == r["curve"]) for r in new_rows)
    capsys.readouterr()


# -- T-PLANT-M4 -------------------------------------------------------------------------------

def _monic(vec: dict, N: int):
    """CC-1 monic form of {coordinate: coefficient}; None for the zero vector."""
    items = sorted((i, c % N) for i, c in vec.items() if c % N)
    if not items:
        return None
    inv = pow(items[0][1], N - 2, N)
    return tuple((i, c * inv % N) for i, c in items)


_K, _R = 1 << 40, (1 << 40) + 1


def _row_vec(h: dict) -> dict:
    v = {i: c for i, c in h["coeffs"]}
    if h["kcoef"]:
        v[_K] = h["kcoef"]
    if h["rhs"]:
        v[_R] = h["rhs"]
    return v


def _recount_tt(hrows: list[dict], N: int) -> dict:
    """Distinct monic TT relations (CC-1) with multiplicities, from star rows."""
    groups: dict = {}
    for h in hrows:
        if h["class"] != "TT":
            continue
        gid = json.dumps(h["elements"][0], sort_keys=True)
        groups.setdefault(gid, []).append(_row_vec(h))
    mult: dict = {}
    for rows in groups.values():
        for j, rj in enumerate(rows):
            rels = [rj] + [{i: rj.get(i, 0) - ri.get(i, 0) for i in set(rj) | set(ri)}
                           for ri in rows[:j]]
            for r in rels:
                key = _monic(r, N)
                if key is not None:
                    mult[key] = mult.get(key, 0) + 1
    return mult


def test_planted_sub_at_m4_one_tt_plant_found(tmp_path, capsys):
    out = _census(tmp_path, "plant", [20, 22, 24], 2, ["planted_sub"])
    rows = out["rows.jsonl"]
    assert len(rows) == 6
    for r in rows:
        assert r["status"] == "completed_valid" and r["checks"]["G7_planted_relations_hold"]
        N = r["N"]
        tts = [x for x in r["fb_params"]["planted_relations"] if x["class"] == "TT"]
        assert r["fb_params"]["n_tt"] == 1 and len(tts) == 1
        idx, sg = tts[0]["indices"], tts[0]["signs"]
        v = _monic(dict(zip(idx, sg)), N)
        hr = [h for h in out["h.jsonl"] if h["bits"] == r["bits"] and h["curve"] == r["curve"]]
        rel = _recount_tt(hr, N)
        assert len(rel) == r["harvest"]["TT"]["at_stop"]["relations_distinct"]
        assert v in rel
        rest = {k: m for k, m in rel.items() if k != v}
        assert len(rest) == len(rel) - 1
        assert all(rest[k] == rel[k] for k in rest)
    capsys.readouterr()


# -- T-DET ------------------------------------------------------------------------------------

def test_new_arm_workers_1_and_2_identical(tmp_path, capsys):
    w1 = _census(tmp_path, "w1", [16, 18], 3, ["random_sub_r0", "small_x_offset"], workers=1)
    w2 = _census(tmp_path, "w2", [16, 18], 3, ["random_sub_r0", "small_x_offset"], workers=2)
    for name in ("rows.jsonl", "h.jsonl", "s.jsonl"):
        a = sorted(_strip(r) for r in w1[name] if r["arm"] == "small_x_offset")
        b = sorted(_strip(r) for r in w2[name] if r["arm"] == "small_x_offset")
        assert a == b, name
    assert sum(1 for r in w1["rows.jsonl"] if r["arm"] == "small_x_offset") == 6
    capsys.readouterr()

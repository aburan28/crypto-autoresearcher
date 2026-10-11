"""EXP-PFDR-011cd0 EC-8 tests: the OBJ-5 repair, the relation counter, table-only and
search-only modes, the planted base, solve certificates and census determinism.

Toy curves only (p <= 2^20); every curve seed here is outside the experiment's
census curves (c >= 10 at 20..32 bits) and Stage R' curves.
tests/test_index_calculus_fp.py and tests/test_index_calculus_harvest.py must pass
unedited beside this file.
"""

from __future__ import annotations

import gzip
import hashlib
import importlib.util
import itertools
import json
import math
import os
import random
import subprocess
import sys
from collections import Counter

import pytest

np = pytest.importorskip("numpy")

from crypto_autoresearcher.index_calculus import harvest as harvest_mod
from crypto_autoresearcher.index_calculus.__main__ import _instance, main
from crypto_autoresearcher.index_calculus.curve import Curve, generate_prime_order_curve
from crypto_autoresearcher.index_calculus.decompose import DecompStats, decompose
from crypto_autoresearcher.index_calculus.factor_base import (
    FACTOR_BASES,
    FactorBase,
    build_factor_base,
    default_fb_size,
    subgroup_prime_filter,
)
from crypto_autoresearcher.index_calculus.harvest import Harvester, unpack
from crypto_autoresearcher.index_calculus.solver import solve_index_calculus
from crypto_autoresearcher.index_calculus.tails import TailTable

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PRE_FIX = os.path.join(REPO, "tests", "fixtures", "harvest_pre_obj5.py")
PRE_FIX_SHA256 = "74f85c2373692996d4899e4d215d432d8911509593809783e8b19046c83b5372"  # a32e70808
VERIFY_SOLVES = os.path.join(REPO, "experiments", "EXP-PFDR-011cd0", "verify_solves.py")
PF = subgroup_prime_filter([3, 4, 5], 0.15)


def _load_pre_fix():
    """The byte copy of harvest.py at a32e70808, loaded as a module of the package
    (its relative imports resolve against crypto_autoresearcher.index_calculus)."""
    raw = open(PRE_FIX, "rb").read()
    assert hashlib.sha256(raw).hexdigest() == PRE_FIX_SHA256
    name = "crypto_autoresearcher.index_calculus._harvest_pre_obj5"
    spec = importlib.util.spec_from_file_location(name, PRE_FIX)
    mod = importlib.util.module_from_spec(spec)
    sys.modules[name] = mod
    spec.loader.exec_module(mod)
    return mod


# -- T-OBJ5: the SS pair counter across unmerged sorted runs ----------------------------------

def _dlog_table(E, P):
    tab, R = {}, None
    for i in range(E.order):
        tab[R] = i
        R = E.add(R, P)
    return tab


def _obj5_fixture():
    """Four attempts on a 12-bit curve whose batch sizes keep three sorted runs
    unmerged (each run more than twice the next), with one x-key x* recorded in
    attempts 1, 2, 3 and 4.  Targets are real: R_t = a_t P + b_t Q, chosen so that
    R_t - F_{j_t} equals the attempt-1 encoding T1 (x(T1) = x*)."""
    E, P, Q, k = _instance(12, 1, 0, PF)
    fb = FactorBase.random(E, 150, seed=1)
    tab = TailTable(E, fb, 2)
    dl = _dlog_table(E, P)
    N = E.order
    rng = random.Random("obj5-fixture")
    a1, b1 = rng.randrange(N), rng.randrange(1, N)
    R1 = E.add(E.mul(a1, P), E.mul(b1, Q))
    ranges = [(0, len(fb) - 1), (10, 59), (70, 85), (100, 104)]  # 300, 100, 32, 10 encodings
    # T1 = R1 - F_j1 for the first j1 of attempt 1 with a usable point
    j1 = 0
    T1 = E.sub(R1, fb.points[j1])
    attempts = [(1, a1, b1, R1)]
    for t, (lo, hi) in zip((2, 3, 4), ranges[1:]):
        j = (lo + hi) // 2
        R = E.add(T1, fb.points[j])  # R - F_j = T1
        b = rng.randrange(1, N)
        a = (dl[R] - b * k) % N  # R = a P + b Q
        assert E.add(E.mul(a, P), E.mul(b, Q)) == R
        attempts.append((t, a, b, R))
    return E, P, Q, fb, tab, attempts, ranges, T1[0]


def _drive(H, E, P, Q, fb, tab, attempts, ranges):
    h = H(E, P, Q, fb, tab, "census", "census")
    h.table_phase()
    batches = []
    run_snapshots = []
    for (t, a, b, R), (lo, hi) in zip(attempts, ranges):
        h.begin_attempt(t, a, b)
        h.recorder.scan(R, lo, hi)
        h.end_attempt()
        xs, ds = h.last_batch
        batches.append([(int(x), int(d)) for x, d in zip(xs, ds)])
        run_snapshots.append([set(int(v) for v in rx) for rx, _ in h.runs])
    return h, batches, run_snapshots


def _brute_pairs(batches):
    """Sum over x-groups of C(k', 2), k' = formally distinct members (no duplicate
    is possible across attempts; asserted below), from every recorded encoding."""
    cnt = Counter(x for b in batches for x, _ in b)
    return sum(c * (c - 1) // 2 for c in cnt.values()), cnt


def test_obj5_fixture_straddles_three_unmerged_runs_and_old_code_undercounts():
    E, P, Q, fb, tab, attempts, ranges, xstar = _obj5_fixture()
    new, batches, runs = _drive(Harvester, E, P, Q, fb, tab, attempts, ranges)
    # the fixture: before attempt 4, three unmerged runs each hold x*
    assert len(runs[2]) == 3
    assert all(xstar in r for r in runs[2])
    assert any(x == xstar for x, _ in batches[3])
    expected, cnt = _brute_pairs(batches)
    assert cnt[xstar] >= 4  # k' >= 3 members straddling >= 3 runs, plus the new one
    assert new.ss_dup == 0
    # (i) repaired: pairs_raw == C(k', 2) summed over groups; every member in the group
    assert new.cls["SS"].pairs_raw == expected
    members = [d for rx, rd in new.runs for x, d in zip(rx.tolist(), rd.tolist()) if x == xstar]
    assert len(members) == cnt[xstar]
    g = new._group_from(members)
    assert len(g.keys) == cnt[xstar]
    # (ii) the pre-fix byte copy undercounts on the same fixture (the test is discriminating)
    old_mod = _load_pre_fix()
    old, batches_old, _ = _drive(old_mod.Harvester, E, P, Q, fb, tab, attempts, ranges)
    assert batches_old == batches
    assert old.cls["SS"].pairs_raw < expected, (old.cls["SS"].pairs_raw, expected)


def test_obj5_rank_and_staircase_unchanged_on_fixture_and_16bit_m4():
    old_mod = _load_pre_fix()
    E, P, Q, fb, tab, attempts, ranges, _ = _obj5_fixture()
    new, _, _ = _drive(Harvester, E, P, Q, fb, tab, attempts, ranges)
    old, _, _ = _drive(old_mod.Harvester, E, P, Q, fb, tab, attempts, ranges)
    for c in ("TT", "TB", "SS"):
        assert new.census[c].rank == old.census[c].rank
        assert new.cls[c].rows_emitted == old.cls[c].rows_emitted
    assert new.staircase() == old.staircase()
    # a 16-bit m = 4 instance driven identically through both harvesters
    E, P, Q, k = _instance(16, 4, 0, PF)
    fb = FactorBase.random(E, default_fb_size(E.order, 4), seed=4)
    tab = TailTable(E, fb, 2)
    hs = [H(E, P, Q, fb, tab, "census", "census") for H in (Harvester, old_mod.Harvester)]
    rows = [[], []]
    for h in hs:
        h.table_phase()
    rng = random.Random("obj5-rank-16-4")
    for t in range(1, 60):
        a, b = rng.randrange(E.order), rng.randrange(1, E.order)
        R = E.add(E.mul(a, P), E.mul(b, Q))
        for i, h in enumerate(hs):
            h.begin_attempt(t, a, b)
            decompose(E, fb, R, 4, DecompStats(), table=tab, recorder=h.recorder)
            rows[i].extend(h.end_attempt())
    assert rows[0] == rows[1]
    for c in ("TT", "TB", "SS"):
        assert hs[0].census[c].rank == hs[1].census[c].rank
    assert hs[0].staircase() == hs[1].staircase()
    assert hs[0].cls["SS"].pairs_raw >= hs[1].cls["SS"].pairs_raw


# -- T-REL: the relation counter against brute force -----------------------------------------

def _proj(v: dict, N: int):
    """Monic projective class of a reduced vector (independent of harvest._RelCounter)."""
    items = sorted((i, c % N) for i, c in v.items() if c % N)
    if not items:
        return None
    inv = pow(items[0][1], N - 2, N)
    return tuple((i, c * inv % N) for i, c in items)


def _sgn(v: dict, N: int):
    items = sorted((i, c % N) for i, c in v.items() if c % N)
    neg = tuple((i, (-c) % N) for i, c in items)
    return min(tuple(items), neg, key=lambda t: [c for _, c in t])


def _brute_tails(E, fb, h):
    """x -> list of (aggregated vector key, y-bit) of every stored tail (independent)."""
    n, pts = len(fb), fb.points
    out: dict = {}
    for idx in itertools.combinations_with_replacement(range(n), h):
        for signs in itertools.product((1, -1), repeat=h - 1):
            sg = (1,) + signs
            S, ok = None, True
            for i, s in zip(reversed(idx), reversed(sg)):
                S = E.add(S, pts[i] if s > 0 else E.neg(pts[i]))
                if S is None:
                    ok = False
                    break
            if not ok:
                continue
            v = Counter()
            for i, s in zip(idx, sg):
                v[i] += s
            out.setdefault(S[0], []).append(({i: c for i, c in v.items() if c}, int(S[1] > E.p // 2)))
    return out


def _brute_table_relations(E, fb, brute):
    """Every x-coincident signed pair of the table classes mapped to its projective class."""
    N, half = E.order, E.p // 2
    res = {"TT": Counter(), "TB": Counter()}
    sign = {"TT": set(), "TB": set()}
    for x, tails in brute.items():
        b = fb.index.get(x)
        first_y = (fb.points[b][1] > half) if b is not None else tails[0][1]
        oriented, seen = [], set()
        for v, yb in tails:
            sg = 1 if yb == first_y else -1
            ov = {i: sg * c for i, c in v.items()}
            key = tuple(sorted(ov.items()))
            if b is not None and key == ((b, 1),):
                continue
            if key in seen:
                continue
            seen.add(key)
            oriented.append(ov)
        pairs = []
        if b is not None:
            pairs += [("TB", {b: 1}, w) for w in oriented]
        pairs += [("TT", u, w) for u, w in itertools.combinations(oriented, 2)]
        for cl, u, w in pairs:
            d = dict(u)
            for i, c in w.items():
                d[i] = d.get(i, 0) - c
            r = _proj(d, N)
            if r is None:
                continue
            res[cl][r] += 1
            sign[cl].add(_sgn(d, N))
    return res, sign


def _star_classes(E, fb, tab):
    """Number of distinct projective classes of TT and TB star pairs, from tab.iter_keys()."""
    N, half = E.order, E.p // 2
    out = {"TT": set(), "TB": set()}
    for x, codes in tab.iter_keys():
        b = fb.index.get(x)
        if len(codes) < 2 and b is None:
            continue
        dec = []
        for code in codes:
            tail, yb = tab.decode(code)
            v = Counter()
            for i, s in tail:
                v[i] += s
            dec.append(({i: c for i, c in v.items() if c}, yb))
        first_y = (fb.points[b][1] > half) if b is not None else dec[0][1]
        distinct, seen = [], set()
        for v, yb in dec:
            sg = 1 if yb == first_y else -1
            ov = {i: sg * c for i, c in v.items()}
            key = tuple(sorted(ov.items()))
            if (b is not None and key == ((b, 1),)) or key in seen:
                continue
            seen.add(key)
            distinct.append(ov)
        pairs = []
        if b is not None:
            pairs += [("TB", {b: 1}, w) for w in distinct]
        if len(distinct) >= 2:
            pairs += [("TT", distinct[0], w) for w in distinct[1:]]
        for cl, u, w in pairs:
            d = dict(u)
            for i, c in w.items():
                d[i] = d.get(i, 0) - c
            r = _proj(d, N)
            if r is not None:
                out[cl].add(r)
    return {c: len(s) for c, s in out.items()}


def _counter_relations(h, cname):
    """Decode the in-process relation keys of a harvester class into (index, coef) tuples."""
    rc = h.rel[cname]
    out = Counter()
    for key, m in rc.mult.items():
        vals = np.frombuffer(key, dtype="<u8").tolist()
        out[tuple(zip(vals[0::2], vals[1::2]))] = m
    return out


@pytest.mark.parametrize("h_ar,size", [(2, 60), (3, 20)])
def test_relation_counter_matches_brute_force_table(h_ar, size):
    E, P = generate_prime_order_curve(14, seed=3)
    assert E.p <= 1 << 14
    fb = build_factor_base(E, "random", size, seed=h_ar)
    tab = TailTable(E, fb, h_ar)
    hv = Harvester(E, P, E.mul(5, P), fb, tab, "census", None, relcount=True)
    hv.table_phase()
    brute = _brute_tails(E, fb, h_ar)
    exp, exp_sign = _brute_table_relations(E, fb, brute)
    gen_tt, gen_tb = math.comb(2 * h_ar, h_ar) // 2, h_ar + 1
    for cname in ("TT", "TB"):
        got = _counter_relations(hv, cname)
        assert got == exp[cname], cname
        blk = hv.rel[cname].block()
        assert blk["relations_distinct"] == len(exp[cname])
        assert blk["relations_distinct_sign"] == len(exp_sign[cname])
        assert blk["relations_nonformal"] == len(exp[cname])  # empty formal basis
        assert blk["multiplicity_histogram"] == {str(k): v for k, v in
                                                 sorted(Counter(exp[cname].values()).items())}
        # R_star: distinct classes of the star pairs only (centre = the first distinct
        # element in the table's stored order), enumerated here from the decoded table
        assert blk["R_star"] == _star_classes(E, fb, tab)[cname]
    # L2: a generic relation (all coefficients +-1 on distinct indices) has the stated multiplicity
    n_gen = {"TT": 0, "TB": 0}
    for cname, support, mult in (("TT", 2 * h_ar, gen_tt), ("TB", h_ar + 1, gen_tb)):
        for r, m in exp[cname].items():
            coefs = [c for _, c in r]
            unit = all(c in (1, E.order - 1) for c in coefs)
            if unit and len(r) == support:
                n_gen[cname] += 1
                assert m == mult, (cname, r, m)
    assert n_gen["TT"] > 0
    if h_ar == 2:
        assert n_gen["TB"] > 0


def test_relation_counter_matches_brute_force_ss():
    """SS: every x-coincident pair of formally distinct encodings, enumerated from the
    recorded batches, mapped to its projective class, equals the in-process count."""
    E, P, Q, k = _instance(14, 2, 0, PF)
    fb = FactorBase.random(E, default_fb_size(E.order, 3), seed=2)
    tab = TailTable(E, fb, 2)
    hv = Harvester(E, P, Q, fb, tab, "census", "census", relcount=True)
    hv.table_phase()
    rng = random.Random("trel-ss")
    encs = []
    for t in range(1, 40):
        a, b = rng.randrange(E.order), rng.randrange(1, E.order)
        R = E.add(E.mul(a, P), E.mul(b, Q))
        hv.begin_attempt(t, a, b)
        decompose(E, fb, R, 3, DecompStats(), table=tab, recorder=hv.recorder)
        hv.end_attempt()
        xs, ds = hv.last_batch
        encs.extend((int(x), int(d)) for x, d in zip(xs, ds))
    N = E.order
    groups: dict = {}
    for x, d in encs:
        groups.setdefault(x, []).append(d)
    exp = Counter()
    star = set()
    for x, ds in groups.items():
        if len(ds) < 2:
            continue
        mem, seen = [], set()
        first_y = None
        for d in ds:
            t, hid, j, s, yb = unpack(d)
            if first_y is None:
                first_y = yb
            sg = 1 if yb == first_y else -1
            A = Counter()
            for i, si in hv.recorder.heads[hid]:
                A[i] += si
            A[j] += s
            oA = {i: sg * c for i, c in A.items() if c}
            key = (t, sg, tuple(sorted(oA.items())))
            if key in seen:
                continue
            seen.add(key)
            mem.append((t, sg, oA))
        for (p1, (t1, s1, A1)), (p2, (t2, s2, A2)) in itertools.combinations(enumerate(mem), 2):
            a1, b1 = hv.targets[t1]
            a2, b2 = hv.targets[t2]
            v = dict(A1)
            for i, c in A2.items():
                v[i] = v.get(i, 0) - c
            v = {i: c for i, c in v.items()}
            v[1 << 40] = -(s1 * b1 - s2 * b2)
            v[(1 << 40) + 1] = s1 * a1 - s2 * a2
            r = _proj(v, N)
            if r is not None:
                exp[r] += 1
                if p1 == 0:
                    star.add(r)
    got = _counter_relations(hv, "SS")
    assert sum(exp.values()) > 20
    assert got == exp
    blk = hv.rel["SS"].block()
    assert blk["R_star"] == len(star)
    assert blk["relations_distinct"] == len(exp)
    assert blk["multiplicity_histogram"] == {str(k): v for k, v in sorted(Counter(exp.values()).items())}


# -- T-TABLE ----------------------------------------------------------------------------------

@pytest.mark.parametrize("m", [3, 4, 5])
@pytest.mark.parametrize("kind", ["small_x", "random", "subgroup", "dickson"])
def test_table_mode_equals_census_mode_on_table_classes(m, kind):
    E, P, Q, k = _instance(16, 5, 0, PF)
    fb = build_factor_base(E, kind, default_fb_size(E.order, m), seed=5)
    out = {}
    for mode in ("census", "table"):
        rows = []
        E.ops.group_ops = 0
        out[mode] = (solve_index_calculus(E, P, Q, m=m, fb_kind=kind, seed=5, factor_base=fb,
                                          engine="mitm", harvest=mode, target_label="census",
                                          harvest_sink=rows.append, relcount=True), rows)
    t, c = out["table"], out["census"]
    assert t[0].harvest["terminated_by"] == "table_only" and t[0].attempts == 0
    for cname in ("TT", "TB"):
        assert t[0].harvest[cname] == c[0].harvest[cname]
        assert [r for r in t[1] if r["class"] == cname] == [r for r in c[1] if r["class"] == cname]
    assert t[0].harvest["table"] == c[0].harvest["table"]
    assert not [r for r in t[1] if r["class"] == "SS"]


# -- T-SEARCH ---------------------------------------------------------------------------------

def _batches_spy(monkeypatch):
    log = []
    orig = Harvester.end_attempt

    def spy(self):
        out = orig(self)
        xs, ds = self.last_batch
        log.append((self.t, [int(x) for x in xs], [int(d) for d in ds]))
        return out

    monkeypatch.setattr(Harvester, "end_attempt", spy)
    return log


@pytest.mark.parametrize("m", [3, 4])
def test_search_mode_records_census_encodings_and_snapshot(monkeypatch, m):
    E, P, Q, k = _instance(14, 6, 0, PF)
    fb = FactorBase.random(E, default_fb_size(E.order, m), seed=6)
    log = _batches_spy(monkeypatch)
    rows, logs = {}, {}
    # census to k
    rows["census"] = []
    log.clear()
    rc = solve_index_calculus(E, P, Q, m=m, seed=6, factor_base=fb, engine="mitm", harvest="census",
                              target_label="census", harvest_sink=rows["census"].append)
    logs["census"] = list(log)
    # search with an X_fix beyond census's stop
    X_census = rc.harvest["ss_store"]["encodings_recorded"] - rc.harvest["SS"]["at_stop"]["dup_formal"]
    rows["search"] = []
    log.clear()
    rs = solve_index_calculus(E, P, Q, m=m, seed=6, factor_base=fb, engine="mitm", harvest="search",
                              target_label="census", harvest_sink=rows["search"].append,
                              encoding_budget=2 * X_census + 10)
    logs["search"] = list(log)
    assert rc.k == k and rs.k is None and rs.harvest["terminated_by"] == "encoding_budget"
    assert rs.attempts > rc.attempts
    # exactly the encodings census mode records, up to census mode's stop
    assert logs["search"][:len(logs["census"])] == logs["census"]
    ss_c = [r for r in rows["census"] if r["class"] == "SS"]
    ss_s = [{kk: v for kk, v in r.items() if kk != "seq"} for r in rows["search"]
            if r["class"] == "SS" and r["attempt"] <= rc.attempts]
    assert ss_s == ss_c
    assert rs.rank == 0  # nothing entered the solver's elimination
    # at_X_fix equals census --budget-snapshot-only's when census mode reaches X_fix
    lam_small = max(1, X_census // (4 * math.isqrt(E.order)))
    xfix = lam_small * math.isqrt(E.order)
    assert xfix < X_census
    snap = {}
    xrows = {}
    for mode in ("census", "search"):
        xrows[mode] = []
        r = solve_index_calculus(E, P, Q, m=m, seed=6, factor_base=fb, engine="mitm", harvest=mode,
                                 target_label="census", harvest_sink=xrows[mode].append,
                                 encoding_budget=xfix, relcount=True, retain="xfix")
        snap[mode] = r.harvest["SS"]["at_X_fix"]
    assert snap["census"]["censored"] is False and snap["search"]["censored"] is False
    assert snap["census"] == snap["search"]
    pick = lambda rr: [{kk: v for kk, v in x.items() if kk != "census_rank_after"}
                       for x in rr if x["class"] == "SS"]
    assert pick(xrows["census"]) == pick(xrows["search"])
    assert all(x["seq"] < xfix for x in xrows["search"] if x["class"] == "SS")


# -- T-PLANT ----------------------------------------------------------------------------------

def test_planted_base_relations_hold_and_are_harvested():
    E, P, Q, k = _instance(18, 7, 0, PF)
    s = max(4, len(FactorBase.subgroup(E, default_fb_size(E.order, 3), 7)))
    fb = FactorBase.planted(E, s, seed=7 + 8000)
    assert fb.kind == "planted" and "planted" not in FACTOR_BASES
    assert len(fb) == s
    assert len({Pt[0] for Pt in fb.points}) == s
    with pytest.raises(NotImplementedError):
        fb.membership_poly()
    rels = fb.params["planted_relations"]
    assert sum(r["class"] == "TT" for r in rels) == fb.params["n_tt"] == max(1, round(s ** 4 / (6 * E.order)))
    assert sum(r["class"] == "TB" for r in rels) == 1
    Ev = Curve(E.p, E.a, E.b, E.order)
    for r in rels:
        S = None
        for i, sg in zip(r["indices"], r["signs"]):
            S = Ev.add(S, fb.points[i] if sg > 0 else Ev.neg(fb.points[i]))
        assert S is None
    # the start is FactorBase.random with the same seed; only the planted indices moved
    base = FactorBase.random(E, s, seed=7 + 8000)
    moved = {r["indices"][-1] for r in rels}
    assert [i for i in range(s) if base.points[i] != fb.points[i]] == sorted(moved)
    tab = TailTable(E, fb, 2)
    hv = Harvester(E, P, Q, fb, tab, "census", None, relcount=True)
    hv.table_phase()
    found = {c: set(hv.rel[c].mult) for c in ("TT", "TB")}
    for r in rels:
        key = hv.rel[r["class"]].monic_key(dict(zip(r["indices"], r["signs"])))
        assert key in found[r["class"]], r


# -- T-CERT -----------------------------------------------------------------------------------

def _strip_seconds(r):
    r = dict(r)
    r.pop("seconds", None)
    return json.dumps(r, sort_keys=True)


def test_solve_certs_rows_identical_and_verified(tmp_path, capsys):
    base = ["sweep", "--bits", "12", "14", "--curves", "2", "--rho-curves", "2", "--m", "3",
            "--fb", "small_x", "random", "--engine", "mitm", "--quiet"]
    a, b, certs = tmp_path / "a.jsonl", tmp_path / "b.jsonl", tmp_path / "c.jsonl"
    assert main(base + ["--out", str(a)]) == 0
    assert main(base + ["--out", str(b), "--solve-certs", str(certs)]) == 0
    ra = sorted(_strip_seconds(json.loads(l)) for l in open(a))
    rb = sorted(_strip_seconds(json.loads(l)) for l in open(b))
    assert ra == rb
    recs = [json.loads(l) for l in open(certs)]
    rows = [json.loads(l) for l in open(b)]
    assert len(recs) == sum(1 for r in rows if r["ok"]) == len(rows)
    out = tmp_path / "v.json"
    r = subprocess.run([sys.executable, VERIFY_SOLVES, str(certs), "--out", str(out)],
                       capture_output=True, text=True)
    assert r.returncode == 0, r.stdout + r.stderr
    rep = json.load(open(out))
    assert rep["pass"] and rep["verified"] == len(recs)
    assert rep["imports_subset_of_declared_and_stdlib"]
    bad = tmp_path / "bad.jsonl.gz"
    with gzip.open(bad, "wt") as fh:
        for i, rec in enumerate(recs):
            if i == 0:
                rec = dict(rec, k=(rec["k"] + 1) % rec["N"])
            fh.write(json.dumps(rec) + "\n")
    r = subprocess.run([sys.executable, VERIFY_SOLVES, str(bad), "--out", str(out)],
                       capture_output=True, text=True)
    assert r.returncode == 1
    rep = json.load(open(out))
    assert rep["failed"] == 1 and "k * P != Q" in rep["failures"][0]["reasons"]
    capsys.readouterr()


def test_census_solve_certs_rows_identical(tmp_path, capsys):
    argv = ["census", "--panel", "main", "--m", "3", "--bits", "12", "--curves", "1",
            "--known-log-max-bits", "12", "--quiet", "--relcount"]
    a, b, certs = tmp_path / "a.jsonl", tmp_path / "b.jsonl", tmp_path / "c.jsonl"
    assert main(argv + ["--out", str(a)]) == 0
    assert main(argv + ["--out", str(b), "--solve-certs", str(certs)]) == 0
    assert sorted(_strip_census(json.loads(l)) for l in open(a)) == \
        sorted(_strip_census(json.loads(l)) for l in open(b))
    rows = [json.loads(l) for l in open(b)]
    recs = [json.loads(l) for l in open(certs)]
    assert len(recs) == sum(1 for r in rows if r.get("k_found") and r.get("k_verified"))
    assert all(r["relcount_version"] == 1 for r in rows if r.get("harvest"))
    out = tmp_path / "v.json"
    r = subprocess.run([sys.executable, VERIFY_SOLVES, str(certs), "--out", str(out)],
                       capture_output=True, text=True)
    assert r.returncode == 0, r.stdout + r.stderr
    capsys.readouterr()


# -- T-DET ------------------------------------------------------------------------------------

def _strip_census(r):
    r = dict(r)
    r.pop("seconds", None)
    h = r.get("harvest")
    if h:
        h = dict(h)
        for kk in ("harvest_seconds", "worker_maxrss_bytes"):
            h.pop(kk, None)
        r["harvest"] = h
    return json.dumps(r, sort_keys=True)


@pytest.mark.parametrize("mode", ["table", "search"])
def test_census_cli_determinism_table_and_search(tmp_path, capsys, mode):
    arms = ["subgroup", "random_sub_r0", "known_null_sub", "dickson", "random_dick_r0",
            "known_null_dick"] + (["planted_sub"] if mode == "table" else [])
    common = ["census", "--panel", "main", "--m", "3", "--bits", "12", "14", "--modes", mode,
              "--arms", *arms, "--relcount", "--retain", "all", "--quiet",
              "--known-log-max-bits", "0"]
    if mode == "search":
        common += ["--encoding-budget-lambda", "4"]
    outs = {}
    for label, extra_runs in (("w1", [["--curves", "2", "--workers", "1"]]),
                              ("w2", [["--curves", "2", "--workers", "2"]]),
                              ("split", [["--curves", "1", "--curve-offset", "0"],
                                         ["--curves", "1", "--curve-offset", "1"]])):
        d = tmp_path / label
        d.mkdir()
        for ex in extra_runs:
            assert main(common + ex + ["--out", str(d / "rows.jsonl"), "--rows-out",
                                       str(d / "h.jsonl"), "--staircase-out",
                                       str(d / "s.jsonl")]) == 0
        outs[label] = {n: sorted(_strip_census(json.loads(l)) for l in open(d / n))
                       for n in ("rows.jsonl", "h.jsonl", "s.jsonl")}
    assert outs["w1"] == outs["w2"] == outs["split"]
    rows = [json.loads(r) for r in outs["w1"]["rows.jsonl"]]
    assert len(rows) == 2 * 2 * len(arms)
    assert all(r["status"] == "completed_valid" and r["mode"] == mode for r in rows)
    capsys.readouterr()


def test_legacy_census_invocation_has_no_new_key(tmp_path, capsys):
    out = tmp_path / "r.jsonl"
    assert main(["census", "--panel", "main", "--m", "3", "--bits", "12", "--curves", "1",
                 "--known-log-max-bits", "12", "--quiet", "--out", str(out)]) == 0
    rows = [json.loads(l) for l in open(out)]
    assert {r["arm"] for r in rows} == {"subgroup", "dickson", "small_x", "random_sub_r0",
                                        "random_sub_r1", "random_sub_r2", "random_dick_r0",
                                        "random_dick_r1", "random_dick_r2", "known_log"}
    for r in rows:
        assert "relcount_version" not in r
        h = r["harvest"]
        assert "relcount_version" not in h and "rows_digest" not in h and "at_X_fix" not in h["SS"]
        assert "relations_distinct" not in h["TT"]["at_stop"]
    capsys.readouterr()


def test_digest_classes_equal_written_rows(tmp_path, capsys):
    base = ["census", "--panel", "main", "--m", "3", "--bits", "14", "--curves", "1",
            "--arms", "random_sub_r0", "--known-log-max-bits", "0", "--relcount", "--quiet"]
    a, b = tmp_path / "a", tmp_path / "b"
    a.mkdir()
    b.mkdir()
    assert main(base + ["--modes", "table", "--retain", "all", "--out", str(a / "r.jsonl"),
                        "--rows-out", str(a / "h.jsonl")]) == 0
    assert main(base + ["--modes", "search", "--retain", "all", "--digest-classes", "TT", "TB",
                        "--encoding-budget-lambda", "2", "--out", str(b / "r.jsonl"),
                        "--rows-out", str(b / "h.jsonl")]) == 0
    ra = json.loads(open(a / "r.jsonl").readline())
    rb = json.loads(open(b / "r.jsonl").readline())
    hrows = [json.loads(l) for l in open(a / "h.jsonl")]
    for cname in ("TT", "TB"):
        assert ra["harvest"][cname] == rb["harvest"][cname]
        h = hashlib.sha256()
        for r in hrows:
            if r["class"] == cname:
                rec = {kk: v for kk, v in r.items() if kk not in ("bits", "curve", "m", "arm", "mode")}
                h.update(harvest_mod.canonical_row_line(rec))
        assert rb["harvest"]["rows_digest"][cname] == h.hexdigest()
    assert not [l for l in open(b / "h.jsonl") if json.loads(l)["class"] != "SS"]
    capsys.readouterr()

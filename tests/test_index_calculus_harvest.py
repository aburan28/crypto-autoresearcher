"""Tests for the collision harvest of EXP-PFDR-1b78f7 (IC-8).

Every test here is on toy curves (p <= 2^20).  tests/test_index_calculus_fp.py
covers the engine itself and must pass unedited.
"""

from __future__ import annotations

import itertools
import json
import math
import random
from collections import Counter

import pytest

from crypto_autoresearcher.index_calculus.__main__ import (
    _instance,
    _instance_j0,
    j0_prime_filter,
    main,
)
from crypto_autoresearcher.index_calculus.curve import (
    Curve,
    generate_prime_order_curve,
    generate_prime_order_curve_j0,
    is_probable_prime,
)
from crypto_autoresearcher.index_calculus.decompose import DecompStats, decompose
from crypto_autoresearcher.index_calculus.factor_base import (
    FACTOR_BASES,
    FactorBase,
    build_factor_base,
    default_fb_size,
    dickson_value,
    subgroup_prime_filter,
)
from crypto_autoresearcher.index_calculus.harvest import (
    CLASSES,
    Harvester,
    SearchRecorder,
    census_elimination,
    formal_basis_j0,
    formal_basis_known_log,
    j0_omega_lambda,
    unpack,
)
from crypto_autoresearcher.index_calculus.solver import solve_index_calculus
from crypto_autoresearcher.index_calculus.tails import TailTable

SOLVER_COLUMNS = ("k", "verified", "attempts", "relations", "rank", "s3_solves",
                  "table_s3_solves", "table_entries", "membership_tests", "group_ops",
                  "target_ops", "la_ops", "la_pivot", "factor_base", "table_arity")


def _hard_targets(E, fb, m, count, seed):
    """Random points, planted sums of m base points, points of +/-F and sums of
    fewer base points (whose searches hit the degenerate index or return early)."""
    rng = random.Random(seed)
    out = []
    while len(out) < count:
        kind = len(out) % 5
        if kind == 0:
            R = E.random_point(rng)
        else:
            R = None
            for _ in range(max(1, (m, 1, m - 1, m - 2)[kind - 1])):
                F = rng.choice(fb.points)
                R = E.add(R, F if rng.random() < 0.5 else E.neg(F))
        if R is not None:
            out.append(R)
    return out


@pytest.fixture(scope="module")
def curve14():
    return generate_prime_order_curve(14, seed=3)


# -- TT / TB groups against brute force -------------------------------------------------

def _brute_tails(E, fb, h):
    """Every tail the table must hold, enumerated independently: orderings
    (i_1, +1), (i_2, s_2), ... with i_1 <= ... <= i_h whose every suffix has a
    non-zero sum.  x -> list of (aggregated vector as a key, y-bit)."""
    n, pts = len(fb), fb.points
    out: dict[int, list] = {}
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
            key = tuple(sorted((i, c) for i, c in v.items() if c))
            out.setdefault(S[0], []).append((key, int(S[1] > E.p // 2)))
    return out


def _expected_table_counts(E, fb, brute):
    """TT/TB raw pairs and dup_formal from the brute-force groups (empty formal basis)."""
    half = E.p // 2
    exp = {"TT": [0, 0], "TB": [0, 0]}  # [pairs_raw, dup_formal]
    for x, tails in brute.items():
        b = fb.index.get(x)
        if len(tails) < 2 and b is None:
            continue
        first_y = (fb.points[b][1] > half) if b is not None else None
        # the table's group order is its stored order, but the counts do not depend on it
        if first_y is None:
            first_y = tails[0][1]
        keys = []
        for key, yb in tails:
            sig = 1 if yb == first_y else -1
            keys.append(tuple((i, sig * c) for i, c in key))
        beta = ((b, 1),) if b is not None else None
        distinct, seen = [], set()
        for k in keys:
            if beta is not None and k == beta:
                exp["TB"][1] += 1
                continue
            if k in seen:
                exp["TT"][1] += 1
                continue
            seen.add(k)
            distinct.append(k)
        if beta is not None:
            exp["TB"][0] += len(distinct)
        exp["TT"][0] += len(distinct) * (len(distinct) - 1) // 2
    return exp


@pytest.mark.parametrize("h,size", [(2, 20), (3, 9)])
@pytest.mark.parametrize("accelerate", [False, True])
def test_tt_tb_groups_match_brute_force(curve14, h, size, accelerate):
    if accelerate:
        pytest.importorskip("numpy")
    E, P = curve14
    assert E.p <= 1 << 14
    fb = build_factor_base(E, "random", size, seed=h)
    tab = TailTable(E, fb, h, accelerate=accelerate)
    brute = _brute_tails(E, fb, h)
    # every stored x-key with its tails equals the independent enumeration
    got = {}
    for x, codes in tab.iter_keys():
        lst = []
        for code in codes:
            tail, yb = tab.decode(code)
            assert tail[0][1] == 1  # stored orientation
            v = Counter()
            for i, s in tail:
                v[i] += s
            lst.append((tuple(sorted((i, c) for i, c in v.items() if c)), yb))
        got[x] = sorted(lst)
    assert got == {x: sorted(t) for x, t in brute.items()}
    sel = dict(tab.iter_keys_selected(fb.index.keys()))
    assert sel == {x: c for x, c in tab.iter_keys() if len(c) >= 2 or x in fb.index}
    Q = E.mul(5, P)
    hv = Harvester(E, P, Q, fb, tab, "census", None)
    hv.table_phase()
    exp = _expected_table_counts(E, fb, brute)
    for cname in ("TT", "TB"):
        c = hv.cls[cname]
        assert [c.pairs_raw, c.dup_formal] == exp[cname], cname
        assert c.cert_fail == 0 and c.cert_pass == c.rows_emitted
    if h == 3:
        assert hv.cls["TB"].dup_formal > 0  # F_a - F_a + F_b cancellations at h = 3


# -- recorder: encodings are exactly the charged S_3 solves ------------------------------

@pytest.mark.parametrize("m", [3, 4, 5])
def test_recorder_encodings_are_the_charged_s3_solves(m):
    np = pytest.importorskip("numpy")
    E, P = generate_prime_order_curve(16, 7)
    size = 60 if m == 3 else 52 if m == 4 else 14
    fb = build_factor_base(E, "random", size, seed=m)
    h = (m + 1) // 2
    tab_np = TailTable(E, fb, h, accelerate=True)
    tab_py = TailTable(E, fb, h, accelerate=False)
    early = degenerate = 0
    for R in _hard_targets(E, fb, m, 20, seed=m):
        encs = []
        for accelerate, tab in ((True, tab_np), (False, tab_py)):
            rec = SearchRecorder(fb, E.p, E.a)
            stats = DecompStats()
            ops0 = E.ops.group_ops
            rel = decompose(E, fb, R, m, stats, accelerate=accelerate, table=tab, recorder=rec)
            # identity G5 at the level of one decomposition
            assert rec.encodings_recorded == 2 * stats.s3_solves - rec.degenerate_roots
            xs, ds = rec.take()
            xs = [int(x) for x in xs]
            ds = [int(d) for d in ds]
            # the recorder never touched the solver's counters: compare with a recorder-free run
            stats2 = DecompStats()
            ops1 = E.ops.group_ops
            rel2 = decompose(E, fb, R, m, stats2, accelerate=accelerate, table=tab)
            assert rel == rel2 and stats == stats2
            assert E.ops.group_ops - ops1 == ops1 - ops0
            # each encoding is R - (head + s F_j), recomputed independently
            Ev = Curve(E.p, E.a, E.b, E.order)
            for x, d in zip(xs, ds):
                t, hid, j, s, yb = unpack(d)
                S = None
                for i, si in rec.heads[hid]:
                    S = Ev.add(S, fb.points[i] if si > 0 else Ev.neg(fb.points[i]))
                S = Ev.add(S, fb.points[j] if s > 0 else Ev.neg(fb.points[j]))
                T = Ev.sub(R, S)
                assert T is not None and T[0] == x and int(T[1] > E.p // 2) == yb
            encs.append(list(zip(xs, ds)))
            degenerate += rec.degenerate_roots
            if rel is not None:
                early += 1
        assert encs[0] == encs[1]  # accelerated and scalar paths record the same encodings
    assert early > 0  # some scans returned early
    if m == 3:
        assert degenerate > 0  # targets in +/-F hit the degenerate index


# -- certificates -----------------------------------------------------------------------

def test_every_row_certifies_and_a_corrupted_row_fails():
    E, P, Q, k = _instance(16, 1, 0, subgroup_prime_filter([3, 4, 5], 0.15))
    rows = []
    for m in (3, 4):
        rows = []  # keep the m = 4 rows for the corruption check below
        fb = FactorBase.random(E, default_fb_size(E.order, m), seed=1)
        res = solve_index_calculus(E, P, Q, m=m, seed=1, factor_base=fb, engine="mitm",
                                   harvest="census", harvest_sink=rows.append)
        for c in CLASSES:
            st = res.harvest[c]["at_stop"]
            assert st["cert_fail"] == 0 and st["cert_pass"] == st["rows_emitted"]
    assert rows and {r["class"] for r in rows} >= {"SS"}
    fb = FactorBase.random(E, default_fb_size(E.order, 4), seed=1)
    tab = TailTable(E, fb, 2)
    hv = Harvester(E, P, Q, fb, tab, "census", None)
    ss = [r for r in rows if r["class"] == "SS" and r["kcoef"]][0]
    # recertify one logged row on this base, then corrupt it
    co = {i: c for i, c in ss["coeffs"]}
    assert hv.certify(co, ss["kcoef"], ss["rhs"])
    assert not hv.certify(co, ss["kcoef"], ss["rhs"] + 1)
    co2 = dict(co)
    i0 = next(iter(co2))
    co2[i0] += 1
    assert not hv.certify(co2, ss["kcoef"], ss["rhs"])


# -- passive mode and harvest on ---------------------------------------------------------

@pytest.mark.parametrize("m", [3, 4, 5])
@pytest.mark.parametrize("kind", ["small_x", "random", "subgroup", "dickson"])
def test_census_mode_leaves_every_solver_column_identical(m, kind):
    E, P, Q, k = _instance(16, 2, 0, subgroup_prime_filter([3, 4, 5], 0.15))
    fb = build_factor_base(E, kind, default_fb_size(E.order, m), seed=2)
    out = {}
    for mode in ("off", "census"):
        E.ops.group_ops = 0
        out[mode] = solve_index_calculus(E, P, Q, m=m, fb_kind=kind, seed=2, factor_base=fb,
                                         engine="mitm", harvest=mode)
    for col in SOLVER_COLUMNS:
        assert getattr(out["off"], col) == getattr(out["census"], col), col
    assert out["off"].harvest is None
    assert out["census"].harvest["ss_store"]["identity_ok"]
    assert out["off"].verified and out["off"].k == k


def test_harvest_on_stops_no_later_and_verifies():
    E, P, Q, k = _instance(18, 0, 0, subgroup_prime_filter([3, 4, 5], 0.15))
    for m in (3, 4, 5):
        fb = FactorBase.small_x(E, default_fb_size(E.order, m))
        off = solve_index_calculus(E, P, Q, m=m, seed=0, factor_base=fb, engine="mitm")
        on = solve_index_calculus(E, P, Q, m=m, seed=0, factor_base=fb, engine="mitm",
                                  harvest="on", attempt_budget=len(fb))
        assert on.attempts <= off.attempts
        assert on.verified and on.k == k
        assert on.harvest["on"]["k_determined_by"] in ("decomp", "TT", "TB", "SS")
        assert on.harvest["terminated_by"] == "k_found"


def test_harvest_needs_the_mitm_engine(curve14):
    E, P = curve14
    with pytest.raises(ValueError):
        solve_index_calculus(E, P, E.mul(3, P), m=3, engine="enumerate", harvest="census")


def test_target_label_replaces_fb_kind_in_the_target_stream(curve14):
    E, P = curve14
    Q = E.mul(99, P)
    fb = FactorBase.small_x(E, default_fb_size(E.order, 3))
    a = solve_index_calculus(E, P, Q, m=3, fb_kind="small_x", factor_base=fb, engine="mitm")
    b = solve_index_calculus(E, P, Q, m=3, fb_kind="random", factor_base=fb, engine="mitm",
                             harvest="census", target_label="small_x")
    assert (a.attempts, a.relations, a.s3_solves) == (b.attempts, b.relations, b.s3_solves)


# -- factor bases -------------------------------------------------------------------------

def test_dickson_builder():
    E, _ = generate_prime_order_curve(18, 4, p_filter=subgroup_prime_filter([3], 0.15))
    size = default_fb_size(E.order, 3)
    fb = FactorBase.dickson(E, size, seed=4)
    sub = FactorBase.subgroup(E, size, seed=4)
    p = E.p
    d, c, g, lam = (fb.params[k] for k in ("d", "c", "coset", "lambda"))
    assert d == sub.params["d"]  # same divisor rule as the subgroup base
    assert "dickson" in FACTOR_BASES
    xs = [P[0] for P in fb.points]
    assert len(set(xs)) == len(xs) and len(fb) > 0
    assert all(E.is_on_curve(P) for P in fb.points)
    assert all(dickson_value(x, c, d, p) == lam for x in xs)
    f = fb.membership_poly()
    assert max(f) == d
    assert all(sum(cf * pow(x, e, p) for e, cf in f.items()) % p == 0 for x in xs)
    assert pow(c * pow(g, -2, p) % p, d, p) != 1  # c not in g^2 mu_d
    # the d preimages u = g zeta^t give d distinct x
    from crypto_autoresearcher.index_calculus.curve import primitive_root

    zeta = pow(primitive_root(p), (p - 1) // d, p)
    us = [g * pow(zeta, t, p) % p for t in range(d)]
    assert len({(u + c * pow(u, -1, p)) % p for u in us}) == d
    assert build_factor_base(E, "dickson", size, 4).points == fb.points


def test_subgroup_default_is_unchanged_and_divisor_multiple_of(curve14):
    E, _ = curve14
    a = FactorBase.subgroup(E, 20, 3)
    assert set(a.params) == {"d", "coset", "seed", "target_size"}
    b = FactorBase.subgroup(E, 20, 3, divisor_multiple_of=3)
    assert b.params["d"] % 3 == 0 and b.params["divisor_multiple_of"] == 3


def test_known_log_base_and_its_formal_basis():
    E, P, Q, k = _instance(16, 3, 0, subgroup_prime_filter([3, 4, 5], 0.15))
    s = 30
    fb = FactorBase.known_log(E, P, s)
    Ev = Curve(E.p, E.a, E.b, E.order)
    assert all(Ev.mul(j, P) == F for j, F in enumerate(fb.points, 1))
    assert "known_log" not in FACTOR_BASES
    with pytest.raises(NotImplementedError):
        fb.membership_poly()
    basis = formal_basis_known_log(s)
    assert census_elimination(E.order, basis).rank == s - 1
    res = solve_index_calculus(E, P, Q, m=3, seed=3, factor_base=fb, engine="mitm",
                               harvest="census", max_attempts=40, attempt_budget=s,
                               formal_basis={"kind": "known_log", "rows": basis})
    h = res.harvest
    assert h["formal_basis_rank"] == s - 1 and h["U"] == 1
    for c in ("TT", "TB"):
        st = h[c]["at_stop"]
        assert st["rows_emitted"] > 0
        assert st["informative_rank"] == 0
        assert st["pairs_formal"] == st["pairs_raw"]
    assert h["terminated_by"] in ("attempt_cap", "k_found")


def test_j0_generator_lambda_and_formal_basis():
    pf = j0_prime_filter(0.15)
    E, P = generate_prime_order_curve_j0(18, 1, p_filter=pf)
    assert E.a == 0 and E.p % 3 == 1 and pf(E.p)
    assert is_probable_prime(E.order) and E.mul(E.order, P) is None
    E2, P2 = generate_prime_order_curve_j0(18, 1, p_filter=pf)
    assert (E.p, E.b, P) == (E2.p, E2.b, P2)
    omega, lam = j0_omega_lambda(E, P)
    assert pow(omega, 3, E.p) == 1 and omega != 1
    assert (lam * lam + lam + 1) % E.order == 0
    assert Curve(E.p, 0, E.b, E.order).mul(lam, P) == (omega * P[0] % E.p, P[1])
    fb = FactorBase.subgroup(E, default_fb_size(E.order, 3), 1, divisor_multiple_of=3)
    assert len(fb) % 3 == 0
    basis = formal_basis_j0(E, fb, omega, lam)
    assert census_elimination(E.order, basis).rank * 3 == 2 * len(fb)
    E3, P3, Q3, k3 = _instance_j0(18, 1, 0, pf)
    assert E3.mul(k3, P3) == Q3


# -- rank instrument: the duplicated-column fixture ---------------------------------------

def test_duplicated_column_fixture_rank_deficit_and_permutation_stability():
    N = 1_000_003  # prime
    B = 24
    rng = random.Random(11)
    rows = []
    for _ in range(3 * B):
        row = {c: rng.randrange(1, N) for c in rng.sample(range(B), 6)}
        # columns 3 and 17 forced equal
        v = row.get(3, row.get(17))
        if v is not None:
            row[3] = row[17] = v
        rows.append(row)
    st = census_elimination(N)
    for r in rows:
        st.add_row(dict(r), 0, 0)
    assert st.rank <= B - 1
    assert B - st.rank == 1  # deficit exactly 1 on this fixture
    ctrl = census_elimination(N)
    for r in rows:
        r2 = dict(r)
        r2.pop(17, None)
        ctrl.add_row(r2, 0, 0)
    assert ctrl.rank == B - 1  # the deficit is the forced column, nothing else
    for seed in range(1, 6):
        perm = rows[:]
        random.Random(seed).shuffle(perm)
        st2 = census_elimination(N)
        for r in perm:
            st2.add_row(dict(r), 0, 0)
        assert st2.rank == st.rank


# -- formal duplicates at m = 4 ----------------------------------------------------------

def test_repeated_target_encodings_are_formal_duplicates_at_m4():
    E, P, Q, k = _instance(16, 4, 0, subgroup_prime_filter([3, 4, 5], 0.15))
    fb = FactorBase.random(E, default_fb_size(E.order, 4), seed=4)
    tab = TailTable(E, fb, 2)
    hv = Harvester(E, P, Q, fb, tab, "census", None)
    hv.table_phase()
    rows = []
    rng = random.Random(4)
    zero_per_attempt = []
    for t in range(1, 16):
        a, b = rng.randrange(E.order), rng.randrange(1, E.order)
        R = E.add(E.mul(a, P), E.mul(b, Q))
        hv.begin_attempt(t, a, b)
        decompose(E, fb, R, 4, DecompStats(), table=tab, recorder=hv.recorder)
        rows.extend(hv.end_attempt())
        ds = hv.last_batch[1]
        zeros = 0
        for d in [int(x) for x in ds]:
            _, hid, j, s, _ = unpack(d)
            (i1, s1), = hv.recorder.heads[hid]
            if i1 == j and s1 == -s:
                zeros += 1  # A = F_i - F_i: the encoding is R_t itself
        zero_per_attempt.append(zeros)
    expected = sum(max(0, z - 1) for z in zero_per_attempt)
    assert expected > 0
    assert hv.cls["SS"].dup_formal == expected
    # no emitted row is the trivial row of a duplicate
    assert all(co or kc % E.order or rh % E.order for _, co, kc, rh in rows)


# -- census CLI determinism ----------------------------------------------------------------

def _strip(r):
    r = dict(r)
    r.pop("seconds", None)
    h = r.get("harvest")
    if h:
        h = dict(h)
        for kk in ("harvest_seconds", "worker_maxrss_bytes"):
            h.pop(kk, None)
        r["harvest"] = h
    return json.dumps(r, sort_keys=True)


def test_census_cli_is_deterministic_across_workers(tmp_path, capsys):
    outs = {}
    for w in (1, 2):
        d = tmp_path / f"w{w}"
        d.mkdir()
        argv = ["census", "--panel", "main", "--m", "3", "--bits", "12", "14", "--curves", "2",
                "--known-log-max-bits", "14", "--workers", str(w), "--quiet",
                "--out", str(d / "rows.jsonl"), "--rows-out", str(d / "h.jsonl"),
                "--staircase-out", str(d / "s.jsonl")]
        assert main(argv) == 0
        outs[w] = {name: sorted(_strip(json.loads(l)) for l in open(d / name))
                   for name in ("rows.jsonl", "h.jsonl", "s.jsonl")}
    assert outs[1] == outs[2]
    rows = [json.loads(r) for r in outs[1]["rows.jsonl"]]
    assert len(rows) == 2 * 2 * (9 * 2 + 2)  # rungs x curves x (9 arms x 2 modes + known_log x 2)
    assert all(r["status"] == "completed_valid" for r in rows)
    capsys.readouterr()


def test_sweep_harvest_off_rows_carry_no_new_key(tmp_path, capsys):
    rows = {}
    for mode in ("off", "census"):
        out = tmp_path / f"{mode}.jsonl"
        assert main(["sweep", "--bits", "12", "14", "--curves", "1", "--rho-curves", "1",
                     "--m", "3", "--fb", "small_x", "subgroup", "--engine", "mitm",
                     "--harvest", mode, "--quiet", "--out", str(out)]) == 0
        rows[mode] = {(r["bits"], r["curve"], r["method"], r["fb"]): r
                      for r in map(json.loads, open(out))}
    for key, r in rows["off"].items():
        assert "harvest" not in r
        c = dict(rows["census"][key])
        if r["method"] != "rho":
            assert "harvest" in c
        c.pop("harvest", None)
        assert {k: v for k, v in c.items() if k != "seconds"} == \
            {k: v for k, v in r.items() if k != "seconds"}
    assert main(["sweep", "--bits", "12", "--curves", "1", "--engine", "enumerate",
                 "--harvest", "census", "--quiet"]) == 2
    capsys.readouterr()

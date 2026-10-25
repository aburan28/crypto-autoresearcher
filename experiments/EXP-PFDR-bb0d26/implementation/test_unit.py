"""Unit tests UT-1 .. UT-12 of EXP-PFDR-bb0d26 (run: python3 test_unit.py or python3 -m pytest).

Readiness tests only; a pass is never evidence about H-PFDR-727bfc. Every curve comes from the
selftest seed block (8,900,000 + c) at bits <= 20; no main-block or replication-block curve is
generated (the guards in setUpModule raise if any is requested), the log-GAP builder is never
run at a design cell size (n >= 256 at bits >= 20), and no ratio of structured to null counts is
computed anywhere: builder and kernel equality tests assert exact equality only, the planted
control and the calibration use planted and null sets only, and the analysis tests use
fabricated numbers.
"""
from __future__ import annotations

import sys

sys.dont_write_bytecode = True
import argparse  # noqa: E402
import copy  # noqa: E402
import hashlib  # noqa: E402
import json  # noqa: E402
import math  # noqa: E402
import os  # noqa: E402
import random  # noqa: E402
import re  # noqa: E402
import shutil  # noqa: E402
import statistics  # noqa: E402
import subprocess  # noqa: E402
import tempfile  # noqa: E402
import time  # noqa: E402
import unittest  # noqa: E402

os.environ["PYTHONDONTWRITEBYTECODE"] = "1"
SCRATCH = os.environ.get("PFDR_SCRATCH", "/tmp/claude-0/-home-user/015c3767-cc03-52db-9b0c-bd2aa6c26537/scratchpad/bb0d26")
os.makedirs(SCRATCH, exist_ok=True)
tempfile.tempdir = SCRATCH

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import check  # noqa: E402
import run  # noqa: E402

SPEC = os.path.join(HERE, "..", "specification.yaml")
KERNEL = ""
WORK = ""
_REAL_GET_CURVE = run.get_curve
_REAL_GAP = run.gap_builder


def _guarded_get_curve(bits, block, c):
    assert block == "selftest", f"unit tests may only use the selftest block, got {block}"
    assert bits <= 20, "unit tests use bits <= 20"
    return _REAL_GET_CURVE(bits, block, c)


def _guarded_gap(E, r, n, rng, keep_vectors=False):
    assert n < 256 or E.p.bit_length() < 20, "log-GAP is never built at a design cell size in tests"
    return _REAL_GAP(E, r, n, rng, keep_vectors)


def setUpModule():
    global KERNEL, WORK
    WORK = tempfile.mkdtemp(prefix="ut-")
    KERNEL = run.build_kernel(os.path.join(WORK, "kernel"))
    run.get_curve = _guarded_get_curve
    run.gap_builder = _guarded_gap


def tearDownModule():
    run.get_curve = _REAL_GET_CURVE
    run.gap_builder = _REAL_GAP
    shutil.rmtree(WORK, ignore_errors=True)


def brute(X, p):
    """Test-local dictionary count (shares nothing with run.py)."""
    d = {}
    for i in range(len(X)):
        for j in range(i + 1, len(X)):
            s = (X[i] + X[j]) % p
            d[s] = d.get(s, 0) + 1
    return sum(m * (m - 1) // 2 for m in d.values()), len(d)


def kern(X, p):
    r = run.run_kernel(KERNEL, p, [X])[0]
    return r[2], r[3]


def nd(p):
    return random.Random(p)


def strip(rec):
    return {k: v for k, v in rec.items() if k != "seconds"}


# ------------------------------------------------------------------ fabricated numbers (analysis tests only)

def fab_design(curves=6):
    return [dict(c, n_curves=curves) for c in run.cells()]


def fab_rec(cell, block, c, rng, mu=700.0, sigma=20.0, kappa=1.0, plant=1.4):
    pairs = cell["n"] * (cell["n"] - 1) // 2
    nullc = [max(1, round(rng.gauss(mu, sigma))) for _ in range(run.NULL_REPS)]
    gap = max(1, round(rng.gauss(mu * kappa, sigma)))
    pl = max(1, round(rng.gauss(mu * plant, sigma)))
    return {"cell": cell["cell"], "block": block, "c": c, "p": 1_000_003, "a": 1, "b_coef": 2, "N": 1_000_001,
            "bits": cell["bits"], "r": cell["r"], "n": cell["n"], "status": "ok",
            "null_C": nullc, "null_D": [pairs - x for x in nullc], "gap_C": gap, "gap_D": pairs - gap,
            "gap_meta": {"T": 5, "enumerated": 9, "duplicate_skips": 0, "first": [1], "last": [9]},
            "plant_m": 10, "plant_internal": 5, "plant_C": pl, "plant_D": pairs - pl, "plant_feasible": True,
            "seconds": 0.0}


def fab_block(design, block, seed, over=None):
    """over: cell id -> dict of fab_rec keyword overrides."""
    rng = random.Random(seed)
    over = over or {}
    return [fab_rec(cell, block, c, rng, **over.get(cell["cell"], {}))
            for cell in design for c in range(cell["n_curves"])]


def write_jsonl(path, recs):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w") as f:
        for r in recs:
            f.write(json.dumps(r, sort_keys=True) + "\n")


def ap_labels(E, n, rng):
    """First n labels of L along a true AP x0 + k w (a pseudo-structured set)."""
    x0, w = rng.randrange(E.p), rng.randrange(1, E.p)
    out, k = [], 0
    while len(out) < n:
        x = (x0 + k * w) % E.p
        if run.in_label_universe(E, x):
            out.append(x)
        k += 1
    return out


# ------------------------------------------------------------------ UT-1 .. UT-3

class UT01Kernel(unittest.TestCase):
    def test_ut01_kernel_against_brute_force(self):
        rng = random.Random(20261022)
        checked = 0
        for t in range(60):
            bits = 12 + t % 5
            p = run.ec.next_prime(rng.randrange(1 << (bits - 1), 1 << bits))
            n = rng.randrange(8, 201)
            X = rng.sample(range(p), n)
            self.assertEqual(kern(X, p), brute(X, p), (p, n))
            checked += 1
        # forced coincidences: an AP and a set with a+b=c+d built in
        p = 40009
        ap = [3 + 17 * k for k in range(60)]
        self.assertEqual(kern(ap, p), brute(ap, p))
        self.assertGreater(kern(ap, p)[0], 0)
        X = rng.sample(range(p), 30)
        X.append((X[0] + X[1] - X[2]) % p)
        self.assertEqual(kern(X, p), brute(X, p))
        self.assertGreaterEqual(kern(X, p)[0], 1)
        # only 2u = v + w holds: C must be 0
        self.assertEqual(kern([10, 20, 30], 1009), (0, 3))
        self.assertEqual(brute([10, 20, 30], 1009), (0, 3))
        # all sums distinct: C = 0, D = n(n-1)/2
        sidon = [2 ** k for k in range(15)]
        self.assertEqual(kern(sidon, 65521), (0, 15 * 14 // 2))
        # wraparound mod p and the smallest sets
        self.assertEqual(kern([0, 50, 51, 100], 101), brute([0, 50, 51, 100], 101))
        self.assertEqual(kern([5, 9], 13), (0, 1))
        print(f"\nUT-1: {checked} random sets checked against a dictionary count")


class UT02KnownAnswers(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        with open(os.path.join(HERE, "fixtures", "kat.json")) as f:
            cls.kat = json.load(f)

    def test_ut02_known_answers(self):
        for s in self.kat["sets"]:
            self.assertEqual(kern(s["X"], s["p"]), (s["C"], s["D"]), s["name"])
            self.assertEqual(run.brute_CD(s["X"], s["p"]), (s["C"], s["D"]), s["name"])
            self.assertEqual(s["pairs"], len(s["X"]) * (len(s["X"]) - 1) // 2)
        first = next(s for s in self.kat["sets"] if s["name"] == "0123-mod-101")
        self.assertEqual((first["C"], first["D"]), (1, 5))
        one = next(s for s in self.kat["sets"] if s["name"] == "hand-built-one-coincidence")
        self.assertEqual((run.HAND_P, run.HAND_SET), (one["p"], one["X"]))
        self.assertEqual(kern(run.HAND_SET, run.HAND_P)[0], 1)
        for u in self.kat["label_universe"]:
            E = run.ec.Curve(u["p"], u["a"], u["b"])
            self.assertEqual([x for x in range(u["p"]) if run.in_label_universe(E, x)], u["L"])
        for h in self.kat["half_box"]:
            self.assertEqual(run.labels_needed(h["n"]), h["need"])
            self.assertEqual(run.half_box_T(h["r"], h["n"]), h["T"])
            self.assertEqual(run.half_box_size(h["r"], h["T"]), h["size"])
        for key, (r, T) in {"r1T3": (1, 3), "r2T2": (2, 2), "r3T1": (3, 1)}.items():
            self.assertEqual([list(v) for v in run.half_box_vectors(r, T)], self.kat["half_box_vectors"][key])
        d = self.kat["design"]
        self.assertEqual(d["toy_cell_count"], len(run.cells()))
        mine = {c["cell"]: c["n_curves"] for c in run.cells()}
        self.assertEqual(mine, {c["cell"]: c["n_curves"] for c in d["cells"]})
        self.assertEqual((mine["b28-r1-n256"], mine["b28-r1-n512"]), (1440, 89))
        src = self.kat["generator_source"]
        self.assertIsNone(re.search(r"^\s*(import|from)\s+(run|check|curve|vendor|labelsum)\b", src, re.M))


class UT03Builder(unittest.TestCase):
    @staticmethod
    def slow(E, pts, r, n):
        """Independent slow path: first-nonzero-positive vectors in lexicographic order, Curve.mul per coefficient."""
        need = -(-(102 * n) // 100) + 8
        T = 1
        while ((2 * T + 1) ** r - 1) // 2 < need:
            T += 1
        import itertools
        vecs = [v for v in itertools.product(range(-T, T + 1), repeat=r) if next((e for e in v if e), 0) > 0]
        labels, seen, dup, inf, used = [], set(), 0, 0, []
        for v in vecs:
            Q = None
            for ci, P in zip(v, pts):
                Q = E.add(Q, E.mul(ci, P))
            if Q is None:
                inf += 1
                continue
            if Q[0] in seen:
                dup += 1
                continue
            seen.add(Q[0])
            labels.append(Q[0])
            used.append(list(v))
            if len(labels) == n:
                break
        return labels, dup, inf, T, used

    def test_ut03_builder_against_slow_path(self):
        cases = 0
        for r in (1, 2, 3):
            for bits, c, n in ((12, 0, 24), (14, 1, 40), (16, 2, 64), (16, 5, 64)):
                E, _ = run.get_curve(bits, "selftest", c)
                labels, meta, st = run.gap_builder(E, r, n, run._rng("ut3", r, bits, c), keep_vectors=True)
                self.assertEqual(st, "ok")
                lab, dup, inf, T, used = self.slow(E, meta["points"], r, n)
                self.assertEqual(labels, lab)
                self.assertEqual(meta["vectors"], used)
                self.assertEqual((meta["duplicate_skips"], meta["infinity_skips"], meta["T"]), (dup, inf, T))
                self.assertEqual(len(set(labels)), n)
                self.assertTrue(all(run.in_label_universe(E, x) for x in labels))
                vs = meta["vectors"]
                self.assertEqual(vs, sorted(vs))                              # lexicographic
                self.assertTrue(all(next(e for e in v if e) > 0 for v in vs))   # first nonzero positive
                need = run.labels_needed(n)
                self.assertGreaterEqual(run.half_box_size(r, T), need)         # T meets the bound ...
                self.assertTrue(T == 1 or run.half_box_size(r, T - 1) < need)  # ... and is least
                self.assertEqual(meta["first"], vs[0])
                self.assertEqual(meta["last"], vs[-1])
                cases += 1
        # duplicate-skips and infinity skips are counted: P2 = 2 P1 gives c1 P1 + c2 P2 = (c1 + 2 c2) P1
        E0, _ = run.get_curve(16, "selftest", 7)
        E = run.ec.Curve(E0.p, E0.a, E0.b, E0.order)
        P1 = run.ec.Curve.random_point(E, run._rng("ut3-stub"))
        pts = [P1, E.mul(2, P1)]
        it = iter(pts)
        E.random_point = lambda _rng, it=it: next(it)
        labels, meta, st = run.gap_builder(E, 2, 8, run._rng("ut3-stub"), keep_vectors=True)
        lab, dup, inf, T, used = self.slow(E, pts, 2, 8)
        self.assertGreater(dup, 0)
        self.assertGreater(inf, 0)
        self.assertEqual((labels, meta["duplicate_skips"], meta["infinity_skips"]), (lab, dup, inf))
        # a forced tiny curve with n above the half-box / label universe gives status degenerate
        Et, _ = run.get_curve(8, "selftest", 0)
        labels, meta, st = run.gap_builder(Et, 2, 200, run._rng("ut3-tiny"))
        self.assertEqual((labels, st), (None, "degenerate"))
        rec = run.job(KERNEL, {"cell": "tiny", "bits": 8, "r": 2, "n": 200}, "selftest", 0)
        self.assertEqual(rec["status"], "degenerate")
        self.assertIsNone(rec["gap_C"])
        print(f"\nUT-3: {cases} builder cases + stub duplicates + degenerate checked")


# ------------------------------------------------------------------ UT-4, UT-5

class UT04Plant(unittest.TestCase):
    def test_ut04_positive_control_reads_as_excess(self):
        cells = [{"cell": f"u4-{bits}-{n}", "bits": bits, "r": 1, "n": n}
                 for bits, n in ((16, 128), (18, 160), (20, 192), (20, 256))]
        out = []
        for i, cell in enumerate(cells):
            recs = [run.job(KERNEL, cell, "selftest", 40 * i + c, kinds=("plant",)) for c in range(40)]
            st = run.plant_stats(recs)
            self.assertTrue(st["plant_feasible_all"], cell)
            self.assertGreaterEqual(st["plant_kappa"], 1.15, cell)
            self.assertGreater(st["plant_z"], 4, cell)
            for r in recs:
                self.assertTrue(4 <= r["plant_m"] <= cell["n"] // 2)
            out.append((cell["cell"], round(st["plant_kappa"], 3), round(st["plant_z"], 1)))
        # the plant size rule is feasible and least: re-derive m with a brute count on one curve
        E, _ = run.get_curve(16, "selftest", 3)
        n = 128
        nullc = [brute(run.null_builder(E, n, run._rng("ut4", k)), E.p)[0] for k in range(run.NULL_REPS)]
        labels, meta = run.planted_builder(E, n, run._rng("ut4-plant"), nullc, lambda ls: brute(ls, E.p)[0])
        thr = run.PLANT_FRACTION * (sum(nullc) / len(nullc))
        self.assertTrue(meta["feasible"])
        self.assertGreaterEqual(brute(labels[:meta["m"]], E.p)[0], thr)
        self.assertTrue(meta["m"] == 4 or brute(labels[:meta["m"] - 1], E.p)[0] < thr)
        self.assertEqual(len(set(labels)), n)
        # infeasible plant: an impossible fraction cap leaves m = n/2 and feasible False
        labels, meta = run.planted_builder(E, n, run._rng("ut4-plant"), [10 ** 9] * 20, lambda ls: brute(ls, E.p)[0])
        self.assertEqual((meta["m"], meta["feasible"]), (n // 2, False))
        # a hand-built set with exactly one planted coincidence yields count 1
        self.assertEqual(kern(run.HAND_SET, run.HAND_P)[0], 1)
        print("\nUT-4: planted-only controls (plant_kappa, plant_z) per cell:", out)


class UT05Calibration(unittest.TestCase):
    def test_ut05_null_passes_calibration(self):
        cells, per = [], 4
        for i in range(100):
            bits = (16, 18, 20)[i % 3]
            n = (128, 160, 192, 224)[i % 4]
            cells.append({"cell": f"u5-{i}", "bits": bits, "r": 1, "n": n})
        recs = {}
        for i, cell in enumerate(cells):
            recs[cell["cell"]] = [run.job(KERNEL, cell, "selftest", per * i + j, kinds=()) for j in range(per)]
        self.assertGreaterEqual(sum(len(v) for v in recs.values()), 200)
        zs = [run.zcal_of(v) for v in recs.values()]
        cal = run.calibration_gate(zs)
        self.assertTrue(0.75 <= cal["sd"] <= 1.25, cal)
        self.assertLessEqual(abs(cal["mean"]), 0.35, cal)
        self.assertTrue(cal["pass"])
        # measured null mean within 5% of 3 binom(n,4)/p averaged over curves
        meas = sum(statistics.fmean(r["null_C"]) for v in recs.values() for r in v)
        form = sum(run.formula_mean(r["n"], r["p"]) for v in recs.values() for r in v)
        self.assertAlmostEqual(meas / form, 1.0, delta=0.05)
        # a deliberately shifted pseudo-structured replicate (all labels from an AP) fails the gate
        shifted = []
        for i, cell in enumerate(cells):
            rs = copy.deepcopy(recs[cell["cell"]])
            for j, r in enumerate(rs):
                E, _ = run.get_curve(cell["bits"], "selftest", per * i + j)
                r["null_C"][0] = kern(ap_labels(E, cell["n"], run._rng("ut5-ap", i, j)), E.p)[0]
            shifted.append(run.zcal_of(rs))
        bad = run.calibration_gate(shifted)
        self.assertFalse(bad["pass"], bad)
        print(f"\nUT-5: calibration over {len(zs)} null cells x {per} curves: n={cal['n']} "
              f"mean={cal['mean']:.3f} sd={cal['sd']:.3f}; AP-shifted gate pass={bad['pass']}")


# ------------------------------------------------------------------ UT-6, UT-7

class UT06Scaling(unittest.TestCase):
    def test_ut06_scaling_identity(self):
        for i in range(12):
            bits = (14, 15, 16)[i % 3]
            E, _ = run.get_curve(bits, "selftest", 20 + i)
            rng = random.Random(600 + i)
            X = run.null_builder(E, 64, rng)
            u = rng.randrange(2, E.p)
            Y = [x * u * u % E.p for x in X]
            self.assertEqual(kern(X, E.p), kern(Y, E.p))
            self.assertEqual(kern(Y, E.p), brute(Y, E.p))
            # the twist isomorphism keeps the label universe: u^2 x is in L for the twisted curve only,
            # so only the counts are compared here
            self.assertNotEqual(sorted(X), sorted(Y))


class UT07Determinism(unittest.TestCase):
    def test_ut07_determinism_and_ordering(self):
        cell = {"cell": "u7-r2", "bits": 16, "r": 2, "n": 64}
        a = run.job(KERNEL, cell, "selftest", 4)
        b = run.job(KERNEL, cell, "selftest", 4)
        self.assertEqual(strip(a), strip(b))
        self.assertNotEqual(strip(a), strip(run.job(KERNEL, cell, "selftest", 5)))
        # re-running with other worker order: a 4-worker census writes the same set of records
        d = os.path.join(WORK, "ut7")
        os.makedirs(d, exist_ok=True)
        design = {"experiment": run.EXP, "toy_cells": [dict(cell, n_curves=6)]}
        with open(os.path.join(d, "design.json"), "w") as f:
            json.dump(design, f)
        for tag in ("x", "y"):
            run.cmd_census(argparse.Namespace(kernel=KERNEL, design=os.path.join(d, "design.json"),
                                              block="selftest", flags=None, out=os.path.join(d, tag), workers=4))
        ra = sorted((strip(r) for r in run.load_jsonl(os.path.join(d, "x", "toy-selftest-jobs.jsonl"))), key=lambda r: r["c"])
        rb = sorted((strip(r) for r in run.load_jsonl(os.path.join(d, "y", "toy-selftest-jobs.jsonl"))), key=lambda r: r["c"])
        self.assertEqual(ra, rb)
        # shuffling the completion order of job records leaves the bootstrap interval identical
        des = fab_design(8)
        recs = fab_block(des, "main", 77)
        cid = des[3]["cell"]
        mine = [r for r in recs if r["cell"] == cid]
        base = run.cell_stats(mine, cid + "|main")
        for seed in range(4):
            sh = mine[:]
            random.Random(seed).shuffle(sh)
            self.assertEqual(run.cell_stats(sh, cid + "|main"), base)
        full = run.analyze_records(des, recs, None, "main")
        sh = recs[:]
        random.Random(9).shuffle(sh)
        self.assertEqual(run.analyze_records(des, sh, None, "main"), full)


def _crashy_job(kernel, cell, block, c, kinds=run.KINDS):
    """Test double: the worker handling curve 1 is killed outright (an OOM kill); others run normally."""
    if c == 1:
        os._exit(9)
    return _REAL_JOB(kernel, cell, block, c, kinds)


_REAL_JOB = run.job


class UT07Infrastructure(unittest.TestCase):
    def test_ut07_crash_and_timeout_are_failed_infrastructure(self):
        d = os.path.join(WORK, "ut7b")
        os.makedirs(d, exist_ok=True)
        cell = {"cell": "u7b", "bits": 16, "r": 1, "n": 32, "n_curves": 3}
        out = os.path.join(d, "crash.jsonl")
        run.job = _crashy_job
        try:
            run._run_jobs(KERNEL, [(cell, "selftest", c) for c in range(3)], out, workers=2)
        finally:
            run.job = _REAL_JOB
        recs = run.load_jsonl(out)
        self.assertEqual(len(recs), 3)
        self.assertTrue(all(r["status"].startswith("failed_infrastructure") for r in recs if r["c"] == 1))
        self.assertTrue(any(r["status"] == "failed_infrastructure:worker_crash" for r in recs))
        # a rerun repeats only the keys that are not ok, and the final analysis input has every key accounted for
        run._run_jobs(KERNEL, [(cell, "selftest", c) for c in range(3)], out, workers=2)
        again = run.load_jsonl(out)
        self.assertEqual({r["c"] for r in again if r["status"] == "ok"}, {0, 1, 2})
        # a kernel timeout is failed_infrastructure for that job
        saved, run.KERNEL_TIMEOUT_S = run.KERNEL_TIMEOUT_S, 1e-6
        try:
            rec = run.job(KERNEL, cell, "selftest", 0)
        finally:
            run.KERNEL_TIMEOUT_S = saved
        self.assertEqual(rec["status"], "failed_infrastructure:kernel_timeout")
        # an exception inside a job is failed_infrastructure too (here an impossible n)
        bad = run.job(KERNEL, {"cell": "u7c", "bits": 16, "r": 1, "n": 6}, "selftest", 0)
        self.assertTrue(bad["status"].startswith("failed_infrastructure:exception_"))


# ------------------------------------------------------------------ UT-8

class UT08Analysis(unittest.TestCase):
    DES = fab_design(6)
    FLAG = "b24-r2-n1024"

    def an(self, over=None, rep_over=None, rep="none", mutate=None, seed=5):
        main = fab_block(self.DES, "main", seed, over)
        if mutate:
            main = mutate(main)
        repl = None
        if rep == "complete":
            repl = fab_block([c for c in self.DES if c["cell"] == self.FLAG], "rep", 99, rep_over)
        elif rep == "incomplete":
            repl = fab_block([c for c in self.DES if c["cell"] == self.FLAG], "rep", 99, rep_over)[:-1]
        elif rep == "empty":
            repl = []
        return run.analyze_records(self.DES, main, repl, "final" if rep != "none" else "main")

    def cls(self, an, cid):
        return next(r["cls"] for r in an["cells"] if r["cell"] == cid)

    def test_ut08_null_only_gives_O_NULL(self):
        a = self.an()
        self.assertEqual({r["cls"] for r in a["cells"]}, {"null"})
        self.assertTrue(a["calibration"]["pass"], a["calibration"])
        self.assertEqual((a["outcome"], a["headline"]), ("O-NULL", "SUPPORT_SCOPED"))
        self.assertEqual(a["flagged_cells"], [])
        self.assertEqual(a["fraction_valid"], 1.0)

    def test_ut08_flagged_cell_replication_states(self):
        over = {self.FLAG: {"kappa": 1.15}}
        a = self.an(over)
        self.assertEqual(self.cls(a, self.FLAG), "flagged")
        self.assertEqual(a["flagged_cells"], [self.FLAG])
        self.assertEqual((a["outcome"], a["headline"]), ("O-PENDING-REPLICATION", "INCONCLUSIVE"))   # analyze-main value
        s = self.an(over, {self.FLAG: {"kappa": 1.15}}, rep="complete")
        self.assertEqual((s["outcome"], s["headline"]), ("O-STRUCT", "FALSIFY_SCOPED"))
        row = next(r for r in s["cells"] if r["cell"] == self.FLAG)
        self.assertTrue(row["replication"]["survives"])
        self.assertEqual(row["replication"]["status"], "complete")
        inc = self.an(over, {self.FLAG: {"kappa": 1.15}}, rep="incomplete")
        self.assertEqual((inc["outcome"], inc["headline"]), ("O-PENDING-REPLICATION", "INCONCLUSIVE"))
        self.assertEqual(next(r for r in inc["cells"] if r["cell"] == self.FLAG)["replication"]["status"], "incomplete")
        self.assertIsNotNone(inc["reading_note"])
        emp = self.an(over, rep="empty")
        self.assertEqual(emp["outcome"], "O-PENDING-REPLICATION")
        nosurv = self.an(over, {self.FLAG: {"kappa": 1.0}}, rep="complete")
        self.assertEqual((nosurv["outcome"], nosurv["headline"]), ("O-MIXED", "INCONCLUSIVE"))
        opp = self.an(over, {self.FLAG: {"kappa": 0.8}}, rep="complete")        # opposite sign never survives
        self.assertNotEqual(opp["outcome"], "O-STRUCT")

    def test_ut08_other_classes(self):
        under = self.an({self.FLAG: {"mu": 100.0}})
        self.assertEqual(self.cls(under, self.FLAG), "inconclusive_underpowered")
        self.assertEqual(under["outcome"], "O-NULL")                      # 44 of 45 valid, all null
        noplant = self.an({self.FLAG: {"plant": 1.0}})
        self.assertEqual(self.cls(noplant, self.FLAG), "inconclusive_plant_not_recovered")
        infeasible = self.an(mutate=lambda m: [dict(r, plant_feasible=False) if (r["cell"], r["c"]) == (self.FLAG, 2) else r for r in m])
        self.assertEqual(self.cls(infeasible, self.FLAG), "inconclusive_plant_not_recovered")
        self.assertIn(self.FLAG, infeasible["plant_infeasible_cells"])
        inter = self.an({self.FLAG: {"kappa": 1.07}})
        self.assertEqual(self.cls(inter, self.FLAG), "intermediate")
        self.assertEqual((inter["outcome"], inter["headline"]), ("O-MIXED", "INCONCLUSIVE"))
        # a failed_infrastructure job and a degenerate job invalidate their cell
        for status in ("failed_infrastructure:kernel_timeout", "degenerate"):
            bad = self.an(mutate=lambda m, s=status: [dict(r, status=s) if (r["cell"], r["c"]) == (self.FLAG, 2) else r for r in m])
            self.assertEqual(self.cls(bad, self.FLAG), "invalid")
            self.assertEqual(bad["failed_jobs"][0]["cell"], self.FLAG)
            self.assertEqual(bad["outcome"], "O-NULL")                     # 44/45 cells valid and all null: >= 80%
        # fewer than half the cells valid: O-INVALID
        many = {c["cell"]: {"mu": 100.0} for c in self.DES[:25]}
        inv = self.an(many)
        self.assertLess(inv["fraction_valid"], 0.5)
        self.assertEqual((inv["outcome"], inv["headline"]), ("O-INVALID", "NOT_EVIDENCE"))

    def test_ut08_calibration_failure_is_not_evidence(self):
        def shift(m):
            for r in m:
                r["null_C"][0] = round(r["null_C"][0] * 1.4)
            return m
        a = self.an(mutate=shift)
        self.assertFalse(a["calibration"]["pass"])
        self.assertEqual((a["outcome"], a["headline"]), ("O-INVALID", "NOT_EVIDENCE"))

    def test_ut08_analyze_commands_complete_on_toy_data(self):
        d = os.path.join(WORK, "ut8")
        os.makedirs(d, exist_ok=True)
        with open(os.path.join(d, "design.json"), "w") as f:
            json.dump({"experiment": run.EXP, "toy_cells": self.DES}, f)
        over = {self.FLAG: {"kappa": 1.15}}
        write_jsonl(os.path.join(d, "main.jsonl"), fab_block(self.DES, "main", 5, over))
        write_jsonl(os.path.join(d, "rep.jsonl"), fab_block([c for c in self.DES if c["cell"] == self.FLAG], "rep", 99, over))
        a = run.cmd_analyze(argparse.Namespace(design=os.path.join(d, "design.json"), main=os.path.join(d, "main.jsonl"),
                                               rep=None, out=os.path.join(d, "analysis-main.json")))
        self.assertEqual(a["outcome"], "O-PENDING-REPLICATION")
        self.assertEqual(json.load(open(os.path.join(d, "flags.json")))["flagged_cells"], [self.FLAG])
        f = run.cmd_analyze(argparse.Namespace(design=os.path.join(d, "design.json"), main=os.path.join(d, "main.jsonl"),
                                               rep=os.path.join(d, "rep.jsonl"), out=os.path.join(d, "analysis.json")))
        self.assertEqual((f["outcome"], f["headline"]), ("O-STRUCT", "FALSIFY_SCOPED"))
        for name in ("analysis-main.json", "analysis.json", "flags.json"):
            json.load(open(os.path.join(d, name)))
        # the slope and tail fields are present
        self.assertIn("b20-r1", f["secondary_slope_logkappa_per_log2n"])
        self.assertIsNotNone(f["largest_abs_z"])


# ------------------------------------------------------------------ UT-9

class UT09Checker(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.root = os.path.join(WORK, "ut9", "runs")
        shutil.rmtree(os.path.dirname(cls.root), ignore_errors=True)
        os.makedirs(cls.root)
        cls.plans = {}

        def sha_map():
            out = {}
            for rel in ("run.py", "check.py", "labelsum.c", "vendor/curve.py", "fixtures/kat.json"):
                out[check.IMPL_REL + rel] = check.sha256_file(os.path.join(HERE, rel))
            return out

        def mk(name, trials):
            plan = {"schema": "crypto.autoresearch.trial_plan.v1", "experiment_id": run.EXP, "task_id": "TASK-UT9",
                    "source_sha256": sha_map(), "trials": trials}
            path = os.path.join(os.path.dirname(cls.root), name)
            with open(path, "w") as f:
                json.dump(plan, f, indent=1, sort_keys=True)
            cls.plans[name] = path
            return path

        row = {t["id"]: t for t in run.TRIAL_TABLE}

        def trial(tid, run_id, **kw):
            t = row[tid]
            d = {"id": tid, "run_id": run_id, "stage": t["stage"], "artifacts": list(t["artifacts"]),
                 "memory_mb": t["memory_mb"], "watchdog_seconds": t["watchdog_seconds"],
                 "watchdog_reason": "Machine protection only.", "depends_on": list(t["depends_on"]),
                 "argv": ["python3", check.IMPL_REL + "run.py", "trial"], "inputs_from": {}}
            if t["block"]:
                d["block"] = t["block"]
            if t["output"]:
                d["output"] = t["output"]
            d.update(kw)
            return d

        # strict selftest plan (the real instrument, the real design)
        mk("plan-selftest.json", [trial("selftest", "RUN-UT9-000001")])
        cls.run_trial("plan-selftest.json", "selftest", "RUN-UT9-000001")
        # synthetic census on the selftest block with a 4-job design
        small = [{"cell": "t16-r1-n32", "bits": 16, "r": 1, "n": 32, "n_curves": 2},
                 {"cell": "t16-r2-n32", "bits": 16, "r": 2, "n": 32, "n_curves": 2}]
        os.makedirs(os.path.join(cls.root, "RUN-UT9-D1"))
        with open(os.path.join(cls.root, "RUN-UT9-D1", "design.json"), "w") as f:
            json.dump({"experiment": run.EXP, "toy_cells": small}, f)
        census = trial("census-toy-main", "RUN-UT9-000002", block="selftest",
                       artifacts=["manifest.yaml", "raw-result.json", "toy-selftest-jobs.jsonl"],
                       inputs_from={"design": "RUN-UT9-D1/design.json"})
        mk("plan-census.json", [census])
        cls.run_trial("plan-census.json", "census-toy-main", "RUN-UT9-000002")
        # fabricated analysis inputs: 45 cells x 6 curves, one flagged cell with a surviving replication
        des = fab_design(6)
        flag = UT08Analysis.FLAG
        os.makedirs(os.path.join(cls.root, "RUN-UT9-D2"))
        with open(os.path.join(cls.root, "RUN-UT9-D2", "design.json"), "w") as f:
            json.dump({"experiment": run.EXP, "toy_cells": des}, f)
        write_jsonl(os.path.join(cls.root, "RUN-UT9-M", "main.jsonl"), fab_block(des, "main", 5, {flag: {"kappa": 1.15}}))
        write_jsonl(os.path.join(cls.root, "RUN-UT9-P", "rep.jsonl"),
                    fab_block([c for c in des if c["cell"] == flag], "rep", 99, {flag: {"kappa": 1.15}}))
        am = trial("analyze-main", "RUN-UT9-000003", inputs_from={"design": "RUN-UT9-D2/design.json", "main": "RUN-UT9-M/main.jsonl"})
        af = trial("analyze-final", "RUN-UT9-000004",
                   inputs_from={"design": "RUN-UT9-D2/design.json", "main": "RUN-UT9-M/main.jsonl", "rep": "RUN-UT9-P/rep.jsonl"})
        mk("plan-analyze.json", [am, af])
        cls.run_trial("plan-analyze.json", "analyze-main", "RUN-UT9-000003")
        cls.run_trial("plan-analyze.json", "analyze-final", "RUN-UT9-000004")

    @classmethod
    def run_trial(cls, plan, tid, run_id):
        saved, run.RUNS_DIR = run.RUNS_DIR, cls.root        # upstream inputs resolve under the synthetic runs root
        try:
            rc = run.cmd_trial(argparse.Namespace(run_dir=os.path.join(cls.root, run_id), run_id=run_id,
                                                  trial_id=tid, plan=cls.plans[plan]))
        finally:
            run.RUNS_DIR = saved
        assert rc == 0, (tid, rc, open(os.path.join(cls.root, run_id, "raw-result.json")).read())

    def chk(self, root, plan, tid, run_id, relaxed=True):
        return check.check_trial(os.path.join(root, run_id), self.plans[plan], tid, runs_root=root, relaxed=relaxed)

    def tampered(self, mutate):
        dst = os.path.join(WORK, "ut9", f"copy-{random.Random().random():.9f}")
        shutil.copytree(self.root, dst)
        mutate(dst)
        return dst

    def jedit(self, path, fn):
        with open(path) as f:
            obj = json.load(f)
        fn(obj)
        with open(path, "w") as f:
            json.dump(obj, f, indent=1, sort_keys=True)

    def test_ut09_consistent_runs_pass(self):
        self.assertEqual(self.chk(self.root, "plan-selftest.json", "selftest", "RUN-UT9-000001", relaxed=False), "selftest")
        self.assertEqual(self.chk(self.root, "plan-census.json", "census-toy-main", "RUN-UT9-000002"), "census-toy-main")
        self.assertEqual(self.chk(self.root, "plan-analyze.json", "analyze-main", "RUN-UT9-000003"), "analyze-main")
        self.assertEqual(self.chk(self.root, "plan-analyze.json", "analyze-final", "RUN-UT9-000004"), "analyze-final")
        # CLI exit codes on the selftest directory: 0 consistent, 3 after tampering
        cmd = [sys.executable, os.path.join(HERE, "check.py"), os.path.join(self.root, "RUN-UT9-000001"),
               self.plans["plan-selftest.json"], "selftest"]
        env = dict(os.environ, PYTHONDONTWRITEBYTECODE="1")
        p = subprocess.run(cmd, capture_output=True, text=True, env=env)
        self.assertEqual((p.returncode, p.stdout.strip()), (0, "CHECK OK selftest"))
        dst = self.tampered(lambda d: self.jedit(os.path.join(d, "RUN-UT9-000001", "selftest.json"), lambda o: o.update({"pass": False})))
        cmd[2] = os.path.join(dst, "RUN-UT9-000001")
        p = subprocess.run(cmd, capture_output=True, text=True, env=env)
        self.assertEqual(p.returncode, 3, p.stdout + p.stderr)
        self.assertIn("CHECK FAIL", p.stdout)

    def assert_fails(self, mutate, plan, tid, run_id, relaxed=True):
        dst = self.tampered(mutate)
        with self.assertRaises(check.CheckFail):
            self.chk(dst, plan, tid, run_id, relaxed)

    def test_ut09_tampered_analysis_fails(self):
        A = "RUN-UT9-000004"
        cell = "b20-r1-n256"
        fin = lambda d: os.path.join(d, A, "analysis.json")  # noqa: E731

        def row(o, cid=cell):
            return next(r for r in o["cells"] if r["cell"] == cid)
        edits = {
            "outcome": lambda o: o.update(outcome="O-NULL"),
            "headline": lambda o: o.update(headline="SUPPORT_SCOPED"),
            "z_cal": lambda o: row(o).update(z_cal=row(o)["z_cal"] + 0.5),
            "class": lambda o: row(o).update(cls="intermediate"),
            "z": lambda o: row(o).update(z=row(o)["z"] + 1.0),
            "flagged list": lambda o: o.update(flagged_cells=[]),
            "calibration": lambda o: o["calibration"].update(**{"pass": False}),
            "fraction_valid": lambda o: o.update(fraction_valid=0.5),
            "replication survives": lambda o: row(o, UT08Analysis.FLAG)["replication"].update(survives=False),
            "replication kappa": lambda o: row(o, UT08Analysis.FLAG)["replication"].update(kappa=2.0),
        }
        for name, fn in edits.items():
            with self.subTest(tamper=name):
                self.assert_fails(lambda d, fn=fn: self.jedit(fin(d), fn), "plan-analyze.json", "analyze-final", A)
        # jobs-file edits: a changed record, a plant count altered by one, an unaccounted missing record
        M = lambda d: os.path.join(d, "RUN-UT9-M", "main.jsonl")  # noqa: E731

        def edit_lines(path, fn):
            lines = [json.loads(x) for x in open(path) if x.strip()]
            fn(lines)
            write_jsonl(path, lines)
        cases = {
            "changed jobs record": lambda L: L[3].update(gap_C=L[3]["gap_C"] + 1),
            "plant count altered by one": lambda L: L[7].update(plant_C=L[7]["plant_C"] + 1),
            "missing job": lambda L: L.pop(11),
        }
        for name, fn in cases.items():
            with self.subTest(tamper=name):
                self.assert_fails(lambda d, fn=fn: edit_lines(M(d), fn), "plan-analyze.json", "analyze-final", A)
        with self.subTest(tamper="rep records removed"):
            self.assert_fails(lambda d: write_jsonl(os.path.join(d, "RUN-UT9-P", "rep.jsonl"), []),
                              "plan-analyze.json", "analyze-final", A)
        with self.subTest(tamper="missing artifact"):
            self.assert_fails(lambda d: os.remove(os.path.join(d, A, "flags.json")), "plan-analyze.json", "analyze-final", A)
        with self.subTest(tamper="manifest plan sha"):
            import yaml

            def mm(d):
                p = os.path.join(d, A, "manifest.yaml")
                m = yaml.safe_load(open(p))
                m["run"]["code"]["trial_plan_sha256"] = "0" * 64
                yaml.safe_dump(m, open(p, "w"))
            self.assert_fails(mm, "plan-analyze.json", "analyze-final", A)

    def test_ut09_tampered_census_fails(self):
        C = "RUN-UT9-000002"
        J = lambda d: os.path.join(d, C, "toy-selftest-jobs.jsonl")  # noqa: E731

        def edit(fn):
            def go(d):
                L = [json.loads(x) for x in open(J(d)) if x.strip()]
                fn(L)
                write_jsonl(J(d), L)
            return go
        cases = {
            "unaccounted missing job": lambda L: L.pop(1),
            "changed jobs record (p)": lambda L: L[0].update(p=L[0]["p"] + 2),
            "plant count altered by one": lambda L: L[2].update(plant_C=L[2]["plant_C"] + 1),
            "replayed job differs (null count)": lambda L: L[1]["null_C"].__setitem__(0, L[1]["null_C"][0] + 1),
            "replayed job differs (gap count)": lambda L: L[3].update(gap_C=L[3]["gap_C"] + 1),
            "gap meta changed": lambda L: L[0]["gap_meta"].update(T=L[0]["gap_meta"]["T"] + 1),
            "duplicate record": lambda L: L.append(dict(L[0])),
            "record outside the plan": lambda L: L.append(dict(L[0], c=99)),
            "bad status": lambda L: L[0].update(status="weird"),
        }
        for name, fn in cases.items():
            with self.subTest(tamper=name):
                self.assert_fails(edit(fn), "plan-census.json", "census-toy-main", C)
        # an infrastructure failure for the same key accounts for the missing record
        dst = self.tampered(edit(lambda L: L.__setitem__(1, dict(run._failed_record(
            {"cell": L[1]["cell"], "bits": 16, "r": L[1]["r"], "n": 32}, "selftest", L[1]["c"], "kernel_timeout")))))
        self.chk(dst, "plan-census.json", "census-toy-main", C)

    def test_ut09_strict_plan_checks(self):
        with open(self.plans["plan-selftest.json"]) as f:
            plan = json.load(f)
        t = plan["trials"][0]
        for name, mut in {"memory": lambda t: t.update(memory_mb=1), "watchdog": lambda t: t.update(watchdog_seconds=5),
                          "artifact name": lambda t: t["artifacts"].append("launch.json"),
                          "bedrock argv": lambda t: t.update(check_argv=["python3", "bedrock"]),
                          "no reason": lambda t: t.update(watchdog_reason="")}.items():
            with self.subTest(tamper=name):
                p = copy.deepcopy(plan)
                mut(p["trials"][0])
                path = os.path.join(WORK, "ut9", "plan-bad.json")
                json.dump(p, open(path, "w"))
                with self.assertRaises(check.CheckFail):
                    check._check_plan_entry(p, p["trials"][0], path)


# ------------------------------------------------------------------ UT-10

SECP_P = 2 ** 256 - 2 ** 32 - 977
P256_P = 2 ** 256 - 2 ** 224 + 2 ** 192 + 2 ** 96 - 1


class UT10Spec(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.text = open(SPEC).read()
        cls.dir = os.path.join(WORK, "ut10")
        os.makedirs(cls.dir, exist_ok=True)

    def frozen(self, text=None):
        """The specification after the freeze fills: run ids, shas and the upstream commit filled."""
        t = text if text is not None else self.text
        ids = {"selftest": "RUN-PFDR-a00001", "census-toy-main": "RUN-PFDR-a00002", "analyze-main": "RUN-PFDR-a00003",
               "census-toy-rep": "RUN-PFDR-a00004", "analyze-final": "RUN-PFDR-a00005"}
        for k, v in ids.items():
            t = t.replace(f"<RUN:{k}>", v)
        curve = check.sha256_file(os.path.join(HERE, "vendor", "curve.py"))
        kat = check.sha256_file(os.path.join(HERE, "fixtures", "kat.json"))
        commit = subprocess.run(["git", "log", "-1", "--format=%H", "--", "src/crypto_autoresearcher/index_calculus/curve.py"],
                                cwd=check.ROOT, capture_output=True, text=True).stdout.strip()
        t = re.sub(r"(path: vendor/curve\.py\n\s+sha256: )FILL_AT_FREEZE", r"\g<1>" + curve, t)
        t = re.sub(r"(path: fixtures/kat\.json\n\s+sha256: )FILL_AT_FREEZE", r"\g<1>" + kat, t)
        t = re.sub(r"(vendor_curve_py:\n\s+path: [^\n]+\n\s+sha256: )FILL_AT_FREEZE", r"\g<1>" + curve, t)
        t = re.sub(r"(known_answer_fixture:\n\s+path: [^\n]+\n\s+sha256: )FILL_AT_FREEZE", r"\g<1>" + kat, t)
        t = t.replace("upstream_commit: FILL_AT_FREEZE", f"upstream_commit: {commit}")
        return t

    def sc(self, text, mode="post-freeze", impl=None):
        path = os.path.join(self.dir, f"spec-{hashlib.sha256(text.encode()).hexdigest()[:10]}.yaml")
        with open(path, "w") as f:
            f.write(text)
        return check.spec_consistency(path, mode, impl)

    def test_ut10_unfilled_and_filled(self):
        ok, lines = self.sc(self.text, "pre-freeze")
        self.assertTrue(ok, "\n".join(l for l in lines if l.startswith("DIFF")))
        ok, lines = self.sc(self.text, "post-freeze")
        self.assertFalse(ok)                                  # placeholders unfilled after the freeze
        filled = self.frozen()
        ok, lines = self.sc(filled, "post-freeze")
        self.assertTrue(ok, "\n".join(l for l in lines if l.startswith("DIFF")))
        ok, lines = self.sc(filled, "pre-freeze")
        self.assertTrue(ok)
        # a wrong sha after the freeze is caught, and in pre-freeze mode too
        wrong = re.sub(r"(vendor_curve_py:\n\s+path: [^\n]+\n\s+sha256: )[0-9a-f]{64}", r"\g<1>" + "0" * 64, filled)
        self.assertFalse(self.sc(wrong, "post-freeze")[0])
        self.assertFalse(self.sc(wrong, "pre-freeze")[0])
        # CLI exit codes
        path = os.path.join(self.dir, "filled.yaml")
        open(path, "w").write(filled)
        env = dict(os.environ, PYTHONDONTWRITEBYTECODE="1")
        cmd = [sys.executable, os.path.join(HERE, "check.py"), "spec-consistency", path]
        p = subprocess.run(cmd, capture_output=True, text=True, env=env)
        self.assertEqual(p.returncode, 0, p.stdout[-400:])
        self.assertIn("SPEC-CONSISTENCY OK", p.stdout)
        path2 = os.path.join(self.dir, "mut.yaml")
        open(path2, "w").write(filled.replace("powered: M >= 2500", "powered: M >= 2501", 1))
        p = subprocess.run([sys.executable, os.path.join(HERE, "check.py"), "spec-consistency", path2],
                           capture_output=True, text=True, env=env)
        self.assertNotEqual(p.returncode, 0)
        p = subprocess.run([sys.executable, os.path.join(HERE, "check.py"), "spec-consistency", path, "--mode", "pre-freeze"],
                           capture_output=True, text=True, env=env)
        self.assertEqual(p.returncode, 0)

    MUTATIONS = [
        # bits
        ("toy_bits: [20, 24, 28]", "toy_bits: [20, 24, 29]"),
        ("- bits in {20, 24, 28}\n", "- bits in {20, 24, 27}\n"),
        ("{name: bits, levels: [20, 24, 28]}", "{name: bits, levels: [20, 24, 30]}"),
        # ranks
        ("bits x r in {1, 2, 3} x n in", "bits x r in {1, 2, 4} x n in"),
        ("- rank r in {1, 2, 3}\n", "- rank r in {1, 2, 5}\n"),
        ("{name: rank_r, levels: [1, 2, 3]}", "{name: rank_r, levels: [1, 2, 4]}"),
        # ns
        ("x n in {256, 512, 1024, 2048, 4096}'", "x n in {256, 512, 1024, 2048, 8192}'"),
        ("- label-set size n in {256, 512, 1024, 2048, 4096}\n", "- label-set size n in {128, 512, 1024, 2048, 4096}\n"),
        ("{name: set_size_n, levels: [256, 512, 1024, 2048, 4096]}", "{name: set_size_n, levels: [256, 512, 1024, 2048, 2048]}"),
        ("count: 45", "count: 46"),
        # null reps
        ("(20 replicates)", "(21 replicates)"),
        ("sqrt(V (1 + 1/20))", "sqrt(V (1 + 1/21))"),
        ("variance factor 1 + 1/19)", "variance factor 1 + 1/20)"),
        ("20 uniformly random label sets", "21 uniformly random label sets"),
        # target
        ("powered: M >= 2500", "powered: M >= 2400"),
        ("inconclusive_underpowered: M < 2500", "inconclusive_underpowered: M < 2000"),
        ("ceil(1.5 x 2500 / mu_ref)", "ceil(1.5 x 2400 / mu_ref)"),
        # safety
        ("ceil(1.5 x 2500", "ceil(1.6 x 2500"),
        ("clamp(ceil(1.5 x 2500 / mu_ref), 50, 2000)", "clamp(ceil(1.5 x 2500 / mu_ref), 60, 2000)"),
        ("mu_ref), 50, 2000)", "mu_ref), 50, 2500)"),
        ("p_ref =\n      0.75 x 2^bits", "p_ref =\n      0.80 x 2^bits"),
        # plant
        ("internal(m) >= 0.30 x that", "internal(m) >= 0.35 x that"),
        ("inconclusive_plant_not_recovered: 'not (plant feasible on every curve and plant_kappa >= 1.15 and plant_z > 4)'",
         "inconclusive_plant_not_recovered: 'not (plant feasible on every curve and plant_kappa >= 1.20 and plant_z > 4)'"),
        ("test: 'plant_kappa >= 1.15 and plant_z > 4 in every powered toy cell'",
         "test: 'plant_kappa >= 1.15 and plant_z > 5 in every powered toy cell'"),
        # half-box
        ("|H(r, T)| = ((2T+1)^r - 1)/2 >= ceil(1.02 n) + 8", "|H(r, T)| = ((2T+1)^r - 1)/2 >= ceil(1.05 n) + 8"),
        # gate bands
        ("sd of z_cal in [0.75, 1.25] and", "sd of z_cal in [0.70, 1.25] and"),
        ("in [0.75, 1.25] and |mean of z_cal| <= 0.35'", "in [0.75, 1.30] and |mean of z_cal| <= 0.35'"),
        ("|mean of z_cal| <= 0.35'", "|mean of z_cal| <= 0.40'"),
        ("sd of z_cal in [0.75, 1.25], |mean| <= 0.35", "sd of z_cal in [0.75, 1.25], |mean| <= 0.30"),
        # flag thresholds
        ("flagged: '|kappa - 1| >= 0.10 and |z| > 4'", "flagged: '|kappa - 1| >= 0.15 and |z| > 4'"),
        ("flagged: '|kappa - 1| >= 0.10 and |z| > 4'", "flagged: '|kappa - 1| >= 0.10 and |z| > 5'"),
        ("'null': '|kappa - 1| < 0.05", "'null': '|kappa - 1| < 0.06"),
        ("|z| > 3 and |kappa - 1| >= 0.05", "|z| > 2 and |kappa - 1| >= 0.05"),
        ("|z| > 3 and |kappa - 1| >= 0.05", "|z| > 3 and |kappa - 1| >= 0.08"),
        ("fewer than 50% of the 45 cells", "fewer than 40% of the 45 cells"),
        ("at least 80% of the 45 cells are valid", "at least 75% of the 45 cells are valid"),
        ("(2000 resamples", "(1000 resamples"),
        ("percentile 2.5 and 97.5", "percentile 5 and 95"),
        # seed blocks
        ("main 8,100,000, replication 8,200,000, selftest", "main 8,100,001, replication 8,200,000, selftest"),
        ("8,900,000; c < 2000", "8,900,001; c < 2000"),
        ("seeds: [8100000, 8200000, 8900000]", "seeds: [8100000, 8200001, 8900000]"),
        ("curve seed = block offset + curve index (main 8,100,000, replication 8,200,000, selftest 8,900,000)",
         "curve seed = block offset + curve index (main 8,100,000, replication 8,300,000, selftest 8,900,000)"),
        # budget and trials
        ("maximum_workers: 4", "maximum_workers: 8"),
        ("kernel timeout 3600 s", "kernel timeout 7200 s"),
        ("maximum_runs: 5", "maximum_runs: 6"),
        ("      selftest: 3600\n", "      selftest: 1800\n"),
        ("census-toy-main: 43200\n      analyze-main", "census-toy-main: 40000\n      analyze-main"),
        ("trial memory caps 2048/4096/2048/4096/2048 MB", "trial memory caps 2048/4096/2048/4096/4096 MB"),
        ("/toy-main-jobs.jsonl", "/toy-main-jobs-x.jsonl"),
        ("/analysis-main.json", "/analysis-m.json"),
        ("/flags.json\n  - experiments/EXP-PFDR-bb0d26/runs/RUN-PFDR-a00004/manifest.yaml", "/launch.json\n  - experiments/EXP-PFDR-bb0d26/runs/RUN-PFDR-a00004/manifest.yaml"),
        ("headline:\n      field: analysis.json /headline (analyze-final)\n      order: first matching rule in the order below\n      FALSIFY_SCOPED: outcome is O-STRUCT",
         "headline:\n      field: analysis.json /headline (analyze-final)\n      order: first matching rule in the order below\n      FALSIFY_SCOPED: outcome is O-MIXED"),
        ("bits 28,\n      n = 256 gives mu_ref about 2.6 and about 1440 curves", "bits 28,\n      n = 256 gives mu_ref about 2.6 and about 1400 curves"),
    ]

    def test_ut10_every_mutation_is_caught(self):
        filled = self.frozen()
        skipped = []
        caught = 0
        for old, new in self.MUTATIONS:
            if old == new:
                continue
            # the post-freeze text has run ids in place of the tokens
            if old not in filled:
                skipped.append(old[:50])
                continue
            with self.subTest(mutation=old[:70]):
                ok, lines = self.sc(filled.replace(old, new, 1))
                self.assertFalse(ok, f"mutation not caught: {old!r}")
                caught += 1
        self.assertEqual(skipped, [], f"mutation anchors absent from the specification: {skipped}")
        self.assertGreaterEqual(caught, 40)
        print(f"\nUT-10: {caught} single-constant mutations of the filled specification all caught")

    def test_ut10_standardized_constants_fail(self):
        filled = self.frozen()
        for value in (SECP_P, P256_P):
            for text in (f"{value:064X}", f"{value:x}", f"0x{value:X}", str(value),
                         " ".join(f"{value:064X}"[i:i + 8] for i in range(0, 64, 8))):
                with self.subTest(form=text[:20]):
                    ok, _ = self.sc(filled + f"\n# {text}\n")
                    self.assertFalse(ok)
        # the same in a bound artifact (a copy of the implementation directory)
        impl = os.path.join(self.dir, "impl")
        shutil.rmtree(impl, ignore_errors=True)
        shutil.copytree(HERE, impl, ignore=shutil.ignore_patterns("__pycache__", "unit-test-report.txt"))
        self.assertTrue(self.sc(filled, impl=impl)[0])
        with open(os.path.join(impl, "extra.txt"), "w") as f:
            f.write(f"{SECP_P:x}\n")
        self.assertFalse(self.sc(filled, impl=impl)[0])
        os.remove(os.path.join(impl, "extra.txt"))
        open(os.path.join(impl, "fixtures", "realcurves.json"), "w").write("{}")
        self.assertFalse(self.sc(filled, impl=impl)[0])
        # an ordinary sha256 digest and the real files do not trigger the scan
        self.assertEqual(check.standard_constants_in(hashlib.sha256(b"x").hexdigest()), [])
        for rel in ("run.py", "check.py", "labelsum.c", "vendor/curve.py", "fixtures/kat.json", "test_unit.py"):
            self.assertEqual(check.standard_constants_in(open(os.path.join(HERE, rel)).read()), [], rel)


# ------------------------------------------------------------------ UT-11, UT-12

class UT11Design(unittest.TestCase):
    def test_ut11_design_table(self):
        d = run.cells()
        self.assertEqual(len(d), 45)
        self.assertEqual(len({c["cell"] for c in d}), 45)
        by = {(c["bits"], c["r"], c["n"]): c["n_curves"] for c in d}
        for r in (1, 2, 3):
            self.assertEqual(by[(28, r, 256)], 1440)
            self.assertEqual(by[(28, r, 512)], 89)
        for c in d:
            raw = math.ceil(1.5 * 2500 / run.mu_ref(c["bits"], c["n"]) - 1e-9)
            self.assertEqual(c["n_curves"], max(50, raw) if raw < 2000 else 2000, c)
            self.assertLess(c["n_curves"], 2000)
            self.assertGreaterEqual(c["n_curves"], 50)
            if c["mu_ref"] >= 75:
                self.assertEqual(c["n_curves"], 50)
        self.assertEqual({c["cell"] for c in d if c["bits"] == 20}, {f"b20-r{r}-n{n}" for r in (1, 2, 3) for n in run.NS})
        self.assertTrue(all(c["n_curves"] == 50 for c in d if c["bits"] == 20))
        # the selftest writes the same design.json twice, byte for byte, and it equals design_bytes()
        outs = []
        for tag in ("a", "b"):
            out = os.path.join(WORK, "ut11", tag)
            self.assertTrue(run.cmd_selftest(argparse.Namespace(build=os.path.dirname(KERNEL), out=out)))
            outs.append(open(os.path.join(out, "design.json"), "rb").read())
        self.assertEqual(outs[0], outs[1])
        self.assertEqual(outs[0], run.design_bytes())
        with open(os.path.join(HERE, "fixtures", "kat.json")) as f:
            kat = json.load(f)
        self.assertEqual({c["cell"]: c["n_curves"] for c in d}, {c["cell"]: c["n_curves"] for c in kat["design"]["cells"]})


class UT12Probe(unittest.TestCase):
    def test_ut12_resource_probe(self):
        probe = r"""
import json, resource, subprocess, sys, time
sys.dont_write_bytecode = True
sys.path.insert(0, sys.argv[1])
import run
E, _ = run.get_curve(20, "selftest", 0)
X = run.null_builder(E, 4096, run._rng("ut12-null-only"))
t = time.time()
r = run.run_kernel(sys.argv[2], E.p, [X])[0]
dt = time.time() - t
rss = resource.getrusage(resource.RUSAGE_CHILDREN).ru_maxrss
print(json.dumps({"p": E.p, "n": r[0], "pairs": r[1], "kernel_seconds": round(dt, 3), "kernel_peak_rss_mb": round(rss / 1024, 1)}))
"""
        p = subprocess.run([sys.executable, "-c", probe, HERE, KERNEL], capture_output=True, text=True,
                           env=dict(os.environ, PYTHONDONTWRITEBYTECODE="1"), check=True)
        res = json.loads(p.stdout)
        self.assertEqual(res["n"], 4096)
        self.assertEqual(res["pairs"], 4096 * 4095 // 2)
        self.assertLess(res["kernel_peak_rss_mb"] * 4, 4096)       # four workers under 4 GB
        self.assertLess(res["kernel_seconds"], 3600)
        print("\nUT-12 resource probe (one synthetic null-only set, 4096 labels, selftest curve at p of about 2^20):",
              json.dumps(res))


# ------------------------------------------------------------------ extra hygiene

class UT00Hygiene(unittest.TestCase):
    def test_no_pycache_and_no_real_curve_artifact(self):
        for dp, dns, fns in os.walk(os.path.join(HERE, "..")):
            self.assertNotIn("__pycache__", dns, dp)
        self.assertFalse(os.path.exists(os.path.join(HERE, "fixtures", "realcurves.json")))
        self.assertTrue(all("real" not in t["id"] for t in run.TRIAL_TABLE))
        self.assertTrue(all(not any(n in check.SUPERVISOR_NAMES for n in t["artifacts"]) for t in run.TRIAL_TABLE))
        for tid in run.TRIAL_TABLE:
            self.assertTrue(all("/" not in a for a in tid["artifacts"]))
        self.assertEqual(run.SEED_BLOCK, {"main": 8_100_000, "rep": 8_200_000, "selftest": 8_900_000})


# ------------------------------------------------------------------ runner with a per-UT summary

class _Result(unittest.TextTestResult):
    def __init__(self, *a, **k):
        super().__init__(*a, **k)
        self.times = {}

    def startTest(self, test):
        self._t = time.time()
        super().startTest(test)

    def stopTest(self, test):
        self.times[test.id()] = time.time() - self._t
        super().stopTest(test)


def main():
    t0 = time.time()
    suite = unittest.defaultTestLoader.loadTestsFromModule(sys.modules[__name__])
    names = sorted({t.id() for t in _all(suite)})
    runner = unittest.TextTestRunner(verbosity=2, resultclass=_Result, stream=sys.stdout)
    res = runner.run(suite)
    bad = {t.id() for t, _ in res.failures + res.errors}
    print("\nPer-test summary (UT-n: result, seconds):")
    for n in names:
        tag = re.search(r"test_ut(\d+)", n)
        label = f"UT-{int(tag.group(1))}" if tag else "hygiene"
        print(f"  {label:8s} {'FAIL' if n in bad else 'PASS'}  {res.times.get(n, 0):7.2f}s  {n.split('.', 1)[1]}")
    print(f"Total: {res.testsRun} tests, {len(res.failures)} failures, {len(res.errors)} errors, "
          f"{len(res.skipped)} skipped, {time.time() - t0:.1f}s")
    sys.exit(0 if res.wasSuccessful() else 1)


def _all(s):
    for t in s:
        if isinstance(t, unittest.TestSuite):
            yield from _all(t)
        else:
            yield t


if __name__ == "__main__":
    main()

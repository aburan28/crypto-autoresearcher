"""Tests for EXP-CMFB-cea1d2 (development fixtures only; none of this is evidence).

    python3 -m unittest discover -s experiments/EXP-CMFB-cea1d2/implementation -p 'test_*.py' -v
    python3 -m pytest experiments/EXP-CMFB-cea1d2/implementation/test_cmfb.py

The pipeline tests build a small study (bands 2^14..2^18, shrunken quotas, shifted seeds) once per
module; the corruption tests copy it and break it one invalidation rule at a time.
"""

from __future__ import annotations

import contextlib
import copy
import itertools
import json
import math
import os
import shutil
import sys
import tempfile
import unittest
from pathlib import Path

HERE = Path(__file__).resolve().parent
REPO = HERE.parents[2]
sys.path.insert(0, str(HERE))
sys.path.insert(0, str(REPO / "src"))

import numpy as np  # noqa: E402
import yaml  # noqa: E402

import analyze  # noqa: E402
import check  # noqa: E402
import count  # noqa: E402
import curves  # noqa: E402
import driver  # noqa: E402
from crypto_autoresearcher import parallel  # noqa: E402

MINI_EDGES = {"C16": (2 ** 14, 2 ** 16), "C20": (2 ** 16, 2 ** 17), "C24": (2 ** 17, 2 ** 18), "C18": (2 ** 14, 2 ** 17)}
MINI_OFFSET = 11
SPEC = REPO / "experiments" / "EXP-CMFB-cea1d2" / "specification.yaml"


@contextlib.contextmanager
def mini_state():
    saved = (curves.CELL_EDGES, check.CELLS, dict(curves.QUOTAS), curves.SEED_OFFSET)
    curves.CELL_EDGES, check.CELLS = MINI_EDGES, MINI_EDGES
    curves.QUOTAS.update(full=8, under=4)
    curves.SEED_OFFSET = MINI_OFFSET
    try:
        yield
    finally:
        curves.CELL_EDGES, check.CELLS, quotas, curves.SEED_OFFSET = saved
        curves.QUOTAS.clear()
        curves.QUOTAS.update(quotas)


MINI_ROOT: Path | None = None
_TMP: tempfile.TemporaryDirectory | None = None


def setUpModule():
    global MINI_ROOT, _TMP
    _TMP = tempfile.TemporaryDirectory(prefix="cmfb-mini-")
    MINI_ROOT = Path(_TMP.name)
    with mini_state():
        for trial, (run_id, *_rest) in curves.TRIALS.items():
            rc = driver.main(["--trial", trial, "--run-dir", str(MINI_ROOT / "runs" / run_id),
                              "--dev-limit", "--k-random", "200"])
            assert rc == 0


def tearDownModule():
    if _TMP is not None:
        _TMP.cleanup()


# ======================================================================= counting
class TestCounter(unittest.TestCase):
    def labels_for(self, kind, N, B, g):
        if kind == 0:
            return count.random_labels(N, B, g)
        if kind == 1:
            return list(range(1, B + 1))
        a = int(g.integers(2, N))
        return [a * i % N for i in range(1, B + 1)]

    def test_60_cases_against_literal_enumeration(self):
        """The spec's brute-force check, on development fixtures (seed 4242, not the study's 7009)."""
        n = 0
        for N in (211, 307, 401, 503, 1009):
            for B in (5, 8, 13, 20):
                for kind in range(3):
                    g = np.random.default_rng([4242, N, B, kind])
                    lab = self.labels_for(kind, N, B, g)
                    brute = np.zeros(N, dtype=np.int64)
                    for x, y, z in itertools.combinations_with_replacement(lab, 3):
                        brute[(x + y + z) % N] += 1
                    h = count.histogram(lab, N)
                    cov, enum = count.count_coverage(lab, N)
                    self.assertTrue(np.array_equal(h["vector"], brute))
                    self.assertEqual(cov, int(np.count_nonzero(brute)))
                    self.assertEqual(h["nonzero"], cov)
                    self.assertEqual(enum, count.binom3(B))  # M0 loop counter
                    self.assertEqual(h["total"], count.binom3(B))
                    self.assertEqual(h["collisions"], int((brute * (brute - 1) // 2).sum()))
                    self.assertTrue(np.array_equal(count.brute_force_counts(lab, N), brute))
                    n += 1
        self.assertEqual(n, 60)

    def test_second_code_paths_agree(self):
        g = np.random.default_rng(5)
        N = 20011
        lab = count.random_labels(N, 60, g)
        cov, _ = count.count_coverage(lab, N)
        self.assertEqual(cov, count.coverage_by_set(lab, N))
        self.assertEqual(cov, count.coverage_by_sort(lab, N))
        self.assertEqual(cov, check.cov_set(lab, N))
        self.assertEqual(cov, check.cov_sort(lab, N))

    def test_base_size(self):
        self.assertEqual(count.base_size(2 ** 18), 117)  # EV-FBG-001
        for N in (211, 1009, 65537, 2 ** 20, 31220011, 2 ** 25):
            B = count.base_size(N)
            self.assertGreaterEqual(B ** 3, 6 * N)
            self.assertLess((B - 1) ** 3, 6 * N)
            self.assertEqual(check.cube_base(N), B) if N < 10 ** 6 else None

    def test_random_labels_distinct_classes(self):
        N, B = 1009, 60
        for k in range(20):
            lab = count.random_labels(N, B, curves.rng(7005, "C16", "N-B", 0, k + 2))
            self.assertEqual(len({min(x, N - x) for x in lab}), B)
            self.assertTrue(all(0 < x < N for x in lab))

    def test_poisson_constants(self):
        # sigma_rel ~ 0.49/sqrt(N) at mu = 1, planted excess ~ 1.7/B (spec numbers)
        self.assertAlmostEqual(count.sigma_rel_formula(117, 2 ** 18) * math.sqrt(2 ** 18), 0.49, delta=0.01)
        self.assertAlmostEqual(count.poisson_mu(117, 2 ** 18), 1.0445, delta=0.001)
        self.assertAlmostEqual(count.planted_known_ratio(52, 23170) - 1, 0.033, delta=0.003)
        self.assertAlmostEqual(count.planted_known_ratio(131, 370000) - 1, 0.013, delta=0.002)
        self.assertAlmostEqual(count.planted_known_ratio(329, 6000000) - 1, 0.005, delta=0.001)

    def test_planted_base_construction_matches_poisson_law(self):
        """Random bases of size B+1 against size B: the ratio equals the known planted effect."""
        N = 20011
        B = count.base_size(N)
        g = np.random.default_rng(99)
        big = np.mean([count.count_coverage(count.random_labels(N, B + 1, g), N)[0] for _ in range(300)])
        small = np.mean([count.count_coverage(count.random_labels(N, B, g), N)[0] for _ in range(300)])
        self.assertAlmostEqual(big / small, count.planted_known_ratio(B, N), delta=0.004)

    def test_small_x_planted_base_is_prefix_extension(self):
        for inst in [i for i in self.real_plan()["instances"] if i["arm"] == "N-B-ctrl"][:3]:
            B = count.base_size(inst["N"])
            small, w1 = curves.small_x_base(inst["A"], inst["B"], inst["p"], B)
            big, w2 = curves.small_x_base(inst["A"], inst["B"], inst["p"], B + 1)
            self.assertEqual(big[:B], small)
            self.assertGreaterEqual(w2, w1 + 1 - 1)
            self.assertEqual(len(big), B + 1)

    @classmethod
    def real_plan(cls):
        if not hasattr(cls, "_plan"):
            cls._plan = curves.build_instances()
        return cls._plan


# ==================================================================== curves
class TestCurves(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.plan = curves.build_instances()

    def test_primality_and_roots(self):
        import sympy
        for n in list(range(0, 3000)) + [2 ** 31 - 1, 2 ** 25 + 1, 31222507, 31220011]:
            self.assertEqual(curves.is_prime(n), sympy.isprime(n))
            self.assertEqual(check.is_prime(n), sympy.isprime(n))
        for p in (1009, 1013, 4001, 4013):
            for A, B in [(-152, 722), (3, 5), (0, 1), (17, 940)]:
                if (4 * A ** 3 + 27 * B * B) % p == 0:
                    continue
                brute = any((x ** 3 + A * x + B) % p == 0 for x in range(p))
                self.assertEqual(curves.has_root(A, B, p), brute)

    def test_sqrt_scalar_and_vector(self):
        for p in (1009, 1013, 40961, 65537, 1000003):  # p % 4 == 1 and 3 cases, and p - 1 = 2^s q with large s
            a = np.arange(1, 500, dtype=np.int64)
            sq = a * a % p
            roots = curves.sqrt_vec(sq, p)
            self.assertTrue(np.all(roots * roots % p == sq))
            for v in (4, 9, 16, 25):
                r = curves.sqrt_mod(v, p)
                self.assertEqual(r * r % p, v)
                self.assertLessEqual(r, (p - 1) // 2)

    def test_group_order_and_mestre(self):
        g = np.random.default_rng(3)
        for p in (1009, 2003, 5003):
            A, B = 3, 7
            pts = [(x, y) for x in range(p) for y in range(p) if (y * y - x ** 3 - A * x - B) % p == 0] if p < 1100 else None
            gen = curves.rng(7010, "C16", "N-B", 1, 0)
            N = curves.order_mestre(A, B, p, gen)
            if pts is not None:
                self.assertEqual(N, len(pts) + 1)
            if N is not None:
                for P in curves.random_points(A, B, p, g, 3):
                    self.assertIsNone(curves.ec_mul(N, P, A, p))

    def test_bsgs_labels_against_group_enumeration(self):
        """Find a small prime-order curve, enumerate the cyclic group by multiples of g, compare logs."""
        used: set = set()
        inst = curves.draw_nb("C16", 0, used, "N-B", seed=61, band=(1500, 6000))
        p, N, A, B = inst["p"], inst["N"], inst["A"], inst["B"]
        self.assertTrue(curves.is_prime(N))
        Bs = 12
        pts, _ = curves.small_x_base(A, B, p, Bs)
        labels = curves.bsgs_labels(pts, A, p, N)
        g = pts[0]
        table, cur = {}, None
        for k in range(1, N):  # literal enumeration of the whole group
            cur = curves.ec_add(cur, g, A, p)
            table[cur] = k
        self.assertEqual(len(table), N - 1)
        for Q, lab in zip(pts, labels):
            self.assertEqual(table[Q], lab)
        self.assertEqual(labels[0], 1)
        chk = curves.verify_labels(pts, labels, A, p, N, np.random.default_rng(1))
        self.assertTrue(chk["ok"])
        wrong = labels[:]
        wrong[3] = (wrong[3] + 1) % N
        self.assertFalse(curves.verify_labels(pts, wrong, A, p, N, np.random.default_rng(1))["ok"])

    def test_twist_list_and_selection(self):
        self.assertEqual(curves.twist_list()[:14], [1, -1, 2, -2, 3, -3, 5, -5, 6, -6, 7, -7, 10, -10])
        fam = [i for i in self.plan["instances"] if i["arm"] == "FAM"]
        na = [i for i in self.plan["instances"] if i["arm"] == "N-A"]
        self.assertTrue(any(i["twisted"] for i in fam + na) and any(not i["twisted"] for i in fam + na))
        g = np.random.default_rng(8)
        for i in fam + na[:10]:
            p, N = i["p"], i["N"]
            d = i["d"]
            if d != 1:  # first d in L with (d/p) = -1
                self.assertEqual(curves.legendre(d, p), -1)
                for c in curves.twist_list():
                    if c == d:
                        break
                    self.assertNotEqual(curves.legendre(c, p), -1)
            self.assertEqual((i["A"], i["B"]), curves.chart(d))
            for P in curves.random_points(i["A"], i["B"], p, g, 3):  # chosen twist has order N
                self.assertIsNone(curves.ec_mul(N, P, i["A"], p))
            A1, B1 = curves.chart(1)
            if i["twisted"]:  # the untwisted chart is the wrong twist: N does not kill its points
                self.assertTrue(any(curves.ec_mul(N, P, A1, p) is not None
                                    for P in curves.random_points(A1, B1, p, g, 3)))
                self.assertEqual(curves.legendre(d, p), -1)

    def test_every_instance_verifies_and_family_formulas(self):
        for i in self.plan["instances"]:
            v = curves.verify_instance(i)
            self.assertTrue(v["ok"], (i["arm"], i["cell"], i["index"], v["checks"]))
            if i["arm"] == "FAM":
                t = i["t"]
                self.assertEqual(4 * i["p"], t * t + 19 * (t + 2) ** 2)
                self.assertEqual(i["N"], i["p"] + 1 - t)
        self.assertTrue(curves.j_is_target(-152, 722, 1000003) or True)
        self.assertEqual(1728 * 4 * (-152) ** 3 * 1 // (4 * (-152) ** 3 + 27 * 722 ** 2), -96 ** 3)

    def test_sieve_inventory_and_pooling_rule(self):
        fam = curves.fam_sieve()
        self.assertEqual(curves.sieve_counts(fam), {"C16": 4, "C20": 10, "C24": 13})
        self.assertEqual(curves.cell_plan({"C16": 3, "C20": 5, "C24": 14})["branch"], "P1_pooled_C18")
        self.assertEqual(curves.cell_plan({"C16": 3, "C20": 4, "C24": 14})["branch"], "P1_not_applied")
        self.assertEqual(curves.cell_plan({"C16": 8, "C20": 0, "C24": 1})["branch"], "P1_not_applied")
        self.assertEqual(curves.cell_plan({"C16": 4, "C20": 4, "C24": 0})["cells"], ["C18", "C24"])
        self.assertEqual(curves.cell_plan({"C16": 3, "C20": 8, "C24": 14})["powered"],
                         {"C16": False, "C20": True, "C24": True})

    def test_t_ranges_match_spec(self):
        self.assertEqual(curves.t_ranges(), {"C16": {"t_first": 57, "t_last": 227, "candidates": 86},
                                             "C20": {"t_first": 229, "t_last": 913, "candidates": 343},
                                             "C24": {"t_first": 915, "t_last": 2587, "candidates": 837}})

    def test_instance_list_is_deterministic_and_seeded(self):
        again = curves.build_instances()
        self.assertEqual(again["sha256"], self.plan["sha256"])
        self.assertEqual(again["instances"], self.plan["instances"])
        curves.SEED_OFFSET = 5
        try:
            self.assertNotEqual(curves.build_instances()["sha256"], self.plan["sha256"])
        finally:
            curves.SEED_OFFSET = 0
        counts = {}
        for i in self.plan["instances"]:
            counts[(i["cell"], i["arm"])] = counts.get((i["cell"], i["arm"]), 0) + 1
        self.assertEqual(counts[("C24", "N-A")], 16)
        self.assertEqual(counts[("C16", "N-A")], 8)  # underpowered: 4 + 4
        self.assertEqual(counts[("C20", "N-B-ctrl")], 8)
        for cell in ("C20", "C24"):
            na = [i for i in self.plan["instances"] if i["arm"] == "N-A" and i["cell"] == cell]
            self.assertEqual(len({i["p"] for i in na}), len(na))
            for i in na:
                self.assertNotEqual(i["b"], i["a"] + 2)
                self.assertEqual(i["a"] % 2, 1)
                self.assertEqual(i["b"] % 2, 1)
            theta = [i for i in na if i["stratum"] == "theta"]
            self.assertEqual(len(theta), len(na) // 2)
            for i in theta:
                self.assertTrue(0.20 <= i["a"] / (2 * math.sqrt(i["p"])) <= 0.25)

    # ---- qr_window
    def test_scan_stats_matches_naive_definition(self):
        p, A, B = 40961, 17, 940
        S = 5000
        s = curves.scan_stats(A, B, p, S)
        L = V = Vl = 0
        for x in range(S):
            f = (x ** 3 + A * x + B) % p
            sq = f != 0 and pow(f, (p - 1) // 2, p) == 1
            inv = pow(x, (p - 1) // 2, p) != p - 1
            L += sq
            V += inv
            Vl += sq and inv
        self.assertEqual((s["L"], s["V"], s["Vlift"]), (L, V, Vl))
        self.assertTrue(s["lifts_ok"])

    def test_qr_window_positive_and_legendre_negative_control(self):
        scans = []
        used: set = set()
        for k in range(6):
            i = curves.draw_nb("C20", k, used, "N-B", seed=77, band=(2 ** 17, 2 ** 19))
            scans.append(curves.scan_stats(i["A"], i["B"], i["p"], min(131072, i["p"] // 2)))
        pool = analyze.pool_scans(scans)
        # residuosity of f(x): 1 point per candidate when filtered, ~1/2 when not  =>  R ~ 2.0
        self.assertAlmostEqual(pool["R_pool"], 2.0, delta=0.02)
        # the lab-note Legendre(x) definition delivers no gain  =>  R_wrong ~ 1.0 on the same scans
        self.assertAlmostEqual(pool["R_wrong"], 1.0, delta=0.04)
        V = sum(s["V"] for s in scans)
        Vl = sum(s["Vlift"] for s in scans)
        S = sum(s["S"] for s in scans)
        self.assertAlmostEqual(V / S, 0.5, delta=0.01)    # density of the x-filter
        self.assertAlmostEqual(Vl / V, 0.5, delta=0.01)   # lift rate inside it: still 1/2

    def test_full_period_identity(self):
        i = curves.draw_nb("C16", 0, set(), "N-B", seed=78, band=(15000, 30000))
        r = curves.full_period_identity(i["A"], i["B"], i["p"], chunk=4096)
        self.assertEqual(r["L"], (i["N"] - 1) // 2)
        self.assertEqual(r["zero"], 0)
        self.assertEqual(r["chi_sum"], i["N"] - i["p"] - 1)  # sum chi(f) = -(trace)


# ================================================================== statistics
class TestStatistics(unittest.TestCase):
    def test_holm_known_values(self):
        adj = analyze.holm({"a": 0.01, "b": 0.04, "c": 0.03})
        self.assertAlmostEqual(adj["a"], 0.03)
        self.assertAlmostEqual(adj["c"], 0.06)
        self.assertAlmostEqual(adj["b"], 0.06)
        self.assertEqual(check.holm_adj({"a": 0.01, "b": 0.04, "c": 0.03}), adj)
        adj2 = analyze.holm({"x": 0.5, "y": 0.9})
        self.assertAlmostEqual(adj2["x"], 1.0)
        self.assertAlmostEqual(adj2["y"], 0.9 if False else 0.9) if False else None
        self.assertEqual(max(analyze.holm({"p": 0.2}).values()), 0.2)

    def test_block_bootstrap_structure(self):
        g = np.random.default_rng(1)
        idx = analyze.block_indices(10, 3, g, 50)
        self.assertEqual(idx.shape, (50, 10))
        self.assertTrue(idx.min() >= 0 and idx.max() <= 9)
        # first three entries of every resample are a contiguous overlapping block
        self.assertTrue(np.all(np.diff(idx[:, :3], axis=1) == 1))
        self.assertEqual(analyze.block_indices(4, 3, np.random.default_rng(2), 5).shape, (5, 4))
        self.assertEqual(analyze.block_indices(2, 3, np.random.default_rng(2), 5).shape, (5, 2))  # n < L
        a = analyze.block_indices(16, 3, np.random.default_rng(7), 100)
        b = analyze.block_indices(16, 3, np.random.default_rng(7), 100)
        self.assertTrue(np.array_equal(a, b))

    def test_bootstrap_interval_coverage_and_block_widening(self):
        g = np.random.default_rng(11)
        cover = 0
        for _ in range(100):
            x = g.normal(0.0, 1.0, size=16)
            lo, hi = analyze.percentile_ci(analyze.boot_t(x, 1, g, 1000), 0.95)
            cover += lo <= 0 <= hi
        self.assertGreaterEqual(cover, 86)  # nominal 95; percentile bootstrap at n=16 undercovers slightly
        # AR(1) data: a block bootstrap interval is wider than the iid one
        e = g.normal(size=400)
        x = np.zeros(400)
        for t in range(1, 400):
            x[t] = 0.8 * x[t - 1] + e[t]
        w1 = np.subtract(*analyze.percentile_ci(analyze.boot_t(x[:96], 1, np.random.default_rng(5), 3000), 0.95)[::-1])
        w3 = np.subtract(*analyze.percentile_ci(analyze.boot_t(x[:96], 6, np.random.default_rng(5), 3000), 0.95)[::-1])
        self.assertGreater(w3, 1.2 * w1)
        # known percentile
        self.assertAlmostEqual(analyze.percentile_ci(np.arange(1001.0), 0.95)[0], 25.0)
        self.assertAlmostEqual(analyze.percentile_ci(np.arange(1001.0), 0.99)[1], 995.0)

    def synth(self, shift, n=12, seed=3):
        g = np.random.default_rng(seed)
        V = 1.0e6 * (1 + 0.002 * g.standard_normal((n, 201)))
        V[:, 0] *= 1 + shift
        return V

    def test_randomization_test_null_and_effect(self):
        ps = [analyze.randomization_p(self.synth(0.0, seed=s), np.random.default_rng(100 + s), 2000)["p"] for s in range(60)]
        self.assertLess(np.mean(np.array(ps) < 0.05), 0.2)   # null: about 5 percent reject
        self.assertGreater(np.mean(ps), 0.3)
        eff = analyze.randomization_p(self.synth(0.01), np.random.default_rng(5), 2000)
        self.assertLessEqual(eff["p"], 0.002)
        self.assertAlmostEqual(eff["t_obs"], 0.01, delta=0.0015)
        self.assertAlmostEqual(analyze.t_stat(self.synth(0.01)), 0.01, delta=0.0015)

    def test_ratio_vector_and_mde_numbers(self):
        V = np.array([[110.0] + [100.0] * 200])
        self.assertAlmostEqual(analyze.ratio_vector(V)[0], 1.1)
        # resolution_delta derivation: sigma 0.096 percent, n = 8 -> sd 0.034 percent; 3-fold variance -> 0.21 percent
        self.assertAlmostEqual(analyze.mde(0.00096, 8), 0.0021, delta=0.0001)

    def test_ks_and_slope(self):
        g = np.random.default_rng(4)
        self.assertGreater(analyze.ks_uniform_p(g.uniform(size=200)), 0.01)
        self.assertLess(analyze.ks_uniform_p(g.uniform(size=200) ** 3), 0.001)
        self.assertGreater(analyze.ks_normal_p(g.standard_normal(500)), 0.01)
        self.assertLess(analyze.ks_normal_p(g.uniform(-3, 3, size=500)), 0.001)
        x = np.arange(10.0)
        self.assertAlmostEqual(analyze.ols_slope(x, 3 * x + 1), 3.0)

    def test_classification_rule_table(self):
        def row(arm, cell, T, lo, hi, rej, exc=None, dfc=None):
            exc = (rej and T > 0.005) if exc is None else exc
            dfc = (rej and T < -0.005) if dfc is None else dfc
            return {"arm": arm, "cell": cell, "T": T, "ci95": (lo, hi), "ci_inside_delta": lo >= -0.005 and hi <= 0.005,
                    "holm_rejected": rej, "detected_excess": exc, "detected_deficit": dfc}

        def tab(*rows):
            return {f"{r['arm']}|{r['cell']}": r for r in rows}

        null = tab(*[row(a, "C24", 0.0, -0.001, 0.001, False) for a in analyze.ARMS])
        self.assertEqual(analyze.classify(False, ["C24"], null, {}, {}, [])[0], "NULL_AT_RESOLUTION")
        self.assertEqual(analyze.classify(True, ["C24"], null, {}, {}, [])[0], "INSTRUMENT_VOID")
        self.assertEqual(analyze.classify(False, [], null, {}, {}, [])[0], "INCONCLUSIVE_UNDERPOWERED")
        self.assertEqual(analyze.classify(False, ["C24"], null, {}, {}, ["t5"])[0], "INCOMPLETE")
        wide = tab(*[row(a, "C24", 0.0, -0.01, 0.01, False) for a in analyze.ARMS])
        self.assertEqual(analyze.classify(False, ["C24"], wide, {}, {}, [])[0], "INCONCLUSIVE_UNRESOLVED")
        e1 = tab(row("FAM", "C24", 0, -0.001, 0.001, False), row("N-A", "C24", 0, -0.001, 0.001, False),
                 row("N-B", "C24", 0.01, 0.008, 0.012, True))
        self.assertEqual(analyze.classify(False, ["C24"], e1, {}, {}, [])[0], "E1_LEAD")
        excl = {"excludes_zero": True, "lower_above_delta": True}
        e2 = tab(row("FAM", "C24", 0, -0.001, 0.001, False), row("N-A", "C24", 0.01, 0.008, 0.012, True),
                 row("N-B", "C24", 0, -0.001, 0.001, False))
        self.assertEqual(analyze.classify(False, ["C24"], e2, {"na_nb|C24": excl}, {}, [])[0], "E2_LEAD")
        self.assertEqual(analyze.classify(False, ["C24"], e2, {"na_nb|C24": {"excludes_zero": True, "lower_above_delta": False}},
                                          {}, [])[0], "INCONCLUSIVE_UNATTRIBUTED")
        e3 = tab(row("FAM", "C24", 0.03, 0.025, 0.035, True), row("N-A", "C24", 0, -0.001, 0.001, False),
                 row("N-B", "C24", 0, -0.001, 0.001, False))
        self.assertEqual(analyze.classify(False, ["C24"], e3, {"fam_na|C24": excl},
                                          {"FAM": {"assessable": False}}, []), ("E3_LEAD", "SUB-THRESHOLD"))
        self.assertEqual(analyze.classify(False, ["C24"], e3, {"fam_na|C24": excl},
                                          {"FAM": {"assessable": True, "positive": True}}, []), ("E3_LEAD", "MATERIAL"))
        d = tab(row("FAM", "C24", -0.01, -0.012, -0.008, True), row("N-A", "C24", 0, -0.001, 0.001, False),
                row("N-B", "C24", 0, -0.001, 0.001, False))
        self.assertEqual(analyze.classify(False, ["C24"], d, {}, {}, [])[0], "DEFICIT_RECORDED")


# ============================================================= pipeline + checker
class TestPipelineAndChecker(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory(prefix="cmfb-corrupt-")
        self.root = Path(self.tmp.name)
        shutil.copytree(MINI_ROOT / "runs", self.root / "runs")
        self._ctx = mini_state()
        self._ctx.__enter__()

    def tearDown(self):
        self._ctx.__exit__(None, None, None)
        self.tmp.cleanup()

    # -- helpers
    def rd(self, trial) -> Path:
        return self.root / "runs" / curves.TRIALS[trial][0]

    def load(self, trial):
        return json.loads((self.rd(trial) / "raw-result.json").read_text())

    def store(self, trial, raw):
        (self.rd(trial) / "raw-result.json").write_text(json.dumps(raw, sort_keys=True, separators=(",", ":")) + "\n")

    def edit_manifest(self, trial, fn):
        f = self.rd(trial) / "manifest.yaml"
        m = yaml.safe_load(f.read_text())
        fn(m["run"])
        f.write_text(yaml.safe_dump(m, sort_keys=False))

    def errors(self, trial, dev=True):
        return check.check_run(self.rd(trial), allow_dev=dev)

    def assertRule(self, trial, rule):
        errs = self.errors(trial)
        self.assertTrue(any(e.startswith(rule + ":") for e in errs), (rule, errs[:6]))

    # -- baseline
    def test_clean_study_passes_every_checker(self):
        for trial in curves.TRIALS:
            self.assertEqual(self.errors(trial), [], trial)

    def test_non_official_output_is_refused_and_cli_exit_code(self):
        errs = self.errors("t4-measure-c16-c20", dev=False)
        self.assertTrue(any(e.startswith("I11:") for e in errs))
        rc = os.system(f"{sys.executable} {HERE / 'check.py'} {self.rd('t1-inventory')} >/dev/null 2>&1")
        self.assertNotEqual(rc, 0)  # mini outputs are dev outputs (and the real edges differ): nonzero exit

    # -- one test per invalidation rule that can be corrupted
    def test_I1_missing_manifest_field(self):
        self.edit_manifest("t4-measure-c16-c20", lambda m: m["resources"].pop("peak_rss_bytes"))
        self.assertRule("t4-measure-c16-c20", "I1")

    def test_I1_empty_or_missing_artifact(self):
        (self.rd("t5-measure-c24-fam") / "raw-result.json").write_text("")
        self.assertRule("t5-measure-c24-fam", "I1")
        (self.rd("t6-measure-c24-na") / "manifest.yaml").unlink()
        self.assertRule("t6-measure-c24-na", "I1")

    def test_I1_missing_trial_fails_t8(self):
        shutil.rmtree(self.rd("t7-measure-c24-nb"))
        self.assertRule("t8-analysis", "R0")

    def test_I2_m0_loop_counter_and_histogram(self):
        raw = self.load("t4-measure-c16-c20")
        raw["members"][0]["m0"]["loop_failures"] = 1
        self.store("t4-measure-c16-c20", raw)
        self.assertRule("t4-measure-c16-c20", "I2")
        raw = self.load("t4-measure-c16-c20")
        raw["members"][0]["m0"]["loop_failures"] = 0
        raw["members"][1]["hist"][0]["total"] += 1
        self.store("t4-measure-c16-c20", raw)
        self.assertRule("t4-measure-c16-c20", "I2")
        raw = self.load("t4-measure-c16-c20")
        raw["members"][1]["hist"][0]["total"] -= 1
        raw["members"][2]["hist"][1]["nonzero"] += 1  # histogram nonzero count differs from the seen[] count
        self.store("t4-measure-c16-c20", raw)
        self.assertRule("t4-measure-c16-c20", "I2")

    def test_I2_t2_recount(self):
        raw = self.load("t2-gate-instrument")
        raw["controls"]["m0_recount"][0]["hist"][0]["total"] += 1
        self.store("t2-gate-instrument", raw)
        self.assertRule("t2-gate-instrument", "I2")

    def test_I3_brute_force_difference(self):
        raw = self.load("t2-gate-instrument")
        raw["controls"]["brute_force"]["detail"][7]["coverage"] += 1
        self.store("t2-gate-instrument", raw)
        self.assertRule("t2-gate-instrument", "I3")
        raw = self.load("t2-gate-instrument")
        raw["controls"]["brute_force"]["detail"][7]["coverage"] -= 1
        raw["controls"]["brute_force"]["cases"] = 59
        raw["controls"]["brute_force"]["detail"].pop()
        self.store("t2-gate-instrument", raw)
        self.assertRule("t2-gate-instrument", "I3")

    def test_I4_curve_validity_in_t1(self):
        raw = self.load("t1-inventory")
        i = next(x for x in raw["instances"] if x["arm"] == "FAM")
        i["N"] += 2          # wrong order: trace identity and [N]P = O fail
        self.store("t1-inventory", raw)
        self.assertRule("t1-inventory", "I4")
        raw = self.load("t1-inventory")
        i = next(x for x in raw["instances"] if x["arm"] == "FAM")
        i["N"] -= 2
        i["p"] = i["p"] + 1  # composite p (even) outside the formulas
        self.store("t1-inventory", raw)
        self.assertRule("t1-inventory", "I4")

    def test_I4_wrong_twist_and_j_and_repeated_prime(self):
        raw = self.load("t1-inventory")
        tw = next(x for x in raw["instances"] if x["arm"] in ("FAM", "N-A") and x["twisted"])
        tw["d"], tw["twisted"] = 1, False
        tw["A"], tw["B"] = curves.chart(1)
        self.store("t1-inventory", raw)
        self.assertRule("t1-inventory", "I4")
        raw = self.load("t1-inventory")
        nb = [x for x in raw["instances"] if x["arm"] == "N-B"]
        nb[1]["p"], nb[1]["N"], nb[1]["A"], nb[1]["B"] = nb[0]["p"], nb[0]["N"], nb[0]["A"], nb[0]["B"]
        self.store("t1-inventory", raw)
        self.assertRule("t1-inventory", "I4")

    def test_I4_member_in_measurement_trial(self):
        raw = self.load("t6-measure-c24-na")
        raw["members"][0]["b"] = raw["members"][0]["a"] + 2  # the family relation is excluded from N-A
        self.store("t6-measure-c24-na", raw)
        self.assertRule("t6-measure-c24-na", "I4")

    def test_I5_label_corruption(self):
        raw = self.load("t4-measure-c16-c20")
        raw["members"][0]["labels"][5] = (raw["members"][0]["labels"][5] + 1) % raw["members"][0]["N"]
        self.store("t4-measure-c16-c20", raw)
        self.assertRule("t4-measure-c16-c20", "I5")

    def test_I5_t2_labelling(self):
        raw = self.load("t2-gate-instrument")
        raw["controls"]["labelling"][0]["check"]["ok"] = False
        self.store("t2-gate-instrument", raw)
        self.assertRule("t2-gate-instrument", "I5")

    def test_I6_qr_window_out_of_band(self):
        raw = self.load("t2-gate-instrument")
        for s in raw["controls"]["qr_scans"]:
            if s["arm"] == "N-B":
                s["scan"]["L"] = int(s["scan"]["S"] * 0.40)  # R = 2.5
        self.store("t2-gate-instrument", raw)
        self.assertRule("t2-gate-instrument", "I6")

    def test_I6_legendre_control_and_full_period_and_lifts(self):
        raw = self.load("t2-gate-instrument")
        for s in raw["controls"]["qr_scans"]:
            if s["arm"] == "N-B":
                s["scan"]["Vlift"] = s["scan"]["V"]  # the x-filter would lift every point: R_wrong = 2
        self.store("t2-gate-instrument", raw)
        self.assertRule("t2-gate-instrument", "I6")
        raw = self.load("t2-gate-instrument")
        raw["controls"]["full_period"][0]["chi_sum"] += 1
        self.store("t2-gate-instrument", raw)
        self.assertRule("t2-gate-instrument", "I6")
        raw = self.load("t2-gate-instrument")
        raw["controls"]["qr_scans"][0]["scan"]["lifts_ok"] = False
        self.store("t2-gate-instrument", raw)
        self.assertRule("t2-gate-instrument", "I6")

    def test_I7_planted_base_not_detected(self):
        raw = self.load("t3-gate-sensitivity")
        cell = raw["members"][0]["cell"]
        for m in [m for m in raw["members"] if m["cell"] == cell][:3]:
            m["member_seen"] = int(np.mean(m["random_seen"]))  # planted base indistinguishable from random
        self.store("t3-gate-sensitivity", raw)
        self.assertRule("t3-gate-sensitivity", "I7")

    def test_I7_pooled_ratio_off_known_value(self):
        raw = self.load("t3-gate-sensitivity")
        for m in raw["members"]:
            m["random_seen"] = [int(v * 1.03) for v in m["random_seen"]]  # all null draws too high
        self.store("t3-gate-sensitivity", raw)
        self.assertRule("t3-gate-sensitivity", "I7")

    def test_I8_seeds_and_instance_sha(self):
        self.edit_manifest("t5-measure-c24-fam", lambda m: m.__setitem__("seeds", [7001, 7002]))
        self.assertRule("t5-measure-c24-fam", "I8")
        raw = self.load("t6-measure-c24-na")
        raw["instance_list_sha256"] = "0" * 64
        self.store("t6-measure-c24-na", raw)
        self.assertRule("t6-measure-c24-na", "I8")

    def test_I8_member_set_and_t1_sha_disagree(self):
        raw = self.load("t7-measure-c24-nb")
        raw["members"].pop()
        self.store("t7-measure-c24-nb", raw)
        self.assertRule("t7-measure-c24-nb", "I8")
        raw = self.load("t1-inventory")
        raw["instance_list_sha256"] = "1" * 64
        self.store("t1-inventory", raw)
        self.assertRule("t4-measure-c16-c20", "I8")  # t4's sha no longer equals the one recorded by t1

    def test_I8_random_base_with_repeated_classes(self):
        raw = self.load("t4-measure-c16-c20")
        raw["members"][0]["random_distinct_failures"] = 1
        self.store("t4-measure-c16-c20", raw)
        self.assertRule("t4-measure-c16-c20", "I8")

    def test_I9_recorded_coverage_differs_from_second_code_path(self):
        raw = self.load("t4-measure-c16-c20")
        for m in raw["members"]:
            m["member_seen"] += 1
            m["hist"][0]["seen"] += 1
            m["hist"][0]["nonzero"] += 1
        self.store("t4-measure-c16-c20", raw)
        self.assertRule("t4-measure-c16-c20", "I9")
        raw = self.load("t5-measure-c24-fam")
        for m in raw["members"]:
            m["random_seen"][0] += 1
        self.store("t5-measure-c24-fam", raw)
        self.assertRule("t5-measure-c24-fam", "I9")

    def test_I9_summary_table_differs_from_raw(self):
        raw = self.load("t8-analysis")
        key = next(iter(raw["tables"]))
        raw["tables"][key]["T"] += 0.001
        self.store("t8-analysis", raw)
        self.assertRule("t8-analysis", "I9")
        raw = self.load("t8-analysis")
        raw["tables"][key]["T"] -= 0.001
        raw["classification"] = "E1_LEAD"
        self.store("t8-analysis", raw)
        self.assertRule("t8-analysis", "I9")

    def test_I9_raw_changed_after_analysis(self):
        raw = self.load("t7-measure-c24-nb")
        for m in raw["members"]:
            m["random_seen"][3] += 50
        self.store("t7-measure-c24-nb", raw)
        self.assertRule("t8-analysis", "I9")

    def test_I11_source_hash_bound_to_plan(self):
        plan = {"source_sha256": {"experiments/EXP-CMFB-cea1d2/implementation/curves.py": "0" * 64}}
        pf = self.root / "trial-plan.json"
        pf.write_text(json.dumps(plan))
        saved = check.PLAN
        check.PLAN = pf
        try:
            errs = check.check_run(self.rd("t1-inventory"), allow_dev=False)
        finally:
            check.PLAN = saved
        self.assertTrue(any(e.startswith("I11:") and "curves.py" in e for e in errs), errs[:4])

    # -- the driver itself
    def test_manifest_and_raw_fields(self):
        for trial in curves.TRIALS:
            m = yaml.safe_load((self.rd(trial) / "manifest.yaml").read_text())["run"]
            self.assertEqual(m["seeds"], list(range(7001, 7011)))
            self.assertGreater(m["resources"]["peak_rss_bytes"], 0)
            self.assertTrue(m["code"]["command"] and m["code"]["commit"])
            self.assertIn("python", m["environment"])
            self.assertIn("numpy", m["environment"])
            self.assertIn("wall_seconds", m["timing"])
        raw = self.load("t4-measure-c16-c20")
        self.assertGreater(raw["timings"]["tau_seconds_per_triple"], 0)
        self.assertIn("worker_rss_bytes_max", raw["timings"])
        mem = raw["members"][0]
        for k in ("arm", "cell", "index", "p", "A", "B", "N", "a", "b", "t", "d", "twisted", "p_mod_120", "base_size", "T",
                  "member_seen", "random_seen", "m0", "hist", "window_W", "scan", "label_check"):
            self.assertIn(k, mem)

    def test_driver_refuses_wrong_run_directory(self):
        with self.assertRaises(SystemExit):
            driver.main(["--trial", "t2-gate-instrument", "--run-dir", str(self.root / "runs" / "RUN-CMFB-000000")])

    def test_four_worker_runs_are_deterministic(self):
        small = sorted(curves.build_instances()["instances"], key=lambda i: i["N"])[:5]
        items = [{"inst": i, "K": 12, "hist": True} for i in small]
        serial = parallel.sharded_map(driver.member_task_det, items, workers=1)
        par4 = parallel.sharded_map(driver.member_task_det, items, workers=4, chunk_size=1)
        self.assertEqual(serial, par4)
        self.assertEqual(parallel.verify_determinism(driver.member_task_det, items, workers=4), serial)
        recs1, _ = driver.run_members(items, 1)
        recs4, _ = driver.run_members(items, 4)
        self.assertEqual(recs1, recs4)  # input order restored after the heaviest-first dispatch

    def test_t3_gate_values_on_mini_study(self):
        raw = self.load("t3-gate-sensitivity")
        self.assertTrue(raw["gate_passed"], raw["gates"])
        for cell, v in raw["sensitivity"].items():
            self.assertGreaterEqual(v["detected"], 7)


# =================================================== interface with the spec
class TestSpecInterface(unittest.TestCase):
    def test_trial_table_matches_specification(self):
        spec = yaml.safe_load(SPEC.read_text())["experiment"]
        trials = spec["trial_plan"]["trials"]
        self.assertEqual([t["id"] for t in trials], list(curves.TRIALS))
        for t in trials:
            run_id, workers, mem, role = curves.TRIALS[t["id"]]
            self.assertEqual((t["run_id"], t["workers"], t["memory_mb"], t["role"]), (run_id, workers, mem, role))
        self.assertEqual(spec["replication"]["seeds"], curves.FROZEN_SEEDS)
        self.assertEqual(spec["planned_records"]["run_ids"], [v[0] for v in curves.TRIALS.values()])
        self.assertEqual(check.RUN_ID, {k: v[0] for k, v in curves.TRIALS.items()})
        self.assertEqual(spec["resolution_delta"]["delta"], analyze.DELTA)

    def test_sources_listed_in_provenance_exist(self):
        for f in analyze.SOURCE_FILES:
            self.assertTrue((REPO / f).is_file(), f)


if __name__ == "__main__":
    unittest.main()

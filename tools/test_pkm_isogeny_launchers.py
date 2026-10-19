#!/usr/bin/env python3
"""Regression tests for the PKM isogeny-chain experiment launchers
(EXP-ECDLP-f49f75, -502ae2, -20a588, -8c41d7).

Each test pins a defect that actually occurred or a property the experiments rely on:
  * the 2-isogeny chain really encodes the fibre x(R + <K>) (distinct, chain(V) = c);
  * the summation polynomials S_3..S_5 vanish on planted decompositions and not on perturbed points;
  * the Singular 32-bit int overflow (AMD-02 of EXP-ECDLP-f49f75) cannot return: planted points must
    still lie in the computed variety for a prime above 46340;
  * msolve keeps only the LAST constant term of a polynomial, so every generated polynomial must
    contain at most one constant;
  * the planted-point checker accepts a true root and rejects non-roots;
  * end to end at m = 3, L = 3: every arm finishes, plants are found, and the chain-first block order
    returns exactly the dense basis (elim_equals_B).
Tool-dependent tests skip when Singular or msolve is missing. Total runtime is a few seconds.
"""
from __future__ import annotations

import hashlib
import importlib.util
import random
import re
import shutil
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def _load(name: str, rel: str):
    spec = importlib.util.spec_from_file_location(name, ROOT / rel)
    mod = importlib.util.module_from_spec(spec)
    sys.modules[name] = mod
    spec.loader.exec_module(mod)
    return mod


HAVE_SINGULAR = shutil.which("Singular") is not None
HAVE_MSOLVE = shutil.which("msolve") is not None
_pkm_path = ROOT / "experiments/EXP-ECDLP-f49f75/pkm_isogeny_fb.py"
SKIP_ALL = not _pkm_path.exists()


def _instance(m: int, L: int, tag: str = "t"):
    """Deterministic planted instance: (p, a, b, chain, picks, T)."""
    pkm = sys.modules["pkm_isogeny_fb"]
    seed = int(hashlib.sha256(f"{tag}|{m}|{L}".encode()).hexdigest()[:12], 16)
    rng = random.Random(seed)
    p = pkm.find_prime(m, L)
    a = p - 3
    while True:
        b = rng.randrange(1, p)
        if (4 * a ** 3 + 27 * b * b) % p:
            break
    chain = pkm.build_chain(p, L, rng)
    fb = pkm.factor_base(chain["V"], a, b, p)
    while True:
        picks = [rng.choice(fb) for _ in range(m)]
        picks = [P if rng.random() < .5 else pkm.ec_neg(P, p) for P in picks]
        T = None
        for P in picks:
            T = pkm.ec_add(T, P, a, p)
        if T is not None:
            return p, a, b, chain, picks, T


@unittest.skipIf(SKIP_ALL, "experiment launchers not present")
class ChainConstruction(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.pkm = _load("pkm_isogeny_fb", "experiments/EXP-ECDLP-f49f75/pkm_isogeny_fb.py")

    def test_fibre_is_distinct_and_maps_to_c(self):
        for L in (3, 4, 5):
            p, a, b, chain, picks, T = _instance(2, L)
            self.assertEqual(len(set(chain["V"])), 2 ** L)
            for v in chain["V"]:
                self.assertEqual(self.pkm.chain_eval(v, chain["steps"], p), chain["c"])

    def test_factor_base_points_are_on_the_target_curve(self):
        p, a, b, chain, picks, T = _instance(2, 4)
        for x, y in self.pkm.factor_base(chain["V"], a, b, p):
            self.assertEqual((y * y - x ** 3 - a * x - b) % p, 0)

    def test_prime_has_the_required_two_power(self):
        for m, L in ((2, 6), (3, 5), (4, 3)):
            p = self.pkm.find_prime(m, L)
            self.assertEqual(p % 4, 3)
            self.assertEqual((p + 1) % 2 ** L, 0)
            self.assertGreater(p, 2 ** (m * L))


@unittest.skipUnless(HAVE_SINGULAR and not SKIP_ALL, "Singular not installed")
class SummationPolynomials(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.pkm = _load("pkm_isogeny_fb", "experiments/EXP-ECDLP-f49f75/pkm_isogeny_fb.py")
        cls.msg = _load("msolve_grid", "experiments/EXP-ECDLP-502ae2/msolve_grid.py")
        cls.m4 = _load("block_order_m4", "experiments/EXP-ECDLP-8c41d7/block_order_m4.py")

    def _poly_zero_on(self, m, L):
        p, a, b, chain, picks, T = _instance(m, L)
        poly = self.m4.summation_poly(p, m, a, b, T[0])
        self.assertNotRegex(poly, r"[XY]")
        names = {f"x{i}": P[0] for i, P in enumerate(picks, 1)}
        val = eval(poly.replace("^", "**"), {"__builtins__": {}}, names) % p
        names["x1"] = (names["x1"] + 1) % p
        pert = eval(poly.replace("^", "**"), {"__builtins__": {}}, names) % p
        return val, pert

    def test_planted_decompositions_vanish_for_m2_m3_m4(self):
        for m in (2, 3, 4):
            val, pert = self._poly_zero_on(m, 3)
            self.assertEqual(val, 0, f"S_{m + 1} must vanish on a planted decomposition")
            self.assertNotEqual(pert, 0, f"S_{m + 1} must not vanish on a perturbed point")

    def test_polynomial_above_the_32bit_int_threshold(self):
        # p > 46340 is where Singular's int arithmetic overflowed before AMD-02 (m = 2 squared a bare integer).
        val, pert = self._poly_zero_on(2, 8)
        self.assertGreater(self.pkm.find_prime(2, 8), 46340)
        self.assertEqual(val, 0)
        self.assertNotEqual(pert, 0)

    def test_m2_planted_point_lies_in_the_singular_variety_above_the_threshold(self):
        # The original defect, end to end. Instance m = 2, L = 9, 0 (p = 263167) is the one on which the
        # planted-decomposition control failed before AMD-02; with bare integers in the Singular script it
        # reports planted_in_variety = False (verified by reintroducing the bug in memory).
        seed = int(hashlib.sha256(b"EXP-ECDLP-f49f75/v1|2|9|0").hexdigest()[:12], 16)
        r = self.pkm.run_instance(dict(m=2, L=9, inst=0, kind="planted", seed=seed, timeout=200,
                                       arms=["B"], solvers=["std"]))
        res = r["results"]["B"]
        self.assertEqual(res["status"], "ok")
        self.assertTrue(res["planted_in_variety"])

    def test_the_regression_test_has_teeth(self):
        # Reintroduce the pre-fix behaviour (bare integers) and require the control to FAIL.
        seed = int(hashlib.sha256(b"EXP-ECDLP-f49f75/v1|2|9|0").hexdigest()[:12], 16)
        job = dict(m=2, L=9, inst=0, kind="planted", seed=seed, timeout=200, arms=["B"], solvers=["std"])
        original = self.pkm.num
        self.pkm.num = lambda v: str(v)
        try:
            res = self.pkm.run_instance(dict(job))["results"]["B"]
        finally:
            self.pkm.num = original
        self.assertFalse(res["planted_in_variety"], "the overflow bug would go undetected by this control")


@unittest.skipUnless(HAVE_MSOLVE and HAVE_SINGULAR and not SKIP_ALL, "msolve and Singular required")
class MsolveInputsAndChecker(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.pkm = _load("pkm_isogeny_fb", "experiments/EXP-ECDLP-f49f75/pkm_isogeny_fb.py")
        cls.msg = _load("msolve_grid", "experiments/EXP-ECDLP-502ae2/msolve_grid.py")

    def test_lin_terms_merges_constants(self):
        s = self.msg.lin_terms([(3, ""), (5, ""), (1, "x")], 101)
        self.assertEqual(len(re.findall(r"(?:^|\+)(\d+)(?=\+|$)", s)), 1)
        self.assertIn("8", s)

    def test_generated_polynomials_have_at_most_one_constant_term(self):
        p, a, b, chain, picks, T = _instance(3, 3)
        S = self.msg.summation_poly(p, 3, a, b, T[0])
        for arm, enc in (("A", chain), ("B", dict(coeffs=self.pkm.poly_from_roots(chain["V"], p)))):
            vars_, polys = self.msg.build_system(arm, p, 3, S, enc)
            for poly in polys:
                consts = [t for t in poly.split("+") if re.fullmatch(r"\d+", t)]
                self.assertLessEqual(len(consts), 1, f"arm {arm}: msolve would drop all but the last constant")

    def test_checker_accepts_a_root_and_rejects_non_roots(self):
        with tempfile.TemporaryDirectory() as d:
            src, out = Path(d) / "k.ms", Path(d) / "k.gb"
            src.write_text("x,y\n65521\nx^2-25,\ny^2-x*y+2*y-28\n")
            status, _, _ = self.msg.run_msolve(["-f", str(src), "-o", str(out), "-g", "2"], 60)
            self.assertEqual(status, "ok")
            gb = out.read_text()
        self.assertTrue(self.msg.eval_gb_at(gb, {"x": 5, "y": 7}, 65521))
        self.assertFalse(self.msg.eval_gb_at(gb, {"x": 5, "y": 8}, 65521))
        self.assertFalse(self.msg.eval_gb_at(gb, {"x": 6, "y": 7}, 65521))


@unittest.skipUnless(HAVE_MSOLVE and HAVE_SINGULAR and not SKIP_ALL, "msolve and Singular required")
class MsolvePrimeCrashCanary(unittest.TestCase):
    """msolve 0.6.5 segfaults on systems over primes with exactly 17 bits (2^16 < p < 2^17); other sizes read
    fine (CORR-20261019-e6f65b, EXP-ECDLP-8c41d7 AMD-03). This is an external defect pinned as a canary: if the
    first assertion starts failing because msolve now succeeds, the defect is fixed and the 17-bit prime
    workaround (block_order_m4_p19.py) and the 'avoid 17-bit primes' rule can be retired."""

    @classmethod
    def setUpClass(cls):
        cls.pkm = _load("pkm_isogeny_fb", "experiments/EXP-ECDLP-f49f75/pkm_isogeny_fb.py")
        cls.msg = _load("msolve_grid", "experiments/EXP-ECDLP-502ae2/msolve_grid.py")

    def _rc(self, p):
        import subprocess
        seed = int(hashlib.sha256(f"canary|{p}".encode()).hexdigest()[:12], 16)
        rng = random.Random(seed)
        a = p - 3
        while True:
            b = rng.randrange(1, p)
            if (4 * a ** 3 + 27 * b * b) % p:
                break
        chain = self.pkm.build_chain(p, 3, rng)
        fb = self.pkm.factor_base(chain["V"], a, b, p)
        picks = [rng.choice(fb) for _ in range(3)]
        T = None
        for P in picks:
            T = self.pkm.ec_add(T, P, a, p)
        S = self.msg.summation_poly(p, 3, a, b, T[0])
        vars_, polys = self.msg.build_system("B", p, 3, S, dict(coeffs=self.pkm.poly_from_roots(chain["V"], p)))
        path = self.msg.write_input(vars_, p, polys)
        return subprocess.run(["msolve", "-f", path, "-o", path + ".gb", "-g", "2", "-t", "1"],
                              capture_output=True, text=True, timeout=120).returncode

    def test_17_bit_prime_crashes_and_other_sizes_do_not(self):
        self.assertEqual(self._rc(70039), -11, "msolve no longer crashes on a 17-bit prime: retire the workaround")
        for p in (60103, 300007):                      # 16 and 19 bits
            self.assertEqual(self._rc(p), 0)


@unittest.skipUnless(HAVE_MSOLVE and HAVE_SINGULAR and not SKIP_ALL, "msolve and Singular required")
class BlockOrderEndToEnd(unittest.TestCase):
    def test_all_arms_finish_plants_found_and_elimination_equals_dense(self):
        bog = _load("block_order_grid", "experiments/EXP-ECDLP-20a588/block_order_grid.py")
        arms = ["A_elim_ms", "A_drl_ms", "B_ms", "A_block_sg", "B_sg"]
        found = 0
        for inst in range(4):
            seed = int(hashlib.sha256(f"EXP-ECDLP-f49f75/v1|3|3|{inst}".encode()).hexdigest()[:12], 16)
            r = bog.run_instance(dict(m=3, L=3, inst=inst, kind="planted", seed=seed, timeout=120, arms=arms))
            if all(v.get("status") == "degenerate_target" for v in r["results"].values()):
                continue
            for arm in arms:
                self.assertEqual(r["results"][arm]["status"], "ok", arm)
                self.assertTrue(r["results"][arm]["planted_in_variety"], arm)
            self.assertTrue(r["elim_equals_B"])
            found += 1
        self.assertGreaterEqual(found, 1)


if __name__ == "__main__":
    unittest.main()

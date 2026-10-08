"""Scalar blinding and GLV decomposition: lattice-vector blinding ("C5") against naive blinding.

Setting.  Endomorphisms act on the order-n subgroup as lambda_1 = 1, ...,
lambda_d; ``lattice.reduce`` gives an LLL-reduced basis b_1..b_d of the
relation lattice L = {v : sum v_i lambda_i = 0 mod n}, and Babai rounding of
(k, 0, ..., 0) gives the short decomposition v(k).  Three ways to randomise
what is computed:

* **classical** k' = k + r n (r of e bits), then decompose: (n, 0, ..., 0) is
  in L, so its coordinates in the basis are integers and rounding commutes
  with the shift -- the decomposition of k' is the decomposition of k.  The
  blinding is erased.  ``erasure`` measures how often the two coincide.
* **naive after decomposition**: x = v(k) + sum r_i b_i with every r_i of e
  bits (each coefficient grows by about e bits; d e bits of randomness).
* **C5 (lattice-vector blinding)**: x = v(k) + sum r_i b_i with r_i of e_i
  bits, sum e_i = e (e/d each): e bits of randomness, each coefficient grows
  by about e/d bits.

Every blinded vector is checked to satisfy sum x_i lambda_i = k (mod n), and
on points for the cases whose maps are available here (secp256k1, CryptoPro-B
from its committed test vectors, FourQ).

What is measured, and what is not.  This module measures the *cost* (the
bit lengths of the coefficients, hence the doubling count of an interleaved
multi-scalar multiplication) and the *distribution* of what is computed (the
min-entropy of the top bits of the blinded coefficients, per coefficient MSB
statistics).  The harness has **no leakage model**: nothing here is a
statement about side-channel security.

Min-entropy of the top bits, three ways:

1. *Exact, any e*: two lattice points in the same cell of side 2^s differ by
   a vector of L with every |coordinate| < 2^s; if 2^s <= lambda_1^inf(L)
   (shortest nonzero vector in the max-norm, computed exactly by bounded
   enumeration) there is none, so the bits >= s of the blinded vector
   determine r and carry exactly e bits of min-entropy given k.
2. *Rigorous lower bound, any window*: if the cell has sides 2^(B_j), a cell
   holds at most N(B) = #{u in L : |u_j| < 2^(B_j)} blinded vectors, so
   H_inf >= e - log2 N(B).  The window used is the bits above the unblinded
   coefficient size B_j (the digits the blinding adds).
3. *Exact enumeration at e = 16*: every one of the 2^16 blinding vectors for
   several fixed k, window as in 2.

    python -m harness.endosweep.blinding --out-dir research/endosweep_frob_blinding_20261008
"""
from __future__ import annotations

import argparse
import ast
import json
import os
import random
import time
from collections import Counter
from dataclasses import dataclass, field
from fractions import Fraction
from itertools import product
from math import log2

from . import lattice as LA

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(os.path.dirname(HERE))

SECP_P = 2 ** 256 - 2 ** 32 - 977
SECP_N = 0xFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFEBAAEDCE6AF48A03BBFD25E8CD0364141
SECP_LAMBDA = 0x5363AD4CC05C30E0A5261C028812645A122E22EA20816678DF02967C1B23BD72
SECP_G = (0x79BE667EF9DCBBAC55A06295CE870B07029BFCDB2DCE28D959F2815B16F81798,
          0x483ADA7726A3C4655DA4FBFC0E1108A8FD17B448A68554199C47D08FFB10D4B8)
# Tom-521 (std-curves other/Tom-521 at 77fe6e3585ca2c2225b59d7df24b7c775437276f): n = 2^521 - 1
TOM521_N = 2 ** 521 - 1


@dataclass
class Case:
    name: str
    n: int
    lams: list[int]
    source: str
    checks: dict = field(default_factory=dict)
    points: dict | None = None          # data for an on-point check, when available


def _cryptopro_b() -> Case:
    path = os.path.join(REPO, "research", "endosweep_20261005", "cryptopro_b_chain_5_5_7.constants.json")
    cp = json.load(open(path))
    n, lam = int(cp["n"], 16), int(cp["eigenvalue"], 16)
    p, a, b = int(cp["p"], 16), int(cp["a"], 16), int(cp["b"], 16)
    def pt(v):
        return [int(x, 16) for x in (ast.literal_eval(v) if isinstance(v, str) else v)]
    tvs = [{"P": pt(tv["P"]), "phiP": pt(tv["phiP"])} for tv in cp["test_vectors"]]
    # 4 + omega, D = -619: trace 9, norm 175; the eigenvalue is that of the element up to sign and conjugation
    chk = {"n prime": _isprime(n), "lambda^2 +- 9 lambda + 175 = 0 mod n":
           any((lam * lam - T * lam + 175) % n == 0 for T in (9, -9))}
    return Case("GOST CryptoPro-B (chain 4+omega, degree 5*5*7)", n, [1, lam],
                "research/endosweep_20261005/cryptopro_b_chain_5_5_7.constants.json", chk,
                {"model": "weierstrass", "p": p, "a": a, "test_vectors": tvs})


def _secp256k1() -> Case:
    chk = {"n prime": _isprime(SECP_N), "lambda^2 + lambda + 1 = 0 mod n":
           (SECP_LAMBDA ** 2 + SECP_LAMBDA + 1) % SECP_N == 0}
    return Case("secp256k1 (zeta_3)", SECP_N, [1, SECP_LAMBDA], "tests/test_endosweep.py constants", chk,
                {"model": "secp256k1"})


def _tom521() -> Case:
    path = os.path.join(REPO, "research", "endosweep_curves_20261006", "curves.json")
    res = json.load(open(path))["results"]
    e = next(x for x in res if x["name"] == "other/Tom-521")
    row = next(r for r in e["rows"] if r["element"] == e["best_element"])
    lam = int(row["eigenvalue"], 16)
    a_, b_ = row["element"]
    D = e["D"]
    T, N = 2 * a_ + b_, a_ * a_ + a_ * b_ + b_ * b_ * (1 - D) // 4         # a + b omega, omega = (1 + sqrt D)/2
    chk = {"n prime": _isprime(TOM521_N), f"lambda^2 +- {T} lambda + {N} = 0 mod n":
           any((lam * lam - s * lam + N) % TOM521_N == 0 for s in (T, -T)), "norm matches curves.json":
           N == row["norm"]}
    return Case(f"Tom-521 (chain {a_}+omega, degree {N})", TOM521_N, [1, lam],
                "research/endosweep_curves_20261006/curves.json (eigenvalue), std-curves (n)", chk)


def _fourq() -> Case:
    from . import fourq as FQ
    res = FQ.verify_fourq()
    N = FQ.N_FOURQ
    lams = [1, res.lambda_phi, res.lambda_psi, res.lambda_phi * res.lambda_psi % N]
    chk = {"FourQ parameters verified": res.verified_parameters,
           "decomposition reconstructs kP (fourq.py)": bool(res.decomposition.get("reconstructs kP (4 random k)"))}
    return Case("FourQ (4-D: 1, phi, psi, phi psi)", N, lams, "harness/endosweep/fourq.py (maps verified on points)",
                chk, {"model": "fourq"})


def _isprime(n: int) -> bool:
    from sympy import isprime
    return isprime(n)


def cases() -> list[Case]:
    return [_cryptopro_b(), _secp256k1(), _tom521(), _fourq()]


# ---------------------------------------------------------------------------
# decomposition and blinding
# ---------------------------------------------------------------------------

class Decomposer:
    """Babai rounding in integer arithmetic: coordinate i of (K, 0, ..., 0) is K * num_i / den_i."""

    def __init__(self, red: LA.ReducedLattice):
        self.red = red
        inv = red._inverse()
        self.row0 = [(x.numerator, x.denominator) for x in inv[0]]

    def decompose_unreduced(self, K: int) -> list[int]:
        """Babai on (K, 0, ..., 0) with K NOT reduced mod n (round half up)."""
        d = self.red.dim
        v = [K] + [0] * (d - 1)
        for (num, den), b in zip(self.row0, self.red.basis):
            c = (2 * K * num + den) // (2 * den)
            if c:
                v = [x - c * y for x, y in zip(v, b)]
        return v


def split_bits(e: int, d: int) -> list[int]:
    """e bits over d coefficients, as evenly as possible."""
    return [e // d + (1 if i < e % d else 0) for i in range(d)]


def blind(v: list[int], basis: list[list[int]], rbits: list[int], rng: random.Random):
    """v + sum r_i b_i with r_i uniform in [-2^(e_i - 1), 2^(e_i - 1)); returns (x, r)."""
    r = [rng.randrange(1 << eb) - (1 << (eb - 1)) if eb else 0 for eb in rbits]
    x = list(v)
    for ri, b in zip(r, basis):
        if ri:
            x = [a + ri * c for a, c in zip(x, b)]
    return x, r


def reconstructs(x: list[int], lams: list[int], k: int, n: int) -> bool:
    return (sum(a * l for a, l in zip(x, lams)) - k) % n == 0


# ---------------------------------------------------------------------------
# lattice geometry: lambda_1 in the max-norm, and box counts
# ---------------------------------------------------------------------------

def _box_enumerate(red: LA.ReducedLattice, R: list[int], limit: int = 3_000_000):
    """Every nonzero u in L with |u_j| <= R_j (exact: coefficient bounds from the inverse basis)."""
    inv = red._inverse()                     # inv[j][i]: coordinate i of the j-th unit vector
    d = red.dim
    C = [int(sum(Fraction(R[j]) * abs(inv[j][i]) for j in range(d))) for i in range(d)]
    total = 1
    for c in C:
        total *= 2 * c + 1
    if total > limit:
        return None
    out = []
    for cs in product(*[range(-c, c + 1) for c in C]):
        if not any(cs):
            continue
        u = [0] * d
        for ci, b in zip(cs, red.basis):
            if ci:
                u = [a + ci * y for a, y in zip(u, b)]
        if all(abs(a) <= R[j] for j, a in enumerate(u)):
            out.append(u)
    return out


def lambda1_inf(red: LA.ReducedLattice) -> int:
    R0 = min(LA.inf_norm(b) for b in red.basis)
    pts = _box_enumerate(red, [R0] * red.dim)
    return min(LA.inf_norm(u) for u in pts)


def box_count(red: LA.ReducedLattice, B: list[int]) -> int | None:
    """N(B) = #{u in L : |u_j| < 2^(B_j)}, the origin included."""
    pts = _box_enumerate(red, [(1 << b) - 1 for b in B])
    return None if pts is None else len(pts) + 1


def _cell(x: list[int], B: list[int]) -> tuple:
    return tuple(a >> b for a, b in zip(x, B))          # floor(x_j / 2^B_j), negatives included


def exact_window_entropy(red: LA.ReducedLattice, v: list[int], rbits: list[int], B: list[int]) -> float:
    """Exact H_inf of the cells floor(x_j / 2^B_j) over every r in the blinding box (small e only)."""
    ranges = [range(-(1 << (eb - 1)), 1 << (eb - 1)) if eb else range(1) for eb in rbits]
    cnt: Counter = Counter()
    total = 0
    basis = red.basis
    for rs in product(*ranges):
        x = list(v)
        for ri, b in zip(rs, basis):
            if ri:
                x = [a + ri * c for a, c in zip(x, b)]
        cnt[_cell(x, B)] += 1
        total += 1
    return log2(total) - log2(max(cnt.values()))


def plugin_min_entropy(values: list) -> float:
    c = Counter(values)
    return -log2(max(c.values()) / len(values))


def top_window(x: int, L: int, T: int) -> tuple:
    """(sign, the T bits of |x| at positions L-1 .. L-T)."""
    return (x < 0, (abs(x) >> (L - T)) & ((1 << T) - 1))


# ---------------------------------------------------------------------------
# on-point checks
# ---------------------------------------------------------------------------

def _w_mul(p, a, k, P):
    from .targets import _mul, _w_add
    if k < 0:
        return _w_mul(p, a, -k, (P[0], (-P[1]) % p))
    return _mul(lambda X, Y: _w_add(p, a, X, Y), None, k, P)


def points_check(case: Case, samples: list[tuple[int, list[int]]]) -> dict | None:
    """sum x_i phi_i(P) = k P on points for a few (k, x)."""
    if not case.points:
        return None
    from .targets import _w_add
    model = case.points["model"]
    ok = True
    if model in ("weierstrass", "secp256k1"):
        if model == "secp256k1":
            p, a = SECP_P, 0
            P = SECP_G
            beta = next(b for b in (pow(g, (p - 1) // 3, p) for g in range(2, 50)) if b != 1
                        and _w_mul(p, 0, SECP_LAMBDA, P) in ((b * P[0] % p, P[1]), (b * b * P[0] % p, P[1])))
            phiP = (beta * P[0] % p, P[1]) if _w_mul(p, 0, SECP_LAMBDA, P) == (beta * P[0] % p, P[1]) \
                else (beta * beta * P[0] % p, P[1])
            pairs = [(P, phiP)]
        else:
            p, a = case.points["p"], case.points["a"]
            pairs = [(tuple(tv["P"]), tuple(tv["phiP"])) for tv in case.points["test_vectors"]]
        lam = case.lams[1]
        for (P, phiP) in pairs[:2]:
            ok &= _w_mul(p, a, lam, P) == phiP
            for k, x in samples:
                lhs = _w_mul(p, a, k, P)
                rhs = _w_add(p, a, _w_mul(p, a, x[0], P), _w_mul(p, a, x[1], phiP))
                ok &= lhs == rhs
        return {"points": len(pairs[:2]), "samples": len(samples), "ok": ok}
    if model == "fourq":
        from . import fourq as FQ
        C = FQ.Fp2Counter()
        maps = FQ.FourQMaps(C)
        E = maps.E
        rng = random.Random(11)
        P = None
        while P is None:
            Q = E.lift_x(FQ.Fp2(rng.randrange(FQ.P127), rng.randrange(FQ.P127), C))
            if Q is None:
                continue
            R = E.mul(FQ.COFACTOR, Q)
            if R != E.identity():
                P = R
        imgs = [P, maps.phi(P), maps.psi(P), maps.psi(maps.phi(P))]

        def smul(k, Q):
            if k < 0:
                return E.neg(E.mul(-k, Q))
            return E.mul(k, Q)
        for k, x in samples:
            rhs = E.identity()
            for xi, Qi in zip(x, imgs):
                rhs = E.add(rhs, smul(xi, Qi))
            ok &= rhs == E.mul(k, P)
        return {"points": 1, "samples": len(samples), "ok": ok}
    return None


# ---------------------------------------------------------------------------
# the measurement
# ---------------------------------------------------------------------------

def _bl(x: int) -> int:
    return abs(x).bit_length()


def measure_case(case: Case, e: int = 64, samples: int = 10_000, seed: int = 20261008, e_small: int = 16,
                 k_small: int = 8, point_samples: int = 3) -> dict:
    n, lams = case.n, case.lams
    red = LA.reduce(lams, n)
    dec = Decomposer(red)
    d = red.dim
    b = n.bit_length()
    rng = random.Random(seed)
    c5_bits = split_bits(e, d)
    naive_bits = [e] * d
    stats = {s: {"D": [], "coeff": [[] for _ in range(d)], "x": []} for s in ("unblinded", "c5", "naive")}
    classical_len = []
    erased = 0
    recon = {"c5": True, "naive": True, "unblinded": True}
    point_pairs = []
    for i in range(samples):
        k = rng.randrange(1, n)
        v = red.decompose(k)
        # classical blinding, then decomposition
        rc = rng.randrange(1 << e)
        kk = k + rc * n
        classical_len.append(kk.bit_length())
        erased += dec.decompose_unreduced(kk) == v
        xs = {"unblinded": v}
        xs["c5"], _ = blind(v, red.basis, c5_bits, rng)
        xs["naive"], _ = blind(v, red.basis, naive_bits, rng)
        for s, x in xs.items():
            recon[s] &= reconstructs(x, lams, k, n)
            stats[s]["D"].append(max(_bl(a) for a in x))
            for j, a in enumerate(x):
                stats[s]["coeff"][j].append(a)
        if i < point_samples:
            point_pairs.append((k, xs["c5"]))
            point_pairs.append((k, xs["naive"]))
    # bit lengths
    out: dict = {"name": case.name, "source": case.source, "case_checks": case.checks, "dim": d,
                 "n_bits": b, "e": e, "samples": samples, "c5_bits_per_coefficient": c5_bits,
                 "basis_inf_norm_bits": [LA.inf_norm(x).bit_length() for x in red.basis],
                 "babai_bound_bits": red.babai_bound.bit_length()}
    mean = lambda v: sum(v) / len(v)  # noqa: E731
    bl = {}
    for s, st in stats.items():
        bl[s] = {"doublings_mean": round(mean(st["D"]), 3), "doublings_max": max(st["D"]),
                 "coeff_bits_max": [max(_bl(a) for a in col) for col in st["coeff"]],
                 "coeff_bits_mean": [round(mean([_bl(a) for a in col]), 3) for col in st["coeff"]]}
    # provable bound on |x_j|: babai bound + sum_i 2^(e_i - 1) |b_ij|
    for s, rb in (("c5", c5_bits), ("naive", naive_bits)):
        bound = [red.babai_bound + sum((1 << (eb - 1)) * abs(bv[j]) for eb, bv in zip(rb, red.basis))
                 for j in range(d)]
        bl[s]["provable_bound_bits"] = [x.bit_length() for x in bound]
    bl["unblinded"]["provable_bound_bits"] = [red.babai_bound.bit_length()] * d
    out["bit_lengths"] = bl
    cl_mean = mean(classical_len)
    out["classical"] = {"k_plus_rn_bits_mean": round(cl_mean, 3), "k_plus_rn_bits_max": max(classical_len),
                        "decomposition_of_k_plus_rn_equals_decomposition_of_k": f"{erased}/{samples}"}
    extra_mean = bl["c5"]["doublings_mean"] - bl["unblinded"]["doublings_mean"]
    extra_max = bl["c5"]["doublings_max"] - bl["unblinded"]["doublings_max"]
    extra_bound = max(bl["c5"]["provable_bound_bits"]) - max(bl["unblinded"]["provable_bound_bits"])
    out["c5_extra_bits"] = {"mean": round(extra_mean, 3), "max": extra_max, "provable": extra_bound,
                            "e_over_d": e / d, "kill_threshold": e / d + 2,
                            "killed": max(extra_mean, extra_max) > e / d + 2}
    out["naive_extra_bits"] = {"mean": round(bl["naive"]["doublings_mean"] - bl["unblinded"]["doublings_mean"], 3),
                               "max": bl["naive"]["doublings_max"] - bl["unblinded"]["doublings_max"]}
    # doubling-count ratios against classical blinding without GLV
    out["doubling_ratio"] = {
        "c5_measured": round(cl_mean / bl["c5"]["doublings_mean"], 3),
        "naive_measured": round(cl_mean / bl["naive"]["doublings_mean"], 3),
        "unblinded_glv_vs_unblinded_plain": round((b - 1) / bl["unblinded"]["doublings_mean"], 3),
        "predicted_c5": d, "predicted_naive": round(d * (b + e) / (b + d * e), 3)}
    out["reconstructs_k_mod_n"] = recon
    out["points"] = points_check(case, point_pairs)
    # --- min-entropy -----------------------------------------------------
    lam1 = lambda1_inf(red)
    s0 = lam1.bit_length() - 1                       # 2^s0 <= lambda_1^inf
    Lc5 = bl["c5"]["provable_bound_bits"]
    ent: dict = {"lambda1_inf_bits": lam1.bit_length(), "s0": s0,
                 "exact_window_s0": {"top_bits_per_coefficient": [L + 1 - s0 for L in Lc5],
                                     "min_entropy_given_k": e,
                                     "why": "2^s0 <= lambda_1^inf(L): distinct r give distinct cells"}}
    B = bl["unblinded"]["coeff_bits_max"]            # bits above the unblinded coefficient size
    N_B = box_count(red, B)
    ent["blinding_window"] = {
        "B": B, "top_bits_per_coefficient": [L + 1 - Bj for L, Bj in zip(Lc5, B)],
        "N_B": N_B, "lower_bound_e": None if N_B is None else round(e - log2(N_B), 3)}
    # exact enumeration at a small e
    rb_small = split_bits(e_small, d)
    rng2 = random.Random(seed + 1)
    hs, hs0 = [], []
    for _ in range(k_small):
        k = rng2.randrange(1, n)
        v = red.decompose(k)
        hs.append(exact_window_entropy(red, v, rb_small, B))
        hs0.append(exact_window_entropy(red, v, rb_small, [s0] * d))
    ent["exact_small_e"] = {"e": e_small, "k_values": k_small, "blinding_window_min": round(min(hs), 3),
                            "blinding_window_mean": round(sum(hs) / len(hs), 3), "window_s0_min": round(min(hs0), 3),
                            "lower_bound": None if N_B is None else round(e_small - log2(N_B), 3)}
    deficit = e_small - min(hs)
    ent["kill_check"] = {"criterion": "total min-entropy of the top digits < e - 4",
                         "deficit_exact_small_e": round(deficit, 3),
                         "deficit_bound_any_e": None if N_B is None else round(log2(N_B), 3),
                         "killed": deficit > 4}
    # per-coefficient top-window statistics at e (sample), against the classical k + r n
    per = []
    for s in ("c5", "naive"):
        Ls = bl[s]["provable_bound_bits"]
        for j in range(d):
            col = stats[s]["coeff"][j]
            L = Ls[j]
            row = {"scheme": s, "coefficient": j, "loop_bits": L,
                   "P(bitlen = loop_bits)": round(sum(1 for a in col if _bl(a) == L) / samples, 4),
                   "P(bitlen >= loop_bits - 2)": round(sum(1 for a in col if _bl(a) >= L - 2) / samples, 4),
                   "P(bit loop_bits-1 set)": round(sum(1 for a in col if abs(a) >> (L - 1) & 1) / samples, 4),
                   "P(sign negative)": round(sum(1 for a in col if a < 0) / samples, 4)}
            for T in (1, 2, 4):
                row[f"H_inf top{T}+sign"] = round(plugin_min_entropy([top_window(a, L, T) for a in col]), 3)
            # the same window at the empirical maximum bit length
            Lm = bl[s]["coeff_bits_max"][j]
            row["H_inf top4+sign at empirical max"] = round(plugin_min_entropy([top_window(a, Lm, 4) for a in col]), 3)
            per.append(row)
    # classical reference: k + r n at its own length
    rng3 = random.Random(seed + 2)
    kk = [rng3.randrange(1, n) + rng3.randrange(1 << e) * n for _ in range(samples)]
    Lk = max(x.bit_length() for x in kk)
    per.append({"scheme": "classical k + r n (no GLV)", "coefficient": 0, "loop_bits": Lk,
                "P(bitlen = loop_bits)": round(sum(1 for a in kk if a.bit_length() == Lk) / samples, 4),
                "P(bit loop_bits-1 set)": round(sum(1 for a in kk if a >> (Lk - 1) & 1) / samples, 4),
                **{f"H_inf top{T}+sign": round(plugin_min_entropy([top_window(a, Lk, T) for a in kk]), 3)
                   for T in (1, 2, 4)}})
    ent["per_coefficient"] = per
    # joint: top 2 bits + sign of every coefficient, C5
    joint = [tuple(top_window(stats["c5"]["coeff"][j][i], Lc5[j], 2) for j in range(d)) for i in range(samples)]
    ent["joint_top2_sign_c5"] = {"outcomes_max": 8 ** d, "H_inf_plugin": round(plugin_min_entropy(joint), 3),
                                 "distinct_seen": len(set(joint))}
    out["min_entropy"] = ent
    out["verdict"] = {"extra_bits_ok": not out["c5_extra_bits"]["killed"],
                      "min_entropy_ok": not ent["kill_check"]["killed"],
                      "doubling_ratio_c5_vs_d": f"{out['doubling_ratio']['c5_measured']} vs {d}"}
    return out


def run(out_dir: str, samples: int, e: int, seed: int = 20261008) -> dict:
    t0 = time.time()
    doc = {"e": e, "samples": samples, "seed": seed,
           "note": "no leakage model: cost and the distribution of the computed coefficients only", "cases": []}
    for c in cases():
        t1 = time.time()
        r = measure_case(c, e=e, samples=samples, seed=seed)
        r["elapsed_s"] = round(time.time() - t1, 1)
        doc["cases"].append(r)
    # e sweep for the cost law on one 2-D and the 4-D case (fewer samples)
    sweep = []
    for c in cases():
        if c.name.startswith("secp256k1") or c.name.startswith("FourQ"):
            red = LA.reduce(c.lams, c.n)
            rng = random.Random(seed + 9)
            for ee in (16, 32, 64, 128):
                D0, D1 = [], []
                for _ in range(2000):
                    k = rng.randrange(1, c.n)
                    v = red.decompose(k)
                    x, _ = blind(v, red.basis, split_bits(ee, red.dim), rng)
                    D0.append(max(_bl(a) for a in v))
                    D1.append(max(_bl(a) for a in x))
                sweep.append({"case": c.name, "e": ee, "e_over_d": ee / red.dim,
                              "extra_bits_mean": round((sum(D1) - sum(D0)) / len(D0), 3),
                              "extra_bits_max": max(D1) - max(D0)})
    doc["e_sweep"] = sweep
    doc["elapsed_s"] = round(time.time() - t0, 1)
    os.makedirs(out_dir, exist_ok=True)
    with open(os.path.join(out_dir, "blinding.json"), "w") as f:
        json.dump(doc, f, indent=1)
    with open(os.path.join(out_dir, "blinding.md"), "w") as f:
        f.write(markdown(doc))
    return doc


def markdown(doc: dict) -> str:
    e = doc["e"]
    L = ["# Lattice-vector blinding for GLV (C5) against naive blinding", "",
         f"e = {e} bits of blinding, {doc['samples']} random scalars per case. **Measured** bit lengths (the doubling "
         "count of an interleaved multi-scalar multiplication is the largest coefficient bit length). "
         f"{doc['note']}.", "",
         "## Cost", "",
         "| case | d | n bits | unblinded D (mean/max) | C5 D (mean/max) | naive D (mean/max) | C5 extra bits "
         "(mean/max/provable) | e/d | k + r n bits | ratio C5 (pred. d) | ratio naive (pred.) | classical erased |",
         "|:--|--:|--:|--:|--:|--:|--:|--:|--:|--:|--:|--:|"]
    for c in doc["cases"]:
        b = c["bit_lengths"]
        x = c["c5_extra_bits"]
        r = c["doubling_ratio"]
        L.append(f"| {c['name']} | {c['dim']} | {c['n_bits']} | {b['unblinded']['doublings_mean']} / "
                 f"{b['unblinded']['doublings_max']} | {b['c5']['doublings_mean']} / {b['c5']['doublings_max']} | "
                 f"{b['naive']['doublings_mean']} / {b['naive']['doublings_max']} | {x['mean']} / {x['max']} / "
                 f"{x['provable']} | {x['e_over_d']:g} | {c['classical']['k_plus_rn_bits_mean']} | "
                 f"{r['c5_measured']} ({r['predicted_c5']}) | {r['naive_measured']} ({r['predicted_naive']}) | "
                 f"{c['classical']['decomposition_of_k_plus_rn_equals_decomposition_of_k']} |")
    L += ["", "Every blinded vector reconstructs k mod n: " + "; ".join(
        f"{c['name']}: {all(c['reconstructs_k_mod_n'].values())}" for c in doc["cases"]), "",
          "On points: " + "; ".join(f"{c['name']}: {c['points']}" for c in doc["cases"] if c["points"]), "",
          "## Min-entropy of the top bits (given k)", "",
          "| case | lambda_1^inf bits | window bits >= s0: H_inf | blinding window B_j | top bits/coeff | N(B) | "
          f"bound e - log2 N(B) | exact at e = 16 (min over k) | deficit | killed (< e - 4) |",
          "|:--|--:|--:|:--|:--|--:|--:|--:|--:|:--|"]
    for c in doc["cases"]:
        m = c["min_entropy"]
        bw = m["blinding_window"]
        ex = m["exact_small_e"]
        L.append(f"| {c['name']} | {m['lambda1_inf_bits']} | {m['exact_window_s0']['min_entropy_given_k']} (exact) | "
                 f"{bw['B']} | {bw['top_bits_per_coefficient']} | {bw['N_B']} | {bw['lower_bound_e']} | "
                 f"{ex['blinding_window_min']} / {ex['e']} | {m['kill_check']['deficit_exact_small_e']} | "
                 f"{m['kill_check']['killed']} |")
    L += ["", "## Per-coefficient top bits (sample of 10^4, plug-in min-entropy)", "",
          "loop_bits = the provable bound (a constant-time loop length); H_inf of (sign, top T bits of |x| below it).",
          "", "| case | scheme | j | loop bits | P(bitlen = loop) | P(top bit set) | H top1+s | H top2+s | H top4+s | "
          "H top4+s at empirical max |", "|:--|:--|--:|--:|--:|--:|--:|--:|--:|--:|"]
    for c in doc["cases"]:
        for r in c["min_entropy"]["per_coefficient"]:
            L.append(f"| {c['name']} | {r['scheme']} | {r['coefficient']} | {r['loop_bits']} | "
                     f"{r['P(bitlen = loop_bits)']} | {r['P(bit loop_bits-1 set)']} | {r['H_inf top1+sign']} | "
                     f"{r['H_inf top2+sign']} | {r['H_inf top4+sign']} | {r.get('H_inf top4+sign at empirical max', '')} |")
    L += ["", "## Extra bits against e (2000 scalars each)", "", "| case | e | e/d | extra mean | extra max |",
          "|:--|--:|--:|--:|--:|"]
    for s in doc["e_sweep"]:
        L.append(f"| {s['case']} | {s['e']} | {s['e_over_d']:g} | {s['extra_bits_mean']} | {s['extra_bits_max']} |")
    L.append("")
    return "\n".join(L)


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description="lattice-vector blinding for GLV decompositions")
    ap.add_argument("--out-dir", required=True)
    ap.add_argument("--samples", type=int, default=10_000)
    ap.add_argument("--e", type=int, default=64)
    args = ap.parse_args(argv)
    doc = run(args.out_dir, args.samples, args.e)
    ok = all(all(c["reconstructs_k_mod_n"].values()) and (c["points"] is None or c["points"]["ok"])
             and all(c["case_checks"].values()) for c in doc["cases"])
    print(f"{len(doc['cases'])} cases, all reconstruct and verify: {ok}, {doc['elapsed_s']} s")
    return 0 if ok else 1


if __name__ == "__main__":
    raise SystemExit(main())

#!/usr/bin/env python3
"""Independent matched-null check of the EV-BINSTD-769c7c collision ratio.

Question. EV-BINSTD-769c7c (EXP-BINSTD-cedae5, H-BINSTD-fe6b59) reports a
curve/generic residual-collision ratio of about 3.1 (n=17 RC-1: 3.105, n=19:
3.030) and reads it as structural concentration. This program rebuilds the
observable from the statement of the experiment alone, WITHOUT reading or
importing the producer's code, and asks what a generic group would give when it
is matched to the curve side on the two features the producer's replica lacks:

  (1) negation closure of the window (V = -V, so {P,Q} and {-P,-Q} are both
      pairs), and
  (2) sign-folded keys (the curve key is x(L), which identifies L and -L).

Observable (from stage0/canonicalisation-convention.md, restated): for each
unordered pair {P,Q} of distinct window points with P+Q != O, the residual is
L = -(P+Q) and the key is x(L).  "combined" = number of unordered pairs of
attempts with equal key = sum over keys of C(multiplicity, 2).  The reported
ratio is combined / (T^2 / (2N)), T = number of attempts, N = group order.

Everything here is exact integer arithmetic.  The only randomness is the
seeded window choice in the generic simulations and the random-window controls.

Usage:  python3 matched_null_check.py --out OUTPUT.json   (about 2 minutes)
"""
from __future__ import annotations

import argparse
import hashlib
import json
import platform
import sys
import time

import numpy as np

# --------------------------------------------------------------------------
# GF(2^n), polynomial basis, bit i = coefficient of t^i.  Both 2^17-1 and
# 2^19-1 are prime, so t generates the multiplicative group whenever the
# modulus is irreducible; this is asserted, not assumed.
# --------------------------------------------------------------------------


class Field:
    def __init__(self, n: int, modulus: int):
        self.n, self.modulus = n, modulus
        self.q1 = (1 << n) - 1
        exp = np.zeros(2 * self.q1 + 2, dtype=np.int64)
        log = np.zeros(1 << n, dtype=np.int64)
        v = 1
        for i in range(self.q1):
            exp[i] = v
            log[v] = i
            v <<= 1
            if v >> n:
                v ^= modulus
        assert v == 1, "t does not have order 2^n-1: modulus not irreducible/primitive"
        assert len(set(exp[: self.q1].tolist())) == self.q1
        exp[self.q1: 2 * self.q1] = exp[: self.q1]
        self.exp, self.log = exp, log
        # solutions of z^2 + z = c: SOL[c] = z (either root), -1 if Tr(c) = 1
        z = np.arange(1 << n, dtype=np.int64)
        f = self.sq(z) ^ z
        sol = np.full(1 << n, -1, dtype=np.int64)
        sol[f] = z
        self.sol = sol

    def mul(self, a, b):
        a, b = np.asarray(a, dtype=np.int64), np.asarray(b, dtype=np.int64)
        r = self.exp[self.log[a] + self.log[b]]
        return np.where((a == 0) | (b == 0), 0, r)

    def sq(self, a):
        a = np.asarray(a, dtype=np.int64)
        return np.where(a == 0, 0, self.exp[2 * self.log[a]])

    def inv(self, a):
        a = np.asarray(a, dtype=np.int64)
        assert (a != 0).all()
        return self.exp[self.q1 - self.log[a]]

    # scalar helpers for the cross-checks
    def smul(self, a: int, b: int) -> int:
        return int(self.mul(a, b)) if a and b else 0

    def sinv(self, a: int) -> int:
        return int(self.inv(a))


class Curve:
    """y^2 + x y = x^3 + a x^2 + b over GF(2^n), b != 0."""

    def __init__(self, F: Field, a: int, b: int, order: int):
        self.F, self.a, self.b, self.order = F, a, b, order
        assert b != 0

    # -- point enumeration -------------------------------------------------
    def points_with_x(self, xs: np.ndarray):
        """All affine points whose abscissa lies in xs (xs: array of ints)."""
        F = self.F
        xs = np.unique(np.asarray(xs, dtype=np.int64))
        out_x, out_y = [], []
        nz = xs[xs != 0]
        if (xs == 0).any():
            # y^2 = b : y = b^(2^(n-1))
            y0 = int(F.exp[(int(F.log[self.b]) * (1 << (F.n - 1))) % F.q1])
            assert (y0 * 0 + int(F.sq(y0))) == self.b
            out_x.append(np.array([0], dtype=np.int64))
            out_y.append(np.array([y0], dtype=np.int64))
        # x != 0 : y = x z, z^2 + z = x + a + b / x^2
        c = nz ^ self.a ^ F.mul(self.b, F.inv(F.sq(nz)))
        z = F.sol[c]
        ok = z >= 0
        x_ok, y_ok = nz[ok], F.mul(nz[ok], z[ok])
        out_x += [x_ok, x_ok]
        out_y += [y_ok, y_ok ^ x_ok]
        px, py = np.concatenate(out_x), np.concatenate(out_y)
        o = np.lexsort((py, px))
        return px[o], py[o]

    def count_affine_points(self) -> int:
        px, _ = self.points_with_x(np.arange(1 << self.F.n))
        return len(px)

    def on_curve(self, x, y):
        F = self.F
        lhs = F.sq(y) ^ F.mul(x, y)
        rhs = F.mul(F.sq(x), x) ^ F.mul(self.a, F.sq(x)) ^ self.b
        return lhs == rhs

    # -- scalar group law (full affine, used only for cross-checks) --------
    def add_scalar(self, P, Q):
        F = self.F
        if P is None:
            return Q
        if Q is None:
            return P
        (x1, y1), (x2, y2) = P, Q
        if x1 == x2:
            if y1 != y2 or x1 == 0:
                return None  # Q = -P, or 2-torsion doubled
            lam = x1 ^ F.smul(y1, F.sinv(x1))
            x3 = int(F.sq(lam)) ^ lam ^ self.a
            y3 = int(F.sq(x1)) ^ F.smul(lam ^ 1, x3)
            return (x3, y3)
        lam = F.smul(y1 ^ y2, F.sinv(x1 ^ x2))
        x3 = int(F.sq(lam)) ^ lam ^ x1 ^ x2 ^ self.a
        y3 = F.smul(lam, x1 ^ x3) ^ x3 ^ y1
        return (x3, y3)

    def mul_scalar(self, k: int, P):
        R = None
        while k:
            if k & 1:
                R = self.add_scalar(R, P)
            P = self.add_scalar(P, P)
            k >>= 1
        return R

    # -- vectorised x-coordinate of the sum --------------------------------
    def sum_x(self, x1, y1, x2, y2):
        """x(P1+P2) for x1 != x2 (affine addition formula)."""
        F = self.F
        lam = F.mul(y1 ^ y2, F.inv(x1 ^ x2))
        return F.sq(lam) ^ lam ^ x1 ^ x2 ^ self.a


# --------------------------------------------------------------------------
# census
# --------------------------------------------------------------------------


def collision_count(keys: np.ndarray) -> tuple[int, int, int]:
    """(sum C(m,2), distinct keys, max multiplicity)."""
    _, c = np.unique(keys, return_counts=True)
    c = c.astype(np.int64)
    return int((c * (c - 1) // 2).sum()), int(len(c)), int(c.max())


def p_same_class(N: int) -> float:
    """P(two independent uniform nonzero residuals of Z/N share a +-class)."""
    return (2 * N - 3) / (N - 1) ** 2


def expected_nontrivial(T: int, N: int) -> float:
    return (T * (T - 1) / 2 - T / 2) * p_same_class(N)


def curve_census(C: Curve, px: np.ndarray, py: np.ndarray, closed: bool) -> dict:
    """Census of the free-leg residual observable on window points (px, py)."""
    F, V, N = C.F, len(px), C.order
    assert C.on_curve(px, py).all()
    I, J = np.triu_indices(V, 1)
    I, J = I.astype(np.int64), J.astype(np.int64)
    valid = px[I] != px[J]
    ident = int((~valid).sum())
    I, J = I[valid], J[valid]
    T = len(I)
    keys = C.sum_x(px[I], py[I], px[J], py[J])
    combined, distinct, maxm = collision_count(keys)
    res = dict(window_size=V, N=N, T=T, identity_sum_pairs=ident,
               combined=combined, distinct_keys=distinct, max_multiplicity=maxm,
               modeled_T2_over_2N=T * T / (2 * N),
               reported_style_ratio=combined / (T * T / (2 * N)),
               S_fit=T * T / (2 * combined))
    if closed:
        # negation map on the window and the partner pair {-P,-Q}
        code = (px << F.n) | py
        order = np.argsort(code)
        ncode = (px << F.n) | (px ^ py)
        pos = np.minimum(np.searchsorted(code[order], ncode), V - 1)
        assert (code[order][pos] == ncode).all(), "window not closed under negation"
        neg = order[pos]
        assert (neg[neg] == np.arange(V)).all()
        I2, J2 = neg[I], neg[J]
        lo, hi = np.minimum(I2, J2), np.maximum(I2, J2)
        self_partner = int(((lo == I) & (hi == J)).sum())
        pair_code = I * V + J
        po = np.argsort(pair_code)
        pc = lo * V + hi
        ppos = np.minimum(np.searchsorted(pair_code[po], pc), len(pc) - 1)
        assert (pair_code[po][ppos] == pc).all(), "partner pair missing"
        keys_partner = C.sum_x(px[lo], py[lo], px[hi], py[hi])
        same_key = int((keys_partner == keys).sum())
        trivial = same_key // 2
        res.update(self_partner_pairs=self_partner, partner_pairs_same_key=same_key,
                   trivial_partner_collisions=trivial)
        non = combined - trivial
        exp_non = expected_nontrivial(T, N)
        res.update(nontrivial_collisions=non, expected_nontrivial_uniform=exp_non,
                   nontrivial_over_expected=non / exp_non,
                   predicted_reported_style_ratio_matched_null=(exp_non + trivial)
                   / (T * T / (2 * N)),
                   leading_order_prediction_2_plus_N_over_T=2 + N / T,
                   S_fit_nontrivial=T * T / (2 * non), S_expected_signfolded=N / 2)
    else:
        exp_all = (T * (T - 1) / 2) * p_same_class(N)
        res.update(expected_collisions_uniform_signfolded=exp_all,
                   combined_over_expected_signfolded=combined / exp_all)
    return res


# --------------------------------------------------------------------------
# generic Z/N simulations
# --------------------------------------------------------------------------


def generic_census(N: int, window: np.ndarray, fold: bool) -> dict:
    V = len(window)
    I, J = np.triu_indices(V, 1)
    s = (window[I] + window[J]) % N
    valid = s != 0
    ident = int((~valid).sum())
    L = (-s[valid]) % N
    T = len(L)
    keys = np.minimum(L, (N - L) % N) if fold else L
    combined, distinct, maxm = collision_count(keys)
    return dict(window_size=V, T=T, identity_sum_pairs=ident, combined=combined,
                distinct_keys=distinct, reported_style_ratio=combined / (T * T / (2 * N)))


def closed_window(N: int, V: int, rng: np.random.Generator) -> np.ndarray:
    """{N/2} u {+-a_k}: negation closed, one self-negative (2-torsion) element,
    like the curve window (V odd)."""
    assert N % 2 == 0 and V % 2 == 1
    m = (V - 1) // 2
    a = rng.choice(np.arange(1, N // 2), size=m, replace=False)
    return np.concatenate([[N // 2], a, N - a]).astype(np.int64)


def open_window(N: int, V: int, rng: np.random.Generator) -> np.ndarray:
    return rng.choice(N, size=V, replace=False).astype(np.int64)


def summarize(vals):
    v = np.asarray(vals, dtype=float)
    return dict(mean=float(v.mean()), sd=float(v.std(ddof=1)), min=float(v.min()),
                max=float(v.max()), n=len(v))


# --------------------------------------------------------------------------


def run_cell(name: str, n: int, modulus: int, a: int, b: int, N: int, k: int,
             sims: int, seed0: int, control_windows: int) -> dict:
    t0 = time.time()
    F = Field(n, modulus)
    C = Curve(F, a, b, N)
    out: dict = dict(cell=name, n=n, modulus_hex=hex(modulus), a=a, b=b, group_order=N,
                     window_bits_k=k)

    # --- instrument checks: the curve and the group law --------------------
    aff = C.count_affine_points()
    out["checks"] = dict(affine_points_counted=aff, affine_plus_infinity=aff + 1,
                         equals_group_order=(aff + 1 == N))
    assert aff + 1 == N, "curve does not have the stated order: wrong curve encoding"
    rng0 = np.random.default_rng(seed0)
    px_all, py_all = C.points_with_x(np.arange(1 << n))
    idx = rng0.choice(len(px_all), size=6, replace=False)
    ok_order = True
    for i in idx:
        P = (int(px_all[i]), int(py_all[i]))
        ok_order &= C.mul_scalar(N, P) is None
    out["checks"]["N_times_random_point_is_infinity_on_6_points"] = bool(ok_order)
    assert ok_order
    # vectorised x(P+Q) against the full scalar group law on 200 random pairs
    ii = rng0.choice(len(px_all), size=(200, 2))
    agree = True
    for i, j in ii:
        if px_all[i] == px_all[j]:
            continue
        S = C.add_scalar((int(px_all[i]), int(py_all[i])), (int(px_all[j]), int(py_all[j])))
        xs = int(C.sum_x(px_all[i:i + 1], py_all[i:i + 1], px_all[j:j + 1], py_all[j:j + 1])[0])
        agree &= (S is not None and S[0] == xs and
                  bool(C.on_curve(np.array([S[0]]), np.array([S[1]]))[0]))
    out["checks"]["vectorised_x_of_sum_matches_scalar_law_on_200_pairs"] = bool(agree)
    assert agree

    # --- 1. the reported census: prefix window deg(x) < k -------------------
    X = np.arange(1 << k)
    px, py = C.points_with_x(X)
    out["prefix_window_closed"] = curve_census(C, px, py, closed=True)

    # --- 1b. the producer's "aligned half" V'_0 = {P in V : constant term of x = 0} --
    # Reported ratio 8.37 (n=17).  Hypothesis tested here: V'_0 lies in the index-2
    # subgroup 2G, so every residual does too (confinement), a fact about parity in a
    # cyclic group of even order, not about the curve.  P in 2G iff (N/2) P = O.
    if name == "n17_RC1":
        sel = (px & 1) == 0
        ax, ay = px[sel], py[sel]
        half = N // 2
        in2G_even = [C.mul_scalar(half, (int(x), int(y))) is None for x, y in zip(ax, ay)]
        in2G_odd = [C.mul_scalar(half, (int(x), int(y))) is None
                    for x, y in zip(px[~sel], py[~sel])]
        cen = curve_census(C, ax, ay, closed=True)
        T0 = cen["T"]
        # residuals confined to a subgroup of order N/2: pairs of +-classes: collision
        # probability ~ 2/(N/2 - 1)
        p_conf = (2 * (N // 2) - 3) / ((N // 2) - 1) ** 2
        exp_non_conf = (T0 * (T0 - 1) / 2 - T0 / 2) * p_conf
        cen["V0_points_in_2G"] = int(sum(in2G_even))
        cen["V0_points"] = len(in2G_even)
        cen["complement_half_points_in_2G"] = int(sum(in2G_odd))
        cen["complement_half_points"] = len(in2G_odd)
        cen["expected_nontrivial_if_confined_to_2G"] = exp_non_conf
        cen["nontrivial_over_expected_if_confined"] = cen["nontrivial_collisions"] / exp_non_conf
        cen["predicted_reported_style_ratio_if_confined"] = (exp_non_conf + T0 // 2) / (
            T0 * T0 / (2 * N))
        # matched generic: negation-closed window inside the even residues, folded keys
        sims_conf = []
        for r in range(sims):
            rng = np.random.default_rng(seed0 + 3000 + r)
            m = (len(ax) - 1) // 2
            a_ = 2 * rng.choice(np.arange(1, N // 4), size=m, replace=False)  # even, < N/2
            w = np.concatenate([[N // 2], a_, N - a_]).astype(np.int64)
            sims_conf.append(generic_census(N, w, True)["reported_style_ratio"])
        cen["generic_confined_window_reported_style_ratio"] = summarize(sims_conf)
        cen["reported_by_producer_ratio"] = 8.37
        out["aligned_half_V0"] = cen

    # --- 2. matched generic simulations in Z/N -----------------------------
    V = len(px)
    N_ = N
    sim = {"closed_folded": [], "closed_unfolded": [], "open_folded": [], "open_unfolded": []}
    detail = []
    for r in range(sims):
        rng = np.random.default_rng(seed0 + 1000 + r)
        wc = closed_window(N_, V, rng)
        wo = open_window(N_, V, rng)
        c_cf = generic_census(N_, wc, True)
        c_cu = generic_census(N_, wc, False)
        c_of = generic_census(N_, wo, True)
        c_ou = generic_census(N_, wo, False)
        T = c_cf["T"]
        trivial = T // 2
        sim["closed_folded"].append(c_cf["reported_style_ratio"])
        sim["closed_unfolded"].append(c_cu["reported_style_ratio"])
        sim["open_folded"].append(c_of["reported_style_ratio"])
        sim["open_unfolded"].append(c_ou["reported_style_ratio"])
        detail.append(dict(seed=seed0 + 1000 + r, T_closed=T, T_open=c_of["T"],
                           closed_folded_combined=c_cf["combined"],
                           closed_folded_nontrivial=c_cf["combined"] - trivial,
                           closed_folded_trivial=trivial))
    nt = [d["closed_folded_nontrivial"] for d in detail]
    out["generic_matched_simulation"] = dict(
        replicates=sims, seeds=[d["seed"] for d in detail],
        ratio_closed_window_folded_key=summarize(sim["closed_folded"]),
        ratio_closed_window_unfolded_key=summarize(sim["closed_unfolded"]),
        ratio_open_window_folded_key=summarize(sim["open_folded"]),
        ratio_open_window_unfolded_key_producer_replica_style=summarize(sim["open_unfolded"]),
        closed_folded_nontrivial_collisions=summarize(nt),
        note=("closed = negation-closed window with one self-negative element; folded = key "
              "min(L,N-L) like x(L); open+unfolded is the producer's replica design"))
    nontriv_curve = out["prefix_window_closed"]["nontrivial_collisions"]
    s = out["generic_matched_simulation"]["closed_folded_nontrivial_collisions"]
    out["prefix_vs_matched_generic"] = dict(
        curve_nontrivial=nontriv_curve, generic_mean=s["mean"], generic_sd=s["sd"],
        z_score=(nontriv_curve - s["mean"]) / s["sd"],
        ratio_curve_to_generic_mean=nontriv_curve / s["mean"],
        curve_reported_style_ratio=out["prefix_window_closed"]["reported_style_ratio"],
        generic_matched_reported_style_ratio_mean=out["generic_matched_simulation"][
            "ratio_closed_window_folded_key"]["mean"])

    # --- 3. other curve windows of the same size (curve-side null) ---------
    wins = {}
    rngw = np.random.default_rng(seed0 + 5000)
    c_shift = int(rngw.integers(1 << k, 1 << n))
    wins["translated_prefix"] = np.arange(1 << k) ^ c_shift
    basis = [int(v) for v in rngw.integers(1, 1 << n, size=k)]
    span = np.zeros(1, dtype=np.int64)
    for v in basis:
        span = np.concatenate([span, span ^ v])
    wins["random_subspace_dim_k"] = np.unique(span)
    wins["random_xset_size_2^k"] = rngw.choice(1 << n, size=1 << k, replace=False)
    other = {}
    for nm, xs in wins.items():
        qx, qy = C.points_with_x(xs)
        other[nm] = curve_census(C, qx, qy, closed=True)
        other[nm]["window_description"] = nm
    out["other_curve_windows_closed"] = other
    ctrl = []
    for r in range(control_windows):
        rr = np.random.default_rng(seed0 + 9000 + r)
        xs = rr.choice(1 << n, size=1 << k, replace=False)
        qx, qy = C.points_with_x(xs)
        c = curve_census(C, qx, qy, closed=True)
        ctrl.append(dict(seed=seed0 + 9000 + r, window_size=c["window_size"], T=c["T"],
                         reported_style_ratio=c["reported_style_ratio"],
                         nontrivial_over_expected=c["nontrivial_over_expected"]))
    out["random_xset_windows"] = dict(
        windows=ctrl,
        nontrivial_over_expected=summarize([c["nontrivial_over_expected"] for c in ctrl]),
        reported_style_ratio=summarize([c["reported_style_ratio"] for c in ctrl]))

    # --- 4. attribution: one point per abscissa (no negation closure) ------
    # window of deg(x) < k+1 (about 2|V| points), then keep one point per abscissa:
    # about |V| points, no negation closure, keys still x(L)
    hx, hy = C.points_with_x(np.arange(1 << (k + 1)))
    keep = np.ones(len(hx), dtype=bool)
    keep[1:] = hx[1:] != hx[:-1]  # sorted by (x, y): keep the first point over each x
    out["one_sign_per_abscissa_window_deg_lt_k_plus_1"] = curve_census(
        C, hx[keep], hy[keep], closed=False)
    out["wall_seconds"] = time.time() - t0
    return out


CELLS = [
    # name, n, modulus, a, b, N, k
    dict(name="n17_RC1", n=17, modulus=(1 << 17) | (1 << 3) | 1, a=97044, b=126251,
         N=130412, k=9),
    dict(name="n19_koblitz", n=19, modulus=0x80027, a=0, b=1, N=523492, k=10),
]


def summary_text(res: dict) -> str:
    """Plain-text table of the headline numbers (also printed to stdout)."""
    L = []
    for c in res["cells"]:
        p = c["prefix_window_closed"]
        g = c["generic_matched_simulation"]
        L.append(f"== {c['cell']}: GF(2^{c['n']}), modulus {c['modulus_hex']}, a={c['a']}, "
                 f"b={c['b']}, #E={c['group_order']}, prefix window deg(x)<{c['window_bits_k']}")
        L.append(f"   checks: affine points + 1 = {c['checks']['affine_plus_infinity']} "
                 f"(= #E: {c['checks']['equals_group_order']}); N*P = O on 6 random points: "
                 f"{c['checks']['N_times_random_point_is_infinity_on_6_points']}; vectorised "
                 f"x(P+Q) = scalar law on 200 pairs: "
                 f"{c['checks']['vectorised_x_of_sum_matches_scalar_law_on_200_pairs']}")
        L.append(f"   reproduction of the producer's census: |V|={p['window_size']} T={p['T']} "
                 f"identity-sum pairs={p['identity_sum_pairs']} combined={p['combined']} "
                 f"distinct keys={p['distinct_keys']} max multiplicity={p['max_multiplicity']} "
                 f"reported-style ratio={p['reported_style_ratio']:.6f} S_fit={p['S_fit']:.2f}")
        L.append(f"   trivial partner collisions {{P,Q}} vs {{-P,-Q}}: {p['trivial_partner_collisions']} "
                 f"(= T/2 = {p['T'] // 2}; self-partner pairs {p['self_partner_pairs']})")
        L.append(f"   nontrivial collisions {p['nontrivial_collisions']} vs expected "
                 f"{p['expected_nontrivial_uniform']:.1f} (uniform sign-folded keys): ratio "
                 f"{p['nontrivial_over_expected']:.4f}; predicted reported-style ratio "
                 f"{p['predicted_reported_style_ratio_matched_null']:.4f} "
                 f"(2+N/T = {p['leading_order_prediction_2_plus_N_over_T']:.4f})")
        for k, lab in (("ratio_open_window_unfolded_key_producer_replica_style",
                        "generic, open window, unfolded key (producer's replica design)"),
                       ("ratio_closed_window_unfolded_key", "generic, negation-closed window, unfolded key"),
                       ("ratio_open_window_folded_key", "generic, open window, sign-folded key"),
                       ("ratio_closed_window_folded_key",
                        "generic, negation-closed window, sign-folded key (MATCHED)")):
            v = g[k]
            L.append(f"   {lab:<66} ratio {v['mean']:.4f} +/- {v['sd']:.4f} "
                     f"(min {v['min']:.4f}, max {v['max']:.4f}, {v['n']} windows)")
        m = c["prefix_vs_matched_generic"]
        L.append(f"   curve nontrivial {m['curve_nontrivial']} vs matched generic "
                 f"{m['generic_mean']:.1f} +/- {m['generic_sd']:.1f}: z = {m['z_score']:+.2f}, "
                 f"ratio {m['ratio_curve_to_generic_mean']:.4f}")
        for nm, v in c["other_curve_windows_closed"].items():
            L.append(f"   curve window {nm:<22} |V|={v['window_size']:<5} T={v['T']:<7} "
                     f"reported-style ratio {v['reported_style_ratio']:.4f} (predicted "
                     f"{v['predicted_reported_style_ratio_matched_null']:.4f}); nontrivial/expected "
                     f"{v['nontrivial_over_expected']:.4f}")
        r = c["random_xset_windows"]
        L.append(f"   {len(r['windows'])} random x-set windows of 2^k abscissae: nontrivial/expected "
                 f"{r['nontrivial_over_expected']['mean']:.4f} +/- {r['nontrivial_over_expected']['sd']:.4f} "
                 f"(min {r['nontrivial_over_expected']['min']:.4f}, max "
                 f"{r['nontrivial_over_expected']['max']:.4f}); reported-style ratio "
                 f"{r['reported_style_ratio']['mean']:.3f} (min {r['reported_style_ratio']['min']:.3f}, "
                 f"max {r['reported_style_ratio']['max']:.3f})")
        o = c["one_sign_per_abscissa_window_deg_lt_k_plus_1"]
        L.append(f"   curve, one point per abscissa (no negation closure), |V|={o['window_size']}: "
                 f"reported-style ratio {o['reported_style_ratio']:.4f}; combined/expected "
                 f"(sign-folded) {o['combined_over_expected_signfolded']:.4f}")
        if "aligned_half_V0" in c:
            a = c["aligned_half_V0"]
            L.append(f"   aligned half V'_0 (constant term of x = 0): |V|={a['window_size']} T={a['T']} "
                     f"combined={a['combined']} reported-style ratio {a['reported_style_ratio']:.4f} "
                     f"(producer 8.37); points in 2G: {a['V0_points_in_2G']}/{a['V0_points']}, "
                     f"complement half in 2G: {a['complement_half_points_in_2G']}/"
                     f"{a['complement_half_points']}; nontrivial/expected if confined to 2G "
                     f"{a['nontrivial_over_expected_if_confined']:.4f}; predicted "
                     f"{a['predicted_reported_style_ratio_if_confined']:.4f}; generic confined window "
                     f"{a['generic_confined_window_reported_style_ratio']['mean']:.3f} +/- "
                     f"{a['generic_confined_window_reported_style_ratio']['sd']:.3f}")
        L.append("")
    return "\n".join(L)


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", required=True)
    ap.add_argument("--sims", type=int, default=20)
    ap.add_argument("--control-windows", type=int, default=8)
    ap.add_argument("--seed", type=int, default=20261026)
    ap.add_argument("--cells", default="n17_RC1,n19_koblitz")
    args = ap.parse_args()
    res = dict(
        program=dict(file="matched_null_check.py",
                     sha256=hashlib.sha256(open(__file__, "rb").read()).hexdigest(),
                     python=platform.python_version(), numpy=np.__version__,
                     platform=platform.platform(), argv=sys.argv, seed=args.seed),
        cells=[])
    for c in CELLS:
        if c["name"] not in args.cells.split(","):
            continue
        res["cells"].append(run_cell(c["name"], c["n"], c["modulus"], c["a"], c["b"], c["N"],
                                     c["k"], args.sims, args.seed, args.control_windows))
    with open(args.out, "w") as fh:
        json.dump(res, fh, indent=1, sort_keys=True)
    print(summary_text(res))
    print(f"wrote {args.out}")
    return 0


if __name__ == "__main__":
    sys.exit(main())

#!/usr/bin/env python3
"""EXP-GFPN-05ff43 protocol v2 -- arm constructions.

Arms (m factor-base points, K = 2^{m-1}, target R with x_R = x(R)):

  raw / raw_x        S_{m+1}(x_1..x_m, x_R) in the x_i (box monomials, per-target grid).
  raw_u              S_{m+1}(lam u_1..lam u_m, x_R) in the u_i (box monomials, per-target grid);
                     the raw system on the RESCALED base (fixture F-1, F-2).
  identity           degenerate-symmetrisation control: the interpolation machinery with the
                     trivial group (box monomials in x); must equal raw_x exactly.
  S{m}               S_{m+1} written in e_1..e_m of x_1..x_m (total degree <= K), X symbolic.
  S{m}_rescaled      the same written in e(u_1..u_m), x_i = lam u_i (amendment DC-2 P-5, T-2).
  torsion_S{m}_rq    amendment DC-3 construction_torsion_S5_rq: unknowns sigma_k = e_k(t'),
                     t'_i = u_i + beta/u_i, and w = prod_i (u_i - beta/u_i); relation function
                     L(u) = S_{m+1}(lam u; X) / prod_i u_i^{K/2} = A(sigma) + w B(sigma), with
                     A of sigma-degree <= K/2 and B of sigma-degree <= K/2 - 1, plus the equation
                     w^2 - prod_i (t'_i^2 - 4 beta) = 0 written in sigma. Group (Z/2)^{m-1} x| S_m,
                     order 2^{m-1} m!.
  torsion_S{m}_norm  the v1 construction (v1 symmetrize.py rhs_arm_T), KEPT AS A LABELLED NEGATIVE
                     CONTROL: Q = s(x; X) s(x^{(1)}; X) in e(t), t = x + b/x, t_R = X + b/X.
                     Group (Z/2)^m x| S_m, order 2^m m! (CORR-20260923-064d0d). Never reported
                     with order 2^{m-1} m!.

Rescaling (DC-3 definition.rescaling): beta in F_p^* is the SMALLEST NON-SQUARE mod p (the
default the amendment names), lam = sqrt(b/beta) in F_q with a recorded, solver-independent root
choice (lexicographically smaller coefficient vector). (beta, lam) is a function of (curve, p')
only and is computed before any target exists. A curve without T = (0,0) rational refuses with
"no rational 2-torsion"; at odd n a curve whose b is a square in F_q refuses with
"b-square class mismatch" (DC-6 R-6). Refusals are values, never exceptions.
"""
import itertools
import math
import time

import flint
import numpy as np

from v2_field import S_poly, S_poly_grp, S_num_res, poly_eval

POOL_LIMIT_DEFAULT = 4000


# ----------------------------------------------------------------------------- arm ids
def parse_arm(arm_id):
    """Return (kind, m) for an arm id. kinds: raw_x, raw_u, identity, S, S_rescaled, rq, norm."""
    if arm_id in ("raw", "raw_x"):
        return "raw_x", None
    if arm_id == "raw_u":
        return "raw_u", None
    if arm_id == "identity":
        return "identity", None
    if arm_id.startswith("torsion_S") and arm_id.endswith("_rq"):
        return "rq", int(arm_id[len("torsion_S"):-len("_rq")])
    if arm_id.startswith("torsion_S") and arm_id.endswith("_norm"):
        return "norm", int(arm_id[len("torsion_S"):-len("_norm")])
    if arm_id.startswith("S") and arm_id.endswith("_rescaled"):
        return "S_rescaled", int(arm_id[1:-len("_rescaled")])
    if arm_id.startswith("S") and arm_id[1:].isdigit():
        return "S", int(arm_id[1:])
    raise ValueError("unknown arm id %r" % arm_id)


def group_order(kind, m):
    """|G| per arm (DC-2 hard_coded_constants replacement)."""
    if kind in ("raw_x", "raw_u", "identity"):
        return 1
    if kind in ("S", "S_rescaled"):
        return math.factorial(m)
    if kind == "rq":
        return 2 ** (m - 1) * math.factorial(m)
    if kind == "norm":
        return 2 ** m * math.factorial(m)
    raise ValueError(kind)


def group_label(kind, m):
    return {"raw_x": "trivial", "raw_u": "trivial", "identity": "trivial",
            "S": "S_%d" % m, "S_rescaled": "S_%d" % m,
            "rq": "(Z/2)^%d x| S_%d" % (m - 1, m),
            "norm": "(Z/2)^%d x| S_%d" % (m, m)}[kind]


def base_of(kind):
    """Which factor base the arm uses."""
    return {"raw_x": "x_in_Fp", "identity": "x_in_Fp", "S": "x_in_Fp",
            "raw_u": "x_over_lam_in_Fp", "S_rescaled": "x_over_lam_in_Fp", "rq": "x_over_lam_in_Fp",
            "norm": "x_plus_b_over_x_in_Fp"}[kind]


def varnames(kind, m):
    if kind in ("raw_x", "identity"):
        return ["x%d" % (i + 1) for i in range(m)]
    if kind == "raw_u":
        return ["u%d" % (i + 1) for i in range(m)]
    if kind in ("S", "S_rescaled", "norm"):
        return ["e%d" % (i + 1) for i in range(m)]
    if kind == "rq":
        return ["s%d" % (i + 1) for i in range(m)] + ["w"]
    raise ValueError(kind)


# ----------------------------------------------------------------------------- F_p helpers
def legendre(a, p):
    a %= p
    if a == 0:
        return 0
    return 1 if pow(a, (p - 1) // 2, p) == 1 else -1


def smallest_nonsquare(p):
    return next(b for b in range(2, p) if legendre(b, p) == -1)


def elem_sym(vals, p):
    e = [1] + [0] * len(vals)
    for v in vals:
        for k in range(len(vals), 0, -1):
            e[k] = (e[k] + e[k - 1] * v) % p
    return e[1:]


def monomials_total(nvars, maxdeg):
    out = []
    for d in range(maxdeg + 1):
        for a in itertools.product(range(d + 1), repeat=nvars):
            if sum(a) == d:
                out.append(tuple(a))
    return out


def monomials_box(nvars, maxdeg):
    return [tuple(a) for a in itertools.product(range(maxdeg + 1), repeat=nvars)]


def monomials_for(kind, m):
    K = 2 ** (m - 1)
    if kind in ("raw_x", "raw_u", "identity"):
        return monomials_box(m, K)
    if kind in ("S", "S_rescaled", "norm"):
        return monomials_total(m, K)
    if kind == "rq":
        A = [a + (0,) for a in monomials_total(m, K // 2)]
        B = [a + (1,) for a in monomials_total(m, K // 2 - 1)] if K // 2 - 1 >= 0 else []
        return A + B
    raise ValueError(kind)


# ----------------------------------------------------------------------------- rescaling
def two_torsion_status(E):
    has = E.has_rational_2torsion()
    at_origin = (E.a6 == 0)
    return has, at_origin


def rescaling(E, beta_override=None, beta_policy="smallest_nonsquare"):
    """(beta, lam) for the curve, or a refusal dict. Never raises for a refusal."""
    F = E.F
    p, n = F.p, F.n
    has, at_origin = two_torsion_status(E)
    if not has:
        return {"refused": True, "reason": "no rational 2-torsion"}
    if not at_origin:
        return {"refused": True, "reason": "no rational 2-torsion at (0,0) (model not supported by DC-3)"}
    b = E.a4
    b_sq = F.is_square(b)
    if beta_override is None:
        beta = smallest_nonsquare(p)
        policy = beta_policy
    else:
        beta = int(beta_override) % p
        policy = "override"
    if n % 2 == 1:
        if b_sq:
            return {"refused": True, "reason": "b-square class mismatch",
                    "detail": "b is a square in F_q; DC-3 requires b a non-square (EcGFp5 class) at odd n"}
        if legendre(beta, p) != -1:
            return {"refused": True, "reason": "beta is not a non-square in F_p (DC-3 requires a non-square at odd n)"}
    lam2 = b / F(beta)
    lam = F.canonical_sqrt(lam2)
    if lam is None:
        return {"refused": True, "reason": "b-square class mismatch", "detail": "b/beta is not a square in F_q"}
    assert lam * lam * F(beta) == b
    return {"refused": False, "beta": beta, "beta_policy": policy, "beta_is_nonsquare_in_Fp": legendre(beta, p) == -1,
            "lam": F.coeffs(lam), "lam_root_choice": "the root of lam^2 = b/beta with the lexicographically smaller coefficient vector [c0..c_{n-1}]",
            "b_is_square_in_Fq": bool(b_sq), "lam_obj": lam}


def public_rescaling(r):
    return {k: v for k, v in r.items() if k != "lam_obj"}


# ----------------------------------------------------------------------------- pools
def pool_x(E, limit):
    F = E.F
    out = []
    for x in range(1, F.p):
        if E.f(F(x)).is_square():
            out.append(x)
            if len(out) >= limit:
                break
    return out


def pool_u(E, lam, limit):
    F = E.F
    out = []
    for u in range(1, F.p):
        if E.f(lam * F(u)).is_square():
            out.append(u)
            if len(out) >= limit:
                break
    return out


def pool_t(E, limit):
    """t in F_p such that X^2 - t X + b splits in F_q with a nonzero root x that lifts (v1 rule)."""
    F = E.F
    b = E.a4
    out = {}
    for t in range(1, F.p):
        tt = F(t)
        disc = tt * tt - 4 * b
        if not disc.is_square():
            continue
        x = (tt + disc.sqrt()) / 2
        if x == 0:
            continue
        if E.f(x).is_square():
            out[t] = x
            if len(out) >= limit:
                break
    return out


# ----------------------------------------------------------------------------- relation functions
def laurent_to_tR(F, cs, b):
    """v1 routine: Laurent polynomial c_{-K}..c_{K} invariant under X -> b/X -> polynomial in X + b/X."""
    K = (len(cs) - 1) // 2
    bk = F.one
    for k in range(1, K + 1):
        bk = bk * b
        assert cs[K - k] == bk * cs[K + k], "Laurent coefficients not X->b/X invariant"
    u_prev = [2 * F.one]
    u_cur = [F.zero, F.one]
    out = [F.zero] * (K + 1)
    out[0] += cs[K]
    for k in range(1, K + 1):
        for i, c in enumerate(u_cur):
            out[i] += cs[K + k] * c
        nxt = [F.zero] * (len(u_cur) + 1)
        for i, c in enumerate(u_cur):
            nxt[i + 1] += c
        for i, c in enumerate(u_prev):
            nxt[i] -= b * c
        u_prev, u_cur = u_cur, nxt
    return out


def rf_norm_from_x(E, xs):
    """v1 negative-control relation function from F_q x-values (points must lift)."""
    F = E.F
    b = E.a4
    m = len(xs)
    K = 2 ** (m - 1)
    h = K // 2
    pts = [E.lift_x(x) for x in xs]
    if any(P is None for P in pts):
        raise ValueError("norm relation function needs liftable x")
    T = (F.zero, F.zero)
    s1 = S_poly_grp(E, pts)
    pts2 = [E.add(pts[0], T)] + pts[1:]
    s2 = S_poly_grp(E, pts2)
    prod = [F.zero] * (2 * K + 1)
    for i, a in enumerate(s1):
        if a == 0:
            continue
        for j, c in enumerate(s2):
            prod[i + j] += a * c
    px = F.one
    for P in pts:
        px = px * P[0]
    px2 = b / pts[0][0]
    for P in pts[1:]:
        px2 = px2 * P[0]
    norm = (px * px2) ** h
    cs = [c / norm for c in prod]
    return laurent_to_tR(F, cs, b)


def relation_function(kind, E, rs, coords):
    """Coefficient list (in X, or in t_R for norm) of the arm's relation function at a sample
    tuple of base coordinates (F_p ints, or F_q elements for flipped test points)."""
    F = E.F
    m = len(coords)
    K = 2 ** (m - 1)
    if kind in ("raw_x", "identity", "S"):
        return S_poly(E, [F(c) if not hasattr(c, "to_list") else c for c in coords])
    if kind in ("raw_u", "S_rescaled", "rq"):
        lam = rs["lam_obj"]
        us = [F(c) if not hasattr(c, "to_list") else c for c in coords]
        cs = S_poly(E, [lam * u for u in us])
        if kind != "rq":
            return cs
        den = F.one
        for u in us:
            den = den * u ** (K // 2)
        return [c / den for c in cs]
    if kind == "norm":
        return rf_norm_from_x(E, coords)
    raise ValueError(kind)


def invariant_row(kind, coords, p, beta=None):
    """Invariant coordinates (the arm's variables) of an F_p sample tuple."""
    if kind in ("raw_x", "raw_u", "identity"):
        return [int(c) % p for c in coords]
    if kind in ("S", "S_rescaled"):
        return elem_sym([int(c) for c in coords], p)
    if kind == "rq":
        ts, w = [], 1
        for u in coords:
            ui = pow(int(u), -1, p)
            ts.append((int(u) + beta * ui) % p)
            w = w * ((int(u) - beta * ui) % p) % p
        return elem_sym(ts, p) + [w]
    raise ValueError(kind)


def invariant_row_Fq(kind, coords_q, F, beta=None):
    """Same invariants evaluated at F_q points (used by the single-flip test at flipped points)."""
    if kind in ("raw_x", "raw_u", "identity"):
        return list(coords_q)
    if kind in ("S", "S_rescaled", "norm"):
        e = [F.one] + [F.zero] * len(coords_q)
        for v in coords_q:
            for k in range(len(coords_q), 0, -1):
                e[k] = e[k] + e[k - 1] * v
        return e[1:]
    if kind == "rq":
        ts, w = [], F.one
        for u in coords_q:
            ts.append(u + F(beta) / u)
            w = w * (u - F(beta) / u)
        return invariant_row_Fq("S", ts, F) + [w]
    raise ValueError(kind)


# ----------------------------------------------------------------------------- numpy helpers
def eval_monomials_rows(points, monos, p):
    A = np.array(monos, dtype=np.int64)
    nvars = A.shape[1]
    maxd = int(A.max()) if A.size else 0
    out = np.empty((len(points), len(monos)), dtype=np.int64)
    for r, pt in enumerate(points):
        pw = np.empty((nvars, maxd + 1), dtype=np.int64)
        for j in range(nvars):
            v = int(pt[j]) % p
            row = [1]
            for _ in range(maxd):
                row.append(row[-1] * v % p)
            pw[j] = row
        acc = np.ones(len(monos), dtype=np.int64)
        for j in range(nvars):
            acc = acc * pw[j][A[:, j]] % p
        out[r] = acc
    return out


def fq_mul_rows(Arows, v, F):
    """Multiply each row (n F_p coefficients) by the F_q element with coefficients v, reduce mod M."""
    p, n, M = F.p, F.n, F.modulus
    prod = np.zeros((Arows.shape[0], 2 * n - 1), dtype=np.int64)
    for i in range(n):
        if v[i]:
            prod[:, i:i + n] = (prod[:, i:i + n] + Arows * int(v[i])) % p
    for k in range(2 * n - 2, n - 1, -1):
        c = prod[:, k].copy()
        if not c.any():
            continue
        for i in range(n):
            if M[i]:
                prod[:, k - n + i] = (prod[:, k - n + i] - c * M[i]) % p
        prod[:, k] = 0
    return prod[:, :n] % p


# ----------------------------------------------------------------------------- the arm polynomial
class ArmPolynomial:
    """Interpolated arm polynomial: C[k, i, j] = z^j-component of the F_q coefficient of
    (target coordinate)^k * monos[i]."""

    def __init__(self, kind, m, monos, F, C, meta):
        self.kind, self.m, self.monos, self.F, self.C, self.meta = kind, m, monos, F, C, meta

    def specialise(self, val, counter=None):
        F = self.F
        K1 = self.C.shape[0]
        vc = F.coeffs(val)
        acc = self.C[K1 - 1].copy()
        for k in range(K1 - 2, -1, -1):
            acc = fq_mul_rows(acc, vc, F)
            acc = (acc + self.C[k]) % F.p
            if counter is not None:
                counter.fq_mul += acc.shape[0]
                counter.fq_add += acc.shape[0]
        return acc

    def eval_at_invariants_Fq(self, inv_q, target_part=None):
        """Evaluate at F_q invariants; returns list of K+1 F_q coefficients (in the target coordinate).
        target_part in (None, 'A', 'B') selects the w^0 or w^1 part (rq only; B is returned WITHOUT w)."""
        F = self.F
        out = []
        powcache = {}

        def pw(j, e):
            key = (j, e)
            if key not in powcache:
                powcache[key] = inv_q[j] ** e
            return powcache[key]

        mono_vals = []
        for a in self.monos:
            if target_part is not None:
                if (target_part == "A" and a[-1] != 0) or (target_part == "B" and a[-1] != 1):
                    mono_vals.append(None)
                    continue
                a = a[:-1]
            v = F.one
            for j, e in enumerate(a):
                if e:
                    v = v * pw(j, e)
            mono_vals.append(v)
        for k in range(self.C.shape[0]):
            s = F.zero
            for i, mv in enumerate(mono_vals):
                if mv is None:
                    continue
                cf = self.C[k, i]
                if cf.any():
                    s = s + F.from_coeffs(cf.tolist()) * mv
            out.append(s)
        return out


def build_arm_polynomial(kind, m, E, rs, pool, rng, extra_rows=64, holdout=32, log=print):
    """Exact interpolation with held-out verification (v1 machinery, generalised)."""
    F = E.F
    p, n = F.p, F.n
    K = 2 ** (m - 1)
    monos = monomials_for(kind, m)
    N = len(monos)
    npts = N + extra_rows + holdout
    beta = rs["beta"] if rs else None
    pool_list = sorted(pool) if isinstance(pool, dict) else list(pool)
    log("[build] kind=%s m=%d p=%d n=%d N=%d samples=%d" % (kind, m, p, n, N, npts))
    resamples = 0
    while True:
        try:
            return _build_once(kind, m, E, rs, pool, rng, N, npts, monos, K, pool_list, beta, resamples, log)
        except ZeroDivisionError as e:
            if "singular" not in str(e) or resamples >= 3:
                raise
            resamples += 1
            log("[build] interpolation matrix singular; deterministic resample %d from the same seeded stream" % resamples)


def _build_once(kind, m, E, rs, pool, rng, N, npts, monos, K, pool_list, beta, resamples, log):
    F = E.F
    p, n = F.p, F.n
    t0 = time.time()
    samples, rhs, inv = [], [], []
    seen = set()
    while len(samples) < npts:
        sel = rng.sample(pool_list, m)
        key = tuple(sorted(sel))
        if key in seen:            # a repeated sample subset would duplicate an interpolation row
            continue
        seen.add(key)
        coords = [pool[t] for t in sel] if kind == "norm" else sel
        try:
            val = relation_function(kind, E, rs, coords)
        except ZeroDivisionError:
            continue
        samples.append(sel)
        rhs.append(val)
        inv.append(elem_sym(sel, p) if kind == "norm" else invariant_row(kind, sel, p, beta))
    t_eval = time.time() - t0
    t1 = time.time()
    Msq = flint.nmod_mat(N, N, p)
    for r0 in range(0, N, 256):
        blk = eval_monomials_rows(inv[r0:min(N, r0 + 256)], monos, p)
        for i in range(blk.shape[0]):
            row = blk[i].tolist()
            for j, v in enumerate(row):
                if v:
                    Msq[r0 + i, j] = v
        del blk
    ncol = (K + 1) * n
    Bsq = flint.nmod_mat(N, ncol, p)
    for r in range(N):
        for k in range(K + 1):
            cs = F.coeffs(rhs[r][k])
            for j in range(n):
                if cs[j]:
                    Bsq[r, k * n + j] = cs[j]
    t2 = time.time()
    Xs = Msq.solve(Bsq)
    del Msq, Bsq
    t_solve = time.time() - t2
    C = np.zeros((K + 1, N, n), dtype=np.int64)
    for i in range(N):
        for c in range(ncol):
            v = int(Xs[i, c])
            if v:
                C[c // n, i, c % n] = v
    del Xs
    bad = 0
    Mrest = eval_monomials_rows(inv[N:], monos, p)
    for r in range(N, npts):
        row = Mrest[r - N]
        for k in range(K + 1):
            want = F.coeffs(rhs[r][k])
            for j in range(n):
                if int((row * C[k, :, j] % p).sum() % p) != want[j]:
                    bad += 1
    support_idx = [i for i in range(N) if C[:, i, :].any()]
    support = [monos[i] for i in support_idx]
    meta = {"kind": kind, "m": m, "p": p, "n": n, "N_basis_monomials": N,
            "support_nonzero_monomials": len(support),
            "support_total_degree": max((sum(a) for a in support), default=None),
            "deg_in_target_coordinate": K, "sample_points": npts, "held_out_rows": npts - N,
            "held_out_mismatches": bad, "seconds_eval": round(t_eval, 2), "seconds_matrix": round(t2 - t1, 2),
            "seconds_solve": round(t_solve, 2), "pool_size": len(pool_list),
            "varnames": varnames(kind, m), "group": group_label(kind, m), "group_order": group_order(kind, m),
            "interpolation_resamples": resamples}
    if kind == "rq":
        A_sup = [a for a in support if a[-1] == 0]
        B_sup = [a for a in support if a[-1] == 1]
        meta["deg_A_sigma"] = max((sum(a[:-1]) for a in A_sup), default=None)
        meta["deg_B_sigma"] = max((sum(a[:-1]) for a in B_sup), default=None)
        meta["n_monomials_A"] = len(A_sup)
        meta["n_monomials_B"] = len(B_sup)
        meta["n_monomials_A_plus_wB"] = len(support)
    pol = ArmPolynomial(kind, m, monos, F, C, meta)
    pol.support = support
    return pol


# ----------------------------------------------------------------------------- single-flip test
def single_flip_test(pol, E, rs, pool, rng, n_points=12):
    """Amendment DC-3 observation_collision (1): numeric single-flip test on the built polynomial.

    For u-based arms the flip is u_1 -> beta/u_1; for x-based arms x_1 -> b/x_1; for the norm arm
    the flip acts on the x-coordinate behind t_1 (x_1 -> b/x_1, i.e. P_1 -> P_1 + T).
      rq   : PASS iff at every point L(u) = A + wB, L(flip u) = A - wB, the even flip
             (u_1, u_2) -> (beta/u_1, beta/u_2) leaves L unchanged, and L changes under the single
             flip at >= 1 point (so B is not identically zero on the sample).
      norm : PASS iff the relation function is unchanged by the single flip at every point and the
             interpolated polynomial reproduces it.
      other: exactness at fresh points is required; the flip behaviour is recorded, not scored.
    """
    kind, m = pol.kind, pol.m
    F = E.F
    beta = rs["beta"] if rs else None
    b = E.a4
    pool_list = sorted(pool) if isinstance(pool, dict) else list(pool)
    rows = []
    for _ in range(n_points):
        sel = rng.sample(pool_list, m)
        if kind == "norm":
            xs = [pool[t] for t in sel]
            base = rf_norm_from_x(E, xs)
            flipped = rf_norm_from_x(E, [b / xs[0]] + xs[1:])
            interp = pol.eval_at_invariants_Fq(invariant_row_Fq("norm", [F(t) for t in sel], F))
            rows.append({"exact_at_point": interp == base, "invariant_under_single_flip": flipped == base})
            continue
        q = [F(c) for c in sel]
        if kind in ("raw_u", "S_rescaled", "rq"):
            qf = [F(beta) / q[0]] + q[1:]
            qe = ([F(beta) / q[0], F(beta) / q[1]] + q[2:]) if m >= 2 else None
        else:
            qf = [b / q[0]] + q[1:]
            qe = ([b / q[0], b / q[1]] + q[2:]) if m >= 2 else None
        base = relation_function(kind, E, rs, q)
        flipped = relation_function(kind, E, rs, qf)
        row = {"invariant_under_single_flip": flipped == base}
        if kind == "rq":
            inv_q = invariant_row_Fq("rq", q, F, beta)
            w = inv_q[-1]
            A = pol.eval_at_invariants_Fq(inv_q, "A")
            B = pol.eval_at_invariants_Fq(inv_q, "B")
            row["equals_A_plus_wB"] = all(base[k] == A[k] + w * B[k] for k in range(len(base)))
            row["flip_equals_A_minus_wB"] = all(flipped[k] == A[k] - w * B[k] for k in range(len(base)))
            even = relation_function(kind, E, rs, qe) if qe else None
            row["invariant_under_even_flip"] = (even == base) if even is not None else None
            row["exact_at_point"] = row["equals_A_plus_wB"]
        else:
            interp = pol.eval_at_invariants_Fq(invariant_row_Fq(kind, q, F, beta))
            row["exact_at_point"] = interp == base
        rows.append(row)
    if kind == "rq":
        ok = (all(r["equals_A_plus_wB"] and r["flip_equals_A_minus_wB"] and r["invariant_under_even_flip"] is not False for r in rows)
              and any(not r["invariant_under_single_flip"] for r in rows))
        rule = "rq: L = A + wB, L(flip) = A - wB, even-flip invariant, and L changes under a single flip"
    elif kind == "norm":
        ok = all(r["exact_at_point"] and r["invariant_under_single_flip"] for r in rows)
        rule = "norm: invariant under the single flip and exact at fresh points"
    else:
        ok = all(r["exact_at_point"] for r in rows)
        rule = "exact at fresh points (flip behaviour recorded, not scored for this arm)"
    return {"pass": bool(ok), "rule": rule, "n_points": n_points,
            "n_invariant_under_single_flip": sum(bool(r["invariant_under_single_flip"]) for r in rows),
            "rows": rows}


# ----------------------------------------------------------------------------- rq relation equation
def rq_relation_equation(m, beta, p):
    """w^2 - prod_i (t'_i^2 - 4 beta) as {exponent tuple over (s1..sm, w): coeff mod p}.
    prod_i (t_i^2 - 4 beta) = P(y) P(-y) at y^2 = 4 beta, P(y) = sum_k (-1)^k s_k y^{m-k}."""
    def P(sign):
        out = {}
        for k in range(m + 1):
            e = [0] * m
            if k:
                e[k - 1] = 1
            yk = m - k
            c = ((-1) ** k) * (sign ** yk)
            key = (tuple(e), yk)
            out[key] = (out.get(key, 0) + c) % p
        return out

    Pp, Pm = P(1), P(-1)
    prod = {}
    for (e1, y1), c1 in Pp.items():
        for (e2, y2), c2 in Pm.items():
            e = tuple(a + b for a, b in zip(e1, e2))
            key = (e, y1 + y2)
            prod[key] = (prod.get(key, 0) + c1 * c2) % p
    poly = {}
    for (e, yd), c in prod.items():
        if c == 0:
            continue
        assert yd % 2 == 0, "odd power of y survived"
        v = c * pow(4 * beta, yd // 2, p) % p
        key = e + (0,)
        poly[key] = (poly.get(key, 0) + v) % p
    eq = {k: (-v) % p for k, v in poly.items() if v % p}
    wkey = (0,) * m + (2,)
    eq[wkey] = (eq.get(wkey, 0) + 1) % p
    return {k: v for k, v in eq.items() if v}


def check_rq_relation_equation(m, beta, p, rng, trials=8):
    """Numeric check of rq_relation_equation at random t' values (validation helper)."""
    eq = rq_relation_equation(m, beta, p)
    for _ in range(trials):
        ts = [rng.randrange(p) for _ in range(m)]
        s = elem_sym(ts, p)
        prod = 1
        for t in ts:
            prod = prod * ((t * t - 4 * beta) % p) % p
        w2 = rng.randrange(p)
        # evaluate eq at (s, w) with w^2 = w2: value = w2 - prod(s) must match
        val = 0
        for e, c in eq.items():
            term = c
            for j in range(m):
                term = term * pow(s[j], e[j], p) % p
            term = term * (w2 if e[m] == 2 else 1) % p
            assert e[m] in (0, 2)
            val = (val + term) % p
        if val != (w2 - prod) % p:
            return False
    return True


# ----------------------------------------------------------------------------- descent
def descend(coeffs, monos, n, p):
    """F_q coefficient rows (N x n) -> n F_p equations {mono: coeff}."""
    eqs = []
    for j in range(n):
        eq = {}
        col = coeffs[:, j]
        nz = np.nonzero(col)[0]
        for i in nz.tolist():
            eq[monos[i]] = int(col[i]) % p
        eqs.append(eq)
    return eqs


def write_msolve_input(path, names, p, eqs):
    """Write msolve input; identically-zero equations are dropped and counted."""
    lines = [",".join(names), str(p)]
    body, dropped, nterms = [], 0, 0
    for eq in eqs:
        terms = []
        for a, c in sorted(eq.items(), key=lambda kv: (-sum(kv[0]), kv[0])):
            if c == 0:
                continue
            mono = "*".join((f"{v}^{e}" if e > 1 else v) for v, e in zip(names, a) if e > 0)
            terms.append(f"{c}*{mono}" if mono else f"{c}")
        if not terms:
            dropped += 1
            continue
        nterms += len(terms)
        body.append("+".join(terms))
    with open(path, "w") as fh:
        fh.write("\n".join(lines) + "\n" + ",\n".join(body) + "\n")
    return {"n_equations": len(body), "n_zero_equations_dropped": dropped, "n_terms": nterms,
            "union_support": len({a for eq in eqs for a, c in eq.items() if c})}


def system_for_target(pol, target_val, rs, counter=None):
    """Specialise, descend and (for rq) append the relation equation. Returns (names, eqs)."""
    F = pol.F
    sp = pol.specialise(target_val, counter)
    eqs = descend(sp, pol.monos, F.n, F.p)
    if counter is not None:
        counter.fp_mul += 0      # descent is a coefficient split: no multiplications
    if pol.kind == "rq":
        eqs.append(rq_relation_equation(pol.m, rs["beta"], F.p))
    return varnames(pol.kind, pol.m), eqs


# ----------------------------------------------------------------------------- raw arms: per-target grid
def raw_system_at_target(kind, m, E, rs, x_R, nodes, counter=None, log=print):
    """S_{m+1}(coords, x_R) on box monomials by tensor-product grid interpolation.
    kind raw_x: coords are x_i; raw_u: coords are u_i with x_i = lam u_i.
    Returns (names, eqs, info). Every evaluation and the Vandermonde solves are charged."""
    F = E.F
    p, n = F.p, F.n
    K = 2 ** (m - 1)
    nn = K + 1
    assert len(nodes) == nn and len(set(nodes)) == nn
    lam = rs["lam_obj"] if kind == "raw_u" else None
    ctr = counter
    saved = E.counter
    E.counter = ctr
    vals = np.zeros([nn] * m + [n], dtype=np.int64)
    t0 = time.time()
    try:
        for idx in itertools.product(range(nn), repeat=m):
            cs = [F(nodes[i]) for i in idx]
            if lam is not None:
                cs = [lam * c for c in cs]
                if ctr is not None:
                    ctr.fq_mul += m
            if len(set(idx)) < m:
                v = S_num_res(E, cs + [x_R], ctr)
            else:
                v = poly_eval(S_poly(E, cs, ctr), x_R, ctr)
            vals[idx] = F.coeffs(v)
    finally:
        E.counter = saved
    V = flint.nmod_mat([[pow(x, k, p) for k in range(nn)] for x in nodes], p)
    Vinv = np.array([[int(V.inv()[i, j]) for j in range(nn)] for i in range(nn)], dtype=np.int64)
    if ctr is not None:
        ctr.fp_inv += nn
        ctr.fp_mul += nn ** 3
    C = vals
    for axis in range(m):
        C = np.moveaxis(C, axis, 0)
        shp = C.shape
        flat = C.reshape(nn, -1)
        new = np.zeros_like(flat)
        for k in range(nn):
            acc = np.zeros(flat.shape[1], dtype=np.int64)
            for nd in range(nn):
                if Vinv[k, nd]:
                    acc = (acc + flat[nd] * int(Vinv[k, nd])) % p
            new[k] = acc
        if ctr is not None:
            ctr.fp_mul += nn * nn * flat.shape[1]
        C = np.moveaxis(new.reshape(shp), 0, axis)
    monos = monomials_box(m, K)
    flat = C.reshape(-1, n)
    eqs = descend(flat, monos, n, p)
    info = {"grid_nodes": list(nodes), "grid_points": nn ** m, "seconds_grid": round(time.time() - t0, 3)}
    return varnames(kind, m), eqs, info, C


def raw_coefficients_equal_identity(C_raw, pol_identity, x_R):
    """degenerate_symmetrization_identity: identity-arm polynomial specialised at x_R equals the raw grid."""
    sp = pol_identity.specialise(x_R)
    m = pol_identity.m
    K = 2 ** (m - 1)
    return bool(np.array_equal(sp.reshape([K + 1] * m + [pol_identity.F.n]), C_raw))

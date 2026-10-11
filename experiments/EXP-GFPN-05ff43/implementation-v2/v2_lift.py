#!/usr/bin/env python3
"""EXP-GFPN-05ff43 protocol v2 -- lifting F_p-rational solutions to relations, and certificates.

Lifting per arm (amendment DC-3 definition.lifting for rq):
  raw_x      x = solution;                     raw_u  u = solution, x = lam u;
  S          x = roots of X^m - e1 X^{m-1} + ...;  S_rescaled  u = those roots, x = lam u;
  norm       t = roots, x = a root of X^2 - t X + b (v1 rule; P and P + T share t);
  rq         1. t'_i = roots of X^m - s1 X^{m-1} + ... + (-1)^m s_m, all in F_p, else reject;
             2. u_i from u^2 - t'_i u + beta = 0, both roots in F_p, else reject;
             3. flips u_i <-> beta/u_i with prod (u_i - beta/u_i) = w (unique up to G2; the
                lexicographically first matching assignment is used), else reject w_sign_inconsistent;
             4. x_i = lam u_i, y must exist in F_q, else reject;
             5. signs eps_i with sum eps_i P_i in {R, R + T}; R + T is flagged relation_mod_T.
Every step's rejection reason is recorded. Relations are DEDUPLICATED as signed-point multisets
(DC-6 R-3: one signed-point multiset is one relation).
"""
import itertools

import flint

from v2_arms import elem_sym, base_of


def _roots_with_mult(coeffs_low_high, p):
    rts = flint.nmod_poly(coeffs_low_high, p).roots()
    out = []
    for r, mult in rts:
        out += [int(r)] * int(mult)
    return out


def _poly_from_e(e, p):
    m = len(e)
    coeffs = [0] * (m + 1)
    coeffs[m] = 1
    for j in range(1, m + 1):
        coeffs[m - j] = ((-1) ** j) * e[j - 1] % p
    return coeffs


def _key(F, P):
    return (tuple(F.coeffs(P[0])), tuple(F.coeffs(P[1])))


def sign_search(E, pts, R, T=None, counter=None):
    """All distinct relations sum eps_i P_i == R (or == R + T when T is given)."""
    F = E.F
    saved = E.counter
    E.counter = counter
    RT = E.add(R, T) if T is not None else None
    seen, rels = set(), []
    try:
        for signs in itertools.product((1, -1), repeat=len(pts)):
            S = None
            signed = []
            for P, s in zip(pts, signs):
                Q = P if s == 1 else E.neg(P)
                signed.append(Q)
                S = E.add(S, Q)
            if S is None:
                continue
            flag = None
            if S == R:
                flag = False
            elif RT is not None and S == RT:
                flag = True
            if flag is None:
                continue
            key = tuple(sorted(_key(F, Q) for Q in signed))
            if key in seen:
                continue
            seen.add(key)
            rels.append({"points": list(pts), "signs": list(signs), "relation_mod_T": flag})
    finally:
        E.counter = saved
    return rels


def _lift_points(E, xs, counter):
    saved = E.counter
    E.counter = counter
    try:
        pts = []
        for x in xs:
            P = E.lift_x(x)
            if P is None:
                return None
            pts.append(P)
        return pts
    finally:
        E.counter = saved


def lift(kind, sol, E, rs, R, counter=None):
    """Return (relations, diag). Each relation carries points, signs, relation_mod_T and u_values."""
    F = E.F
    p = F.p
    m = len(sol) - 1 if kind == "rq" else len(sol)
    diag = {}
    T = (F.zero, F.zero) if kind in ("rq", "norm") else None
    lam = rs["lam_obj"] if rs else None
    beta = rs["beta"] if rs else None
    us = None
    if kind in ("raw_x", "identity"):
        xs = [F(v) for v in sol]
    elif kind == "raw_u":
        us = [int(v) % p for v in sol]
        if any(u == 0 for u in us):
            diag["reject"] = "u_i = 0"
            return [], diag
        xs = [lam * F(u) for u in us]
    elif kind in ("S", "S_rescaled"):
        roots = _roots_with_mult(_poly_from_e(sol, p), p)
        if counter is not None:
            counter.fp_mul += (m + 1) * m
        diag["n_roots_in_Fp"] = len(roots)
        if len(roots) != m:
            diag["reject"] = "polynomial in e does not split over F_p"
            return [], diag
        if kind == "S":
            xs = [F(r) for r in roots]
        else:
            us = roots
            if any(u == 0 for u in us):
                diag["reject"] = "u_i = 0"
                return [], diag
            xs = [lam * F(u) for u in us]
    elif kind == "norm":
        ts = _roots_with_mult(_poly_from_e(sol, p), p)
        diag["n_roots_in_Fp"] = len(ts)
        if len(ts) != m:
            diag["reject"] = "t-polynomial does not split over F_p"
            return [], diag
        xs = []
        b = E.a4
        for t in ts:
            tt = F(t)
            disc = tt * tt - 4 * b
            if counter is not None:
                counter.fq_mul += 2
                counter.fq_inv += 1
            if not disc.is_square():
                diag["reject"] = "t^2 - 4b not a square in F_q"
                return [], diag
            x = (tt + disc.sqrt()) / 2
            if x == 0:
                diag["reject"] = "x = 0"
                return [], diag
            xs.append(x)
    elif kind == "rq":
        sig, w = [int(v) % p for v in sol[:m]], int(sol[m]) % p
        tps = _roots_with_mult(_poly_from_e(sig, p), p)
        diag["n_t_roots_in_Fp"] = len(tps)
        if len(tps) != m:
            diag["reject"] = "step1: t' not all in F_p"
            return [], diag
        pairs = []
        for t in tps:
            r = _roots_with_mult([beta % p, (-t) % p, 1], p)
            if counter is not None:
                counter.fp_mul += 2
            if len(r) != 2:
                diag["reject"] = "step2: u^2 - t'u + beta has no two roots in F_p"
                return [], diag
            pairs.append(sorted(r))
        choice = None
        for pick in itertools.product((0, 1), repeat=m):
            cand = [pairs[i][pick[i]] for i in range(m)]
            prod = 1
            for u in cand:
                prod = prod * ((u - beta * pow(u, -1, p)) % p) % p
            if counter is not None:
                counter.fp_mul += 2 * m
                counter.fp_inv += m
            if prod == w:
                choice = cand
                break
        if choice is None:
            diag["reject"] = "w_sign_inconsistent"
            return [], diag
        us = choice
        xs = [lam * F(u) for u in us]
        if counter is not None:
            counter.fq_mul += m
    else:
        raise ValueError(kind)
    pts = _lift_points(E, xs, counter)
    if pts is None:
        diag["reject"] = "step4: y does not exist in F_q" if kind == "rq" else "x does not lift to a point over F_q"
        return [], diag
    rels = sign_search(E, pts, R, T, counter)
    for r in rels:
        r["u_values"] = list(us) if us is not None else None
    diag["n_relations"] = len(rels)
    diag["n_relation_mod_T"] = sum(1 for r in rels if r["relation_mod_T"])
    return rels, diag


# ----------------------------------------------------------------------------- orbit keys (F-2(b))
def g2_orbit_key_of_u(us, beta, p):
    """G2-orbit invariant of an F_p u-tuple (all u_i != 0, beta a non-square): (sigma(t'), w)."""
    ts = [(u + beta * pow(u, -1, p)) % p for u in us]
    w = 1
    for u in us:
        w = w * ((u - beta * pow(u, -1, p)) % p) % p
    return tuple(elem_sym(ts, p)), w


# ----------------------------------------------------------------------------- certificates
def make_certificate(F, cv, shape, arm, kind, m, rs, nsub, G, k, R, rel, run_id, target, index, target_kind, extra=None):
    fbk = base_of(kind)
    fb = {"kind": fbk}
    if fbk == "x_over_lam_in_Fp":
        fb.update({"beta": rs["beta"], "lam": F.coeffs(rs["lam_obj"]), "u_values": rel.get("u_values"),
                   "lam_root_choice": rs.get("lam_root_choice")})
    cert = {
        "schema": "crypto.autoresearch.decomposition_certificate.v2",
        "experiment_id": "EXP-GFPN-05ff43", "protocol_version": 2,
        "amendment_id": "AMD-EXP-GFPN-05ff43-20260923-reanchor-arm-iii",
        "run_id": run_id, "arm": arm, "m": m, "n": F.n, "curve_shape": shape, "p": F.p,
        "modulus": list(F.modulus),
        "field": "%s; elements are [c0..c%d] = c0 + c1 z + ..." % (F.describe(), F.n - 1),
        "curve": {"a2": _pad(cv["a2"], F.n), "a4": _pad(cv["a4"], F.n), "a6": _pad(cv["a6"], F.n),
                  "order": cv.get("order"), "cofactor": cv.get("cofactor")},
        "subgroup_order": int(nsub), "G": [F.coeffs(G[0]), F.coeffs(G[1])], "k": int(k),
        "R": [F.coeffs(R[0]), F.coeffs(R[1])], "known_scalar": True,
        "target_index": target, "relation_index": index, "target_kind": target_kind,
        "factor_base": fb,
        "points": [[F.coeffs(P[0]), F.coeffs(P[1])] for P in rel["points"]],
        "signs": list(rel["signs"]), "relation_mod_T": bool(rel["relation_mod_T"]),
        "statement": ("sum_i signs[i] * points[i] == R == [k]G (or == R + T when relation_mod_T), every point in the "
                      "arm's factor base; re-verified by v2_verify_independent.py (pure Python, no shared code)"),
    }
    if extra:
        cert.update(extra)
    return cert


def _pad(cs, n):
    cs = [int(c) for c in cs]
    return cs + [0] * (n - len(cs))

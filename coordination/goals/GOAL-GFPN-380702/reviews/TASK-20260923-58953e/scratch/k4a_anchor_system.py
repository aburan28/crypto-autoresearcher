#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
TASK-20260923-58953e, joint K4 (a) -- scratch invocation 1 of 3 (RC-3 (a)).

Independent re-derivation of the Joux-Vitse anchor system of RUN-GFPN-61bba9
(and of RUN-GFPN-bbed6f, same shape at p' = 65551) FROM THE CURVE COEFFICIENTS
RECORDED IN THOSE RUNS' MANIFESTS, with code written by this validator. It reads
no producer implementation module at run time and imports none.

What it computes, per curve:
  * Semaev's 5th summation polynomial S_5(x1,x2,x3,x4, X) for
    y^2 = x^3 + a x + b over F_q = F_p[z]/(z^5 - c), evaluated NUMERICALLY by
    Semaev's own recursion, using the closed-form resultant of two quadratics:
        S_3(u,v,w) = (u-v)^2 w^2 - 2((u+v)(uv+a)+2b) w + (uv-a)^2 - 4b(u+v)
        S_4(x1,x2,x3,U) = Res_T( S_3(x1,x2,T), S_3(x3,U,T) )
        S_5(x1,..,x4,X) = Res_U( S_4(x1,x2,x3,U), S_3(x4,X,U) )
    (formal degrees are asserted: 4 in U for S_4, 2 in U for S_3).
  * The S_4-symmetrised form Q_R(e1..e4) = S_5(x; x(R)) written in the
    elementary symmetric functions of x1..x4, by exact interpolation over F_p
    on the C(4+8,4) = 495 monomials of total degree <= 8, with held-out rows:
    a zero held-out mismatch count is the check that the symmetrised
    polynomial really has total degree <= 8 in e1..e4 (JV: "5 equations
    defined over Fp of total degree 8 in 4 variables").
  * Weil descent: the 5 z-components of Q_R -> 5 equations over F_p in
    e1..e4, written in msolve input format (same variable names and layout as
    the producer's descend_and_write, so the msolve logs are comparable).
  * A PLANTED control: R = P1+P2+P3+P4 with x(Pi) in F_p; the descended
    equations must vanish at e(x(P1..P4)) in F_p^4 and must not vanish at a
    random e.
  * A RANDOM target R (the anchor's object: JV's relation-search system for a
    random point), written for msolve -g 1 (invocations 2 and 3).
  * The Hilbert-series degree of regularity of a generic (semi-regular)
    system of 5 equations of degree 8 in 4 variables, for comparison with
    the highest F4 degree printed in the archived logs.
  * #E(F_q) by PARI SEA (via Sage), compared with the order in the manifest.
No solver is run here.
"""
import sys, os, json, time, hashlib, random, itertools

from sage.all import (GF, PolynomialRing, EllipticCurve, matrix, set_random_seed,
                      binomial)
try:
    from cysignals.alarm import alarm, cancel_alarm
    from cysignals.signals import AlarmInterrupt
except Exception:                      # order check then runs without an alarm
    def alarm(_s):
        return None

    def cancel_alarm():
        return None

    class AlarmInterrupt(Exception):
        pass

OUT = sys.argv[1]
os.makedirs(OUT, exist_ok=True)
T0 = time.time()
LOG = []


def log(*a):
    s = "%8.1fs " % (time.time() - T0) + " ".join(str(x) for x in a)
    print(s, flush=True)
    LOG.append(s)


# Curve coefficients copied from the archived manifests (inputs.parameters),
# lists are ascending coefficients of z^0..z^4.
CURVES = {
    "RUN-GFPN-61bba9": dict(
        p=16777291, cmod=2,
        a4=[9325376, 11721011, 8046041, 11531229, 5335856],
        a6=[11628446, 16321197, 11704219, 10318081, 12690816],
        order_manifest=1329257706611493025395407532399004523, tag="anchor25"),
    "RUN-GFPN-bbed6f": dict(
        p=65551, cmod=2,
        a4=[46177, 55794, 58975, 5913, 30430],
        a6=[55342, 21968, 2740, 31231, 60676],
        order_manifest=1210309958882862543130501, tag="anchor17"),
}

M_PTS = 4                     # m = 4 points (JV's (n-1)-point method, n = 5)
DEG = 8                       # 2^(m-1): total degree bound in e1..e4
MONOS = [a for d in range(DEG + 1)
         for a in itertools.product(range(d + 1), repeat=M_PTS) if sum(a) == d]
assert len(MONOS) == binomial(M_PTS + DEG, M_PTS) == 495
HELD_OUT = 40
VARS = ["e1", "e2", "e3", "e4"]


def dreg_semiregular(neq, deg, nvar, maxd=60):
    # coefficients of (1 - t^deg)^neq / (1 - t)^nvar; first index with coeff <= 0
    num = [0] * (maxd + 1)
    for k in range(neq + 1):
        if k * deg <= maxd:
            num[k * deg] += (-1) ** k * binomial(neq, k)
    coeffs = []
    for d in range(maxd + 1):
        coeffs.append(sum(num[i] * binomial(d - i + nvar - 1, nvar - 1)
                          for i in range(d + 1)))
    for d, c in enumerate(coeffs):
        if c <= 0:
            return d, [int(x) for x in coeffs[:d + 1]]
    return None, [int(x) for x in coeffs]


def elem_sym(xs, p):
    e = [1] + [0] * len(xs)
    for x in xs:
        for k in range(len(xs), 0, -1):
            e[k] = (e[k] + e[k - 1] * x) % p
    return e[1:]


def mono_row(e, p):
    pw = [[1] * (DEG + 1) for _ in range(M_PTS)]
    for i in range(M_PTS):
        for k in range(1, DEG + 1):
            pw[i][k] = pw[i][k - 1] * e[i] % p
    row = []
    for a in MONOS:
        v = 1
        for i in range(M_PTS):
            v = v * pw[i][a[i]] % p
        row.append(v)
    return row


def run_curve(label, cv, results):
    p, cmod = cv["p"], cv["cmod"]
    Fp = GF(p)
    PZ = PolynomialRing(Fp, "Zv")
    Zv = PZ.gen()
    modulus = Zv ** 5 - cmod
    irreducible = bool(modulus.is_irreducible())
    Fq = GF(p ** 5, "z", modulus=modulus)
    z = Fq.gen()

    def elt(cs):
        return sum(Fq(c) * z ** i for i, c in enumerate(cs))

    def comps(c):
        lst = [int(v) for v in c.polynomial().list()]
        return lst + [0] * (5 - len(lst))

    a, b = elt(cv["a4"]), elt(cv["a6"])
    E = EllipticCurve(Fq, [0, 0, 0, a, b])
    res = {"run": label, "p": p, "field": "F_%d[z]/(z^5 - %d)" % (p, cmod),
           "modulus_irreducible": irreducible, "curve": "y^2 = x^3 + a4 x + a6 (a4, a6 from manifest)",
           "j_invariant_nonsingular": True}
    log(label, "field and curve built; modulus irreducible:", irreducible)

    # --- order check against manifest (PARI SEA via Sage) ---------------------
    try:
        alarm(240)
        t = time.time()
        N = int(E.order())
        cancel_alarm()
        res["order_sage_sea"] = str(N)
        res["order_manifest"] = str(cv["order_manifest"])
        res["order_matches_manifest"] = (N == cv["order_manifest"])
        res["order_seconds"] = round(time.time() - t, 2)
        log(label, "order", N, "matches manifest:", N == cv["order_manifest"])
    except AlarmInterrupt:
        res["order_sage_sea"] = None
        res["order_note"] = "not computed: 240 s alarm fired (infrastructure, not evidence)"
        log(label, "order: alarm fired")
    except Exception as ex:
        cancel_alarm()
        res["order_sage_sea"] = None
        res["order_note"] = "not computed: %r" % (ex,)
        log(label, "order failed:", repr(ex))

    PU = PolynomialRing(Fq, "U")
    U = PU.gen()

    def s4_in_U(x1, x2, x3):
        # Res_T(f, g), f = S_3(x1,x2,T) in Fq[T], g = S_3(x3,U,T) in Fq[U][T]
        f2 = (x1 - x2) ** 2
        f1 = -2 * ((x1 + x2) * (x1 * x2 + a) + 2 * b)
        f0 = (x1 * x2 - a) ** 2 - 4 * b * (x1 + x2)
        g2 = (x3 - U) ** 2
        g1 = -2 * ((x3 + U) * (x3 * U + a) + 2 * b)
        g0 = (x3 * U - a) ** 2 - 4 * b * (x3 + U)
        return (f2 * g0 - f0 * g2) ** 2 - (f2 * g1 - f1 * g2) * (f1 * g0 - f0 * g1)

    def s3_in_U(x4, X):
        return ((x4 - X) ** 2 * U ** 2 - 2 * ((x4 + X) * (x4 * X + a) + 2 * b) * U
                + (x4 * X - a) ** 2 - 4 * b * (x4 + X))

    def S5(s4, x4, X):
        h = s3_in_U(x4, X)
        assert s4.degree() == 4 and h.degree() == 2, "formal degree dropped"
        return s4.resultant(h)

    # --- sanity: S_5 vanishes at a genuine 5-term relation -------------------
    rng = random.Random("TASK-20260923-58953e:K4a:%d" % p)
    set_random_seed(20260923 + p)

    def fb_point():
        while True:
            x = Fq(rng.randrange(p))
            rhs = x ** 3 + a * x + b
            if rhs != 0 and rhs.is_square():
                return E(x, rhs.sqrt())

    pts = [fb_point() for _ in range(M_PTS)]
    Rpl = sum(pts[1:], pts[0])
    assert not Rpl.is_zero()
    xs_pl = [P.xy()[0] for P in pts]
    xR_pl = Rpl.xy()[0]
    v_true = S5(s4_in_U(*xs_pl[:3]), xs_pl[3], xR_pl)
    # and not at a perturbed X
    v_false = S5(s4_in_U(*xs_pl[:3]), xs_pl[3], xR_pl + 1)
    res["S5_vanishes_at_genuine_relation"] = (v_true == 0)
    res["S5_nonzero_at_perturbed_X"] = (v_false != 0)
    log(label, "S5 at genuine relation == 0:", v_true == 0, "| at perturbed X != 0:", v_false != 0)

    # --- random target (anchor object) ---------------------------------------
    Rrand = E.random_point()
    while Rrand.is_zero():
        Rrand = E.random_point()
    xR_rand = Rrand.xy()[0]
    res["random_target_x_R"] = comps(xR_rand)
    res["planted_target_x_R"] = comps(xR_pl)
    res["planted_x_coordinates_in_Fp"] = [comps(x)[0] for x in xs_pl]

    # --- interpolation in e-space over F_p -----------------------------------
    npts = len(MONOS) + HELD_OUT
    rows, rhs_cols = [], []
    t = time.time()
    tries = 0
    while len(rows) < npts:
        tries += 1
        xs = [rng.randrange(p) for _ in range(M_PTS)]
        X4 = [Fq(x) for x in xs]
        s4 = s4_in_U(*X4[:3])
        if s4.degree() != 4 or X4[3] == xR_rand or X4[3] == xR_pl:
            continue
        vals = []
        for xR in (xR_rand, xR_pl):
            vals += comps(S5(s4, X4[3], xR))
        rows.append(mono_row(elem_sym(xs, p), p))
        rhs_cols.append(vals)
    log(label, "evaluated", npts, "sample points in %.1fs (%d draws)" % (time.time() - t, tries))
    Mfull = matrix(Fp, rows)
    Bfull = matrix(Fp, rhs_cols)
    Msq = Mfull[:len(MONOS)]
    rank = Msq.rank()
    res["interpolation_matrix_rank"] = int(rank)
    C = Msq.solve_right(Bfull[:len(MONOS)])
    held = Mfull[len(MONOS):] * C - Bfull[len(MONOS):]
    mism = sum(1 for i in range(held.nrows()) for j in range(held.ncols()) if held[i, j] != 0)
    res["held_out_rows"] = HELD_OUT
    res["held_out_mismatches"] = int(mism)
    log(label, "rank", rank, "held-out mismatches", mism)

    out = {}
    for ti, tname in enumerate(("random", "planted")):
        eqs = []
        for j in range(5):
            col = [int(C[i, 5 * ti + j]) for i in range(len(MONOS))]
            eqs.append(col)
        nterms = [sum(1 for c in col if c) for col in eqs]
        support = sorted({i for col in eqs for i, c in enumerate(col) if c})
        tdeg = [max((sum(MONOS[i]) for i, c in enumerate(col) if c), default=None) for col in eqs]
        # write msolve input
        lines = [",".join(VARS), str(p)]
        polys = []
        for col in eqs:
            terms = []
            for i, c in enumerate(col):
                if not c:
                    continue
                mono = "*".join((v + "^" + str(e)) if e > 1 else v for v, e in zip(VARS, MONOS[i]) if e > 0)
                terms.append("%d*%s" % (c, mono) if mono else "%d" % c)
            polys.append("+".join(terms) if terms else "0")
        fn = os.path.join(OUT, "%s_%s.ms" % (cv["tag"], tname))
        with open(fn, "w") as fh:
            fh.write("\n".join(lines) + "\n" + ",\n".join(polys) + "\n")
        sha = hashlib.sha256(open(fn, "rb").read()).hexdigest()
        info = {"file": os.path.basename(fn), "sha256": sha, "n_variables": 4, "n_equations": 5,
                "nonzero_terms_per_equation": nterms, "nonzero_terms_total": sum(nterms),
                "union_support_monomials": len(support), "total_degree_per_equation": tdeg}
        if tname == "planted":
            e_pl = elem_sym([comps(x)[0] for x in xs_pl], p)
            r_pl = mono_row(e_pl, p)
            vals_pl = [sum(c * r for c, r in zip(col, r_pl)) % p for col in eqs]
            e_rnd = [rng.randrange(p) for _ in range(4)]
            r_rnd = mono_row(e_rnd, p)
            vals_rnd = [sum(c * r for c, r in zip(col, r_rnd)) % p for col in eqs]
            info["planted_e"] = e_pl
            info["descended_equations_vanish_at_planted_e"] = all(v == 0 for v in vals_pl)
            info["descended_equations_nonzero_at_random_e"] = any(v != 0 for v in vals_rnd)
        out[tname] = info
        log(label, tname, json.dumps(info))
    res["systems"] = out
    results[label] = res


def main():
    results = {"task": "TASK-20260923-58953e", "joint": "K4 (a)", "invocation": 1,
               "script": os.path.basename(__file__),
               "script_sha256": hashlib.sha256(open(__file__, "rb").read()).hexdigest()}
    d, co = dreg_semiregular(5, 8, 4)
    results["generic_semiregular_5eq_deg8_4var"] = {"dreg": d, "hilbert_coeffs_to_dreg": co}
    log("semi-regular d_reg for 5 equations of degree 8 in 4 variables:", d)
    for label, cv in CURVES.items():
        try:
            run_curve(label, cv, results)
        except Exception as ex:
            import traceback
            results[label] = {"error": repr(ex), "traceback": traceback.format_exc()}
            log(label, "ERROR", repr(ex))
    results["wall_seconds"] = round(time.time() - T0, 1)
    results["log"] = LOG
    with open(os.path.join(OUT, "k4a_results.json"), "w") as fh:
        json.dump(results, fh, indent=1, default=str)
    log("done")


if __name__ == "__main__":
    main()

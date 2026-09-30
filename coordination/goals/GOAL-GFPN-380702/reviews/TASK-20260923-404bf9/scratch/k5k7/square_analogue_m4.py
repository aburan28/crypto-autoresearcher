#!/usr/bin/env sage-python
"""TASK-20260923-404bf9 (red team) -- K5 square analogue at n = m = 4 (one prime, one target).

Same construction as square_analogue.py (own code, Sage + Singular + msolve cross-check),
one extension degree up, raw arm omitted (predicted 4! * 8^4 = 98304, too large to be
worth the lock time).  At EVEN extension degree every element of F_p is a square in K, so a
rescaling b = lam^2 * beta with beta in F_p exists only when b is itself a square in K; the
curve is therefore taken with b a square (FHJRV Prop. 8 setting, beta = 1), which changes
nothing in the S4-versus-product comparison.  (The EcGFp5 case, odd degree and b a
non-square, is the n = m = 3 run.)  Degrees by msolve only (Singular std is slow at 4096).
Predictions written BEFORE running:
  D_S4 = 8^4 = 4096 = 2^{m(m-1)},  D_product = 4096 (no drop),
  D_D4type = 4! * 8^4 / (2^3 * 4!) = 512 = 2^{(m-1)^2}.
"""
import sys, os, json, time
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from square_analogue import (S3_poly, ec_add, random_point, descend, laurent_to_t, poly_to_laurent,
                             log, HERE)
import re, subprocess
def ideal_degree(polys, Rp, label, workdir):
    fn = os.path.join(workdir, f"{label}.ms")
    with open(fn, "w") as fh:
        fh.write(",".join(str(v) for v in Rp.gens()) + "\n" + str(Rp.base_ring().order()) + "\n")
        fh.write(",\n".join(str(f).replace(" ", "") for f in polys) + "\n")
    t0 = time.time()
    r = subprocess.run(["/usr/bin/msolve", "-v", "2", "-t", "4", "-f", fn, "-o", fn + ".out"], capture_output=True, text=True, timeout=3600)
    txt = r.stdout + r.stderr
    m = re.search(r"Dimension of quotient:\s*(\d+)", txt)
    pos = "positive dimension" in txt.lower()
    os.remove(fn)
    if os.path.exists(fn + ".out"): os.remove(fn + ".out")
    return {"D_msolve": int(m.group(1)) if m else None, "msolve_rc": r.returncode, "positive_dimension_reported": pos,
            "msolve_seconds": round(time.time() - t0, 1)}
from sage.all import GF, PolynomialRing, prod, is_prime, set_random_seed
import itertools

def to_elementary(F, xs, dmax, Re):
    """Leading-term (lex) reduction of a symmetric polynomial to e1..en (exact; terminates at 0
    only if F is symmetric).  dmax is ignored (kept for the call signature)."""
    K = F.parent().base_ring(); n = len(xs)
    names = [str(v) for v in xs]
    Rl = PolynomialRing(K, names, order='lex'); V = Rl.gens()
    f = Rl({tuple(e): c for e, c in F.dict().items()})
    es = [sum(prod(c) for c in itertools.combinations(V, k)) for k in range(1, n + 1)]
    powc = {}
    def epow(i, k):
        if (i, k) not in powc:
            powc[(i, k)] = es[i]**k
        return powc[(i, k)]
    E = Re.gens(); G = Re(0); steps = 0
    while f != 0:
        a = f.lm().exponents()[0]; c = f.lc()
        assert all(a[i] >= a[i + 1] for i in range(n - 1)), "not symmetric"
        d = [a[i] - a[i + 1] for i in range(n - 1)] + [a[n - 1]]
        f -= c * prod(epow(i, d[i]) for i in range(n) if d[i])
        G += c * prod(E[i]**d[i] for i in range(n))
        steps += 1
        assert steps < 100000
    return G

def run(p, seed):
    set_random_seed(seed)
    n = m = 4
    Fp = GF(p); K = GF(p**n, 'z'); z = K.gen()
    a2, a6 = K(2), K(0)
    # every element of F_p is a square in F_{p^4}; take b = (z + j)^2, smallest j with a2^2 - 4b != 0
    j = next(v for v in range(0, 500) if (a2 * a2 - 4 * (z + v)**2) != 0)
    b = (z + j)**2; a4 = b
    res = {"p": p, "field": f"GF({p}^4) modulus {K.modulus()}", "curve": f"y^2 = x(x^2 + 2x + (z+{j})^2)",
           "b_is_square": bool(b.is_square()), "a2^2-4b_is_square": bool((a2 * a2 - 4 * b).is_square())}
    beta = Fp(1); lam = b.sqrt(); assert lam**2 == b
    res["beta"] = int(beta) if lam is not None else None
    R = random_point(K, a2, a4, a6); X0 = R[0]
    PR = PolynomialRing(K, ['x1', 'x2', 'x3', 'x4', 'Y', 'W'])
    x1, x2, x3, x4, Y, W = PR.gens()
    t0 = time.time()
    S4_34Y = S3_poly(x3, x4, W, a2, a4, a6).resultant(S3_poly(K(X0), Y, W, a2, a4, a6), W)     # S_4(x3, x4, X0, Y)
    S5 = S3_poly(x1, x2, Y, a2, a4, a6).resultant(S4_34Y, Y)                                    # S_5(x1..x4, X0)
    Rx = PolynomialRing(K, ['x1', 'x2', 'x3', 'x4']); X = Rx.gens()
    F = Rx({e[:4]: c for e, c in S5.dict().items()})
    res["S5"] = {"degree_per_variable": [int(F.degree(v)) for v in X], "n_terms": len(F.dict()), "seconds": round(time.time() - t0, 1),
                 "symmetric": bool(F == F.subs({X[0]: X[1], X[1]: X[0]}) and F == F.subs({X[0]: X[3], X[3]: X[0]}))}
    log("S5 built", res["S5"])
    Re = PolynomialRing(K, ['e1', 'e2', 'e3', 'e4'])
    Rpe = PolynomialRing(Fp, ['e1', 'e2', 'e3', 'e4'], order='degrevlex')
    G = to_elementary(F, list(X), 8, Re)
    res["S4"] = ideal_degree(descend(G, Rpe, n), Rpe, f"S4_m4_p{p}", HERE)
    res["S4"].update({"n_monomials": len(G.dict()), "total_degree": int(G.total_degree())})
    log("S4", res["S4"])
    # (iii) product construction
    Fsub = Rx({(8 - e[0],) + tuple(e[1:]): c * b**e[0] for e, c in F.dict().items()})   # x1^8 F(b/x1, ...)
    H = F * Fsub
    Td = laurent_to_t(poly_to_laurent(H.dict(), (8, 8, 8, 8)), 4, b, K)
    Rt = PolynomialRing(K, ['t1', 't2', 't3', 't4']); T = Rt.gens()
    Gt = to_elementary(Rt(Td), list(T), 8, Re)
    res["product"] = ideal_degree(descend(Gt, Rpe, n), Rpe, f"prod_m4_p{p}", HERE)
    res["product"].update({"n_monomials": len(Gt.dict()), "total_degree": int(Gt.total_degree()),
                           "same_support_as_S4": set(Gt.dict().keys()) == set(G.dict().keys())})
    log("product", res["product"])
    # (iv) D4-type on the rescaled base, if a rescaling with beta in F_p exists
    if lam is not None:
        Ru = PolynomialRing(K, ['u1', 'u2', 'u3', 'u4']); U = Ru.gens()
        Fu = {e: c * lam**sum(e) for e, c in F.dict().items()}
        Ld = poly_to_laurent(Fu, (4, 4, 4, 4))
        L1 = {(-a[0],) + a[1:]: c * K(beta)**a[0] for a, c in Ld.items()}
        keys = set(Ld) | set(L1)
        Ad = {a: (Ld.get(a, 0) + L1.get(a, 0)) / 2 for a in keys}; Ad = {a: c for a, c in Ad.items() if c}
        Nd = {a: (Ld.get(a, 0) - L1.get(a, 0)) / 2 for a in keys}; Nd = {a: c for a, c in Nd.items() if c}
        sh = 5
        Npoly = Ru({tuple(ai + sh for ai in a): c for a, c in Nd.items()})
        q, r = Npoly.quo_rem(prod(v**2 - K(beta) for v in U)); assert r == 0
        Bd = {tuple(ai - sh + 1 for ai in a): c for a, c in q.dict().items()}
        At = Rt(laurent_to_t(Ad, 4, K(beta), K)); Bt = Rt(laurent_to_t(Bd, 4, K(beta), K))
        Qt = prod(v**2 - 4 * K(beta) for v in T)
        ReW = PolynomialRing(K, ['s1', 's2', 's3', 's4', 'w']); w = ReW.gens()[4]
        Rs = PolynomialRing(K, ['s1', 's2', 's3', 's4'])
        Ga = ReW(to_elementary(At, list(T), 4, Rs)); Gb = ReW(to_elementary(Bt, list(T), 4, Rs)); Gq = ReW(to_elementary(Qt, list(T), 4, Rs))
        RpW = PolynomialRing(Fp, ['s1', 's2', 's3', 's4', 'w'], order='degrevlex')
        eqs = descend(Ga + w * Gb, RpW, n) + [RpW(w**2 - Gq)]
        res["D4type"] = ideal_degree(eqs, RpW, f"D4_m4_p{p}", HERE)
        res["D4type"].update({"deg_A_sigma": int(Ga.total_degree()), "deg_B_sigma": int(Gb.total_degree()), "n_monomials_A_plus_wB": len((Ga + w * Gb).dict())})
        log("D4type", res["D4type"])
    return res

if __name__ == "__main__":
    t0 = time.time()
    out = {"task": "TASK-20260923-404bf9", "joint": "K5", "n": 4, "m": 4,
           "predictions_before_run": {"S4": 4096, "product": 4096, "D4type": 512}}
    out["result"] = run(4111, 3)
    out["wall_seconds"] = round(time.time() - t0, 1)
    json.dump(out, open(os.path.join(HERE, "square_analogue_n4.json"), "w"), indent=1, default=str)
    log("done", out["wall_seconds"])

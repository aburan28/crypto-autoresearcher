#!/usr/bin/env sage-python
"""TASK-20260923-404bf9 (red team) -- K5 / K7 square analogue, n = m = 3.

Own code (Sage + Singular), sharing nothing with experiments/EXP-GFPN-05ff43/.
Over K = F_p[z]/(z^3 - c) with the double-odd-shaped curve
    E : y^2 = x (x^2 + 2x + b),  b = b0*z,  b and a^2 - 4b non-squares in K
(the EcGFp5 shape one degree down), and a target R in E(K), build and Weil-descend
to F_p the four square (3 equations / 3 unknowns, or 4/4) systems:

  (i)   raw        S_4(x1,x2,x3; x_R), unknowns x_i in F_p
  (ii)  S3         the same polynomial in e1,e2,e3 of the x_i
  (iii) product    the producer's arm-(iii) construction (implementation.md 1.3, D-6):
                   S_4(x; X) * S_4(b/x1, x2, x3; X), Laurent-normalised, rewritten in
                   t_i = x_i + b/x_i, then in e(t); unknowns e(t) in F_p
  (iv)  D3-type    a (Z/2)^{m-1} x| S_m quotient that IS defined over F_p:
                   rescale x = lam*u with b = lam^2*beta, beta in F_p (non-square),
                   so translation by T=(0,0) is u -> beta/u over F_p for every Frobenius
                   conjugate; unknowns sigma_k(t'_i), t'_i = u_i + beta/u_i, and
                   w = prod (u_i - beta/u_i), with S_4 = A(sigma) + w B(sigma) and
                   the relation w^2 = prod (t'_i^2 - 4 beta).

and report the ideal degree D (Singular vdim, cross-checked with msolve's
"Dimension of quotient") at two primes and two targets per prime.

Predictions written BEFORE running (K5/K7 derivation in review-report.yaml):
  D_raw = 3! * 4^3 = 384, D_S3 = 4^3 = 64 = 2^{m(m-1)}, D_product = 64 (no drop),
  D_D3type = 384 / (2^2 * 3!) = 16 = 2^{(m-1)^2}.
"""
import sys, json, time, itertools, subprocess, os, re
from sage.all import (GF, PolynomialRing, ZZ, prod, binomial, matrix, vector, Integer, is_prime, set_random_seed)

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = {}

def log(*a):
    print(time.strftime("%H:%M:%S"), *a, flush=True)

def setup_field(p, n):
    Fp = GF(p)
    Rt = PolynomialRing(Fp, 't'); t = Rt.gen()
    c = next(c for c in range(2, p) if (t**n - c).is_irreducible())
    K = GF(p**n, 'z', modulus=t**n - c)
    return Fp, K, K.gen(), c

def choose_curve(K, z, a2=2):
    for b0 in range(1, 500):
        b = b0 * z
        if b.is_square() or (a2 * a2 - 4 * b).is_square():
            continue
        disc = 16 * b * b * (a2 * a2 - 4 * b)        # disc of x(x^2+a2x+b) up to sign
        if disc == 0:
            continue
        return b0, b
    raise RuntimeError("no curve")

def S3_poly(u, v, w, a2, a4, a6):
    """S_3 for y^2 = x^3 + a2 x^2 + a4 x + a6, derived from x(P1 +- P2)
    (sum 2(f1+f2)/d^2 - 2c, product (g^2 - 2c(f1+f2))/d^2 + c^2), cleared by d^2."""
    f = lambda s: s**3 + a2 * s**2 + a4 * s + a6
    d = u - v
    g = u * u + u * v + v * v + a2 * (u + v) + a4          # (f(u)-f(v))/(u-v)
    cc = a2 + u + v
    return d**2 * w**2 - (2 * (f(u) + f(v)) - 2 * cc * d**2) * w + (g**2 - 2 * cc * (f(u) + f(v)) + cc**2 * d**2)

def ec_add(P, Q, a2, a4, a6):
    if P is None: return Q
    if Q is None: return P
    (x1, y1), (x2, y2) = P, Q
    if x1 == x2:
        if y1 + y2 == 0: return None
        lam = (3 * x1**2 + 2 * a2 * x1 + a4) / (2 * y1)
    else:
        lam = (y2 - y1) / (x2 - x1)
    x3 = lam**2 - a2 - x1 - x2
    return (x3, lam * (x1 - x3) - y1)

def random_point(K, a2, a4, a6):
    while True:
        x = K.random_element(); r = x**3 + a2 * x**2 + a4 * x + a6
        if r != 0 and r.is_square():
            return (x, r.sqrt())

def descend(poly, Rp, n):
    """poly in K[vars] -> list of n polynomials over F_p (z-components)."""
    comps = [dict() for _ in range(n)]
    for mon, coef in poly.dict().items():
        for k, ck in enumerate(coef.polynomial().list()):
            if ck:
                comps[k][tuple(mon)] = comps[k].get(tuple(mon), 0) + ck
    return [Rp(cd) for cd in comps]

def to_elementary(F, xs, dmax, Re):
    """Write symmetric F(x) as G(e1..en), total degree <= dmax; exact linear algebra; verified."""
    Rx = F.parent(); n = len(xs); K = Rx.base_ring()
    es = [sum(prod(c) for c in itertools.combinations(xs, k)) for k in range(1, n + 1)]
    monos = [a for d in range(dmax + 1) for a in itertools.product(range(d + 1), repeat=n) if sum(a) == d]
    basis = [prod(es[i]**a[i] for i in range(n)) for a in monos]
    supp = sorted(set().union(*[set(b.dict().keys()) for b in basis]) | set(F.dict().keys()))
    idx = {mm: i for i, mm in enumerate(supp)}
    M = matrix(K, len(supp), len(basis))
    for j, bpol in enumerate(basis):
        for mm, cc in bpol.dict().items():
            M[idx[mm], j] = cc
    rhs = vector(K, len(supp))
    for mm, cc in F.dict().items():
        rhs[idx[mm]] = cc
    sol = M.solve_right(rhs)
    E = Re.gens()
    G = sum(sol[j] * prod(E[i]**monos[j][i] for i in range(n)) for j in range(len(monos)))
    back = sum(sol[j] * basis[j] for j in range(len(monos)))
    assert back == F, "symmetric reduction failed"
    return G

def dickson(beta, kmax, Rt1):
    t = Rt1.gen(); D = [Rt1(2), t]
    for k in range(2, kmax + 1):
        D.append(t * D[-1] - beta * D[-2])
    return D

def laurent_to_t(Ld, n, beta, K):
    """Ld: {exponent tuple (ints, maybe negative): coeff in K}, invariant under a_i -> -a_i
    with c(-a_i) = beta^{a_i} c(a_i) in every variable.  Returns {degree tuple: coeff} in t_i = u_i + beta/u_i."""
    Rt1 = PolynomialRing(K, 'tt')
    cur = dict(Ld)
    for i in range(n):
        groups = {}
        for a, c in cur.items():
            groups.setdefault(a[:i] + a[i + 1:], {})[a[i]] = c
        new = {}
        for rest, col in groups.items():
            h = max(abs(k) for k in col)
            for k in range(1, h + 1):
                assert col.get(-k, 0) == beta**k * col.get(k, 0), ("not invariant", i, k)
            Dk = dickson(beta, h, Rt1)
            pt = Rt1(col.get(0, 0)) + sum(col.get(k, 0) * Dk[k] for k in range(1, h + 1))
            for deg, cc in enumerate(pt.list()):
                if cc:
                    key = rest[:i] + (deg,) + rest[i:]
                    new[key] = new.get(key, 0) + cc
        cur = new
    return cur

def poly_to_laurent(Pd, shift):
    return {tuple(a - s for a, s in zip(mon, shift)): c for mon, c in Pd.items()}

def ideal_degree(polys, Rp, label, workdir):
    I = Rp.ideal(polys)
    dim = I.dimension()
    D = I.vector_space_dimension() if dim == 0 else None
    # cross-check with msolve (Dimension of quotient)
    msD = None
    try:
        fn = os.path.join(workdir, f"{label}.ms")
        with open(fn, "w") as fh:
            fh.write(",".join(str(v) for v in Rp.gens()) + "\n" + str(Rp.base_ring().order()) + "\n")
            fh.write(",\n".join(str(f).replace(" ", "") for f in polys) + "\n")
        r = subprocess.run(["/usr/bin/msolve", "-v", "2", "-t", "1", "-f", fn, "-o", fn + ".out"],
                           capture_output=True, text=True, timeout=1800)
        m = re.search(r"Dimension of quotient:\s*(\d+)", r.stdout + r.stderr)
        msD = int(m.group(1)) if m else ("rc=%d" % r.returncode)
        os.remove(fn)
        if os.path.exists(fn + ".out"): os.remove(fn + ".out")
    except Exception as ex:
        msD = f"msolve error {ex}"
    return {"krull_dim": int(dim), "D_singular_vdim": (int(D) if D is not None else None), "D_msolve": msD}

def run_prime(p, seed, ntargets=2):
    set_random_seed(seed)
    n = m = 3
    Fp, K, z, c = setup_field(p, n)
    a2, a6 = K(2), K(0)
    b0, b = choose_curve(K, z)
    a4 = b
    res = {"p": p, "field": f"F_{p}[z]/(z^3 - {c})", "curve": f"y^2 = x(x^2 + 2x + {b0}*z)",
           "b_is_square": bool(b.is_square()), "a2^2-4b_is_square": bool((a2 * a2 - 4 * b).is_square()), "targets": []}
    # beta in F_p non-square, lam^2 = b/beta
    beta = next(Fp(v) for v in range(2, p) if not Fp(v).is_square())
    lam = (b / K(beta)).sqrt()
    assert lam**2 * K(beta) == b
    res["beta"] = int(beta)
    PR = PolynomialRing(K, ['x1', 'x2', 'x3', 'X', 'Y'])
    x1, x2, x3, X, Y = PR.gens()
    S4gen = S3_poly(x1, x2, Y, a2, a4, a6).resultant(S3_poly(x3, X, Y, a2, a4, a6), Y)
    # sanity: degree 4 in each variable, symmetric, vanishes at genuine sums
    degs = [S4gen.degree(v) for v in (x1, x2, x3, X)]
    sym_ok = S4gen == S4gen.subs({x1: x2, x2: x1}) and S4gen == S4gen.subs({x1: x3, x3: x1}) and S4gen == S4gen.subs({x3: X, X: x3})
    van = 0
    for _ in range(5):
        P1, P2, P3 = [random_point(K, a2, a4, a6) for _ in range(3)]
        Rs = ec_add(ec_add(P1, P2, a2, a4, a6), P3, a2, a4, a6)
        if Rs is None: continue
        van += int(S4gen.subs({x1: P1[0], x2: P2[0], x3: P3[0], X: Rs[0]}) == 0)
    res["S4_checks"] = {"degree_per_variable": [int(d) for d in degs], "symmetric": bool(sym_ok), "vanish_at_sums_of_5": van}
    Rx = PolynomialRing(K, ['x1', 'x2', 'x3']); X1, X2, X3 = Rx.gens()
    Ru = PolynomialRing(K, ['u1', 'u2', 'u3']); U1, U2, U3 = Ru.gens()
    for ti in range(ntargets):
        R = random_point(K, a2, a4, a6)
        X0 = R[0]
        S4X = S4gen.subs({X: X0, Y: 0})
        assert all(e[3] == 0 and e[4] == 0 for e in S4X.dict())
        F = Rx({(e[0], e[1], e[2]): cc for e, cc in S4X.dict().items()})
        tr = {"target": ti, "x_R": str(X0)}
        # (i) raw
        Rp = PolynomialRing(Fp, ['x1', 'x2', 'x3'], order='degrevlex')
        tr["raw"] = ideal_degree(descend(F, Rp, n), Rp, f"raw_p{p}_t{ti}", HERE)
        # (ii) S3
        ReK = PolynomialRing(K, ['e1', 'e2', 'e3'])
        G = to_elementary(F, [X1, X2, X3], 4, ReK)
        Rpe = PolynomialRing(Fp, ['e1', 'e2', 'e3'], order='degrevlex')
        tr["S3"] = ideal_degree(descend(G, Rpe, n), Rpe, f"S3_p{p}_t{ti}", HERE)
        tr["S3"]["n_monomials"] = len(G.dict()); tr["S3"]["total_degree"] = int(G.total_degree())
        # (iii) producer's product construction, t = x + b/x
        Fsub = sum(cc * (b**mon[0]) * X1**(4 - mon[0]) * X2**mon[1] * X3**mon[2] for mon, cc in F.dict().items())  # x1^4 F(b/x1,..)
        H = F * Fsub
        Ld = poly_to_laurent(H.dict(), (4, 4, 4))
        Td = laurent_to_t(Ld, 3, b, K)
        Rt = PolynomialRing(K, ['t1', 't2', 't3']); T1, T2, T3 = Rt.gens()
        Tpoly = Rt(Td)
        assert all(Tpoly.degree(v) <= 4 for v in (T1, T2, T3))
        Gt = to_elementary(Tpoly, [T1, T2, T3], 4, ReK)
        tr["product"] = ideal_degree(descend(Gt, Rpe, n), Rpe, f"prod_p{p}_t{ti}", HERE)
        tr["product"]["n_monomials"] = len(Gt.dict()); tr["product"]["total_degree"] = int(Gt.total_degree())
        tr["product"]["same_support_as_S3"] = set(Gt.dict().keys()) == set(G.dict().keys())
        # (iv) D3-type quotient on the rescaled base u = x / lam
        Fu = Ru(sum(cc * (lam**sum(mon)) * U1**mon[0] * U2**mon[1] * U3**mon[2] for mon, cc in F.dict().items()))
        Ld = poly_to_laurent(Fu.dict(), (2, 2, 2))                         # L = F(lam u) / (u1 u2 u3)^2
        L1 = {(-a[0],) + a[1:]: c * K(beta)**a[0] for a, c in Ld.items()}   # L(beta/u1, u2, u3)
        keys = set(Ld) | set(L1)
        Ad = {a: (Ld.get(a, 0) + L1.get(a, 0)) / 2 for a in keys}
        Nd = {a: (Ld.get(a, 0) - L1.get(a, 0)) / 2 for a in keys}
        Ad = {a: c for a, c in Ad.items() if c}; Nd = {a: c for a, c in Nd.items() if c}
        # B = N / W, W = prod(u_i - beta/u_i): multiply by (u1u2u3)^3 and divide by prod(u_i^2 - beta)
        shift = 3
        Npoly = Ru({tuple(ai + shift for ai in a): c for a, c in Nd.items()})
        Wp = prod(v**2 - K(beta) for v in (U1, U2, U3))
        q, r = Npoly.quo_rem(Wp)
        assert r == 0, "N not divisible by W"
        Bd = {tuple(ai - shift + 1 for ai in a): c for a, c in q.dict().items()}   # q = N*(u1u2u3)^3/(W*u1u2u3)
        At = Rt(laurent_to_t(Ad, 3, K(beta), K)); Bt = Rt(laurent_to_t(Bd, 3, K(beta), K))
        # check L == A + W B exactly (as Laurent dicts)
        Qt = prod(v**2 - 4 * K(beta) for v in (T1, T2, T3))
        ReW = PolynomialRing(K, ['s1', 's2', 's3', 'w'])
        s1, s2, s3, w = ReW.gens()
        Res3 = PolynomialRing(K, ['s1', 's2', 's3'])
        Ga = ReW(to_elementary(At, [T1, T2, T3], 4, Res3)); Gb = ReW(to_elementary(Bt, [T1, T2, T3], 4, Res3))
        Gq = ReW(to_elementary(Qt, [T1, T2, T3], 6, Res3))
        RpW = PolynomialRing(Fp, ['s1', 's2', 's3', 'w'], order='degrevlex')
        eqs = descend(Ga + w * Gb, RpW, n) + [RpW(w**2 - Gq)]
        tr["D3type"] = ideal_degree(eqs, RpW, f"D3_p{p}_t{ti}", HERE)
        tr["D3type"]["deg_A_sigma"] = int(Ga.total_degree()); tr["D3type"]["deg_B_sigma"] = int(Gb.total_degree())
        tr["D3type"]["n_monomials_A_plus_wB"] = len((Ga + w * Gb).dict())
        log("p", p, "target", ti, {k: tr[k] for k in ("raw", "S3", "product", "D3type")})
        res["targets"].append(tr)
    return res

if __name__ == "__main__":
    t0 = time.time()
    out = {"task": "TASK-20260923-404bf9", "joint": "K5 (and K7 sanity)", "n": 3, "m": 3,
           "predictions_before_run": {"raw": 384, "S3": 64, "product": 64, "D3type": 16}, "primes": []}
    for p, seed in ((4111, 1), (16777291, 2)):
        assert is_prime(p) and p % 3 == 1
        out["primes"].append(run_prime(p, seed))
    out["wall_seconds"] = round(time.time() - t0, 1)
    json.dump(out, open(os.path.join(HERE, "square_analogue_n3.json"), "w"), indent=1, default=str)
    log("done", out["wall_seconds"])

# B2 cross-check (C-4): deg rad(I_R cap F_p[u]) computed in Sage, independent of
# B2's point arithmetic. I_R = <S5(u, X3, X4, X5, x(R)), f_V(X3), f_V(X4), f_V(X5)>,
# f_V = prod_{v in V}(X - v); for R = O the generator is S4(u, X3, X4, X5).
#
# Methods (per query, chosen by the caller):
#   fglm  -- literal Singular elimination: Groebner basis of I_R in degrevlex,
#            FGLM to lex with u last; the unique basis element in F_p[u] generates
#            I_R cap F_p[u]. Slow at |V| = 8 (~10 min/query on the smoke machine).
#   split -- because f_V splits into distinct linear factors over F_p,
#            V(I_R) = {(u, v3, v4, v5) : v_i in V, S5(u, v3, v4, v5, x(R)) = 0}, so
#            rad(I_R cap F_p[u]) = rad(lcm over ordered (v3, v4, v5) in V^3 of
#            S5(u, v3, v4, v5, x(R))). Univariate Sage arithmetic only.
#
# Run with: sage -python sage_b2_crosscheck.py IN.json OUT.json
# IN: {"p","a","b","semaev_file", "queries":[{"query_id","V":[...],"xR":int|null,
#      "methods":["split","fglm"]}]}
import itertools
import json
import sys
import time

from sage.all import GF, PolynomialRing

inp = json.load(open(sys.argv[1]))
p, a, b = inp["p"], inp["a"], inp["b"]
terms = json.load(open(inp["semaev_file"]))
F = GF(p)
Fa, Fb = F(a), F(b)
R5 = PolynomialRing(F, "X3,X4,X5,u,Y", order="degrevlex")
X3, X4, X5, u, Y = R5.gens()
Ru = PolynomialRing(F, "w")
w = Ru.gen()


def build(tl, n, vals):
    d = {}
    for t in tl:
        c = F(t[2 + n]) * Fa ** t[0] * Fb ** t[1]
        if c == 0:
            continue
        e = [0] * 5
        for var_index, ex in zip(vals, t[2:2 + n]):
            e[var_index] += ex
        d[tuple(e)] = d.get(tuple(e), F(0)) + c
    return R5(d)


# variable indices in R5: X3=0, X4=1, X5=2, u=3, Y=4
S5_full = build(terms["S5"], 5, [3, 0, 1, 2, 4])   # S5(u, X3, X4, X5, Y)
S4_full = build(terms["S4"], 4, [3, 0, 1, 2])       # S4(u, X3, X4, X5)


def radical(g):
    return g // g.gcd(g.derivative())


def split_method(V, xR):
    gen = S4_full if xR is None else S5_full.subs({Y: F(xR)})
    lcm = Ru(1)
    for v3, v4, v5 in itertools.product(V, repeat=3):
        bu = gen.subs({X3: F(v3), X4: F(v4), X5: F(v5)})
        bu = Ru(bu.univariate_polynomial()(w)) if bu.degree() > 0 else Ru(bu.constant_coefficient())
        if bu == 0:
            return None, "identically zero S5 specialization"
        lcm = lcm.lcm(radical(bu))
    return radical(lcm), None


def fglm_method(V, xR):
    Rg = PolynomialRing(F, "X3,X4,X5,u", order="degrevlex")
    x3, x4, x5, uu = Rg.gens()
    gen = S4_full if xR is None else S5_full.subs({Y: F(xR)})
    gen = Rg({k[:4]: v for k, v in gen.dict().items()})  # Y already substituted
    fV = [Rg.prod([X - F(v) for v in V]) for X in (x3, x4, x5)]
    J = Rg.ideal(Rg.ideal([gen] + fV).groebner_basis())
    lexb = J.transformed_basis("fglm", other_ring=PolynomialRing(F, "X3,X4,X5,u", order="lex"))
    elim = [h for h in lexb if h != 0 and all(m[0] == m[1] == m[2] == 0 for m in h.exponents())]
    if len(elim) != 1:
        return None, f"{len(elim)} eliminant generators"
    g = Ru(elim[0].univariate_polynomial()(w))
    return radical(g), int(g.degree())


out = []
for qd in inp["queries"]:
    rec = {"query_id": qd["query_id"]}
    for m in qd.get("methods", ["split"]):
        t0 = time.time()
        if m == "split":
            rad, err = split_method(qd["V"], qd["xR"])
            extra = {"error": err}
        else:
            rad, gdeg = fglm_method(qd["V"], qd["xR"])
            extra = {"eliminant_degree": gdeg} if rad is not None else {"error": gdeg}
        if rad is None:
            rec[m] = dict(extra, seconds=round(time.time() - t0, 2))
            continue
        roots = sorted(int(r) for r, _ in rad.roots())
        rec[m] = dict(extra, radical_degree=int(rad.degree()), rational_roots=len(roots),
                      roots=roots, seconds=round(time.time() - t0, 2))
        print(qd["query_id"], m, rec[m]["radical_degree"], rec[m]["seconds"], flush=True)
    out.append(rec)
    json.dump({"results": out}, open(sys.argv[2], "w"), indent=1)
json.dump({"results": out}, open(sys.argv[2], "w"), indent=1)

# Offline derivation of the Semaev summation polynomials S3, S4, S5 over
# Z[a, b] (AMD-20260926-3479cf C-3). Run with: sage -python derive_semaev.py OUT.json
#
# S3 is P1480's formula, verbatim from C-3:
#   S3(v, u, x) = (u-v)^2 x^2 - 2((u+v)(uv+a)+2b) x + (uv-a)^2 - 4b(u+v)
# S4(x1,x2,x3,x4) = Res_t(S3(x1,x2,t), S3(x3,x4,t))
# S5(x1,...,x5)   = Res_t(S4(x1,x2,x3,t), S3(x4,x5,t))
# i.e. elimination of the intermediate x-coordinate t. The output is a
# canonical JSON term list [[ea, eb, e1, ..., en, coeff], ...] sorted
# lexicographically, so the file hash is deterministic.
import json
import sys
import time

from sage.all import QQ, ZZ, PolynomialRing

R = PolynomialRing(ZZ, "a,b,x1,x2,x3,x4,x5,t", order="lex")
a, b, x1, x2, x3, x4, x5, t = R.gens()


def S3(v, u, x):
    return ((u - v) ** 2 * x ** 2 - 2 * ((u + v) * (u * v + a) + 2 * b) * x
            + (u * v - a) ** 2 - 4 * b * (u + v))


def terms(poly, xs):
    out = []
    for mon, c in poly.dict().items():
        e = dict(zip(R.gens(), mon))
        out.append([int(e[a]), int(e[b])] + [int(e[x]) for x in xs] + [int(c)])
    out.sort()
    return out


t0 = time.time()
s3 = S3(x1, x2, x3)
s4 = S3(x1, x2, t).resultant(S3(x3, x4, t), t)
t1 = time.time()
s4t = s4.subs({x4: t})
s5 = s4t.resultant(S3(x4, x5, t), t)
t2 = time.time()

# primitive part with positive leading term (roots are what matter)
def normalize(p):
    c = p.content() if hasattr(p, "content") else 1
    p = p // c
    lc = p.lc()
    if lc < 0:
        p = -p
    return p, int(c)

s4n, c4 = normalize(s4)
s5n, c5 = normalize(s5)

degs5 = [int(s5n.degree(v)) for v in (x1, x2, x3, x4, x5)]
degs4 = [int(s4n.degree(v)) for v in (x1, x2, x3, x4)]
sym5 = all(s5n == s5n.subs({x1: x2, x2: x1}) for _ in [0]) and s5n == s5n.subs({x1: x5, x5: x1})

doc = {
    "description": "Semaev summation polynomials over Z[a,b] derived by resultant "
                   "elimination (EXP-SDEG-85eefd AMD-20260926-3479cf C-3). Term format: "
                   "[ea, eb, e1..en, coeff].",
    "S3_formula": "(u-v)^2*x^2 - 2*((u+v)*(u*v+a)+2*b)*x + (u*v-a)^2 - 4*b*(u+v) with (v,u,x)=(x1,x2,x3)",
    "S4_definition": "primitive part of Res_t(S3(x1,x2,t), S3(x3,x4,t))",
    "S5_definition": "primitive part of Res_t(S4(x1,x2,x3,t), S3(x4,x5,t))",
    "content_removed": {"S4": c4, "S5": c5},
    "degrees": {"S4": degs4, "S5": degs5},
    "symmetric_check_S5_swaps_12_15": bool(sym5),
    "derivation_seconds": {"S4": round(t1 - t0, 3), "S5": round(t2 - t1, 3)},
    "S3": terms(s3, [x1, x2, x3]),
    "S4": terms(s4n, [x1, x2, x3, x4]),
    "S5": terms(s5n, [x1, x2, x3, x4, x5]),
}
# timings are not deterministic; keep them out of the hashed file
timing = doc.pop("derivation_seconds")
with open(sys.argv[1], "w") as fh:
    json.dump(doc, fh, sort_keys=True, separators=(",", ":"))
    fh.write("\n")
print(json.dumps({"derivation_seconds": timing, "terms": {k: len(doc[k]) for k in ("S3", "S4", "S5")},
                  "degrees": doc["degrees"], "content_removed": doc["content_removed"],
                  "symmetric": doc["symmetric_check_S5_swaps_12_15"]}))

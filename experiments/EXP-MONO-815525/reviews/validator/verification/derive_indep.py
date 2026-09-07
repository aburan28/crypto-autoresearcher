"""Validator's INDEPENDENT derivation of S_3, S_4 and the leading
T-coefficient c_4 of Q_e(T) = S_4(x1,x2,x3,T).  Answers J1's core question:
what does c_4(e)=0 mean?"""
from mpoly import *

x1, x2, x3, x4, U = (var(v) for v in ("x1", "x2", "x3", "x4", "U"))
A, B, y1, y2 = (var(v) for v in ("A", "B", "y1", "y2"))

# ---- S_3 from the group law, my own elimination -------------------------
# x(P1+P2) = lambda^2 - x1 - x2 with lambda=(y2-y1)/(x2-x1); so
#   (y2-y1)^2 = (x1+x2+x3)(x2-x1)^2  is x3 = x(P1+P2) or x(P1-P2)
rel = sub(power(sub(y2, y1), 2), mul(add(x1, x2, x3), power(sub(x2, x1), 2)))
f1 = sub(power(y1, 2), add(power(x1, 3), mul(A, x1), B))
f2 = sub(power(y2, 2), add(power(x2, 3), mul(A, x2), B))
r1 = sylvester_resultant(rel, f1, "y1")
r2 = sylvester_resultant(r1, f2, "y2")

# candidate S_3 built by hand from the same elimination:
S3 = add(power(A, 2),
         smul(-2, mul(A, add(mul(x1, x2), mul(x1, x3), mul(x2, x3)))),
         smul(-4, mul(B, add(x1, x2, x3))),
         mul(power(x1, 2), power(x2, 2)),
         smul(-2, mul(mul(power(x1, 2), x2), x3)),
         mul(power(x1, 2), power(x3, 2)),
         smul(-2, mul(mul(x1, power(x2, 2)), x3)),
         smul(-2, mul(mul(x1, x2), power(x3, 2))),
         mul(power(x2, 2), power(x3, 2)))
chk = sub(r2, mul(power(sub(x1, x2), 4), power(S3, 2)))
print("[my derivation] Res_{y1,y2} == (x1-x2)^4 * S_3^2 :", chk == {})
print("[my derivation] deg S_3 in x1,x2,x3:",
      [degree_in(S3, v) for v in ("x1", "x2", "x3")])
sym = all(subst(S3, dict(zip(("x1", "x2", "x3"), (var(a), var(b), var(c)))))
          == S3 for a, b, c in permutations(("x1", "x2", "x3")))
print("[my derivation] S_3 symmetric:", sym)

# ---- S_4 = Res_U( S_3(x1,x2,U), S_3(x3,x4,U) ) --------------------------
S3a = subst(S3, {"x3": U})
S3b = subst(S3, {"x1": x3, "x2": x4, "x3": U})
S4 = sylvester_resultant(S3a, S3b, "U")
print("[my derivation] S_4 #terms:", len(S4),
      " degrees in x1..x4:", [degree_in(S4, v) for v in ("x1","x2","x3","x4")])

# ---- THE KEY STRUCTURAL FACT: leading T-coefficient ---------------------
c = coeff_list(S4, "x4")
print("[my derivation] c_4 - S_3(x1,x2,x3)^2 == 0 :",
      sub(c[4], power(S3, 2)) == {})

# ---- descend both to e1,e2,e3 ------------------------------------------
# S_3 in symmetric functions: A^2 - 2A e2 - 4B e1 + e2^2 - 4 e1 e3
e1, e2, e3 = var("y1"), var("y2"), var("U")     # reuse free slots as e1,e2,e3
S3e = add(power(A, 2), smul(-2, mul(A, e2)), smul(-4, mul(B, e1)),
          power(e2, 2), smul(-4, mul(e1, e3)))
# verify by substituting elementary symmetric relations numerically
import random
random.seed(7)
ok = True
for _ in range(200):
    a, b, cc, AA, BB = (random.randint(-40, 40) for _ in range(5))
    ee1, ee2, ee3 = a + b + cc, a * b + a * cc + b * cc, a * b * cc
    def ev(poly, sub_):
        t = 0
        for m, co in poly.items():
            v = co
            for i, d in enumerate(m):
                if d:
                    v *= sub_[VARS[i]] ** d
            t += v
        return t
    lhs = ev(S3, {"x1": a, "x2": b, "x3": cc, "A": AA, "B": BB,
                  "x4": 0, "U": 0, "y1": 0, "y2": 0})
    rhs = ev(S3e, {"y1": ee1, "y2": ee2, "U": ee3, "A": AA, "B": BB,
                   "x1": 0, "x2": 0, "x3": 0, "x4": 0})
    if lhs != rhs:
        ok = False
print("[my derivation] S_3(x1,x2,x3) == A^2-2A e2-4B e1+e2^2-4 e1 e3 :", ok)
print("[my derivation]   => c_4(e) = (A^2 - 2A e2 - 4B e1 + e2^2 - 4 e1 e3)^2")

# also dump c_3 in e-form later numerically; store S4 table for reuse
import json
json.dump({"vars": list(VARS),
           "S4": {",".join(map(str, m)): v for m, v in S4.items()},
           "S3": {",".join(map(str, m)): v for m, v in S3.items()}},
          open("indep_tables.json", "w"))
print("[my derivation] tables written")

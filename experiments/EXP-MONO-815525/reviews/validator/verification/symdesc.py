"""My own symmetric descent: express each x4-coefficient of MY S_4 in
e1,e2,e3 by the classical symmetric-reduction algorithm.  Output: c_k as a
dict (i,j,k,l,m) -> coeff for e1^i e2^j e3^k A^l B^m."""
import json, sys
sys.path.insert(0, ".")
from mpoly import *

tabs = json.load(open("indep_tables.json"))
S4 = {tuple(map(int, k.split(","))): v for k, v in tabs["S4"].items()}
IXA, IXB = IDX["A"], IDX["B"]
x1, x2, x3 = var("x1"), var("x2"), var("x3")
E1 = add(x1, x2, x3)
E2 = add(mul(x1, x2), mul(x1, x3), mul(x2, x3))
E3 = mul(mul(x1, x2), x3)

def sym_reduce(P):
    out = {}
    P = dict(P)
    while P:
        # lex-greatest monomial with key (a,b,c,i,j)
        m = max(P, key=lambda t: (t[IDX["x1"]], t[IDX["x2"]], t[IDX["x3"]],
                                  t[IXA], t[IXB]))
        c = P[m]
        a, b, cc = m[IDX["x1"]], m[IDX["x2"]], m[IDX["x3"]]
        assert a >= b >= cc, ("not symmetric-leading", m)
        i, j = m[IXA], m[IXB]
        key = (a - b, b - cc, cc, i, j)
        out[key] = out.get(key, 0) + c
        term = smul(c, mul(mul(power(E1, a - b), power(E2, b - cc)),
                           mul(power(E3, cc),
                               mul(power(var("A"), i), power(var("B"), j)))))
        P = sub(P, term)
    return {k: v for k, v in out.items() if v}

CK = {}
for k, coef in enumerate(coeff_list(S4, "x4")):
    CK[k] = sym_reduce(coef)
    print("my c_%d: %d terms in (e1,e2,e3,A,B)" % (k, len(CK[k])))

# cross-check against the Executor's symmetric table
REPO = "/Volumes/SSD990/crypto-autoresearcher/experiments/EXP-MONO-815525/implementation"
th = json.load(open(REPO + "/s4_symmetric_coeffs.json"))
allsame = True
for k in range(5):
    theirs = {}
    for kk, v in th["coeffs"][str(k)].items():
        m = tuple(map(int, kk.split(",")))
        theirs[(m[0], m[1], m[2], m[3], m[4])] = v
    same = theirs == CK[k]
    allsame &= same
    print("  c_%d identical to executor's symmetric table: %s" % (k, same))
print("ALL symmetric coefficients identical:", allsame)
print("my c_4 == (A^2 - 2A e2 - 4B e1 + e2^2 - 4 e1 e3)^2 :",
      CK[4] == {(0,0,0,4,0):1, (0,1,0,3,0):-4, (1,0,0,2,1):-8, (1,0,1,2,0):-8,
                (0,2,0,2,0):6, (1,1,0,1,1):16, (1,1,1,1,0):16, (0,3,0,1,0):-4,
                (2,0,0,0,2):16, (2,0,1,0,1):32, (1,2,0,0,1):-8, (2,0,2,0,0):16,
                (1,2,1,0,0):-8, (0,4,0,0,0):1})
json.dump({str(k): {",".join(map(str, kk)): v for kk, v in CK[k].items()}
           for k in range(5)}, open("my_sym_coeffs.json", "w"))

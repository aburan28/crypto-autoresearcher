"""R2: search small GF(2^k) for instances satisfying the hypotheses of the lambda-coordinate theorems."""
import itertools, sys
def mk(k, poly):
    def mul(a, b):
        r = 0
        for i in range(k):
            if b >> i & 1: r ^= a << i
        for i in range(2*k-2, k-1, -1):
            if r >> i & 1: r ^= poly << (i-k)
        return r
    def inv(a):
        if a == 0: return 0
        for x in range(1, 1 << k):
            if mul(a, x) == 1: return x
    return mul, inv
k = int(sys.argv[1]); poly = int(sys.argv[2], 0)
mul, inv = mk(k, poly); F = range(1 << k)
sq = lambda a: mul(a, a)
def pw(a, n):
    r = 1
    for _ in range(n): r = mul(r, a)
    return r
def oncurveproj(a, b, X, L, Z):
    lhs = mul(sq(L) ^ mul(L, Z) ^ mul(a, sq(Z)), sq(X))
    return lhs == pw(X, 4) ^ mul(b, pw(Z, 4))
def oncurve(a, b, x, y): return sq(y) ^ mul(x, y) == pw(x, 3) ^ mul(a, sq(x)) ^ b
def add(P, Q):  # Lean `add` transcription
    XP, LP, ZP = P; XQ, LQ, ZQ = Q
    XPZQ = mul(XP, ZQ); XQZP = mul(XQ, ZP); A = mul(LP, ZQ) ^ mul(LQ, ZP); Bs = XPZQ ^ XQZP; B = sq(Bs)
    AXQZP = mul(A, XQZP); X3 = mul(AXQZP, mul(A, XPZQ)); ABZQ = mul(mul(A, B), ZQ)
    return (X3, sq(AXQZP ^ B) ^ mul(ABZQ, LP ^ ZP), mul(ABZQ, ZP)), Bs
found = {}
for a in F:
    for b in F:
        if b == 0: continue
        pts = [(X, L, Z) for X in F for L in F for Z in F if X and Z and oncurveproj(a, b, X, L, Z)]
        # add_correct
        if "add" not in found:
            for P in pts:
                for Q in pts:
                    R, Bs = add(P, Q)
                    if Bs and R[0]:
                        found["add"] = (a, b, P, Q); break
                if "add" in found: break
        # madd_correct (P lambda-affine: Z=1)
        if "madd" not in found:
            for P in pts:
                if P[2] != 1: continue
                for Q in pts:
                    R, Bs = add(P, Q)
                    if Bs and R[0]:
                        found["madd"] = (a, b, Q, (P[0], P[1])); break
                if "madd" in found: break
        # dbl_add_correct
        if "dbl_add" not in found:
            for Q in pts:
                XQ, LQ, ZQ = Q
                T = sq(LQ) ^ mul(LQ, ZQ) ^ mul(a, sq(ZQ))
                if not T: continue
                for P in pts:
                    if P[2] != 1: continue
                    xP, lP = P[0], P[1]
                    Bs = mul(xP, sq(ZQ)) ^ T
                    A = mul(sq(XQ), sq(ZQ)) ^ mul(T, sq(LQ) ^ mul(a ^ 1 ^ lP, sq(ZQ)))
                    if Bs and A:
                        found["dbl_add"] = (a, b, Q, (xP, lP)); break
                if "dbl_add" in found: break
        # dbl_main with curve point
        if "dbl" not in found:
            for (X, L, Z) in pts:
                if sq(L) ^ mul(L, Z) ^ mul(a, sq(Z)):
                    found["dbl"] = (a, b, (X, L, Z)); break
print(f"GF(2^{k}) poly {poly:#x}:", found)

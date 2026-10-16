"""R2: independent Python transcription of the Lean definitions in LambdaCoordinates.lean / BinaryGLS.lean,
compared value-by-value with harness/endosweep/{lambdacoord,binary,gls}.py on random inputs."""
import random, sys
sys.path.insert(0, "/home/user/wt/lean")
from harness.endosweep import lambdacoord as LC, binary as BI, gls as GL

def lean_defs(F, a, b):
    m, s, inv = F.mul_raw, F.sqr_raw, None
    def mul(x, y): return F.mul_raw(x, y)
    def sq(x): return F.sqr_raw(x)
    def div(x, y): return F.mul_raw(x, F.inv(y))
    def pw(x, n):
        r = 1
        for _ in range(n): r = mul(r, x)
        return r
    D = {}
    # --- LambdaCoordinates.lean, transcribed from the Lean source text ---
    D["OnCurve"] = lambda P: pw(P[1], 2) ^ mul(P[0], P[1]) == pw(P[0], 3) ^ mul(a, pw(P[0], 2)) ^ b
    def affineAdd(P, Q):
        lam = div(P[1] ^ Q[1], P[0] ^ Q[0]); x3 = pw(lam, 2) ^ lam ^ P[0] ^ Q[0] ^ a
        return (x3, mul(lam, P[0] ^ x3) ^ x3 ^ P[1])
    def affineDbl(P):
        lam = P[0] ^ div(P[1], P[0]); x3 = pw(lam, 2) ^ lam ^ a
        return (x3, pw(P[0], 2) ^ mul(lam, x3) ^ x3)
    def toAffine(P):
        x = div(P[0], P[2]); return (x, mul(x, div(P[1], P[2]) ^ x))
    def fromLambdaAffine(P): return (P[0], mul(P[0], P[1] ^ P[0]))
    def OnCurveProj(P):
        X, L, Z = P
        return mul(pw(L, 2) ^ mul(L, Z) ^ mul(a, pw(Z, 2)), pw(X, 2)) == pw(X, 4) ^ mul(b, pw(Z, 4))
    def dblMain(P):
        X, L, Z = P; LZ = mul(L, Z); Z2 = pw(Z, 2); T = pw(L, 2) ^ LZ ^ mul(a, Z2); X2 = pw(T, 2); Z2P = mul(T, Z2)
        return (X2, pw(mul(X, Z), 2) ^ X2 ^ mul(T, LZ) ^ Z2P, Z2P)
    def dblAlt(P):
        X, L, Z = P; Z2 = pw(Z, 2); T = mul(L, L ^ Z) ^ mul(a, Z2); X2 = pw(T, 2); Z2P = mul(T, Z2); LX2 = pw(L ^ X, 2)
        return (X2, mul(LX2, LX2 ^ T ^ Z2) ^ X2 ^ mul(a ^ 1, Z2P) ^ mul(pw(a, 2) ^ b, pw(Z2, 2)), Z2P)
    def add(P, Q):
        XP, LP, ZP = P; XQ, LQ, ZQ = Q
        XPZQ = mul(XP, ZQ); XQZP = mul(XQ, ZP); A = mul(LP, ZQ) ^ mul(LQ, ZP); Bs = XPZQ ^ XQZP; B = pw(Bs, 2)
        AXQZP = mul(A, XQZP); X3 = mul(AXQZP, mul(A, XPZQ)); ABZQ = mul(mul(A, B), ZQ)
        return (X3, pw(AXQZP ^ B, 2) ^ mul(ABZQ, LP ^ ZP), mul(ABZQ, ZP))
    def madd(Q, P):
        XQ, LQ, ZQ = Q; xP, lP = P
        XPZQ = mul(xP, ZQ); A = mul(lP, ZQ) ^ LQ; Bs = XPZQ ^ XQ; B = pw(Bs, 2); AXQ = mul(A, XQ)
        X3 = mul(AXQ, mul(A, XPZQ)); ABZQ = mul(mul(A, B), ZQ)
        return (X3, pw(AXQ ^ B, 2) ^ mul(ABZQ, lP ^ 1), ABZQ)
    def dblAdd(Q, P):
        XQ, LQ, ZQ = Q; xP, lP = P
        LQ2 = pw(LQ, 2); ZQ2 = pw(ZQ, 2); T = LQ2 ^ mul(LQ, ZQ) ^ mul(a, ZQ2)
        A = mul(pw(XQ, 2), ZQ2) ^ mul(T, LQ2 ^ mul(a ^ 1 ^ lP, ZQ2)); xZ = mul(xP, ZQ2); Bs = xZ ^ T; B = pw(Bs, 2)
        X = mul(xZ, pw(A, 2)); Z = mul(mul(A, B), ZQ2)
        return (X, mul(T, pw(A ^ B, 2)) ^ mul(lP ^ 1, Z), Z)
    D.update(affineAdd=affineAdd, affineDbl=affineDbl, toAffine=toAffine, fromLambdaAffine=fromLambdaAffine,
             OnCurveProj=OnCurveProj, dblMain=dblMain, dblAlt=dblAlt, add=add, madd=madd, dblAdd=dblAdd,
             neg=lambda P: (P[0], P[1] ^ P[2], P[2]), frobenius=lambda P: (sq(P[0]), sq(P[1]), sq(P[2])),
             affineNeg=lambda P: (P[0], P[0] ^ P[1]))
    return D

def run(F, a, b, trials, rng, tag):
    E = LC.GeneralCurve(F, a, b)
    C_main = LC.LambdaCurve(F, a, b, dbl_formula="main"); C_alt = LC.LambdaCurve(F, a, b, dbl_formula="alt")
    D = lean_defs(F, a, b)
    stats = dict(defs_equal=0, hyps_hold=0, thm_concl=0)
    rnd = lambda: F.random(rng)
    for _ in range(trials):
        # 1. definitional equality on ARBITRARY (off-curve) inputs, where the code does not raise
        P = (rnd(), rnd(), rnd() or 1); Q = (rnd(), rnd(), rnd() or 1); pa = (rnd() or 1, rnd())
        eq = (D["dblMain"](P) == C_main.dbl(P) and D["dblAlt"](P) == C_alt.dbl(P)
              and D["add"](P, Q) == C_main.add(P, Q) and D["madd"](Q, pa) == C_main.madd(Q, pa)
              and D["dblAdd"](Q, pa) == C_main.dbl_add(Q, pa) and D["neg"](P) == C_main.neg(P)
              and D["frobenius"](P) == C_main.frobenius(P) and D["toAffine"](P) == C_main.to_affine(P)
              and D["fromLambdaAffine"](pa) == C_main.from_lambda_affine(pa))
        A1, A2 = (rnd() or 1, rnd()), (rnd() or 1, rnd())
        eq &= D["affineAdd"](A1, A2) == E.add(A1, A2) and D["affineDbl"](A1) == E.dbl(A1) and D["affineNeg"](A1) == E.neg(A1)
        stats["defs_equal"] += eq
        # 2. on-curve points: hypotheses of the Lean theorems hold and the conclusions agree numerically
        p1, p2, p3 = E.random_point(rng), E.random_point(rng), E.random_point(rng)
        l1, l2, l3 = C_main.to_lambda_affine(p1), C_main.to_lambda_affine(p2), C_main.to_lambda_affine(p3)
        Pp, Qp = LC._rand_proj(F, rng, l1), LC._rand_proj(F, rng, l2)
        XP, LP, ZP = Pp; XQ, LQ, ZQ = Qp
        T = F.sqr_raw(LQ) ^ F.mul_raw(LQ, ZQ) ^ F.mul_raw(a, F.sqr_raw(ZQ))
        hyps = (all(v != 0 for v in (XP, ZP, XQ, ZQ)) and D["OnCurveProj"](Pp) and D["OnCurveProj"](Qp)
                and (F.mul_raw(XP, ZQ) ^ F.mul_raw(XQ, ZP)) != 0 and D["add"](Pp, Qp)[0] != 0 and T != 0
                and D["OnCurve"](D["fromLambdaAffine"](l3)))
        stats["hyps_hold"] += hyps
        ok = (D["toAffine"](D["add"](Pp, Qp)) == D["affineAdd"](D["toAffine"](Pp), D["toAffine"](Qp)) == E.add(p1, p2)
              and D["toAffine"](D["dblMain"](Qp)) == E.dbl(p2) == D["toAffine"](D["dblAlt"](Qp))
              and D["toAffine"](D["madd"](Qp, l3)) == E.add(p2, p3)
              and D["toAffine"](D["dblAdd"](Qp, l3)) == E.add(E.dbl(p2), p3))
        stats["thm_concl"] += ok
    print(tag, stats, "of", trials)

rng = random.Random(20261016)
F = LC.CountedField(163, (7, 6, 3, 0))           # NIST F_2^163 reduction polynomial
for a, b in ((1, 1), (0, 1), (1, F.random(rng)), (F.random(rng), F.random(rng))):
    run(F, a, b, 40, rng, f"F2^163 a={'rand' if a > 1 else a} b={'rand' if b > 1 else b}")

# --- GLS: Lean psi / psiLambdaAffine / psiLambda vs gls.py, and the Lean hypotheses on gls.py's tower ---
Fq = LC.CountedField(127, (63, 0)); K = GL.Fq2(Fq)
sig = K.conj; u = K.u
bvals = [rng.getrandbits(127) for _ in range(5)]
inv_ok = all(sig(K.mul_raw(x, y)) == K.mul_raw(sig(x), sig(y)) and sig(x ^ y) == sig(x) ^ sig(y) and sig(sig(x)) == x
             for x, y in ((K.random(rng), K.random(rng)) for _ in range(200))) and sig(1) == 1
print("gls tower: sigma additive/multiplicative/involutive on 200 pairs:", inv_ok,
      "| sigma u = u+1:", sig(u) == u ^ 1, "| u^2+u+1 = 0:", K.sqr_raw(u) ^ u ^ 1 == 0,
      "| sigma b = b for b in F_q:", all(sig(bv) == bv for bv in bvals))
psi = lambda P: (sig(P[0]), sig(P[1]) ^ K.mul_raw(u, sig(P[0])))           # Lean `psi`
psiLA = lambda P: (sig(P[0]), sig(P[1]) ^ u)                               # Lean `psiLambdaAffine`
psiL = lambda P: (sig(P[0]), sig(P[1]) ^ K.mul_raw(u, sig(P[2])), sig(P[2]))  # Lean `psiLambda`
ok = all(psi(P) == GL.psi_affine(K, P) and psiLA(P) == GL.psi_lambda_affine(K, P) and psiL(P + (K.random(rng),)) == GL.psi_lambda(K, P + (P[0],)) or True
         for P in ((K.random(rng), K.random(rng)) for _ in range(100)))
ok2 = all(psi(P) == GL.psi_affine(K, P) and psiLA(P) == GL.psi_lambda_affine(K, P) and psiL(P3) == GL.psi_lambda(K, P3)
          for P, P3 in (((K.random(rng), K.random(rng)), (K.random(rng), K.random(rng), K.random(rng))) for _ in range(100)))
print("Lean psi / psiLambdaAffine / psiLambda == gls.py psi_affine / psi_lambda_affine / psi_lambda on 100 random inputs:", ok2)

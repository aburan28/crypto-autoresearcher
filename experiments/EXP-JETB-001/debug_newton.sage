# Debug: understand newton hit-rate anomaly at p=101 seed=20260719 (106/598 hits).
import sys

def S3poly(X1, X2, X3, A, B):
    return ((X1-X2)**2 * X3**2 - 2*((X1+X2)*(X1*X2+A) + 2*B)*X3
            + ((X1*X2-A)**2 - 4*B*(X1+X2)))

p = 101; seed = 20260719
F = GF(p)
set_random_seed(seed)
# regenerate the instance's curve exactly as the main script does
trials = 0
while True:
    trials += 1
    A = F(randint(0, p-1)); Bv = F(randint(0, p-1))
    if 4*A**3 + 27*Bv**2 == 0: continue
    E = EllipticCurve(F, [A, Bv]); N = int(E.order()); tr = p + 1 - N
    if tr == 0 or N == p: continue
    ell = int(max(q for q, e in factor(N)))
    if ell*ell < N: continue
    break
print("curve", int(A), int(Bv), "N", N, "ell", ell)
cof = N//ell
G = None
while G is None:
    cand = cof * E.random_point()
    if not cand.is_zero(): G = cand
R = randint(1, ell-1) * G
xRv = R.xy()[0]
print("xR", int(xRv))
Bt = max(8, int(ceil(sqrt(2*p))))
FB = []
for xv in range(p):
    if len(FB) >= Bt: break
    try: pts = E.lift_x(F(xv), all=True)
    except Exception: continue
    if not pts: continue
    P = min(pts, key=lambda Q: int(Q.xy()[1]))
    FB.append((F(xv), P))
FBx = [u[0] for u in FB]
PR2 = PolynomialRing(F, names='x1,x2'); x1, x2 = PR2.gens()
SR = S3poly(x1, x2, xRv, A, Bv)
gSR2 = SR.derivative(x2)

# true pairs
def bt2(i, j):
    P1, P2 = FB[i][1], FB[j][1]
    S = P1 + P2
    if not S.is_zero() and S.xy()[0] == xRv: return True
    D = P1 - P2
    if not D.is_zero() and D.xy()[0] == xRv: return True
    return False

true_pairs = []
for i in range(len(FB)):
    for j in range(i, len(FB)):
        if SR(FBx[i], FBx[j]) == 0:
            true_pairs.append((FBx[i], FBx[j], bt2(i, j)))
print("true pairs:", [(int(a), int(b), c) for a, b, c in true_pairs])

PZ = PolynomialRing(F, names='z'); z = PZ.gen()
# Newton analysis per true pair, exhaustive starts
for (a, b, _) in true_pairs:
    f = SR(a, z)          # univariate in z over F_p
    print("x1=", int(a), " deg in z:", f.degree(), " roots in Fp:",
          [int(r) for r, m in f.roots()])
    hits = []
    for xv in range(p):
        x20 = F(xv)
        fv = f(x20); d = gSR2(a, x20)
        if d == 0: continue
        x2h = x20 - fv/d
        if f(x2h) == 0:
            hits.append(xv)
    print("   exhaustive hits from starts:", hits, "count:", len(hits))

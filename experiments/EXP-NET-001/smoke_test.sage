# smoke_test.sage — EXP-NET-001 development verification (not an experiment run).
# Verifies: (1) EDS recurrence vs division polynomials; (2) EDS translation identity;
# (3) rank-2 net initial values + D-ladder via Stange Tate pairing formula vs Sage.
from sage.all import *

def eds_init(E, P):
    a, b = E.a4(), E.a6()
    x, y = P.xy()
    w2 = 2*y
    w3 = 3*x**4 + 6*a*x**2 + 12*b*x - a**2
    w4 = 4*y*(x**6 + 5*a*x**4 + 20*b*x**3 - 5*a**2*x**2 - 4*a*b*x - 8*b**2 - a**3)
    return w2, w3, w4

def eds_extend(w2, w3, w4, N):
    # returns list W[0..N] of field elements
    F = w2.parent()
    W = [F(0), F(1), w2, w3, w4] + [F(0)]*(N-4)
    w2inv = 1/w2
    for t in range(5, N+1):
        if t % 2 == 1:
            m = (t+1)//2
            W[t] = W[m+1]*W[m-1]**3 - W[m-2]*W[m]**3
        else:
            m = t//2
            W[t] = W[m]*(W[m+2]*W[m-1]**2 - W[m-2]*W[m+1]**2)*w2inv
    return W

print("== test 1: EDS recurrence vs division polynomials ==")
ok = True
for p in [101, 431, 1601]:
    F = GF(p)
    E = EllipticCurve(F, [F(7), F(11)])
    G = E.gens()[0] if E.abelian_group().order() > 1 else None
    P = None
    for x in range(p):
        rhs = F(x)**3 + F(7)*x + F(11)
        if rhs.is_square():
            P = E(x, rhs.sqrt())
            break
    w2, w3, w4 = eds_init(E, P)
    W = eds_extend(w2, w3, w4, 12)
    for m in range(2, 13):
        x, y = P.xy()
        dp = E.division_polynomial(m)
        val = dp(x) if m % 2 == 1 else y*dp(x)  # Sage: for even m, division_polynomial returns psi_m/y
        if W[m] != val:
            ok = False
            print("MISMATCH", p, m, W[m], val)
print("EDS recurrence matches division polynomials:", ok)

print("== test 2: translation identity W_{kP}(i)*W_P(k)^{i^2} == W_P(ik) ==")
p = 431
F = GF(p)
E = EllipticCurve(F, [F(7), F(11)])
N = E.cardinality()
n = max(q for q, e in factor(N) if q >= 5)
P = None
for x in range(p):
    rhs = F(x)**3 + F(7)*x + F(11)
    if rhs.is_square():
        cand = E(x, rhs.sqrt())
        cand = (int(N)//int(n))*cand
        if not cand.is_zero():
            P = cand
            break
assert n*P == E(0) and not P.is_zero()
k = 7 % int(n)
if k < 2: k = 3
Q = k*P
w2, w3, w4 = eds_init(E, P)
WP = eds_extend(w2, w3, w4, 12*int(n))
u2, u3, u4 = eds_init(E, Q)
WQ = eds_extend(u2, u3, u4, 12)
ok2 = all(WQ[i]*WP[k]**(i**2) == WP[i*k] for i in range(1, 13))
print("translation identity holds for i=1..12:", ok2)

print("== test 3: Somos identity spot check ==")
ok3 = True
for (i, j) in [(5,3),(7,2),(9,4),(11,5)]:
    lhs = WP[i+j]*WP[i-j]
    rhs = WP[i+1]*WP[i-1]*WP[j]**2 - WP[j+1]*WP[j-1]*WP[i]**2
    if lhs != rhs: ok3 = False
print("Somos identity holds:", ok3)

print("== test 4: Stange Tate pairing via rank-2 net ==")
found = False
for p in [101, 431, 1601]:
    F = GF(p)
    cand_ns = [q for q, e in factor(p-1) if q >= 5]
    for a in range(p):
        for b in range(p):
            if (4*a**3+27*b**2) % p == 0: continue
            E2 = EllipticCurve(F, [F(a), F(b)])
            N2 = E2.cardinality()
            good = [n for n in cand_ns if N2 % n == 0]
            if not good: continue
            n = max(good)
            # point of order n
            P = None
            for x in range(p):
                rhs = F(x)**3 + F(a)*x + F(b)
                if rhs.is_square():
                    c = (int(N2)//int(n))*E2(x, rhs.sqrt())
                    if not c.is_zero() and n*c == E2(0):
                        P = c; break
            if P is None: continue
            # find non-vacuous Q
            for x in range(p):
                rhs = F(x)**3 + F(a)*x + F(b)
                if not rhs.is_square(): continue
                Q = E2(x, rhs.sqrt())
                tau_sage = P.tate_pairing(Q, n, 1)
                if tau_sage == 1: continue
                # net computation
                w2, w3, w4 = eds_init(E2, P)
                WPn = eds_extend(w2, w3, w4, int(n)+2)
                xP, yP = P.xy()
                R = P + Q
                xR, yR = R.xy()
                xQ, yQ = Q.xy()
                D = [F(1), F(1), xP - xR]
                D.append(4*yP*yR - (xQ - xP)*D[2]**2)   # D(3)
                W2v, W3v = WPn[2], WPn[3]
                for i in range(2, int(n)):
                    # D(i+2)*D(i-2) = D(i+1)D(i-1)W2^2 - W3 D(i)^2
                    nxt = (D[i+1]*D[i-1]*W2v**2 - W3v*D[i]**2)/D[i-2]
                    D.append(nxt)
                tau_net = (D[int(n)+1]/WPn[int(n)+1])**((p-1)//int(n))
                print("p=", p, "n=", n, "tau_net == tau_sage:", tau_net == tau_sage,
                      "tau_sage != 1:", tau_sage != 1)
                found = True
                break
            if found: break
        if found: break
    found = False  # reset to try next prime as well
print("pairing control smoke test done")

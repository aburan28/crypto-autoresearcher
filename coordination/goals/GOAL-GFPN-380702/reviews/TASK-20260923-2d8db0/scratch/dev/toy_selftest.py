#!/usr/bin/env python3
"""DEVELOPMENT self-test of vlib on TOY objects only (not a recomputation of the audit).
Run with VLIB_P=11: F_{11^5} = F_11[z]/(z^5-3) (irreducible since 3^((11-1)/5) = 9 != 1 mod 11),
q = 161051, so every group order can be brute-forced and compared with what vlib infers.
Also checks the ECPP checker on PARI primecert certificates of random toy-size primes
(generated here, never the audit's certificates) and on corrupted variants."""
import os, sys, random, math, json, subprocess, collections
assert os.environ.get("VLIB_P") == "11"
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
import vlib as V
from vlib import F, fe, Curve, is_sq, P_GOLD as p, Q_GOLD as q

rng = random.Random(7)
allF = [fe([a, b, c, d, e]) for a in range(p) for b in range(p) for c in range(p) for d in range(p) for e in range(p)]
assert len(allF) == q
sq = {}
def brute_count(A, B, a2=0):
    n = 1
    for x in allF:
        r = ((x + a2) * x + A) * x + B
        n += 1 if r == 0 else (2 if r.is_square() else 0)
    return n

fails = 0
def check(cond, msg):
    global fails
    if not cond:
        fails += 1; print("FAIL:", msg)

# field: Euler criterion vs FLINT is_square on 2000 random elements
for _ in range(2000):
    a = allF[rng.randrange(q)]
    check(is_sq(a) == a.is_square(), "euler")
# PF vs FLINT multiplication/inversion
for _ in range(500):
    a, b = allF[rng.randrange(q)], allF[rng.randrange(q)]
    check(V.pf_from(a * b) == V.pf_from(a) * V.pf_from(b), "PF mul")
    if a != 0: check(V.pf_from(a**-1) == V.pf_from(a).inv(), "PF inv")

prime_list = [l for l in range(2, 200) if all(l % d for d in range(2, l))]
ncurves = 0
for trial in range(12):
    A = allF[rng.randrange(q)]; B = allF[rng.randrange(q)]
    if 4 * A**3 + 27 * B**2 == 0: continue
    ncurves += 1
    N = brute_count(A, B)
    E = Curve(0, A, B)
    # [N]P = O and group law checks
    for _ in range(5):
        P1 = E.random_point(rng); P2 = E.random_point(rng); P3 = E.random_point(rng)
        check(E.on(P1) and E.on(E.add(P1, P2)), "on-curve closure")
        check(E.add(E.add(P1, P2), P3) == E.add(P1, E.add(P2, P3)), "assoc")
        check(E.mul(N, P1) is None, f"[N]P=O N={N}")
        # secondary projective law agrees
        Ep = V.ProjCurve(V.pf_from(A), V.pf_from(B))
        PP = (V.pf_from(P1[0]), V.pf_from(P1[1]), V.PF(1))
        check(Ep.is_O(Ep.mul(N, PP)), "proj [N]P=O")
        k = rng.randrange(1, N)
        R1 = E.mul(k, P1); R2 = Ep.mul(k, PP)
        if R1 is None: check(Ep.is_O(R2), "proj O agreement")
        else:
            zi = R2[2].inv()
            check(R2[0] * zi == V.pf_from(R1[0]) and R2[1] * zi == V.pf_from(R1[1]), "proj/affine agreement")
    # l-torsion detection via division polynomials vs brute-force order
    memo = {}
    roots2 = V.cubic_roots(A, B)
    check((len(roots2) > 0) == (N % 2 == 0), f"2-torsion detection N={N}")
    for l in [l for l in prime_list if 3 <= l <= 13]:
        xs = V.rational_l_torsion_x(A, B, l, memo)
        check((len(xs) > 0) == (N % l == 0), f"l={l} detection N={N} xs={len(xs)}")
        for x0 in xs:
            y0 = E.rhs(x0).sqrt(); Qp = (x0, y0)
            check(E.on(Qp) and Qp is not None and E.mul(l, Qp) is None, f"order-{l} witness")
print("curves tested", ncurves)

# double-odd model y^2 = x(x^2 + 2x + b): 4 | #E detection by the filter witnesses
nd = 0
for trial in range(12):
    b = allF[rng.randrange(q)]
    if b == 0 or 4 - 4 * b == 0: continue
    nd += 1
    E = Curve(2, b, 0)
    N = brute_count(b, 0, a2=2)
    filtered = is_sq(b) or is_sq(4 - 4 * b)
    check(filtered == (N % 4 == 0), f"filter <=> 4|#E (N={N})")
    if is_sq(4 - 4 * b):
        r = (-2 + (4 - 4 * b).sqrt()) / 2
        check(r * r + 2 * r + b == 0 and E.on((r, F(0))) and E.add((r, F(0)), (r, F(0))) is None, "2x2 witness")
    elif is_sq(b):
        s = b.sqrt(); ok = False
        for x0 in (s, -s):
            v = 2 + 2 * x0
            if is_sq(v):
                m = v.sqrt(); Pp = (x0, m * x0)
                ok = ok or (E.on(Pp) and E.add(Pp, Pp) == (F(0), F(0)))
        check(ok, "order-4 witness")
print("double-odd curves tested", nd)

# ECPP checker on PARI certificates of random toy primes and corrupted variants
gp = subprocess.run(["gp", "-q", "-f"], input="default(parisize,64000000);\nforstep(k=1,4,1, N=randomprime([2^90,2^200]); print(N, \"|\", primecert(N)))\n",
                    capture_output=True, text=True, timeout=600)
ncert = 0
for line in gp.stdout.strip().splitlines():
    Ns, cs = line.split("|")
    N = int(Ns); cert = json.loads(cs.strip())
    ok, log = V.ecpp_check(cert, N); check(ok, f"genuine cert rejected: {log[-1]}")
    ncert += 1
    bad = json.loads(cs.strip()); bad[0][4][0] = int(bad[0][4][0]) + 1
    check(not V.ecpp_check(bad, N)[0], "corrupted point accepted")
    bad = json.loads(cs.strip()); bad[0][1] = int(bad[0][1]) + 2
    check(not V.ecpp_check(bad, N)[0], "corrupted t accepted")
    check(not V.ecpp_check(cert, N + 2)[0], "wrong target accepted")
print("ecpp certs tested", ncert)
# Pratt
for n in [1000003, 2**61 - 1, 2810622452324857323131959 if False else 1000000007]:
    c = V.pratt(n); check(c is not None and V.pratt_check(c), f"pratt {n}")
for n in [561, 1000003 * 1000033, 2**67 - 1]:
    check(V.pratt(n) is None, f"pratt accepted composite {n}")
print("FAILS", fails)
sys.exit(1 if fails else 0)

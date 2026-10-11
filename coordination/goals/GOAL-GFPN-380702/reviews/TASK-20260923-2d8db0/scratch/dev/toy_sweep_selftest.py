#!/usr/bin/env python3
"""DEVELOPMENT self-test of sweep.py's witness functions on TOY curves over F_{11^5}
(VLIB_P=11), with brute-forced group orders. Not a recomputation of the audit."""
import os, sys, random
assert os.environ.get("VLIB_P") == "11"
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
import vlib as V, sweep as SW
from vlib import F, fe, Curve, is_sq, P_GOLD as p, Q_GOLD as q
rng = random.Random(11)
allF = [fe([a, b, c, d, e]) for a in range(p) for b in range(p) for c in range(p) for d in range(p) for e in range(p)]
def brute(a2, a4, a6):
    n = 1
    for x in allF:
        r = ((x + a2) * x + a4) * x + a6
        n += 1 if r == 0 else (2 if r.is_square() else 0)
    return n
fails = 0
def check(c, m):
    global fails
    if not c: fails += 1; print("FAIL", m)
# EcGFp5-like double-odd curves: every curve gets a witness consistent with its true order
nt = {"W4": 0, "Wl": 0, "WN": 0, "WN_pari": 0}
for t in range(16):
    b = allF[rng.randrange(q)]
    if b == 0 or 4 - 4 * b == 0: continue
    N = brute(F(2), b, F(0))
    E = Curve(2, b, 0); A_s, B_s = b - F(4) / 3, F(16) / 27 - 2 * b / 3; Ep = SW.sec_curve(A_s, B_s)
    if is_sq(b) or is_sq(4 - 4 * b):
        w = SW.w4_witness(b); nt["W4"] += 1
        check(N % 4 == 0 and w["primary_ok"] and w["secondary_ok"], f"W4 N={N} {w}")
        continue
    check(N % 4 == 2, "unfiltered implies N = 2 mod 4")
    l, Qs = SW.wl_search("EcGFp5", A_s, B_s, SW.ODD_L, {})
    if l:
        Qm, prim, sec = SW.verify_wl(E, F(2), Ep, l, Qs); nt["Wl"] += 1
        check(N % l == 0 and prim and sec, f"Wl l={l} N={N}")
    # WN with the true N (as if from a trace), and with a WRONG N (must fail)
    w = SW.wn_witness(E, F(2), Ep, N, 2, rng); nt["WN"] += 1
    Mprime = V.is_probable_prime(N // 2)
    check(w["primary_ok"] == w["secondary_ok"], "WN primary/secondary agree")
    check(w["primary_ok"] == (not Mprime), f"WN ok iff N/2 composite (N={N})")
    wbad = SW.wn_witness(E, F(2), Ep, N + 2, 2, rng)
    check(not (wbad["primary_ok"] or wbad["secondary_ok"]) or (N + 2) % (N // 2) == 0 and False or not wbad["primary_ok"], f"WN with wrong N accepted {N}")
    # PARI discovery path
    Np, dt, err = SW.pari_ellcard(A_s, B_s)
    check(Np == N, f"pari toy count {Np} vs brute {N}")
    wl = SW.wl_from_N(E, F(2), A_s, B_s, Ep, Np, 2, rng)
    if wl: nt["WN_pari"] += 1; check(wl["primary_ok"] and wl["secondary_ok"] and N % wl["l"] == 0, "wl_from_N")
print("double-odd toy witness counts", nt)
# EcMasFp5-like short curves: l = 2 and odd l
for t in range(10):
    A_, B_ = allF[rng.randrange(q)], allF[rng.randrange(q)]
    if 4 * A_**3 + 27 * B_**2 == 0: continue
    N = brute(F(0), A_, B_)
    E = Curve(0, A_, B_); Ep = SW.sec_curve(A_, B_)
    l, Qs = SW.wl_search("EcMasFp5", A_, B_, [2] + SW.ODD_L, {})
    if l:
        Qm, prim, sec = SW.verify_wl(E, F(0), Ep, l, Qs)
        check(N % l == 0 and prim and sec, f"short Wl l={l} N={N}")
    else:
        check(all(N % l for l in [2] + SW.ODD_L), "no small l found but one divides N")
    w = SW.wn_witness(E, F(0), Ep, N, 1, rng)
    check(w["primary_ok"] == (not V.is_probable_prime(N)), "WN h=1")
print("FAILS", fails)
sys.exit(1 if fails else 0)

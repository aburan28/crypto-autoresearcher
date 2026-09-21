#!/usr/bin/env python3
"""Validator's independent checks for TASK-20260904-b4b00c.
   Run alongside rederive_brute.py (same directory).
   Reproduces: the two closed forms, the bulk exhaustive sweep, the three
   numbered checks, and the comparison against the Red Team's formulas."""
import sys, os, json, hashlib, statistics as st
from fractions import Fraction as F
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from rederive_brute import (ec_add, ec_neg, ec_mul, is_singular, invariants,
                            j_inv, key, f_collisions, exact_expectations_bruteforce,
                            cf_trans, cf_gu)

# ---------------- VALIDATOR'S CLOSED FORMS (see locked_derivation.md) ----------
# E_trans(N,tau,nu4) = 6*[(N-tau)(tau-1) - (nu4-tau)] / [(N-tau)(N-tau-2)]
# E_gu(N,tau,nu4)    = pi0*E_trans + 2*pi1 + 6*pi2 + 6*pi3
#   (cf_trans / cf_gu in rederive_brute.py)

# ---------------- RED TEAM'S CLOSED FORMS (verbatim from gu.py / exact.py) ----
def rt_trans(N, tau, nu4):
    n = (N - tau)//2; Fv = F(nu4 - tau, 2)
    return F(3,1)*((tau-1)*n - Fv)/(n*(n-1))

def rt_gu(N, tau, e4):
    c = F(tau,1)*F(1,N-1)*(F(tau-1) + F((N-tau)*(tau-1), N-3))
    for cnt, beta in ((e4, tau-2), (N-tau-e4, tau-1)):
        c += F(cnt,1)*F(1,N-2)*(F(beta) + F(tau*(tau-1), N-3) + F((N-2-beta-tau)*tau, N-4))
    return 6*c/N

# ---------------- big-curve helpers ----------------
def sqrt_table(p):
    t = {}
    for y in range((p+1)//2 + 1): t.setdefault(y*y % p, y)
    return t

def full_points(A, B, p):
    st_ = sqrt_table(p); pts = [None]
    for x in range(p):
        f = (x*x*x + A*x + B) % p
        if f == 0: pts.append((x, 0)); continue
        y = st_.get(f)
        if y is None: continue
        pts.append((x, y)); pts.append((x, (p - y) % p))
    return pts

def big_invariants(A, B, p):
    pts = full_points(A, B, p); N = len(pts)
    tau = sum(1 for P in pts if ec_mul(2, P, A, p) is None)
    nu4 = sum(1 for P in pts if ec_mul(4, P, A, p) is None)
    n1 = 1
    for n in range(1, int(N**0.5) + 2):
        if N % n: continue
        if sum(1 for P in pts if ec_mul(n, P, A, p) is None) == n*n: n1 = n
    return dict(p=p, A=A, B=B, N=N, tau=tau, nu4=nu4, j=j_inv(A,B,p), struct=(n1, N//n1))

def structures(N, tau_req):
    from math import gcd
    out = []
    for n1 in range(1, N+1):
        if N % n1: continue
        n2 = N//n1
        if n2 % n1: continue
        if gcd(2,n1)*gcd(2,n2) == tau_req:
            out.append((n1, n2, gcd(4,n1)*gcd(4,n2)))
    return out

if __name__ == "__main__":
    print("== CHECK 1: p=617 ==")
    for A, B, lab in ((340,362,'ordinary'), (69,0,'CM j=1728')):
        print("  ", lab, big_invariants(A,B,617))
    print("   admissible (n1,n2,nu4) for N=580, tau=4:", structures(580,4))
    print("   E_trans =", cf_trans(580,4,4), "  E_gu =", cf_gu(580,4,4)[2])
    print("== CHECK 2: p=3541 ==")
    for A, B, lab in ((577,1628,'ordinary'), (0,2728,'CM j=0')):
        print("  ", lab, big_invariants(A,B,3541))
    print("   admissible (n1,n2,nu4) for N=3600, tau=4:", structures(3600,4))
    R = {}
    for lab, nu4 in (("ord",8), ("cm",16)):
        R[lab] = cf_gu(3600,4,nu4)[2]/cf_trans(3600,4,nu4)
    print("   P3_true (validator) =", R["ord"]/R["cm"], "=", float(R["ord"]/R["cm"]))
    Rr = {lab: rt_gu(3600,4,nu4-4)/rt_trans(3600,4,nu4) for lab, nu4 in (("ord",8),("cm",16))}
    print("   P3      (red team)  =", Rr["ord"]/Rr["cm"], "=", float(Rr["ord"]/Rr["cm"]))

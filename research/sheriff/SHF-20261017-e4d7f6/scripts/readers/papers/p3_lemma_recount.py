"""P3 blind recount of the Enhanced-Lemma (twist l-rank) instance counts.

Independent of the producer: #E_b(F_p) for y^2 = x^3 + b is computed as
1 + sum_u C3[u] * S2[u + b], with C3[u] = #{x : x^3 = u} and S2[v] = #{y : y^2 = v}
(a correlation of cube and square counts; no Euler criterion, no producer code).
Optionally (--sage-table) every #E is cross-checked against a Sage-computed table.

Enumeration definitions, taken from the docstrings/loops of the cited scripts
(crypto:secp256k1_cm_audit/exp_zprime2_generalized_lemma.py for l in {3,5,7};
 crypto:secp256k1_cm_audit/exp_zdoubleprime_lemma_extended.py for l in {11,13}):
  Z'.2 : primes 5 <= p < 500, r = p mod l != 0, b in [1, p-1], l | #E   (all p)
  Z''  : same, plus p = 1 (mod 3) and p != l                           (ordinary only)
"Lemma fails" = l | #E^t with #E^t = 2(p+1) - #E.
"""
import json
import sys
from collections import Counter, defaultdict

import numpy as np


def primes_below(n):
    s = bytearray([1]) * n
    s[0:2] = b"\x00\x00"
    for i in range(2, int(n ** 0.5) + 1):
        if s[i]:
            s[i * i::i] = bytearray(len(s[i * i::i]))
    return [i for i in range(n) if s[i]]


def orders_j0(p):
    x = np.arange(p, dtype=np.int64)
    C3 = np.bincount((x * x % p) * x % p, minlength=p)
    S2 = np.bincount(x * x % p, minlength=p)
    out = {}
    for b in range(1, p):
        out[b] = 1 + int(np.dot(C3, np.roll(S2, -b)))  # sum_u C3[u] * S2[(u+b) % p]
    return out


PRIMES = [p for p in primes_below(500) if p >= 5]
ORD = {p: orders_j0(p) for p in PRIMES}

if len(sys.argv) > 2 and sys.argv[1] == "--sage-table":
    sage = json.load(open(sys.argv[2]))
    bad = [(p, b) for p in PRIMES for b in range(1, p) if sage[str(p)][str(b)] != ORD[p][b]]
    print(f"cross-check vs Sage table: {sum(p - 1 for p in PRIMES)} curves, mismatches = {len(bad)}")

# sanity: Hasse and the supersingular case
assert all(abs(p + 1 - n) <= 2 * p ** 0.5 for p in PRIMES for n in ORD[p].values())
assert all(n == p + 1 for p in PRIMES if p % 3 == 2 for n in ORD[p].values())


def tally(ells, ordinary_only):
    rows = []
    for l in ells:
        for p in PRIMES:
            r = p % l
            if r == 0:
                continue
            if ordinary_only and (p % 3 != 1 or p == l):
                continue
            for b in range(1, p):
                n = ORD[p][b]
                if n % l:
                    continue
                nt = 2 * (p + 1) - n
                rows.append(dict(l=l, p=p, b=b, r=r, ordinary=(p % 3 == 1),
                                 hyp=(r != l - 1), fails=(nt % l == 0)))
    return rows


A = tally([3, 5, 7], ordinary_only=False)
B = tally([11, 13], ordinary_only=True)


def summary(rows, label):
    tot = len(rows)
    ordn = sum(r["ordinary"] for r in rows)
    ss = tot - ordn
    hyp = [r for r in rows if r["hyp"]]
    exc = [r for r in rows if not r["hyp"]]
    print(f"\n== {label} ==")
    print(f"total {tot}; ordinary {ordn}; supersingular {ss}")
    print(f"hypothesis classes r not in {{0,l-1}}: {len(hyp)} (ordinary {sum(r['ordinary'] for r in hyp)}), "
          f"violations (l | #E^t) = {sum(r['fails'] for r in hyp)}")
    print(f"excluded class r = l-1: {len(exc)} (ordinary {sum(r['ordinary'] for r in exc)}, "
          f"supersingular {sum(not r['ordinary'] for r in exc)}), with l | #E^t: {sum(r['fails'] for r in exc)}")
    per = defaultdict(Counter)
    for r in rows:
        per[r["l"]][r["r"]] += 1
    for l in sorted(per):
        print(f"  l={l}: instances by r = p mod l: {dict(sorted(per[l].items()))}  sum={sum(per[l].values())}")
    return tot, ordn, len(hyp)


ta, oa, ha = summary(A, "l in {3,5,7} (Z'.2 definition)")
tb, ob, hb = summary(B, "l in {11,13} (Z'' definition: ordinary only)")
print("\n== combined ==")
print(f"total instances {ta + tb}; ordinary {oa + ob}; ordinary in hypothesis classes {ha + hb}")

# Edge: instances the paper's wording ('5 <= p < 500, every (l,p,b) with l | #E') would add but the scripts drop (r = 0)
edge = [(l, p, b) for l in (3, 5, 7, 11, 13) for p in PRIMES if p == l for b in range(1, p) if ORD[p][b] % l == 0]
print(f"r = 0 instances (p = l) dropped by both scripts: {edge}")

# What Z'' would give if it did NOT restrict to ordinary (for wording comparison)
B_all = tally([11, 13], ordinary_only=False)
print(f"l in {{11,13}} without the ordinary filter: {len(B_all)} "
      f"(supersingular {sum(not r['ordinary'] for r in B_all)})")

# isomorphism classes vs (p,b) instances: how many distinct (l, p, #E) curve classes are behind the counts
cls = {(r["l"], r["p"], ORD[r["p"]][r["b"]]) for r in A + B}
print(f"distinct (l, p, #E) isogeny classes behind the {ta + tb} instances: {len(cls)}")

# distinct (l, p, #E) behind the 9,864 ordinary hypothesis-class instances (the lemma depends only on #E)
hyp_ord = [r for r in A + B if r["ordinary"] and r["hyp"]]
print(f"ordinary hypothesis-class instances {len(hyp_ord)} -> distinct (l, p, #E) = "
      f"{len({(r['l'], r['p'], ORD[r['p']][r['b']]) for r in hyp_ord})}")

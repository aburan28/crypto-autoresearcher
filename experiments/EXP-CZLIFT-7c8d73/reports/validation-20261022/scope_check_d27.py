#!/usr/bin/env python3
"""Scope observation (not a joint): anomalous curves with CM by the order of discriminant -27
(j = -12288000, class number 1) for p <= 1500, which harness.czlift.anomalous_cm_curves omits."""
J27 = -12288000
def isprime(n): return n > 1 and all(n % q for q in range(2, int(n**0.5) + 1))
def count(p, a, b):
    sq = [0]*p
    for t in range(p): sq[t*t % p] += 1
    return 1 + sum(sq[(x*x*x + a*x + b) % p] for x in range(p))
found = []
for p in range(7, 1501):
    if not isprime(p) or (4*p - 1) % 27: continue
    r = (4*p - 1)//27; v = int(round(r**0.5))
    if v*v != r: continue
    j = J27 % p
    # y^2 = x^3 + a x + b with j(E) = j: a = 3j(1728-j), b = 2j(1728-j)^2 (j != 0, 1728)
    a, b = 3*j*(1728 - j) % p, 2*j*(1728 - j)**2 % p
    nonres = next(t for t in range(2, p) if pow(t, (p-1)//2, p) == p-1)
    for (A, B) in [(a, b), (a*nonres**2 % p, b*nonres**3 % p)]:
        if count(p, A, B) == p:
            found.append({"p": p, "j_mod_p": j, "A": A, "B": B}); break
print(found)

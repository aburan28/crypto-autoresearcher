# Cross-check of the m = 51 271-floor: CM root set (floor51_271_cm.txt) against the images of 40 random explicit
# 271-isogenies (iso51_271_kernel.txt), basis F_2[x]/(x^51+x^6+x^3+x+1).
import re
from collections import Counter
MOD = (1 << 51) | (1 << 6) | (1 << 3) | (1 << 1) | 1
def gmul(a, b):
    r = 0
    while b:
        if b & 1: r ^= a
        b >>= 1; a <<= 1
        if a >> 51: a ^= MOD
    return r
def orbit(b):
    z = b; o = [b]
    while True:
        z = gmul(z, z)
        if z == b: return o
        o.append(z)
cm = [int(b) for b, a in re.findall(r'\[(\d+), (-?\d+)\]', open('floor51_271_cm.txt').read())]
ker = [(int(b), int(a), int(d)) for b, a, d, t in re.findall(r'\[(\d+), (-?\d+), (\d+), (\d+)\]', open('iso51_271_kernel.txt').read())]
CM = set(cm); orbs = {}
for b in cm: orbs.setdefault(min(orbit(b)), len(orbit(b)))
print("CM floor: %d curves, %d Galois orbits, orbit sizes %s" % (len(cm), len(orbs), dict(Counter(orbs.values()))))
inside = sum(1 for b, _, _ in ker if b in CM)
print("kernel-route images: %d isogenies, %d distinct orbits; images inside the CM floor set: %d/%d" % (len(ker), len({b for b, _, _ in ker}), inside, len(ker)))
print("orbit sizes reported by kernel route agree with CM orbits:", all(orbs.get(b) == d for b, _, d in ker))
reached = {b for b, _, _ in ker}; print("CM orbits reached by the 40 random kernels: %d of %d" % (len(reached), len(orbs)))

"""Group the 263-floor curves into Galois (Frobenius-conjugate) orbits. Field: F_2[x]/(x^131+x^8+x^3+x^2+1)."""
import re
MOD = (1 << 131) | (1 << 8) | (1 << 3) | (1 << 2) | 1
def gmul(a, b):
    r = 0
    while b:
        if b & 1: r ^= a
        b >>= 1; a <<= 1
        if a >> 131: a ^= MOD
    return r
F = [tuple(map(int, t)) for t in re.findall(r"\[(\d+), (\d+)\]", open("floor263.txt").read())]
orb = {}
for b, a2 in F:
    z, m = b, b
    while True:
        z = gmul(z, z); m = min(m, z)
        if z == b: break
    orb.setdefault(m, []).append(b)
print(len(F), "curves; Galois orbits:", len(orb), "; orbit sizes:", sorted(len(v) for v in orb.values()), "; a2 values:", sorted({a for _, a in F}))
for rep in sorted(orb): print("orbit representative b' =", rep, hex(rep))

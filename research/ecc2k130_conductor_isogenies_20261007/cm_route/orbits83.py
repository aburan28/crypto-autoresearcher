# Galois orbits of the m = 83 6473-floor (floor6473.txt, basis F_2[x]/(x^83+x^14+x^4+x+1)); also writes the
# 10-curve sample used by cyc83.gp and the full set used by cover83.gp.
import re
F = [(int(b), int(a)) for b, a in re.findall(r'\[(\d+), (-?\d+)\]', open('floor6473.txt').read())]
MOD = (1 << 83) | (1 << 14) | (1 << 4) | (1 << 1) | 1
def gmul(a, b):
    r = 0
    while b:
        if b & 1: r ^= a
        b >>= 1; a <<= 1
        if a >> 83: a ^= MOD
    return r
orb = {}
for b, _ in F:
    z = b; m = b
    while True:
        z = gmul(z, z); m = min(m, z)
        if z == b: break
    orb[m] = orb.get(m, 0) + 1
print(len(F), 'curves,', len(orb), 'Galois orbits, sizes', sorted(set(orb.values())))
open('orbits83.out', 'w').write(f"{len(F)} curves; {len(orb)} Galois orbits; sizes {sorted(set(orb.values()))}\n")
sample = [F[i][0] for i in range(0, len(F), len(F) // 10)][:10]
open('sample83.gp', 'w').write('SAMPLE=[' + ','.join(map(str, sample)) + '];\n')
open('all83.gp', 'w').write('ALL=Set([' + ','.join(str(b) for b, _ in F) + ']);\n')

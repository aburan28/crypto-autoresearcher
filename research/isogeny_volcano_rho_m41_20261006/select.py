"""Sample selection per PROTOCOL.md (m = 41). Exact level of scan hits by membership: the floors are fully enumerated."""
import re
MOD = (1 << 41) | 0x9
def gmul(a, b):
    r = 0
    while b:
        if b & 1: r ^= a
        b >>= 1; a <<= 1
        if a >> 41: a ^= MOD
    return r
def orbit(b):
    z, m = b, b
    for i in range(1, 42):
        z = gmul(z, z); m = min(m, z)
        if z == b: return i, m
def readlist(fn): return [int(x) for x in re.findall(r"\d+", open(fn).read())]
f409, f1721 = readlist("floor409.txt"), readlist("floor1721.txt")
S409, S1721 = set(f409), set(f1721)
hits = sorted(int(l) for l in open("hits_all.txt") if l.strip())
lev = {b: ("crater" if b == 1 else "floor409" if b in S409 else "floor1721" if b in S1721 else "bottom") for b in hits}
from collections import Counter; print("scan hits by level:", Counter(lev.values()))
rows = [(0, "crater", 1)]
rows += [(1 + i, "floor409", b) for i, b in enumerate(f409[:30])]
seen, sel = set(), []
for b in f1721:
    o = orbit(b)[1]
    if o not in seen: seen.add(o); sel.append(b)
    if len(sel) == 30: break
rows += [(101 + i, "floor1721", b) for i, b in enumerate(sel)]
seen, sel = set(), []
for b in hits:
    if lev[b] != "bottom": continue
    o = orbit(b)[1]
    if o not in seen: seen.add(o); sel.append(b)
    if len(sel) == 30: break
rows += [(201 + i, "bottom", b) for i, b in enumerate(sel)]
with open("sample.csv", "w") as f:
    f.write("id,level,b\n"); [f.write(f"{i},{l},{b}\n") for i, l, b in rows]
print(len(rows), "curves;", Counter(r[1] for r in rows))
print("floor409 Galois orbits among sample:", len({orbit(b)[1] for _, l, b in rows if l == "floor409"}), "| orbit sizes:", Counter(orbit(b)[0] for _, l, b in rows if l != "crater"))

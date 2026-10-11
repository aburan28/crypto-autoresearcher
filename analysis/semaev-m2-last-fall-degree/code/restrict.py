"""Restrict a Boolean system: fix variables to constants, re-index the rest.
usage: restrict.py in.sys out.sys var=val [var=val ...]"""
import sys
inp, out = sys.argv[1], sys.argv[2]
fix = {}
for a in sys.argv[3:]:
    v, b = a.split('='); fix[int(v)] = int(b)
tok = open(inp).read().split()
N, npol = int(tok[0]), int(tok[1]); p = 2; polys = []
for _ in range(npol):
    k = int(tok[p]); p += 1
    polys.append([int(x, 16) for x in tok[p:p + k]]); p += k
keep = [v for v in range(N) if v not in fix]
newidx = {v: i for i, v in enumerate(keep)}
fixmask = sum(1 << v for v in fix); onemask = sum(1 << v for v, b in fix.items() if b)
res = []
for poly in polys:
    acc = {}
    for m in poly:
        if (m & fixmask) & ~onemask:   # contains a variable fixed to 0
            continue
        r = m & ~fixmask; nm = 0
        while r:
            low = r & -r; v = low.bit_length() - 1; r ^= low; nm |= 1 << newidx[v]
        acc[nm] = acc.get(nm, 0) ^ 1
    res.append(sorted(m for m, c in acc.items() if c))
with open(out, 'w') as fh:
    fh.write(f"{len(keep)} {len(res)}\n")
    for q in res:
        fh.write(str(len(q)) + " " + " ".join(format(m, 'x') for m in q) + "\n")

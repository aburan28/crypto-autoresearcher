#!/usr/bin/env python3
"""Pure-Python producer of closure certificates, for small instances and for negative controls of cert_check.py.

usage: make_cert_py.py OUT D MODE n f_hex a2 a6_hex z_hex basis_hex...
  MODE = closure   U = W_D (Macaulay rows, then the closure rule until nothing new): the certificate is valid
  MODE = macaulay  U = M_D (Macaulay rows only, no closure): a certificate the checker must REJECT whenever
                   M_D is not closed under the closure rule (e.g. when W_D has a mutant that M_D lacks)
Writes the file format of code/lfdclose2.c (export_cert). If 1 is in U the file is not written.
"""
import sys, struct, itertools
sys.path.insert(0, __import__("os").path.dirname(__import__("os").path.abspath(__file__)))
from cert_check import descend

out, D, mode = sys.argv[1], int(sys.argv[2]), sys.argv[3]
n = int(sys.argv[4]); f = int(sys.argv[5], 16); a2 = int(sys.argv[6]); a6 = int(sys.argv[7], 16)
xR = int(sys.argv[8], 16); basis = [int(x, 16) for x in sys.argv[9:]]
N, polys = descend(n, f, a2, a6, xR, basis)

masks = []                      # column order: degree ascending, so the highest bit is the highest degree
for d in range(D + 1):
    for comb in itertools.combinations(range(N), d):
        masks.append(sum(1 << i for i in comb))
col = {m: i for i, m in enumerate(masks)}
ncols = len(masks)
lowlim = sum(1 for m in masks if bin(m).count("1") <= D - 1)

piv = {}
def insert(r):
    while r:
        hb = r.bit_length() - 1
        p = piv.get(hb)
        if p is None:
            piv[hb] = r; return hb
        r ^= p
    return None

newlow = []
for p in polys:
    dp = max(bin(m).count("1") for m in p)
    for d in range(D - dp + 1):
        for comb in itertools.combinations(range(N), d):
            mm = sum(1 << i for i in comb)
            r = 0
            for t in p:
                r ^= 1 << col[t | mm]
            hb = insert(r)
            if hb is not None and hb < lowlim:
                newlow.append(hb)

if mode == "closure":
    done = set()
    while newlow:
        hb = newlow.pop()
        if hb in done:
            continue
        done.add(hb)
        g = piv[hb]
        for v in range(N):
            vb = 1 << v; r2 = 0; r = g
            while r:
                b = r & -r; i = b.bit_length() - 1; r ^= b
                r2 ^= 1 << col[masks[i] | vb]
            h2 = insert(r2)
            if h2 is not None and h2 < lowlim:
                newlow.append(h2)
elif mode != "macaulay":
    sys.exit("MODE must be closure or macaulay")

if 0 in piv:
    sys.exit(f"1 is in U (D = {D}, mode {mode}): no certificate")
Q = [c for c in range(ncols) if c not in piv]
qidx = {c: i for i, c in enumerate(Q)}
nq = len(Q)
NF = {}
for c in range(ncols):          # increasing column index: lower terms of a pivot row are already reduced
    if c not in piv:
        NF[c] = 1 << qidx[c]
    else:
        r = piv[c] ^ (1 << c); acc = 0
        while r:
            b = r & -r; t = b.bit_length() - 1; r ^= b
            acc ^= NF[t]
        NF[c] = acc
qw = max(1, (nq + 63) // 64)
with open(out, "wb") as fh:
    fh.write(struct.pack("<4q", N, D, ncols, nq))
    fh.write(struct.pack(f"<{ncols}Q", *masks))
    for c in range(ncols):
        fh.write(NF[c].to_bytes(8 * qw, "little"))
print(f"wrote {out}: mode {mode}, D = {D}, ncols {ncols}, rank {len(piv)}, nq {nq}")

#!/usr/bin/env python3
"""L4 / P-N7 (SHF-20261016-3caa6f, SHF-20261017-e4d7f6): recount the frob
(n = 21) gaps from crypto:research/ic_tree_split_structured_v_20261011/runs/
registered/cells.jsonl, and decide which v_info.g divide t^7 - 1 (and t^3 - 1)
over GF(2) with our own polynomial arithmetic (ints as coefficient bit vectors).

gap = curve.d_s - r.d_s (RESULTS.md: "gaps (D_s(curve) - D_s(R))").
Usage: python3 -I treesplit_cells.py /home/user/crypto <rev>
"""
import collections
import json
import subprocess
import sys

repo, rev = sys.argv[1], sys.argv[2]
base = "research/ic_tree_split_structured_v_20261011/"


def show(path):
    return subprocess.run(["git", "-C", repo, "-c", "gc.auto=0", "show", f"{rev}:{base}{path}"],
                          capture_output=True, check=True).stdout.decode()


def gf2_mod(a, m):
    dm = m.bit_length() - 1
    while a and a.bit_length() - 1 >= dm:
        a ^= m << (a.bit_length() - 1 - dm)
    return a


cells = [json.loads(l) for l in show("runs/registered/cells.jsonl").splitlines() if l.strip()]
print(f"commit {rev}; cells: {len(cells)}")
print("cells by (vtype, n):", dict(collections.Counter((c['vtype'], c['n']) for c in cells)))
frob = [c for c in cells if c["vtype"] == "frob" and c["n"] == 21]
T7, T3 = 0b10000001, 0b1001  # t^7 + 1, t^3 + 1 over GF(2)
gaps = collections.Counter()
rows = []
for c in frob:
    g = c["v_info"]["g"]
    gap = c["curve"]["d_s"] - c["r"]["d_s"]
    sub7 = gf2_mod(T7, g) == 0 if g.bit_length() <= 8 else False
    sub3 = gf2_mod(T3, g) == 0 if g.bit_length() <= 4 else False
    gaps[gap] += 1
    rows.append((c["a"], c["seed"], c["ell"], g, c["t2_size"], c["curve"]["d_s"], c["r"]["d_s"], gap, sub7, sub3,
                 c["curve"]["censored"] or c["r"]["censored"]))
print(f"frob n=21 cells: {len(frob)}; gap counts: {dict(sorted(gaps.items()))}  (corrected text: 15 x 0, 5 x -1)")
print("a  seed      ell  g    |T2|  Ds(curve) Ds(R) gap  g|t^7-1 g|t^3-1 censored")
for r in sorted(rows, key=lambda x: (x[0], x[1], x[2])):
    print("{:<2} {:<9} {:<4} {:<4} {:<5} {:<9} {:<5} {:<4} {:<7} {:<7} {}".format(*r))
gset = sorted({r[3] for r in rows})
print(f"distinct g in frob n=21 cells (run order not preserved): {gset}")
print(f"g dividing t^7-1: {sorted({r[3] for r in rows if r[8]})}  (Leak.lean: [23, 29, 127])")
print(f"g dividing t^3-1: {sorted({r[3] for r in rows if r[9]})}  (Leak.lean: none)")
sub = [r for r in rows if r[8]]
print(f"cells with g | t^7-1: {len(sub)}; of these at gap -1: {sum(1 for r in sub if r[7] == -1)}; at gap 0: {sum(1 for r in sub if r[7] == 0)}")
print(f"cells at gap -1 with g not dividing t^7-1: {sum(1 for r in rows if r[7] == -1 and not r[8])}")
print(f"|T2| of the gap -1 cells: {[r[4] for r in sorted(rows, key=lambda x: (x[0], x[1], x[2])) if r[7] == -1]}  (RESULTS.md: 29, 28, 70, 29, 35)")
leak = show("lean/TreeSplit/Leak.lean")
start = leak.index("def gs : List Nat := [") + len("def gs : List Nat := [")
gs_lean = [int(x) for x in leak[start:leak.index("]", start)].split(",")]
print(f"Leak.lean gs = {gs_lean}; equals distinct cell g set: {sorted(gs_lean) == gset}")
print(f"polyMod-free check: Leak gs filtered by g | t^7-1 = {[g for g in gs_lean if gf2_mod(T7, g) == 0]}")
ro = show("runs/registered/readout.txt").splitlines()
for ln in (19, 26, 51, 56, 58):
    print(f"readout.txt:{ln}: {ro[ln - 1].strip()[:140]}")

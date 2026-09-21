#!/usr/bin/env python3
"""V2/V1 supplement: the m2-s2 gate manifest prints its generator S~ in full and
its per-layer profile.  Rebuild both with my own code (4 squarefree variables,
ell_1 = a10 + 2 a11, ell_2 = a20 + 2 a21, p = 4099, a = 527, b = 72, x_R = 2374)
and compare term by term.  This is the one cell where a producer-recorded
generator can be compared against an independent construction."""
import yaml, re

p, A, B, xR = 4099, 527, 72, 2374
NV = 4
NAMES = ["a10", "a11", "a20", "a21"]
POP = [bin(m).count("1") for m in range(1 << NV)]

def zero(): return [0] * (1 << NV)
def mul(u, v):
    w = zero()
    for i, ui in enumerate(u):
        if ui:
            for j, vj in enumerate(v):
                if vj: w[i | j] = (w[i | j] + ui * vj) % p
    return w
def add(u, v): return [(x + y) % p for x, y in zip(u, v)]
def sub(u, v): return [(x - y) % p for x, y in zip(u, v)]
def sm(c, u): return [(c * x) % p for x in u]
def const(c):
    v = zero(); v[0] = c % p; return v

e1 = zero(); e1[1 << 0] = 1; e1[1 << 1] = 2
e2 = zero(); e2[1 << 2] = 1; e2[1 << 3] = 2
d = sub(e1, e2); s = add(e1, e2); pr = mul(e1, e2)
St = add(add(sm(pow(xR, 2, p), mul(d, d)),
             sm((-2 * xR) % p, add(mul(s, add(pr, const(A))), const(2 * B)))),
         add(mul(sub(pr, const(A)), sub(pr, const(A))), sm((-4 * B) % p, s)))

def name(m): return "*".join(NAMES[i] for i in range(NV) if m >> i & 1) or "1"
mine = {name(m): c for m, c in enumerate(St) if c}

man = yaml.safe_load(open("experiments/EXP-PFDR-5726af/runs/RUN-PFDR-5726af-m2-s2-gate/manifest.yaml"))["run"]
rec = man["result"]["metrics"]["CTRL-S2-HAND-FIXTURE"]
gen = re.sub(r"\s+", "", rec["generator"])
theirs = {}
for term in gen.replace("-", "+-").split("+"):
    if not term: continue
    parts = term.split("*")
    if parts[0].lstrip("-").isdigit():
        c, mono = int(parts[0]), "*".join(parts[1:]) or "1"
    else:
        c, mono = 1, "*".join(parts)
    theirs[mono] = (theirs.get(mono, 0) + c) % p

print("my S~ terms:      ", len(mine))
print("manifest S~ terms:", len(theirs))
print("term-by-term identical:", mine == theirs)
if mine != theirs:
    for k in sorted(set(mine) | set(theirs)):
        if mine.get(k) != theirs.get(k):
            print("   DIFFER", k, mine.get(k), theirs.get(k))

# per-layer profile with my own rank code
import sys
sys.path.insert(0, "/home/user/crypto-autoresearcher/coordination/reviews/pfdr-battery-20260904/reviews/TASK-20260904-642cf5")
from v1_blind_rederive import rank_mod_p
prof = []
for D in (4, 5, 6):
    mus = [m for m in range(1 << NV) if POP[m] == D - 4]
    rows = []
    for mu in mus:
        w = zero()
        for m, c in enumerate(St):
            if c: w[m | mu] = (w[m | mu] + c) % p
        rows.append(w)
    cols = [m for m in range(1 << NV) if POP[m] == D]
    full = rank_mod_p(rows, p) if rows else 0
    top = rank_mod_p([[r[c] for c in cols] for r in rows], p) if (rows and cols) else 0
    prof.append(dict(D=D, rows=len(rows), ncols_top=len(cols), full_rank=full,
                     top_rank=top, fall_dim=full - top))
print()
print("my per-layer profile: ", [(x['D'], x['full_rank'], x['top_rank'], x['fall_dim']) for x in prof])
print("manifest profile:     ", [(x['D'], x['full_rank'], x['top_rank'], x['fall_dim']) for x in rec['profile']])
print("manifest oracle:      ", [(x['D'], x['oracle_full_rank'], x['oracle_top_rank'], x['oracle_fall_dim']) for x in rec['oracle']])
agree = all((a['D'], a['full_rank'], a['top_rank'], a['fall_dim']) ==
            (b['D'], b['full_rank'], b['top_rank'], b['fall_dim'])
            for a, b in zip(prof, rec['profile']))
print("profiles agree:", agree)
print("my d_ff =", next(x['D'] for x in prof if x['fall_dim'] > 0),
      " fall_dim =", next(x['fall_dim'] for x in prof if x['fall_dim'] > 0),
      "| manifest d_ff =", rec['d_ff'], "fall_dim =", rec['fall_dim'])
print("degree-4 part:", {k: v for k, v in mine.items() if k.count('*') == 3},
      "| manifest expected:", rec['degree_4_part_expected'])

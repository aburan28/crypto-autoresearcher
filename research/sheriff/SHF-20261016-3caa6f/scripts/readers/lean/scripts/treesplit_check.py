# Independent checks for crypto:research/ic_tree_split_structured_v_20261011
# (a) Data.lean rows == cells.jsonl; (b) verdict per PREREGISTRATION.md §4 prose (lines 86-104);
# (c) Leak.lean claim: which frob n=21 g divide t^7+1 / t^3+1, and the gap -1 cells.
import json, re, sys
from fractions import Fraction
from math import ceil
base = sys.argv[1]
rows = [json.loads(l) for l in open(base + "/runs/registered/cells.jsonl")]
def d1def(c):
    for r in c["rows"]:
        if r["d"] == 1: return r["deficit"]
    return 0
J = []
for r in rows:
    J.append(dict(vtype=r["vtype"], n=r["n"], a=r["a"], seed=r["seed"], ell=r["ell"], t2=r["t2_size"],
                  dsCurve=None if r["curve"]["censored"] else r["curve"]["d_s"],
                  dsR=None if r["r"]["censored"] else r["r"]["d_s"],
                  deficit1=d1def(r["curve"]), t2InV=bool(r["t2_in_v"])))
L = []
pat = re.compile(r"\{ vtype := \.(\w+), n := (\d+), a := (\d+), seed := (\d+), ell := (\d+), t2 := (\d+), dsCurve := (some \d+|none), dsR := (some \d+|none), deficit1 := (\d+), t2InV := (true|false) \}")
for m in pat.finditer(open(base + "/lean/TreeSplit/Data.lean").read()):
    o = lambda s: None if s == "none" else int(s.split()[1])
    L.append(dict(vtype=m[1], n=int(m[2]), a=int(m[3]), seed=int(m[4]), ell=int(m[5]), t2=int(m[6]),
                  dsCurve=o(m[7]), dsR=o(m[8]), deficit1=int(m[9]), t2InV=m[10] == "true"))
print("jsonl rows", len(J), "Data.lean rows", len(L), "identical (order+values):", J == L)
mism = [i for i,(x,y) in enumerate(zip(J,L)) if x != y]
print("mismatching row indices:", mism[:10])
def verdict(rs):
    keys = []
    for r in rs:
        k = (r["n"], r["a"], r["seed"])
        if k not in keys: keys.append(k)
    series = []
    for k in keys:
        pts = [(r["ell"], r["dsCurve"], r["dsCurve"] - r["dsR"]) for r in rs if (r["n"], r["a"], r["seed"]) == k and r["dsCurve"] is not None and r["dsR"] is not None]
        if pts: series.append(pts)
    def slope(ps):
        k = len(ps); xs = [p[0] for p in ps]; ys = [p[1] for p in ps]
        mx = Fraction(sum(xs), k); my = Fraction(sum(ys), k)
        den = sum((x-mx)**2 for x in xs)
        return None if den == 0 else sum((x-mx)*(y-my) for x,y in zip(xs,ys)) / den
    alive_gap = all(max(s)[2] <= -2 for s in series)
    nslope = sum(1 for s in series if slope(s) is not None and slope(s) <= Fraction(15,100))
    slopes = [float(slope(s)) if slope(s) is not None else None for s in series]
    gaps = [p[2] for s in series for p in s]
    if series and alive_gap and nslope >= ceil(len(series)/2): v = "alive"
    elif all(g >= -1 for g in gaps): v = "closed"
    else: v = "inconclusive"
    return v, len(series), slopes, sorted(set(gaps))
sub = [r for r in J if r["vtype"] == "subfield"]
gate = bool(sub) and all(r["t2InV"] and r["deficit1"] >= r["n"] - r["ell"] for r in sub)
print("gate:", gate, [(r["a"], r["t2InV"], r["deficit1"], r["n"]-r["ell"]) for r in sub])
for arm, f in [("poly", lambda r: r["vtype"]=="poly"), ("frob n=21", lambda r: r["vtype"]=="frob" and r["n"]==21), ("rand", lambda r: r["vtype"]=="rand")]:
    print(arm, verdict([r for r in J if f(r)]))
print("poly cells with ell<=5 (Replay targets):", sum(1 for r in J if r["vtype"]=="poly" and r["ell"]<=5))
# (c) Leak
def pmod(a, b):
    db = b.bit_length()-1
    while a and a.bit_length()-1 >= db: a ^= b << (a.bit_length()-1-db)
    return a
gs = [r["v_info"]["g"] for r in rows if r["vtype"]=="frob" and r["n"]==21]
print("frob n=21 g in run order:", gs, "== Leak.gs:", gs == [23, 35, 101, 159, 421, 29, 49, 127, 249, 331])
print("g | t^7+1:", [g for g in gs if pmod(129, g) == 0], " g | t^3+1:", [g for g in gs if pmod(9, g) == 0])
print("NB Leak.lean computes polyMod 129 g, i.e. (t^7+1) mod g")
gm1 = [(r["a"], r["seed"], r["ell"], r["v_info"]["g"], r["t2_size"]) for r in rows if r["vtype"]=="frob" and r["n"]==21 and not r["curve"]["censored"] and r["curve"]["d_s"]-r["r"]["d_s"] == -1]
print("frob n=21 gap -1 cells (a,seed,ell,g,|T2|):", gm1)

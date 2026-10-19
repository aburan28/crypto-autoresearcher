# Python transcription of crypto:research/ic_tree_split_structured_v_20261011/lean/TreeSplit/Replay.lean
# (lines 38-242), run on the 12 poly cells with ell<=5 from cells.jsonl. Purpose: check the claim that
# `replay_ok` (closed by native_decide, Replay.lean:249) is TRUE without trusting the Lean compiler.
# Caveat: this is a transcription of Replay.lean, not a design independent of it.
import json, sys
M64 = (1 << 64) - 1
def mix(s):
    s2 = (s + 0x9E3779B97F4A7C15) & M64
    z = ((s2 ^ (s2 >> 30)) * 0xBF58476D1CE4E5B9) & M64
    z = ((z ^ (z >> 27)) * 0x94D049BB133111EB) & M64
    return s2, z ^ (z >> 31)
def streamSeed(seed, n, a, ell, tag):
    return ((seed & M64) ^ ((a << 40) & M64) ^ ((n << 32) & M64) ^ ((ell << 24) & M64) ^ ((tag << 56) & M64))
def log2(a): return a.bit_length() - 1 if a else 0
def polyMod(a, b):
    db = log2(b)
    for _ in range(130):
        if a != 0 and log2(a) >= db: a ^= b << (log2(a) - db)
    return a
def polyGcd(a, b):
    x, y = a, b
    for _ in range(130):
        if y != 0: x, y = y, polyMod(x, y)
    return x
def fmul(n, poly, a, b):
    r, x = 0, a
    for i in range(n):
        if (b >> i) & 1: r ^= x
        x <<= 1
        if (x >> n) & 1: x ^= poly
    return r
def finv(n, poly, a):
    e = 2 ** n - 2; r = 1; base = a
    for i in range(n):
        if (e >> i) & 1: r = fmul(n, poly, r, base)
        base = fmul(n, poly, base, base)
    return r
def ftrace(n, poly, a):
    t, x = 0, a
    for _ in range(n): t ^= x; x = fmul(n, poly, x, x)
    return t
def fhalf(n, poly, c):
    z, x = 0, c
    for _ in range((n + 1) // 2):
        z ^= x; x = fmul(n, poly, fmul(n, poly, x, x), fmul(n, poly, x, x))
    return z
def irreducible(p, n):
    t = 2
    for _ in range(n // 2):
        t = fmul(n, p, t, t)
        if polyGcd(p, t ^ 2) != 1: return False
    return True
def fieldPoly(n):
    for k in range(1, n):
        p = 2 ** n + 2 ** k + 1
        if irreducible(p, n): return p
    for a in range(1, n):
        for b in range(a + 1, n):
            for c in range(b + 1, n):
                p = 2 ** n + 2 ** a + 2 ** b + 2 ** c + 1
                if irreducible(p, n): return p
    return 0
def pointsWithX(n, poly, a, x):
    if x == 0: return []
    c = x ^ a ^ finv(n, poly, fmul(n, poly, x, x))
    if ftrace(n, poly, c) != 0: return []
    y = fmul(n, poly, x, fhalf(n, poly, c))
    return [(x, y), (x, y ^ x)]
def add(n, poly, a, P, Q):
    (x1, y1), (x2, y2) = P, Q
    sq = lambda u: fmul(n, poly, u, u)
    if x1 == x2:
        if (y1 ^ y2) == x1 or x1 == 0: return None
        l = x1 ^ fmul(n, poly, y1, finv(n, poly, x1))
        x3 = sq(l) ^ l ^ a
        return (x3, sq(x1) ^ fmul(n, poly, l ^ 1, x3))
    l = fmul(n, poly, y1 ^ y2, finv(n, poly, x1 ^ x2))
    x3 = sq(l) ^ l ^ x1 ^ x2 ^ a
    return (x3, fmul(n, poly, l, x1 ^ x3) ^ x3 ^ y1)
def t2Poly(n, poly, a, ell):
    base = [P for x in range(2 ** ell) for P in pointsWithX(n, poly, a, x)]
    s = set()
    for i in range(len(base)):
        for j in range(i, len(base)):
            R = add(n, poly, a, base[i], base[j])
            if R is not None: s.add(R[0])
    return s
def control(n, size, st):
    mask = ((1 << n) - 1) & M64; s = set()
    for _ in range(size * 64 + 1000):
        if len(s) < size:
            st, z = mix(st); x = z & mask
            if x != 0: s.add(x)
    return s
def samples(n, k, S, st):
    mask = ((1 << n) - 1) & M64; out = []
    for _ in range(k * 64):
        if len(out) < k:
            st, z = mix(st); x = z & mask
            if x not in S: out.append(x)
    return out
def combos(vs, k):
    if k == 0: return [0]
    if not vs: return []
    v, rest = vs[0], vs[1:]
    return [c | (1 << v) for c in combos(rest, k - 1)] + combos(rest, k)
def monomials(n, d):
    return [m for k in range(d + 1) for m in combos(list(range(n)), k)]
def evalRow(monos, p):
    row = 0
    for j, m in enumerate(monos):
        if p & m == m: row |= 1 << j
    return row
def reduce_(basis, v):
    while v:
        b = basis.get(v.bit_length() - 1)
        if b is None: return v
        v ^= b
    return v
def cutOut(pts, n, smp):
    for d in range(1, 7):
        monos = monomials(n, d); m = len(monos)
        if m > 90000: return None
        basis = {}
        for p in pts:
            v = reduce_(basis, evalRow(monos, p))
            if v: basis[v.bit_length() - 1] = v
        fz = len(smp) if len(basis) == m else sum(1 for p in smp if reduce_(basis, evalRow(monos, p)) == 0)
        if fz == 0: return d
    return None
def recompute(r):
    n, a, ell, seed = r["n"], r["a"], r["ell"], r["seed"]
    poly = fieldPoly(n)
    t2 = t2Poly(n, poly, a, ell)
    ctl = control(n, len(t2), streamSeed(seed, n, a, ell, 2))
    sc = samples(n, 2000, t2, streamSeed(seed, n, a, ell, 3))
    sr = samples(n, 2000, ctl, streamSeed(seed, n, a, ell, 4))
    return poly, len(t2), cutOut(list(t2), n, sc), cutOut(list(ctl), n, sr)
rows = [json.loads(l) for l in open(sys.argv[1])]
tg = [r for r in rows if r["vtype"] == "poly" and r["ell"] <= 5]
print("targets:", len(tg)); ok = 0
for r in tg:
    poly, t2, dc, dr = recompute(r)
    rec = (r["field_poly"], r["t2_size"], None if r["curve"]["censored"] else r["curve"]["d_s"], None if r["r"]["censored"] else r["r"]["d_s"])
    got = (poly, t2, dc, dr); ok += got == rec
    print((r["n"], r["a"], r["ell"]), "recomputed", got, "recorded", rec, "MATCH" if got == rec else "MISMATCH", flush=True)
print("matches:", ok, "/", len(tg))

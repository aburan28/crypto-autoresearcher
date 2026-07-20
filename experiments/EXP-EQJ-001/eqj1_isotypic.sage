# EXP-EQJ-001 / EQJ / eqj1_isotypic.sage
# Candidate B3: Equivariant index calculus on the Semaev fiber-product curve.
# Isotypic decomposition of the m=4 relation space under G = B_3 = S_3 ⋉ (Z/2)^3
# (order 48) using exact group-algebra idempotents; per-block masses, ranks,
# orbit-compressed storage, blind-descent; symmetrized baseline + random null.
#
# Usage: sage eqj1_isotypic.sage --p 211 --out runs/RUN-EQJ-001-a/raw.json [--crosscheck]
#
# Deterministic: all randomness flows from seeds [20260717, 20260718, 20260719]
# via numpy RandomState. No wall-clock-dependent choices.

import sys, json, time, itertools
from fractions import Fraction
import numpy as np
from sage.all import *
from sage.libs.gap.libgap import libgap

# ---------------- args ----------------
p = None; OUT = None; CROSSCHECK = False
_av = sys.argv
for _i, _a in enumerate(_av):
    if _a == '--p': p = int(_av[_i+1])
    if _a == '--out': OUT = _av[_i+1]
    if _a == '--crosscheck': CROSSCHECK = True
assert p in (211, 1009, 4099), "p must be one of the frozen primes"
K_MAP = {211: 12, 1009: 12, 4099: 16}
k = K_MAP[p]
SEEDS = [20260717, 20260718, 20260719]
NULL_DRAWS = 8
T0 = time.time()
def log(msg):
    sys.stderr.write("[t=%.1fs] %s\n" % (time.time()-T0, msg)); sys.stderr.flush()

log("start p=%d k=%d" % (p, k))

# ---------------- curve (deterministic rule from specification) ----------------
F = GF(p)
E = None; a_c = b_c = None; n = None
_found = False
for a in range(1, 400):
    for b in range(1, 400):
        if (4*a**3 + 27*b**2) % p == 0:
            continue
        E0 = EllipticCurve(F, [a, b])
        n0 = E0.order()
        if is_prime(n0):
            E, a_c, b_c, n = E0, a, b, int(n0)
            _found = True
            break
    if _found: break
assert _found, "no prime-order curve found in deterministic scan"
assert n > 48 and is_prime(n), "need group order prime and coprime to |G|=48"
ordinary = (int(E.order()) != p + 1)
log("curve y^2 = x^3 + %d x + %d, n=%d prime, ordinary=%s" % (a_c, b_c, n, ordinary))

# ---------------- factor base ----------------
O = E(0)
xs = sorted({int(P[0]) for P in E.points() if P != O})
assert len(xs) >= k, "not enough x-coordinates"
FB_x = xs[:k]
fb_index = {x: j for j, x in enumerate(FB_x)}
Q = []
for x in FB_x:
    lifts = E.lift_x(F(x), all=True)
    lifts_sorted = sorted(lifts, key=lambda P: int(P[1]))
    Pc = lifts_sorted[0]
    assert int(Pc[1]) <= (p-1)//2
    Q.append(Pc)
negQ = [-P for P in Q]
def pt(u):
    u = int(u)
    return Q[u >> 1] if (u & 1) == 0 else negQ[u >> 1]

twok = 2 * k
M = twok ** 3
log("FB_x=%s ... M=(2k)^3=%d" % (FB_x[:4], M))

# pair-sum table over signed points
PS = [[pt(a) + pt(b) for b in range(twok)] for a in range(twok)]
log("pair-sum table built")

# ---------------- group G = B_3 ----------------
# elements: (perm, signs); g sends slot content: new slot j gets signs[j] * old slot perm[j]
elements = []
for perm in itertools.permutations(range(3)):
    for signs in itertools.product([1, -1], repeat=3):
        elements.append((tuple(perm), tuple(signs)))
assert len(elements) == 48
NG = 48

def perm_sign(el):
    s = 1
    pr = el[0]
    for i in range(3):
        for j in range(i+1, 3):
            if pr[i] > pr[j]: s = -s
    return s
def det_natural(el):
    d = 1
    for sg in el[1]: d *= sg
    return perm_sign(el) * d
def prod_signs(el):
    d = 1
    for sg in el[1]: d *= sg
    return d

# gap permutations on 6 points {+e1,+e2,+e3,-e1,-e2,-e3} = {1..6}
def gap_perm(el):
    perm, signs = el
    img = [0]*6
    for j in range(3):
        tgt = perm[j] + (1 if signs[j] == 1 else 4)
        img[j] = tgt                      # image of +e_j (point j+1)
        img[j+3] = perm[j] + (4 if signs[j] == 1 else 1)  # image of -e_j
    return img
gap_perms = [gap_perm(el) for el in elements]
g_gap = [libgap.PermList(im) for im in gap_perms]
gens_idx = []
# generators: transposition (0 1), 3-cycle, sign flip of axis 0
for el in elements:
    if el == ((1, 0, 2), (1, 1, 1)): gens_idx.append(elements.index(el))
    if el == ((1, 2, 0), (1, 1, 1)): gens_idx.append(elements.index(el))
    if el == ((0, 1, 2), (-1, 1, 1)): gens_idx.append(elements.index(el))
assert len(gens_idx) == 3
Ggap = libgap.Group([g_gap[i] for i in gens_idx])
assert int(libgap.Size(Ggap)) == 48, "group order != 48"
ccs = libgap.ConjugacyClasses(Ggap)
irr = libgap.Irr(Ggap)
assert int(libgap.Size(ccs)) == 10, "B_3 must have 10 conjugacy classes"
assert int(libgap.Size(irr)) == 10, "B_3 must have 10 irreps"
cc_list = [ccs[i] for i in range(10)]
cc_reps = [cc.Representative() for cc in cc_list]
cc_sizes = [int(libgap.Size(cc)) for cc in cc_list]
assert sum(cc_sizes) == 48
# class index of each of my 48 elements via IsConjugate in G (NOT S_6)
elem_class = []
for g in g_gap:
    ci = None
    for i in range(10):
        if bool(libgap.IsConjugate(Ggap, cc_reps[i], g)):
            ci = i; break
    assert ci is not None
    elem_class.append(ci)
irr_vals = []   # irr_vals[lam][classidx] as python ints
for lam in range(10):
    vals = [int(v.sage()) for v in libgap.ValuesOfClassFunction(irr[lam])]
    irr_vals.append(vals)
# find identity element index
id_idx = elements.index(((0, 1, 2), (1, 1, 1)))
id_class = elem_class[id_idx]
dims = [irr_vals[lam][id_class] for lam in range(10)]
assert sum(d*d for d in dims) == 48, "sum of squared dimensions must be 48"
# orthogonality self-check: for each lam, sum_classes |cc| chi^2 = 48
for lam in range(10):
    s = sum(cc_sizes[i] * irr_vals[lam][i]**2 for i in range(10))
    assert s == 48, "character orthogonality failed for lam=%d" % lam
chi = [[irr_vals[lam][elem_class[g]] for g in range(NG)] for lam in range(10)]
# labels
labels = []
for lam in range(10):
    if all(chi[lam][g] == 1 for g in range(NG)):
        labels.append("trivial")
    elif all(chi[lam][g] == det_natural(elements[g]) for g in range(NG)):
        labels.append("sign_det")
    elif all(chi[lam][g] == perm_sign(elements[g]) for g in range(NG)):
        labels.append("sign_perm")
    elif all(chi[lam][g] == prod_signs(elements[g]) for g in range(NG)):
        labels.append("sign_prod")
    else:
        labels.append("irrep_%d_dim%d" % (lam, dims[lam]))
triv_lam = labels.index("trivial")
log("character table ok: dims=%s labels=%s" % (dims, labels))

# ---------------- permutation action on tuples (index arrays) ----------------
base = np.arange(M, dtype=np.int64)
u0 = base // (twok*twok); u1 = (base // twok) % twok; u2 = base % twok
us = [u0, u1, u2]
maps = []
for (perm, signs) in elements:
    flips = [1 if s < 0 else 0 for s in signs]
    nu = [np.bitwise_xor(us[perm[j]], flips[j]) for j in range(3)]
    maps.append((nu[0]*twok + nu[1])*twok + nu[2])
fixcounts = [int(np.count_nonzero(maps[g] == base)) for g in range(NG)]
mults = []
for lam in range(10):
    s = sum(fixcounts[g] * chi[lam][g] for g in range(NG))
    assert s % NG == 0, "multiplicity not integral for lam=%d" % lam
    mults.append(s // NG)
d_iso = [mults[lam]*dims[lam] for lam in range(10)]
assert sum(d_iso) == M, "sum mult*dim != M"
log("maps built; multiplicities=%s" % mults)

# orbits
orbit_id = np.full(M, -1, dtype=np.int64)
reps = []
for i in range(M):
    if orbit_id[i] >= 0: continue
    oid = len(reps); reps.append(i)
    for g in range(NG):
        orbit_id[maps[g][i]] = oid
reps = np.array(reps, dtype=np.int64)
orbit_sizes = np.bincount(orbit_id)
orbit_size_hist = {int(s): int((orbit_sizes == s).sum()) for s in np.unique(orbit_sizes)}
log("orbits: %d orbits, size histogram %s" % (len(reps), orbit_size_hist))

# ---------------- modular rank (numpy GE, cross-checked against Sage at p=211) ----------------
def mod_rank(B, nn):
    B = np.array(B, dtype=np.int64) % nn
    Mx, kk = B.shape
    rank = 0; row = 0
    for col in range(kk):
        if row >= Mx: break
        nz = np.nonzero(B[row:, col] % nn)[0]
        if len(nz) == 0: continue
        piv = row + int(nz[0])
        if piv != row:
            B[[row, piv]] = B[[piv, row]]
        inv = pow(int(B[row, col]) % nn, -1, nn)
        B[row] = (B[row] * inv) % nn
        below = np.nonzero(B[row+1:, col] % nn)[0] + row + 1
        if len(below):
            factors = B[below, col] % nn
            B[below] = (B[below] - factors[:, None] * B[row]) % nn
        rank += 1; row += 1
    return rank

# ---------------- projector application ----------------
def apply_proj(fvec, lam):
    acc = np.zeros_like(fvec)
    for g in range(NG):
        cg = chi[lam][g]
        if cg == 0: continue
        acc += cg * fvec[maps[g]]
    return acc  # pi_lam f = (d_lam/48) * acc

inv48 = inverse_mod(48, n)

result = {
    "p": p, "m": 4, "k": k,
    "curve": {"a": a_c, "b": b_c, "n": n, "ordinary": ordinary},
    "group": {"order": 48, "classes": 10,
              "labels": labels, "dims": dims,
              "class_sizes": cc_sizes,
              "char_table": irr_vals,
              "elem_class": elem_class},
    "ambient_M": M,
    "FB_x": FB_x,
    "multiplicities": [{"label": labels[lam], "dim": dims[lam], "mult": mults[lam], "d_iso": d_iso[lam]} for lam in range(10)],
    "orbit_size_hist": orbit_size_hist,
    "n_orbits": int(len(reps)),
    "seeds": SEEDS,
    "null_draws": NULL_DRAWS,
    "started_at": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
    "per_seed": [],
    "observations": [],
    "crosscheck": {},
}
log("entering seed loop")

for seed in SEEDS:
    ts = time.time()
    rng = np.random.RandomState(int(seed))
    # ----- target -----
    t0 = int(rng.randint(2, int(n-1)))
    T = t0 * Q[0]
    assert T != O
    # ----- relation enumeration (fiber U_T) -----
    f = np.zeros(M, dtype=np.int64)
    rows = []   # (idx, [(col, coeff), ...])
    A_dense = np.zeros((M, k), dtype=np.int64)
    degenerate = 0
    for u0i in range(twok):
        PSrow = PS[u0i]
        for u1i in range(twok):
            S01 = PSrow[u1i]
            for u2i in range(twok):
                S = S01 + pt(u2i)
                R4 = T - S
                if R4 == O:
                    degenerate += 1; continue
                j = fb_index.get(int(R4[0]))
                if j is None: continue
                c4 = 1 if R4 == Q[j] else -1
                idx = (u0i*twok + u1i)*twok + u2i
                f[idx] = 1
                ent = [(u0i >> 1, 1 if (u0i & 1) == 0 else -1),
                       (u1i >> 1, 1 if (u1i & 1) == 0 else -1),
                       (u2i >> 1, 1 if (u2i & 1) == 0 else -1),
                       (j, c4)]
                rows.append((idx, ent))
                for (col, c) in ent:
                    A_dense[idx, col] = (A_dense[idx, col] + c) % n
    N = len(rows)
    assert N == int(f.sum())
    # ----- POS-3 spotcheck: 5 sampled relations re-verified by fresh EC addition -----
    spot_ok = True
    for (idx, ent) in rows[:5]:
        u0i = idx // (twok*twok); u1i = (idx // twok) % twok; u2i = idx % twok
        S = PS[u0i][u1i] + pt(u2i)
        R4 = T - S
        if S + R4 != T: spot_ok = False
        if int(R4[0]) not in fb_index: spot_ok = False
        j = fb_index[int(R4[0])]
        if not (R4 == Q[j] or R4 == negQ[j]): spot_ok = False
    # explicit x-membership check for the three slots
    for (idx, ent) in rows[:5]:
        u0i = idx // (twok*twok); u1i = (idx // twok) % twok; u2i = idx % twok
        if int(pt(u0i)[0]) != FB_x[u0i >> 1]: spot_ok = False
        if int(pt(u1i)[0]) != FB_x[u1i >> 1]: spot_ok = False
        if int(pt(u2i)[0]) != FB_x[u2i >> 1]: spot_ok = False
    # ----- per-block masses -----
    w = []
    for lam in range(10):
        acc = apply_proj(f, lam)
        num = int(acc @ acc) * int(dims[lam]) * int(dims[lam])
        w.append(Fraction(num, int(NG*NG)))
    parseval_ok = (sum(w) == Fraction(N))
    w_float = [float(x) for x in w]
    w_triv_centered = w[triv_lam] - Fraction(N*N, int(M))
    # ----- block matrices mod n -----
    r_blocks = []; B_list = []
    for lam in range(10):
        accM = np.zeros((M, k), dtype=np.int64)
        for g in range(NG):
            cg = chi[lam][g]
            if cg == 0: continue
            accM += cg * A_dense[maps[g]]
        Blam = (accM * (int(dims[lam]) * int(inv48) % n)) % n
        B_list.append(Blam)
        r_blocks.append(int(mod_rank(Blam, n)))
    r_full = int(mod_rank(A_dense, n))
    conservation_ok = bool(((sum(B_list) % n) == (A_dense % n)).all())
    # cross-check numpy rank vs Sage rank (p=211 run only)
    if CROSSCHECK:
        cc_ok = True; cc_detail = []
        for lam in range(10):
            rsage = Matrix(GF(n), B_list[lam].tolist()).rank()
            cc_detail.append(int(rsage))
            if int(rsage) != r_blocks[lam]: cc_ok = False
        rsage_full = int(Matrix(GF(n), A_dense.tolist()).rank())
        result["crosscheck"] = {"sage_r_blocks": cc_detail, "sage_r_full": rsage_full,
                                "numpy_r_full": r_full, "rank_crosscheck_ok": bool(cc_ok and rsage_full == r_full)}
    # ----- storage -----
    orbits_hit = int(len(np.unique(orbit_id[np.nonzero(f)[0]])))
    storage_factor = float(Fraction(orbits_hit, N))
    # ----- blind descent flags -----
    blind_flags = [bool(r_blocks[lam] == k) for lam in range(10)]
    # ----- DLP instance: baseline scan vs orbit-rep scan -----
    secret = int(rng.randint(2, int(n-2)))
    R = secret * Q[0]
    J = k + 4
    def collect(order_source):
        rels = []; tests_list = []; fails = 0
        for j in range(J):
            aj = int(rng.randint(0, int(n-1))); bj = int(rng.randint(0, int(n-1)))
            Tj = aj * R + bj * Q[0]
            if Tj == O:
                Tj = Tj + Q[0]; bj = (bj + 1) % n
            order = rng.permutation(order_source)
            found = None; tests = 0
            for idx in order:
                tests += 1
                idx = int(idx)
                u0i = idx // (twok*twok); u1i = (idx // twok) % twok; u2i = idx % twok
                S = PS[u0i][u1i] + pt(u2i)
                R4 = Tj - S
                if R4 == O: continue
                jj = fb_index.get(int(R4[0]))
                if jj is None: continue
                c4 = 1 if R4 == Q[jj] else -1
                found = [(u0i >> 1, 1 if (u0i & 1) == 0 else -1),
                         (u1i >> 1, 1 if (u1i & 1) == 0 else -1),
                         (u2i >> 1, 1 if (u2i & 1) == 0 else -1),
                         (jj, c4)]
                break
            if found is None:
                fails += 1
            else:
                rels.append((aj, bj, found)); tests_list.append(tests)
        return rels, tests_list, fails
    def solve_dlp(rels):
        rows_mat = []; bvec = []
        for (aj, bj, ent) in rels:
            v = [0]*k
            for (col, c) in ent:
                v[col] = (v[col] + c) % n
            rows_mat.append(v + [(-aj) % n])
            bvec.append(bj % n)
        try:
            Mm = Matrix(GF(n), rows_mat)
            bb = vector(GF(n), bvec)
            x = Mm.solve_right(bb)
            rka = int(Mm.rank())
            rec = int(x[k]) % n
            return {"rank_aug": rka, "recovered": rec, "success": bool(rka == k+1 and rec == secret % n), "n_relations": len(rels)}
        except Exception as e:
            return {"rank_aug": None, "recovered": None, "success": False, "error": str(e), "n_relations": len(rels)}
    rels_b, tests_b, fails_b = collect(int(M))
    dlp_baseline = solve_dlp(rels_b)
    rels_o, tests_o, fails_o = collect(reps)
    dlp_orbit = solve_dlp(rels_o)
    # ----- null model: uniform random N-subsets -----
    rng2 = np.random.RandomState(int(seed) + 999983)
    nulls = []
    for d in range(NULL_DRAWS):
        sub = rng2.choice(int(M), size=int(N), replace=False)
        fn = np.zeros(M, dtype=np.int64); fn[sub] = 1
        wn = []
        for lam in range(10):
            acc = apply_proj(fn, lam)
            wn.append(float(Fraction(int(acc @ acc) * int(dims[lam]) * int(dims[lam]), int(NG*NG))))
        oh = int(len(np.unique(orbit_id[sub])))
        nulls.append({"w": wn, "orbits_hit": oh})
    null_w = np.array([nl["w"] for nl in nulls])  # 8 x 10
    envelope = []
    for lam in range(10):
        col = null_w[:, lam]
        mn = float(col.min()); mx = float(col.max()); mean = float(col.mean())
        sd = float(col.std())
        z = (w_float[lam] - mean) / sd if sd > 0 else None
        envelope.append({"label": labels[lam], "null_min": mn, "null_max": mx, "null_mean": mean,
                         "null_std": sd, "ec": w_float[lam], "z": z,
                         "ec_within_range": bool(mn <= w_float[lam] <= mx)})
    null_oh = [nl["orbits_hit"] for nl in nulls]
    # ----- LA factor -----
    sum_rcubes = int(sum(int(r)**3 for r in r_blocks))
    la_factor = float(Fraction(int(r_full)**3, sum_rcubes)) if sum_rcubes > 0 else None
    per_seed = {
        "seed": seed, "t0": t0, "N": N,
        "w": [{"label": labels[lam], "exact": "%d/%d" % (w[lam].numerator, w[lam].denominator), "float": w_float[lam]} for lam in range(10)],
        "w_sum_check": str(sum(w)),
        "w_triv": float(w[triv_lam]),
        "w_triv_centered": float(w_triv_centered),
        "w_triv_share": float(w[triv_lam] / N),
        "r_full": r_full, "r_triv": r_blocks[triv_lam], "r_blocks": r_blocks,
        "sum_r": sum(r_blocks), "sum_rcubes": sum_rcubes, "la_factor": la_factor,
        "orbits_hit": orbits_hit, "storage_factor": storage_factor,
        "combined_la_storage_factor": (la_factor / storage_factor) if la_factor else None,
        "blind_flags": blind_flags,
        "dlp": {"secret": secret, "baseline": dlp_baseline, "orbit_scan": dlp_orbit,
                "baseline_tests": tests_b, "orbit_tests": tests_o,
                "baseline_fails": fails_b, "orbit_fails": fails_o},
        "null_envelope": envelope,
        "null_orbits_hit": {"min": min(null_oh), "max": max(null_oh), "mean": float(np.mean(null_oh))},
        "controls": {"parseval": bool(parseval_ok), "conservation": conservation_ok, "spotcheck": bool(spot_ok),
                     "degenerate_P4": degenerate, "baseline_failed_decomps": fails_b, "orbit_failed_decomps": fails_o},
        "seed_wall_seconds": time.time() - ts,
    }
    result["per_seed"].append(per_seed)
    log("seed %d done: N=%d r_full=%d r_blocks=%s orbits_hit=%d wall=%.1fs" % (seed, N, r_full, r_blocks, orbits_hit, time.time()-ts))

result["finished_at"] = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
result["wall_seconds"] = time.time() - T0
log("total wall %.1fs" % result["wall_seconds"])

if OUT:
    with open(OUT, "w") as fh:
        json.dump(result, fh, indent=1, default=str)
    log("wrote %s" % OUT)
else:
    print(json.dumps(result, indent=1, default=str))

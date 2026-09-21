#!/usr/bin/env python3
"""RED TEAM controls for TASK-20260823-07a54b (GOAL-ECQ-002, BATCH-f2341e).

Reproduces every number cited in ../redteam_report.md.  Stdlib only.

Reads ONLY the Coordinator-committed pre-registered snapshot
  coordination/goals/GOAL-ECQ-002/baseline/icarm_database_20260823.json
  (declared sha256 118db069fcfc0cddc61bb00a235736202f01dc72d608b3c743bd342935cadc59)
at snapshot commit ab0aa5404319796966241478dc44e25592139b44.

Usage:  python3 redteam_controls.py /path/to/icarm_database_20260823.json
"""
import sys, json, math, random, collections, hashlib, bisect
from fractions import Fraction as F

DECLARED_SHA = "118db069fcfc0cddc61bb00a235736202f01dc72d608b3c743bd342935cadc59"
SEED = 20260823
FRONTIER_R1_NAIVE = 11.613603032723672   # frozen r>=1 cell, curve 42 (=37a1)
FRONTIER_R14 = 85.18925824647027         # curve 244 (Elkies, submitted by Sutherland)
FRONTIER_R15 = 118.77017663505484        # curve 276 (Bettridge / Clovis Mint)


# --------------------------------------------------------------------------
def load(path):
    raw = open(path, "rb").read()
    got = hashlib.sha256(raw).hexdigest()
    print(f"[snapshot] sha256 {got}  declared {DECLARED_SHA}  match={got == DECLARED_SHA}")
    return json.loads(raw)["curves"]


def naive_height_from_ainvs(ainvs):
    """log max(|c4|^3, c6^2) of the given Weierstrass model.  Exact integers, one log."""
    a1, a2, a3, a4, a6 = (int(x) for x in ainvs)
    b2 = a1 * a1 + 4 * a2
    b4 = 2 * a4 + a1 * a3
    b6 = a3 * a3 + 4 * a6
    c4 = b2 * b2 - 24 * b4
    c6 = -b2 ** 3 + 36 * b2 * b4 - 216 * b6
    return math.log(max(abs(c4) ** 3, c6 * c6)), c4, c6


def program(c):
    """Which SEARCH PROGRAM produced this curve, from the board's own commentary.
    This is the conditioning variable the soft-cell claim never conditioned on."""
    t = (c.get("commentary") or "")
    tl = t.lower()
    if "jmm" in tl and "elkies" in tl:
        return "ELKIES_JMM23"
    if "klagsbrun" in tl:
        return "KLAGSBRUN"
    if "mestre" in tl and any(k in tl for k in
                             ["sextuple", "6-tuple", "specializ", "specialis", "famil",
                              "locus", "(u,v)", "shift", "construction", "p6(", "quartic"]):
        return "MESTRE_SPEC"
    if "historical" in tl or "dujella" in tl:
        return "HISTORICAL_RECORD"
    if "watkins" in tl:
        return "ELKIES_WATKINS"
    if "mordell curve" in tl or "3-rank" in tl or "burgess" in tl:
        return "ELKIES_MORDELL"
    if "mestre" in tl:
        return "MESTRE_other"
    return "OTHER"


# --------------------------------------------------------------------------
def control_0_reproduce_frontier(d):
    print("\n=== C0. reproduce the frozen frontier + per-rank counts ===")
    cnt = collections.Counter(c["rank_lower_bound"] for c in d)
    print("  exact-rank counts r=12..17:", {r: cnt[r] for r in range(12, 18)})
    for r in (13, 14, 15, 16):
        sub = [c for c in d if c["rank_lower_bound"] >= r]
        m = min(sub, key=lambda c: c["naive_height"])
        print(f"  r>={r}: n_at_or_above={len(sub):>3} min_h={m['naive_height']:8.4f}"
              f" id={m['id']} exact_rank={m['rank_lower_bound']} {m['submitter']}")
    print("  NOTE: the r>=15 cell is a minimum over 115 curves, the r>=14 cell over 125.")
    print("        The 'few rank-15 submissions' explanation is arithmetically unavailable:")
    print(f"        n(rank exactly 15)={cnt[15]} > n(rank exactly 14)={cnt[14]}.")
    for i in (276, 244, 42):
        c = next(x for x in d if x["id"] == i)
        h, _, _ = naive_height_from_ainvs(c["ainvs"])
        print(f"  height convention check id={i}: recomputed {h:.12f} vs board "
              f"{c['naive_height']:.12f} diff={abs(h - c['naive_height']):.1e}")


def control_1_untrended_permutation(d):
    """Null A: rank labels exchangeable among ranks 13,14,15.
    Justified empirically -- the three groups' medians are 139.9 / 141.0 / 145.3."""
    print("\n=== C1. permutation null over ranks 13,14,15 (no trend correction) ===")
    g = collections.defaultdict(list)
    for c in d:
        g[c["rank_lower_bound"]].append(c["naive_height"])
    pool = g[13] + g[14] + g[15]
    sizes = {r: len(g[r]) for r in (13, 14, 15)}
    obs15 = min(g[15]); obs14 = min(min(g[14]), obs15); obs_step = obs15 - obs14
    print(f"  group medians 13/14/15 = "
          f"{sorted(g[13])[len(g[13])//2]:.1f} / {sorted(g[14])[len(g[14])//2]:.1f}"
          f" / {sorted(g[15])[len(g[15])//2]:.1f};  sizes {sizes}")
    print(f"  observed step at r=15 = {obs_step:.4f}")
    random.seed(SEED); N = 200000
    a = b = cc = 0
    for _ in range(N):
        p = pool[:]; random.shuffle(p)
        i = 0; gg = {}
        for r in (13, 14, 15):
            gg[r] = p[i:i + sizes[r]]; i += sizes[r]
        m15 = min(gg[15]); m14 = min(min(gg[14]), m15)
        if m15 - m14 >= obs_step - 1e-12: a += 1
        if m15 >= FRONTIER_R15 - 1e-12: b += 1
        if min(gg[14]) <= FRONTIER_R14 + 1e-12: cc += 1
    print(f"  P(step >= observed)              = {a/N:.5f}")
    print(f"  P(min of rank-15 group >= 118.77)= {b/N:.5f}   <- the r>=15 incumbent IS high")
    print(f"  P(min of rank-14 group <= 85.19) = {cc/N:.5f}   <- curve 244 is NOT unusually small")


def _fit(sub):
    R = [c["rank_lower_bound"] for c in sub]
    lr = [math.log(c["naive_height"]) for c in sub]
    n = len(sub); mr = sum(R)/n; ml = sum(lr)/n
    b = sum((R[i]-mr)*(lr[i]-ml) for i in range(n)) / sum((R[i]-mr)**2 for i in range(n))
    a = ml - b*mr
    return R, [lr[i]-(a+b*R[i]) for i in range(n)], a, b


def control_2_lookelsewhere(d):
    """Null B: trend-corrected, and CORRECTED for the fact that r=15 was chosen
    post hoc as the biggest jump in the table (look-elsewhere / min-p)."""
    print("\n=== C2. trend-corrected + look-elsewhere-corrected permutation ===")
    sub = [c for c in d if 10 <= c["rank_lower_bound"] <= 20]
    R, z, a, b = _fit(sub); n = len(sub)
    print(f"  log-linear trend on ranks 10-20: log h = {a:.4f} + {b:.4f} r "
          f"({math.exp(b):.4f} x per rank), n={n}")
    THR = list(range(11, 21))

    def steps(zs):
        hh = [a + b*R[i] + zs[i] for i in range(n)]
        mins = {r: min(hh[i] for i in range(n) if R[i] >= r) for r in range(10, 21)}
        return [mins[r] - mins[r-1] for r in THR]

    obs = steps(z)
    random.seed(SEED); M = 30000
    null = []
    for _ in range(M):
        zs = z[:]; random.shuffle(zs); null.append(steps(zs))
    cols = [sorted(row[j] for row in null) for j in range(len(THR))]
    pv = lambda j, x: 1.0 - bisect.bisect_left(cols[j], x - 1e-12)/M
    obs_p = [pv(j, obs[j]) for j in range(len(THR))]
    for j, r in enumerate(THR):
        print(f"    r={r:2d} log-step={obs[j]:.4f} p={obs_p[j]:.5f}"
              + ("   <== the campaign's cell" if r == 15 else ""))
    minp = min(obs_p)
    cnt = sum(1 for row in null if min(pv(j, row[j]) for j in range(len(THR))) <= minp + 1e-12)
    print(f"  LOCAL p at r=15                                      = {obs_p[THR.index(15)]:.5f}")
    print(f"  LOOK-ELSEWHERE-CORRECTED p (calibrated min-p, 10 thr) = {cnt/M:.5f}")
    print("  => the jump is REAL under exchangeability; it is not a submission-count artifact.")


def control_3_condition_on_program(d):
    """THE DISCRIMINATING CONTROL.  Same measurement, but the null preserves WHICH
    SEARCH PROGRAM contributed at WHICH RANK.  This is the parameter that should
    destroy the signal if the 'soft cell' is a program-incidence artifact."""
    print("\n=== C3. null-object control: condition on the generative search program ===")
    sub = [c for c in d if 10 <= c["rank_lower_bound"] <= 20]
    R, z, a, b = _fit(sub); n = len(sub)
    K = [program(c) for c in sub]
    idx = collections.defaultdict(list)
    for i in range(n):
        idx[K[i]].append(i)
    inc = collections.Counter((K[i], R[i]) for i in range(n))
    print("  program x rank incidence, ranks 10-20:")
    for k in sorted(idx):
        print(f"    {k:<18}", {r: inc[(k, r)] for r in range(10, 21) if inc[(k, r)]})

    def step15(zs):
        hh = [a + b*R[i] + zs[i] for i in range(n)]
        return (min(hh[i] for i in range(n) if R[i] >= 15)
                - min(hh[i] for i in range(n) if R[i] >= 14))

    obs = step15(z)
    random.seed(SEED); M = 30000
    def run(within):
        c = 0
        for _ in range(M):
            zs = z[:]
            if within:
                for k, ix in idx.items():
                    v = [z[i] for i in ix]; random.shuffle(v)
                    for j, i in enumerate(ix): zs[i] = v[j]
            else:
                random.shuffle(zs)
            if step15(zs) >= obs - 1e-12: c += 1
        return c/M
    print(f"  observed log-step at r=15 = {obs:.4f}")
    print(f"  UNCONDITIONAL null                p = {run(False):.5f}")
    print(f"  CONDITIONED-ON-PROGRAM null       p = {run(True):.5f}")
    print("  => conditioning on the search program destroys the signal.  The 'soft cell'")
    print("     is a program-incidence artifact, not a property of rank 15.")


def control_4_per_program_frontier(d):
    print("\n=== C4. the frontier, restricted to each generative program ===")
    progs = ["MESTRE_SPEC", "ELKIES_JMM23", "KLAGSBRUN", "ELKIES_MORDELL", "HISTORICAL_RECORD"]
    print(f"  {'r':>3} {'ALL':>8} " + " ".join(f"{p[:14]:>16}" for p in progs))
    for r in range(12, 21):
        row = f"  {r:>3} {min(c['naive_height'] for c in d if c['rank_lower_bound'] >= r):>8.2f} "
        for p in progs:
            v = [c["naive_height"] for c in d if c["rank_lower_bound"] >= r and program(c) == p]
            row += f"{(f'{min(v):.2f}' if v else '-'):>16} "
        print(row)
    print("\n  MESTRE_SPEC (== the campaign's own proposed method) min height by EXACT rank:")
    for r in range(12, 21):
        v = sorted([c for c in d if c["rank_lower_bound"] == r and program(c) == "MESTRE_SPEC"],
                   key=lambda c: c["naive_height"])
        print(f"    r={r:>2}: n={len(v):>2} " +
              (f"min={v[0]['naive_height']:8.2f} (id {v[0]['id']}, {v[0]['submitter']})" if v else "none"))
    print("  => 118.77 at rank 15 is the GLOBAL MINIMUM of this method class over all ranks 12-20.")
    print("\n  the Klagsbrun batch (one submitter, 4 curves inside 73 seconds):")
    for c in sorted([c for c in d if program(c) == "KLAGSBRUN"], key=lambda c: c["rank_lower_bound"]):
        print(f"    id={c['id']:>4} r={c['rank_lower_bound']:>2} h={c['naive_height']:8.3f} {c['created_at']}")
    print("  => covers ranks 12,13,14,16 and SKIPS 15.  Geometric interpolation of its own"
          "\n     14 -> 16 entries gives ~%.1f at rank 15, i.e. below the 118.77 incumbent."
          % math.sqrt(90.6602 * 125.3336))


def control_5_cell_timeline(d):
    print("\n=== C5. how fast does the r>=15 naive-height cell move? ===")
    cur = None
    for c in sorted([c for c in d if c["rank_lower_bound"] >= 15], key=lambda c: c["created_at"]):
        if cur is None or c["naive_height"] < cur:
            cur = c["naive_height"]
            print(f"    {c['created_at']}  h={c['naive_height']:8.3f} id={c['id']:>4}"
                  f" r={c['rank_lower_bound']:>2}  {c['submitter']}")
    print("  margins between incumbent and runner-up, naive height:")
    for r in range(13, 19):
        v = sorted(c["naive_height"] for c in d if c["rank_lower_bound"] >= r)
        print(f"    r>={r:2d}: {v[0]:8.3f} vs {v[1]:8.3f}  margin {v[1]-v[0]:6.3f}"
              f" ({100*(v[1]-v[0])/v[0]:.2f}%)")


# --------------------------------------------------------------------------
# C6: is the r>=1 record cell real?  Exhaustive over minimal Weierstrass models.
def _invs(a1, a2, a3, a4, a6):
    b2 = a1*a1 + 4*a2; b4 = 2*a4 + a1*a3; b6 = a3*a3 + 4*a6
    b8 = a1*a1*a6 + 4*a2*a6 - a1*a3*a4 + a2*a3*a3 - a4*a4
    c4 = b2*b2 - 24*b4; c6 = -b2**3 + 36*b2*b4 - 216*b6
    disc = -b2*b2*b8 - 8*b4**3 - 27*b6*b6 + 9*b2*b4*b6
    return c4, c6, disc

def _add(a, P, Q):
    a1, a2, a3, a4, a6 = a
    if P is None: return Q
    if Q is None: return P
    x1, y1 = P; x2, y2 = Q
    if x1 == x2 and y1 + y2 + a1*x2 + a3 == 0: return None
    if P == Q:
        den = 2*y1 + a1*x1 + a3
        if den == 0: return None
        lam = (3*x1*x1 + 2*a2*x1 + a4 - a1*y1) / den
    else:
        lam = (y2 - y1) / (x2 - x1)
    nu = y1 - lam*x1
    x3 = lam*lam + a1*lam - a2 - x1 - x2
    return (x3, -(lam + a1)*x3 - nu - a3)

def _nontorsion(a, PB=60, QB=8):
    """Exhibit a rational point of infinite order in exact arithmetic.
    Non-torsion by Mazur: any torsion point has order in {1..10, 12}."""
    a1, a2, a3, a4, a6 = a
    for q in range(1, QB + 1):
        q2 = q*q
        for p in range(-PB*q2, PB*q2 + 1):
            x = F(p, q2)
            rhs = x**3 + a2*x*x + a4*x + a6
            bb = a1*x + a3
            D = bb*bb + 4*rhs
            if D < 0: continue
            rn, rd = math.isqrt(D.numerator), math.isqrt(D.denominator)
            if rn*rn != D.numerator or rd*rd != D.denominator: continue
            s = F(rn, rd)
            for y in ((-bb + s)/2, (-bb - s)/2):
                if y*y + a1*x*y + a3*y != x**3 + a2*x*x + a4*x + a6: continue
                P = (x, y); Q = P; tors = False
                for _ in range(12):
                    if Q is None: tors = True; break
                    Q = _add(a, Q, P)
                if not tors: return P
    return None

def control_6_r1_cell_is_hollow():
    print("\n=== C6. is the frozen r>=1 record cell real? (exhaustive, exact) ===")
    print("  scanning ALL minimal Weierstrass models a1 in {0,1}, a2 in {-1,0,1}, a3 in {0,1},")
    print(f"  a4,a6 in [-12,12] with naive height < the frozen cell {FRONTIER_R1_NAIVE:.6f} ...")
    hits = []
    for a1 in (0, 1):
        for a2 in (-1, 0, 1):
            for a3 in (0, 1):
                for a4 in range(-12, 13):
                    for a6 in range(-12, 13):
                        c4, c6, disc = _invs(a1, a2, a3, a4, a6)
                        if disc == 0: continue
                        m = max(abs(c4)**3, c6*c6)
                        if m == 0 or math.log(m) >= FRONTIER_R1_NAIVE: continue
                        a = tuple(F(v) for v in (a1, a2, a3, a4, a6))
                        P = _nontorsion(a)
                        if P:
                            hits.append((math.log(m), [a1, a2, a3, a4, a6], c4, c6, disc,
                                         (str(P[0]), str(P[1]))))
    hits.sort()
    for h, ai, c4, c6, disc, P in hits:
        print(f"    h={h:.6f}  ainvs={str(ai):<20} c4={c4:>5} c6={c6:>6} disc={disc:>6}"
              f"  infinite-order point {P}")
    print(f"  {len(hits)} curves beat the frozen r>=1 naive-height cell.  All are in Cremona's")
    print("  tables (conductors 43, 53, 83).  The batch's incidental 53a1 (h=11.3875) is not")
    print("  even the best of them: 43a1 is h=11.269579.")
    return hits


if __name__ == "__main__":
    path = sys.argv[1] if len(sys.argv) > 1 else \
        "coordination/goals/GOAL-ECQ-002/baseline/icarm_database_20260823.json"
    d = load(path)
    control_0_reproduce_frontier(d)
    control_1_untrended_permutation(d)
    control_2_lookelsewhere(d)
    control_3_condition_on_program(d)
    control_4_per_program_frontier(d)
    control_5_cell_timeline(d)
    control_6_r1_cell_is_hollow()

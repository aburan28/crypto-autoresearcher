#!/usr/bin/env python3
"""Proves-too-much control (validator TASK-20260926-44629c, REVIEW-ICPERF-20260926-bcf1b2).

The free-oracle floor of KN-FIND-aa2efc is a claimed LOWER BOUND on any attack in the
decomposition-oracle family: F(m; N) = min over l of [ R(l) * N / C(2^l, m) + m R(l)^2 ], with
R(l) = 2^l (subspace base) or 2^l / n (Frobenius-stable set), one operation charged per target
tried, the oracle charged nothing.  Instantiate it at the toy Koblitz cells where the external
repository MEASURED whole index-calculus solves, and compare with the measured cost.

Same-unit object: docs/ic/runs/ic-boundary-ledger-round3-2026-09-21.json (unit S = group-addition
equivalents / sqrt(r); total_gae is the whole solve, native counts exact).  Base shape there:
Frobenius orbit unions with signed-orbit columns (one unknown per <pi,-1>-orbit), m = 2 and 3.
Tournament cells (rounds 0021/0022): unit is whole-process callgrind instructions; NO conversion to
group operations is recorded, so those cells get the bounding arithmetic only and are marked
inconclusive on unit grounds.
"""
import json, mpmath as mp
from math import comb, log2, sqrt, pi
mp.mp.dps = 40
LEDGER = "/home/user/crypto/docs/ic/runs/ic-boundary-ledger-round3-2026-09-21.json"

def binom_real(x, m):
    x = mp.mpf(x); p = mp.mpf(1)
    for i in range(m): p *= (x - i)
    return p / mp.factorial(m)

def floor_min(m, N, div):
    """min over real l of [ (2^l/div) N / C(2^l, m) + m (2^l/div)^2 ]; targets term floored at 1 target per relation."""
    def c(l):
        F = mp.power(2, l); R = F / div
        tpr = N / binom_real(F, m)
        if tpr < 1: tpr = mp.mpf(1)
        return R * tpr + m * R * R
    lo, hi = mp.mpf(log2(m) + 0.01), mp.mpf(log2(N) + 2)
    gr = (mp.sqrt(5) - 1) / 2; a, b = lo, hi
    for _ in range(200):
        cc = b - gr * (b - a); d = a + gr * (b - a)
        if c(cc) < c(d): b = d
        else: a = cc
    l = (a + b) / 2
    return float(l), float(c(l))

def trace(n, t1):
    tp, t = 2, t1
    for _ in range(2, n + 1): tp, t = t, t1 * t - 2 * tp
    return t

def order(n, a):
    t1 = -1 if a == 0 else 1
    return 2 ** n + 1 - trace(n, t1)

def b(x): return log2(x) if x > 0 else float('nan')

d = json.load(open(LEDGER))
print("LEDGER unit:", d['ledger']['unit'])
print("LEDGER reference:", d['ledger']['reference'])
inst = [i for i in d['ledger']['instances'] if i['regime'] == 'koblitz']
print(f"{len(inst)} Koblitz instances\n")

worst = []
for i in inst:
    n = i['curve']['field']['degree']; a = i['curve']['a']; r = i['r']; N = int(i['group_order']); h = i['cofactor']
    Ecalc = order(n, a)
    rho_mean_gae = i['rho_s_mean'] * sqrt(r)
    rho_formula = sqrt(pi * r / (4 * n))
    print("=" * 110)
    print(f"{i['curve']['name']}  a={a} n={n} r={r} (2^{b(r):.2f}) #E={N} cofactor={h}  recurrence #E={Ecalc} match={Ecalc == N}")
    print(f"  rho: formula sqrt(pi r/(4n)) = {rho_formula:.1f} steps; ledger expected_steps={i['rho'][0]['expected_steps']:.1f}; ledger mean rho gae = {rho_mean_gae:.1f} (S={i['rho_s_mean']:.3f}); generic floor S={i['floor_s']:.4f}")
    floors = {}
    for m in (2, 3):
        for lab, div in (("no-collapse (finding table)", 1), ("collapse /n", n), ("collapse /2n (signed orbits)", 2 * n)):
            for Nlab, NN in (("N=#E", N), ("N=r", r)):
                l, f = floor_min(m, NN, div)
                floors[(m, lab, Nlab)] = (l, f)
    for m in (2, 3):
        print(f"  free-oracle floors m={m} [gae, bits]: " + "; ".join(f"{lab},{Nlab}: 2^{b(f):.2f} (l*={l:.1f})" for (mm, lab, Nlab), (l, f) in floors.items() if mm == m))
    for v in i['variants']:
        m = v['summands']; F = v['signed_points']; K = v['columns']; tot = v['total_gae']; trials = v['trials']
        rel = v['relations']['gae']; fb = v['factor_base']['gae']; la = v['linear_algebra']['gae']
        # floor model evaluated at the row's own base: relations = K (signed-orbit columns), targets/relation = max(1, N/C(F,m)), LA = m K^2
        tpr = max(1.0, N / comb(F, m)); T_row = K * tpr; LA_row = m * K * K
        tpr_r = max(1.0, r / comb(F, m)); T_row_r = K * tpr_r
        shape_floor = floors[(m, "collapse /2n (signed orbits)", "N=#E")][1]
        shape_floor_r = floors[(m, "collapse /2n (signed orbits)", "N=r")][1]
        nc = floors[(m, "no-collapse (finding table)", "N=#E")][1]
        flag = ""
        if tot < shape_floor_r: flag = "  <<< BELOW shape-matched floor even with N=r"
        elif tot < shape_floor: flag = "  <<< BELOW shape-matched floor with N=#E (above it with N=r)"
        worst.append((tot / shape_floor, i['curve']['name'], v['name'], tot, shape_floor, shape_floor_r))
        print(f"  {v['name']:<58} m={m} |F|={F:>6} K={K:>4} table={v['table']:<17} tgt={v['targets']:<6} trials={trials:>9} rels={v['relations_found']:>4} "
              f"total={tot:>12.0f} (2^{b(tot):.2f}, {v['ratio_to_rho']:.1f}x rho) [fb {fb:.0f} rel {rel:.0f} la {la:.1f}] | "
              f"model@row: T={T_row:.0f} (N=r: {T_row_r:.0f}) LA={LA_row} trials/T={trials/T_row:.2f} | total/floor_shape(#E)=2^{b(tot/shape_floor):+.2f} total/floor_shape(r)=2^{b(tot/shape_floor_r):+.2f} total/floor_nocollapse=2^{b(tot/nc):+.2f}{flag}")
print()
print("=" * 110)
print("SUMMARY over all Koblitz rows: measured total / shape-matched collapsed floor (N=#E), smallest ratios first")
for ratio, cname, vname, tot, fl, flr in sorted(worst)[:12]:
    print(f"  2^{b(ratio):+.2f}  {cname:<18} {vname:<58} total={tot:.0f} floor(#E)={fl:.0f} floor(r)={flr:.0f}")
print(f"  minimum ratio over {len(worst)} rows: 2^{b(min(w[0] for w in worst)):+.2f}; rows below the shape-matched floor (N=#E): {sum(1 for w in worst if w[0] < 1)}; below the N=r variant: {sum(1 for w in worst if w[3] < w[5])}")

print()
print("=" * 110)
print("TOURNAMENT CELLS (rounds 0021/0022): unit = whole-process callgrind instructions; bounding arithmetic only")
print("=" * 110)
CELLS = [('n23a1', 23, 1, 4_196_903, 8, 0.831, (0.772, 0.894), (2_598_899, 5_268_988)),
         ('n37a0', 37, 0, 230_603_167, 16, 1.396, (1.244, 1.567), (50_425_517, 24_665_546)),
         ('n43a1', 43, 1, 4_644_189_029, 24, 2.207, (1.933, 2.519), None)]
for name, n, a, r, orbits, ratio, band, ir in CELLS:
    N = order(n, a); h = N // r; assert N % r == 0
    rho_ops = sqrt(pi * r / (4 * n))
    absc = orbits * n; pts = 2 * absc  # every abscissa of a lifting orbit lifts; both signs
    K = orbits
    fl2 = floor_min(2, N, 2 * n); fl2r = floor_min(2, r, 2 * n); fl2nc = floor_min(2, N, 1)
    tpr = max(1.0, N / comb(pts, 2)); T_row = K * tpr
    print(f"{name}: a={a} n={n} r={r} #E={N} cofactor={h}; base {orbits} orbits = {absc} abscissae ~ {pts} signed points, K={K} columns")
    print(f"   rho expected steps sqrt(pi r/(4n)) = {rho_ops:.1f} group ops; measured IC/rho = {ratio} {band} in INSTRUCTIONS" + (f"; single-fixture Ir ic={ir[0]:,} rho={ir[1]:,} -> {ir[1]/rho_ops:,.0f} instructions per expected rho step" if ir else ""))
    print(f"   m=2 floors: shape-matched /2n N=#E 2^{b(fl2[1]):.2f} ({fl2[1]:.0f} ops, l*={fl2[0]:.1f}); N=r 2^{b(fl2r[1]):.2f} ({fl2r[1]:.0f}); finding's no-collapse 2^{b(fl2nc[1]):.2f}")
    print(f"   floor/rho in GROUP OPS: shape-matched(#E) {fl2[1]/rho_ops:.2f}x, (r) {fl2r[1]/rho_ops:.2f}x, no-collapse {fl2nc[1]/rho_ops:.2f}x  vs measured IC/rho in INSTRUCTIONS {ratio}x")
    print(f"   model at the cell's own base: targets = K x max(1, #E/C(pts,2)) = {T_row:.0f}; + LA 2K^2 = {2*K*K}; that alone is {T_row/rho_ops:.2f}x rho's expected steps")
    print(f"   -> a same-unit comparison needs instructions-per-group-op for BOTH arms; none is recorded in rounds 0021/0022. INCONCLUSIVE on unit grounds.")
    print(f"      For the measured instruction ratio to be consistent with the shape-matched floor, the IC arm would need at least {fl2[1]/rho_ops/ratio:.1f}x fewer instructions per group-op-equivalent than the rho arm (or the same factor in fixed overhead).")
print()
print("CROSS-CHECK at n=23 (same curve, same r, same family, two harnesses): ledger m=2 frobfold_walk row = 7.47x rho in group-addition equivalents; tournament koblitz_tiny_ic = 0.831x rho in instructions.")
print("  The two harnesses disagree by ~9x on IC/rho for the same cell and family, which is exactly why the instruction ratio cannot be read as a group-operation ratio.")

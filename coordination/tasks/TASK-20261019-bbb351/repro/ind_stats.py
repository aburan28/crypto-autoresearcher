"""Validator re-derivation of the t8 statistics, the frozen decision rule, the I10 flag and the MDE/powered
question, from the raw per-member coverages only (indlib.py; no experiment code)."""
import math, json, collections
import numpy as np
from indlib import *

DELTA, ALPHA, DRAWS, RES = 0.005, 0.05, 20000, 5000
mem = []
for t in ('t4', 't5', 't6', 't7'):
    mem += load(t)['members']
rec8 = load('t8')
cells = ['C16', 'C20', 'C24']
ARMS = ['FAM', 'N-A', 'N-B']


def rng(seed, cell, arm, a, b):
    return np.random.Generator(np.random.PCG64(np.random.SeedSequence([seed, CELL_CODE[cell], ARM_CODE[arm], a, b])))


def blocks(n, L, g, R):
    L = min(L, n)
    if L == 1:
        return g.integers(0, n, size=(R, n))
    nb = -(-n // L)
    s = g.integers(0, n - L + 1, size=(R, nb))
    return (s[:, :, None] + np.arange(L)).reshape(R, nb * L)[:, :n]


def pct(d, level):
    a = 50 * (1 - level)
    return tuple(float(v) for v in np.percentile(d, [a, 100 - a]))


def holm(ps):
    items = sorted(ps.items(), key=lambda kv: (kv[1], str(kv[0])))
    out, run = {}, 0.0
    for r, (k, p) in enumerate(items):
        run = max(run, min(1.0, (len(items) - r) * p))
        out[k] = run
    return out


rows = {}
for cell in cells:
    for arm in ARMS:
        ms = sorted((m for m in mem if m['arm'] == arm and m['cell'] == cell), key=lambda m: m['index'])
        V = np.array([[m['member_seen']] + m['random_seen'] for m in ms], float)
        n = len(ms)
        x = V[:, 0] / V[:, 1:].mean(axis=1) - 1
        L = 3 if arm == 'FAM' else 1
        ci = pct(x[blocks(n, L, rng(7006, cell, arm, 0, 0), RES)].mean(axis=1), 0.95)
        u = rng(7007, cell, arm, 0, 0).integers(0, V.shape[1], size=(DRAWS, n))
        pick = V[np.arange(n)[None, :], u]
        ts = (pick / ((V.sum(axis=1)[None, :] - pick) / (V.shape[1] - 1)) - 1).mean(axis=1)
        p = (1 + int((np.abs(ts) >= abs(x.mean())).sum())) / (DRAWS + 1)
        sd = np.array([np.std(V[j, 1:], ddof=1) / V[j, 1:].mean() for j in range(n)])
        Ns = np.array([m['N'] for m in ms], float)
        rms = float(np.sqrt(np.mean(sd ** 2)))
        f14 = float(np.sqrt(np.mean((1.4 / np.sqrt(Ns)) ** 2)))
        # per-member ratio to 1.4/sqrt(N)
        pm = sd / (1.4 / np.sqrt(Ns))
        rows[(arm, cell)] = dict(n=n, x=x, T=float(x.mean()), ci=ci, p=p, rms=rms, f14=f14, ratio14=rms / f14,
                                 pm_min=float(pm.min()), pm_max=float(pm.max()),
                                 mde_spec=3.61 * rms / math.sqrt(n),             # frozen text: no inflation factor
                                 mde_code=1.0025 * math.sqrt(3) * 3.61 * rms / math.sqrt(n))

print('--- recomputed vs recorded (T, ci95, randomization p)')
bad = 0
for (arm, cell), r in rows.items():
    t = rec8['tables'][f'{arm}|{cell}']
    ok = (abs(t['T'] - r['T']) < 1e-12 and abs(t['ci95'][0] - r['ci'][0]) < 1e-12 and abs(t['ci95'][1] - r['ci'][1]) < 1e-12
          and abs(t['randomization_p'] - r['p']) < 1e-12 and t['n'] == r['n'])
    bad += (not ok)
    print(f"{arm:4s}{cell}: n={r['n']:2d} T={100*r['T']:+.5f}%  CI95=[{100*r['ci'][0]:+.4f}%, {100*r['ci'][1]:+.4f}%]  p={r['p']:.5f}  match_recorded={ok}")
print('rows differing from recorded:', bad)

print('--- I10: measured relative sd of the 200 random coverages vs the formula')
for (arm, cell), r in rows.items():
    t = rec8['tables'][f'{arm}|{cell}']
    print(f"{arm:4s}{cell}: rms_meas={r['rms']:.3e}  vs frozen 1.4/sqrt(N): ratio={r['ratio14']:.3f} (per-member min {r['pm_min']:.3f} max {r['pm_max']:.3f}) in-band[0.75,1.33]={0.75 <= r['ratio14'] <= 1.33}"
          f"   |  recorded (analyze.py draft occupancy formula) ratio={t['sigma_ratio']:.3f} flag={t['sigma_flag_I10']}")

print('--- MDE and POWERED')
for cell in cells:
    spec_ok = all(rows[(a, cell)]['mde_spec'] <= DELTA / 2 for a in ARMS)
    code_ok = all(rows[(a, cell)]['mde_code'] <= DELTA / 2 for a in ARMS)
    print(cell, 'MDE spec-literal (3.61*rms/sqrt n):', {a: round(100 * rows[(a, cell)]['mde_spec'], 4) for a in ARMS},
          '| code (x1.0025 x sqrt3):', {a: round(100 * rows[(a, cell)]['mde_code'], 4) for a in ARMS},
          '| mde_ok spec', spec_ok, 'code', code_ok, '| recorded powered', rec8['cells'][cell]['powered'])
print('recorded mde (code):', {k: round(100 * v['mde'], 4) for k, v in rec8['tables'].items()})


def classify(powered):
    ps = {k: rows[k]['p'] for k in rows if k[1] in powered}
    adj = holm(ps)
    exc = [k for k, a in adj.items() if a <= ALPHA and rows[k]['T'] > DELTA]
    dfc = [k for k, a in adj.items() if a <= ALPHA and rows[k]['T'] < -DELTA]
    rej = [k for k, a in adj.items() if a <= ALPHA]
    inside = all(rows[k]['ci'][0] >= -DELTA and rows[k]['ci'][1] <= DELTA for k in ps)
    if not powered:
        cl = 'R2 INCONCLUSIVE_UNDERPOWERED'
    elif not exc and not dfc and inside:
        cl = 'R3 NULL_AT_RESOLUTION'
    elif not exc and not dfc:
        cl = 'R4 INCONCLUSIVE_UNRESOLVED'
    elif exc:
        cl = 'R5 (lead)'
    else:
        cl = 'R6 DEFICIT_RECORDED'
    return adj, rej, cl


for label, powered in (('code powered set (C24 only)', ['C24']), ('spec-literal powered set (C20, C24)', ['C20', 'C24']),
                       ('pre-measurement member-count set (C20, C24)', ['C20', 'C24'])):
    adj, rej, cl = classify(powered)
    print(f'--- decision rule with {label}: {cl}; Holm rejections {rej}')
    print('    Holm-adjusted p:', {f'{k[0]}|{k[1]}': round(v, 4) for k, v in sorted(adj.items())})
print('recorded Holm-adjusted p:', {k: (round(v['holm_p'], 4) if v['holm_p'] is not None else None) for k, v in rec8['tables'].items()})

# ---- contrasts under both stream orderings
def xs(arm, cell, stratum=None):
    ms = sorted((m for m in mem if m['arm'] == arm and m['cell'] == cell and (stratum is None or m['stratum'] == stratum)), key=lambda m: m['index'])
    V = np.array([[m['member_seen']] + m['random_seen'] for m in ms], float)
    return V[:, 0] / V[:, 1:].mean(axis=1) - 1


print('--- contrasts (99%), producer stream order [seed,cell,arm,0,stream] vs spec-literal order [seed,cell,arm,stream,0]')
for cell in ['C20', 'C24']:
    for name, (a1, s1, a2, s2), sid in (('fam_na', ('FAM', None, 'N-A', None), 1), ('fam_natheta', ('FAM', None, 'N-A', 'theta'), 2), ('na_nb', ('N-A', None, 'N-B', None), 3)):
        x1, x2 = xs(a1, cell, s1), xs(a2, cell, s2)
        out = []
        for order in ('producer', 'literal'):
            g = rng(7006, cell, a1, 0, sid) if order == 'producer' else rng(7006, cell, a1, sid, 0)
            d1 = x1[blocks(len(x1), 3 if a1 == 'FAM' else 1, g, RES)].mean(axis=1)
            d2 = x2[blocks(len(x2), 3 if a2 == 'FAM' else 1, g, RES)].mean(axis=1)
            lo, hi = pct(d1 - d2, 0.99)
            out.append((round(100 * lo, 4), round(100 * hi, 4), bool(lo > 0 or hi < 0)))
        rc = rec8['contrasts'].get(f'{name}|{cell}')
        print(f'  {name}|{cell}: est={100*(x1.mean()-x2.mean()):+.4f}%  producer-order CI99%={out[0][:2]} excl0={out[0][2]}  literal-order CI99%={out[1][:2]} excl0={out[1][2]}  recorded={None if rc is None else [round(100*rc["ci99"][0],4), round(100*rc["ci99"][1],4)]}')

# ---- robustness: CI for FAM|C24 and the randomization test p under 5 other seeds' streams (sensitivity to RNG, not a re-test)
print('--- sensitivity of the headline numbers to the RNG stream (not new tests)')
for arm in ARMS:
    r = rows[(arm, 'C24')]
    ms = sorted((m for m in mem if m['arm'] == arm and m['cell'] == 'C24'), key=lambda m: m['index'])
    V = np.array([[m['member_seen']] + m['random_seen'] for m in ms], float)
    n = len(ms)
    ps, cis = [], []
    for s in range(1, 6):
        u = rng(7007, 'C24', arm, 99, s).integers(0, V.shape[1], size=(DRAWS, n))
        pick = V[np.arange(n)[None, :], u]
        ts = (pick / ((V.sum(axis=1)[None, :] - pick) / (V.shape[1] - 1)) - 1).mean(axis=1)
        ps.append((1 + int((np.abs(ts) >= abs(r['x'].mean())).sum())) / (DRAWS + 1))
        cis.append(pct(r['x'][blocks(n, 3 if arm == 'FAM' else 1, rng(7006, 'C24', arm, 99, s), RES)].mean(axis=1), 0.95))
    print(f'  {arm}|C24: randomization p over 5 alt streams: {[round(v,4) for v in ps]} ; CI95 lower/upper range: [{100*min(c[0] for c in cis):+.4f}%, {100*max(c[1] for c in cis):+.4f}%]')

# exact permutation-free check: with p~0.03 at FAM|C24, per-member ratio list
x = rows[('FAM', 'C24')]['x']
print('FAM|C24 per-member (ratio-1)% :', [round(100 * v, 4) for v in x])
print('mean log2 p / T slope informal: none (growth not assessable: powered cells <3)')

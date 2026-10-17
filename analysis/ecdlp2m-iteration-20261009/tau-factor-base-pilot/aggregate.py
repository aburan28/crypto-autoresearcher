#!/usr/bin/env python3
"""Aggregate results/cells.jsonl into aggregate.md (derived numbers only)."""
import json, math, sys, collections, hashlib, os

HERE = os.path.dirname(os.path.abspath(__file__))
cells = [json.loads(l) for l in open(os.path.join(HERE, 'results/cells.jsonl'))]
curves = [json.loads(l) for l in open(os.path.join(HERE, 'results/curves.jsonl'))]


def lg(x):
    return math.log2(x) if x and x > 0 else float('nan')


def fmt(x, d=3):
    if x is None or (isinstance(x, float) and math.isnan(x)):
        return '--'
    return f'{x:.{d}f}'


# ---- pool replicates per (n, m, k, V)
pool = collections.OrderedDict()
for c in cells:
    key = (c['n'], c['m'], c['k'], c['V'])
    p = pool.setdefault(key, dict(reps=0, targets=0, succ=0, dec=0, rows=0, lam_t=0.0, FBp=[], FBx=[], orb=[], Vs=[],
                                  shifts_w=0.0, shifts_n=0, conj=[], nbU=[], nbUFB=[], censored=False, a=c['a'], r=c['r'], h=c['h']))
    p['reps'] += 1
    p['targets'] += c['targets']
    p['succ'] += c['successes']
    p['dec'] += c['decompositions']
    p['rows'] += c.get('reduced_rows', c['decompositions'])
    p['lam_t'] += c['heuristic_lambda_r'] * c['targets']
    p['FBp'].append(c['FB_points']); p['FBx'].append(c['FB_x']); p['orb'].append(c['tau_orbits']); p['Vs'].append(c['V_size'])
    if c['mean_usable_shifts'] is not None:
        p['shifts_w'] += c['mean_usable_shifts'] * c['decompositions']; p['shifts_n'] += c['decompositions']
    if c.get('mean_conjugates_in_V') is not None:
        p['conj'].append(c['mean_conjugates_in_V'])
    if 'nb_union_size' in c:
        p['nbU'].append(c['nb_union_size']); p['nbUFB'].append(c['nb_union_FB_points'])
    p['censored'] |= c['censored']

rows = {}
for key, p in pool.items():
    n, m, k, V = key
    FBp = sum(p['FBp']) / p['reps']; FBx = sum(p['FBx']) / p['reps']; orb = sum(p['orb']) / p['reps']
    rpa = p['dec'] / p['targets'] if p['targets'] else None
    rows_pa = p['rows'] / p['targets'] if p['targets'] else None
    lam = p['lam_t'] / p['targets'] if p['targets'] else None
    eff = (rows_pa / lam) if (rows_pa is not None and lam) else None
    eff_dec = (rpa / lam) if (rpa is not None and lam) else None
    # Poisson-count standard error on eff
    eff_se = (math.sqrt(p['rows']) / (lam * p['targets'])) if (lam and p['rows']) else None
    rows[key] = dict(n=n, m=m, k=k, V=V, reps=p['reps'], Vsize=sum(p['Vs']) / p['reps'], FBp=FBp, FBx=FBx, orb=orb,
                     g=(FBx / orb) if orb else None, targets=p['targets'], succ=p['succ'], dec=p['dec'],
                     p=p['succ'] / p['targets'] if p['targets'] else None, rpa=rpa, rows=rows_pa, nrows=p['rows'], lam=lam, eff=eff, eff_dec=eff_dec, eff_se=eff_se,
                     shifts=(p['shifts_w'] / p['shifts_n']) if p['shifts_n'] else None,
                     conj=(sum(p['conj']) / len(p['conj'])) if p['conj'] else None,
                     nbU=(sum(p['nbU']) / len(p['nbU'])) if p['nbU'] else None,
                     nbUFB=(sum(p['nbUFB']) / len(p['nbUFB'])) if p['nbUFB'] else None,
                     censored=p['censored'], a=p['a'], r=p['r'], h=p['h'])

out = []
w = out.append
w('# tau factor-base pilot: aggregate (derived from results/cells.jsonl)\n')
w('Exploratory pilot, NOT program evidence. Every number below is computed by `aggregate.py` from '
  '`results/cells.jsonl` (written by `tau_fb_pilot.py`); nothing is typed in by hand.\n')
w('## Curves\n')
w('| n | a | #E | h | r | r prime | #E by exhaustive point count | field polynomial | primitive element |')
w('|---|---|---|---|---|---|---|---|---|')
for c in curves:
    w(f"| {c['n']} | {c['a']} | {c['order']} | {c['h']} | {c['r']} | {c['r_prime']} | {c['order_by_point_count']} | {c['irreducible']} | {c['primitive_element']} |")
w('\nThe curve used at each n is the a with r prime. Points of the factor base and all targets lie in the order-r subgroup.\n')

w('## Per-cell table (pooled over replicates)\n')
w('Columns: |V| x-values; |FB| subgroup points with x in V; FB_x distinct x in FB (= negation-reduced size); '
  'orbits = number of tau-orbits meeting FB_x (= <tau,-1>-orbit count, the orbit-reduced factor-base size); '
  'g = FB_x/orbits; T targets; p = P(at least one decomposition); d/s = decompositions per success; '
  'dpa = decompositions per attempt; rpa = DISTINCT relations per attempt after projecting each decomposition onto <tau,-1>-orbit representatives '
  '(row = {orbit rep: sum of sign*mu^j} mod r; decompositions of one target that differ by a kernel identity such as tau^2 - t*tau + 2 = 0 collapse to one row); '
  'dup = 1 - rpa/dpa; lambda = C(|FB|,m)/r; eff = rpa/lambda (+- 1 s.e.); shifts = mean number of j in [0,n) such that the conjugate relation tau^j(.) lies entirely inside FB again '
  '(the usable part of the orbit; 1 means only j=0).\n')
w('| n | m | k | V | reps | \\|V\\| | \\|FB\\| | FB_x | orbits | g | T | p | d/s | dpa | rpa | dup | lambda | eff | shifts/n |')
w('|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|')
for key, r in rows.items():
    ds = (r['dec'] / r['succ']) if r['succ'] else None
    effs = f"{fmt(r['eff'],2)}+-{fmt(r['eff_se'],2)}" if r['eff'] is not None else '--'
    w(f"| {r['n']} | {r['m']} | {r['k']} | {r['V']} | {r['reps']} | {r['Vsize']:.0f} | {r['FBp']:.0f} | {r['FBx']:.0f} | {r['orb']:.0f} | {fmt(r['g'],2)} | {r['targets']} | {fmt(r['p'])} | {fmt(ds,2)} | {fmt(r['rpa'])} | {fmt(r['rows'])} | {fmt(1 - r['rows']/r['rpa'] if r['rpa'] else None,2)} | {fmt(r['lam'])} | {effs} | {fmt(r['shifts'],1)}/{r['n']} |"
      + (' CENSORED' if r['censored'] else ''))

w('\n## Gain in the relation-collection phase, per V, relative to V_poly with negation only\n')
w('Accounting (derived, see README): in the orbit-reduced matrix each decomposition is one row and the number of '
  'unknowns is `orbits`; the conjugate rows tau^j(rel) are the same row times mu^j, so they add no rank. '
  'Relations needed = orbits. Attempts needed = orbits/rpa. '
  'Baseline: V_poly, negation only (unknowns = FB_x_poly, rows per attempt = rpa_poly).\n')
w('- `raw` = log2((rpa_V/orbits_V)/(rpa_poly/FB_x_poly)) at the sizes actually realised (|FB| differ slightly between V families at the same k); rpa counts distinct projected rows.')
w('- `struct` = log2(g_V): the orbit-reduction factor alone (pure counting of the factor base).')
w('- `dec` = log2(eff_V/eff_poly): change in decomposition yield at matched |FB| (measured; 0 means tau-friendliness does not change the decomposition probability).')
w('- `matched` = struct + dec: the size-normalised gain. Bound: log2(n) for tau (negation is shared by all three V and is not counted).')
w('- `unreduced check` = log2((rpa_V*2*shifts_V/|FB|_V)/(rpa_poly*2*1/|FB|_poly)): the same quantity computed in the UNreduced matrix (rows = all usable conjugates, unknowns = all points). It must agree with `raw` when the factor base is an orbit union; multiplying rows by conjugates AND dividing unknowns by orbits would double count.\n')
w('| n | m | k | V | raw | struct | dec | matched | log2(n) | unreduced check |')
w('|---|---|---|---|---|---|---|---|---|---|')
gain_summary = collections.defaultdict(list)
for key, r in rows.items():
    n, m, k, V = key
    base = rows.get((n, m, k, 'poly'))
    if base is None or not base['rows'] or not r['rows'] or not r['orb']:
        continue
    raw = lg((r['rows'] / r['orb']) / (base['rows'] / base['FBx']))
    struct = lg(r['g'])
    dec = lg(r['eff'] / base['eff']) if (r['eff'] and base['eff']) else float('nan')
    matched = struct + dec
    unred = lg((r['rows'] * 2 * (r['shifts'] or 0) / r['FBp']) / (base['rows'] * 2 * 1 / base['FBp'])) if r['shifts'] else float('nan')
    w(f"| {n} | {m} | {k} | {V} | {fmt(raw,2)} | {fmt(struct,2)} | {fmt(dec,2)} | {fmt(matched,2)} | {fmt(lg(n),2)} | {fmt(unred,2)} |")
    for thr in (30, 300):
        if r['nrows'] >= thr and base['nrows'] >= thr:
            gain_summary[(thr, V, m)].append((n, k, struct, dec, matched, lg(n)))

for thr in (30, 300):
    w(f'\n### Summary by V family (cells with >= {thr} decompositions in both the cell and its poly baseline)\n')
    w('| V | m | cells | struct bits: mean [min,max] | dec bits: mean [min,max] | matched bits: mean [min,max] | log2(n) range |')
    w('|---|---|---|---|---|---|---|')
    for (t_, V, m), L in sorted(gain_summary.items()):
        if t_ != thr:
            continue
        s = [x[2] for x in L]; d = [x[3] for x in L]; t = [x[4] for x in L]; b = [x[5] for x in L]
        w(f"| {V} | {m} | {len(L)} | {sum(s)/len(s):.2f} [{min(s):.2f},{max(s):.2f}] | {sum(d)/len(d):.2f} [{min(d):.2f},{max(d):.2f}] | {sum(t)/len(t):.2f} [{min(t):.2f},{max(t):.2f}] | [{min(b):.2f},{max(b):.2f}] |")

w('\n## V_nb: what fraction of the tau-orbit is usable\n')
w('Inside V_nb itself a relation can be shifted only while every x_i stays in the window (`shifts` column above). '
  'The union of all n shifted windows U = union_j tau^j(V_nb) is an orbit union, in which every conjugate is usable; its orbit count equals `orbits` of V_nb (same orbits), but its point count is larger, so it is a V_orb of another size, not a free gain.\n')
w('| n | m | k | \\|V_nb\\| | \\|FB_nb\\| | orbits | mean conjugates of an FB x inside V_nb | shifts usable per relation (of n) | \\|U\\| | \\|FB_U\\| | \\|FB_U\\|/orbits |')
w('|---|---|---|---|---|---|---|---|---|---|---|')
for key, r in rows.items():
    if r['V'] != 'nb':
        continue
    w(f"| {r['n']} | {r['m']} | {r['k']} | {r['Vsize']:.0f} | {r['FBp']:.0f} | {r['orb']:.0f} | {fmt(r['conj'],2)} | {fmt(r['shifts'],2)} | {fmt(r['nbU'],0)} | {fmt(r['nbUFB'],0)} | {fmt((r['nbUFB']/r['orb']) if r['orb'] else None,1)} |")

w('\n## V_poly self-overlap under tau\n')
w('| n | m | k | FB_x | orbits | g | mean conjugates of an FB x inside V_poly | shifts usable per relation |')
w('|---|---|---|---|---|---|---|---|')
for key, r in rows.items():
    if r['V'] != 'poly':
        continue
    w(f"| {r['n']} | {r['m']} | {r['k']} | {r['FBx']:.0f} | {r['orb']:.0f} | {fmt(r['g'],3)} | {fmt(r['conj'],3)} | {fmt(r['shifts'],3)} |")

w('\n## Heuristic check (d): V_poly, m = 2\n')
w('lambda_r = C(|FB|,2)/r (targets and factor base in the order-r subgroup); lambda_E = C(|FB|,2)/#E is the formula with #E, off by the cofactor h.\n')
w('| n | k | \\|FB\\| | T | p measured | 1-exp(-lambda_r) | dpa measured | lambda_r | dpa/lambda_r | lambda_E | dpa/lambda_E |')
w('|---|---|---|---|---|---|---|---|---|---|---|')
for key, r in rows.items():
    if r['V'] != 'poly' or r['m'] != 2:
        continue
    lamE = r['lam'] / r['h']
    w(f"| {r['n']} | {r['k']} | {r['FBp']:.0f} | {r['targets']} | {fmt(r['p'])} | {fmt(1-math.exp(-r['lam']))} | {fmt(r['rpa'])} | {fmt(r['lam'])} | {fmt(r['eff_dec'],2)} | {fmt(lamE)} | {fmt(r['rpa']/lamE if lamE else None,2)} |")

# provenance
w('\n## Provenance\n')
for fn in ['tau_fb_pilot.py', 'aggregate.py', 'results/cells.jsonl', 'results/curves.jsonl']:
    pth = os.path.join(HERE, fn)
    if os.path.exists(pth):
        w(f"- `{fn}` sha256 `{hashlib.sha256(open(pth,'rb').read()).hexdigest()}`")
w(f"- cells: {len(cells)} rows; mu per curve: { {c['n']: c.get('mu') for c in cells} }; censored cells: {sum(1 for c in cells if c['censored'])}; total enumeration seconds: {sum(c['seconds'] for c in cells):.0f}")
open(os.path.join(HERE, 'aggregate.md'), 'w').write('\n'.join(out) + '\n')
print('\n'.join(out))

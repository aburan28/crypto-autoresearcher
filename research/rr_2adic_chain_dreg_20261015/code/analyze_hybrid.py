"""Hybrid (guess g unknowns) summary and graph, recorded values only.

Usage: python analyze_hybrid.py OUTDIR HYBRID.jsonl BASELINE_runs.csv
g = 0 rows come from the baseline sweep (circuit, mult arm, seed 1); g = 1, 2 from the hybrid run.
"""
import csv, json, os, sys
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

outdir, hyb, base = sys.argv[1], sys.argv[2], sys.argv[3]
rows = []
for r in csv.DictReader(open(base)):
    if r['enc'] == 'circuit' and r['arm'] == 'mult' and r['seed'] == '1' and r['phase'] in ('1', '2', '3'):
        if r['k'] == '4' and r['phase'] == '1':
            continue  # phase 1 k=4 ran 3 jobs sharing memory; phase 2 repeats it alone
        guess = 'true' if r['inst'] == 'planted' else 'wrong'
        rows.append(dict(source=f"baseline phase {r['phase']}", tag=r['tag'], k=int(r['k']), g=0, inst=r['inst'],
                         guess='none', nvars=int(r['nvars']), stop=r['stop'],
                         f4_max_degree=int(r['f4_max_degree']) if r['f4_max_degree'] else '',
                         lower_bound=r['stop'] != 'complete', wall_s=float(r['wall_s']),
                         maxrss_mb=r['maxrss_mb'], outcome=r['outcome'], n_solutions=r['n_solutions']))
for l in open(hyb):
    r = json.loads(l)
    if str(r.get('status', '')).startswith('skipped'):
        rows.append(dict(source='hybrid', tag=r['tag'], k=r['k'], g=r['g'], inst=r['inst'], guess=r['guess'], nvars='',
                         stop='skipped (smaller k incomplete)', f4_max_degree='', lower_bound='', wall_s='',
                         maxrss_mb='', outcome='', n_solutions=''))
        continue
    st = r['status']
    rows.append(dict(source='hybrid', tag=r['tag'], k=r['k'], g=r['g'], inst=r['inst'], guess=r['guess'], nvars=r['nvars'],
                     stop='complete' if st == 'ok' else ('timeout' if st == 'timeout' else ('killed_oom' if st == 'exit_-9' else st)),
                     f4_max_degree=r.get('dmax') or '', lower_bound=st != 'ok', wall_s=r.get('wall_s'),
                     maxrss_mb=round(r['maxrss_kb'] / 1024, 1) if r.get('maxrss_kb') else '',
                     outcome=r.get('outcome') or '', n_solutions=r.get('n_solutions') if r.get('n_solutions') is not None else ''))
rows.sort(key=lambda r: (r['k'], r['g'], r['inst'], r['guess']))
with open(os.path.join(outdir, 'hybrid_runs.csv'), 'w', newline='') as fh:
    w = csv.DictWriter(fh, fieldnames=list(rows[0])); w.writeheader(); w.writerows(rows)

cols = {0: '#7f7f7f', 1: '#1f77b4', 2: '#d62728'}
mk = {('planted', 'true'): 'o', ('planted', 'none'): 'o', ('planted', 'wrong'): 's', ('random', 'wrong'): 'D', ('random', 'none'): 'D'}
fig, axes = plt.subplots(1, 2, figsize=(11.5, 4.6))
for g in (0, 1, 2):
    for (inst, guess), m in mk.items():
        sel = [r for r in rows if r['g'] == g and r['inst'] == inst and r['guess'] == guess and r['f4_max_degree'] != '']
        off = {0: -0.12, 1: 0.0, 2: 0.12}[g] + {('planted', 'true'): -0.04, ('planted', 'none'): -0.04,
                                               ('planted', 'wrong'): 0.0, ('random', 'wrong'): 0.04, ('random', 'none'): 0.04}[(inst, guess)]
        for r in sel:
            filled = not r['lower_bound']
            kw = dict(c=cols[g]) if filled else dict(facecolors='none', edgecolors=cols[g])
            axes[0].scatter(r['k'] + off, r['f4_max_degree'], marker=m if filled else '^', s=34, **kw)
            if r['wall_s'] != '':
                axes[1].scatter(r['k'] + off, r['wall_s'], marker=m if filled else '^', s=34, **kw)
for g in (0, 1, 2):
    axes[0].scatter([], [], c=cols[g], marker='o', label=f'g = {g} guessed unknowns')
axes[0].scatter([], [], c='k', marker='o', label='planted, correct guess (g=0: no guess)')
axes[0].scatter([], [], c='k', marker='s', label='planted, wrong guess')
axes[0].scatter([], [], c='k', marker='D', label='random T')
axes[0].scatter([], [], facecolors='none', edgecolors='k', marker='^', label='stopped: lower bound')
axes[0].set_xlabel('k'); axes[0].set_ylabel('max F4 step degree (msolve 0.10.1)')
axes[0].set_title('Hybrid: solving degree vs k for g = 0, 1, 2 guessed unknowns\n(circuit encoding, mult arm, p = 268496897, seed 1)', fontsize=8)
axes[0].legend(fontsize=6.5); axes[0].grid(alpha=.3); axes[0].set_ylim(0, 8.5); axes[0].set_xticks([3, 4, 5, 6, 7])
axes[1].set_yscale('log'); axes[1].set_xlabel('k'); axes[1].set_ylabel('msolve wall time per system (s)')
axes[1].set_title('Wall time per specialised system (open triangles: stopped at limit/OOM)', fontsize=8)
axes[1].grid(alpha=.3); axes[1].set_xticks([3, 4, 5, 6, 7])
fig.suptitle(f'Hybrid guessing on the six-point Riemann-Roch / 2-adic chain system ({len(rows)} rows; tags in hybrid_runs.csv)', fontsize=9)
fig.tight_layout()
for ext in ('svg', 'png'):
    fig.savefig(os.path.join(outdir, f'hybrid_dmax_vs_k.{ext}'), dpi=150)
for r in rows:
    print(r['k'], r['g'], r['inst'], r['guess'], r['nvars'], r['stop'], r['f4_max_degree'], r['wall_s'], r['maxrss_mb'], r['outcome'], r['n_solutions'])

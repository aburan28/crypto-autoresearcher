"""Summarize the k-sweep run records and draw the graphs (recorded values only, no new computation).

Usage: python analyze.py OUTDIR PHASE1.jsonl [PHASE2.jsonl ...]
A run counts as complete only when msolve exited 0; for runs stopped by the timeout or killed
(exit -9, out of memory), the highest F4 step degree that started is a lower bound on the solving degree.
"""
import csv, json, sys, os
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

outdir, srcs = sys.argv[1], sys.argv[2:]
recs = []
for i, s in enumerate(srcs, 1):
    for l in open(s):
        r = json.loads(l); r['phase'] = i; recs.append(r)
        # degree of an F4 step whose pairs were selected but whose matrix never completed
        lp = os.path.join(os.path.dirname(s), 'runs', r['tag'] + '.log')
        r['deg_started_unfinished'] = None
        if r.get('status') not in (None, 'ok') and os.path.exists(lp):
            last = [ln for ln in open(lp).read().splitlines() if ln.strip()][-1].split()
            if len(last) == 3 and all(t.isdigit() for t in last):
                r['deg_started_unfinished'] = int(last[0])
with open(os.path.join(outdir, 'results_all.jsonl'), 'w') as fh:
    for r in recs:
        fh.write(json.dumps(r) + '\n')

def stop_kind(r):
    st = r.get('status', '')
    return 'complete' if st == 'ok' else ('timeout' if st == 'timeout' else ('killed_oom' if st == 'exit_-9' else st))

rows = []
for r in recs:
    if str(r.get('status', '')).startswith('skipped'):
        continue
    mm = r.get('max_matrix') or [None, None]
    rows.append(dict(phase=r['phase'], tag=r['tag'], arm=r['arm'], enc=r['enc'], k=r['k'], inst=r['inst'], seed=r['seed'],
                     p=r['p'], nvars=r.get('nvars'), neqs=r.get('neqs'), input_maxdeg=r.get('maxdeg'),
                     fb_x=r.get('fb_size_x'), fb_points=r.get('fb_points'), witness_checked=r.get('witness_checked'),
                     stop=stop_kind(r), f4_max_degree=r.get('dmax'),
                     solving_degree=r.get('dmax') if r.get('status') == 'ok' else '',
                     deg_started_unfinished=r.get('deg_started_unfinished') or '',
                     solving_degree_lower_bound='' if r.get('status') == 'ok' else max(r.get('dmax') or 0, r.get('deg_started_unfinished') or 0),
                     max_matrix_rows=mm[0], max_matrix_cols=mm[1], wall_s=r.get('wall_s'), cpu_s=r.get('cpu_s'),
                     maxrss_mb=round(r['maxrss_kb'] / 1024, 1) if r.get('maxrss_kb') else '',
                     outcome=r.get('outcome') or '', n_solutions=r.get('n_solutions') if r.get('n_solutions') is not None else ''))
with open(os.path.join(outdir, 'runs.csv'), 'w', newline='') as fh:
    w = csv.DictWriter(fh, fieldnames=list(rows[0])); w.writeheader(); w.writerows(rows)

colors = {('mult', 'circuit'): '#1f77b4', ('dickson', 'circuit'): '#2ca02c',
          ('mult', 'direct'): '#d62728', ('dickson', 'direct'): '#ff7f0e'}
fig, axes = plt.subplots(1, 2, figsize=(11.5, 5.6))
ax = axes[0]
for (arm, enc), col in colors.items():
    for inst, dx in [('planted', -0.07), ('random', 0.07)]:
        sel = [r for r in rows if r['arm'] == arm and r['enc'] == enc and r['inst'] == inst]
        jit = (0.025 if arm == 'dickson' else -0.025) + (0.18 if enc == 'direct' else 0)
        done = [r for r in sel if r['stop'] == 'complete']
        lb = [r for r in sel if r['stop'] != 'complete' and r['f4_max_degree']]
        mk = 'o' if inst == 'planted' else 's'
        if done:
            ax.scatter([r['k'] + dx + jit for r in done], [r['solving_degree'] for r in done], c=col, marker=mk, s=30,
                       label=f'{arm}/{enc}/{inst} complete')
        if lb:
            ax.scatter([r['k'] + dx + jit for r in lb], [r['solving_degree_lower_bound'] for r in lb], facecolors='none',
                       edgecolors=col, marker='^', s=46, label=f'{arm}/{enc}/{inst} stopped (lower bound)')
ax.set_xlabel('k  (factor-base chain depth; |S| = 2^k x-values)')
ax.set_ylabel('max F4 step degree (msolve 0.10.1, grevlex)')
ax.set_title('Solving degree vs k. Filled: complete; open triangle: lower bound\n(run stopped by 600/2400 s timeout or out of memory at ~14 GB)', fontsize=8)
ax.legend(fontsize=5.6, ncol=2, loc='upper center', bbox_to_anchor=(0.5, -0.16)); ax.set_ylim(0, 27); ax.grid(alpha=.3); ax.set_xticks(sorted({r['k'] for r in rows}))
ax = axes[1]
# fixed-degree comparison: largest F4 matrix at degree D, circuit encoding, mult arm, planted seed 1
# (k=3 from phase 1, k=4 from phase 2 (single job), k=5..7 from phase 3)
import re
pick = {3: ('data/phase1', 'mult_circuit_k3_planted_s1'), 4: ('data/phase2', 'mult_circuit_k4_planted_s1')}
pick.update({k: ('data/phase3', f'mult_circuit_k{k}_planted_s1') for k in (5, 6, 7)})
fixed = []
for k, (d, tag) in sorted(pick.items()):
    lp = os.path.join(d, 'runs', tag + '.log')
    if not os.path.exists(lp):
        continue
    best = {}
    for ln in open(lp):
        m = re.match(r'\s*(\d+)\s+(\d+)\s+(\d+)\s+(\d+) x (\d+)\s', ln)
        if m:
            D, rr, cc = int(m.group(1)), int(m.group(4)), int(m.group(5))
            if rr * cc > best.get(D, (0, 0))[0] * best.get(D, (0, 0))[1]:
                best[D] = (rr, cc)
    for D, (rr, cc) in best.items():
        fixed.append(dict(k=k, tag=tag, degree=D, rows=rr, cols=cc))
with open(os.path.join(outdir, 'matrix_by_degree.csv'), 'w', newline='') as fh:
    w = csv.DictWriter(fh, fieldnames=['k', 'tag', 'degree', 'rows', 'cols']); w.writeheader(); w.writerows(fixed)
for D, col in zip((3, 4, 5, 6, 7), ('#9ecae1', '#6baed6', '#3182bd', '#08519c', '#08306b')):
    pts = sorted((f['k'], f['cols']) for f in fixed if f['degree'] == D)
    if pts:
        ax.plot([p[0] for p in pts], [p[1] for p in pts], marker='o', color=col, label=f'F4 degree {D}')
ax.set_yscale('log'); ax.set_xlabel('k'); ax.set_ylabel('columns of largest F4 matrix at that degree')
ax.set_title('Circuit encoding, mult arm, planted seed 1: matrix width per F4 degree\n'
             '(n = 11k - 19 variables; last point of each run is where memory ran out)', fontsize=8)
ax.legend(fontsize=7); ax.grid(alpha=.3)
fig.suptitle(f'Six-point Riemann-Roch decomposition with 2-adic chain factor base, p ~ 2^28 '
             f'({len(rows)} msolve runs, phases 1-{len(srcs)}; run tags in runs.csv)', fontsize=9)
fig.tight_layout()
for ext in ('svg', 'png'):
    fig.savefig(os.path.join(outdir, f'dmax_vs_k.{ext}'), dpi=150)
for r in rows:
    print(r['phase'], r['tag'], r['nvars'], r['stop'], r['f4_max_degree'], r['solving_degree_lower_bound'], r['max_matrix_rows'], r['max_matrix_cols'], r['outcome'], r['n_solutions'], r['wall_s'], r['maxrss_mb'])

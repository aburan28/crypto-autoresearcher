"""Summarize results.jsonl and draw the solving-degree and time graphs (recorded values only)."""
import csv, json, sys, os
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

src, outdir = sys.argv[1], sys.argv[2]
recs = [json.loads(l) for l in open(src)]
keys = sorted({(r['arm'], r['enc'], r['inst'], r['k']) for r in recs}, key=lambda t: (t[0], t[1], t[2], t[3]))
rows = []
for arm, enc, inst, k in keys:
    rs = [r for r in recs if (r['arm'], r['enc'], r['inst'], r['k']) == (arm, enc, inst, k)]
    ok = [r for r in rs if r.get('status') == 'ok']
    d = [r['dmax'] for r in ok]
    dto = [r['dmax'] for r in rs if r.get('status') == 'timeout' and r.get('dmax')]
    rows.append(dict(arm=arm, enc=enc, inst=inst, k=k, n=len(rs), ok=len(ok),
                     timeout=sum(r.get('status') == 'timeout' for r in rs),
                     skipped=sum(str(r.get('status', '')).startswith('skipped') for r in rs),
                     nvars=rs[0].get('nvars'), neqs=rs[0].get('neqs'), input_maxdeg=rs[0].get('maxdeg'),
                     dmax_min=min(d) if d else '', dmax_max=max(d) if d else '',
                     dmax_reached_before_timeout=max(dto) if dto else '',
                     wall_s_median=sorted(r['wall_s'] for r in ok)[len(ok) // 2] if ok else '',
                     max_rss_mb_max=round(max(r.get('maxrss_kb', 0) for r in ok) / 1024, 1) if ok else '',
                     outcomes=';'.join(sorted({f"{r['outcome']}:{r['n_solutions']}" for r in ok}))))
with open(os.path.join(outdir, 'summary.csv'), 'w', newline='') as fh:
    w = csv.DictWriter(fh, fieldnames=list(rows[0])); w.writeheader(); w.writerows(rows)

colors = {('mult', 'circuit'): '#1f77b4', ('dickson', 'circuit'): '#2ca02c',
          ('mult', 'direct'): '#d62728', ('dickson', 'direct'): '#ff7f0e'}
fig, axes = plt.subplots(1, 2, figsize=(11, 4.2))
for (arm, enc), col in colors.items():
    for inst, mk, off in [('planted', 'o', -0.08), ('random', 's', 0.08)]:
        pts = [(r['k'] + off + (0.03 if arm == 'dickson' else -0.03), r['dmax'], r['wall_s'])
               for r in recs if r['arm'] == arm and r['enc'] == enc and r['inst'] == inst and r.get('status') == 'ok']
        tpts = [(r['k'] + off, r['dmax']) for r in recs if r['arm'] == arm and r['enc'] == enc and r['inst'] == inst
                and r.get('status') == 'timeout' and r.get('dmax')]
        if pts:
            axes[0].scatter([p[0] for p in pts], [p[1] for p in pts], c=col, marker=mk, s=28,
                            label=f'{arm}/{enc}/{inst}')
            axes[1].scatter([p[0] for p in pts], [p[2] for p in pts], c=col, marker=mk, s=28)
        if tpts:
            axes[0].scatter([p[0] for p in tpts], [p[1] for p in tpts], facecolors='none', edgecolors=col,
                            marker='^', s=40)
axes[0].set_xlabel('k (factor-base chain depth; |S| = 2^k x-values)')
axes[0].set_ylabel('max F4 step degree (msolve, grevlex)')
axes[0].set_title('Solving degree vs k  (open triangles: degree reached before timeout)', fontsize=9)
axes[0].legend(fontsize=6.5, ncol=2)
axes[0].grid(alpha=.3)
axes[1].set_yscale('log'); axes[1].set_xlabel('k'); axes[1].set_ylabel('msolve wall time (s), completed runs')
axes[1].set_title('Wall time vs k (timeout 600 s)', fontsize=9); axes[1].grid(alpha=.3)
n = len(recs)
fig.suptitle(f'Six-point Riemann-Roch decomposition, 2-adic chain factor base; p ~ 2^28; {n} runs, 3 seeds per cell', fontsize=9)
fig.tight_layout()
for ext in ('svg', 'png'):
    fig.savefig(os.path.join(outdir, f'dmax_vs_k.{ext}'), dpi=150)
print(open(os.path.join(outdir, 'summary.csv')).read())

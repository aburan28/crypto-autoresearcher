"""Compare the guessing strategies on the mult arm, seed 1 (recorded values only).

Usage: python analyze_guessing.py OUTDIR
Reads, relative to the study directory:
  runs.csv                          baseline circuit (no guess)                         [g = 0]
  hybrid_runs.csv                   guess coefficients of C (u4, u3)                     [hybrid1]
  data/remainder1/results.jsonl     guess last-remainder coefficients, k = 4             [remainder1]
  data/remainder2/results.jsonl     guess last-remainder coefficients, k = 5, 6           [remainder2]
  data/split1/results.jsonl         one-level sign split, all m, k = 4 (first attempt)    [split1]
  data/splitq/results.jsonl         one- and two-level sign splits, representative guesses [splitq]
Writes guessing_runs.csv and guessing_compare.{svg,png}.
"""
import csv, json, os, sys
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

outdir = sys.argv[1]
rows = []

def stop_of(st):
    if st == 'ok':
        return 'complete'
    if st == 'timeout':
        return 'timeout'
    if st in ('exit_-9', 'exit_-11'):
        return 'memory'  # -9: kernel OOM kill; -11: allocation failure under the 8.6 GB ulimit
    return st

def add(strategy, source, r, guess_label, branch):
    st = r.get('status', '')
    if str(st).startswith('skipped') or st == 'build_failed':
        return
    rows.append(dict(strategy=strategy, source=source, tag=r['tag'], k=int(r['k']), guess=guess_label, branch=branch,
                     nvars=r.get('nvars'), stop=stop_of(st), f4_max_degree=r.get('dmax'),
                     lower_bound=st != 'ok', wall_s=r.get('wall_s'),
                     maxrss_mb=round(r['maxrss_kb'] / 1024, 1) if r.get('maxrss_kb') else '',
                     outcome=r.get('outcome') or '', n_solutions=r.get('n_solutions') if r.get('n_solutions') is not None else ''))

for r in csv.DictReader(open('runs.csv')):
    if r['enc'] == 'circuit' and r['arm'] == 'mult' and r['seed'] == '1' and not (r['k'] == '4' and r['phase'] == '1'):
        st = {'complete': 'ok', 'killed_oom': 'exit_-9', 'timeout': 'timeout'}[r['stop']]
        add('none', f"baseline phase {r['phase']}", dict(tag=r['tag'], k=r['k'], status=st, nvars=int(r['nvars']),
            dmax=int(r['f4_max_degree']) if r['f4_max_degree'] else None, wall_s=float(r['wall_s']),
            maxrss_kb=float(r['maxrss_mb']) * 1024 if r['maxrss_mb'] else None, outcome=r['outcome'],
            n_solutions=int(r['n_solutions']) if r['n_solutions'] else None), 'none',
            'planted/true' if r['inst'] == 'planted' else 'random')
for r in csv.DictReader(open('hybrid_runs.csv')):
    if r['g'] in ('1', '2') and r['stop'] != 'skipped (smaller k incomplete)':
        st = {'complete': 'ok', 'timeout': 'timeout', 'killed_oom': 'exit_-9'}[r['stop']]
        add(f"C coeffs (g={r['g']})", 'hybrid1', dict(tag=r['tag'], k=r['k'], status=st, nvars=int(r['nvars']),
            dmax=int(r['f4_max_degree']) if r['f4_max_degree'] else None, wall_s=float(r['wall_s']),
            maxrss_kb=float(r['maxrss_mb']) * 1024 if r['maxrss_mb'] else None, outcome=r['outcome'],
            n_solutions=int(r['n_solutions']) if r['n_solutions'] else None), f"g={r['g']}",
            f"{r['inst']}/{r['guess']}")
for src in ('remainder1', 'remainder2'):
    p = os.path.join('data', src, 'results.jsonl')
    if os.path.exists(p):
        for line in open(p):
            r = json.loads(line)
            add(f"remainder coeffs (g={r['g']})", src, r, f"r{r['g']}", f"{r['inst']}/{r['guess']}")
p = os.path.join('data', 'split1', 'results.jsonl')
if os.path.exists(p):
    for line in open(p):
        r = json.loads(line)
        add('one-level split', 'split1', r, f"m={r['m']}",
            'planted/true' if r['inst'] == 'planted' and r.get('true_m') == r['m'] else
            ('planted/wrong' if r['inst'] == 'planted' else 'random'))
for line in open(os.path.join('data', 'splitq', 'results.jsonl')):
    r = json.loads(line)
    strat = 'one-level split' if r['enc'] == 'split1' else 'two-level split'
    g = r['guess'] if isinstance(r['guess'], int) else ''.join(map(str, r['guess']))
    branch = 'planted/true' if r['role'] == 'true' else ('planted/wrong' if r['inst'] == 'planted' else 'random')
    add(strat, 'splitq', r, f"m={g}" if strat == 'one-level split' else f"({','.join(g)})", branch)

rows.sort(key=lambda r: (r['k'], r['strategy'], r['branch'], r['guess']))
with open(os.path.join(outdir, 'guessing_runs.csv'), 'w', newline='') as fh:
    w = csv.DictWriter(fh, fieldnames=list(rows[0])); w.writeheader(); w.writerows(rows)

strategies = ['none', 'C coeffs (g=1)', 'C coeffs (g=2)', 'remainder coeffs (g=1)', 'remainder coeffs (g=2)',
              'remainder coeffs (g=6)', 'remainder coeffs (g=12)', 'one-level split', 'two-level split']
colors = ['#7f7f7f', '#9ecae1', '#3182bd', '#fdae6b', '#e6550d', '#a63603', '#7f2704', '#74c476', '#238b45']
markers = {'planted/true': 'o', 'planted/wrong': 's', 'random': 'D'}
fig, axes = plt.subplots(1, 2, figsize=(12, 5.2))
for si, (strat, col) in enumerate(zip(strategies, colors)):
    for r in [r for r in rows if r['strategy'] == strat]:
        x = r['k'] + (si - 4) * 0.075
        filled = not r['lower_bound']
        kw = dict(c=col) if filled else dict(facecolors='none', edgecolors=col)
        mk = markers.get(r['branch'].replace('/none', ''), 'o') if filled else '^'
        if r['f4_max_degree'] is not None:
            axes[0].scatter(x, r['f4_max_degree'], marker=mk, s=30, **kw)
        if r['wall_s'] not in ('', None):
            axes[1].scatter(x, r['wall_s'], marker=mk, s=30, **kw)
    axes[0].scatter([], [], c=col, marker='o', label=strat)
for b, m in markers.items():
    axes[0].scatter([], [], c='k', marker=m, label=b)
axes[0].scatter([], [], facecolors='none', edgecolors='k', marker='^', label='stopped (timeout or memory): lower bound')
axes[0].set_xlabel('k'); axes[0].set_ylabel('max F4 step degree (msolve 0.10.1)'); axes[0].set_xticks([3, 4, 5, 6])
axes[0].set_title('Max F4 degree per specialised system, by guessing strategy\n(mult arm, p = 268496897, seed 1)', fontsize=8)
axes[0].legend(fontsize=5.8, loc='upper left', ncol=2); axes[0].grid(alpha=.3); axes[0].set_ylim(0, 10.5)
axes[1].set_yscale('log'); axes[1].set_xlabel('k'); axes[1].set_ylabel('wall time per system (s)'); axes[1].set_xticks([3, 4, 5, 6])
axes[1].set_title('Wall time per specialised system (open triangles: stopped)', fontsize=8); axes[1].grid(alpha=.3)
fig.suptitle(f'Guessing strategies compared ({len(rows)} msolve runs; tags in guessing_runs.csv)', fontsize=9)
fig.tight_layout()
for ext in ('svg', 'png'):
    fig.savefig(os.path.join(outdir, f'guessing_compare.{ext}'), dpi=150)
for r in rows:
    print(r['k'], r['strategy'], r['guess'], r['branch'], r['nvars'], r['stop'], r['f4_max_degree'], r['wall_s'], r['maxrss_mb'], r['outcome'], r['n_solutions'])

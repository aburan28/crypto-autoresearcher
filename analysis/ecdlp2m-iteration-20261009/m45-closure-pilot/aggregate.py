"""Aggregate results/*.jsonl per (cell, family, closure+degree): UNSAT refuted, SAT falsely refuted,
censored, median wall, column count. Used because summarize.py crashed on the interrupted ladder."""
import json, glob, collections, statistics, os
here = os.path.dirname(os.path.abspath(__file__))
agg = collections.defaultdict(lambda: {'unsat': 0, 'unsat_ref': 0, 'sat': 0, 'sat_ref': 0, 'cens': 0, 'wall': [], 'ncols': set()})
for f in sorted(glob.glob(os.path.join(here, 'results', '*.jsonl'))):
    cell = os.path.basename(f)[:-6]
    for line in open(f):
        r = json.loads(line)
        a = agg[(cell, r['family'], r['kind'] + str(r['D']))]
        if r.get('status') != 'completed':
            a['cens'] += 1
            continue
        if r['nsol'] == 0:
            a['unsat'] += 1; a['unsat_ref'] += bool(r['contains_one'])
        else:
            a['sat'] += 1; a['sat_ref'] += bool(r['contains_one'])
        a['wall'].append(r.get('wall_s') or 0); a['ncols'].add(r.get('ncols'))
print('| cell | family | closure | UNSAT refuted | SAT refuted (must be 0) | censored | median wall s | columns |')
print('|---|---|---|---|---|---|---|---|')
for k in sorted(agg):
    a = agg[k]
    w = round(statistics.median(a['wall']), 1) if a['wall'] else '-'
    cols = ','.join(str(x) for x in sorted(x for x in a['ncols'] if x)) or '-'
    print(f"| {k[0]} | {k[1]} | {k[2]} | {a['unsat_ref']}/{a['unsat']} | {a['sat_ref']}/{a['sat']} | {a['cens']} | {w} | {cols} |")

import json, sys, csv, time, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from brial_degree import step_degree
def masks_to_system(eqs):
    return [[tuple(i for i in range(64) if (m >> i) & 1) for m in eq] for eq in eqs]
systems = json.load(open('brial_systems.json'))
w = csv.writer(open('brial_crosscheck.csv', 'w'))
w.writerow(['cell','id','family','n','N','nsol','brial_unsat','max_step_degree','degrees','gb_size','wall_s'])
for cell, rows in systems.items():
    for i in rows:
        r = step_degree(masks_to_system(i['equations']), i['N'])
        w.writerow([cell, i['id'], i['family'], i['n'], i['N'], i['nsol'], r['unsat'], r['max_step_degree'], ' '.join(map(str, r['degrees'])), r['gb_size'], round(r['wall_s'], 3)])
    print('done', cell, flush=True)

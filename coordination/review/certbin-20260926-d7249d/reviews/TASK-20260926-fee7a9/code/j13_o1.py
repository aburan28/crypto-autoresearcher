"""J13 O1: satisfiable controls. From archived closures.jsonl.gz (engine W_4 final dims,
M_3/M_4/W_4 `one`) and instances.jsonl.gz (s, solutions). Own checks: every listed
solution satisfies its system (own evaluation of the decoded E_hex); the evaluation map
B_{<=4} -> F_2^S on the listed solution set has rank |S| (surjectivity verified directly
per system, not taken from the Reed-Muller bound)."""
import sys, json, gzip, collections
sys.path.insert(0, sys.argv[1])
from rtlib19 import *
run, outp = sys.argv[2], sys.argv[3]
inst = [json.loads(l) for l in gzip.open(run + '/instances.jsonl.gz', 'rt')]
arch = {}
for l in gzip.open(run + '/closures.jsonl.gz', 'rt'):
    r = json.loads(l); arch[r['key']] = r
M4 = Mono(20, 4)
rows = []
for r in inst:
    if r['role'] != 'sat':
        continue
    P = decode_E_hex(r['E_hex'])
    sols = r['solutions']
    ok_sols = all(all(eval_poly(f, u) == 0 for f in P) for u in sols)
    distinct = len(set(sols)) == len(sols)
    # evaluation-map rank on B_{<=4}: rows = solutions, columns = monomials; rank via echelon over solution vectors
    E = Echelon()
    for u in sols:
        x = 0
        for p, m in enumerate(M4.masks):
            if m & u == m:
                x |= 1 << p
        E.add(x)
    rev = E.dim()
    a = arch[r['key']]
    codim = 6196 - a['W_4']['final_dim']
    rows.append({'key': r['key'], 'arm': r['arm'], 's_archived': r['s'], 'n_listed': len(sols), 'listed_solutions_valid': ok_sols,
                 'distinct': distinct, 'eval_rank_B4': rev, 'M3_one': a['M_3']['one'], 'M4_one': a['M_4']['one'], 'W4_one': a['W_4']['one'],
                 'W4_final_dim': a['W_4']['final_dim'], 'codim_W4': codim,
                 'codim_ge_s': codim >= r['s'], 'codim_eq_s': codim == r['s'], 's_le_31': r['s'] <= 31})
summ = collections.OrderedDict()
by = collections.defaultdict(list)
for x in rows:
    by[x['arm']].append(x)
for arm, xs in by.items():
    summ[arm] = {'n': len(xs), 's_distribution': dict(collections.Counter(x['s_archived'] for x in xs)),
                 'listed_valid_all': all(x['listed_solutions_valid'] and x['distinct'] and x['n_listed'] == x['s_archived'] for x in xs),
                 'eval_rank_eq_s_all': all(x['eval_rank_B4'] == x['s_archived'] for x in xs),
                 'any_refutation_M3_M4_W4': sum(x['M3_one'] or x['M4_one'] or x['W4_one'] for x in xs),
                 'codim_ge_s': sum(x['codim_ge_s'] for x in xs),
                 'codim_eq_s_among_s_le_31': [sum(x['codim_eq_s'] for x in xs if x['s_le_31']), sum(x['s_le_31'] for x in xs)],
                 'codim_minus_s_distribution': dict(collections.Counter(x['codim_W4'] - x['s_archived'] for x in xs))}
out = {'summary': summ, 'rows': rows}
json.dump(out, open(outp, 'w'), indent=1)
print(json.dumps(summ, indent=1))

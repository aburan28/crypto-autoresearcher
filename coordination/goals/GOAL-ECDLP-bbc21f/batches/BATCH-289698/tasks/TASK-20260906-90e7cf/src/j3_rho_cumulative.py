"""J3 (iv): rho_T on the CUMULATIVE (batch-average over the first U targets) success, the quantity the
RQ's (P, S, L, epsilon, U) frontier indexes by U, beside the producer's steady-state rho_T."""
import json, sys
import numpy as np
sys.path.insert(0, 'experiments/EXP-ECDLP-612fb1/source')
from analysis import rho_from_eps
BASE = 'experiments/EXP-ECDLP-612fb1/runs'
out = {}
for cell, rr in {'2^24,a=1/4': range(13, 18), '2^30,a=1/4': range(23, 28)}.items():
    raws = [json.load(open(f'{BASE}/RUN-ECDLP-612fb1-{i:03d}/raw-result.json')) for i in rr]
    T = {13: 256, 23: 1024}[rr[0]]
    sol = lambda a: [np.asarray(r['arms'][a]['solved'], float) for r in raws]
    res = {}
    for lab, U in (('4T', 4 * T), ('8T', 8 * T), ('16T', 16 * T)):
        ecum = {k: float(np.concatenate([x[:U] for x in sol(f'RESEL-L({k})')]).mean()) for k in ('T/4', 'T/2', '3T/4', 'T')}
        tcum = float(np.concatenate([x[:U] for x in sol('STATIC(T)')]).mean())
        ess = {k: float(np.concatenate([x[U - 2 * T:U] for x in sol(f'RESEL-L({k})')]).mean()) for k in ('T/4', 'T/2', '3T/4', 'T')}
        tss = float(np.concatenate([x[U - 2 * T:U] for x in sol('STATIC(T)')]).mean())
        rc = rho_from_eps(ecum, tcum, T); rs = rho_from_eps(ess, tss, T)
        # per-seed cumulative rho
        rc_seed = []
        for r in raws:
            e = {k: float(np.mean(r['arms'][f'RESEL-L({k})']['solved'][:U])) for k in ('T/4', 'T/2', '3T/4', 'T')}
            rc_seed.append(rho_from_eps(e, float(np.mean(r['arms']['STATIC(T)']['solved'][:U])), T)[0])
        res[lab] = {'rho_cumulative': rc[0], 'censor': rc[1], 'rho_cumulative_per_seed': rc_seed, 'rho_steady_state_recomputed': rs[0],
                    'eps_cum_resel_by_tsel': ecum, 'eps_cum_static_T': tcum}
        print(f"{cell} U={lab}: rho_T cumulative = {rc[0]:.3f} (per seed {[round(x,3) for x in rc_seed]}) vs steady-state {rs[0]:.3f}; eps_cum RESEL-L by T_sel {dict((k,round(v,4)) for k,v in ecum.items())} vs STATIC(T) {tcum:.4f}")
    out[cell] = res
json.dump(out, open(sys.argv[1] + '/j3_rho_cumulative.json', 'w'), indent=1)

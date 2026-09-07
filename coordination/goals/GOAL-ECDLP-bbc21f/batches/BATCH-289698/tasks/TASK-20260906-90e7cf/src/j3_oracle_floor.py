"""J3: the oracle floor on rho_T. No selection rule can beat ORACLE(T_sel)
(top-T_sel by exact basin size).  rho_oracle(U) = T_sel/T at which
ORACLE(T_sel)'s eps_ss equals STATIC(T)'s, by the same log-linear
interpolation the producer uses for rho_T.  Also: fraction of the
STATIC(T_sel) -> ORACLE(T_sel) gap closed by RESEL-L(T_sel) at 8T and 16T."""
import json, sys
import numpy as np
sys.path.insert(0, 'experiments/EXP-ECDLP-612fb1/source')
from analysis import rho_from_eps
BASE = 'experiments/EXP-ECDLP-612fb1/runs'
CELLS = {'2^20,a=1/4': range(1, 6), '2^24,a=1/4': range(13, 18), '2^20,a=1/2': range(6, 11), '2^24,a=1/2': range(18, 23)}
out = {}
for cell, rr in CELLS.items():
    runs = [(json.load(open(f'{BASE}/RUN-ECDLP-612fb1-{i:03d}/summary.json')), json.load(open(f'{BASE}/RUN-ECDLP-612fb1-{i:03d}/raw-result.json'))) for i in rr]
    T = runs[0][0]['params']['T']
    def eps(arm, lo, hi):
        return float(np.concatenate([np.asarray(raw['arms'][arm]['solved'], float)[lo:hi] for _, raw in runs]).mean())
    def eps_seed(arm, lo, hi):
        return [float(np.asarray(raw['arms'][arm]['solved'], float)[lo:hi].mean()) for _, raw in runs]
    res = {'T': T}
    for lab, U in (('8T', 8 * T), ('16T', 16 * T)):
        lo, hi = U - 2 * T, U
        e_or = {k: eps(f'ORACLE({k})', lo, hi) for k in ('T/4', 'T/2', '3T/4', 'T')}
        e_rl = {k: eps(f'RESEL-L({k})', lo, hi) for k in ('T/4', 'T/2', '3T/4', 'T')}
        e_st = {k: eps(f'STATIC({k})', lo, hi) for k in ('T/4', 'T/2', '3T/4', 'T')}
        tgt = e_st['T']
        rho_or = rho_from_eps(e_or, tgt, T)
        rho_rl = rho_from_eps(e_rl, tgt, T)
        # per-seed rho_oracle
        rho_or_seed = []
        for i in range(len(runs)):
            eo = {k: eps_seed(f'ORACLE({k})', lo, hi)[i] for k in ('T/4', 'T/2', '3T/4', 'T')}
            rho_or_seed.append(rho_from_eps(eo, eps_seed('STATIC(T)', lo, hi)[i], T)[0])
        closed = {k: ((e_rl[k] - e_st[k]) / (e_or[k] - e_st[k]) if e_or[k] > e_st[k] else None) for k in e_or}
        res[lab] = {'eps_ss_STATIC': e_st, 'eps_ss_ORACLE': e_or, 'eps_ss_RESEL_L': e_rl,
                    'rho_oracle_pooled': rho_or[0], 'rho_oracle_censor': rho_or[1], 'rho_oracle_per_seed': rho_or_seed,
                    'rho_T_resel_pooled_recomputed': rho_rl[0], 'rho_T_resel_censor': rho_rl[1],
                    'fraction_of_static_to_oracle_gap_closed_by_RESEL_L': closed,
                    'ORACLE_T2_minus_STATIC_T': e_or['T/2'] - tgt,
                    'ORACLE_T2_minus_STATIC_T_per_seed': [a - b for a, b in zip(eps_seed('ORACLE(T/2)', lo, hi), eps_seed('STATIC(T)', lo, hi))]}
    out[cell] = res
    print(f'\n== {cell} (T={T}) ==')
    for lab in ('8T', '16T'):
        r = res[lab]
        print(f" U={lab}: STATIC eps_ss by T_sel {dict((k, round(v,4)) for k,v in r['eps_ss_STATIC'].items())}")
        print(f"        ORACLE eps_ss by T_sel {dict((k, round(v,4)) for k,v in r['eps_ss_ORACLE'].items())}")
        print(f"        RESEL-L eps_ss by T_sel {dict((k, round(v,4)) for k,v in r['eps_ss_RESEL_L'].items())}")
        print(f"        rho_ORACLE = {r['rho_oracle_pooled']:.3f} {r['rho_oracle_censor'] or ''} per seed {[round(x,3) for x in r['rho_oracle_per_seed']]};  rho_T(RESEL-L) recomputed = {r['rho_T_resel_pooled_recomputed']:.3f}")
        print(f"        ORACLE(T/2) - STATIC(T) = {r['ORACLE_T2_minus_STATIC_T']:+.4f}; per seed {[round(x,4) for x in r['ORACLE_T2_minus_STATIC_T_per_seed']]}")
        print(f"        gap closed by RESEL-L: {dict((k, (round(v,3) if v is not None else None)) for k,v in r['fraction_of_static_to_oracle_gap_closed_by_RESEL_L'].items())}")
json.dump(out, open(sys.argv[1] + '/j3_oracle_floor.json', 'w'), indent=1)

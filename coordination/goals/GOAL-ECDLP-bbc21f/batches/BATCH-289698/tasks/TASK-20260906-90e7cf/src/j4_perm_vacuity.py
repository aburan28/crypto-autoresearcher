"""J4(i) S1 non-vacuity: on the bijection objects, is STATIC(T) within CI of the RHO floor, and is the
'S1' difference RESEL-L(T/2) - STATIC(T) within CI of zero merely because every arm is at the floor?
Stratified-by-seed paired bootstrap (producer's Boot class, my seed) on the red-team run outputs."""
import json, sys
import numpy as np
sys.path.insert(0, 'experiments/EXP-ECDLP-612fb1/source')
from analysis import Boot, pooled_mean
TD = '/home/user/crypto-autoresearcher/coordination/goals/GOAL-ECDLP-bbc21f/batches/BATCH-289698/tasks/TASK-20260906-90e7cf'
boot = Boot(2000, seed=11)
out = {}
for kind in ('permutation', 'affine_xorshift'):
    raws = [json.load(open(f'{TD}/results/j4_perm/{kind}/RUN-RT-90e7cf-{kind}-s{s}/raw-result.json')) for s in (1, 2, 3)]
    T = 64
    arms = ['STATIC(T)', 'STATIC(T/2)', 'RESEL-L(T/2)', 'RESEL-L(T)', 'RHO', 'ORACLE(T)', 'ORACLE(T/2)', 'NULL-A(T/2)', 'STATIC2T']
    sol = {a: [np.asarray(r['arms'][a]['solved'], float) for r in raws] for a in arms}
    def ps(names, lo, hi):
        return [{n: sol[n][i][lo:hi] for n in names} for i in range(3)]
    res = {}
    for lab, (lo, hi) in (('ss_8T', (6 * T, 8 * T)), ('cum_16T', (0, 16 * T))):
        res[lab] = {}
        for a, b in (('STATIC(T)', 'RHO'), ('RESEL-L(T/2)', 'STATIC(T)'), ('RESEL-L(T)', 'STATIC(T)'), ('RESEL-L(T/2)', 'STATIC(T/2)'), ('ORACLE(T)', 'STATIC(T)'), ('STATIC2T', 'STATIC(T)'), ('NULL-A(T/2)', 'STATIC(T/2)')):
            c = boot.ci(ps([a, b], lo, hi), lambda d, a=a, b=b: pooled_mean(d, a) - pooled_mean(d, b))
            res[lab][f'{a} - {b}'] = {'point': c['point'], 'lo': c['lo'], 'hi': c['hi'], 'ci_contains_zero': (c['lo'] is not None and c['lo'] <= 0 <= c['hi'])}
        res[lab]['levels'] = {a: float(np.concatenate([x[lo:hi] for x in sol[a]]).mean()) for a in arms}
    out[kind] = res
    print(f'== {kind} ==')
    for lab in res:
        print(f' {lab}: levels', {a: round(v, 4) for a, v in res[lab]['levels'].items()})
        for k, v in res[lab].items():
            if k != 'levels':
                print(f"   {k:28s} {v['point']:+.4f} [{v['lo']:+.4f}, {v['hi']:+.4f}] contains 0: {v['ci_contains_zero']}")
json.dump(out, open(f'{TD}/results/j4_perm_vacuity.json', 'w'), indent=1)

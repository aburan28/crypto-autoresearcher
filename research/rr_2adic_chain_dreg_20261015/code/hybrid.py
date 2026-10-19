"""Hybrid variant: fix g variables of the circuit system and write the specialised system.

Usage (sage-python): hybrid.py ARM K P INST SEED ENC G GUESS OUT [SET]
  SET = 'u' (default): the unknowns u4 = c1, then u3 = c0 (g <= 2; g = 2 fixes C(x) completely)
        'r'          : coefficients of the remainders of the last squaring steps, highest first:
                       r{L}_5, r{L}_4, ..., r{L}_0, then r{L-1}_5, ... where L is the last step that has
                       remainder variables (R_L = X^(2^(L+1)) mod q); g = 6 fixes R_L, g = 12 fixes R_L and R_(L-1)
  GUESS = 'true'  : planted instance, guessed values are the planted witness (the consistent branch)
          'wrong' : guessed values drawn at random (planted or random T; almost surely inconsistent)
The guessed variables are substituted and removed, so the system has n - g variables.
"""
import json, sys
from sage.all__sagemath_schemes import *
from sage.all__sagemath_singular import *
import build_systems as B

GUESS_ORDER = ['u4', 'u3']  # c1, then c0: g = 2 fixes C(x) completely

def guess_order(varnames, which):
    if which == 'u':
        return GUESS_ORDER
    steps = sorted({int(n[1:].split('_')[0]) for n in varnames if n.startswith('r')}, reverse=True)
    return ['r%d_%d' % (i, j) for i in steps for j in range(5, -1, -1)]

def main():
    arm, k, p, inst, seed, enc, g, guess, out = (sys.argv[1], int(sys.argv[2]), int(sys.argv[3]), sys.argv[4],
                                                int(sys.argv[5]), sys.argv[6], int(sys.argv[7]), sys.argv[8], sys.argv[9])
    which = sys.argv[10] if len(sys.argv) > 10 else 'u'
    d = B.build(arm, k, p, inst, seed, enc)
    F = GF(p)
    R = PolynomialRing(F, d['varnames'], order='degrevlex')
    eqs = [R(e) for e in d['eqs']]
    order = guess_order(d['varnames'], which)
    assert g <= len(order), f'only {len(order)} {which}-variables to guess at k={k}'
    fixed = order[:g]
    truth = {n: d['ustar'][int(n[1:])] for n in GUESS_ORDER} if d['ustar'] is not None else None
    if which == 'r':
        truth = d['witness']
    set_random_seed(seed + 1000 * g + 7)
    vals = {}
    for name in fixed:
        if guess == 'true':
            assert truth is not None, 'true guess needs a planted instance'
            vals[name] = F(truth[name])
        else:
            v = F.random_element()
            if truth is not None:
                while v == F(truth[name]):
                    v = F.random_element()
            vals[name] = v
    keep = [n for n in d['varnames'] if n not in fixed]
    R2 = PolynomialRing(F, keep, order='degrevlex')
    sub = {R(n): vals[n] for n in fixed}
    eqs2 = [R2(str(e.subs(sub))) for e in eqs]
    eqs2 = [e for e in eqs2 if e != 0]
    assert all(e.degree() > 0 for e in eqs2) or guess != 'true', 'true guess produced a nonzero constant'
    with open(out + '.ms', 'w') as fh:
        fh.write(','.join(keep) + '\n' + str(p) + '\n' + ',\n'.join(str(e).replace(' ', '') for e in eqs2) + '\n')
    meta = {x: v for x, v in d.items() if x not in ('eqs', 'witness')}
    meta.update(arm=arm, k=k, inst=inst, seed=seed, enc=enc, g=g, guess=guess, guess_set=which, fixed=fixed,
                fixed_values=[int(vals[n]) for n in fixed], varnames=keep, nvars=len(keep), neqs=len(eqs2))
    json.dump(meta, open(out + '.json', 'w'), default=int)
    print(json.dumps({x: meta[x] for x in ['arm', 'k', 'enc', 'inst', 'g', 'guess', 'nvars', 'neqs']}))

if __name__ == '__main__':
    main()

"""Hybrid variant: fix g of the five unknowns u (u4 = c1, then u3 = c0) and write the specialised system.

Usage (sage-python): hybrid.py ARM K P INST SEED ENC G GUESS OUT
  GUESS = 'true'  : planted instance, guessed values are the planted witness (the consistent branch)
          'wrong' : guessed values drawn at random (planted or random T; almost surely inconsistent)
The guessed variables are substituted and removed, so the system has n - g variables.
"""
import json, sys
from sage.all__sagemath_schemes import *
from sage.all__sagemath_singular import *
import build_systems as B

GUESS_ORDER = ['u4', 'u3']  # c1, then c0: g = 2 fixes C(x) completely

def main():
    arm, k, p, inst, seed, enc, g, guess, out = (sys.argv[1], int(sys.argv[2]), int(sys.argv[3]), sys.argv[4],
                                                int(sys.argv[5]), sys.argv[6], int(sys.argv[7]), sys.argv[8], sys.argv[9])
    d = B.build(arm, k, p, inst, seed, enc)
    F = GF(p)
    R = PolynomialRing(F, d['varnames'], order='degrevlex')
    eqs = [R(e) for e in d['eqs']]
    fixed = GUESS_ORDER[:g]
    set_random_seed(seed + 1000 * g + 7)
    vals = {}
    for name in fixed:
        idx = int(name[1:])
        if guess == 'true':
            assert d['ustar'] is not None, 'true guess needs a planted instance'
            vals[name] = F(d['ustar'][idx])
        else:
            v = F.random_element()
            if d['ustar'] is not None:
                while v == F(d['ustar'][idx]):
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
    meta = {x: v for x, v in d.items() if x != 'eqs'}
    meta.update(arm=arm, k=k, inst=inst, seed=seed, enc=enc, g=g, guess=guess, fixed=fixed,
                fixed_values=[int(vals[n]) for n in fixed], varnames=keep, nvars=len(keep), neqs=len(eqs2))
    json.dump(meta, open(out + '.json', 'w'), default=int)
    print(json.dumps({x: meta[x] for x in ['arm', 'k', 'enc', 'inst', 'g', 'guess', 'nvars', 'neqs']}))

if __name__ == '__main__':
    main()

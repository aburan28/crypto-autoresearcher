"""F-1b (re-scoped): the admissible-shape test over ENUMERATED special families.

    python3 experiments/EXP-FALSIFY-d770c1/falsify/run_families.py

F-1b was originally motivated by a quantifier gap in KN-FIND-a1f3c2's proof
sketch. CORR-20260808-3d4031 voided that motivation: CORR-20260807-652652
supplied the missing step and KN-FIND-a8990a Theorem A now derives the group in
every characteristic. F-1b is re-scoped here to what is actually uncovered.

It is MOSTLY COVERED ALREADY, which was checked before writing this rather than
assumed. KN-FIND-a8990a's run RUN-SMON-e5cbe6-001 enumerates 20 curves labelled:
12 generic-j, 1 "j=0, p=1 mod 3", 1 "j=0, p=2 mod 3", 1 "j=1728, p=1 mod 4",
1 "j=1728, p=3 mod 4 (supersingular)", and 4 "full rational 2-torsion". That is a
deliberate family design, not a uniform sample.

What remains genuinely untested:

  - ANOMALOUS curves, #E(F_p) = p. Absent from a8990a's labels. These are the
    curves where the Smart/Satoh-Araki/Semaev attack breaks ECDLP entirely, so
    if any family carries an exceptional monodromy locus this is a candidate.
  - An INDEPENDENT implementation on the families a8990a did cover. Agreement
    between two codebases is worth more than more samples from one, especially
    while AGENTS.md rule 12 is unmet for a8990a.

Same admissible-shape test as F-1 and the same null object: for a regular cover
with group C_2^(m-2), every unramified specialisation factors into equal-degree
factors of degree 1 or 2, so [1,3], [3,5], [8] or [1,1,2] refutes it.
"""

import json
import os
import subprocess
import sys
from collections import Counter
from datetime import datetime, timezone

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from falsify import ec, fp, probes                                  # noqa: E402

SEED = 20260808


def curve_order(a, b, p):
    return len(ec.affine_points(a, b, p)) + 1


def classify(a, b, p):
    """Every family label this curve belongs to."""
    labs = []
    if a % p == 0:
        labs.append('j=0')
    if b % p == 0:
        labs.append('j=1728')
    # full rational 2-torsion: x^3+ax+b splits completely over F_p
    roots = [x for x in range(p) if (x * x * x + a * x + b) % p == 0]
    if len(roots) == 3:
        labs.append('full-2-torsion')
    n = curve_order(a, b, p)
    if n == p:
        labs.append('ANOMALOUS')
    if n == p + 1:
        labs.append('supersingular')
    if not labs:
        labs.append('generic-j')
    return labs


def enumerate_families(primes):
    """Exhaustively scan (a,b) at each prime and bucket curves by family."""
    fams = {}
    for p in primes:
        for a in range(p):
            for b in range(p):
                if not ec.nonsingular(a, b, p):
                    continue
                for lab in classify(a, b, p):
                    fams.setdefault(lab, []).append((p, a, b))
    return fams


def shapes_for(m, p, a, b, rng_vals):
    """Admissible-shape test on one curve over supplied parameter tuples."""
    adm = probes.admissible_shapes(m)
    target = 2 ** (m - 2)
    used, viol, shapes = 0, 0, Counter()
    wit = None
    for others in rng_vals:
        f = ec.summation_fibre(m, list(others), a, b, p)
        if f is None or fp.deg(f) != target or not fp.is_squarefree(f, p):
            continue
        s = tuple(fp.factor_pattern(f, p))
        shapes[s] += 1
        used += 1
        if s not in adm:
            viol += 1
            wit = wit or {'p': p, 'a': a, 'b': b, 'others': list(others),
                          'shape': list(s)}
    return used, viol, shapes, wit


def main():
    import random
    rng = random.Random(SEED)
    primes = [11, 13, 17, 19, 23, 29, 31, 37, 41, 43, 47]
    print('F-1b  admissible-shape test over ENUMERATED special families')
    print('      (a8990a already covers j=0, j=1728, full-2-torsion; ANOMALOUS is new)\n')
    fams = enumerate_families(primes)
    print('  family sizes found by exhaustive (a,b) scan:')
    for lab in sorted(fams):
        print(f"    {lab:<18} {len(fams[lab]):>6} curves")

    order = ['ANOMALOUS', 'supersingular', 'j=0', 'j=1728', 'full-2-torsion',
             'generic-j']
    results, total_viol = {}, 0
    print(f"\n  {'family':<18}{'m':>3}{'curves':>8}{'usable':>8}{'viol':>6}  shapes")
    for lab in order:
        if lab not in fams:
            continue
        for m in (4, 5):
            sel = fams[lab]
            rng.shuffle(sel)
            sel = sel[:14 if lab in ('ANOMALOUS', 'supersingular') else 8]
            u = v = 0
            agg = Counter()
            wit = None
            for (p, a, b) in sel:
                vals = [tuple(rng.randrange(p) for _ in range(m - 1))
                        for _ in range(18)]
                uu, vv, ss, w = shapes_for(m, p, a, b, vals)
                u += uu
                v += vv
                agg += ss
                wit = wit or w
            total_viol += v
            results[f'{lab}|m={m}'] = {'curves': len(sel), 'usable': u,
                                       'violations': v, 'witness': wit,
                                       'shapes': {str(list(k)): n
                                                  for k, n in agg.items()}}
            top = ', '.join(f'{list(k)}:{n}' for k, n in agg.most_common(3))
            print(f"  {lab:<18}{m:>3}{len(sel):>8}{u:>8}{v:>6}  {top}")

    print(f"\n  TOTAL VIOLATIONS ACROSS ALL FAMILIES: {total_viol}")
    print('  (null object and positive control for this test are exercised by'
          '\n   RUN-FALSIFY-d770c1-001; the instrument is unchanged.)')

    out = {'experiment_id': 'EXP-FALSIFY-d770c1',
           'run_id': 'RUN-FALSIFY-d770c1-006',
           'probe': 'monodromy_special_families_f1b',
           'seed': SEED, 'primes': primes,
           'a8990a_families_already_covered':
               ['j=0 (p=1 mod 3)', 'j=0 (p=2 mod 3)', 'j=1728 (p=1 mod 4)',
                'j=1728 (p=3 mod 4, supersingular)', 'full rational 2-torsion',
                'generic-j'],
           'new_family_here': 'ANOMALOUS (#E = p)',
           'family_sizes': {k: len(v) for k, v in fams.items()},
           'results': results, 'total_violations': total_viol,
           'timestamp_utc': datetime.now(timezone.utc).isoformat(),
           'git_commit': subprocess.run(['git', 'rev-parse', 'HEAD'],
                                        capture_output=True, text=True).stdout.strip()}
    dest = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
                        'runs', 'RUN-FALSIFY-d770c1-006', 'raw-result.json')
    os.makedirs(os.path.dirname(dest), exist_ok=True)
    json.dump(out, open(dest, 'w'), indent=2, sort_keys=True)
    print(f'\nresults written to {dest}')


if __name__ == '__main__':
    main()

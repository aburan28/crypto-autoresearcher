"""Driver for EXP-FALSIFY-d770c1.  Emits results.json; prints a readable report.

    python3 -m experiments.EXP-FALSIFY-d770c1.falsify.run_all      # not importable, see below
    python3 experiments/EXP-FALSIFY-d770c1/falsify/run_all.py [--quick]

The directory name contains a hyphen, so this is run as a script and fixes up
sys.path itself rather than being imported as a package path.
"""

import argparse
import json
import os
import platform
import subprocess
import sys
from datetime import datetime, timezone

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from falsify import probes  # noqa: E402

SEED = 20260808
PRIMES = [11, 13, 17, 19, 23, 29, 31, 37, 41, 43, 47, 53, 59, 61, 67, 71, 73,
          79, 83, 89, 97, 101, 103]


def git_state():
    def sh(*c):
        try:
            return subprocess.run(c, capture_output=True, text=True,
                                  timeout=20).stdout.strip()
        except Exception:
            return None
    return {
        'commit': sh('git', 'rev-parse', 'HEAD'),
        'dirty': bool(sh('git', 'status', '--porcelain')),
        'branch': sh('git', 'rev-parse', '--abbrev-ref', 'HEAD'),
    }


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--quick', action='store_true',
                    help='smaller sweeps; still runs every control')
    ap.add_argument('--out', default=None)
    args = ap.parse_args()

    trials4 = 25 if args.quick else 60
    trials5 = 12 if args.quick else 45
    primes = PRIMES[:10] if args.quick else PRIMES
    iid_trials = 60000 if args.quick else 400000
    null_trials = 40000 if args.quick else 120000

    out = {
        'experiment_id': 'EXP-FALSIFY-d770c1',
        'run_id': 'RUN-FALSIFY-d770c1-001',
        'started_utc': datetime.now(timezone.utc).isoformat(),
        'seed': SEED,
        'quick': args.quick,
        'environment': {
            'python': sys.version.split()[0],
            'platform': platform.platform(),
            'cas_available': False,
            'cas_note': 'no sympy/numpy/sage/pari/flint in this harness; all '
                        'arithmetic is standard library',
        },
        'git': git_state(),
        'probes': {},
    }

    # ------------------------------------------------------------ PROBE 1
    print('=' * 74)
    print('PROBE 1  KN-FIND-a1f3c2 : Semaev monodromy = C_2^(m-2) for EVERY curve')
    print('=' * 74)
    mono = {}
    for m in (4, 5):
        r = probes.probe_monodromy(m, primes, trials4 if m == 4 else trials5,
                                   SEED + m)
        mono[f'm{m}'] = r
        c = r['controls']
        print(f"\n  m = {m}   admissible shapes: "
              f"{sorted(str(list(s)) for s in probes.admissible_shapes(m))}")
        print(f"    control  null object (Galois group of exponent 2): "
              f"{c['null_object_violations']}/{c['null_object_tested']} false violations")
        print(f"    control  positive (summation vanishes on real relations): "
              f"{c['positive_control_vanish']} ok / {c['positive_control_fail']} fail")
        if not c['controls_passed']:
            print('    CONTROLS FAILED -- measurement is NOT reportable')
            continue
        print(f"    measurement  {r['specialisations_used']} specialisations "
              f"({r['specialisations_skipped']} skipped as degenerate)")
        for s, n in list(r['shapes'].items())[:6]:
            print(f"        {s:<26} {n:>5}")
        print(f"    VIOLATIONS: {r['violations']}/{r['specialisations_used']}"
              f"   -> {r['verdict'].upper()}")
    out['probes']['monodromy'] = mono

    # ------------------------------------------------------------ PROBE 2
    print()
    print('=' * 74)
    print('PROBE 2  KN-FIND-c7d31e : BKK Speedup Theorem verification table')
    print('=' * 74)
    bkk = {'iid_model': {}, 'null_multiplicity': {}, 'curve': []}

    print('\n  2a  the theorem\'s own model (i.i.d. uniform, one decomposition)')
    print(f"      {'m':>2} {'theory':>10} {'simulated':>11} {'abs err':>10}")
    for m in (2, 3, 4, 5):
        sim = probes.probe_bkk_iid(m, 64, iid_trials, SEED + 100 + m)
        th = probes.gamma_theory(m)
        bkk['iid_model'][m] = {'theory': th, 'simulated': sim, 'abs_error': abs(th - sim)}
        print(f"      {m:>2} {th:>10.4f} {sim:>11.4f} {abs(th - sim):>10.4f}")

    print('\n  2b  NULL OBJECT: k decompositions per target, NO elliptic curve')
    print('      does pure multiplicity reproduce the reported "EC group law bonus"?')
    ks = [1, 2, 3, 4]
    print(f"      {'m':>2} {'theory':>8} {'reported':>9} | "
          + ' '.join(f'k={k:<6}' for k in ks))
    for m in (2, 3, 4, 5):
        row = {}
        cells = []
        for k in ks:
            v = probes.probe_bkk_null_multiplicity(m, 64, k, null_trials,
                                                   SEED + 200 + 10 * m + k)
            row[k] = v
            cells.append(f'{v:<8.3f}')
        bkk['null_multiplicity'][m] = row
        print(f"      {m:>2} {probes.gamma_theory(m):>8.3f} "
              f"{probes.REPORTED_TABLE[m]:>9.3f} | " + ' '.join(cells))

    print('\n  2c  real curve at p=1009, the two estimands separated')
    print(f"      {'m':>2} {'B':>4} {'theory':>8} {'per-decomp':>11} {'err':>8} "
          f"{'per-target':>11} {'mean mult':>10}")
    plan = [(3, B) for B in ([10, 16, 24, 32, 40] if not args.quick else [10, 24, 40])] + \
           [(4, B) for B in ([8, 12, 16, 20] if not args.quick else [8, 16])]
    for m, B in plan:
        r = probes.probe_bkk_curve(m, 1, 1, 1009, B)
        bkk['curve'].append(r)
        print(f"      {m:>2} {B:>4} {r['theory']:>8.4f} {r['per_decomposition']:>11.4f} "
              f"{r['per_decomposition_error']:>8.4f} {r['per_target']:>11.4f} "
              f"{r['mean_multiplicity']:>10.3f}")
    out['probes']['bkk'] = bkk

    out['finished_utc'] = datetime.now(timezone.utc).isoformat()

    dest = args.out or os.path.join(
        os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
        'runs', 'RUN-FALSIFY-d770c1-001', 'raw-result.json')
    os.makedirs(os.path.dirname(dest), exist_ok=True)
    with open(dest, 'w') as fh:
        json.dump(out, fh, indent=2, sort_keys=True)
    print(f'\nresults written to {dest}')


if __name__ == '__main__':
    main()

"""F-4 driver: is KN-FIND-2a8b7e's growing-with-m BKK speedup an m-effect or a
B-effect, and can it coexist with KN-FIND-c7d31e's theorem?

    python3 experiments/EXP-FALSIFY-d770c1/falsify/run_bkk_scaling.py

KN-FIND-2a8b7e reports, at p=1009 and "near-optimal B":

    m |  B | gamma_m | speedup
    2 | 54 |  0.86   | 1.72x
    3 | 18 |  0.66   | 2.62x
    4 | 12 |  0.35   | 2.82x
    5 | 10 |  0.27   | 4.24x

fits  gamma_m ~ 0.86 * 0.68^(m-2),  concludes  speedup ~ 1.72 * 1.36^(m-2)
"geometrically growing", and extrapolates m=6 -> 5.9x, m=7 -> 8.0x, m=8 -> 10.9x.

Two things are wrong with that, and this run separates them.

(1) CONFOUND.  B is not held fixed: it falls 54 -> 18 -> 12 -> 10 as m rises.
    Per-target success depends strongly on B (RUN-FALSIFY-d770c1-001 drove it
    from 0.61 to 1.000 at fixed m=3 by raising B alone).  So a decay fitted
    across those four rows attributes to m an effect that B is producing.
    Control: hold B fixed and re-measure the same decay.

(2) INCOMPATIBILITY.  KN-FIND-c7d31e proves speedup = (m+1)/2, which is LINEAR
    in m, and the corpus states that theorem "provides the combinatorial
    foundation for the empirical improvements in KN-FIND-2a8b7e".  A geometric
    law and a linear law cannot both describe the same quantity; they diverge
    without bound.
"""

import json
import os
import subprocess
import sys
from datetime import datetime, timezone

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from falsify import probes                                          # noqa: E402

P, A, B_CURVE = 1009, 1, 1
REPORTED = {2: (54, 0.86, 1.72), 3: (18, 0.66, 2.62),
            4: (12, 0.35, 2.82), 5: (10, 0.27, 4.24)}
FIXED_B = [12, 18, 24]


def geometric_model(m):
    """KN-FIND-2a8b7e's fitted law."""
    return 1.72 * 1.36 ** (m - 2)


def theorem_model(m):
    """KN-FIND-c7d31e's proved per-decomposition speedup."""
    return (m + 1) / 2


def main():
    out = {'experiment_id': 'EXP-FALSIFY-d770c1',
           'run_id': 'RUN-FALSIFY-d770c1-003',
           'probe': 'bkk_speedup_scaling_f4',
           'curve': {'p': P, 'a': A, 'b': B_CURVE},
           'reported_table': {str(k): {'B': v[0], 'gamma': v[1], 'speedup': v[2]}
                              for k, v in REPORTED.items()}}

    # ---------------------------------------------------------------- F-4a
    print('F-4a  reproduce the reported table at ITS OWN (m, B) pairs')
    print('      note B varies with m: 54, 18, 12, 10\n')
    print(f"      {'m':>2}{'B':>5}{'reported':>10}{'per-decomp':>12}{'theory':>9}"
          f"{'err':>8}{'per-target':>12}{'mult':>8}")
    a_rows = []
    for m, (B, g, _sp) in REPORTED.items():
        r = probes.probe_bkk_curve(m, A, B_CURVE, P, B)
        a_rows.append({'m': m, 'B': B, 'reported_gamma': g,
                       'per_decomposition': r['per_decomposition'],
                       'theory': r['theory'],
                       'per_decomposition_error': r['per_decomposition_error'],
                       'per_target': r['per_target'],
                       'mean_multiplicity': r['mean_multiplicity']})
        print(f"      {m:>2}{B:>5}{g:>10.3f}{r['per_decomposition']:>12.4f}"
              f"{r['theory']:>9.4f}{r['per_decomposition_error']:>8.4f}"
              f"{r['per_target']:>12.4f}{r['mean_multiplicity']:>8.2f}")
    out['f4a_reported_parameters'] = a_rows

    # ---------------------------------------------------------------- F-4b
    print('\nF-4b  CONTROL: hold B fixed, re-measure the decay')
    print('      claimed per-step ratio: 0.68 (geometric decay in m)\n')
    b_blocks = {}
    for B in FIXED_B:
        print(f"      --- B = {B} fixed ---")
        print(f"      {'m':>2}{'per-decomp':>12}{'theory':>9}{'per-target':>12}"
              f"{'mult':>9}{'ratio/prev':>12}")
        rows, prev = [], None
        for m in (2, 3, 4, 5):
            r = probes.probe_bkk_curve(m, A, B_CURVE, P, B)
            pt = r['per_target']
            ratio = (pt / prev) if prev else None
            prev = pt
            rows.append({'m': m, 'per_decomposition': r['per_decomposition'],
                         'theory': r['theory'], 'per_target': pt,
                         'mean_multiplicity': r['mean_multiplicity'],
                         'ratio_vs_previous_m': ratio})
            rs = f"{ratio:>12.3f}" if ratio else f"{'-':>12}"
            print(f"      {m:>2}{r['per_decomposition']:>12.4f}{r['theory']:>9.4f}"
                  f"{pt:>12.4f}{r['mean_multiplicity']:>9.2f}{rs}")
        b_blocks[str(B)] = rows
        print()
    out['f4b_fixed_B'] = b_blocks

    # ---------------------------------------------------------------- F-4c
    print('F-4c  the two corpus models are incompatible and diverge')
    print(f"      {'m':>2}{'2a8b7e geometric':>20}{'c7d31e theorem':>17}{'ratio':>9}")
    c_rows = []
    for m in (4, 5, 6, 7, 8):
        g, t = geometric_model(m), theorem_model(m)
        c_rows.append({'m': m, 'geometric_2a8b7e': g, 'theorem_c7d31e': t,
                       'ratio': g / t})
        print(f"      {m:>2}{g:>20.2f}{t:>17.2f}{g/t:>9.2f}")
    out['f4c_model_divergence'] = c_rows
    print('\n      KN-FIND-c7d31e states it "provides the combinatorial foundation')
    print('      for the empirical improvements in KN-FIND-2a8b7e". A geometric law')
    print('      and a linear law cannot both describe one quantity.')

    out['timestamp_utc'] = datetime.now(timezone.utc).isoformat()
    out['git_commit'] = subprocess.run(['git', 'rev-parse', 'HEAD'],
                                       capture_output=True, text=True).stdout.strip()
    dest = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
                        'runs', 'RUN-FALSIFY-d770c1-003', 'raw-result.json')
    os.makedirs(os.path.dirname(dest), exist_ok=True)
    with open(dest, 'w') as fh:
        json.dump(out, fh, indent=2, sort_keys=True)
    print(f'\nresults written to {dest}')


if __name__ == '__main__':
    main()

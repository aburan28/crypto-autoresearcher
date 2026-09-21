"""Probe 3 driver: is the H-PSEUDO constant C(p) a power law, or a fit artifact?

    python3 experiments/EXP-FALSIFY-d770c1/falsify/run_pseudo.py [--trials N]
"""

import argparse
import json
import math
import os
import random
import statistics
import subprocess
import sys
from datetime import datetime, timezone

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from falsify import ec                                             # noqa: E402
from falsify.probe_pseudo import (cyclic_generator, dlog_table,     # noqa: E402
                                  max_character_sum)

SEED = 20260808
PRIMES = [1009, 2003, 4001, 9001]
B_FRAC = 0.05
CORPUS = {'KN-FIND-d4f820': 0.055, 'KN-FIND-e7a3b1': 0.079,
          'KN-FIND-4c9e71': 'O(1) ~ 4'}


def slope(ps, vals):
    xs = [math.log(p) for p in ps]
    ys = [math.log(v) for v in vals]
    n = len(xs)
    mx, my = sum(xs) / n, sum(ys) / n
    return (sum((x - mx) * (y - my) for x, y in zip(xs, ys))
            / sum((x - mx) ** 2 for x in xs))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--trials', type=int, default=5,
                    help='independent curves per prime')
    args = ap.parse_args()

    per_prime = {}
    print('Probe 3: H-PSEUDO character-sum constant C(p)')
    print(f'  C = max_{{k!=0}} |sum_{{P in F}} e^(2 pi i k DL(P)/N)| / sqrt(B),'
          f' B_frac={B_FRAC}, {args.trials} curves per prime\n')
    print(f"  {'p':>6} {'C_factorbase':>26} {'C_random_null':>22}")
    print(f"  {'':>6} {'mean':>8}{'sd':>9}{'range':>18}{'mean':>10}{'sd':>9}")
    for p in PRIMES:
        rng = random.Random(SEED + p)
        cs, ns = [], []
        guard = 0
        while len(cs) < args.trials and guard < 4000:
            guard += 1
            a, b = rng.randrange(p), rng.randrange(p)
            if not ec.nonsingular(a, b, p):
                continue
            g = cyclic_generator(a, b, p, rng)
            if not g:
                continue
            G, N, pts = g
            tab = dlog_table(G, a, p, N)
            B = max(8, int(round(B_FRAC * N)))
            fb = sorted(pts, key=lambda P: (P[0], P[1]))[:B]
            d = [tab[P] for P in fb if P in tab]
            rb = math.sqrt(len(d))
            cs.append(max_character_sum(d, N) / rb)
            ns.append(max_character_sum(rng.sample(range(N), len(d)), N) / rb)
        per_prime[p] = {'C_factorbase': cs, 'C_random_null': ns}
        print(f"  {p:>6} {statistics.mean(cs):>8.3f}{statistics.stdev(cs):>9.3f}"
              f"  [{min(cs):>6.3f},{max(cs):>6.3f}]"
              f"{statistics.mean(ns):>10.3f}{statistics.stdev(ns):>9.3f}")

    means = [statistics.mean(per_prime[p]['C_factorbase']) for p in PRIMES]
    nulls = [statistics.mean(per_prime[p]['C_random_null']) for p in PRIMES]
    sds = [statistics.stdev(per_prime[p]['C_factorbase']) for p in PRIMES]
    worst = max((max(per_prime[p]['C_factorbase'])
                 / min(per_prime[p]['C_factorbase']), p) for p in PRIMES)

    exp_fb, exp_null = slope(PRIMES, means), slope(PRIMES, nulls)
    across = max(means) / min(means)

    print(f"\n  p range tested                 : {max(PRIMES)/min(PRIMES):.2f}x"
          f"  (under one decade)")
    print(f"  across-p variation of the mean : {across:.3f}x")
    print(f"  worst within-p spread          : {worst[0]:.3f}x  at p={worst[1]}")
    print(f"  mean within-p sd               : {statistics.mean(sds):.3f}"
          f"  ({100*statistics.mean(sds)/statistics.mean(means):.1f}% of mean)")
    print(f"\n  fitted exponent, factor base   : p^{exp_fb:.4f}")
    print(f"  fitted exponent, RANDOM null   : p^{exp_null:.4f}   <-- no arithmetic structure")
    print(f"  corpus records                 : d4f820 p^0.055 | e7a3b1 p^0.079 | 4c9e71 O(1)~4")
    print(f"\n  p^0.055 predicts {max(PRIMES)/min(PRIMES):.2f}x -> "
          f"{ (max(PRIMES)/min(PRIMES))**0.055:.3f}x variation")
    print(f"  p^0.079 predicts -> { (max(PRIMES)/min(PRIMES))**0.079:.3f}x variation")
    print(f"  observed structural offset C_factorbase / C_null : "
          f"{statistics.mean(means)/statistics.mean(nulls):.3f}x")

    out = {
        'experiment_id': 'EXP-FALSIFY-d770c1',
        'run_id': 'RUN-FALSIFY-d770c1-002',
        'probe': 'h_pseudo_character_sum_constant',
        'seed': SEED, 'b_frac': B_FRAC, 'trials_per_prime': args.trials,
        'primes': PRIMES,
        'per_prime': {str(k): v for k, v in per_prime.items()},
        'summary': {
            'means': dict(zip(map(str, PRIMES), means)),
            'null_means': dict(zip(map(str, PRIMES), nulls)),
            'within_prime_sd': dict(zip(map(str, PRIMES), sds)),
            'across_p_variation_ratio': across,
            'worst_within_p_spread_ratio': worst[0],
            'worst_within_p_spread_prime': worst[1],
            'fitted_exponent_factorbase': exp_fb,
            'fitted_exponent_random_null': exp_null,
            'corpus_claims': CORPUS,
            'structural_offset_factorbase_over_null':
                statistics.mean(means) / statistics.mean(nulls),
        },
        'timestamp_utc': datetime.now(timezone.utc).isoformat(),
        'git_commit': subprocess.run(['git', 'rev-parse', 'HEAD'],
                                     capture_output=True, text=True).stdout.strip(),
    }
    dest = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
                        'runs', 'RUN-FALSIFY-d770c1-002', 'raw-result.json')
    os.makedirs(os.path.dirname(dest), exist_ok=True)
    with open(dest, 'w') as fh:
        json.dump(out, fh, indent=2, sort_keys=True)
    print(f'\nresults written to {dest}')


if __name__ == '__main__':
    main()

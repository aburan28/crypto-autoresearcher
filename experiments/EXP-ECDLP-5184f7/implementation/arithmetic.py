#!/usr/bin/env python3
"""One isolated worker per modulus; five fixed batches, no curve attack claims."""
import argparse
import json
import os
import platform
import random
import resource
import statistics
import subprocess
import sys
import time
from pathlib import Path

from common import Stream, generator, limits, sha, write
from finite_math import Curve


class FoldCurve(Curve):
    def __init__(self, p, a, b):
        super().__init__(p, a, b)
        self.bits = p.bit_length()
        self.mask = (1 << self.bits) - 1
        self.replacement = (1 << self.bits) - p

    def reduce(self, value):
        if value < 0:
            return -self.reduce(-value) % self.p
        while value >> self.bits:
            value = (value & self.mask) + (value >> self.bits) * self.replacement
        return value - self.p if value >= self.p else value

    def mult_field(self, a, b):
        self.count['field_multiplications'] += 1
        return self.reduce(a * b)


def worker(args):
    out, prep = args.out.resolve(), args.prep.resolve()
    out.mkdir(parents=True, exist_ok=False)
    sample = json.loads((prep / 'prime-sample.json').read_text())
    modulus = next(m for m in sample['moduli'] if m['id'] == args.modulus)
    rows = json.loads((prep / 'curves' / args.modulus / 'curves.json').read_text())['curves']
    row, p = rows[0], modulus['p']
    tick = time.monotonic()
    rng = Stream(f'arithmetic/{args.modulus}/20261011')
    products = [(rng.below(p), rng.below(p)) for _ in range(65536)]
    inversions = [1 + rng.below(p - 1) for _ in range(16384)]
    G, _ = generator(row, domain='arithmetic-public-point')
    reference = Curve(p, row['A'], row['B'])
    points, point = [], None
    for _ in range(4099):
        points.append(point)
        point = reference.add(point, tuple(G))
    pairs = list(zip(points[:4096], points[3:4099]))
    generic = Curve(p, row['A'], row['B'])
    specialized = FoldCurve(p, row['A'], row['B'])
    # Exact agreement is checked outside timing, before every measured output
    # comparison; the inverse implementation is intentionally the same.
    expected = {'products': [a * b % p for a, b in products],
                'inversions': [pow(x, -1, p) for x in inversions],
                'point_additions': [generic.add(a, b) for a, b in pairs]}
    assert [specialized.reduce(a * b) for a, b in products] == expected['products']
    assert [specialized.add(a, b) for a, b in pairs] == expected['point_additions']
    observations = []
    order = ['generic', 'sparse', 'sparse', 'generic', 'generic', 'sparse', 'sparse', 'generic', 'generic', 'sparse'] if modulus['arm'] == 'S' else ['generic'] * 5
    repetitions = {'generic': 0, 'sparse': 0}
    for backend in order:
        repetitions[backend] += 1
        curve = generic if backend == 'generic' else specialized
        for workload in ['products', 'inversions', 'point_additions']:
            begin_wall, begin_cpu = time.perf_counter(), time.process_time()
            if workload == 'products':
                actual = [a * b % p for a, b in products] if backend == 'generic' else [specialized.reduce(a * b) for a, b in products]
            elif workload == 'inversions':
                actual = [pow(x, -1, p) for x in inversions]
            else:
                actual = [curve.add(a, b) for a, b in pairs]
            cpu, wall = time.process_time() - begin_cpu, time.perf_counter() - begin_wall
            assert actual == expected[workload]
            observations.append({'backend': backend, 'workload': workload, 'batch': repetitions[backend],
                                 'operations': len(actual), 'cpu_seconds': cpu, 'wall_seconds': wall,
                                 'seconds_per_operation': cpu / len(actual), 'outputs_exactly_equal': True})
    write(out / 'result.json', {'modulus': modulus, 'public_curve': {'p': p, 'A': row['A'], 'B': row['B'], 'G': G},
          'input_seed_domain': f'arithmetic/{args.modulus}/20261011',
          'input_SHA256': __import__('hashlib').sha256(json.dumps([products, inversions, pairs], separators=(',', ':')).encode()).hexdigest(),
          'reference_output_SHA256': __import__('hashlib').sha256(json.dumps(expected, separators=(',', ':')).encode()).hexdigest(),
          'observations': observations, 'elapsed_seconds_including_preparation': time.monotonic() - tick,
          'maximum_RSS_KiB': resource.getrusage(resource.RUSAGE_SELF).ru_maxrss,
          'implementation_scope': 'Python builtin modular arithmetic versus Python binary-fold reduction; field inversion uses the same builtin pow in both backends. This is not an optimized assembly comparison.'})
    print('ARITHMETIC_MODULUS', args.modulus, p.bit_length(), len(observations), flush=True)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--prep', type=Path, required=True)
    parser.add_argument('--out', type=Path, required=True)
    parser.add_argument('--modulus')
    args = parser.parse_args()
    if args.modulus:
        worker(args)
        return
    out = args.out.resolve()
    out.mkdir(parents=True, exist_ok=False)
    cpus = sorted(os.sched_getaffinity(0))
    os.sched_setaffinity(0, {cpus[0]})
    moduli = json.loads((args.prep / 'prime-sample.json').read_text())['moduli']
    random.Random(2026101110).shuffle(moduli)
    start = time.monotonic()
    results = []
    for m in moduli:
        command = [sys.executable, str(Path(__file__).resolve()), '--prep', str(args.prep.resolve()),
                   '--out', str(out / m['id']), '--modulus', m['id']]
        with (out / (m['id'] + '.stdout')).open('x') as so, (out / (m['id'] + '.stderr')).open('x') as se:
            process = subprocess.run(command, stdout=so, stderr=se, timeout=600, preexec_fn=limits)
        if process.returncode:
            raise RuntimeError(f'Arithmetic worker failed: {m["id"]}')
        results.append(m['id'])
        print('ARITHMETIC', len(results), '/', len(moduli), m['id'], flush=True)
    write(out / 'arithmetic-result.json', {'moduli': results, 'complete': True,
          'elapsed_seconds': time.monotonic() - start, 'timing_CPU': cpus[0], 'python': platform.python_version(),
          'source_sha256': sha(Path(__file__)), 'preparation_workers_concurrent': 0,
          'sparse_backend_scope': 'Binary-fold reduction prototype, generic inversion unchanged'})


if __name__ == '__main__':
    main()

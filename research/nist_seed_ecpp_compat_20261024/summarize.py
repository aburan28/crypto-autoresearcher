#!/usr/bin/env python3
"""Replay completed control evidence; report unresolved gates explicitly."""
import hashlib
import json
import platform
import re
from datetime import datetime, timezone
from math import isqrt
from pathlib import Path

HERE = Path(__file__).resolve().parent


def sha(p):
    return hashlib.sha256(Path(p).read_bytes()).hexdigest()


def load(p):
    return json.loads((HERE / p).read_text())


def main():
    target = HERE / 'summary.json'
    assert not target.exists()
    builds = []
    for v in range(1, 5):
        path = HERE / f'attempts/build-v{v}/result.json'
        d = json.loads(path.read_text())
        builds.append({'version': v, 'status': d['status'], 'successful_commands': sum(s['exit_code'] == 0 for s in d['steps']), 'failed_commands': sum(s['exit_code'] != 0 for s in d['steps']), 'receipt_sha256': sha(path)})
    arithmetic = HERE / 'attempts/arithmetic-v3'
    vectors = json.loads((arithmetic / 'fixture.json').read_text())
    lines = (arithmetic / 'run.stdout').read_text().splitlines()
    assert lines[0] == 'ABI 4 4 4 4' and len(lines) == len(vectors) + 1
    for i, (v, line) in enumerate(zip(vectors, lines[1:])):
        a, b = int(v['a']), int(v['b'])
        expected = [a + b, a - b, a * b, a // b, a % b]
        assert line.split()[:2] == ['ROW', str(i)]
        assert list(map(int, line.split()[2:])) == expected
    small = []
    for directory, label, n in [('small-v1', 'prime-101', 101), ('small-v1', 'prime-65537', 65537), ('small-v1', 'composite-15', 15), ('small-v2', 'composite-341', 341)]:
        path = HERE / 'attempts' / directory / label
        prime = n >= 2 and all(n % d for d in range(2, isqrt(n) + 1))
        found = re.findall(r'^(?:% )?This number is (prime|composite)\b.*$', (path / 'stdout.txt').read_text(), re.M)
        assert found == ['prime' if prime else 'composite']
        small.append({'input': n, 'label': found[0], 'stdout_sha256': sha(path / 'stdout.txt')})
    empty = load('attempts/small-v2/empty-catalog-101/result.json')
    missing = load('attempts/small-v2/missing-catalog-101/result.json')
    assert empty['input'] == 101 and empty['exit_code'] == 0 and empty['observed_labels'] == ['composite'] and empty['no_next_D_messages'] == 2 and empty['retry_messages'] == 1
    assert missing['exit_code'] == 139 and not missing['observed_labels']
    cm = load('attempts/cm-only-v1/cm-only-101/result.json')
    assert cm['exit_code'] == 0 and cm['observed_labels'] == ['prime']
    # Independent affine arithmetic and exhaustive point count for the planted
    # CM-branch control. This does not execute a named historical curve.
    p, a, b, P = 101, 21, 0, (20, 80)
    assert (P[1] ** 2 - P[0] ** 3 - a * P[0] - b) % p == 0
    def add(Q, R):
        if Q is None: return R
        if R is None: return Q
        x, y = Q; u, v = R
        if x == u and (y + v) % p == 0: return None
        slope = ((3 * x * x + a) * pow(2 * y, -1, p)) % p if Q == R else ((v - y) * pow(u - x, -1, p)) % p
        z = (slope * slope - x - u) % p
        return z, (slope * (x - z) - y) % p
    def mul(k, Q):
        R = None
        while k:
            if k & 1: R = add(R, Q)
            Q = add(Q, Q); k >>= 1
        return R
    count = 1 + sum((y * y - x ** 3 - a * x - b) % p == 0 for x in range(p) for y in range(p))
    assert count == 104 and mul(26, P) is None and mul(13, P) is not None and mul(2, P) is not None
    initial_checker = []
    for name in ('source-certif1', 'source-certif2'):
        path = HERE / 'attempts/checker-controls-v1' / name
        d = json.loads((path / 'result.json').read_text())
        initial_checker.append({k: d[k] for k in ('name', 'expected_accept', 'admission_accept', 'exit_code')})
    assert initial_checker[0]['admission_accept'] and not initial_checker[1]['admission_accept']
    stop = load('attempts/checker-controls-v2/infrastructure_stop.json')
    assert stop['status'] == 'failed_infrastructure_before_fixture_execution'
    assert not (HERE / 'attempts/checker-controls-v2/started.json').exists()
    artifacts = []
    work = Path(load('attempts/build-v4/result.json')['work_path'])
    for name in ('runecpp', 'checkcertif', 'arithmetic_vectors_v3'):
        path = work / name
        artifacts.append({'path': str(path), 'sha256': sha(path), 'bytes': path.stat().st_size, 'retention': 'local ignored build directory; original source and build recipes are bound'})
    summary = {'recorded_utc': datetime.now(timezone.utc).isoformat(), 'status': 'partial compatibility admission; remaining checker controls unresolved', 'scope': 'engineering controls, not a named-order selection experiment', 'named_order_cases_executed': 0, 'host': platform.platform(), 'python': platform.python_version(), 'builds': builds, 'arithmetic': {'cases': len(vectors), 'exact_comparisons': 5 * len(vectors), 'fixture_sha256': sha(arithmetic / 'fixture.json')}, 'small': small, 'induced_empty': empty, 'induced_missing': missing, 'cm_control': {'p': p, 'a': a, 'b': b, 'P': P, 'point_count': count, 'point_order': 26, 'independent_affine_check': 'passed'}, 'initial_checker': initial_checker, 'checker_continuation_stop': stop, 'pending': ['current-reader variant and remaining positive/negative checker fixtures', 'complete fail-closed launcher and frozen full-cohort replay', 'historical linkage and any ECDLP relevance'], 'artifacts': artifacts, 'summarizer_sha256': sha(__file__)}
    target.write_text(json.dumps(summary, indent=2, sort_keys=True) + '\n')
    print(json.dumps({'status': summary['status'], 'arithmetic_comparisons': 5 * len(vectors), 'normal_small_correct': len(small), 'cm_affine_check': 'passed', 'named_order_cases_executed': 0}))


if __name__ == '__main__':
    main()

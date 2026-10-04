#!/usr/bin/env python3
"""Fixed synthetic F2 circulants only. Importing performs no arithmetic."""
import argparse
import copy
import hashlib
import itertools
import json
import os
import platform
import resource
import subprocess
import sys
import time
import traceback
from datetime import datetime, timezone
from pathlib import Path

EXP = 'EXP-FROB-0d885c'
RUN = 'RUN-FROB-eba655'
SPEC = 'experiments/EXP-FROB-0d885c/specification-component-BATCH-4b3e38.yaml'
OWNED = ('manifest.yaml', 'raw-result.json', 'fixtures.json', 'metrics.json', 'certificates.json', 'report.md')


class Field:
    def __init__(self):
        self.counts = {}
        self.stage = 'arithmetic_and_fixtures'

    def tick(self, op):
        c = self.counts.setdefault(self.stage, {})
        c[op] = c.get(op, 0) + 1

    def add(self, a, b):
        self.tick('addition')
        return a ^ b

    def mul(self, a, b):
        self.tick('multiplication')
        z = 0
        while b:
            if b & 1:
                z ^= a
            b >>= 1
            a <<= 1
            if a & 16:
                a ^= 19
        return z

    def power(self, a, n):
        z = 1
        for _ in range(n):
            z = self.mul(z, a)
        return z

    def inv(self, a):
        self.tick('inversion')
        if not a:
            raise ZeroDivisionError('zero_has_no_inverse')
        return self.power(a, 14)

    def dot(self, a, b):
        z = 0
        for x, y in zip(a, b):
            z = self.add(z, self.mul(x, y))
        return z

    def mm(self, a, b):
        return [[self.dot(row, col) for col in zip(*b)] for row in a]

    def plus(self, a, b):
        return [[self.add(x, y) for x, y in zip(r, s)] for r, s in zip(a, b)]

    def rref(self, a):
        a = copy.deepcopy(a)
        pivots = []
        for col in range(len(a[0])):
            k = next((r for r in range(len(pivots), len(a)) if a[r][col]), None)
            if k is None:
                continue
            r = len(pivots)
            a[r], a[k] = a[k], a[r]
            q = self.inv(a[r][col])
            a[r] = [self.mul(q, x) for x in a[r]]
            for t in range(len(a)):
                if t != r and a[t][col]:
                    q = a[t][col]
                    a[t] = [self.add(x, self.mul(q, y)) for x, y in zip(a[t], a[r])]
            pivots.append(col)
        return a, pivots


def require(ok, reason):
    if not ok:
        raise ValueError(reason)


def identity(n):
    return [[int(i == j) for j in range(n)] for i in range(n)]


def binary_rref(a):
    a = copy.deepcopy(a)
    piv = []
    for c in range(3):
        k = next((i for i in range(len(piv), 3) if a[i][c]), None)
        if k is None:
            continue
        r = len(piv)
        a[r], a[k] = a[k], a[r]
        for i in range(3):
            if i != r and a[i][c]:
                a[i] = [x ^ y for x, y in zip(a[i], a[r])]
        piv.append(c)
    return a, piv


def order_gate(characteristic, order):
    if order % characteristic == 0:
        raise ValueError('cycle_order_not_invertible')


def fixture_errors(row, f):
    errors = []
    if row['reconstructed'] != row['M']:
        errors.append('reconstruction_identity')
    if any(any(f.mm(row['M'], [[v] for v in vector])[i][0] for i in range(3))
           for vector in row['f2_kernel']):
        errors.append('rational_kernel_residual')
    return errors


def panel(f, data):
    # Exhaustive field axioms, independent binary reference used below.
    invs = []
    for a in range(16):
        require(f.add(a, 0) == a and f.add(a, a) == 0 and f.mul(a, 1) == a and f.mul(a, 0) == 0, 'field_identity')
        if a:
            invs.append([a, f.inv(a)])
            require(f.mul(a, invs[-1][1]) == 1, 'field_inverse')
        for b in range(16):
            require(f.add(a, b) == f.add(b, a) and f.mul(a, b) == f.mul(b, a), 'field_commutativity')
            for c in range(16):
                require(f.add(f.add(a, b), c) == f.add(a, f.add(b, c)), 'addition_associativity')
                require(f.mul(f.mul(a, b), c) == f.mul(a, f.mul(b, c)), 'multiplication_associativity')
                require(f.mul(a, f.add(b, c)) == f.add(f.mul(a, b), f.mul(a, c)), 'distributivity')
    try:
        f.inv(0)
    except ZeroDivisionError:
        pass
    else:
        raise ValueError('zero_inverse_accepted')
    data['arithmetic'] = {'elements': 16, 'triples': 4096, 'inverses': invs, 'zero_inverse_rejected': True}
    f.stage = 'representation_checks'
    eye = identity(3)
    zero = [[0] * 3 for _ in range(3)]
    s = [[int(i == (j + 1) % 3) for j in range(3)] for i in range(3)]
    s2 = f.mm(s, s)
    require(f.mm(s2, s) == eye, 'cycle_action')
    order_gate(2, 3)
    omega = next(a for a in range(2, 16) if f.power(a, 3) == 1)
    require(omega != 1 and f.power(omega, 3) == 1, 'omega_order')
    projectors = []
    for j in range(3):
        p = copy.deepcopy(zero)
        for r, sr in enumerate((eye, s, s2)):
            scalar = f.power(omega, (-j * r) % 3)
            p = f.plus(p, [[f.mul(scalar, x) for x in row] for row in sr])
        projectors.append(p)
    require(f.plus(f.plus(*projectors[:2]), projectors[2]) == eye, 'projector_sum')
    columns, selections = [], []
    for j, p in enumerate(projectors):
        require(f.mm(p, p) == p, 'projector_idempotence')
        for k, q in enumerate(projectors):
            if j != k:
                require(f.mm(p, q) == zero, 'projector_orthogonality')
        chosen, indices = [], []
        for i in range(3):
            candidate = chosen + [[row[i] for row in p]]
            if len(f.rref(list(map(list, zip(*candidate))))[1]) > len(chosen):
                chosen = candidate
                indices.append(i)
        require(len(chosen) == 1, 'character_block_dimension')
        columns.extend(chosen)
        selections.append(indices)
    b = list(map(list, zip(*columns)))
    aug, piv = f.rref([row + e for row, e in zip(b, eye)])
    require(piv == [0, 1, 2], 'basis_invertible')
    bi = [row[3:] for row in aug]
    require(f.mm(b, bi) == eye and f.mm(bi, b) == eye, 'basis_inverse')
    data.update(S=s, omega=omega, projectors=projectors, basis_columns=selections, B=b, B_inverse=bi)
    for coeff in itertools.product(range(2), repeat=3):
        m = [[0] * 3 for _ in range(3)]
        for scalar, sr in zip(coeff, (eye, s, s2)):
            m = f.plus(m, [[f.mul(scalar, x) for x in row] for row in sr])
        require(f.mm(s, m) == f.mm(m, s), 'matrix_commutation')
        for p in projectors:
            require(f.mm(p, m) == f.mm(m, p), 'projector_matrix_commutation')
        transformed = f.mm(f.mm(bi, m), b)
        require(all(transformed[i][j] == 0 for i in range(3) for j in range(3) if i != j), 'off_block_zero')
        blocks = [[[transformed[j][j]]] for j in range(3)]
        reconstructed = f.mm(f.mm(b, transformed), bi)
        projected = zero
        for p in projectors:
            projected = f.plus(projected, f.mm(f.mm(p, m), p))
        require(reconstructed == m == projected, 'reconstruction_identity')
        require(all(f.mul(x, x) == x and x in (0, 1) for row in reconstructed for x in row), 'rational_descent')
        rr, piv = binary_rref(m)
        transported, block_kernels = [], []
        for j in range(3):
            kernels = [[1]] if transformed[j][j] == 0 else []
            block_kernels.append(kernels)
            for vector in kernels:
                embedded = [0, 0, 0]
                embedded[j] = vector[0]
                v = [row[0] for row in f.mm(b, [[x] for x in embedded])]
                require(f.mm(m, [[x] for x in v]) == [[0], [0], [0]], 'extension_kernel_residual')
                transported.append({'block': j, 'embedded': embedded, 'vector': v})
        require(len(transported) == 3 - len(piv), 'rank_nullity_agreement')
        kernel, membership = [], []
        for v in itertools.product(range(2), repeat=3):
            residual = [sum(x * y for x, y in zip(row, v)) % 2 for row in m]
            t = [row[0] for row in f.mm(bi, [[x] for x in v])]
            br = [f.mul(transformed[j][j], t[j]) for j in range(3)]
            require((not any(residual)) == (not any(br)), 'rational_kernel_membership')
            if not any(residual):
                kernel.append(list(v))
            membership.append({'vector': list(v), 'direct_residual': residual, 'transformed': t, 'block_residual': br})
        data['fixtures'].append({'coefficients': list(coeff), 'M': m, 'transformed': transformed, 'blocks': blocks,
            'reconstructed': reconstructed, 'projected_reconstruction': projected, 'direct_rref': rr,
            'direct_rank': len(piv), 'direct_nullity': 3-len(piv), 'block_ranks': [int(x[0][0] != 0) for x in blocks],
            'block_kernel_bases': block_kernels, 'transported_kernel': transported, 'f2_kernel': kernel,
            'membership': membership})
    f.stage = 'controls_and_serialization'
    unit = next(x for x in data['fixtures'] if x['coefficients'] == [1, 0, 0])
    perturbed = copy.deepcopy(eye)
    perturbed[0][0] ^= 1
    commutator = f.plus(f.mm(s, perturbed), f.mm(perturbed, s))
    require(commutator != zero, 'commutation_control_accepted')
    omitted = f.plus(projectors[0], projectors[2])
    require(omitted != eye, 'omission_control_accepted')
    try:
        order_gate(2, 2)
    except ValueError as e:
        gate_reason = str(e)
    else:
        raise ValueError('characteristic_gate_control_accepted')
    corrupted = copy.deepcopy(unit)
    corrupted['reconstructed'][0][0] ^= 1
    bad_kernel = copy.deepcopy(unit)
    bad_kernel['f2_kernel'] = [[1, 0, 0]]
    for payload, reason in ((corrupted, 'reconstruction_identity'), (bad_kernel, 'rational_kernel_residual')):
        require(fixture_errors(payload, f) == [reason], 'corruption_control_sensitivity')
    data['controls'] = {'noncommuting': {'M': perturbed, 'commutator': commutator, 'rejected_by': 'matrix_commutation'},
        'omitted_block': {'omitted_j': 1, 'reconstructed': omitted, 'mismatch': f.plus(omitted, eye), 'rejected_by': 'reconstruction_identity'},
        'characteristic_gate': {'characteristic': 2, 'order': 2, 'rejected_by': gate_reason, 'projector_attempted': False},
        'corrupt_reconstruction': {'payload': corrupted, 'rejected_by': fixture_errors(corrupted, f)},
        'corrupt_kernel': {'payload': bad_kernel, 'rejected_by': fixture_errors(bad_kernel, f)}}


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def write_json(path, value):
    with path.open('x') as stream:
        json.dump(value, stream, sort_keys=True, indent=2, allow_nan=False)
        stream.write('\n')


def main():
    parser = argparse.ArgumentParser(description=__doc__, allow_abbrev=False)
    parser.add_argument('--run-dir', required=True, type=Path)
    args = parser.parse_args()
    directory = args.run_dir.resolve()
    require(directory.is_dir(), 'adapter_must_create_run_directory')
    require(not any((directory / name).exists() for name in OWNED), 'existing_output_refused')
    started = datetime.now(timezone.utc).isoformat()
    wall, cpu = time.perf_counter(), time.process_time()
    env, launch, tracked = {}, {}, None
    setup_failure = None
    try:
        env = json.loads((directory / 'environment.json').read_text())
        launch = json.loads((directory / 'launch.json').read_text())
        root = Path(__file__).resolve().parents[3]
        require(launch['run_id'] == RUN and env['commit'] == launch['authority']['commit'], 'launch_binding')
        require(digest(root / SPEC) == env['specification_sha256'], 'specification_hash')
        expected_sources = {str(Path('experiments') / EXP / 'component-BATCH-4b3e38' / name) for name in ('driver.py', 'checker.py', 'dependencies.json', 'implementation-report.json')}
        require(set(env['source_sha256']) == expected_sources, 'source_closure')
        for name, sha in env['source_sha256'].items():
            require(digest(root / name) == sha, 'source_hash:' + name)
        tracked = subprocess.run(['git', 'status', '--porcelain', '--untracked-files=no'], cwd=root, capture_output=True, text=True, check=True).stdout
    except Exception as exc:
        setup_failure = {'type': type(exc).__name__, 'reason': str(exc), 'traceback': traceback.format_exc()}
    f = Field()
    data = {'fixtures': [], 'controls': {}}
    failure = setup_failure
    status = 'failed_infrastructure' if setup_failure else 'completed_valid'
    setup = {'wall_seconds': time.perf_counter()-wall, 'cpu_seconds': time.process_time()-cpu}
    science_wall, science_cpu = time.perf_counter(), time.process_time()
    try:
        require(sys.platform == 'linux', 'linux_guard_required')
        require(os.getpgrp() == os.getpid(), 'isolated_process_group_required')
        require(resource.getrlimit(resource.RLIMIT_AS) == (1073741824, 1073741824), 'memory_guard_not_exact')
        if setup_failure is None:
            panel(f, data)
    except BaseException as exc:
        failure = {'type': type(exc).__name__, 'reason': str(exc), 'traceback': traceback.format_exc()}
        status = 'resource_exhaustion' if isinstance(exc, MemoryError) else 'failed_implementation'
        if str(exc) in ('linux_guard_required', 'memory_guard_not_exact', 'isolated_process_group_required'):
            status = 'failed_infrastructure'
    science = {'wall_seconds': time.perf_counter()-science_wall, 'cpu_seconds': time.process_time()-science_cpu}
    metrics = {'fixture_count': len(data['fixtures']), 'expected_fixture_count': 8, 'control_count': len(data['controls']),
        'expected_control_count': 5, 'field_operation_counts': f.counts, 'operation_count_semantics': 'Count Field.add/mul/inv calls; inv includes its internal multiplications. Binary reference XOR and host bookkeeping excluded.',
        'setup': setup, 'diagnostic': science, 'checker': 'Measured separately in checker stdout; adapter owns final logs.',
        'failure': failure, 'rss_native': resource.getrusage(resource.RUSAGE_SELF).ru_maxrss,
        'rss_native_unit': 'KiB' if sys.platform == 'linux' else 'bytes' if sys.platform == 'darwin' else 'platform-dependent'}
    result = {'valid': failure is None, 'invalid_reason': None if failure is None else failure['reason'],
        'metrics': metrics, 'certificate': {'kind': 'none', 'verified': None, 'verifier': None}}
    write_json(directory / 'fixtures.json', data)
    write_json(directory / 'metrics.json', metrics)
    write_json(directory / 'certificates.json', {'kind': 'none', 'finite_witnesses': 'fixtures.json', 'failure': failure, 'requires_independent_review': True})
    write_json(directory / 'raw-result.json', result)
    with (directory / 'report.md').open('x') as stream:
        stream.write(f'# Synthetic cyclic component\n\nStatus: {status}. Fixtures: {len(data["fixtures"])}/8; controls: {len(data["controls"])}/5.\n\n')
        stream.write('Only the frozen finite representation diagnostic; independent review pending. Original performance thresholds are untested.\n\n')
        stream.write('Failure: ' + json.dumps(failure, sort_keys=True) + '\n')
    bound = {name: {'sha256': digest(directory/name), 'bytes': (directory/name).stat().st_size}
             for name in OWNED if name != 'manifest.yaml'}
    for name in ('launch.json', 'environment.json', 'command.txt'):
        if (directory/name).is_file():
            bound[name] = {'sha256': digest(directory/name), 'bytes': (directory/name).stat().st_size}
    run = {'id': RUN, 'experiment_id': EXP, 'status': status,
        'code': {'commit': env.get('commit'), 'dirty': None if tracked is None else bool(tracked), 'command': (directory/'command.txt').read_text().strip() if (directory/'command.txt').is_file() else None},
        'environment': {'adapter': env, 'python_driver': sys.version, 'platform_driver': platform.platform(),
            'tracked_dirty_status': tracked, 'dirty_scope': 'tracked files only; adapter-created untracked outputs excluded'},
        'inputs': {'curve_id': None, 'seed': 0, 'parameters': {'randomness': 'none; seed 0 is schema sentinel',
            'specification': SPEC, 'specification_sha256': env.get('specification_sha256'), 'source_sha256': env.get('source_sha256'),
            'run_id': RUN, 'base_field': 2, 'character_modulus': 19, 'dimension': 3, 'cycle_order': 3,
            'coefficient_triples': list(map(list, itertools.product(range(2), repeat=3))) }},
        'timing': {'started_at': started, 'finished_at': datetime.now(timezone.utc).isoformat(), 'wall_seconds': time.perf_counter()-wall},
        'resources': {'cpu_seconds': time.process_time()-cpu, 'peak_rss_bytes': resource.getrusage(resource.RUSAGE_SELF).ru_maxrss * (1024 if sys.platform == 'linux' else 1)},
        'result': result, 'artifacts': bound}
    write_json(directory/'manifest.yaml', {'run': run})
    print(json.dumps({'status': status, 'artifact_bytes': {n: (directory/n).stat().st_size for n in OWNED}}, sort_keys=True))
    return 0 if failure is None else 1


if __name__ == '__main__':
    sys.exit(main())

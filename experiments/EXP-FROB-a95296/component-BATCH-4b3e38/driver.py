"""Fixed GF8/GF16 synthetic arithmetic diagnostic; execution requires admission.

Import is inert. The only CLI input is the adapter-created run directory.
"""
import argparse
import copy
import hashlib
import itertools
import json
import platform
import resource
import subprocess
import sys
import time
import traceback
from datetime import datetime, timezone
from pathlib import Path

EXPERIMENT = 'EXP-FROB-a95296'
RUN = 'RUN-FROB-1760cc'
SPEC = 'experiments/EXP-FROB-a95296/specification-component-BATCH-4b3e38.yaml'
SOURCE = 'experiments/EXP-FROB-a95296/component-BATCH-4b3e38/'
FILES = ('manifest.yaml', 'raw-result.json', 'fixtures.json', 'metrics.json', 'certificates.json', 'report.md')


def encode(value):
    return (json.dumps(value, sort_keys=True, separators=(',', ':')) + '\n').encode()


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


class Field:
    def __init__(self, n, modulus):
        self.n, self.modulus, self.q = n, modulus, 1 << n
        self.counts = {'addition': 0, 'multiplication': 0}

    def add(self, x, y):
        self.counts['addition'] += 1
        return x ^ y

    def mul(self, x, y):
        self.counts['multiplication'] += 1
        z = 0
        while y:
            if y & 1:
                z ^= x
            y >>= 1
            x <<= 1
            if x & self.q:
                x ^= self.modulus
        return z


def linear(columns, vector):
    answer = 0
    for i, column in enumerate(columns):
        if (vector >> i) & 1:
            answer ^= column
    return answer


def inverse_columns(columns, n):
    # Gauss-Jordan on rows [B | I]; result returned as columns.
    rows = [sum(((columns[j] >> i) & 1) << j for j in range(n)) | (1 << (n + i)) for i in range(n)]
    for j in range(n):
        pivot = next((i for i in range(j, n) if (rows[i] >> j) & 1), None)
        if pivot is None:
            return None
        rows[j], rows[pivot] = rows[pivot], rows[j]
        for i in range(n):
            if i != j and ((rows[i] >> j) & 1):
                rows[i] ^= rows[j]
    return [sum(((rows[i] >> (n + j)) & 1) << i for i in range(n)) for j in range(n)]


def tensor_mul(tensor, x, y, n):
    out = 0
    for i, j, k in itertools.product(range(n), repeat=3):
        out ^= (((x >> i) & 1) & ((y >> j) & 1) & tensor[i][j][k]) << k
    return out


def project(relation, q, order):
    current, names, stages = list(map(tuple, relation)), ['a', 'b', 'c', 'd'], []
    for removed in order:
        position = names.index(removed)
        kept = names[:position] + names[position + 1:]
        fibers = {key: [] for key in itertools.product(range(q), repeat=len(kept))}
        for row in current:
            key = row[:position] + row[position + 1:]
            fibers[key].append(row[position])
        records = [{'key': list(k), 'values': sorted(set(v))} for k, v in sorted(fibers.items())]
        projected = [r['key'] for r in records if r['values']]
        stages.append({'removed': removed, 'input_coordinates': list(names), 'coordinates': kept,
                       'projection': projected, 'fibers': records,
                       'tuple_count': len(projected), 'fiber_count': len(records),
                       'empty_fiber_count': sum(not r['values'] for r in records),
                       'multiple_fiber_count': sum(len(r['values']) > 1 for r in records),
                       'maximum_branching': max(map(lambda r: len(r['values']), records)),
                       'serialized_witness_bytes': len(encode(records))})
        current, names = list(map(tuple, projected)), kept
    reconstructed = current
    for stage in reversed(stages):
        index = stage['input_coordinates'].index(stage['removed'])
        fibers = {tuple(r['key']): r['values'] for r in stage['fibers']}
        reconstructed = [row[:index] + (v,) + row[index:]
                         for row in reconstructed for v in fibers[row]]
    return {'order': list(order), 'stages': stages,
            'reconstructed': list(map(list, sorted(set(reconstructed))))}


def check_field(f):
    checks, failures = {}, []
    def test(name, passed, witness):
        checks[name] = checks.get(name, 0) + 1
        if not passed:
            failures.append({'check': name, 'witness': witness})
    for a in range(f.q):
        test('additive_identity', f.add(a, 0) == a, [a])
        test('additive_inverse', f.add(a, a) == 0, [a])
        test('multiplicative_identity', f.mul(a, 1) == a, [a])
        test('zero_product', f.mul(a, 0) == 0, [a])
        if a:
            inverses = [b for b in range(f.q) if f.mul(a, b) == 1]
            test('unique_multiplicative_inverse', len(inverses) == 1, [a, inverses])
        for b in range(f.q):
            test('closure', 0 <= f.mul(a, b) < f.q and 0 <= f.add(a, b) < f.q, [a, b])
            test('additive_commutativity', f.add(a, b) == f.add(b, a), [a, b])
            test('multiplicative_commutativity', f.mul(a, b) == f.mul(b, a), [a, b])
            for c in range(f.q):
                test('additive_associativity', f.add(f.add(a, b), c) == f.add(a, f.add(b, c)), [a, b, c])
                test('multiplicative_associativity', f.mul(f.mul(a, b), c) == f.mul(a, f.mul(b, c)), [a, b, c])
                test('distributivity', f.mul(a, f.add(b, c)) == f.add(f.mul(a, b), f.mul(a, c)), [a, b, c])
    return {'counts': checks, 'failures': failures}


def field_panel(n, modulus, fixture, certificate):
    f = Field(n, modulus)
    stages = {}
    def mark(name):
        stages[name] = dict(f.counts)
        f.counts = dict.fromkeys(f.counts, 0)
    fixture.update({'degree': n, 'modulus': modulus})
    certificate['degree'] = n
    certificate['axioms'] = check_field(f)
    fixture['multiplication_table'] = [[f.mul(a, b) for b in range(f.q)] for a in range(f.q)]
    mark('arithmetic_gate')
    if certificate['axioms']['failures']:
        raise ValueError('arithmetic gate failed; dependent checks stopped')
    candidates, bases, seen = [], [], set()
    for theta in range(1, f.q):
        columns, x = [], theta
        for _ in range(n):
            columns.append(x)
            x = f.mul(x, x)
        inverse = inverse_columns(columns, n)
        orbit = tuple(sorted(set(columns)))
        selected = inverse is not None and orbit not in seen and len(bases) < 2
        reason = ('selected' if selected else 'dependent_columns' if inverse is None else
                  'same_selected_orbit' if orbit in seen else 'two_representative_limit')
        candidates.append({'theta': theta, 'columns': columns, 'orbit': list(orbit),
                           'independent': inverse is not None, 'selected': selected, 'reason': reason})
        if selected:
            seen.add(orbit)
            bases.append({'theta': theta, 'columns': columns, 'inverse_columns': inverse})
    fixture.update({'candidates': candidates, 'bases': bases})
    mark('basis_setup')
    relation, relaxed = [], []
    for a, b, c, d in itertools.product(range(f.q), repeat=4):
        if c == f.mul(a, b):
            relaxed.append([a, b, c, d])
            if d == f.add(c, a):
                relation.append([a, b, c, d])
    fixture['reference_relation'] = relation
    fixture['dropped_constraint_relation'] = relaxed
    correct_projection = sorted({(r[0], r[3]) for r in relation})
    relaxed_projection = sorted({(r[0], r[3]) for r in relaxed})
    certificate['dropped_constraint'] = {
        'rejected': relation != relaxed and correct_projection != relaxed_projection,
        'correct_projection': list(map(list, correct_projection)),
        'relaxed_projection': list(map(list, relaxed_projection)),
        'extra_full_tuples': [r for r in relaxed if r not in relation],
        'extra_projected_tuples': list(map(list, sorted(set(relaxed_projection) - set(correct_projection))))}
    mark('direct_relations')
    certificate['bases'] = []
    for basis in bases:
        columns, inverse = basis['columns'], basis['inverse_columns']
        tensor = [[[((linear(inverse, f.mul(columns[i], columns[j])) >> k) & 1)
                    for k in range(n)] for j in range(n)] for i in range(n)]
        basis['tensor'] = tensor
        table = [[linear(columns, tensor_mul(tensor, linear(inverse, a), linear(inverse, b), n))
                  for b in range(f.q)] for a in range(f.q)]
        basis['tensor_multiplication_table'] = table
        failures, roundtrips, squares, units = [], [], [], []
        for a in range(f.q):
            coords = linear(inverse, a)
            back = linear(columns, coords)
            roundtrips.append([a, coords, back])
            shift = ((coords << 1) & (f.q - 1)) | (coords >> (n - 1))
            squared = linear(inverse, f.mul(a, a))
            squares.append([a, coords, squared, shift])
            if back != a or squared != shift:
                failures.append({'check': 'roundtrip_or_square', 'operand': a})
        for i, j in itertools.product(range(n), repeat=2):
            actual = linear(columns, tensor_mul(tensor, 1 << i, 1 << j, n))
            expected = f.mul(columns[i], columns[j])
            units.append([i, j, actual, expected])
            if actual != expected:
                failures.append({'check': 'unit_pair', 'operands': [i, j]})
        for a, b in itertools.product(range(f.q), repeat=2):
            if table[a][b] != fixture['multiplication_table'][a][b]:
                failures.append({'check': 'operand_pair', 'operands': [a, b]})
        entry = {'theta': basis['theta'], 'roundtrips': roundtrips, 'squares': squares,
                 'unit_pairs': units, 'positive_failures': failures}
        certificate['bases'].append(entry)
        if failures:
            raise ValueError('basis/reference gate failed; dependent checks stopped')
        tensor_relation = []
        for a, b, c, d in itertools.product(range(f.q), repeat=4):
            ac, bc, cc, dc = [linear(inverse, v) for v in (a, b, c, d)]
            if cc == tensor_mul(tensor, ac, bc, n) and dc == (cc ^ ac):
                tensor_relation.append([a, b, c, d])
        basis['tensor_relation'] = tensor_relation
        if tensor_relation != relation:
            entry['positive_failures'].append({'check': 'tensor_relation', 'actual': tensor_relation})
            raise ValueError('tensor relation gate failed')
        basis['eliminations'] = [project(tensor_relation, f.q, order) for order in [('b', 'c'), ('c', 'b')]]
        entry['reconstruction_equal'] = [p['reconstructed'] == relation for p in basis['eliminations']]
        if not all(entry['reconstruction_equal']):
            raise ValueError('fiber reconstruction gate failed')
        mark('basis_' + str(basis['theta']) + '_positive')
        terms = [list(ijk) for ijk in itertools.product(range(n), repeat=3) if tensor[ijk[0]][ijk[1]][ijk[2]]]
        term = next((t for t in terms if t[0] != t[1]), terms[0])
        bad_tensor = copy.deepcopy(tensor)
        bad_tensor[term[0]][term[1]][term[2]] = 0
        bad_units = []
        for i, j in itertools.product(range(n), repeat=2):
            actual = linear(columns, tensor_mul(bad_tensor, 1 << i, 1 << j, n))
            expected = f.mul(columns[i], columns[j])
            if actual != expected:
                bad_units.append([i, j, actual, expected])
        bad_inverse = inverse[:]
        bad_inverse[0] ^= 1
        bad_roundtrips = [[a, linear(columns, linear(bad_inverse, a)), a] for a in range(f.q)
                          if linear(columns, linear(bad_inverse, a)) != a]
        bad_inverse_units = []
        for i, j in itertools.product(range(n), repeat=2):
            actual = linear(columns, tensor_mul(tensor, linear(bad_inverse, columns[i]), linear(bad_inverse, columns[j]), n))
            expected = f.mul(columns[i], columns[j])
            if actual != expected:
                bad_inverse_units.append([i, j, actual, expected])
        collision = [[0, b, 0, 0] for b in range(f.q)]
        thinned = [r for r in tensor_relation if r[0] != 0 or r[1] == 0]
        collision_orders = [project(thinned, f.q, order) for order in [('b', 'c'), ('c', 'b')]]
        entry['controls'] = {
            'deleted_tensor_term': {'term': term, 'tensor': bad_tensor, 'unit_failures': bad_units, 'rejected': bool(bad_units)},
            'corrupt_inverse': {'bit': [0, 0], 'inverse_columns': bad_inverse,
                                'roundtrip_failures': bad_roundtrips, 'unit_failures': bad_inverse_units,
                                'rejected': bool(bad_roundtrips) and bool(bad_inverse_units)},
            'collision': {'full_fiber': collision, 'retained_representative': collision[0],
                          'thinned_relation': thinned, 'eliminations': collision_orders,
                          'missing_tuples': collision[1:],
                          'rejected': all(p['reconstructed'] != relation for p in collision_orders)},
            'dropped_constraint': copy.deepcopy(certificate['dropped_constraint'])}
        mark('basis_' + str(basis['theta']) + '_controls')
    return stages


def provenance(run_dir):
    root = Path(__file__).resolve().parents[3]
    env = json.loads((run_dir / 'environment.json').read_text())
    launch = json.loads((run_dir / 'launch.json').read_text())
    if launch['run_id'] != RUN or run_dir.name != RUN:
        raise ValueError('unexpected fixed run identity')
    if env['commit'] != launch['authority']['commit']:
        raise ValueError('launch/environment commit mismatch')
    if digest(root / SPEC) != env['specification_sha256']:
        raise ValueError('specification hash mismatch')
    expected_paths = {SOURCE + p for p in ('driver.py', 'checker.py', 'dependencies.json', 'implementation-report.json')}
    if set(env['source_sha256']) != expected_paths:
        raise ValueError('source closure mismatch')
    for name, sha in env['source_sha256'].items():
        if digest(root / name) != sha:
            raise ValueError('source hash mismatch: ' + name)
    status = subprocess.run(['git', 'status', '--porcelain', '--untracked-files=no'], cwd=root,
                            capture_output=True, text=True, check=True)
    head = subprocess.run(['git', 'rev-parse', 'HEAD'], cwd=root, capture_output=True, text=True, check=True).stdout.strip()
    if head != env['commit']:
        raise ValueError('actual checkout commit differs from launch authority')
    soft, hard = resource.getrlimit(resource.RLIMIT_AS)
    if sys.platform != 'linux' or soft <= 0 or soft > 1024 * 1024 * 1024 or hard != soft:
        raise RuntimeError('required Linux 1024MiB or tighter fixed address-space guard missing')
    code = {'commit': head, 'dirty': bool(status.stdout), 'tracked_status_porcelain': status.stdout,
            'dirty_scope': 'tracked files only; generated untracked run artifacts excluded',
            'command': (run_dir / 'command.txt').read_text().strip(), 'argv': launch['argv'],
            'source_sha256': env['source_sha256']}
    return env, launch, code


def main():
    parser = argparse.ArgumentParser(description=__doc__, allow_abbrev=False)
    parser.add_argument('--run-dir', required=True, type=Path)
    args = parser.parse_args()
    run_dir = args.run_dir.resolve()
    if not run_dir.is_dir() or any((run_dir / p).exists() for p in FILES):
        parser.error('adapter directory required; all six driver outputs must be absent')
    wall, cpu, started = time.monotonic(), time.process_time(), datetime.now(timezone.utc).isoformat()
    fixtures, certificates, stages = {'fields': []}, {'kind': 'none', 'fields': []}, {}
    errors, env, launch, code = [], {}, {}, {}
    setup_cpu = setup_wall = None
    try:
        env, launch, code = provenance(run_dir)
        setup_cpu, setup_wall = time.process_time() - cpu, time.monotonic() - wall
        for n, modulus in [(3, 11), (4, 19)]:
            fixture, certificate = {}, {}
            fixtures['fields'].append(fixture)
            certificates['fields'].append(certificate)
            stages[str(n)] = field_panel(n, modulus, fixture, certificate)
        control_pass = all(c['rejected'] for f in certificates['fields'] for b in f['bases'] for c in b['controls'].values())
        if not control_pass:
            errors.append({'kind': 'implementation_error', 'detail': 'one or more specified negative controls were accepted'})
    except Exception as exc:
        errors.append({'kind': 'infrastructure_error' if not code else 'implementation_error',
                       'type': type(exc).__name__, 'detail': str(exc), 'traceback': traceback.format_exc()})
    status = 'completed_valid' if not errors else ('failed_infrastructure' if not code else 'failed_implementation')
    result = {'status': status, 'errors': errors, 'certificate': {'kind': 'none'},
              'scope': 'Fixed synthetic GF8/GF16 finite component only; independent review pending.',
              'fields_completed': sorted(map(int, stages)),
              'basis_counts': {str(f['degree']): len(f.get('bases', [])) for f in fixtures['fields'] if 'degree' in f},
              'controls_all_rejected': not errors,
              'original_experiment_thresholds_tested': False}
    companions = {'fixtures.json': encode(fixtures), 'certificates.json': encode(certificates), 'raw-result.json': encode(result),
                  'report.md': ('# Finite component execution\n\nStatus: ' + status + '\n\n' + result['scope'] +
                                '\n\nSee exact fixtures, all retained witnesses, and failure records. No original performance threshold was tested.\n').encode()}
    timing = {'started_at': started, 'finished_at': datetime.now(timezone.utc).isoformat(),
              'wall_seconds': time.monotonic() - wall, 'process_cpu_seconds': time.process_time() - cpu,
              'setup_cpu_seconds': setup_cpu, 'setup_wall_seconds': setup_wall,
              'peak_rss': resource.getrusage(resource.RUSAGE_SELF).ru_maxrss,
              'peak_rss_units': 'KiB' if sys.platform == 'linux' else 'bytes' if sys.platform == 'darwin' else 'platform_native',
              'measurement_boundary': 'entry through computation and primary companion encoding; excludes final writes and manifest/metrics encoding',
              'checker_costs': 'measured independently in checker stdout; not available while driver runs'}
    metrics = {'timing': timing, 'field_operation_counts_by_stage': stages,
               'operation_count_definition': 'Calls to physical quotient field add/mul only; binary matrix/tensor bit operations excluded. Counts include reference/control work.',
               'serialized_artifact_bytes': {k: len(v) for k, v in companions.items()},
               'byte_count_scope': 'four closed primary companions; metrics/manifest sizes excluded to avoid recursive sizes'}
    companions['metrics.json'] = encode(metrics)
    for name, data in companions.items():
        with (run_dir / name).open('xb') as stream:
            stream.write(data)
    hashes = {name: digest(run_dir / name) for name in companions}
    for name in ('launch.json', 'command.txt', 'environment.json'):
        if (run_dir / name).is_file():
            hashes[name] = digest(run_dir / name)
    manifest = {'run': {'id': RUN, 'experiment_id': EXPERIMENT, 'status': status, 'code': code,
                       'environment': {'adapter': env, 'python': sys.version, 'platform': platform.platform(),
                                       'inference': {'configured_model': 'gpt-6-astra', 'reasoning_effort': 'medium',
                                                     'resolved_model_id': None, 'model_verified': False,
                                                     'note': 'Source preparation configuration only; diagnostic is deterministic Python.'}},
                       'inputs': {'specification': SPEC, 'specification_sha256': env.get('specification_sha256'),
                                  'fields': [[3, 11], [4, 19]], 'randomness': None, 'run_id': launch.get('run_id')},
                       'timing': timing, 'result': result, 'artifact_sha256': hashes}}
    with (run_dir / 'manifest.yaml').open('xb') as stream:
        stream.write(encode(manifest))
    print(json.dumps({'run_id': RUN, 'status': status}, sort_keys=True))
    return 0 if not errors else 1


if __name__ == '__main__':
    raise SystemExit(main())

"""Independent stdout-only verifier for the fixed synthetic GF8/GF16 run.

No driver import or reference-table trust. Arithmetic uses coefficient convolution,
normal coordinates use exhaustive binary linear-combination enumeration, and
reconstruction uses dictionary natural joins on every common coordinate.
"""
import argparse
import hashlib
import itertools
import json
import resource
import sys
import time
from pathlib import Path

SPEC = 'experiments/EXP-FROB-a95296/specification-component-BATCH-4b3e38.yaml'
SOURCE = 'experiments/EXP-FROB-a95296/component-BATCH-4b3e38/'
RUN = 'RUN-FROB-1760cc'


def packed(x):
    return (json.dumps(x, sort_keys=True, separators=(',', ':')) + '\n').encode()


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def require(condition, detail):
    if not condition:
        raise ValueError(detail)


def multiply(a, b, n, modulus):
    # Explicit carryless coefficient convolution, then high-to-low division.
    coefficients = [0] * (2 * n - 1)
    for i in range(n):
        for j in range(n):
            coefficients[i + j] ^= ((a >> i) & 1) * ((b >> j) & 1)
    for degree in range(2 * n - 2, n - 1, -1):
        if coefficients[degree]:
            for j in range(n + 1):
                coefficients[degree - n + j] ^= (modulus >> j) & 1
    return sum(coefficients[i] << i for i in range(n))


def apply(columns, value):
    selected = [columns[i] for i in range(len(columns)) if value & (1 << i)]
    answer = 0
    for item in selected:
        answer ^= item
    return answer


def normal_candidates(n, modulus):
    q = 2 ** n
    records, selected, chosen_orbits = [], [], []
    for theta in range(1, q):
        orbit_columns = [theta]
        while len(orbit_columns) < n:
            orbit_columns.append(multiply(orbit_columns[-1], orbit_columns[-1], n, modulus))
        mapping = {apply(orbit_columns, bits): bits for bits in range(q)}
        independent = len(mapping) == q
        orbit = sorted(set(orbit_columns))
        accepted = independent and orbit not in chosen_orbits and len(selected) < 2
        reason = ('selected' if accepted else 'dependent_columns' if not independent else
                  'same_selected_orbit' if orbit in chosen_orbits else 'two_representative_limit')
        records.append({'theta': theta, 'columns': orbit_columns, 'orbit': orbit,
                        'independent': independent, 'selected': accepted, 'reason': reason})
        if accepted:
            chosen_orbits.append(orbit)
            selected.append({'theta': theta, 'columns': orbit_columns,
                             'inverse_columns': [mapping[2 ** i] for i in range(n)]})
    return records, selected


def contraction(tensor, x, y, n):
    # Sum each output coordinate independently, with integer parity reduction.
    return sum((sum(tensor[i][j][k] for i in range(n) for j in range(n)
                    if (x & (2 ** i)) and (y & (2 ** j))) % 2) * (2 ** k) for k in range(n))


def elimination(rows, q, order):
    coordinates = ['a', 'b', 'c', 'd']
    current = {tuple(row) for row in rows}
    history = []
    for removed in order:
        remaining = [name for name in coordinates if name != removed]
        indices = [coordinates.index(name) for name in remaining]
        removed_index = coordinates.index(removed)
        # Derive table as the set image of the full current relation.
        image = {(tuple(row[i] for i in indices), row[removed_index]) for row in current}
        lookup = {}
        for key, value in sorted(image):
            lookup.setdefault(key, []).append(value)
        fibers = [{'key': list(key), 'values': lookup.get(key, [])}
                  for key in itertools.product(range(q), repeat=len(remaining))]
        projected = sorted({key for key, _ in image})
        history.append({'removed': removed, 'input_coordinates': coordinates, 'coordinates': remaining,
                        'projection': list(map(list, projected)), 'fibers': fibers,
                        'tuple_count': len(projected), 'fiber_count': len(fibers),
                        'empty_fiber_count': sum(len(row['values']) == 0 for row in fibers),
                        'multiple_fiber_count': sum(len(row['values']) >= 2 for row in fibers),
                        'maximum_branching': max(len(row['values']) for row in fibers),
                        'serialized_witness_bytes': len(packed(fibers))})
        coordinates, current = remaining, set(projected)
    joined = [dict(zip(coordinates, row)) for row in sorted(current)]
    for stage in reversed(history):
        index = {tuple(f['key']): f['values'] for f in stage['fibers']}
        next_join = []
        for row in joined:
            common = tuple(row[name] for name in stage['coordinates'])
            for value in index[common]:
                extension = dict(row)
                extension[stage['removed']] = value
                next_join.append(extension)
        joined = next_join
    restored = sorted({tuple(row[name] for name in ['a', 'b', 'c', 'd']) for row in joined})
    return {'order': list(order), 'stages': history, 'reconstructed': list(map(list, restored))}


def expected_field(n, modulus):
    q = 2 ** n
    domain = range(q)
    table = [[multiply(a, b, n, modulus) for b in domain] for a in domain]
    # Check the reference itself before any artifact comparison.
    for a in domain:
        require(a ^ 0 == a and a ^ a == 0 and table[a][1] == a and table[a][0] == 0, 'reference identities')
        if a:
            require(sum(table[a][b] == 1 for b in domain) == 1, 'reference inverse')
        for b in domain:
            require(0 <= table[a][b] < q and 0 <= a ^ b < q, 'reference closure')
            require(a ^ b == b ^ a and table[a][b] == table[b][a], 'reference commutativity')
            for c in domain:
                require((a ^ b) ^ c == a ^ (b ^ c), 'reference additive associativity')
                require(table[table[a][b]][c] == table[a][table[b][c]], 'reference multiplicative associativity')
                require(table[a][b ^ c] == table[a][b] ^ table[a][c], 'reference distributivity')
    candidates, bases = normal_candidates(n, modulus)
    reference = [list(row) for row in itertools.product(domain, repeat=4)
                 if row[2] == table[row[0]][row[1]] and row[3] == row[2] ^ row[0]]
    relaxed = [list(row) for row in itertools.product(domain, repeat=4) if row[2] == table[row[0]][row[1]]]
    correct_set, relaxed_set = {tuple(row) for row in reference}, {tuple(row) for row in relaxed}
    correct_projected = {(row[0], row[3]) for row in reference}
    relaxed_projected = {(row[0], row[3]) for row in relaxed}
    drop = {'rejected': correct_set != relaxed_set and correct_projected != relaxed_projected,
            'correct_projection': list(map(list, sorted(correct_projected))),
            'relaxed_projection': list(map(list, sorted(relaxed_projected))),
            'extra_full_tuples': list(map(list, sorted(relaxed_set - correct_set))),
            'extra_projected_tuples': list(map(list, sorted(relaxed_projected - correct_projected)))}
    counts = {'additive_identity': q, 'additive_inverse': q, 'multiplicative_identity': q,
              'zero_product': q, 'unique_multiplicative_inverse': q - 1,
              'closure': q*q, 'additive_commutativity': q*q, 'multiplicative_commutativity': q*q,
              'additive_associativity': q**3, 'multiplicative_associativity': q**3, 'distributivity': q**3}
    certificate = {'degree': n, 'axioms': {'counts': counts, 'failures': []}, 'dropped_constraint': drop, 'bases': []}
    fixture = {'degree': n, 'modulus': modulus, 'multiplication_table': table,
               'candidates': candidates, 'bases': bases, 'reference_relation': reference,
               'dropped_constraint_relation': relaxed}
    operation_counts = {
        'arithmetic_gate': {'addition': 2*q + 3*q*q + 6*q**3,
                            'multiplication': 2*q + (q-1)*q + 4*q*q + 7*q**3},
        'basis_setup': {'addition': 0, 'multiplication': (q-1)*n},
        'direct_relations': {'addition': q**3, 'multiplication': q**4}}
    for basis in bases:
        columns, inverse = basis['columns'], basis['inverse_columns']
        coordinate_lookup = {apply(columns, bits): bits for bits in domain}
        tensor = [[[((coordinate_lookup[table[x][y]] // (2**k)) % 2) for k in range(n)]
                   for y in columns] for x in columns]
        basis['tensor'] = tensor
        transported = [[apply(columns, contraction(tensor, coordinate_lookup[a], coordinate_lookup[b], n))
                        for b in domain] for a in domain]
        require(transported == table, 'reference tensor transport')
        basis['tensor_multiplication_table'] = transported
        tensor_relation = [list(row) for row in itertools.product(domain, repeat=4)
                           if coordinate_lookup[row[2]] == contraction(tensor, coordinate_lookup[row[0]], coordinate_lookup[row[1]], n)
                           and coordinate_lookup[row[3]] == coordinate_lookup[row[2]] ^ coordinate_lookup[row[0]]]
        require(tensor_relation == reference, 'reference tensor relation')
        basis['tensor_relation'] = tensor_relation
        basis['eliminations'] = [elimination(tensor_relation, q, order) for order in [('b', 'c'), ('c', 'b')]]
        roundtrips = [[a, coordinate_lookup[a], apply(columns, coordinate_lookup[a])] for a in domain]
        squares = []
        for a in domain:
            bits = coordinate_lookup[a]
            shift = sum(((bits >> i) & 1) << ((i + 1) % n) for i in range(n))
            squares.append([a, bits, coordinate_lookup[table[a][a]], shift])
        require(all(row[2] == row[3] for row in squares), 'reference Frobenius shift')
        units = [[i, j, apply(columns, contraction(tensor, 2**i, 2**j, n)), table[columns[i]][columns[j]]]
                 for i, j in itertools.product(range(n), repeat=2)]
        require(all(row[2] == row[3] for row in units), 'reference units')
        nonzero = [list(t) for t in itertools.product(range(n), repeat=3) if tensor[t[0]][t[1]][t[2]] == 1]
        cross = [term for term in nonzero if term[0] != term[1]]
        removed = (cross or nonzero)[0]
        broken = [[[bit for bit in row] for row in plane] for plane in tensor]
        broken[removed[0]][removed[1]][removed[2]] = 0
        broken_units = []
        for i, j in itertools.product(range(n), repeat=2):
            actual, expected = apply(columns, contraction(broken, 2**i, 2**j, n)), table[columns[i]][columns[j]]
            if actual != expected:
                broken_units.append([i, j, actual, expected])
        broken_inverse = [v ^ (1 if i == 0 else 0) for i, v in enumerate(inverse)]
        broken_roundtrips = [[a, apply(columns, apply(broken_inverse, a)), a] for a in domain
                             if apply(columns, apply(broken_inverse, a)) != a]
        inverse_units = []
        for i, j in itertools.product(range(n), repeat=2):
            actual = apply(columns, contraction(tensor, apply(broken_inverse, columns[i]), apply(broken_inverse, columns[j]), n))
            expected = table[columns[i]][columns[j]]
            if actual != expected:
                inverse_units.append([i, j, actual, expected])
        collision = [[0, b, 0, 0] for b in domain]
        thinned = [row for row in reference if row[0] != 0 or row[1] == 0]
        bad_eliminations = [elimination(thinned, q, order) for order in [('b', 'c'), ('c', 'b')]]
        controls = {
            'deleted_tensor_term': {'term': removed, 'tensor': broken, 'unit_failures': broken_units, 'rejected': bool(broken_units)},
            'corrupt_inverse': {'bit': [0, 0], 'inverse_columns': broken_inverse,
                                'roundtrip_failures': broken_roundtrips, 'unit_failures': inverse_units,
                                'rejected': bool(broken_roundtrips) and bool(inverse_units)},
            'collision': {'full_fiber': collision, 'retained_representative': collision[0],
                          'thinned_relation': thinned, 'eliminations': bad_eliminations,
                          'missing_tuples': collision[1:],
                          'rejected': all(item['reconstructed'] != reference for item in bad_eliminations)},
            'dropped_constraint': drop}
        require(all(c['rejected'] for c in controls.values()), 'reference negative controls')
        certificate['bases'].append({'theta': basis['theta'], 'roundtrips': roundtrips, 'squares': squares,
                                     'unit_pairs': units, 'positive_failures': [],
                                     'reconstruction_equal': [item['reconstructed'] == reference for item in basis['eliminations']],
                                     'controls': controls})
        operation_counts['basis_' + str(basis['theta']) + '_positive'] = {'addition': 0, 'multiplication': n**3 + q + n*n}
        operation_counts['basis_' + str(basis['theta']) + '_controls'] = {'addition': 0, 'multiplication': 2*n*n}
    return fixture, certificate, operation_counts


def verify(directory):
    root = Path(__file__).resolve().parents[3]
    load = lambda name: json.loads((directory / name).read_text())
    manifest, result = load('manifest.yaml'), load('raw-result.json')
    require(set(manifest) == {'run'}, 'canonical manifest envelope')
    run = manifest['run']
    require({'id', 'experiment_id', 'status', 'code', 'environment', 'inputs', 'timing', 'result'} <= set(run), 'manifest required fields')
    require(run['id'] == RUN and directory.name == RUN and run['experiment_id'] == 'EXP-FROB-a95296', 'identity')
    require(run['status'] == result['status'] == 'completed_valid' and run['result'] == result, 'raw/canonical result mismatch or incomplete run')
    require(result['certificate'] == {'kind': 'none'} and not result['errors'], 'unexpected certificate/errors')
    env, launch = load('environment.json'), load('launch.json')
    require(launch['run_id'] == RUN and env['commit'] == launch['authority']['commit'], 'adapter identity')
    require(run['code']['commit'] == env['commit'], 'code commit binding')
    require(run['environment']['adapter'] == env, 'adapter environment binding')
    require(run['inputs']['specification'] == SPEC and run['inputs']['specification_sha256'] == env['specification_sha256'] == sha(root / SPEC), 'spec binding')
    require(run['inputs']['fields'] == [[3, 11], [4, 19]] and run['inputs']['randomness'] is None and run['inputs']['run_id'] == RUN, 'frozen domain identity')
    expected_sources = {SOURCE + name for name in ('driver.py', 'checker.py', 'dependencies.json', 'implementation-report.json')}
    require(set(env['source_sha256']) == expected_sources and run['code']['source_sha256'] == env['source_sha256'], 'source closure')
    for name, value in env['source_sha256'].items():
        require(sha(root / name) == value, 'source content binding: ' + name)
    require(run['code']['argv'] == launch['argv'] == json.loads((directory / 'command.txt').read_text()), 'command binding')
    require(run['code']['dirty'] == bool(run['code']['tracked_status_porcelain']), 'tracked dirty representation')
    companions = {'raw-result.json', 'fixtures.json', 'metrics.json', 'certificates.json', 'report.md', 'launch.json', 'command.txt', 'environment.json'}
    require(set(run['artifact_sha256']) == companions, 'hash coverage')
    for name in companions:
        require(sha(directory / name) == run['artifact_sha256'][name], 'artifact hash: ' + name)
    fixtures, certificates, metrics = load('fixtures.json'), load('certificates.json'), load('metrics.json')
    require(set(fixtures) == {'fields'} and len(fixtures['fields']) == 2, 'complete fixture field coverage')
    require(certificates.get('kind') == 'none' and len(certificates['fields']) == 2, 'certificate field coverage')
    expected_counts, basis_counts = {}, {}
    for index, (n, modulus) in enumerate([(3, 11), (4, 19)]):
        fixture, certificate, counts = expected_field(n, modulus)
        require(fixtures['fields'][index] == fixture, 'complete fixture mismatch degree ' + str(n))
        require(certificates['fields'][index] == certificate, 'complete certificate/control mismatch degree ' + str(n))
        expected_counts[str(n)] = counts
        basis_counts[str(n)] = len(fixture['bases'])
    require(metrics['field_operation_counts_by_stage'] == expected_counts, 'analytically derived driver operation counts')
    require(result['fields_completed'] == [3, 4] and result['basis_counts'] == basis_counts and result['controls_all_rejected'] is True,
            'result coverage/controls')
    require(result['original_experiment_thresholds_tested'] is False, 'scope boundary')
    require(metrics['timing'] == run['timing'], 'timing consistency')
    timing = run['timing']
    for key in ('wall_seconds', 'process_cpu_seconds', 'setup_cpu_seconds', 'setup_wall_seconds', 'peak_rss'):
        require(isinstance(timing[key], (int, float)) and timing[key] >= 0, 'invalid measured timing: ' + key)
    require(timing['peak_rss_units'] == 'KiB', 'Linux RSS units')
    sizes = metrics['serialized_artifact_bytes']
    require(set(sizes) == {'raw-result.json', 'fixtures.json', 'certificates.json', 'report.md'}, 'byte count coverage')
    for name, count in sizes.items():
        require((directory / name).stat().st_size == count, 'artifact byte count: ' + name)
    return {'status': 'verified_fixed_finite_component', 'run_id': RUN, 'basis_counts': basis_counts,
            'scope': 'Exact frozen synthetic fields only; no original performance or cryptanalytic claim.'}


def main():
    parser = argparse.ArgumentParser(description=__doc__, allow_abbrev=False)
    parser.add_argument('--run-dir', required=True, type=Path)
    args = parser.parse_args()
    start_wall, start_cpu = time.monotonic(), time.process_time()
    try:
        output = verify(args.run_dir.resolve())
        code = 0
    except Exception as exc:
        output = {'status': 'rejected', 'type': type(exc).__name__, 'detail': str(exc)}
        code = 1
    output['checker_timing'] = {'wall_seconds': time.monotonic() - start_wall,
                                'process_cpu_seconds': time.process_time() - start_cpu,
                                'peak_rss': resource.getrusage(resource.RUSAGE_SELF).ru_maxrss,
                                'peak_rss_units': 'KiB' if sys.platform == 'linux' else 'bytes' if sys.platform == 'darwin' else 'platform_native',
                                'boundary': 'checker verification including independent arithmetic and artifact reads; before stdout serialization'}
    print(json.dumps(output, sort_keys=True))
    return code


if __name__ == '__main__':
    raise SystemExit(main())

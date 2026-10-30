#!/usr/bin/env python3
"""Post-data deductions from two sealed matrices; no relation or target sampling."""
from pathlib import Path
import argparse
import datetime
import gzip
import hashlib
import json


def eliminate(matrix, modulus, rhs=None):
    width = len(matrix[0]) if matrix else 0
    rows = [[x % modulus for x in row] for row in matrix]
    if rhs is not None:
        rows = [row + [b % modulus] + [int(i == j) for j in range(len(rows))]
                for i, (row, b) in enumerate(zip(rows, rhs))]
    pivot_columns = []
    for col in range(width):
        index = next((i for i in range(len(pivot_columns), len(rows)) if rows[i][col]), None)
        if index is None:
            continue
        pivot = len(pivot_columns)
        rows[pivot], rows[index] = rows[index], rows[pivot]
        inv = pow(rows[pivot][col], -1, modulus)
        rows[pivot] = [x * inv % modulus for x in rows[pivot]]
        for i in range(len(rows)):
            if i != pivot and rows[i][col]:
                scale = rows[i][col]
                rows[i] = [(a-scale*b) % modulus for a, b in zip(rows[i], rows[pivot])]
        pivot_columns.append(col)
    return rows, pivot_columns


def dot(a, b, r):
    return sum(x*y for x, y in zip(a, b)) % r


def point_add(a, b, p):
    if a is None:
        return b
    if b is None:
        return a
    x, y = a
    u, v = b
    if x == u and (y+v) % p == 0:
        return None
    slope = ((3*x*x+2) * pow(2*y, -1, p) if a == b
             else (v-y) * pow(u-x, -1, p)) % p
    w = (slope*slope-x-u) % p
    return (w, (slope*(x-w)-y) % p)


def scalar_mul(k, point, p):
    result = None
    while k:
        if k & 1:
            result = point_add(result, point, p)
        point = point_add(point, point, p)
        k >>= 1
    return result


def review(cell):
    r = {13: 4021, 16: 4111}[cell['b']]
    assert cell['p'] == 4099
    q = cell['projection']
    matrix, rhs, width = q['projected_rows'], q['rhs'], q['U']
    assert width == 15 and len(matrix) == len(rhs)
    assert all(len(row) == width for row in matrix)
    reduced, pivots = eliminate(matrix, r, rhs)
    rank = len(pivots)
    assert rank == q['rank'] == q['augmented_rank']
    assert not any(any(row[width:width+1]) for row in reduced[rank:])
    free = [j for j in range(width) if j not in pivots]
    kernel = []
    for j in free:
        v = [0]*width
        v[j] = 1
        for i, col in enumerate(pivots):
            v[col] = -reduced[i][j] % r
        kernel.append(v)
    assert len(kernel) == q['nullity']
    assert all(dot(row, v, r) == 0 for row in matrix for v in kernel)
    native = q['right_kernel']
    assert len(eliminate(native, r)[1]) == len(kernel)
    assert len(eliminate(native+kernel, r)[1]) == len(kernel)
    assert all(dot(row, v, r) == 0 for row in matrix for v in native)

    graph = [set() for _ in range(width)]
    for row in matrix:
        support = {j for j, x in enumerate(row) if x % r}
        for j in support:
            graph[j].update(support-{j})
    components, seen = [], set()
    for j in range(width):
        if j in seen:
            continue
        component, stack = set(), [j]
        while stack:
            k = stack.pop()
            if k not in component:
                component.add(k)
                stack.extend(graph[k]-component)
        seen.update(component)
        components.append(sorted(component))

    g = tuple(q['public_derivations'][0]['point'])
    assert scalar_mul(r, g, cell['p']) is None
    certificates = []
    for j in range(width):
        if any(v[j] for v in kernel):
            continue
        index = pivots.index(j)
        row = reduced[index]
        assert row[:width] == [int(j == k) for k in range(width)]
        weights = row[width+1:]
        assert [sum(a*matrix[i][k] for i, a in enumerate(weights)) % r
                for k in range(width)] == row[:width]
        value = dot(weights, rhs, r)
        assert value == row[width]
        point = tuple(q['unknown_points'][j])
        assert scalar_mul(value, g, cell['p']) == point
        certificates.append(dict(column=j, point=point, value=value,
                                 row_combination=weights, scalar_certificate_passed=True))

    # All coefficient directions of support <=2 with coefficients +/-1,
    # counted once up to overall sign: 15 + 2*C(15,2) = 225.
    candidates = [dict(columns=[i], coefficients=[1]) for i in range(width)]
    candidates += [dict(columns=[i, j], coefficients=[1, sign])
                   for i in range(width) for j in range(i+1, width)
                   for sign in [1, -1]]
    identifiable = []
    for item in candidates:
        v = [0]*width
        for i, a in zip(item['columns'], item['coefficients']):
            v[i] = a % r
        if all(dot(v, z, r) == 0 for z in kernel):
            identifiable.append(item)

    return dict(b=cell['b'], p=cell['p'], a=2, subgroup_order=r,
                ec1_curve_uid=cell['ec1_curve_uid'], factor_base_uid=cell['curve_uid'],
                accepted_rows=len(matrix), U=width, rank=rank, nullity=len(kernel),
                all_columns_covered=all(any(row[j] for row in matrix) for j in range(width)),
                support_components=components,
                component_ranks=[len(eliminate([[row[j] for j in c] for row in matrix], r)[1])
                                 for c in components],
                identifiable_unit_columns=[v['column'] for v in certificates],
                unit_certificates=certificates,
                sparse_direction_count=len(candidates),
                identifiable_sparse_directions=identifiable,
                independently_rederived_kernel=kernel,
                native_kernel_span_matches=True,
                rank_increment_rule='new row w increases rank iff its syndrome w*K is nonzero',
                uniform_coefficient_row_identifiability_fraction=dict(numerator=1, denominator=r**len(kernel)))


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--input', type=Path, required=True)
    ap.add_argument('--output', type=Path, required=True)
    args = ap.parse_args()
    assert not args.output.exists(), 'Write-once review output already exists'
    stored = args.input.read_bytes()
    logical = gzip.decompress(stored)
    assert hashlib.sha256(logical).hexdigest() == '8f3d5b98b91b01dab9694e3a4c59a4559dbd7bcfa1cb7c4a3045475948fdb007'
    raw = json.loads(logical)
    assert raw['complete'] and raw['experiment_id'] == 'EXP-ECDLP-a9b6a5'
    assert raw['run_id'] == 'RUN-ECDLP-967315' and not raw['secret_labels_present']
    result = dict(schema='prym-retained-matrix-review/v1',
                  generated_at=datetime.datetime.now(datetime.timezone.utc).isoformat(),
                  source=str(args.input), source_stored_sha256=hashlib.sha256(stored).hexdigest(),
                  source_logical_sha256=hashlib.sha256(logical).hexdigest(),
                  implementation_sha256=hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
                  analysis='Exploratory post-data exact deductions from two retained matrices; no new scientific trial or target sample.',
                  command=['python3', str(Path(__file__)), '--input', str(args.input), '--output', str(args.output)],
                  new_scientific_attempts=0, target_points_generated=0,
                  cells=[review(cell) for cell in raw['cells']],
                  limits=['No hidden-log table or discrete-log enumeration.',
                          'Identifiability is conditional on the collected linear equations, not a natural target-descent algorithm.',
                          'Uniform coefficient-vector fractions do not model the distribution of a geometric descent.',
                          'Support graph connectivity does not certify absence of an algebraic invariant.'])
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(result, indent=2)+'\n')
    for c in result['cells']:
        print(json.dumps({k:c[k] for k in ['b','rank','nullity','identifiable_unit_columns','support_components']}))


if __name__ == '__main__':
    main()

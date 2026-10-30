#!/usr/bin/env python3
"""Exploratory small-support row-space deductions, reusing sealed inputs only."""
from pathlib import Path
from itertools import combinations
import datetime
import gzip
import hashlib
import json

from review_matrices import dot, eliminate, point_add, scalar_mul


def main():
    source = Path('experiments/EXP-ECDLP-a9b6a5/runs/RUN-ECDLP-967315/raw-result.json.gz')
    first = Path('research/prym_leads_20261027/derived/matrix-review.json')
    output = Path('research/prym_leads_20261027/derived/matrix-matroid-review.json')
    assert not output.exists()
    logical = gzip.decompress(source.read_bytes())
    assert hashlib.sha256(logical).hexdigest() == '8f3d5b98b91b01dab9694e3a4c59a4559dbd7bcfa1cb7c4a3045475948fdb007'
    cells = []
    raw = json.loads(logical)
    for original, checked in zip(raw['cells'], json.loads(first.read_text())['cells']):
        assert original['b'] == checked['b']
        q = original['projection']
        matrix, rhs, width = q['projected_rows'], q['rhs'], q['U']
        r, kernel = checked['subgroup_order'], checked['independently_rederived_kernel']
        reduced, pivots = eliminate(matrix, r, rhs)
        deficient = {}
        for size in [1, 2, 3]:
            deficient[size] = [c for c in combinations(range(width), size)
                               if len(eliminate([[v[j] for j in c] for v in kernel], r)[1]) < size]
        certificates = []
        for i, j in deficient[2]:
            k = next(k for k, z in enumerate(kernel) if z[j])
            ratio = -kernel[k][i]*pow(kernel[k][j], -1, r) % r
            # Bounded scaling merely presents an already derived coefficient
            # pair compactly. It never samples group points or secret labels.
            a, b = min([(scale, ((scale*ratio+r//2) % r)-r//2) for scale in range(1, 9)],
                       key=lambda v: (max(abs(t) for t in v), sum(abs(t) for t in v)))
            vector = [0]*width
            vector[i], vector[j] = a % r, b % r
            assert all(dot(vector, z, r) == 0 for z in kernel)
            weights = [sum(vector[pivot]*reduced[t][width+1+k]
                           for t, pivot in enumerate(pivots)) % r for k in range(len(matrix))]
            assert [sum(weights[t]*matrix[t][k] for t in range(len(matrix))) % r
                    for k in range(width)] == vector
            value = dot(weights, rhs, r)
            points = [tuple(q['unknown_points'][col]) for col in [i, j]]
            point = point_add(scalar_mul(a % r, points[0], original['p']),
                              scalar_mul(b % r, points[1], original['p']), original['p'])
            assert point == scalar_mul(value, tuple(q['public_derivations'][0]['point']), original['p'])
            certificates.append(dict(columns=[i, j], coefficients=[a, b],
                                     rhs=value, modulus=r, points=points,
                                     row_combination=weights, point_check_passed=True))
        nonminimal = [c for c in deficient[3] if any(set(pair).issubset(c) for pair in deficient[2])]
        cells.append(dict(b=original['b'], ec1_curve_uid=original['ec1_curve_uid'],
                          subgroup_order=r, subsets_checked={str(k): len(list(combinations(range(width), k)))
                                                            for k in [1, 2, 3]},
                          dependent_kernel_column_subsets={str(k): len(v) for k, v in deficient.items()},
                          identifiable_arbitrary_coefficient_pairs=certificates,
                          minimal_support_three_circuits=len(deficient[3])-len(nonminimal),
                          interpretation='The displayed pair combinations are determined by existing rows; neither individual logarithm is determined.'))
    result = dict(schema='prym-retained-small-support-review/v1',
                  generated_at=datetime.datetime.now(datetime.timezone.utc).isoformat(),
                  source_logical_sha256=hashlib.sha256(logical).hexdigest(),
                  first_review_sha256=hashlib.sha256(first.read_bytes()).hexdigest(),
                  source_code_sha256=hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
                  command=['python3', str(Path(__file__))],
                  analysis='Second exploratory post-data deduction; distinguishes arbitrary coefficients from the earlier signed +/-1 directions.',
                  cells=cells, new_scientific_trials=0, target_points_generated=0,
                  limits=['No new independent relation: each displayed certificate is a linear combination of retained rows.',
                          'No target-descent success or attack-cost improvement follows.'])
    output.write_text(json.dumps(result, indent=2)+'\n')
    for c in cells:
        print(c['b'], c['dependent_kernel_column_subsets'],
              [(p['columns'], p['coefficients'], p['rhs']) for p in c['identifiable_arbitrary_coefficient_pairs']])


if __name__ == '__main__':
    main()

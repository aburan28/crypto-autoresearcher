"""Read-only, exploratory recomputation of retained matrices; no new trials.

The input records predate this analysis. No target, divisor, or collector branch
is generated. Output does not promote a scientific claim or measure throughput.
"""
import argparse
from dataclasses import asdict
import gzip
from hashlib import sha256
from itertools import combinations
import json
from pathlib import Path
import subprocess

from crypto_autoresearcher.index_calculus.relation_quality import AffineRelations, cancel_outside

ROOT = Path(__file__).resolve().parents[2]


def analyze():
    input_hashes = {}

    def read(relative, compressed=False):
        path = ROOT/relative
        raw = path.read_bytes()
        input_hashes[relative] = sha256(raw).hexdigest()
        return json.loads(gzip.decompress(raw) if compressed else raw)

    panel = read('research/prym_factor_base_width_20261025/fixtures.json')
    retained = read('experiments/EXP-ECDLP-a9b6a5/runs/RUN-ECDLP-967315/raw-result.json.gz', True)
    fixtures = {f['uid']: f for f in panel['fixtures']}
    prym = []
    for cell in retained['cells']:
        fixture = fixtures[cell['curve_uid']]
        r, projection = fixture['r'], cell['projection']
        matrix = AffineRelations(r, projection['U'])
        progress = []
        for native, row, rhs in zip(cell['rows'], projection['projected_rows'], projection['rhs']):
            # Reconstruct the affine row from the retained native witness labels.
            vector, value = [0]*projection['U'], native['source_scalar']
            for coefficient, mapping in zip(native['coefficients'], projection['native_to_projected']):
                if mapping[0] == 'known':
                    value -= coefficient*mapping[1]
                elif mapping[0] == 'unknown':
                    vector[mapping[1]] += coefficient*mapping[2]
            assert [v % r for v in vector] == row and value % r == rhs
            independent = matrix.add(row, rhs)
            progress.append(dict(witness=len(progress)+1, independent=independent, **matrix.summary()))
        assert len(matrix.rows) == len(cell['rows']) == len(projection['rhs'])
        assert matrix.rank == projection['rank'] and matrix.columns-matrix.rank == projection['nullity']
        assert all(not sum(x*y for x, y in zip(row, vector)) % r
                   for row in matrix.rows for vector in projection['right_kernel'])
        kernel = matrix.kernel()
        singletons = []
        pairs = []
        for i in range(matrix.columns):
            v = [int(j == i) for j in range(matrix.columns)]
            if matrix.identify(v).identifiable:
                singletons.append(i)
        # Enumerate supports, solving the two-column kernel equation exactly.
        # Coefficients are chosen AFTER seeing M. These are not natural targets.
        for i, j in combinations(range(matrix.columns), 2):
            left = [v[i] for v in kernel]
            right = [v[j] for v in kernel]
            pivot = next((h for h, x in enumerate(right) if x), None)
            if pivot is None:
                continue
            c = -left[pivot]*pow(right[pivot], -1, r) % r
            if not c or any((a+c*b) % r for a, b in zip(left, right)):
                continue
            v = [0]*matrix.columns
            v[i], v[j] = 1, c
            certificate = matrix.identify(v)
            assert certificate.identifiable
            pairs.append(dict(columns=[i, j], coefficients=[1, c],
                              points=[projection['unknown_points'][i], projection['unknown_points'][j]],
                              **asdict(certificate)))
        prym.append(dict(p=fixture['p'], a=fixture['a'], b=fixture['b'], r=r,
                         curve_uid=fixture['uid'], generator=fixture['P'],
                         first_atom=fixture['factor_base'][0],
                         public_zero_atom=fixture['P'] == fixture['factor_base'][0]['point'] and fixture['P'][0] == 0,
                         summary=matrix.summary(), progress=progress,
                         identifiable_single_columns=singletons,
                         identifiable_two_column_combinations=pairs,
                         target_scope='post-data selected coefficient combinations; no new target or target recovery'))

    f4 = 'research/p256_factor_base_parallel_20261025/tracks/f4/receipts/check-04/'
    receipt = read(f4+'receipt.json')
    cancellation = []
    for name in ['one_outside', 'two_outside', 'unbalanced_triangle', 'combined']:
        graph = read(f4+'graph_'+name+'.json')
        cases = [read(f4+identifier+'.json') for identifier in graph['case_ids']]
        columns, outside = graph['base_columns'], graph['outside_columns']
        base = AffineRelations(receipt['r'], len(columns))
        B, U, rhs, partial_ids = [], [], [], []
        for case in cases:
            b = [case['row'].get(key, 0) for key in columns]
            u = [case['row'].get(key, 0) for key in outside]
            if not any(u):
                base.add(b, 0)
            else:
                B.append(b); U.append(u); rhs.append(0); partial_ids.append(case['id'])
        result = cancel_outside(base, B, U, rhs)
        assert result['base_rank_after'] == graph['rank_after_cancellation']
        assert result['outside_rank'] == graph['outside_incidence_rank']
        cancellation.append(dict(family=name, input_rows=len(cases), partial_row_ids=partial_ids,
                                 constructed_fixture=True, **result,
                                 counted_cost=None, rate=None,
                                 scope='retained constructed fixtures; no natural row/collision rate'))
    return dict(schema='prime-field-retained-diagnostics/v1',
                source_commit=subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=ROOT, text=True).strip(),
                input_sha256=input_hashes, prym=prym, outside_cancellation=cancellation,
                scientific_trials_started=0, targets_generated=0,
                interpretation='Exploratory post-data algebraic recomputation; not independent scientific review')


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--out', required=True, type=Path)
    args = parser.parse_args()
    output = analyze()
    args.out.parent.mkdir(parents=True, exist_ok=True)
    with args.out.open('x') as stream:
        json.dump(output, stream, indent=2)
        stream.write('\n')
    print(json.dumps(dict(prym=[dict(b=c['b'], **c['summary'],
                       singletons=len(c['identifiable_single_columns']),
                       pair_combinations=len(c['identifiable_two_column_combinations']),
                       public_zero_atom=c['public_zero_atom']) for c in output['prym']],
                       cancellation=[{k:c[k] for k in ['family','base_rank_before','outside_rank','rank_gain','base_rank_after']}
                                     for c in output['outside_cancellation']]), indent=2))


if __name__ == '__main__':
    main()

#!/usr/bin/env python3
"""Explain multiplicity in retained witnesses without collecting new rows."""
from collections import defaultdict, Counter
from itertools import combinations
from pathlib import Path
import datetime
import gzip
import hashlib
import json

from review_matrices import eliminate


def main():
    source = Path('experiments/EXP-ECDLP-a9b6a5/runs/RUN-ECDLP-967315/raw-result.json.gz')
    output = Path('research/prym_leads_20261027/derived/matrix-duplicate-review.json')
    assert not output.exists()
    logical = gzip.decompress(source.read_bytes())
    assert hashlib.sha256(logical).hexdigest() == '8f3d5b98b91b01dab9694e3a4c59a4559dbd7bcfa1cb7c4a3045475948fdb007'
    cells = []
    for cell in json.loads(logical)['cells']:
        q, p, b = cell['projection'], cell['p'], cell['b']
        r = {13: 4021, 16: 4111}[b]
        groups = defaultdict(list)
        assert len(q['projected_rows']) == len(q['rhs']) == len(cell['rows'])
        for i, (row, rhs) in enumerate(zip(q['projected_rows'], q['rhs'])):
            groups[tuple(row)+(rhs,)].append(i)
        records = []
        for affine, indices in groups.items():
            witnesses = [cell['rows'][i] for i in indices]
            assert len({tuple(w['v_coefficients']) for w in witnesses}) == 1
            assert len({w['source_scalar'] for w in witnesses}) == 1
            w = witnesses[0]
            v = w['v_coefficients']
            points = [tuple(t) for t in w['constraints']]
            points += [(x, sum(c*pow(x, i, p) for i, c in enumerate(v)) % p)
                       for x in w['residual_roots']]
            assert len(set(points)) == 6 and len({x for x, y in points}) == 6
            assert all((y*y-x**6-2*x*x-b) % p == 0 for x, y in points)
            source_point = tuple(w['constraints'][0])
            remaining = [point for point in points if point != source_point]
            allowed = {tuple(sorted(t)) for t in combinations(remaining, 3)
                       if all(x for x, y in t) and len({x*x % p for x, y in t}) == 3}
            observed = {tuple(sorted(tuple(t) for t in w['constraints'][1:])) for w in witnesses}
            assert observed == allowed and len(observed) == len(witnesses)
            # Each row used the same complete principal zero divisor, despite
            # selecting different interpolation triples from its support.
            for witness in witnesses:
                zeros = [tuple(t) for t in witness['constraints']]
                zeros += [(x, sum(c*pow(x, i, p) for i, c in enumerate(v)) % p)
                          for x in witness['residual_roots']]
                assert sorted(zeros) == sorted(points)
            records.append(dict(native_witness_indices=indices, source_scalar=w['source_scalar'],
                                projected_coefficients=list(affine[:-1]), rhs=affine[-1],
                                interpolation_coefficients=v, complete_zero_divisor=sorted(points),
                                native_witness_count=len(indices), admissible_constraint_triples=len(allowed),
                                exact_constraint_subset_match=True))
        unique_rows = [list(row[:-1]) for row in groups]
        unique_rank = len(eliminate(unique_rows, r)[1])
        assert unique_rank == len(unique_rows) == q['rank']
        total_sources = len(cell['source_order'])
        assert sorted(cell['source_order']) == list(range(1, 65))
        per_source = 35840
        assert cell['reasons']['S'] % per_source == 0
        active_sources = total_sources-cell['reasons']['S']//per_source
        excluded_anchor_triples = len(list(combinations(range(15), 2)))*4**3
        assert active_sources*excluded_anchor_triples == cell['reasons']['D']
        cells.append(dict(b=b, ec1_curve_uid=cell['ec1_curve_uid'], subgroup_order=r,
                          native_witnesses=len(cell['rows']), distinct_projected_affine_rows=len(records),
                          rank_of_distinct_rows=unique_rank, dependencies_among_distinct_rows=0,
                          multiplicity_histogram=dict(sorted(Counter(str(len(v)) for v in groups.values()).items())),
                          groups=records, active_nonzero_lift_source_blocks=active_sources,
                          source_blocks_rejected_by_S=total_sources-active_sources,
                          excluded_anchor_triples_per_active_source=excluded_anchor_triples,
                          D_count_matches_anchor_triple_identity=True,
                          retained_rows_with_zero_residual=sum(0 in w['residual_roots'] for w in cell['rows']),
                          pole_order_rejections=cell['reasons']['P']))
    result = dict(schema='prym-retained-duplicate-explanation/v1',
                  generated_at=datetime.datetime.now(datetime.timezone.utc).isoformat(),
                  source_logical_sha256=hashlib.sha256(logical).hexdigest(),
                  source_code_sha256=hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
                  command=['python3', str(Path(__file__))], cells=cells,
                  new_scientific_trials=0, target_points_generated=0,
                  interpretation='Finite deficiency is a shortage of distinct projected equations; native witness multiplicity is explained exactly by admissible interpolation-subset choices.',
                  limits=['No universal constructor invariant or asymptotic conclusion.',
                          'Historical native witness and attempt counts remain correct and unchanged.',
                          'The D-count identity is paired with source inspection; no rejected constructor was re-executed.'])
    output.write_text(json.dumps(result, indent=2)+'\n')
    for c in cells:
        print(c['b'], c['native_witnesses'], c['distinct_projected_affine_rows'],
              c['multiplicity_histogram'], 'exact subsets', all(g['exact_constraint_subset_match'] for g in c['groups']))


if __name__ == '__main__':
    main()

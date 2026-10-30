"""Complete zero-completion replay using the existing separate arithmetic lane.

No imports from prym_completion, relations, arithmetic or relation_quality.
This is an implementation cross-check, not an independent scientific review.
"""
from collections import Counter
from hashlib import sha256
from itertools import combinations, product
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT/'research/prym_experiment_design_20261019/implementation'))
from census import Census
from independent import dense_rank, multiply, verify_fixture, verify_row
sys.path.insert(0, str(ROOT/'research/prym_rank_census_20261025'))
from check_census import outcome
sys.path.insert(0, str(ROOT/'research/prym_factor_base_width_20261025'))
from check_inputs import public_projection


class CompletionCensus(Census):
    def descriptor(self, scalar, triple, options):
        f, p = self.fixture, self.p
        if scalar not in self.sources:
            point = multiply(p, 0, f['a'], scalar, tuple(f['P']))
            self.sources[scalar] = None if point is None or point[0] not in self.roots else (
                self.roots[point[0]], -point[1] % p)
        source = self.sources[scalar]
        if source is None:
            return None
        points = [source]
        for j, option in zip(triple, options):
            x, y = f['factor_base'][j]['lift']
            points.append(((-x if option & 2 else x) % p, (-y if option & 1 else y) % p))
        return points if len({x for x, _ in points}) == 4 else None


def check(fixture, sources, result):
    verify_fixture(fixture)
    if (result.get('schema') != 'prym-zero-completion/v1' or result.get('complete') is not True or
            result.get('curve_uid') != fixture['uid'] or result.get('source_order') != sources or
            type(result.get('include_zero')) is not bool):
        raise ValueError('wrong/incomplete result identity')
    reference = (CompletionCensus if result['include_zero'] else Census)(fixture)
    projection = public_projection(fixture, sources)
    if result['projection'] != projection:
        raise ValueError('projection differs from independent public-anchor derivation')
    reasons = dict(S='source_no_nonzero_rational_lift', P='exceptional_pole_order',
                   R='residual_not_two_distinct_rational_roots', X='intersection_not_squarefree',
                   B='residual_endpoint_outside_factor_base', A='canonical_alias', **{'+': 'accepted'})
    seen, counts, digest = set(), Counter(), sha256()
    rows, M, rhs, equations = [], [], [], set()
    attempts = 0
    blocks = []
    legend = dict(S='source_no_nonzero_rational_lift', Z='exceptional_interpolation_x_zero',
                  D='duplicate_interpolation_x', P='exceptional_pole_order',
                  R='residual_not_two_distinct_rational_roots', X='intersection_not_squarefree',
                  B='residual_endpoint_outside_factor_base', A='canonical_alias', **{'+': 'accepted'})
    codes = {value: key for key, value in legend.items()}
    for source in sources:
        source_statuses, source_digest = [], sha256()
        for triple in combinations(range(len(fixture['factor_base'])), 3):
            for options in product(range(4), repeat=3):
                attempts += 1
                status, identity, row = outcome(reference, source, triple, options, seen)
                if status == 'D':
                    # Only the legacy arm has a separate zero-coordinate guard.
                    points = [reference.sources[source]] + [
                        fixture['factor_base'][j]['lift'] for j in triple]
                    reason = ('exceptional_interpolation_x_zero' if not result['include_zero'] and
                              any(point[0] == 0 for point in points) else 'duplicate_interpolation_x')
                else:
                    reason = reasons[status]
                counts[reason] += 1
                encoded = json.dumps([source, list(triple), list(options), identity, reason],
                                     separators=(',', ':')).encode()+b'\n'
                digest.update(encoded)
                source_digest.update(encoded)
                source_statuses.append(codes[reason])
                if row is not None:
                    verify_row(fixture, row)
                    rows.append(row)
                    vector, value = [0]*projection['U'], row['source_scalar']
                    for c, mapping in zip(row['coefficients'], projection['native_to_projected']):
                        if mapping[0] == 'known':
                            value -= c*mapping[1]
                        elif mapping[0] == 'unknown':
                            vector[mapping[1]] += c*mapping[2]
                    vector = [v % fixture['r'] for v in vector]
                    value %= fixture['r']
                    M.append(vector)
                    rhs.append(value)
                    affine = vector+[value]
                    nonzero = next((v for v in affine if v), None)
                    equations.add(tuple(v*pow(nonzero, -1, fixture['r']) % fixture['r'] for v in affine)
                                  if nonzero else tuple(affine))
        blocks.append(dict(scalar=source, attempts=attempts, statuses=''.join(source_statuses),
                           branch_sha256=source_digest.hexdigest()))
    if (result['attempts'] != attempts or result['statuses'] != dict(counts) or result['rows'] != rows or
            result['branch_sha256'] != digest.hexdigest()):
        raise ValueError('complete branch/row replay differs')
    if (result.get('status_blocks') != blocks or result.get('status_legend') != legend):
        raise ValueError('per-source branch statuses differ')
    r, U = fixture['r'], projection['U']
    rank = dense_rank(M, r)
    quality = dict(rows=len(rows), unique_affine_equations=len(equations),
                   duplicate_equations=len(rows)-len(equations), rank=rank, columns=U, nullity=U-rank)
    kernel = result['kernel']
    if (result['quality'] != quality or dense_rank([row+[b] for row, b in zip(M, rhs)], r) != rank or
            len(kernel) != U-rank or any(len(v) != U for v in kernel) or
            dense_rank(kernel, r) != U-rank or
            any(sum(x*y for x, y in zip(row, v)) % r for row in M for v in kernel)):
        raise ValueError('affine rank/kernel certificate differs')
    return dict(attempts_replayed=attempts, rows_verified=len(rows), **quality, checked=True,
                source_statuses_checked=True)

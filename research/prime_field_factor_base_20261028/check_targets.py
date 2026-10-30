"""Independent full target-branch replay and affine recovery certificates.

Uses the historical Census/independent arithmetic, never the target producer,
its arithmetic, or relation_quality. A second implementation is not a separate
scientific reviewer. No scalar label is generated or supplied for Q.
"""
from collections import Counter
from copy import deepcopy
from hashlib import sha256
from itertools import combinations, product
import json

from check_prym import CompletionCensus
from check_inputs import public_projection
from check_census import outcome
from independent import multiply, verify_fixture, verify_row


def reduced(matrix, rhs, width, p):
    """Dense Gauss-Jordan reference, including a consistency check."""
    if len(matrix) != len(rhs) or any(len(row) != width for row in matrix):
        raise ValueError('reference matrix dimensions differ')
    rows = [[x % p for x in row]+[b % p] for row, b in zip(matrix, rhs)]
    pivots, rank = [], 0
    for column in range(width):
        index = next((i for i in range(rank, len(rows)) if rows[i][column]), None)
        if index is None:
            continue
        rows[rank], rows[index] = rows[index], rows[rank]
        inverse = pow(rows[rank][column], -1, p)
        rows[rank] = [x*inverse % p for x in rows[rank]]
        for i, row in enumerate(rows):
            if i != rank and row[column]:
                c = row[column]
                rows[i] = [(x-c*y) % p for x, y in zip(row, rows[rank])]
        pivots.append(column)
        rank += 1
    if any(not any(row[:width]) and row[-1] for row in rows):
        raise ValueError('inconsistent replayed affine system')
    return rows[:rank], pivots


def value_of(form, pivots, vector, p):
    residual, value = [x % p for x in vector], 0
    for row, pivot in zip(form, pivots):
        c = residual[pivot]
        residual = [(x-c*y) % p for x, y in zip(residual, row[:-1])]
        value = (value+c*row[-1]) % p
    return None if any(residual) else value


def project(row, projection, p):
    vector, rhs = [0]*projection['U'], row['source_scalar']
    for c, mapping in zip(row['coefficients'], projection['native_to_projected']):
        if mapping[0] == 'known':
            rhs -= c*mapping[1]
        elif mapping[0] == 'unknown':
            vector[mapping[1]] += c*mapping[2]
    return [v % p for v in vector], rhs % p


def check_weights(record, matrix, rhs, unit, scalar, p):
    if record.get('identifiable') is not True or record.get('value') != scalar:
        raise ValueError('wrong target-identification value')
    weights = record.get('row_weights')
    if not isinstance(weights, (list, tuple)) or len(weights) != len(matrix):
        raise ValueError('wrong target certificate length')
    if (any(type(w) is not int or not 0 <= w < p for w in weights) or
            [sum(w*row[j] for w, row in zip(weights, matrix)) % p for j in range(len(unit))] != unit or
            sum(w*b for w, b in zip(weights, rhs)) % p != scalar):
        raise ValueError('false original-row target certificate')


def check_recipe(fixture,curve_uid,domain,index,max_counters,recipe,attempt_records):
    """Replay the public hash recipe through roots-set/separate group arithmetic."""
    field,r=fixture['p'],fixture['r']
    roots={}
    for y in range(field):roots.setdefault(y*y%field,y)
    rejected=[];attempts=[];expected=None
    for counter in range(max_counters):
        digest=sha256(f'{domain}|{curve_uid}|{index}|{counter}'.encode('utf-8')).digest()
        x=int.from_bytes(digest,'big')%field
        y=roots.get((x**3+fixture['a']*x+fixture['b'])%field)
        point=None if y is None else (x,y)
        reason='not_rational' if point is None else 'outside_subgroup' if multiply(field,0,fixture['a'],r,point) is not None else None
        record=dict(counter=counter,sha256=digest.hex(),x=x)
        attempts.append(dict(record,status=reason or 'selected'))
        if reason:rejected.append(dict(record,reason=reason));continue
        expected=dict(curve_uid=curve_uid,domain=domain,index=index,
                      encoding='UTF-8 domain|curve_uid|decimal_index|decimal_counter; SHA256 big-endian mod p',
                      point=list(point),selected=record,rejected=rejected,subgroup_order=r,scalar_label_generated=False)
        break
    if expected is None:raise ValueError('public target hash counter bound exhausted in replay')
    if recipe!=expected or attempt_records!=attempts:raise ValueError('public hash target recipe/attempts differ')
    return dict(hash_recipe_checked=True,hash_attempts_replayed=len(attempts))


def check(fixture, source_order, preprocessing_rows, target, multipliers, result):
    verify_fixture(fixture)
    p, Q, P = fixture['r'], tuple(target), tuple(fixture['P'])
    field = fixture['p']
    if ((Q[1]*Q[1]-Q[0]**3-fixture['a']*Q[0]-fixture['b']) % field or
            multiply(field, 0, fixture['a'], p, Q) is not None):
        raise ValueError('invalid replay target')
    expected_identity = dict(schema='prym-natural-target-completion/v1', curve_uid=fixture['uid'],
                             target=list(Q), source_order=list(source_order), multipliers=list(multipliers),
                             complete=True, stopping_rule='full census regardless of recovery', scientific_promotion=False)
    if any(result.get(k) != v for k, v in expected_identity.items()):
        raise ValueError('wrong or incomplete target result identity')
    projection = public_projection(fixture, source_order)
    if result['projection'] != projection:
        raise ValueError('target projection differs from fixed public anchors')
    negative = (Q[0], -Q[1] % field)
    native_points = {tuple(atom['point']) for atom in fixture['factor_base']}
    anchor_points = {tuple(anchor['point']) for anchor in projection['public_derivations']}
    if (result['target_is_signed_base_point'] != (Q in native_points or negative in native_points) or
            result['target_is_public_anchor'] != (Q in anchor_points or negative in anchor_points)):
        raise ValueError('target coincidence flags differ from public points')
    width = projection['U']
    base, base_rhs, equations = [], [], set()
    for row in preprocessing_rows:
        if row.get('target_coefficient', 0):
            raise ValueError('target-dependent preprocessing')
        verify_row(fixture, row)
        v, b = project(row, projection, p)
        base.append(v); base_rhs.append(b)
        affine = v+[b]
        first = next((x for x in affine if x), None)
        equations.add(tuple(x*pow(first, -1, p) % p for x in affine) if first else tuple(affine))
    base_form, base_pivots = reduced(base, base_rhs, width, p)
    quality = dict(rows=len(base), unique_affine_equations=len(equations),
                   duplicate_equations=len(base)-len(equations), rank=len(base_pivots),
                   columns=width, nullity=width-len(base_pivots))
    if result['preprocessing'] != quality:
        raise ValueError('preprocessing quality differs from replay')
    # Census uses its P only as the geometric source. Its public-anchor
    # projection is never used here: all anchors above use the original P.
    geometric = deepcopy(fixture)
    geometric['P'] = list(Q)
    reference = CompletionCensus(geometric)
    A, b = [v+[0] for v in base], list(base_rhs)
    unit = [0]*width+[1]
    reasons = dict(S='source_no_nonzero_rational_lift', D='duplicate_interpolation_x',
                   P='exceptional_pole_order', R='residual_not_two_distinct_rational_roots',
                   X='intersection_not_squarefree', B='residual_endpoint_outside_factor_base',
                   A='canonical_alias', **{'+': 'accepted'})
    seen, counts, digest, rows = set(), Counter(), sha256(), []
    attempts, first_single, first_combined = 0, None, None
    blocks=[];codes={v:k for k,v in reasons.items()}
    for t in multipliers:
        statuses=[];source_digest=sha256()
        for triple in combinations(range(len(fixture['factor_base'])), 3):
            for options in product(range(4), repeat=3):
                attempts += 1
                status, identity, row = outcome(reference, t, triple, options, seen)
                reason = reasons[status]
                counts[reason] += 1
                statuses.append(codes[reason])
                encoded=json.dumps([t, list(triple), list(options), identity, reason],separators=(',', ':')).encode()+b'\n'
                digest.update(encoded);source_digest.update(encoded)
                if row is None:
                    continue
                row.update(source_scalar=0, target_coefficient=t)
                verify_row(fixture, row, target=Q)
                rows.append(row)
                v, offset = project(row, projection, p)
                single = value_of(base_form, base_pivots, v, p)
                if single is not None and first_single is None:
                    first_single = dict(attempt=attempts, scalar=(single-offset)*pow(t, -1, p) % p)
                A.append(v+[-t % p]); b.append(offset)
                form, pivots = reduced(A, b, width+1, p)
                scalar = value_of(form, pivots, unit, p)
                if scalar is not None and first_combined is None:
                    first_combined = dict(attempt=attempts, scalar=scalar, A=list(A), b=list(b),
                                          target_rows=len(rows), rank=len(pivots))
        blocks.append(dict(multiplier=t,attempts=attempts,statuses=''.join(statuses),branch_sha256=source_digest.hexdigest()))
    if (result['attempts'] != attempts or result['rows'] != rows or result['statuses'] != dict(counts) or
            result['branch_sha256'] != digest.hexdigest()):
        raise ValueError('complete target branch/row replay differs')
    if result.get('status_blocks')!=blocks or result.get('status_legend')!=reasons:
        raise ValueError('target per-multiplier status coverage differs')
    if result['first_single_recovery'] != first_single:
        raise ValueError('first single-row recovery differs')
    first = result['first_combined_recovery']
    if first_combined is None:
        if first is not None:
            raise ValueError('false combined recovery prefix')
    else:
        if first is None or first['attempt'] != first_combined['attempt']:
            raise ValueError('first combined recovery prefix differs')
        check_weights(first['certificate'], first_combined['A'], first_combined['b'],
                      unit, first_combined['scalar'], p)
        prefix_facts = dict(base_rank=len(base_pivots), base_columns=width, base_rows=len(base),
                            target_rows=first_combined['target_rows'], augmented_rank=first_combined['rank'])
        if (any(first['certificate'].get(k) != v for k, v in prefix_facts.items()) or
                first['certificate'].get('scalar') != first_combined['scalar'] or
                first['certificate'].get('verified') is not True or
                list(first['certificate']['syndrome']) != [0]*(width+1-first_combined['rank'])):
            raise ValueError('combined recovery prefix metadata differs')
    form, pivots = reduced(A, b, width+1, p)
    scalar = value_of(form, pivots, unit, p)
    diagnostic, certificate = result['target_identification'], result['final_target_certificate']
    expected_facts = dict(base_rank=len(base_pivots), base_columns=width, base_rows=len(base),
                          target_rows=len(rows), augmented_rank=len(pivots))
    if any(diagnostic.get(k) != v for k, v in expected_facts.items()):
        raise ValueError('target rank/count metadata differs')
    # Canonical free-variable kernel; the unit-vector syndrome is its last coordinate.
    syndrome = []
    for free in range(width+1):
        if free not in pivots:
            syndrome.append(1 if free == width else (
                -form[pivots.index(width)][free] % p if width in pivots else 0))
    if list(diagnostic['syndrome']) != syndrome:
        raise ValueError('target kernel syndrome differs')
    if scalar is None:
        if certificate is not None or diagnostic['identifiable'] or diagnostic['value'] is not None or diagnostic['row_weights'] is not None:
            raise ValueError('unidentified target reported as recovered')
    else:
        check_weights(diagnostic, A, b, unit, scalar, p)
        if certificate is None or certificate.get('scalar') != scalar or certificate.get('verified') is not True:
            raise ValueError('missing target recovery certificate')
        check_weights(certificate, A, b, unit, scalar, p)
        if (any(certificate.get(k) != v for k, v in expected_facts.items()) or
                list(certificate['syndrome']) != syndrome):
            raise ValueError('target recovery certificate metadata differs')
        if multiply(field, 0, fixture['a'], scalar, P) != Q:
            raise ValueError('replayed scalar fails public point verification')
    return dict(checked=True, attempts_replayed=attempts, rows_verified=len(rows),
                base_rank=len(base_pivots), augmented_rank=len(pivots), target_identifiable=scalar is not None,
                scalar=scalar, complete_branch_replay=True)

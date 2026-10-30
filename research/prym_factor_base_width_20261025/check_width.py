"""Independent exhaustive replay; never imports collect_width or producer arithmetic.

Native target replay is only a later post-run checker. Engineering tests use
marked small planted fixtures. No input-validation path evaluates acceptance.
"""
import argparse
from collections import Counter
from copy import deepcopy
from hashlib import sha256
from itertools import combinations
import json
from pathlib import Path
import resource
import sys
from time import perf_counter, process_time

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT/'research/prym_experiment_design_20261019/implementation'))
from census import Census
from independent import dense_rank, verify_fixture, verify_row, multiply
# This frozen checker has an independently implemented cubic/residual/status
# replay and imports neither rank_census nor its producer arithmetic.
sys.path.insert(0, str(ROOT/'research/prym_rank_census_20261025'))
from check_census import outcome
from check_inputs import public_projection, validate

_REPLAY_CAPABILITY = object()


def digest(value):
    return sha256(json.dumps(value, sort_keys=True, separators=(',', ':')).encode()).hexdigest()


def projected_equation(row, projection, r):
    M, rhs = [0]*projection['U'], row['source_scalar'] % r
    for coefficient, item in zip(row['coefficients'], projection['native_to_projected']):
        if item[0] == 'known':
            rhs -= coefficient*item[1]
        if item[0] == 'unknown':
            M[item[1]] += coefficient*item[2]
    return [a % r for a in M], rhs % r


def reencode(fixture, row):
    # Construct the fixed transport independently from the producer helper.
    other, witness = deepcopy(fixture), deepcopy(row)
    n, p, r = len(fixture['factor_base']), fixture['p'], fixture['r']
    for new in range(n):
        old = n-1-new
        atom = fixture['factor_base'][old]
        x, y = atom['lift']
        sy = (-1)**(old % 2)
        sx = 1 if old % 3 == 0 else -1
        other['factor_base'][new] = dict(point=[atom['point'][0], sy*y % p], lift=[sx*x % p, sy*y % p])
        witness['coefficients'][new] = sy*row['coefficients'][old] % r
    witness['base_labels'] = []
    for old, sign, option in row['base_labels']:
        sy = (-1)**(old % 2)
        sx = 1 if old % 3 == 0 else -1
        new_sign = sy*sign
        deck = sx*(-1 if option >= 2 else 1)
        witness['base_labels'].append([n-1-old, new_sign, int(new_sign < 0)+2*int(deck < 0)])
    verify_row(other, witness)
    return other, witness


def check_certificate(fixture, cell, sources):
    projection = public_projection(fixture, sources)
    declared = cell['projection']
    if any(declared[k] != value for k, value in projection.items()):
        raise ValueError('false public projection/anchor/U/map')
    M, b = [], []
    for row in cell['rows']:
        verify_row(fixture, row)
        coefficients, rhs = projected_equation(row, projection, fixture['r'])
        M.append(coefficients)
        b.append(rhs)
    augmented = [row+[rhs] for row, rhs in zip(M, b)]
    rank, augmented_rank = dense_rank(M, fixture['r']), dense_rank(augmented, fixture['r'])
    U, r = projection['U'], fixture['r']
    if (declared['projected_rows'] != M or declared['rhs'] != b or
        (declared['rank'], declared['augmented_rank'], declared['nullity'], declared['consistent'],
         declared['all_columns_publicly_known']) != (rank, augmented_rank, U-rank, rank == augmented_rank, U == 0)):
        raise ValueError('false affine/augmented matrix/rank/nullity')
    indices = declared['independent_row_indices']
    if (len(set(indices)) != rank or len(indices) != rank or
        any(not isinstance(i, int) or not 0 <= i < len(M) for i in indices) or
        dense_rank([M[i] for i in indices], r) != rank):
        raise ValueError('false independent-row certificate')
    pivots = {int(k): row for k, row in declared['pivots'].items()}
    if len(pivots) != rank:
        raise ValueError('false pivot count')
    for pivot, row in pivots.items():
        if not 0 <= pivot < U or len(row) != U+1 or row[pivot] != 1 or any(row[:pivot]):
            raise ValueError('false echelon pivot')
    if dense_rank(augmented+list(pivots.values()), r) != augmented_rank:
        raise ValueError('pivot row outside augmented span')
    kernel = declared['right_kernel']
    if (len(kernel) != U-rank or any(len(v) != U for v in kernel) or
        any(any(type(x) is not int or not 0 <= x < r for x in v) for v in kernel) or
        dense_rank(kernel, r) != U-rank or
        any(sum(x*y for x, y in zip(row, v)) % r for row in M for v in kernel)):
        raise ValueError('false finite right-kernel certificate')
    solution = declared['solution']
    if rank == U and augmented_rank == rank:
        if not isinstance(solution, list) or len(solution) != U:
            raise ValueError('missing full-rank solution')
        if any(sum(x*y for x, y in zip(row, solution)) % r != rhs for row, rhs in zip(M, b)):
            raise ValueError('false affine solution')
        for point, scalar in zip(projection['unknown_points'], solution):
            if multiply(fixture['p'], 0, fixture['a'], scalar, tuple(fixture['P'])) != tuple(point):
                raise ValueError('solution fails public point equation')
    elif solution is not None:
        raise ValueError('solution asserted without full consistent rank')
    return dict(U=U, rank=rank, augmented_rank=augmented_rank, nullity=U-rank, rows_verified=len(M))


def check(config, panel, result, blocks, *, software=False, capability=None):
    if software:
        if any(not f.get('software_control') or f['p'] > 211 for f in panel['fixtures']):
            raise ValueError('software replay restricted to marked small fixtures')
    else:
        if capability is not _REPLAY_CAPABILITY:
            raise ValueError('target replay requires post-run native admission')
        validate(config, panel)
    if not result['complete'] or result['secret_labels_present'] or result['new_m8_attempts'] != 0:
        raise ValueError('incomplete, secret-labelled or extra m8 workload')
    if not software and result['historical_reference_sha256'] != panel['historical_reference_sha256']:
        raise ValueError('false historical reference binding')
    expected = [f['uid'] for f in panel['fixtures']]
    if [c['curve_uid'] for c in result['cells']] != expected or len(set(expected)) != len(expected):
        raise ValueError('wrong/missing/duplicate cell')
    blocks, checks = iter(blocks), []
    for fixture, cell in zip(panel['fixtures'], result['cells']):
        verify_fixture(fixture)
        if (cell['p'], cell['b'], cell['ec1_curve_uid']) != (
                fixture['p'], fixture['b'], fixture.get('ec1', {}).get('curve_uid')):
            raise ValueError('false cell curve/display identity')
        sources = fixture['width_binding']['source_order']
        if cell['source_order'] != sources or cell['seed'] != 0 or cell['arm'] != 'm16_full35840':
            raise ValueError('false source schedule/arm/seed')
        ref = Census(fixture)
        triples = list(combinations(range(len(fixture['factor_base'])), 3))
        seen, counts, attempts, row_index = set(), Counter(), 0, 0
        M, basis, progress, checkpoints, first = [], [], [], [], None
        projection = public_projection(fixture, sources)
        for source in sources:
            witnesses = []
            block = next(blocks)
            while block.get('schema') == 'prym-width-accepted-witness/v1':
                witnesses.append(block)
                block = next(blocks)
            if (block['schema'], block['curve_uid'], block['seed'], block['arm'], block['scalar']) != (
                'prym-width-source-block/v1', fixture['uid'], 0, 'm16_full35840', source):
                raise ValueError('wrong source block identity/order')
            if len(block['statuses']) != len(triples)*64:
                raise ValueError('dropped/duplicate branch status')
            commitment = sha256()
            source_row_index = 0
            for branch in range(len(triples)*64):
                attempts += 1
                option = branch % 64
                options = (option//16, option//4 % 4, option % 4)
                status, identity, row = outcome(ref, source, triples[branch//64], options, seen)
                if status != block['statuses'][branch]:
                    raise ValueError('false replayed branch status at '+str(attempts))
                commitment.update(json.dumps([source, branch, identity, status], separators=(',', ':')).encode()+b'\n')
                counts[status] += 1
                if row is None:
                    continue
                actual = cell['rows'][row_index]
                verify_row(fixture, actual)
                if row != actual or cell['row_attempts'][row_index] != attempts:
                    raise ValueError('false source/witness/row location')
                if witnesses[source_row_index] != dict(
                        schema='prym-width-accepted-witness/v1', curve_uid=fixture['uid'],
                        scalar=source, attempt=attempts, row_index=row_index, row=actual,
                        transported_witness_sha256=cell['transported_witness_hashes'][row_index]):
                    raise ValueError('missing/altered immediate witness record')
                source_row_index += 1
                other, witness = reencode(fixture, actual)
                other_projection = public_projection(other, sources)
                # Compare canonical projected points/equations; native map
                # arrays follow the declared signed permutation.
                if (digest(witness) != cell['transported_witness_hashes'][row_index] or
                    other_projection['unknown_points'] != projection['unknown_points'] or
                    projected_equation(actual, projection, fixture['r']) !=
                    projected_equation(witness, other_projection, fixture['r'])):
                    raise ValueError('false transported encoding A/A')
                vector, rhs = projected_equation(actual, projection, fixture['r'])
                M.append(vector)
                now = dense_rank(basis+[vector], fixture['r'])
                row_index += 1
                if now > len(basis):
                    basis.append(vector)
                    progress.append((attempts, row_index, now))
                    if projection['U'] > 0 and now == projection['U'] and first is None:
                        first = (attempts, row_index, now)
            if commitment.hexdigest() != block['attempt_digest']:
                raise ValueError('altered branch digest')
            if source_row_index != len(witnesses):
                raise ValueError('extra/duplicate immediate witness record')
            checkpoint = (source, attempts, row_index, len(basis))
            if checkpoint != tuple(block['checkpoint'][k] for k in ['source_scalar', 'attempt', 'accepted_rows', 'rank']):
                raise ValueError('source-block checkpoint differs')
            checkpoints.append(checkpoint)
        if (len(cell['rows']) != row_index or len(cell['row_attempts']) != row_index or
            len(cell['transported_witness_hashes']) != row_index or Counter(cell['reasons']) != counts or
            cell['attempts'] != attempts or cell['distinct_candidates'] != len(seen)):
            raise ValueError('wrong complete status/row/alias totals')
        if progress != [tuple(v[k] for k in ['attempt', 'accepted_rows', 'rank']) for v in cell['rank_progress']]:
            raise ValueError('false rank progress')
        observed = cell['first_full_rank']
        if first != (None if observed is None else tuple(observed[k] for k in ['attempt', 'accepted_rows', 'rank'])):
            raise ValueError('false first-full location')
        if checkpoints != [tuple(v[k] for k in ['source_scalar', 'attempt', 'accepted_rows', 'rank']) for v in cell['source_checkpoints']]:
            raise ValueError('false complete source checkpoints')
        certificates = check_certificate(fixture, cell, sources)
        checks.append(dict(curve_uid=fixture['uid'], attempts_replayed=attempts,
                           rejected_attempts_replayed=attempts-row_index, **certificates))
    if next(blocks, None) is not None:
        raise ValueError('extra/duplicate source block')
    return checks


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--config', required=True, type=Path)
    parser.add_argument('--run-dir', required=True, type=Path)
    args = parser.parse_args()
    start, cpu = perf_counter(), process_time()
    failures, checks = [], []
    raw = args.run_dir/'raw-result.json'
    try:
        config = json.loads(args.config.read_text())
        panel = json.loads((ROOT/config['fixture_file']).read_text())
        result = json.loads(raw.read_text())
        if result['config_sha256'] != sha256(args.config.read_bytes()).hexdigest():
            raise ValueError('configuration digest differs')
        # A target checker requires a completed native producer receipt context;
        # it is not exposed as a target acceptance pilot.
        from runtime_width import check_replay_admission
        check_replay_admission(args.run_dir, args.config)
        with (args.run_dir/'events.jsonl').open() as stream:
            checks = check(config, panel, result, map(json.loads, stream), capability=_REPLAY_CAPABILITY)
    except Exception as exc:
        failures.append(repr(exc))
    verification = dict(schema='prym-width-independent/v1', status='failed' if failures else 'passed',
                        failed_checks=failures, cells=checks,
                        raw_result_sha256=sha256(raw.read_bytes()).hexdigest() if raw.exists() else None,
                        producer_collector_imported=False, producer_arithmetic_imported=False,
                        scope='Complete rejected/alias/accepted branch replay, public witnesses, signed/deck A/A, exact affine/augmented rank and right-kernel certificates.',
                        operation_counters_independently_verified=False, prescribed_execution_proof=False,
                        replay_operation_vector=dict(
                            branches_replayed=sum(c['attempts_replayed'] for c in checks),
                            accepted_witnesses_replayed=sum(c['rows_verified'] for c in checks)),
                        checker_cost_exclusions=['Independent arithmetic primitive counts and dense-elimination units uninstrumented.',
                                                 'No compression/upload/readback cost in this checker.'],
                        wall_seconds=perf_counter()-start, cpu_seconds=process_time()-cpu,
                        peak_rss_bytes=resource.getrusage(resource.RUSAGE_SELF).ru_maxrss*1024)
    with (args.run_dir/'verification.json').open('x') as stream:
        json.dump(verification, stream, indent=2)
        stream.write('\n')
    print(json.dumps(dict(status=verification['status'], failed_checks=failures, cells=len(checks))))
    return bool(failures)


if __name__ == '__main__':
    raise SystemExit(main())

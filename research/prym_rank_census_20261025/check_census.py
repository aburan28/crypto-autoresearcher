"""Independent complete-stream replay. Does not import the collector or its arithmetic."""
import argparse
from collections import Counter
from copy import deepcopy
from hashlib import sha256
from itertools import combinations, product
import json
from pathlib import Path
import random
import resource
import sys
from time import perf_counter, process_time

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / 'research/prym_experiment_design_20261019/implementation'))
from census import Census
from independent import (convolution, dense_rank, multiply, vandermonde,
                         verify_fixture, verify_rank, verify_row)


def encode(value):
    return json.dumps(value, sort_keys=True, separators=(',', ':'))


def identity(fixture, scalar, triple, options, points):
    choices = []
    for xsign in [1, -1]:
        for ysign in [1, -1]:
            transformed = [(xsign*x % fixture['p'], ysign*y % fixture['p']) for x, y in points]
            labels = sorted((j, ysign*(-1 if op & 1 else 1), *point)
                            for j, op, point in zip(triple, options, transformed[1:]))
            choices.append(dict(curve_uid=fixture['uid'], source_scalar=ysign*scalar % fixture['r'],
                                lambda_=1, signed_fb_lift_ids=dict(source_lift=transformed[0], base_lifts=labels)))
    for choice in choices:
        choice['lambda'] = choice.pop('lambda_')
    return sha256(min(map(encode, choices)).encode()).hexdigest()


def outcome(reference, scalar, triple, options, seen):
    points = reference.descriptor(scalar, triple, options)
    if points is None:
        return ('S' if reference.sources[scalar] is None else 'D'), None, None
    key = identity(reference.fixture, scalar, triple, options, points)
    if key in seen:
        return 'A', key, None
    seen.add(key)
    p, f = reference.p, reference.fixture
    v = vandermonde(p, points)
    if len(v) == 4 and v[-1]*v[-1] % p == 1:
        return 'P', key, None
    vv = convolution(p, v, v)
    F = [f['b'], 0, f['a'], 0, 0, 0, 1]
    remainder = [((vv[j] if j < len(vv) else 0)-F[j]) % p for j in range(7)]
    divisor = [1]
    for x, y in points:
        divisor = convolution(p, divisor, [-x % p, 1])
    quotient = [0]*3
    for j in [2, 1, 0]:
        quotient[j] = remainder[j+4]
        for i, c in enumerate(divisor):
            remainder[j+i] = (remainder[j+i]-quotient[j]*c) % p
    if any(remainder):
        raise ValueError('independent residual division failed')
    c, b, a = quotient
    disc = (b*b-4*a*c) % p
    if not a or not disc or disc not in reference.roots:
        return 'R', key, None
    root = reference.roots[disc]
    inv = pow(2*a, -1, p)
    roots = {(-b-root)*inv % p, (-b+root)*inv % p}
    if len(roots) != 2 or roots & {x for x, y in points}:
        return 'X', key, None
    row = reference.accepted(scalar, triple, options)
    return ('B', key, None) if row is None else ('+', key, row)


def independent_schedule(fixture, seed, config):
    sources = list(range(1, min(config['public_source_max'], fixture['r']-1)+1))
    random.Random(f"{config['domain']}|sources|{fixture['uid']}|{seed}").shuffle(sources)
    # Arithmetic decoding of branch b = 64*t+16*o0+4*o1+o2.
    triples = list(combinations(range(len(fixture['factor_base'])), 3))
    rng = random.Random(f"{config['domain']}|tuples|{fixture['uid']}|{seed}")
    sampled = {s: rng.sample(range(64*len(triples)), config['sample_branches_per_source']) for s in sources}
    return sources, triples, sampled


def exact_public(fixture, maximum):
    known = {}
    for scalar in range(1, min(maximum, fixture['r']-1)+1):
        point = multiply(fixture['p'], 0, fixture['a'], scalar, tuple(fixture['P']))
        for j, atom in enumerate(fixture['factor_base']):
            if point == tuple(atom['point']):
                known[j] = scalar
            if point == (atom['point'][0], -atom['point'][1] % fixture['p']):
                known[j] = -scalar % fixture['r']
    return known


def check(config, panel, result, blocks):
    if not result['complete'] or result['secret_labels_present']:
        raise ValueError('incomplete or secret-labelled result')
    fixtures = {f['uid']: f for f in panel['fixtures']}
    for f in fixtures.values():
        verify_fixture(f)
    expected = [(f['uid'], s, arm) for f in panel['fixtures'] for s in config['seeds'] for arm in config['arms']]
    cells = {(c['curve_uid'], c['seed'], c['arm']): c for c in result['cells']}
    if list(cells) != expected or len(cells) != len(result['cells']):
        raise ValueError('missing/duplicate/reordered cells')
    blocks = iter(blocks)
    checks, matrices = [], {}
    for key in expected:
        cell = cells[key]
        f = fixtures[key[0]]
        ref = Census(f)
        sources, triples, sampled = independent_schedule(f, key[1], config)
        declared = {v['column']: v['scalar'] for v in cell['projection']['public_derivations']}
        known = exact_public(f, config['public_source_max'])
        unknown = [j for j in range(len(f['factor_base'])) if j not in known]
        if declared != known or cell['projection']['unknown_columns'] != unknown:
            raise ValueError('incomplete or false public-column removal')
        seen, counts, attempts, row_index = set(), Counter(), 0, 0
        M, augmented, basis, progress, checkpoints, first = [], [], [], [], [], None
        previous_rank = 0
        for source in sources:
            block = next(blocks)
            if (block['curve_uid'], block['seed'], block['arm'], block['scalar']) != (*key, source):
                raise ValueError('source block changed')
            branches = sampled[source] if key[2] == 'sample64' else range(64*len(triples))
            if len(block['statuses']) != len(branches):
                raise ValueError('branch coverage mismatch')
            digest = sha256()
            for offset, branch in enumerate(branches):
                attempts += 1
                triple = triples[branch//64]
                option = branch % 64
                options = (option//16, option//4 % 4, option % 4)
                status, ident, row = outcome(ref, source, triple, options, seen)
                if status != block['statuses'][offset]:
                    raise ValueError(f'replayed status differs at {key} attempt {attempts}')
                digest.update(json.dumps([source, branch, ident, status], separators=(',', ':')).encode()+b'\n')
                counts[status] += 1
                if row is None:
                    continue
                actual = cell['rows'][row_index]
                verify_row(f, actual)
                if row != actual or cell['row_attempts'][row_index] != attempts:
                    raise ValueError('replayed witness or attempt differs')
                perm = list(range(len(f['factor_base'])))
                random.Random(f'prym-W-reencode-v1|{key[1]}').shuffle(perm)
                inverse = {old: new for new, old in enumerate(perm)}
                other, witness = deepcopy(f), deepcopy(actual)
                other['factor_base'] = [f['factor_base'][j] for j in perm]
                witness['coefficients'] = [actual['coefficients'][j] for j in perm]
                witness['base_labels'] = [[inverse[j], sign, op] for j, sign, op in actual['base_labels']]
                verify_row(other, witness)
                if sha256(encode(witness).encode()).hexdigest() != cell['transported_witness_hashes'][row_index]:
                    raise ValueError('A/A transported witness differs')
                coefficients = [row['coefficients'][j] for j in unknown]
                rhs = (source-sum(row['coefficients'][j]*value for j, value in known.items())) % f['r']
                M.append(coefficients)
                augmented.append(coefficients+[rhs])
                now = dense_rank(basis+[coefficients], f['r'])
                row_index += 1
                if now > previous_rank:
                    basis.append(coefficients)
                    progress.append((attempts, row_index, now))
                    previous_rank = now
                    if unknown and now == len(unknown) and first is None:
                        first = (attempts, row_index, now)
            if digest.hexdigest() != block['attempt_digest']:
                raise ValueError('attempt commitment differs')
            checkpoints.append((source, attempts, row_index, previous_rank))
        if len(cell['rows']) != row_index or len(cell['transported_witness_hashes']) != row_index:
            raise ValueError('extra/missing row')
        if counts != Counter(cell['reasons']) or attempts != cell['attempts'] or len(seen) != cell['distinct_candidates']:
            raise ValueError('finite census totals differ')
        if progress != [(v['attempt'], v['accepted_rows'], v['rank']) for v in cell['rank_progress']]:
            raise ValueError('rank progression differs')
        observed_first = cell['first_full_rank']
        observed_first = None if observed_first is None else tuple(observed_first[k] for k in ['attempt', 'accepted_rows', 'rank'])
        if first != observed_first:
            raise ValueError('first full-rank location differs')
        if checkpoints != [tuple(v[k] for k in ['source_scalar', 'attempt', 'accepted_rows', 'rank']) for v in cell['source_checkpoints']]:
            raise ValueError('source checkpoint differs')
        rank_check = verify_rank(f, cell)
        kernel = cell['nullspace']
        U, rank = rank_check['U'], rank_check['rank']
        if len(kernel) != U-rank or any(len(v) != U for v in kernel) or dense_rank(kernel, f['r']) != U-rank:
            raise ValueError('nullspace basis dimension differs')
        if any(sum(x*y for x, y in zip(row, v)) % f['r'] for row in M for v in kernel):
            raise ValueError('false finite nullspace witness')
        matrices[key] = M
        checks.append(dict(curve_uid=key[0], seed=key[1], arm=key[2], **rank_check,
                           rejected_attempts_replayed=attempts-row_index, attempts_replayed=attempts))
    if next(blocks, None) is not None:
        raise ValueError('extra source block')
    for f in fixtures.values():
        for seed in config['seeds']:
            sample = cells[(f['uid'], seed, 'sample64')]
            full = cells[(f['uid'], seed, 'full3584')]
            if sample['projection']['U'] != full['projection']['U']:
                raise ValueError('arms have different unknowns')
            def equations(cell):
                output = set()
                for row in cell['rows']:
                    vector = tuple(row['coefficients']+[row['source_scalar']])
                    output.add(min(vector, tuple(-x % f['r'] for x in vector)))
                return output
            if not equations(sample) <= equations(full):
                raise ValueError('sample equation absent from exhaustive support')
            S, F = matrices[(f['uid'], seed, 'sample64')], matrices[(f['uid'], seed, 'full3584')]
            if dense_rank(F+S, f['r']) != full['projection']['rank']:
                raise ValueError('sample rowspace is not contained in census')
    if len(result['controls']) != 11 or any(c['expected'] != c['observed'] for c in result['controls']):
        raise ValueError('planted controls failed')
    return checks


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--config', required=True, type=Path)
    parser.add_argument('--run-dir', required=True, type=Path)
    args = parser.parse_args()
    start, cpu = perf_counter(), process_time()
    failed, checks = [], []
    raw = args.run_dir / 'raw-result.json'
    try:
        config = json.loads(args.config.read_text())
        panel = json.loads((ROOT/config['fixture_file']).read_text())
        result = json.loads(raw.read_text())
        if result['config_sha256'] != sha256(args.config.read_bytes()).hexdigest():
            raise ValueError('configuration commitment differs')
        with (args.run_dir/'events.jsonl').open() as stream:
            checks = check(config, panel, result, map(json.loads, stream))
    except Exception as exc:
        failed.append(repr(exc))
    verification = dict(schema='prym-rank-census-independent/v1',
        status='failed' if failed else 'passed', failed_checks=failed, cells=checks,
        raw_result_sha256=sha256(raw.read_bytes()).hexdigest(), producer_arithmetic_imported=False,
        scope='All branch statuses and accepted witnesses replayed; exact projected ranks and finite right kernels.',
        operation_counters_independently_verified=False, prescribed_execution_proof=False,
        wall_seconds=perf_counter()-start, cpu_seconds=process_time()-cpu,
        peak_rss_bytes=resource.getrusage(resource.RUSAGE_SELF).ru_maxrss*1024)
    with (args.run_dir/'verification.json').open('x') as stream:
        json.dump(verification, stream, indent=2)
        stream.write('\n')
    print(json.dumps(dict(status=verification['status'], failed_checks=failed, cells=len(checks))))
    return bool(failed)


if __name__ == '__main__':
    raise SystemExit(main())

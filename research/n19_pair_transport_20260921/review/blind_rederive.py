#!/usr/bin/env python3
"""Permanent-blind replay of N19 pair membership, transport, and paired math.

This is independent static arithmetic over frozen public inputs and raw records.
It imports no producer kernel and launches no native worker, solver, or benchmark.
"""
from __future__ import annotations

import hashlib
import io
import itertools
import json
import random
import statistics
import tarfile
import time
from collections import Counter, defaultdict
from functools import cache
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
P = ROOT / 'research/n19_pair_transport_20260921'
R = ROOT / 'experiments/EXP-KIC-7bcef8/runs/RUN-KIC-278e3e'
MOD = 524327
MASK = (1 << 19) - 1
ORDER = 262543
ARMS = ('expanded', 'canonical_poly', 'canonical_normal_x')
READS = []


def source(path):
    path = Path(path)
    READS.append(str(path.relative_to(ROOT)))
    return path.read_bytes()


def load_json(path):
    b = source(path)
    return json.loads(b), hashlib.sha256(b).hexdigest()


def load_jsonl(path):
    b = source(path)
    return [json.loads(x) for x in b.splitlines() if x], hashlib.sha256(b).hexdigest()


def sha(data):
    return hashlib.sha256(data).hexdigest()


def mul(a, b):
    out = 0
    while b:
        if b & 1:
            out ^= a
        b >>= 1
        a <<= 1
        if a & (1 << 19):
            a ^= MOD
    return out


def square(a):
    return mul(a, a)


@cache
def inv(a):
    assert a
    u, v = a, MOD
    s, t = 1, 0
    while u != 1:
        assert u
        shift = u.bit_length() - v.bit_length()
        if shift < 0:
            u, v = v, u
            s, t = t, s
            shift = -shift
        u ^= v << shift
        s ^= t << shift
    while s.bit_length() > 19:
        s ^= MOD << (s.bit_length() - 20)
    assert mul(a, s) == 1
    return s


def neg(p):
    return None if p is None else (p[0], p[0] ^ p[1])


def add(p, q):
    if p is None:
        return q
    if q is None:
        return p
    x, y = p
    u, v = q
    if x == u:
        if y != v or x == 0:
            return None
        lam = x ^ mul(y, inv(x))
        xx = square(lam) ^ lam ^ 1
        return (xx, square(x) ^ mul(lam ^ 1, xx))
    lam = mul(y ^ v, inv(x ^ u))
    xx = square(lam) ^ lam ^ x ^ u ^ 1
    return (xx, mul(lam, x ^ xx) ^ xx ^ y)


def on_curve(p):
    if p is None:
        return True
    x, y = p
    return square(y) ^ mul(x, y) == mul(square(x), x) ^ square(x) ^ 1


def multiple(p, n):
    out = None
    while n:
        if n & 1:
            out = add(out, p)
        p = add(p, p)
        n >>= 1
    return out


def frob(p, count=1):
    if p is None:
        return None
    for _ in range(count % 19):
        p = (square(p[0]), square(p[1]))
    return p


def apply_frame(p, shift, sign):
    p = frob(p, shift)
    return p if sign == 1 else neg(p)


def pack(p):
    return None if p is None else (p[0] << 19) | p[1]


def build_base(base):
    g = tuple(base['generator'])
    assert on_curve(g) and multiple(g, ORDER) is None
    assert tuple(sorted(x['point'][0] for x in base['seed_points'])) == tuple(base['plane_key'])
    a, b, c = base['affine_coordinates']
    assert tuple(sorted((a, a ^ b, a ^ c, a ^ b ^ c))) == tuple(base['plane_key'])
    seeds = [tuple(x['point']) for x in base['seed_points']]
    all_points = set()
    orbits = []
    for seed in seeds:
        assert on_curve(seed) and multiple(seed, ORDER) is None
        orbit = []
        seen = set()
        q = seed
        for _ in range(19):
            for p in (q, neg(q)):
                assert p not in seen and p not in all_points
                assert on_curve(p) and multiple(p, ORDER) is None
                orbit.append(p)
                seen.add(p)
                all_points.add(p)
            q = frob(q)
        assert q == seed and len(orbit) == 38
        orbits.append(orbit)
    assert len(all_points) == 152 and len({p[0] for p in all_points}) == 76
    return g, seeds, orbits, sorted(all_points)


def gf2_rank(columns):
    pivots = {}
    for value in columns:
        while value:
            pivot = value.bit_length() - 1
            if pivot not in pivots:
                pivots[pivot] = value
                break
            value ^= pivots[pivot]
    return len(pivots)


def normal_basis():
    for beta in range(1, 1 << 19):
        cols = []
        q = beta
        for _ in range(19):
            cols.append(q)
            q = square(q)
        if gf2_rank(cols) == 19:
            return beta, cols
    raise AssertionError('no normal basis')


def linear_solver(columns):
    pivots = {}
    for i, col in enumerate(columns):
        value, mask = col, 1 << i
        while value:
            pivot = value.bit_length() - 1
            if pivot in pivots:
                v, m = pivots[pivot]
                value ^= v
                mask ^= m
            else:
                pivots[pivot] = (value, mask)
                break
    assert len(pivots) == 19
    def solve(value):
        mask = 0
        while value:
            pivot = value.bit_length() - 1
            v, m = pivots[pivot]
            value ^= v
            mask ^= m
        return mask
    return solve


def rotl19(x, j):
    j %= 19
    return ((x << j) & MASK) | (x >> (19 - j) if j else 0)


def canonical_poly(p):
    if p is None:
        return ('infinity', None, 0, 1)
    choices = []
    q = p
    for j in range(19):
        choices.append((pack(q), j, 1, q))
        choices.append((pack(neg(q)), j, -1, neg(q)))
        q = frob(q)
    value, j, sign, canonical = min(choices, key=lambda x: (x[0], x[1], 0 if x[2] == 1 else 1))
    return ('full_point', value, j, sign, canonical)


def canonical_normal(p, to_normal):
    if p is None:
        return ('infinity', None, 0)
    normal = to_normal(p[0])
    choices = [(rotl19(normal, j), j) for j in range(19)]
    value, j = min(choices)
    return ('normal_x', value, j)


def pair_set(points):
    witnesses = {}
    for i, p in enumerate(points):
        for q in points[i:]:
            s = add(p, q)
            pair = tuple(sorted((p, q)))
            if s not in witnesses or pair < witnesses[s]:
                witnesses[s] = pair
    assert len(witnesses) == 11097
    return witnesses


def archive_verified(path, manifest):
    data = source(path)
    assert sha(data) == manifest['archive_sha256']
    raw = {}
    with tarfile.open(fileobj=io.BytesIO(data), mode='r:gz') as tf:
        for member in tf.getmembers():
            assert member.isfile() and member.name not in raw
            raw[member.name] = tf.extractfile(member).read()
    expected = {x['path']: x for x in manifest['files']}
    assert set(raw) == set(expected)
    for name, value in raw.items():
        row = expected[name]
        assert len(value) == row['bytes'] and sha(value) == row['sha256'], name
    return raw, sha(data)


def validate_table_rows(tables, seeds, points, pairs, to_normal):
    point_set = set(points)
    by_arm = {x['arm']: x for x in tables['arms']}
    assert set(by_arm) == set(ARMS)
    expected = {'expanded': 11097, 'canonical_poly': 293, 'canonical_normal_x': 293}
    indexed = {}
    table_checks = Counter()
    for arm in ARMS:
        block = by_arm[arm]
        assert block['stats']['keys'] == block['stats']['rows'] == expected[arm]
        assert len(block['rows']) == expected[arm]
        rows = {}
        for row in block['rows']:
            kind, value = row['key']['kind'], row['key']['value']
            key = (kind, value)
            assert key not in rows
            rows[key] = row
            endpoints = tuple(tuple(p) for p in row['normalized_endpoints'])
            assert len(endpoints) == 2 and all(p in point_set for p in endpoints)
            stored = None if row['stored_sum'] is None else tuple(row['stored_sum'])
            assert add(*endpoints) == stored
            anchor = row['anchor']
            frame = row['source_frame']
            if arm == 'expanded':
                assert anchor == [-1, -1, -1, 0] and frame == [0, 1]
                assert key == (('infinity', None) if stored is None else ('full_point', pack(stored)))
            else:
                i, k, shift, sign = anchor
                assert 0 <= i <= k < 4 and 0 <= shift < 19 and sign in (-1, 1)
                original = (seeds[i], apply_frame(seeds[k], shift, sign))
                original_sum = add(*original)
                fj, fsign = frame
                assert 0 <= fj < 19 and fsign in (-1, 1)
                mapped = tuple(sorted(apply_frame(p, fj, fsign) for p in original))
                assert mapped == tuple(sorted(endpoints))
                assert apply_frame(original_sum, fj, fsign) == stored
                if arm == 'canonical_poly':
                    ck = canonical_poly(original_sum)
                    assert key == (ck[0], ck[1]) and (fj, fsign) == (ck[2], ck[3])
                else:
                    ck = canonical_normal(original_sum, to_normal)
                    assert key == (ck[0], ck[1]) and fj == ck[2] and fsign == 1
                    if stored is not None:
                        assert to_normal(stored[0]) == value
            table_checks[arm] += 1
        indexed[arm] = rows
    # Every full pair sum must be found and inverse-transport to a valid pair.
    transport = Counter()
    for s in pairs:
        full_key = ('infinity', None) if s is None else ('full_point', pack(s))
        assert full_key in indexed['expanded']
        cp = canonical_poly(s)
        row = indexed['canonical_poly'][(cp[0], cp[1])]
        endpoints = tuple(tuple(p) for p in row['normalized_endpoints'])
        recovered = tuple(sorted(apply_frame(p, (19 - cp[2]) % 19, cp[3]) for p in endpoints))
        assert all(p in point_set for p in recovered) and add(*recovered) == s
        cn = canonical_normal(s, to_normal)
        row = indexed['canonical_normal_x'][(cn[0], cn[1])]
        endpoints = tuple(tuple(p) for p in row['normalized_endpoints'])
        stored = None if row['stored_sum'] is None else tuple(row['stored_sum'])
        rprime = frob(s, cn[2])
        sign = 1 if rprime == stored else -1
        assert apply_frame(rprime, 0, sign) == stored
        recovered = tuple(sorted(apply_frame(p, (19 - cn[2]) % 19, sign) for p in endpoints))
        assert all(p in point_set for p in recovered) and add(*recovered) == s
        transport['canonical_poly'] += 1
        transport['canonical_normal_x'] += 1
    return indexed, dict(table_checks), dict(transport)


def generate_universe(pool, g):
    powers = []
    q = g
    for _ in range(ORDER.bit_length()):
        powers.append(q)
        q = add(q, q)
    def fixed(k):
        out = None
        bit = 0
        while k:
            if k & 1:
                out = add(out, powers[bit])
            k >>= 1
            bit += 1
        return out
    universe = [None]
    seen = {None}
    reps = []
    for scalar in pool['public_target_scalar_representatives']:
        q = fixed(scalar)
        assert q is not None and on_curve(q) and multiple(q, ORDER) is None
        reps.append(q)
        for _ in range(19):
            for p in (q, neg(q)):
                assert p not in seen
                seen.add(p)
                universe.append(p)
            q = frob(q)
    assert len(universe) == len(seen) == ORDER
    return universe, reps


def membership_bytes(universe, members):
    out = bytearray((len(universe) + 7) // 8)
    for i, p in enumerate(universe):
        if p in members:
            out[i // 8] |= 1 << (i % 8)
    return bytes(out)


def parse_membership(data):
    import struct
    assert data[:8] == b'KIC19PT1'
    version, points, arms, each = struct.unpack('<4I', data[8:24])
    assert (version, points, arms, each) == (1, ORDER, 3, 32818)
    assert len(data) == 24 + arms * each
    payload = [data[24+i*each:24+(i+1)*each] for i in range(arms)]
    assert all(x[-1] & 0b11111110 == 0 for x in payload)
    return payload


def query_oracle(q, points, pairs):
    for i, p in enumerate(points):
        if add(q, neg(p)) in pairs:
            return 'SAT', i
    return 'UNSAT', -1


def validate_query_record(row, q, points, pairs):
    expected, third = query_oracle(q, points, pairs)
    assert (None if row['Q'] is None else tuple(row['Q'])) == q
    for arm in ARMS:
        result = row['arms'][arm]
        assert result['status'] == expected and result['third_index'] == third
        assert result['probes'] == (third + 1 if third >= 0 else len(points))
        if arm == 'expanded':
            assert result['canonicalizations'] == 0
        else:
            assert result['canonicalizations'] == result['probes']
        witness = result['witness']
        if expected == 'SAT':
            w = tuple(tuple(p) for p in witness)
            assert len(w) == 3 and all(p in set(points) for p in w)
            assert add(add(w[0], w[1]), w[2]) == q
            assert w[2] == points[third]
        else:
            assert witness is None and result['transport_rows_examined'] == 0
    return expected


def type7(values, p):
    values = sorted(values)
    z = (len(values) - 1) * p
    i = int(z)
    f = z - i
    return values[i] * (1-f) + values[min(i+1, len(values)-1)] * f


def bootstrap(ratios, case_map):
    sat = [i for i in sorted(ratios) if case_map[i]['stratum'] == 'SAT']
    unsat = [i for i in sorted(ratios) if case_map[i]['stratum'] == 'UNSAT']
    assert len(sat) == len(unsat) == 4
    rng = random.Random('N19-PAIR-TRANSPORT-v1-bootstrap')
    medians = []
    for _ in range(10000):
        chosen = [sat[rng.randrange(4)] for _ in range(4)] + [unsat[rng.randrange(4)] for _ in range(4)]
        medians.append(statistics.median(ratios[i] for i in chosen))
    return [type7(medians, .025), type7(medians, .975)]


def main():
    started = time.perf_counter()
    protocol, protocol_sha = load_json(P/'protocol.json')
    base, base_sha = load_json(P/'inputs/base.json')
    cases, cases_sha = load_json(P/'inputs/cases.json')
    pool, pool_sha = load_json(P/'inputs/pool.json')
    schedule, schedule_sha = load_json(P/'inputs/schedule.json')
    assert protocol['inputs']['base_sha256'] == base_sha
    assert protocol['inputs']['cases_sha256'] == cases_sha
    assert protocol['inputs']['pool_sha256'] == pool_sha
    assert protocol['inputs']['schedule_sha256'] == schedule_sha
    base_manifest, _ = load_json(R/'base_manifest.json')
    case_manifest, _ = load_json(R/'case_manifest.json')
    native_controls, _ = load_json(R/'native_controls.json')
    tables, tables_sha = load_json(R/'control_tables.json')
    queries, queries_sha = load_json(R/'control_queries.json')
    membership_hashes, _ = load_json(R/'membership_hashes.json')
    membership_data = source(R/'control_membership.bin')
    control_receipt, _ = load_json(R/'control_receipt.json')
    checker_receipt, _ = load_json(R/'checker_receipt.json')
    receipts, receipts_sha = load_jsonl(R/'benchmark_receipts.jsonl')
    raw_manifest, _ = load_json(R/'raw_manifest.json')
    raw, raw_archive_sha = archive_verified(R/'raw_outputs.tar.gz', raw_manifest)
    assert base_manifest['input_sha256'] == base_sha
    assert case_manifest['cases'] == cases['cases']
    assert case_manifest['blocks'] == schedule['blocks']
    assert case_manifest['workers'] == schedule['workers']
    assert native_controls['status'] == 'passed'
    assert control_receipt['classification'] == 'completed_valid' and control_receipt['valid']
    assert checker_receipt['classification'] == 'completed_valid' and checker_receipt['valid']
    assert not control_receipt['watchdog_reached'] and not checker_receipt['watchdog_reached']
    assert control_receipt['outputs']['control_tables.json'] == tables_sha
    assert control_receipt['outputs']['control_queries.json'] == queries_sha
    g, seeds, orbits, points = build_base(base)
    assert points == sorted(points)
    beta, columns = normal_basis()
    assert beta == native_controls['normal_beta'] == 3
    assert columns == native_controls['normal_columns']
    to_normal = linear_solver(columns)
    # Conversion and Frobenius direction over the full field.
    for x in range(1 << 19):
        coords = to_normal(x)
        rebuilt = 0
        for j, col in enumerate(columns):
            if coords >> j & 1:
                rebuilt ^= col
        assert rebuilt == x
        assert to_normal(square(x)) == rotl19(coords, 1)
    pairs = pair_set(points)
    indexed, table_checks, transport_checks = validate_table_rows(tables, seeds, points, pairs, to_normal)
    universe, public_reps = generate_universe(pool, g)
    expected_bits = membership_bytes(universe, set(pairs))
    payloads = parse_membership(membership_data)
    for arm, payload in zip(ARMS, payloads):
        assert payload == expected_bits
        assert sha(payload) == membership_hashes[f'{arm}_sha256']
    assert membership_hashes['universe_points'] == len(universe)
    assert sum(x.bit_count() for x in expected_bits) == len(pairs) == 11097
    assert len(queries['targets']) == 6909 and len(queries['exceptions']) == 153
    target_counts = Counter()
    for i, (row, q) in enumerate(zip(queries['targets'], public_reps)):
        assert row['target_index'] == i
        target_counts[validate_query_record(row, q, points, pairs)] += 1
    assert target_counts == {'SAT': 6189, 'UNSAT': 720}
    assert queries['exceptions'][0]['kind'] == 'infinity'
    exception_points = [None] + points
    exception_counts = Counter()
    for i, (row, q) in enumerate(zip(queries['exceptions'], exception_points)):
        assert row['index'] == i
        exception_counts[validate_query_record(row, q, points, pairs)] += 1
    assert exception_counts == {'SAT': 152, 'UNSAT': 1}
    # Frozen eight-case oracles.
    case_map = {x['case_id']: x for x in cases['cases']}
    for case in case_map.values():
        assert tuple(case['Q']) == public_reps[pool['public_target_scalar_representatives'].index(case['public_scalar'])]
        expected, _ = query_oracle(tuple(case['Q']), points, pairs)
        assert expected == case['stratum']
    assert len(receipts) == 144 and len(schedule['workers']) == 144
    measurements = defaultdict(lambda: defaultdict(list))
    worker_rows = []
    for receipt, planned in zip(receipts, schedule['workers']):
        for key in ('ordinal', 'block', 'case_id', 'replicate', 'arm', 'Q', 'stratum'):
            assert receipt[key] == planned[key]
        assert receipt['classification'] == 'completed_valid' and receipt['valid']
        assert receipt['exit_code'] == 0 and receipt['error'] is None and receipt['popen_error'] is None
        assert receipt['telemetry_valid'] and not receipt['watchdog_reached'] and not receipt['memory_cap_reached']
        assert receipt['wait4']['rss_unit'] == 'bytes' and receipt['wait4']['peak_rss'] > 0
        assert receipt['wait4']['user_seconds'] >= 0 and receipt['wait4']['system_seconds'] >= 0
        assert receipt['wall_seconds'] > 0
        root = f"raw/benchmark/{receipt['ordinal']:03d}_{receipt['case_id']}_{receipt['replicate']}_{receipt['arm']}"
        assert sha(raw[f'{root}/result.json']) == receipt['result_sha256']
        assert sha(raw[f'{root}/result.json.timing.json']) == receipt['output_timing_sha256']
        assert sha(raw[f'{root}/stdout.log']) == receipt['stdout_sha256']
        assert sha(raw[f'{root}/stderr.log']) == receipt['stderr_sha256']
        result = json.loads(raw[f'{root}/result.json'])
        timing = json.loads(raw[f'{root}/result.json.timing.json'])
        assert result == receipt['result'] and timing == receipt['output_timing']
        assert result['arm'] == receipt['arm'] and result['Q'] == receipt['Q']
        assert result['status'] == result['result']['status'] == receipt['stratum']
        expected, third = query_oracle(tuple(receipt['Q']), points, pairs)
        assert expected == receipt['stratum'] and result['result']['third_index'] == third
        assert result['result']['probes'] == (third + 1 if third >= 0 else 152)
        if receipt['arm'] == 'expanded':
            assert result['table']['keys'] == 11097 and result['result']['canonicalizations'] == 0
        else:
            assert result['table']['keys'] == 293
            assert result['result']['canonicalizations'] == result['result']['probes']
        witness = result['result']['witness']
        if expected == 'SAT':
            w = tuple(tuple(p) for p in witness)
            assert len(w) == 3 and all(p in set(points) for p in w)
            assert w[2] == points[third] and add(add(w[0], w[1]), w[2]) == tuple(receipt['Q'])
        else:
            assert witness is None
        measurements[receipt['case_id']][receipt['arm']].append(receipt['wall_seconds'])
        worker_rows.append({'ordinal':receipt['ordinal'],'case_id':receipt['case_id'],
                            'replicate':receipt['replicate'],'arm':receipt['arm'],
                            'stratum':receipt['stratum'],'status':expected,
                            'wall_seconds':receipt['wall_seconds'],
                            'user_seconds':receipt['wait4']['user_seconds'],
                            'system_seconds':receipt['wait4']['system_seconds'],
                            'peak_rss_bytes':receipt['wait4']['peak_rss']})
    assert set(measurements) == set(range(1, 9))
    medians = {}
    for case_id in sorted(measurements):
        medians[case_id] = {}
        for arm in ARMS:
            values = measurements[case_id][arm]
            assert len(values) == 6
            medians[case_id][arm] = statistics.median(values)
    eligible = (all(x['classification'] == 'completed_valid' and x['valid'] for x in receipts)
                and control_receipt['valid'] and checker_receipt['valid'])
    assert eligible
    ratio_defs = {
        'canonical_normal_x_over_expanded': ('canonical_normal_x', 'expanded'),
        'canonical_poly_over_expanded': ('canonical_poly', 'expanded'),
        'canonical_normal_x_over_canonical_poly': ('canonical_normal_x', 'canonical_poly'),
    }
    ratios = {}
    for name, (num, den) in ratio_defs.items():
        per_case = {i: medians[i][num] / medians[i][den] for i in sorted(medians)}
        ratios[name] = {'per_case':per_case,
                        'median':statistics.median(per_case.values()),
                        'SAT_median':statistics.median(v for i,v in per_case.items() if case_map[i]['stratum']=='SAT'),
                        'UNSAT_median':statistics.median(v for i,v in per_case.items() if case_map[i]['stratum']=='UNSAT'),
                        'stratified_bootstrap_type7_95':bootstrap(per_case, case_map)}
    output = {
        'schema':'crypto.autoresearch.n19_pair_transport_blind_replay.v1',
        'task_id':'TASK-20260921-c6dbe6',
        'input_sha256':{'protocol':protocol_sha,'base':base_sha,'cases':cases_sha,
                        'pool':pool_sha,'schedule':schedule_sha},
        'raw_archive_sha256':raw_archive_sha,'raw_files_verified':len(raw),
        'benchmark_receipts_sha256':receipts_sha,
        'base':{'points':len(points),'x_values':len({p[0] for p in points}),
                'expanded_pair_sum_members':len(pairs),'normal_beta':beta,
                'normal_columns':columns},
        'tables':{'row_checks':table_checks,'inverse_transport_checks':transport_checks},
        'membership':{'universe_points':len(universe),'members':len(pairs),
                      'bitvector_sha256':sha(expected_bits),'all_three_exact_match':True},
        'control_queries':{'targets':len(public_reps),'SAT':target_counts['SAT'],'UNSAT':target_counts['UNSAT'],
                           'exceptions':len(exception_points),'exception_SAT':exception_counts['SAT'],
                           'exception_UNSAT':exception_counts['UNSAT']},
        'benchmark':{'planned_workers':144,'complete_valid_workers':len(receipts),
                     'technical_repeats_per_case_arm':6,'independent_cases':8,
                     'case_arm_wall_medians':medians,'ratios':ratios,
                     'eligible':eligible,'workers':worker_rows,
                     'total_wall_seconds_across_serial_workers':sum(x['wall_seconds'] for x in receipts)},
        'own_static_replay_elapsed_seconds':time.perf_counter()-started,
        'sources_read':READS,
    }
    out = P/'review/blind_results.json'
    out.write_text(json.dumps(output,indent=2,sort_keys=True)+'\n')
    print(json.dumps({'planes_pair_members':len(pairs),'targets':dict(target_counts),
                      'workers':len(receipts),'primary':ratios['canonical_normal_x_over_expanded']}))


if __name__ == '__main__':
    main()

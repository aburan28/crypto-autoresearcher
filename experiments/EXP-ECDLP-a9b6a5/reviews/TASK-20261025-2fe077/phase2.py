"""Independent finite-stream audit using only sealed reviewer arithmetic.

Injected ``g`` is the logged, immutable phase-one reviewer namespace. No
producer/checker module is imported or executed, including target construction.
"""
import copy
import gzip
import hashlib
import itertools
import json
import os
import resource
import time
from collections import Counter
from pathlib import Path

BASE = 'experiments/EXP-ECDLP-a9b6a5'
OUT = BASE + '/reviews/TASK-20261025-2fe077'
ROOT = Path('/workspace/crypto-autoresearcher')
LOCATOR = 'explicit interpolation and residual quadratic; no post-hoc kernel'


def check(test, reason):
    if not test:
        raise ValueError(reason)


def text_bytes(value):
    return json.dumps(value, sort_keys=True, separators=(',', ':')).encode()


def digest(value):
    return hashlib.sha256(text_bytes(value)).hexdigest()


def save(name, value):
    path = ROOT / OUT / name
    path.parent.mkdir(parents=True, exist_ok=True)
    body = (json.dumps(value, indent=2) + '\n').encode()
    with path.open('xb') as stream:
        stream.write(body)
    return {'path': str(path.relative_to(ROOT)), 'sha256': hashlib.sha256(body).hexdigest(), 'bytes': len(body)}


def elimination(rows, modulus, columns=None):
    m = [[x % modulus for x in row] for row in rows]
    if not m:
        return [], []
    columns = len(m[0]) if columns is None else columns
    pivots, i = [], 0
    for col in range(columns):
        candidate = next((j for j in range(i, len(m)) if m[j][col]), None)
        if candidate is None:
            continue
        m[i], m[candidate] = m[candidate], m[i]
        z = pow(m[i][col], -1, modulus)
        m[i] = [(v * z) % modulus for v in m[i]]
        for j in range(len(m)):
            if j != i and m[j][col]:
                z = m[j][col]
                m[j] = [(a - z * b) % modulus for a, b in zip(m[j], m[i])]
        pivots.append(col)
        i += 1
        if i == len(m):
            break
    return pivots, m[:i]


def rank(rows, r):
    return len(elimination(rows, r)[0])


class Replay:
    def __init__(self, fixture, arithmetic):
        self.f = fixture
        self.g = arithmetic
        self.p, self.a, self.b, self.r = (fixture[k] for k in ('p', 'a', 'b', 'r'))
        self.ec = arithmetic['EC'](self.p, self.a, self.b)
        self.P = tuple(fixture['P'])
        self.base = [tuple(v['point']) for v in fixture['factor_base']]
        self.lifts = [tuple(v['lift']) for v in fixture['factor_base']]
        self.by_x = {v[0]: j for j, v in enumerate(self.base)}
        self.sources = {}
        self.interpolation_plans = {}
        self.seen = set()
        self.f_poly = [self.b, 0, self.a, 0, 0, 0, 1]

    def source(self, scalar):
        if scalar not in self.sources:
            S = self.ec.neg(self.ec.mul(scalar, self.P))
            x = None if S is None else self.g['square_root'](S[0], self.p)
            self.sources[scalar] = None if x in (None, 0) else (x, S[1])
        return self.sources[scalar]

    def descriptor(self, scalar, triple, options):
        source = self.source(scalar)
        if source is None:
            return None, 'S'
        points = [source]
        for j, op in zip(triple, options):
            x, y = self.lifts[j]
            points.append(((-x if op & 2 else x) % self.p,
                           (-y if op & 1 else y) % self.p))
        if any(x == 0 for x, y in points) or len({x for x, y in points}) < 4:
            return None, 'D'
        return points, None

    def identity(self, scalar, triple, options, points):
        # The lexicographically first signed label determines global y sign;
        # then that label's x string determines global deck. This is derived
        # directly from the declared JSON key ordering, without a producer ID.
        p = self.p
        h = 1 if options[0] & 1 else -1
        first_x = points[1][0]
        d = 1 if str(first_x) < str(-first_x % p) else -1
        changed = [(d*x % p, h*y % p) for x, y in points]
        labels = [[j, h*(-1 if op & 1 else 1), x, y]
                  for j, op, (x, y) in zip(triple, options, changed[1:])]
        value = {'curve_uid': self.f['uid'], 'source_scalar': h*scalar % self.r,
                 'lambda': 1, 'signed_fb_lift_ids': {'source_lift': changed[0], 'base_lifts': labels}}
        return digest(value)

    def identity_four_way(self, scalar, triple, options, points):
        encodings = []
        for d in (1, -1):
            for h in (1, -1):
                changed = [(d*x % self.p, h*y % self.p) for x, y in points]
                labels = [[j, h*(-1 if op & 1 else 1), x, y]
                          for j, op, (x, y) in zip(triple, options, changed[1:])]
                value = {'curve_uid': self.f['uid'], 'source_scalar': h*scalar % self.r,
                         'lambda': 1, 'signed_fb_lift_ids': {'source_lift': changed[0], 'base_lifts': labels}}
                encodings.append(text_bytes(value))
        return hashlib.sha256(min(encodings)).hexdigest()

    def cubic(self, points):
        p = self.p
        xs = tuple(x for x, y in points)
        if xs not in self.interpolation_plans:
            basis = []
            for i, x in enumerate(xs):
                poly, denom = [1], 1
                for j, y in enumerate(xs):
                    if i != j:
                        poly = self.g['poly_mul'](poly, [-y, 1], p)
                        denom = denom * (x-y) % p
                scale = pow(denom, -1, p)
                basis.append([v*scale % p for v in poly])
            self.interpolation_plans[xs] = basis
        return self.g['trim']([sum(y*self.interpolation_plans[xs][i][j]
                                  for i, (x, y) in enumerate(points)) % p
                               for j in range(4)], p)

    def outcome(self, scalar, triple, options):
        points, status = self.descriptor(scalar, triple, options)
        if status:
            return status, None, None
        ident = self.identity(scalar, triple, options, points)
        if ident in self.seen:
            return 'A', ident, None
        self.seen.add(ident)
        p, g = self.p, self.g
        v = self.cubic(points)
        if len(v) == 4 and v[3]*v[3] % p == 1:
            return 'P', ident, None
        vv = g['poly_mul'](v, v, p)
        intersection = g['poly_add'](vv, [-x for x in self.f_poly], p)
        divisor = [1]
        for x, y in points:
            divisor = g['poly_mul'](divisor, [-x, 1], p)
        residual, remainder = g['poly_div'](intersection, divisor, p)
        check(remainder == [0], 'fresh interpolation remainder nonzero')
        if len(residual) != 3 or not residual[2]:
            return 'R', ident, None
        c, b, a = residual
        delta = (b*b-4*a*c) % p
        sqrt = g['square_root'](delta, p)
        if not delta or sqrt is None:
            return 'R', ident, None
        inv = pow(2*a, -1, p)
        roots = sorted({(-b-sqrt)*inv % p, (-b+sqrt)*inv % p})
        if len(roots) != 2 or set(roots) & {x for x, y in points}:
            return 'X', ident, None
        coefficients = [0]*len(self.base)
        for j, op in zip(triple, options):
            coefficients[j] += -1 if op & 1 else 1
        for x in roots:
            y = g['poly_eval'](v, x, p)
            j = self.by_x.get(x*x % p)
            if j is None:
                return 'B', ident, None
            check(y in (self.base[j][1], -self.base[j][1] % p), 'residual orientation off base')
            coefficients[j] += 1 if y == self.base[j][1] else -1
        row = {'schema': 'prym-principal-row/v1', 'curve_uid': self.f['uid'],
               'source_scalar': scalar, 'coefficients': [c % self.r for c in coefficients],
               'constraints': [list(v) for v in points],
               'base_labels': [[j, -1 if op & 1 else 1, op] for j, op in zip(triple, options)],
               'v_coefficients': v, 'residual_coefficients': residual, 'residual_roots': roots,
               'pole_orders_at_infinity': [3, 3], 'source_locator': LOCATOR}
        return '+', ident, row


def verify_row(f, row, g, principal=True):
    p, a, b, r = (f[k] for k in ('p', 'a', 'b', 'r'))
    ec = g['EC'](p, a, b)
    check(row['schema'] == 'prym-principal-row/v1' and row['curve_uid'] == f['uid'], 'wrong row identity')
    check(row['source_locator'] == LOCATOR and row['pole_orders_at_infinity'] == [3, 3], 'wrong locator/poles')
    scalar = row['source_scalar']
    check(type(scalar) is int and 0 <= scalar < r, 'source scalar out of range')
    check(len(row['coefficients']) == len(f['factor_base']), 'wrong coefficient width')
    expected = ec.mul(scalar, tuple(f['P']))
    total = None
    for c, atom in zip(row['coefficients'], f['factor_base']):
        check(type(c) is int and 0 <= c < r, 'noncanonical row coefficient')
        total = ec.add(total, ec.mul(c, tuple(atom['point'])))
    check(total == expected, 'E1 source equation fails')
    if not principal:
        return True
    points = [tuple(v) for v in row['constraints']]
    check(len(points) == 4 and len({x for x, y in points}) == 4, 'wrong interpolation support')
    check((points[0][0]**2 % p, points[0][1]) == ec.neg(expected), 'false lifted source')
    v = g['interpolate'](points, p)
    check(v == row['v_coefficients'], 'cubic independently differs')
    check(len(v) <= 4 and (len(v) != 4 or v[3]*v[3] % p != 1), 'exceptional pole order')
    labels = row['base_labels']
    check(len(labels) == 3, 'wrong base label arity')
    coefficients = [0]*len(f['factor_base'])
    for actual, (j, sign, option) in zip(points[1:], labels):
        check(0 <= j < len(coefficients) and option in range(4), 'base option out of range')
        check(sign == (-1 if option & 1 else 1), 'wrong hyperelliptic bit')
        x, y = f['factor_base'][j]['lift']
        check(actual == ((-x if option & 2 else x) % p, sign*y % p), 'false base lift')
        coefficients[j] += sign
    divisor = [1]
    for x, y in points:
        divisor = g['poly_mul'](divisor, [-x, 1], p)
    intersection = g['poly_add'](g['poly_mul'](v, v, p), [-b, 0, -a, 0, 0, 0, -1], p)
    residual = row['residual_coefficients']
    check(len(residual) == 3 and residual[-1], 'nonquadratic residual')
    check(g['poly_mul'](divisor, residual, p) == intersection, 'principal polynomial identity fails')
    roots = row['residual_roots']
    check(len(roots) == 2 and roots == sorted(set(roots)), 'bad residual roots/order')
    check(len(set(roots + [x for x, y in points])) == 6, 'intersection not squarefree')
    for x in roots:
        check(g['poly_eval'](residual, x, p) == 0, 'wrong residual root')
        y = g['poly_eval'](v, x, p)
        matches = [(j, s) for j, atom in enumerate(f['factor_base']) for s in (1, -1)
                   if atom['point'][0] == x*x % p and s*atom['point'][1] % p == y]
        check(len(matches) == 1, 'residual endpoint outside distinct signed base')
        j, s = matches[0]
        coefficients[j] += s
        points.append((x, y))
    check([c % r for c in coefficients] == row['coefficients'], 'wrong witness coefficients')
    inv3 = pow(3, -1, p)
    e2 = g['EC'](p, -a*a*inv3 % p, (b*b+2*a**3*pow(27, -1, p)) % p)
    S1 = S2 = None
    for x, y in points:
        check((y*y-x**6-a*x*x-b) % p == 0, 'intersection off native curve')
        S1 = ec.add(S1, (x*x % p, y))
        if x:
            u, z = pow(x*x % p, -1, p), y*pow(pow(x, 3, p), -1, p) % p
            Q = ((b*u+a*inv3) % p, b*z % p)
            check(e2.on(Q), 'pi2 image off quotient')
            S2 = e2.add(S2, Q)
    check(S1 is None and S2 is None, 'principal quotient sum does not cancel')
    return True


def public_projection(f, sources, g):
    p, r = f['p'], f['r']
    ec = g['EC'](p, f['a'], f['b'])
    public = {}
    for k in sources:
        S = ec.mul(k, tuple(f['P']))
        for sign in (1, -1):
            public[S if sign == 1 else ec.neg(S)] = sign*k % r
    unknown = sorted({(u, min(v, -v % p)) for u, v in [a['point'] for a in f['factor_base']]
                      if (u, v) not in public})
    mapping = []
    for atom in f['factor_base']:
        Q = tuple(atom['point'])
        canonical = (Q[0], min(Q[1], -Q[1] % p))
        mapping.append(['known', public[Q]] if Q in public else
                       ['unknown', unknown.index(canonical), 1 if Q == canonical else -1])
    return {'U': len(unknown), 'unknown_points': [list(q) for q in unknown], 'native_to_projected': mapping}


def project_equation(row, projection, r):
    vector = [0]*projection['U']
    rhs = row['source_scalar'] % r
    for c, item in zip(row['coefficients'], projection['native_to_projected']):
        if item[0] == 'known':
            rhs -= c*item[1]
        elif item[0] == 'unknown':
            vector[item[1]] += c*item[2]
    return [v % r for v in vector], rhs % r


def certificate(f, cell, g, projection=None):
    projection = public_projection(f, cell['source_order'], g) if projection is None else projection
    actual = cell['projection']
    for key, value in projection.items():
        check(actual[key] == value, 'false public projection '+key)
    U, r = projection['U'], f['r']
    M, rhs = [], []
    independent, previous = [], 0
    for i, row in enumerate(cell['rows']):
        v, b = project_equation(row, projection, r)
        M.append(v)
        rhs.append(b)
        current = rank(M, r)
        if current > previous:
            independent.append(i)
            previous = current
    augmented = [v+[b] for v, b in zip(M, rhs)]
    R, AR = rank(M, r), rank(augmented, r)
    check(actual['projected_rows'] == M and actual['rhs'] == rhs, 'false projected matrix/RHS')
    check((actual['rank'], actual['augmented_rank'], actual['nullity'], actual['consistent']) ==
          (R, AR, U-R, R == AR), 'false matrix rank/consistency')
    check(actual['independent_row_indices'] == independent, 'false first-independent-row certificate')
    pivots = {int(k): v for k, v in actual['pivots'].items()}
    check(len(pivots) == R, 'false pivot count')
    for pivot, row in pivots.items():
        check(0 <= pivot < U and len(row) == U+1 and row[pivot] == 1 and not any(row[:pivot]), 'malformed pivot')
    check(rank(augmented+list(pivots.values()), r) == AR, 'pivot outside row span')
    kernel = actual['right_kernel']
    check(len(kernel) == U-R and all(len(v) == U for v in kernel) and rank(kernel, r) == U-R, 'wrong kernel dimension')
    check(all(type(x) is int and 0 <= x < r for v in kernel for x in v), 'noncanonical kernel')
    check(not any(sum(x*y for x, y in zip(row, v)) % r for row in M for v in kernel), 'kernel vector fails equation')
    if R < U or AR != R:
        check(actual['solution'] is None, 'solution asserted without consistent full rank')
    else:
        check(len(actual['solution']) == U and all(sum(x*y for x, y in zip(row, actual['solution'])) % r == b
                                                 for row, b in zip(M, rhs)), 'wrong full-rank solution')
    check(actual['all_columns_publicly_known'] == (U == 0), 'wrong public-calibration flag')
    for item in actual['public_derivations']:
        k = item['public_source']
        check(k in cell['source_order'] and item['scalar'] == item['sign']*k % r, 'false public-anchor derivation')
        ec = g['EC'](f['p'], f['a'], f['b'])
        check(ec.mul(item['scalar'], tuple(f['P'])) == tuple(item['point']), 'false public-anchor point')
    return {'U': U, 'rank': R, 'augmented_rank': AR, 'nullity': U-R,
            'M': M, 'rhs': rhs, 'independent_row_indices': independent,
            'right_kernel': kernel, 'projection': projection}


def transport(f, row):
    other, witness = copy.deepcopy(f), copy.deepcopy(row)
    n, p, r = len(f['factor_base']), f['p'], f['r']
    other['factor_base'] = []
    for old in reversed(range(n)):
        atom = f['factor_base'][old]
        s, d = (-1 if old % 2 else 1), (-1 if old % 3 else 1)
        other['factor_base'].append({'point': [atom['point'][0], s*atom['point'][1] % p],
                                     'lift': [d*atom['lift'][0] % p, s*atom['lift'][1] % p]})
    witness['coefficients'] = [(-1 if j % 2 else 1)*row['coefficients'][j] % r for j in reversed(range(n))]
    witness['base_labels'] = []
    for j, sign, option in row['base_labels']:
        sign *= -1 if j % 2 else 1
        deck = (-1 if option & 2 else 1)*(-1 if j % 3 else 1)
        witness['base_labels'].append([n-1-j, sign, int(sign < 0)+2*int(deck < 0)])
    return other, witness


def block_identity(block, f, scalar, width):
    check((block['schema'], block['curve_uid'], block['seed'], block['arm'], block['scalar']) ==
          ('prym-width-source-block/v1', f['uid'], 0, 'm16_full35840', scalar), 'wrong source block order/identity')
    check(len(block['statuses']) == 64*len(list(itertools.combinations(range(width), 3))), 'dropped/duplicate status')


def replay_cell(f, cell, records, g):
    start = time.monotonic()
    replay = Replay(f, g)
    sources = f['width_binding']['source_order']
    check(cell['source_order'] == sources and cell['seed'] == 0 and cell['arm'] == 'm16_full35840', 'changed source schedule')
    check(cell['curve_uid'] == f['uid'] and cell['ec1_curve_uid'] == f['ec1']['curve_uid'], 'changed cell curve identity')
    records = iter(records)
    triples = list(itertools.combinations(range(len(f['factor_base'])), 3))
    counts, attempts, row_index, digest_bytes = Counter(), 0, 0, 0
    checks, progress, M, previous, first = [], [], [], 0, None
    projection = public_projection(f, sources, g)
    identity_calibrations = 0
    for source_index, scalar in enumerate(sources):
        replay.interpolation_plans.clear()
        block = next(records)
        immediate = []
        while block['schema'] == 'prym-width-accepted-witness/v1':
            immediate.append(block)
            block = next(records)
        block_identity(block, f, scalar, len(f['factor_base']))
        commitment, local_witness = hashlib.sha256(), 0
        for t, triple in enumerate(triples):
            for option in range(64):
                options = (option // 16, (option // 4) % 4, option % 4)
                branch = t*64+option
                attempts += 1
                status, ident, row = replay.outcome(scalar, triple, options)
                if ident is not None and option == 0:
                    points, _ = replay.descriptor(scalar, triple, options)
                    check(ident == replay.identity_four_way(scalar, triple, options, points), 'optimized canonical ID differs from four-way definition')
                    identity_calibrations += 1
                check(block['statuses'][branch] == status, 'replayed status differs at '+str((f['b'], attempts)))
                payload = json.dumps([scalar, branch, ident, status], separators=(',', ':')).encode()+b'\n'
                commitment.update(payload)
                digest_bytes += len(payload)
                counts[status] += 1
                if row is None:
                    continue
                check(row_index < len(cell['rows']) and row == cell['rows'][row_index], 'fresh witness differs')
                check(cell['row_attempts'][row_index] == attempts, 'wrong row attempt')
                verify_row(f, row, g)
                other, witness = transport(f, row)
                verify_row(other, witness, g)
                aa = digest(witness)
                check(aa == cell['transported_witness_hashes'][row_index], 'transported witness hash differs')
                check(project_equation(row, projection, f['r']) ==
                      project_equation(witness, public_projection(other, sources, g), f['r']), 'transported projected equation differs')
                expected = {'schema': 'prym-width-accepted-witness/v1', 'curve_uid': f['uid'],
                            'scalar': scalar, 'attempt': attempts, 'row_index': row_index,
                            'row': row, 'transported_witness_sha256': aa}
                check(local_witness < len(immediate) and immediate[local_witness] == expected, 'false/missing immediate witness')
                local_witness += 1
                M.append(project_equation(row, projection, f['r'])[0])
                current = rank(M, f['r'])
                row_index += 1
                if current > previous:
                    progress.append([attempts, row_index, current])
                    previous = current
                    if current == projection['U'] and first is None:
                        first = progress[-1]
        check(local_witness == len(immediate), 'extra immediate witness')
        check(commitment.hexdigest() == block['attempt_digest'], 'branch commitment differs')
        expected_checkpoint = [scalar, attempts, row_index, previous]
        check(expected_checkpoint == [block['checkpoint'][k] for k in ('source_scalar', 'attempt', 'accepted_rows', 'rank')], 'block checkpoint differs')
        check(block['checkpoint'] == cell['source_checkpoints'][source_index], 'raw/event checkpoint bytes differ')
        checks.append({'source': scalar, 'attempts': attempts, 'accepted_rows': row_index, 'rank': previous,
                       'attempt_digest': commitment.hexdigest(), 'statuses_sha256': hashlib.sha256(block['statuses'].encode()).hexdigest()})
        if source_index % 8 == 7:
            print(json.dumps({'progress_b': f['b'], 'sources': source_index+1, 'attempts': attempts,
                              'rows': row_index, 'rank': previous, 'seconds': round(time.monotonic()-start, 2)}), flush=True)
    check(next(records, None) is None, 'extra/duplicate source block')
    check(row_index == len(cell['rows']) == len(cell['row_attempts']) == len(cell['transported_witness_hashes']), 'extra/missing row')
    check(attempts == cell['attempts'] and counts == Counter(cell['reasons']) and len(replay.seen) == cell['distinct_candidates'], 'wrong status/candidate totals')
    check(progress == [[v[k] for k in ('attempt', 'accepted_rows', 'rank')] for v in cell['rank_progress']], 'rank progress differs')
    check(first == (None if cell['first_full_rank'] is None else [cell['first_full_rank'][k] for k in ('attempt', 'accepted_rows', 'rank')]), 'first full rank differs')
    cert = certificate(f, cell, g, projection)
    sample = sorted(set(list(range(min(4, row_index))) + list(range(max(0, row_index-4), row_index)) +
                        sorted(range(row_index), key=lambda i: digest(cell['rows'][i]))[:8]))
    storage = cell['storage_operation_vector']
    check((storage['attempt_digest_updates'], storage['attempt_digest_input_bytes'], storage['source_blocks'], storage['status_bytes']) ==
          (attempts, digest_bytes, len(sources), attempts), 'storage/hash byte counts differ')
    return {'b': f['b'], 'curve_uid': f['uid'], 'attempts_replayed': attempts,
            'source_blocks': len(sources), 'accepted_rows': row_index,
            'reasons': dict(counts), 'distinct_candidates': len(replay.seen),
            'canonical_identity_four_way_checks': identity_calibrations,
            'all_E1_rows_verified': row_index, 'all_principal_E2_rows_verified': row_index,
            'all_transported_rows_verified': row_index, 'required_principal_sample_indices': sample,
            'sample_rule': 'first4,last4,8 lexicographically smallest SHA256(canonical JSON row); deduplicate',
            'checkpoints': checks, 'rank_progress': progress, 'first_full_rank': first,
            'certificate': cert, 'attempt_digest_input_bytes_recomputed': digest_bytes,
            'wall_seconds_diagnostic': time.monotonic()-start}


def run_math(reader, g):
    start = time.monotonic()
    config = json.loads(reader.read('research/prym_factor_base_width_20261025/config.json'))
    fixtures = json.loads(reader.read('research/prym_factor_base_width_20261025/fixtures.json'))['fixtures']
    raw = json.loads(reader.read(BASE+'/export-inputs/RUN-ECDLP-967315/raw-result.json'))
    event_bytes = reader.read(BASE+'/export-inputs/RUN-ECDLP-967315/events.jsonl')
    records = [json.loads(line) for line in event_bytes.splitlines()]
    check(raw['complete'] and not raw['secret_labels_present'] and raw['new_m8_attempts'] == 0, 'invalid complete/secret/extra-arm flags')
    check(len(raw['cells']) == len(fixtures) == 2, 'wrong cell count')
    check(len(records) == raw['producer_artifact_counters']['source_blocks_written'] + raw['producer_artifact_counters']['accepted_witnesses_written'], 'wrong event flow')
    checks = []
    for f, cell in zip(fixtures, raw['cells']):
        subset = [v for v in records if v['curve_uid'] == f['uid']]
        check(subset == records[sum(len([v for v in records if v['curve_uid'] == earlier['uid']]) for earlier in fixtures[:len(checks)]):
                                sum(len([v for v in records if v['curve_uid'] == earlier['uid']]) for earlier in fixtures[:len(checks)+1])], 'reordered curve blocks')
        checks.append(replay_cell(f, cell, subset, g))
    result = {'schema': 'prym-fresh-independent-math-review/v1', 'task_id': 'TASK-20261025-2fe077',
              'generated_at': g['now'](), 'status': 'passed', 'cells': checks,
              'attempts_replayed': sum(x['attempts_replayed'] for x in checks),
              'all_rows_verified': sum(x['accepted_rows'] for x in checks),
              'producer_arithmetic_imported': False, 'checker_arithmetic_imported': False,
              'wall_seconds_diagnostic': time.monotonic()-start,
              'peak_rss_bytes': resource.getrusage(resource.RUSAGE_SELF).ru_maxrss*1024,
              'scope': 'Complete recorded m16 replay; all E1, principal/E2, transported rows, finite matrices and checkpoints. Validation replay only, no new scientific arm.',
              'prescribed_execution_proof': False, 'independent_remote_GET': False}
    binding = save('math-verification.json', result)
    print(json.dumps({'math_done': binding, 'cells': [{k: x[k] for k in ('b','attempts_replayed','accepted_rows')} for x in checks]}), flush=True)
    return result

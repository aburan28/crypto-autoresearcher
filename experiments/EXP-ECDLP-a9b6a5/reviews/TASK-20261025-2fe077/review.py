"""Fresh sealed phase-one arithmetic; no producer imports or target enumeration.

The caller must append a read event before loading this file, pass the exact
source bytes and already-logged event list, and choose preview or finalize.
Only stdlib imports are used. No module import reads another repository file.
"""

import hashlib
import itertools
import json
import math
import os
import random
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path('/workspace/crypto-autoresearcher')
TASK = 'TASK-20261025-2fe077'
PREFIX = 'experiments/EXP-ECDLP-a9b6a5/reviews/' + TASK
EVENT_PATH = PREFIX + '/read-events.json'
CODE_PATH = PREFIX + '/review.py'
PLAN_PATH = 'ledger/handoffs/' + TASK + '.yaml'
PLAN_SHA = 'c348ead5736ad00ec9972ce4baf3c3551dbb0fd3003968ecafc93834c99905f3'
CONFIG_PATH = 'research/prym_factor_base_width_20261025/config.json'
FIXTURE_PATH = 'research/prym_factor_base_width_20261025/fixtures.json'


def now():
    return datetime.now(timezone.utc).isoformat().replace('+00:00', 'Z')


def encoded(obj):
    return (json.dumps(obj, indent=2, ensure_ascii=True) + '\n').encode()


def compact(obj):
    return json.dumps(obj, sort_keys=True, separators=(',', ':')).encode()


def sha(data):
    return hashlib.sha256(data).hexdigest()


class Reads:
    def __init__(self, events):
        self.events = events
        self.hashes = {}

    def read(self, source):
        self.events.append({'seq': len(self.events) + 1, 'kind': 'read',
                            'at': now(), 'source': source})
        # Persist and fsync BEFORE the file read, even for a repeated read.
        data = encoded(self.events)
        with (ROOT / EVENT_PATH).open('wb') as stream:
            stream.write(data)
            stream.flush()
            os.fsync(stream.fileno())
        body = (ROOT / source).read_bytes()
        self.hashes[source] = sha(body)
        return body


def prime(n):
    if n < 2:
        return False
    return all(n % k for k in range(2, math.isqrt(n) + 1))


def square_root(n, p):
    assert p % 4 == 3
    n %= p
    x = pow(n, (p + 1) // 4, p)
    return min(x, (-x) % p) if x * x % p == n else None


class EC:
    def __init__(self, p, a, b):
        self.p, self.a, self.b = p, a % p, b % p
        assert (4 * self.a ** 3 + 27 * self.b ** 2) % p

    def on(self, point):
        return point is None or (point[1] ** 2 - point[0] ** 3
                                 - self.a * point[0] - self.b) % self.p == 0

    def neg(self, point):
        return None if point is None else (point[0], -point[1] % self.p)

    def add(self, left, right):
        if left is None:
            return right
        if right is None:
            return left
        x, y = left
        u, v = right
        p = self.p
        if x == u and (y + v) % p == 0:
            return None
        if left == right:
            slope = (3 * x * x + self.a) * pow(2 * y, -1, p) % p
        else:
            slope = (v - y) * pow(u - x, -1, p) % p
        z = (slope * slope - x - u) % p
        result = (z, (slope * (x - z) - y) % p)
        assert self.on(result)
        return result

    def mul(self, n, point):
        if n < 0:
            return self.mul(-n, self.neg(point))
        out = None
        while n:
            if n & 1:
                out = self.add(out, point)
            point = self.add(point, point)
            n //= 2
        return out

    def cardinality(self):
        # Enumerate abscissae, NOT discrete logs or all scalar multiples.
        p = self.p
        out = 1
        for x in range(p):
            v = (x ** 3 + self.a * x + self.b) % p
            out += 1 if not v else (2 if pow(v, (p - 1) // 2, p) == 1 else 0)
        return out


def trim(poly, p):
    poly = [x % p for x in poly]
    while len(poly) > 1 and poly[-1] == 0:
        poly.pop()
    return poly or [0]


def poly_add(a, b, p):
    return trim([(a[i] if i < len(a) else 0)
                 + (b[i] if i < len(b) else 0)
                 for i in range(max(len(a), len(b)))], p)


def poly_mul(a, b, p):
    out = [0] * (len(a) + len(b) - 1)
    for i, x in enumerate(a):
        for j, y in enumerate(b):
            out[i + j] += x * y
    return trim(out, p)


def poly_div(a, b, p):
    a, b = trim(a, p), trim(b, p)
    assert b != [0]
    q = [0] * max(1, len(a) - len(b) + 1)
    while a != [0] and len(a) >= len(b):
        offset = len(a) - len(b)
        c = a[-1] * pow(b[-1], -1, p) % p
        q[offset] = c
        for j, v in enumerate(b):
            a[offset + j] -= c * v
        a = trim(a, p)
    return trim(q, p), a


def poly_eval(a, x, p):
    out = 0
    for c in reversed(a):
        out = (out * x + c) % p
    return out


def poly_gcd(a, b, p):
    a, b = trim(a, p), trim(b, p)
    while b != [0]:
        a, b = b, poly_div(a, b, p)[1]
    return trim([v * pow(a[-1], -1, p) for v in a], p)


def interpolate(points, p):
    # Incremental Newton interpolation, sharing no producer implementation.
    out, basis = [0], [1]
    for x, y in points:
        value = (y - poly_eval(out, x, p)) * pow(poly_eval(basis, x, p), -1, p) % p
        out = poly_add(out, [value * c for c in basis], p)
        basis = poly_mul(basis, [-x, 1], p)
    return out


def arithmetic_controls():
    p = 101
    v = [3, 5, 7, 11]
    points = [(x, poly_eval(v, x, p)) for x in (0, 1, 4, 9)]
    assert interpolate(points, p) == v
    d = [1]
    for x, _ in points:
        d = poly_mul(d, [-x, 1], p)
    h = [13, 17, 19]
    g = poly_mul(d, h, p)
    q, rem = poly_div(g, d, p)
    assert q == h and rem == [0]
    changed = list(g)
    changed[0] += 1
    assert poly_div(changed, d, p)[1] != [0]
    for x, y in points:
        assert poly_eval(v, x, p) == y
    return {'polynomial_calibration_field': p, 'interpolation_coefficients': v,
            'monic_degree4_divisor': d, 'quadratic_quotient': h,
            'exact_division_checked': True, 'changed_constant_rejected': True,
            'target_constructor_calls': 0}


def project(base, exposed, p, r):
    reps, indices, columns, known = [], {}, [], []
    for i, atom in enumerate(base):
        point = tuple(atom['point'])
        x, y = point
        canonical = (x, min(y, -y % p))
        sign = 1 if point == canonical else -1
        if point in exposed:
            scalar = exposed[point]
            signed_scalar = scalar if scalar <= 64 else scalar - r
            columns.append({'atom': i, 'kind': 'public_anchor',
                            'point': list(point), 'scalar_mod_r': scalar,
                            'signed_public_scalar': signed_scalar})
            known.append(i)
        else:
            if canonical not in indices:
                indices[canonical] = len(reps)
                reps.append(list(canonical))
            columns.append({'atom': i, 'kind': 'unknown',
                            'point': list(point), 'column': indices[canonical],
                            'sign': sign})
    return {'width': len(base), 'U': len(reps), 'known_atoms': known,
            'unknown_representatives': reps, 'native_to_projected': columns,
            'equal_or_opposite_unknown_merges': len(base) - len(known) - len(reps)}


def derived_schedule(binding):
    # The public card fixes the literal seed string but not its Python seed
    # conversion. Inspect finitely many conventional conversions, report only
    # an actual match; do not silently assume the producer's convention.
    literal = binding['source_order_derivation']
    digest = hashlib.sha256(literal.encode()).digest()
    candidates = [('literal_string', literal), ('sha256_hex_string', digest.hex()),
                  ('sha256_big_endian_integer', int.from_bytes(digest, 'big')),
                  ('sha256_bytes', digest)]
    matches = []
    for name, value in candidates:
        seq = list(range(1, 65))
        random.Random(value).shuffle(seq)
        if seq == binding['source_order']:
            matches.append(name)
    return {'literal': literal, 'matching_stdlib_Random_seed_conventions': matches,
            'exact_order': binding['source_order'],
            'is_public_1_through_64_permutation': sorted(binding['source_order']) == list(range(1, 65)),
            'limitation': 'A matched conventional seed rule is a public-array consistency check; producer derivation implementation is unread in phase1.'}


def derive_fixture(fixture, config):
    p, a, b, r = (fixture[k] for k in ('p', 'a', 'b', 'r'))
    P = tuple(fixture['P'])
    assert prime(p) and prime(r)
    e1 = EC(p, a, b)
    assert e1.on(P) and P is not None
    n = e1.cardinality()
    assert n == r and e1.mul(r, P) is None
    assert fixture['ec1']['curve']['cofactor'] == 1
    f = [b, 0, a, 0, 0, 0, 1]
    df = [0, 2 * a, 0, 0, 0, 6]
    assert poly_gcd(f, df, p) == [1]
    # E2: v^2 = b*u^3 + a*u^2 + 1. The following invertible change
    # puts it into short form, allowing independent affine group arithmetic.
    inv3, inv27 = pow(3, -1, p), pow(27, -1, p)
    short_a2 = -a * a * inv3 % p
    short_b2 = (b * b + 2 * a ** 3 * inv27) % p
    e2 = EC(p, short_a2, short_b2)
    Tplus = (a * inv3 % p, b % p)
    Tminus = e2.neg(Tplus)
    assert e2.on(Tplus) and e2.add(Tplus, Tminus) is None
    # Verify the quotient and coordinate-change identities as polynomials.
    x_of_u = [a * inv3, b]
    short_rhs = poly_add(poly_add(poly_mul(poly_mul(x_of_u, x_of_u, p), x_of_u, p),
                                 [short_a2 * v for v in x_of_u], p), [short_b2], p)
    expected_rhs = [(b * b) % p, 0, (b * b * a) % p, (b ** 3) % p]
    assert trim(short_rhs, p) == trim(expected_rhs, p)
    # Deterministically reconstruct the base by rational native x order.
    base, trace, seen = [], [], set()
    for x in range(p):
        u = x * x % p
        y = square_root((x ** 6 + a * x * x + b) % p, p)
        reason = 'not_rational' if y is None else ('duplicate_norm_x' if u in seen else 'append')
        entry = {'x': x, 'norm_x': u, 'canonical_y': y, 'reason': reason}
        if reason == 'append':
            entry['atom_index'] = len(base)
            atom = {'point': [u, y], 'lift': [x, y]}
            assert e1.on(tuple(atom['point']))
            base.append(atom)
            seen.add(u)
        trace.append(entry)
        if len(base) == config['factor_base_size']:
            break
    assert base == fixture['factor_base']
    assert trace == fixture['width_binding']['construction_trace']
    assert fixture['width_binding']['old_to_new_atoms'] == list(range(8))
    assert sha(compact(base[:8])) == fixture['width_binding']['old_prefix_sha256']
    assert sha(compact(base)) == fixture['width_binding']['new_base_sha256']
    assert sha(compact(trace)) == fixture['width_binding']['construction_trace_sha256']
    # Public anchors only: no scalar beyond +/-1..64, no unknown log table.
    images, exposed = [], {}
    liftable = []
    Pprevious = None
    for k in range(1, config['public_source_max'] + 1):
        S = e1.mul(k, P)
        assert S == e1.add(Pprevious, P)
        assert S is not None
        Pprevious = S
        NS = e1.neg(S)
        assert S not in exposed and NS not in exposed and S != NS
        exposed[S], exposed[NS] = k, (-k) % r
        x = square_root(S[0], p)
        lift = None if x is None else [x, S[1]]
        phi2 = None
        if x is not None:
            assert (S[1] ** 2 - x ** 6 - a * x * x - b) % p == 0
            liftable.append(k)
            if x:
                u = pow(x * x % p, -1, p)
                v = S[1] * pow(pow(x, 3, p), -1, p) % p
                assert (v * v - b * u ** 3 - a * u * u - 1) % p == 0
                S2 = ((b * u + a * inv3) % p, b * v % p)
                assert e2.on(S2)
                phi2 = [u, v]
        images.append({'a': k, 'positive_E1': list(S), 'negative_E1': list(NS),
                       'negative_scalar_mod_r': (-k) % r,
                       'canonical_native_lift': lift,
                       'pi2_lift_image': phi2,
                       'zero_native_x': x == 0})
    assert len(exposed) == 128
    for i in range(1, 33):
        assert e1.add(tuple(images[i - 1]['positive_E1']),
                      tuple(images[64 - i - 1]['positive_E1'])) == e1.mul(64, P)
    projection8 = project(base[:8], exposed, p, r)
    projection16 = project(base, exposed, p, r)
    # Target-independent copied fixture and signed-map controls.
    assert not e1.on((P[0], (P[1] + 1) % p))
    probe = list(P)
    probe[1] = -probe[1] % p
    assert exposed[tuple(probe)] == r - 1
    signed = [{'point': atom['point'], 'lift': atom['lift'],
               'deck': [-atom['lift'][0] % p, atom['lift'][1]],
               'hyperelliptic': [atom['lift'][0], -atom['lift'][1] % p],
               'pi1': atom['point']}
              for atom in base]
    schedule = derived_schedule(fixture['width_binding'])
    assert schedule['is_public_1_through_64_permutation']
    assert sha(compact(schedule['exact_order'])) == fixture['width_binding']['source_order_sha256']
    return {'b': b, 'p': p, 'a': a, 'r_recounted': n, 'r_prime': True,
            'P': list(P), 'P_order': r, 'P_order_reason': 'nonidentity point killed by prime recounted group order',
            'E1_discriminant_nonzero': True, 'C_squarefree_gcd': [1],
            'canonical_reconstructed_factor_base': base,
            'construction_trace': trace, 'old8_prefix_sha256': sha(compact(base[:8])),
            'new16_base_sha256': sha(compact(base)),
            'public_signed_images': images, 'signed_anchor_count': len(exposed),
            'public_source_liftable_labels_including_x0': liftable,
            'public_source_nonzero_native_x_labels': [v['a'] for v in images if v['canonical_native_lift'] is not None and not v['zero_native_x']],
            'old8_projection': projection8, 'new16_projection': projection16,
            'norm_deck_records': signed, 'source_schedule': schedule,
            'E2_short_form': {'a': short_a2, 'b': short_b2, 'recounted_order': e2.cardinality(),
                              'X': 'b*u+a/3', 'Y': 'b*v',
                              'Tplus_short': list(Tplus), 'Tminus_short': list(Tminus)},
            'arithmetic_checks': {'generator_order': True, 'public_scalar_addition_recurrence': True,
                                  'public_pair_addition_checks': 32,
                                  'changed_generator_y_rejected': True,
                                  'negative_anchor_sign_checked': True,
                                  'base_and_lift_reconstruction_equal': True,
                                  'quotient_coordinate_polynomial_identity': True}}


def conventions():
    # Collect every symbolic c_i*c_j contribution to f-v^2 independently.
    square = [[] for _ in range(7)]
    for i in range(4):
        for j in range(i, 4):
            square[i + j].append({'coefficient': 1 if i == j else 2,
                                  'c_indices': [i, j]})
    return {
        'C': 'y^2=x^6+A*x^2+B',
        'pi1': {'map': '(x,y)->(u=x^2,v=y)', 'equation': 'v^2=u^3+A*u+B',
                'infinity_images': {'infinity_plus': 'O', 'infinity_minus': 'O'},
                'x0_images': '(0,+/-sqrt(B))'},
        'pi2': {'map': '(x,y)->(u=x^-2,v=y*x^-3)',
                'equation': 'v^2=B*u^3+A*u^2+1',
                'infinity_images': {'infinity_plus': [0, 1], 'infinity_minus': [0, -1]},
                'x0_images': 'O; use smooth projective extension, never divide by zero'},
        'infinity_definition': 't=1/x,z=y*t^3; z^2=1+A*t^4+B*t^6; infinity_epsilon has z=epsilon',
        'deck_hyperelliptic_actions': [
            {'deck_sign': d, 'hyper_sign': h, 'native': '(d*x,h*y)',
             'pi1_sign': h, 'pi2_sign': d * h}
            for d in (1, -1) for h in (1, -1)],
        'numeric_option_label_limit': 'The public statement names four deck/hyperelliptic options but does not fix which flag occupies which integer bit. The intrinsic sign table is derived here; exact producer option numbering must be compared after release.',
        'cubic': 'v(x)=c0+c1*x+c2*x^2+c3*x^3; four distinct interpolation abscissae give a unique cubic',
        'f_minus_v_squared_coefficients_low_to_high': [
            'B-c0^2', '-2*c0*c1', 'A-c1^2-2*c0*c2',
            '-2*c0*c3-2*c1*c2', '-c2^2-2*c1*c3',
            '-2*c2*c3', '1-c3^2'],
        'fresh_symbolic_square_terms_low_to_high': square,
        'monic_four_root_divisor': 'D=x^4-s1*x^3+s2*x^2-s3*x+s4',
        'residual': {'identity': 'f-v^2=D*(h0+h1*x+h2*x^2) with zero remainder',
                     'h2': 'g6=1-c3^2', 'h1': 'g5+s1*g6',
                     'h0': 'g4+s1*h1-s2*g6',
                     'rational_simple_roots': 'h2 nonzero; h1^2-4*h2*h0 is a nonzero square; residual x values distinct from interpolation x values and satisfy every stated chart/support check'},
        'generic_principal_divisor': 'div(y-v)=sum_of_six_finite_intersections-3*infinity_plus-3*infinity_minus, counting multiplicities; requires c3^2!=1',
        'generic_E1_equation': 'sum pi1(Q_i)=O; if pi1(Q_source)=[s*a]P and n_j are signed atom multiplicities, [s*a]P=-sum_j[n_j]F_j; equivalently c=s and e_j=-n_j',
        'generic_E2_equation': 'sum pi2(Q_i)=3*Tplus+3*Tminus=O because Tminus=-Tplus',
        'exceptional_infinity_rule': 'At infinity_epsilon, ord(y-v)=ord_t(z_epsilon-c3-c2*t-c1*t^2-c0*t^3)-3. For c3=epsilon, first nonzero coefficient occurs at m=1 if c2!=0, m=2 if c2=0,c1!=0, m=3 if c2=c1=0,c0!=0, m=4 if c2=c1=c0=0 and A!=0. Other infinity has order -3. Therefore the finite E2 sum is -m*T_epsilon, not automatically O. These are exceptional charts, not ordinary residual-quadratic rows.',
        'projection_equation': 'For [c*a]P=sum e_j*F_j, subtract public signed anchors k_j: sum_unknown(sum_native e_j*sign_j)*x_column=c*a-sum_known e_j*k_j mod r. Equal/opposite norm representatives merge by signed coefficients; infinity is a zero column.',
        'rank_limit': 'Only 0<=rank(M)<=U follows from public inputs. No observed rank, augmented rank, acceptance or universal m-1 bound is derived in phase1.'
    }


def run(events, source_bytes, finalize=False):
    reader = Reads(events)
    config = json.loads(reader.read(CONFIG_PATH))
    fixture_bytes = reader.read(FIXTURE_PATH)
    fixtures = json.loads(fixture_bytes)['fixtures']
    plan = reader.read(PLAN_PATH)
    assert sha(plan) == PLAN_SHA
    # This is the final repository read of each invocation. Everything below
    # operates only on in-memory public data and stdlib runtime internals.
    spec = reader.read('experiments/EXP-ECDLP-a9b6a5/specification.yaml')
    results = [derive_fixture(f, config) for f in fixtures]
    counts = {'m8_combinations': math.comb(8, 3), 'm16_combinations': math.comb(16, 3),
              'options_per_tuple': 4 ** 3, 'old8_branches_per_source': math.comb(8, 3) * 4 ** 3,
              'new16_branches_per_source': math.comb(16, 3) * 4 ** 3,
              'source_blocks': len(fixtures) * config['public_source_max'],
              'new16_per_curve': config['public_source_max'] * math.comb(16, 3) * 4 ** 3,
              'new16_total': len(fixtures) * config['public_source_max'] * math.comb(16, 3) * 4 ** 3,
              'old8_two_curve_reference_total': len(fixtures) * config['public_source_max'] * math.comb(8, 3) * 4 ** 3,
              'new_m8_scientific_attempts': 0}
    assert counts['new16_branches_per_source'] == config['branches_per_source']
    assert counts['new16_per_curve'] == config['new_attempts_per_curve']
    assert counts['new16_total'] == config['new_attempts_total']
    old_tuples = list(itertools.combinations(range(8), 3))
    new_tuples = list(itertools.combinations(range(16), 3))
    inclusion = [new_tuples.index(t) for t in old_tuples]
    assert len(set(inclusion)) == 56
    # Support-only enumeration, never interpolation or acceptance enumeration.
    controls = arithmetic_controls()
    assert [e['seq'] for e in events] == list(range(1, len(events) + 1))
    assert all(e['kind'] == 'read' for e in events)
    times = [datetime.fromisoformat(e['at'].replace('Z', '+00:00')) for e in events]
    assert times == sorted(times)
    sources = list(dict.fromkeys(e['source'] for e in events))
    quantities = {'descriptor_cardinalities': counts, 'fixtures': results,
                  'quotient_polynomial_infinity_conventions': conventions(),
                  'old8_tuple_embedding_in_m16_combination_indices': inclusion,
                  'old8_option_transport': 'same deck/hyperelliptic flags on the same three inherited atoms; numeric branch indices are width dependent',
                  'arithmetic_controls': controls}
    summary = {'phase': 'phase1', 'finalized': finalize,
               'last_read_at': events[-1]['at'], 'event_count': len(events),
               'source_count': len(sources),
               'derived': [{'b': x['b'], 'r': x['r_recounted'],
                            'U8': x['old8_projection']['U'], 'U16': x['new16_projection']['U'],
                            'known16': x['new16_projection']['known_atoms'],
                            'schedule_matches': x['source_schedule']['matching_stdlib_Random_seed_conventions'],
                            'E2_order': x['E2_short_form']['recounted_order']}
                           for x in results]}
    if not finalize:
        print(json.dumps(summary, indent=2))
        return
    generated = now()
    assert datetime.fromisoformat(generated.replace('Z', '+00:00')) > times[-1]
    derivation = {'task_id': TASK, 'schema': 'prym-fresh-independent-phase1-derivation/v1',
                  'generated_at': generated, 'sources_read': sources, 'quantities': quantities,
                  'input_bindings_sha256': reader.hashes,
                  'review_code_sha256': sha(source_bytes),
                  'read_events_sha256': sha(encoded(events)),
                  'read_events_count': len(events), 'last_phase1_read_at': events[-1]['at'],
                  'scope': 'Fresh public-input/order/base/projection/count/quotient derivation only. No producer helper, output, report, hidden log table or unknown-target secret was inspected or evaluated.',
                  'procedure_deviations': [],
                  'limitations': ['Public historical eight-atom prefix is reconstructed and compared to its supplied hash; archived historical fixture bytes are intentionally unread until release.',
                                  'Source scheduling seed conversion and numeric option labels have the explicitly stated limits in quantities.',
                                  'No stream acceptance, rank, cost, scientific verdict, publication authentication or prescribed-execution-proof claim.'],
                  'phase1_status': 'written; quiescent pending Coordinator archive/seal and deliberate later release'}
    body = encoded(derivation)
    target = ROOT / PREFIX / 'derivation.json'
    fd = os.open(target, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o644)
    with os.fdopen(fd, 'wb') as stream:
        stream.write(body)
        stream.flush()
        os.fsync(stream.fileno())
    # No repository reads (including readback or hashes) occur past generated_at.
    summary.update({'generated_at': generated, 'derivation_path': PREFIX + '/derivation.json',
                    'derivation_sha256': sha(body), 'code_path': CODE_PATH,
                    'code_sha256': sha(source_bytes), 'events_path': EVENT_PATH,
                    'events_sha256': sha(encoded(events)), 'sources_read': sources,
                    'quiescent': True})
    print(json.dumps(summary, indent=2))

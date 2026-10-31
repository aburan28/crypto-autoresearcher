"""Independent assertions for the frozen 15/8 cases and mandated corruptions.

Run once with the prescribed interpreter and -B. The controller retains every
attempt in independent-results.json and bounds each worker to 240 seconds.
No producer tests, results, derivations or README are read. No fixture search.
"""
import copy
import hashlib
import json
import math
import os
from pathlib import Path
import platform
import subprocess
import sys
import traceback
from collections import Counter
from datetime import datetime, timezone
from unittest.mock import patch

HERE = Path(__file__).resolve().parent
SOURCE = HERE.parent
REPO = SOURCE.parent.parent
CONTRACT = REPO / 'coordination/prime_sat_shared_signed_chart_20261030/fixed-software-contract.json'
EXPECTED = {
    'quotient.py': '0a5ac4ef58ef1c4616f849af6bb3895ca927f241f53a05baf21ee028fda3a433',
    'charts.py': 'c808c7d3a5a2a96316a0c13c9faafd848406ef44e960a1bcc52bde700e6a818b',
    'projectors.py': '1f27515ad569061ae5599e8988611d9a5722518a6fa23e537f0febcbf3f5b6af',
    'signed_recovery.py': 'bf67fa02e1778b8de89f4305c2ecda338977ab17ce24941503bb8ce61d4c8bc3',
    'check_chart.py': '139ec0d1b2a13d0add5547b81a363bc402fe59af13d94965beb21a6f0725de65',
}


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def source_hashes():
    return {name: digest(SOURCE / name) for name in EXPECTED}


def clean(poly, p):
    a = [x % p for x in poly]
    while len(a) > 1 and a[-1] == 0:
        a.pop()
    return a or [0]


def plus(a, b, p):
    c = [0] * max(len(a), len(b))
    for i, x in enumerate(a):
        c[i] += x
    for i, x in enumerate(b):
        c[i] += x
    return clean(c, p)


def times(a, b, p):
    c = [0] * (len(a) + len(b) - 1)
    for i in range(len(a)):
        for j in range(len(b)):
            c[i + j] += a[i] * b[j]
    return clean(c, p)


def remainder(a, u, p):
    a = clean(a, p)
    assert u[-1] == 1
    while a != [0] and len(a) >= len(u):
        shift, lead = len(a) - len(u), a[-1]
        for j in range(len(u)):
            a[j + shift] = (a[j + shift] - lead * u[j]) % p
        a = clean(a, p)
    return a


def power_mod(a, n, u, p):
    acc = remainder([1], u, p)
    for bit in bin(n)[2:]:
        acc = remainder(times(acc, acc, p), u, p)
        if bit == '1':
            acc = remainder(times(acc, a, p), u, p)
    return acc


def product_factors(factors, p):
    acc = [1]
    for x, m in factors:
        assert type(m) is int and m > 0
        for _ in range(m):
            acc = times(acc, [-x, 1], p)
    return acc


def on_curve(P, curve):
    x, y = P
    return (y*y - x*x*x - curve['a']*x - curve['b']) % curve['p'] == 0


def group_sum(points, curve):
    p = curve['p']
    acc = None
    for raw in points:
        P = tuple(raw)
        assert on_curve(P, curve)
        if acc is None:
            acc = P
            continue
        x1, y1 = acc
        x2, y2 = P
        if x1 == x2 and (y1 + y2) % p == 0:
            acc = None
            continue
        if acc == P:
            num, den = 3*x1*x1 + curve['a'], 2*y1
        else:
            num, den = y2-y1, x2-x1
        # Fermat inversion is separate from the implementation's inverse call.
        slope = num * pow(den % p, p-2, p) % p
        x3 = (slope*slope-x1-x2) % p
        acc = x3, (slope*(x1-x3)-y1) % p
    return acc


def coefficient_product(a, b, n, p):
    return sum(a[i] * b[n-i] for i in range(n+1)
               if i < len(a) and n-i < len(b)) % p


def series_mul(a, b, length, p):
    return [coefficient_product(a, b, n, p) for n in range(length)]


def substitute(poly, variable, length, p):
    # Power expansion rather than the target checker's Horner recurrence.
    out, power = [0]*length, [1] + [0]*(length-1)
    for c in poly:
        out = [(x + c*y) % p for x, y in zip(out, power)]
        power = series_mul(power, variable, length, p)
    return out


def hasse_order(curve, P, A, B, d):
    p, a, b = curve['p'], curve['a'], curve['b']
    alpha, beta = P
    assert on_curve(P, curve)
    length = d+1
    if beta:
        # Hasse/Taylor coefficients use integer binomial coefficients, never n!^-1.
        f = [b, a, 0, 1]
        shifted = [sum(f[i]*math.comb(i, n)*pow(alpha, i-n, p)
                       for i in range(n, len(f))) % p for n in range(length)]
        y = [beta] + [0]*d
        for n in range(1, length):
            y[n] = (shifted[n] - sum(y[i]*y[n-i] for i in range(1, n))) \
                * pow(2*beta, p-2, p) % p
        x = [alpha, 1] + [0]*(length-2)
    else:
        # Let w=x-alpha and z=y. Solve f'(alpha)w+3alpha*w²+w³=z².
        w = [0]*length
        den = (3*alpha*alpha+a) % p
        assert den
        for n in range(1, length):
            w2 = series_mul(w, w, length, p)
            w3n = coefficient_product(w2, w, n, p)
            w[n] = ((int(n == 2)-3*alpha*w2[n]-w3n)*pow(den, p-2, p)) % p
        x = w[:]
        x[0] = alpha
        y = [0, 1] + [0]*(length-2)
    aa = substitute(A, x, length, p)
    by = series_mul(substitute(B, x, length, p), y, length, p)
    coefficients = [(u+v) % p for u, v in zip(aa, by)]
    order = next((n for n, c in enumerate(coefficients) if c), None)
    assert order is not None, ('order exceeds exact pole bound', P, coefficients)
    return order, coefficients


def own_quotient(U, t, s, e, curve=None):
    p, u = U['p'], U['coeffs']
    k = len(u)-1
    if k == 0:
        assert u == [1] and e == []
        return {'nilpotent': [0], 'rationality_nilpotent': None}
    assert len(e) == s
    weighted = [t]
    for j, v in enumerate(e):
        assert remainder(plus(times(v, v, p), [-x for x in v], p), u, p) == [0]
        weighted = plus(weighted, [2**j*x for x in v], p)
    n = remainder(plus([0, 1], [-x for x in weighted], p), u, p)
    assert power_mod(n, k, u, p) == [0]
    T = None
    if curve:
        f = [curve['b'], curve['a'], 0, 1]
        T = remainder(times(f, plus(power_mod(f, (p-1)//2, u, p), [-1], p), p), u, p)
        assert power_mod(T, k, u, p) == [0]
    return {'nilpotent': n, 'rationality_nilpotent': T}


def worker():
    assert source_hashes() == EXPECTED, 'source hash mismatch before imports'
    sys.path.insert(0, str(SOURCE))
    import quotient as q
    import charts
    import projectors
    import signed_recovery as signed
    import check_chart as checker
    contract = json.loads(CONTRACT.read_text())
    assert len(contract['chart_fixtures']) == 15 and len(contract['projector_fixtures']) == 8
    records, stored = [], {}

    def case(identifier, joint, fn):
        try:
            detail = fn()
            records.append({'id': identifier, 'joint': joint, 'status': 'pass', 'detail': detail})
        except Exception as err:
            records.append({'id': identifier, 'joint': joint, 'status': 'fail',
                            'exception_type': type(err).__name__, 'message': str(err),
                            'traceback': traceback.format_exc()})

    def rejected(fn, obligation):
        try:
            value = fn()
        except q.ObligationError as err:
            assert str(err) == obligation, (str(err), obligation)
            return {'rejected_obligation': str(err), 'exception_type': type(err).__name__}
        raise AssertionError(('accepted corruption', value, obligation))

    def checker_reject(w, output, obligation):
        verdict = checker.check_chart(w, output)
        assert verdict['status'] == 'invalid', verdict
        assert verdict['obligation'] == obligation, (verdict, obligation)
        return verdict

    def chart_case(c):
        curve = {name: c[name] for name in ('p', 'a', 'b')}
        interval = {name: c[name] for name in ('t', 's')}
        target = None if c['target'] is None else tuple(c['target'])
        k, p = len(c['points']), c['p']
        spec = charts.chart_spec(curve, k, c['target'])
        if c['expected'].startswith('reject'):
            assert spec['possible'] is False
            return rejected(lambda: charts.construct_from_signed_multiset(curve, interval, c['points'], c['target']), 'possible pole chart')
        assert group_sum(c['points'], curve) == target
        witness = charts.construct_from_signed_multiset(curve, interval, c['points'], c['target'])
        expected_factors = [[x, m] for x, m in sorted(Counter(P[0] for P in c['points']).items())]
        assert witness['U'] == {'p': p, 'coeffs': product_factors(expected_factors, p)}
        equations = own_quotient(witness['U'], c['t'], c['s'], witness['e'], curve)
        cert = projectors.recover_interval_factors(witness['U'], c['t'], c['s'], witness['e'])
        assert cert == {'p': p, 't': c['t'], 's': c['s'], 'factors': expected_factors}
        output = signed.recover_signed_divisor(curve, c['target'], witness['A'], witness['B'], witness['U'], cert, witness['root_lifts'])
        expected_output = sorted(c['points']) + [None]*(5-k)
        assert output == expected_output, (output, expected_output)
        assert checker.check_chart(witness, output) == {'status': 'valid', 'obligation': None}
        witness['factors'] = cert
        assert checker.check_chart(witness, output) == {'status': 'valid', 'obligation': None}
        d = k + int(target is not None)
        orders = []
        if k:
            A, B = witness['A'], witness['B']
            da = -1 if A == [0] else len(A)-1
            db = -1 if B == [0] else len(B)-1
            assert spec['d'] == d and spec['c'] == (-1 if d % 2 else 1)
            own_basis = [('A', i, 2*i) for i in range(d//2+1)] + [('B', j, 2*j+3) for j in range(max(0, (d-3)//2+1))]
            assert spec['basis'] == sorted(own_basis, key=lambda term: term[2])
            if d % 2:
                assert B[-1] == 1 and 2*db+3 == d and 2*da < d
            else:
                assert A[-1] == 1 and 2*da == d and (B == [0] or 2*db+3 < d)
            norm = plus(times(A, A, p), [-v for v in times([curve['b'], curve['a'], 0, 1], times(B, B, p), p)], p)
            signed_norm = clean([spec['c']*v for v in norm], p)
            rhs = witness['U']['coeffs']
            if target:
                rhs = times([-target[0], 1], rhs, p)
            assert signed_norm == rhs
            zeros = Counter(tuple(P) for P in c['points'])
            if target:
                zeros[(target[0], -target[1] % p)] += 1
            support_signs = set(zeros)
            support_signs.update((x, -y % p) for x, y in list(support_signs))
            for P in sorted(support_signs):
                order, coefficients = hasse_order(curve, P, A, B, d)
                assert order == zeros[P], (P, order, zeros[P])
                assert checker.local_order(curve, P, A, B, d) == order
                orders.append({'point': list(P), 'order': order, 'series_coefficients': coefficients})
            assert sum(row['order'] for row in orders) == d
        else:
            assert witness['A'] == [1] and witness['B'] == [0] and spec['special'] == 'all_identity'
        stored[c['id']] = (copy.deepcopy(witness), copy.deepcopy(output))
        return {'witness': witness, 'recovered': output, 'd': d, 'independent_local_orders': orders, 'independent_quotient': equations}

    for c in contract['chart_fixtures']:
        case('chart/' + c['id'], 'chart_correspondence', lambda c=c: chart_case(c))

    def projector_case(c):
        U = {'p': c['p'], 'coeffs': c['U']}
        if 'expected_factors' not in c:
            obligation = 'interval nilpotence' if c['id'] == 'non_split_reject' else 'idempotence'
            return rejected(lambda: projectors.recover_interval_factors(U, c['t'], c['s'], c['e']), obligation)
        equations = own_quotient(U, c['t'], c['s'], c['e'])
        result = projectors.recover_interval_factors(U, c['t'], c['s'], c['e'])
        assert result['factors'] == c['expected_factors']
        assert product_factors(result['factors'], c['p']) == c['U']
        assert len(result['factors']) <= len(c['U'])-1
        return {'factors': result, 'independent_quotient': equations}

    for c in contract['projector_fixtures']:
        case('projector/' + c['id'], 'projector_recovery', lambda c=c: projector_case(c))

    def mutate_output(fixture, fn, obligation):
        w, output = copy.deepcopy(stored[fixture])
        return checker_reject(w, fn(output), obligation)

    def mutate_witness(fixture, fn, obligation):
        w, output = copy.deepcopy(stored[fixture])
        fn(w)
        return checker_reject(w, output, obligation)

    def simple_roots_control():
        U = {'p': 5, 'coeffs': [1, 3, 1]}
        n = own_quotient(U, 0, 1, [[1]])['nilpotent']
        assert n == [4, 1] and n != [0] and power_mod(n, 2, U['coeffs'], 5) == [0]
        assert q.verify_quotient_witness(U, 0, 1, [[1]]) is True
        return {'n': n, 'n_squared_mod_U': [0], 'incorrect_n_equals_zero_accepts': False}

    case('mutation/n_instead_of_n_power_k', 'quotient_membership', simple_roots_control)
    case('mutation/trace_zero_instead_of_integer_five', 'projector_recovery', lambda: rejected(
        lambda: projectors.check_factor_certificate({'p': 5, 'coeffs': [4, 0, 0, 0, 0, 1]},
            {'p': 5, 't': 0, 's': 1, 'factors': [[1, 0]]}), 'positive integer multiplicity'))

    def dropped_target():
        w, output = copy.deepcopy(stored['target_outside_interval'])
        with patch.object(signed, 'norm_support', lambda factors, target: factors['factors']):
            return rejected(lambda: signed.recover_signed_divisor(w['curve'], w['target'], w['A'], w['B'], w['U'], w['factors'], w['root_lifts']), 'complete signed degree')

    case('mutation/omit_outside_target_support', 'signed_local_orders', dropped_target)

    def wrong_target():
        w, output = copy.deepcopy(stored['finite_one'])
        divisor = Counter(tuple(P) for P in output if P is not None)
        R = tuple(w['target'])
        divisor[(R[0], -R[1] % w['curve']['p'])] += 1
        divisor[R] -= 1
        wrong = [list(P) for P, m in sorted(divisor.items()) for _ in range(m)] + [None]*4
        assert group_sum([P for P in wrong if P], w['curve']) != R
        result = checker_reject(w, wrong, 'checker exact signed local order')
        result['wrong_output'] = wrong
        return result

    case('mutation/subtract_R_instead_of_negative_R', 'signed_local_orders', wrong_target)
    case('mutation/collapse_inverse_signs', 'signed_local_orders', lambda: mutate_output(
        'identity_two_inverse', lambda out: [[0, 1], [0, 1]]+[None]*3, 'checker exact signed local order'))
    case('mutation/remove_common_factor_sign_contribution', 'signed_local_orders', lambda: mutate_output(
        'finite_three_common', lambda out: [[0, 1]]*3+[None]*2, 'checker exact signed local order'))
    case('mutation/two_torsion_doubled_sign', 'signed_local_orders', lambda: mutate_output(
        'finite_two_torsion', lambda out: [[3, 0]]*3+[None]*2, 'canonical multiset and padding'))

    def nonsquare_common_root():
        U = {'p': 5, 'coeffs': [1, 3, 1]}
        assert q.verify_quotient_witness(U, 0, 1, [[1]]) is True
        curve = {'p': 5, 'a': 1, 'b': 1}
        assert (1+1+1) % 5 == 3 and pow(3, 2, 5) == 4
        result = rejected(lambda: q.verify_quotient_witness(U, 0, 1, [[1]], curve), 'rational ordinate support')
        result['interval_only_passes'] = True
        result['f_at_one'] = 3
        return result

    case('mutation/drop_rationality_common_root', 'quotient_membership', nonsquare_common_root)
    case('mutation/idempotent_coefficient', 'quotient_membership', lambda: rejected(
        lambda: q.verify_quotient_witness({'p': 5, 'coeffs': [1, 3, 1]}, 0, 1, [[2]]), 'idempotence'))
    case('mutation/norm_coefficient', 'chart_correspondence', lambda: mutate_witness(
        'finite_one', lambda w: w.update(A=[1, 1]), 'checker norm identity'))
    case('mutation/U_leading_coefficient', 'quotient_membership', lambda: mutate_witness(
        'finite_one', lambda w: w['U']['coeffs'].__setitem__(-1, 2), 'monic quotient modulus'))
    case('mutation/factor_multiplicity', 'projector_recovery', lambda: mutate_witness(
        'finite_two_repeat', lambda w: w['factors']['factors'][0].__setitem__(1, 1), 'independent factor product'))
    case('mutation/target_ordinate_opposite_valid_sign', 'signed_local_orders', lambda: mutate_witness(
        'finite_one', lambda w: w['target'].__setitem__(1, 4), 'checker exact signed local order'))
    case('mutation/target_ordinate_off_curve', 'signed_local_orders', lambda: mutate_witness(
        'finite_one', lambda w: w['target'].__setitem__(1, 2), 'checker point on curve'))

    # Late malformed entries ensure no prefix-only validation of field or mask data.
    for value, label in [(True, 'boolean'), ('1', 'string'), (5, 'out_of_field'), (-1, 'negative')]:
        case('mutation/late_field_' + label, 'quotient_membership', lambda value=value: mutate_witness(
            'finite_one', lambda w: w['root_lifts'].append([0, value]), 'canonical field element'))
    for value, label in [(True, 'boolean'), ('0', 'string'), (7, 'out_of_field'), (-1, 'negative')]:
        case('mutation/late_mask_' + label, 'quotient_membership', lambda value=value: mutate_witness(
            'identity_five_two_torsion', lambda w: w['e'][-1].append(value), 'canonical field element'))
    case('mutation/late_mask_trailing_zero', 'quotient_membership', lambda: mutate_witness(
        'identity_five_two_torsion', lambda w: w['e'][-1].append(0), 'trailing polynomial zero'))
    case('mutation/noncanonical_mask_container', 'quotient_membership', lambda: mutate_witness(
        'identity_five_two_torsion', lambda w: w['e'].__setitem__(-1, tuple(w['e'][-1])), 'polynomial representation'))
    case('mutation/noncanonical_interval_bit_count', 'quotient_membership', lambda: mutate_witness(
        'finite_one', lambda w: w['interval'].update(s=True), 'interval bit count'))
    case('mutation/noncanonical_factor_integer', 'projector_recovery', lambda: mutate_witness(
        'finite_one', lambda w: w['factors']['factors'][0].__setitem__(1, True), 'positive integer multiplicity'))
    case('source_hashes_after', 'fixed_execution', lambda: {'unchanged': source_hashes() == EXPECTED} if source_hashes() == EXPECTED else (_ for _ in ()).throw(AssertionError('source hashes changed')))
    payload = {'records': records, 'source_hashes_after': source_hashes(), 'passed': sum(r['status'] == 'pass' for r in records), 'failed': sum(r['status'] == 'fail' for r in records)}
    print(json.dumps(payload, sort_keys=True))
    return int(payload['failed'] != 0)


def controller():
    out = HERE / 'independent-results.json'
    doc = json.loads(out.read_text()) if out.exists() else {
        'schema': 'prime-shared-chart-independent-software/v1',
        'task_id': 'TASK-20261030-0c09df',
        'source_commit_declared': '1a944ab5677a4e0b1059d1afd965cdd1b87acdf6',
        'source_commit_verified_by_reviewer': False,
        'source_identity_verified_by': 'exact content SHA256 before and after suite',
        'scope': '15 fixed chart cases, 8 fixed projector cases, mandatory mutations only',
        'scientific_runs': 0, 'solver_instances': 0, 'remote_jobs': 0,
        'maximum_suite_invocations': 4, 'suite_watchdog_seconds': 240,
        'attempts': []}
    assert len(doc['attempts']) < 4, 'suite invocation limit'
    assert not doc.get('sealed'), 'sealed review output'
    before = source_hashes()
    assert before == EXPECTED, 'source identity mismatch'
    command = [sys.executable, '-B', str(Path(__file__).resolve()), '--worker']
    row = {'attempt': len(doc['attempts'])+1, 'command': command,
           'started_at': datetime.now(timezone.utc).isoformat(),
           'source_hashes_before': before, 'test_source_sha256': digest(Path(__file__)),
           'contract_sha256': digest(CONTRACT), 'python': sys.version,
           'platform': platform.platform(), 'cwd': os.getcwd()}
    try:
        proc = subprocess.run(command, capture_output=True, text=True, timeout=240,
                              env={**os.environ, 'PYTHONDONTWRITEBYTECODE': '1'})
        row.update(returncode=proc.returncode, stdout=proc.stdout, stderr=proc.stderr, watchdog_expired=False)
        try:
            row['result'] = json.loads(proc.stdout)
        except json.JSONDecodeError:
            row['result'] = None
    except subprocess.TimeoutExpired as err:
        row.update(returncode=None, stdout=(err.stdout or b'').decode() if isinstance(err.stdout, bytes) else (err.stdout or ''),
                   stderr=(err.stderr or b'').decode() if isinstance(err.stderr, bytes) else (err.stderr or ''),
                   watchdog_expired=True, result=None)
    row['finished_at'] = datetime.now(timezone.utc).isoformat()
    row['source_hashes_after'] = source_hashes()
    doc['attempts'].append(row)
    out.write_text(json.dumps(doc, indent=2, sort_keys=True)+'\n')
    result = row['result'] or {}
    print(json.dumps({'attempt': row['attempt'], 'returncode': row['returncode'],
                      'passed': result.get('passed'), 'failed': result.get('failed'),
                      'failures': [r for r in result.get('records', []) if r['status'] == 'fail'],
                      'watchdog_expired': row['watchdog_expired']}, indent=2))
    return row['returncode'] if row['returncode'] is not None else 124


if __name__ == '__main__':
    sys.exit(worker() if sys.argv[1:] == ['--worker'] else controller())

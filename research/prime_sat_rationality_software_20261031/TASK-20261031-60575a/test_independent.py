#!/usr/bin/env python3
"""Independent fixed review; no search, census, random inputs or solver.

Run --record once to gate and retain a bounded --suite invocation. The evaluator,
symbolic coefficient algebra, polynomial arithmetic, series and expected charts
below are reviewer-authored. Only the driver imports the eight reviewed modules.
"""
import argparse
import collections
import copy
import datetime
import hashlib
import json
import os
from pathlib import Path
import platform
import resource
import subprocess
import sys
import time
import traceback

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
TASK = 'TASK-20261031-60575a'
NEW = 'research/prime_sat_rationality_software_20261031/'
OLD = 'research/prime_sat_shared_signed_chart_20261030/'
COORD = 'coordination/prime_sat_rationality_software_20261031/'
SCIENTIFIC = [NEW+n for n in ('circuits.py', 'rationality.py', 'checker.py')]
SCIENTIFIC += [OLD+n for n in ('quotient.py', 'charts.py', 'projectors.py', 'signed_recovery.py', 'check_chart.py')]
SCIENTIFIC += [COORD+n for n in ('SOURCE-API.md', 'fixed-software-contract.json', 'inference-amendment.yaml', 'review-plan.yaml', 'reviewer-brief.md')]
ROWS = []


def utc():
    return datetime.datetime.now(datetime.timezone.utc).isoformat()


def digest(data):
    return hashlib.sha256(data).hexdigest()


def snapshot(paths):
    return {p: {'sha256': digest((ROOT/p).read_bytes()),
                'utf8': (ROOT/p).read_text()} for p in paths}


def test(name, operation):
    try:
        result = operation()
        ROWS.append({'name': name, 'status': 'pass', 'evidence': result})
    except Exception as exc:
        ROWS.append({'name': name, 'status': 'fail', 'exception': type(exc).__name__,
                     'message': str(exc), 'traceback': traceback.format_exc()})


def insist(condition, message):
    if not condition:
        raise AssertionError(message)


def trim(a):
    out = list(a) or [0]
    while len(out) > 1 and out[-1] == 0:
        out.pop()
    return out


def plus(a, b, p):
    return trim([((a[i] if i < len(a) else 0)+(b[i] if i < len(b) else 0)) % p
                 for i in range(max(len(a), len(b)))])


def times(a, b, p):
    out = [0] * max(1, len(a)+len(b)-1)
    for i in range(len(a)):
        for j in range(len(b)):
            out[i+j] = (out[i+j]+a[i]*b[j]) % p
    return trim(out)


def minus(a, b, p):
    return plus(a, [-v % p for v in b], p)


def remainder(a, u, p):
    out = trim([x % p for x in a])
    while out != [0] and len(out) >= len(u):
        offset = len(out)-len(u)
        c = out[-1]*pow(u[-1], -1, p) % p
        for j in range(len(u)):
            out[offset+j] = (out[offset+j]-c*u[j]) % p
        out = trim(out)
    return out


def power_mod(a, exponent, u, p):
    out = remainder([1], u, p)
    # At most five fixed multiplications, deliberately not producer's binary power.
    for _ in range(exponent):
        out = remainder(times(out, a, p), u, p)
    return out


def eval_poly(poly, x, p):
    return sum(c*pow(x, i, p) for i, c in enumerate(poly)) % p


def local_order(curve, point, A, B, degree):
    """Own formal series, no factorials and no producer arithmetic/recovery."""
    p, a, b = curve['p'], curve['a'], curve['b']
    x0, y0 = point
    length = degree+1
    def padded(v):
        return (v+[0]*length)[:length]
    def stimes(u, v):
        return padded(times(u, v, p))
    def compose(coeffs, series):
        out = [0]*length
        pow_x = [1]+[0]*(length-1)
        for c in coeffs:
            out = [(r+c*s) % p for r, s in zip(out, pow_x)]
            pow_x = stimes(pow_x, series)
        return out
    if y0:
        x = padded([x0, 1]); y = padded([y0])
        fx = compose([b, a, 0, 1], x)
        for n in range(1, length):
            residual = (stimes(y, y)[n]-fx[n]) % p
            y[n] = -residual*pow(2*y0, -1, p) % p
    else:
        y = padded([0, 1]); x = padded([x0])
        for n in range(1, length):
            residual = (compose([b, a, 0, 1], x)[n]-int(n == 2)) % p
            x[n] = -residual*pow(3*x0*x0+a, -1, p) % p
    h = [(u+v) % p for u, v in zip(compose(A, x), stimes(compose(B, x), y))]
    nz = [i for i, c in enumerate(h) if c]
    insist(bool(nz), 'finite order must occur within degree bound')
    return nz[0]


class Symbolic:
    """Reviewer coefficient algebra: monomials are tuples of variable names."""
    def __init__(self, p):
        self.p = p
    def c(self, value):
        return {(): value % self.p} if value % self.p else {}
    def v(self, name):
        return {(name,): 1}
    def sum(self, *terms):
        out = collections.Counter()
        for term in terms:
            out.update(term)
        return {m: c % self.p for m, c in out.items() if c % self.p}
    def neg(self, term):
        return {m: -c % self.p for m, c in term.items()}
    def product(self, a, b):
        out = collections.Counter()
        for m, c in a.items():
            for n, d in b.items():
                out[tuple(sorted(m+n))] += c*d
        return {m: c % self.p for m, c in out.items() if c % self.p}


def expected_symbolic(kind, k, p, a, b):
    """Full unspecialized coefficient equations derived from the frozen API."""
    S = Symbolic(p); v = S.v; const = S.c
    equations = {}; aux = []
    def fresh(name):
        aux.append(name)
        return v(name)
    def equation(label, *parts):
        equations[label] = S.sum(*parts)
    def mul(x, y):
        return S.product(x, y)
    def neg(x):
        return S.neg(x)
    if kind == 'nilpotent':
        inputs = ['u'+str(i) for i in range(k)]
        U = [v(n) for n in inputs]+[const(1)]
        C = [fresh('C'+str(i)) for i in range(k)]
        def modular(L, R, name, zero=False):
            P = [{} for _ in range(k)] if zero else [fresh(name+'.P'+str(i)) for i in range(k)]
            Q = [fresh(name+'.Q'+str(i)) for i in range(k-1)]
            for d in range(2*k-1):
                # Direct convolution at coefficient d; every U_i Q_j remains symbolic.
                terms = [mul(L[i], R[d-i]) for i in range(k) if 0 <= d-i < k]
                if d < k:
                    terms.append(neg(P[d]))
                terms += [neg(mul(U[i], Q[d-i])) for i in range(k+1) if 0 <= d-i < k-1]
                equation(name+'.coefficient'+str(d), *terms)
            return P
        if k == 1:
            V = fresh('v'); F = fresh('F')
            equation('evaluation.square', V, neg(mul(U[0], U[0])))
            equation('evaluation.cubic', F, mul(U[0], V), mul(const(a), U[0]), const(-b))
            equation('ordinate.square', mul(C[0], C[0]), neg(F))
        elif k >= 2:
            if k == 2:
                Q = fresh('f.q'); F1 = fresh('f.F1'); F0 = fresh('f.F0')
                equation('f.degree2', Q, U[1])
                equation('f.degree1', F1, U[0], mul(U[1], Q), const(-a))
                equation('f.degree0', F0, mul(U[0], Q), const(-b))
                F = [F0, F1]
            else:
                F = [const(x) for x in [b, a, 0, 1]+[0]*(k-4)]
                if k == 3:
                    F = [S.sum(const(x), neg(U[i])) for i, x in enumerate([b, a, 0])]
            W = modular(C, C, 'C2')
            D = [S.sum(w, neg(f)) for w, f in zip(W, F)]
            if k == 2:
                modular(D, D, 'D2zero', True)
            else:
                T2 = modular(D, D, 'D2')
                if k == 3:
                    modular(T2, D, 'D3zero', True)
                elif k == 4:
                    modular(T2, T2, 'D4zero', True)
                else:
                    T4 = modular(T2, T2, 'D4')
                    modular(T4, D, 'D5zero', True)
    elif kind == 'constant':
        inputs = ['b0']; z = fresh('z')
        equation('constant.inverse', mul(v('b0'), z), const(-1))
    else:
        inputs = ['A'+str(i) for i in range(4)]+['b0', 'b1']
        for n in ['z', 'alpha', 'q1', 'q2', 'c', 'v', 'F']:
            fresh(n)
        equation('linear.inverse', mul(v('b1'), v('z')), const(-1))
        equation('linear.root', mul(v('b1'), v('alpha')), v('b0'))
        equation('A.horner1', v('q1'), neg(mul(v('A3'), v('alpha'))), neg(v('A2')))
        equation('A.horner2', v('q2'), neg(mul(v('q1'), v('alpha'))), neg(v('A1')))
        equation('A.value', v('c'), neg(mul(v('q2'), v('alpha'))), neg(v('A0')))
        equation('f.square', v('v'), neg(mul(v('alpha'), v('alpha'))))
        equation('f.value', v('F'), neg(mul(v('alpha'), v('v'))), neg(mul(const(a), v('alpha'))), const(-b))
        if kind == 'guard':
            for n in ['e', 'u', 'beta']:
                fresh(n)
            equation('guard.inverse', mul(v('c'), v('u')), v('e'), const(-1))
            equation('guard.c', mul(v('c'), v('e')))
            equation('guard.u', mul(v('u'), v('e')))
            equation('guard.beta', v('beta'), neg(mul(v('e'), v('beta'))))
            equation('guard.square', mul(v('beta'), v('beta')), neg(mul(v('e'), v('F'))))
        else:
            fresh('beta'); fresh('u')
            equation('slack.square', mul(v('beta'), v('beta')), neg(v('F')), neg(mul(v('c'), v('u'))))
    return inputs, aux, equations


def independent_ir(bundle, expected, require_template=True):
    """Separate eager validator/evaluator; no calls to producer arithmetic."""
    c, values = bundle['circuit'], bundle['assignment']
    p = expected['p']
    names = c['inputs']+c['auxiliaries']
    insist(len(names) == len(set(names)), 'unique names')
    insist(set(values) == set(names), 'exact assignment domain')
    for n in names:
        insist(type(values[n]) is int and 0 <= values[n] < p, 'canonical '+n)
    insist(c['p'] == p and c['curve'] == expected['curve'], 'field/curve binding')
    insist(c['projection'] == expected['projection'], 'projection')
    insist({n: values[n] for n in c['inputs']} == expected['inputs'], 'input binding')
    parsed = {}
    residuals = []; degrees = []
    for eq in c['equations']:
        insist(eq['label'] not in parsed, 'unique labels')
        coefficients = {}
        for t in eq['terms']:
            mon = tuple(t['variables']); coeff = t['coefficient']
            insist(type(coeff) is int and 0 < coeff < p, 'canonical nonzero coefficient')
            insist(all(type(n) is str and n in values for n in mon), 'declared variables')
            insist(mon == tuple(sorted(mon)) and mon not in coefficients, 'canonical monomial')
            coefficients[mon] = coeff
        parsed[eq['label']] = coefficients
        degrees.append(max(map(len, coefficients), default=0))
        total = 0
        for mon, coeff in coefficients.items():
            monvalue = 1
            for n in mon:
                monvalue *= values[n]
            total += coeff*monvalue
        residuals.append(total % p)
    expected_inputs, expected_aux, expected_equations = expected_symbolic(c['kind'], c['k'], p, expected['curve']['a'], expected['curve']['b'])
    if require_template:
        insist(c['inputs'] == expected_inputs, 'symbolic inputs retained')
        insist(c['auxiliaries'] == expected_aux, 'all exact auxiliary variables')
        insist(parsed == expected_equations, 'full coefficient expansion differs')
        insist([e['label'] for e in c['equations']] == list(expected_equations), 'equation order')
    insist(max(degrees, default=0) <= 2, 'field generator degree')
    return {'accepts': all(r == 0 for r in residuals), 'residuals': residuals,
            'inputs': len(c['inputs']), 'auxiliaries': len(c['auxiliaries']),
            'equations': len(c['equations']), 'maximum_total_degree': max(degrees, default=0),
            'equation_degrees': degrees, 'exact_symbolic_coefficients_checked': require_template}


def binding(kind, k, p, a, b, inputs):
    return {'p': p, 'curve': {'a': a, 'b': b}, 'kind': kind, 'k': k,
            'inputs': inputs, 'projection': list(inputs)}


EXPECTED_AB = {
    'identity_zero': ([1], [0]),
    'finite_one': ([0, 1], [0]),
    'finite_two_repeat': ([4], [1]),
    'identity_two_inverse': ([0, 1], [0]),
    'finite_three_common': ([0, 0, 1], [0]),
    'identity_three': ([4], [1]),
    'finite_four': ([0, 4], [0, 1]),
    'identity_four': ([0, 0, 1], [0]),
    'finite_five_characteristic5': ([2, 0, 0, 1], [3]),
    'identity_five_two_torsion': ([3, 6], [4, 1]),
    'wrapped_five_balanced': ([0, 0, 1, 1], [0]),
    'target_outside_interval': ([4, 2], [1]),
    'finite_two_torsion': ([4, 1], [0]),
}


def signed_oracle(w, points):
    p = w['curve']['p']; target = w['target']; k = len(points)
    expected = collections.Counter(tuple(P) for P in points)
    zeros = expected.copy()
    if target is not None:
        zeros[(target[0], -target[1] % p)] += 1
    support = set(zeros)
    support |= {(x, -y % p) for x, y in support}
    observed = {}
    for P in sorted(support):
        observed[P] = local_order(w['curve'], P, w['A'], w['B'], k+int(target is not None))
        insist(observed[P] == zeros[P], 'independent local order mismatch at '+str(P))
    product = [1]
    for x, y in points:
        product = times(product, [-x % p, 1], p)
    insist(product == w['U']['coeffs'], 'independent U factor product')
    return {'signed_multiplicities': [{'point': list(P), 'multiplicity': n} for P, n in sorted(expected.items())],
            'norm_divisor_local_orders': [{'point': list(P), 'order': n} for P, n in sorted(observed.items())],
            'expected_output': [list(P) for P in sorted(tuple(P) for P in points)]+[None]*(5-k)}


def chart_binding(w, c):
    p, a, b = [w['curve'][n] for n in ('p', 'a', 'b')]
    if c['arm'] == 'uniform_nilpotent_square' or w['B'] == [0]:
        return binding('nilpotent', w['k'], p, a, b, {'u'+str(i): v for i, v in enumerate(w['U']['coeffs'][:-1])})
    if len(w['B']) == 1:
        return binding('constant', None, p, a, b, {'b0': w['B'][0]})
    aa = w['A']+[0]*(4-len(w['A']))
    inputs = {'A'+str(i): aa[i] for i in range(4)}
    inputs.update({'b0': w['B'][0], 'b1': w['B'][1]})
    return binding('guard' if 'guard' in c['arm'] else 'slack', None, p, a, b, inputs)


def suite():
    resource.setrlimit(resource.RLIMIT_AS, (2*1024**3, 2*1024**3))
    sys.path.insert(0, str(ROOT/NEW)); sys.path.insert(0, str(ROOT/OLD))
    import circuits
    import rationality as candidate
    import checker
    import charts
    import quotient
    import projectors
    import signed_recovery
    import check_chart
    spec = json.loads((ROOT/(COORD+'fixed-software-contract.json')).read_text())
    source_before = {p: digest((ROOT/p).read_bytes()) for p in SCIENTIFIC}
    blocks = {}; fixed_charts = {}; candidates = {}

    for f in spec['nilpotent_fixtures']:
        def check_nil(f=f):
            p, a, b, U, C = [f[n] for n in ('p', 'a', 'b', 'U', 'C')]
            k = len(U)-1
            block = candidate.nilpotent_square_block(k, p, a, b, U, C)
            exp = binding('nilpotent', k, p, a, b, {'u'+str(i): U[i] for i in range(k)})
            ev = independent_ir(block, exp)
            direct_difference = remainder(minus(times(C, C, p), [b, a, 0, 1], p), U, p)
            nil = power_mod(direct_difference, k, U, p) == [0]
            actual = checker.check_assignment(block['circuit'], block['assignment'], exp)
            insist(nil == f['valid'] and ev['accepts'] == nil, 'direct nilpotent predicate disagreement')
            insist(actual['status'] == ('valid' if nil else 'invalid'), 'candidate nilpotent acceptance')
            if f['id'] == 'repeated_branch':
                insist(direct_difference != [0], 'exact-square negative control')
            blocks[f['id']] = (block, exp)
            return {'independent': ev, 'direct_C2_minus_f_remainder': direct_difference,
                    'direct_nilpotence': nil, 'candidate': actual}
        test('nilpotent/'+f['id'], check_nil)

    for k in range(6):
        def check_count(k=k):
            U = [0]*k+[1]; C = [] if not k else [1]
            block = candidate.nilpotent_square_block(k, 5, 0, 1, U, C)
            exp = binding('nilpotent', k, 5, 0, 1, {'u'+str(i): 0 for i in range(k)})
            ev = independent_ir(block, exp)
            count = [0, 3, 9, 15, 21, 36][k]
            insist(ev['auxiliaries'] == ev['equations'] == count, 'nilpotent exact count')
            insist(ev['accepts'], 'fixed count witness')
            insist(checker.check_assignment(block['circuit'], block['assignment'], exp)['status'] == 'valid', 'count candidate')
            blocks['k'+str(k)] = (block, exp)
            return ev
        test('symbolic/nilpotent_k'+str(k), check_count)

    for f in spec['guard_fixtures']:
        for mode in ['guard', 'slack']:
            def check_guard(f=f, mode=mode):
                p = f['p']; block = candidate.linear_B_square_block(p, 1, f['F'], mode, [f['c']], [0, 1], f['beta'])
                exp = binding(mode, None, p, 1, f['F'], {'A0': f['c'], 'A1': 0, 'A2': 0, 'A3': 0, 'b0': 0, 'b1': 1})
                if mode == 'guard':
                    block['assignment'].update({n: f[n] for n in ('e', 'u', 'beta')})
                    residues = [(f['c']*f['u']+f['e']-1) % p, f['c']*f['e'] % p,
                                f['u']*f['e'] % p, (1-f['e'])*f['beta'] % p,
                                (f['beta']**2-f['e']*f['F']) % p]
                    truth = all(r == 0 for r in residues)
                    insist(truth == f['valid'], 'literal guard contract')
                else:
                    u = block['assignment']['u']
                    residues = [(f['beta']**2-f['F']-f['c']*u) % p]
                    truth = residues == [0]
                    insist(truth == (bool(f['c']) or f['beta']**2 % p == f['F']), 'slack existential arithmetic on supplied values')
                ev = independent_ir(block, exp)
                actual = checker.check_assignment(block['circuit'], block['assignment'], exp)
                insist(ev['accepts'] == truth and actual['status'] == ('valid' if truth else 'invalid'), 'guard/slack acceptance')
                insist((ev['auxiliaries'], ev['equations']) == ((10, 12) if mode == 'guard' else (9, 8)), 'guard/slack counts')
                if f['id'] == 'common_square_positive':
                    blocks[mode] = (block, exp)
                return {'literal_residuals': residues, 'independent': ev, 'candidate': actual,
                        'interpretation': 'slack uses its deterministic supplied beta witness; guard validity flags are not reused for slack'}
            test(mode+'/'+f['id'], check_guard)

    arms = [a for a in spec['arms'] if a != 'full_euler_reference']
    for f in spec['chart_fixtures']:
        def check_fixed_chart(f=f):
            curve = {n: f[n] for n in ('p', 'a', 'b')}
            if f['id'] in ('finite_zero_impossible', 'identity_one_impossible'):
                try:
                    charts.construct_from_signed_multiset(curve, {'t': f['t'], 's': f['s']}, f['points'], f['target'])
                except quotient.ObligationError as exc:
                    insist(str(exc) == 'possible pole chart', 'declared impossible chart rejection')
                    return {'explicit_rejection': str(exc), 'exception_type': type(exc).__name__,
                            'candidate_acceptance': 'not_constructible', 'reference_acceptance': 'not_constructible'}
                raise AssertionError('impossible chart accepted')
            w = charts.construct_from_signed_multiset(curve, {'t': f['t'], 's': f['s']}, f['points'], f['target'])
            insist((w['A'], w['B']) == EXPECTED_AB[f['id']], 'independently factored normalized A/B')
            oracle = signed_oracle(w, f['points'])
            output = oracle['expected_output']
            reference = checker.reference_check(w, output)
            insist(reference['status'] == 'valid', 'separate Euler reference acceptance')
            fixed_charts[f['id']] = w
            checks = []
            for arm in arms:
                c = candidate.construct_auxiliaries_from_checked_chart(w, output, arm)
                exp = chart_binding(w, c)
                ev = independent_ir(c['block'], exp)
                insist(ev['accepts'], 'own candidate field predicate')
                actual = checker.check_candidate_chart(w, c)
                insist(actual['status'] == 'valid', 'candidate chart acceptance')
                insist(c['recovered'] == output == actual['recovered'], 'signed multiset equals independent fixture')
                stratum = 'zero' if w['B'] == [0] else ('constant' if len(w['B']) == 1 else 'linear')
                insist(c['stratum'] == stratum, 'disjoint B stratum')
                candidates[(f['id'], arm)] = c
                checks.append({'arm': arm, 'stratum': stratum, 'candidate_acceptance': actual,
                               'reference_acceptance': reference, 'independent': ev})
            return {'chart': w, 'oracle': oracle, 'arms': checks}
        test('chart/'+f['id'], check_fixed_chart)

    # Prescribed F1 A=-X,B=X,U=X^5, with both explicitly supplied beta roots.
    def f1():
        fixed = spec['signed_recovery_regressions'][0]
        w = {'curve': {n: fixed[n] for n in ('p', 'a', 'b')}, 'interval': {'t': 0, 's': 0},
             'k': 5, 'target': None, 'A': fixed['A'], 'B': fixed['B'],
             'U': {'p': fixed['p'], 'coeffs': fixed['U']}, 'e': [], 'root_lifts': [[0, 1], [0, 4]]}
        points = [[0, 1]]*4+[[0, 4]]
        oracle = signed_oracle(w, points)
        insist(oracle['signed_multiplicities'] == fixed['expected_divisor'], 'F1 independently derived multiplicities')
        records = []
        for beta in fixed['guard_beta_values']:
            c = candidate.construct_auxiliaries_from_checked_chart(w, points, 'stratified_guard_with_nilpotent_zero_B', beta_override=beta)
            insist(c['block']['assignment']['beta'] == beta, 'literal requested guard beta')
            ev = independent_ir(c['block'], chart_binding(w, c))
            actual = checker.check_candidate_chart(w, c); reference = checker.reference_check(w, points)
            insist(ev['accepts'] and actual['status'] == reference['status'] == 'valid', 'F1 both-sign acceptance')
            insist(c['recovered'] == points, 'F1 residual ratio sign independent of beta')
            candidates[('F1_'+str(beta), 'guard')] = c
            records.append({'beta': beta, 'independent': ev, 'candidate': actual, 'reference': reference, 'chart': c['chart']})
        insist(records[0]['chart'] == records[1]['chart'], 'identical outer chart projection')
        fixed_charts['F1'] = w
        return {'oracle': oracle, 'both_signs': records}
    test('F1/both_guard_roots', f1)

    # Every mutation is a named, deterministic alteration of a fixed exported example.
    def block_mutation(name, key, change):
        def run():
            base, exp = blocks[key]; altered = copy.deepcopy(base)
            change(altered)
            actual = checker.check_assignment(altered['circuit'], altered['assignment'], exp)
            insist(actual['status'] == 'invalid', 'must explicitly reject mutation '+name+': '+str(actual))
            return {'fixture': key, 'candidate': actual, 'altered_bundle': altered}
        test('mutation/'+name, run)
    block_mutation('modular_quotient', 'k3', lambda x: x['assignment'].__setitem__('C2.Q0', (x['assignment']['C2.Q0']+1) % 5))
    block_mutation('modular_remainder', 'k3', lambda x: x['assignment'].__setitem__('C2.P0', (x['assignment']['C2.P0']+1) % 5))
    block_mutation('guard_variable', 'guard', lambda x: x['assignment'].__setitem__('e', 0))
    for label, value in [('late_noncanonical_p', 5), ('late_negative', -1), ('late_bool', True), ('late_float', 1.0), ('late_string', '1')]:
        block_mutation(label, 'guard', lambda x, value=value: x['assignment'].__setitem__('beta', value))
    block_mutation('missing_assignment_key', 'guard', lambda x: x['assignment'].pop('beta'))
    block_mutation('unknown_assignment_key', 'guard', lambda x: x['assignment'].__setitem__('unused_late', 0))
    block_mutation('duplicate_variable', 'guard', lambda x: x['circuit']['auxiliaries'].__setitem__(-1, 'u'))
    block_mutation('undeclared_monomial', 'guard', lambda x: x['circuit']['equations'][0]['terms'][0].__setitem__('variables', ['undeclared']))
    block_mutation('changed_projection', 'guard', lambda x: x['circuit'].__setitem__('projection', list(reversed(x['circuit']['projection']))))
    block_mutation('changed_p_without_binding', 'guard', lambda x: x['circuit'].__setitem__('p', 7))
    block_mutation('unknown_schema_field', 'guard', lambda x: x['circuit'].__setitem__('unknown', 0))
    block_mutation('noncanonical_coefficient', 'guard', lambda x: x['circuit']['equations'][0]['terms'][0].__setitem__('coefficient', 5))
    block_mutation('bool_polynomial_coefficient', 'guard', lambda x: x['circuit']['equations'][0]['terms'][0].__setitem__('coefficient', True))
    block_mutation('duplicate_projection', 'guard', lambda x: x['circuit'].__setitem__('projection', ['A0', 'A0']))
    block_mutation('omitted_reduction_quotient', 'k3', lambda x: (x['circuit']['auxiliaries'].remove('C2.Q0'), x['assignment'].pop('C2.Q0')))

    def chart_mutation(name, fkey, ckey, change, change_w=None):
        def run():
            w = copy.deepcopy(fixed_charts[fkey]); c = copy.deepcopy(candidates[ckey])
            change(c)
            if change_w:
                change_w(w)
            actual = checker.check_candidate_chart(w, c)
            insist(actual['status'] == 'invalid', 'must explicitly reject '+name+': '+str(actual))
            return {'candidate': actual, 'altered_chart': w, 'altered_candidate': c}
        test('mutation/'+name, run)
    first_arm = arms[0]
    chart_mutation('B_stratum_mismatch', 'finite_four', ('finite_four', arms[2]), lambda c: c.__setitem__('stratum', 'zero'))
    chart_mutation('outer_chart_projection', 'finite_four', ('finite_four', arms[2]), lambda c: c['chart'].__setitem__('k', 3))
    chart_mutation('F1_swapped_multiplicities', 'F1', ('F1_1', 'guard'), lambda c: c.__setitem__('recovered', [[0, 1]]+[[0, 4]]*4))
    chart_mutation('F1_balanced_substitution', 'F1', ('F1_4', 'guard'), lambda c: c.__setitem__('recovered', [[0, 1]]*2+[[0, 4]]*2+[None]))
    chart_mutation('F1_bad_auxiliary_beta', 'F1', ('F1_1', 'guard'), lambda c: c['block']['assignment'].__setitem__('beta', 2))
    chart_mutation('interval_split_premise', 'wrapped_five_balanced', ('wrapped_five_balanced', first_arm), lambda c: None, lambda w: w.__setitem__('e', [[0]]))

    def specialized():
        block, exp = blocks['k3']; bad = copy.deepcopy(block)
        for eq in bad['circuit']['equations']:
            result = collections.Counter()
            for term in eq['terms']:
                coefficient = term['coefficient']; names = []
                for n in term['variables']:
                    if n in bad['circuit']['inputs']:
                        coefficient *= bad['assignment'][n]
                    else:
                        names.append(n)
                result[tuple(names)] += coefficient
            eq['terms'] = [{'coefficient': c % 5, 'variables': list(m)} for m, c in sorted(result.items()) if c % 5]
        try:
            independent_ir(bad, exp)
        except AssertionError as exc:
            insist(str(exc) == 'full coefficient expansion differs', 'specific symbolic rejection')
            return {'reviewer_rejection': str(exc), 'reason': 'Input specialization erases symbolic U_i Q_j terms despite unchanged fixed values.',
                    'producer_generic_IR_evaluator': checker.check_assignment(bad['circuit'], bad['assignment'], exp)}
        raise AssertionError('reviewer accepted specialized symbolic model')
    test('proves_too_much/fixture_specialization', specialized)

    # Explicitly retain malformed outer k behavior as a diagnostic finding; this
    # fixed mutation tests strict field binding beyond equality to an untrusted w.
    chart_mutation('inconsistent_outer_k', 'finite_four', ('finite_four', arms[2]),
                   lambda c: c['chart'].__setitem__('k', 3), lambda w: w.__setitem__('k', 3))

    source_after = {p: digest((ROOT/p).read_bytes()) for p in SCIENTIFIC}
    test('custody/source_unchanged', lambda: insist(source_before == source_after, 'source changed during suite'))
    events = {m.__name__: dict(m.EVENTS) for m in (candidate, checker, quotient)}
    result = {'schema': 'independent-fixed-rationality-suite/v1', 'task': TASK,
              'rows': ROWS, 'passed': sum(r['status'] == 'pass' for r in ROWS),
              'failed': sum(r['status'] == 'fail' for r in ROWS),
              'source_hashes_before': source_before, 'source_hashes_after': source_after,
              'event_counters_by_module': events, 'events_are_not_summed_across_names': True,
              'scientific_runs': 0, 'solver_instances': 0, 'remote_jobs': 0,
              'maximum_resident_set_kib': resource.getrusage(resource.RUSAGE_SELF).ru_maxrss}
    print(json.dumps(result, sort_keys=True))
    return int(result['failed'] != 0)


def record():
    path = HERE/'independent-results.json'
    if path.exists():
        report = json.loads(path.read_text())
    else:
        report = {'schema': 'independent-rationality-software-review/v1', 'task_id': TASK,
                  'attempts': [], 'checkpoint_gate_attempts': []}
    insist(len(report['attempts']) < 4, 'maximum four suite invocations')
    report['source_snapshots'] = snapshot(SCIENTIFIC)
    gate = {'command': ['scripts/checkpoint.sh', 'gate'], 'cwd': str(ROOT), 'started_at': utc()}
    # Required checkpoint operation can have its own S3 bookkeeping; no bypass.
    try:
        proc = subprocess.run(gate['command'], cwd=ROOT, capture_output=True, text=True, timeout=1800)
        gate.update({'returncode': proc.returncode, 'stdout': proc.stdout, 'stderr': proc.stderr})
    except subprocess.TimeoutExpired as exc:
        gate.update({'returncode': None, 'timeout_seconds': 1800,
                     'stdout': (exc.stdout or b'').decode() if isinstance(exc.stdout, bytes) else (exc.stdout or ''),
                     'stderr': (exc.stderr or b'').decode() if isinstance(exc.stderr, bytes) else (exc.stderr or '')})
    gate['finished_at'] = utc(); report['checkpoint_gate_attempts'].append(gate)
    path.write_text(json.dumps(report, indent=2, sort_keys=True)+'\n')
    if gate.get('returncode') != 0:
        print(json.dumps({'checkpoint_refused': gate, 'suite_invocations': len(report['attempts'])}))
        return 2
    command = [sys.executable, '-B', str(Path(__file__).resolve()), '--suite']
    attempt = {'index': len(report['attempts'])+1, 'command': command, 'cwd': str(ROOT),
               'started_at': utc(), 'suite_watchdog_seconds': 240, 'memory_limit_bytes': 2*1024**3,
               'source_hashes_before': {p: s['sha256'] for p, s in report['source_snapshots'].items()},
               'test_source_sha256': digest(Path(__file__).read_bytes()), 'test_source_utf8': Path(__file__).read_text(),
               'python': sys.version, 'platform': platform.platform(),
               'git_head': subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=ROOT, text=True).strip(),
               'git_scoped_status': subprocess.check_output(['git', 'status', '--short', '--untracked-files=no', '--']+SCIENTIFIC, cwd=ROOT, text=True),
               'status': 'started'}
    report['attempts'].append(attempt)
    path.write_text(json.dumps(report, indent=2, sort_keys=True)+'\n')
    start = time.monotonic()
    try:
        proc = subprocess.run(command, cwd=ROOT, capture_output=True, text=True, timeout=240)
        attempt.update({'returncode': proc.returncode, 'stdout': proc.stdout, 'stderr': proc.stderr,
                        'status': 'completed'})
        try:
            attempt['suite_result'] = json.loads(proc.stdout)
        except json.JSONDecodeError as exc:
            attempt['parse_error'] = str(exc)
    except subprocess.TimeoutExpired as exc:
        attempt.update({'returncode': None, 'status': 'timeout',
                        'stdout': (exc.stdout or b'').decode() if isinstance(exc.stdout, bytes) else (exc.stdout or ''),
                        'stderr': (exc.stderr or b'').decode() if isinstance(exc.stderr, bytes) else (exc.stderr or '')})
    attempt.update({'elapsed_seconds_diagnostic_only': time.monotonic()-start, 'finished_at': utc(),
                    'source_hashes_after': {p: digest((ROOT/p).read_bytes()) for p in SCIENTIFIC}})
    path.write_text(json.dumps(report, indent=2, sort_keys=True)+'\n')
    result = attempt.get('suite_result', {})
    print(json.dumps({'attempt': attempt['index'], 'returncode': attempt['returncode'],
                      'passed': result.get('passed'), 'failed': result.get('failed'),
                      'failures': [r for r in result.get('rows', []) if r['status'] != 'pass'],
                      'checkpoint': gate, 'result_path': str(path)}))
    return attempt['returncode'] if attempt['returncode'] is not None else 124


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--record', action='store_true')
    parser.add_argument('--suite', action='store_true')
    args = parser.parse_args()
    if args.record == args.suite:
        parser.error('exactly one of --record or --suite is required')
    sys.exit(record() if args.record else suite())

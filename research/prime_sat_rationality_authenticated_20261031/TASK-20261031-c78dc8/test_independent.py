"""Fresh fixed source-aware review. No producer tests/results are loaded.

Run --supervise only after the native checkpoint gate. Every suite attempt is
retained in independent-results.json, including nonzero exits and raw output.
"""
from collections import Counter
from copy import deepcopy
from pathlib import Path
import datetime
import hashlib
import json
import os
import platform
import resource
import subprocess
import sys
import time
import traceback

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
TASK = 'TASK-20261031-c78dc8'
PYTHON = '/home/ec2-user/prime-sat-research-venv/bin/python'
CONTRACT = 'coordination/prime_sat_rationality_authenticated_20261031/fixed-software-contract.json'
SCIENCE = [
    'research/prime_sat_rationality_authenticated_20261031/authenticated.py',
    'research/prime_sat_rationality_software_20261031/circuits.py',
    'research/prime_sat_rationality_software_20261031/rationality.py',
    'research/prime_sat_rationality_software_20261031/checker.py',
    'research/prime_sat_shared_signed_chart_20261030/quotient.py',
    'research/prime_sat_shared_signed_chart_20261030/charts.py',
    'research/prime_sat_shared_signed_chart_20261030/projectors.py',
    'research/prime_sat_shared_signed_chart_20261030/signed_recovery.py',
    'research/prime_sat_shared_signed_chart_20261030/check_chart.py',
    'coordination/prime_sat_rationality_authenticated_20261031/SOURCE-API.md',
    CONTRACT,
    'coordination/prime_sat_rationality_authenticated_20261031/inference-amendment.yaml',
    'coordination/prime_sat_rationality_authenticated_20261031/review-plan.yaml',
    'coordination/prime_sat_rationality_authenticated_20261031/reviewer-brief.md',
]
POLICY_READS = [
    'AGENTS.md', 'docs/agent-contract-extended.md', 'docs/lab-contract.md',
    '.claude/skills/review-evidence/SKILL.md', 'templates/research-records.md',
    'tools/check_review_independence.py', '.resume/checkpoint_gate_with_provider.py',
    'coordination/goals/GOAL-PFDR-fd09e0/batches/BATCH-a99822/claims/TASK-20261031-c78dc8.1.claim.json',
]
ARMS = ['uniform_nilpotent_square', 'stratified_slack_with_nilpotent_zero_B',
        'stratified_guard_with_nilpotent_zero_B']
ROWS = []
INDEPENDENT_EVENTS = Counter()


def now():
    return datetime.datetime.now(datetime.timezone.utc).isoformat()


def digest(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def exact(a, b):
    if type(a) is not type(b):
        return False
    if type(a) is dict:
        if set(a) == {'label', 'terms'}:
            INDEPENDENT_EVENTS['reviewer_equation_comparisons'] += 1
        if set(a) == {'coefficient', 'variables'}:
            INDEPENDENT_EVENTS['reviewer_term_comparisons'] += 1
        return a.keys() == b.keys() and all(exact(a[k], b[k]) for k in a)
    if type(a) is list:
        return len(a) == len(b) and all(exact(x, y) for x, y in zip(a, b))
    return a == b


def record(name, group, actual, expected, evidence=None):
    passed = exact(actual, expected)
    def compact(value):
        encoded = json.dumps(value, sort_keys=True, separators=(',', ':'))
        if passed and len(encoded) > 1500:
            return {'canonical_json_sha256': hashlib.sha256(encoded.encode()).hexdigest(),
                    'canonical_json_bytes': len(encoded), 'full_value_reproducible_from_test_source': True}
        return value
    row = {'id': name, 'group': group, 'expected': compact(expected), 'actual': compact(actual),
           'passed': passed}
    if evidence is not None:
        row['evidence'] = evidence
    ROWS.append(row)
    return row['passed']


# Independent coefficient-list arithmetic; no q/charts arithmetic is used.
def trim(v):
    v = list(v)
    while len(v) > 1 and v[-1] == 0:
        v.pop()
    return v or [0]


def plus(a, b, p):
    return trim([((a[i] if i < len(a) else 0) + (b[i] if i < len(b) else 0)) % p
                 for i in range(max(len(a), len(b)))])


def times(a, b, p):
    INDEPENDENT_EVENTS['polynomial_product'] += 1
    out = [0] * (len(a) + len(b) - 1)
    for i, x in enumerate(a):
        for j, y in enumerate(b):
            out[i+j] = (out[i+j] + x*y) % p
    return trim(out)


def neg(a, p):
    return [(-x) % p for x in a]


def divide(a, b, p):
    a = trim(a)
    out = [0] * max(1, len(a)-len(b)+1)
    while a != [0] and len(a) >= len(b):
        k = len(a)-len(b)
        v = a[-1] * pow(b[-1], -1, p) % p
        out[k] = v
        for i, x in enumerate(b):
            a[i+k] = (a[i+k] - v*x) % p
        a = trim(a)
    return trim(out), a


def power(a, n, p):
    out = [1]
    for _ in range(n):
        out = times(out, a, p)
    return out


def at(a, x, p):
    return sum(c * pow(x, i, p) for i, c in enumerate(a)) % p


def inverse_poly(a, m, p):
    r0, r1, s0, s1 = m, a, [0], [1]
    while r1 != [0]:
        quotient, rem = divide(r0, r1, p)
        r0, r1 = r1, rem
        s0, s1 = s1, plus(s0, neg(times(quotient, s1, p), p), p)
    assert len(r0) == 1 and r0[0]
    return divide([x*pow(r0[0], -1, p) % p for x in s0], m, p)[1]


def independent_group_sum(points, p, a):
    total = None
    for point in points:
        if total is None:
            total = tuple(point)
            continue
        x, y = total
        xx, yy = point
        if x == xx and (y+yy) % p == 0:
            total = None
            continue
        slope = ((3*x*x+a)*pow(2*y, -1, p) if x == xx else
                 (yy-y)*pow(xx-x, -1, p)) % p
        z = (slope*slope-x-xx) % p
        total = (z, (slope*(x-z)-y) % p)
    return list(total) if total is not None else None


def ordinate_interpolant(points, p):
    roots = {x: min(y, -y % p) for x, y in points}
    result = [0]
    for x, y in roots.items():
        basis, denominator = [1], 1
        for other in roots:
            if other != x:
                basis = times(basis, [-other % p, 1], p)
                denominator = denominator*(x-other) % p
        result = plus(result, [v*y*pow(denominator, -1, p) % p for v in basis], p)
    return result


# Literal A/B witnesses derived from divisors, not from the source constructor.
LITERALS = {
    'identity_zero': ([1], [0]),
    'finite_zero_impossible': ([1], [0]),
    'finite_one': ([0, 1], [0]),
    'identity_one_impossible': ([0, 1], [0]),
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
    'F1_unbalanced_common_root': ([0, 4], [0, 1]),
}


def witness(fixture):
    p, t, s = fixture['p'], fixture['t'], fixture['s']
    points = fixture['points']
    u = [1]
    for x, _ in points:
        u = times(u, [-x % p, 1], p)
    e = [[0] for _ in range(s)] if points else []
    for x, m in Counter(x for x, y in points).items():
        local = power([-x % p, 1], m, p)
        other, rem = divide(u, local, p)
        assert rem == [0]
        projector = divide(times(other, inverse_poly(other, local, p), p), u, p)[1]
        for j in range(s):
            if ((x-t) % p) & (1 << j):
                e[j] = plus(e[j], projector, p)
    a, b = LITERALS[fixture['id']]
    lifts = sorted(set(tuple(v) for v in points + ([fixture['target']] if fixture['target'] else [])))
    return {'curve': {k: fixture[k] for k in ('p', 'a', 'b')},
            'interval': {'t': t, 's': s}, 'target': fixture['target'], 'k': len(points),
            'A': a[:], 'B': b[:], 'U': {'p': p, 'coeffs': u}, 'e': e,
            'root_lifts': [list(v) for v in lifts]}


def expected_binding(block):
    c, assignment = block['circuit'], block['assignment']
    return {k: deepcopy(c[k]) for k in ('p', 'curve', 'kind', 'k', 'projection')} | {
        'inputs': {name: assignment[name] for name in c['inputs']}}


def descriptor(block):
    return {k: deepcopy(block['circuit'][k]) for k in ('p', 'curve', 'kind', 'k', 'projection')}


def make_candidate(w, points, arm, beta_override=None):
    p, a, b = [w['curve'][key] for key in ('p', 'a', 'b')]
    B = w['B']
    stratum = 'zero' if B == [0] else 'constant' if len(B) == 1 else 'linear'
    roots = []
    if arm == ARMS[0] or stratum == 'zero':
        C = ordinate_interpolant(points, p) if points else []
        block = builders.nilpotent_square_block(w['k'], p, a, b, w['U']['coeffs'], C)
        roots = [[x, at(C, x, p)] for x in sorted(set(x for x, y in points))]
    elif stratum == 'constant':
        block = builders.constant_B_block(w['curve'], B)
    else:
        alpha = -B[0] * pow(B[1], -1, p) % p
        common = at(w['A'], alpha, p) == 0
        beta = 0
        if common:
            beta = min(min(y, -y % p) for x, y in w['root_lifts'] if x == alpha)
            if beta_override is not None:
                beta = beta_override
            roots = [[alpha, beta]]
        block = builders.linear_B_square_block(p, a, b, 'guard' if arm == ARMS[2] else 'slack',
                                               w['A'], B, beta)
    return {'arm': arm, 'stratum': stratum,
            'chart': {k: deepcopy(w[k]) for k in ('curve', 'interval', 'target', 'k', 'A', 'B', 'U')},
            'block': block, 'root_lifts': roots,
            'recovered': sorted(deepcopy(points)) + [None]*(5-len(points))}


def coefficient_residuals(block):
    circuit, assignment = block['circuit'], block['assignment']
    p = circuit['p']
    result = []
    for equation in circuit['equations']:
        total = 0
        for term in equation['terms']:
            v = term['coefficient']
            for name in term['variables']:
                v *= assignment[name]
                INDEPENDENT_EVENTS['coefficient_field_multiply'] += 1
            total += v
            INDEPENDENT_EVENTS['coefficient_term_add'] += 1
        result.append({'label': equation['label'], 'value': total % p})
        INDEPENDENT_EVENTS['coefficient_equation_evaluate'] += 1
    return result


# Separate sparse symbolic arithmetic derives the equations independently.
def symbol(x, p):
    return {(): x % p} if type(x) is int and x % p else {} if type(x) is int else {(x,): 1}


def sadd(p, *terms):
    acc = Counter()
    for term in terms:
        for monomial, coefficient in term.items():
            acc[monomial] += coefficient
    return {m: c % p for m, c in acc.items() if c % p}


def sneg(a, p):
    return {m: -c % p for m, c in a.items()}


def smul(a, b, p):
    acc = Counter()
    for m, c in a.items():
        for n, d in b.items():
            acc[tuple(sorted(m+n))] += c*d
    return {m: c % p for m, c in acc.items() if c % p}


def symbolic_equations(kind, k, p, a, b):
    S = lambda name: symbol(name, p)
    equations = []
    def eq(label, *terms):
        expression = sadd(p, *terms)
        equations.append({'label': label, 'terms': [
            {'coefficient': expression[m], 'variables': list(m)} for m in sorted(expression)]})
    def product(L, R, U, label, final=False):
        P = [{} for _ in range(k)] if final else [S(label+'.P'+str(i)) for i in range(k)]
        Q = [S(label+'.Q'+str(i)) for i in range(k-1)]
        for d in range(2*k-1):
            terms = [smul(L[i], R[j], p) for i in range(k) for j in range(k) if i+j == d]
            terms += [sneg(smul(U[i], Q[j], p), p) for i in range(k+1) for j in range(k-1) if i+j == d]
            if d < k:
                terms.append(sneg(P[d], p))
            eq(label+'.coefficient'+str(d), *terms)
        return P
    if kind == 'constant':
        eq('constant.inverse', smul(S('b0'), S('z'), p), S(-1))
    elif kind in ('guard', 'slack'):
        eq('linear.inverse', smul(S('b1'), S('z'), p), S(-1))
        eq('linear.root', smul(S('b1'), S('alpha'), p), S('b0'))
        eq('A.horner1', S('q1'), sneg(smul(S('A3'), S('alpha'), p), p), sneg(S('A2'), p))
        eq('A.horner2', S('q2'), sneg(smul(S('q1'), S('alpha'), p), p), sneg(S('A1'), p))
        eq('A.value', S('c'), sneg(smul(S('q2'), S('alpha'), p), p), sneg(S('A0'), p))
        eq('f.square', S('v'), sneg(smul(S('alpha'), S('alpha'), p), p))
        eq('f.value', S('F'), sneg(smul(S('alpha'), S('v'), p), p), smul(S(-a), S('alpha'), p), S(-b))
        if kind == 'guard':
            eq('guard.inverse', smul(S('c'), S('u'), p), S('e'), S(-1))
            eq('guard.c', smul(S('c'), S('e'), p))
            eq('guard.u', smul(S('u'), S('e'), p))
            eq('guard.beta', S('beta'), sneg(smul(S('e'), S('beta'), p), p))
            eq('guard.square', smul(S('beta'), S('beta'), p), sneg(smul(S('e'), S('F'), p), p))
        else:
            eq('slack.square', smul(S('beta'), S('beta'), p), sneg(S('F'), p), sneg(smul(S('c'), S('u'), p), p))
    elif k:
        U = [S('u'+str(i)) for i in range(k)] + [S(1)]
        C = [S('C'+str(i)) for i in range(k)]
        if k == 1:
            eq('evaluation.square', S('v'), sneg(smul(U[0], U[0], p), p))
            eq('evaluation.cubic', S('F'), smul(U[0], S('v'), p), smul(S(a), U[0], p), S(-b))
            eq('ordinate.square', smul(C[0], C[0], p), sneg(S('F'), p))
        else:
            if k == 2:
                eq('f.degree2', S('f.q'), U[1])
                eq('f.degree1', S('f.F1'), U[0], smul(U[1], S('f.q'), p), S(-a))
                eq('f.degree0', S('f.F0'), smul(U[0], S('f.q'), p), S(-b))
                F = [S('f.F0'), S('f.F1')]
            elif k == 3:
                F = [sadd(p, S(b), sneg(U[0], p)), sadd(p, S(a), sneg(U[1], p)), sneg(U[2], p)]
            else:
                F = [S(v) for v in [b, a, 0, 1]+[0]*(k-4)]
            W = product(C, C, U, 'C2')
            D = [sadd(p, x, sneg(y, p)) for x, y in zip(W, F)]
            if k == 2:
                product(D, D, U, 'D2zero', True)
            else:
                D2 = product(D, D, U, 'D2')
                if k == 3:
                    product(D2, D, U, 'D3zero', True)
                elif k == 4:
                    product(D2, D2, U, 'D4zero', True)
                else:
                    D4 = product(D2, D2, U, 'D4')
                    product(D4, D, U, 'D5zero', True)
    return equations


def audit_block(label, block, valid=None):
    c = block['circuit']
    result = auth.check_authenticated_assignment(c, block['assignment'], expected_binding(block))
    residuals = coefficient_residuals(block)
    record(label+'/residuals', 'independent_arithmetic', result.get('residuals'), residuals)
    if valid is not None:
        record(label+'/acceptance', 'fixed_blocks', result['status'], 'valid' if valid else 'invalid', result)
    equations = symbolic_equations(c['kind'], c['k'], c['p'], c['curve']['a'], c['curve']['b'])
    record(label+'/symbolic_coefficients', 'symbolic_binding', c['equations'], equations)
    degrees = [len(t['variables']) for e in c['equations'] for t in e['terms']]
    record(label+'/quadratic', 'symbolic_binding', max(degrees, default=0) <= 2, True)
    record(label+'/canonical_content', 'symbolic_binding', auth.canonical_circuit(descriptor(block)), c)
    return result


def chart_cases(contract):
    cache = {}
    for f in contract['chart_fixtures']:
        name = f['id']
        w = witness(f)
        good = not f['expected'].startswith('reject')
        points = sorted(deepcopy(f['points']))
        expected = points + [None]*(5-len(points))
        record(name+'/independent_group_sum', 'signed_fidelity', independent_group_sum(points, f['p'], f['a']), f['target'] if good else None,
               {'informational_for_impossible_chart': not good}) if good else None
        reference = checker.reference_check(w, expected)
        record(name+'/reference', 'base_reference', reference['status'], 'valid' if good else 'invalid', reference)
        for arm in ARMS:
            candidate = make_candidate(w, points, arm)
            result = auth.check_authenticated_chart(w, candidate)
            record(name+'/'+arm, 'base_candidate', result['status'], 'valid' if good else 'invalid', result)
            if good:
                record(name+'/'+arm+'/signed_output', 'signed_fidelity', result.get('recovered'), expected)
                audit_block(name+'/'+arm, candidate['block'], True)
                cache[(name, arm)] = (w, candidate)
    return cache


def block_cases(contract):
    for f in contract['nilpotent_fixtures']:
        p, U, C = f['p'], f['U'], f['C'] or [0]
        delta = plus(times(C, C, p), neg([f['b'], f['a'], 0, 1], p), p)
        mathematical = divide(power(delta, len(U)-1, p), U, p)[1] == [0]
        record('nil/'+f['id']+'/polynomial', 'independent_arithmetic', mathematical, f['valid'])
        block = builders.nilpotent_square_block(len(U)-1, p, f['a'], f['b'], U, f['C'])
        audit_block('nil/'+f['id'], block, f['valid'])
        if f['id'] == 'repeated_branch':
            record('nil/repeated_branch/exact_square_control', 'independent_arithmetic', divide(delta, U, p)[1] == [0], False)
    for f in contract['guard_fixtures']:
        p = f['p']
        e, c, u, beta, F = [f[k] for k in ('e', 'c', 'u', 'beta', 'F')]
        residual = [(c*u+e-1) % p, c*e % p, u*e % p, (1-e)*beta % p, (beta*beta-e*F) % p]
        record('guard/'+f['id']+'/scalar_equations', 'independent_arithmetic', not any(residual), f['valid'], residual)
        block = builders.linear_B_square_block(p, 1, F, 'guard', [c], [0, 1], beta)
        block['assignment'].update(e=e, u=u, beta=beta)
        audit_block('guard/'+f['id'], block, f['valid'])
    for k in range(6):
        one = builders.nilpotent_square_block(k, 5, 0, 1)
        two = builders.nilpotent_square_block(k, 5, 0, 1, [2]*k+[1], [3]*k)
        audit_block('symbolic/nil-degree'+str(k), two)
        record('symbolic/nil-degree'+str(k)+'/witness_independence', 'symbolic_binding', one['circuit'], two['circuit'])
        products = {0: 0, 1: 0, 2: 2, 3: 3, 4: 3, 5: 4}[k]
        eq_count = 0 if k == 0 else 3 if k == 1 else products*(2*k-1)+(3 if k == 2 else 0)
        c = two['circuit']
        record('symbolic/nil-degree'+str(k)+'/count', 'accounting', [len(c['auxiliaries']), len(c['equations'])], [eq_count, eq_count],
               {'modular_products': products, 'quotient_variables': sum('.Q' in n for n in c['auxiliaries']),
                'expected_quotient_variables': products*max(k-1, 0), 'terms': sum(len(e['terms']) for e in c['equations'])})
        record('symbolic/nil-degree'+str(k)+'/quotient_count', 'accounting', sum('.Q' in n for n in c['auxiliaries']), products*max(k-1, 0))
    for kind in ('guard', 'slack'):
        one = builders.linear_B_square_block(5, 1, 1, kind)
        two = builders.linear_B_square_block(5, 1, 1, kind, [3, 1, 4, 2], [3, 2], 4)
        audit_block('symbolic/'+kind, two)
        record('symbolic/'+kind+'/witness_independence', 'symbolic_binding', one['circuit'], two['circuit'])
    one = builders.constant_B_block({'p': 5, 'a': 1, 'b': 1}, [1])
    two = builders.constant_B_block({'p': 5, 'a': 1, 'b': 1}, [3])
    audit_block('symbolic/constant', two, True)
    record('symbolic/constant/witness_independence', 'symbolic_binding', one['circuit'], two['circuit'])


def outer_cases(cache):
    for name in ('finite_one', 'finite_two_repeat', 'finite_four'):
        for arm in ARMS:
            original, candidate = cache[(name, arm)]
            for label, value in [('bool', True), ('float', float(original['k'])), ('negative', -1),
                                 ('above5', 6), ('degree_mismatch', original['k']-1)]:
                w, c = deepcopy(original), deepcopy(candidate)
                w['k'] = value
                c['chart']['k'] = value
                before = auth.EVENTS.get('canonical_builder_calls', 0)
                result = auth.check_authenticated_chart(w, c)
                delta = auth.EVENTS.get('canonical_builder_calls', 0)-before
                record('outer/'+name+'/'+arm+'/'+label, 'outer_arity', [result['status'], delta], ['invalid', 0], result)
    w, candidate = cache[('finite_four', ARMS[2])]
    record('R1/literal', 'outer_arity', {key: w[key] for key in ('curve', 'target', 'interval', 'A', 'B', 'U', 'k')},
           {'curve': {'p': 5, 'a': 0, 'b': 1}, 'target': [0, 1], 'interval': {'t': 0, 's': 1},
            'A': [0, 4], 'B': [0, 1], 'U': {'p': 5, 'coeffs': [0, 0, 0, 0, 1]}, 'k': 4})


def mutate_circuit(c, which, assignment):
    if which == 'coefficient':
        t = c['equations'][0]['terms'][0]
        t['coefficient'] = t['coefficient'] % (c['p']-1)+1
    elif which == 'coefficient_bool':
        next(t for e in c['equations'] for t in e['terms'] if t['coefficient'] == 1)['coefficient'] = True
    elif which == 'coefficient_float':
        c['equations'][-1]['terms'][-1]['coefficient'] = float(c['equations'][-1]['terms'][-1]['coefficient'])
    elif which == 'late_malformed_coefficient':
        c['equations'][-1]['terms'][-1]['coefficient'] = 'bad'
    elif which == 'omit_equation':
        c['equations'].pop()
    elif which == 'zero_equation':
        c['equations'][-1]['terms'] = []
    elif which == 'all_zero':
        for e in c['equations']:
            e['terms'] = []
    elif which == 'fixture_specialization':
        inputs = set(c['inputs'])
        for e in c['equations']:
            terms = Counter()
            for t in e['terms']:
                coefficient, variables = t['coefficient'], []
                for v in t['variables']:
                    if v in inputs:
                        coefficient *= assignment[v]
                    else:
                        variables.append(v)
                terms[tuple(variables)] += coefficient
            e['terms'] = [{'coefficient': x % c['p'], 'variables': list(m)}
                          for m, x in sorted(terms.items()) if x % c['p']]
    elif which == 'projection':
        c['projection'] = []
    elif which == 'name_order':
        if len(c['auxiliaries']) > 1:
            c['auxiliaries'].reverse()
        else:
            c['auxiliaries'][0] = 'renamed'
    elif which == 'metadata':
        c['metadata']['extra'] = 0
    elif which == 'label':
        c['equations'][-1]['label'] += '.changed'
    elif which == 'schema':
        c['schema'] += '.changed'
    elif which == 'monomial':
        next(t for e in c['equations'] for t in e['terms'] if t['variables'])['variables'].pop()
    elif which == 'field':
        c['p'] = 7
    elif which == 'curve':
        c['curve']['a'] = (c['curve']['a']+1) % c['p']
    elif which == 'kind':
        c['kind'] = 'guard' if c['kind'] != 'guard' else 'slack'
    elif which == 'degree':
        c['k'] = 1 if c['k'] is None else c['k']+1
    else:
        raise AssertionError(which)


def authentication_cases(cache):
    entries = [
        ('nilpotent', cache[('identity_two_inverse', ARMS[0])][1]['block']),
        ('constant', cache[('finite_two_repeat', ARMS[2])][1]['block']),
        ('guard', cache[('finite_four', ARMS[2])][1]['block']),
        ('slack', cache[('finite_four', ARMS[1])][1]['block']),
    ]
    for kind, block in entries:
        expected = expected_binding(block)
        for mutation in ('coefficient', 'coefficient_bool', 'coefficient_float', 'late_malformed_coefficient',
                         'omit_equation', 'zero_equation', 'all_zero', 'fixture_specialization', 'projection',
                         'name_order', 'metadata', 'label', 'schema', 'monomial', 'field', 'curve', 'kind', 'degree'):
            c = deepcopy(block['circuit'])
            mutate_circuit(c, mutation, block['assignment'])
            result = auth.check_authenticated_assignment(c, block['assignment'], expected)
            record('authentication/'+kind+'/'+mutation, 'canonical_authentication',
                   [result['status'], result.get('stage')], ['invalid', 'authentication'], result)
            if mutation in ('all_zero', 'fixture_specialization'):
                generic = checker.check_assignment(c, block['assignment'], expected)
                record('proves_too_much/'+kind+'/'+mutation, 'proves_too_much', generic['status'], 'valid',
                       {'generic': generic, 'authenticated': result})
        for mutation in ('wrong_p', 'wrong_curve', 'wrong_kind', 'wrong_degree', 'bool_p', 'singular_curve',
                         'curve_bool', 'curve_float', 'noncanonical_curve', 'extra_descriptor', 'projection_tuple'):
            e = deepcopy(expected)
            if mutation == 'wrong_p': e['p'] = 7
            elif mutation == 'wrong_curve': e['curve']['a'] = 1
            elif mutation == 'wrong_kind': e['kind'] = 'slack' if kind != 'slack' else 'guard'
            elif mutation == 'wrong_degree': e['k'] = 3 if kind == 'nilpotent' else 1
            elif mutation == 'bool_p': e['p'] = True
            elif mutation == 'singular_curve': e['curve'] = {'a': 0, 'b': 0}
            elif mutation == 'curve_bool': e['curve']['a'] = False
            elif mutation == 'curve_float': e['curve']['b'] = 1.0
            elif mutation == 'noncanonical_curve': e['curve']['b'] = 6
            elif mutation == 'extra_descriptor': e['extra'] = 0
            elif mutation == 'projection_tuple': e['projection'] = tuple(e['projection'])
            result = auth.check_authenticated_assignment(block['circuit'], block['assignment'], e)
            record('public/'+kind+'/'+mutation, 'canonical_authentication',
                   [result['status'], result.get('stage')], ['invalid', 'authentication'], result)
        last = block['circuit']['auxiliaries'][-1]
        for mutation, value in [('missing', None), ('bool', False), ('float', 0.0), ('negative', -1),
                                ('p', block['circuit']['p']), ('string', '0'), ('null', None), ('extra', 0)]:
            assignment = deepcopy(block['assignment'])
            if mutation == 'missing': del assignment[last]
            elif mutation == 'extra': assignment['not_declared'] = 0
            else: assignment[last] = value
            result = auth.check_authenticated_assignment(block['circuit'], assignment, expected)
            record('assignment_parser/'+kind+'/'+mutation, 'assignment_parser',
                   [result['status'], result.get('stage'), result.get('canonical_authenticated'), 'exception_type' in result],
                   ['invalid', 'evaluation', True, True], result)
        assignment = deepcopy(block['assignment'])
        residual_variable = 'beta' if kind == 'slack' else last
        assignment[residual_variable] = (assignment[residual_variable]+1) % block['circuit']['p']
        result = auth.check_authenticated_assignment(block['circuit'], assignment, expected)
        record('assignment_residual/'+kind, 'arithmetic_residual',
               [result['status'], result.get('stage'), result.get('canonical_authenticated'), result.get('obligation')],
               ['invalid', 'evaluation', True, 'nonzero equation residual'], result)
    block = entries[0][1]
    for variable in ('C2.Q0', 'C2.P0', 'D2zero.Q0'):
        assignment = deepcopy(block['assignment'])
        assignment[variable] = (assignment[variable]+1) % 5
        result = auth.check_authenticated_assignment(block['circuit'], assignment, expected_binding(block))
        record('reduction/'+variable, 'arithmetic_residual',
               [result['status'], result.get('obligation')], ['invalid', 'nonzero equation residual'], result)
    for name, arm in [('identity_two_inverse', ARMS[0]), ('finite_two_repeat', ARMS[2]),
                      ('finite_four', ARMS[2]), ('finite_four', ARMS[1])]:
        w, c = cache[(name, arm)]
        for mutation in ('all_zero', 'fixture_specialization', 'metadata'):
            altered = deepcopy(c)
            mutate_circuit(altered['block']['circuit'], mutation, altered['block']['assignment'])
            candidate_result = auth.check_authenticated_chart(w, altered)
            reference_result = checker.reference_check(w, c['recovered'])
            record('chart_authentication/'+name+'/'+arm+'/'+mutation, 'canonical_authentication',
                   [candidate_result['status'], reference_result['status']], ['invalid', 'valid'],
                   {'candidate': candidate_result, 'independent_reference': reference_result,
                    'control': 'Reference acceptance cannot substitute for candidate authentication'})


def signed_cases(cache):
    f = {'id': 'F1_unbalanced_common_root', 'p': 5, 'a': 0, 'b': 1, 't': 0, 's': 1,
         'points': [[0, 1]]*4+[[0, 4]], 'target': None}
    w = witness(f)
    outputs = []
    for beta in (1, 4):
        c = make_candidate(w, f['points'], ARMS[2], beta)
        result = auth.check_authenticated_chart(w, c)
        reference = checker.reference_check(w, c['recovered'])
        outputs.append(c['chart'])
        record('F1/beta'+str(beta)+'/acceptance', 'signed_fidelity', [result['status'], reference['status']], ['valid', 'valid'],
               {'candidate': result, 'reference': reference, 'beta': c['block']['assignment']['beta']})
        record('F1/beta'+str(beta)+'/multiplicities', 'signed_fidelity', result.get('recovered'), [[0, 1]]*4+[[0, 4]])
        audit_block('F1/beta'+str(beta), c['block'], True)
        for label, bad in [('swapped', [[0, 1]]+[[0, 4]]*4), ('balanced_degree4', [[0, 1]]*2+[[0, 4]]*2+[None]),
                           ('near_balanced', [[0, 1]]*3+[[0, 4]]*2)]:
            cc = deepcopy(c)
            cc['recovered'] = bad
            actual = auth.check_authenticated_chart(w, cc)
            ref = checker.reference_check(w, bad)
            record('F1/beta'+str(beta)+'/'+label, 'signed_fidelity', [actual['status'], ref['status']], ['invalid', 'invalid'],
                   {'candidate': actual, 'reference': ref})
    record('F1/same_normalized_chart', 'signed_fidelity', outputs[0], outputs[1])
    for name, arm in [('target_outside_interval', ARMS[2]), ('wrapped_five_balanced', ARMS[0]),
                      ('finite_two_torsion', ARMS[2]), ('finite_five_characteristic5', ARMS[2])]:
        w, c = cache[(name, arm)]
        for mutation in ('wrong_idempotent', 'wrong_recovered_sign', 'noncanonical_U', 'nonmonic_U', 'wrong_norm', 'wrong_stratum'):
            ww, cc = deepcopy(w), deepcopy(c)
            if mutation == 'wrong_idempotent':
                if ww['e']:
                    ww['e'][0] = [(ww['e'][0][0]+2) % ww['curve']['p']]
                else:
                    ww['e'] = [[0]]
            elif mutation == 'wrong_recovered_sign':
                cc['recovered'][0][1] = (cc['recovered'][0][1]+1) % ww['curve']['p']
            elif mutation == 'noncanonical_U': ww['U']['coeffs'][0] += ww['curve']['p']
            elif mutation == 'nonmonic_U': ww['U']['coeffs'][-1] = 2
            elif mutation == 'wrong_norm': ww['A'][0] = (ww['A'][0]+1) % ww['curve']['p']
            elif mutation == 'wrong_stratum': cc['stratum'] = 'linear' if cc['stratum'] != 'linear' else 'zero'
            if mutation in ('noncanonical_U', 'nonmonic_U', 'wrong_norm'):
                cc['chart'] = {k: deepcopy(ww[k]) for k in ('curve', 'interval', 'target', 'k', 'A', 'B', 'U')}
            result = auth.check_authenticated_chart(ww, cc)
            record('signed_mutation/'+name+'/'+mutation, 'signed_mutations', result['status'], 'invalid', result)
    # Fixed format controls report both interfaces separately. No inference that
    # the unused source root-lift list must equal the candidate root-lift list.
    w, c = cache[('wrapped_five_balanced', ARMS[0])]
    for mutation in ('candidate_bad_root', 'candidate_duplicate_root'):
        cc = deepcopy(c)
        if mutation == 'candidate_bad_root': cc['root_lifts'][0][1] = 0
        else: cc['root_lifts'].append(deepcopy(cc['root_lifts'][0]))
        result = auth.check_authenticated_chart(w, cc)
        record(mutation, 'signed_mutations', result['status'], 'invalid', result)


def suite():
    global auth, builders, checker
    sys.path.insert(0, str(ROOT/'research/prime_sat_rationality_authenticated_20261031'))
    import authenticated as auth
    builders, checker = auth.builders, auth.evaluator
    contract = json.loads((ROOT/CONTRACT).read_text())
    stages = [('block_cases', lambda: block_cases(contract)), ('chart_cases', lambda: chart_cases(contract))]
    cache = None
    for name, function in stages:
        try:
            result = function()
            if name == 'chart_cases': cache = result
        except Exception:
            record(name+'/exception', 'suite_failure', traceback.format_exc(), 'no exception')
    if cache is not None:
        for name, function in [('outer_cases', outer_cases), ('authentication_cases', authentication_cases), ('signed_cases', signed_cases)]:
            try:
                function(cache)
            except Exception:
                record(name+'/exception', 'suite_failure', traceback.format_exc(), 'no exception')
    summary = {'checks': len(ROWS), 'passed': sum(row['passed'] for row in ROWS),
               'failed': sum(not row['passed'] for row in ROWS),
               'by_group': {group: {'total': sum(r['group'] == group for r in ROWS),
                                    'failed': sum(r['group'] == group and not r['passed'] for r in ROWS)}
                            for group in sorted(set(r['group'] for r in ROWS))}}
    out = {'schema': 'prime-rationality-authenticated-independent-suite/v1', 'task_id': TASK,
           'summary': summary, 'checks': ROWS,
           'events': {'authenticated_wrapper': auth.EVENTS, 'reviewed_builders': builders.EVENTS,
                      'generic_evaluator': checker.EVENTS, 'shared_arithmetic': auth.q.EVENTS,
                      'independent_review_arithmetic': dict(INDEPENDENT_EVENTS)},
           'scientific_runs': 0, 'solver_instances': 0, 'remote_jobs': 0,
           'field_census': False, 'performance_comparison': False}
    print(json.dumps(out, separators=(',', ':')))
    return int(summary['failed'] != 0)


def supervise(gate_path):
    receipt = json.loads(Path(gate_path).read_text())
    if receipt.get('returncode') != 0 or receipt.get('native_gate_bypassed') is not False:
        raise SystemExit('native checkpoint receipt does not authorize launch')
    outpath = HERE/'independent-results.json'
    data = json.loads(outpath.read_text()) if outpath.exists() else {
        'schema': 'prime-rationality-authenticated-independent-review/v1', 'task_id': TASK,
        'scientific_inputs_sha256': {path: digest(ROOT/path) for path in SCIENCE},
        'sources_read': SCIENCE+POLICY_READS,
        'read_sibling_reports': False, 'blind_from_respected': True,
        'runtime': {'python': sys.version, 'executable': sys.executable, 'platform': platform.platform(),
                    'requested_policy': 'review-adversarial', 'requested_effort': 'xhigh',
                    'actual_model': None, 'actual_model_verified': False, 'actual_effort_verified': False,
                    'inference_amendment': 'coordination/prime_sat_rationality_authenticated_20261031/inference-amendment.yaml'},
        'limits': {'maximum_attempts': 4, 'suite_watchdog_seconds': 240, 'memory_limit_bytes': 2147483648},
        'attempts': []}
    if len(data['attempts']) >= 4:
        raise SystemExit('four-suite-invocation limit exhausted')
    command = [PYTHON, '-B', str(Path(__file__).resolve()), '--suite']
    attempt = {'attempt': len(data['attempts'])+1, 'started_at': now(), 'command': command,
               'cwd': str(ROOT), 'test_source_sha256': digest(__file__),
               'test_source': Path(__file__).read_text(),
               'checkpoint_receipt': str(Path(gate_path).resolve()),
               'checkpoint_receipt_sha256': digest(gate_path), 'state': 'started'}
    data['attempts'].append(attempt)
    outpath.write_text(json.dumps(data, indent=2)+'\n')
    def limits():
        resource.setrlimit(resource.RLIMIT_AS, (2147483648, 2147483648))
    start = time.monotonic()
    try:
        result = subprocess.run(command, cwd=ROOT, capture_output=True, text=True, timeout=240,
                                preexec_fn=limits, env=os.environ | {'PYTHONDONTWRITEBYTECODE': '1'})
        attempt.update(returncode=result.returncode, stdout=result.stdout, stderr=result.stderr, state='finished')
        try:
            parsed = json.loads(result.stdout)
            attempt['suite'] = {key: parsed[key] for key in ('schema', 'task_id', 'summary', 'events')}
            attempt['full_check_rows_location'] = 'JSON-decode this attempt.stdout; checks are preserved there once'
        except json.JSONDecodeError:
            attempt['output_parse_error'] = True
    except subprocess.TimeoutExpired as error:
        attempt.update(returncode=None, state='watchdog_timeout',
                       stdout=error.stdout.decode() if isinstance(error.stdout, bytes) else error.stdout or '',
                       stderr=error.stderr.decode() if isinstance(error.stderr, bytes) else error.stderr or '')
    except Exception:
        attempt.update(returncode=None, state='supervisor_error', stderr=traceback.format_exc(), stdout='')
    attempt.update(finished_at=now(), elapsed_seconds_observation=time.monotonic()-start,
                   child_peak_rss_kib=resource.getrusage(resource.RUSAGE_CHILDREN).ru_maxrss)
    outpath.write_text(json.dumps(data, indent=2)+'\n')
    print(json.dumps({'attempt': attempt['attempt'], 'state': attempt['state'],
                      'returncode': attempt['returncode'],
                      'summary': attempt.get('suite', {}).get('summary'), 'output': str(outpath)}))
    return attempt['returncode'] if type(attempt['returncode']) is int else 2


if __name__ == '__main__':
    if sys.argv[1:] == ['--suite']:
        raise SystemExit(suite())
    if len(sys.argv) == 3 and sys.argv[1] == '--supervise':
        raise SystemExit(supervise(sys.argv[2]))
    raise SystemExit('usage: test_independent.py --supervise NATIVE_GATE_RECEIPT')

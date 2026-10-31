"""Additive binding to reviewed symbolic builders; frozen evaluator unchanged.

Prime p>3 is a caller premise. The expected descriptor is trusted public input,
not metadata extracted from the untrusted submitted circuit. Builder fidelity
remains the separately reviewed mathematical dependency.
"""
from pathlib import Path
import sys

FROZEN = Path(__file__).resolve().parent.parent / 'prime_sat_rationality_software_20261031'
sys.path.insert(0, str(FROZEN))
import rationality as builders
import checker as evaluator
import quotient as q
import signed_recovery

EVENTS = {}
same = evaluator.same
reference_check = evaluator.reference_check


def event(name, amount=1):
    EVENTS[name] = EVENTS.get(name, 0) + amount


def require(condition, message):
    if not condition:
        raise ValueError(message)


def _equal(left, right):
    event('canonical_comparison_nodes')
    if type(left) is not type(right):
        return False
    if type(left) is dict:
        return set(left) == set(right) and all(_equal(left[k], right[k]) for k in left)
    if type(left) is list:
        return len(left) == len(right) and all(_equal(a, b) for a, b in zip(left, right))
    return left == right


def canonical_circuit(public_descriptor):
    """Rebuild symbolic equations with discarded dummy witness values."""
    d = public_descriptor
    require(type(d) is dict and set(d) == {'p','curve','kind','k','projection'}, 'public descriptor schema')
    p = d['p']; require(type(p) is int and p > 3, 'public prime p>3 premise')
    curve = d['curve']
    require(type(curve) is dict and set(curve) == {'a','b'}, 'public curve schema')
    for key in ('a','b'):
        require(type(curve[key]) is int and 0 <= curve[key] < p, 'public canonical '+key)
    a,b = curve['a'],curve['b']
    require((4*a*a*a+27*b*b)%p != 0, 'public nonsingular curve')
    kind,k = d['kind'],d['k']
    require(type(kind) is str and kind in ('nilpotent','guard','slack','constant'), 'public block kind')
    if kind == 'nilpotent':
        require(type(k) is int and 0 <= k <= 5, 'public nilpotent degree')
    else:
        require(k is None, 'public non-nilpotent degree')
    names = ['u'+str(i) for i in range(k)] if kind == 'nilpotent' else (['b0'] if kind == 'constant' else ['A'+str(i) for i in range(4)]+['b0','b1'])
    require(same(d['projection'], names), 'canonical full block projection')
    event('canonical_builder_calls')
    if kind == 'nilpotent':
        block = builders.nilpotent_square_block(k,p,a,b)
    elif kind == 'constant':
        block = builders.constant_B_block({'p':p,'a':a,'b':b},[1])
    else:
        block = builders.linear_B_square_block(p,a,b,kind)
    circuit = block['circuit']
    event('canonical_equations_constructed',len(circuit['equations']))
    event('canonical_terms_constructed',sum(len(e['terms']) for e in circuit['equations']))
    return circuit


def _authenticate(circuit, expected):
    require(type(expected) is dict and set(expected) == {'p','curve','kind','k','inputs','projection'}, 'expected public binding schema')
    d = {k:expected[k] for k in ('p','curve','kind','k','projection')}
    canonical = canonical_circuit(d)
    require(_equal(circuit,canonical), 'canonical circuit content mismatch')
    event('canonical_authentications')


def _failure(error, stage):
    return {'status':'invalid','obligation':str(error),'exception_type':type(error).__name__,'stage':stage}


def check_authenticated_assignment(circuit, assignment, expected):
    try:
        _authenticate(circuit,expected)
    except (ValueError,KeyError,TypeError,IndexError) as error:
        return _failure(error,'authentication')
    result = evaluator.check_assignment(circuit,assignment,expected)
    event('generic_evaluator_calls')
    return {**result,'stage':'evaluation','canonical_authenticated':True}


def _chart(w, candidate):
    require(type(w) is dict, 'source chart mapping')
    k = w['k']
    require(type(k) is int and 0 <= k <= 5, 'outer k exact integer in0..5')
    up,u = q.modulus(w['U'])
    require(len(u) == k+1, 'outer k must equal degree(U)')
    require(up == w['curve']['p'], 'outer quotient field binding')
    event('outer_degree_checks')
    signed_recovery.validate_shape(w['curve'],w['target'],w['A'],w['B'],w['U'])
    require(type(candidate) is dict and set(candidate) == {'arm','stratum','chart','block','root_lifts','recovered'}, 'candidate schema')
    require(same(candidate['chart'],{key:w[key] for key in ('curve','interval','target','k','A','B','U')}), 'normalized chart identity binding')
    B = w['B']; stratum = 'zero' if B == [0] else ('constant' if len(B)==1 else 'linear')
    require(candidate['stratum'] == stratum, 'actual B stratum')
    arm = candidate['arm']
    require(arm in ('uniform_nilpotent_square','stratified_slack_with_nilpotent_zero_B','stratified_guard_with_nilpotent_zero_B'), 'candidate arm')
    if arm == 'uniform_nilpotent_square' or stratum == 'zero':
        kind, degree = 'nilpotent',k
        inputs = {'u'+str(i):v for i,v in enumerate(u[:-1])}
    elif stratum == 'constant':
        kind,degree,inputs = 'constant',None,{'b0':B[0]}
    else:
        kind,degree = ('guard' if arm=='stratified_guard_with_nilpotent_zero_B' else 'slack'),None
        A = w['A']+[0]*(4-len(w['A']))
        inputs = {'A'+str(i):v for i,v in enumerate(A)}
        inputs.update(b0=B[0],b1=B[1])
    block = candidate['block']
    require(type(block) is dict and set(block)=={'circuit','assignment'}, 'block schema')
    curve = w['curve']
    expected = {'p':curve['p'],'curve':{'a':curve['a'],'b':curve['b']},'kind':kind,'k':degree,'inputs':inputs,'projection':list(inputs)}
    _authenticate(block['circuit'],expected)
    # The frozen chart checker performs generic residual evaluation, interval
    # membership, signed reconstruction and exact recovered-output binding.
    result = evaluator.check_candidate_chart(w,candidate)
    event('frozen_chart_checker_calls')
    return {**result,'stage':'chart_evaluation','canonical_authenticated':True}


def check_authenticated_chart(w,candidate):
    try:
        return _chart(w,candidate)
    except (ValueError,KeyError,TypeError,IndexError) as error:
        return _failure(error,'chart_binding_or_authentication')


# Drop-in names for the retained producer fixture suite, not a monkey patch.
check_assignment = check_authenticated_assignment
check_candidate_chart = check_authenticated_chart

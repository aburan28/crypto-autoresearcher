"""Independent IR parser/evaluator and chart binding; no builder arithmetic imported."""
from pathlib import Path
import sys
sys.path.insert(0, str(Path(__file__).resolve().parent.parent/'prime_sat_shared_signed_chart_20261030'))
import quotient as q
import projectors, signed_recovery, check_chart

EVENTS = {}


def event(name):
    EVENTS[name] = EVENTS.get(name, 0)+1


def require(condition, message):
    if not condition:
        raise ValueError(message)


def field_value(value, p, message):
    require(type(value) is int and 0 <= value < p, message)


def same(left, right):
    """Exact JSON-type equality: bool must never alias integer field values."""
    if type(left) is not type(right):
        return False
    if type(left) is dict:
        return set(left) == set(right) and all(same(left[k], right[k]) for k in left)
    if type(left) is list:
        return len(left) == len(right) and all(same(a,b) for a,b in zip(left,right))
    return left == right


def names(value, message):
    require(type(value) is list and all(type(x) is str and x for x in value), message)
    require(len(set(value)) == len(value), message+' uniqueness')
    return value


def _assignment(circuit, assignment, expected):
    required = {'schema','p','curve','kind','k','inputs','auxiliaries','projection','equations','metadata'}
    require(type(circuit) is dict and set(circuit) == required, 'exact circuit schema')
    require(circuit['schema'] == 'prime-rationality-field-circuit/v1', 'schema version')
    p = circuit['p'];require(type(p) is int and p > 3, 'prime p>3 premise')
    require(type(circuit['curve']) is dict and set(circuit['curve']) == {'a','b'}, 'curve schema')
    a, b = circuit['curve']['a'], circuit['curve']['b']
    field_value(a, p, 'curve a');field_value(b, p, 'curve b')
    require((4*a*a*a+27*b*b) % p != 0, 'nonsingular curve')
    require(type(expected) is dict and set(expected) == {'p','curve','kind','k','inputs','projection'}, 'expected binding schema')
    require(type(expected['p']) is int and p == expected['p'], 'external field binding')
    require(same(circuit['curve'], expected['curve']), 'external curve binding')
    kind = circuit['kind'];k = circuit['k']
    require(kind in ('nilpotent','guard','slack','constant') and kind == expected['kind'], 'block kind binding')
    require(same(k, expected['k']), 'degree binding')
    if kind == 'nilpotent':
        require(type(k) is int and 0 <= k <= 5, 'nilpotent degree')
        counts = ([0,3,9,15,21,36][k],)*2
        input_names = ['u'+str(i) for i in range(k)]
    else:
        require(k is None, 'non-nilpotent degree tag')
        counts = {'guard':(10,12),'slack':(9,8),'constant':(1,1)}[kind]
        input_names = ['b0'] if kind == 'constant' else ['A'+str(i) for i in range(4)]+['b0','b1']
    inputs = names(circuit['inputs'], 'input names')
    auxiliaries = names(circuit['auxiliaries'], 'auxiliary names')
    projection = names(circuit['projection'], 'projection names')
    require(inputs == input_names and not set(inputs)&set(auxiliaries), 'input roles and disjoint names')
    require(set(projection) <= set(inputs) and projection == expected['projection'], 'external projection binding')
    require(type(expected['inputs']) is dict and set(expected['inputs']) == set(inputs), 'external input schema')
    require(type(assignment) is dict and set(assignment) == set(inputs+auxiliaries), 'complete assignment keys')
    # Eager validation covers every value before testing any equation.
    for name in inputs+auxiliaries:
        field_value(assignment[name], p, 'canonical assignment '+name)
    for name in inputs:
        field_value(expected['inputs'][name], p, 'canonical expected input '+name)
        require(assignment[name] == expected['inputs'][name], 'input value binding '+name)
    equations = circuit['equations']
    require(type(equations) is list and len(equations) == counts[1] and len(auxiliaries) == counts[0], 'fixed symbolic block size')
    labels = [];parsed = [];degrees = []
    for eq in equations:
        require(type(eq) is dict and set(eq) == {'label','terms'}, 'equation schema')
        label = eq['label'];require(type(label) is str and label and label not in labels, 'unique equation label')
        labels.append(label);require(type(eq['terms']) is list, 'term list')
        monomials = [];terms = []
        for term in eq['terms']:
            require(type(term) is dict and set(term) == {'coefficient','variables'}, 'term schema')
            c = term['coefficient'];field_value(c, p, 'canonical polynomial coefficient')
            require(c != 0, 'omit zero coefficient terms')
            variables = term['variables']
            require(type(variables) is list and all(type(n) is str and n in assignment for n in variables), 'declared monomial variables')
            require(variables == sorted(variables) and len(variables) <= 2, 'quadratic canonical monomial')
            m = tuple(variables);require(m not in monomials, 'unique monomial')
            monomials.append(m);terms.append((c,m))
        require(monomials == sorted(monomials), 'deterministic term ordering')
        parsed.append(terms);degrees.append(max((len(m) for c,m in terms), default=0))
    require(type(circuit['metadata']) is dict and set(circuit['metadata']) == {'blocks'}, 'metadata schema')
    require(circuit['metadata']['blocks'] == [{'name':kind,'auxiliaries':auxiliaries,'equations':labels}], 'obligation ownership')
    residuals = []
    for label, terms in zip(labels, parsed):
        total = 0
        for c, m in terms:
            value = c
            for name in m:
                value = value*assignment[name] % p;event('IR_field_multiply')
            total = (total+value) % p;event('IR_field_add')
        residuals.append({'label':label,'value':total})
    return {'status':'valid' if all(x['value'] == 0 for x in residuals) else 'invalid',
            'obligation':None if all(x['value'] == 0 for x in residuals) else 'nonzero equation residual',
            'counts':{'inputs':len(inputs),'auxiliaries':len(auxiliaries),'equations':len(equations),'maximum_total_degree':max(degrees,default=0)},
            'residuals':residuals}


def check_assignment(circuit, assignment, expected):
    try:
        return _assignment(circuit, assignment, expected)
    except (ValueError, KeyError, TypeError, IndexError) as error:
        return {'status':'invalid','obligation':str(error),'exception_type':type(error).__name__}
    except Exception as error:
        return {'status':'error','obligation':str(error),'exception_type':type(error).__name__}


def _chart(w, candidate):
    require(type(candidate) is dict and set(candidate) == {'arm','stratum','chart','block','root_lifts','recovered'}, 'candidate chart schema')
    p = w['curve']['p'];a = w['curve']['a'];b = w['curve']['b']
    signed_recovery.validate_shape(w['curve'],w['target'],w['A'],w['B'],w['U'])
    expected_chart = {key:w[key] for key in ('curve','interval','target','k','A','B','U')}
    require(same(candidate['chart'], expected_chart), 'normalized chart identity binding')
    stratum = 'zero' if w['B'] == [0] else 'constant' if len(w['B']) == 1 else 'linear'
    require(candidate['stratum'] == stratum, 'actual B stratum')
    arm = candidate['arm']
    require(arm in ('uniform_nilpotent_square','stratified_slack_with_nilpotent_zero_B','stratified_guard_with_nilpotent_zero_B'), 'candidate arm')
    if arm == 'uniform_nilpotent_square' or stratum == 'zero':
        kind = 'nilpotent';k = w['k'];inputs = {'u'+str(i):v for i,v in enumerate(w['U']['coeffs'][:-1])}
    elif stratum == 'constant':
        kind = 'constant';k = None;inputs = {'b0':w['B'][0]}
    else:
        kind = 'guard' if 'guard' in arm else 'slack';k = None
        aa = w['A']+[0]*(4-len(w['A']));inputs = {'A'+str(i):v for i,v in enumerate(aa)}
        inputs.update({'b0':w['B'][0],'b1':w['B'][1]})
    require(type(candidate['block']) is dict and set(candidate['block']) == {'circuit','assignment'}, 'block bundle schema')
    expected = {'p':p,'curve':{'a':a,'b':b},'kind':kind,'k':k,'inputs':inputs,'projection':list(inputs)}
    block = check_assignment(candidate['block']['circuit'],candidate['block']['assignment'],expected)
    require(block['status'] == 'valid', 'candidate field equations: '+str(block.get('obligation')))
    # Membership/splitting is checked without the Euler rationality predicate.
    q.verify_quotient_witness(w['U'],w['interval']['t'],w['interval']['s'],w['e'])
    factors = projectors.recover_interval_factors(w['U'],w['interval']['t'],w['interval']['s'],w['e'])
    recovered = signed_recovery.recover_signed_divisor(w['curve'],w['target'],w['A'],w['B'],w['U'],factors,candidate['root_lifts'])
    require(same(candidate['recovered'], recovered), 'candidate signed reconstruction binding')
    event('candidate_chart_check')
    return {'status':'valid','obligation':None,'counts':block['counts'],'recovered':recovered,
            'projection_kind':'normalized A/B with outer chart tags; block projection is local only'}


def check_candidate_chart(w, candidate):
    """Candidate arithmetic and membership checks; no full Euler reference call."""
    try:
        return _chart(w, candidate)
    except (ValueError, KeyError, TypeError, IndexError) as error:
        return {'status':'invalid','obligation':str(error),'exception_type':type(error).__name__}
    except Exception as error:
        return {'status':'error','obligation':str(error),'exception_type':type(error).__name__}


def reference_check(w, recovered):
    """Explicitly separate frozen Euler/local-series cross-check and its events."""
    event('full_reference_chart_check')
    return check_chart.check_chart(w,recovered)

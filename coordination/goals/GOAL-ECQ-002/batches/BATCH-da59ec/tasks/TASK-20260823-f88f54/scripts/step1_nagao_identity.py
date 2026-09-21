#!/usr/bin/env python3
"""STEP 1 -- symbolic re-verification of the NAGAO-1994 self-consistency identity.

Reads the transcribed quartic and the published section straight from
BATCH-f2341e's candidate_families.json (no coefficient is retyped here), and
checks SYMBOLICALLY, at all seven coefficients t^0..t^6, whether

    Q(x=(t+703)/15, t) * 15^4   ==   ratio * 9 * N(t)^2 ,
    N(t) = -224 t^3 - 844 t^2 + 900484 t + 2161725

with a CONSTANT rational ratio, and whether that ratio is 1557504 = 1248^2,
i.e. whether the point ( (t+703)/15 , 1248*N(t)/75 ) lies on the quartic.

Exact integer arithmetic, stdlib only.  Output: JSON to stdout/OUT.
"""
import json, re, sys
from fractions import Fraction as F

SRC = ('/home/user/crypto-autoresearcher/coordination/goals/GOAL-ECQ-002/batches/'
       'BATCH-f2341e/tasks/TASK-20260823-d1cb76/candidate_families.json')

# --- minimal dense univariate polynomial arithmetic over Q -------------------
def padd(a, b):
    n = max(len(a), len(b))
    return [ (a[i] if i < len(a) else 0) + (b[i] if i < len(b) else 0) for i in range(n) ]
def pmul(a, b):
    out = [F(0)] * (len(a) + len(b) - 1)
    for i, x in enumerate(a):
        if x == 0: continue
        for j, y in enumerate(b):
            out[i + j] += x * y
    return out
def pscal(a, c):
    return [c * x for x in a]
def ppow(a, n):
    r = [F(1)]
    for _ in range(n): r = pmul(r, a)
    return r
def trim(a):
    while len(a) > 1 and a[-1] == 0: a.pop()
    return a

def parse_poly_in_t(s):
    """Parse expressions like '330112972800 + 14017536*t^2' into coeff list."""
    s = s.replace('-', '+-').replace(' ', '')
    terms = [x for x in s.split('+') if x]
    coeffs = {}
    for term in terms:
        m = re.fullmatch(r'(-?\d*)\*?t\^(\d+)', term)
        if m:
            c = m.group(1); c = -1 if c == '-' else (1 if c == '' else int(c))
            coeffs[int(m.group(2))] = coeffs.get(int(m.group(2)), 0) + c
            continue
        m = re.fullmatch(r'(-?\d*)\*?t', term)
        if m:
            c = m.group(1); c = -1 if c == '-' else (1 if c == '' else int(c))
            coeffs[1] = coeffs.get(1, 0) + c
            continue
        m = re.fullmatch(r'-?\d+', term)
        if m:
            coeffs[0] = coeffs.get(0, 0) + int(term)
            continue
        raise ValueError('unparsed term: %r' % term)
    d = max(coeffs)
    return [F(coeffs.get(i, 0)) for i in range(d + 1)]

def main(out_path=None):
    db = json.load(open(SRC))
    fam = next(x for x in db['families'] if x['id'] == 'NAGAO-1994')
    wc = fam['weierstrass_coefficients_in_t']
    quartic = {k: parse_poly_in_t(wc[k]) for k in ('c4', 'c3', 'c2', 'c1', 'c0')}
    pt = fam['published_section_retrieved']['point']

    # x = (t+703)/15  as a polynomial over Q ; N(t) from the published section
    X = [F(703, 15), F(1, 15)]
    N = [F(2161725), F(900484), F(-844), F(-224)]

    # sanity: the section string in the record really is ((t+703)/15, N(t)/75)
    assert '(t + 703)/15' in pt and '-224*t^3 - 844*t^2 + 900484*t + 2161725' in pt, pt

    RHS = [F(0)]
    for k, name in ((4, 'c4'), (3, 'c3'), (2, 'c2'), (1, 'c1'), (0, 'c0')):
        RHS = padd(RHS, pmul(quartic[name], ppow(X, k)))
    RHS = pscal(RHS, F(15 ** 4))          # multiply through by 15^4 = 50625
    LEFT = pscal(pmul(N, N), F(9))        # 50625 * (N/75)^2 = 9 N^2
    RHS, LEFT = trim(RHS), trim(LEFT)

    n = max(len(RHS), len(LEFT))
    per_coeff, ratios = [], []
    for i in range(n):
        r = RHS[i] if i < len(RHS) else F(0)
        l = LEFT[i] if i < len(LEFT) else F(0)
        rat = (r / l) if l != 0 else None
        per_coeff.append({'power_of_t': i, 'left_9Nsq': str(l), 'right_quartic': str(r),
                          'ratio_right_over_left': (str(rat) if rat is not None else None)})
        if l != 0 or r != 0:
            ratios.append(rat)
    constant = (len(set(map(str, ratios))) == 1 and ratios[0] is not None)
    ratio = ratios[0] if constant else None

    # the actual on-curve statement: y = 1248*N/75
    Y = pscal(N, F(1248, 75))
    Q_at_X = trim([c / F(15 ** 4) for c in RHS])   # undo the 15^4 scaling
    on_curve = trim(padd(Q_at_X, pscal(pmul(Y, Y), F(-1))))
    exact_on_curve = all(c == 0 for c in on_curve)

    res = {
      'step': 1,
      'what': 'symbolic re-verification of the NAGAO-1994 self-consistency identity',
      'source_file': SRC,
      'source_transcription_status': wc['TRANSCRIPTION_STATUS'],
      'point_tested': '((t+703)/15, 1248*N(t)/75)',
      'N_of_t': '-224*t^3 - 844*t^2 + 900484*t + 2161725',
      'identity_tested': '15^4 * Q((t+703)/15, t)  vs  9*N(t)^2, coefficientwise in t',
      'n_coefficients_compared': n,
      'per_coefficient': per_coeff,
      'ratio_is_constant_across_all_coefficients': constant,
      'ratio': str(ratio) if ratio is not None else None,
      'ratio_equals_1557504': (ratio == 1557504),
      'ratio_is_1248_squared': (ratio == 1248 ** 2),
      'point_lies_exactly_on_transcribed_quartic': exact_on_curve,
      'coordinator_claim_reproduced': bool(constant and ratio == 1557504 and exact_on_curve),
      'batch_f2341e_verdict': fam['internal_consistency_check_run_here']['verdict'],
      'batch_f2341e_t6_left': fam['internal_consistency_check_run_here']['t6_left'],
      'batch_f2341e_t6_right': fam['internal_consistency_check_run_here']['t6_right'],
    }
    js = json.dumps(res, indent=1)
    print(js)
    if out_path: open(out_path, 'w').write(js)
    return 0 if res['coordinator_claim_reproduced'] else 3

if __name__ == '__main__':
    sys.exit(main(sys.argv[1] if len(sys.argv) > 1 else None))

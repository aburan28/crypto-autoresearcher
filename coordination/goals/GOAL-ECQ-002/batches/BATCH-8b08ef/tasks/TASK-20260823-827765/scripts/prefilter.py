#!/usr/bin/env python3
"""
THE SQUAREFREE-DISCRIMINANT PRE-FILTER, applied BEFORE any height evaluation,
any Mestre-Nagao ordering and any rank search (EXP-ECQ-0e0cbb step_1).

WHAT IT IS
----------
For an admissible family, form the minimal Weierstrass model over Q[T] and its
discriminant DD(T) over the FINITE T-line (degree 20 for d = 2).  The filter is
ONE SQUAREFREENESS TEST on DD:

    Res(DD, DD') != 0   <=>   DD squarefree   <=>   deg gcd(DD, DD') = 0

and the quantitative version is the degree of that gcd.  It is implemented as a
polynomial gcd rather than by forming the resultant integer, because the two
decide the SAME predicate and the resultant of a degree-20 polynomial with
coefficients of this size is an integer with thousands of digits that is
computed only to be compared with zero.  `resultant_cross_check()` forms the
resultant explicitly on a sample and confirms the two agree, so the identity is
exercised rather than asserted.

WHY IT IS SOUND -- NO FALSE NEGATIVES, BY CONSTRUCTION
------------------------------------------------------
Write G = gcd(DD, DD').  In residue characteristic 0, G = prod_v p_v^(N_v - 1)
over the finite places v with N_v = v(DD) >= 1, so

    deg G = sum_{finite v} deg(v) * (N_v - 1).                         (*)

For a MULTIPLICATIVE fibre (v(a4) = 0) the Kodaira type is I_{N_v} and
m_v = N_v, so deg(v)(m_v - 1) = deg(v)(N_v - 1): the term in (*) is EXACT.
For every ADDITIVE type in the characteristic-0 table -- II (N=2,m=1),
III (3,2), IV (4,3), I_0* (6,5), I_n* (n+6,n+5), IV* (8,7), III* (9,8),
II* (10,9) -- one has m_v = N_v - 1, so deg(v)(m_v - 1) < deg(v)(N_v - 1) and
the term in (*) OVERSTATES the true reducible contribution.

Therefore, letting S_fin = sum_{finite v} deg(v)(m_v - 1),

    S_fin <= deg G, with EQUALITY when no repeated fibre is additive.

Additivity of a repeated fibre is detected by ONE MORE GCD: a repeated place
p_v is additive exactly when v(a4) >= 1, i.e. when p_v | gcd(G, a4).  So:

  * deg gcd(G, a4) = 0  =>  S_fin = deg G EXACTLY, and
        ceiling = (10d - 2) - deg G - (m_infinity - 1)
    is DECIDED without any factorisation.  Discard iff that value < 13.
  * deg gcd(G, a4) > 0  =>  some repeated fibre may be additive, the cheap
    bound is only an upper bound on S_fin, and the family is RETAINED and
    marked `undecidable_cheaply`.  A retained family costs measurement time;
    it never costs a false negative.

Consequently the pre-filter CANNOT discard a family of ceiling >= 13.  That is
a proof, and CTL-PREFILTER-SOUNDNESS additionally CHECKS it empirically against
the full fibre census of every enumerated family.

WHAT IT IS NOT
--------------
IT IS AN EFFICIENCY HEURISTIC, NEVER AN IMPOSSIBILITY CLAIM.  The Shioda-Tate
ceiling bounds the GENERIC rank over Qbar(T); a specialisation over Q is at
least the generic rank and CAN EXCEED IT (KN-FIND-6b3e17).  Nothing here says,
or may be read as saying, that a discarded family cannot host a rank-12
specialisation over Q.  Discarded families are discarded for cost alone.

The fibre at T = infinity is NOT the steerable quantity: it is I_4 on 13352 of
13391 measured families and stratifies nothing.  It is computed here only
because it enters the ceiling, and it is read from (v(a4), v(a6), v(DD)) at
infinity, never assumed.
"""
import time

import cypari

import surface

pari = cypari.pari

CEILING_TARGET = 13          # pre-declared in H-ECQ-0ed5c8; frozen


def prefilter(r_coeffs, ceiling_target=CEILING_TARGET):
    """One squarefreeness test on the finite discriminant.  Never factors.

    Returns a dict recording the decision, the quantities behind it, and the
    measured cost.  `decision` is 'retained' or 'discarded'.
    """
    t0 = time.time()
    out = {'ceiling_target': ceiling_target}
    a4, a6 = surface.a4a6_over_QT(r_coeffs)
    pari('Q4 = %s' % surface.poly_str(a4))
    pari('Q6 = %s' % surface.poly_str(a6))
    # minimalise over Q[T]: strip p^4 | a4 and p^6 | a6.  gcd-driven, no
    # factorisation of the discriminant.
    removed = 0
    while True:
        if int(pari('poldegree(gcd(Q4, Q6))')) <= 0:
            break
        fg = pari('fgg = factor(gcd(Q4, Q6))')
        nf = int(pari('matsize(fgg)[1]'))
        did = False
        for i in range(1, nf + 1):
            p = pari('fgg[%d,1]' % i)
            if int(pari('poldegree(%s)' % p)) <= 0:
                continue
            k = min(int(pari('valuation(Q4, %s)' % p)) // 4,
                    int(pari('valuation(Q6, %s)' % p)) // 6)
            if k >= 1:
                pari('Q4 = Q4/(%s)^%d; Q6 = Q6/(%s)^%d' % (p, 4 * k, p, 6 * k))
                removed += 1
                did = True
                break
        if not did:
            break
    d4 = int(pari('poldegree(Q4)'))
    d6 = int(pari('poldegree(Q6)'))
    d = max(-(-d4 // 4), -(-d6 // 6))
    pari('DDF = -16*(4*Q4^3 + 27*Q6^2)')
    if int(pari('DDF == 0')):
        out.update(decision='discarded', reason='degenerate_zero_discriminant',
                   surface_degree_d=d, prefilter_seconds=time.time() - t0)
        return out
    degD = int(pari('poldegree(DDF)'))
    # --- THE FILTER: one squarefreeness test on the degree-20 finite disc ---
    deg_gcd = int(pari('poldegree(gcd(DDF, deriv(DDF)))'))
    squarefree = (deg_gcd == 0)
    deg_gcd_a4 = int(pari('poldegree(gcd(gcd(DDF, deriv(DDF)), Q4))'))
    # the place at infinity, read from its own valuations (never assumed)
    Ai, Bi, Ni = 4 * d - d4, 6 * d - d6, 12 * d - degD
    typ_inf, m_inf = surface.kodaira(Ai, Bi, Ni)
    out.update({
        'surface_degree_d': d,
        'deg_a4': d4, 'deg_a6': d6,
        'n_square_factors_removed_minimalising': removed,
        'deg_finite_discriminant': degD,
        'resultant_test': {
            'predicate': 'Res(DD, DD_prime) != 0  <=>  DD squarefree',
            'implemented_as': 'deg gcd(DD, DD_prime) == 0 (same predicate; the '
                              'resultant integer is formed only in '
                              'resultant_cross_check())',
            'deg_gcd_DD_DDprime': deg_gcd,
            'finite_discriminant_squarefree': squarefree,
        },
        'deg_gcd_repeated_part_with_a4': deg_gcd_a4,
        'fibre_at_infinity': {'v_a4': Ai, 'v_a6': Bi, 'v_disc': Ni,
                              'type': typ_inf, 'm_v': m_inf},
    })
    if m_inf is None:
        out.update(decision='retained',
                   reason='fibre_at_infinity_unclassified_cannot_decide_cheaply',
                   cheap_ceiling=None)
    elif deg_gcd_a4 > 0:
        # a repeated fibre may be ADDITIVE: deg G only bounds S_fin from above,
        # so the ceiling is not decided.  RETAIN -- never a false negative.
        out.update(decision='retained',
                   reason='repeated_fibre_may_be_additive_undecidable_cheaply',
                   cheap_ceiling=None,
                   cheap_ceiling_lower_bound=(10 * d - 2) - deg_gcd - (m_inf - 1))
    else:
        ceil_exact = (10 * d - 2) - deg_gcd - (m_inf - 1)
        out['cheap_ceiling'] = ceil_exact
        out['cheap_ceiling_is_exact'] = True
        if ceil_exact >= ceiling_target:
            out.update(decision='retained',
                       reason='ceiling_at_or_above_target_%d' % ceiling_target)
        else:
            out.update(decision='discarded',
                       reason='finite_discriminant_far_from_squarefree_'
                              'ceiling_%d_below_target_%d'
                              % (ceil_exact, ceiling_target))
    out['prefilter_seconds'] = time.time() - t0
    return out


def resultant_cross_check(r_coeffs):
    """Form Res(DD, DD') EXPLICITLY and confirm it agrees with the gcd test.

    Exercised on a sample only: the resultant is a several-thousand-digit
    integer whose only use is comparison with zero.
    """
    a4, a6 = surface.a4a6_over_QT(r_coeffs)
    pari('R4 = %s' % surface.poly_str(a4))
    pari('R6 = %s' % surface.poly_str(a6))
    pari('RD = -16*(4*R4^3 + 27*R6^2)')
    res_zero = bool(int(pari('polresultant(RD, deriv(RD)) == 0')))
    gcd_zero = int(pari('poldegree(gcd(RD, deriv(RD)))')) > 0
    return {'resultant_is_zero': res_zero,
            'gcd_degree_positive': gcd_zero,
            'agree': res_zero == gcd_zero,
            'resultant_n_decimal_digits':
                len(str(pari('polresultant(RD, deriv(RD))')).lstrip('-'))}

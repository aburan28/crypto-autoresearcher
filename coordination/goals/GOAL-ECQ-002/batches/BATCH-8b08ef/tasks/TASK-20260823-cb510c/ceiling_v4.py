#!/usr/bin/env python3
"""
VALIDATOR CEILING COMPUTATION - V4
Uses ellfromeqn to get Weierstrass model, then minimalises at infinity
by dividing by appropriate powers of T (u = T^k transformation).
"""
from cypari import pari

def compute_ceiling_v4(tuple_vals):
    pari.allocatemem(1 << 28, silent=True)
    
    a = tuple_vals
    
    # Build q(x) = prod(x - a_i)
    q_terms = " * ".join([f"(x - ({ai}))" for ai in a])
    pari(f'q = {q_terms}')
    
    # p(x, t) = q(x-t) * q(x+t)
    pari('qt = subst(q, x, x - t)')
    pari('qpt = subst(q, x, x + t)')
    pari('p = qt * qpt')
    
    # Compute g by coefficient matching
    pari('p11 = polcoeff(p, 11, x)')
    pari('p10 = polcoeff(p, 10, x)')
    pari('p9 = polcoeff(p, 9, x)')
    pari('p8 = polcoeff(p, 8, x)')
    pari('p7 = polcoeff(p, 7, x)')
    pari('p6 = polcoeff(p, 6, x)')
    
    pari('g5 = p11 / 2')
    pari('g4 = (p10 - g5^2) / 2')
    pari('g3 = (p9 - 2*g5*g4) / 2')
    pari('g2 = (p8 - g4^2 - 2*g5*g3) / 2')
    pari('g1 = (p7 - 2*g5*g2 - 2*g4*g3) / 2')
    pari('g0 = (p6 - g3^2 - 2*g5*g1 - 2*g4*g2) / 2')
    
    pari('g = x^6 + g5*x^5 + g4*x^4 + g3*x^3 + g2*x^2 + g1*x + g0')
    pari('r = g^2 - p')
    deg_r = int(pari('poldegree(r, x)'))
    
    # Convert to Weierstrass form
    pari('E = ellfromeqn(y^2 - r)')
    
    # Get the Weierstrass coefficients
    pari('a1p = E[1]')
    pari('a2p = E[2]')
    pari('a3p = E[3]')
    pari('a4p = E[4]')
    pari('a6p = E[5]')
    
    # Compute the discriminant manually
    pari('b2 = a1p^2 + 4*a2p')
    pari('b4 = 2*a4p + a1p*a3p')
    pari('b6 = a3p^2 + 4*a6p')
    pari('b8 = a1p^2*a6p + 4*a2p*a6p - a1p*a3p*a4p + a2p*a3p^2 - a4p^2')
    pari('DD_full = -b2^2*b8 - 8*b4^3 - 27*b6^2 + 9*b2*b4*b6')
    
    deg_a1 = int(pari('poldegree(a1p, t)'))
    deg_a2 = int(pari('poldegree(a2p, t)'))
    deg_a3 = int(pari('poldegree(a3p, t)'))
    deg_a4 = int(pari('poldegree(a4p, t)'))
    deg_a6 = int(pari('poldegree(a6p, t)'))
    deg_DD_full = int(pari('poldegree(DD_full, t)'))
    
    # Minimalise at infinity: find the largest k such that
    # a1/T^k, a2/T^(2k), a3/T^(3k), a4/T^(4k), a6/T^(6k) are all polynomials
    # This means T^k | a1, T^(2k) | a2, T^(3k) | a3, T^(4k) | a4, T^(6k) | a6
    
    # Check divisibility by powers of T
    # v_T(f) = order of vanishing at T=0 = lowest degree of T in f
    # For a polynomial, v_T(f) = the minimum degree of T among all terms
    
    def v_T(var_name):
        """Compute the T-adic valuation of a polynomial."""
        try:
            pari(f'v = valuation({var_name}, t)')
            return int(pari('v'))
        except:
            return 0
    
    v_a1 = v_T('a1p')
    v_a2 = v_T('a2p')
    v_a3 = v_T('a3p')
    v_a4 = v_T('a4p')
    v_a6 = v_T('a6p')
    v_DD = v_T('DD_full')
    
    # The minimalisation at infinity uses u = T^k where
    # k = max(ceil(v_a1/1), ceil(v_a2/2), ceil(v_a3/3), ceil(v_a4/4), ceil(v_a6/6))
    # But actually, for the place at INFINITY (not T=0), we need to consider
    # the valuations at T=infinity, which are related to the degrees.
    
    # For the place at infinity, v_inf(f) = -deg(f) for a polynomial f.
    # The minimalisation at infinity uses u = (1/T)^k = T^(-k), so
    # the transformed a_i' = a_i * T^(i*k) (for the standard transformation).
    # We need a_i' to be polynomials, so we need T^(i*k) to cancel the poles.
    # v_inf(a_i') = v_inf(a_i) + i*k = -deg(a_i) + i*k >= 0
    # So k >= deg(a_i) / i for each i.
    
    import math
    k = max(
        math.ceil(deg_a1 / 1) if deg_a1 > 0 else 0,
        math.ceil(deg_a2 / 2) if deg_a2 > 0 else 0,
        math.ceil(deg_a3 / 3) if deg_a3 > 0 else 0,
        math.ceil(deg_a4 / 4) if deg_a4 > 0 else 0,
        math.ceil(deg_a6 / 6) if deg_a6 > 0 else 0,
    )
    
    # Apply the minimalisation: u = T^(-k), so a_i' = a_i * T^(i*k)
    # But we need to check that a_i * T^(i*k) is a polynomial, which it is
    # since deg(a_i) <= i*k.
    
    # The minimal discriminant is DD_full * T^(12*k) / (leading coefficient adjustments)
    # Actually, Delta' = Delta / u^12 = Delta * T^(12*k)
    # But Delta has degree deg_DD_full, and after multiplying by T^(12*k),
    # the degree becomes deg_DD_full + 12*k, which is WRONG.
    
    # I think I have the direction wrong. Let me reconsider.
    # The transformation x -> u^2*x, y -> u^3*y with u = T^k gives:
    # a_i' = a_i / u^i = a_i / T^(i*k)
    # Delta' = Delta / u^12 = Delta / T^(12*k)
    # For this to give polynomials, we need T^(i*k) | a_i.
    # The valuation at T=0: v_T(a_i) >= i*k
    
    # So the correct k is:
    # k = min(v_a1//1, v_a2//2, v_a3//3, v_a4//4, v_a6//6)
    
    k = min(
        v_a1 // 1 if v_a1 > 0 else 0,
        v_a2 // 2 if v_a2 > 0 else 0,
        v_a3 // 3 if v_a3 > 0 else 0,
        v_a4 // 4 if v_a4 > 0 else 0,
        v_a6 // 6 if v_a6 > 0 else 0,
    )
    
    # Apply minimalisation at T=0 (which corresponds to the place at infinity
    # after the substitution T -> 1/T)
    # Wait, I'm confusing T=0 with T=infinity again.
    
    # Let me think about this more carefully.
    # The Weierstrass model has coefficients that are polynomials in T.
    # The place at infinity on the T-line corresponds to T = infinity.
    # To minimalise at T = infinity, we substitute T = 1/s and look at s = 0.
    # After T = 1/s, the coefficients become Laurent polynomials in s.
    # The valuation at s = 0 is v_s(a_i) = -deg_T(a_i).
    # The minimalisation uses u = s^k = (1/T)^k, so a_i' = a_i * s^(i*k) = a_i / T^(i*k).
    # For a_i' to be a polynomial in s (i.e., regular at s=0), we need:
    # v_s(a_i') = v_s(a_i) + i*k = -deg_T(a_i) + i*k >= 0
    # So k >= deg_T(a_i) / i.
    
    # The minimal k is:
    k_inf = max(
        math.ceil(deg_a1 / 1) if deg_a1 > 0 else 0,
        math.ceil(deg_a2 / 2) if deg_a2 > 0 else 0,
        math.ceil(deg_a3 / 3) if deg_a3 > 0 else 0,
        math.ceil(deg_a4 / 4) if deg_a4 > 0 else 0,
        math.ceil(deg_a6 / 6) if deg_a6 > 0 else 0,
    )
    
    # After minimalisation at infinity with u = (1/T)^k_inf:
    # a_i' = a_i / T^(i*k_inf) (these are polynomials since deg(a_i) <= i*k_inf)
    # Delta' = Delta / T^(12*k_inf)
    # deg(Delta') = deg(Delta) - 12*k_inf
    
    # But we also need to check if there's further minimalisation at T=0
    # (i.e., at the finite place T=0)
    
    # First, apply the infinity minimalisation
    pari(f'a1m = a1p / t^({k_inf * 1})')
    pari(f'a2m = a2p / t^({k_inf * 2})')
    pari(f'a3m = a3p / t^({k_inf * 3})')
    pari(f'a4m = a4p / t^({k_inf * 4})')
    pari(f'a6m = a6p / t^({k_inf * 6})')
    
    # Compute minimal discriminant
    pari('b2m = a1m^2 + 4*a2m')
    pari('b4m = 2*a4m + a1m*a3m')
    pari('b6m = a3m^2 + 4*a6m')
    pari('b8m = a1m^2*a6m + 4*a2m*a6m - a1m*a3m*a4m + a2m*a3m^2 - a4m^2')
    pari('DD_min = -b2m^2*b8m - 8*b4m^3 - 27*b6m^2 + 9*b2m*b4m*b6m')
    
    deg_DD_min = int(pari('poldegree(DD_min, t)'))
    deg_a4m = int(pari('poldegree(a4m, t)'))
    deg_a6m = int(pari('poldegree(a6m, t)'))
    
    # Now check if there's further minimalisation at T=0
    v_a1m = v_T('a1m')
    v_a2m = v_T('a2m')
    v_a3m = v_T('a3m')
    v_a4m = v_T('a4m')
    v_a6m = v_T('a6m')
    
    k_zero = min(
        v_a1m // 1 if v_a1m > 0 else 0,
        v_a2m // 2 if v_a2m > 0 else 0,
        v_a3m // 3 if v_a3m > 0 else 0,
        v_a4m // 4 if v_a4m > 0 else 0,
        v_a6m // 6 if v_a6m > 0 else 0,
    )
    
    if k_zero > 0:
        # Further minimalisation at T=0
        pari(f'a1m2 = a1m / t^({k_zero * 1})')
        pari(f'a2m2 = a2m / t^({k_zero * 2})')
        pari(f'a3m2 = a3m / t^({k_zero * 3})')
        pari(f'a4m2 = a4m / t^({k_zero * 4})')
        pari(f'a6m2 = a6m / t^({k_zero * 6})')
        pari('b2m2 = a1m2^2 + 4*a2m2')
        pari('b4m2 = 2*a4m2 + a1m2*a3m2')
        pari('b6m2 = a3m2^2 + 4*a6m2')
        pari('b8m2 = a1m2^2*a6m2 + 4*a2m2*a6m2 - a1m2*a3m2*a4m2 + a2m2*a3m2^2 - a4m2^2')
        pari('DD_min2 = -b2m2^2*b8m2 - 8*b4m2^3 - 27*b6m2^2 + 9*b2m2*b4m2*b6m2')
        deg_DD_min = int(pari('poldegree(DD_min2, t)'))
        deg_a4m = int(pari('poldegree(a4m2, t)'))
        deg_a6m = int(pari('poldegree(a6m2, t)'))
        pari('DD_min = DD_min2')
        pari('a4m = a4m2')
        pari('a6m = a6m2')
    
    # Now compute the ceiling from the minimal model
    # DD_min is the finite discriminant
    # gcd(DD_min, DD_min') gives the repeated roots
    pari('DDp = deriv(DD_min, t)')
    pari('G = gcd(DD_min, DDp)')
    deg_G = int(pari('poldegree(G, t)'))
    
    # Check for additive fibres: gcd(G, a4)
    try:
        pari('Ga4 = gcd(G, a4m)')
        deg_Ga4 = int(pari('poldegree(Ga4, t)'))
    except:
        deg_Ga4 = 0
    
    # Fibre at infinity: v_inf(disc) = 24 - deg(DD_min)
    v_inf_disc = 24 - deg_DD_min
    euler_check = deg_DD_min + v_inf_disc
    
    m_inf = v_inf_disc
    fibre_type_inf = f'I_{v_inf_disc}' if v_inf_disc > 0 else 'I_0'
    
    ceiling = 18 - deg_G - (m_inf - 1)
    
    return {
        'tuple': tuple_vals,
        'deg_r_in_x': deg_r,
        'nonminimal_degrees': {'a1': deg_a1, 'a2': deg_a2, 'a3': deg_a3, 'a4': deg_a4, 'a6': deg_a6, 'DD': deg_DD_full},
        'k_inf_minimalisation': k_inf,
        'k_zero_minimalisation': k_zero,
        'minimal_degrees': {'a4': deg_a4m, 'a6': deg_a6m, 'DD': deg_DD_min},
        'deg_finite_discriminant': deg_DD_min,
        'deg_gcd_DD_DDprime': deg_G,
        'finite_discriminant_squarefree': deg_G == 0,
        'v_inf_disc': v_inf_disc,
        'fibre_at_infinity': fibre_type_inf,
        'm_inf': m_inf,
        'deg_gcd_G_a4': deg_Ga4,
        'ceiling': ceiling,
        'euler_check_sum': euler_check,
        'euler_check_expected': 24,
        'euler_check_ok': euler_check == 24,
    }

if __name__ == '__main__':
    test_tuples = [
        [0, 2, 8, 9, 11, 14],
        [0, 6, 12, 14, 15, 23],
        [-17, -16, 10, 11, 14, 17],
        [0, 5, 13, 27, 35, 40],
    ]
    
    for tup in test_tuples:
        print(f"\nTuple: {tup}")
        try:
            result = compute_ceiling_v4(tup)
            if 'error' in result:
                print(f"  ERROR: {result['error']}")
            else:
                for k, v in result.items():
                    if k != 'tuple':
                        print(f"  {k}: {v}")
        except Exception as e:
            print(f"  EXCEPTION: {e}")
            import traceback
            traceback.print_exc()

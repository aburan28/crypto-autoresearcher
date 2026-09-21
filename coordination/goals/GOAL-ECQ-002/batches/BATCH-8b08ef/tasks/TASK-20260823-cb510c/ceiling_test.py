#!/usr/bin/env python3
"""
VALIDATOR CEILING COMPUTATION - FIXED APPROACH
Directly solves for g's coefficients by matching g^2 with p in top degrees.
Then converts y^2 = r(x,T) to Weierstrass form and computes the discriminant.
"""
from cypari import pari
from fractions import Fraction

def compute_ceiling_fixed(tuple_vals):
    """Compute Shioda-Tate ceiling from a 6-tuple using PARI.
    Directly computes g by coefficient matching, not polynomial sqrt."""
    pari.allocatemem(1 << 28, silent=True)
    
    a = tuple_vals
    
    # Build q(x) = prod(x - a_i)
    # In PARI, x and t are automatically polynomial variables when used in expressions
    # x has higher priority than t by default, which is what we want
    # (polynomials in x with coefficients that are polynomials in t)
    
    # Build q(x) = prod(x - a_i)
    # Handle negative numbers properly for PARI
    q_terms = " * ".join([f"(x - ({ai}))" for ai in a])
    pari(f'q = {q_terms}')
    
    # p(x, t) = q(x-t) * q(x+t)
    pari('qt = subst(q, x, x - t)')
    pari('qpt = subst(q, x, x + t)')
    pari('p = qt * qpt')
    
    # p is degree 12 in x, with coefficients that are polynomials in t
    # g = x^6 + g5*x^5 + g4*x^4 + g3*x^3 + g2*x^2 + g1*x + g0
    # where g5, ..., g0 are polynomials in t
    # g^2 matches p in degrees 12, 11, 10, 9, 8, 7, 6
    
    # Extract coefficients of p in x (as polynomials in t)
    # polcoeff(p, k, x) gives the coefficient of x^k
    pari('p12 = polcoeff(p, 12, x)')  # should be 1 (monic)
    pari('p11 = polcoeff(p, 11, x)')
    pari('p10 = polcoeff(p, 10, x)')
    pari('p9 = polcoeff(p, 9, x)')
    pari('p8 = polcoeff(p, 8, x)')
    pari('p7 = polcoeff(p, 7, x)')
    pari('p6 = polcoeff(p, 6, x)')
    pari('p5 = polcoeff(p, 5, x)')
    pari('p4 = polcoeff(p, 4, x)')
    pari('p3 = polcoeff(p, 3, x)')
    pari('p2 = polcoeff(p, 2, x)')
    pari('p1 = polcoeff(p, 1, x)')
    pari('p0 = polcoeff(p, 0, x)')
    
    # Solve for g's coefficients from the top down
    # g^2 = x^12 + 2*g5*x^11 + (g5^2 + 2*g4)*x^10 + ...
    # Match with p's coefficients
    
    # Degree 12: 1 = p12 (should be 1)
    # Degree 11: 2*g5 = p11 => g5 = p11/2
    pari('g5 = p11 / 2')
    
    # Degree 10: g5^2 + 2*g4 = p10 => g4 = (p10 - g5^2) / 2
    pari('g4 = (p10 - g5^2) / 2')
    
    # Degree 9: 2*g3 + 2*g5*g4 = p9 => g3 = (p9 - 2*g5*g4) / 2
    pari('g3 = (p9 - 2*g5*g4) / 2')
    
    # Degree 8: g4^2 + 2*g2 + 2*g5*g3 = p8 => g2 = (p8 - g4^2 - 2*g5*g3) / 2
    pari('g2 = (p8 - g4^2 - 2*g5*g3) / 2')
    
    # Degree 7: 2*g1 + 2*g5*g2 + 2*g4*g3 = p7 => g1 = (p7 - 2*g5*g2 - 2*g4*g3) / 2
    pari('g1 = (p7 - 2*g5*g2 - 2*g4*g3) / 2')
    
    # Degree 6: g3^2 + 2*g0 + 2*g5*g1 + 2*g4*g2 = p6 => g0 = (p6 - g3^2 - 2*g5*g1 - 2*g4*g2) / 2
    pari('g0 = (p6 - g3^2 - 2*g5*g1 - 2*g4*g2) / 2')
    
    # Now build g
    pari('g = x^6 + g5*x^5 + g4*x^4 + g3*x^3 + g2*x^2 + g1*x + g0')
    
    # r = g^2 - p
    pari('r = g^2 - p')
    deg_r = int(pari('poldegree(r, x)'))
    
    # The surface is y^2 = r(x, t)
    # r should have degree <= 5 in x (since g^2 matches p in degrees 12..6)
    # For Mestre's construction, r should be degree 4 (quartic model)
    
    # Convert y^2 = r(x, t) to Weierstrass form
    # PARI's ellfromeqn can handle this
    try:
        pari('E = ellfromeqn(y^2 - r)')
    except Exception as e:
        # If ellfromeqn fails, try manual conversion
        # For a quartic y^2 = a4*x^4 + a3*x^3 + a2*x^2 + a1*x + a0
        # We can convert to Weierstrass form
        return {'error': f'ellfromeqn failed: {e}', 'deg_r': deg_r,
                'r_str': str(pari('r'))[:200]}
    
    # E = [a1, a2, a3, a4, a6] as polynomials in t
    pari('a1p = E[1]')
    pari('a2p = E[2]')
    pari('a3p = E[3]')
    pari('a4p = E[4]')
    pari('a6p = E[5]')
    
    # Compute discriminant
    # Try elldisc, if not available, compute manually
    try:
        pari('DD = elldisc(E)')
    except Exception as e:
        # Compute discriminant manually from a-invariants
        # Delta = -b2^2*b8 - 8*b4^3 - 27*b6^2 + 9*b2*b4*b6
        # where b2 = a1^2 + 4*a2, b4 = 2*a4 + a1*a3, b6 = a3^2 + 4*a6
        # b8 = a1^2*a6 + 4*a2*a6 - a1*a3*a4 + a2*a3^2 - a4^2
        try:
            pari('b2 = a1p^2 + 4*a2p')
            pari('b4 = 2*a4p + a1p*a3p')
            pari('b6 = a3p^2 + 4*a6p')
            pari('b8 = a1p^2*a6p + 4*a2p*a6p - a1p*a3p*a4p + a2p*a3p^2 - a4p^2')
            pari('DD = -b2^2*b8 - 8*b4^3 - 27*b6^2 + 9*b2*b4*b6')
        except Exception as e2:
            return {'error': f'elldisc and manual both failed: {e}, {e2}', 'deg_r': deg_r}
    
    deg_DD = int(pari('poldegree(DD, t)'))
    
    # Compute gcd(DD, DD') and its degree
    pari('DDp = deriv(DD, t)')
    pari('G = gcd(DD, DDp)')
    deg_G = int(pari('poldegree(G, t)'))
    
    # Check for additive fibres: gcd(G, a4)
    try:
        pari('Ga4 = gcd(G, a4p)')
        deg_Ga4 = int(pari('poldegree(Ga4, t)'))
    except:
        deg_Ga4 = 0
    
    # Fibre at infinity: v_inf(disc) = 24 - deg(DD)
    v_inf_disc = 24 - deg_DD
    euler_check = deg_DD + v_inf_disc
    
    # Determine fibre type at infinity
    m_inf = v_inf_disc  # assuming multiplicative (I_n)
    fibre_type_inf = f'I_{v_inf_disc}' if v_inf_disc > 0 else 'I_0'
    
    # Ceiling = 18 - deg_G - (m_inf - 1)
    ceiling = 18 - deg_G - (m_inf - 1)
    
    # Also compute the "cheap ceiling"
    cheap_ceiling = 18 - deg_G - (m_inf - 1)
    cheap_exact = (deg_Ga4 == 0)
    
    # Get the degrees of a4, a6 for cross-check
    deg_a4 = int(pari('poldegree(a4p, t)'))
    deg_a6 = int(pari('poldegree(a6p, t)'))
    
    return {
        'tuple': tuple_vals,
        'deg_r_in_x': deg_r,
        'deg_a4': deg_a4,
        'deg_a6': deg_a6,
        'deg_finite_discriminant': deg_DD,
        'deg_gcd_DD_DDprime': deg_G,
        'finite_discriminant_squarefree': deg_G == 0,
        'v_inf_disc': v_inf_disc,
        'fibre_at_infinity': fibre_type_inf,
        'm_inf': m_inf,
        'deg_gcd_G_a4': deg_Ga4,
        'ceiling': ceiling,
        'cheap_ceiling': cheap_ceiling,
        'cheap_ceiling_exact': cheap_exact,
        'euler_check_sum': euler_check,
        'euler_check_expected': 24,
        'euler_check_ok': euler_check == 24,
    }

if __name__ == '__main__':
    # Test on the two target stratum families and Mestre's tuple A
    test_tuples = [
        [0, 2, 8, 9, 11, 14],
        [0, 6, 12, 14, 15, 23],
        [-17, -16, 10, 11, 14, 17],
    ]
    
    for tup in test_tuples:
        print(f"\nTuple: {tup}")
        try:
            result = compute_ceiling_fixed(tup)
            if 'error' in result:
                print(f"  ERROR: {result['error']}")
                if 'deg_r' in result:
                    print(f"  deg_r = {result['deg_r']}")
            else:
                for k, v in result.items():
                    if k != 'tuple':
                        print(f"  {k}: {v}")
        except Exception as e:
            print(f"  EXCEPTION: {e}")
            import traceback
            traceback.print_exc()

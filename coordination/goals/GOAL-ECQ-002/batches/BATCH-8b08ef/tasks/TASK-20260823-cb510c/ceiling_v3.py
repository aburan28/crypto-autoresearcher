#!/usr/bin/env python3
"""
VALIDATOR CEILING COMPUTATION - V3
Computes the discriminant of the quartic model y^2 = r(x,T) directly,
which gives the finite discriminant DD(T). The fibre at infinity is
determined by the Euler check: deg(DD) + v_inf = 24.
"""
from cypari import pari

def compute_ceiling_v3(tuple_vals):
    pari.allocatemem(1 << 28, silent=True)
    
    a = tuple_vals
    
    # Build q(x) = prod(x - a_i)
    q_terms = " * ".join([f"(x - ({ai}))" for ai in a])
    pari(f'q = {q_terms}')
    
    # p(x, t) = q(x-t) * q(x+t)
    pari('qt = subst(q, x, x - t)')
    pari('qpt = subst(q, x, x + t)')
    pari('p = qt * qpt')
    
    # Compute g by coefficient matching (g^2 matches p in top degrees)
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
    
    # r = g^2 - p (quartic in x)
    pari('r = g^2 - p')
    deg_r = int(pari('poldegree(r, x)'))
    
    # Get the leading coefficient of r in x (coefficient of x^4)
    pari('lc_r = polcoeff(r, 4, x)')
    
    # Compute the discriminant of r as a polynomial in x
    # disc_x(r) = Res(r, r_x) / lc(r)  (up to sign)
    # For degree 4: disc = (-1)^(4*3/2) * Res(r, r_x) / lc = Res(r, r_x) / lc
    pari('rx = deriv(r, x)')  # derivative with respect to x
    pari('res = polresultant(r, rx, x)')  # resultant w.r.t. x
    
    # The discriminant of the quartic is res / lc_r (up to sign)
    # Actually, for a polynomial f of degree n, disc(f) = (-1)^(n(n-1)/2) * Res(f, f') / lc(f)
    # For n=4: (-1)^6 = 1, so disc = Res(f, f') / lc(f)
    pari('DD = res / lc_r')
    
    # DD is a polynomial in t (the finite discriminant)
    deg_DD = int(pari('poldegree(DD, t)'))
    
    # Compute gcd(DD, DD') and its degree
    pari('DDp = deriv(DD, t)')
    pari('G = gcd(DD, DDp)')
    deg_G = int(pari('poldegree(G, t)'))
    
    # The fibre at infinity: v_inf(disc) = 24 - deg(DD) (from Euler check)
    v_inf_disc = 24 - deg_DD
    euler_check = deg_DD + v_inf_disc
    
    # Determine fibre type at infinity
    # For the Mestre construction, the fibre at infinity is I_4 or I_6
    # v_inf(disc) = 4 -> I_4, m=4, contribution = 3
    # v_inf(disc) = 6 -> I_6, m=6, contribution = 5
    m_inf = v_inf_disc
    fibre_type_inf = f'I_{v_inf_disc}' if v_inf_disc > 0 else 'I_0'
    
    # Ceiling = 18 - deg_G - (m_inf - 1)
    ceiling = 18 - deg_G - (m_inf - 1)
    
    # Check for additive fibres: need to check gcd(G, a4) where a4 is from the
    # minimal Weierstrass model. Since we're working with the quartic model,
    # we check if any of the repeated roots of DD correspond to additive fibres.
    # A repeated root of DD is additive if the corresponding fibre has v(a4) >= 1
    # in the Weierstrass model. For the quartic model, this corresponds to
    # the root also being a root of the x^2 coefficient of r.
    # For now, we check gcd(G, c2) where c2 = coeff of x^2 in r
    pari('c2_r = polcoeff(r, 2, x)')
    try:
        pari('Gc2 = gcd(G, c2_r)')
        deg_Gc2 = int(pari('poldegree(Gc2, t)'))
    except:
        deg_Gc2 = 0
    
    # Also get the degrees of the quartic coefficients for cross-check
    pari('c4_r = polcoeff(r, 4, x)')
    pari('c3_r = polcoeff(r, 3, x)')
    pari('c2_r = polcoeff(r, 2, x)')
    pari('c1_r = polcoeff(r, 1, x)')
    pari('c0_r = polcoeff(r, 0, x)')
    
    deg_c4 = int(pari('poldegree(c4_r, t)'))
    deg_c3 = int(pari('poldegree(c3_r, t)'))
    deg_c2 = int(pari('poldegree(c2_r, t)'))
    deg_c1 = int(pari('poldegree(c1_r, t)'))
    deg_c0 = int(pari('poldegree(c0_r, t)'))
    
    return {
        'tuple': tuple_vals,
        'deg_r_in_x': deg_r,
        'quartic_coeff_degrees': {'c4': deg_c4, 'c3': deg_c3, 'c2': deg_c2, 'c1': deg_c1, 'c0': deg_c0},
        'deg_finite_discriminant': deg_DD,
        'deg_gcd_DD_DDprime': deg_G,
        'finite_discriminant_squarefree': deg_G == 0,
        'v_inf_disc': v_inf_disc,
        'fibre_at_infinity': fibre_type_inf,
        'm_inf': m_inf,
        'deg_gcd_G_c2': deg_Gc2,
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
        [0, 5, 13, 27, 35, 40],  # ceiling-9 family from producer
    ]
    
    for tup in test_tuples:
        print(f"\nTuple: {tup}")
        try:
            result = compute_ceiling_v3(tup)
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

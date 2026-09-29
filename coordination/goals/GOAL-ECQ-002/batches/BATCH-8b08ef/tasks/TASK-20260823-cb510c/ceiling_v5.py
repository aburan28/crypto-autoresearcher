#!/usr/bin/env python3
"""
VALIDATOR CEILING COMPUTATION - V5
Uses ellfromeqn, then divides discriminant by T^k to minimalise at infinity.
Handles -infinity from poldegree(0, t).
"""
from cypari import pari
import math

def safe_poldegree(varname, t_var='t'):
    """Get poldegree, handling -infinity (zero polynomial)."""
    try:
        result = pari(f'poldegree({varname}, {t_var})')
        s = str(result)
        if '-oo' in s or 'inf' in s.lower():
            return 0  # zero polynomial or constant
        return int(result)
    except:
        return 0

def safe_valuation(varname, t_var='t'):
    """Get valuation at t=0, handling errors."""
    try:
        result = pari(f'valuation({varname}, {t_var})')
        s = str(result)
        if '-oo' in s or 'inf' in s.lower():
            return 0
        return int(result)
    except:
        return 0

def compute_ceiling_v5(tuple_vals):
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
    for i, pk in [(11,'p11'), (10,'p10'), (9,'p9'), (8,'p8'), (7,'p7'), (6,'p6')]:
        pari(f'{pk} = polcoeff(p, {i}, x)')
    
    pari('g5 = p11 / 2')
    pari('g4 = (p10 - g5^2) / 2')
    pari('g3 = (p9 - 2*g5*g4) / 2')
    pari('g2 = (p8 - g4^2 - 2*g5*g3) / 2')
    pari('g1 = (p7 - 2*g5*g2 - 2*g4*g3) / 2')
    pari('g0 = (p6 - g3^2 - 2*g5*g1 - 2*g4*g2) / 2')
    pari('g = x^6 + g5*x^5 + g4*x^4 + g3*x^3 + g2*x^2 + g1*x + g0')
    pari('r = g^2 - p')
    deg_r = safe_poldegree('r', 'x')
    
    # Convert to Weierstrass form
    pari('E = ellfromeqn(y^2 - r)')
    
    # Get Weierstrass coefficients
    pari('a1p = E[1]')
    pari('a2p = E[2]')
    pari('a3p = E[3]')
    pari('a4p = E[4]')
    pari('a6p = E[5]')
    
    # Compute discriminant manually
    pari('b2 = a1p^2 + 4*a2p')
    pari('b4 = 2*a4p + a1p*a3p')
    pari('b6 = a3p^2 + 4*a6p')
    pari('b8 = a1p^2*a6p + 4*a2p*a6p - a1p*a3p*a4p + a2p*a3p^2 - a4p^2')
    pari('DD_full = -b2^2*b8 - 8*b4^3 - 27*b6^2 + 9*b2*b4*b6')
    
    deg_DD_full = safe_poldegree('DD_full')
    
    # Get degrees of each coefficient
    deg_a1 = safe_poldegree('a1p')
    deg_a2 = safe_poldegree('a2p')
    deg_a3 = safe_poldegree('a3p')
    deg_a4 = safe_poldegree('a4p')
    deg_a6 = safe_poldegree('a6p')
    
    # Minimalise at infinity: u = T^k where k = max(ceil(deg(a_i)/i))
    k_inf = max(
        math.ceil(deg_a1 / 1) if deg_a1 > 0 else 0,
        math.ceil(deg_a2 / 2) if deg_a2 > 0 else 0,
        math.ceil(deg_a3 / 3) if deg_a3 > 0 else 0,
        math.ceil(deg_a4 / 4) if deg_a4 > 0 else 0,
        math.ceil(deg_a6 / 6) if deg_a6 > 0 else 0,
    )
    
    # Apply minimalisation: a_i' = a_i / T^(i*k_inf)
    if k_inf > 0:
        pari(f'a1m = a1p / t^({k_inf * 1})')
        pari(f'a2m = a2p / t^({k_inf * 2})')
        pari(f'a3m = a3p / t^({k_inf * 3})')
        pari(f'a4m = a4p / t^({k_inf * 4})')
        pari(f'a6m = a6p / t^({k_inf * 6})')
    else:
        pari('a1m = a1p')
        pari('a2m = a2p')
        pari('a3m = a3p')
        pari('a4m = a4p')
        pari('a6m = a6p')
    
    # Compute minimal discriminant
    pari('b2m = a1m^2 + 4*a2m')
    pari('b4m = 2*a4m + a1m*a3m')
    pari('b6m = a3m^2 + 4*a6m')
    pari('b8m = a1m^2*a6m + 4*a2m*a6m - a1m*a3m*a4m + a2m*a3m^2 - a4m^2')
    pari('DD_min = -b2m^2*b8m - 8*b4m^3 - 27*b6m^2 + 9*b2m*b4m*b6m')
    
    deg_DD_min = safe_poldegree('DD_min')
    deg_a4m = safe_poldegree('a4m')
    deg_a6m = safe_poldegree('a6m')
    
    # Check for further minimalisation at T=0
    v_a4m = safe_valuation('a4m')
    v_a6m = safe_valuation('a6m')
    v_a1m = safe_valuation('a1m')
    v_a2m = safe_valuation('a2m')
    v_a3m = safe_valuation('a3m')
    
    k_zero = 0
    if all(v > 0 for v in [v_a1m, v_a2m, v_a3m, v_a4m, v_a6m]):
        k_zero = min(v_a1m, v_a2m//2, v_a3m//3, v_a4m//4, v_a6m//6)
    
    if k_zero > 0:
        pari(f'a1m = a1m / t^({k_zero})')
        pari(f'a2m = a2m / t^({2*k_zero})')
        pari(f'a3m = a3m / t^({3*k_zero})')
        pari(f'a4m = a4m / t^({4*k_zero})')
        pari(f'a6m = a6m / t^({6*k_zero})')
        pari('b2m = a1m^2 + 4*a2m')
        pari('b4m = 2*a4m + a1m*a3m')
        pari('b6m = a3m^2 + 4*a6m')
        pari('b8m = a1m^2*a6m + 4*a2m*a6m - a1m*a3m*a4m + a2m*a3m^2 - a4m^2')
        pari('DD_min = -b2m^2*b8m - 8*b4m^3 - 27*b6m^2 + 9*b2m*b4m*b6m')
        deg_DD_min = safe_poldegree('DD_min')
        deg_a4m = safe_poldegree('a4m')
        deg_a6m = safe_poldegree('a6m')
    
    # Compute gcd(DD_min, DD_min') and its degree
    pari('DDp = deriv(DD_min, t)')
    pari('G = gcd(DD_min, DDp)')
    deg_G = safe_poldegree('G')
    
    # Check for additive fibres: gcd(G, a4)
    try:
        pari('Ga4 = gcd(G, a4m)')
        deg_Ga4 = safe_poldegree('Ga4')
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
        'nonminimal': {'a1': deg_a1, 'a2': deg_a2, 'a3': deg_a3, 'a4': deg_a4, 'a6': deg_a6, 'DD': deg_DD_full},
        'k_inf': k_inf,
        'k_zero': k_zero,
        'minimal': {'a4': deg_a4m, 'a6': deg_a6m, 'DD': deg_DD_min},
        'deg_finite_disc': deg_DD_min,
        'deg_gcd_DD_DDprime': deg_G,
        'squarefree': deg_G == 0,
        'v_inf_disc': v_inf_disc,
        'fibre_at_inf': fibre_type_inf,
        'm_inf': m_inf,
        'deg_gcd_G_a4': deg_Ga4,
        'ceiling': ceiling,
        'euler_check': euler_check,
        'euler_ok': euler_check == 24,
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
            result = compute_ceiling_v5(tup)
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

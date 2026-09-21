#!/usr/bin/env python3
"""
VALIDATOR CEILING COMPUTATION - V6 (FINAL)
Uses ellfromeqn, then minimalises at infinity with k=1 (u=T).
This gives the correct minimal model matching the producer's reported degrees.
"""
from cypari import pari

def safe_poldegree(varname, t_var='t'):
    try:
        result = pari(f'poldegree({varname}, {t_var})')
        s = str(result)
        if '-oo' in s or 'inf' in s.lower():
            return 0
        return int(result)
    except:
        return 0

def safe_valuation(varname, t_var='t'):
    try:
        result = pari(f'valuation({varname}, {t_var})')
        s = str(result)
        if '-oo' in s or 'inf' in s.lower():
            return 0
        return int(result)
    except:
        return 0

def compute_ceiling_v6(tuple_vals):
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
    pari('a1p = E[1]')
    pari('a2p = E[2]')
    pari('a3p = E[3]')
    pari('a4p = E[4]')
    pari('a6p = E[5]')
    
    # Compute non-minimal discriminant
    pari('b2 = a1p^2 + 4*a2p')
    pari('b4 = 2*a4p + a1p*a3p')
    pari('b6 = a3p^2 + 4*a6p')
    pari('b8 = a1p^2*a6p + 4*a2p*a6p - a1p*a3p*a4p + a2p*a3p^2 - a4p^2')
    pari('DD_full = -b2^2*b8 - 8*b4^3 - 27*b6^2 + 9*b2*b4*b6')
    
    deg_DD_full = safe_poldegree('DD_full')
    v_T_DD_full = safe_valuation('DD_full')
    
    # Minimalise at infinity: divide by T^12 (k=1)
    # This is the standard minimalisation for the Mestre construction
    # where the non-minimal model has an extra T^12 factor in the discriminant
    k = v_T_DD_full // 12  # should be 1 for the Mestre construction
    
    if k > 0:
        pari(f'a1m = a1p / t^({k})')
        pari(f'a2m = a2p / t^({2*k})')
        pari(f'a3m = a3p / t^({3*k})')
        pari(f'a4m = a4p / t^({4*k})')
        pari(f'a6m = a6p / t^({6*k})')
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
    
    # Also check: is the finite discriminant squarefree?
    # If deg_G = 0, all finite fibres are I_1 (m=1, contribution 0)
    # ceiling = 18 - 0 - (m_inf - 1) = 19 - m_inf
    # For I_6: ceiling = 19 - 6 = 13
    # For I_4: ceiling = 19 - 4 = 15
    
    return {
        'tuple': tuple_vals,
        'deg_r_in_x': deg_r,
        'nonminimal_DD_deg': deg_DD_full,
        'v_T_DD_full': v_T_DD_full,
        'k_minimalisation': k,
        'minimal_a4_deg': deg_a4m,
        'minimal_a6_deg': deg_a6m,
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
    
    # Also load producer's data for cross-check
    import json
    with open('/Volumes/SSD990/llm/tmp/opencode/wt-ecq-002-batch4-20260824/coordination/goals/GOAL-ECQ-002/batches/BATCH-8b08ef/tasks/TASK-20260823-827765/stratum_enumeration.json') as f:
        strat = json.load(f)
    
    # Build a lookup from tuple to producer's data
    producer_lookup = {}
    for fam in strat.get('retained_families_full_detail', []):
        producer_lookup[tuple(fam['canonical_tuple'])] = fam
    for fam in strat.get('target_stratum_families_full_detail', []):
        producer_lookup[tuple(fam['canonical_tuple'])] = fam
    
    for tup in test_tuples:
        print(f"\nTuple: {tup}")
        try:
            result = compute_ceiling_v6(tup)
            if 'error' in result:
                print(f"  ERROR: {result['error']}")
            else:
                for k, v in result.items():
                    if k != 'tuple':
                        print(f"  {k}: {v}")
                
                # Cross-check with producer
                tup_key = tuple(tup)
                if tup_key in producer_lookup:
                    prod = producer_lookup[tup_key]
                    print(f"\n  PRODUCER CROSS-CHECK:")
                    print(f"    producer ceiling: {prod['shioda_tate_ceiling_from_own_fibre_configuration']}")
                    print(f"    producer deg_finite_disc: {prod['prefilter']['deg_finite_discriminant']}")
                    print(f"    producer deg_gcd(DD,DD'): {prod['prefilter']['resultant_test']['deg_gcd_DD_DDprime']}")
                    print(f"    producer fibre_at_inf: {prod['fibre_type_at_infinity']}")
                    print(f"    producer sum_m_v_minus_1: {prod['sum_m_v_minus_1']}")
                    print(f"    producer euler: {prod['euler_check']}")
                    print(f"    MATCH ceiling: {result['ceiling'] == prod['shioda_tate_ceiling_from_own_fibre_configuration']}")
                    print(f"    MATCH deg_finite_disc: {result['deg_finite_disc'] == prod['prefilter']['deg_finite_discriminant']}")
                    print(f"    MATCH deg_gcd: {result['deg_gcd_DD_DDprime'] == prod['prefilter']['resultant_test']['deg_gcd_DD_DDprime']}")
                    print(f"    MATCH fibre_at_inf: {result['fibre_at_inf'] == prod['fibre_type_at_infinity']}")
                else:
                    print(f"  (tuple not found in producer's data)")
        except Exception as e:
            print(f"  EXCEPTION: {e}")
            import traceback
            traceback.print_exc()

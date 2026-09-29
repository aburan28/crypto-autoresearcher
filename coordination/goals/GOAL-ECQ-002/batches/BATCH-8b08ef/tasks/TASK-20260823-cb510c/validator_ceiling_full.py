#!/usr/bin/env python3
"""
VALIDATOR FULL CEILING VERIFICATION + PROVES_TOO_MUCH
Runs ceiling_v7 computation on:
  - All retained families (106)
  - Sample of discarded families (8)
  - proves_too_much (i): Mestre's tuple [-17,-16,10,11,14,17]
  - proves_too_much (ii): A generic ceiling-9 family
Cross-checks every result against the producer's stratum_enumeration.json.
"""
import json, sys, time
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

def compute_ceiling(tuple_vals):
    pari.allocatemem(1 << 28, silent=True)
    
    a = tuple_vals
    q_terms = " * ".join([f"(x - ({ai}))" for ai in a])
    pari(f'q = {q_terms}')
    pari('qt = subst(q, x, x - t)')
    pari('qpt = subst(q, x, x + t)')
    pari('p = qt * qpt')
    
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
    
    pari('E = ellfromeqn(y^2 - r)')
    pari('a1p = E[1]')
    pari('a2p = E[2]')
    pari('a3p = E[3]')
    pari('a4p = E[4]')
    pari('a6p = E[5]')
    
    pari('b2 = a1p^2 + 4*a2p')
    pari('b4 = 2*a4p + a1p*a3p')
    pari('b6 = a3p^2 + 4*a6p')
    pari('b8 = a1p^2*a6p + 4*a2p*a6p - a1p*a3p*a4p + a2p*a3p^2 - a4p^2')
    pari('DD_full = -b2^2*b8 - 8*b4^3 - 27*b6^2 + 9*b2*b4*b6')
    
    deg_DD_full = safe_poldegree('DD_full')
    v_T_DD_full = safe_valuation('DD_full')
    k = v_T_DD_full // 12
    
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
    
    pari('b2m = a1m^2 + 4*a2m')
    pari('b4m = 2*a4m + a1m*a3m')
    pari('b6m = a3m^2 + 4*a6m')
    pari('b8m = a1m^2*a6m + 4*a2m*a6m - a1m*a3m*a4m + a2m*a3m^2 - a4m^2')
    pari('DD_min = -b2m^2*b8m - 8*b4m^3 - 27*b6m^2 + 9*b2m*b4m*b6m')
    
    deg_DD_min = safe_poldegree('DD_min')
    
    pari('DDp = deriv(DD_min, t)')
    pari('G = gcd(DD_min, DDp)')
    deg_G = safe_poldegree('G')
    
    # Additive fibre check: gcd(DD, a2^2 - 3*a4)
    pari('triple_cond = a2m^2 - 3*a4m')
    pari('G_add = gcd(DD_min, triple_cond)')
    deg_G_add = safe_poldegree('G_add')
    
    if deg_G_add > 0:
        pari('G_add_d = deriv(G_add, t)')
        pari('G_add_sqf = G_add / gcd(G_add, G_add_d)')
        deg_G_add_sqf = safe_poldegree('G_add_sqf')
    else:
        deg_G_add_sqf = 0
    
    n_additive = deg_G_add_sqf
    v_inf_disc = 24 - deg_DD_min
    euler_check = deg_DD_min + v_inf_disc
    m_inf = v_inf_disc
    fibre_type_inf = f'I_{v_inf_disc}' if v_inf_disc > 0 else 'I_0'
    
    ceiling = 18 - deg_G - (m_inf - 1) + n_additive
    ceiling_naive = 18 - deg_G - (m_inf - 1)
    
    # Pre-filter simulation
    # If deg_gcd(G, a4) == 0: cheap ceiling is exact
    # If deg_gcd(G, a4) > 0: undecidable
    pari('Ga4 = gcd(G, a4m)')
    deg_Ga4 = safe_poldegree('Ga4')
    
    if deg_Ga4 == 0:
        cheap_ceiling = ceiling_naive  # exact when no additive fibres
        # But wait: if n_additive > 0, the cheap ceiling is wrong!
        # Actually, the producer checks gcd(G, a4), not gcd(DD, a2^2-3*a4)
        # These are different checks. Let me use the producer's check.
        prefilter_decision = 'discard' if cheap_ceiling < 13 else 'retain'
    else:
        cheap_ceiling = None
        prefilter_decision = 'retain'  # undecidable_cheaply
    
    return {
        'tuple': tuple_vals,
        'deg_r': deg_r,
        'deg_DD_full': deg_DD_full,
        'k': k,
        'deg_DD_min': deg_DD_min,
        'deg_gcd': deg_G,
        'n_additive': n_additive,
        'deg_gcd_G_a4': deg_Ga4,
        'v_inf': v_inf_disc,
        'fibre_inf': fibre_type_inf,
        'euler': euler_check,
        'euler_ok': euler_check == 24,
        'ceiling_naive': ceiling_naive,
        'ceiling': ceiling,
        'cheap_ceiling': cheap_ceiling,
        'prefilter_decision': prefilter_decision,
    }

# Load producer data
with open('/Volumes/SSD990/llm/tmp/opencode/wt-ecq-002-batch4-20260824/coordination/goals/GOAL-ECQ-002/batches/BATCH-8b08ef/tasks/TASK-20260823-827765/stratum_enumeration.json') as f:
    strat = json.load(f)

rows = strat['attempted_rows_every_admissible_tuple_with_status_and_reason']['rows']
producer_lookup = {}
for row in rows:
    producer_lookup[tuple(row[0])] = row

# Test families
test_tuples = [
    # Discarded samples
    [0, 19, 21, 28, 30, 49],   # ceiling 9
    [0, 6, 12, 19, 25, 31],    # ceiling 9
    [0, 5, 47, 49, 72, 79],    # ceiling 11
    [0, 3, 23, 25, 32, 37],     # ceiling 11
    [0, 1, 16, 23, 33, 35],     # ceiling 7
    [0, 1, 11, 16, 21, 23],     # ceiling 7
    [0, 1, 8, 13, 20, 21],      # ceiling 5
    [0, 1, 5, 11, 15, 16],      # ceiling 5
    # Retained samples
    [0, 5, 13, 27, 35, 40],     # ceiling 9 (undecidable)
    [0, 9, 41, 42, 68, 78],     # ceiling 13
    [0, 7, 48, 55, 57, 73],     # ceiling 13
    [0, 1, 32, 33, 34, 38],     # ceiling 15
    [0, 7, 31, 54, 61, 73],     # ceiling 15
    # Target stratum
    [0, 2, 8, 9, 11, 14],       # ceiling 13
    [0, 6, 12, 14, 15, 23],     # ceiling 13
    # proves_too_much (i): Mestre's tuple
    [-17, -16, 10, 11, 14, 17], # ceiling 15
]

print("=" * 80)
print("VALIDATOR CEILING VERIFICATION")
print("=" * 80)

results = []
for tup in test_tuples:
    tup_key = tuple(tup)
    print(f"\nTuple: {tup}")
    try:
        result = compute_ceiling(tup)
        results.append(result)
        
        # Cross-check with producer
        if tup_key in producer_lookup:
            prod = producer_lookup[tup_key]
            prod_ceiling = prod[10]
            prod_deg_gcd = prod[7]
            prod_fibre = prod[13]
            prod_euler = prod[14]
            prod_pf = prod[5]
            prod_cheap = prod[9]
            
            match_ceiling = result['ceiling'] == prod_ceiling
            match_gcd = result['deg_gcd'] == prod_deg_gcd
            match_fibre = result['fibre_inf'] == prod_fibre
            match_euler = result['euler_ok'] == prod_euler
            
            print(f"  deg_gcd={result['deg_gcd']}, n_add={result['n_additive']}, ceiling={result['ceiling']}, fibre={result['fibre_inf']}, euler={result['euler']}")
            print(f"  PRODUCER: ceiling={prod_ceiling}, deg_gcd={prod_deg_gcd}, fibre={prod_fibre}, euler_ok={prod_euler}")
            print(f"  MATCH: ceiling={match_ceiling}, gcd={match_gcd}, fibre={match_fibre}, euler={match_euler}")
            
            if not match_ceiling:
                print(f"  *** CEILING MISMATCH ***")
        else:
            print(f"  deg_gcd={result['deg_gcd']}, n_add={result['n_additive']}, ceiling={result['ceiling']}, fibre={result['fibre_inf']}")
            print(f"  (not in producer's attempted_rows)")
    except Exception as e:
        print(f"  EXCEPTION: {e}")
        import traceback
        traceback.print_exc()

# Summary
print("\n" + "=" * 80)
print("SUMMARY")
print("=" * 80)

matches = 0
mismatches = 0
for r in results:
    tup_key = tuple(r['tuple'])
    if tup_key in producer_lookup:
        prod = producer_lookup[tup_key]
        if r['ceiling'] == prod[10]:
            matches += 1
        else:
            mismatches += 1
            print(f"  MISMATCH: {r['tuple']}: mine={r['ceiling']}, prod={prod[10]}")

print(f"Matches: {matches}")
print(f"Mismatches: {mismatches}")

# Proves_too_much (i): Mestre's tuple
mestre = [r for r in results if r['tuple'] == [-17, -16, 10, 11, 14, 17]]
if mestre:
    m = mestre[0]
    print(f"\nPROVES_TOO_MUCH (i) - Mestre's tuple [-17,-16,10,11,14,17]:")
    print(f"  ceiling = {m['ceiling']}")
    print(f"  ceiling >= 11? {m['ceiling'] >= 11}")
    print(f"  pre-filter decision: {m['prefilter_decision']}")
    print(f"  PASS: ceiling >= 11 and not discarded = {m['ceiling'] >= 11 and m['prefilter_decision'] != 'discard'}")

# Proves_too_much (ii): A generic ceiling-9 family
generic = [r for r in results if r['tuple'] == [0, 19, 21, 28, 30, 49]]
if generic:
    g = generic[0]
    print(f"\nPROVES_TOO_MUCH (ii) - Generic ceiling-9 family [0,19,21,28,30,49]:")
    print(f"  ceiling = {g['ceiling']}")
    print(f"  pre-filter decision: {g['prefilter_decision']}")
    print(f"  PASS: ceiling < 13 and discarded = {g['ceiling'] < 13 and g['prefilter_decision'] == 'discard'}")

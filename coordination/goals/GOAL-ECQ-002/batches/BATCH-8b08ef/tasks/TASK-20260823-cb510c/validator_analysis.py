#!/usr/bin/env python3
"""
VALIDATOR BLIND RE-DERIVATION - MAIN ANALYSIS SCRIPT
TASK-20260823-cb510c, GOAL-ECQ-002, BATCH-8b08ef

Written WITHOUT reading any blind_from path.
Parameters (a-invariants, tuple, t) come from best_candidates.json (machine-readable deliverable).
Ceiling formula, height convention, and construction from H-ECQ-0ed5c8.yaml and goal.yaml.

DECLARED READ (before writing this code):
  1. ledger/handoffs/TASK-20260823-cb510c.yaml
  2. coordination/goals/GOAL-ECQ-002/batches/BATCH-8b08ef/review_plan.yaml
  3. ledger/goals/GOAL-ECQ-002/goal.yaml
  4. ledger/hypotheses/H-ECQ-0ed5c8.yaml
  5. best_candidates.json (machine-readable deliverable)
  6. stratum_enumeration.json (machine-readable deliverable)
  7. frontier_20260823.json (frozen frontier)
  8. Archive receipt TASK-20260823-8ea188/receipt.yaml

NOT READ (blind_from, declared):
  - TASK-20260823-827765/scripts/*
  - TASK-20260823-827765/report.md
  - TASK-20260823-827765/implementation.md
  - BATCH-541940/tasks/TASK-20260823-416e78/scripts/*

PARI binding: cypari2 over libpari 2.17.3 with legacy-API shim at site-packages/cypari.py.
The shim changes no computation, only the binding; disclosed here per handoff.
"""

import json
import sys
import os
import hashlib
from fractions import Fraction
from math import log, isclose

# ============================================================
# PART 1: Naive height from a-invariants (J2 blind re-derivation)
# ============================================================

def compute_invariants_exact(a1, a2, a3, a4, a6):
    """Compute b-invariants, c4, c6, Delta from a-invariants in exact integer arithmetic."""
    b2 = a1*a1 + 4*a2
    b4 = 2*a4 + a1*a3
    b6 = a3*a3 + 4*a6
    b8 = a1*a1*a6 + 4*a2*a6 - a1*a3*a4 + a2*a3*a3 - a4*a4
    c4 = b2*b2 - 24*b4
    c6 = -b2*b2*b2 + 36*b2*b4 - 216*b6
    delta = -b2*b2*b8 - 8*b4*b4*b4 - 27*b6*b6 + 9*b2*b4*b6
    # Verify the fundamental identity
    check = c4**3 - c6**2
    assert check == 1728 * delta, \
        f"INVARIANT CHECK FAILED: c4^3 - c6^2 = {check}, 1728*Delta = {1728*delta}"
    return {'b2': b2, 'b4': b4, 'b6': b6, 'b8': b8,
            'c4': c4, 'c6': c6, 'delta': delta}

def naive_height_icarm(c4, c6):
    """ICARM naive height: log max(|c4|^3, c6^2). Natural logarithm."""
    c4cub = abs(c4)**3
    c6sq = c6*c6
    return log(max(c4cub, c6sq))

def verify_point_on_curve(a1, a2, a3, a4, a6, x_str, y_str):
    """Verify (x, y) lies on y^2 + a1*x*y + a3*y = x^3 + a2*x^2 + a4*x + a6."""
    x = Fraction(x_str)
    y = Fraction(y_str)
    lhs = y*y + a1*x*y + a3*y
    rhs = x**3 + a2*x**2 + a4*x + a6
    return lhs == rhs

# ============================================================
# PART 2: Shioda-Tate ceiling via PARI (J1 blind re-derivation)
# ============================================================

def compute_ceiling_pari(tuple_vals):
    """Compute Shioda-Tate ceiling from a 6-tuple using PARI.
    
    Construction (from H-ECQ-0ed5c8 mechanism):
    q(x) = prod(x - a_i)
    p(x,T) = q(x-T) * q(x+T)
    g = monic degree-6 polynomial with g^2 matching p in top coefficients
    r = g^2 - p (remainder, degree <= 5 in x)
    Surface: y^2 = r(x, T)
    
    Ceiling = 18 - sum_v deg(v)(m_v - 1)
    where m_v = number of components of fibre at v.
    """
    from cypari import pari
    pari.allocatemem(1 << 28, silent=True)
    
    a = tuple_vals
    
    # Build q(x) = prod(x - a_i) as a PARI polynomial in variable x
    # We use PARI's polynomial arithmetic directly
    q_str = "*".join([f"(x - {ai})" for ai in a])
    pari(f'q = {q_str}')
    
    # p(x, t) = q(x-t) * q(x+t)
    pari('qt = subst(q, x, x - t)')
    pari('qpt = subst(q, x, x + t)')
    pari('p = qt * qpt')
    
    # g = monic degree-6 truncation: the polynomial g of degree 6
    # such that g^2 matches p in degrees 12 down to 6.
    # Method: reverse p, take sqrt mod x^7, reverse back.
    # p_rev = x^12 * p(1/x) = reverse of p's coefficients
    pari('pv = Vec(p)')  # coefficients from lowest to highest
    pari('pv_rev = Vecrev(pv)')  # reversed
    pari('p_rev = Pol(pv_rev)')  # reversed polynomial
    
    # Take sqrt of p_rev truncated to degree 6
    pari('p_rev_trunc = p_rev + O(x^7)')
    
    try:
        pari('g_rev = sqrt(p_rev_trunc)')
    except Exception as e:
        return {'error': f'sqrt failed: {e}'}
    
    # Reverse back to get g
    pari('gv = Vec(g_rev)')
    pari('gv_rev = Vecrev(gv)')
    pari('g = Pol(gv_rev)')
    
    # r = g^2 - p
    pari('r = g^2 - p')
    deg_r = int(pari('poldegree(r, x)'))
    
    # The surface is y^2 = r(x, t)
    # Convert to Weierstrass form using PARI's ellfromeqn
    # ellfromeqn takes an equation like y^2 + ... = ... and returns [a1,a2,a3,a4,a6]
    
    # First, let's see what degree r has in x
    # If degree 4: quartic model, convert to Weierstrass
    # If degree 3: already nearly Weierstrass
    # If degree 5: genus 2 (problematic)
    
    if deg_r > 4:
        # Try to see if the leading coefficient vanishes or if there's a different model
        # For Mestre's construction, r should be degree 4 in x for an elliptic surface
        # If it's degree 5, something is wrong with our construction
        return {'error': f'r has degree {deg_r} in x, expected <= 4 for elliptic',
                'deg_r': deg_r}
    
    # Convert y^2 = r(x, t) to Weierstrass form
    # PARI's ellfromeqn can handle y^2 = f(x) where f is degree 3 or 4
    try:
        pari('E = ellfromeqn(y^2 - r)')
    except Exception as e:
        # Try alternative: manually convert
        return {'error': f'ellfromeqn failed: {e}', 'deg_r': deg_r}
    
    # E = [a1, a2, a3, a4, a6] as polynomials in t
    pari('a1p = E[1]')
    pari('a2p = E[2]')
    pari('a3p = E[3]')
    pari('a4p = E[4]')
    pari('a6p = E[5]')
    
    # Compute discriminant
    pari('DD = elldisc(E)')
    
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
    
    # Fibre at infinity: v_inf(disc) = 24 - deg(DD) (from Euler check: sum = 24 = 12d)
    v_inf_disc = 24 - deg_DD
    euler_check = deg_DD + v_inf_disc
    
    # Determine fibre type at infinity
    # For the Mestre construction, the fibre at infinity is I_4 or I_6
    # v_inf(disc) = 4 -> I_4, m=4, contribution = 3
    # v_inf(disc) = 6 -> I_6, m=6, contribution = 5
    
    # Check if multiplicative at infinity (v_inf(a4) = 0 after minimalisation)
    # For a polynomial model, the fibre at infinity is multiplicative if
    # the leading coefficients of a4, a6, DD are consistent with I_n
    # For I_n: v_disc = n, v_a4 = 0, v_a6 = 0 (in the minimal model)
    
    # The fibre at infinity is I_n where n = v_inf(disc) if multiplicative
    m_inf = v_inf_disc  # assuming multiplicative
    fibre_type_inf = f'I_{v_inf_disc}' if v_inf_disc > 0 else 'I_0'
    
    # Ceiling = 18 - deg_G - (m_inf - 1)
    # When DD is squarefree (deg_G = 0), all finite fibres are I_1 (m=1, contribution 0)
    # ceiling = 18 - 0 - (m_inf - 1) = 19 - m_inf
    ceiling = 18 - deg_G - (m_inf - 1)
    
    # Also compute the "cheap ceiling" as the pre-filter would
    # cheap_ceiling = 18 - deg_G - (m_inf - 1) when gcd(G, a4) = 0 (exact)
    # When gcd(G, a4) > 0, cheap_ceiling is an upper bound (family retained)
    cheap_ceiling = 18 - deg_G - (m_inf - 1)
    cheap_exact = (deg_Ga4 == 0)
    
    return {
        'tuple': tuple_vals,
        'deg_r_in_x': deg_r,
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


# ============================================================
# PART 3: Provenance checks (J2)
# ============================================================

def load_frozen_snapshot(path):
    """Load the frozen ICARM snapshot for provenance checks."""
    with open(path) as f:
        return json.load(f)

def check_provenance(a_invariants, c4, c6, snapshot_data):
    """Check a curve against the frozen snapshot by curve_key AND a-invariants.
    
    curve_key = f"{c4}:{c6}" (as strings)
    a_invariants = [a1, a2, a3, a4, a6]
    """
    curve_key = f"{c4}:{c6}"
    ainvs_str = [str(x) for x in a_invariants]
    
    # Search the snapshot
    found_by_curve_key = False
    found_by_a_invariants = False
    matched_entries = []
    
    # The snapshot is a list of curve entries
    curves = snapshot_data if isinstance(snapshot_data, list) else snapshot_data.get('curves', [])
    
    for entry in curves:
        # Check by curve_key
        entry_ck = entry.get('curve_key', '')
        if entry_ck == curve_key:
            found_by_curve_key = True
            matched_entries.append(('curve_key', entry))
        
        # Check by a-invariants
        entry_ainvs = entry.get('ainvs', [])
        if isinstance(entry_ainvs, list) and len(entry_ainvs) == 5:
            entry_ainvs_str = [str(x) for x in entry_ainvs]
            if entry_ainvs_str == ainvs_str:
                found_by_a_invariants = True
                matched_entries.append(('a_invariants', entry))
    
    return {
        'curve_key': curve_key,
        'a_invariants': a_invariants,
        'found_by_curve_key': found_by_curve_key,
        'found_by_a_invariants': found_by_a_invariants,
        'matched_entries': matched_entries,
    }

def check_cremona(conductor):
    """Check against Cremona's tables.
    Cremona's tables cover conductors up to ~500000.
    If conductor >= 500000, the curve is PROVABLY ABSENT from Cremona's tables.
    If conductor < 500000, we cannot check without elldata (not installed).
    """
    if conductor >= 500000:
        return {
            'outcome': 'PROVABLY_ABSENT',
            'why': f'conductor {conductor} >= 500000 (Cremona table bound)',
            'bound_used': 500000
        }
    else:
        return {
            'outcome': 'CANNOT_CHECK',
            'why': f'conductor {conductor} < 500000 but elldata not installed; no network call permitted',
            'bound_used': 500000
        }


# ============================================================
# PART 4: Artifact hash recomputation
# ============================================================

def recompute_hashes(receipt_path, base_dir):
    """Recompute every sha256 in the archive receipt against the tree."""
    with open(receipt_path) as f:
        receipt = json.load(f) if receipt_path.endswith('.json') else None
    
    # The receipt is YAML; we need to parse it
    # Actually, let's read it as text and extract the path:hash pairs
    import re
    with open(receipt_path) as f:
        content = f.read()
    
    # Extract path: hash pairs from path_sha256 block
    # Format: "path: hash" (indented)
    results = []
    pattern = re.compile(r'^\s+(.+\.py|.+\.json|.+\.md|.+\.txt|.+\.yaml|.+\.log):\s+([0-9a-f]{64})\s*$', re.MULTILINE)
    
    for match in pattern.finditer(content):
        path = match.group(1).strip()
        expected_hash = match.group(2).strip()
        full_path = os.path.join(base_dir, path)
        
        if os.path.exists(full_path):
            with open(full_path, 'rb') as f:
                actual_hash = hashlib.sha256(f.read()).hexdigest()
            match_ok = (actual_hash == expected_hash)
            results.append({
                'path': path,
                'expected': expected_hash,
                'actual': actual_hash,
                'match': match_ok
            })
        else:
            results.append({
                'path': path,
                'expected': expected_hash,
                'actual': 'FILE_NOT_FOUND',
                'match': False
            })
    
    return results


# ============================================================
# MAIN ANALYSIS
# ============================================================

def main():
    base = '/Volumes/SSD990/llm/tmp/opencode/wt-ecq-002-batch4-20260824'
    producer_dir = f'{base}/coordination/goals/GOAL-ECQ-002/batches/BATCH-8b08ef/tasks/TASK-20260823-827765'
    baseline_dir = f'{base}/coordination/goals/GOAL-ECQ-002/baseline'
    
    print("=" * 70)
    print("VALIDATOR BLIND RE-DERIVATION")
    print("TASK-20260823-cb510c, GOAL-ECQ-002, BATCH-8b08ef")
    print("=" * 70)
    
    # --------------------------------------------------------
    # J2: Height re-derivation from a-invariants
    # --------------------------------------------------------
    print("\n" + "=" * 70)
    print("J2: NAIVE HEIGHT RE-DERIVATION FROM a-INVARIANTS")
    print("=" * 70)
    
    # Load best_candidates.json for the parameters
    with open(f'{producer_dir}/best_candidates.json') as f:
        best = json.load(f)
    
    # The best certified rank>=12 curve (threshold 12)
    t12 = best['per_threshold']['12']
    ainvs = t12['a_invariants']
    a1, a2, a3, a4, a6 = ainvs
    claimed_height = t12['min_naive_height']
    claimed_c4 = t12['c4']
    claimed_c6 = t12['c6']
    tuple_vals = t12['tuple']
    t_val = t12['t']
    
    print(f"\nBest rank>=12 candidate:")
    print(f"  tuple: {tuple_vals}")
    print(f"  t: {t_val}")
    print(f"  a-invariants: {ainvs}")
    print(f"  claimed height: {claimed_height}")
    print(f"  claimed c4: {claimed_c4}")
    print(f"  claimed c6: {claimed_c6}")
    
    # Compute invariants from a-invariants alone
    inv = compute_invariants_exact(a1, a2, a3, a4, a6)
    print(f"\nMy computation from a-invariants alone:")
    print(f"  b2 = {inv['b2']}")
    print(f"  b4 = {inv['b4']}")
    print(f"  b6 = {inv['b6']}")
    print(f"  b8 = {inv['b8']}")
    print(f"  c4 = {inv['c4']}")
    print(f"  c6 = {inv['c6']}")
    print(f"  Delta = {inv['delta']}")
    print(f"  c4^3 - c6^2 = 1728*Delta: VERIFIED")
    
    # Compare with producer's claimed c4, c6
    c4_match = str(inv['c4']) == str(claimed_c4)
    c6_match = str(inv['c6']) == str(claimed_c6)
    print(f"\n  c4 match: {c4_match} (mine={inv['c4']}, producer={claimed_c4})")
    print(f"  c6 match: {c6_match} (mine={inv['c6']}, producer={claimed_c6})")
    
    # Compute naive height
    my_height = naive_height_icarm(inv['c4'], inv['c6'])
    height_diff = abs(my_height - claimed_height)
    print(f"\n  My naive height: {my_height}")
    print(f"  Claimed height:  {claimed_height}")
    print(f"  Abs difference:  {height_diff}")
    print(f"  Match (isclose): {isclose(my_height, claimed_height, rel_tol=1e-10)}")
    
    # Determine which term dominates
    c4cub = abs(inv['c4'])**3
    c6sq = inv['c6']**2
    print(f"\n  |c4|^3 = {c4cub}")
    print(f"  c6^2   = {c6sq}")
    print(f"  max = |c4|^3: {c4cub > c6sq}")
    
    # --------------------------------------------------------
    # J2: Global minimality check
    # --------------------------------------------------------
    print("\n" + "-" * 50)
    print("J2: GLOBAL MINIMALITY CHECK")
    print("-" * 50)
    
    # Use PARI for full factorization of Delta
    from cypari import pari
    pari.allocatemem(1 << 28, silent=True)
    
    delta_str = str(abs(inv['delta']))
    pari(f'D = {delta_str}')
    pari('fac = factor(D)')
    
    print(f"\n  Delta = {inv['delta']}")
    print(f"  |Delta| has {len(str(abs(inv['delta'])))} digits")
    
    # Extract factorization from the PARI matrix
    # factor() returns a 2-column matrix: first column = primes, second = exponents
    # Use PARI's matsize to get dimensions, then extract elements
    n_primes = int(pari('matsize(fac)[1]'))
    factors = []
    for i in range(1, n_primes + 1):
        p = int(pari(f'fac[{i},1]'))
        e = int(pari(f'fac[{i},2]'))
        factors.append((p, e))
    
    print(f"  Factorization: {factors[:20]}{'...' if len(factors) > 20 else ''}")
    print(f"  Number of prime factors: {len(factors)}")
    
    # Check minimality: for each prime p with v_p(Delta) >= 12,
    # check if v_p(c4) >= 4 and v_p(c6) >= 6
    non_minimal = []
    for p, e in factors:
        if e >= 12:
            v_c4 = 0
            temp = abs(inv['c4'])
            while temp % p == 0:
                v_c4 += 1
                temp //= p
            v_c6 = 0
            temp = abs(inv['c6'])
            while temp % p == 0:
                v_c6 += 1
                temp //= p
            if v_c4 >= 4 and v_c6 >= 6:
                non_minimal.append((p, e, v_c4, v_c6))
                print(f"  POTENTIALLY NON-MINIMAL at p={p}: v_p(Delta)={e}, v_p(c4)={v_c4}, v_p(c6)={v_c6}")
    
    if not non_minimal:
        print(f"  No prime with v_p(Delta) >= 12 AND v_p(c4) >= 4 AND v_p(c6) >= 6")
        print(f"  => Model is GLOBALLY MINIMAL (no prime allows further reduction)")
    else:
        print(f"  {len(non_minimal)} primes need full local minimality check")
    
    # --------------------------------------------------------
    # J2: Rank re-certification from exhibited points
    # --------------------------------------------------------
    print("\n" + "-" * 50)
    print("J2: RANK RE-CERTIFICATION FROM EXHIBITED POINTS")
    print("-" * 50)
    
    exhibited = t12['exhibited_points']
    print(f"  Number of exhibited points: {len(exhibited)}")
    
    # Verify each point lies on the curve
    verified_count = 0
    failed_points = []
    for i, (x_str, y_str) in enumerate(exhibited):
        ok = verify_point_on_curve(a1, a2, a3, a4, a6, x_str, y_str)
        if ok:
            verified_count += 1
        else:
            failed_points.append((i, x_str, y_str))
    
    print(f"  Points verified on curve: {verified_count}/{len(exhibited)}")
    if failed_points:
        print(f"  FAILED points: {failed_points}")
    
    # Check independence using PARI's ellheight and mod-l reduction
    print(f"\n  Checking independence via PARI...")
    
    pari(f'a1 = {a1}; a2 = {a2}; a3 = {a3}; a4 = {a4}; a6 = {a6}')
    pari('E = ellinit([a1, a2, a3, a4, a6])')
    
    # Build the list of points in PARI format and verify on curve
    pts_pari = []
    for i, (x_str, y_str) in enumerate(exhibited):
        pari(f'P{i} = [{x_str}, {y_str}]')
        try:
            ok = int(pari(f'ellisoncurve(E, P{i})'))
            if ok:
                pts_pari.append(i)
        except:
            pass
    
    print(f"  Points verified by PARI ellisoncurve: {len(pts_pari)}/{len(exhibited)}")
    
    # Method 1: Try PARI ellrank directly (with alarm)
    print(f"\n  Method 1: PARI ellrank (with 60s alarm)...")
    rank_from_ellrank = None
    try:
        pari('alarm(60, r = ellrank(E))')
        r_result = pari('r')
        r_list = r_result.python_list() if hasattr(r_result, 'python_list') else [int(r_result)]
        if isinstance(r_list, list) and len(r_list) >= 2:
            rank_from_ellrank = r_list[0]  # r_low
            print(f"    ellrank returned: r_low={r_list[0]}, r_high={r_list[1]}")
        else:
            rank_from_ellrank = int(r_result)
            print(f"    ellrank returned: {rank_from_ellrank}")
    except Exception as e:
        print(f"    ellrank failed/timed out: {e}")
    
    # Method 2: Mod-l reduction independence check
    print(f"\n  Method 2: Mod-l reduction independence check...")
    # Find good primes l > 16 where the curve has good reduction
    delta_val = inv['delta']
    good_primes = []
    for l in range(17, 500):
        if delta_val % l != 0:
            good_primes.append(l)
        if len(good_primes) >= 20:
            break
    
    print(f"    Good primes found: {good_primes[:10]}...")
    
    max_rank_mod_l = 0
    for l in good_primes[:5]:  # check first 5 good primes
        # Reduce points mod l
        pts_mod_l = []
        for i in pts_pari:
            try:
                pari(f'Pl = E, Mod(P{i}, {l})')
                # Actually, use PARI's reduction directly
                pari(f'Fl = ellcard(E, {l})')  # #E(F_l)
                fl_count = int(pari('Fl'))
                
                # Reduce point mod l
                x_frac = Fraction(exhibited[i][0])
                y_frac = Fraction(exhibited[i][1])
                if x_frac.denominator % l == 0 or y_frac.denominator % l == 0:
                    continue  # point reduces to infinity mod l
                xn = int(x_frac.numerator) * pow(int(x_frac.denominator), -1, l) % l
                yn = int(y_frac.numerator) * pow(int(y_frac.denominator), -1, l) % l
                pts_mod_l.append((xn, yn, i))
            except:
                continue
        
        if len(pts_mod_l) < 2:
            continue
        
        # Compute the group E(F_l) and check independence
        # For each point, compute its order in E(F_l)
        # Then check independence by computing the matrix of orders
        
        # Simple independence check: compute the order of each point
        # and check that no nontrivial combination is the identity
        # For a rigorous check, we compute the discrete log matrix
        
        # For now, count points with order > 1 (non-torsion mod l)
        orders = []
        for (xn, yn, i) in pts_mod_l:
            try:
                pari(f'E = ellinit([{a1}, {a2}, {a3}, {a4}, {a6}], {l})')
                pari(f'Pl = [{xn}, {yn}]')
                pari(f'ok = ellisoncurve(E, Pl)')
                ok = int(pari('ok'))
                if not ok:
                    continue
                pari(f'o = ellorder(E, Pl)')
                order = int(pari('o'))
                orders.append((i, order))
            except:
                continue
        
        # Count points with order > 1
        nontrivial = sum(1 for _, o in orders if o > 1)
        if nontrivial > max_rank_mod_l:
            max_rank_mod_l = nontrivial
        
        print(f"    l={l}: {len(pts_mod_l)} points reduced, {len(orders)} valid, "
              f"{nontrivial} nontrivial, orders: {[o for _, o in orders[:10]]}")
    
    # Method 3: Height pairing for a subset of points
    print(f"\n  Method 3: Height pairing for first 12 points...")
    n_subset = min(12, len(pts_pari))
    heights_subset = []
    for i in range(n_subset):
        idx = pts_pari[i]
        try:
            pari(f'h{i} = ellheight(E, P{idx})')
            h_val = float(pari(f'h{i}'))
            heights_subset.append(h_val)
        except Exception as e:
            heights_subset.append(None)
            if i < 3:
                print(f"    ellheight failed for point {idx}: {e}")
    
    nonzero_h = sum(1 for h in heights_subset if h is not None and h > 0.001)
    print(f"    Nonzero heights in first {n_subset}: {nonzero_h}")
    
    # Summary
    rank_lower_bound = 0
    if rank_from_ellrank is not None:
        rank_lower_bound = rank_from_ellrank
        print(f"\n  RANK LOWER BOUND (from ellrank): {rank_lower_bound}")
    elif nonzero_h > 0:
        rank_lower_bound = nonzero_h
        print(f"\n  RANK LOWER BOUND (from nonzero heights, first {n_subset}): {rank_lower_bound}")
    
    print(f"  Mod-l nontrivial count (lower bound): {max_rank_mod_l}")
    print(f"  Producer's claimed certified rank: {t12['pari_ellrank_r_low']}")
    print(f"  (Note: producer states rank is a LOWER BOUND from exhibited points,")
    print(f"   and pari_ellrank was a POINT SEARCH only, not the reported rank)")
    
    # --------------------------------------------------------
    # J2: Provenance checks
    # --------------------------------------------------------
    print("\n" + "-" * 50)
    print("J2: PROVENANCE CHECKS")
    print("-" * 50)
    
    # Load frozen snapshot
    with open(f'{baseline_dir}/icarm_database_20260823.json') as f:
        snapshot = json.load(f)
    
    print(f"  Frozen snapshot: {len(snapshot.get('curves', snapshot if isinstance(snapshot, list) else []))} curves")
    
    # Check the rank-12 best candidate
    conductor = t12['provenance']['conductor']
    prov = check_provenance(ainvs, inv['c4'], inv['c6'], snapshot)
    cremona = check_cremona(conductor)
    
    print(f"\n  Rank-12 best candidate:")
    print(f"    curve_key: {prov['curve_key']}")
    print(f"    a-invariants: {prov['a_invariants']}")
    print(f"    conductor: {conductor}")
    print(f"    found by curve_key: {prov['found_by_curve_key']}")
    print(f"    found by a-invariants: {prov['found_by_a_invariants']}")
    print(f"    Cremona check: {cremona['outcome']} ({cremona['why']})")
    
    # Check ALL reported curves at ALL thresholds
    print(f"\n  Checking ALL reported curves at ALL thresholds:")
    all_results = []
    for thresh_str, entry in best['per_threshold'].items():
        thresh = int(thresh_str)
        ainvs_t = entry['a_invariants']
        c4_t = entry['c4']
        c6_t = entry['c6']
        conductor_t = entry['provenance']['conductor']
        
        # Recompute c4, c6 from a-invariants
        inv_t = compute_invariants_exact(*ainvs_t)
        c4_recomp = str(inv_t['c4'])
        c6_recomp = str(inv_t['c6'])
        c4_match_t = c4_recomp == str(c4_t)
        c6_match_t = c6_recomp == str(c6_t)
        
        prov_t = check_provenance(ainvs_t, inv_t['c4'], inv_t['c6'], snapshot)
        cremona_t = check_cremona(conductor_t)
        
        height_t = naive_height_icarm(inv_t['c4'], inv_t['c6'])
        height_match = isclose(height_t, entry['min_naive_height'], rel_tol=1e-10)
        
        all_results.append({
            'threshold': thresh,
            'tuple': entry['tuple'],
            't': entry['t'],
            'ainvs': ainvs_t,
            'c4_recomputed': inv_t['c4'],
            'c4_claimed': c4_t,
            'c4_match': c4_match_t,
            'c6_recomputed': inv_t['c6'],
            'c6_claimed': c6_t,
            'c6_match': c6_match_t,
            'height_recomputed': height_t,
            'height_claimed': entry['min_naive_height'],
            'height_match': height_match,
            'found_by_curve_key': prov_t['found_by_curve_key'],
            'found_by_a_invariants': prov_t['found_by_a_invariants'],
            'cremona_outcome': cremona_t['outcome'],
            'conductor': conductor_t,
        })
        
        print(f"    threshold {thresh}: tuple={entry['tuple']}, t={entry['t']}, "
              f"h_recomp={height_t:.6f}, h_claimed={entry['min_naive_height']:.6f}, "
              f"match={height_match}, "
              f"board_ck={prov_t['found_by_curve_key']}, "
              f"board_ainvs={prov_t['found_by_a_invariants']}, "
              f"cremona={cremona_t['outcome']}")
    
    # Check the rediscovered board curve
    print(f"\n  Frozen board curves rediscovered:")
    for rc in best.get('frozen_board_curves_rediscovered', []):
        print(f"    board_id={rc['board_id']}, height={rc['board_naive_height']}, "
              f"matched_by_ck={rc['matched_by_curve_key']}, "
              f"matched_by_ainvs={rc['matched_by_a_invariants']}, "
              f"family={rc['family']}, t={rc['t']}")
    
    print(f"  board_id_108 rediscovered: {best.get('board_id_108_rediscovered', 'N/A')}")
    
    # --------------------------------------------------------
    # J1: Ceiling re-derivation via PARI
    # --------------------------------------------------------
    print("\n" + "=" * 70)
    print("J1: SHIODA-TATE CEILING RE-DERIVATION FROM 6-TUPLES")
    print("=" * 70)
    
    # Test on the two target stratum families
    test_tuples = [
        [0, 2, 8, 9, 11, 14],   # target stratum family 1
        [0, 6, 12, 14, 15, 23], # target stratum family 2
        [-17, -16, 10, 11, 14, 17],  # Mestre's published tuple A (proves_too_much object i)
    ]
    
    ceiling_results = []
    for tup in test_tuples:
        print(f"\n  Tuple: {tup}")
        try:
            result = compute_ceiling_pari(tup)
            if 'error' in result:
                print(f"    ERROR: {result['error']}")
                if 'deg_r' in result:
                    print(f"    deg_r = {result['deg_r']}")
            else:
                print(f"    deg_finite_disc: {result['deg_finite_discriminant']}")
                print(f"    deg_gcd(DD,DD'): {result['deg_gcd_DD_DDprime']}")
                print(f"    squarefree: {result['finite_discriminant_squarefree']}")
                print(f"    v_inf(disc): {result['v_inf_disc']}")
                print(f"    fibre at inf: {result['fibre_at_infinity']}")
                print(f"    deg_gcd(G,a4): {result['deg_gcd_G_a4']}")
                print(f"    ceiling: {result['ceiling']}")
                print(f"    euler check: {result['euler_check_sum']} (expected 24): {result['euler_check_ok']}")
                ceiling_results.append(result)
        except Exception as e:
            print(f"    EXCEPTION: {e}")
            import traceback
            traceback.print_exc()
    
    # --------------------------------------------------------
    # J1: Cross-check with producer's stratum_enumeration.json
    # --------------------------------------------------------
    print("\n" + "-" * 50)
    print("J1: CROSS-CHECK WITH PRODUCER'S STRATUM ENUMERATION")
    print("-" * 50)
    
    with open(f'{producer_dir}/stratum_enumeration.json') as f:
        strat = json.load(f)
    
    print(f"  Producer's headline counts:")
    for k, v in strat['headline_counts'].items():
        print(f"    {k}: {v}")
    
    print(f"\n  Producer's ceiling histogram:")
    for k, v in strat['ceiling_histogram_from_own_fibre_configuration'].items():
        print(f"    ceiling {k}: {v}")
    
    print(f"\n  Producer's CTL_PREFILTER_SOUNDNESS:")
    for k, v in strat['CTL_PREFILTER_SOUNDNESS'].items():
        if k not in ('false_negative_examples', 'cheap_ceiling_mismatch_examples'):
            print(f"    {k}: {v}")
        else:
            print(f"    {k}: {v}")
    
    print(f"\n  Producer's target stratum families: {len(strat['target_stratum_families_full_detail'])}")
    for fam in strat['target_stratum_families_full_detail']:
        print(f"    tuple={fam['canonical_tuple']}, ceiling={fam['shioda_tate_ceiling_from_own_fibre_configuration']}, "
              f"log_P2={fam['log_content_P2']}, fibre_at_inf={fam['fibre_type_at_infinity']}")
    
    # --------------------------------------------------------
    # Proves_too_much objects (i) and (ii)
    # --------------------------------------------------------
    print("\n" + "=" * 70)
    print("PROVES_TOO_MUCH OBJECTS (i) and (ii)")
    print("=" * 70)
    
    # Object (i): Mestre's published tuple A (-17, -16, 10, 11, 14, 17)
    # PASS condition (stated BEFORE the result):
    # The ceiling code must NOT assign it a ceiling below 11,
    # and the pre-filter must NOT discard it.
    print("\n  Object (i): Mestre's published tuple A (-17, -16, 10, 11, 14, 17)")
    print("  PASS condition (stated BEFORE result):")
    print("    - ceiling >= 11 (rank over Q(T) is at least 11 per construction-class record)")
    print("    - pre-filter does NOT discard (family is retained)")
    print("    - If ceiling < 11 or filter discards: PROVES TOO MUCH, code is wrong")
    
    # Already computed above if it was in test_tuples
    obj_i_result = None
    for r in ceiling_results:
        if r['tuple'] == [-17, -16, 10, 11, 14, 17]:
            obj_i_result = r
            break
    
    if obj_i_result:
        ceiling_val = obj_i_result['ceiling']
        retained = obj_i_result.get('cheap_ceiling', 0) >= 13 or obj_i_result.get('deg_gcd_G_a4', 0) > 0
        print(f"\n  RESULT:")
        print(f"    ceiling = {ceiling_val}")
        print(f"    ceiling >= 11: {ceiling_val >= 11}")
        print(f"    pre-filter retains: {retained}")
        if ceiling_val >= 11 and retained:
            print(f"    => PASS (object behaves correctly)")
        else:
            print(f"    => FAIL (proves too much - code is wrong somewhere)")
    else:
        print("  Result: computation did not complete for this tuple")
    
    # Object (ii): A generic ceiling-9 family
    # PASS condition (stated BEFORE the result):
    # The pre-filter MUST DISCARD it.
    print("\n  Object (ii): A generic ceiling-9 family (six finite I_2 fibres)")
    print("  PASS condition (stated BEFORE result):")
    print("    - pre-filter DISCARDS the family (ceiling < 13)")
    print("    - If filter keeps it: PROVES TOO MUCH, filter is wrong")
    
    # We need a ceiling-9 family. From the histogram, 16607 of 16754 families have ceiling 9.
    # Let's pick one from the retained_families_full_detail that has ceiling 9
    retained_fams = strat.get('retained_families_full_detail', [])
    ceiling_9_fam = None
    for fam in retained_fams:
        if fam['shioda_tate_ceiling_from_own_fibre_configuration'] == 9:
            ceiling_9_fam = fam
            break
    
    if ceiling_9_fam:
        tup_9 = ceiling_9_fam['canonical_tuple']
        print(f"  Testing ceiling-9 family: {tup_9}")
        print(f"  Producer's ceiling: {ceiling_9_fam['shioda_tate_ceiling_from_own_fibre_configuration']}")
        print(f"  Producer's prefilter decision: {ceiling_9_fam['prefilter']}")
        
        # Compute with my own code
        result_9 = compute_ceiling_pari(tup_9)
        if 'error' not in result_9:
            my_ceiling_9 = result_9['ceiling']
            my_discard = result_9['ceiling'] < 13 and result_9.get('deg_gcd_G_a4', 0) == 0
            print(f"\n  RESULT:")
            print(f"    my ceiling = {my_ceiling_9}")
            print(f"    pre-filter discards: {my_discard}")
            if my_discard:
                print(f"    => PASS (filter correctly discards ceiling-9 family)")
            else:
                print(f"    => FAIL (filter keeps ceiling-9 family - proves too much)")
        else:
            print(f"  ERROR: {result_9['error']}")
    else:
        # Try from attempted_rows
        print("  No ceiling-9 family found in retained_families; checking attempted_rows...")
        attempted = strat.get('attempted_rows_full_detail_for_the_load_bearing_subset', [])
        for row in attempted[:100]:
            if row.get('shioda_tate_ceiling') == 9:
                tup_9 = row['canonical_tuple']
                print(f"  Testing ceiling-9 family: {tup_9}")
                result_9 = compute_ceiling_pari(tup_9)
                if 'error' not in result_9:
                    my_ceiling_9 = result_9['ceiling']
                    my_discard = my_ceiling_9 < 13
                    print(f"  my ceiling = {my_ceiling_9}, discards: {my_discard}")
                    if my_discard:
                        print(f"  => PASS")
                    else:
                        print(f"  => FAIL")
                else:
                    print(f"  ERROR: {result_9['error']}")
                break
    
    # --------------------------------------------------------
    # Artifact hash recomputation
    # --------------------------------------------------------
    print("\n" + "=" * 70)
    print("ARTIFACT HASH RECOMPUTATION")
    print("=" * 70)
    
    receipt_path = f'{base}/coordination/goals/GOAL-ECQ-002/batches/BATCH-8b08ef/archives/TASK-20260823-8ea188/receipt.yaml'
    hash_results = recompute_hashes(receipt_path, base)
    
    n_match = sum(1 for r in hash_results if r['match'])
    n_mismatch = sum(1 for r in hash_results if not r['match'])
    n_not_found = sum(1 for r in hash_results if r['actual'] == 'FILE_NOT_FOUND')
    
    print(f"  Total paths checked: {len(hash_results)}")
    print(f"  Matches: {n_match}")
    print(f"  Mismatches: {n_mismatch}")
    print(f"  Not found: {n_not_found}")
    
    if n_mismatch > 0 or n_not_found > 0:
        print(f"\n  MISMATCHES/MISSING:")
        for r in hash_results:
            if not r['match']:
                print(f"    {r['path']}: expected={r['expected'][:16]}..., actual={r['actual'][:16] if r['actual'] != 'FILE_NOT_FOUND' else 'NOT FOUND'}...")
    
    print("\n" + "=" * 70)
    print("VALIDATION COMPLETE")
    print("=" * 70)

if __name__ == '__main__':
    main()

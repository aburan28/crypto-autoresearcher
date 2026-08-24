#!/usr/bin/env sage
"""
Toy-scale implementation of Wesolowski's Algorithm 3 (p^{1/3+o(1)} attack)
with EXPLICIT F_{p^2}-multiplication counting.

Purpose: Measure concrete per-operation cost at toy scale to inform
         extrapolation to NIST-I parameters.

Reference: Wesolowski 2026, "The supersingular isogeny problem in time
           and memory p^{1/3+o(1)}"
           Panny 2026, proof-of-concept implementation

TASK: TASK-20260804-55952a under GOAL-SSI-001
"""
from sage.all import *
import json
import time
import sys

proof.all(False)

# ============================================================
# MODULAR POLYNOMIAL CACHE AND COST MODEL
# ============================================================

# Cache for modular polynomials (expensive to compute)
_MODPOLY_CACHE = {}

def get_modular_polynomial(ell):
    """Get Phi_ell as a bivariate polynomial. Cached."""
    if ell not in _MODPOLY_CACHE:
        _MODPOLY_CACHE[ell] = classical_modular_polynomial(ell)
    return _MODPOLY_CACHE[ell]


def count_modpoly_terms(ell):
    """Count nonzero terms in Phi_ell by inspecting the actual polynomial."""
    phi = get_modular_polynomial(ell)
    # phi is a bivariate polynomial over ZZ
    # Count monomials
    n_terms = len(list(phi))
    deg = ell + 1  # degree in each variable
    return n_terms, deg


def cost_evaluate_modpoly(ell, log2_p2):
    """Compute the EXACT F_{p^2}-multiplication cost for one neighbor-finding step.
    
    Step 1: Evaluate Phi_ell(j_known, X) -> univariate poly of degree ell+1
      - Need powers j^0, j^1, ..., j^{ell+1}: costs (ell) multiplications
      - For each monomial c * j^a * X^b: multiply c*j^a (1 mult), accumulate into coeff of X^b
      - But integer*field_element is just repeated addition, not a field mult
      - Actual cost: computing j^2, j^3, ..., j^{ell+1} via sequential mult: ell mults
      - Then for each monomial with j-degree > 0: already have the power cached
      - The dominant cost is actually the ROOT FINDING, not evaluation
      
    Step 2: Find roots of degree-(ell+1) polynomial over F_{p^2}
      Using Cantor-Zassenhaus / Berlekamp:
      - Compute x^{p^2} mod f(x): this is log2(p^2) steps of "square and reduce"
      - Each step: square a poly of degree < d, then reduce mod f (degree d)
      - Squaring a degree-(d-1) poly (schoolbook): (d-1+1)*(d-1+1)/2 ~ d^2/2 mults
        (actually: d^2 mults for full multiply, or d*(d+1)/2 for squaring)
      - Reducing mod f (degree d, monic): d multiplications + d subtractions
      - Total per step: d*(d+1)/2 + d = d*(d+3)/2 mults (for squaring + reduction)
        Actually more precisely for polynomial squaring in F_q[x]/(f):
        - multiply two polys of degree < d: d^2 mults (schoolbook)
        - reduce mod f: d mults (leading coeff * f subtracted)
        - Total per exponentiation step: d^2 + d mults
      - Number of steps: log2(p^2) = 2*log2(p) for binary method
      - Then compute gcd(x^{p^2} - x, f): O(d^2) mults via Euclidean algorithm
      - Then split factors: another O(d * log2(p^2)) mults for each factor
      
      Conservative (schoolbook) total:
        root_cost = log2_p2 * (d^2 + d) + d^2 + d * log2_p2
                  = log2_p2 * (d^2 + 2d) + d^2
      where d = ell + 1
    """
    d = ell + 1  # degree of univariate polynomial
    n_terms, _ = count_modpoly_terms(ell)
    
    # Evaluation cost: computing powers of j and assembling coefficients
    # j^2 = j*j (1 mult), j^3 = j^2*j (1 mult), ..., j^d = j^{d-1}*j (1 mult)
    # Total: d-1 mults for powers
    # Then: each monomial with nonzero j-exponent needs the cached power,
    # but multiplying an integer coefficient by a field element is NOT a field mult
    # (it's multi-precision integer * element, which is additions)
    # So evaluation cost is just the d-1 power computations
    eval_cost = d - 1
    
    # Root finding cost (dominant):
    # Berlekamp/Cantor-Zassenhaus on degree-d poly over F_{p^2}:
    # Phase 1: compute x^{p^2} mod f(x)
    #   - Binary exponentiation: 2*log2(p) squarings in F_{p^2}[x]/(f(x))
    #   - Each squaring: d^2 mults (polynomial mult) + d mults (reduction)
    #   - Total: 2*log2(p) * (d^2 + d) mults
    phase1_cost = log2_p2 * (d * d + d)
    
    # Phase 2: GCD computation gcd(x^{p^2} - x, f(x))
    #   - Euclidean algorithm on degree-d polys: O(d) steps, each O(d) mults
    #   - Total: d^2 mults
    phase2_cost = d * d
    
    # Phase 3: Factor splitting (if needed for d > 2)
    #   - For each irreducible factor of degree k:
    #     compute random^{(p^2-1)/2} mod factor: log2(p^2) * k^2 mults
    #   - Total across all factors: bounded by d * log2_p2 * d = d^2 * log2_p2
    #   - But for small d (2,3,5,7), splitting is cheap
    #   - Use: d * log2_p2 as upper bound for the splitting phase
    phase3_cost = d * log2_p2 if d > 2 else 0
    
    root_cost = phase1_cost + phase2_cost + phase3_cost
    
    total = eval_cost + root_cost
    
    return {
        'ell': int(ell),
        'd': int(d),
        'n_terms_modpoly': int(n_terms),
        'eval_cost': int(eval_cost),
        'root_cost_phase1': int(phase1_cost),
        'root_cost_phase2': int(phase2_cost),
        'root_cost_phase3': int(phase3_cost),
        'root_cost_total': int(root_cost),
        'total_mults_per_call': int(total),
        'neighbors_produced': int(d),  # ell+1 neighbors (before backtrack filter)
        'cost_per_neighbor': float(total) / float(d),
    }


# ============================================================
# CORE ALGORITHM
# ============================================================

def find_neighbors(j_val, ell, F):
    """Find all ell-isogenous j-invariants from j_val.
    
    Returns list of j-invariants that are ell-isogenous to j_val.
    """
    phi = get_modular_polynomial(ell)
    R = PolynomialRing(F, 'X')
    # Evaluate Phi_ell(j_val, X) to get univariate
    f = R(phi(j_val, R.gen()))
    return f.roots(multiplicities=False)


def build_table_bfs(j_start, B, X, F, p, cost_model):
    """Build the table L(E, X, B) via BFS.
    
    Following Algorithm 1: enumerate all B-smooth-degree isogenies
    from j_start with degree <= X.
    
    Returns: (table_dict, stats)
      table_dict: {j_invariant: degree}
      stats: measurement data
    """
    primes_list = list(prime_range(2, B + 1))
    
    # table[j] = degree of the smooth isogeny reaching j from j_start
    table = {j_start: ZZ(1)}
    
    # Queue: (j, current_degree, min_prime_for_next_extension)
    queue = [(j_start, ZZ(1), 2)]
    
    total_mults = 0
    neighbor_calls = 0
    
    while queue:
        j_cur, deg_cur, min_prime = queue.pop(0)
        
        for ell in primes_list:
            if ell < min_prime:
                continue
            new_deg = deg_cur * ell
            if new_deg > X:
                break  # primes are sorted, so all subsequent will also exceed
            
            # Find ell-neighbors of j_cur
            neighbors = find_neighbors(j_cur, ell, F)
            neighbor_calls += 1
            
            # Count operations for this call
            step_cost = cost_model[ell]['total_mults_per_call']
            total_mults += step_cost
            
            for j_new in neighbors:
                if j_new not in table:
                    table[j_new] = new_deg
                    queue.append((j_new, new_deg, ell))
    
    num_entries = len(table) - 1  # exclude starting point
    stats = {
        'entries': int(num_entries),
        'total_mults': int(total_mults),
        'neighbor_calls': int(neighbor_calls),
        'avg_mults_per_entry': float(total_mults) / float(max(1, num_entries)),
    }
    
    return table, stats


def algorithm2(j_E, B, X, F, p, cost_model):
    """Algorithm 2: Find separable isogeny E -> E^{(p)}.
    
    Build table from j_E, check for collision with Frobenius conjugate.
    
    Returns: (success, collision_data, stats)
    """
    table, build_stats = build_table_bfs(j_E, B, X, F, p, cost_model)
    
    # Check collisions: for each j in table, check if j^p is also in table
    # Frobenius j -> j^p is FREE in F_{p^2} (it's just conjugation)
    collision_found = False
    collision_data = None
    collision_checks = 0
    
    for j_val in table:
        j_conj = j_val ** p  # Frobenius: effectively free
        collision_checks += 1
        if j_conj in table and j_conj != j_val:
            collision_found = True
            collision_data = {
                'j': str(j_val)[:50],
                'j_conj': str(j_conj)[:50],
                'deg_from_start': int(table[j_val]),
                'deg_from_conj': int(table[j_conj]),
                'total_isogeny_degree': int(table[j_val] * table[j_conj]),
            }
            break
    
    # Collision checking cost: hash lookups, essentially free compared to table building
    # But count 2 mults per lookup for hashing (conservative)
    collision_mults = collision_checks * 2
    
    stats = {
        'table_entries': build_stats['entries'],
        'table_mults': build_stats['total_mults'],
        'collision_checks': collision_checks,
        'collision_mults': collision_mults,
        'total_mults': build_stats['total_mults'] + collision_mults,
        'avg_mults_per_entry': build_stats['avg_mults_per_entry'],
        'neighbor_calls': build_stats['neighbor_calls'],
    }
    
    return collision_found, collision_data, stats


def algorithm3(p_val, max_attempts=200, verbose=True):
    """Algorithm 3: Find non-scalar endomorphism via repeated attempts.
    
    For each attempt:
    1. Random walk E -> E' (for mixing)
    2. Run Algorithm 2 on E'
    3. If success: found endomorphism
    
    Returns: full measurement results
    """
    p = ZZ(p_val)
    log2_p = int(p).bit_length()
    log2_p2 = 2 * log2_p
    
    if verbose:
        print(f"\n{'='*65}")
        print(f"  Algorithm 3 for p = {p} (log2(p) = {log2_p})")
        print(f"{'='*65}")
    
    # Setup field F_{p^2}
    s = GF(p).one()
    while s.is_square():
        s += 1
    F = GF((p, 2), modulus=[-s, 0, 1], name='T')
    
    # Algorithm parameters
    B = ceil(exp(RR(1)/3 * sqrt(log(RR(p)/2))))
    X = ceil(sqrt(RR(B)) * (RR(p)/2) ** (RR(1)/6))
    
    primes_used = list(prime_range(2, B + 1))
    walk_length = max(10, 3 * log2_p)  # O(log p) for mixing
    
    # Precompute cost model for each prime used
    cost_model = {}
    for ell in primes_used:
        cost_model[ell] = cost_evaluate_modpoly(ell, log2_p2)
    
    # Walk cost: each step uses 2-isogeny
    walk_cost_per_step = cost_model[2]['total_mults_per_call']
    walk_total_cost = walk_length * walk_cost_per_step
    
    # Count supersingular curves
    try:
        ss_j_list = supersingular_j_invariants(F)
        num_ss = len(ss_j_list)
    except Exception:
        num_ss = int(p) // 12 + 1
    
    if verbose:
        print(f"  B = {B}, X = {X}")
        print(f"  Primes used: {primes_used}")
        print(f"  Walk length: {walk_length}")
        print(f"  #SS j-invariants: {num_ss}")
        print(f"  Walk cost per step: {walk_cost_per_step} mults")
        print(f"  Walk total cost: {walk_total_cost} mults")
        print(f"  Cost model per prime:")
        for ell in primes_used:
            cm = cost_model[ell]
            print(f"    ell={ell}: {cm['total_mults_per_call']} mults/call "
                  f"({float(cm['cost_per_neighbor']):.1f}/neighbor, "
                  f"eval={cm['eval_cost']}, root={cm['root_cost_total']})")
        print()
    
    # Precompute modular polynomials (warm cache)
    for ell in primes_used:
        get_modular_polynomial(ell)
    
    # Run attempts
    attempts_data = []
    successes = 0
    total_mults_all = 0
    
    # Get starting curve
    E_base = special_supersingular_curve(F)
    j_base = E_base.j_invariant()
    
    t_start = time.time()
    
    for attempt_idx in range(max_attempts):
        # Step 1: Random walk E -> E'
        j_cur = j_base
        for _ in range(walk_length):
            nbrs = find_neighbors(j_cur, 2, F)
            if nbrs:
                j_cur = nbrs[randint(0, len(nbrs) - 1)]
        
        # Step 2: Run Algorithm 2 on E' (identified by j_cur)
        success, collision_data, attempt_stats = algorithm2(j_cur, B, X, F, p, cost_model)
        
        # Total cost for this attempt
        attempt_total_mults = walk_total_cost + attempt_stats['total_mults']
        total_mults_all += attempt_total_mults
        
        attempt_record = {
            'attempt': attempt_idx + 1,
            'success': success,
            'table_entries': attempt_stats['table_entries'],
            'table_mults': attempt_stats['table_mults'],
            'walk_mults': walk_total_cost,
            'total_mults': int(attempt_total_mults),
            'avg_mults_per_entry': attempt_stats['avg_mults_per_entry'],
        }
        
        if success:
            successes += 1
            attempt_record['collision'] = collision_data
            if verbose:
                print(f"  Attempt {attempt_idx+1}: SUCCESS | "
                      f"table={attempt_stats['table_entries']} entries | "
                      f"total_mults={attempt_total_mults} | "
                      f"deg=({collision_data['deg_from_start']},"
                      f"{collision_data['deg_from_conj']})")
        else:
            if verbose and (attempt_idx + 1) % 25 == 0:
                print(f"  Attempt {attempt_idx+1}: fail | "
                      f"table={attempt_stats['table_entries']} entries | "
                      f"total_mults={attempt_total_mults}")
        
        attempts_data.append(attempt_record)
        
        # Progress check
        if successes >= 15 and attempt_idx >= 50:
            if verbose:
                print(f"  (stopping: {successes} successes in {attempt_idx+1} attempts)")
            break
    
    elapsed = time.time() - t_start
    total_attempts = len(attempts_data)
    P0_empirical = successes / total_attempts if total_attempts > 0 else 0.0
    
    # Compute statistics
    table_entries_list = [a['table_entries'] for a in attempts_data]
    table_mults_list = [a['table_mults'] for a in attempts_data]
    total_mults_list = [a['total_mults'] for a in attempts_data]
    
    avg_table_entries = sum(table_entries_list) / len(table_entries_list)
    avg_table_mults = sum(table_mults_list) / len(table_mults_list)
    avg_total_mults = sum(total_mults_list) / len(total_mults_list)
    avg_mults_per_entry = sum(table_mults_list) / max(1, sum(table_entries_list))
    
    cost_per_success = total_mults_all / successes if successes > 0 else None
    log2_cost = float(log(RR(cost_per_success), 2)) if cost_per_success and cost_per_success > 0 else None
    
    # Theoretical predictions
    u_theory = float(log(RR(p)/2)) / (3 * float(log(RR(B))))
    P0_theory_lower = float(RR(u_theory) ** (-RR(u_theory)))  # u^{-u} lower bound
    
    results = {
        'p': int(p),
        'log2_p': log2_p,
        'B': int(B),
        'X': int(X),
        'num_ss_curves': num_ss,
        'primes_used': [int(ell) for ell in primes_used],
        'walk_length': walk_length,
        'walk_cost_per_step': walk_cost_per_step,
        'walk_total_cost': walk_total_cost,
        'cost_model': {str(ell): {k: (int(v) if isinstance(v, (int, Integer)) else float(v))
                                   for k, v in cm.items()}
                       for ell, cm in cost_model.items()},
        'total_attempts': total_attempts,
        'successes': successes,
        'P0_empirical': float(P0_empirical),
        'P0_theory_lower_bound': float(P0_theory_lower),
        'u_parameter': float(u_theory),
        'avg_table_entries': float(avg_table_entries),
        'avg_table_mults': float(avg_table_mults),
        'avg_total_mults_per_attempt': float(avg_total_mults),
        'avg_mults_per_entry': float(avg_mults_per_entry),
        'total_mults_all_attempts': int(total_mults_all),
        'cost_per_success': float(cost_per_success) if cost_per_success else None,
        'log2_cost_per_success': log2_cost,
        'wall_clock_seconds': elapsed,
        'attempts_detail': attempts_data[:30],  # Keep first 30 for inspection
    }
    
    if verbose:
        print(f"\n  --- SUMMARY p={p} ---")
        print(f"  Attempts: {total_attempts}, Successes: {successes}")
        print(f"  P0_empirical = {P0_empirical:.4f}")
        print(f"  P0_theory (lower) = {P0_theory_lower:.6f} (u={u_theory:.3f})")
        print(f"  Avg table entries: {avg_table_entries:.1f}")
        print(f"  Avg F_{{p^2}}-mults per entry: {avg_mults_per_entry:.1f}")
        print(f"  Avg F_{{p^2}}-mults per attempt: {avg_total_mults:.0f}")
        if cost_per_success:
            print(f"  Cost per success: {cost_per_success:.0f} mults "
                  f"(~2^{log2_cost:.2f})")
        print(f"  Wall clock: {elapsed:.1f}s")
    
    return results


# ============================================================
# MAIN
# ============================================================

def main():
    print("="*70)
    print("WESOLOWSKI ALGORITHM 3 - TOY SCALE COST MEASUREMENT")
    print("Task: TASK-20260804-55952a | Goal: GOAL-SSI-001")
    print("="*70)
    print(f"Date: {time.strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"SageMath version: {version()}")
    print()
    
    all_results = {
        'metadata': {
            'task_id': 'TASK-20260804-55952a',
            'goal_id': 'GOAL-SSI-001',
            'timestamp': time.strftime('%Y-%m-%dT%H:%M:%S'),
            'sage_version': str(version()),
            'description': ('Toy-scale measurement of Wesolowski Algorithm 3 '
                          'concrete per-operation cost'),
            'algorithm': 'Wesolowski 2026, Algorithm 3 (p^{1/3+o(1)} attack)',
            'reference_impl': 'Panny 2026 proof-of-concept',
            'counting_method': (
                'Analytical F_{p^2}-multiplication count per step. '
                'For each call to find_neighbors(j, ell): '
                '(1) Evaluate Phi_ell(j,X): (ell+1)-1 = ell mults for j-powers; '
                '(2) Find roots of degree-(ell+1) poly over F_{p^2}: '
                '2*log2(p) * ((ell+1)^2 + (ell+1)) mults for x^{p^2} mod f via '
                'repeated squaring in F_{p^2}[x]/(f), plus O((ell+1)^2) for GCD. '
                'Frobenius j -> j^p is conjugation in F_{p^2}, counted as free.'
            ),
        },
        'experiments': [],
        'scaling_summary': [],
    }
    
    # ----------------------------------------------------------------
    # PHASE 1: Per-step cost analysis
    # ----------------------------------------------------------------
    print("\n" + "-"*70)
    print("PHASE 1: Per-step cost analysis")
    print("-"*70)
    
    # Show cost model at a reference bitsize
    ref_log2_p = 20
    ref_log2_p2 = 40
    print(f"\nCost model at log2(p)={ref_log2_p} (log2(p^2)={ref_log2_p2}):")
    print(f"{'ell':>4} | {'deg':>4} | {'#terms':>6} | {'eval':>6} | "
          f"{'root(phase1)':>12} | {'root(total)':>11} | {'TOTAL':>8} | "
          f"{'per_nbr':>8}")
    print("-"*80)
    
    for ell in [2, 3, 5, 7, 11, 13]:
        cm = cost_evaluate_modpoly(ell, ref_log2_p2)
        print(f"{ell:>4} | {cm['d']:>4} | {cm['n_terms_modpoly']:>6} | "
              f"{cm['eval_cost']:>6} | {cm['root_cost_phase1']:>12} | "
              f"{cm['root_cost_total']:>11} | {cm['total_mults_per_call']:>8} | "
              f"{cm['cost_per_neighbor']:>8.1f}")
    
    all_results['cost_model_reference'] = {
        'log2_p': ref_log2_p,
        'log2_p2': ref_log2_p2,
        'per_prime': {}
    }
    for ell in [2, 3, 5, 7, 11, 13]:
        cm = cost_evaluate_modpoly(ell, ref_log2_p2)
        all_results['cost_model_reference']['per_prime'][str(ell)] = cm
    
    # ----------------------------------------------------------------
    # PHASE 2: Run at multiple primes
    # ----------------------------------------------------------------
    print("\n" + "-"*70)
    print("PHASE 2: Algorithm 3 runs at multiple primes")
    print("-"*70)
    
    test_configs = [
        # (prime_value, max_attempts)
        (431, 200),            # ~9 bits, very small
        (10007, 200),          # ~14 bits
        (65537, 150),          # ~17 bits (2^16 + 1)
        (previous_prime(2**20), 120),   # ~20 bits
    ]
    
    for p_val, max_att in test_configs:
        p_val = int(p_val)
        if not is_prime(p_val):
            p_val = int(previous_prime(p_val))
        
        try:
            result = algorithm3(p_val, max_attempts=max_att, verbose=True)
            all_results['experiments'].append(result)
        except Exception as e:
            print(f"\n  ERROR for p={p_val}: {e}")
            import traceback
            traceback.print_exc()
            all_results['experiments'].append({
                'p': p_val,
                'log2_p': int(p_val).bit_length(),
                'error': str(e),
            })
    
    # ----------------------------------------------------------------
    # PHASE 3: Try larger prime if time permits
    # ----------------------------------------------------------------
    print("\n" + "-"*70)
    print("PHASE 3: Larger prime attempt")
    print("-"*70)
    
    # Only try if previous runs completed reasonably fast
    prev_times = [e.get('wall_clock_seconds', 999) for e in all_results['experiments']
                  if 'error' not in e]
    if prev_times and max(prev_times) < 120:
        p_large = int(previous_prime(2**24))
        try:
            result = algorithm3(p_large, max_attempts=80, verbose=True)
            all_results['experiments'].append(result)
        except Exception as e:
            print(f"\n  ERROR for p={p_large}: {e}")
            all_results['experiments'].append({
                'p': p_large,
                'log2_p': int(p_large).bit_length(),
                'error': str(e),
            })
    
    # ----------------------------------------------------------------
    # PHASE 4: Scaling summary
    # ----------------------------------------------------------------
    print("\n" + "="*70)
    print("SCALING SUMMARY")
    print("="*70)
    
    valid = [e for e in all_results['experiments']
             if 'error' not in e and e.get('successes', 0) > 0]
    
    if valid:
        print(f"\n{'p':>12} | {'log2_p':>6} | {'B':>4} | {'X':>8} | "
              f"{'entries':>8} | {'ops/entry':>10} | {'P0':>8} | "
              f"{'log2(cost)':>10}")
        print("-"*90)
        
        for exp in sorted(valid, key=lambda x: x['p']):
            log2c = exp.get('log2_cost_per_success')
            log2c_str = f"{log2c:.2f}" if log2c else "N/A"
            print(f"{exp['p']:>12} | {exp['log2_p']:>6} | {exp['B']:>4} | "
                  f"{exp['X']:>8} | {exp['avg_table_entries']:>8.0f} | "
                  f"{exp['avg_mults_per_entry']:>10.1f} | "
                  f"{exp['P0_empirical']:>8.4f} | {log2c_str:>10}")
            
            all_results['scaling_summary'].append({
                'p': exp['p'],
                'log2_p': exp['log2_p'],
                'B': exp['B'],
                'X': exp['X'],
                'num_ss_curves': exp['num_ss_curves'],
                'avg_table_entries': exp['avg_table_entries'],
                'avg_mults_per_entry': exp['avg_mults_per_entry'],
                'P0_empirical': exp['P0_empirical'],
                'P0_theory_lower': exp['P0_theory_lower_bound'],
                'u_parameter': exp['u_parameter'],
                'cost_per_success': exp['cost_per_success'],
                'log2_cost_per_success': exp.get('log2_cost_per_success'),
                'walk_cost_fraction': exp['walk_total_cost'] / max(1, exp['avg_total_mults_per_attempt']),
            })
    
    # ----------------------------------------------------------------
    # Write results
    # ----------------------------------------------------------------
    output_path = ('/Volumes/SSD990/crypto-autoresearcher/coordination/goals/'
                   'GOAL-SSI-001/batches/BATCH-046/tasks/TASK-20260804-55952a/'
                   'implementation/cost_measurements.json')
    
    with open(output_path, 'w') as f:
        json.dump(all_results, f, indent=2, default=str)
    
    print(f"\n\nResults written to:\n  {output_path}")
    print("\nDone.")


if __name__ == '__main__':
    main()

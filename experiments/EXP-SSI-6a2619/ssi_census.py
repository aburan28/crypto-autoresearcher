#!/usr/bin/env python3
"""
EXP-SSI-6a2619: Toy-scale census of minimal L-smooth Frobenius-conjugate
isogeny degree over supersingular graphs.

Pure Python + numpy implementation. No SageMath, no sympy used.
Measures distribution of delta_L(E) = minimal L-smooth isogeny degree from E
to E^{(p)} (Frobenius conjugate) over ALL supersingular curves.
"""

import numpy as np
import hashlib
import json
import time
import os
import sys
import math
from collections import defaultdict
import heapq
import traceback
import resource

# ======================================================================
# CONFIGURATION
# ======================================================================
PRIMES = [503, 1019, 2003, 4003]
ELL_SET_L = [2, 3]
MASTER_SEED = 6262019
DOMAIN = "EXP-SSI-6a2619/v1"

# ======================================================================
# MODULAR POLYNOMIALS (exact integer coefficients)
# Phi_ell(X, Y) as dict {(deg_X, deg_Y): coefficient}
# ======================================================================

# Classical modular polynomial Phi_2(X, Y)
PHI2_COEFFS = {
    (3, 0): 1,
    (0, 3): 1,
    (2, 2): -1,
    (2, 1): 1488,
    (1, 2): 1488,
    (2, 0): -162000,
    (0, 2): -162000,
    (1, 1): 40773375,
    (1, 0): 8748000000,
    (0, 1): 8748000000,
    (0, 0): -157464000000000,
}

# Classical modular polynomial Phi_3(X, Y)
PHI3_COEFFS = {
    (4, 0): 1,
    (0, 4): 1,
    (3, 3): -1,
    (3, 2): 2232,
    (2, 3): 2232,
    (3, 1): -1069956,
    (1, 3): -1069956,
    (3, 0): 36864000,
    (0, 3): 36864000,
    (2, 2): 2587918086,
    (2, 1): 8900222976000,
    (1, 2): 8900222976000,
    (2, 0): 452984832000000,
    (0, 2): 452984832000000,
    (1, 1): -770845966336000000,
    (1, 0): 1855425871872000000000,
    (0, 1): 1855425871872000000000,
    (0, 0): 0,
}

PHI_COEFFS = {2: PHI2_COEFFS, 3: PHI3_COEFFS}


def sha256_hex(data):
    """SHA-256 hex digest of bytes."""
    return hashlib.sha256(data).hexdigest()


def log(msg):
    """Print timestamped log message."""
    print(f"[{time.strftime('%H:%M:%S')}] {msg}", flush=True)


# ======================================================================
# F_{p^2} SCALAR ARITHMETIC: elements as (a, b) representing a + b*i
# where i^2 = -1, p = 3 mod 4
# ======================================================================

def fp2_add(x, y, p):
    return ((x[0] + y[0]) % p, (x[1] + y[1]) % p)

def fp2_sub(x, y, p):
    return ((x[0] - y[0]) % p, (x[1] - y[1]) % p)

def fp2_mul(x, y, p):
    a, b = x
    c, d = y
    return ((a * c - b * d) % p, (a * d + b * c) % p)

def fp2_sq(x, p):
    a, b = x
    return ((a * a - b * b) % p, (2 * a * b) % p)

def fp2_pow(x, n, p):
    """x^n in F_{p^2} via square-and-multiply."""
    if n == 0:
        return (1, 0)
    result = (1, 0)
    base = x
    while n > 0:
        if n & 1:
            result = fp2_mul(result, base, p)
        base = fp2_sq(base, p)
        n >>= 1
    return result

def fp2_inv(x, p):
    """Inverse of x in F_{p^2}. Returns None if x = 0."""
    a, b = x
    norm = (a * a + b * b) % p
    if norm == 0:
        return None
    norm_inv = pow(norm, p - 2, p)
    return ((a * norm_inv) % p, ((-b) * norm_inv) % p)

def fp2_neg(x, p):
    return ((-x[0]) % p, (-x[1]) % p)

def fp2_from_int(n, p):
    return (n % p, 0)

def fp2_eq(x, y):
    return x[0] == y[0] and x[1] == y[1]

def fp2_is_zero(x):
    return x[0] == 0 and x[1] == 0


# ======================================================================
# POLYNOMIAL ARITHMETIC OVER F_{p^2}
# Polynomials as lists: poly[i] = coefficient of X^i
# ======================================================================

def poly_degree(f):
    """Degree of polynomial f. Returns -1 for zero polynomial."""
    i = len(f) - 1
    while i >= 0 and fp2_is_zero(f[i]):
        i -= 1
    return i

def poly_strip(f):
    """Remove leading zeros."""
    d = poly_degree(f)
    if d < 0:
        return [(0, 0)]
    return f[:d + 1]

def poly_mul_mod(f, g, m, p):
    """Multiply f * g mod m over F_{p^2}."""
    # First multiply
    df = poly_degree(f)
    dg = poly_degree(g)
    if df < 0 or dg < 0:
        return [(0, 0)]
    prod = [(0, 0)] * (df + dg + 1)
    for i in range(df + 1):
        if fp2_is_zero(f[i]):
            continue
        for j in range(dg + 1):
            if fp2_is_zero(g[j]):
                continue
            prod[i + j] = fp2_add(prod[i + j], fp2_mul(f[i], g[j], p), p)
    # Then reduce mod m
    return poly_mod(prod, m, p)

def poly_mod(f, m, p):
    """f mod m over F_{p^2}."""
    f = list(f)
    df = poly_degree(f)
    dm = poly_degree(m)
    if dm < 0:
        raise ValueError("Division by zero polynomial")
    if df < dm:
        return poly_strip(f)
    lc_inv = fp2_inv(m[dm], p)
    while df >= dm:
        if not fp2_is_zero(f[df]):
            coeff = fp2_mul(f[df], lc_inv, p)
            for i in range(dm + 1):
                shift = df - dm
                f[shift + i] = fp2_sub(f[shift + i], fp2_mul(coeff, m[i], p), p)
        df -= 1
    return poly_strip(f[:dm])

def poly_gcd(f, g, p):
    """GCD of f and g over F_{p^2}."""
    f = poly_strip(list(f))
    g = poly_strip(list(g))
    while poly_degree(g) >= 0:
        f, g = g, poly_mod(f, g, p)
    # Make monic
    d = poly_degree(f)
    if d >= 0 and not fp2_is_zero(f[d]):
        lc_inv = fp2_inv(f[d], p)
        f = [fp2_mul(c, lc_inv, p) for c in f]
    return poly_strip(f)

def poly_powmod(base, exp, mod, p):
    """base^exp mod mod over F_{p^2} using square-and-multiply."""
    result = [(0, 0)] * poly_degree(mod)
    if len(result) == 0:
        result = [(0, 0)]
    result[0] = (1, 0)  # result = 1
    base = poly_mod(base, mod, p)
    while exp > 0:
        if exp & 1:
            result = poly_mul_mod(result, base, mod, p)
        base = poly_mul_mod(base, base, mod, p)
        exp >>= 1
    return poly_strip(result)


def find_roots_fp2(coeffs_list, p):
    """
    Find all roots of a polynomial in F_{p^2}.
    coeffs_list: list where coeffs_list[i] is the F_{p^2} coefficient of X^i.
    Returns list of roots (a, b) in F_{p^2}.
    """
    f = poly_strip(list(coeffs_list))
    d = poly_degree(f)
    if d <= 0:
        return []

    roots = []
    # Factor out linear factors one by one
    rng_state = [0]  # mutable counter for deterministic "randomness"

    def split_poly(f):
        d = poly_degree(f)
        if d == 0:
            return []
        if d == 1:
            # f = a1*X + a0, root = -a0/a1
            a0, a1 = f[0], f[1]
            a1_inv = fp2_inv(a1, p)
            root = fp2_mul(fp2_neg(a0, p), a1_inv, p)
            return [root]

        # Try to split using Cantor-Zassenhaus
        # GCD(f, X^{p^2} - X) = f (since f splits over F_{p^2})
        # Split by computing GCD(f, (X + t)^{(p^2-1)/2} - 1) for random t
        exp = (p * p - 1) // 2
        for attempt in range(200):
            # Generate a "random" element of F_{p^2}
            rng_state[0] += 1
            t_r = (rng_state[0] * 7 + 13) % p
            t_i = (rng_state[0] * 11 + 29) % p
            t = (t_r, t_i)

            # Compute (X + t)^{exp} mod f
            x_plus_t = [t, (1, 0)]  # X + t
            powered = poly_powmod(x_plus_t, exp, f, p)

            # Subtract 1
            powered[0] = fp2_sub(powered[0], (1, 0), p)
            powered = poly_strip(powered)

            g = poly_gcd(f, powered, p)
            dg = poly_degree(g)
            if 0 < dg < d:
                # Found a proper factor
                left_roots = split_poly(g)
                # Divide f by g
                quotient = poly_exact_div(f, g, p)
                right_roots = split_poly(quotient)
                return left_roots + right_roots

        # Fallback: brute force for very small degree
        # This shouldn't happen but is a safety net
        found = []
        # Try to find at least one root by evaluating at elements
        for a in range(min(p, 50)):
            for b in range(min(p, 50)):
                val = poly_eval(f, (a, b), p)
                if fp2_is_zero(val):
                    found.append((a, b))
                    if len(found) == d:
                        return found
        return found

    return split_poly(f)


def poly_exact_div(f, g, p):
    """Exact polynomial division f / g over F_{p^2}."""
    f = list(f)
    df = poly_degree(f)
    dg = poly_degree(g)
    if dg < 0:
        raise ValueError("Division by zero")
    if df < dg:
        return [(0, 0)]
    lc_inv = fp2_inv(g[dg], p)
    quotient = [(0, 0)] * (df - dg + 1)
    for i in range(df, dg - 1, -1):
        if fp2_is_zero(f[i]):
            continue
        coeff = fp2_mul(f[i], lc_inv, p)
        quotient[i - dg] = coeff
        for j in range(dg + 1):
            f[i - dg + j] = fp2_sub(f[i - dg + j], fp2_mul(coeff, g[j], p), p)
    return poly_strip(quotient)


def poly_eval(f, x, p):
    """Evaluate polynomial f at x in F_{p^2} using Horner."""
    d = poly_degree(f)
    if d < 0:
        return (0, 0)
    result = f[d]
    for i in range(d - 1, -1, -1):
        result = fp2_add(fp2_mul(result, x, p), f[i], p)
    return result


# ======================================================================
# MODULAR POLYNOMIAL EVALUATION
# ======================================================================

def eval_phi_ell(ell, j1, j2, p):
    """Evaluate Phi_ell(j1, j2) in F_{p^2}. Returns True if zero."""
    coeffs = PHI_COEFFS[ell]
    result = (0, 0)
    # Precompute powers of j1 and j2
    max_i = max(k[0] for k in coeffs.keys())
    max_j = max(k[1] for k in coeffs.keys())
    pow_j1 = [(1, 0)]
    pow_j2 = [(1, 0)]
    for _ in range(max_i):
        pow_j1.append(fp2_mul(pow_j1[-1], j1, p))
    for _ in range(max_j):
        pow_j2.append(fp2_mul(pow_j2[-1], j2, p))

    for (di, dj), c in coeffs.items():
        c_mod = c % p
        if c_mod == 0:
            continue
        term = fp2_mul(pow_j1[di], pow_j2[dj], p)
        term = fp2_mul(term, (c_mod, 0), p)
        result = fp2_add(result, term, p)
    return fp2_is_zero(result)


def phi2_as_poly_in_x(j0, p):
    """
    Given j0 in F_{p^2}, return Phi_2(X, j0) as polynomial in X
    (list of coefficients, ascending degree).
    """
    # Phi_2(X, Y) = X^3 + (-Y^2 + 1488Y - 162000)X^2
    #             + (1488Y^2 + 40773375Y + 8748000000)X
    #             + (Y^3 - 162000Y^2 + 8748000000Y - 157464000000000)
    j0_sq = fp2_sq(j0, p)
    j0_cu = fp2_mul(j0_sq, j0, p)

    # Coefficient of X^3
    c3 = (1, 0)

    # Coefficient of X^2: -j0^2 + 1488*j0 - 162000
    c2 = fp2_neg(j0_sq, p)
    c2 = fp2_add(c2, fp2_mul(fp2_from_int(1488, p), j0, p), p)
    c2 = fp2_add(c2, fp2_from_int(-162000, p), p)

    # Coefficient of X: 1488*j0^2 + 40773375*j0 + 8748000000
    c1 = fp2_mul(fp2_from_int(1488, p), j0_sq, p)
    c1 = fp2_add(c1, fp2_mul(fp2_from_int(40773375, p), j0, p), p)
    c1 = fp2_add(c1, fp2_from_int(8748000000, p), p)

    # Constant: j0^3 - 162000*j0^2 + 8748000000*j0 - 157464000000000
    c0 = j0_cu
    c0 = fp2_add(c0, fp2_mul(fp2_from_int(-162000, p), j0_sq, p), p)
    c0 = fp2_add(c0, fp2_mul(fp2_from_int(8748000000, p), j0, p), p)
    c0 = fp2_add(c0, fp2_from_int(-157464000000000, p), p)

    return [c0, c1, c2, c3]


# ======================================================================
# CONSTRUCTION A: Deuring-Hasse roots
# Vectorized over all lambda in F_{p^2}
# ======================================================================

def construction_a(p):
    """
    Construct supersingular j-invariants via the Hasse polynomial.
    Returns sorted list of (a, b) pairs (j = a + b*i in F_{p^2}).
    """
    log(f"  Construction A: p={p}, computing Hasse polynomial coefficients...")
    t0 = time.time()

    m = (p - 1) // 2  # degree of Hasse polynomial

    # Compute coefficients c_i = binom(m, i)^2 mod p
    # Use iterative computation of binom(m, i) mod p
    coeffs = np.zeros(m + 1, dtype=np.int64)
    binom_val = 1  # binom(m, 0) = 1
    for i in range(m + 1):
        coeffs[i] = (binom_val * binom_val) % p
        if i < m:
            binom_val = binom_val * (m - i) % p
            binom_val = binom_val * pow(i + 1, p - 2, p) % p

    log(f"  Coefficients computed in {time.time()-t0:.2f}s, evaluating at all {p*p} elements...")
    t1 = time.time()

    # Create all elements of F_{p^2} as two arrays (real, imag)
    # Element (a, b) represents a + b*i
    # Arrange as all combinations: a in [0,p-1], b in [0,p-1]
    real_parts = np.repeat(np.arange(p, dtype=np.int64), p)
    imag_parts = np.tile(np.arange(p, dtype=np.int64), p)

    # Vectorized Horner evaluation of H(lambda) over F_{p^2}
    # H = c[m], then for i from m-1 down to 0: H = H * lambda + c[i]
    # In F_{p^2}: (h_r + h_i*i) * (l_r + l_i*i) = (h_r*l_r - h_i*l_i) + (h_r*l_i + h_i*l_r)*i
    h_real = np.full(p * p, int(coeffs[m]), dtype=np.int64)
    h_imag = np.zeros(p * p, dtype=np.int64)

    for idx in range(m - 1, -1, -1):
        # Multiply by lambda
        new_real = (h_real * real_parts - h_imag * imag_parts) % p
        new_imag = (h_real * imag_parts + h_imag * real_parts) % p
        # Add coefficient (real only since coeffs are in F_p)
        new_real = (new_real + int(coeffs[idx])) % p
        h_real = new_real
        h_imag = new_imag

        if idx % 500 == 0 and idx > 0:
            elapsed = time.time() - t1
            progress = (m - idx) / m
            log(f"    Horner step {m-idx}/{m} ({progress*100:.0f}%), elapsed {elapsed:.1f}s")

    elapsed_eval = time.time() - t1
    log(f"  Horner evaluation done in {elapsed_eval:.1f}s")

    # Find roots: where both h_real == 0 and h_imag == 0
    root_mask = (h_real == 0) & (h_imag == 0)
    root_indices = np.where(root_mask)[0]
    root_reals = real_parts[root_indices]
    root_imags = imag_parts[root_indices]

    log(f"  Found {len(root_indices)} roots of Hasse polynomial")

    # Convert lambda roots to j-invariants
    # j(lambda) = 256 * (lambda^2 - lambda + 1)^3 / (lambda^2 * (lambda - 1)^2)
    j_invariants = set()
    zero_norm_count = 0

    for idx in range(len(root_indices)):
        lam = (int(root_reals[idx]), int(root_imags[idx]))

        # Compute denominator: lambda^2 * (lambda - 1)^2
        lam_sq = fp2_sq(lam, p)
        lam_minus_1 = fp2_sub(lam, (1, 0), p)
        lam_minus_1_sq = fp2_sq(lam_minus_1, p)
        denom = fp2_mul(lam_sq, lam_minus_1_sq, p)

        # Check for zero denominator
        if fp2_is_zero(denom):
            zero_norm_count += 1
            continue

        # Compute numerator: 256 * (lambda^2 - lambda + 1)^3
        lam_sq_minus_lam_plus_1 = fp2_add(fp2_sub(lam_sq, lam, p), (1, 0), p)
        numer_base = lam_sq_minus_lam_plus_1
        numer_cu = fp2_mul(fp2_mul(numer_base, numer_base, p), numer_base, p)
        numer = fp2_mul((256 % p, 0), numer_cu, p)

        # j = numer / denom
        denom_inv = fp2_inv(denom, p)
        if denom_inv is None:
            zero_norm_count += 1
            continue

        j = fp2_mul(numer, denom_inv, p)
        j_invariants.add(j)

    if zero_norm_count > 0:
        log(f"  WARNING: {zero_norm_count} roots had zero norm denominator (excluded)")

    j_list = sorted(j_invariants)
    log(f"  Construction A: {len(j_list)} distinct j-invariants found (time: {time.time()-t0:.1f}s)")
    return j_list


# ======================================================================
# CONSTRUCTION B: BFS from j=1728 using Phi_2 root-finding
# ======================================================================

def construction_b(p, budget_seconds=600):
    """
    BFS from j=1728 over the 2-isogeny graph.
    Returns sorted list of (a, b) pairs, or None if budget exceeded.
    """
    log(f"  Construction B: BFS from j=1728, p={p}")
    t0 = time.time()

    j_1728 = (1728 % p, 0)
    visited = {j_1728}
    frontier = [j_1728]

    while frontier:
        if time.time() - t0 > budget_seconds:
            log(f"  Construction B: BUDGET EXCEEDED at {len(visited)} vertices")
            return None

        new_frontier = []
        for j0 in frontier:
            # Find roots of Phi_2(X, j0)
            poly = phi2_as_poly_in_x(j0, p)
            roots = find_roots_fp2(poly, p)
            for r in roots:
                if r not in visited:
                    visited.add(r)
                    new_frontier.append(r)
        frontier = new_frontier

    j_list = sorted(visited)
    log(f"  Construction B: {len(j_list)} vertices found in {time.time()-t0:.1f}s")
    return j_list


# ======================================================================
# GRAPH CONSTRUCTION via pairwise Phi_ell evaluation
# ======================================================================

def build_isogeny_graph(j_list, ell_set, p):
    """
    Build the L-smooth isogeny graph.
    Returns adjacency dict: adj[i] = list of (j_idx, ell) for neighbors.
    """
    log(f"  Building isogeny graph for ell_set={ell_set}, |S|={len(j_list)}...")
    t0 = time.time()
    n = len(j_list)
    j_to_idx = {j: i for i, j in enumerate(j_list)}

    # For each ell, find edges by pairwise evaluation
    adj = defaultdict(list)  # adj[i] = [(j_idx, ell), ...]

    for ell in ell_set:
        coeffs = PHI_COEFFS[ell]
        edge_count = 0
        # Reduce coefficients mod p
        coeffs_mod = {k: v % p for k, v in coeffs.items()}

        for i in range(n):
            j1 = j_list[i]
            # Precompute powers of j1
            max_di = max(k[0] for k in coeffs_mod.keys())
            pow_j1 = [(1, 0)]
            for _ in range(max_di):
                pow_j1.append(fp2_mul(pow_j1[-1], j1, p))

            for j_idx in range(n):
                j2 = j_list[j_idx]
                # Evaluate Phi_ell(j1, j2)
                max_dj = max(k[1] for k in coeffs_mod.keys())
                pow_j2 = [(1, 0)]
                for _ in range(max_dj):
                    pow_j2.append(fp2_mul(pow_j2[-1], j2, p))

                result = (0, 0)
                for (di, dj), c in coeffs_mod.items():
                    if c == 0:
                        continue
                    term = fp2_mul(pow_j1[di], pow_j2[dj], p)
                    term = fp2_mul(term, (c, 0), p)
                    result = fp2_add(result, term, p)

                if fp2_is_zero(result):
                    adj[i].append((j_idx, ell))
                    edge_count += 1

        log(f"    ell={ell}: {edge_count} directed edges ({edge_count/n:.1f} per vertex)")

    elapsed = time.time() - t0
    log(f"  Graph built in {elapsed:.1f}s")
    return adj


# ======================================================================
# DIJKSTRA: minimal L-smooth degree from source to target
# ======================================================================

def dijkstra_all_targets(adj, source, n):
    """
    Dijkstra from source. Edge weights are the ell values (multiplicative -> use log for priority).
    Returns dict: target_idx -> (exact_degree_int, path_ells)
    where exact_degree_int is the product of ell values along the shortest path.
    """
    # Priority queue: (log_degree, degree_int, vertex, path_ells)
    INF = float('inf')
    best_degree = [None] * n
    best_log = [INF] * n
    best_path = [None] * n

    best_log[source] = 0.0
    best_degree[source] = 1
    best_path[source] = []

    # heap entries: (log_degree, degree, vertex)
    heap = [(0.0, 1, source, [])]

    while heap:
        log_d, degree, u, path = heapq.heappop(heap)
        if log_d > best_log[u]:
            continue

        for (v, ell) in adj[u]:
            new_log = log_d + math.log(ell)
            new_degree = degree * ell
            if new_log < best_log[v]:
                best_log[v] = new_log
                best_degree[v] = new_degree
                best_path[v] = path + [ell]
                heapq.heappush(heap, (new_log, new_degree, v, best_path[v]))

    return best_degree, best_path


def compute_all_delta_L(adj, n):
    """Compute shortest-path degrees from every source to every target."""
    log(f"  Computing all-pairs shortest L-smooth degrees (n={n})...")
    t0 = time.time()
    # all_degrees[i][j] = minimal L-smooth degree from i to j
    all_degrees = []
    for i in range(n):
        degrees, _ = dijkstra_all_targets(adj, i, n)
        all_degrees.append(degrees)
    log(f"  All-pairs done in {time.time()-t0:.1f}s")
    return all_degrees


# ======================================================================
# DISTRIBUTION MEASUREMENT
# ======================================================================

def compute_L_smooth_integers(L, bound):
    """Generate all L-smooth integers up to bound, sorted."""
    smooths = set()
    smooths.add(1)
    queue = [1]
    while queue:
        x = queue.pop(0)
        for ell in L:
            y = x * ell
            if y <= bound and y not in smooths:
                smooths.add(y)
                queue.append(y)
    return sorted(smooths)


def compute_D_window(p):
    """Compute D_max = floor((p/2)^(1/3))."""
    return int(math.floor((p / 2) ** (1.0 / 3.0)))


def measure_cdf(delta_values, D_grid, S_size):
    """
    Compute F_L(D) = #{E : delta_L(E) <= D} for each D in D_grid.
    delta_values: list of exact integer degrees.
    """
    cdf = {}
    for D in D_grid:
        count = sum(1 for d in delta_values if d is not None and d <= D)
        cdf[D] = count
    return cdf


# ======================================================================
# NULL ARM: SHA-256 based random target selection
# ======================================================================

def draw_null_targets(p, S_size, seed_label="null-target"):
    """
    Draw random targets for each curve using SHA-256 rejection sampling.
    Returns list of target indices.
    """
    targets = []
    threshold = (2**256 // S_size) * S_size  # rejection threshold

    for i in range(S_size):
        sub_counter = 0
        while True:
            data = f"{DOMAIN}|{seed_label}|{p}|{i}|{sub_counter}".encode('ascii')
            digest = hashlib.sha256(data).digest()
            value = int.from_bytes(digest, 'big')
            if value < threshold:
                targets.append(value % S_size)
                break
            sub_counter += 1
    return targets


# ======================================================================
# CLASS NUMBER COMPUTATION (counting reduced forms)
# ======================================================================

def class_number(D):
    """
    Compute h(D) for fundamental discriminant D < 0 by counting
    reduced binary quadratic forms ax^2 + bxy + cy^2 with b^2 - 4ac = D.
    """
    assert D < 0
    count = 0
    # Reduced forms: |b| <= a <= c, and if |b| = a or a = c then b >= 0
    # b^2 - 4ac = D => 4ac = b^2 - D
    # a >= 1, |b| <= a, c = (b^2 - D) / (4a)
    abs_D = -D
    # b^2 = D + 4ac => b^2 = -|D| + 4ac => b^2 + |D| = 4ac
    # So b^2 + |D| must be divisible by 4a and c = (b^2 + |D|) / (4a)
    # Constraint: a <= c => a <= (b^2 + |D|)/(4a) => 4a^2 <= b^2 + |D|
    # => a <= sqrt((b^2 + |D|)/4)
    # Also |b| <= a
    # Iterate over b from 0 upward, and for each b find valid a
    # Actually iterate differently: for each a, find valid b

    max_a = int(math.isqrt(abs_D // 3)) + 1  # 4a^2 <= |D| + a^2 => 3a^2 <= |D|

    for a in range(1, max_a + 1):
        for b in range(-a, a + 1):
            rem = b * b + abs_D
            if rem % (4 * a) != 0:
                continue
            c = rem // (4 * a)
            if c < a:
                continue
            # Reduced form conditions
            if abs(b) > a:
                continue
            if abs(b) == a and b < 0:
                continue
            if a == c and b < 0:
                continue
            count += 1
    return count


# ======================================================================
# OLS FITTING
# ======================================================================

def ols_slope(x, y):
    """
    OLS slope of y on x (both 1D arrays).
    Returns (slope, intercept, R^2, residuals).
    """
    x = np.array(x, dtype=np.float64)
    y = np.array(y, dtype=np.float64)
    n = len(x)
    if n < 2:
        return None, None, None, None
    x_mean = np.mean(x)
    y_mean = np.mean(y)
    ss_xx = np.sum((x - x_mean) ** 2)
    ss_xy = np.sum((x - x_mean) * (y - y_mean))
    if ss_xx == 0:
        return None, None, None, None
    slope = ss_xy / ss_xx
    intercept = y_mean - slope * x_mean
    y_pred = slope * x + intercept
    residuals = y - y_pred
    ss_res = np.sum(residuals ** 2)
    ss_tot = np.sum((y - y_mean) ** 2)
    r_squared = 1.0 - ss_res / ss_tot if ss_tot > 0 else 0.0
    return float(slope), float(intercept), float(r_squared), residuals.tolist()


# ======================================================================
# HASH COMMITMENT
# ======================================================================

def hash_commit(data_dict):
    """SHA-256 hash commitment of a JSON-serializable dict."""
    canonical = json.dumps(data_dict, sort_keys=True, separators=(',', ':'))
    return sha256_hex(canonical.encode('utf-8'))


# ======================================================================
# CANONICAL SET HASH (as per spec)
# ======================================================================

def canonical_set_hash(j_list, p):
    """
    SHA-256 over canonical sorted decimal "a,b\n" encoding of each j = a + b*i.
    """
    lines = []
    for (a, b) in sorted(j_list):
        lines.append(f"{a},{b}\n")
    data = "".join(lines).encode('ascii')
    return sha256_hex(data)


# ======================================================================
# MAIN EXECUTION
# ======================================================================

def run_experiment():
    """Main experiment execution."""
    results = {
        "experiment_id": "EXP-SSI-6a2619",
        "run_id": "RUN-SSI-6a2619-001",
        "started_at": time.strftime("%Y-%m-%dT%H:%M:%S%z"),
        "master_seed": MASTER_SEED,
        "domain": DOMAIN,
        "primes": PRIMES,
        "ell_set_L": ELL_SET_L,
    }

    all_cell_results = {}
    controls = {
        "positive_control_rate": {},
        "envelope_violations": {},
        "construction_agreement": {},
        "sanity_invariants": {},
        "graded_control": {},
    }

    null_arm_committed = False
    null_commitment_hash = None
    null_commitment_timestamp = None
    null_results_all = {}

    # ================================================================
    # PHASE 1: For each prime, construct vertex set and graph
    # ================================================================
    for p in PRIMES:
        log(f"\n{'='*60}")
        log(f"PRIME p = {p}")
        log(f"{'='*60}")

        cell_t0 = time.time()

        # Verify prime conditions
        assert p > 2 and all(p % d != 0 for d in range(2, int(p**0.5)+1)), f"{p} not prime"
        assert p % 4 == 3, f"{p} not 3 mod 4"

        # Construction A
        j_list_a = construction_a(p)
        hash_a = canonical_set_hash(j_list_a, p)
        log(f"  Construction A hash: {hash_a[:16]}...")

        # Construction B (with budget)
        j_list_b = construction_b(p, budget_seconds=300)
        if j_list_b is not None:
            hash_b = canonical_set_hash(j_list_b, p)
            log(f"  Construction B hash: {hash_b[:16]}...")
            agreement = (set(map(tuple, j_list_a)) == set(map(tuple, j_list_b)))
            if not agreement:
                log(f"  FATAL: Construction A and B DISAGREE at p={p}")
                results["status"] = "invalid_measurement"
                results["reason"] = f"Construction disagreement at p={p}"
                return results
            controls["construction_agreement"][str(p)] = {
                "status": "AGREE",
                "hash_a": hash_a,
                "hash_b": hash_b,
            }
        else:
            controls["construction_agreement"][str(p)] = {
                "status": "NOT_PERFORMED",
                "reason": "Construction B budget exceeded",
                "hash_a": hash_a,
            }

        j_list = j_list_a
        S_size = len(j_list)
        j_to_idx = {j: i for i, j in enumerate(j_list)}

        # Sanity invariants
        expected_size = p // 12 + 1
        size_check = abs(S_size - expected_size) <= 2
        log(f"  |S| = {S_size}, floor(p/12)+1 = {expected_size}, within 2: {size_check}")

        # Frobenius closure: conjugate of (a, b) is (a, (-b) % p)
        conjugate_closed = all(
            (a, (-b) % p) in j_to_idx for (a, b) in j_list
        )
        log(f"  Frobenius closure: {conjugate_closed}")

        # F_p-rational j-invariants (b = 0)
        fp_rational = [(a, b) for (a, b) in j_list if b == 0]
        fp_rational_count = len(fp_rational)
        log(f"  F_p-rational j-invariants: {fp_rational_count}")

        # Check that F_p-rational are their own conjugate
        fp_self_conjugate = all(
            (a, (-b) % p) == (a, b) for (a, b) in fp_rational
        )
        log(f"  F_p-rational self-conjugate: {fp_self_conjugate}")

        # Build isogeny graph
        adj = build_isogeny_graph(j_list, ELL_SET_L, p)

        # Check connectivity of ell=2 graph
        # BFS from vertex 0 using only ell=2 edges
        visited_bfs = set()
        queue = [0]
        visited_bfs.add(0)
        while queue:
            u = queue.pop(0)
            for (v, ell) in adj[u]:
                if ell == 2 and v not in visited_bfs:
                    visited_bfs.add(v)
                    queue.append(v)
        ell2_connected = (len(visited_bfs) == S_size)
        log(f"  ell=2 graph connected: {ell2_connected}")

        # Check neighbour counts per vertex
        for ell in ELL_SET_L:
            neighbor_counts = defaultdict(int)
            for i in range(S_size):
                nc = len([1 for (v, e) in adj[i] if e == ell])
                neighbor_counts[nc] += 1
            min_nc = min(neighbor_counts.keys()) if neighbor_counts else 0
            max_nc = max(neighbor_counts.keys()) if neighbor_counts else 0
            log(f"  ell={ell} neighbor count range: [{min_nc}, {max_nc}] (expected [1, {ell+1}])")
            if max_nc > ell + 1:
                log(f"  WARNING: ell={ell} has vertices with >{ell+1} neighbors!")

        controls["sanity_invariants"][str(p)] = {
            "size_check": size_check,
            "S_size": S_size,
            "expected_floor_p12_plus1": expected_size,
            "conjugate_closed": conjugate_closed,
            "ell2_connected": ell2_connected,
            "fp_self_conjugate": fp_self_conjugate,
        }

        # Compute all-pairs shortest L-smooth degrees
        all_degrees = compute_all_delta_L(adj, S_size)

        # D window and grid
        D_max = compute_D_window(p)
        D_grid = compute_L_smooth_integers(ELL_SET_L, D_max)
        log(f"  D_max = {D_max}, D_grid = {D_grid}")

        # ============================================================
        # NULL ARM (must be computed and committed BEFORE treatment)
        # ============================================================
        log(f"  --- NULL ARM ---")
        null_targets = draw_null_targets(p, S_size, "null-target")
        null_deltas = []
        for i in range(S_size):
            target_idx = null_targets[i]
            delta = all_degrees[i][target_idx]
            null_deltas.append(delta)

        null_cdf = measure_cdf(null_deltas, D_grid, S_size)

        # Fit null arm: beta_hat_null
        log_D_vals = [math.log(D) for D in D_grid if null_cdf[D] > 0]
        log_F_vals = [math.log(null_cdf[D] / S_size) for D in D_grid if null_cdf[D] > 0]
        beta_null, intercept_null, r2_null, resid_null = ols_slope(log_D_vals, log_F_vals)

        null_results_all[str(p)] = {
            "S_size": S_size,
            "D_grid": D_grid,
            "null_targets": null_targets,
            "null_deltas": null_deltas,
            "null_cdf": {str(k): v for k, v in null_cdf.items()},
            "beta_hat_null": beta_null,
            "intercept_null": intercept_null,
            "r2_null": r2_null,
            "residuals_null": resid_null,
        }
        log(f"  Null arm: beta_hat_null={beta_null}, R^2={r2_null}")

        # Store cell data for treatment phase
        all_cell_results[str(p)] = {
            "j_list": j_list,
            "adj": adj,
            "S_size": S_size,
            "D_max": D_max,
            "D_grid": D_grid,
            "all_degrees": all_degrees,
            "j_to_idx": j_to_idx,
            "fp_rational_count": fp_rational_count,
            "hash_a": hash_a,
            "cell_time_construction": time.time() - cell_t0,
        }

    # ================================================================
    # COMMIT NULL ARM BEFORE ANY TREATMENT
    # ================================================================
    null_commitment_hash = hash_commit(null_results_all)
    null_commitment_timestamp = time.strftime("%Y-%m-%dT%H:%M:%S%z")
    null_arm_committed = True
    log(f"\n{'='*60}")
    log(f"NULL ARM COMMITTED")
    log(f"  Hash: {null_commitment_hash}")
    log(f"  Timestamp: {null_commitment_timestamp}")
    log(f"{'='*60}\n")

    # ================================================================
    # NULL ARM REPLICATION (3 additional seeds)
    # ================================================================
    log("NULL ARM REPLICATION (3 additional seeds)...")
    null_replication = {}
    for rep_idx in range(1, 4):
        seed_label = f"null-target-r{rep_idx}"
        rep_betas = {}
        for p in PRIMES:
            cell = all_cell_results[str(p)]
            S_size = cell["S_size"]
            D_grid = cell["D_grid"]
            all_degrees = cell["all_degrees"]

            rep_targets = draw_null_targets(p, S_size, seed_label)
            rep_deltas = [all_degrees[i][rep_targets[i]] for i in range(S_size)]
            rep_cdf = measure_cdf(rep_deltas, D_grid, S_size)

            log_D_vals = [math.log(D) for D in D_grid if rep_cdf[D] > 0]
            log_F_vals = [math.log(rep_cdf[D] / S_size) for D in D_grid if rep_cdf[D] > 0]
            beta_rep, _, r2_rep, _ = ols_slope(log_D_vals, log_F_vals)
            rep_betas[str(p)] = {"beta_hat_null": beta_rep, "r2": r2_rep}

        null_replication[seed_label] = rep_betas
        log(f"  {seed_label}: betas = {[rep_betas[str(pp)]['beta_hat_null'] for pp in PRIMES]}")

    # ================================================================
    # PHASE 2: TREATMENT ARM (Frobenius conjugate target)
    # ================================================================
    log(f"\n{'='*60}")
    log(f"TREATMENT ARM")
    log(f"{'='*60}")

    treatment_results = {}
    for p in PRIMES:
        log(f"\n  --- p = {p} ---")
        cell = all_cell_results[str(p)]
        j_list = cell["j_list"]
        S_size = cell["S_size"]
        D_grid = cell["D_grid"]
        all_degrees = cell["all_degrees"]
        j_to_idx = cell["j_to_idx"]

        # Treatment: target = Frobenius conjugate = (a, -b mod p)
        treatment_deltas = []
        for i, (a, b) in enumerate(j_list):
            conjugate = (a, (-b) % p)
            target_idx = j_to_idx[conjugate]
            delta = all_degrees[i][target_idx]
            treatment_deltas.append(delta)

        treatment_cdf = measure_cdf(treatment_deltas, D_grid, S_size)

        # Fit treatment arm: beta_hat
        log_D_vals = [math.log(D) for D in D_grid if treatment_cdf[D] > 0]
        log_F_vals = [math.log(treatment_cdf[D] / S_size) for D in D_grid if treatment_cdf[D] > 0]
        beta_hat, intercept_hat, r2_hat, resid_hat = ols_slope(log_D_vals, log_F_vals)

        log(f"  Treatment: beta_hat={beta_hat}, R^2={r2_hat}")
        log(f"  CDF: {dict(treatment_cdf)}")

        # Positive control: all F_p-rational j (b=0) must have delta = 1
        pos_ctrl_pass = all(
            treatment_deltas[j_to_idx[(a, 0)]] == 1
            for (a, b) in j_list if b == 0
        )
        pos_ctrl_count = sum(1 for (a, b) in j_list if b == 0)
        pos_ctrl_delta1 = sum(1 for (a, b) in j_list if b == 0 and treatment_deltas[j_to_idx[(a, 0)]] == 1)
        controls["positive_control_rate"][str(p)] = {
            "rate": pos_ctrl_delta1 / pos_ctrl_count if pos_ctrl_count > 0 else None,
            "pass": pos_ctrl_pass,
            "count_fp_rational": pos_ctrl_count,
            "count_delta1": pos_ctrl_delta1,
        }
        log(f"  Positive control: {pos_ctrl_delta1}/{pos_ctrl_count} = {'PASS' if pos_ctrl_pass else 'FAIL'}")

        if not pos_ctrl_pass:
            log(f"  FATAL: Positive control FAILED at p={p}. Halting.")
            results["status"] = "invalid_measurement"
            results["reason"] = f"Positive control failed at p={p}"
            return results

        # Envelope control: delta_L(E) <= 4^{k(E)} where k(E) = ell=2 distance to nearest F_p vertex
        # Compute k(E) for each vertex: BFS distance to F_p-rational set in ell=2 graph
        fp_indices = [j_to_idx[(a, b)] for (a, b) in j_list if b == 0]
        adj_ell2 = defaultdict(list)
        for i in range(S_size):
            for (v, ell) in cell["adj"][i]:
                if ell == 2:
                    adj_ell2[i].append(v)

        # BFS from all F_p-rational vertices simultaneously
        k_values = [None] * S_size
        bfs_queue = list(fp_indices)
        for idx in fp_indices:
            k_values[idx] = 0
        qi = 0
        while qi < len(bfs_queue):
            u = bfs_queue[qi]
            qi += 1
            for v in adj_ell2[u]:
                if k_values[v] is None:
                    k_values[v] = k_values[u] + 1
                    bfs_queue.append(v)

        # Check envelope: delta_L(E) <= 4^{k(E)}
        envelope_violations = []
        for i in range(S_size):
            if k_values[i] is not None:
                envelope = 4 ** k_values[i]
                if treatment_deltas[i] > envelope:
                    envelope_violations.append({
                        "vertex_idx": i,
                        "j": j_list[i],
                        "delta_L": treatment_deltas[i],
                        "k": k_values[i],
                        "envelope_4k": envelope,
                    })

        controls["envelope_violations"][str(p)] = {
            "count": len(envelope_violations),
            "violations": envelope_violations,
        }
        log(f"  Envelope violations: {len(envelope_violations)}")

        if len(envelope_violations) > 0:
            log(f"  FATAL: Envelope violation at p={p}. Halting.")
            results["status"] = "invalid_measurement"
            results["reason"] = f"Envelope violation at p={p}"
            return results

        # Graded control: bucket by k(E)
        k_buckets = defaultdict(list)
        for i in range(S_size):
            if k_values[i] is not None:
                k_buckets[k_values[i]].append(treatment_deltas[i])

        graded_table = {}
        for k in sorted(k_buckets.keys()):
            deltas_in_bucket = k_buckets[k]
            graded_table[k] = {
                "bucket_size": len(deltas_in_bucket),
                "median_delta_L": int(np.median(deltas_in_bucket)),
                "max_delta_L": max(deltas_in_bucket),
                "envelope_4k": 4 ** k,
            }

        # Check monotone medians
        k_sorted = sorted(graded_table.keys())
        medians = [graded_table[k]["median_delta_L"] for k in k_sorted]
        monotone = all(medians[i] <= medians[i+1] for i in range(len(medians)-1))
        interior_buckets = len([k for k in k_sorted if k > 0 and k < max(k_sorted)])

        controls["graded_control"][str(p)] = {
            "table": {str(k): v for k, v in graded_table.items()},
            "monotone_medians": monotone,
            "interior_buckets_count": interior_buckets,
            "performed": interior_buckets >= 3,
        }
        log(f"  Graded control: {len(k_sorted)} buckets, monotone={monotone}, interior={interior_buckets}")

        # Predicted law: F_L_pred(D) = K * sqrt(p) * sum_{d<=D, d L-smooth} sqrt(d)
        # K fitted by matching total mass at D_max
        sqrt_p = math.sqrt(p)
        smooth_sqrt_cumsum = {}
        running = 0.0
        all_smooth = compute_L_smooth_integers(ELL_SET_L, max(D_grid) if D_grid else 1)
        for D in D_grid:
            smooth_at_D = [d for d in all_smooth if d <= D]
            running = sum(math.sqrt(d) for d in smooth_at_D)
            smooth_sqrt_cumsum[D] = running

        # Fit K at D_max
        D_max_val = D_grid[-1] if D_grid else 1
        if smooth_sqrt_cumsum[D_max_val] > 0 and treatment_cdf[D_max_val] > 0:
            K_fitted = treatment_cdf[D_max_val] / (sqrt_p * smooth_sqrt_cumsum[D_max_val])
        else:
            K_fitted = None

        # Compute predicted values and ratio drift
        predicted_cdf = {}
        ratio_drift = {}
        if K_fitted is not None:
            for D in D_grid:
                pred = K_fitted * sqrt_p * smooth_sqrt_cumsum[D]
                predicted_cdf[D] = pred
                if pred > 0 and treatment_cdf[D] > 0:
                    ratio_drift[D] = treatment_cdf[D] / pred
        max_ratio = max(ratio_drift.values()) if ratio_drift else None
        min_ratio = min(ratio_drift.values()) if ratio_drift else None

        # Class number tail check
        h_neg_p = class_number(-p)
        log(f"  h(-{p}) = {h_neg_p}, F_p-rational count = {cell['fp_rational_count']}")
        log(f"  F_L(1) = {treatment_cdf.get(1, 0)}")

        treatment_results[str(p)] = {
            "S_size": S_size,
            "D_max": cell["D_max"],
            "D_grid": D_grid,
            "treatment_deltas": treatment_deltas,
            "treatment_cdf": {str(k): v for k, v in treatment_cdf.items()},
            "beta_hat": beta_hat,
            "intercept": intercept_hat,
            "r2": r2_hat,
            "residuals": resid_hat,
            "k_values": k_values,
            "graded_table": {str(k): v for k, v in graded_table.items()},
            "K_fitted": K_fitted,
            "predicted_cdf": {str(k): v for k, v in predicted_cdf.items()},
            "ratio_drift": {str(k): v for k, v in ratio_drift.items()},
            "max_min_ratio": [max_ratio, min_ratio],
            "h_neg_p": h_neg_p,
            "fp_rational_count": cell["fp_rational_count"],
            "F_L_1": treatment_cdf.get(1, 0),
        }

    # ================================================================
    # CROSS-PRIME gamma_hat
    # ================================================================
    log(f"\n{'='*60}")
    log(f"CROSS-PRIME GAMMA FIT")
    log(f"{'='*60}")

    # gamma_hat: OLS slope of log(F_L(1)/|S|) on log(p)
    log_p_vals = []
    log_F1_vals = []
    for p in PRIMES:
        tr = treatment_results[str(p)]
        F1 = tr["F_L_1"]
        S = tr["S_size"]
        if F1 > 0:
            log_p_vals.append(math.log(p))
            log_F1_vals.append(math.log(F1 / S))

    gamma_hat, gamma_intercept, gamma_r2, gamma_resid = ols_slope(log_p_vals, log_F1_vals)
    # gamma is the NEGATIVE of the slope (since F(1)/N ~ p^{-gamma})
    gamma_hat_val = -gamma_hat if gamma_hat is not None else None
    log(f"  gamma_hat = {gamma_hat_val} (slope = {gamma_hat}), R^2 = {gamma_r2}")

    # ================================================================
    # TAIL CHECKS
    # ================================================================
    log(f"\n{'='*60}")
    log(f"TAIL CHECKS")
    log(f"{'='*60}")

    tail_checks = {}
    for p in PRIMES:
        tr = treatment_results[str(p)]
        nr = null_results_all[str(p)]

        # Top of window: F_L(D_max)/|S| < 1
        D_max_val = tr["D_grid"][-1] if tr["D_grid"] else None
        if D_max_val:
            top_coverage = tr["treatment_cdf"][str(D_max_val)] / tr["S_size"]
        else:
            top_coverage = None

        # Null-arm sanity: log(median)/log(|S|) in [0.35, 0.65]
        null_deltas_sorted = sorted(nr["null_deltas"])
        null_median = null_deltas_sorted[len(null_deltas_sorted) // 2] if null_deltas_sorted else 1
        if null_median > 0 and tr["S_size"] > 1:
            log_ratio = math.log(null_median) / math.log(tr["S_size"])
        else:
            log_ratio = None

        # Extreme value: max delta_L <= 4^{k_max}
        max_delta = max(tr["treatment_deltas"])
        k_max = max(tr["k_values"][i] for i in range(tr["S_size"]) if tr["k_values"][i] is not None)
        extreme_bound = 4 ** k_max

        tail_checks[str(p)] = {
            "D_max_coverage_below_1": top_coverage is not None and top_coverage < 1.0,
            "D_max_coverage": top_coverage,
            "null_median": null_median,
            "null_log_ratio": log_ratio,
            "null_log_ratio_in_range": log_ratio is not None and 0.35 <= log_ratio <= 0.65,
            "max_delta_L": max_delta,
            "k_max": k_max,
            "extreme_bound_4_k_max": extreme_bound,
            "extreme_check_pass": max_delta <= extreme_bound,
        }
        log(f"  p={p}: top_cov={top_coverage:.4f}, null_log_ratio={log_ratio}, max_delta={max_delta} <= 4^{k_max}={extreme_bound}: {max_delta <= extreme_bound}")

    # ================================================================
    # APPLY PRE-REGISTERED FORK
    # ================================================================
    fork_verdicts = {}
    for p in PRIMES:
        tr = treatment_results[str(p)]
        beta = tr["beta_hat"]
        r2 = tr["r2"]
        if beta is None or r2 is None:
            fork_verdicts[str(p)] = "NO_FIT"
        elif r2 < 0.9:
            fork_verdicts[str(p)] = "NO_POWER_LAW_AT_THIS_SCALE"
        elif 1.35 <= beta <= 1.65:
            fork_verdicts[str(p)] = "CONSISTENT_WITH_3_OVER_2"
        elif 0.35 <= beta <= 0.65:
            fork_verdicts[str(p)] = "CONSISTENT_WITH_1_OVER_2"
        elif beta >= 1.85:
            fork_verdicts[str(p)] = "COVERING_BELOW_P13_HYPOTHESIS_GENERATING"
        elif 0.3 <= beta <= 2.5:
            fork_verdicts[str(p)] = "INTERMEDIATE_NO_CLEAR_MATCH"
        else:
            fork_verdicts[str(p)] = "OUTSIDE_PLAUSIBLE_RANGE"

    # ================================================================
    # NULL ARM SEED SPREAD
    # ================================================================
    null_seed_spread = {}
    for p in PRIMES:
        main_beta = null_results_all[str(p)]["beta_hat_null"]
        rep_betas = [null_replication[f"null-target-r{r}"][str(p)]["beta_hat_null"]
                     for r in range(1, 4)]
        all_null_betas = [main_beta] + rep_betas
        all_null_betas_clean = [b for b in all_null_betas if b is not None]
        if all_null_betas_clean:
            null_seed_spread[str(p)] = {
                "betas": all_null_betas_clean,
                "spread": max(all_null_betas_clean) - min(all_null_betas_clean),
                "mean": sum(all_null_betas_clean) / len(all_null_betas_clean),
            }
        else:
            null_seed_spread[str(p)] = {"betas": [], "spread": None, "mean": None}

    # ================================================================
    # SMOOTHNESS GAP DRIFT
    # ================================================================
    smoothness_gap = {}
    for p in PRIMES:
        tr = treatment_results[str(p)]
        if tr["max_min_ratio"][0] is not None and tr["max_min_ratio"][1] is not None:
            smoothness_gap[str(p)] = {
                "max_over_min": tr["max_min_ratio"][0] / tr["max_min_ratio"][1] if tr["max_min_ratio"][1] > 0 else None,
                "max_ratio": tr["max_min_ratio"][0],
                "min_ratio": tr["max_min_ratio"][1],
            }
        else:
            smoothness_gap[str(p)] = {"max_over_min": None}

    # ================================================================
    # ASSEMBLE FINAL RESULTS
    # ================================================================
    results["status"] = "completed"
    results["completed_at"] = time.strftime("%Y-%m-%dT%H:%M:%S%z")
    results["null_commitment"] = {
        "hash": null_commitment_hash,
        "timestamp": null_commitment_timestamp,
        "committed_before_treatment": null_arm_committed,
    }
    results["null_arm"] = null_results_all
    results["null_replication"] = null_replication
    results["null_seed_spread"] = null_seed_spread
    results["treatment_arm"] = {
        str(p): {
            "S_size": treatment_results[str(p)]["S_size"],
            "D_max": treatment_results[str(p)]["D_max"],
            "D_grid": treatment_results[str(p)]["D_grid"],
            "treatment_cdf": treatment_results[str(p)]["treatment_cdf"],
            "beta_hat": treatment_results[str(p)]["beta_hat"],
            "intercept": treatment_results[str(p)]["intercept"],
            "r2": treatment_results[str(p)]["r2"],
            "residuals": treatment_results[str(p)]["residuals"],
            "K_fitted": treatment_results[str(p)]["K_fitted"],
            "predicted_cdf": treatment_results[str(p)]["predicted_cdf"],
            "ratio_drift": treatment_results[str(p)]["ratio_drift"],
            "F_L_1": treatment_results[str(p)]["F_L_1"],
            "fp_rational_count": treatment_results[str(p)]["fp_rational_count"],
            "h_neg_p": treatment_results[str(p)]["h_neg_p"],
        }
        for p in PRIMES
    }
    results["gamma_hat"] = gamma_hat_val
    results["gamma_slope"] = gamma_hat
    results["gamma_r2"] = gamma_r2
    results["gamma_residuals"] = gamma_resid
    results["fork_verdicts"] = fork_verdicts
    results["controls"] = controls
    results["tail_checks"] = tail_checks
    results["smoothness_gap_drift"] = smoothness_gap

    return results


# ======================================================================
# ENTRY POINT
# ======================================================================

if __name__ == "__main__":
    log("=" * 60)
    log("EXP-SSI-6a2619: Supersingular Isogeny Census")
    log("=" * 60)
    log(f"Python: {sys.version}")
    log(f"Numpy: {np.__version__}")
    log(f"PID: {os.getpid()}")

    # Environment checks
    env_checks = {}
    try:
        import numpy
        env_checks["numpy"] = f"{numpy.__version__} -- import SUCCEEDS"
    except ImportError as e:
        env_checks["numpy"] = f"ABSENT -- {e}"
    try:
        import sympy
        env_checks["sympy"] = f"{sympy.__version__} -- import SUCCEEDS (NOT USED)"
    except ImportError as e:
        env_checks["sympy"] = f"ABSENT -- {e}"
    try:
        import sage
        env_checks["sage"] = f"PRESENT -- import SUCCEEDS (NOT USED)"
    except ImportError as e:
        env_checks["sage"] = f"ABSENT -- {e}"

    for k, v in env_checks.items():
        log(f"  {k}: {v}")

    t_start = time.time()

    try:
        results = run_experiment()
    except Exception as e:
        results = {
            "experiment_id": "EXP-SSI-6a2619",
            "run_id": "RUN-SSI-6a2619-001",
            "status": "infrastructure_error",
            "error": str(e),
            "traceback": traceback.format_exc(),
        }
        log(f"FATAL ERROR: {e}")
        traceback.print_exc()

    t_end = time.time()
    wall_clock = t_end - t_start

    results["wall_clock_seconds"] = wall_clock
    results["environment_checks"] = env_checks

    # Resource usage
    try:
        ru = resource.getrusage(resource.RUSAGE_SELF)
        results["peak_rss_mb"] = ru.ru_maxrss / (1024 * 1024)  # macOS reports in bytes
        results["user_time_seconds"] = ru.ru_utime
        results["system_time_seconds"] = ru.ru_stime
    except Exception:
        pass

    log(f"\nTotal wall clock: {wall_clock:.1f}s")
    log(f"Status: {results.get('status', 'unknown')}")

    # Write results
    output_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                              "runs", "RUN-SSI-6a2619-001")
    os.makedirs(output_dir, exist_ok=True)

    results_path = os.path.join(output_dir, "raw-result.json")
    with open(results_path, 'w') as f:
        json.dump(results, f, indent=2, default=str)
    log(f"Results written to {results_path}")

    # Summary
    if results.get("status") == "completed":
        log("\n" + "=" * 60)
        log("SUMMARY")
        log("=" * 60)
        for p in PRIMES:
            tr = results["treatment_arm"][str(p)]
            nr = results["null_arm"][str(p)]
            log(f"  p={p}: beta_hat={tr['beta_hat']:.4f}, R^2={tr['r2']:.4f}, "
                f"beta_null={nr['beta_hat_null']:.4f}" if tr['beta_hat'] else f"  p={p}: NO FIT")
        log(f"  gamma_hat = {results['gamma_hat']}")
        log(f"  Fork verdicts: {results['fork_verdicts']}")
        log(f"  Controls: positive={all(v['pass'] for v in results['controls']['positive_control_rate'].values())}, "
            f"envelope={all(v['count']==0 for v in results['controls']['envelope_violations'].values())}")

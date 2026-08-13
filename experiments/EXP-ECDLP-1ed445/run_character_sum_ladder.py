#!/usr/bin/env python3
"""
EXP-ECDLP-1ed445: Null-normalised H-PSEUDO character-sum ladder.

Measures C = max_{k=1..N-1} |sum_{P in F} e(2*pi*i*k*DL_G(P)/N)| / sqrt(B)
on three arms at each of four bit sizes (20, 22, 24, 26):
  - Treatment (EC factor base): small-x elliptic-curve factor base
  - Null (random subset): uniformly random B-subset of Z_N
  - Positive control (arithmetic progression): planted AP with forced C value

Reports ratio R = C_EC / C_null and growth rate across bit sizes.

Pure Python + numpy (for FFT and vectorized curve order). Deterministic seeds.
"""

import hashlib
import json
import math
import os
import sys
import time
from math import gcd
from typing import Optional

import numpy as np

# === Constants ===
DOMAIN = "EXP-ECDLP-1ed445/v1"
MASTER_SEED = 7719364
BITS_LIST = [20, 22, 24, 26]
B_PRIMARY = 512
B_SWEEP = [256, 512, 1024]
NULL_DRAWS = 200
CURVES_PER_RUNG_MEAN = 8
CURVES_PER_RUNG_MAX = 20
THETA_SWEEP = [0.0, 0.25, 0.5, 0.75, 1.0]
THETA_DRAWS = 20
GAMMA_E = 0.5772156649015329

# Committed values from KN-FIND-d4f820 and KN-FIND-4c9e71
COMMITTED_MEAN_C = {1009: 3.0, 4001: 3.5, 9001: 3.7, 50021: 3.84}
COMMITTED_MAX_C = {1009: 3.90, 4001: 3.87, 9001: 4.11, 50021: 5.18}


# === Seed derivation ===
def derive_seed(label: str, bits: int, counter: int) -> int:
    """
    Derive a deterministic seed from SHA-256 of:
    domain || "#" || decimal(master_seed) || "|" || label || "|" ||
    decimal(bits) || "|" || decimal(counter)
    Returns big-endian unsigned integer from the hash.
    """
    msg = f"{DOMAIN}#{MASTER_SEED}|{label}|{bits}|{counter}"
    h = hashlib.sha256(msg.encode('ascii')).digest()
    return int.from_bytes(h, 'big')


def derive_seed_int(label: str, bits: int, counter: int, modulus: int) -> int:
    """Derive a seed reduced modulo a given modulus."""
    return derive_seed(label, bits, counter) % modulus


# === Number theory utilities ===
def is_prime_trial(n: int) -> bool:
    """Trial division primality test (sufficient for n < 2^27)."""
    if n < 2:
        return False
    if n < 4:
        return True
    if n % 2 == 0 or n % 3 == 0:
        return False
    i = 5
    while i * i <= n:
        if n % i == 0 or n % (i + 2) == 0:
            return False
        i += 6
    return True


def mod_inverse(a: int, m: int) -> int:
    """Extended Euclidean algorithm for modular inverse."""
    if a < 0:
        a = a % m
    g, x, _ = _extended_gcd(a, m)
    if g != 1:
        raise ValueError(f"No inverse: gcd({a}, {m}) = {g}")
    return x % m


def _extended_gcd(a: int, b: int):
    if a == 0:
        return b, 0, 1
    g, x, y = _extended_gcd(b % a, a)
    return g, y - (b // a) * x, x


def sqrt_mod(a: int, p: int) -> Optional[int]:
    """Tonelli-Shanks square root mod p. Returns None if no root."""
    if a == 0:
        return 0
    if pow(a, (p - 1) // 2, p) != 1:
        return None
    if p % 4 == 3:
        return pow(a, (p + 1) // 4, p)
    # Tonelli-Shanks
    s, q = 0, p - 1
    while q % 2 == 0:
        s += 1
        q //= 2
    z = 2
    while pow(z, (p - 1) // 2, p) != p - 1:
        z += 1
    m_val = s
    c = pow(z, q, p)
    t = pow(a, q, p)
    r = pow(a, (q + 1) // 2, p)
    while True:
        if t == 1:
            return r
        i = 1
        tmp = (t * t) % p
        while tmp != 1:
            tmp = (tmp * tmp) % p
            i += 1
        b = pow(c, 1 << (m_val - i - 1), p)
        m_val = i
        c = (b * b) % p
        t = (t * c) % p
        r = (r * b) % p


def largest_prime_factor(n: int) -> Optional[int]:
    """Find largest prime factor of n."""
    if n <= 1:
        return None
    d = 2
    temp = n
    while d * d <= temp:
        while temp % d == 0:
            temp //= d
        d += 1
    if temp > 1:
        return temp
    # If temp == 1, the largest prime factor is d-1 or we need to re-find
    # Actually let's redo properly
    temp = n
    largest = None
    d = 2
    while d * d <= temp:
        while temp % d == 0:
            largest = d
            temp //= d
        d += 1
    if temp > 1:
        largest = temp
    return largest


# === Elliptic curve operations ===
def ec_add(P, Q, a, p):
    """Add two points on y^2 = x^3 + ax + b mod p. Points as (x,y) or None."""
    if P is None:
        return Q
    if Q is None:
        return P
    x1, y1 = P
    x2, y2 = Q
    if x1 == x2:
        if (y1 + y2) % p == 0:
            return None
        num = (3 * x1 * x1 + a) % p
        den = (2 * y1) % p
    else:
        num = (y2 - y1) % p
        den = (x2 - x1) % p
    inv_den = mod_inverse(den, p)
    lam = (num * inv_den) % p
    x3 = (lam * lam - x1 - x2) % p
    y3 = (lam * (x1 - x3) - y1) % p
    return (x3, y3)


def ec_mul(k: int, P, a, p):
    """Scalar multiplication k*P using double-and-add."""
    if k == 0 or P is None:
        return None
    if k < 0:
        P = (P[0], (-P[1]) % p)
        k = -k
    result = None
    addend = P
    while k > 0:
        if k & 1:
            result = ec_add(result, addend, a, p)
        addend = ec_add(addend, addend, a, p)
        k >>= 1
    return result


# === Vectorized curve order (numpy) ===
def build_legendre_table(p: int) -> np.ndarray:
    """Build Legendre symbol lookup table for F_p using numpy."""
    leg_table = np.full(p, -1, dtype=np.int8)
    leg_table[0] = 0
    x_vals = np.arange(1, (p + 1) // 2, dtype=np.int64)
    squares = (x_vals * x_vals) % p
    leg_table[squares] = 1
    return leg_table


def count_curve_order_fast(a_coeff: int, b_coeff: int, p: int,
                           leg_table: np.ndarray) -> int:
    """Count #E(F_p) using vectorized Legendre symbol lookup."""
    x_all = np.arange(p, dtype=np.int64)
    rhs = x_all * x_all % p
    rhs = rhs * x_all % p
    rhs = (rhs + a_coeff * x_all) % p
    rhs = (rhs + b_coeff) % p
    leg_vals = leg_table[rhs.astype(np.intp)]
    return int(p + 1 + np.sum(leg_vals))


# === Curve construction ===
def construct_prime(bits: int) -> int:
    """Construct prime deterministically per spec."""
    seed_val = derive_seed("prime", bits, 0)
    h = seed_val
    L = 1 << (bits - 1)
    U = 1 << bits
    c0 = L + 1 + 2 * (h % (1 << (bits - 2)))
    if c0 >= U:
        c0 = L + 1 + 2 * ((h % (1 << (bits - 2))) % ((U - L) // 2))
    k = 0
    while True:
        candidate = c0 + 2 * k
        if candidate >= U:
            raise RuntimeError(
                f"CONSTRUCTION_FAILURE: no prime in [{L},{U}) for bits={bits}")
        if is_prime_trial(candidate):
            return candidate
        k += 1


def construct_curve(bits: int, p: int, counter: int, leg_table: np.ndarray):
    """
    Construct curve deterministically. Returns (a, b, N, cofactor, G) or None.
    """
    a_coeff = derive_seed_int("curve-a", bits, counter, p)
    b_coeff = derive_seed_int("curve-b", bits, counter, p)

    # Non-singular check
    disc = (4 * pow(a_coeff, 3, p) + 27 * pow(b_coeff, 2, p)) % p
    if disc == 0:
        return None

    # Count order (vectorized)
    order = count_curve_order_fast(a_coeff, b_coeff, p, leg_table)

    # Find largest prime factor
    N = largest_prime_factor(order)
    if N is None or N <= order // 8:
        return None

    cofactor = order // N

    # Find generator G
    G = None
    for x in range(p):
        rhs = (x * x * x + a_coeff * x + b_coeff) % p
        y = sqrt_mod(rhs, p)
        if y is None:
            continue
        P = (x, y)
        candidate = ec_mul(cofactor, P, a_coeff, p)
        if candidate is not None:
            check = ec_mul(N, candidate, a_coeff, p)
            if check is None:
                G = candidate
                break

    if G is None:
        return None

    return a_coeff, b_coeff, N, cofactor, G


# === DL table construction ===
def build_dl_table(G, N: int, a_coeff: int, p: int) -> dict:
    """
    Build DL table by iterating Q <- Q + G for N steps.
    Returns dict mapping (x, y) -> DL value.
    """
    dl_table = {}
    Q = G
    for i in range(1, N + 1):
        if Q is not None and Q not in dl_table:
            dl_table[Q] = i % N
        Q = ec_add(Q, G, a_coeff, p)
    return dl_table


# === Factor base construction ===
def build_factor_base(dl_table: dict, B: int):
    """
    Build factor base F sorted by (x, y), truncated to first B points.
    Returns (tau, F_points_list, F_dls).
    """
    points_by_coord = [(x, y, dl_val) for (x, y), dl_val in dl_table.items()]
    points_by_coord.sort(key=lambda t: (t[0], t[1]))

    F = points_by_coord[:B]
    if len(F) < B:
        tau = None  # insufficient points
    else:
        tau = F[-1][0] + 1

    F_dls = [pt[2] for pt in F]
    return tau, F, F_dls


# === Character sum (FFT) ===
def compute_C_fft(positions: list, N: int) -> tuple:
    """
    Compute C = max_{k=1..N-1} |sum e(2*pi*i*k*j/N)| / sqrt(|positions|)
    via one real FFT of length N.
    Returns (C, k_star).
    """
    B = len(positions)
    indicator = np.zeros(N, dtype=np.float64)
    for pos in positions:
        indicator[pos % N] += 1.0

    # rfft: returns N//2 + 1 complex coefficients for k=0..N//2
    # By conjugate symmetry, max over k=1..N-1 = max over k=1..N//2
    spectrum = np.fft.rfft(indicator)
    magnitudes = np.abs(spectrum[1:])  # k=1 to k=N//2
    k_star_idx = np.argmax(magnitudes)
    k_star = k_star_idx + 1
    max_mag = magnitudes[k_star_idx]

    C = max_mag / math.sqrt(B)
    return C, int(k_star)


# === Null subset generation ===
def generate_null_subset(bits: int, draw_idx: int, N: int, B: int) -> list:
    """Generate uniform random B-subset of Z_N via SHA-256 rejection."""
    positions = set()
    counter = 0
    while len(positions) < B:
        val = derive_seed_int("null", bits, draw_idx * 10000 + counter, N)
        positions.add(val)
        counter += 1
    return list(positions)


# === Statistics ===
def least_squares_slope(x: list, y: list) -> float:
    """Simple OLS slope."""
    n = len(x)
    x_mean = sum(x) / n
    y_mean = sum(y) / n
    num = sum((xi - x_mean) * (yi - y_mean) for xi, yi in zip(x, y))
    den = sum((xi - x_mean) ** 2 for xi in x)
    return num / den if den != 0 else 0.0


def least_squares_slope_with_ci(x: list, y: list) -> tuple:
    """OLS slope with 95% CI. Returns (slope, ci_low, ci_high)."""
    n = len(x)
    slope = least_squares_slope(x, y)
    if n < 3:
        return slope, slope - 0.1, slope + 0.1

    x_mean = sum(x) / n
    y_mean = sum(y) / n
    intercept = y_mean - slope * x_mean

    residuals = [yi - (slope * xi + intercept) for xi, yi in zip(x, y)]
    sse = sum(r * r for r in residuals)
    mse = sse / (n - 2)
    ss_xx = sum((xi - x_mean) ** 2 for xi in x)
    se_slope = math.sqrt(mse / ss_xx) if ss_xx > 0 and mse >= 0 else 0.1

    # t-values for 95% CI
    t_table = {1: 12.706, 2: 4.303, 3: 3.182, 4: 2.776, 5: 2.571}
    t_val = t_table.get(n - 2, 2.0)

    return slope, slope - t_val * se_slope, slope + t_val * se_slope


def r_squared(x: list, y: list) -> float:
    """R^2 of linear fit."""
    n = len(x)
    slope = least_squares_slope(x, y)
    x_mean = sum(x) / n
    y_mean = sum(y) / n
    intercept = y_mean - slope * x_mean
    ss_res = sum((yi - (slope * xi + intercept)) ** 2 for xi, yi in zip(x, y))
    ss_tot = sum((yi - y_mean) ** 2 for yi in y)
    return 1.0 - ss_res / ss_tot if ss_tot != 0 else 1.0


# ============================================================
# STAGE 0: Arithmetic on committed values
# ============================================================
def run_stage0() -> dict:
    """Reproduce ratio table from KN-FIND committed values."""
    print("=" * 70)
    print("STAGE 0: Arithmetic reproduction from committed values")
    print("=" * 70)

    results = {"mean": {}, "max": {}, "models": {}}
    primes = sorted(COMMITTED_MEAN_C.keys())

    for p_val in primes:
        N_approx = p_val  # N ~ p for these curves
        c_null = math.sqrt(math.log((N_approx - 1) / 2) + GAMMA_E)
        c_mean = COMMITTED_MEAN_C[p_val]
        c_max = COMMITTED_MAX_C[p_val]
        r_mean = c_mean / c_null
        r_max = c_max / c_null
        results["mean"][str(p_val)] = {
            "C_committed": c_mean,
            "C_null_derived": round(c_null, 6),
            "R": round(r_mean, 6)
        }
        results["max"][str(p_val)] = {
            "C_committed": c_max,
            "C_null_derived": round(c_null, 6),
            "R": round(r_max, 6)
        }
        print(f"  p={p_val:>6}: C_null={c_null:.4f}, "
              f"R_mean={r_mean:.4f}, R_max={r_max:.4f}")

    # Log-log slopes
    log_p = [math.log(p_val) for p_val in primes]
    R_mean_vals = [results["mean"][str(p_val)]["R"] for p_val in primes]
    R_max_vals = [results["max"][str(p_val)]["R"] for p_val in primes]
    log_R_mean = [math.log(r) for r in R_mean_vals]
    log_R_max = [math.log(r) for r in R_max_vals]

    alpha_mean = least_squares_slope(log_p, log_R_mean)
    alpha_max = least_squares_slope(log_p, log_R_max)

    results["alpha_resid_mean"] = round(alpha_mean, 6)
    results["alpha_resid_max"] = round(alpha_max, 6)

    # Three model R^2 for raw C_mean
    log_c_mean = [math.log(COMMITTED_MEAN_C[p_val]) for p_val in primes]
    r2_power = r_squared(log_p, log_c_mean)
    log_log_p = [math.log(math.log(p_val)) for p_val in primes]
    r2_sqrtlog = r_squared(log_log_p, log_c_mean)
    log_log_log_p = [math.log(math.log(math.log(p_val))) for p_val in primes]
    r2_logloglog = r_squared(log_log_log_p, log_c_mean)

    results["models"] = {
        "R2_power_law_C_vs_p": round(r2_power, 6),
        "R2_sqrt_log_p": round(r2_sqrtlog, 6),
        "R2_log_log_log_p": round(r2_logloglog, 6)
    }

    # Alpha_equiv over three consecutive intervals
    alpha_intervals = []
    for i in range(len(primes) - 1):
        a_i = (log_c_mean[i + 1] - log_c_mean[i]) / (log_p[i + 1] - log_p[i])
        alpha_intervals.append(round(a_i, 6))
    results["alpha_equiv_intervals"] = alpha_intervals

    # Terminating check
    results["R_mean_values"] = [round(r, 6) for r in R_mean_vals]
    results["terminating_check"] = "PASS" if abs(alpha_mean) < 0.040 else "FAIL"

    print(f"\n  alpha_resid (mean): {alpha_mean:.6f}")
    print(f"  alpha_resid (max):  {alpha_max:.6f}")
    print(f"  R (mean) values: {[round(r, 4) for r in R_mean_vals]}")
    print(f"  Model R^2: power={r2_power:.4f}, sqrt_log={r2_sqrtlog:.4f}, "
          f"lll={r2_logloglog:.4f}")
    print(f"  alpha_equiv intervals: {alpha_intervals}")
    print(f"  Terminating check (|alpha_mean| < 0.040): {results['terminating_check']}")

    return results


# ============================================================
# STAGE 1: Null arm and controls
# ============================================================
def run_stage1(bits_list: list) -> dict:
    """Generate null arm, CTRL-AP, CTRL-THETA at all rungs."""
    print("\n" + "=" * 70)
    print("STAGE 1: Null arm and controls (committed BEFORE EC arm)")
    print("=" * 70)

    results = {
        "null_arm": {},
        "ctrl_ap": {},
        "ctrl_theta": {},
        "curve_metadata": {}  # store curve info for stage 2
    }

    for bits in bits_list:
        print(f"\n  {'='*50}")
        print(f"  RUNG: bits = {bits}")
        print(f"  {'='*50}")

        p = construct_prime(bits)
        print(f"  p = {p} ({p.bit_length()} bits)")

        # Build Legendre table for fast curve order
        leg_table = build_legendre_table(p)

        # Generate curves to get N values
        curve_data = []
        counter = 0
        max_attempts = 2000
        while len(curve_data) < CURVES_PER_RUNG_MAX and counter < max_attempts:
            result = construct_curve(bits, p, counter, leg_table)
            counter += 1
            if result is not None:
                a_c, b_c, N, cofactor, G = result
                curve_data.append({
                    "counter": counter - 1,
                    "a": a_c, "b": b_c,
                    "N": N, "cofactor": cofactor, "G": G, "p": p
                })
                if len(curve_data) <= 3:
                    print(f"    Curve {len(curve_data)}: a={a_c}, b={b_c}, "
                          f"N={N}, cof={cofactor}")

        print(f"  Found {len(curve_data)} valid curves in {counter} attempts")

        if len(curve_data) == 0:
            print(f"  *** CONSTRUCTION_FAILURE at bits={bits} ***")
            results["null_arm"][str(bits)] = {"status": "CONSTRUCTION_FAILURE"}
            continue

        # Use first curve's N as representative for null arm
        N_rep = curve_data[0]["N"]
        results["curve_metadata"][str(bits)] = {
            "p": p,
            "N_representative": N_rep,
            "num_curves": len(curve_data),
            "attempts": counter
        }

        # --- NULL ARM ---
        print(f"\n  NULL ARM: {NULL_DRAWS} draws, N={N_rep}, B={B_PRIMARY}")
        t0 = time.time()
        null_C_values = []
        for draw_idx in range(NULL_DRAWS):
            positions = generate_null_subset(bits, draw_idx, N_rep, B_PRIMARY)
            C_val, _ = compute_C_fft(positions, N_rep)
            null_C_values.append(C_val)
            if (draw_idx + 1) % 50 == 0:
                print(f"    ... {draw_idx+1}/{NULL_DRAWS} draws "
                      f"({time.time()-t0:.1f}s)")

        null_mean = float(np.mean(null_C_values))
        null_std = float(np.std(null_C_values))
        null_max_val = float(np.max(null_C_values))
        null_min_val = float(np.min(null_C_values))
        c_null_derived = math.sqrt(math.log((N_rep - 1) / 2) + GAMMA_E)
        rel_error = abs(null_mean - c_null_derived) / c_null_derived

        results["null_arm"][str(bits)] = {
            "N": N_rep,
            "B": B_PRIMARY,
            "null_mean_C": round(null_mean, 6),
            "null_std_C": round(null_std, 6),
            "null_max_C": round(null_max_val, 6),
            "null_min_C": round(null_min_val, 6),
            "C_null_derived": round(c_null_derived, 6),
            "relative_error_G1": round(rel_error, 6),
            "G1_pass": rel_error < 0.05,
            "num_draws": NULL_DRAWS,
            "elapsed_s": round(time.time() - t0, 2)
        }

        print(f"  NULL result: mean={null_mean:.4f}, derived={c_null_derived:.4f}, "
              f"rel_err={rel_error:.4f}")
        print(f"    G1 ({'PASS' if rel_error < 0.05 else '*** FAIL ***'})")

        # --- CTRL-AP ---
        print(f"\n  CTRL-AP:")
        a_ap = derive_seed_int("ap-a", bits, 0, N_rep)
        d_ap = derive_seed_int("ap-d", bits, 0, N_rep)
        d_attempts = 0
        while gcd(d_ap, N_rep) != 1:
            d_attempts += 1
            d_ap = derive_seed_int("ap-d", bits, d_attempts, N_rep)

        ap_positions = [(a_ap + j * d_ap) % N_rep for j in range(B_PRIMARY)]
        C_ap, k_star_ap = compute_C_fft(ap_positions, N_rep)
        forced_val = math.sqrt(B_PRIMARY)
        ap_rel_error = abs(C_ap - forced_val) / forced_val

        # Expected k* = d^{-1} mod N
        d_inv = mod_inverse(d_ap, N_rep)
        # k_star from rfft is in [1, N//2], the true maximizer could be d_inv or N-d_inv
        k_star_match = (k_star_ap == d_inv) or (k_star_ap == N_rep - d_inv)

        results["ctrl_ap"][str(bits)] = {
            "C_ap": round(C_ap, 6),
            "forced_sqrt_B": round(forced_val, 6),
            "relative_error_G2": round(ap_rel_error, 8),
            "G2_pass": ap_rel_error < 0.01,
            "k_star": k_star_ap,
            "d_inv_mod_N": d_inv,
            "k_star_matches_theory": k_star_match,
            "a_ap": a_ap,
            "d_ap": d_ap,
            "d_attempts": d_attempts
        }

        print(f"    C_AP={C_ap:.6f}, forced={forced_val:.6f}, "
              f"rel_err={ap_rel_error:.8f}")
        print(f"    k*={k_star_ap}, d^-1={d_inv}, match={k_star_match}")
        print(f"    G2 ({'PASS' if ap_rel_error < 0.01 else '*** FAIL ***'})")

        # --- CTRL-THETA ---
        print(f"\n  CTRL-THETA sweep:")
        theta_results = []
        for theta in THETA_SWEEP:
            theta_C_values = []
            for draw_idx in range(THETA_DRAWS):
                n_random = int(round(theta * B_PRIMARY))
                n_ap = B_PRIMARY - n_random

                # AP part
                positions = [(a_ap + j * d_ap) % N_rep for j in range(n_ap)]
                # Random part
                for ri in range(n_random):
                    seed_counter = draw_idx * B_PRIMARY + ri + int(theta * 100000)
                    val = derive_seed_int("theta", bits, seed_counter, N_rep)
                    positions.append(val)

                C_val, _ = compute_C_fft(positions, N_rep)
                theta_C_values.append(C_val)

            t_mean = float(np.mean(theta_C_values))
            t_std = float(np.std(theta_C_values))
            theta_results.append({
                "theta": theta,
                "mean_C": round(t_mean, 6),
                "std_C": round(t_std, 6)
            })
            print(f"    theta={theta:.2f}: mean_C={t_mean:.4f} +/- {t_std:.4f}")

        means = [tr["mean_C"] for tr in theta_results]
        monotone = all(means[i] >= means[i + 1] for i in range(len(means) - 1))

        results["ctrl_theta"][str(bits)] = {
            "sweep": theta_results,
            "monotone_decreasing": monotone,
            "G3_pass": monotone
        }
        print(f"    Monotone decreasing: {monotone} -> G3 "
              f"({'PASS' if monotone else '*** FAIL ***'})")

        # Store curve data (internal, not serialized)
        results[f"_curves_{bits}"] = curve_data

    # Compute digest of the null arm record
    serializable = {k: v for k, v in results.items() if not k.startswith("_")}
    null_digest = hashlib.sha256(
        json.dumps(serializable, sort_keys=True, default=str).encode()
    ).hexdigest()
    results["null_arm_digest_sha256"] = null_digest
    print(f"\n  Null arm + controls digest: {null_digest[:32]}...")

    return results


# ============================================================
# STAGE 2: EC arm
# ============================================================
def run_stage2(bits_list: list, stage1: dict) -> dict:
    """EC arm: DL tables, factor bases, character sums."""
    print("\n" + "=" * 70)
    print("STAGE 2: EC arm (DL tables + factor bases + FFTs)")
    print("=" * 70)

    # Check terminating conditions
    for bits in bits_list:
        bs = str(bits)
        if bs in stage1["null_arm"]:
            if stage1["null_arm"][bs].get("status") == "CONSTRUCTION_FAILURE":
                return {"status": "CONSTRUCTION_FAILURE", "bits": bits}
            if not stage1["null_arm"][bs].get("G1_pass", True):
                return {"status": "TERMINATED_G1", "bits": bits,
                        "reason": f"G1 failed at bits={bits}"}
        if bs in stage1["ctrl_ap"]:
            if not stage1["ctrl_ap"][bs].get("G2_pass", True):
                return {"status": "TERMINATED_G2", "bits": bits,
                        "reason": f"G2 failed at bits={bits}"}
        if bs in stage1["ctrl_theta"]:
            if not stage1["ctrl_theta"][bs].get("G3_pass", True):
                return {"status": "TERMINATED_G3", "bits": bits,
                        "reason": f"G3 failed at bits={bits}"}

    results = {"per_rung": {}, "per_curve": []}

    for bits in bits_list:
        print(f"\n  {'='*50}")
        print(f"  EC ARM: bits = {bits}")
        print(f"  {'='*50}")

        curve_data = stage1.get(f"_curves_{bits}", [])
        if not curve_data:
            results["per_rung"][str(bits)] = {"status": "NO_CURVES"}
            continue

        p = curve_data[0]["p"]
        ec_C_mean_list = []  # first 8 curves
        ec_C_all_list = []   # all curves (up to 20)

        for ci, cd in enumerate(curve_data):
            t_curve_start = time.time()
            a_coeff = cd["a"]
            b_coeff = cd["b"]
            N = cd["N"]
            cofactor = cd["cofactor"]
            G = cd["G"]

            # Build DL table
            dl_table = build_dl_table(G, N, a_coeff, p)
            t_dl = time.time() - t_curve_start

            # Build factor base
            tau, F_points, F_dls = build_factor_base(dl_table, B_PRIMARY)
            actual_B = len(F_dls)

            if actual_B < B_PRIMARY:
                print(f"    Curve {ci+1}: SKIP (only {actual_B} FB points)")
                continue

            # Character sum on EC factor base
            C_ec, k_star = compute_C_fft(F_dls, N)
            elapsed = time.time() - t_curve_start

            # Check if [k*]G lies in F
            k_star_point = ec_mul(k_star, G, a_coeff, p)
            F_point_set = set((pt[0], pt[1]) for pt in F_points)
            k_star_in_F = k_star_point in F_point_set if k_star_point else False

            record = {
                "bits": bits, "p": p, "curve_index": ci,
                "a": a_coeff, "b": b_coeff, "N": N,
                "cofactor": cofactor, "G": list(G),
                "tau": tau, "F_size": actual_B,
                "C_EC": round(C_ec, 6),
                "k_star": k_star,
                "k_star_in_F": k_star_in_F,
                "dl_table_time_s": round(t_dl, 2),
                "total_time_s": round(elapsed, 2)
            }
            results["per_curve"].append(record)
            ec_C_all_list.append(C_ec)
            if ci < CURVES_PER_RUNG_MEAN:
                ec_C_mean_list.append(C_ec)

            if (ci + 1) % 5 == 0 or ci == 0:
                print(f"    Curve {ci+1}/{len(curve_data)}: C_EC={C_ec:.4f}, "
                      f"k*={k_star}, k*_in_F={k_star_in_F} "
                      f"[DL:{t_dl:.1f}s, total:{elapsed:.1f}s]")

        if not ec_C_mean_list:
            results["per_rung"][str(bits)] = {"status": "NO_VALID_CURVES"}
            continue

        # Rung statistics
        C_ec_mean = float(np.mean(ec_C_mean_list))
        C_ec_std = float(np.std(ec_C_mean_list))
        C_ec_max = float(np.max(ec_C_all_list))
        C_null_mean = stage1["null_arm"][str(bits)]["null_mean_C"]

        R_mean = C_ec_mean / C_null_mean
        R_max = C_ec_max / C_null_mean
        delta_mean = C_ec_mean - C_null_mean
        delta_max = C_ec_max - C_null_mean

        results["per_rung"][str(bits)] = {
            "p": p,
            "N_representative": curve_data[0]["N"],
            "num_curves_mean": len(ec_C_mean_list),
            "num_curves_max": len(ec_C_all_list),
            "C_EC_mean": round(C_ec_mean, 6),
            "C_EC_std": round(C_ec_std, 6),
            "C_EC_max": round(C_ec_max, 6),
            "C_null_mean": round(C_null_mean, 6),
            "R_mean": round(R_mean, 6),
            "R_max": round(R_max, 6),
            "delta_mean": round(delta_mean, 6),
            "delta_max": round(delta_max, 6),
            "G4_R_mean_in_range": 1.05 <= R_mean <= 1.40
        }

        print(f"\n  RUNG SUMMARY (bits={bits}):")
        print(f"    C_EC: mean={C_ec_mean:.4f} +/- {C_ec_std:.4f}, max={C_ec_max:.4f}")
        print(f"    C_null_mean={C_null_mean:.4f}")
        print(f"    R_mean={R_mean:.4f}, R_max={R_max:.4f}")
        print(f"    delta_mean={delta_mean:.4f}, delta_max={delta_max:.4f}")
        print(f"    G4 (R_mean in [1.05,1.40]): "
              f"{'PASS' if 1.05 <= R_mean <= 1.40 else 'OUTSIDE RANGE'}")

    # === Global metrics G5-G8 ===
    rungs = sorted([int(b) for b in results["per_rung"]
                    if "R_mean" in results["per_rung"][b]])

    if len(rungs) >= 2:
        log_p_vals = [math.log(results["per_rung"][str(b)]["p"]) for b in rungs]
        log_R_mean = [math.log(results["per_rung"][str(b)]["R_mean"]) for b in rungs]
        log_R_max = [math.log(results["per_rung"][str(b)]["R_max"]) for b in rungs]

        # G5
        alpha_m, ci_lo_m, ci_hi_m = least_squares_slope_with_ci(log_p_vals, log_R_mean)
        results["G5"] = {
            "alpha_resid_mean": round(alpha_m, 6),
            "ci_95": [round(ci_lo_m, 6), round(ci_hi_m, 6)],
            "contains_zero": ci_lo_m <= 0 <= ci_hi_m,
            "pass_lt_0.020": abs(alpha_m) < 0.020
        }

        # G6
        alpha_x, ci_lo_x, ci_hi_x = least_squares_slope_with_ci(log_p_vals, log_R_max)
        results["G6"] = {
            "alpha_resid_max": round(alpha_x, 6),
            "ci_95": [round(ci_lo_x, 6), round(ci_hi_x, 6)],
            "pass_lt_0.030": abs(alpha_x) < 0.030
        }

        # G7: Three model R^2 for C_EC
        log_C_ec = [math.log(results["per_rung"][str(b)]["C_EC_mean"]) for b in rungs]
        r2_pow = r_squared(log_p_vals, log_C_ec)
        log_log_p = [math.log(lp) for lp in log_p_vals]
        r2_slp = r_squared(log_log_p, log_C_ec)
        log3_p = [math.log(math.log(math.log(
            results["per_rung"][str(b)]["p"]))) for b in rungs]
        r2_lll = r_squared(log3_p, log_C_ec)
        results["G7_R2"] = {
            "C_vs_power_p": round(r2_pow, 6),
            "C_vs_sqrt_log_p": round(r2_slp, 6),
            "C_vs_log_log_log_p": round(r2_lll, 6)
        }

        # G8: additive residual slope
        deltas = [results["per_rung"][str(b)]["delta_mean"] for b in rungs]
        log_delta = [math.log(max(d, 1e-6)) for d in deltas]
        alpha_d, ci_lo_d, ci_hi_d = least_squares_slope_with_ci(log_p_vals, log_delta)
        results["G8"] = {
            "delta_slope": round(alpha_d, 6),
            "ci_95": [round(ci_lo_d, 6), round(ci_hi_d, 6)],
            "delta_values": [round(d, 6) for d in deltas]
        }

        # Maximising frequency analysis
        k_star_in_F_count = sum(1 for r in results["per_curve"]
                                if r.get("k_star_in_F", False))
        results["k_star_analysis"] = {
            "total_curves": len(results["per_curve"]),
            "k_star_in_F_count": k_star_in_F_count,
            "k_star_in_F_fraction": round(
                k_star_in_F_count / max(len(results["per_curve"]), 1), 4)
        }

        print(f"\n  {'='*50}")
        print(f"  GLOBAL METRICS")
        print(f"  {'='*50}")
        print(f"  G5: alpha_resid(mean) = {alpha_m:.6f} "
              f"CI=[{ci_lo_m:.4f}, {ci_hi_m:.4f}]")
        print(f"       contains_zero={ci_lo_m <= 0 <= ci_hi_m}, "
              f"|alpha|<0.020: {abs(alpha_m) < 0.020}")
        print(f"  G6: alpha_resid(max) = {alpha_x:.6f} "
              f"CI=[{ci_lo_x:.4f}, {ci_hi_x:.4f}]")
        print(f"       |alpha|<0.030: {abs(alpha_x) < 0.030}")
        print(f"  G7: R^2 power={r2_pow:.4f}, sqrt_log={r2_slp:.4f}, "
              f"lll={r2_lll:.4f}")
        print(f"  G8: delta slope = {alpha_d:.6f}")
        print(f"  k* in F: {k_star_in_F_count}/{len(results['per_curve'])}")

    return results


# ============================================================
# B-SWEEP DIAGNOSTIC
# ============================================================
def run_b_sweep(bits_targets: list, stage1: dict) -> dict:
    """B-sweep at bits=20 and 24 with B in {256, 512, 1024}."""
    print("\n" + "=" * 70)
    print("B-SWEEP DIAGNOSTIC (bits=20, 24; B in {256, 512, 1024})")
    print("=" * 70)

    results = {}
    for bits in bits_targets:
        curve_data = stage1.get(f"_curves_{bits}", [])
        if not curve_data:
            continue

        cd = curve_data[0]
        p, a_coeff, N, G = cd["p"], cd["a"], cd["N"], cd["G"]

        print(f"\n  bits={bits}, p={p}, N={N}")
        dl_table = build_dl_table(G, N, a_coeff, p)

        sweep = {}
        for B_val in B_SWEEP:
            _, _, F_dls = build_factor_base(dl_table, B_val)
            if len(F_dls) < B_val:
                sweep[str(B_val)] = {"status": "INSUFFICIENT_POINTS",
                                     "available": len(F_dls)}
                print(f"    B={B_val}: INSUFFICIENT ({len(F_dls)} available)")
                continue

            C_ec, _ = compute_C_fft(F_dls, N)

            # 50 null draws for diagnostic
            null_vals = []
            for di in range(50):
                pos = set()
                ctr = 0
                while len(pos) < B_val:
                    v = derive_seed_int("null", bits, 90000 + di * 10000 + ctr, N)
                    pos.add(v)
                    ctr += 1
                C_n, _ = compute_C_fft(list(pos), N)
                null_vals.append(C_n)

            null_mean = float(np.mean(null_vals))
            R_diag = C_ec / null_mean

            sweep[str(B_val)] = {
                "C_EC": round(C_ec, 4),
                "C_null_mean": round(null_mean, 4),
                "R": round(R_diag, 4),
                "B_over_N": round(B_val / N, 8)
            }
            print(f"    B={B_val}: C_EC={C_ec:.4f}, C_null={null_mean:.4f}, "
                  f"R={R_diag:.4f}")

        results[str(bits)] = sweep

    return results


# ============================================================
# TAIL CHECKS
# ============================================================
def compute_tail_checks(stage1: dict, stage2: dict, bits_list: list) -> dict:
    """Compute required tail statistics."""
    checks = {}

    # Largest C on null arm
    null_max_global = 0
    null_max_rung = None
    for bits in bits_list:
        bs = str(bits)
        if bs in stage1["null_arm"]:
            nm = stage1["null_arm"][bs].get("null_max_C", 0)
            if nm > null_max_global:
                null_max_global = nm
                null_max_rung = bits

    checks["null_max_C_global"] = round(null_max_global, 6)
    checks["null_max_rung"] = null_max_rung

    # Gumbel tail for the largest rung
    largest_bits = max(bits_list)
    bs = str(largest_bits)
    if bs in stage1["null_arm"] and "N" in stage1["null_arm"][bs]:
        N_largest = stage1["null_arm"][bs]["N"]
        M = (N_largest - 1) // 2
        if null_max_global > 0:
            # Pr[max > x] = 1 - (1 - exp(-x^2))^M
            # Use log for numerical stability
            log_surv = M * math.log(1.0 - math.exp(-null_max_global ** 2))
            p_exceed = 1.0 - math.exp(log_surv)
            checks["null_max_gumbel_exceedance_prob"] = p_exceed
        checks["smallest_B_over_N"] = round(B_PRIMARY / N_largest, 8)
        checks["exponential1_marginal_expected"] = (B_PRIMARY / N_largest) < 0.01

    # Largest C on EC arm
    if "per_curve" in stage2 and stage2["per_curve"]:
        best = max(stage2["per_curve"], key=lambda r: r.get("C_EC", 0))
        checks["ec_max_C_global"] = best["C_EC"]
        checks["ec_max_curve"] = {
            "bits": best["bits"], "p": best["p"],
            "curve_index": best["curve_index"],
            "k_star": best["k_star"],
            "k_star_in_F": best["k_star_in_F"]
        }

    return checks


# ============================================================
# MAIN
# ============================================================
def main():
    wall_start = time.time()
    print("=" * 70)
    print("EXP-ECDLP-1ed445: Null-normalised H-PSEUDO character-sum ladder")
    print("=" * 70)
    print(f"Started: {time.strftime('%Y-%m-%dT%H:%M:%SZ')}")
    print(f"Python: {sys.version}")
    print(f"NumPy: {np.__version__}")
    print(f"Master seed: {MASTER_SEED}")
    print(f"Domain: {DOMAIN}")
    print(f"B (primary): {B_PRIMARY}")
    print(f"Bits: {BITS_LIST}")
    print()

    all_results = {
        "experiment_id": "EXP-ECDLP-1ed445",
        "run_id": "RUN-ECDLP-1ed445-001",
        "master_seed": MASTER_SEED,
        "domain": DOMAIN,
        "B_primary": B_PRIMARY,
        "bits_list": BITS_LIST,
        "start_time": time.strftime('%Y-%m-%dT%H:%M:%SZ'),
        "python_version": sys.version.split()[0],
        "numpy_version": np.__version__,
    }

    # ---- STAGE 0 ----
    t0 = time.time()
    stage0 = run_stage0()
    all_results["stage0"] = stage0
    all_results["stage0_elapsed_s"] = round(time.time() - t0, 2)

    if stage0["terminating_check"] == "FAIL":
        all_results["status"] = "TERMINATED_STAGE0"
        all_results["terminal_reason"] = "alpha_resid(mean) >= 0.040 on committed values"
        all_results["end_time"] = time.strftime('%Y-%m-%dT%H:%M:%SZ')
        all_results["total_elapsed_s"] = round(time.time() - wall_start, 2)
        save_results(all_results)
        return all_results

    # ---- STAGE 1 ----
    t1 = time.time()
    stage1 = run_stage1(BITS_LIST)
    stage1_elapsed = time.time() - t1
    # Save only serializable parts
    stage1_out = {k: v for k, v in stage1.items() if not k.startswith("_")}
    all_results["stage1"] = stage1_out
    all_results["stage1_elapsed_s"] = round(stage1_elapsed, 2)

    # Check terminating
    terminated_stage1 = False
    for bits in BITS_LIST:
        bs = str(bits)
        if bs in stage1["null_arm"] and not stage1["null_arm"][bs].get("G1_pass", True):
            all_results["status"] = "TERMINATED_STAGE1_G1"
            all_results["terminal_bits"] = bits
            terminated_stage1 = True
            break
        if bs in stage1["ctrl_ap"] and not stage1["ctrl_ap"][bs].get("G2_pass", True):
            all_results["status"] = "TERMINATED_STAGE1_G2"
            all_results["terminal_bits"] = bits
            terminated_stage1 = True
            break
        if bs in stage1["ctrl_theta"] and not stage1["ctrl_theta"][bs].get("G3_pass", True):
            all_results["status"] = "TERMINATED_STAGE1_G3"
            all_results["terminal_bits"] = bits
            terminated_stage1 = True
            break

    if terminated_stage1:
        all_results["end_time"] = time.strftime('%Y-%m-%dT%H:%M:%SZ')
        all_results["total_elapsed_s"] = round(time.time() - wall_start, 2)
        save_results(all_results)
        return all_results

    # ---- STAGE 2 ----
    t2 = time.time()
    stage2 = run_stage2(BITS_LIST, stage1)
    all_results["stage2"] = stage2
    all_results["stage2_elapsed_s"] = round(time.time() - t2, 2)

    if isinstance(stage2.get("status"), str) and "TERMINATED" in stage2["status"]:
        all_results["status"] = stage2["status"]
        all_results["end_time"] = time.strftime('%Y-%m-%dT%H:%M:%SZ')
        all_results["total_elapsed_s"] = round(time.time() - wall_start, 2)
        save_results(all_results)
        return all_results

    # ---- B-SWEEP ----
    t3 = time.time()
    b_sweep = run_b_sweep([20, 24], stage1)
    all_results["b_sweep_diagnostic"] = b_sweep
    all_results["b_sweep_elapsed_s"] = round(time.time() - t3, 2)

    # ---- TAIL CHECKS ----
    tail_checks = compute_tail_checks(stage1_out, stage2, BITS_LIST)
    all_results["tail_checks"] = tail_checks

    # ---- FINAL ----
    all_results["status"] = "COMPLETED"
    all_results["end_time"] = time.strftime('%Y-%m-%dT%H:%M:%SZ')
    all_results["total_elapsed_s"] = round(time.time() - wall_start, 2)

    save_results(all_results)
    return all_results


def save_results(results: dict):
    """Save raw results JSON."""
    run_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                           "runs", "RUN-ECDLP-1ed445-001")
    os.makedirs(run_dir, exist_ok=True)

    path = os.path.join(run_dir, "raw-result.json")
    # Compute digest before saving
    content = json.dumps(results, indent=2, sort_keys=True, default=str)
    digest = hashlib.sha256(content.encode()).hexdigest()
    results["result_digest_sha256"] = digest

    # Re-serialize with digest
    content = json.dumps(results, indent=2, sort_keys=True, default=str)
    with open(path, 'w') as f:
        f.write(content)

    print(f"\n  Results saved: {path}")
    print(f"  Digest: {digest}")


if __name__ == "__main__":
    results = main()
    print(f"\n{'='*70}")
    print(f"FINAL STATUS: {results.get('status', 'UNKNOWN')}")
    print(f"Total wall time: {results.get('total_elapsed_s', 0):.1f}s")
    print(f"{'='*70}")

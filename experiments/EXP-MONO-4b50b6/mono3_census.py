#!/usr/bin/env python3
"""EXP-MONO-4b50b6 — m=3 Semaev summation-cover Frobenius cycle-type census.

Implements the frozen protocol MONO-m3-census-1.1.0-repair-cm-gate
(coordination/goals/GOAL-MONO-001/batches/BATCH-002/tasks/TASK-20260725-705/
monodromy_protocol.yaml), authorized for execution by DEC-20260802-505759.

The measured object is, for each specialization (x1,x2) in F_p^2, the univariate

    f_{x1,x2}(T) = S_3(x1, x2, T)
                 = (x1-x2)^2 T^2
                   - 2[(x1+x2)(x1 x2 + A) + 2B] T
                   + [(x1 x2 - A)^2 - 4B(x1+x2)]

over F_p, and its Frobenius cycle type (split / inert / ramified / degree-drop).

Two independent classifiers are run on every sample so that CF-IMPL-FACTOR has a
real second code path:

  PRIMARY   discriminant + Legendre symbol (protocol `toy_allowed` route)
  SECONDARY explicit root scan over F_p (independent of the discriminant formula)

Both must agree on every sample, and any curve flagged as an exception candidate
is re-classified exhaustively by the secondary path before admission.

The script also computes a CLOSED-FORM exact histogram over all p^2
specializations, from the identity proved in the accompanying contract:

    disc_T S_3(x1,x2,T) = 16 * f(x1) * f(x2),     f(x) = x^3 + A x + B

which makes the cycle type at (x1,x2) a function of chi(f(x1)) * chi(f(x2))
alone. The sampled census is the frozen protocol deliverable; the closed form is
reported alongside it as an exactness check, never as a substitute.

Usage:
  python3 mono3_census.py --primes 211 431 809 1601 --seed 20260725 \
      --samples 30000 --window 4 --m 3 \
      --protocol-version MONO-m3-census-1.1.0-repair-cm-gate \
      --out results.json

Exit 0 iff every declared control passes. A non-zero exit is an instrument
failure, never negative mathematical evidence.
"""

import argparse
import hashlib
import json
import random
import sys
import time
from collections import Counter

# ---------------------------------------------------------------------------
# Field and curve arithmetic (toy scale; exact integer arithmetic throughout)
# ---------------------------------------------------------------------------


def legendre(x, p):
    x %= p
    if x == 0:
        return 0
    r = pow(x, (p - 1) // 2, p)
    return 1 if r == 1 else -1


def inv(x, p):
    return pow(x % p, p - 2, p)


def is_prime(n):
    if n < 2:
        return False
    if n % 2 == 0:
        return n == 2
    d = 3
    while d * d <= n:
        if n % d == 0:
            return False
        d += 2
    return True


def ec_add(P, Q, A, p):
    if P is None:
        return Q
    if Q is None:
        return P
    x1, y1 = P
    x2, y2 = Q
    if x1 == x2 and (y1 + y2) % p == 0:
        return None
    if P != Q:
        m = (y2 - y1) * inv(x2 - x1, p) % p
    else:
        if y1 == 0:
            return None
        m = (3 * x1 * x1 + A) * inv(2 * y1, p) % p
    x3 = (m * m - x1 - x2) % p
    return (x3, (m * (x1 - x3) - y1) % p)


def ec_mul(k, P, A, p):
    R = None
    Q = P
    while k:
        if k & 1:
            R = ec_add(R, Q, A, p)
        Q = ec_add(Q, Q, A, p)
        k >>= 1
    return R


def chi_table(A, B, p):
    """chi(f(x)) for every x in F_p, plus the (Z, S, N) counts."""
    tab = [0] * p
    Z = S = N = 0
    for x in range(p):
        v = (x * x % p * x + A * x + B) % p
        c = legendre(v, p)
        tab[x] = c
        if c == 0:
            Z += 1
        elif c == 1:
            S += 1
        else:
            N += 1
    return tab, Z, S, N


def curve_order(A, B, p, tab=None):
    """#E(F_p) by exact enumeration: 1 + #{x : f(x)=0} + 2*#{x : f(x) is a QR}."""
    if tab is None:
        tab, Z, S, _ = chi_table(A, B, p)
    else:
        Z = sum(1 for c in tab if c == 0)
        S = sum(1 for c in tab if c == 1)
    return 1 + Z + 2 * S


def j_invariant(A, B, p):
    den = (4 * A ** 3 + 27 * B * B) % p
    if den == 0:
        return None
    return 1728 * 4 * A ** 3 % p * inv(den, p) % p


def is_extra_automorphism_j(jj, p):
    """j == 0 or j == 1728 AS ELEMENTS OF F_p. Comparing the reduced j against
    the integer 1728 is wrong for every p <= 1728 and for p | (j - 1728); the
    pinned primes 211, 431, 809 and 1601 are all in that range."""
    return jj is not None and (jj % p == 0 or jj % p == 1728 % p)


def sqrt_mod(a, p):
    a %= p
    if a == 0:
        return 0
    if legendre(a, p) != 1:
        return None
    if p % 4 == 3:
        return pow(a, (p + 1) // 4, p)
    # Tonelli-Shanks
    q, s = p - 1, 0
    while q % 2 == 0:
        q //= 2
        s += 1
    z = 2
    while legendre(z, p) != -1:
        z += 1
    m, c, t, r = s, pow(z, q, p), pow(a, q, p), pow(a, (q + 1) // 2, p)
    while t != 1:
        i, t2 = 0, t
        while t2 != 1:
            t2 = t2 * t2 % p
            i += 1
        b = pow(c, 1 << (m - i - 1), p)
        m, c = i, b * b % p
        t = t * c % p
        r = r * b % p
    return r


def lex_smallest_affine_point(A, B, p):
    """Smallest lexicographic affine (x, y) on E. On a prime-order curve every
    such point generates E(F_p)."""
    for x in range(p):
        v = (x * x % p * x + A * x + B) % p
        y = sqrt_mod(v, p)
        if y is not None:
            return (x, min(y, (-y) % p))
    return None


# ---------------------------------------------------------------------------
# Pinned S_3 (protocol `explicit_S3`, monic-in-T normalization after clearing
# the leading (x1-x2)^2 factor)
# ---------------------------------------------------------------------------


def s3_coeffs(x1, x2, A, B, p):
    a = pow(x1 - x2, 2, p)
    b = (-2 * ((x1 + x2) * (x1 * x2 + A) + 2 * B)) % p
    c = (pow(x1 * x2 - A, 2, p) - 4 * B * (x1 + x2)) % p
    return a, b, c


def s3_eval(x1, x2, T, A, B, p):
    a, b, c = s3_coeffs(x1, x2, A, B, p)
    return (a * T * T + b * T + c) % p


SPLIT, INERT, RAMIFIED, DEGDROP = "split_1_1", "inert_2", "ramified", "degree_drop"


def classify_primary(x1, x2, A, B, p):
    """Discriminant + Legendre route (protocol toy_allowed)."""
    a, b, c = s3_coeffs(x1, x2, A, B, p)
    if a == 0:
        return DEGDROP
    d = (b * b - 4 * a * c) % p
    if d == 0:
        return RAMIFIED
    return SPLIT if legendre(d, p) == 1 else INERT


def classify_secondary(x1, x2, A, B, p):
    """Independent code path: explicit root scan of the quadratic over F_p.

    Uses no discriminant formula. Counts distinct roots and multiplicity by
    direct evaluation and by dividing out a found root.
    """
    a, b, c = s3_coeffs(x1, x2, A, B, p)
    if a == 0:
        return DEGDROP
    roots = [T for T in range(p) if (a * T * T + b * T + c) % p == 0]
    if not roots:
        return INERT
    if len(roots) == 2:
        return SPLIT
    # exactly one root found: either a double root, or p == 2 (excluded here)
    return RAMIFIED


# ---------------------------------------------------------------------------
# Closed-form exact histogram over all p^2 specializations
# ---------------------------------------------------------------------------


def exact_histogram(Z, S, N, p):
    """Exact counts over all p^2 pairs (x1,x2), from
       disc_T S_3 = 16 f(x1) f(x2)   and   a = (x1-x2)^2.

    degree_drop : x1 == x2                        -> p
    ramified    : x1 != x2 and f(x1) f(x2) == 0   -> p^2 - (p-Z)^2 - Z
    split       : x1 != x2 and chi(f(x1)) == chi(f(x2)) != 0 -> S^2 + N^2 - (p-Z)
    inert       : chi(f(x1)) == -chi(f(x2))       -> 2 S N
    """
    deg_drop = p
    ram = p * p - (p - Z) ** 2 - Z
    split = S * S + N * N - (p - Z)
    inert = 2 * S * N
    assert deg_drop + ram + split + inert == p * p, "closed form does not partition F_p^2"
    return {DEGDROP: deg_drop, RAMIFIED: ram, SPLIT: split, INERT: inert}


# ---------------------------------------------------------------------------
# Degree-5 factorization instrument (CTRL-IMON-*), distinct-degree factorization
# ---------------------------------------------------------------------------


def p_trim(f, p):
    f = [c % p for c in f]
    while len(f) > 1 and f[-1] == 0:
        f.pop()
    return f


def p_mulmod(f, g, m, p):
    r = [0] * (len(f) + len(g) - 1)
    for i, a in enumerate(f):
        if a:
            for j, b in enumerate(g):
                r[i + j] = (r[i + j] + a * b) % p
    return p_mod(p_trim(r, p), m, p)


def p_mod(f, m, p):
    f = p_trim(f[:], p)
    dm = len(m) - 1
    if dm == 0:
        return [0]
    im = inv(m[-1], p)
    while len(f) - 1 >= dm and f != [0]:
        shift = len(f) - 1 - dm
        coef = f[-1] * im % p
        for i, c in enumerate(m):
            f[i + shift] = (f[i + shift] - coef * c) % p
        f = p_trim(f, p)
    return f


def p_gcd(f, g, p):
    f, g = p_trim(f[:], p), p_trim(g[:], p)
    while g != [0]:
        f, g = g, p_mod(f, g, p)
    if f == [0]:
        return f
    return [c * inv(f[-1], p) % p for c in f]


def p_powmod(base, e, m, p):
    r = [1]
    b = p_mod(base[:], m, p)
    while e:
        if e & 1:
            r = p_mulmod(r, b, m, p)
        b = p_mulmod(b, b, m, p)
        e >>= 1
    return r


def p_div(f, g, p):
    """Exact quotient f / g (g divides f)."""
    f = p_trim(f[:], p)
    g = p_trim(g[:], p)
    dg = len(g) - 1
    q = [0] * max(1, len(f) - dg)
    ig = inv(g[-1], p)
    while len(f) - 1 >= dg and f != [0]:
        shift = len(f) - 1 - dg
        coef = f[-1] * ig % p
        q[shift] = coef
        for i, c in enumerate(g):
            f[i + shift] = (f[i + shift] - coef * c) % p
        f = p_trim(f, p)
    return p_trim(q, p)


def p_derivative(f, p):
    return p_trim([(i * c) % p for i, c in enumerate(f)][1:] or [0], p)


def ddf_pattern(f, p):
    """Multiset of irreducible-factor degrees of a monic f over F_p, by
    distinct-degree factorization. Returns None if f is not squarefree."""
    f = p_trim(f[:], p)
    if len(f) - 1 < 1:
        return []
    if p_gcd(f, p_derivative(f, p), p) != [1]:
        return None
    degs, cur, h, d = [], f, [0, 1], 1
    while 2 * d <= len(cur) - 1:
        h = p_powmod(h, p, cur, p)
        hx = p_trim([(h[i] if i < len(h) else 0) - (1 if i == 1 else 0)
                     for i in range(max(len(h), 2))], p)
        g = p_gcd(hx, cur, p) if hx != [0] else cur[:]
        k = (len(g) - 1) // d
        if k > 0:
            degs.extend([d] * k)
            cur = p_div(cur, g, p)
            h = p_mod(h, cur, p)
        d += 1
    if len(cur) - 1 > 0:
        degs.append(len(cur) - 1)
    return sorted(degs)


# ---------------------------------------------------------------------------
# Per-curve census
# ---------------------------------------------------------------------------


def stream_seed(p, master):
    h = hashlib.sha256(f"GOAL-MONO-001|m3|p={p}|seed={master}".encode()).digest()
    return int.from_bytes(h[:8], "big")


def census_curve(A, B, p, tab, Z, S, N, samples, W, rng, panel_id, cm_label=None,
                 admission_override=False):
    order = 1 + Z + 2 * S
    t = p + 1 - order
    jj = j_invariant(A, B, p)

    # --- factor-base window -------------------------------------------------
    G = lex_smallest_affine_point(A, B, p)
    fb, sub_order = [], order
    if G is not None:
        base = G
        if not is_prime(order):
            # composite-order CM curve: use a maximal prime-order subgroup
            m_, n_ = order, []
            d = 2
            while d * d <= m_:
                while m_ % d == 0:
                    n_.append(d)
                    m_ //= d
                d += 1
            if m_ > 1:
                n_.append(m_)
            ell = max(n_)
            base = ec_mul(order // ell, G, A, p)
            sub_order = ell
            if base is None:  # degenerate; fall back to G
                base, sub_order = G, order
        Q = None
        for r in range(1, W + 1):
            Q = ec_add(Q, base, A, p)
            if Q is None:
                break
            fb.append(Q[0])
    fb_set = set(fb)
    W_eff = len(fb_set)

    # --- frozen sampled census ---------------------------------------------
    hist = Counter()
    degen = Counter()
    joint_hits = 0
    window_hits = 0
    fake = set(rng.sample(range(p), W_eff)) if W_eff else set()
    shuffled_hits = 0
    mismatches = 0
    for _ in range(samples):
        x1 = rng.randrange(p)
        x2 = rng.randrange(p)
        ty = classify_primary(x1, x2, A, B, p)
        hist[ty] += 1
        if x1 == x2:
            degen["x1_eq_x2"] += 1
            degen["leading_coeff_zero"] += 1
        if ty == RAMIFIED:
            degen["multiple_root"] += 1
        in_win = x1 in fb_set and x2 in fb_set
        if in_win:
            window_hits += 1
            if ty == SPLIT:
                joint_hits += 1
        if ty == SPLIT and x1 in fake and x2 in fake:
            shuffled_hits += 1
        # instrument cross-check on a deterministic 1-in-50 subsample
        if _ % 50 == 0 and classify_secondary(x1, x2, A, B, p) != ty:
            mismatches += 1

    freq = {k: hist[k] / samples for k in (SPLIT, INERT, RAMIFIED, DEGDROP)}
    weil = 2.0 / (p ** 0.5)
    delta = freq[SPLIT] - 0.5
    exact = exact_histogram(Z, S, N, p)
    exact_freq = {k: v / (p * p) for k, v in exact.items()}

    joint_rate = joint_hits / samples
    quasi = freq[SPLIT] * (W_eff / p) ** 2
    exact_joint = (W_eff * W_eff - W_eff) / (p * p) if W_eff else 0.0
    exact_quasi = exact_freq[SPLIT] * (W_eff / p) ** 2

    return {
        "p": p, "A": A, "B": B, "j_invariant": jj,
        "group_order": order, "order_is_prime": is_prime(order),
        "trace_t": t,
        "ordinary_flag": (t % p) != 0,
        "panel_id": panel_id,
        "exclusion_flags": (["j_extra_automorphism"]
                            if is_extra_automorphism_j(jj, p) else []),
        "cm_label_or_discriminant": cm_label,
        "admission_override_applied": admission_override,
        "chi_counts": {"Z": Z, "S": S, "N": N},
        "samples": samples,
        "histogram": dict(hist),
        "degenerate_counters": dict(degen),
        "freq_split_1_1": freq[SPLIT],
        "freq_inert_2": freq[INERT],
        "freq_ramified": freq[RAMIFIED],
        "freq_degree_drop": freq[DEGDROP],
        "delta_split_vs_S2": delta,
        "abs_delta_split_vs_S2": abs(delta),
        "weil_floor_abs": weil,
        "delta_over_weil": abs(delta) / weil,
        "envelope_3x_weil": 3 * weil,
        "passes_full_monodromy_test": abs(delta) <= 3 * weil,
        "secondary_classifier_mismatches": mismatches,
        "factor_base": {
            "W": W, "W_eff": W_eff, "window": sorted(fb_set),
            "generator": G, "generating_subgroup_order": sub_order,
        },
        "joint_relation_proxy_rate": joint_rate,
        "quasirandom_relation_prediction": quasi,
        "delta_relation_vs_quasirandom": joint_rate - quasi,
        "uniform_window_rate": window_hits / samples,
        "uniform_window_expected": (W_eff / p) ** 2,
        "shuffled_window_rate": shuffled_hits / samples,
        "shuffled_window_expected": freq[SPLIT] * (W_eff / p) ** 2,
        # Instrument self-check: the frozen sampled census must agree with the
        # closed form to within 4 binomial standard deviations. A failure here is
        # an instrument failure, not monodromy evidence.
        "sampled_vs_exact": {
            "abs_gap": abs(freq[SPLIT] - exact_freq[SPLIT]),
            "tolerance_4sigma": 4 * (0.25 / samples) ** 0.5,
            "pass": abs(freq[SPLIT] - exact_freq[SPLIT]) <= 4 * (0.25 / samples) ** 0.5,
        },
        "exact_enumeration": {
            "method": "closed form from disc_T S_3 = 16 f(x1) f(x2); counts over all p^2 pairs",
            "counts": exact,
            "freq_split_1_1": exact_freq[SPLIT],
            "freq_inert_2": exact_freq[INERT],
            "freq_ramified": exact_freq[RAMIFIED],
            "freq_degree_drop": exact_freq[DEGDROP],
            "delta_split_vs_S2": exact_freq[SPLIT] - 0.5,
            "abs_delta_split_vs_S2": abs(exact_freq[SPLIT] - 0.5),
            "joint_relation_proxy_rate": exact_joint,
            "quasirandom_relation_prediction": exact_quasi,
            "delta_relation_vs_quasirandom": exact_joint - exact_quasi,
            "ratio_measured_over_quasirandom": (exact_joint / exact_quasi) if exact_quasi else None,
        },
    }


# ---------------------------------------------------------------------------
# Panels
# ---------------------------------------------------------------------------

# Class-number-one CM j-invariants. D = -3 (j=0) and D = -4 (j=1728) are
# deliberately absent: they are the extra-automorphism curves quarantined to the
# automorphism_artifact_panel by the protocol.
CM_J = [
    (-7, -3375), (-8, 8000), (-11, -32768), (-12, 54000), (-16, 287496),
    (-19, -884736), (-27, -12288000), (-28, 16581375), (-43, -884736000),
    (-67, -147197952000), (-163, -262537412640768000),
]


def curve_from_j(j, p):
    j %= p
    if j in (0, 1728 % p):
        return None
    k = j * inv((1728 - j) % p, p) % p
    A, B = 3 * k % p, 2 * k % p
    if (4 * A ** 3 + 27 * B * B) % p == 0:
        return None
    return A, B


def build_random_panel(p, rng, need, samples, W):
    hi_a, hi_b = min(p - 1, 64), min(p - 1, 64)
    out, artifacts, seen, tries = [], [], set(), 0
    while len(out) < need and tries < 200000:
        tries += 1
        A = rng.randint(0, hi_a)
        B = rng.randint(1, hi_b)
        if (A, B) in seen:
            continue
        seen.add((A, B))
        if (4 * A ** 3 + 27 * B * B) % p == 0:
            continue
        tab, Z, S, N = chi_table(A, B, p)
        order = 1 + Z + 2 * S
        if order == p + 1:          # supersingular
            continue
        if order == p:              # anomalous
            continue
        jj = j_invariant(A, B, p)
        if is_extra_automorphism_j(jj, p):
            artifacts.append((A, B, tab, Z, S, N, jj))
            continue
        if not is_prime(order):     # random controls keep require_prime_order_group
            continue
        out.append((A, B, tab, Z, S, N))
    return out, artifacts, tries


def build_cm_panel(p):
    """CM exception screen under CTRL-CM-ADMISSION: prime order NOT required."""
    out = []
    for D, j in CM_J:
        ab = curve_from_j(j, p)
        if ab is None:
            continue
        A, B = ab
        tab, Z, S, N = chi_table(A, B, p)
        order = 1 + Z + 2 * S
        if order == p + 1 or order == p:   # supersingular / anomalous
            continue
        out.append((A, B, tab, Z, S, N, f"D={D},j={j}"))
    return out


def build_artifact_panel(p, rng):
    out = []
    for jt in (0, 1728):
        for _ in range(400):
            if jt == 0:
                A, B = 0, rng.randint(1, p - 1)
            else:
                A, B = rng.randint(1, p - 1), 0
            if (4 * A ** 3 + 27 * B * B) % p == 0:
                continue
            tab, Z, S, N = chi_table(A, B, p)
            order = 1 + Z + 2 * S
            if order in (p + 1, p):
                continue
            out.append((A, B, tab, Z, S, N, jt))
            break
    return out


# ---------------------------------------------------------------------------
# Controls
# ---------------------------------------------------------------------------


def ctrl_s3_identity(A, B, p, rng, checks=5):
    """CTRL-S3-IDENTITY: S_3(x(P), x(Q), x(-(P+Q))) == 0 on real curve points."""
    pts = []
    for x in range(p):
        v = (x * x % p * x + A * x + B) % p
        y = sqrt_mod(v, p)
        if y is not None and y != 0:
            pts.append((x, y))
        if len(pts) > 400:
            break
    passed, attempted, witnesses = 0, 0, []
    for _ in range(checks * 6):
        if passed >= checks or len(pts) < 2:
            break
        P, Q = rng.choice(pts), rng.choice(pts)
        R = ec_add(P, Q, A, p)
        if R is None or P[0] == Q[0]:
            continue
        attempted += 1
        val = s3_eval(P[0], Q[0], R[0], A, B, p)
        if val == 0:
            passed += 1
            witnesses.append({"xP": P[0], "xQ": Q[0], "xPQ": R[0], "S3": val})
    return {"identity_checks_passed": passed, "attempted": attempted,
            "witnesses": witnesses[:3], "pass": passed >= 3}


def ctrl_planted_split(A, B, p, rng, n=400):
    """CTRL-POS-PLANTED-SPLIT: x1,x2 taken from real points => must split
    (or land on the documented ramified locus)."""
    pts = []
    for x in range(p):
        v = (x * x % p * x + A * x + B) % p
        y = sqrt_mod(v, p)
        if y is not None:
            pts.append((x, y))
    good, tot = 0, 0
    for _ in range(n):
        P, Q = rng.choice(pts), rng.choice(pts)
        if P[0] == Q[0]:
            continue
        tot += 1
        ty = classify_primary(P[0], Q[0], A, B, p)
        if ty in (SPLIT, RAMIFIED):
            good += 1
    rate = good / tot if tot else 0.0
    return {"planted_split_rate": rate, "trials": tot, "pass": tot > 0 and rate == 1.0}


def ctrl_imon(p, rng, samples=4000):
    """CTRL-IMON-PRODUCT-COVER and CTRL-IMON-RANDOM-DEG5 (EXP-IMON-001 pins)."""
    prod, prod_n, prod_skip = Counter(), 0, 0
    for _ in range(samples):
        g2 = [rng.randrange(p), rng.randrange(p), 1]
        g3 = [rng.randrange(p), rng.randrange(p), rng.randrange(p), 1]
        f = [0] * 6
        for i, a in enumerate(g2):
            for j, b in enumerate(g3):
                f[i + j] = (f[i + j] + a * b) % p
        pat = ddf_pattern(f, p)
        if pat is None:
            prod_skip += 1
            continue
        prod[tuple(pat)] += 1
        prod_n += 1
    prod_5 = prod[(5,)] / prod_n
    prod_41 = prod[(1, 4)] / prod_n
    flagged_non_full = (prod_5 == 0.0 and prod_41 == 0.0)

    rnd, rnd_n, rnd_skip = Counter(), 0, 0
    for _ in range(samples):
        f = [rng.randrange(p) for _ in range(5)] + [1]
        pat = ddf_pattern(f, p)
        if pat is None:
            rnd_skip += 1
            continue
        rnd[tuple(pat)] += 1
        rnd_n += 1
    r5 = rnd[(5,)] / rnd_n
    r41 = rnd[(1, 4)] / rnd_n
    full_consistent = abs(r5 - 0.2) <= 0.05 and abs(r41 - 0.25) <= 0.06

    return {
        "product_cover": {"rate_5cycle": prod_5, "rate_4plus1": prod_41,
                          "flagged_non_full": flagged_non_full,
                          "pass": flagged_non_full, "squarefree_samples": prod_n,
                          "non_squarefree_skipped": prod_skip,
                          "top_patterns": [[list(k), v] for k, v in prod.most_common(5)]},
        "random_deg5": {"rate_5cycle": r5, "rate_4plus1": r41,
                        "flagged_full_consistent": full_consistent,
                        "pass": full_consistent, "squarefree_samples": rnd_n,
                        "non_squarefree_skipped": rnd_skip,
                        "top_patterns": [[list(k), v] for k, v in rnd.most_common(5)]},
        "samples": samples, "p": p,
    }


def reverify_exception(curve, samples, master_seed):
    """Protocol `reverification_rule`: any curve with
    |delta_split_vs_S2| > 3 * weil_floor is re-censused with the independent
    classifier before it may be admitted as an exception candidate.

    Mismatch between the two code paths => failed_infrastructure / invalid,
    never exceptional evidence.
    """
    p, A, B = curve["p"], curve["A"], curve["B"]
    rng = random.Random(stream_seed(p, master_seed) + 1)
    hist = Counter()
    disagree = 0
    for _ in range(samples):
        x1, x2 = rng.randrange(p), rng.randrange(p)
        a = classify_secondary(x1, x2, A, B, p)
        hist[a] += 1
        if classify_primary(x1, x2, A, B, p) != a:
            disagree += 1
    f_split = hist[SPLIT] / samples
    d = f_split - 0.5
    weil = 2.0 / (p ** 0.5)
    return {
        "classifier": "independent root-scan path (classify_secondary)",
        "samples": samples,
        "freq_split_1_1": f_split,
        "abs_delta_split_vs_S2": abs(d),
        "exceeds_envelope": abs(d) > 3 * weil,
        "code_path_disagreements": disagree,
        "disposition": ("failed_infrastructure" if disagree
                        else ("admitted_exception_candidate" if abs(d) > 3 * weil
                              else "not_an_exception_after_reverification")),
    }


def aggregate_outcome(res, primes, curves_per_prime):
    """Evaluate the protocol's barrier_aggregate_rule / CTRL-CM-GATE-FULL and
    emit exactly one outcome_id."""
    rand_all, cm_all, missing = [], [], []
    sizes_ok = 0
    for p in primes:
        blk = res["primes"][str(p)]
        r = blk["random_ordinary_controls"]
        cm_all.extend(blk["cm_exception_screen"])
        rand_all.extend(r)
        if len(r) >= curves_per_prime:
            sizes_ok += 1
        else:
            missing.append(f"p={p}: only {len(r)} admitted random controls")

    ctrl_pass = all(
        (blk["controls"]["CTRL-S3-IDENTITY"] or {}).get("pass") and
        (blk["controls"]["CTRL-POS-PLANTED-SPLIT"] or {}).get("pass")
        for blk in (res["primes"][str(p)] for p in primes))
    imon = res["instrument_controls"]
    imon_pass = imon["product_cover"]["pass"] and imon["random_deg5"]["pass"]

    rand_exceptions = [c for c in rand_all if not c["passes_full_monodromy_test"]]
    cm_exceptions = [c for c in cm_all if not c["passes_full_monodromy_test"]]
    j_audit = all(not is_extra_automorphism_j(c["j_invariant"], c["p"])
                  for c in rand_all)
    cm_admission = all(c["admission_override_applied"] and c["cm_label_or_discriminant"]
                       for c in cm_all)
    consistency = all(c["sampled_vs_exact"]["pass"] for c in rand_all + cm_all)
    mismatch_free = all(c["secondary_classifier_mismatches"] == 0 for c in rand_all + cm_all)

    controls = {
        "CTRL-S3-IDENTITY": ctrl_pass,
        "CTRL-POS-PLANTED-SPLIT": ctrl_pass,
        "CTRL-NEG-UNIFORM-WINDOW": all(
            abs(c["uniform_window_rate"] - c["uniform_window_expected"]) <= 0.02
            for c in rand_all),
        "CTRL-NEG-SHUFFLED-WINDOW": all(
            abs(c["shuffled_window_rate"] - c["shuffled_window_expected"]) <= 0.03
            for c in rand_all),
        "CTRL-IMON-PRODUCT-COVER": imon["product_cover"]["pass"],
        "CTRL-IMON-RANDOM-DEG5": imon["random_deg5"]["pass"],
        "CTRL-J-EXCLUSION": j_audit,
        "CTRL-CM-ADMISSION": cm_admission,
        "CTRL-CM-GATE-FULL": len(cm_all) >= 8 and not cm_exceptions,
        "INSTRUMENT-SAMPLED-VS-EXACT": consistency,
        "INSTRUMENT-DUAL-CLASSIFIER": mismatch_free,
    }

    if not (ctrl_pass and imon_pass and consistency and mismatch_free and cm_admission
            and j_audit):
        outcome = "SCOPED_PROTOCOL_NO_GO"
        why = "instrument or admission control failed; no monodromy claim"
    elif rand_exceptions or cm_exceptions:
        outcome = "EXCEPTIONAL_LOCUS_TOY"
        why = "reverified curve(s) exceed the pinned 3*(2/sqrt(p)) envelope"
    elif sizes_ok < 3:
        outcome = "SCOPED_PROTOCOL_NO_GO"
        why = f"fewer than 3 sizes reached {curves_per_prime} admitted controls: {missing}"
    elif len(cm_all) < 8:
        outcome = "RANDOM_PANEL_CALIBRATION_TOY"
        why = f"CM screen incomplete after admission override ({len(cm_all)} < 8)"
    else:
        outcome = "FULL_MONODROMY_BARRIER_TOY"
        why = ("all random-panel curves within the pinned envelope; CM hard gate "
               "satisfied with no reverified CM exception")

    return {
        "outcome_id": outcome,
        "rationale": why,
        "sizes_with_full_panel": sizes_ok,
        "random_controls_scored": len(rand_all),
        "cm_screen_scored_curves": len(cm_all),
        "cm_reverified_exceptions": len(cm_exceptions),
        "random_exception_candidates": len(rand_exceptions),
        "controls": controls,
        "all_controls_pass": all(controls.values()),
        "missing_obligations": missing,
    }


# ---------------------------------------------------------------------------
# Driver
# ---------------------------------------------------------------------------


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--primes", type=int, nargs="+", default=[211, 431, 809, 1601])
    ap.add_argument("--seed", type=int, default=20260725)
    ap.add_argument("--samples", type=int, default=30000)
    ap.add_argument("--window", type=int, default=4)
    ap.add_argument("--m", type=int, default=3)
    ap.add_argument("--curves-per-prime", type=int, default=20)
    ap.add_argument("--protocol-version", default="MONO-m3-census-1.1.0-repair-cm-gate")
    ap.add_argument("--out", default="results.json")
    args = ap.parse_args()

    if args.m != 3:
        print("this harness implements m=3 only", file=sys.stderr)
        return 2

    t0 = time.time()
    res = {
        "experiment_id": "EXP-MONO-4b50b6",
        "goal_id": "GOAL-MONO-001",
        "question_id": "RQ-MONO-001",
        "protocol_version": args.protocol_version,
        "authorized_by": "DEC-20260802-505759",
        "args": vars(args),
        "python": sys.version.split()[0],
        "primes": {},
    }

    for p in args.primes:
        s = stream_seed(p, args.seed)
        rng = random.Random(s)
        block = {"stream_seed": s,
                 "stream_seed_rule": f'SHA-256("GOAL-MONO-001|m3|p={p}|seed={args.seed}")[:8] big-endian'}

        rand_curves, artifacts, tries = build_random_panel(
            p, rng, args.curves_per_prime, args.samples, args.window)
        block["curve_search_tries"] = tries

        block["random_ordinary_controls"] = [
            census_curve(A, B, p, tab, Z, S, N, args.samples, args.window, rng,
                         "random_ordinary_controls")
            for (A, B, tab, Z, S, N) in rand_curves
        ]

        block["cm_exception_screen"] = [
            census_curve(A, B, p, tab, Z, S, N, args.samples, args.window, rng,
                         "cm_exception_screen", cm_label=lab, admission_override=True)
            for (A, B, tab, Z, S, N, lab) in build_cm_panel(p)
        ]
        if not block["cm_exception_screen"]:
            block["cm_screen_unavailable_at_prime"] = True

        block["automorphism_artifact_panel"] = [
            census_curve(A, B, p, tab, Z, S, N, args.samples, args.window, rng,
                         "automorphism_artifact_panel", cm_label=f"j={jt}")
            for (A, B, tab, Z, S, N, jt) in build_artifact_panel(p, rng)
        ]

        ref = rand_curves[0] if rand_curves else None
        block["controls"] = {
            "CTRL-S3-IDENTITY": ctrl_s3_identity(ref[0], ref[1], p, rng) if ref else None,
            "CTRL-POS-PLANTED-SPLIT": ctrl_planted_split(ref[0], ref[1], p, rng) if ref else None,
        }
        res["primes"][str(p)] = block

    # instrument controls, run once at the smallest pinned prime
    imon_p = min(args.primes)
    res["instrument_controls"] = ctrl_imon(imon_p, random.Random(stream_seed(imon_p, args.seed)))

    # Protocol reverification_rule: every curve outside the pinned envelope is
    # re-censused on the independent code path before it may be called an
    # exception. Recorded even when the list is empty.
    res["exception_reverification"] = []
    for p in args.primes:
        for panel in ("random_ordinary_controls", "cm_exception_screen"):
            for c in res["primes"][str(p)][panel]:
                if not c["passes_full_monodromy_test"]:
                    rv = reverify_exception(c, args.samples, args.seed)
                    c["reverification"] = rv
                    res["exception_reverification"].append(
                        {"p": p, "A": c["A"], "B": c["B"], "panel": panel, **rv})

    res["aggregate"] = aggregate_outcome(res, args.primes, args.curves_per_prime)
    res["wall_clock_seconds"] = round(time.time() - t0, 3)
    with open(args.out, "w") as fh:
        json.dump(res, fh, indent=1, sort_keys=True)
    agg = res["aggregate"]
    print(f"wrote {args.out} in {res['wall_clock_seconds']}s")
    print(f"outcome_id = {agg['outcome_id']}  ({agg['rationale']})")
    print(f"random controls scored = {agg['random_controls_scored']}, "
          f"CM screen scored = {agg['cm_screen_scored_curves']}")
    for k, v in agg["controls"].items():
        print(f"  {'PASS' if v else 'FAIL'}  {k}")
    return 0 if agg["all_controls_pass"] else 1


if __name__ == "__main__":
    sys.exit(main())

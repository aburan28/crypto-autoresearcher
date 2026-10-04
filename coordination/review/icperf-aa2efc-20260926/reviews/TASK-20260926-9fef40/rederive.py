#!/usr/bin/env python3
"""Blind re-derivation for TASK-20260926-9fef40.

Self-contained and deterministic. Works only from the parameters and quantity
statements given in the handoff; reads no repository file.

Precision: mpmath at 60 decimal digits for the real-l optimisation and all
logarithms; exact Python integers / fractions.Fraction for every quantity that
is exactly computable (integer-l minima, binomial ratios, point counts, the
Frobenius-trace recurrence, Miller-Rabin).

Binomial convention for real x: C(x, m) = x (x-1) ... (x-m+1) / m!  (falling
factorial).  For integer x >= m this coincides with math.comb.

Domain note for Q1: with x = 2^(l-s), the falling-factorial C(x, m) is zero at
x in {0, 1, ..., m-1} and negative on some sub-intervals below m-1, so the
objective is undefined / unbounded below there.  We therefore minimise over
l >= max(1, s + log2(m-1)) + epsilon, i.e. x > m-1, where C(x, m) > 0 and the
objective is finite.  The optimum found is orders of magnitude inside that
domain (x ~ N^(1/(m+1))), so the restriction never binds.
"""

import math
import random
from fractions import Fraction

import mpmath as mp

mp.mp.dps = 60

R_PARAM = 680564733841876926932320129493409985129
N_FIELD = 131
M_LIST = [2, 3, 4, 5, 6, 8]
SETTINGS = [("4r,0", 4 * R_PARAM, 0), ("r,2", R_PARAM, 2)]

LOG2 = mp.log(2)


def log2(x):
    return mp.log(x) / LOG2


def fmt(x, nd=4):
    return mp.nstr(mp.mpf(x), nd + 8, min_fixed=-100, max_fixed=100) if False else f"{float(x):.{nd}f}"


def ffact_binom_mp(x, m):
    """C(x, m) for real x (mpf), falling-factorial form."""
    num = mp.mpf(1)
    for i in range(m):
        num *= (x - i)
    return num / mp.factorial(m)


def ffact_binom_frac(x, m):
    """C(x, m) for rational x (Fraction), falling-factorial form (exact)."""
    num = Fraction(1)
    for i in range(m):
        num *= (x - i)
    return num / math.factorial(m)


def objective_terms_mp(l, m, N, s):
    x = mp.power(2, l - s)
    t1 = x * N / ffact_binom_mp(x, m)
    t2 = m * x * x
    return t1, t2


def objective_mp(l, m, N, s):
    t1, t2 = objective_terms_mp(l, m, N, s)
    return t1 + t2


def golden_section_min(f, lo, hi, iters=260):
    """Golden-section search for the minimiser of a unimodal f on [lo, hi]."""
    lo = mp.mpf(lo)
    hi = mp.mpf(hi)
    invphi = (mp.sqrt(5) - 1) / 2
    a, b = lo, hi
    c = b - invphi * (b - a)
    d = a + invphi * (b - a)
    fc, fd = f(c), f(d)
    for _ in range(iters):
        if fc < fd:
            b, d, fd = d, c, fc
            c = b - invphi * (b - a)
            fc = f(c)
        else:
            a, c, fc = c, d, fd
            d = a + invphi * (b - a)
            fd = f(d)
    return (a + b) / 2


def q1_real(m, N, s):
    # domain: x = 2^(l-s) > m-1  and l >= 1
    lo = max(mp.mpf(1), s + log2(m - 1) if m > 1 else mp.mpf(0)) + mp.mpf("1e-9")
    hi = mp.mpf(400)
    f = lambda l: objective_mp(l, m, N, s)
    lstar = golden_section_min(f, lo, hi)
    # polish: zero of d/dl objective via secant on the numerical derivative
    df = lambda l: mp.diff(f, l)
    try:
        lpol = mp.findroot(df, lstar)
        if lo < lpol < hi and f(lpol) <= f(lstar):
            lstar = lpol
    except Exception:
        pass
    t1, t2 = objective_terms_mp(lstar, m, N, s)
    # sanity: derivative sign change around lstar
    dl = mp.mpf("1e-6")
    assert f(lstar - dl) >= f(lstar) <= f(lstar + dl), "not a local minimum"
    return lstar, t1, t2, t1 + t2


def q1_integer(m, N, s):
    best = None
    for l in range(1, 401):
        x = Fraction(2 ** l, 2 ** s)
        c = ffact_binom_frac(x, m)
        if c <= 0:
            continue  # outside domain (C(x,m) <= 0)
        t1 = x * N / c
        t2 = m * x * x
        F = t1 + t2
        if best is None or F < best[3]:
            best = (l, t1, t2, F)
    return best


def frac_log2(q):
    q = Fraction(q)
    return log2(mp.mpf(q.numerator) / mp.mpf(q.denominator))


def main():
    out = []
    P = out.append

    # ---------------- Q3 first (needed by Q2) ----------------
    R_val = mp.sqrt(mp.pi * R_PARAM / (4 * N_FIELD))
    log2R = log2(R_val)
    log2r = log2(mp.mpf(R_PARAM))

    P("Q3:")
    P(f"  r_minus_2_pow_129: {R_PARAM - 2**129}")
    P(f"  log2_r_bits: {fmt(log2r)}")
    P(f"  log2_R_bits: {fmt(log2R)}")
    P(f"  R_value: {mp.nstr(R_val, 25)}")

    # ---------------- Q1 / Q2 ----------------
    P("Q1:")
    q1_store = {}
    for label, N, s in SETTINGS:
        P(f"  '({label})':")
        for m in M_LIST:
            lstar, t1, t2, F = q1_real(m, N, s)
            il, it1, it2, iF = q1_integer(m, N, s)
            q1_store[(label, m)] = (lstar, t1, t2, F)
            P(f"    m{m}:")
            P(f"      real_l:")
            P(f"        l_star: {mp.nstr(lstar, 12)}")
            P(f"        log2_x_star: {mp.nstr(lstar - s, 12)}")
            P(f"        term1_log2: {fmt(log2(t1))}")
            P(f"        term2_log2: {fmt(log2(t2))}")
            P(f"        log2_F: {fmt(log2(F))}")
            P(f"      integer_l:")
            P(f"        l_int: {il}")
            P(f"        term1_log2: {fmt(frac_log2(it1))}")
            P(f"        term2_log2: {fmt(frac_log2(it2))}")
            P(f"        log2_F: {fmt(frac_log2(iF))}")
    P("Q2:")
    for label, N, s in SETTINGS:
        P(f"  '({label})':")
        for m in M_LIST:
            lstar, t1, t2, F = q1_store[(label, m)]
            log2T = log2(t1)
            P(f"    m{m}:")
            P(f"      log2_T: {fmt(log2T)}")
            P(f"      B_bits: {fmt(log2R - log2T)}")

    # ---------------- Q4 ----------------
    P("Q4:")
    label, N, s = SETTINGS[0]
    for m in M_LIST:
        lstar = q1_store[(label, m)][0]
        lint = int(mp.nint(lstar))
        x = 2 ** lint
        exact = Fraction(math.comb(x, m - 1), math.comb(x, m))
        closed = Fraction(m, x - m + 1)
        assert exact == closed
        naive = Fraction(m, x)
        ratio = exact / naive  # = 2^l / (2^l - m + 1)
        P(f"  m{m}:")
        P(f"    l_int_nearest_lstar: {lint}")
        P(f"    exact_ratio_closed_form: m/(2^l-m+1) = {m}/{x - m + 1}")
        P(f"    exact_ratio_log2: {fmt(frac_log2(exact))}")
        P(f"    m_over_2l_log2: {fmt(frac_log2(naive))}")
        P(f"    ratio_of_the_two: {mp.nstr(mp.mpf(ratio.numerator) / mp.mpf(ratio.denominator), 30)}")
        P(f"    ratio_minus_1: {mp.nstr(mp.mpf(ratio.numerator - ratio.denominator) / mp.mpf(ratio.denominator), 8)}")

    # ---------------- Q5 ----------------
    P("Q5:")
    a, b = 0, 1
    pts = []
    for x in (0, 1):
        for y in (0, 1):
            lhs = (y * y + x * y) % 2
            rhs = (x ** 3 + a * x * x + b) % 2
            if lhs == rhs:
                pts.append((x, y))
    n1 = len(pts) + 1  # + point at infinity
    t = 2 + 1 - n1
    P(f"  affine_points_F2: {pts}")
    P(f"  E_F2_order: {n1}")
    P(f"  trace_t: {t}")
    s_prev, s_cur = 2, t
    for _ in range(2, N_FIELD + 1):
        s_prev, s_cur = s_cur, t * s_cur - 2 * s_prev
    s131 = s_cur
    order131 = 2 ** N_FIELD + 1 - s131
    P(f"  s_131: {s131}")
    P(f"  E_F2_131_order: {order131}")
    P(f"  four_r: {4 * R_PARAM}")
    P(f"  order_equals_4r: {order131 == 4 * R_PARAM}")
    P(f"  order_div_4: {order131 // 4}")
    P(f"  order_mod_4: {order131 % 4}")
    # Hasse check: |s_131| <= 2*sqrt(2^131)
    P(f"  hasse_bound_ok: {abs(s131) ** 2 <= 4 * 2 ** N_FIELD}")

    # primality of r
    def small_primes(limit):
        sieve = bytearray([1]) * (limit + 1)
        sieve[0] = sieve[1] = 0
        for i in range(2, int(limit ** 0.5) + 1):
            if sieve[i]:
                sieve[i * i :: i] = bytearray(len(sieve[i * i :: i]))
        return [i for i in range(limit + 1) if sieve[i]]

    sp = small_primes(10000)
    trial_ok = all(R_PARAM % p != 0 for p in sp)

    def mr_witness(n, a):
        d, k = n - 1, 0
        while d % 2 == 0:
            d //= 2
            k += 1
        y = pow(a, d, n)
        if y in (1, n - 1):
            return False
        for _ in range(k - 1):
            y = y * y % n
            if y == n - 1:
                return False
        return True

    rng = random.Random(20260926)
    bases = sp[:25] + [rng.randrange(2, R_PARAM - 2) for _ in range(40)]
    witnesses = [a for a in bases if mr_witness(R_PARAM, a)]
    P(f"  trial_division_to_10000_no_factor: {trial_ok}")
    P(f"  miller_rabin_bases: {len(bases)} (25 smallest primes + 40 random, seed 20260926)")
    P(f"  miller_rabin_witnesses_found: {len(witnesses)}")
    P(f"  r_probable_prime: {trial_ok and not witnesses}")

    print("\n".join(out))


if __name__ == "__main__":
    main()

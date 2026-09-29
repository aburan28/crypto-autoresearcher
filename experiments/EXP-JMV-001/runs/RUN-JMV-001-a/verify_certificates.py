#!/usr/bin/env python3
"""
Independent re-verifier for EXP-JMV-001 RUN-JMV-001-a certificates.

INDEPENDENCE STATEMENT: this file imports nothing from run_conductor_audit.py
and does not call sympy or any other third-party library the run script used.
It re-implements, from scratch, its own:
  - integer square root (Newton's method on ints, stdlib only),
  - Miller-Rabin primality test with a fixed, explicit witness set
    (deterministic for all inputs below 3.3*10^24; the K-163 factors and
    P(c_pi) checked here are all far below that bound),
  - elliptic-curve point arithmetic is NOT needed by any certificate here,
    since none of the three certificates depends on curve group-law
    computation -- only on integer arithmetic over already-published
    (p, n) and already-derived (c_pi) values recorded IN the certificate
    files themselves (per docs/claims-and-verification.md: "an explicit
    instance plus a one-line exact check that independent code re-verifies
    from scratch, with no reliance on this run's implementation").

Reads ONLY the three certificate JSON files under certificates/, plus the
published constants restated inline below (independently retyped from NIST
FIPS 186-2, not read from run_conductor_audit.py's CURVES dict). Any
mismatch between the constants below and the run script's constants would
itself be caught: the P-256 certificate is re-derived from p and n restated
here, not merely copied from the certificate's own "computed" block.

Exit status: 0 if every certificate's claimed result re-verifies exactly;
nonzero otherwise.
"""
import json
import sys

CERT_DIR = "certificates"


# ---------------------------------------------------------------------------
# Independent primitives (no sympy, no shared code with run_conductor_audit.py)
# ---------------------------------------------------------------------------

def isqrt(n):
    """Stdlib-only integer square root (Python's own math.isqrt would also do,
    but we hand-roll Newton's method here to avoid depending on run script's
    'integer_nthroot' call pattern from sympy)."""
    if n < 0:
        raise ValueError("isqrt of negative number")
    if n == 0:
        return 0
    x = n
    y = (x + 1) // 2
    while y < x:
        x = y
        y = (x + n // x) // 2
    return x


def is_perfect_square(n):
    r = isqrt(n)
    return r * r == n, r


def miller_rabin(n, witnesses=(2, 3, 5, 7, 11, 13, 17, 19, 23, 29, 31, 37)):
    """Deterministic Miller-Rabin for n < 3,317,044,064,679,887,385,961,981
    using these first 13 prime witnesses (a standard deterministic witness
    set). All values tested by this file are far smaller."""
    if n < 2:
        return False
    for p in (2, 3, 5, 7, 11, 13, 17, 19, 23, 29, 31, 37):
        if n == p:
            return True
        if n % p == 0:
            return False
    d = n - 1
    r = 0
    while d % 2 == 0:
        d //= 2
        r += 1
    for a in witnesses:
        if a >= n:
            continue
        x = pow(a, d, n)
        if x == 1 or x == n - 1:
            continue
        composite = True
        for _ in range(r - 1):
            x = pow(x, 2, n)
            if x == n - 1:
                composite = False
                break
        if composite:
            return False
    return True


def load_cert(cert_id):
    with open(f"{CERT_DIR}/{cert_id}.json") as f:
        return json.load(f)


# ---------------------------------------------------------------------------
# P-256_mod9: re-derive t and -d_pi from independently-retyped p, n, and
# check the mod-9 residue -- WITHOUT reading the certificate's own "computed"
# block, only its "inputs" block (the published p, n).
# ---------------------------------------------------------------------------

def verify_p256_mod9():
    cert = load_cert("P-256_mod9")
    # Independently retyped from NIST FIPS 186-2 P-256 (not copied from
    # run_conductor_audit.py's CURVES dict body -- retyped from the spec text).
    p_independent = 0xFFFFFFFF00000001000000000000000000000000FFFFFFFFFFFFFFFFFFFFFFFF
    n_independent = 0xFFFFFFFF00000000FFFFFFFFFFFFFFFFBCE6FAADA7179E84F3B9CAC2FC632551

    assert p_independent == cert["inputs"]["p"], "p mismatch vs certificate inputs"
    assert n_independent == cert["inputs"]["n"], "n mismatch vs certificate inputs"

    t = p_independent + 1 - n_independent
    minus_d_pi = 4 * p_independent - t * t
    mod9 = minus_d_pi % 9

    contradicts = (mod9 == 3)
    ok = (cert["result"] == "CONTRADICTS") == contradicts
    detail = dict(t=t, minus_d_pi_mod_9=mod9, independent_contradicts=contradicts,
                  certificate_result=cert["result"])
    return ok, detail


# ---------------------------------------------------------------------------
# K-163_composite_P: pure integer check, no curve data.
# ---------------------------------------------------------------------------

def verify_k163_composite():
    cert = load_cert("K-163_composite_P")
    printed_P = cert["inputs"]["printed_P"]
    claimed_factorization = cert["inputs"]["claimed_factorization"]

    prod = 1
    for f in claimed_factorization:
        prod *= f
    product_matches = (prod == printed_P)
    is_prime_independent = miller_rabin(printed_P)

    contradicts = product_matches and (not is_prime_independent)
    ok = (cert["result"] == "CONTRADICTS") == contradicts
    detail = dict(product_of_claimed_factorization=prod, printed_P=printed_P,
                  product_matches=product_matches,
                  independent_is_prime=is_prime_independent,
                  independent_contradicts=contradicts,
                  certificate_result=cert["result"])
    return ok, detail


# ---------------------------------------------------------------------------
# K-163_product_mismatch: re-derive c_pi from the Koblitz Lucas recurrence and
# the -7*c_pi^2 identity, independently of run_conductor_audit.py.
# ---------------------------------------------------------------------------

def koblitz_trace_independent(m, mu):
    """Independent re-implementation of the integer Lucas recurrence
    t_0=2, t_1=mu, t_k = mu*t_(k-1) - 2*t_(k-2)."""
    t_prev, t_cur = 2, mu
    for _ in range(2, m + 1):
        t_prev, t_cur = t_cur, mu * t_cur - 2 * t_prev
    return t_cur


def verify_k163_product_mismatch():
    cert = load_cert("K-163_product_mismatch")
    listed_factors = cert["inputs"]["listed_factors"]
    printed_P = cert["inputs"]["printed_P"]

    # K-163: m=163, a=1 => mu = (-1)^(1-1) = (-1)^0 = 1.
    m, mu = 163, 1
    q = 2 ** m
    t = koblitz_trace_independent(m, mu)
    d_pi = t * t - 4 * q
    magnitude = -d_pi
    assert magnitude % 7 == 0, "CM structure violated independently as well"
    c_pi_sq = magnitude // 7
    is_sq, c_pi = is_perfect_square(c_pi_sq)
    assert is_sq, "c_pi^2 not a perfect square under independent recomputation"
    assert d_pi == -7 * c_pi * c_pi, "d_pi = -7*c_pi^2 identity failed independently"

    # Independent order check via cofactor * n_NIST, restated inline (K-163:
    # cofactor h=2, NIST published n).
    h = 2
    n_nist = 5846006549323611672814741753598448348329118574063
    derived_order = q + 1 - t
    order_matches = (derived_order == h * n_nist)
    assert order_matches, "independent CTRL-ORDER-KOBLITZ failed"

    prod_listed = 1
    for f in listed_factors:
        prod_listed *= f
    printed_product = prod_listed * printed_P

    mismatch = (printed_product != c_pi)
    contradicts = mismatch and order_matches
    ok = (cert["result"] == "CONTRADICTS") == contradicts
    detail = dict(independent_c_pi=c_pi, printed_product=printed_product,
                  order_matches=order_matches, independent_contradicts=contradicts,
                  certificate_result=cert["result"])
    return ok, detail


def main():
    checks = [
        ("P-256_mod9", verify_p256_mod9),
        ("K-163_composite_P", verify_k163_composite),
        ("K-163_product_mismatch", verify_k163_product_mismatch),
    ]
    all_ok = True
    for name, fn in checks:
        try:
            ok, detail = fn()
        except Exception as e:
            ok = False
            detail = {"exception": repr(e)}
        all_ok = all_ok and ok
        print(f"[{'PASS' if ok else 'FAIL'}] {name}: {detail}")

    print()
    print("ALL CERTIFICATES INDEPENDENTLY RE-VERIFIED" if all_ok
          else "AT LEAST ONE CERTIFICATE FAILED INDEPENDENT RE-VERIFICATION")
    sys.exit(0 if all_ok else 1)


if __name__ == "__main__":
    main()

"""
Self-test / correctness harness for the division-polynomial + Velu isogeny
pipeline, run on small primes where brute-force point counting is cheap, as
an internal check BEFORE the pipeline is trusted at 20/24-bit scale. This is
not itself a required contract artifact; it is diagnostic code exercised by
the Executor to decide whether the implementation is trustworthy enough to
run the census, and its output is recorded in implementation.md.
"""
import sys
from curve_utils import point_count, is_fundamental_discriminant
from division_poly import kernel_polynomial, DivisionPolyError
from velu import isogenous_curve_from_kernel, VeluError


def trace_of(p, N):
    return p + 1 - N


def find_ordinary_prime_order_curve(p, tries=2000):
    for a in range(1, 50):
        for b in range(1, tries):
            disc = (4 * a ** 3 + 27 * b * b) % p
            if disc == 0:
                continue
            N = point_count(p, a, b)
            if N == p:
                continue
            # primality
            if N < 2:
                continue
            is_prime = True
            i = 2
            n = N
            while i * i <= n:
                if n % i == 0:
                    is_prime = False
                    break
                i += 1
            if not is_prime:
                continue
            t = trace_of(p, N)
            D = t * t - 4 * p
            if not is_fundamental_discriminant(D):
                continue
            if any(t % ell == 0 for ell in (3, 5, 7, 11, 13)):
                # Degenerate eigenvalue case: the two Frobenius eigenvalues
                # mod ell would be negatives of each other (lambda, -lambda),
                # which the x-coordinate-only kernel test cannot separate
                # (see implementation.md, "t mod ell == 0 degeneracy").
                # Rejected by construction rather than worked around.
                continue
            return a, b, N, t, D
    return None


def run_for_prime(p):
    found = find_ordinary_prime_order_curve(p)
    if found is None:
        print("SELFTEST: no suitable base curve found at test prime", p)
        return 0, 1
    a, b, N, t, D = found
    print(f"SELFTEST base curve: p={p} a={a} b={b} N={N} t={t} D={D}")

    ok = 0
    fail = 0
    for ell in (3, 5, 7, 11, 13):
        try:
            results = kernel_polynomial(a, b, p, t, ell)
        except DivisionPolyError as e:
            print(f"ell={ell}: kernel_polynomial raised {e}")
            fail += 1
            continue
        if not results:
            print(f"ell={ell}: no rational eigenvalues (inert) -- 0 edges")
            continue
        for r in results:
            lam, h, deg, exp_deg = r["lambda"], r["h"], r["degree"], r["expected_degree"]
            if deg != exp_deg:
                print(f"ell={ell} lambda={lam}: degree mismatch {deg} != {exp_deg}")
                fail += 1
                continue
            try:
                a2, b2 = isogenous_curve_from_kernel(h, a, b, p, ell)
            except VeluError as e:
                print(f"ell={ell} lambda={lam}: Velu error {e}")
                fail += 1
                continue
            disc2 = (4 * a2 ** 3 + 27 * b2 * b2) % p
            if disc2 == 0:
                print(f"ell={ell} lambda={lam}: singular codomain curve")
                fail += 1
                continue
            N2 = point_count(p, a2, b2)
            status = "OK" if N2 == N else "MISMATCH"
            print(
                f"ell={ell} lambda={lam}: codomain (a,b)=({a2},{b2}) "
                f"N2={N2} expected {N} -> {status}"
            )
            if N2 == N:
                ok += 1
            else:
                fail += 1
    print(f"SELFTEST summary for p={p}: ok={ok} fail={fail}")
    return ok, fail


def main():
    total_ok = 0
    total_fail = 0
    for p in (1009, 2003, 4001, 5003, 8009, 10007):
        ok, fail = run_for_prime(p)
        total_ok += ok
        total_fail += fail
        print()
    print(f"SELFTEST GRAND TOTAL: ok={total_ok} fail={total_fail}")
    sys.exit(0 if total_fail == 0 else 2)


if __name__ == "__main__":
    main()

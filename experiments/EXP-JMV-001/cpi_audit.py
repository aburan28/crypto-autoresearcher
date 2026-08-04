#!/usr/bin/env python3
"""EXP-JMV-001 scouting script - conductor audit of JMV (arXiv:math/0411378v3) Figure 1.

STATUS: SCOUTING, NOT A RUN. This produced the observation recorded in
research/JMV2005_experiment_suite_20260726.md Sec. 2. It is not an approved
experiment run and emits no run record. The approved EXP-JMV-001 must extend it
to the full Figure 1 curve set (including the Koblitz K-curves, whose
d_pi = -7*c_pi^2 identity is the pipeline's positive control) and must record
censored factorizations explicitly.

CORRECTED DEFINITION OF c_pi (this script previously had it wrong).
  c_pi is the CONDUCTOR of Z[pi]: d_pi = c_pi^2 * d_K with d_K the FUNDAMENTAL
  discriminant. It is NOT simply "the largest integer whose square divides d_pi".
  Writing d_pi = s^2 * u with u squarefree:
      u = 1 (mod 4)  ->  d_K = u,   c_pi = s
      otherwise      ->  d_K = 4u,  c_pi = s/2
  The second case forces s even, since a discriminant is 0 or 1 mod 4.

  WHEN THE CORRECTION BITES: only when 4 | d_pi. For a prime-field curve of odd
  prime order n WITH COFACTOR 1 (true of the five NIST prime curves, not of
  prime-field curves generally), p is odd so p+1 is even and t = p+1-n is ODD,
  hence d_pi = t^2-4q is odd, s is odd, u = 1 (mod 4), and c_pi = s exactly.
  It does not bite on the Koblitz rows either, but for a different reason:
  there d_K = -7 = 1 (mod 4) is ALREADY fundamental, so c_pi = sqrt(-d_pi/7)
  exactly whatever the parity of t. (An earlier version of this note claimed the
  correction did affect the Koblitz rows. It does not.)

  The script reports t's parity and nu_2(d_pi) so this is visible per row rather
  than assumed.

KOBLITZ POSITIVE CONTROL - and why NO binary-field arithmetic is required.
  An earlier version of this note said the K-* rows needed F_2^m arithmetic and
  that omitting them cost the pipeline its positive control. That was wrong.
  Everything needed is pure integer arithmetic:

  For the Koblitz curve E_a: y^2+xy = x^3+ax^2+1 over F_2, with mu = (-1)^(1-a),
  Frobenius tau satisfies tau^2 - mu*tau + 2 = 0, so disc(Z[tau]) = mu^2-8 = -7
  and the CM field is Q(sqrt(-7)). The trace over F_2^m obeys a Lucas recurrence
  in the INTEGERS:
        t_0 = 2,  t_1 = mu,  t_k = mu*t_(k-1) - 2*t_(k-2)
        #E_a(F_2^m) = 2^m + 1 - t_m
  This DERIVES the group order from theory instead of trusting a published n -
  a strictly stronger control than checking [n]G = O, which only confirms that a
  published n is consistent with a published G. Both are then available: the
  derived order is compared against cofactor * n_NIST.

  The positive control d_pi = -7*c_pi^2 is likewise pure integer arithmetic, and
  c_pi = sqrt(-d_pi/7) is exactly computable (81-285 bits here).

  WHAT MAKES THE K-ROWS CHECKABLE - and a claim this file previously got wrong.
  It is NOT that "c_pi is small enough to factor": K-409 leaves a 96-bit residual
  after its listed factors and K-571 a 263-bit one, and 263 bits is not routinely
  factorable. The real reason is that VERIFYING A COMPLETE CLAIMED FACTORIZATION
  NEEDS NO FACTORING AT ALL - only multiplication and primality tests. K-163/233/
  283 carry a complete claimed factorization in the paste and are fully checkable.
  K-409/K-571 do not (their P(c_pi) values are line-wrapped into unusability) and
  are reported CENSORED, level counts included.

  Checking a claimed factorization means all THREE of: the product equals c_pi,
  every listed factor is prime, and P(c_pi) is the largest of them. A product
  identity alone is not reproduction - Figure 1's P(c_pi) column claims
  maximality, and the K-163 row satisfies neither primality nor the product.

What is computed, and what is rigorous:
  t     = q + 1 - n                       (exact)
  d_pi  = t^2 - 4q                        (exact)
  nu_l(d_pi) for l <= B by trial division (exact, no factoring needed)
  the odd-square part below B, which divides c_pi when 4 does not divide d_pi

The mod-9 test below is EXACT and needs no factorization: if -d_pi = 3 (mod 9)
then 3 exactly divides -d_pi, so 9 does not divide d_pi, so 3 does not divide
c_pi. Figure 1 reports c_pi = 3 for P-256, which requires 9 | d_pi.

The order n is NOT taken on trust: each curve is checked by verifying that the
standard generator G lies on the curve and that [n]G = O. Without that check a
transcription error in n is indistinguishable from an error in the paper.

Usage: python3 cpi_audit.py
"""
from sympy import sieve, integer_nthroot, isprime

TRIAL_BOUND = 10**6

# NIST prime curves: y^2 = x^3 - 3x + b over F_p, generator G, prime order n.
CURVES = {
    "P-192": dict(
        p=2**192 - 2**64 - 1, a=-3,
        b=0x64210519E59C80E70FA7E9AB72243049FEB8DEECC146B9B1,
        Gx=0x188DA80EB03090F67CBF20EB43A18800F4FF0AFD82FF1012,
        Gy=0x07192B95FFC8DA78631011ED6B24CDD573F977A11E794811,
        n=6277101735386680763835789423176059013767194773182842284081),
    "P-224": dict(
        p=2**224 - 2**96 + 1, a=-3,
        b=0xB4050A850C04B3ABF54132565044B0B7D7BFD8BA270B39432355FFB4,
        Gx=0xB70E0CBD6BB4BF7F321390B94A03C1D356C21122343280D6115C1D21,
        Gy=0xBD376388B5F723FB4C22DFE6CD4375A05A07476444D5819985007E34,
        n=26959946667150639794667015087019625940457807714424391721682722368061),
    "P-256": dict(
        p=2**256 - 2**224 + 2**192 + 2**96 - 1, a=-3,
        b=0x5AC635D8AA3A93E7B3EBBD55769886BC651D06B0CC53B0F63BCE3C3E27D2604B,
        Gx=0x6B17D1F2E12C4247F8BCE6E563A440F277037D812DEB33A0F4A13945D898C296,
        Gy=0x4FE342E2FE1A7F9B8EE7EB4A7C0F9E162BCE33576B315ECECBB6406837BF51F5,
        n=115792089210356248762697446949407573529996955224135760342422259061068512044369),
    "P-384": dict(
        p=2**384 - 2**128 - 2**96 + 2**32 - 1, a=-3,
        b=0xB3312FA7E23EE7E4988E056BE3F82D19181D9C6EFE8141120314088F5013875AC656398D8A2ED19D2A85C8EDD3EC2AEF,
        Gx=0xAA87CA22BE8B05378EB1C71EF320AD746E1D3B628BA79B9859F741E082542A385502F25DBF55296C3A545E3872760AB7,
        Gy=0x3617DE4A96262C6F5D9E98BF9292DC29F8F41DBD289A147CE9DA3113B5F0B8C00A60B1CE1D7E819D7A431D7C90EA0E5F,
        n=39402006196394479212279040100143613805079739270465446667946905279627659399113263569398956308152294913554433653942643),
    "P-521": dict(
        p=2**521 - 1, a=-3,
        b=0x0051953EB9618E1C9A1F929A21A0B68540EEA2DA725B99B315F3B8B489918EF109E156193951EC7E937B1652C0BD3BB1BF073573DF883D2C34F1EF451FD46B503F00,
        Gx=0x00C6858E06B70404E9CD9E3ECB662395B4429C648139053FB521F828AF606B4D3DBAA14B5E77EFE75928FE1DC127A2FFA8DE3348B3C1856A429BF97E7E31C2E5BD66,
        Gy=0x011839296A789A3BC0045C8A5FB42C7D1BD998F54449579B446817AFBD17273E662C97EE72995EF42640C550B9013FAD0761353C7086A272C24088BE94769FD16650,
        n=6864797660130609714981900799081393217269435300143305409394463459185543183397655394245057746333217197532963996371363321113864768612440380340372808892707005449),
}


def inv(x, p):
    return pow(x, p - 2, p)


def add(P, Q, a, p):
    if P is None:
        return Q
    if Q is None:
        return P
    x1, y1 = P
    x2, y2 = Q
    if x1 == x2 and (y1 + y2) % p == 0:
        return None
    if P != Q:
        m = (y2 - y1) * inv((x2 - x1) % p, p) % p
    else:
        m = (3 * x1 * x1 + a) * inv(2 * y1, p) % p
    x3 = (m * m - x1 - x2) % p
    return (x3, (m * (x1 - x3) - y1) % p)


def mul(k, P, a, p):
    R, Q = None, P
    while k:
        if k & 1:
            R = add(R, Q, a, p)
        Q = add(Q, Q, a, p)
        k >>= 1
    return R


def square_part_below(m, bound):
    """Exact square part of m contributed by primes <= bound, plus the cofactor."""
    sieve.extend(bound)
    sq, rem, vals = 1, m, {}
    for q in sieve.primerange(2, bound):
        if q * q > rem:
            break
        e = 0
        while rem % q == 0:
            rem //= q
            e += 1
        if e:
            vals[q] = e
        if e >= 2:
            sq *= q ** (e // 2)
    return sq, rem, vals


# Koblitz curves: m, a, cofactor, NIST published prime order n.
# Figure 1 gives c_pi as a product of listed primes times P(c_pi); recorded here
# as (listed_factors, P_cpi_as_printed) so the row can be checked term by term.
KOBLITZ = {
    "K-163": (163, 1, 2, 5846006549323611672814741753598448348329118574063,
              [45641, 82153, 56498081], 86110311),
    "K-233": (233, 0, 4, 3450873173395281893717377931138512760570940988862252126328087024741343,
              [5610641, 85310626991], 150532234816721999),
    "K-283": (283, 0, 4, 3885337784451458141838923813647037813284811733793061324295874997529815829704422603873,
              [1697, 162254089], 1779143207551652584836995286271),
    "K-409": (409, 0, 4, 330527984395124299475957654016385519914202341482140609642324395022880711289249191050673258457777458014096366590617731358671,
              [21262439877311, 22431439539154506863], None),
    "K-571": (571, 0, 4, 1932268761508629172347675945465993672149463664853217499328617625725759571144780212268133978522706711834706712800825351461273674974066617311929682421617092503555733685276673,
              [3952463], None),
}


def koblitz_trace(m, a):
    """Trace of Frobenius over F_2^m by the integer Lucas recurrence."""
    mu = 1 if a == 1 else -1
    t0, t1 = 2, mu
    for _ in range(2, m + 1):
        t0, t1 = t1, mu * t1 - 2 * t0
    return t1


def koblitz_audit():
    print("\nKoblitz rows - positive control, pure integer arithmetic (no F_2^m needed)\n")
    print(f"    {'curve':7s} {'order=h*n_NIST':>15s} {'d_pi=-7c^2':>11s} {'c_pi bits':>10s} "
          f"{'Fig1 product':>13s}")
    results = {}
    for name, (m, a, h, n, listed, p_printed) in KOBLITZ.items():
        q = 2 ** m
        t = koblitz_trace(m, a)
        order_ok = (q + 1 - t) == h * n
        d = t * t - 4 * q
        c, exact = integer_nthroot(-d // 7, 2)
        cm_ok = ((-d) % 7 == 0) and exact and (d == -7 * c * c)
        # Figure 1 states c_pi = (product of listed primes) * P(c_pi)
        prod = 1
        for f in listed:
            prod *= f
        if p_printed is not None:
            fig_ok = (prod * p_printed == c)
            fig = "MATCH" if fig_ok else "MISMATCH"
        else:
            fig = "n/a"
        results[name] = (c, listed, p_printed)
        print(f"    {name:7s} {str(order_ok):>15s} {str(cm_ok):>11s} {c.bit_length():>10d} {fig:>13s}")

    # A product identity ALONE is not reproduction of a factorization. Figure 1's
    # c_pi column claims a factorization into primes and its P(c_pi) column claims
    # the LARGEST of them. All three must be checked, and rows with no usable
    # claimed factorization must be reported censored rather than silently "n/a".
    print("\n    Full Figure 1 row check (product AND primality of every factor AND maximality)\n")
    print(f"    {'curve':7s} {'product':>9s} {'all prime':>10s} {'P=max':>7s} {'verdict':>11s}")
    for name, (m, a, h, n, listed, p_printed) in KOBLITZ.items():
        c = results[name][0]
        if p_printed is None:
            # Censored: the paste's P(c_pi) for these rows is line-wrapped into
            # unusability. Report what IS checkable - that the listed factors
            # divide c_pi - and the residual that remains unfactored.
            prod = 1
            for f in listed:
                prod *= f
            divides = (c % prod == 0)
            resid = c // prod if divides else None
            note = f"resid {resid.bit_length()}b" if divides else "LISTED NOT DIVISOR"
            print(f"    {name:7s} {'CENSORED':>9s} {'-':>10s} {'-':>7s} {note:>11s}")
            continue
        factors = listed + [p_printed]
        prod = 1
        for f in factors:
            prod *= f
        prod_ok = (prod == c)
        all_prime = all(isprime(f) for f in factors)
        max_ok = (p_printed == max(factors))
        verdict = "REPRODUCED" if (prod_ok and all_prime and max_ok) else "FAILS"
        print(f"    {name:7s} {str(prod_ok):>9s} {str(all_prime):>10s} {str(max_ok):>7s} {verdict:>11s}")
    return results


def main():
    print(f"{'curve':7s} {'G on E':>7s} {'[n]G==O':>8s} {'t parity':>9s} {'nu_2(d)':>8s} "
          f"{'-d mod 9':>9s} {'sq part<=1e6':>13s} {'cofac bits':>11s}")
    for name, C in CURVES.items():
        p, a, b = C["p"], C["a"] % C["p"], C["b"]
        G, n = (C["Gx"], C["Gy"]), C["n"]

        on_curve = (G[1] * G[1] - (G[0] ** 3 + a * G[0] + b)) % p == 0
        order_ok = mul(n, G, a, p) is None

        t = p + 1 - n
        d = t * t - 4 * p
        assert d < 0 and abs(t) <= 2 * integer_nthroot(p, 2)[0] + 2, "Hasse violated"
        m = -d

        nu2 = 0
        tmp = m
        while tmp % 2 == 0:
            tmp //= 2
            nu2 += 1

        sq, cofac, _ = square_part_below(m, TRIAL_BOUND)
        parity = "odd" if t % 2 else "EVEN"

        print(f"{name:7s} {str(on_curve):>7s} {str(order_ok):>8s} {parity:>9s} {nu2:>8d} "
              f"{m % 9:>9d} {sq:>13d} {cofac.bit_length():>11d}")

    print()
    print("Figure 1 reports c_pi = 3, P(c_pi) = 3 for P-256, which requires 9 | d_pi.")
    print("A '-d mod 9' of 3 for P-256 refutes that entry exactly, with no factoring:")
    print("3 is odd, so 3 | c_pi would force 9 | d_pi whichever branch of the")
    print("conductor definition applies. The result is independent of the s vs s/2 fix.")
    print("P-224, absent from Figure 1, is the curve with 9 | -d_pi.")
    print()
    print("t is odd on every row above, so nu_2(d_pi) = 0, so c_pi = s here and the")
    print("factor-of-2 conductor correction does not bite for these curves. It does not")
    print("bite for the Koblitz rows below either, but for a different reason: there")
    print("d_K = -7 = 1 (mod 4) is already fundamental, so c_pi = sqrt(-d_pi/7) exactly,")
    print("whatever the parity of t.")
    print()
    print("NOT CONCLUDED: the exact c_pi for any row. A cofactor with no square factor")
    print("below 1e6 may still have one above it; that is a CENSORED result, not c_pi = 1.")
    print()
    koblitz_audit()
    print()
    print("K-233 and K-283 reproduce Figure 1's claimed factorization on all three checks.")
    print("That is a strong positive control on the COMPUTATION -- Lucas recurrence,")
    print("conductor definition, and -7c^2 identity jointly correct.")
    print()
    print("It is a much WEAKER control on the TRANSCRIPTION, and does NOT raise confidence")
    print("in the P-256 row (Coordinator ruling DEC-20260726-004). The competing explanation")
    print("for P-256 is a DROPPED row, which a paste can satisfy while reproducing every row")
    print("it does contain; and there is no transfer across blocks, since the K-rows are")
    print("checkable only because Koblitz CM makes c_pi exactly computable.")
    print()
    print("K-163 does NOT match as printed. Its printed P(c_pi) = 86110311 is COMPOSITE")
    print("(= 3*7*367*11173), so it cannot be a prime factor of anything. The true")
    print("factorization is 45641*82153*8610311*56498081, and the largest prime factor")
    print("is 56498081 -- which Figure 1 already lists as one of the OTHER factors.")
    print("So the row is internally inconsistent however the digits are read.")
    print()
    print("TRANSCRIPTION RISK, NARROWED: the Figure 1 values used here come from a")
    print("plain-text paste, not from arXiv:math/0411378v3 itself, and that paste has")
    print("no P-224 row at all. A dropped or shifted row in the PASTE would produce")
    print("exactly the discrepancy reported above. Until the table is checked verbatim")
    print("against the source, 'the paper is wrong' is NOT an available conclusion --")
    print("only 'the transcription we hold is inconsistent with these curves'.")


if __name__ == "__main__":
    main()

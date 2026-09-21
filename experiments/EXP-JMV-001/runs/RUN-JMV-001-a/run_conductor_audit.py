#!/usr/bin/env python3
"""
EXP-JMV-001 RUN-JMV-001-a: Conductor audit of the JMV Figure 1 curve set,
against this program's own held transcription artifact, per
specification.yaml version 2 (approved under DEC-20260906-b083ce).

This is the RUN script (not the scouting script cpi_audit.py, which this run
extends but does not import or share code with, per specification.yaml
notes). verify_certificates.py is a SEPARATE, independently-written checker
that does not import this file and shares no function bodies with it.

Scope: exactly the ten curves_attempted rows (P-192/224/256/384/521,
K-163/233/283/409/571). No curve in curves_not_attempted is computed.

Conductor definition: CONDITION D1, binding (specification.yaml). For
d_pi = s^2 * u with u squarefree: c_pi = s if u == 1 (mod 4), else c_pi = s/2.
The branch is COMPUTED per row, not assumed.

Level count: CONDITION D2, binding. Number of divisors of c_pi; CENSORED
whenever the factorization of c_pi is incomplete.

Trial division bound: 10**6 (specification.yaml inputs.trial_division_bound).
Primality routine: sympy.isprime (BPSW + Miller-Rabin bases), stated here so
the manifest can record it; the cap on any single factorization attempt is
the trial-division bound itself -- no factoring beyond trial division to 1e6
is performed by this run script (Pollard-rho / ECM are explicitly NOT used
here, matching the scouting script's discipline and the spec's stopping rule
on large-factorization effort).
"""
import json
import math
import sys
import time

from sympy import sieve, integer_nthroot, isprime

TRIAL_BOUND = 1_000_000

# ---------------------------------------------------------------------------
# Held transcription artifact (verbatim numeric content), reproduced here from
# research/JMV2005_experiment_suite_20260726.md Sec. 2 and the embedded
# constants of experiments/EXP-JMV-001/cpi_audit.py. This IS the complete
# figure1_transcription_artifact as held -- there is no cleaner source. It is
# archived VERBATIM (not tidied) in figure1_transcription.md alongside this
# run.
# ---------------------------------------------------------------------------

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

# Held Figure-1 numeric content for the prime rows, AS ACTUALLY TRANSCRIBED IN
# THIS PROGRAM'S ARTIFACT (research/JMV2005_experiment_suite_20260726.md Sec.
# 2). This is deliberately incomplete: the paste we hold gives an explicit
# claimed value ONLY for P-256 (c_pi = 3, P(c_pi) = 3), and explicitly
# confirms P-224 is ABSENT from Figure 1 as pasted. It contains NO transcribed
# Figure-1 value at all -- not even "absent" -- for P-192, P-384, or P-521;
# the held artifact is simply silent on those three rows. This silence is
# itself part of what C1b requires be recorded, not papered over.
FIG1_PRIME_ROWS = {
    "P-192": {"held": "NO_ROW_VALUE_TRANSCRIBED"},
    "P-224": {"held": "CONFIRMED_ABSENT_FROM_FIGURE_1"},
    "P-256": {"held": "VALUE_TRANSCRIBED", "c_pi": 3, "P_c_pi": 3},
    "P-384": {"held": "NO_ROW_VALUE_TRANSCRIBED"},
    "P-521": {"held": "NO_ROW_VALUE_TRANSCRIBED"},
}

# Koblitz curves: m, a, cofactor h, NIST published prime order n_NIST, the
# listed (non-P) claimed factors of c_pi as pasted, and the claimed P(c_pi)
# (None where the paste's P(c_pi) is line-wrapped into unusability: K-409,
# K-571, per the held artifact).
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


def inv(x, p):
    return pow(x, p - 2, p)


def ec_add(P, Q, a, p):
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


def ec_mul(k, P, a, p):
    R, Q = None, P
    while k:
        if k & 1:
            R = ec_add(R, Q, a, p)
        Q = ec_add(Q, Q, a, p)
        k >>= 1
    return R


def koblitz_trace(m, a):
    mu = 1 if a == 1 else -1
    t0, t1 = 2, mu
    for _ in range(2, m + 1):
        t0, t1 = t1, mu * t1 - 2 * t0
    return t1


def factor_below_bound(m, bound):
    """Trial-division factorization of |m| by every prime <= bound.
    Returns (factors: {prime: exponent}, cofactor: the unfactored remainder).
    No factoring beyond this bound is attempted (spec: trial_division_bound).
    """
    sieve.extend(bound)
    rem = abs(m)
    factors = {}
    for q in sieve.primerange(2, bound + 1):
        if q * q > rem:
            break
        e = 0
        while rem % q == 0:
            rem //= q
            e += 1
        if e:
            factors[int(q)] = e
    return factors, rem


def square_part_and_cofactor(factors, cofactor):
    """From a partial factorization (factors dict + unfactored cofactor),
    the exact square part contributed by primes below the trial bound, and
    whether the factorization is COMPLETE (cofactor == 1)."""
    s_below = 1
    odd_leftover = 1  # exponent-1 parity leftover from below-bound primes, if any prime had odd exponent
    for q, e in factors.items():
        s_below *= q ** (e // 2)
        if e % 2:
            odd_leftover *= q
    complete = (cofactor == 1)
    return s_below, odd_leftover, complete


def audit_prime_row(name, C):
    p, a, b, n = C["p"], C["a"] % C["p"], C["b"], C["n"]
    G = (C["Gx"], C["Gy"])

    on_curve = (G[1] * G[1] - (G[0] ** 3 + a * G[0] + b)) % p == 0
    order_ok = ec_mul(n, G, a, p) is None
    ctrl_order_prime = bool(on_curve and order_ok)

    t = p + 1 - n
    d_pi = t * t - 4 * p  # negative
    m = -d_pi  # positive magnitude, m = 4p - t^2

    two_sqrt_p = integer_nthroot(p, 2)[0]
    hasse_ok = abs(t) <= 2 * two_sqrt_p + 2  # Hasse bound with integer-sqrt slack

    nu2 = 0
    tmp = m
    while tmp % 2 == 0:
        tmp //= 2
        nu2 += 1

    factors, cofactor = factor_below_bound(m, TRIAL_BOUND)
    s_below, odd_leftover, complete = square_part_and_cofactor(factors, cofactor)

    t_parity = "odd" if t % 2 else "even"
    # u mod 4 branch: per specification's conductor_definition_applicability_note,
    # for these prime-field curves t is expected odd => d_pi odd => u = d_pi mod 4 == 1
    # => c_pi = s. We COMPUTE this rather than assume it.
    if complete:
        u = m if (m % 4 in (0, 1)) else None  # m = -d_pi is a valid discriminant candidate only if 0/1 mod4
        # exact s is the full square part (all primes, all below bound since complete)
        s_exact = s_below
        # squarefree u_exact = m // s_exact**2
        u_exact = m // (s_exact * s_exact)
        branch = "u=1(mod4)->c_pi=s" if (u_exact % 4 == 1) else "u!=1(mod4)->c_pi=s/2"
        if u_exact % 4 == 1:
            c_pi = s_exact
        else:
            assert s_exact % 2 == 0, "s must be even in the s/2 branch (discriminant parity)"
            c_pi = s_exact // 2
        c_pi_censored = False
        level_count = None  # filled by caller only if factorization of c_pi itself is complete (it is, since m is completely factored)
        # level_count = number of divisors of c_pi; derivable from factors of s once we
        # divide out any factor of 2 from the s/2 branch -- but per the
        # applicability note this branch never bites on these rows; compute
        # divisor count directly if c_pi factorization is fully known.
    else:
        c_pi = None
        c_pi_censored = True
        branch = "UNDETERMINED (incomplete factorization below trial bound)"
        level_count = None

    residual_bitlen = cofactor.bit_length() if not complete else 0

    row = dict(
        curve=name,
        ctrl_order_prime=ctrl_order_prime,
        on_curve=on_curve,
        order_ok=order_ok,
        t=t,
        t_parity=t_parity,
        d_pi=d_pi,
        hasse_ok=hasse_ok,
        nu2_d_pi=nu2,
        nu_l_below_bound=factors,
        conductor_branch=branch,
        c_pi=c_pi,
        c_pi_censored=c_pi_censored,
        c_pi_secondary_naive_square_part_below_bound=s_below,
        residual_cofactor_bitlength=residual_bitlen,
        factorization_complete=complete,
        level_count=(None if c_pi_censored else _divisor_count(c_pi)),
    )
    return row


def _divisor_count(n):
    if n is None:
        return None
    if n == 1:
        return 1
    factors, cofactor = factor_below_bound(n, TRIAL_BOUND)
    if cofactor != 1:
        # Should not happen for these rows given how c_pi was derived (already
        # fully factored via m's factorization), but guard defensively.
        return None
    count = 1
    for _, e in factors.items():
        count *= (e + 1)
    return count


def audit_koblitz_row(name, spec):
    m, a, h, n_nist, listed, p_printed = spec
    q = 2 ** m
    t = koblitz_trace(m, a)
    derived_order = q + 1 - t
    ctrl_order_koblitz = (derived_order == h * n_nist)

    d_pi = t * t - 4 * q  # = -7 * c_pi^2 exactly, by CM theory
    magnitude = -d_pi
    assert magnitude % 7 == 0, "CM structure violated: -d_pi not divisible by 7"
    c_pi_sq = magnitude // 7
    c_pi, exact_sqrt = integer_nthroot(c_pi_sq, 2)
    ctrl_cm_koblitz = bool(exact_sqrt and d_pi == -7 * c_pi * c_pi)

    two_sqrt_q = integer_nthroot(q, 2)[0]
    hasse_ok = abs(t) <= 2 * two_sqrt_q + 2

    prod_listed = 1
    for f in listed:
        prod_listed *= f

    row = dict(
        curve=name,
        ctrl_order_koblitz=ctrl_order_koblitz,
        derived_order=derived_order,
        cofactor_times_n_nist=h * n_nist,
        t=t,
        d_pi=d_pi,
        ctrl_cm_koblitz=ctrl_cm_koblitz,
        hasse_ok=hasse_ok,
        c_pi=int(c_pi),
        c_pi_bits=int(c_pi).bit_length(),
        listed_factors=listed,
        p_printed=p_printed,
    )

    if p_printed is not None:
        # COMPLETE claimed factorization: run all three CTRL-FIG1-ROWCHECK parts.
        factors = listed + [p_printed]
        prod_all = 1
        for f in factors:
            prod_all *= f
        product_identity_ok = (prod_all == c_pi)
        all_prime = {f: bool(isprime(f)) for f in factors}
        primality_ok = all(all_prime.values())
        maximality_ok = (p_printed == max(factors))
        reproduces = product_identity_ok and primality_ok and maximality_ok
        row.update(
            factorization_status="COMPLETE_AS_HELD",
            product_identity_ok=product_identity_ok,
            primality_by_factor=all_prime,
            primality_ok=primality_ok,
            maximality_ok=maximality_ok,
            verdict=("reproduces" if reproduces else "contradicts"),
            level_count=None,  # only meaningful if c_pi's OWN factorization is fully established
        )
        if reproduces:
            # c_pi's complete factorization is exactly {listed factors} + {p_printed},
            # all confirmed prime -> level_count = number of divisors of c_pi.
            from collections import Counter
            cnt = Counter(factors)
            level_count = 1
            for _, e in cnt.items():
                level_count *= (e + 1)
            row["level_count"] = level_count
    else:
        # INCOMPLETE claimed factorization (K-409, K-571 as held): divisibility +
        # censored residual, per CTRL-FIG1-ROWCHECK second branch.
        divides = (c_pi % prod_listed == 0)
        residual = c_pi // prod_listed if divides else None
        row.update(
            factorization_status="INCOMPLETE_AS_HELD",
            listed_product=prod_listed,
            listed_divides_c_pi=divides,
            residual_cofactor=residual,
            residual_cofactor_bitlength=(residual.bit_length() if residual is not None else None),
            verdict="censored/undecidable",
            level_count=None,
        )
    return row


def main():
    t_start = time.time()
    prime_rows = {}
    for name, C in CURVES.items():
        prime_rows[name] = audit_prime_row(name, C)

    koblitz_rows = {}
    for name, spec in KOBLITZ.items():
        koblitz_rows[name] = audit_koblitz_row(name, spec)

    # ---- Certificates (contradicted rows only) --------------------------
    certificates = {}

    # P-256_mod9: exact, factoring-free.
    p256 = CURVES["P-256"]
    p, n = p256["p"], p256["n"]
    t_256 = p + 1 - n
    minus_d_pi_256 = 4 * p - t_256 * t_256
    mod9 = minus_d_pi_256 % 9
    p256_cert = dict(
        certificate_id="P-256_mod9",
        claim="Figure 1 (as held) reports c_pi = 3, P(c_pi) = 3 for P-256; "
              "this contradicts the published P-256 parameters.",
        inputs=dict(p=p, n=n),
        derivation=(
            "t = p + 1 - n; minus_d_pi = 4*p - t^2; "
            "if 3 | c_pi then 9 | c_pi^2 | d_pi, contradicting minus_d_pi = 3 (mod 9). "
            "The argument is independent of the D1 s-vs-s/2 branch: 3 | c_pi implies "
            "3 | s implies 9 | s^2 | d_pi either way."
        ),
        computed=dict(t=t_256, minus_d_pi=minus_d_pi_256, minus_d_pi_mod_9=mod9),
        check="assert minus_d_pi_mod_9 == 3  # hence 3 does not divide c_pi, contradicting the held c_pi = 3",
        result="CONTRADICTS" if mod9 == 3 else "DOES_NOT_CONTRADICT",
    )
    certificates["P-256_mod9"] = p256_cert

    # K-163_composite_P: no curve data required at all.
    P_printed = 86110311
    factors_of_P = [3, 7, 367, 11173]
    prod_check = 1
    for f in factors_of_P:
        prod_check *= f
    k163_composite_cert = dict(
        certificate_id="K-163_composite_P",
        claim="Figure 1 (as held) prints P(c_pi) = 86110311 for K-163; this value "
              "is composite and therefore cannot be a prime factor of anything.",
        inputs=dict(printed_P=P_printed, claimed_factorization=factors_of_P),
        derivation="86110311 == 3*7*367*11173 (direct multiplication, no curve data used).",
        computed=dict(product_of_claimed_factorization=prod_check),
        check="assert product_of_claimed_factorization == printed_P and not is_prime(printed_P)",
        result="CONTRADICTS" if (prod_check == P_printed and not isprime(P_printed)) else "DOES_NOT_CONTRADICT",
    )
    certificates["K-163_composite_P"] = k163_composite_cert

    # K-163_product_mismatch: depends on curve data / CTRL-ORDER-KOBLITZ passing.
    k163_row = koblitz_rows["K-163"]
    listed_163 = KOBLITZ["K-163"][4]
    prod_listed_163 = 1
    for f in listed_163:
        prod_listed_163 *= f
    printed_product_163 = prod_listed_163 * P_printed
    derived_c_pi_163 = k163_row["c_pi"]
    k163_product_cert = dict(
        certificate_id="K-163_product_mismatch",
        claim="Figure 1's printed K-163 product (listed factors x P(c_pi)) does not "
              "equal the c_pi derived from the curve's own Lucas trace and the "
              "d_pi = -7*c_pi^2 identity.",
        inputs=dict(
            listed_factors=listed_163,
            printed_P=P_printed,
            derived_c_pi=derived_c_pi_163,
            ctrl_order_koblitz_passed=k163_row["ctrl_order_koblitz"],
            ctrl_cm_koblitz_passed=k163_row["ctrl_cm_koblitz"],
        ),
        derivation=(
            "derived_c_pi is computed independently from the Lucas recurrence trace "
            "and d_pi = -7*c_pi^2 (CTRL-CM-KOBLITZ). printed_product = "
            "product(listed_factors) * printed_P. Mismatch shows the printed "
            "factorization's product does not equal the true c_pi."
        ),
        computed=dict(printed_product=printed_product_163, derived_c_pi=derived_c_pi_163,
                      ratio_printed_over_derived=printed_product_163 / derived_c_pi_163),
        check="assert printed_product != derived_c_pi  # depends on CTRL-ORDER-KOBLITZ and CTRL-CM-KOBLITZ passing",
        result=("CONTRADICTS" if (printed_product_163 != derived_c_pi_163
                                   and k163_row["ctrl_order_koblitz"] and k163_row["ctrl_cm_koblitz"])
                else "DOES_NOT_CONTRADICT_OR_CONTROL_FAILED"),
    )
    certificates["K-163_product_mismatch"] = k163_product_cert

    # ---- Figure 1 verdicts, prime rows (using held transcription content) -
    fig1_verdicts = {}
    for name, row in prime_rows.items():
        held = FIG1_PRIME_ROWS[name]["held"]
        if name == "P-256":
            fig1_verdicts[name] = dict(
                verdict="contradicts",
                reason="Held transcription reports c_pi=3, P(c_pi)=3; certificate P-256_mod9 "
                       "shows -d_pi mod 9 == 3, so 3 does not divide c_pi.",
                checks_applied=["mod-9 factoring-free exclusion (not the 3-part CTRL-FIG1-ROWCHECK, "
                                "which applies only to complete/incomplete listed factorizations; "
                                "no factorization is listed for any prime row in the held artifact)"],
            )
        elif held == "CONFIRMED_ABSENT_FROM_FIGURE_1":
            fig1_verdicts[name] = dict(
                verdict="censored/undecidable",
                reason="SPEC GAP (reported, not patched): the verdict enum in specification.yaml "
                       "metrics.primary has no value for 'row confirmed absent from Figure 1 as "
                       "held'. P-224 IS in curves_attempted and its curve arithmetic is fully "
                       "computed above; there is simply no Figure-1 row to compare it against. "
                       "'censored/undecidable' is used as the nearest available bucket meaning "
                       "'no reproduces/contradicts verdict can be rendered', NOT because any "
                       "arithmetic is incomplete for this row.",
                checks_applied=[],
            )
        else:  # NO_ROW_VALUE_TRANSCRIBED
            fig1_verdicts[name] = dict(
                verdict="censored/undecidable",
                reason="SPEC GAP (reported, not patched): the held transcription (research/"
                       "JMV2005_experiment_suite_20260726.md Sec. 2 and cpi_audit.py) never "
                       "transcribes an explicit Figure-1 numeric value for this row at all -- "
                       "distinct from P-224, which is explicitly confirmed absent. There is no "
                       "held row content to check the computed c_pi against. 'censored/"
                       "undecidable' is used as the nearest available bucket; the true status is "
                       "'no transcribed comparison value held', which the enum does not name.",
                checks_applied=[],
            )
    for name, row in koblitz_rows.items():
        fig1_verdicts[name] = dict(
            verdict=row["verdict"],
            reason=(
                "Full three-part CTRL-FIG1-ROWCHECK applied (complete claimed factorization)."
                if row.get("factorization_status") == "COMPLETE_AS_HELD"
                else "Incomplete claimed factorization as held; divisibility + censored residual reported."
            ),
            checks_applied=(
                ["product_identity", "primality", "maximality"]
                if row.get("factorization_status") == "COMPLETE_AS_HELD"
                else ["divisibility_of_listed_factors"]
            ),
        )

    wall_clock = time.time() - t_start

    raw = dict(
        run_id="RUN-JMV-001-a",
        experiment_id="EXP-JMV-001",
        trial_division_bound=TRIAL_BOUND,
        prime_rows=prime_rows,
        koblitz_rows=koblitz_rows,
        fig1_verdicts=fig1_verdicts,
        certificates=certificates,
        wall_clock_seconds=wall_clock,
    )
    with open("raw.json", "w") as f:
        json.dump(raw, f, indent=2, default=str)

    for cid, cert in certificates.items():
        with open(f"certificates/{cid}.json", "w") as f:
            json.dump(cert, f, indent=2, default=str)

    # ---- controls.json ----------------------------------------------------
    controls = dict(
        CTRL_ORDER_PRIME={name: row["ctrl_order_prime"] for name, row in prime_rows.items()},
        CTRL_ORDER_KOBLITZ={name: row["ctrl_order_koblitz"] for name, row in koblitz_rows.items()},
        CTRL_CM_KOBLITZ={name: row["ctrl_cm_koblitz"] for name, row in koblitz_rows.items()},
        CTRL_HASSE={
            **{name: row["hasse_ok"] for name, row in prime_rows.items()},
            **{name: row["hasse_ok"] for name, row in koblitz_rows.items()},
        },
        all_CTRL_ORDER_PRIME_pass=all(row["ctrl_order_prime"] for row in prime_rows.values()),
        all_CTRL_ORDER_KOBLITZ_pass=all(row["ctrl_order_koblitz"] for row in koblitz_rows.values()),
        all_CTRL_CM_KOBLITZ_pass=all(row["ctrl_cm_koblitz"] for row in koblitz_rows.values()),
        all_CTRL_HASSE_pass=(
            all(row["hasse_ok"] for row in prime_rows.values())
            and all(row["hasse_ok"] for row in koblitz_rows.values())
        ),
    )
    controls["pipeline_valid"] = (
        controls["all_CTRL_ORDER_PRIME_pass"]
        and controls["all_CTRL_ORDER_KOBLITZ_pass"]
        and controls["all_CTRL_CM_KOBLITZ_pass"]
        and controls["all_CTRL_HASSE_pass"]
    )
    with open("controls.json", "w") as f:
        json.dump(controls, f, indent=2, default=str)

    # ---- cpi_table.csv ------------------------------------------------------
    import csv
    with open("cpi_table.csv", "w", newline="") as f:
        w = csv.writer(f)
        w.writerow([
            "curve", "t", "t_parity", "d_pi", "conductor_branch", "c_pi",
            "c_pi_censored", "secondary_naive_square_part_below_bound",
            "residual_cofactor_bitlength", "P_c_pi", "level_count",
            "fig1_verdict", "fig1_checks_applied", "fig1_reason",
        ])
        for name, row in prime_rows.items():
            v = fig1_verdicts[name]
            w.writerow([
                name, row["t"], row["t_parity"], row["d_pi"], row["conductor_branch"],
                row["c_pi"], row["c_pi_censored"],
                row["c_pi_secondary_naive_square_part_below_bound"],
                row["residual_cofactor_bitlength"], "", row["level_count"],
                v["verdict"], ";".join(v["checks_applied"]), v["reason"],
            ])
        for name, row in koblitz_rows.items():
            v = fig1_verdicts[name]
            w.writerow([
                name, row["t"], "n/a (Koblitz)", row["d_pi"],
                "d_K=-7 already fundamental -> c_pi = sqrt(-d_pi/7)",
                row["c_pi"], False, "", row.get("residual_cofactor_bitlength", ""),
                row.get("p_printed", ""), row.get("level_count"),
                v["verdict"], ";".join(v["checks_applied"]), v["reason"],
            ])

    print(f"DONE. wall_clock_seconds={wall_clock:.3f}", file=sys.stderr)
    return raw, controls


if __name__ == "__main__":
    main()

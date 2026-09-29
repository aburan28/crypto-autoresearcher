"""
Curve-panel construction for EXP-MONO-12ce1c, built ONLY from the primitives
in curve.py (construct_prime, curve_stream, curve_discriminant_ok,
count_E_points, count_Z, cm_discriminant_test), run against the FIXED panel
domain (not seed-dependent -- see implementation.md "domain split" for why
panel construction must not vary across the two replication runs while the
Stage-2/3/4 sampling draws do).

Panel design (documented, deterministic, reproducible from PANEL_DOMAIN alone):
  - construct one prime per field_bits entry [7,8,9,10,11] -> 5 primes.
  - 4 "random ordinary" curves: the FIRST accepted (non-singular, ordinary)
    curve from the curve-a/curve-b stream at each of the 4 smallest primes
    (t=0 accepted immediately at all four primes, per the run transcript).
  - j=0 and j=1728 members: per spec text, constructed at a SINGLE additional
    prime satisfying the standard non-supersingularity congruences for each
    family (p = 1 mod 3 for j=0, p = 1 mod 4 for j=1728) -- both conditions
    happen to be satisfiable at the SAME field_bits prime (421, the 9-bit
    one, which is also RO3's prime): j=0 uses A=0 with B = first accepted
    value of the curve-b stream at that prime; j=1728 uses B=0 with A = first
    accepted value of the curve-a stream at that prime.
  - 2 CM members: continuing the curve-a/curve-b stream (from t where the
    random-ordinary search for that prime left off) at the smallest prime,
    testing each accepted candidate's Frobenius trace against
    curve.cm_discriminant_test (a declared, standard small-fundamental-
    discriminant list), taking the first two hits.

This yields 8 distinct (p, A, B) curves. tau in {1,2,4} coverage (the Stage-3
hard precondition) is CHECKED, not assumed, after construction.
"""
from curve import (
    construct_prime, curve_stream, curve_discriminant_ok, count_E_points,
    count_Z, cm_discriminant_test, ConstructionFailure,
)

PANEL_DOMAIN = "EXP-MONO-12ce1c/v1"
FIELD_BITS = [7, 8, 9, 10, 11]


def accept_first_ordinary(domain, p, t_start=0, t_max=2000, require_A=None, require_B=None):
    """Scans the curve stream from t_start, returns first (t,A,B) that is
    non-singular and ordinary, optionally forcing A or B to a fixed value
    (used for the j=0 / j=1728 special members, which use only ONE of the
    two stream sequences)."""
    for t, a_t, b_t in curve_stream(domain, p, t_start, t_max):
        A = require_A if require_A is not None else a_t
        B = require_B if require_B is not None else b_t
        if not curve_discriminant_ok(A, B, p):
            continue
        N = count_E_points(A, B, p)
        if N % p == 1:
            continue
        return t, A, B, N
    raise ConstructionFailure(f"no accepted ordinary curve found for p={p} in t<{t_max}")


def build_panel():
    """Returns dict with 'primes' transcript and 'curves': list of curve dicts,
    each with role, p, A, B, N, trace, Z, tau, j_invariant_class, cm_discriminant."""
    domain = PANEL_DOMAIN
    prime_transcript = {}
    primes = []
    for b in FIELD_BITS:
        p, tr = construct_prime(domain, b)
        prime_transcript[b] = tr
        primes.append(p)
    p7, p8, p9, p10, p11 = primes

    curves = []

    def curve_record(role, p, A, B, t_used, stream_note, source_prime_bits):
        N = count_E_points(A, B, p)
        trace = p + 1 - N
        Z = count_Z(A, B, p)
        tau = Z + 1
        return {
            "role": role, "p": p, "A": A, "B": B, "N": N, "trace": trace,
            "Z": Z, "tau": tau, "t_used": t_used, "stream_note": stream_note,
            "source_prime_bits": source_prime_bits,
        }

    # 4 random ordinary curves, one per prime p7,p8,p9,p10
    ro_primes = [("RO1", p7, 7), ("RO2", p8, 8), ("RO3", p9, 9), ("RO4", p10, 10)]
    ro_next_t = {}
    for role, p, bits in ro_primes:
        t, A, B, N = accept_first_ordinary(domain, p, t_start=0)
        ro_next_t[p] = t + 1
        curves.append(curve_record(role, p, A, B, t, "curve-a/curve-b stream, both free", bits))

    # j = 0 at p9 (421): A=0, B = first accepted value of curve-b stream
    t0, A0, B0, N0 = accept_first_ordinary(domain, p9, t_start=0, require_A=0)
    curves.append(curve_record("J0", p9, 0, B0, t0, "curve-b stream only, A fixed to 0", 9))

    # j = 1728 at p9 (421): B=0, A = first accepted value of curve-a stream
    t1, A1, B1, N1 = accept_first_ordinary(domain, p9, t_start=0, require_B=0)
    curves.append(curve_record("J1728", p9, A1, 0, t1, "curve-a stream only, B fixed to 0", 9))

    # 2 CM curves: continue the p7 stream from where RO1 left off, testing
    # cm_discriminant_test on each accepted candidate.
    cm_found = []
    t_start = ro_next_t[p7]
    for t, a_t, b_t in curve_stream(domain, p7, t_start, t_start + 5000):
        if not curve_discriminant_ok(a_t, b_t, p7):
            continue
        N = count_E_points(a_t, b_t, p7)
        if N % p7 == 1:
            continue
        trace = p7 + 1 - N
        D = cm_discriminant_test(trace, p7)
        if D is not None:
            cm_found.append((t, a_t, b_t, D))
            if len(cm_found) == 2:
                break
    if len(cm_found) < 2:
        raise ConstructionFailure(f"fewer than 2 CM curves found at p={p7} (found {len(cm_found)})")
    for i, (t, A, B, D) in enumerate(cm_found, start=1):
        rec = curve_record(f"CM{i}", p7, A, B, t, "curve-a/curve-b stream, continued after RO1", 7)
        rec["cm_discriminant"] = D
        curves.append(rec)

    tau_values = sorted({c["tau"] for c in curves})
    tau_coverage_met = all(t in tau_values for t in (1, 2, 4))

    return {
        "domain": domain,
        "prime_transcript": prime_transcript,
        "primes": {"p7": p7, "p8": p8, "p9": p9, "p10": p10, "p11": p11},
        "curves": curves,
        "tau_values_present": tau_values,
        "tau_coverage_met": tau_coverage_met,
    }

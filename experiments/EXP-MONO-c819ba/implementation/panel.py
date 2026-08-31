"""
Curve-panel construction for EXP-MONO-c819ba: >=8 non-singular ordinary
curves (4 random-ordinary min, 2 CM min, j=0, j=1728), built deterministically
from PANEL_DOMAIN per specification.yaml `inputs.curve_construction`. Modeled
on EXP-MONO-12ce1c's panel.py pattern (same construction algorithm, new
domain, independent seed stream -- no cross-contract comparability implied,
per specification.yaml `comparability_policy`).
"""
from curve import (
    construct_prime, curve_stream, curve_discriminant_ok, count_E_points,
    count_Z, cm_discriminant_test, ConstructionFailure,
)

PANEL_DOMAIN = "EXP-MONO-c819ba/v1"
FIELD_BITS = [7, 8, 9, 10, 11]


def accept_first_ordinary(domain, p, t_start=0, t_max=2000, require_A=None, require_B=None):
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
        return {"role": role, "p": p, "A": A, "B": B, "N": N, "trace": trace,
                "Z": Z, "t_used": t_used, "stream_note": stream_note,
                "source_prime_bits": source_prime_bits}

    ro_primes = [("RO1", p7, 7), ("RO2", p8, 8), ("RO3", p9, 9), ("RO4", p10, 10)]
    ro_next_t = {}
    for role, p, bits in ro_primes:
        t, A, B, N = accept_first_ordinary(domain, p, t_start=0)
        ro_next_t[p] = t + 1
        curves.append(curve_record(role, p, A, B, t, "curve-a/curve-b stream, both free", bits))

    # j=0 (y^2=x^3+B) is ordinary only for p = 1 mod 3 (else forced supersingular);
    # j=1728 (y^2=x^3+Ax) only for p = 1 mod 4. p9 need not satisfy either
    # congruence under this contract's own domain (it happened to for
    # EXP-MONO-12ce1c's domain, but seed streams differ per contract by design
    # -- comparability_policy). Search the already-constructed field_bits primes
    # for the smallest that satisfies each congruence; this is a deterministic,
    # seed-free selection over a fixed, already-committed prime list.
    bits_by_prime = {p7: 7, p8: 8, p9: 9, p10: 10, p11: 11}
    j0_host = next((p for p in (p9, p10, p11, p8, p7) if p % 3 == 1), None)
    j1728_host = next((p for p in (p9, p10, p11, p8, p7) if p % 4 == 1), None)
    if j0_host is None:
        raise ConstructionFailure("no field_bits prime with p = 1 mod 3 for a j=0 ordinary curve")
    if j1728_host is None:
        raise ConstructionFailure("no field_bits prime with p = 1 mod 4 for a j=1728 ordinary curve")

    t0, A0, B0, N0 = accept_first_ordinary(domain, j0_host, t_start=0, t_max=20000, require_A=0)
    curves.append(curve_record("J0", j0_host, 0, B0, t0,
                                "curve-b stream only, A fixed to 0; host prime chosen "
                                "for p=1 mod 3 (deviation: not necessarily p9, see "
                                "implementation.md interpretation note)",
                                bits_by_prime[j0_host]))

    t1, A1, B1, N1 = accept_first_ordinary(domain, j1728_host, t_start=0, t_max=20000, require_B=0)
    curves.append(curve_record("J1728", j1728_host, A1, 0, t1,
                                "curve-a stream only, B fixed to 0; host prime chosen "
                                "for p=1 mod 4 (deviation: not necessarily p9, see "
                                "implementation.md interpretation note)",
                                bits_by_prime[j1728_host]))

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

    return {
        "domain": domain,
        "prime_transcript": prime_transcript,
        "primes": {"p7": p7, "p8": p8, "p9": p9, "p10": p10, "p11": p11},
        "curves": curves,
    }

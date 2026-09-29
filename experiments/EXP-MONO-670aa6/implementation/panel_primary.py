"""
Primary >=100-curve panel construction for EXP-MONO-670aa6
(inputs.primary_panel / inputs.prime_construction / inputs.curve_construction).

50 independently-constructed j=0 curves + 50 independently-constructed
random-ordinary curves. curve_ordinal k runs 0..49 WITHIN each family
(independently numbered); field_bits round-robin across [7,8,9,10,11] via
field_bits[k mod 5]. Each curve gets its OWN prime (via construct_prime with
that curve's (b,k)) and its OWN (A,B) (via curve_stream with that curve's
(p,k)). A construction failure at a given (b,k) is reported and that ordinal
is simply ABSENT from the panel -- no backfilling from a different bit
length, no reseeding.
"""
from curve import (
    construct_prime, curve_stream, curve_discriminant_ok, count_E_points,
    ConstructionFailure,
)

PRIMARY_DOMAIN = "EXP-MONO-670aa6/v1"
FIELD_BITS = [7, 8, 9, 10, 11]
PANEL_N_PER_FAMILY = 50


def _construct_one(domain, family, k, t_max=20000):
    """Construct one curve at curve_ordinal k for the given family
    ('j0' or 'random-ordinary'). Returns a curve record dict, or raises
    ConstructionFailure (caller records and skips)."""
    b = FIELD_BITS[k % len(FIELD_BITS)]
    p, prime_transcript = construct_prime(domain, b, k)

    for t, a_t, b_t in curve_stream(domain, p, k, t_start=0, t_max=t_max):
        if family == "j0":
            A = 0
            B = b_t
            if B == 0:
                continue  # reject B=0 (degenerate / avoids double-special locus)
        elif family == "random-ordinary":
            A = a_t
            B = b_t
            if A == 0 or B == 0:
                continue  # reject the j=0 and j=1728 loci exactly
        else:
            raise ValueError(f"unknown family {family!r}")

        if not curve_discriminant_ok(A, B, p):
            continue
        N = count_E_points(A, B, p)
        # NOTE: the frozen curve_construction text names exactly two rejection
        # rules -- singular discriminant, and B=0 (j0) / A=0-or-B=0
        # (random-ordinary) -- and no supersingular-curve rejection. A
        # supersingular-vs-ordinary reject WAS present in EXP-MONO-c819ba's
        # reused accept_first_ordinary() helper; carrying it into this
        # contract's j0 family construction was tried during implementation
        # and found to eliminate ~half of all j0 curve_ordinal slots
        # (every j=0 curve at a prime p = 2 mod 3 is supersingular with
        # N=p+1 for EVERY choice of B, so the "first non-singular candidate"
        # loop would exhaust all 20000 t values whenever the ordinal's own
        # prime happened to be 2 mod 3). That filter is NOT in this
        # contract's own frozen text, so it is omitted here: the panel may
        # include supersingular j=0 curves when the curve_ordinal's own
        # prime is 2 mod 3, exactly as the literal construction rule
        # implies. Recorded as an implementation.md interpretation note,
        # not a silent deviation.
        return {
            "family": family, "curve_ordinal": k, "field_bits": b, "p": p,
            "A": A, "B": B, "N": N, "trace": p + 1 - N, "t_used": t,
            "prime_transcript": prime_transcript,
        }
    raise ConstructionFailure(
        f"no accepted {family} curve found for k={k}, p={p}, b={b} in t<{t_max}")


def build_primary_panel(domain=PRIMARY_DOMAIN, n_per_family=PANEL_N_PER_FAMILY):
    panel = {"j0": [], "random-ordinary": []}
    construction_failures = {"j0": [], "random-ordinary": []}
    for family in ("j0", "random-ordinary"):
        for k in range(n_per_family):
            try:
                rec = _construct_one(domain, family, k)
                panel[family].append(rec)
            except ConstructionFailure as e:
                construction_failures[family].append({"curve_ordinal": k, "error": str(e)})
    return {"domain": domain, "panel": panel, "construction_failures": construction_failures,
            "realized_counts": {f: len(panel[f]) for f in panel},
            "declared_counts": {f: n_per_family for f in panel}}

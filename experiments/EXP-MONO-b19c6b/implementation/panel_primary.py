"""
Primary >=100-curve panel construction for EXP-MONO-b19c6b
(inputs.primary_panel / inputs.prime_construction / inputs.curve_construction).

50 independently-constructed j=0 curves + 50 independently-constructed
random-ordinary curves. curve_ordinal k runs 0..49 WITHIN each family
(independently numbered); field_bits round-robin across [7,8,9,10,11] via
field_bits[k mod 5]. Each curve gets its OWN prime (via construct_prime with
that curve's (family,b,k)) and its OWN (A,B) (via curve_stream with that
curve's (family,p,k)). A construction failure at a given (b,k,family) is
reported and that ordinal is simply ABSENT from the panel -- no
backfilling from a different bit length, no reseeding.

Written FRESH for this contract: `family` is passed to every seed call
(construct_prime, curve_stream) so the j0 and random-ordinary streams are
disjoint by construction, per `inputs.seed_derivation_rule`. Also enforces:
  - j0: p = 1 (mod 3) admission rule already guaranteed by construct_prime;
    RE-CHECKED here directly (not merely assumed from the construction rule
    succeeding), per the handoff's explicit requirement.
  - random-ordinary: explicit computed supersingularity rejection
    (is_supersingular), since a free (A,B) pair has no congruence guarantee.
"""
from curve import (
    construct_prime, curve_stream, curve_discriminant_ok, count_E_points,
    is_supersingular, ConstructionFailure,
)

PRIMARY_DOMAIN = "EXP-MONO-b19c6b/v1"
FIELD_BITS = [7, 8, 9, 10, 11]
PANEL_N_PER_FAMILY = 50


def _construct_one(domain, master_seed, family, k, t_max=20000):
    """Construct one curve at curve_ordinal k for the given family
    ('j0' or 'random-ordinary'). Returns a curve record dict, or raises
    ConstructionFailure (caller records and skips)."""
    b = FIELD_BITS[k % len(FIELD_BITS)]
    p, prime_transcript = construct_prime(domain, master_seed, family, b, k)

    if family == "j0":
        # construct_prime's own admission rule already enforces this; this is
        # a direct re-check, not a re-derivation, per the handoff's mandate
        # that the j0 admission rule be "checked directly, not merely
        # assumed from the construction rule succeeding."
        if p % 3 != 1:
            raise ConstructionFailure(
                f"j0 admission-rule re-check failed: p={p} is not 1 (mod 3) "
                f"(construct_prime should have excluded this candidate)")

    for t, a_t, b_t in curve_stream(domain, master_seed, family, p, k, t_start=0, t_max=t_max):
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

        if family == "random-ordinary":
            # Explicit, computed supersingularity check (unlike j0, ordinary
            # is NOT guaranteed here by a congruence alone for a free (A,B)
            # pair): reject supersingular candidates and continue scanning.
            if is_supersingular(N, p):
                continue

        supersingular_flag = is_supersingular(N, p)
        if family == "j0":
            # j0 family is guaranteed ordinary by the p=1(mod 3) congruence
            # alone; assert this is consistent with the direct computed
            # check as a cross-check, never silently trusted.
            assert not supersingular_flag, (
                f"j0 curve at p={p} (1 mod 3 by construction) computed as "
                f"supersingular (N={N}) -- congruence-based guarantee violated, "
                f"this is a construction-implementation defect, not evidence")

        return {
            "family": family, "curve_ordinal": k, "field_bits": b, "p": p,
            "A": A, "B": B, "N": N, "trace": p + 1 - N, "t_used": t,
            "computed_supersingular": supersingular_flag,
            "p_mod_3": p % 3,
            "prime_transcript": prime_transcript,
        }
    raise ConstructionFailure(
        f"no accepted {family} curve found for k={k}, p={p}, b={b} in t<{t_max}")


def build_primary_panel(master_seed, domain=PRIMARY_DOMAIN, n_per_family=PANEL_N_PER_FAMILY):
    panel = {"j0": [], "random-ordinary": []}
    construction_failures = {"j0": [], "random-ordinary": []}
    for family in ("j0", "random-ordinary"):
        for k in range(n_per_family):
            try:
                rec = _construct_one(domain, master_seed, family, k)
                panel[family].append(rec)
            except ConstructionFailure as e:
                construction_failures[family].append({"curve_ordinal": k, "error": str(e)})
    return {"domain": domain, "master_seed": master_seed, "panel": panel,
            "construction_failures": construction_failures,
            "realized_counts": {f: len(panel[f]) for f in panel},
            "declared_counts": {f: n_per_family for f in panel}}

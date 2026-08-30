"""Stage 0: exhaustive curve enumeration, invariant table, matched-pair
census, panel selection, and closed-form pre-registration.

REQUIRED O(p) POINT-COUNTING METHOD (spec `curve_invariants_per_curve`):
for each non-singular (A,B), a SINGLE pass x = 0..p-1 computes:
  (a) t via the character sum: #E(F_p) = p+1+sum_x chi(f(x)), t = p+1-#E(F_p)
      i.e. t = -sum_x chi(f(x));
  (b) Z, the free byproduct count of x with f(x) == 0 in the same sweep;
  (c) j-invariant, O(1), computed once per curve (not in the x-loop);
  (d) order-3 point count, folded into the SAME x-loop by testing psi_3(x)
      for every x in the same range (psi_3 has degree 4, so testing all p
      residues costs O(p), not more).
This gives O(p) per curve, O(p^3) total per prime -- NOT O(p^2) per curve
(which would give O(p^4) total and risk the budget; see the spec's
`curve_enumeration_cost_note`).
"""
from __future__ import annotations

from fp_common import legendre, inverse


def curve_invariants(p: int, A: int, B: int):
    """Single O(p) sweep over x in F_p. Returns
    (t, Z, order3_count, anomaly_count, disc) or None if singular."""
    disc = (4 * pow(A, 3, p) + 27 * pow(B, 2, p)) % p
    if disc == 0:
        return None
    chi_sum = 0
    Z = 0
    order3_sum = 0
    anomaly_count = 0
    A2 = A * A % p
    for x in range(p):
        fx = (x * x * x + A * x + B) % p
        if fx == 0:
            Z += 1
            chi_fx = 0
        else:
            chi_fx = 1 if pow(fx, (p - 1) // 2, p) == 1 else -1
        chi_sum += chi_fx
        # psi_3(x) = 3x^4 + 6Ax^2 + 12Bx - A^2 mod p, tested in the SAME
        # sweep (folding the order-3 root search into the O(p) loop).
        x2 = x * x % p
        x4 = x2 * x2 % p
        psi3 = (3 * x4 + 6 * A * x2 + 12 * B * x - A2) % p
        if psi3 == 0:
            if fx == 0:
                # A genuine order-3 point cannot coincide with a 2-torsion
                # point (f(x0)=0). Log as an anomaly, exclude from the
                # order-3 count -- never silently dropped.
                anomaly_count += 1
            elif chi_fx == 1:
                order3_sum += 2
            # chi_fx == -1: contributes 0, no point over F_p at this root.
    t = -chi_sum
    order3_count = 1 + order3_sum
    j = (1728 * 4 * pow(A, 3, p) % p * inverse(disc, p)) % p
    return t, Z, j, order3_count, anomaly_count, disc


def enumerate_curves(p: int):
    """Enumerate every non-singular (A,B) in F_p x F_p. Returns
    table: dict (A,B) -> dict(t=,Z=,j=,order3_count=,anomaly_count=)
    """
    table = {}
    for A in range(p):
        for B in range(p):
            res = curve_invariants(p, A, B)
            if res is None:
                continue
            t, Z, j, order3_count, anomaly_count, disc = res
            table[(A, B)] = {
                "t": t, "Z": Z, "j": j,
                "order3_count": order3_count,
                "anomaly_count": anomaly_count,
                "disc": disc,
            }
    return table


def group_by_tz(table: dict):
    """Group (A,B) keys by (t,Z) cell. Returns dict (t,Z) -> sorted list of
    (A,B) in lexicographic order (guaranteed by the enumeration order)."""
    cells: dict = {}
    for (A, B), rec in table.items():
        key = (rec["t"], rec["Z"])
        cells.setdefault(key, []).append((A, B))
    for key in cells:
        cells[key].sort()
    return cells


def isomorphic(A: int, B: int, A2: int, B2: int, p: int) -> bool:
    """(A,B) ~ (A2,B2) over F_p iff exists u in F_p^* with A2 = u^4 A mod p
    and B2 = u^6 B mod p (standard criterion for j != 0, 1728). Handles the
    A=0 / B=0 edge cases (which can occur during the full Stage-0
    enumeration, though such curves are never selected into the Stage-1
    panel per `curve_panel_note`) by direct brute-force search over u,
    since the O(1) algebraic shortcut below requires A, A2 both nonzero.
    """
    if A == 0 or A2 == 0:
        if not (A == 0 and A2 == 0):
            return False
        if B == 0 or B2 == 0:
            # disc != 0 requires B != 0 when A == 0 (27B^2 != 0), so this
            # branch is unreachable for genuinely non-singular curves, but
            # guarded explicitly rather than assumed.
            return B == 0 and B2 == 0
        target = (B2 * inverse(B, p)) % p
        for u in range(1, p):
            if pow(u, 6, p) == target:
                return True
        return False
    if B == 0 or B2 == 0:
        if not (B == 0 and B2 == 0):
            return False
        target = (A2 * inverse(A, p)) % p
        for u in range(1, p):
            if pow(u, 4, p) == target:
                return True
        return False
    # Generic case: A, A2, B, B2 all nonzero (j != 0, 1728).
    # u^4 = r := A2/A, u^6 = s := B2/B  =>  u^12 = r^3 = s^2 (necessary),
    # and setting w := s/r = u^2, sufficiency holds iff w is a square (or 0)
    # in F_p: any square root u0 of w automatically satisfies u0^4 = w^2 = r
    # and u0^6 = u0^4 u0^2 = r w = s.
    r = (A2 * inverse(A, p)) % p
    s = (B2 * inverse(B, p)) % p
    if (s * s) % p != (r * r * r) % p:
        return False
    w = (s * inverse(r, p)) % p
    return legendre(w, p) != -1


def matched_pair_census(p: int, cells: dict, table: dict, preferred_ab: set):
    """For every (t,Z) cell with >=2 curves, exhaustively test every pair
    for non-isomorphism (spec `stage0_curve_enumeration_and_prereg` step 3).

    MEMORY NOTE (deviation logged in implementation.md): a first
    implementation materialized every non-isomorphic pair found into a
    Python list. At p=211 this list held ~14.7 MILLION 6-tuples (every
    (t,Z) cell is large -- up to 1260 curves -- so C(cell,2) pairs add up
    fast even though each pairwise isomorphism check is O(1)), driving
    peak RSS to roughly 3 GB and breaching the frozen 1 GB budget. Because
    the completeness claim under test needs only the lexicographically
    smallest qualifying pair (per prime, with an optional preference for a
    pair touching a Z-coverage/sibling curve), this function instead
    tracks two RUNNING MINIMA in a single streaming pass and never
    materializes the full pair list -- the exhaustive-testing REQUIREMENT
    (every pair is still tested) is preserved; only the accumulation
    strategy changed. The full test is still exhaustive: `pairs_tested`
    and `non_iso_pairs_count` per cell, and the process-wide
    `non_iso_pairs_total`, are exact counts obtained by testing every pair.

    A pair qualifies as a matched-pair CANDIDATE iff it is non-isomorphic,
    both curves are non-special (A!=0 and B!=0, i.e. j not in {0,1728},
    per `curve_panel_note`), and the two curves differ in at least one of
    {j, order3_count} (the non-vacuity pre-check). `preferred_ab` is the
    set of (A,B) tuples (sibling + Z-coverage curves) that make a
    candidate touching them PREFERRED, per the spec's forward-referencing
    preference clause (see implementation.md for the declared reading).

    Returns:
      census: dict (t,Z) -> {curve_count, pairs_tested, non_iso_pairs_count,
                              found: bool}
      non_iso_pairs_total: int, exact count of non-isomorphic pairs found
                            across the whole prime (every cell, every pair
                            tested).
      best_overall: lexicographically smallest qualifying candidate tuple
                    (A,B,A2,B2,t,Z), or None.
      best_preferred: lexicographically smallest qualifying candidate that
                      also touches `preferred_ab`, or None.
    """
    census = {}
    non_iso_pairs_total = 0
    best_overall = None
    best_preferred = None

    def is_special(A, B):
        return A == 0 or B == 0

    for (t, Z), curves in cells.items():
        n = len(curves)
        if n < 2:
            continue
        pairs_tested = 0
        non_iso_count = 0
        for i in range(n):
            Ai, Bi = curves[i]
            for jx in range(i + 1, n):
                Aj, Bj = curves[jx]
                pairs_tested += 1
                if isomorphic(Ai, Bi, Aj, Bj, p):
                    continue
                non_iso_count += 1
                non_iso_pairs_total += 1
                if is_special(Ai, Bi) or is_special(Aj, Bj):
                    continue
                rec_i = table[(Ai, Bi)]
                rec_j = table[(Aj, Bj)]
                if rec_i["j"] == rec_j["j"] and rec_i["order3_count"] == rec_j["order3_count"]:
                    continue  # vacuous on both controls
                cand = (Ai, Bi, Aj, Bj, t, Z)
                if best_overall is None or cand < best_overall:
                    best_overall = cand
                if (Ai, Bi) in preferred_ab or (Aj, Bj) in preferred_ab:
                    if best_preferred is None or cand < best_preferred:
                        best_preferred = cand
        census[(t, Z)] = {
            "curve_count": n,
            "pairs_tested": pairs_tested,
            "non_iso_pairs_count": non_iso_count,
            "found": non_iso_count > 0,
        }
    return census, non_iso_pairs_total, best_overall, best_preferred


def closed_form_seven_tuple(p: int, t: int, Z: int):
    """The seven exact closed-form counts of H-MONO-0f9170's `statement`,
    as integer functions of (p,t,Z) alone. Also returns S, N, Zprime, M for
    diagnostics. Raises AssertionError if any divisibility required by the
    closed forms fails (that would itself be a falsifier -- reported, never
    silently coerced with integer floor division)."""
    assert (p - t - Z) % 2 == 0, "S=(p-t-Z)/2 not integral"
    assert (p + t - Z) % 2 == 0, "N=(p+t-Z)/2 not integral"
    S = (p - t - Z) // 2
    N = (p + t - Z) // 2
    if Z == 0:
        Zprime = 0
    elif Z == 1:
        Zprime = 3
    elif Z == 3:
        Zprime = 3
    else:
        raise ValueError(f"Z={Z} out of {{0,1,3}}")

    A1 = S * (S - 1) // 2
    A2 = S * N
    A3 = N * (N - 1) // 2
    A4 = Z * (p - Z) + Z * (Z - 1) // 2

    numerator = p * p + 2 * p - t * t - Zprime
    assert numerator % 2 == 0, "M numerator not even"
    M = numerator // 2 - (p - Z)
    assert M % 2 == 0, "M not even (B1=M/2 not integral)"
    B1 = M // 2
    assert (Zprime - Z) % 2 == 0, "B2=(Z'-Z)/2 not integral"
    B2 = (Zprime - Z) // 2
    B3 = p * (p - 1) // 2 - B1 - B2

    return {
        "A1_identity": A1, "A2_sigma_i": A2, "A3_sigma1sigma2": A3,
        "A4_ramified_A": A4, "B1_block_swap": B1, "B2_ramified_B": B2,
        "B3_four_cycle": B3,
        "S": S, "N": N, "Zprime": Zprime, "M": M,
    }

"""Executor driver for EXP-JINV-bd141d (GOAL-ENDO-001 BATCH-d7e255).

Relation-collection density against the CM fundamental discriminant on a
MATCHED-ORDER family: N = 19507 held identically fixed across every isogeny
class (D = t^2 - 4p = (t-2)^2 - 4N, sweeping t with p = N + t - 1 prime), plus
the separate depth-1 107-volcano contrast at t = 211, p = 19717,
D = -3*107^2. This module implements the frozen contract
`experiments/EXP-JINV-bd141d/specification.yaml` (status approved, approved_by
coordinator, approved_at 2026-08-10). It does not edit
`harness/exp_icinv.py` (source_constraints) and is a NEW driver over
`harness/isogeny_class.py`, `harness/toycurve.py` and
`harness/exp_icinv_fullgroup.py`, exactly as the contract requires.

SPECIFICATION GAP, DISCLOSED RATHER THAN WORKED AROUND. Unlike its sibling
contract EXP-ICINV-4d33aa (whose `inputs.density_grid` section lists explicit
`factor_base_sizes: [4,5,6,7,8,9,10,11,12,13,15,18,22]` and
`target_counts: [100,400,1600]`), EXP-JINV-bd141d's `inputs.density_grid`
gives only `factor_base_rule`, `sweep_required: true` and
`operating_density_target: 0.16666666` -- it never instantiates the swept
factor-base sizes or the target count(s) T anywhere in the approved text, and
no `experiments/EXP-JINV-bd141d/amendments/` directory exists to supply them.
SR5 ("FROZEN GRID... NO additional N, class, density row or seed without a
versioned protocol_amendment filed BEFORE the extra data is generated")
presupposes a frozen grid to compare "additional" rows against; inventing one
here would BE the violation SR5 exists to prevent, not a way to satisfy it.
This module therefore executes everything the frozen contract's OTHER inputs
fully determine (SR1 family re-derivation, per-curve #E and support
certification for the whole family, the |Aut|-arm structural enumeration) and
STOPS, reporting `specification_error` with the exact missing fields, at the
first point that would require inventing `factor_base_sizes` or `T`
(SR4's baseline-identity gate, and the density-swept
decomposition_rate/liftable_density/decomposition_efficiency measurements
`ARM 1` and `ARM 2` depend on). This is reported as data, not as a verdict.

SR3, SEPARATELY. Even had the grid been frozen, SR3 blocks reading or
reporting any |D_0|-arm or |Aut|-arm VERDICT until EXP-INSTR-36c8cf delivers a
two-directional detection floor / false-positive rate at this design's actual
geometry -- which it has not (Phase A stopped at its own falsification
criterion with no interval accepted; Phase B has not run). This module never
computes a TREND-DETECTED / NO-TREND / NOT-RESOLVABLE verdict for either arm.

Toy scale only (p up to ~2^15). No ECDLP claim, no exponent, sota_delta zero.
"""
from __future__ import annotations

import math
import time
from dataclasses import dataclass, field

import sympy

from . import isogeny_class as ic
from .exp_icinv_fullgroup import enumerate_points_table
from .toycurve import EllipticCurve, Point

EXP_ID = "EXP-JINV-bd141d"

MATCHED_N = 19507                       # inputs.family_construction.matched_order_N
AUT_ARM_T = 211                         # inputs.aut_arm_class.t
AUT_ARM_P = 19717                       # inputs.aut_arm_class.p
AUT_ARM_D = -34347                      # inputs.aut_arm_class.discriminant
AUT_ARM_CRATER_EXPECTED = 1
AUT_ARM_FLOOR_EXPECTED = 36             # class_number_crosscheck h(-3*107^2)=36
SEEDS = [20260810, 20260811, 11235813]  # replication.seeds (frozen, unused: no draws made)

# design document's own quoted inventory (retrospective_note /
# inputs.family_construction.expected_inventory_from_design_document), copied
# verbatim from the frozen contract text -- SR1 compares the RE-DERIVATION
# against this, not the other way around.
EXPECTED_INVENTORY = {
    "classes_total": 59,
    "classes_at_f1": 51,
    "distinct_D0_at_f1": 46,
    "D0_hit_twice_count": 5,
    "abs_D0_min": 1299,
    "abs_D0_max": 78027,
    "conductor_arm": [1, 3, 107],
    "curves_total_approx": 2000,
}

# Missing frozen fields (SC-1 / specification_error), disclosed once at import
# time so every downstream artifact can cite the identical text.
MISSING_SPEC_FIELDS = [
    "inputs.density_grid.factor_base_sizes (or an equivalent explicit list): "
    "the contract states only the RULE (exp_icinv.factor_base_fixed_size) and "
    "`sweep_required: true`, never the swept sizes themselves.",
    "inputs.density_grid.target_counts / n_targets: no target-draw count T is "
    "frozen anywhere in the approved text (contrast EXP-ICINV-4d33aa's "
    "explicit target_counts: [100, 400, 1600]).",
]


# --------------------------------------------------------------------------
# SR1 -- family gate
# --------------------------------------------------------------------------


@dataclass
class FamilyMember:
    t: int
    p: int
    D: int
    D0: int
    f: int


def derive_family(N: int) -> list[FamilyMember]:
    """Every (t, p) with N = p + 1 - t, p = N + t - 1 prime, and the class
    ordinary (p does not divide t). D = t^2 - 4p = (t - 2)^2 - 4N, per the
    contract's own identity. The Hasse bound pins the search range: D <= 0 and
    real trace requires t^2 <= 4p, i.e. (t-2)^2 <= 4N.
    """
    bound = int(math.isqrt(N)) * 2 + 5
    out: list[FamilyMember] = []
    for t in range(2 - bound, 2 + bound + 1):
        p = N + t - 1
        if p <= 3:
            continue
        if (t - 2) ** 2 > 4 * N:
            continue
        if not sympy.isprime(p):
            continue
        if t % p == 0:                       # ordinary: p does not divide t
            continue
        D = t * t - 4 * p
        D0, f = ic.fundamental_discriminant(D)
        out.append(FamilyMember(t, p, D, D0, f))
    return out


def family_summary(members: list[FamilyMember]) -> dict:
    f1 = [m for m in members if m.f == 1]
    d0_abs = [abs(m.D0) for m in f1]
    from collections import Counter
    counts = Counter(d0_abs)
    hit_twice = sorted(d for d, n in counts.items() if n == 2)
    conductors = sorted({m.f for m in members})
    return {
        "classes_total": len(members),
        "classes_at_f1": len(f1),
        "distinct_D0_at_f1": len(set(d0_abs)),
        "D0_hit_twice_count": len(hit_twice),
        "D0_hit_twice_values": hit_twice,
        "abs_D0_min": min(d0_abs) if d0_abs else None,
        "abs_D0_max": max(d0_abs) if d0_abs else None,
        "conductor_arm": conductors,
        "curves_total_approx": None,   # filled once curves are actually enumerated (Stage 2)
    }


def sr1_family_gate(N: int, expected: dict) -> dict:
    members = derive_family(N)
    summary = family_summary(members)
    checks = {
        "classes_total": summary["classes_total"] == expected["classes_total"],
        "classes_at_f1": summary["classes_at_f1"] == expected["classes_at_f1"],
        "distinct_D0_at_f1": summary["distinct_D0_at_f1"] == expected["distinct_D0_at_f1"],
        "D0_hit_twice_count": summary["D0_hit_twice_count"] == expected["D0_hit_twice_count"],
        "abs_D0_min": summary["abs_D0_min"] == expected["abs_D0_min"],
        "abs_D0_max": summary["abs_D0_max"] == expected["abs_D0_max"],
        "conductor_arm": summary["conductor_arm"] == expected["conductor_arm"],
    }
    aut_member = next((m for m in members if m.t == AUT_ARM_T), None)
    aut_checks = {
        "aut_arm_class_present": aut_member is not None,
        "aut_arm_p_matches": bool(aut_member and aut_member.p == AUT_ARM_P),
        "aut_arm_D_matches": bool(aut_member and aut_member.D == AUT_ARM_D),
    }
    agrees = all(checks.values()) and all(aut_checks.values())
    return {
        "N": N,
        "members": [vars(m) for m in members],
        "summary": summary,
        "expected_inventory": expected,
        "checks": checks,
        "aut_arm_checks": aut_checks,
        "agrees_with_design_document": bool(agrees),
        "gate": "PASS" if agrees else "PREMISE-FAILED",
    }


# --------------------------------------------------------------------------
# SR1 completeness certificate (Hurwitz-Kronecker) + SR2 support / order
# certification, computed together: both need the FULL per-p enumeration.
# --------------------------------------------------------------------------


@dataclass
class CurveCertificate:
    p: int
    t: int
    a: int
    b: int
    j: int
    aut_order: int
    order_character_sum: int          # ic.CurveRecord.order (independent character sum)
    order_enumerated: int             # len(independently enumerated point set)
    order_matches_N: bool
    r: int                            # # of (x, 0) points -- rational 2-torsion x-roots
    generator_found: bool
    cyclic_table_size: int
    support_equals_enumerated_points: bool
    support_certificate_pass: bool


def certify_class(p: int, t: int, N: int) -> tuple[dict, list[CurveCertificate]]:
    """Full enumeration at p, Hurwitz-Kronecker census, and per-curve order +
    targets_B support certification for every curve of trace t.

    Support certification is EXACT and STRUCTURAL: since N = 19507 is prime,
    Lagrange's theorem forces every non-identity point of a curve with
    #E(F_p) = N to generate the WHOLE group, so the cyclic table built from any
    one point IS targets_B's support ([u]P + [v]G2 with n1 = 1 degenerates to
    [v]G2 over the whole group). This is certified per curve by explicit
    construction (build the cyclic table, compare as a SET against an
    independently enumerated point table that does not share code with the
    table-building loop), not asserted from the N-prime argument alone.
    """
    recs = ic.enumerate_curves(p)
    classes = ic.isogeny_classes(p)
    census = ic.class_census(p, classes)
    census_this = next((c for c in census if c.trace == t), None)
    census_out = {
        "p": p, "trace": t,
        "found": census_this is not None,
        "observed_curves": getattr(census_this, "observed_curves", None),
        "observed_weighted": getattr(census_this, "observed_weighted", None),
        "predicted_weighted": getattr(census_this, "predicted_weighted", None),
        "agrees": bool(getattr(census_this, "agrees", False)),
        "note": getattr(census_this, "note", ""),
    }
    certs: list[CurveCertificate] = []
    for rec in recs:
        if rec.trace != t:
            continue
        E = rec.curve()
        pts = enumerate_points_table(E)      # independent (sqrt-table) enumeration
        order_enum = len(pts)
        # generator: any non-identity point (all are full-order since N prime)
        G = next(iter(q for q in pts if q is not None), None)
        table: list[Point] = [None]
        support_eq = False
        cyclic_size = 0
        if G is not None:
            R = G
            seen = {None}
            steps = 0
            while R is not None and steps <= order_enum + 2:
                table.append(R)
                seen.add(R)
                R = E.add(R, G)
                steps += 1
            cyclic_size = len(table)
            support_eq = bool(set(table) == pts and cyclic_size == order_enum)
        r = sum(1 for q in pts if q is not None and q[1] == 0)
        certs.append(CurveCertificate(
            p=p, t=t, a=rec.a, b=rec.b, j=rec.j, aut_order=rec.aut_order,
            order_character_sum=rec.order, order_enumerated=order_enum,
            order_matches_N=bool(rec.order == order_enum == N),
            r=r, generator_found=G is not None, cyclic_table_size=cyclic_size,
            support_equals_enumerated_points=support_eq,
            support_certificate_pass=bool(support_eq and cyclic_size == N),
        ))
    return census_out, certs


# --------------------------------------------------------------------------
# |Aut| arm structural enumeration -- crater/floor identification by j and
# aut_order ONLY (two_torsion_x_count / ell_subgroup_count(.,2) are prohibited
# as crater/level proxies by the contract's invalidation_rules).
# --------------------------------------------------------------------------


def aut_arm_enumeration(certs: list[CurveCertificate]) -> dict:
    crater = [c for c in certs if c.j == 0]
    floor = [c for c in certs if c.j != 0]
    return {
        "t": AUT_ARM_T, "p": AUT_ARM_P, "D": AUT_ARM_D,
        "total_vertices_enumerated": len(certs),
        "crater_vertices": [vars(c) for c in crater],
        "floor_vertices_count": len(floor),
        "expected_crater_count": AUT_ARM_CRATER_EXPECTED,
        "expected_floor_count_class_number_crosscheck": AUT_ARM_FLOOR_EXPECTED,
        "crater_count_matches_expected": len(crater) == AUT_ARM_CRATER_EXPECTED,
        "total_matches_1_plus_36": len(certs) == 1 + AUT_ARM_FLOOR_EXPECTED,
        "vertex_count_authority": (
            "Hurwitz-Kronecker enumeration via isogeny_class.enumerate_curves "
            "at p=19717 filtered to trace=211, per contract "
            "inputs.aut_arm_class.vertex_count_authority -- NOT the class "
            "number formula, which is quoted above only as a cross-check."),
        "identification_method": (
            "crater = {curves with j == 0} (End = Z[zeta_3], aut_order == 6); "
            "floor = every other curve of the same trace (aut_order == 2). "
            "two_torsion_x_count and ell_subgroup_count(., 2) were NOT used "
            "(contract invalidation_rules)."),
    }


# --------------------------------------------------------------------------
# T1 transport attempt for the |Aut| arm (C-TRANSPORT-CERT) -- reports the
# concrete obstruction rather than fabricating a certificate.
# --------------------------------------------------------------------------


def attempt_transport_certificate(p: int, N: int, ell: int) -> dict:
    """Attempts the crater<->floor Velu ell-isogeny transport C-TRANSPORT-CERT
    requires, using ONLY the machinery already committed in
    harness/isogeny_class.py (velu_odd / find_kernel_generator), and reports
    exactly why it can or cannot proceed.

    harness/isogeny_class.py:find_kernel_generator requires an F_p-RATIONAL
    point of exact order `ell` on the source curve (order // ell must be an
    integer, i.e. ell | #E(F_p)). Here #E(F_p) = N for every curve in this
    class (Tate: F_p-isogenous curves share the same trace, hence the same
    #E(F_p)), and gcd(ell, N) = 1 by the contract's own stated identity -- so
    NO curve in this class carries an F_p-rational point of order ell = 107,
    and this function's kernel construction cannot be invoked on this class at
    all. The genuine crater/floor 107-isogeny (a Galois-stable but not
    pointwise-F_p-rational subgroup of E[107], defined over an extension
    field, whose KERNEL POLYNOMIAL is nonetheless F_p-rational) requires a
    different construction -- e.g. an explicit 107th modular-polynomial or
    division-polynomial factorisation over F_p -- that is not implemented
    anywhere in this codebase today.
    """
    gcd = math.gcd(ell, N)
    return {
        "attempted_construction": "harness.isogeny_class.find_kernel_generator "
                                  "+ velu_odd (the only ell-isogeny machinery "
                                  "committed in this codebase)",
        "gcd_ell_N": gcd,
        "obstruction": (
            f"gcd({ell}, {N}) == {gcd}: with N = #E(F_p) identical on every "
            f"curve of this trace (Tate), no curve carries an F_p-rational "
            f"point of exact order {ell}, so find_kernel_generator(order=N, "
            f"ell={ell}) is UNSATISFIABLE by construction (order % ell != 0 "
            f"for every curve here) and velu_odd cannot be called."
            if gcd == 1 else
            f"gcd({ell}, {N}) == {gcd} != 1; a rational-point kernel "
            f"construction MAY be possible, but was not attempted in this run."
        ),
        "genuine_construction_required": (
            "a kernel-polynomial (Galois-stable, extension-field-kernel) "
            "ell-isogeny construction -- e.g. explicit division-polynomial "
            "factorisation or a degree-107 modular polynomial evaluation over "
            "F_p -- which is NOT implemented in harness/isogeny_class.py or "
            "elsewhere in this codebase as of this run"),
        "status": "UNREACHED",
        "reason": "implementation_gap: required construction absent from the committed instrument",
        "no_certificate_fabricated": True,
    }


# --------------------------------------------------------------------------
# r-composition structural argument + spot verification
# --------------------------------------------------------------------------


def r_structural_argument(N: int) -> dict:
    """N odd (in this contract, N = 19507 is prime, hence odd) forces
    #E(F_p)[2] to be trivial for EVERY curve of order N: a nontrivial rational
    2-torsion point would force 2 | #E(F_p) = N. So the r = #{x : cubic(x)=0}
    stratification variable is IDENTICALLY 0 across the ENTIRE matched-order
    family -- there is exactly one populated stratum, not three. This is a
    consequence of N being odd, verified per curve by the r field already
    computed in `certify_class` (counting (x, 0) points in the independently
    enumerated point set), not asserted without measurement.
    """
    return {
        "N": N, "N_is_odd": bool(N % 2 == 1),
        "claim": "E(F_p)[2] is trivial for every curve of odd order N, so "
                 "r = 0 identically across the whole matched-order family "
                 "(both arms): only one r-stratum is ever populated here.",
        "verified_by": "per-curve r field in CurveCertificate (count of (x,0) "
                       "points in the independently enumerated point set), "
                       "not asserted from the parity argument alone",
    }


__all__ = [
    "EXP_ID", "MATCHED_N", "AUT_ARM_T", "AUT_ARM_P", "AUT_ARM_D",
    "AUT_ARM_CRATER_EXPECTED", "AUT_ARM_FLOOR_EXPECTED", "SEEDS",
    "EXPECTED_INVENTORY", "MISSING_SPEC_FIELDS",
    "FamilyMember", "derive_family", "family_summary", "sr1_family_gate",
    "CurveCertificate", "certify_class", "aut_arm_enumeration",
    "attempt_transport_certificate", "r_structural_argument",
]

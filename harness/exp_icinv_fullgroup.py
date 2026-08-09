"""EXP-ICINV-4d33aa: does the within-class m=3 over-dispersion survive a
CERTIFIED FULL-GROUP target sampler, and does it stratify by r?

This module implements the frozen contract
`experiments/EXP-ICINV-4d33aa/specification.yaml` (status: approved,
approved_by: coordinator, approved_at 2026-08-07). Nothing here may change a
threshold, a prime, a factor-base size, a target count or a seed: every such
value is copied from that file into the FROZEN block below and is used by
reference.

Three commitments this file exists to keep, each of which the contract makes an
invalidation rule:

1.  `harness/exp_icinv.py` IS NOT EDITED AND IS NOT REIMPLEMENTED. Arm A0 gets
    its targets by CALLING the committed `exp_icinv.targets_uniform`, so the
    baseline is bit-exact and every already-committed run stays reproducible
    against the same file. `verify_committed_cyclic_base` re-derives that
    function's base point here ONLY to certify its support, and then proves the
    re-derivation correct against the committed function's own output.

2.  THE EXACT m=3 SUM SET IS COMPUTED ONCE PER (curve, fb_size) AND REUSED for
    every arm, seed and target count. `measure_curve_all_arms` holds the sum set
    in one local variable and scores all arms against it, so the arms differ in
    the sampler and in nothing else. That is a contract requirement, not an
    optimisation.

3.  `exp_icinv.permutation_null` (NULL-C) IS NEVER CALLED. It is a between-class
    MEAN detector and every question here is within-class; using it would make
    the run INVALID. `self_audit_no_null_c` checks the source text of this
    module and its driver and records the answer in the run record.

Sampler arms (contract `inputs.arms_frozen`):
    A0  committed cyclic sampler, requested-count denominator  (the true baseline)
    A1  same cyclic support, exactly T non-identity draws, per-curve denominator
    B   [u]P + [v]G2 over Z/n1 x Z/n2 -- support certified equal to E(F_p)
    C   uniform on [2]E, planted index-2 restriction, NULL-R class only

Toy scale only (p <= 10007). Exact enumeration, not an algorithm. No ECDLP
claim, no exponent, sota_delta zero.
"""
from __future__ import annotations

import hashlib
import math
import statistics
from dataclasses import dataclass, field

from . import exp_icinv as ex
from . import isogeny_class as ic
from .toycurve import EllipticCurve, Point

# --------------------------------------------------------------------------
# FROZEN PARAMETERS -- copied verbatim from the approved contract.
# Changing any value here requires a versioned protocol_amendment under
# experiments/EXP-ICINV-4d33aa/amendments/ filed BEFORE the data is generated
# (stopping rule SR4). They are module constants so that any change is a
# reviewable diff rather than a command-line flag.
# --------------------------------------------------------------------------

EXP_ID = "EXP-ICINV-4d33aa"

FB_SIZES = [4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 15, 18, 22]
TARGET_COUNTS = [100, 400, 1600]
TARGET_COUNT_PRIMARY = 400
SEEDS = [20260807, 20260808, 11235813]
SEED_PRIMARY = 20260807
PRIMES_REQUIRED = [2003, 4001, 6007]
PRIMES_STRETCH = [10007]
ARITY = 3
OPERATING_DENSITY_TARGET = 0.16666666
STRATUM_FLOOR_FOR_VERDICT = 20
STRATUM_FLOOR_FOR_REPORTING = 8

# frozen_decision_rule
PERSISTENCE_VR_THRESHOLD = 1.3          # state_2, "floor of the committed range"
PERSISTENCE_F_THRESHOLD = 0.5           # PERSISTS iff F_p >= 1/2
INCONCLUSIVE_ROW_FRACTION_LIMIT = 1.0 / 3.0
S_ROW_FRACTION = 0.5                    # S_POSITIVE needs >= 1/2 of rows ...
S_PRIME_COUNT = 2                       # ... at >= 2 of the 3 primes
S1_SIGMA_MULTIPLIER = 3.0
S2_WITHIN_FRACTION = 0.6
S3_STRATUM_FACTOR = 2.0
IDENTITY_CHECK_RELATIVE_TOLERANCE = 1e-9

# controls.BASELINE-REPRODUCTION CONTROL (blocking)
BASELINE_VR_BAND = (1.3, 3.6)
BASELINE_OPERATING_TOLERANCE = 0.25
BASELINE_COMMITTED_OPERATING_VR = {4001: 1.918, 6007: 1.591}
BASELINE_PRIMES = [4001, 6007]
# The committed EV-ENDO-10109d runs, READ FROM THEIR OWN RUN RECORDS AT RUN TIME
# and bound by SHA-256. They are deliberately NOT transcribed into this file.
#
# DEFECT DEF-2, DISCLOSED RATHER THAN REPAIRED IN SILENCE. The first version of
# this module carried these rows as hardcoded float literals, and 22 of the 24
# literals had FABRICATED low-order digits: only the two operating rows had been
# copied from a full-precision dump, and the rest were filled in to plausible
# precision from a 4-decimal print. That is a fabricated statistic under
# AGENTS.md rule 9. It did not touch any gate verdict -- the three baseline
# checks read only measured values and the contract's own stated targets 1.918
# and 1.591 -- but it corrupted the `committed_variance_ratio`,
# `delta_vs_committed` and `exact_match_with_committed` columns of
# `baseline-reproduction.json`, and in particular under-reported the exactness of
# the p=4001 reproduction. Every run written with the fabricated literals is
# superseded by a new run id and retained. Reading the numbers from the record
# removes the transcription step, and therefore this failure mode, entirely.
COMMITTED_BASELINE_RUNS = {4001: "RUN-ICINV-p4001-fixed",
                           6007: "RUN-ICINV-p6007-fixed"}
COMMITTED_BASELINE_EXPERIMENT = "EXP-ICINV-55c2d8"


def load_committed_baseline(p: int) -> dict | None:
    """The committed EV-ENDO-10109d density sweep at p, from its own run record.

    NOTE, AND IT IS NOT A DETAIL: the committed p=6007 run used T=500 and the
    factor-base grid {5,6,7,8,9,10,11,12,14,17,21}, NEITHER of which is the grid
    this contract freezes (T=400, {4,...,22}). Rows without a counterpart are
    reported as having none; they are never silently aligned.
    """
    import json
    import os
    rid = COMMITTED_BASELINE_RUNS.get(p)
    if rid is None:
        return None
    repo = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    path = os.path.join(repo, "experiments", COMMITTED_BASELINE_EXPERIMENT,
                        "runs", rid, "raw-result.json")
    with open(path, "rb") as f:
        blob = f.read()
    d = json.loads(blob)["raw"]
    return {
        "run_id": rid,
        "source_path": os.path.relpath(path, repo),
        "source_sha256": hashlib.sha256(blob).hexdigest(),
        "n_targets": d["n_targets"], "trace": d["target_trace"],
        "order": d["order"], "n_curves": d["n_curves"],
        "rows": {r["fb_size"]: r["variance_ratio"] for r in d["rows"]},
        "mean_densities": {r["fb_size"]: r["mean_density_3V_over_order"]
                           for r in d["rows"]},
        "monotonic_decay": d["variance_ratio_decays_monotonically_with_density"],
        "operating_fb": d["row_closest_to_operating_density"]["fb_size"],
        "operating_variance_ratio": d["row_closest_to_operating_density"]["variance_ratio"],
    }

# --------------------------------------------------------------------------
# CONTRACT VERSION 2 -- experiments/EXP-ICINV-4d33aa/amendments/v2.yaml
# (status: filed_before_re_execution, approved_by: coordinator, 2026-08-07)
#
# Everything above stays exactly as version 1 left it so the version-1 run
# records remain readable and their code path remains re-executable. The block
# below is ADDITIVE and implements the amendment's changes A1 and A4.
# --------------------------------------------------------------------------

CONTRACT_VERSION = 2
AMENDMENT_PATH = "experiments/EXP-ICINV-4d33aa/amendments/v2.yaml"

# CHANGE A1. Version 1's SR3 gate compared Arm A0 at p=6007 against a committed
# run measured at T=500 over ELEVEN different factor-base sizes, while the
# contract froze T=400 over thirteen -- so the gate was unsatisfiable by
# construction (CORR-20260807-14431d). The amendment requires the p=6007
# baseline to be RE-MEASURED at the contract's own frozen parameters and
# recorded as a new run under EXP-ICINV-55c2d8, and makes SR3 at p=6007 compare
# Arm A0 against THAT run.
#
# ONLY THE RUN ID APPEARS HERE. Every NUMBER is read from the record at run time
# and bound by sha256 (change A4): a transcribed value cannot be distinguished
# from a measured one by any later reader, which is the defect
# CORR-20260807-a24675 recorded.
BASELINE_RUNS_V2 = {
    4001: ("EXP-ICINV-55c2d8", "RUN-ICINV-p4001-fixed"),
    6007: ("EXP-ICINV-55c2d8", "RUN-ICINV-f09176"),
}

# Retained for reporting only, and DELIBERATELY NOT USED as a reference: the
# committed p=6007 sweep whose parameters differ from the frozen grid. It is
# read and hashed in baseline-provenance.json so a reviewer can see the
# parameters that made version 1's gate unsatisfiable, without any number of it
# entering a comparison.
BASELINE_RUNS_SUPERSEDED_V2 = {
    6007: ("EXP-ICINV-55c2d8", "RUN-ICINV-p6007-fixed"),
}

# The contract's own prose constants for the operating-row sub-check. They are
# stated in `controls.BASELINE-REPRODUCTION CONTROL` and are the ONLY reference
# numbers this experiment takes from text rather than from a record; they are
# reported beside the record-read reference at every prime and NEVER replace it
# (see deviation D8).
CONTRACT_STATED_OPERATING_VR = dict(BASELINE_COMMITTED_OPERATING_VR)


def read_baseline_record(exp_id: str, run_id: str) -> dict | None:
    """A committed saturation-sweep run, READ AND HASHED AT RUN TIME (change A4).

    Reads BOTH `raw-result.json` (the numbers) and `manifest.yaml` (the declared
    inputs: seed and parameters), hashes both, and returns the values as read.
    Nothing here is transcribed and nothing is rounded.
    """
    import json
    import os
    repo = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    raw_path = os.path.join(repo, "experiments", exp_id, "runs", run_id,
                            "raw-result.json")
    man_path = os.path.join(repo, "experiments", exp_id, "runs", run_id,
                            "manifest.yaml")
    if not os.path.exists(raw_path):
        return None
    with open(raw_path, "rb") as f:
        raw_blob = f.read()
    d = json.loads(raw_blob)["raw"]
    declared_seed = None
    declared_params = None
    man_sha = None
    if os.path.exists(man_path):
        import yaml
        with open(man_path, "rb") as f:
            man_blob = f.read()
        man_sha = hashlib.sha256(man_blob).hexdigest()
        man = (yaml.safe_load(man_blob.decode("utf-8")) or {}).get("run") or {}
        declared_seed = (man.get("inputs") or {}).get("seed")
        declared_params = (man.get("inputs") or {}).get("parameters")
    return {
        "run_id": run_id,
        "experiment_id": exp_id,
        "raw_result_path": os.path.relpath(raw_path, repo),
        "raw_result_sha256": hashlib.sha256(raw_blob).hexdigest(),
        "manifest_path": (None if man_sha is None
                          else os.path.relpath(man_path, repo)),
        "manifest_sha256": man_sha,
        "declared_seed_as_read": declared_seed,
        "declared_parameters_as_read": declared_params,
        "n_targets": d["n_targets"],
        "fb_sizes": list(d["fb_sizes"]),
        "trace": d["target_trace"],
        "order": d["order"],
        "n_curves": d["n_curves"],
        "rows": {r["fb_size"]: r["variance_ratio"] for r in d["rows"]},
        "row_verdicts": {r["fb_size"]: r["verdict"] for r in d["rows"]},
        "mean_densities": {r["fb_size"]: r["mean_density_3V_over_order"]
                           for r in d["rows"]},
        "monotonic_decay": d["variance_ratio_decays_monotonically_with_density"],
        "operating_fb": d["row_closest_to_operating_density"]["fb_size"],
        "operating_variance_ratio":
            d["row_closest_to_operating_density"]["variance_ratio"],
    }


def load_baseline_v2(p: int) -> dict | None:
    """The SR3 reference sweep at p under contract version 2, as read."""
    entry = BASELINE_RUNS_V2.get(p)
    if entry is None:
        return None
    rec = read_baseline_record(*entry)
    if rec is None:
        raise FileNotFoundError(
            f"change A1 requires the re-measured baseline {entry[1]} under "
            f"{entry[0]} to exist BEFORE any Arm A0 or Arm B measurement of "
            f"contract version 2; it was not found")
    rec["parameters_match_frozen_grid"] = bool(
        rec["n_targets"] == TARGET_COUNT_PRIMARY and rec["fb_sizes"] == FB_SIZES)
    rec["rows_outside_frozen_band"] = sorted(
        fb for fb, vr in rec["rows"].items()
        if not (BASELINE_VR_BAND[0] <= vr <= BASELINE_VR_BAND[1]))
    rec["reference_itself_inside_band_at_every_row"] = (
        not rec["rows_outside_frozen_band"])
    return rec


def baseline_provenance(primes: list[int]) -> dict:
    """The change-A4 artifact: what was read, from where, and its digest.

    For each prime: the run id read, its declared parameters AS READ from the
    record (never asserted from the contract), the sha256 of every file read,
    and the full row table as read. A reviewer can recompute every reference
    number in this run from these digests without rerunning anything.
    """
    per_prime: dict = {}
    for p in primes:
        entry = BASELINE_RUNS_V2.get(p)
        if entry is None:
            per_prime[str(p)] = {
                "reference": None,
                "why_absent": ("no committed EV-ENDO-10109d density sweep exists at this "
                               "prime, so the contract states no baseline-reproduction "
                               "control here and none is evaluated"),
            }
            continue
        rec = load_baseline_v2(p)
        per_prime[str(p)] = {
            "reference": rec,
            "used_for": ["SR3 row-by-row reproduction comparison",
                         "SR3 operating-row +-0.25 tolerance reference"],
            "frozen_grid_expected": {"n_targets": TARGET_COUNT_PRIMARY,
                                     "fb_sizes": FB_SIZES},
            "parameters_match_frozen_grid": rec["parameters_match_frozen_grid"],
        }
    superseded: dict = {}
    for p, entry in BASELINE_RUNS_SUPERSEDED_V2.items():
        rec = read_baseline_record(*entry)
        if rec is None:
            continue
        superseded[str(p)] = {
            "reference": rec,
            "used_for": [],
            "not_used_because": (
                "its declared parameters, READ FROM THE RECORD, are n_targets "
                f"{rec['n_targets']} over {len(rec['fb_sizes'])} factor-base sizes "
                f"{rec['fb_sizes']}, which is not the grid this contract froze "
                f"(n_targets {TARGET_COUNT_PRIMARY} over {FB_SIZES}). Comparing "
                "against it is what made the version-1 gate unsatisfiable by "
                "construction (CORR-20260807-14431d); amendment change A1 replaces "
                "it with a re-measurement at the frozen parameters. No number from "
                "this record enters any comparison in this run."),
        }
    return {
        "scope": ("change A4: every reference value quoted from a committed record is "
                  "READ FROM THAT RECORD AT RUN TIME and bound by sha256. No reference "
                  "value is transcribed into source at any precision "
                  "(CORR-20260807-a24675)."),
        "amendment": AMENDMENT_PATH,
        "contract_version": CONTRACT_VERSION,
        "per_prime": per_prime,
        "superseded_references_read_but_not_used": superseded,
        "contract_stated_operating_vr": {
            "values": CONTRACT_STATED_OPERATING_VR,
            "provenance": ("quoted from the frozen contract's own prose "
                           "(controls.BASELINE-REPRODUCTION CONTROL), not from a run "
                           "record. Reported beside the record-read reference at every "
                           "prime; the gate uses the record-read value (deviation D8)."),
        },
        "transcribed_reference_values_in_source": 0,
    }


ARMS_PRIMARY_CLASS = ["A0", "A1", "B"]
ARMS_NULLR_CLASS = ["A0", "A1", "B", "C"]

# Hash tags for the index streams. A0's tag belongs to the committed function
# and is NOT reproduced here (A0 calls it). fg1/fg2 are frozen by the contract's
# sampler_construction_frozen step (6); "pl" is this module's declared tag for
# the planted arm, which the contract leaves to the implementation.
TAG_FULLGROUP_U = "fg1"
TAG_FULLGROUP_V = "fg2"
TAG_PLANTED = "pl"
TAG_CYCLIC = "u"                        # the committed function's own tag


# --------------------------------------------------------------------------
# exact point-set enumeration -- INDEPENDENT of toycurve.lift_x
# --------------------------------------------------------------------------


def enumerate_points_table(E: EllipticCurve) -> set[Point]:
    """Every point of E(F_p), by lifting every x with an independent sqrt.

    Deliberately does NOT call `toycurve.lift_x` (which routes through sympy):
    the support certificate must not be checked by the same code path that
    builds the objects it certifies. Instead a full table of squares mod p is
    built once and inverted, which is a different algorithm with different
    failure modes. `certify_group_structure` additionally cross-checks the
    resulting count against `isogeny_class.trace_of_frobenius`, an exact
    character sum -- a third independent path.
    """
    p, a, b = E.p, E.a, E.b
    root: dict[int, int] = {}
    for y in range((p + 1) // 2):
        root.setdefault(y * y % p, y)
    pts: set[Point] = {None}
    for x in range(p):
        rhs = (x * x % p * x + a * x + b) % p
        if rhs == 0:
            pts.add((x, 0))
            continue
        y = root.get(rhs)
        if y is not None:
            pts.add((x, y))
            pts.add((x, p - y))
    return pts


def enumerate_points_liftx(E: EllipticCurve) -> set[Point]:
    """The same set via `toycurve.lift_x`, for the agreement cross-check."""
    pts: set[Point] = {None}
    for x in range(E.p):
        P = E.lift_x(x)
        if P is not None:
            pts.add(P)
            pts.add(E.negate(P))
    return pts


def cyclic_table(E: EllipticCurve, G: Point) -> list[Point]:
    """[O, G, 2G, ...] until the identity returns. One addition per element.

    The construction is itself the proof that the result is a cyclic subgroup
    of order len(table): it closes on O after exactly that many steps.
    """
    table: list[Point] = [None]
    Q = G
    while Q is not None:
        table.append(Q)
        Q = E.add(Q, G)
    return table                        # table[k] == [k]G for k < len(table)


# --------------------------------------------------------------------------
# group structure: proposed cheaply, CERTIFIED by enumeration
# --------------------------------------------------------------------------


@dataclass
class GroupCert:
    p: int
    a: int
    b: int
    r: int
    order: int
    order_character_sum: int
    order_enumerated: int
    n1: int
    n2: int
    n2_proposed: int
    n2_proposal_corrected: bool
    exponent_certified: bool            # [n2]Q = O for every Q (via ord(P) | n2)
    n1_divides_n2: bool
    bijection_certified: bool           # {[u]P+[v]G2} == E(F_p) as sets
    order_agrees: bool                  # enumeration == character sum == p+1-t
    liftx_agreement_checked: bool
    liftx_agreement: bool | None
    G2: Point = None
    P: Point = None


def propose_exponent(E: EllipticCurve, order: int, n_points: int = 40) -> int:
    """lcm of the exact orders of the first `n_points` liftable points.

    Contract step (2): cheap, NOT TRUSTED, certified by step (5).
    """
    e = 1
    seen = 0
    for x in range(E.p):
        Q = E.lift_x(x)
        if Q is None:
            continue
        o = ex._point_order(E, Q, order)
        e = e * o // math.gcd(e, o)
        seen += 1
        if seen >= n_points or e == order:
            break
    return e


def exact_exponent(E: EllipticCurve, order: int) -> int:
    """The group exponent from EVERY liftable point. Used only when the cheap
    proposal fails to certify; the fallback is recorded, never silent."""
    e = 1
    for x in range(E.p):
        Q = E.lift_x(x)
        if Q is None:
            continue
        o = ex._point_order(E, Q, order)
        e = e * o // math.gcd(e, o)
        if e == order:
            break
    return e


def find_point_of_order(E: EllipticCurve, order: int, target: int) -> Point:
    """The first liftable point of exact order `target`."""
    for x in range(E.p):
        Q = E.lift_x(x)
        if Q is None:
            continue
        if ex._point_order(E, Q, order) == target:
            return Q
    return None


def find_quotient_generator(E: EllipticCurve, S: set[Point], n1: int) -> Point:
    """First liftable Q whose image in E/<G2> has order exactly n1.

    Contract step (4): test [i]Q in S for i = 1..n1 and keep the first Q whose
    image order is exactly n1.
    """
    for x in range(E.p):
        Q = E.lift_x(x)
        if Q is None:
            continue
        R = Q
        img = None
        for i in range(1, n1 + 1):
            if R in S:
                img = i
                break
            R = E.add(R, Q)
        if img == n1:
            return Q
    return None


def certify_group_structure(rec: ic.CurveRecord, points: set[Point],
                            check_liftx: bool = False) -> GroupCert:
    """(n1, n2) proposed cheaply and then CERTIFIED by explicit enumeration."""
    E = rec.curve()
    order = rec.order
    t_char = ic.trace_of_frobenius(rec.p, rec.a, rec.b)
    order_char = rec.p + 1 - t_char
    r = ex.two_torsion_x_count(rec.p, rec.a, rec.b)

    n2_proposed = propose_exponent(E, order)
    n2 = n2_proposed
    corrected = False
    G2 = find_point_of_order(E, order, n2)
    if G2 is None:
        n2 = exact_exponent(E, order)
        corrected = n2 != n2_proposed
        G2 = find_point_of_order(E, order, n2)
    n1 = order // n2

    S_table = cyclic_table(E, G2) if G2 is not None else [None]
    S = set(S_table)
    if n1 > 1:
        P = find_quotient_generator(E, S, n1)
    else:
        P = None                        # contract step (4): cyclic group
    # ord(P) | n2 -- with the bijection below this certifies exponent == n2
    exponent_ok = (P is None) or (E.mul(n2, P) is None)

    liftx_ok = None
    if check_liftx:
        liftx_ok = points == enumerate_points_liftx(E)

    return GroupCert(
        p=rec.p, a=rec.a, b=rec.b, r=r, order=order,
        order_character_sum=order_char, order_enumerated=len(points),
        n1=n1, n2=n2, n2_proposed=n2_proposed, n2_proposal_corrected=corrected,
        exponent_certified=bool(exponent_ok),
        n1_divides_n2=bool(n2 % n1 == 0),
        bijection_certified=False,      # filled by build_fullgroup_table
        order_agrees=bool(order == order_char == len(points)),
        liftx_agreement_checked=bool(check_liftx), liftx_agreement=liftx_ok,
        G2=G2, P=P)


def build_fullgroup_table(E: EllipticCurve, cert: GroupCert,
                          S_table: list[Point]) -> list[Point]:
    """[u]P + [v]G2 for all (u, v), computed incrementally: #E additions.

    Index k = u * n2 + v, so the table is a direct-access sampler for Arm B.
    """
    out: list[Point] = []
    base: Point = None
    for _ in range(cert.n1):
        for v in range(cert.n2):
            out.append(E.add(base, S_table[v]))
        if cert.P is not None:
            base = E.add(base, cert.P)
    return out


# --------------------------------------------------------------------------
# the committed cyclic sampler's base point, re-derived and then PROVED
# --------------------------------------------------------------------------


@dataclass
class CyclicBaseCert:
    gen_order: int
    G: Point
    replication_verified: bool          # predicted stream == committed output
    draws_compared: int
    all_committed_targets_in_support: bool
    committed_returned: dict            # seed -> {T: n_returned}


def replicate_cyclic_base(E: EllipticCurve, order: int,
                          max_candidates: int = 200) -> tuple[Point, int]:
    """The base point `exp_icinv.targets_uniform` selects, re-derived.

    This is a RE-DERIVATION FOR CERTIFICATION ONLY. It is never used to produce
    Arm A0's targets (the committed function is called for those), and its
    correctness is not assumed: `verify_committed_cyclic_base` proves the
    re-derivation reproduces the committed function's output element by element.
    The loop mirrors the committed one exactly, including its x start of 2 and
    its early stop when a full-order point is found.
    """
    G, gen_order, x = None, 0, 2
    tried = 0
    while tried < max_candidates and gen_order < order and x < E.p:
        P = E.lift_x(x)
        x += 1
        if P is None:
            continue
        tried += 1
        o = ex._point_order(E, P, order)
        if o > gen_order:
            G, gen_order = P, o
    return G, gen_order


def verify_committed_cyclic_base(E: EllipticCurve, order: int,
                                 committed: dict[int, dict[int, list[Point]]],
                                 G: Point, gen_order: int,
                                 g_table: list[Point],
                                 draws_to_compare: int = 200) -> CyclicBaseCert:
    """Prove the re-derived (G, gen_order) is the committed function's own.

    Two independent checks:
      (i)  every point the committed function returned lies in <G>  -- this is
           exactly the support claim, and it is checked on ALL returned points;
      (ii) the first `draws_to_compare` hashed indices predict the committed
           output ELEMENT BY ELEMENT, which pins gen_order exactly (a wrong
           multiple would desynchronise the stream immediately).
    """
    support = set(g_table)
    all_in = all(Q in support
                 for per_t in committed.values()
                 for lst in per_t.values()
                 for Q in lst)
    ok = True
    compared = 0
    for seed, per_t in committed.items():
        biggest_T = max(per_t)
        got = per_t[biggest_T]
        predicted: list[Point] = []
        for i in range(min(draws_to_compare, biggest_T)):
            h = int(hashlib.sha256(f"{seed}:{TAG_CYCLIC}:{i}".encode()).hexdigest(), 16)
            R = g_table[h % gen_order] if gen_order else None
            if R is not None:
                predicted.append(R)
        n = len(predicted)
        compared += n
        if got[:n] != predicted:
            ok = False
    return CyclicBaseCert(
        gen_order=gen_order, G=G, replication_verified=bool(ok and all_in),
        draws_compared=compared, all_committed_targets_in_support=bool(all_in),
        committed_returned={s: {t: len(v) for t, v in d.items()}
                            for s, d in committed.items()})


# --------------------------------------------------------------------------
# samplers
# --------------------------------------------------------------------------


def targets_A0(E: EllipticCurve, order: int, T: int, seed: int) -> list[Point]:
    """THE COMMITTED SAMPLER, CALLED NOT REIMPLEMENTED (contract arms_frozen).

    Retains both known defects on purpose: identity draws are lost, and the
    caller divides by the REQUESTED T. That is what makes A0 the true baseline.
    """
    return ex.targets_uniform(E, order, T, seed)


def targets_A1(g_table: list[Point], gen_order: int, T: int, seed: int
               ) -> tuple[list[Point], int]:
    """Same cyclic support as A0, rejection-sampled to exactly T non-identity
    draws, denominator = targets actually used. Isolates the denominator defect.

    Uses the committed function's own hash stream (`seed:u:i`) so the first
    draws coincide with A0's exactly and the A0 -> A1 delta is the denominator
    and nothing else.
    """
    out: list[Point] = []
    i = 0
    while len(out) < T:
        h = int(hashlib.sha256(f"{seed}:{TAG_CYCLIC}:{i}".encode()).hexdigest(), 16)
        R = g_table[h % gen_order]
        if R is not None:
            out.append(R)
        i += 1
    return out, i


def targets_B(fg_table: list[Point], n1: int, n2: int, T: int, seed: int
              ) -> tuple[list[Point], int]:
    """[u]P + [v]G2 with u uniform on [0,n1), v uniform on [0,n2).

    The modular reduction of a 256-bit hash by a modulus below 2^14 is
    non-uniform by under 2^-240. DECLARED (contract step 6), not hidden.
    """
    out: list[Point] = []
    i = 0
    while len(out) < T:
        u = int(hashlib.sha256(f"{seed}:{TAG_FULLGROUP_U}:{i}".encode()).hexdigest(), 16) % n1
        v = int(hashlib.sha256(f"{seed}:{TAG_FULLGROUP_V}:{i}".encode()).hexdigest(), 16) % n2
        R = fg_table[u * n2 + v]
        if R is not None:
            out.append(R)
        i += 1
    return out, i


def targets_C(two_table: list[Point], T: int, seed: int
              ) -> tuple[list[Point], int]:
    """Uniform on [2]E, the index-2 subgroup. PLANTED SIGNAL arm."""
    m = len(two_table)
    out: list[Point] = []
    i = 0
    while len(out) < T:
        w = int(hashlib.sha256(f"{seed}:{TAG_PLANTED}:{i}".encode()).hexdigest(), 16) % m
        R = two_table[w]
        if R is not None:
            out.append(R)
        i += 1
    return out, i


# --------------------------------------------------------------------------
# exact m=3 sum set -- ONE computation per (curve, fb_size)
# --------------------------------------------------------------------------


SUMSET_COMPUTATIONS = 0
"""Counts every exact sum-set enumeration this process performs.

The contract makes recomputing a sum set per arm an INVALIDATION RULE, so the
count is evidence rather than telemetry: a run records it, and the run record
asserts `sumset_computations == n_curves * n_fb_sizes`. Each measurement row
carries the index of the single computation it was scored against, so a
reviewer can verify the sharing from the raw table alone.
"""


def sum_sets_m2_m3(E: EllipticCurve, fb: list[int]) -> tuple[set, set]:
    """(2V, 3V) by exact enumeration.

    Algorithmically identical to `exp_icinv.decomposition_rate_m3` and to
    `run_saturation.decomposition_rate_m3_with_size` (which is what
    EV-ENDO-10109d measured); it returns the SETS instead of a hit count so
    that one computation can serve every arm, seed and target count.
    `verify_sumset_against_committed` checks the equivalence on real data.
    """
    global SUMSET_COMPUTATIONS
    SUMSET_COMPUTATIONS += 1
    pts: list[Point] = []
    for x in fb:
        P = E.lift_x(x)
        if P is not None:
            pts.append(P)
            pts.append(E.negate(P))
    two = set()
    for i in range(len(pts)):
        for jx in range(i, len(pts)):
            S = E.add(pts[i], pts[jx])
            if S is not None:
                two.add(S)
    three = set()
    for S in two:
        for R in pts:
            Tt = E.add(S, R)
            if Tt is not None:
                three.add(Tt)
    return two, three


def verify_sumset_against_committed(E: EllipticCurve, fb: list[int],
                                    targets: list[Point], three: set,
                                    two: set) -> dict:
    """Independent check that scoring against the shared set reproduces the
    committed functions' hit counts on the same inputs."""
    h3, t3 = ex.decomposition_rate_m3(E, fb, targets)
    h2, t2 = ex.decomposition_rate_m2(E, fb, targets)
    return {
        "committed_m3_hits": h3, "shared_m3_hits": sum(1 for q in targets if q in three),
        "committed_m2_hits": h2, "shared_m2_hits": sum(1 for q in targets if q in two),
        "trials": t3, "agrees": bool(
            h3 == sum(1 for q in targets if q in three) and
            h2 == sum(1 for q in targets if q in two) and t2 == t3 == len(targets)),
    }


# --------------------------------------------------------------------------
# NULL-B statistics (the ONLY null this experiment uses)
# --------------------------------------------------------------------------


def wilson_hilferty_band(df: int, z: float = 1.96) -> tuple[float, float]:
    """The acceptance band `exp_icinv.binomial_null_verdict` uses, as numbers.

    Same formula, recomputed so the band can be REPORTED with every ratio
    (contract controls block and the CHI-SQUARE TAIL check) instead of being
    parsed out of a detail string. `nullb` asserts the recomputed verdict equals
    the committed function's verdict, so the two can never drift.
    """
    if df <= 0:
        return float("nan"), float("nan")
    lo = df * (1 - 2 / (9 * df) - z * math.sqrt(2 / (9 * df))) ** 3
    hi = df * (1 - 2 / (9 * df) + z * math.sqrt(2 / (9 * df))) ** 3
    return lo, hi


def nullb(name: str, hits: list[int], trials: int) -> dict:
    """NULL-B via the COMMITTED `exp_icinv.binomial_null_verdict`, plus its band.

    The verdict string is the committed function's; the chi-square statistic and
    both Wilson-Hilferty bounds are recomputed here for reporting and are
    cross-checked against that verdict. A mismatch raises rather than being
    reported, because it would mean this module and the committed statistic
    disagree about what was measured.
    """
    v = ex.binomial_null_verdict(name, hits, trials)
    df = len(hits) - 1
    lo, hi = wilson_hilferty_band(df)
    stat = df * v.ratio if v.null_variance > 0 else float("nan")
    if v.null_variance > 0 and df > 0:
        recomputed = ("over-dispersed" if stat > hi
                      else "under-dispersed" if stat < lo else "invariant")
        if recomputed != v.verdict:
            raise AssertionError(
                f"band recomputation disagrees with the committed verdict: "
                f"{recomputed} vs {v.verdict} ({v.detail})")
    return {
        "name": name, "n": v.n_curves, "mean": v.mean, "variance": v.variance,
        "null_variance": v.null_variance, "ratio": v.ratio,
        "verdict": v.verdict, "detail": v.detail,
        "chi2": stat, "df": df, "band_lo": lo, "band_hi": hi,
        "trials": trials,
    }


def stratified_stats(hits: list[int], strata: list[int], trials: int,
                     name: str) -> dict:
    """Everything the contract's variance decomposition needs, in one place.

    Reports each stratum against BOTH nulls, and says which is which:
      * `own_null`    -- the stratum's own mubar, which is what the per-cell
                         verdict and its acceptance band must use (controls
                         block: "the band must be recomputed per cell from that
                         cell's own df");
      * `pooled_null` -- the class-wide v = mubar(1-mubar)/T, which is the only
                         null under which the STEP-2 identity is an identity.
    Reporting one and calling it the other is how an identity check gets faked.
    """
    n = len(hits)
    rates = [h / trials for h in hits]
    pooled = nullb(name, hits, trials)
    v_pooled = pooled["null_variance"]

    out: dict = {"pooled": pooled, "strata": {}, "n": n}
    idx: dict[int, list[int]] = {}
    for i, rv in enumerate(strata):
        idx.setdefault(rv, []).append(i)

    for rv, positions in sorted(idx.items()):
        sub = [hits[i] for i in positions]
        sub_rates = [rates[i] for i in positions]
        entry = {
            "r": rv, "n": len(sub),
            "mean_rate": sum(sub_rates) / len(sub_rates),
            "variance": statistics.variance(sub_rates) if len(sub) > 1 else 0.0,
            "own_null": nullb(f"{name}|r={rv}", sub, trials) if len(sub) > 1 else None,
        }
        entry["ratio_pooled_null"] = (entry["variance"] / v_pooled
                                      if v_pooled > 0 else None)
        entry["stratum_class"] = ("verdict_eligible" if len(sub) >= STRATUM_FLOOR_FOR_VERDICT
                                  else "weak_stratum" if len(sub) >= STRATUM_FLOOR_FOR_REPORTING
                                  else "insufficient_stratum")
        out["strata"][str(rv)] = entry

    s1 = out["strata"].get("1")
    s3 = out["strata"].get("3")
    if s1 and s3 and s1["n"] > 1 and s3["n"] > 1 and v_pooled > 0:
        n1c, n3c = s1["n"], s3["n"]
        var1, var3 = s1["variance"], s3["variance"]
        mu1, mu3 = s1["mean_rate"], s3["mean_rate"]
        w = n3c / n
        within_ss = (n1c - 1) * var1 + (n3c - 1) * var3
        between = n * w * (1 - w) * (mu1 - mu3) ** 2
        lhs = pooled["ratio"]
        rhs = (within_ss / (n - 1) + between / (n - 1)) / v_pooled
        rel = abs(lhs - rhs) / abs(lhs) if lhs else abs(lhs - rhs)
        within_var = within_ss / (n - 2)
        vr_within = within_var / v_pooled
        wlo, whi = wilson_hilferty_band(n - 2)
        wstat = (n - 2) * vr_within
        out["decomposition"] = {
            "n1c": n1c, "n3c": n3c, "w": w,
            "mu_1": mu1, "mu_3": mu3, "delta_mu": mu1 - mu3,
            "delta_mu_se": math.sqrt(v_pooled * (1 / n1c + 1 / n3c)),
            "VR_1_pooled_null": var1 / v_pooled, "VR_3_pooled_null": var3 / v_pooled,
            "within_term": (within_ss / (n - 1)) / v_pooled,
            "between_term": (between / (n - 1)) / v_pooled,
            "VR_pooled_measured": lhs, "VR_pooled_reconstructed": rhs,
            "identity_relative_error": rel,
            "identity_holds": bool(rel <= IDENTITY_CHECK_RELATIVE_TOLERANCE),
            "VR_within": vr_within, "VR_within_df": n - 2,
            "VR_within_chi2": wstat, "VR_within_band_lo": wlo,
            "VR_within_band_hi": whi,
            "VR_within_inside_band": bool(wlo <= wstat <= whi),
            "mechanism_accounting": {
                "excess": lhs - 1.0,
                "fraction_within_r3": (((n3c - 1) * var3 / (n - 1)) / v_pooled) / (lhs - 1.0)
                if abs(lhs - 1.0) > 1e-12 else None,
                "fraction_within_r1": (((n1c - 1) * var1 / (n - 1)) / v_pooled) / (lhs - 1.0)
                if abs(lhs - 1.0) > 1e-12 else None,
                "fraction_between": ((between / (n - 1)) / v_pooled) / (lhs - 1.0)
                if abs(lhs - 1.0) > 1e-12 else None,
            },
        }
    else:
        out["decomposition"] = None
        out["decomposition_absent_reason"] = (
            "the class carries a single r stratum (r constant), so the two-stratum "
            "identity is not defined; this is expected on the NULL-R class")
    return out


# --------------------------------------------------------------------------
# birthday check (secondary, behind the exact certificate)
# --------------------------------------------------------------------------


def birthday_expectation(support: int, draws: int) -> tuple[float, float]:
    """(E[distinct], sd) for `draws` uniform draws from `support` cells."""
    if support <= 0 or draws <= 0:
        return 0.0, 0.0
    q = (1 - 1 / support) ** draws
    mean = support * (1 - q)
    var = (support * (support - 1) * (1 - 2 / support) ** draws
           + support * q - (support * q) ** 2)
    return mean, math.sqrt(max(var, 0.0))


# --------------------------------------------------------------------------
# per-curve measurement -- ONE sum set per (curve, fb_size), ALL arms scored
# --------------------------------------------------------------------------


@dataclass
class CurvePackage:
    """Everything about one curve that does not depend on the factor base."""
    rec: ic.CurveRecord
    cert: GroupCert
    base: CyclicBaseCert
    coverage: dict                      # arm -> certificate dict
    targets: dict                       # (arm, seed, T) -> list[Point]
    targets_used: dict                  # (arm, seed, T) -> int
    draws_consumed: dict
    arms: list[str] = field(default_factory=list)
    notes: list[str] = field(default_factory=list)


def build_curve_package(rec: ic.CurveRecord, arms: list[str], *,
                        planted: bool, check_liftx: bool = False,
                        seeds: list[int] | None = None,
                        target_counts: list[int] | None = None) -> CurvePackage:
    """Certify the curve's structure and every arm's support, then draw targets.

    Order matters: the support certificate is computed BEFORE any rate is
    measured, so a curve whose sampler is not what it claims is caught before
    it can contribute a number.
    """
    seeds = SEEDS if seeds is None else seeds
    target_counts = TARGET_COUNTS if target_counts is None else target_counts
    E = rec.curve()
    pts = enumerate_points_table(E)
    cert = certify_group_structure(rec, pts, check_liftx=check_liftx)

    S_table = cyclic_table(E, cert.G2)
    fg_table = build_fullgroup_table(E, cert, S_table)
    cert.bijection_certified = bool(len(fg_table) == rec.order
                                    and set(fg_table) == pts)

    # ---- Arm A support: the COMMITTED sampler's own cyclic subgroup ----
    G, gen_order = replicate_cyclic_base(E, rec.order)
    g_table = cyclic_table(E, G) if G is not None else [None]

    targets: dict = {}
    used: dict = {}
    draws: dict = {}
    committed_raw: dict[int, dict[int, list[Point]]] = {}
    for seed in seeds:
        committed_raw[seed] = {}
        for T in target_counts:
            tg = targets_A0(E, rec.order, T, seed)
            committed_raw[seed][T] = tg
            targets[("A0", seed, T)] = tg
            used[("A0", seed, T)] = T          # THE DEFECT A0 RETAINS: requested T
            draws[("A0", seed, T)] = T
    base = verify_committed_cyclic_base(E, rec.order, committed_raw, G,
                                        gen_order, g_table)

    two_table: list[Point] = []
    doubling_image: set = set()
    cyclic_two_agrees = None
    if planted and rec.order % 2 == 0:
        # [2]E directly as the image of the doubling map, which is a subgroup
        # because doubling is a homomorphism; its index is #E[2] = 1 + r, so on
        # an r = 1 curve it is exactly 2. Deterministically indexed so the
        # hashed draw is reproducible.
        doubling_image = {E.mul(2, Q) for Q in pts}
        two_table = [None] + sorted(q for q in doubling_image if q is not None)
        if cert.n1 == 1 and cert.G2 is not None:
            # independent cross-check by a different construction
            cyclic_two_agrees = set(cyclic_table(E, E.mul(2, cert.G2))) == doubling_image

    for seed in seeds:
        for T in target_counts:
            if "A1" in arms:
                tg, di = targets_A1(g_table, gen_order, T, seed)
                targets[("A1", seed, T)] = tg
                used[("A1", seed, T)] = len(tg)
                draws[("A1", seed, T)] = di
            if "B" in arms:
                tg, di = targets_B(fg_table, cert.n1, cert.n2, T, seed)
                targets[("B", seed, T)] = tg
                used[("B", seed, T)] = len(tg)
                draws[("B", seed, T)] = di
            if "C" in arms and two_table:
                tg, di = targets_C(two_table, T, seed)
                targets[("C", seed, T)] = tg
                used[("C", seed, T)] = len(tg)
                draws[("C", seed, T)] = di

    # ---- EXACT SUPPORT CERTIFICATES, per arm ----
    coverage = {}
    coverage["A"] = _support_cert(
        "A", set(g_table), pts, rec.order,
        predicted_size=cert.n2,
        predicted_fraction=1.0 / cert.n1,
        equals_predicted=bool(len(g_table) == gen_order and gen_order == cert.n2
                              and set(g_table) <= pts),
        extra={"gen_order": gen_order,
               "gen_order_equals_exponent": bool(gen_order == cert.n2),
               "predicted_subgroup_test": "cyclic subgroup <G> closes on O after "
                                          "exactly gen_order additions, is contained in "
                                          "the enumerated E(F_p), and gen_order equals "
                                          "the certified exponent n2 (index n1)"})
    if "B" in arms:
        coverage["B"] = _support_cert(
            "B", set(fg_table), pts, rec.order,
            predicted_size=rec.order, predicted_fraction=1.0,
            equals_predicted=bool(set(fg_table) == pts and len(fg_table) == rec.order),
            extra={"predicted_subgroup_test": "set equality against the independently "
                                              "enumerated full point set"})
    if "C" in arms and two_table:
        coverage["C"] = _support_cert(
            "C", set(two_table), pts, rec.order,
            predicted_size=rec.order // 2, predicted_fraction=0.5,
            equals_predicted=bool(len(two_table) == rec.order // 2
                                  and set(two_table) <= pts
                                  and cert.r == 1
                                  and cyclic_two_agrees is not False),
            extra={"predicted_subgroup_test":
                   "support is the image of the doubling homomorphism (hence a subgroup); "
                   "index certified as #E[2] = 1 + r = 2 with r from "
                   "exp_icinv.two_torsion_x_count, size checked against #E/2, and (when "
                   "n1 = 1) cross-checked by set equality against <[2]G2> built by "
                   "repeated addition",
                   "cyclic_construction_agrees": cyclic_two_agrees})

    notes = []
    if cert.n2_proposal_corrected:
        notes.append("cheap exponent proposal (lcm of 40 point orders) was WRONG and was "
                     f"corrected by exact computation: {cert.n2_proposed} -> {cert.n2}")
    if cert.n1 == 1 and "B" in arms:
        same = set(g_table) == set(fg_table)
        notes.append(f"cyclic curve (n1=1): CYCLIC-CURVE IDENTITY CONTROL supports_equal={same}")
    if planted and not two_table:
        notes.append("PLANTED ARM NOT APPLIED: the curve has odd order, so no index-2 "
                     "subgroup exists; recorded rather than silently skipped")
    return CurvePackage(rec=rec, cert=cert, base=base, coverage=coverage,
                        targets=targets, targets_used=used, draws_consumed=draws,
                        arms=list(arms), notes=notes)


def _support_cert(arm: str, support: set, pts: set, order: int, *,
                  predicted_size: int, predicted_fraction: float,
                  equals_predicted: bool, extra: dict) -> dict:
    cert = {
        "arm": arm,
        "support_size": len(support),
        "coverage_fraction": len(support) / order,
        "predicted_support_size": predicted_size,
        "predicted_coverage_fraction": predicted_fraction,
        "support_subset_of_curve": bool(support <= pts),
        "support_equals_predicted": bool(equals_predicted),
        "coverage_matches_prediction": bool(
            abs(len(support) / order - predicted_fraction) < 1e-12),
    }
    cert.update(extra)
    return cert


def measure_curve_all_arms(pkg: CurvePackage, fb_sizes: list[int],
                           verify_sumset: bool = False) -> list[dict]:
    """THE SHARED-SUM-SET LOOP.

    For each factor-base size the exact m=3 (and free m=2) sum set is computed
    EXACTLY ONCE and every arm, seed and target count is scored against that one
    object. This function is the contract's `cost_sharing_requirement`: there is
    no code path in this module that computes a sum set per arm.
    """
    E = pkg.rec.curve()
    rows: list[dict] = []
    for fb_size in fb_sizes:
        fb = ex.factor_base_fixed_size(E, fb_size)
        two, three = sum_sets_m2_m3(E, fb)              # <-- ONE computation
        sumset_id = SUMSET_COMPUTATIONS
        checked = None
        if verify_sumset:
            key = ("A0", SEED_PRIMARY, TARGET_COUNT_PRIMARY)
            checked = verify_sumset_against_committed(E, fb, pkg.targets[key],
                                                      three, two)
        for arm in pkg.arms:
            for seed in SEEDS:
                for T in TARGET_COUNTS:
                    key = (arm, seed, T)
                    if key not in pkg.targets:
                        continue
                    tg = pkg.targets[key]
                    h3 = sum(1 for q in tg if q in three)
                    h2 = sum(1 for q in tg if q in two)
                    rows.append({
                        "a": pkg.rec.a, "b": pkg.rec.b, "r": pkg.cert.r,
                        "n1": pkg.cert.n1, "n2": pkg.cert.n2,
                        "order": pkg.rec.order,
                        "arm": arm, "fb_size": fb_size, "fb_actual": len(fb),
                        "seed": seed, "T": T,
                        "targets_requested": T,
                        "targets_returned": len(tg),
                        "targets_distinct": len(set(tg)),
                        "denominator": pkg.targets_used[key],
                        "hits_m3": h3, "hits_m2": h2,
                        "sumset_3v": len(three), "sumset_2v": len(two),
                        "density_3v": len(three) / pkg.rec.order,
                        "sumset_computation_index": sumset_id,
                        "committed_hit_check": checked if (arm == "A0" and
                                                           seed == SEED_PRIMARY and
                                                           T == TARGET_COUNT_PRIMARY) else None,
                    })
    return rows


# --------------------------------------------------------------------------
# aggregation
# --------------------------------------------------------------------------


def aggregate_rows(rows: list[dict], arm: str, seed: int, T: int,
                   fb_size: int) -> dict | None:
    """Class-level statistics for one (arm, seed, T, fb_size) cell."""
    sel = [r for r in rows if r["arm"] == arm and r["seed"] == seed
           and r["T"] == T and r["fb_size"] == fb_size]
    if not sel:
        return None
    hits = [r["hits_m3"] for r in sel]
    strata = [r["r"] for r in sel]
    denominators = {r["denominator"] for r in sel}
    stats = stratified_stats(hits, strata, T, f"rate_m3[{arm}]")
    dens = [r["density_3v"] for r in sel]
    eff = [r["hits_m3"] / r["denominator"] * r["order"]
           / ex.max_sums(r["fb_size"], ARITY) for r in sel]
    resid = [r["hits_m3"] / r["denominator"] - r["density_3v"] for r in sel]
    v = stats["pooled"]["null_variance"]
    hits_m2 = [r["hits_m2"] for r in sel]
    out = {
        "arm": arm, "seed": seed, "T": T, "fb_size": fb_size,
        "n_curves": len(sel),
        "denominators_uniform": len(denominators) == 1,
        "denominator_values": sorted(denominators),
        "mean_density_3V_over_order": statistics.mean(dens),
        "mean_sumset_3v": statistics.mean([r["sumset_3v"] for r in sel]),
        "stats": stats,
        "decomposition_efficiency_mean": statistics.mean(eff),
        "decomposition_efficiency_variance": statistics.variance(eff) if len(eff) > 1 else 0.0,
        "residual_after_3V_prediction_variance": statistics.variance(resid) if len(resid) > 1 else 0.0,
        "residual_over_binomial_ratio": (statistics.variance(resid) / v
                                         if v > 0 and len(resid) > 1 else None),
        "m2": nullb(f"rate_m2[{arm}]", hits_m2, T),
    }
    return out


def operating_row(rows_by_fb: dict[int, dict]) -> int | None:
    """The density row nearest |3V|/#E = 1/3! (contract operating_density_target)."""
    if not rows_by_fb:
        return None
    return min(rows_by_fb,
               key=lambda fb: abs(rows_by_fb[fb]["mean_density_3V_over_order"]
                                  - OPERATING_DENSITY_TARGET))


def monotonic_decay(ordered: list[float]) -> bool:
    """`run_saturation.run`'s own definition, so the baseline comparison uses
    the committed notion of decay and not a new one."""
    return all(ordered[i] >= ordered[i + 1] - 1e-9
               for i in range(len(ordered) - 1)
               if ordered[i] != float("inf") and ordered[i + 1] != float("inf"))


# --------------------------------------------------------------------------
# tail checks (all five, always, whatever the verdict) -- contract tail_checks
# --------------------------------------------------------------------------


def tail_checks(rows: list[dict], cells: dict, coverage: list[dict],
                seed: int, T: int) -> dict:
    extreme = {}
    degenerate = []
    for arm in sorted({r["arm"] for r in rows}):
        for fb in sorted({r["fb_size"] for r in rows}):
            sel = [r for r in rows if r["arm"] == arm and r["fb_size"] == fb
                   and r["seed"] == seed and r["T"] == T]
            if not sel:
                continue
            def _row(r):
                return {"a": r["a"], "b": r["b"], "r": r["r"],
                        "n1": r["n1"], "n2": r["n2"],
                        "rate": r["hits_m3"] / r["denominator"],
                        "hits": r["hits_m3"], "denominator": r["denominator"],
                        "sumset_3v": r["sumset_3v"],
                        "coverage_fraction": _coverage_of(coverage, r["a"], r["b"], arm)}
            srt = sorted(sel, key=lambda r: r["hits_m3"] / r["denominator"])
            extreme[f"{arm}|fb={fb}"] = {
                "smallest_3": [_row(r) for r in srt[:3]],
                "largest_3": [_row(r) for r in srt[-3:]],
            }
            for r in sel:
                rate = r["hits_m3"] / r["denominator"]
                if rate in (0.0, 1.0):
                    degenerate.append({**_row(r), "arm": arm, "fb_size": fb,
                                       "density_3v": r["density_3v"]})
    cov_tail = {}
    for arm in sorted({c["arm"] for c in coverage}):
        vals = [c["coverage_fraction"] for c in coverage if c["arm"] == arm]
        cov_tail[arm] = {
            "min": min(vals), "max": max(vals), "n": len(vals),
            "curves_with_n1_gt_2": [
                {"a": c["a"], "b": c["b"], "r": c["r"], "n1": c["n1"],
                 "n2": c["n2"], "coverage_fraction": c["coverage_fraction"]}
                for c in coverage if c["arm"] == arm and c["n1"] > 2],
        }
    chi = []
    for key, cell in sorted(cells.items()):
        st = cell["stats"]["pooled"]
        chi.append({"cell": key, "ratio": st["ratio"], "chi2": st["chi2"],
                    "df": st["df"], "band_lo": st["band_lo"],
                    "band_hi": st["band_hi"], "verdict": st["verdict"],
                    "near_band_edge": bool(
                        st["df"] > 0 and st["null_variance"] > 0 and
                        (abs(st["chi2"] - st["band_hi"]) / st["band_hi"] < 0.10 or
                         abs(st["chi2"] - st["band_lo"]) / max(st["band_lo"], 1e-12) < 0.10))})
    return {
        "extreme_curve_check": extreme,
        "degenerate_rate_check": {"n": len(degenerate), "rows": degenerate},
        "coverage_tail": cov_tail,
        "chi_square_tail": chi,
        "t_scaling_tail": None,          # filled by t_scaling
    }


def _coverage_of(coverage: list[dict], a: int, b: int, arm: str):
    key = "A" if arm in ("A0", "A1") else arm
    for c in coverage:
        if c["a"] == a and c["b"] == b and c["arm"] == key:
            return c["coverage_fraction"]
    return None


def t_scaling(rows: list[dict], arm: str, seed: int, fb_size: int) -> dict:
    """VR at T in {100, 400, 1600} on the SAME sum sets, plus the linear
    prediction the contract's T-SCALING TAIL asks for."""
    out = {}
    for T in TARGET_COUNTS:
        cell = aggregate_rows(rows, arm, seed, T, fb_size)
        out[str(T)] = None if cell is None else cell["stats"]["pooled"]["ratio"]
    v100, v400, v1600 = out["100"], out["400"], out["1600"]
    pred = None
    if None not in (v100, v400) and all(math.isfinite(x) for x in (v100, v400)):
        # VR(T) ~= 1 + T*sigma^2/(mubar(1-mubar)): linear in T, so the T=1600
        # value is predicted by the line through the T=100 and T=400 points.
        slope = (v400 - v100) / (400 - 100)
        pred = v100 + slope * (1600 - 100)
    ratio_growth = (v1600 / v100 if (v100 not in (None, 0)
                                     and v1600 is not None
                                     and math.isfinite(v100) and math.isfinite(v1600))
                    else None)
    return {
        "arm": arm, "seed": seed, "fb_size": fb_size, "vr_by_T": out,
        "linear_prediction_at_1600_from_100_and_400": pred,
        "observed_at_1600": v1600,
        "departure_from_linear": (None if pred is None or v1600 is None
                                  else v1600 - pred),
        "vr1600_over_vr100": ratio_growth,
        "fitted_slope_of_VR_minus_1_vs_T": (
            None if None in (v100, v400, v1600) else
            _fit_slope([(T, out[str(T)] - 1.0) for T in TARGET_COUNTS
                        if out[str(T)] is not None and math.isfinite(out[str(T)])])),
    }


def _fit_slope(pts: list[tuple[float, float]]) -> float | None:
    if len(pts) < 2:
        return None
    n = len(pts)
    sx = sum(x for x, _ in pts)
    sy = sum(y for _, y in pts)
    sxx = sum(x * x for x, _ in pts)
    sxy = sum(x * y for x, y in pts)
    den = n * sxx - sx * sx
    return None if den == 0 else (n * sxy - sx * sy) / den


# --------------------------------------------------------------------------
# self audit
# --------------------------------------------------------------------------


def self_audit_no_null_c() -> dict:
    """Mechanical evidence that NULL-C is not used anywhere in this experiment."""
    import os
    here = os.path.dirname(os.path.abspath(__file__))
    # The call pattern is ASSEMBLED AT RUNTIME so that this auditor's own source
    # does not contain the string it searches for and count itself as a hit.
    name_token = "permutation" + "_null"
    call_token = name_token + "("
    findings = {}
    for name in ("exp_icinv_fullgroup.py", "run_fullgroup.py"):
        path = os.path.join(here, name)
        try:
            with open(path, encoding="utf-8") as f:
                text = f.read()
        except FileNotFoundError:
            findings[name] = "missing"
            continue
        findings[name] = {"mentions": text.count(name_token),
                          "call_sites": text.count(call_token)}
    return {"forbidden_statistic": f"exp_icinv.{name_token} (NULL-C)",
            "call_sites_total": sum(v["call_sites"] for v in findings.values()
                                    if isinstance(v, dict)),
            "imported_into_this_module": bool(
                getattr(ex, name_token, None) is not None
                and name_token in globals()),
            "per_file": findings}


def committed_file_digest(relpath: str = "harness/exp_icinv.py") -> dict:
    """Prove `harness/exp_icinv.py` is byte-identical to its committed version."""
    import os
    import subprocess
    repo = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    with open(os.path.join(repo, relpath), "rb") as f:
        worktree = hashlib.sha256(f.read()).hexdigest()
    try:
        blob = subprocess.run(["git", "show", f"HEAD:{relpath}"], cwd=repo,
                              capture_output=True)
        committed = hashlib.sha256(blob.stdout).hexdigest() if blob.returncode == 0 else None
    except Exception as exc:                                # pragma: no cover
        committed = f"error: {exc}"
    return {"path": relpath, "worktree_sha256": worktree,
            "head_sha256": committed,
            "byte_identical": bool(committed == worktree)}


__all__ = [
    "EXP_ID", "FB_SIZES", "TARGET_COUNTS", "SEEDS", "PRIMES_REQUIRED",
    "GroupCert", "CyclicBaseCert", "CurvePackage",
    "enumerate_points_table", "enumerate_points_liftx", "cyclic_table",
    "certify_group_structure", "build_fullgroup_table",
    "replicate_cyclic_base", "verify_committed_cyclic_base",
    "targets_A0", "targets_A1", "targets_B", "targets_C",
    "sum_sets_m2_m3", "verify_sumset_against_committed",
    "nullb", "wilson_hilferty_band", "stratified_stats",
    "birthday_expectation", "build_curve_package", "measure_curve_all_arms",
    "aggregate_rows", "operating_row", "monotonic_decay", "tail_checks",
    "t_scaling", "self_audit_no_null_c", "committed_file_digest",
    # contract version 2 (amendment changes A1 and A4)
    "CONTRACT_VERSION", "AMENDMENT_PATH", "BASELINE_RUNS_V2",
    "BASELINE_RUNS_SUPERSEDED_V2", "CONTRACT_STATED_OPERATING_VR",
    "read_baseline_record", "load_baseline_v2", "baseline_provenance",
]

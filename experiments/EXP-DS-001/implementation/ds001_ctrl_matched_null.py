#!/usr/bin/env python3
"""RUN-DS-001-ctrl-matched-null driver (CTRL-RT047-MATCHED-NULL).

Binds to:
  experiments/EXP-DS-001/specification.v2.yaml               (immutable parent, v2)
  experiments/EXP-DS-001/controls/CTRL-RT047-MATCHED-NULL.yaml (operative control)
  experiments/EXP-DS-001/amendments/v2_ctrl_matched_null.yaml

Single cell: bits=20, B=64, m=4, seed=101.

WHAT THIS RUN DOES
------------------
It runs the SAME search kernels (`ds001_driver.naive_search`,
`ds001_driver.split_search`, `ds001_driver.build_claw_table`) against a
MATCHED-ALGORITHM NULL OBJECT: the additive cyclic group Z/NZ with
N = 753848, which is exactly the full curve group order #E(F_p) recorded in
RUN-DS-001-ctrl-unplanted.  The object carries no curve, no x-coordinate, no
point at infinity, no summation polynomial and no Semaev structure.  The
composition law, the group order, the factor-base cardinality and its closure
under negation, the arity m = 4, the target count, the seed, the stopping rule
and the cost identity are all preserved.

ALGORITHM INVARIANCE.  `naive_search`, `split_search` and `build_claw_table`
are IMPORTED UNCHANGED from ds001_driver and are byte-identical to the code
that produced RUN-DS-001-ctrl-unplanted.  The only thing that differs across
arms is the OBJECT handed to them: an `AdditiveGroupZN` duck-type in place of
`harness.toycurve.EllipticCurve`, and residue elements in place of curve
points.  The search kernels are not parameterized, subclassed, monkeypatched
or copied.

The per-arm harvest WRAPPER (`harvest`) is a copy of
`ds001_ctrl_unplanted.harvest_real` with instrumentation added, because the
control protocol mandates per-arm fields (n_enum, per_arm_capped_attempt_count,
peak_rss_bytes, claw_table_build_count) that `harvest_real` does not emit.  The
exact unified diff is computed at runtime and archived in raw-result.json under
`algorithm_invariance.harvest_wrapper_diff`.  The same wrapper serves EVERY
arm, so amortization and accounting are identical across objects.

ds001_driver.py and ds001_ctrl_unplanted.py are NOT modified by this run.

Records observations only.  Interprets nothing, classifies nothing against the
frozen disposition map, and assigns no hypothesis status.
"""
from __future__ import annotations

import argparse
import difflib
import hashlib
import inspect
import json
import os
import random
import resource
import sys
import time
from pathlib import Path
from typing import Any, Optional

HERE = Path(__file__).resolve().parent
REPO = HERE.parents[2]
for _p in (str(REPO), str(HERE)):
    if _p not in sys.path:
        sys.path.insert(0, _p)

import ds001_driver as DRV                     # noqa: E402  search kernels, UNCHANGED
import ds001_ctrl_unplanted as CTRL            # noqa: E402  BATCH-020 driver, UNCHANGED
from harness.toycurve import EllipticCurve, generate_instance, _seed_int  # noqa: E402

RUN_ID = "RUN-DS-001-ctrl-matched-null"
TASK_ID = "TASK-20260801-005"
BATCH_ID = "BATCH-021"
GOAL_ID = "GOAL-ECDLP-001"
SUB_GOAL_ID = "SG-ECDLP-001"
CONTROL_ID = "CTRL-RT047-MATCHED-NULL"
AMENDMENT_ID = "PA-DS-001-v2-ctrl-matched-null"
NULL_OBJECT_ID = "NULL-DS-ADDITIVE-Z753848"

PARENT_CONTRACT = "experiments/EXP-DS-001/specification.v2.yaml"
PARENT_CONTRACT_SHA256_EXPECTED = (
    "898304bfc9225062e68c5d7977d1490cad95957e856847676ef7ae1423a5636a")
CONTROL_CONTRACT = "experiments/EXP-DS-001/controls/CTRL-RT047-MATCHED-NULL.yaml"
AMENDMENT_PATH = "experiments/EXP-DS-001/amendments/v2_ctrl_matched_null.yaml"
APPROVAL_RECEIPT = ("coordination/goals/GOAL-ECDLP-001/batches/BATCH-021/"
                    "archives/TASK-20260801-004/snapshot_commit_receipt.json")

CELL = {"bits": 20, "B": 64, "m": 4, "seed": 101}
RELATIONS_TARGET = 200
SMOOTHNESS_ABORT = False
PER_TARGET_CAP_SECONDS = 5.0          # DECLARED in CTRL-RT047-MATCHED-NULL
PLANT_DIVISOR = 1.0                   # NO LIVE PLANT IN BATCH-021
MATCHED_NULL_MODULUS = 753848         # must equal #E(F_p) of the BATCH-020 cell
MATCHED_NULL_TARGET_COUNT = 200

# Reference figures quoted from the archived BATCH-020 package (RT047-B1
# discharging requirement 2).  Quoted, never recomputed into a new claim.
BATCH020_REFERENCE = {
    "R_real_wall": 0.0322,
    "R_real_unit": 0.0147,
    "R_null_legacy_wall": 111.445,
    "R_null_legacy_unit": 0.9569,
    "proxy_disagreement_real_factor": 2.20,
    "proxy_disagreement_null_factor": 116.5,
    "source_run": "RUN-DS-001-ctrl-unplanted",
}

LOG: list[str] = []


def log(msg: str) -> None:
    line = f"[{time.strftime('%H:%M:%S')}] {msg}"
    LOG.append(line)
    print(line, flush=True)


def rss_bytes() -> int:
    ru = resource.getrusage(resource.RUSAGE_SELF).ru_maxrss
    return ru if sys.platform == "darwin" else ru * 1024


# ==========================================================================
# THE MATCHED NULL OBJECT - Z/NZ under addition
# ==========================================================================

class AdditiveGroupZN:
    """The additive cyclic group Z/NZ, presented with the EXACT method surface
    the frozen search kernels consume from `EllipticCurve`: `.add`, `.negate`.

    Element encoding (CTRL-RT047-MATCHED-NULL.matched_null_object):
      * a nonzero residue g in [1, N) is the 1-tuple (g,);
      * the identity (residue 0) is `None`, mirroring the curve's point at
        infinity, so that the kernels' `if s is None: N = 0` branches and the
        `rem in S` membership tests behave exactly as on the curve;
      * `pt[0]` yields the residue, which is what `encode_intermediate`
        consumes in place of a curve x-coordinate.

    There is no curve, no y-coordinate, no summation polynomial, no degree,
    no resultant and no smoothness-bearing algebraic intermediate here.
    """

    def __init__(self, N: int):
        self.N = int(N)
        self.p = int(N)          # name kept only for duck-type parity
        self.object_id = NULL_OBJECT_ID

    @staticmethod
    def elem(g: int, N: int):
        g %= N
        return None if g == 0 else (g,)

    def negate(self, pt):
        if pt is None:
            return None
        return AdditiveGroupZN.elem(self.N - pt[0], self.N)

    def add(self, P, Q):
        if P is None:
            return Q
        if Q is None:
            return P
        return AdditiveGroupZN.elem(P[0] + Q[0], self.N)

    def order(self) -> int:
        return self.N

    def is_in_group(self, pt) -> bool:
        if pt is None:
            return True
        return isinstance(pt, tuple) and len(pt) == 1 and 0 < pt[0] < self.N


def build_matched_null_factor_base(N: int, seed: int, size_unsigned: int) -> dict:
    """Draw the 64 unsigned residues and build the 128-element signed base.

    Rejection classes are exactly CTRL-RT047-MATCHED-NULL.factor_base_construction:
      (a) zero; (b) duplicate of an accepted g; (c) 2g == 0 mod N (g = N/2,
      its own negation); (d) N-g already accepted.
    Draw order is recorded so the base regenerates byte-for-byte from seed 101.
    """
    rng = random.Random(_seed_int(seed, "matched_null_factor_base"))
    accepted: list[int] = []
    accepted_set: set[int] = set()
    rejections = {"a_zero": 0, "b_duplicate": 0,
                  "c_self_negation": 0, "d_negation_already_accepted": 0}
    rejected_values: dict[str, list[int]] = {k: [] for k in rejections}
    draws = 0
    while len(accepted) < size_unsigned:
        g = rng.randrange(N)
        draws += 1
        if g == 0:
            rejections["a_zero"] += 1
            rejected_values["a_zero"].append(g)
            continue
        if g in accepted_set:
            rejections["b_duplicate"] += 1
            rejected_values["b_duplicate"].append(g)
            continue
        if (2 * g) % N == 0:
            rejections["c_self_negation"] += 1
            rejected_values["c_self_negation"].append(g)
            continue
        if (N - g) % N in accepted_set:
            rejections["d_negation_already_accepted"] += 1
            rejected_values["d_negation_already_accepted"].append(g)
            continue
        accepted.append(g)
        accepted_set.add(g)

    signed_residues: list[int] = []
    for g in accepted:
        signed_residues.append(g)
        signed_residues.append((N - g) % N)
    canonical = ",".join(str(g) for g in signed_residues)
    signed = [AdditiveGroupZN.elem(g, N) for g in signed_residues]
    return {
        "modulus": N,
        "size_unsigned": len(accepted),
        "size_signed": len(signed_residues),
        "unsigned_in_draw_order": accepted,
        "signed_residues_in_order": signed_residues,
        "signed_elements": signed,
        "closed_under_negation": sorted(signed_residues) == sorted(
            [(N - g) % N for g in signed_residues]),
        "all_distinct": len(set(signed_residues)) == len(signed_residues),
        "rng_seed_label": "matched_null_factor_base",
        "master_seed": seed,
        "draw_order_description": (
            "rng = random.Random(_seed_int(101, 'matched_null_factor_base')); "
            "repeat g = rng.randrange(N) until 64 unsigned residues are "
            "accepted under rejection classes (a)-(d) in that order; the "
            "signed base is [g1, N-g1, g2, N-g2, ...] in acceptance order."),
        "total_draws": draws,
        "rejection_counts": rejections,
        "rejected_values": rejected_values,
        "factor_base_sha256": hashlib.sha256(canonical.encode()).hexdigest(),
        "factor_base_canonical_serialization": (
            "comma-joined decimal residues of the 128 signed elements in order"),
        "structured_base_used": False,
        "curve_x_coordinates_reused": False,
    }


def matched_null_target_stream(N: int, seed: int, count: int) -> tuple[list, dict]:
    """`count` uniform random residues from [0, N).  NOT planted m-sums."""
    rng = random.Random(_seed_int(seed, "matched_null_targets"))
    t0 = time.perf_counter()
    residues = [rng.randrange(N) for _ in range(count)]
    gen_wall = time.perf_counter() - t0
    targets = [AdditiveGroupZN.elem(g, N) for g in residues]
    canonical = ",".join(str(g) for g in residues)
    return targets, {
        "mode": "matched_null_uniform_random",
        "rng_seed_label": "matched_null_targets",
        "master_seed": seed,
        "modulus": N,
        "targets_generated": len(residues),
        "zero_residues_drawn": sum(1 for g in residues if g == 0),
        "target_stream_sha256": hashlib.sha256(canonical.encode()).hexdigest(),
        "generation_wall_seconds_not_charged_to_arms": gen_wall,
        "planted_m_sums_used": False,
    }


# ==========================================================================
# CERTIFICATES - independent verifier paths
# ==========================================================================

def make_cert_additive(N: int, relation: dict) -> dict:
    return {
        "kind": "decomposition",
        "group": {"modulus": N, "law": "additive", "object_id": NULL_OBJECT_ID},
        "target": int(relation["target"][0]),
        "summands": [int(s[0]) for s in relation["summands"]],
        "method": relation.get("method"),
    }


def independent_verify_additive(cert: dict, fb_signed_residues: set, m: int
                                ) -> tuple[bool, str]:
    """Recompute the sum in Z/NZ from the certificate ALONE.

    Uses plain Python integer arithmetic; touches no solver state, no
    AdditiveGroupZN instance and no ds001_driver function.
    """
    if cert.get("kind") != "decomposition":
        return False, "wrong_kind"
    g = cert.get("group") or {}
    N = int(g.get("modulus", 0))
    if N <= 0:
        return False, "missing_modulus"
    if g.get("law") != "additive":
        return False, "wrong_law"
    summands = cert.get("summands")
    if not isinstance(summands, list):
        return False, "missing_summands"
    if len(summands) != m:
        return False, "arity_mismatch"
    acc = 0
    for s in summands:
        s = int(s)
        if not (0 < s < N):
            return False, "summand_out_of_range"
        if s not in fb_signed_residues:
            return False, "summand_not_in_factor_base"
        acc = (acc + s) % N
    if acc != int(cert["target"]) % N:
        return False, "sum_mismatch"
    return True, "ok"


def make_cert_legacy_null(relation: dict, seed: int, bits: int, B: int, m: int) -> dict:
    return {
        "kind": "null_relation",
        "null_object_id": DRV.NULL_SPEC_ID,
        "params": {"seed": seed, "bits": bits, "B": B, "m": m},
        "xs": [int(x) for x in relation["xs"]],
        "target_tag": int(relation["target_tag"]),
        "method": relation.get("method"),
    }


def independent_verify_legacy_null(cert: dict, fb_xs_set: set, m: int
                                   ) -> tuple[bool, str]:
    """Re-evaluate the null membership oracle from the certificate alone.

    The blake2b acceptance predicate is re-derived inline here rather than by
    calling ds001_driver.null_full_hit, so this is an independent code path.
    """
    if cert.get("kind") != "null_relation":
        return False, "wrong_kind"
    xs = cert.get("xs")
    if not isinstance(xs, list) or len(xs) != m:
        return False, "arity_mismatch"
    for x in xs:
        if int(x) not in fb_xs_set:
            return False, "element_not_in_factor_base"
    pr = cert["params"]
    seed, bits, B = int(pr["seed"]), int(pr["bits"]), int(pr["B"])
    tag = int(cert["target_tag"])
    msg = (f"{cert['null_object_id']}|{seed}|{bits}|{B}|{m}|full|{tag}|"
           f"{','.join(str(int(x)) for x in xs)}").encode()
    v = int.from_bytes(hashlib.blake2b(msg, digest_size=8).digest(), "big")
    modulus = max(B ** (m // 2 - 1), 2)
    if v % modulus != 0:
        return False, "oracle_rejects_tuple"
    return True, "ok"


# ==========================================================================
# ARM HARVEST - instrumented copy of ds001_ctrl_unplanted.harvest_real
# ==========================================================================

def harvest(
    G,
    fb_signed: list,
    method: str,
    targets: list,
    relations_target: int,
    wall_budget: float,
    plant_divisor: float,
    backend_object: str,
    cert_fn,
) -> dict:
    """One arm.  `G` is the OBJECT (EllipticCurve or AdditiveGroupZN); the
    search kernels are ds001_driver's, unchanged.

    Amortization parity: for `method == "split"` the claw table is built ONCE,
    before the target loop, exactly as ds001_ctrl_unplanted.harvest_real does
    for the real split arm.  claw_table_build_count is recorded so a
    per-attempt rebuild cannot hide.
    """
    bits, B, m = CELL["bits"], CELL["B"], CELL["m"]
    rss_before = rss_bytes()
    t_arm0 = time.perf_counter()
    reported_wall = 0.0
    reported_units = 0.0
    n_enum = 0
    n_usable = 0
    attempted = 0
    capped = 0
    arm_budget_truncated = 0
    rel_wall_samples: list[float] = []
    certs: list[dict] = []
    table = None
    peak_table = 0
    table_build_reported = 0.0
    table_build_count = 0

    if method == "split":
        seg0 = time.perf_counter()
        table, entries, _ = DRV.build_claw_table(
            G, fb_signed, m // 2, DRV.frozen_D(bits, m), B, SMOOTHNESS_ABORT,
            time.perf_counter() + wall_budget * 0.4,
        )
        seg = time.perf_counter() - seg0
        table_build_reported = seg / plant_divisor
        reported_wall += table_build_reported
        peak_table = entries
        table_build_count = 1

    stop_reason = "target_stream_exhausted"
    for T in targets:
        if n_usable >= relations_target:
            stop_reason = "relations_target_reached"
            break
        if time.perf_counter() - t_arm0 >= wall_budget:
            stop_reason = "arm_wall_budget"
            break
        seg0 = time.perf_counter()
        cap_deadline = seg0 + PER_TARGET_CAP_SECONDS
        arm_deadline = t_arm0 + wall_budget
        deadline = min(arm_deadline, cap_deadline)
        cap_is_binding_deadline = cap_deadline <= arm_deadline
        if method == "naive":
            ar = DRV.naive_search(G, fb_signed, T, m, deadline,
                                  lambda mm: DRV.charge_backend_units(mm))
        else:
            assert table is not None
            ar = DRV.split_search(G, fb_signed, T, m, bits, B, table, deadline,
                                  lambda mm: DRV.charge_backend_units(mm),
                                  SMOOTHNESS_ABORT)
            peak_table = max(peak_table, ar.peak_table_entries)
        seg = time.perf_counter() - seg0
        reported_wall += seg / plant_divisor
        reported_units += ar.backend_units / plant_divisor
        n_enum += ar.n_enumerations
        attempted += 1
        if cap_is_binding_deadline and seg >= PER_TARGET_CAP_SECONDS - 1e-6:
            capped += 1
        elif (not cap_is_binding_deadline) and time.perf_counter() >= arm_deadline:
            arm_budget_truncated += 1
        if ar.found and ar.relation and not ar.incomplete:
            n_usable += 1
            rel_wall_samples.append(seg / plant_divisor)
            certs.append(cert_fn(ar.relation))
    else:
        if n_usable >= relations_target:
            stop_reason = "relations_target_reached"

    true_wall = time.perf_counter() - t_arm0
    overhead_reported = reported_wall - sum(rel_wall_samples)
    return {
        "method": method,
        "backend_object": backend_object,
        "backend_id": DRV.BACKEND_ID,
        "plant_divisor_applied_live": plant_divisor,
        "plant_applied": plant_divisor != 1.0,
        "reported_wall_seconds": reported_wall,
        "true_elapsed_wall_seconds": true_wall,
        "reported_backend_units": reported_units,
        "n_enum": n_enum,
        "n_usable_relations": n_usable,
        "n_usable": n_usable,
        "attempted_targets": attempted,
        "success_count": n_usable,
        "empirical_success_probability": n_usable / max(attempted, 1),
        "hit_relations_target": n_usable >= relations_target,
        "stop_reason": stop_reason,
        "peak_claw_table_entries": peak_table,
        "claw_table_build_count": table_build_count,
        "claw_table_amortized_once": (table_build_count == 1) if method == "split" else None,
        "table_build_reported_wall_seconds": table_build_reported,
        "table_build_measurable": True,
        "per_relation_wall_samples": rel_wall_samples,
        "reported_overhead_wall_seconds": overhead_reported,
        "per_target_cap_seconds": PER_TARGET_CAP_SECONDS,
        "per_arm_capped_attempt_count": capped,
        "per_arm_arm_budget_truncated_attempt_count": arm_budget_truncated,
        "peak_rss_bytes": rss_bytes(),
        "peak_rss_bytes_label": (
            "process high-water mark (ru_maxrss) sampled at the end of this "
            "arm; monotone across the run, therefore an upper bound for the "
            "arm and not an arm-exclusive figure"),
        "peak_rss_bytes_at_arm_start": rss_before,
        "_certs": certs,
    }


def harvest_legacy_null(
    fb_xs: list,
    method: str,
    relations_target: int,
    wall_budget: float,
    plant_divisor: float,
) -> dict:
    """Legacy NULL-DS-RANDOM-MULTIHOMOGENEOUS arm, carried for DISCLOSURE ONLY.

    Instrumented copy of ds001_ctrl_unplanted.harvest_null.  The legacy null's
    split kernel builds its table INSIDE every attempt; that is a property of
    ds001_driver.null_split_search, which is imported unchanged and not
    repaired here.  It is recorded rather than fixed.
    """
    bits, B, m, seed = CELL["bits"], CELL["B"], CELL["m"], CELL["seed"]
    rss_before = rss_bytes()
    t_arm0 = time.perf_counter()
    reported_wall = 0.0
    reported_units = 0.0
    n_enum = 0
    n_usable = 0
    tag = 0
    capped = 0
    arm_budget_truncated = 0
    peak_table = 0
    rel_wall_samples: list[float] = []
    certs: list[dict] = []
    stop_reason = "attempt_cap"
    while True:
        if n_usable >= relations_target:
            stop_reason = "relations_target_reached"
            break
        if time.perf_counter() - t_arm0 >= wall_budget:
            stop_reason = "arm_wall_budget"
            break
        if tag > relations_target * 80:
            stop_reason = "attempt_cap_no_progress"
            break
        tag += 1
        seg0 = time.perf_counter()
        cap_deadline = seg0 + PER_TARGET_CAP_SECONDS
        arm_deadline = t_arm0 + wall_budget
        deadline = min(arm_deadline, cap_deadline)
        cap_is_binding_deadline = cap_deadline <= arm_deadline
        if method == "naive":
            ar = DRV.null_naive_search(fb_xs, seed, bits, B, m, tag, deadline,
                                       lambda mm: DRV.charge_backend_units(mm))
        else:
            ar = DRV.null_split_search(fb_xs, seed, bits, B, m, tag, deadline,
                                       lambda mm: DRV.charge_backend_units(mm))
        seg = time.perf_counter() - seg0
        reported_wall += seg / plant_divisor
        reported_units += ar.backend_units / plant_divisor
        n_enum += ar.n_enumerations
        peak_table = max(peak_table, ar.peak_table_entries)
        if cap_is_binding_deadline and seg >= PER_TARGET_CAP_SECONDS - 1e-6:
            capped += 1
        elif (not cap_is_binding_deadline) and time.perf_counter() >= arm_deadline:
            arm_budget_truncated += 1
        if ar.found and not ar.incomplete:
            n_usable += 1
            rel_wall_samples.append(seg / plant_divisor)
            if ar.relation:
                certs.append(make_cert_legacy_null(ar.relation, seed, bits, B, m))
    true_wall = time.perf_counter() - t_arm0
    return {
        "method": method,
        "backend_object": "null-random-multihomogeneous (legacy, UNMATCHED)",
        "backend_id": DRV.BACKEND_ID,
        "plant_divisor_applied_live": plant_divisor,
        "plant_applied": plant_divisor != 1.0,
        "reported_wall_seconds": reported_wall,
        "true_elapsed_wall_seconds": true_wall,
        "reported_backend_units": reported_units,
        "n_enum": n_enum,
        "n_usable_relations": n_usable,
        "n_usable": n_usable,
        "attempted_targets": tag,
        "success_count": n_usable,
        "empirical_success_probability": n_usable / max(tag, 1),
        "hit_relations_target": n_usable >= relations_target,
        "stop_reason": stop_reason,
        "peak_claw_table_entries": peak_table,
        "claw_table_build_count": (tag if method == "split" else 0),
        "claw_table_amortized_once": (False if method == "split" else None),
        "table_build_reported_wall_seconds": 0.0,
        "table_build_measurable": False,
        "table_build_note": (
            "NOT SEPARATELY MEASURABLE. ds001_driver.null_split_search builds "
            "its half-map table INSIDE each attempt, so its build time is "
            "folded into the per-attempt segment and cannot be split out "
            "without editing the frozen kernel. Recorded as 0.0 with this "
            "note and with claw_table_build_count = attempted_targets, which "
            "is the honest statement; the legacy null arm does NOT amortize "
            "once. This is the RT047-B2 amortization asymmetry, present "
            "unchanged and reported, not repaired."),
        "per_relation_wall_samples": rel_wall_samples,
        "reported_overhead_wall_seconds": reported_wall - sum(rel_wall_samples),
        "per_target_cap_seconds": PER_TARGET_CAP_SECONDS,
        "per_arm_capped_attempt_count": capped,
        "per_arm_arm_budget_truncated_attempt_count": arm_budget_truncated,
        "peak_rss_bytes": rss_bytes(),
        "peak_rss_bytes_label": (
            "process high-water mark (ru_maxrss) sampled at the end of this arm"),
        "peak_rss_bytes_at_arm_start": rss_before,
        "_certs": certs,
    }


# ==========================================================================
# COST IDENTITIES AND THE TWO PROXIES
# ==========================================================================

COST_IDENTITY_STATEMENT = (
    "The frozen cost identity is WALL-DERIVED: "
    "cost_arm = reported_wall_seconds * rho_gop_per_second / max(n_usable, 1), "
    "and R = cost_split / cost_naive. CHARGED UNITS NEVER ENTER THE FROZEN "
    "COST IDENTITY. The charged-unit ratio reported beside every wall ratio is "
    "a SECOND, SEPARATE proxy computed only for the two-proxy disclosure "
    "required by CTRL-RT047-MATCHED-NULL; it is not a term of R and it does "
    "not correct, weight or replace the wall-derived R. This statement "
    "supersedes the BATCH-020 summary wording "
    "optimistic_assumptions_restated[0], which described the charged-unit "
    "proxy as 'optimistic for BOTH arms equally' and thereby implied it "
    "participated in the cost identity (RT047-B1 discharging requirement 1).")

UNIT_PROXY_FORMULA = (
    "U = (reported_backend_units_split / max(n_usable_split, 1)) / "
    "(reported_backend_units_naive / max(n_usable_naive, 1)). "
    "Candidate definition 2 (raw unit ratio, no per-relation divisor) is "
    "U_raw = reported_backend_units_split / reported_backend_units_naive. The "
    "two coincide exactly whenever both arms reach the same n_usable; both are "
    "reported here so the reader can check the agreement rather than take it "
    "on assertion (VAL/reviewer defect DEF-6).")


def arm_cost_wall(arm: dict, rho: float) -> float:
    return DRV.cost_from_wall(arm["reported_wall_seconds"], rho,
                              arm["n_usable_relations"])


def ratio_pair(naive: dict, split: dict, rho: float) -> dict:
    cn = arm_cost_wall(naive, rho)
    cs = arm_cost_wall(split, rho)
    wall = (cs / cn) if cn > 0 else None
    un = naive["reported_backend_units"] / max(naive["n_usable_relations"], 1)
    us = split["reported_backend_units"] / max(split["n_usable_relations"], 1)
    unit = (us / un) if un > 0 else None
    raw_n = naive["reported_backend_units"]
    raw_s = split["reported_backend_units"]
    unit_raw = (raw_s / raw_n) if raw_n > 0 else None
    agree = (unit is not None and unit_raw is not None
             and abs(unit - unit_raw) <= 1e-12 * max(1.0, abs(unit)))
    return {
        "ordered_pair_wall_then_charged_units": [wall, unit],
        "wall_proxy": wall,
        "charged_unit_proxy": unit,
        "charged_unit_proxy_raw_variant": unit_raw,
        "charged_unit_proxy_definitions_agree": bool(agree),
        "charged_unit_proxy_formula": UNIT_PROXY_FORMULA,
        "neither_proxy_privileged": True,
        "cost_wall_naive_gops_per_relation": cn,
        "cost_wall_split_gops_per_relation": cs,
        "units_per_relation_naive": un,
        "units_per_relation_split": us,
        "frozen_cost_identity_note": COST_IDENTITY_STATEMENT,
    }


def strip_certs(arms: dict) -> dict:
    certs = {}
    for name, arm in arms.items():
        certs[name] = arm.pop("_certs", [])
    return certs


# ==========================================================================
# MAIN
# ==========================================================================

def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--wall", type=float, default=1800.0)
    ap.add_argument("--arm-wall", type=float, default=600.0)
    ap.add_argument("--relations", type=int, default=RELATIONS_TARGET)
    ap.add_argument("--real-targets", type=int, default=4000,
                    help="size of the BATCH-020 unplanted curve target stream")
    ap.add_argument("--memory-gb", type=float, default=8.0)
    ap.add_argument("--run-dir", default=f"experiments/EXP-DS-001/runs/{RUN_ID}")
    ap.add_argument("--results-dir",
                    default="experiments/EXP-DS-001/results/ctrl_matched_null")
    args = ap.parse_args()

    started = DRV.utc_now()
    t_run0 = time.perf_counter()
    deadline_run = t_run0 + args.wall

    mem_cap_applied = False
    mem_cap_kind = None
    mem_cap_error: dict[str, str] = {}
    cap = int(args.memory_gb * (1 << 30))
    for kind in ("RLIMIT_AS", "RLIMIT_DATA", "RLIMIT_RSS"):
        lim = getattr(resource, kind, None)
        if lim is None:
            mem_cap_error[kind] = "not available on this platform"
            continue
        try:
            soft, hard = resource.getrlimit(lim)
            resource.setrlimit(lim, (cap, hard))
            mem_cap_applied = True
            mem_cap_kind = kind
            break
        except Exception as e:
            mem_cap_error[kind] = f"{type(e).__name__}: {e}"

    log(f"{RUN_ID} start {started}")
    log(f"contract={PARENT_CONTRACT} control={CONTROL_CONTRACT}")
    log(f"cell={CELL} relations_target={args.relations} "
        f"smoothness_abort={SMOOTHNESS_ABORT} "
        f"PER_TARGET_CAP_SECONDS={PER_TARGET_CAP_SECONDS} "
        f"plant_divisor={PLANT_DIVISOR}")
    log(f"backend_id={DRV.BACKEND_ID}")
    log(f"memory_cap_applied={mem_cap_applied} kind={mem_cap_kind} err={mem_cap_error}")

    contract_sha = DRV.sha256_file(REPO / PARENT_CONTRACT)
    control_sha = DRV.sha256_file(REPO / CONTROL_CONTRACT)
    amendment_sha = DRV.sha256_file(REPO / AMENDMENT_PATH)
    log(f"specification.v2.yaml sha256={contract_sha} "
        f"matches_expected={contract_sha == PARENT_CONTRACT_SHA256_EXPECTED}")
    log(f"CTRL-RT047-MATCHED-NULL.yaml sha256={control_sha}")
    log(f"v2_ctrl_matched_null.yaml sha256={amendment_sha}")

    # ---- approval gate ----------------------------------------------------
    receipt = json.loads((REPO / APPROVAL_RECEIPT).read_text())
    approval = receipt.get("APPROVAL_DETERMINATION")
    log(f"approval gate: TASK-20260801-004 APPROVAL_DETERMINATION={approval} "
        f"run_authorized={receipt.get('run_authorized')} "
        f"authorized_run_id={receipt.get('authorized_run_id')}")
    if approval != "APPROVED":
        log("REFUSING TO RUN: approval determination is not APPROVED.")
        return 2

    bits, B, m, seed = CELL["bits"], CELL["B"], CELL["m"], CELL["seed"]

    # ---- the real object (BATCH-020 instance), for the re-measure arms -----
    inst = generate_instance(seed, bits)
    E = inst.curve()
    real_group_order = E.order()
    fb = DRV.make_factor_base(inst, B, seed)
    fb_signed_set = set(fb.signed)
    log(f"real instance p={inst.p} a={inst.a} b={inst.b} subgroup_n={inst.n} "
        f"group_order={real_group_order} fb_x_hash={fb.x_hash}")

    # ---- the matched null object ------------------------------------------
    N = MATCHED_NULL_MODULUS
    order_match = (real_group_order == N)
    log(f"matched null: Z/{N}Z additive; order_matches_curve_group_order={order_match}")
    if not order_match:
        log("REFUSING TO RUN: matched-null modulus does not equal the curve "
            f"group order ({N} != {real_group_order}).")
        return 3
    G = AdditiveGroupZN(N)
    fbn = build_matched_null_factor_base(N, seed, CELL["B"])
    fbn_signed = fbn["signed_elements"]
    fbn_residue_set = set(fbn["signed_residues_in_order"])
    log(f"matched-null factor base: unsigned={fbn['size_unsigned']} "
        f"signed={fbn['size_signed']} draws={fbn['total_draws']} "
        f"rejections={fbn['rejection_counts']} "
        f"sha256={fbn['factor_base_sha256']}")

    null_targets, null_target_meta = matched_null_target_stream(
        N, seed, MATCHED_NULL_TARGET_COUNT)
    log(f"matched-null targets: {null_target_meta['targets_generated']} "
        f"uniform residues, stream_sha256={null_target_meta['target_stream_sha256']}")

    # ---- CTRL-RHO / CTRL-BSGS on the real instance (rho calibrates the
    #      wall-derived identity; it cancels in every ratio) -----------------
    rho = DRV.run_rho(inst)
    bsgs = DRV.run_bsgs(inst)
    rho_gop_per_second = (max(rho["total_group_operations"], 1)
                          / max(rho["wall_seconds"], 1e-9))
    log(f"CTRL-RHO solved={rho['solved']} ops={rho['total_group_operations']} "
        f"wall={rho['wall_seconds']:.6f}s cert_verified={rho['certificate_verified']} "
        f"rho_gop_per_second={rho_gop_per_second:.3f}")

    real_targets, real_target_meta = CTRL.unplanted_target_stream(
        E, seed, args.real_targets)
    log(f"real re-measure targets: {real_target_meta['targets_generated']} "
        f"(identical stream discipline to BATCH-020), "
        f"stream_sha256={real_target_meta['target_stream_sha256'][:16]}...")

    def remaining_arm_wall() -> float:
        return min(args.arm_wall, max(deadline_run - time.perf_counter(), 1.0))

    # ---- ARMS (contract order) --------------------------------------------
    arms: dict[str, dict] = {}

    log("ARM 1/6 matched_null_naive")
    arms["matched_null_naive"] = harvest(
        G, fbn_signed, "naive", null_targets, args.relations,
        remaining_arm_wall(), PLANT_DIVISOR, f"additive-Z{N}",
        lambda rel: make_cert_additive(N, rel))

    log("ARM 2/6 matched_null_split")
    arms["matched_null_split"] = harvest(
        G, fbn_signed, "split", null_targets, args.relations,
        remaining_arm_wall(), PLANT_DIVISOR, f"additive-Z{N}",
        lambda rel: make_cert_additive(N, rel))

    log("ARM 3/6 real_naive_remeasure")
    arms["real_naive_remeasure"] = harvest(
        E, fb.signed, "naive", real_targets, args.relations,
        remaining_arm_wall(), PLANT_DIVISOR, "curve-E(F_p)",
        lambda rel: CTRL.make_cert(inst, rel))

    log("ARM 4/6 real_split_remeasure")
    arms["real_split_remeasure"] = harvest(
        E, fb.signed, "split", real_targets, args.relations,
        remaining_arm_wall(), PLANT_DIVISOR, "curve-E(F_p)",
        lambda rel: CTRL.make_cert(inst, rel))

    log("ARM 5/6 legacy_null_naive")
    arms["legacy_null_naive"] = harvest_legacy_null(
        fb.xs, "naive", args.relations, remaining_arm_wall(), PLANT_DIVISOR)

    log("ARM 6/6 legacy_null_split")
    arms["legacy_null_split"] = harvest_legacy_null(
        fb.xs, "split", args.relations, remaining_arm_wall(), PLANT_DIVISOR)

    for name, a in arms.items():
        log(f"  {name}: n_usable={a['n_usable_relations']} "
            f"attempted={a['attempted_targets']} n_enum={a['n_enum']} "
            f"wall={a['reported_wall_seconds']:.6f}s "
            f"units={a['reported_backend_units']:.0f} "
            f"claw_entries={a['peak_claw_table_entries']} "
            f"table_build={a['table_build_reported_wall_seconds']:.6f}s "
            f"capped={a['per_arm_capped_attempt_count']} "
            f"stop={a['stop_reason']}")

    certs_by_arm = strip_certs(arms)

    # ---- certificate re-verification (independent paths) ------------------
    cert_stats: dict[str, dict] = {}
    all_ok = True
    for name, certs in certs_by_arm.items():
        ok = 0
        fails: list[str] = []
        for c in certs:
            if name.startswith("matched_null"):
                good, why = independent_verify_additive(c, fbn_residue_set, m)
            elif name.startswith("real"):
                good, why = CTRL.independent_verify_decomposition(c, fb_signed_set)
            else:
                good, why = independent_verify_legacy_null(c, set(fb.xs), m)
            if good:
                ok += 1
            else:
                fails.append(why)
        cert_stats[name] = {
            "count": len(certs), "verified": ok, "failed": len(certs) - ok,
            "verified_over_total": f"{ok}/{len(certs)}",
            "failure_reasons": sorted(set(fails)),
            "verifier_path": (
                "independent_verify_additive (plain int arithmetic mod N, "
                "rebuilt from the certificate)" if name.startswith("matched_null")
                else "ds001_ctrl_unplanted.independent_verify_decomposition "
                     "(curve rebuilt from the certificate)"
                if name.startswith("real")
                else "independent_verify_legacy_null (blake2b oracle predicate "
                     "re-derived inline, not via ds001_driver.null_full_hit)"),
        }
        if ok != len(certs):
            all_ok = False
        log(f"certificates[{name}] {ok}/{len(certs)} independently verified")

    # ---- ratios, both proxies ---------------------------------------------
    R_matched_null = ratio_pair(arms["matched_null_naive"],
                                arms["matched_null_split"], rho_gop_per_second)
    R_real_remeasure = ratio_pair(arms["real_naive_remeasure"],
                                  arms["real_split_remeasure"], rho_gop_per_second)
    R_null_legacy = ratio_pair(arms["legacy_null_naive"],
                               arms["legacy_null_split"], rho_gop_per_second)

    for nm, r in (("R_matched_null", R_matched_null),
                  ("R_real_remeasure", R_real_remeasure),
                  ("R_null_legacy", R_null_legacy)):
        log(f"  {nm} = (wall={r['wall_proxy']}, units={r['charged_unit_proxy']})")

    boot = {
        "estimator": "overhead-unresampled (the current BATCH-020 estimator)",
        "rt047_m1_advisory": (
            "RT047-M1 carried: the bootstrap CI adds each arm's fixed overhead "
            "UNRESAMPLED and is therefore anticonservative. Only the current "
            "estimator was computed. An overhead-resampled variant was NOT "
            "computed, because constructing one would introduce a new "
            "estimator and CTRL-RT047-MATCHED-NULL.budget.new_dependencies "
            "forbids new mathematics in this run. The contract's second "
            "option - stating plainly that only the current estimator was "
            "computed - is the option taken."),
        "R_matched_null_ci95_wall": CTRL.bootstrap_R(
            arms["matched_null_naive"], arms["matched_null_split"], "boot_R_matched_null"),
        "R_real_remeasure_ci95_wall": CTRL.bootstrap_R(
            arms["real_naive_remeasure"], arms["real_split_remeasure"], "boot_R_real_remeasure"),
        "R_null_legacy_ci95_wall": CTRL.bootstrap_R(
            arms["legacy_null_naive"], arms["legacy_null_split"], "boot_R_null_legacy"),
        "proxy_note": "Bootstrap CIs are computed on the WALL proxy only.",
    }

    # ---- guard observations (recorded; NOT classified) ---------------------
    capped_any = any(a["per_arm_capped_attempt_count"] > 0 for a in arms.values())
    all_hit = all(a["n_usable_relations"] >= args.relations for a in arms.values())
    matched_split_amortized_once = (
        arms["matched_null_split"]["claw_table_build_count"] == 1)
    real_split_amortized_once = (
        arms["real_split_remeasure"]["claw_table_build_count"] == 1)

    # ---- R-1 / v2 F-criterion observation labels (OBSERVATION ONLY) -------
    Rw = R_real_remeasure["wall_proxy"]
    Rn_matched_w = R_matched_null["wall_proxy"]
    Rn_matched_u = R_matched_null["charged_unit_proxy"]
    Ru = R_real_remeasure["charged_unit_proxy"]

    def r1_label_for(R, Rnull):
        if R is None or Rnull is None:
            return "metrics_incomplete"
        if R < 0.5 and Rnull < 0.9:
            return "F2_eligible"
        if R < 0.5 and Rnull >= 0.9:
            return "S1_eligible_on_null_axis"
        if R >= 0.9:
            return "F1_band"
        return "middle_band"

    r1_matched_wall = r1_label_for(Rw, Rn_matched_w)
    r1_matched_unit = r1_label_for(Ru, Rn_matched_u)
    log(f"R-1 observation label (wall proxy, matched null) = {r1_matched_wall}")
    log(f"R-1 observation label (charged-unit proxy, matched null) = {r1_matched_unit}")

    # ---- status ------------------------------------------------------------
    if not all_ok:
        status = "invalid_measurement"
        invalid_reason = ("a relation certificate failed independent "
                          "re-verification")
    elif not all_hit:
        status = "resource_exhaustion"
        invalid_reason = ("at least one arm did not reach relations_target "
                          "within budget; infrastructure/instrument signal, "
                          "NOT a mathematical negative (AGENTS.md rule 5)")
    else:
        status = "completed_valid"
        invalid_reason = None

    run_wall = time.perf_counter() - t_run0
    finished = DRV.utc_now()
    log(f"status={status} run_wall={run_wall:.3f}s")

    # ---- algorithm-invariance evidence -------------------------------------
    harvest_diff = "\n".join(difflib.unified_diff(
        inspect.getsource(CTRL.harvest_real).splitlines(),
        inspect.getsource(harvest).splitlines(),
        fromfile="ds001_ctrl_unplanted.harvest_real",
        tofile="ds001_ctrl_matched_null.harvest", lineterm=""))
    kernel_hashes = {
        fn: DRV.sha256_bytes(inspect.getsource(getattr(DRV, fn)).encode())
        for fn in ("naive_search", "split_search", "build_claw_table",
                   "charge_backend_units", "encode_intermediate", "claw_key",
                   "cost_from_wall", "frozen_D", "null_naive_search",
                   "null_split_search")
    }

    algorithm_invariance = {
        "binding_quoted": (
            "naive_search and split_search run UNCHANGED. The ONLY permitted "
            "difference from RUN-DS-001-ctrl-unplanted is the object the arms "
            "operate on."),
        "search_kernels_imported_unchanged": True,
        "search_kernels_source_sha256": kernel_hashes,
        "shared_backend_module": "experiments/EXP-DS-001/implementation/ds001_driver.py",
        "shared_backend_module_sha256": DRV.sha256_file(HERE / "ds001_driver.py"),
        "shared_backend_module_modified": False,
        "batch020_driver_module": "experiments/EXP-DS-001/implementation/ds001_ctrl_unplanted.py",
        "batch020_driver_module_sha256": DRV.sha256_file(HERE / "ds001_ctrl_unplanted.py"),
        "batch020_driver_module_modified": False,
        "object_substitution": (
            "AdditiveGroupZN exposes exactly the two methods the frozen "
            "kernels call on the object (.add, .negate) and elements are "
            "1-tuples (g,) with None for the identity, so pt[0] supplies the "
            "residue where a curve supplies an x-coordinate. No kernel was "
            "parameterized, subclassed, monkeypatched or copied."),
        "harvest_wrapper_is_a_copy": True,
        "harvest_wrapper_diff_declared_as_protocol_deviation": True,
        "harvest_wrapper_diff": harvest_diff,
        "harvest_wrapper_diff_rationale": (
            "CTRL-RT047-MATCHED-NULL.required_per_arm_fields mandates n_enum, "
            "per_arm_capped_attempt_count and peak_rss_bytes per arm, none of "
            "which ds001_ctrl_unplanted.harvest_real emits, and the reviewer's "
            "recommended claw_table_build_count likewise. The wrapper copy adds "
            "those counters and the object/backend_object plumbing. It changes "
            "no search logic, no deadline arithmetic, no charging, no "
            "amortization structure and no stopping rule, and the SAME wrapper "
            "serves every arm so no arm is advantaged by it."),
        "encode_intermediate_identity_at_these_parameters": {
            "D": DRV.frozen_D(bits, m),
            "D_bits": DRV.frozen_D(bits, m).bit_length(),
            "max_residue_below": N,
            "residue_bits": N.bit_length(),
            "is_identity_map": True,
            "note": ("D = 2^40 while every residue is < 753848 < 2^20, so "
                     "encode_intermediate is the identity map on this object, "
                     "exactly as RT047-B2 derived for the curve case. Expected "
                     "and recorded, not fixed."),
        },
        "join_predicate": ("Unchanged: exact equality of the encoded "
                           "intermediate via the frozen claw_key hash join. On "
                           "the additive object that is equality of residues."),
    }

    # ---- artifacts ---------------------------------------------------------
    run_dir = REPO / args.run_dir
    res_dir = REPO / args.results_dir
    run_dir.mkdir(parents=True, exist_ok=True)
    res_dir.mkdir(parents=True, exist_ok=True)

    rusage = resource.getrusage(resource.RUSAGE_SELF)
    peak_rss = rss_bytes()

    required_disclosures = {
        "d1_cost_identity_is_wall_derived": COST_IDENTITY_STATEMENT,
        "d2_batch020_reference_figures": (
            "Archived BATCH-020 figures quoted for reference: R_wall = 0.0322 "
            "and R_unit = 0.0147 on the real arms (a 2.20x proxy "
            "disagreement), and R_null_wall = 111.445 against "
            "R_null_unit = 0.9569 on the legacy null arms (a 116.5x proxy "
            "disagreement). Quoted from RUN-DS-001-ctrl-unplanted; not "
            "recomputed, not corrected, and not superseded by this run."),
        "d3_null_gate_not_robust_to_proxy_choice": (
            "The frozen R_null >= 0.9 gate is NOT robust to proxy choice. "
            "Under the charged-unit ledger the BATCH-020 legacy null passed it "
            "by about 6 percent (0.9569 against 0.9), not by the roughly "
            "12,000 percent margin the wall proxy's 111.445 suggests."),
        "d4_amortization_asymmetry": {
            "statement": (
                "The split arm's amortization asymmetry is present unchanged "
                "in the LEGACY null arms: the real split arm builds its claw "
                "table ONCE before the target loop, while "
                "ds001_driver.null_split_search rebuilds a half-map table "
                "INSIDE every attempt. That asymmetry is the RT047-B2 defect "
                "and it is reported here, not repaired."),
            "does_the_matched_null_split_arm_amortize_once": (
                "YES" if matched_split_amortized_once else "NO"),
            "matched_null_split_claw_table_build_count":
                arms["matched_null_split"]["claw_table_build_count"],
            "real_split_remeasure_claw_table_build_count":
                arms["real_split_remeasure"]["claw_table_build_count"],
            "legacy_null_split_claw_table_build_count":
                arms["legacy_null_split"]["claw_table_build_count"],
            "same_wrapper_serves_both": True,
            "evidence": ("Both the matched-null split arm and the real split "
                         "re-measure arm run the SAME harvest wrapper, which "
                         "builds the claw table once before the target loop; "
                         "claw_table_build_count is recorded per arm and "
                         "table_build_reported_wall_seconds is a separately "
                         "measured segment on both."),
        },
        "d5_rt047_m1_bootstrap_advisory": boot["rt047_m1_advisory"],
        "d6_dominated_by": {
            "dominated_by_is_null": False,
            "rows": [
                {"method": "Pollard rho on the BATCH-020 curve instance",
                 "cost": rho["total_group_operations"],
                 "cost_units": "group operations",
                 "label": "measured",
                 "memory": "negligible (constant-space cycle finding)"},
                {"method": "BSGS on the BATCH-020 curve instance",
                 "cost": bsgs["group_operations_modeled"],
                 "cost_units": "group operations",
                 "label": "modeled",
                 "memory": f"{bsgs['storage_elements_modeled']} stored elements "
                           f"(modeled)"},
                {"method": "Discrete log in Z/753848Z (the matched null object "
                           "itself)",
                 "cost": 1,
                 "cost_units": "modular inversion",
                 "label": "analytic",
                 "memory": "O(1)",
                 "note": ("A discrete log in an additive group is one modular "
                          "inverse. This is NOT a defect of the control: the "
                          "control measures ALGORITHM COST ONLY and claims "
                          "nothing whatsoever about the hardness of the null "
                          "object.")},
            ],
            "axes_covered": ["time", "memory", "stored elements"],
        },
    }

    guards_observed = {
        "note": ("GUARD OBSERVATIONS ONLY. The Executor records these values "
                 "and does NOT classify this run against the frozen "
                 "disposition map D-1..D-5. That classification is "
                 "TASK-20260801-009's exclusive job."),
        "per_target_cap_seconds": PER_TARGET_CAP_SECONDS,
        "per_arm_capped_attempt_count": {
            k: v["per_arm_capped_attempt_count"] for k, v in arms.items()},
        "any_arm_capped": capped_any,
        "certificate_verification_complete_on_every_arm": all_ok,
        "every_arm_reached_relations_target": all_hit,
        "matched_null_split_amortizes_claw_table_once": matched_split_amortized_once,
        "real_split_remeasure_amortizes_claw_table_once": real_split_amortized_once,
        "algorithm_invariance_binding_broken_by_undeclared_code_change": False,
        "run_terminated_by_timeout_crash_or_resource_exhaustion": (
            status == "resource_exhaustion"),
        "max_per_relation_wall_seconds_by_arm": {
            k: (max(v["per_relation_wall_samples"])
                if v["per_relation_wall_samples"] else None)
            for k, v in arms.items()},
    }

    reference_comparison = {
        "note": ("Comparison of the live same-host re-measure against the "
                 "archived BATCH-020 anchors. REPORTED AS HOST-VARIANCE "
                 "OBSERVATION ONLY. It does not correct, supersede or re-score "
                 "RUN-DS-001-ctrl-unplanted or EV-DS-003."),
        "archived": BATCH020_REFERENCE,
        "live_R_real_remeasure_ordered_pair_wall_then_units":
            R_real_remeasure["ordered_pair_wall_then_charged_units"],
        "wall_ratio_live_over_archived": (
            Rw / BATCH020_REFERENCE["R_real_wall"] if Rw else None),
        "unit_ratio_live_over_archived": (
            Ru / BATCH020_REFERENCE["R_real_unit"] if Ru else None),
        "deviation_exceeds_factor_2_wall": (
            bool(Rw and (Rw / BATCH020_REFERENCE["R_real_wall"] > 2.0
                         or Rw / BATCH020_REFERENCE["R_real_wall"] < 0.5))),
        "deviation_exceeds_factor_2_unit": (
            bool(Ru and (Ru / BATCH020_REFERENCE["R_real_unit"] > 2.0
                         or Ru / BATCH020_REFERENCE["R_real_unit"] < 0.5))),
    }

    live_plant_block = {
        "live_plant_run_in_this_batch": False,
        "plant_divisor": PLANT_DIVISOR,
        "plant_divisor_on_every_arm": {
            k: v["plant_divisor_applied_live"] for k, v in arms.items()},
        "plant_applied": False,
        "synthetic_known_answer_used": False,
        "hardcoded_detection_used": False,
        "CTRL_RT025_PLANT_LIVE_status": (
            "UNDISCHARGED, and remains undischarged after this batch "
            "(CTRL-RT047-MATCHED-NULL.live_plant_prohibition)."),
    }

    raw = {
        "schema": "crypto.autoresearch.raw_result.v1",
        "run_id": RUN_ID,
        "task_id": TASK_ID,
        "experiment_id": "EXP-DS-001",
        "hypothesis_id": "H-DS-001",
        "goal_id": GOAL_ID,
        "sub_goal_id": SUB_GOAL_ID,
        "batch_id": BATCH_ID,
        "control_protocol_id": CONTROL_ID,
        "protocol_amendment_id": AMENDMENT_ID,
        "claim_tier": "toy",
        "confirmatory_status": "exploratory_control",
        "contract": {
            "parent": PARENT_CONTRACT,
            "parent_sha256": contract_sha,
            "parent_sha256_expected": PARENT_CONTRACT_SHA256_EXPECTED,
            "parent_sha256_matches": contract_sha == PARENT_CONTRACT_SHA256_EXPECTED,
            "control": CONTROL_CONTRACT,
            "control_sha256": control_sha,
            "amendment": AMENDMENT_PATH,
            "amendment_sha256": amendment_sha,
            "approval_receipt": APPROVAL_RECEIPT,
            "approval_determination": approval,
            "run_authorized": receipt.get("run_authorized"),
            "authorized_run_id": receipt.get("authorized_run_id"),
            "v1_executed": False,
        },
        "cell": CELL,
        "backend_id": DRV.BACKEND_ID,
        "backend_id_sha256": DRV.sha256_bytes(DRV.BACKEND_ID.encode()),
        "smoothness_abort": SMOOTHNESS_ABORT,
        "relations_target": args.relations,
        "per_target_cap_seconds": PER_TARGET_CAP_SECONDS,
        "matched_null_object": {
            "id": NULL_OBJECT_ID,
            "group": f"Z/{N}Z under addition",
            "modulus": N,
            "order": G.order(),
            "curve_full_group_order": real_group_order,
            "order_matches_curve_group_order": order_match,
            "order_source": ("experiments/EXP-DS-001/runs/"
                             "RUN-DS-001-ctrl-unplanted/raw-result.json "
                             "instance.full_group_order = 753848, recomputed "
                             "live as E.order()"),
            "element_encoding": ("nonzero residue g -> (g,); identity residue "
                                 "0 -> None (the point-at-infinity analogue)"),
            "what_is_destroyed": ("every elliptic-curve and Semaev property: "
                                  "no curve, no x-coordinate, no point at "
                                  "infinity as an algebraic object, no "
                                  "summation polynomial, no degree, no "
                                  "resultant, no multihomogeneous structure, "
                                  "no smoothness-bearing intermediate"),
            "factor_base": {k: v for k, v in fbn.items()
                            if k != "signed_elements"},
            "target_mode": null_target_meta,
            "representation_density": {
                "signed_base_size": fbn["size_signed"],
                "m": m,
                "multiset_count_C_131_4": 11716640,
                "expected_representations_per_uniform_target":
                    11716640 / N,
                "label": "modeled",
            },
        },
        "real_instance": {
            "p": inst.p, "a": inst.a, "b": inst.b,
            "subgroup_order_n": inst.n,
            "full_group_order": real_group_order,
            "generator_P": list(inst.P),
            "fb_x_hash": fb.x_hash,
            "factor_base_size": len(fb.xs),
            "signed_factor_base_size": len(fb.signed),
            "target_mode": real_target_meta,
        },
        "algorithm_invariance": algorithm_invariance,
        "controls": {
            "CTRL_RHO": rho,
            "CTRL_BSGS": bsgs,
            "CTRL_BACKEND_IDENTICAL": {
                "backend_id": DRV.BACKEND_ID,
                "shared_by": sorted(arms.keys()),
                "backend_object_per_arm": {
                    k: v["backend_object"] for k, v in arms.items()},
                "charge_function": "ds001_driver.charge_backend_units (unmodified)",
                "charge_constant_for_m4": DRV.charge_backend_units(4),
            },
            "CTRL_NULL_SHAPE_legacy": {
                "null_object_spec_hash": DRV.null_spec_hash(seed, bits, B, m),
                "null_object_id": DRV.NULL_SPEC_ID,
                "status": ("DECLARED UNMATCHED for structure-dependence "
                           "readings (RT047-B2); carried for disclosure only"),
            },
            "CTRL_MATCHED_NULL": {
                "null_object_id": NULL_OBJECT_ID,
                "matched_axes": ["group order", "composition law",
                                 "factor-base cardinality and negation closure",
                                 "arity m", "representation density",
                                 "seed", "stopping rule", "cost identity",
                                 "the algorithm"],
                "destroyed_axes": ["elliptic-curve structure",
                                   "Semaev/summation-polynomial structure",
                                   "multihomogeneous grading",
                                   "smoothness-bearing intermediates"],
            },
            "CTRL_RT025_PLANT_LIVE": live_plant_block,
            "CTRL_CERT": {"verified": all_ok, "aggregate": cert_stats},
        },
        "arms": arms,
        "metrics": {
            "R_matched_null": R_matched_null,
            "R_real_remeasure": R_real_remeasure,
            "R_null_legacy": R_null_legacy,
            "bootstrap": boot,
            "per_arm": {
                k: {f: v.get(f) for f in (
                    "reported_wall_seconds", "reported_backend_units", "n_enum",
                    "n_usable", "attempted_targets", "success_count",
                    "empirical_success_probability", "peak_claw_table_entries",
                    "peak_rss_bytes", "reported_overhead_wall_seconds",
                    "table_build_reported_wall_seconds",
                    "per_arm_capped_attempt_count", "stop_reason")}
                for k, v in arms.items()},
            "r1_observation_label_wall_proxy": r1_matched_wall,
            "r1_observation_label_charged_unit_proxy": r1_matched_unit,
            "r1_rule_quoted": (
                "R-1 / specification.v2 F2: if R < 0.5 AND R_null < 0.9 the "
                "observation label is F2_eligible. OBSERVATION LABEL ONLY - "
                "the Executor does not adjudicate it, does not assert F2_met, "
                "and does not state a disposition."),
            "f_criteria_flags_observed": {
                "note": ("Raw observation of the frozen specification.v2 "
                         "criteria as arithmetic on this run's numbers. "
                         "Recorded because DEF-2 requires the frozen F2 "
                         "criterion to be evaluated on the record. NOT an "
                         "adjudication and NOT a disposition."),
                "R_real_below_0_5_wall": bool(Rw is not None and Rw < 0.5),
                "R_real_below_0_5_unit": bool(Ru is not None and Ru < 0.5),
                "R_matched_null_below_0_5_wall": bool(
                    Rn_matched_w is not None and Rn_matched_w < 0.5),
                "R_matched_null_below_0_5_unit": bool(
                    Rn_matched_u is not None and Rn_matched_u < 0.5),
                "R_matched_null_at_or_above_0_9_wall": bool(
                    Rn_matched_w is not None and Rn_matched_w >= 0.9),
                "R_matched_null_at_or_above_0_9_unit": bool(
                    Rn_matched_u is not None and Rn_matched_u >= 0.9),
            },
        },
        "required_disclosures": required_disclosures,
        "guards_observed": guards_observed,
        "reference_comparison": reference_comparison,
        "certificate": {
            "kind": "decomposition",
            "verified": all_ok,
            "verifier": ("per-arm independent verifier paths; see "
                         "controls.CTRL_CERT.aggregate[*].verifier_path"),
            "aggregate": cert_stats,
            "statement": (certs_by_arm.get("matched_null_split") or [None])[0],
        },
        "certificates_by_arm": certs_by_arm,
        "status": status,
        "invalid_reason": invalid_reason,
        "budget": {
            "wall_clock_seconds_allowed": args.wall,
            "wall_clock_seconds_used": run_wall,
            "memory_gb_allowed": args.memory_gb,
            "memory_cap_applied": mem_cap_applied,
            "memory_cap_kind": mem_cap_kind,
            "memory_cap_errors": mem_cap_error,
            "peak_rss_bytes": peak_rss,
            "maximum_runs": 1,
        },
        "randomness_sources": [
            "master seed 101 -> harness.toycurve.generate_instance(101, 20) "
            "(real re-measure object)",
            "master seed 101 -> ds001_driver.make_factor_base(inst, 64, 101) "
            "(real re-measure factor base)",
            "_seed_int(101, 'matched_null_factor_base') -> matched-null "
            "unsigned residue draws",
            "_seed_int(101, 'matched_null_targets') -> matched-null uniform "
            "target residues",
            "_seed_int(101, 'ctrl_unplanted_targets') -> real re-measure "
            "unplanted curve target stream (unchanged from BATCH-020)",
            "_seed_int(101, 'null_naive_<tag>') / _seed_int(101, "
            "'null_split_<tag>') -> legacy null samplers (ds001_driver, "
            "unmodified)",
            "_seed_int(101, 'boot_R_*') -> bootstrap resampling",
        ],
        "interpretation": (
            "NONE. Observations only. This run states no disposition, "
            "classifies nothing against the frozen D-1..D-5 map, assigns no "
            "hypothesis status, adjudicates no success or falsification "
            "criterion, and declares no heuristic validated or refuted."),
        "timing": {"started_at": started, "finished_at": finished,
                   "wall_seconds": run_wall},
    }

    (run_dir / "raw-result.json").write_text(
        json.dumps(raw, indent=2, default=str) + "\n", encoding="utf-8")

    g = DRV.git_state()
    env = DRV.env_block()
    env["numpy_version"] = _optional_version("numpy")
    env["sympy_version"] = _optional_version("sympy")
    env["cwd"] = os.getcwd()
    env["repo_root"] = str(REPO)
    env["pid"] = os.getpid()
    env["cpu_count"] = os.cpu_count()
    env["argv"] = sys.argv
    env["resource_limits"] = {
        "requested_bytes": cap,
        "applied": mem_cap_applied,
        "applied_limit_kind": mem_cap_kind,
        "errors": mem_cap_error,
    }
    (run_dir / "environment.json").write_text(
        json.dumps(env, indent=2, default=str) + "\n", encoding="utf-8")

    manifest = {
        "schema": "crypto.autoresearch.run_manifest.v1",
        "run_id": RUN_ID,
        "experiment_id": "EXP-DS-001",
        "hypothesis_id": "H-DS-001",
        "task_id": TASK_ID,
        "goal_id": GOAL_ID,
        "sub_goal_id": SUB_GOAL_ID,
        "batch_id": BATCH_ID,
        "contract": {
            "path": PARENT_CONTRACT,
            "version": "2 (parent, immutable)",
            "parent_sha256": contract_sha,
            "parent_sha256_expected": PARENT_CONTRACT_SHA256_EXPECTED,
            "parent_sha256_matches": contract_sha == PARENT_CONTRACT_SHA256_EXPECTED,
            "control_protocol_path": CONTROL_CONTRACT,
            "control_protocol_sha256": control_sha,
            "control_protocol_id": CONTROL_ID,
            "amendment_path": AMENDMENT_PATH,
            "amendment_sha256": amendment_sha,
            "amendment_id": AMENDMENT_ID,
            "narrowed_version": "2.2-ctrl",
            "approval_receipt": APPROVAL_RECEIPT,
            "approval_determination": approval,
            "approval_commit": "d9e396142776c3f78f0598907d36258808585a28",
            "reviewer_verdict": "PASS (TASK-20260801-003 / REV-20260801-003)",
            "reviewer_recommendation": "APPROVE",
            "v1_executed": False,
        },
        "status": status,
        "claim_tier": "toy",
        "confirmatory_status": "exploratory_control",
        "per_target_cap_seconds": PER_TARGET_CAP_SECONDS,
        "per_arm_capped_attempt_count": {
            k: v["per_arm_capped_attempt_count"] for k, v in arms.items()},
        "live_plant": live_plant_block,
        "code": {
            "commit": g.get("commit"),
            "dirty": g.get("dirty"),
            "branch": g.get("branch"),
            "driver": "experiments/EXP-DS-001/implementation/ds001_ctrl_matched_null.py",
            "driver_sha256": DRV.sha256_file(Path(__file__)),
            "shared_backend_module": "experiments/EXP-DS-001/implementation/ds001_driver.py",
            "shared_backend_module_sha256": DRV.sha256_file(HERE / "ds001_driver.py"),
            "shared_backend_module_modified": False,
            "batch020_driver_module_sha256": DRV.sha256_file(HERE / "ds001_ctrl_unplanted.py"),
            "batch020_driver_module_modified": False,
            "command": ((run_dir / "command.txt").read_text().strip()
                        if (run_dir / "command.txt").exists() else None),
            "argv": sys.argv,
        },
        "algorithm_invariance": {
            k: v for k, v in algorithm_invariance.items()
            if k != "harvest_wrapper_diff"},
        "inference": {
            "requested_policy": "executor-implementation",
            "resolved_model_id": "claude-opus-5 (Claude Code subagent; runtime-reported)",
            "reasoning_effort": None,
            "fallback_used": True,
            "fallback_reason": (
                "This Claude Code harness cannot resolve "
                "orchestration/model-policies.yaml GPT-5.6-family policy "
                "aliases; subagent frontmatter supports Claude models only. "
                "Recorded rather than silently substituted."),
            "model_verified": False,
            "model_verified_reason": (
                "no python3 -m orchestration.adapter doctor --probe was run in "
                "this session, so the identifier is unverified configuration"),
            "independent_session_required": False,
            "degraded_allowed": False,
            "adapter_version": None,
        },
        "environment": env,
        "inputs": {
            "cell": CELL,
            "seeds": [seed],
            "matched_null_modulus": N,
            "matched_null_target_mode": "matched_null_uniform_random",
            "matched_null_target_count": MATCHED_NULL_TARGET_COUNT,
            "matched_null_target_stream_sha256":
                null_target_meta["target_stream_sha256"],
            "matched_null_factor_base_sha256": fbn["factor_base_sha256"],
            "matched_null_factor_base_rejection_counts": fbn["rejection_counts"],
            "real_target_stream_sha256": real_target_meta["target_stream_sha256"],
            "real_fb_x_hash": fb.x_hash,
            "planted_m_sums_used_as_yield_source": False,
            "relations_target": args.relations,
            "smoothness_abort": SMOOTHNESS_ABORT,
            "backend_id": DRV.BACKEND_ID,
            "backend_id_sha256": DRV.sha256_bytes(DRV.BACKEND_ID.encode()),
            "legacy_null_object_spec_hash": DRV.null_spec_hash(seed, bits, B, m),
        },
        "timing": {"started_at": started, "finished_at": finished,
                   "wall_seconds": run_wall},
        "resources": {
            "peak_rss_bytes": peak_rss,
            "peak_rss_bytes_per_arm": {
                k: v["peak_rss_bytes"] for k, v in arms.items()},
            "cpu_seconds": rusage.ru_utime + rusage.ru_stime,
            "memory_gb_limit": args.memory_gb,
            "wall_clock_seconds_limit": args.wall,
        },
        "result": {
            "R_matched_null_ordered_pair_wall_then_units":
                R_matched_null["ordered_pair_wall_then_charged_units"],
            "R_real_remeasure_ordered_pair_wall_then_units":
                R_real_remeasure["ordered_pair_wall_then_charged_units"],
            "R_null_legacy_ordered_pair_wall_then_units":
                R_null_legacy["ordered_pair_wall_then_charged_units"],
            "valid": status == "completed_valid",
            "invalid_reason": invalid_reason,
            "certificate": {"verified": all_ok, "aggregate": cert_stats},
        },
        "guards_observed": guards_observed,
        "artifacts": {
            "raw-result.json": str(run_dir / "raw-result.json"),
            "stdout.txt": str(run_dir / "stdout.txt"),
            "stderr.txt": str(run_dir / "stderr.txt"),
            "command.txt": str(run_dir / "command.txt"),
            "environment.json": str(run_dir / "environment.json"),
            "summary.json": str(res_dir / "summary.json"),
            "R_cell.json": str(res_dir / "R_cell.json"),
            "matched_null_report.json": str(res_dir / "matched_null_report.json"),
            "proxy_sensitivity_report.json":
                str(res_dir / "proxy_sensitivity_report.json"),
        },
        "hypothesis_status_changed_by_this_run": False,
        "disposition_stated": False,
        "interpretation": (
            "NONE. Executor records observations only. Classification against "
            "the frozen disposition map D-1..D-5 is TASK-20260801-009's "
            "exclusive job and is deliberately absent here."),
    }
    (run_dir / "manifest.json").write_text(
        json.dumps(manifest, indent=2, default=str) + "\n", encoding="utf-8")

    # ---- results/ctrl_matched_null ----------------------------------------
    R_cell = {
        "schema": "exp_ds_001.ctrl_matched_null.R_cell.v1",
        "run_id": RUN_ID,
        "control_protocol_id": CONTROL_ID,
        "cell": CELL,
        "per_target_cap_seconds": PER_TARGET_CAP_SECONDS,
        "plant_state_for_these_numbers": "OFF (plant_divisor 1.0 on every arm)",
        "both_proxies_mandatory": (
            "EVERY ratio below is an ORDERED PAIR (wall proxy, charged-unit "
            "proxy) with NEITHER PRIVILEGED."),
        "ratios": {
            "R_matched_null": R_matched_null,
            "R_real_remeasure": R_real_remeasure,
            "R_null_legacy": R_null_legacy,
        },
        "bootstrap": boot,
        "per_arm": raw["metrics"]["per_arm"],
        "arms_full": arms,
        "rho_gop_per_second": rho_gop_per_second,
        "rho_note": ("Single matched CTRL-RHO capture on the curve instance, "
                     "reused for every arm; it cancels in every ratio."),
        "modeled": {
            "bsgs_group_operations_modeled": bsgs["group_operations_modeled"],
            "bsgs_storage_elements_modeled": bsgs["storage_elements_modeled"],
            "label": "modeled - cost model only, not measured",
        },
        "cost_identities_used": {
            "rho_gop_per_second": ("rho_total_group_operations / "
                                   "rho_wall_seconds (CTRL-RHO receipt)"),
            "cost_arm": ("reported_wall_seconds * rho_gop_per_second / "
                         "max(n_usable, 1)"),
            "R": "cost_split / cost_naive",
            "identical_to": "specification.v2.yaml cost_identities",
            "charged_units_never_enter_R": True,
        },
        "r1_observation_label_wall_proxy": r1_matched_wall,
        "r1_observation_label_charged_unit_proxy": r1_matched_unit,
        "f_criteria_flags_observed": raw["metrics"]["f_criteria_flags_observed"],
        "claim_tier": "toy",
        "interpretation": "NONE.",
    }
    (res_dir / "R_cell.json").write_text(
        json.dumps(R_cell, indent=2, default=str) + "\n", encoding="utf-8")

    matched_report = {
        "schema": "exp_ds_001.ctrl_matched_null.matched_null_report.v1",
        "run_id": RUN_ID,
        "control_protocol_id": CONTROL_ID,
        "null_object": raw["matched_null_object"],
        "algorithm_invariance": algorithm_invariance,
        "measured": {
            "R_matched_null": R_matched_null,
            "R_real_remeasure": R_real_remeasure,
            "R_null_legacy": R_null_legacy,
            "matched_null_naive_arm": arms["matched_null_naive"],
            "matched_null_split_arm": arms["matched_null_split"],
            "real_naive_remeasure_arm": arms["real_naive_remeasure"],
            "real_split_remeasure_arm": arms["real_split_remeasure"],
            "legacy_null_naive_arm": arms["legacy_null_naive"],
            "legacy_null_split_arm": arms["legacy_null_split"],
        },
        "required_disclosures": required_disclosures,
        "guards_observed": guards_observed,
        "reference_comparison": reference_comparison,
        "legacy_null_status": (
            "NULL-DS-RANDOM-MULTIHOMOGENEOUS is DECLARED UNMATCHED for "
            "structure-dependence readings (RT047-B2). R_null_legacy is "
            "reported for disclosure and comparison ONLY and licenses no "
            "structure reading."),
        "null_object_hardness_note": (
            "A discrete log in Z/NZ is trivial (one modular inverse). This "
            "control therefore measures ALGORITHM COST ONLY and claims nothing "
            "about the hardness of the null object."),
        "certificate_summary": {"all_verified": all_ok, "per_arm": cert_stats},
        "claim_tier": "toy",
        "confirmatory_status": "exploratory_control",
        "disposition_stated": False,
        "interpretation": "NONE.",
    }
    (res_dir / "matched_null_report.json").write_text(
        json.dumps(matched_report, indent=2, default=str) + "\n", encoding="utf-8")

    proxy_report = {
        "schema": "exp_ds_001.ctrl_matched_null.proxy_sensitivity_report.v1",
        "run_id": RUN_ID,
        "frozen_cost_identity_statement": COST_IDENTITY_STATEMENT,
        "charged_unit_proxy_formula": UNIT_PROXY_FORMULA,
        "charged_unit_definitions_agree_on_this_run": {
            "R_matched_null": R_matched_null["charged_unit_proxy_definitions_agree"],
            "R_real_remeasure": R_real_remeasure["charged_unit_proxy_definitions_agree"],
            "R_null_legacy": R_null_legacy["charged_unit_proxy_definitions_agree"],
            "why_they_can_agree": (
                "The per-relation divisors cancel exactly when both arms of a "
                "ratio reach the same n_usable. n_usable per arm is recorded "
                "so the reader can check rather than assume."),
        },
        "ordered_pairs_wall_then_charged_units": {
            "R_matched_null": R_matched_null["ordered_pair_wall_then_charged_units"],
            "R_real_remeasure": R_real_remeasure["ordered_pair_wall_then_charged_units"],
            "R_null_legacy": R_null_legacy["ordered_pair_wall_then_charged_units"],
        },
        "proxy_disagreement_factor": {
            "R_matched_null": (
                (Rn_matched_w / Rn_matched_u)
                if (Rn_matched_w and Rn_matched_u) else None),
            "R_real_remeasure": (Rw / Ru) if (Rw and Ru) else None,
            "R_null_legacy": (
                (R_null_legacy["wall_proxy"] / R_null_legacy["charged_unit_proxy"])
                if (R_null_legacy["wall_proxy"] and R_null_legacy["charged_unit_proxy"])
                else None),
            "label": "measured",
        },
        "archived_batch020_disclosure": required_disclosures["d2_batch020_reference_figures"],
        "null_gate_not_robust_to_proxy_choice":
            required_disclosures["d3_null_gate_not_robust_to_proxy_choice"],
        "charged_unit_proxy_is_object_independent_by_construction": (
            "ds001_driver.charge_backend_units charges a constant "
            f"{DRV.charge_backend_units(4)} units per membership call for m = 4 "
            "regardless of which group the call ran in. The charged-unit proxy "
            "is therefore close to a function of the fixed enumeration counts "
            "rather than a measurement of the object. Stated as a property of "
            "the instrument; the Executor draws no conclusion from it."),
        "per_arm_units_and_enumerations": {
            k: {"reported_backend_units": v["reported_backend_units"],
                "n_enum": v["n_enum"],
                "n_usable": v["n_usable_relations"],
                "units_per_enumeration": (v["reported_backend_units"] / v["n_enum"]
                                          if v["n_enum"] else None)}
            for k, v in arms.items()},
        "bootstrap": boot,
        "neither_proxy_privileged": True,
        "claim_tier": "toy",
        "interpretation": "NONE.",
    }
    (res_dir / "proxy_sensitivity_report.json").write_text(
        json.dumps(proxy_report, indent=2, default=str) + "\n", encoding="utf-8")

    summary = {
        "schema": "exp_ds_001.ctrl_matched_null.summary.v1",
        "run_id": RUN_ID,
        "task_id": TASK_ID,
        "batch_id": BATCH_ID,
        "goal_id": GOAL_ID,
        "experiment_id": "EXP-DS-001",
        "hypothesis_id": "H-DS-001",
        "hypothesis_status_changed_by_this_run": False,
        "control_protocol_id": CONTROL_ID,
        "protocol_amendment_id": AMENDMENT_ID,
        "status": status,
        "invalid_reason": invalid_reason,
        "claim_tier": "toy",
        "confirmatory_status": "exploratory_control",
        "cell": CELL,
        "matched_null_object_id": NULL_OBJECT_ID,
        "matched_null_modulus": N,
        "matched_null_order_matches_curve_group_order": order_match,
        "target_mode": ("matched_null_uniform_random for the null arms "
                        "(planted m-sums NOT used); unplanted_uniform_random "
                        "curve points for the real re-measure arms"),
        "backend_id": DRV.BACKEND_ID,
        "smoothness_abort": SMOOTHNESS_ABORT,
        "relations_target": args.relations,
        "per_target_cap_seconds": PER_TARGET_CAP_SECONDS,
        "per_arm_capped_attempt_count": {
            k: v["per_arm_capped_attempt_count"] for k, v in arms.items()},
        "any_arm_capped": capped_any,
        "measured_ratios_ordered_pairs_wall_then_charged_units": {
            "R_matched_null": R_matched_null["ordered_pair_wall_then_charged_units"],
            "R_real_remeasure": R_real_remeasure["ordered_pair_wall_then_charged_units"],
            "R_null_legacy": R_null_legacy["ordered_pair_wall_then_charged_units"],
        },
        "measured_ratio_detail": {
            "R_matched_null": R_matched_null,
            "R_real_remeasure": R_real_remeasure,
            "R_null_legacy": R_null_legacy,
        },
        "measured_per_arm": raw["metrics"]["per_arm"],
        "measured_extra_per_arm": {
            k: {"claw_table_build_count": v["claw_table_build_count"],
                "claw_table_amortized_once": v["claw_table_amortized_once"],
                "true_elapsed_wall_seconds": v["true_elapsed_wall_seconds"],
                "hit_relations_target": v["hit_relations_target"],
                "backend_object": v["backend_object"]}
            for k, v in arms.items()},
        "modeled": {
            "bsgs_group_operations_modeled": bsgs["group_operations_modeled"],
            "bsgs_storage_elements_modeled": bsgs["storage_elements_modeled"],
            "expected_representations_per_uniform_target_matched_null":
                11716640 / N,
            "label": "modeled - never measured",
        },
        "required_disclosures": required_disclosures,
        "guards_observed": guards_observed,
        "reference_comparison": reference_comparison,
        "live_plant": live_plant_block,
        "optimistic_assumptions_restated": [
            COST_IDENTITY_STATEMENT,
            "Charged units use a frozen backend cost proxy "
            "(ds001_driver.charge_backend_units), NOT a per-attempt Groebner "
            "solve. This is the pre-existing v2 deviation. It affects the "
            "charged-unit proxy U only; it does not affect the wall-derived R, "
            "because charged units are not a term of the frozen cost identity.",
            "rho_gop_per_second comes from one matched CTRL-RHO capture on the "
            "curve instance and is reused for every arm including the "
            "matched-null arms; it cancels in every ratio. It is NOT a "
            "calibration of the additive object's per-operation cost, and no "
            "object-cost-parity measurement was performed in this run.",
            "BSGS numbers are modeled from 2*ceil(sqrt(n)), never measured.",
            "encode_intermediate is the identity map at these parameters "
            "(D = 2^40, residues < 2^20) on BOTH objects, so the split arm's "
            "join is exact equality rather than a truncated encoding.",
        ],
        "r1_observation_label_wall_proxy": r1_matched_wall,
        "r1_observation_label_charged_unit_proxy": r1_matched_unit,
        "f_criteria_flags_observed": raw["metrics"]["f_criteria_flags_observed"],
        "r1_note": ("Observation labels only. The Executor does not adjudicate "
                    "S1/F1/F2/F3, does not declare the heuristic validated or "
                    "refuted, changes no hypothesis status, and states no "
                    "disposition."),
        "certificate_summary": {"all_verified": all_ok, "per_arm": cert_stats},
        "disposition_stated": False,
        "disposition_note": (
            "Classification against the frozen disposition map D-1..D-5 is "
            "TASK-20260801-009's exclusive job and is deliberately absent from "
            "every artifact of this run."),
        "interpretation": "NONE.",
    }
    (res_dir / "summary.json").write_text(
        json.dumps(summary, indent=2, default=str) + "\n", encoding="utf-8")

    log("artifacts written:")
    for p in ["manifest.json", "raw-result.json", "environment.json"]:
        log(f"  {run_dir / p}")
    for p in ["summary.json", "R_cell.json", "matched_null_report.json",
              "proxy_sensitivity_report.json"]:
        log(f"  {res_dir / p}")
    log(f"{RUN_ID} end status={status}")
    return 0


def _optional_version(mod: str) -> Optional[str]:
    try:
        return __import__(mod).__version__
    except Exception:
        return None


if __name__ == "__main__":
    raise SystemExit(main())

#!/usr/bin/env python3
"""RIDER (i) -- TASK-20260812-78a6e3 -- the C-1 resolving tabulation.

GOAL-MLKEM-005 / BATCH-4ed139.  Governed by PREREG-1 (TASK-20260812-34b86c),
section 8.1, frozen and notarized.  CLAIM TIER: TOY, unconditionally.

WHAT THIS DOES.  It reads the COMMITTED, IMMUTABLE file

    coordination/goals/GOAL-MLKEM-005/batches/BATCH-9e3584/
        tasks/TASK-20260809-cda2f6/results_relvar.json

pinned by sha256, NEVER EDITED, and tabulates the 19 G-REL2 cells and the 10
G-REL1 lattices of the `null` (X_null) candidate under ALL THREE declared
readings of PREREG-1 section 8.1 --

    R_i0     legacy i = 0            per_basis[0]
    R_npass  count of passing bases  n_pass_<norm>_of_8
    R_mean8  mean over 8             mean of per_basis over i = 0..7

-- and, because the committed file carries TWO normalizations of the same
criterion value side by side, under BOTH of them:

    maxfloor  value_maxfloor   (the scale-floor normalization)
    absX      value_absX       (the |X| normalization)

The normalization is NOT one of the three declared readings.  It is reported
because both values are in the committed file under the same cell and a count
of "entries below 6x" is not defined without saying which one is meant.

NO reduction, NO fpylll, NO basis rebuild, NO write outside this task
directory.  Nothing here bears on ML-KEM, on any FIPS 203 parameter set, on
any attack cost or on any cost model.

This script RECORDS OBSERVATIONS.  It does not adjudicate C-1, does not
declare either validator wrong beyond what the numbers show, and does not
make either count citable: until the Coordinator rules on this tabulation in
the batch decision, NEITHER COUNT IS CITABLE, and "a factor of 6 to 31"
remains FALSE and uncitable regardless.
"""

import hashlib
import json
import math
import os
import platform
import subprocess
import sys
import time

# ---------------------------------------------------------------- constants

TAU_REL = 0.10                     # frozen, PREREG-1 section 2.1
SIX_X = 6.0 * TAU_REL              # 0.60 -- the "6x" boundary being counted
PLATEAU = 4.0 / 7.0                # 0.5714285714... , see MOD_NOTE below
N_BASES = 8
TOL = 1e-12                        # relative tolerance for the boundary rule

# 1 - k/(d-k) = 1 - 30/70 = 4/7 = 0.5714285714... for (d,k) = (100,30).
# Flagged in the task card BEFORE looking: this value is STRUCTURALLY
# AVAILABLE in this family, so wave 1's "5.71x" is not obviously a typo.
MOD_NOTE = ("1 - k/(d-k) = 4/7 = 0.5714285714285714 for (d,k) = (100,30); "
            "structurally available in this family")

_HERE = os.path.dirname(os.path.abspath(__file__))
# _HERE is <repo>/coordination/goals/<GOAL>/batches/<BATCH>/tasks/<TASK>, so the
# repository root is SEVEN levels up.  Asserted below rather than assumed.
REPO = os.path.abspath(os.path.join(_HERE, *([os.pardir] * 7)))
assert os.path.isdir(os.path.join(REPO, ".git")), \
    "repository root not resolved from %s (got %s)" % (_HERE, REPO)
SRC = os.path.join(
    REPO, "coordination", "goals", "GOAL-MLKEM-005", "batches", "BATCH-9e3584",
    "tasks", "TASK-20260809-cda2f6", "results_relvar.json")
SRC_REL = os.path.relpath(SRC, REPO)
OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                   "results_c1res.json")

# The two counts in conflict, quoted from the two committed validation
# reports and from DEC-20260812-7c4a1e C-1.  Quoted, never re-worded.
WAVE1 = {
    "task": "TASK-20260809-3f1dc4",
    "finding": "F-1",
    "claim": ("15 of the 19 G-REL2 cells fall BELOW the stated lower bound of "
              "6x; thirteen G-REL2 cells sit at exactly 5.71x and one at "
              "4.97x; the minimum over all scored cells is 4.87x at L1/L2 "
              "beta 15; the G-REL1 range is 12.17x to 31.03x; the G-REL2 "
              "range is 4.87x to 6.00x"),
    "count_below_6x": 15,
    "denominator": 19,
    "denominator_set": "G-REL2 cells",
}
WAVE2 = {
    "task": "TASK-20260812-da8c3b",
    "finding": "F-1",
    "claim": ("at the mean-over-8 reading the range is 0.486626 to 3.103480, "
              "i.e. a factor of 4.87 to 31.03; TWO entries fall below 6x: "
              "0.486626 (REL2, L1/L2, beta 15) = 4.87x and 0.496557 (REL2, "
              "L4/L5, beta 20) = 4.97x"),
    "count_below_6x": 2,
    "denominator": 29,
    "denominator_set": "all 29 X_null G-REL entries",
}


def sha256_of(path):
    h = hashlib.sha256()
    with open(path, "rb") as fh:
        for chunk in iter(lambda: fh.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def git(*args):
    try:
        return subprocess.run(["git", "-C", REPO] + list(args),
                              capture_output=True, text=True,
                              check=True).stdout.strip()
    except Exception as exc:                                   # pragma: no cover
        return "UNAVAILABLE: %s" % exc


def mean(xs):
    # math.fsum is correctly rounded and division by a power of two is exact,
    # so when all 8 values are bit-identical the mean IS that value bitwise.
    return math.fsum(xs) / float(len(xs))


def main():
    t0 = time.time()
    src_sha = sha256_of(SRC)
    with open(SRC) as fh:
        data = json.load(fh)

    src_mtime_before = os.stat(SRC).st_mtime_ns

    rel2 = data["G_REL2"]["null"]
    rel1 = data["G_REL1"]["null"]

    # ------------------------------------------------------------- entries
    # An "entry" is one scored G-REL2 cell (pair, beta) or one scored G-REL1
    # lattice.  19 + 10 = 29, exactly the two denominators in conflict.
    entries = []
    for pair, cells in rel2.items():
        for beta, cell in cells.items():
            entries.append({
                "group": "G-REL2",
                "label": "%s beta %s" % (pair, beta),
                "pair": pair,
                "beta": int(beta),
                "block": cell,
            })
    for lat, block in rel1.items():
        entries.append({
            "group": "G-REL1",
            "label": lat,
            "lattice": lat,
            "beta_lo": block.get("beta_lo"),
            "beta_hi": block.get("beta_hi"),
            "block": block,
        })

    assert sum(1 for e in entries if e["group"] == "G-REL2") == 19
    assert sum(1 for e in entries if e["group"] == "G-REL1") == 10
    assert len(entries) == 29

    # ------------------------------------------------------------- readings
    records = []
    for ent in entries:
        blk = ent.pop("block")
        pb = blk["per_basis"]
        assert len(pb) == N_BASES
        for norm, key, npass_key in (("maxfloor", "value_maxfloor",
                                      "n_pass_maxfloor_of_8"),
                                     ("absX", "value_absX",
                                      "n_pass_absX_of_8")):
            vals = [b[key] for b in pb]
            distinct = sorted(set(vals))
            bitwise_identical = len(distinct) == 1
            n_below_6x_bases = sum(1 for v in vals if v < SIX_X)
            committed_mean = blk[norm]["mean"]
            committed_sd = blk[norm]["sd"]

            readings = {
                "R_i0_legacy": {
                    "definition": "per_basis[0].%s (legacy i = 0 draw)" % key,
                    "value": vals[0],
                },
                "R_npass_of_8": {
                    "definition": ("count of passing bases out of 8, "
                                   "committed as %s; the criterion VALUE under "
                                   "this reading is well defined only because "
                                   "all 8 per-basis values are bit-identical "
                                   "(distinct_ieee754_values = %d)"
                                   % (npass_key, len(distinct))),
                    "n_pass_of_8": blk[npass_key],
                    "value": vals[0] if bitwise_identical else None,
                    "n_bases_below_6x_of_8": n_below_6x_bases,
                },
                "R_mean_over_8": {
                    "definition": ("mean over i = 0..7 of %s, computed with "
                                   "math.fsum (correctly rounded) then divided "
                                   "by 8, which is exact in binary; a naive "
                                   "left-to-right sum introduces ulp noise "
                                   "that would move entries across the "
                                   "boundaries counted below" % key),
                    "value": mean(vals),
                    "committed_mean_in_source": committed_mean,
                    "agrees_with_committed_mean_bitwise":
                        mean(vals) == committed_mean,
                },
            }
            for rname, r in readings.items():
                v = r["value"]
                r["ratio_to_tau_rel"] = (None if v is None else v / TAU_REL)
                r["value_repr"] = (None if v is None else repr(v))
                # TWO boundary rules, both reported, neither chosen for the
                # reader.  Several entries sit within ONE ULP of 0.60 and the
                # two rules classify them differently; that is a measured
                # property of the committed file, not a modelling choice.
                r["below_6x_strict_ieee"] = (None if v is None
                                             else bool(v < SIX_X))
                r["below_6x_tol_1e_12"] = (
                    None if v is None
                    else bool(v < SIX_X and abs(v - SIX_X) > TOL * SIX_X))
                r["at_6x_within_1e_12"] = (
                    None if v is None else bool(abs(v - SIX_X) <= TOL * SIX_X))
                r["equals_4_over_7_bitwise"] = (None if v is None
                                                else bool(v == PLATEAU))
                r["equals_4_over_7_within_1e_12"] = (
                    None if v is None else bool(abs(v - PLATEAU)
                                                <= TOL * PLATEAU))
                r["below_4_over_7_tol_1e_12"] = (
                    None if v is None
                    else bool(v < PLATEAU and abs(v - PLATEAU) > TOL * PLATEAU))

            records.append({
                "group": ent["group"],
                "label": ent["label"],
                "normalization": norm,
                "per_basis_values": vals,
                "distinct_ieee754_values_over_8": len(distinct),
                "bitwise_identical_over_8": bitwise_identical,
                "committed_sd_over_8": committed_sd,
                "n_bases_below_6x_of_8": n_below_6x_bases,
                "readings": readings,
            })

    # ------------------------------------------------- per-reading summaries
    reading_names = ["R_i0_legacy", "R_npass_of_8", "R_mean_over_8"]
    summaries = {}
    for norm in ("maxfloor", "absX"):
        for rname in reading_names:
            rows = [(rec["group"], rec["label"],
                     rec["readings"][rname]["value"])
                    for rec in records if rec["normalization"] == norm]
            assert all(v is not None for _, _, v in rows)
            lo = min(rows, key=lambda r: r[2])
            hi = max(rows, key=lambda r: r[2])

            def near(a, b):
                return abs(a - b) <= TOL * b

            below_strict = [(g, l, v) for g, l, v in rows if v < SIX_X]
            below_tol = [(g, l, v) for g, l, v in rows
                         if v < SIX_X and not near(v, SIX_X)]
            at_6x = [(g, l, v) for g, l, v in rows if near(v, SIX_X)]
            plateau_bit = [(g, l, v) for g, l, v in rows if v == PLATEAU]
            plateau_tol = [(g, l, v) for g, l, v in rows if near(v, PLATEAU)]
            sub_plateau = [(g, l, v) for g, l, v in rows
                           if v < PLATEAU and not near(v, PLATEAU)]

            def cnt(sel, grp=None):
                return sum(1 for g, _, _ in sel if grp is None or g == grp)

            def listing(sel):
                return [{"group": g, "label": l, "value": v,
                         "value_repr": repr(v), "ratio_to_tau_rel": v / TAU_REL}
                        for g, l, v in sel]

            summaries["%s | %s" % (norm, rname)] = {
                "normalization": norm,
                "reading": rname,
                "n_entries": len(rows),
                "min": {"value": lo[2], "value_repr": repr(lo[2]),
                        "ratio_to_tau_rel": lo[2] / TAU_REL,
                        "group": lo[0], "label": lo[1]},
                "max": {"value": hi[2], "value_repr": repr(hi[2]),
                        "ratio_to_tau_rel": hi[2] / TAU_REL,
                        "group": hi[0], "label": hi[1]},
                # RULE A: strict IEEE-754 comparison v < 0.60.
                "strict_ieee": {
                    "count_below_6x_over_19_G_REL2": cnt(below_strict, "G-REL2"),
                    "count_below_6x_over_10_G_REL1": cnt(below_strict, "G-REL1"),
                    "count_below_6x_over_all_29": cnt(below_strict),
                    "entries_below_6x": listing(below_strict),
                },
                # RULE B: entries within a relative 1e-12 of 0.60 are counted
                # as AT 6x, not below it.
                "tol_1e_12": {
                    "count_below_6x_over_19_G_REL2": cnt(below_tol, "G-REL2"),
                    "count_below_6x_over_10_G_REL1": cnt(below_tol, "G-REL1"),
                    "count_below_6x_over_all_29": cnt(below_tol),
                    "entries_below_6x": listing(below_tol),
                    "count_at_6x_over_19_G_REL2": cnt(at_6x, "G-REL2"),
                    "count_at_6x_over_all_29": cnt(at_6x),
                    "entries_at_6x": listing(at_6x),
                },
                "count_exactly_5_71x_bitwise_over_19_G_REL2":
                    cnt(plateau_bit, "G-REL2"),
                "count_exactly_5_71x_bitwise_over_all_29": cnt(plateau_bit),
                "count_5_71x_within_1e_12_over_19_G_REL2":
                    cnt(plateau_tol, "G-REL2"),
                "count_5_71x_within_1e_12_over_10_G_REL1":
                    cnt(plateau_tol, "G-REL1"),
                "count_5_71x_within_1e_12_over_all_29": cnt(plateau_tol),
                "entries_at_5_71x_within_1e_12": listing(plateau_tol),
                "count_strictly_below_5_71x_over_all_29": cnt(sub_plateau),
                "entries_strictly_below_5_71x": listing(sub_plateau),
                # Wave 1 claimed BOTH a count (15 of 19 G-REL2 below 6x) and a
                # structure (13 at exactly 5.71x, one at 4.97x). Both halves
                # are checked; a count matching without the structure is
                # reported as such rather than as a reproduction.
                "wave1_count_reproduced_strict_ieee": (
                    cnt(below_strict, "G-REL2") == WAVE1["count_below_6x"]),
                "wave1_count_reproduced_tol_1e_12": (
                    cnt(below_tol, "G-REL2") == WAVE1["count_below_6x"]),
                "wave1_structure_13_at_5_71x_reproduced": (
                    cnt(plateau_tol, "G-REL2") == 13),
                "wave1_structure_one_at_4_97x_reproduced": any(
                    round(v / TAU_REL, 2) == 4.97 for _, _, v in rows),
                "wave1_fully_reproduced_tol_1e_12": (
                    cnt(below_tol, "G-REL2") == WAVE1["count_below_6x"]
                    and cnt(plateau_tol, "G-REL2") == 13
                    and any(round(v / TAU_REL, 2) == 4.97
                            for _, _, v in rows)),
                "wave2_count_reproduced_strict_ieee": (
                    cnt(below_strict) == WAVE2["count_below_6x"]),
                "wave2_count_reproduced_tol_1e_12": (
                    cnt(below_tol) == WAVE2["count_below_6x"]),
                # The two values wave 2 names, checked as values rather than
                # as a count: are they present, and what threshold would make
                # them the only two entries below it?
                "wave2_named_values_present": {
                    "0.486626": any(round(v, 6) == 0.486626
                                    for _, _, v in rows),
                    "0.496557": any(round(v, 6) == 0.496557
                                    for _, _, v in rows),
                },
                "n_entries_strictly_below_5_71x_equals_wave2_count": (
                    cnt(sub_plateau) == WAVE2["count_below_6x"]),
                "multiset_below_6x_ratios_tol": sorted(
                    round(v / TAU_REL, 6) for _, _, v in below_tol),
                "multiset_all_29_ratios": sorted(
                    round(v / TAU_REL, 6) for _, _, v in rows),
                "multiset_all_29_values_repr": sorted(
                    repr(v) for _, _, v in rows),
            }

    # ------------------------------------- the agreed range, re-derived here
    range_checks = {}
    for norm in ("maxfloor", "absX"):
        rows = [(rec["group"], rec["label"],
                 rec["readings"]["R_mean_over_8"]["value"])
                for rec in records if rec["normalization"] == norm]
        lo = min(rows, key=lambda r: r[2])
        hi = max(rows, key=lambda r: r[2])
        range_checks[norm] = {
            "min_value": lo[2], "min_ratio": lo[2] / TAU_REL,
            "min_location": "%s %s" % (lo[0], lo[1]),
            "max_value": hi[2], "max_ratio": hi[2] / TAU_REL,
            "max_location": "%s %s" % (hi[0], hi[1]),
            "min_ratio_rounded_2dp": round(lo[2] / TAU_REL, 2),
            "max_ratio_rounded_2dp": round(hi[2] / TAU_REL, 2),
        }
    agreed = range_checks["maxfloor"]
    range_confirmation = {
        "agreed_two_wave_replicated_range": "4.87x to 31.03x",
        "re_derived_under": "maxfloor normalization, all 29 entries, "
                            "identical under all three readings",
        "re_derived_min_ratio_2dp": agreed["min_ratio_rounded_2dp"],
        "re_derived_max_ratio_2dp": agreed["max_ratio_rounded_2dp"],
        "re_derived_min_value": agreed["min_value"],
        "re_derived_min_location": agreed["min_location"],
        "CONFIRMED": (agreed["min_ratio_rounded_2dp"] == 4.87
                      and agreed["max_ratio_rounded_2dp"] == 31.03),
        "minimum_0_486626_at_G_REL2_L1_L2_beta_15_CONFIRMED": (
            round(agreed["min_value"], 6) == 0.486626
            and agreed["min_location"] == "G-REL2 L1/L2 beta 15"),
        "note_absX": ("under the absX normalization the same 29 entries span "
                      "%.2fx to %.2fx; that is a different normalization of "
                      "the same committed criterion, not a contradiction of "
                      "the agreed range, which is the maxfloor one"
                      % (range_checks["absX"]["min_ratio"],
                         range_checks["absX"]["max_ratio"])),
    }

    # ------------------------------------------------------ P-C1 adjudication input
    def cells_where(pred):
        return [k for k, s in summaries.items() if pred(s)]

    w1_cells = cells_where(lambda s: s["wave1_fully_reproduced_tol_1e_12"])
    w1_count_cells = cells_where(
        lambda s: s["wave1_count_reproduced_tol_1e_12"]
        or s["wave1_count_reproduced_strict_ieee"])
    w2_cells = cells_where(lambda s: s["wave2_count_reproduced_tol_1e_12"]
                           or s["wave2_count_reproduced_strict_ieee"])
    w2_alt_cells = cells_where(
        lambda s: s["n_entries_strictly_below_5_71x_equals_wave2_count"])
    pc1 = {
        "statement": ("PREREG-1 section 8.1 P-C1: at least one declared "
                      "reading reproduces exactly one of the two conflicting "
                      "counts."),
        "falsifier": "no reading reproduces either count",
        "wave1_count_reproduced_somewhere": bool(w1_count_cells),
        "wave1_count_reproducing_cells": w1_count_cells,
        "wave1_fully_reproduced_somewhere": bool(w1_cells),
        "wave1_reproducing_cells": w1_cells,
        "wave2_count_reproduced_somewhere": bool(w2_cells),
        "wave2_reproducing_cells": w2_cells,
        "wave2_count_matches_a_DIFFERENT_threshold_at": w2_alt_cells,
        "wave2_alternative_threshold_note": (
            "the two values wave 2 names, 0.486626 and 0.496557, are the ONLY "
            "two entries strictly below the 4/7 = 5.714x plateau under the "
            "maxfloor normalization. A count of 2 is what a 5.71x threshold "
            "yields over the 29 entries; the 6x threshold yields a larger "
            "count under every reading and both boundary rules. This is a "
            "recorded observation about which threshold the count of 2 "
            "corresponds to. It is NOT a finding that wave 2 applied that "
            "threshold, which this tabulation cannot see."),
        "OBSERVATION_ONLY": ("the Executor records which counts reproduce "
                             "under which reading and normalization. The "
                             "adjudication of C-1, and any decision to make "
                             "either count citable, belong to the Coordinator "
                             "in the batch decision. NEITHER COUNT IS CITABLE "
                             "UNTIL THEN, and 'a factor of 6 to 31' remains "
                             "FALSE and uncitable regardless."),
    }

    src_sha_after = sha256_of(SRC)
    payload = {
        "task_id": "TASK-20260812-78a6e3",
        "batch_id": "BATCH-4ed139",
        "goal_id": "GOAL-MLKEM-005",
        "role": "executor",
        "rider": "(i) -- the C-1 resolving tabulation",
        "outcome_row": "R2-OUT-6",
        "claim_tier": "toy",
        "certificate": {
            "kind": "none",
            "reason": ("pure re-tabulation of a committed measurement file. "
                       "No discrete-log solve and no factor-base relation is "
                       "claimed or produced, so docs/claims-and-verification.md "
                       "requires no solution certificate."),
        },
        "governed_by": {
            "prereg": ("coordination/goals/GOAL-MLKEM-005/batches/BATCH-4ed139/"
                       "tasks/TASK-20260812-34b86c/prereg.md"),
            "section": "8.1 (rider i), with sections 11 and 11.1 binding",
            "decision": "DEC-20260812-7c4a1e (C-1, AM-17)",
        },
        "source": {
            "path": SRC_REL,
            "sha256": src_sha,
            "sha256_after_read": src_sha_after,
            "unmodified_by_this_run": (src_sha == src_sha_after
                                       and os.stat(SRC).st_mtime_ns
                                       == src_mtime_before),
            "source_task": "TASK-20260809-cda2f6",
            "source_batch": "BATCH-9e3584",
        },
        "git": {
            "revision": git("rev-parse", "HEAD"),
            "branch": git("rev-parse", "--abbrev-ref", "HEAD"),
            "dirty": bool(git("status", "--porcelain")),
            "dirty_paths": [ln for ln in git("status", "--porcelain").split("\n")
                            if ln],
        },
        "environment": {
            "operating_system": platform.platform(),
            "python_version": sys.version.split()[0],
            "dependencies": {"stdlib_only": True,
                             "numpy": "not imported",
                             "fpylll": "not imported"},
        },
        "frozen_constants": {
            "tau_rel": TAU_REL,
            "six_x_boundary": SIX_X,
            "six_x_boundary_repr": repr(SIX_X),
            "six_x_boundary_note": (
                "6.0 * 0.10 is %r in IEEE-754 double, NOT 0.6. Under the "
                "strict rule an entry stored as exactly 0.6 therefore counts "
                "as BELOW 6x; under the tolerance rule it counts as AT 6x. "
                "The two rules differ by exactly 2 G-REL2 cells and that "
                "difference is reported, not resolved here." % SIX_X),
            "boundary_relative_tolerance": TOL,
            "n_bases": N_BASES,
            "plateau_value_4_over_7": PLATEAU,
            "plateau_value_4_over_7_repr": repr(PLATEAU),
            "plateau_note": MOD_NOTE,
        },
        "declared_readings": {
            "R_i0_legacy": "legacy i = 0 draw",
            "R_npass_of_8": "count of passing bases out of 8",
            "R_mean_over_8": "mean over the 8 bases",
        },
        "normalization_axis_disclosure": (
            "the committed file stores TWO normalizations of the same "
            "criterion value at every entry -- value_maxfloor and value_absX. "
            "The normalization is NOT one of the three declared readings; it "
            "is tabulated here because a count of entries below 6x is "
            "undefined without naming it, and because the two conflicting "
            "waves' numbers differ along axes this tabulation must expose "
            "rather than choose between."),
        "conflicting_claims": {"wave1": WAVE1, "wave2": WAVE2},
        "entries": records,
        "per_reading_summaries": summaries,
        "range_re_derivation": range_checks,
        "range_confirmation": range_confirmation,
        "P_C1": pc1,
        "binding_carries": [
            "AM-10..AM-14 (DEC-20260808-05b684), AM-15, AM-16 "
            "(DEC-20260809-afe29b), AM-17 (DEC-20260812-7c4a1e).",
            "AM-3 IS NOT RETIRED; its 0.096 family-wise false-failure bound "
            "stands.",
            "BATCH-a44d08 IS NOT RESCORED IN ANY RESPECT.",
            "'a factor of 6 to 31' is FALSE and is not citable anywhere; the "
            "citable range is 4.87x to 31.03x.",
            "Both sub-6x counts remain NOT CITABLE pending the Coordinator's "
            "ruling on this tabulation.",
            "CLAIM TIER STAYS TOY: nothing here bears on ML-KEM security, on "
            "any FIPS 203 parameter set, on any attack cost or on any cost "
            "model.",
        ],
        "measurement_wall_clock_seconds": None,
        "validity": {"status": "valid",
                     "reason": ("deterministic re-tabulation of a committed "
                                "file pinned by sha256; no randomness, no "
                                "reduction, no external dependency")},
        "randomness": "none -- this run draws no random numbers",
        "finished_utc": None,
    }
    payload["measurement_wall_clock_seconds"] = round(time.time() - t0, 4)
    payload["finished_utc"] = time.strftime("%Y-%m-%dT%H:%M:%SZ",
                                            time.gmtime())

    with open(OUT, "w") as fh:
        json.dump(payload, fh, indent=1, sort_keys=False)
        fh.write("\n")

    # ------------------------------------------------------------- stdout
    p = print
    p("RIDER (i) -- C-1 RESOLVING TABULATION -- TASK-20260812-78a6e3")
    p("GOAL-MLKEM-005 / BATCH-4ed139 / outcome row R2-OUT-6 / CLAIM TIER TOY")
    p("source: %s" % SRC_REL)
    p("source sha256: %s" % src_sha)
    p("source unmodified by this run: %s"
      % payload["source"]["unmodified_by_this_run"])
    p("tau_rel = %r ; 6x boundary computed as 6.0*tau_rel = %r ; 4/7 = %r"
      % (TAU_REL, SIX_X, PLATEAU))
    p("NOTE ON THE BOUNDARY: 6.0*0.10 is %r in IEEE-754 double, NOT 0.6."
      % SIX_X)
    p("  RULE A (strict) compares against that value, so an entry stored as")
    p("  exactly 0.6 counts as BELOW it. RULE B counts anything within a")
    p("  relative %g of the boundary as AT 6x. Both are reported; neither is"
      % TOL)
    p("  chosen for the reader, and the two rules differ by 2 cells.")
    p("NOTE ON 5.71x: %s" % MOD_NOTE)
    p("entries: 19 G-REL2 cells + 10 G-REL1 lattices = 29")
    p("")
    p("PER-ENTRY MULTISET (value / ratio to tau_rel), by normalization.")
    p("All 8 per-basis values are bit-identical at every entry under both")
    p("normalizations, so the three declared readings coincide numerically;")
    p("the per-reading columns below are printed separately anyway.")
    p("")
    hdr = ("%-7s %-16s %-9s %-22s %-22s %-22s %-9s %-7s %-7s"
           % ("group", "label", "norm", "i0", "npass_val", "mean8",
              "ratio", "b6x_ie", "b6x_tol"))
    p(hdr)
    p("-" * len(hdr))
    for rec in records:
        r = rec["readings"]
        p("%-7s %-16s %-9s %-22s %-22s %-22s %-9.4f %-7s %-7s"
          % (rec["group"], rec["label"], rec["normalization"],
             r["R_i0_legacy"]["value_repr"],
             r["R_npass_of_8"]["value_repr"],
             r["R_mean_over_8"]["value_repr"],
             r["R_mean_over_8"]["ratio_to_tau_rel"],
             r["R_mean_over_8"]["below_6x_strict_ieee"],
             r["R_mean_over_8"]["below_6x_tol_1e_12"]))
        p("        n_pass_of_8 = %d ; distinct IEEE-754 values over 8 = %d ; "
          "committed sd over 8 = %s ; mean bitwise == committed mean: %s ; "
          "== 4/7 bitwise: %s ; == 4/7 to 1e-12: %s"
          % (r["R_npass_of_8"]["n_pass_of_8"],
             rec["distinct_ieee754_values_over_8"],
             rec["committed_sd_over_8"],
             r["R_mean_over_8"]["agrees_with_committed_mean_bitwise"],
             r["R_mean_over_8"]["equals_4_over_7_bitwise"],
             r["R_mean_over_8"]["equals_4_over_7_within_1e_12"]))
    p("")
    p("PER-READING SUMMARIES")
    for k in sorted(summaries):
        s = summaries[k]
        p("")
        p("  [%s]" % k)
        p("    min  %.12f = %.4fx  at %s %s"
          % (s["min"]["value"], s["min"]["ratio_to_tau_rel"],
             s["min"]["group"], s["min"]["label"]))
        p("    max  %.12f = %.4fx  at %s %s"
          % (s["max"]["value"], s["max"]["ratio_to_tau_rel"],
             s["max"]["group"], s["max"]["label"]))
        a, b = s["strict_ieee"], s["tol_1e_12"]
        p("    below 6x [RULE A strict IEEE v < 0.60]:  %d of 19 G-REL2   "
          "%d of 10 G-REL1   %d of all 29"
          % (a["count_below_6x_over_19_G_REL2"],
             a["count_below_6x_over_10_G_REL1"],
             a["count_below_6x_over_all_29"]))
        p("    below 6x [RULE B within 1e-12 of 0.60 counted AS 6x]:  "
          "%d of 19 G-REL2   %d of 10 G-REL1   %d of all 29"
          % (b["count_below_6x_over_19_G_REL2"],
             b["count_below_6x_over_10_G_REL1"],
             b["count_below_6x_over_all_29"]))
        p("    AT 6x within 1e-12: %d of 19 G-REL2, %d of all 29  %s"
          % (b["count_at_6x_over_19_G_REL2"], b["count_at_6x_over_all_29"],
             [(e["label"], e["value_repr"]) for e in b["entries_at_6x"]]))
        p("    at 5.71x (= 4/7) bitwise: %d of 19 G-REL2, %d of all 29 ; "
          "within 1e-12: %d of 19 G-REL2, %d of 10 G-REL1, %d of all 29"
          % (s["count_exactly_5_71x_bitwise_over_19_G_REL2"],
             s["count_exactly_5_71x_bitwise_over_all_29"],
             s["count_5_71x_within_1e_12_over_19_G_REL2"],
             s["count_5_71x_within_1e_12_over_10_G_REL1"],
             s["count_5_71x_within_1e_12_over_all_29"]))
        p("    strictly below 5.71x over all 29: %d  %s"
          % (s["count_strictly_below_5_71x_over_all_29"],
             [(e["label"], round(e["ratio_to_tau_rel"], 4))
              for e in s["entries_strictly_below_5_71x"]]))
        p("    WAVE 1 (15 of 19 G-REL2 below 6x): count reproduced  "
          "RULE A %s / RULE B %s ; 13 at 5.71x: %s ; one at 4.97x: %s ; "
          "FULLY reproduced under RULE B: %s"
          % (s["wave1_count_reproduced_strict_ieee"],
             s["wave1_count_reproduced_tol_1e_12"],
             s["wave1_structure_13_at_5_71x_reproduced"],
             s["wave1_structure_one_at_4_97x_reproduced"],
             s["wave1_fully_reproduced_tol_1e_12"]))
        p("    WAVE 2 (2 of 29 below 6x): count reproduced  RULE A %s / "
          "RULE B %s ; both named values present: %s ; a 5.71x threshold "
          "would give exactly 2: %s"
          % (s["wave2_count_reproduced_strict_ieee"],
             s["wave2_count_reproduced_tol_1e_12"],
             s["wave2_named_values_present"],
             s["n_entries_strictly_below_5_71x_equals_wave2_count"]))
    p("")
    p("RANGE RE-DERIVATION (mean-over-8 reading, all 29 entries)")
    for norm, rc in range_checks.items():
        p("  %-9s %.6f (%.2fx) at %s   ..   %.6f (%.2fx) at %s"
          % (norm, rc["min_value"], rc["min_ratio"], rc["min_location"],
             rc["max_value"], rc["max_ratio"], rc["max_location"]))
    p("  agreed two-wave range 4.87x to 31.03x re-derived under maxfloor: %s"
      % range_confirmation["CONFIRMED"])
    p("  minimum 0.486626 at G-REL2 L1/L2 beta 15 re-derived: %s"
      % range_confirmation["minimum_0_486626_at_G_REL2_L1_L2_beta_15_CONFIRMED"])
    p("")
    p("P-C1 ADJUDICATION INPUT (observation only; the Coordinator rules)")
    p("  wave 1 count reproduced under: %s"
      % (pc1["wave1_count_reproducing_cells"] or "NO reading/normalization"))
    p("  wave 1 count AND structure reproduced under: %s"
      % (pc1["wave1_reproducing_cells"] or "NO reading/normalization"))
    p("  wave 2 count reproduced under: %s"
      % (pc1["wave2_reproducing_cells"] or "NO reading/normalization"))
    p("  wave 2's count of 2 equals the number of entries strictly below the")
    p("  4/7 = 5.71x plateau under: %s"
      % (pc1["wave2_count_matches_a_DIFFERENT_threshold_at"] or "nowhere"))
    p("")
    p("BINDING: NEITHER SUB-6x COUNT IS CITABLE until the Coordinator rules "
      "in the batch decision.")
    p("BINDING: 'a factor of 6 to 31' is FALSE; the citable range is 4.87x to "
      "31.03x.")
    p("BINDING: CLAIM TIER TOY -- nothing here bears on ML-KEM security, any "
      "FIPS 203 parameter set, any attack cost or any cost model.")
    p("")
    p("wrote %s" % os.path.relpath(OUT, REPO))
    p("measurement wall clock: %.4f s"
      % payload["measurement_wall_clock_seconds"])


if __name__ == "__main__":
    main()

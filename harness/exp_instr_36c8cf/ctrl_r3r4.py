"""EXP-INSTR-36c8cf: R3/R4 reanalysis and control (TASK-20260811-bc336d).

Dispatched directly from a Coordinator decision's named `next_actions`
(DEC-20260811-a4c7ec), following the CTRL-VALUESHUFFLE precedent
(`harness/ctrl_valueshuffle.py`): a NEW module producing a NEW immutable run
under an EXISTING, approved experiment contract (EXP-INSTR-36c8cf,
`specification.yaml` `status: approved`), with no new specification.yaml and
no amendment. This module does not approve, reject, withdraw or amend
EXP-INSTR-36c8cf amendment v2 (`approved_by` stays null there); it does not
move any hypothesis status; it makes no curve-side, within-class or
between-class claim. `claim_tier: toy`, `sota_delta: 0` on every axis.

R3 and R4 are the required controls named by RT-20260811-35ab34 (report lines
294-299, 434-444) and adjudicated as the concrete next step by
DEC-20260811-a4c7ec.next_actions:

  R3a  Leave-one-out (jackknife) exceedance-rate reanalysis of the
       ALREADY-COLLECTED rung-3 (n_seeds=48) reference-sampling data
       (`RUN-INSTR-36c8cf-phaseA-v2-57ca9a/sr3v3-reference-sampling.json`,
       family 4001). For each of the 13 density rows: hold out each of the
       48 per-seed variance ratios, refit `sr3v3.interval_for_rung` on the
       remaining 47 with a freshly-computed z (`sr3v3.z_from_coverage`,
       standing rule A4: z is never transcribed), and record whether the
       held-out ratio falls outside the refit interval, and on which side.
       Reported next to the file's own IN-SAMPLE exceedance count (the
       already-computed rung-3 interval's own recorded max/min against its
       own recorded interval_high/interval_low) and the Gaussian-rule
       expected count under two-sided coverage 259/260 (n_trials / 260).

  R3b  Fisher's-exact correlation test on the 13-row 2x2 table "row has
       >=1 jackknife exceedance" x "row fails `sr3v3.stability_check` at the
       rung2->rung3 transition", the latter recomputed here from the raw
       rung-2/rung-3 interval dicts in the same committed file by calling
       the frozen `stability_check` function directly (not hand-copied from
       any derived report). Exact p-value by direct hypergeometric
       enumeration (`math.comb`), formula stated in `fishers_exact_2x2`.

  R4   A Student-t(df=5) null-object control (finite variance, heavy tail):
       for each of the 13 rows, draw a synthetic 1536-sample seed ladder
       with the row's OWN observed rung-3 location (mean) and scale
       (sd_sample_n_minus_1), through the IDENTICAL, UNMODIFIED
       `interval_for_rung` / `stability_check` / `z_from_coverage` pipeline
       functions the real characterisation uses, nested exactly as E2/E6
       nest (each rung a superset of the previous). Replicated across many
       independent seeds (`numpy.random.SeedSequence(...).spawn(...)`, one
       declared master seed) to report an empirical accept-by-rung-8 rate,
       the empirical distribution over which rung first accepts, and (as a
       diagnostic only, gating nothing) the per-replication sample skewness
       and terminal-rung exceedance/side-asymmetry, as a distribution across
       replications.

WHAT THIS MODULE DOES NOT DO. It does not discharge R1, R2 or R5 (textual /
analytical repairs to the amendment, filed only by the Coordinator). It does
not touch `RUN-INSTR-36c8cf-phaseA-v2-57ca9a` or
`RUN-INSTR-36c8cf-phaseA-2a5cd1` (read-only inputs). It does not edit
`sr3v3.py`, `phase_a_v2.py`, `refvalues.py`, `refvalues_v2.py`, or anything
under `experiments/`. It interprets nothing against HEUR-INSTR-4 or the
amendment's approval -- that judgement belongs to the Coordinator, after
independent review, in a decision record.
"""
from __future__ import annotations

import argparse
import json
import math
import os
import time

import numpy as np

from harness.exp_instr_36c8cf import refvalues_v2, sr3v3
from harness.exp_instr_36c8cf.refvalues import sha256_of

EXPERIMENT_ID = "EXP-INSTR-36c8cf"
RUN_AREA = "INSTR"
CONTROL_ID = "CTRL-R3R4-JACKKNIFE-NULLOBJECT"
TASK_ID = "TASK-20260811-bc336d"

REFERENCE_RUN_ID = "RUN-INSTR-36c8cf-phaseA-v2-57ca9a"
REFERENCE_SAMPLING_JSON = (
    f"experiments/{EXPERIMENT_ID}/runs/{REFERENCE_RUN_ID}/"
    "sr3v3-reference-sampling.json")
INTERVAL_STABILITY_JSON = (
    f"experiments/{EXPERIMENT_ID}/runs/{REFERENCE_RUN_ID}/"
    "sr3v3-interval-stability.json")
AMENDMENT_V1 = f"experiments/{EXPERIMENT_ID}/amendments/v1.yaml"
AMENDMENT_V2 = f"experiments/{EXPERIMENT_ID}/amendments/v2.yaml"
SR3V3_MODULE = "harness/exp_instr_36c8cf/sr3v3.py"
REFVALUES_V2_MODULE = "harness/exp_instr_36c8cf/refvalues_v2.py"

FAMILY_PRIME = "4001"          # RT-20260811-35ab34's named family/rung.
RUNG3_INDEX = 2                # zero-based: rungs[0]=rung1(n=12), [1]=rung2(n=24), [2]=rung3(n=48)

# R4 ladder: mirrors E2/E6's nesting exactly (each rung a superset).
R4_RUNG_SIZES = [12, 24, 48, 96, 192, 384, 768, 1536]

# DECLARED MASTER SEEDS. Arbitrary fixed integers named explicitly here, NOT
# the system clock, NOT PID, and NOT a seed borrowed from elsewhere in this
# contract (the contract's own declared seeds -- 20260810, 20260811,
# 11235813, etc. -- are reserved for the real characterisation and its own
# amendments; reusing one here would make this control's randomness look
# entangled with the contract's own seed schedule, which it is not). Chosen
# as recognisable fixed constants with no other role in this campaign.
R4_MASTER_SEED = 314159265          # Student-t(df=5) null-object arm.
R4_GAUSSIAN_MASTER_SEED = 271828182  # OPTIONAL matched-variance Gaussian arm.

R4_REPLICATIONS = 500
R4_GAUSSIAN_REPLICATIONS = 500

CERTIFICATE_NOTE = (
    "certificate.kind: none, EXPLICITLY. This is post-hoc statistics "
    "(jackknife reanalysis, Fisher's-exact test) and pure numpy simulation "
    "(Student-t / Gaussian null-object control). No discrete logarithm is "
    "computed and no factor-base relation is claimed anywhere in this "
    "module, so there is no solve or relation to certify "
    "(docs/claims-and-verification.md).")

SCOPE_NOTE = (
    "Tier TOY. Instrument characterisation only: a statistical reanalysis "
    "of an already-collected reference-sampling distribution, plus a "
    "synthetic null-object control run through the same pipeline functions. "
    "No ECDLP attack, exponent or speedup claim of any kind. claim_tier "
    "toy, sota_delta 0 on every axis. This module does not approve, reject "
    "or amend EXP-INSTR-36c8cf amendment v2, and does not move any "
    "hypothesis status.")


def _repo() -> str:
    return os.path.dirname(os.path.dirname(os.path.dirname(
        os.path.abspath(__file__))))


def _run_dir(run_id: str) -> str:
    return os.path.join(_repo(), "experiments", EXPERIMENT_ID, "runs", run_id)


def _load_json(rel: str) -> dict:
    with open(os.path.join(_repo(), rel), encoding="utf-8") as fh:
        return json.load(fh)


# --------------------------------------------------------------------------
# frozen inputs, read at run time -- nothing transcribed (standing rule A4)
# --------------------------------------------------------------------------


def load_frozen_inputs() -> dict:
    """Every frozen number this module needs, read from its own record."""
    z_block = sr3v3.z_from_coverage(519, 520)
    amend = refvalues_v2.amendment_frozen_parameters()
    grid = refvalues_v2.icinv_frozen_grid()
    return {
        "z_block": z_block,
        "z": z_block["z"],
        "amendment_frozen_parameters": amend,
        "stability_relative_half_width_pct": amend[
            "stability_relative_half_width_pct"],
        "icinv_frozen_grid": grid,
        "fb_sizes": list(grid["factor_base_sizes"]),
        "source_sha256": {
            REFERENCE_SAMPLING_JSON: sha256_of(REFERENCE_SAMPLING_JSON),
            AMENDMENT_V1: sha256_of(AMENDMENT_V1),
            AMENDMENT_V2: sha256_of(AMENDMENT_V2),
            SR3V3_MODULE: sha256_of(SR3V3_MODULE),
            REFVALUES_V2_MODULE: sha256_of(REFVALUES_V2_MODULE),
        },
    }


def load_rung3_family(fb_sizes: list) -> dict:
    """family["4001"]'s rung 3 (n_seeds=48) intervals dict, and rungs 1/2."""
    data = _load_json(REFERENCE_SAMPLING_JSON)
    family = data["families"][FAMILY_PRIME]
    rungs = family["rungs"]
    if len(rungs) != 3:
        raise RuntimeError(
            f"expected 3 rungs in family {FAMILY_PRIME}, found {len(rungs)}")
    rung3 = rungs[RUNG3_INDEX]["intervals"]
    for fb in fb_sizes:
        n = rung3[str(fb)]["n_seeds"]
        if n != 48:
            raise RuntimeError(
                f"row fb={fb} rung 3 has n_seeds={n}, expected 48")
    return {"raw": data, "family": family, "rungs": rungs,
            "rung1": rungs[0]["intervals"], "rung2": rungs[1]["intervals"],
            "rung3": rung3}


# --------------------------------------------------------------------------
# R3a: leave-one-out (jackknife) exceedance-rate reanalysis
# --------------------------------------------------------------------------


def jackknife_row(per_seed_ratios: dict, z: float) -> dict:
    """Hold out each of the 48 seeds; refit `interval_for_rung` on the other
    47 with the given (freshly-computed) z; record whether the held-out
    ratio falls outside the refit interval, and on which side.
    """
    seeds = sorted(per_seed_ratios, key=int)
    if len(seeds) != 48:
        raise RuntimeError(f"expected 48 seeds, found {len(seeds)}")
    below = above = within = 0
    trials = []
    for held_out in seeds:
        rest = [per_seed_ratios[s] for s in seeds if s != held_out]
        refit = sr3v3.interval_for_rung(rest, z)
        held_val = per_seed_ratios[held_out]
        if held_val < refit["interval_low"]:
            side, below = "below", below + 1
        elif held_val > refit["interval_high"]:
            side, above = "above", above + 1
        else:
            side, within = "within", within + 1
        trials.append({
            "held_out_seed": int(held_out),
            "held_out_ratio": held_val,
            "refit_n_seeds": refit["n_seeds"],
            "refit_interval_low": refit["interval_low"],
            "refit_interval_high": refit["interval_high"],
            "side": side,
        })
    return {"n_trials": len(seeds), "exceed_below": below,
            "exceed_above": above, "exceed_total": below + above,
            "within": within, "trials": trials}


def r3a_analysis(rung3: dict, fb_sizes: list, z: float) -> dict:
    per_row = {}
    jk_below = jk_above = jk_trials = 0
    in_below = in_above = 0
    for fb in fb_sizes:
        row = rung3[str(fb)]
        jk = jackknife_row(row["per_seed_ratios"], z)
        # IN-SAMPLE exceedance: recoverable directly from the committed
        # file's own recorded rung-3 interval (mean +/- z*sd fit on all 48
        # seeds), not recomputed -- this is the "naive 2.4" reference point.
        row_in_below = int(row["min_per_seed_ratio"] < row["interval_low"])
        row_in_above = int(row["max_per_seed_ratio"] > row["interval_high"])
        per_row[str(fb)] = {
            "fb_size": fb,
            "jackknife": jk,
            "in_sample_exceed_below": row_in_below,
            "in_sample_exceed_above": row_in_above,
            "in_sample_exceed_total": row_in_below + row_in_above,
            "in_sample_interval_low": row["interval_low"],
            "in_sample_interval_high": row["interval_high"],
            "in_sample_min_per_seed_ratio": row["min_per_seed_ratio"],
            "in_sample_max_per_seed_ratio": row["max_per_seed_ratio"],
            "in_sample_z": row["z"],
            "recomputed_z": z,
        }
        jk_below += jk["exceed_below"]
        jk_above += jk["exceed_above"]
        jk_trials += jk["n_trials"]
        in_below += row_in_below
        in_above += row_in_above
    gaussian_expected = jk_trials / 260.0
    return {
        "fb_sizes": fb_sizes,
        "per_row": per_row,
        "jackknife_total_trials": jk_trials,
        "jackknife_total_exceed_below": jk_below,
        "jackknife_total_exceed_above": jk_above,
        "jackknife_total_exceed": jk_below + jk_above,
        "in_sample_total_exceed_below": in_below,
        "in_sample_total_exceed_above": in_above,
        "in_sample_total_exceed": in_below + in_above,
        "gaussian_rule_expected_count": gaussian_expected,
        "gaussian_rule_expected_count_formula": (
            "n_trials / 260 = (13 rows * 48 seeds) / 260, where 260 is the "
            "denominator implied by two-sided coverage 259/260 (alpha = "
            "1 - 259/260 = 1/260), matching z_from_coverage(519, 520): "
            "two-sided alpha = 2*(1 - 519/520) = 1/260."),
        "jackknife_exceeds_in_sample": bool(
            (jk_below + jk_above) > (in_below + in_above)),
        "note": (
            "V2's prediction (F3): in-sample checking mechanically "
            "suppresses the true exceedance rate because the interval at "
            "each row is fit from the same 48 seeds whose own extremes are "
            "checked against it. This states the comparison plainly; it "
            "does not conclude anything about HEUR-INSTR-4."),
    }


# --------------------------------------------------------------------------
# R3b: stability-failure correlation (2x2 table, exact Fisher's test)
# --------------------------------------------------------------------------


def fishers_exact_2x2(a: int, b: int, c: int, d: int) -> dict:
    """Exact two-sided Fisher's test on a 2x2 table by direct hypergeometric
    enumeration (no scipy).

        row1 = a + b   (row category 1 total: "has jackknife exceedance")
        row2 = c + d   (row category 2 total: "no jackknife exceedance")
        col1 = a + c   (column category 1 total: "fails stability")
        col2 = b + d   (column category 2 total: "does not fail stability")
        n    = a+b+c+d

    Under the null (fixed margins), the top-left cell x follows a
    hypergeometric distribution:

        P(X = x) = C(row1, x) * C(row2, col1 - x) / C(n, col1)

    for x in [max(0, col1-row2), min(row1, col1)]. The two-sided p-value is
    the sum of P(X = x) over every x in that range whose probability is
    <= P(X = a) (the observed table's own probability), i.e. every table at
    least as extreme as the one observed, using the "sum of probabilities as
    extreme or more extreme" convention (the standard exact-test definition,
    equivalent to `scipy.stats.fisher_exact`'s default two-sided p-value).
    """
    row1, row2 = a + b, c + d
    col1, col2 = a + c, b + d
    n = a + b + c + d

    def p_of(x: int):
        y = row1 - x
        w = col1 - x
        v = row2 - w
        if y < 0 or w < 0 or v < 0:
            return None
        return (math.comb(row1, x) * math.comb(row2, w)) / math.comb(n, col1)

    lo = max(0, col1 - row2)
    hi = min(row1, col1)
    obs_p = p_of(a)
    # tolerance guards against floating comparison excluding the observed
    # table itself due to rounding.
    tol = 1e-9 * (obs_p if obs_p else 1.0)
    two_sided = 0.0
    per_x = {}
    for x in range(lo, hi + 1):
        px = p_of(x)
        per_x[x] = px
        if px is not None and px <= obs_p + tol:
            two_sided += px
    return {
        "table": {"a_exceed_and_fails": a, "b_exceed_and_ok": b,
                  "c_noexceed_and_fails": c, "d_noexceed_and_ok": d},
        "row1_has_jackknife_exceedance": row1,
        "row2_no_jackknife_exceedance": row2,
        "col1_fails_stability": col1,
        "col2_ok_stability": col2,
        "n": n,
        "p_observed_table": obs_p,
        "p_value_two_sided": two_sided,
        "support_x_range": [lo, hi],
        "formula": (
            "P(X=x) = C(row1,x)*C(row2,col1-x)/C(n,col1); two-sided "
            "p-value = sum of P(X=x) over x in [max(0,col1-row2), "
            "min(row1,col1)] with P(X=x) <= P(X=a_observed)."),
    }


def r3b_analysis(rung2: dict, rung3: dict, fb_sizes: list,
                 stability_pct: float, r3a: dict) -> dict:
    # Recompute the rung2->rung3 stability check from the RAW intervals via
    # the frozen function -- not hand-copied from any derived report. May be
    # cross-checked (not sourced) against sr3v3-interval-stability.json's own
    # rung-3 `stability_vs_previous_rung`.
    stab = sr3v3.stability_check(rung2, rung3, stability_pct)
    rows_failing = set(stab["rows_failing"])

    rows = []
    a = b = c = d = 0
    for fb in fb_sizes:
        has_exceed = r3a["per_row"][str(fb)]["jackknife"]["exceed_total"] >= 1
        fails_stability = fb in rows_failing
        rows.append({"fb_size": fb, "jackknife_exceedance": has_exceed,
                     "fails_stability_rung2_to_rung3": fails_stability})
        if has_exceed and fails_stability:
            a += 1
        elif has_exceed and not fails_stability:
            b += 1
        elif not has_exceed and fails_stability:
            c += 1
        else:
            d += 1
    fisher = fishers_exact_2x2(a, b, c, d)
    return {
        "stability_check_recomputed": stab,
        "rows_failing_stability": sorted(rows_failing),
        "rows": rows,
        "contingency_table": fisher["table"],
        "fisher_exact": fisher,
    }


def cross_check_against_committed_stability(rung3_stability_recomputed: dict
                                            ) -> dict:
    """OPTIONAL sanity cross-check against
    sr3v3-interval-stability.json's own rung-3 `stability_vs_previous_rung`
    (a derived report artifact from the same reference run). The number this
    module REPORTS in R3b comes from its own call to `stability_check`
    above; this function only checks the two agree, per the handoff's own
    instruction ("you may cross-check it ... but the number you report must
    come from your own call to stability_check").
    """
    committed = _load_json(INTERVAL_STABILITY_JSON)
    committed_rung3 = committed["families"][FAMILY_PRIME]["rungs"][
        RUNG3_INDEX]["stability_vs_previous_rung"]
    agree_met = (committed_rung3["met_at_every_row"]
                == rung3_stability_recomputed["met_at_every_row"])
    committed_failing = sorted(int(k) for k, v in committed_rung3["rows"].items()
                               if not v["within_rule"])
    recomputed_failing = rung3_stability_recomputed["rows_failing"]
    agree_failing = committed_failing == recomputed_failing
    return {
        "source": INTERVAL_STABILITY_JSON,
        "source_sha256": sha256_of(INTERVAL_STABILITY_JSON),
        "committed_met_at_every_row": committed_rung3["met_at_every_row"],
        "recomputed_met_at_every_row":
            rung3_stability_recomputed["met_at_every_row"],
        "agree_on_met_at_every_row": agree_met,
        "committed_rows_failing": committed_failing,
        "recomputed_rows_failing": recomputed_failing,
        "agree_on_rows_failing": agree_failing,
        "note": (
            "Sanity cross-check only; NOT the source of R3b's reported "
            "number, which comes from this module's own call to "
            "sr3v3.stability_check on the raw rung-2/rung-3 interval "
            "dicts (per the handoff's own instruction)."),
    }


# --------------------------------------------------------------------------
# R4: Student-t(df=5) null-object control, replicated
# --------------------------------------------------------------------------


def _skewness(x: np.ndarray) -> float | None:
    """Sample skewness, biased (Fisher-Pearson) estimator g1:

        g1 = mean((x - mean(x))^3) / std(x)^3

    with `std(x)` the POPULATION (ddof=0) standard deviation -- the same
    convention numpy's default `.std()` uses and the plain, uncorrected
    third-standardised-moment formula (no small-sample bias correction
    applied, since this is a diagnostic on already-large rung sizes, not an
    inferential statistic anything gates on). Returns None when std is 0
    (degenerate; cannot occur here since scale > 0 by construction, guarded
    anyway).
    """
    mean = float(np.mean(x))
    std = float(np.std(x))
    if std == 0.0:
        return None
    return float(np.mean((x - mean) ** 3) / std ** 3)


def draw_null_object_replication(fb_sizes: list, loc_scale: dict, z: float,
                                 stability_pct: float, rep_seed,
                                 distribution: str,
                                 rung_sizes=R4_RUNG_SIZES) -> dict:
    """One replication of the null-object ladder across all 13 rows.

    `distribution` is "student_t5" (draws standard_t(df=5), rescaled to the
    row's own observed scale via /sqrt(5/3), since Student-t(df=5) has
    variance 5/3 in standard form) or "gaussian" (the OPTIONAL matched-
    variance calibration arm: draws Generator.normal(loc, scale) directly,
    no rescale needed since a standard normal already has unit variance).
    """
    row_seeds = rep_seed.spawn(len(fb_sizes))
    draws = {}
    for fb, rseed in zip(fb_sizes, row_seeds):
        rng = np.random.default_rng(rseed)
        loc = loc_scale[str(fb)]["mean"]
        scale = loc_scale[str(fb)]["sd_sample_n_minus_1"]
        n_max = rung_sizes[-1]
        if distribution == "student_t5":
            t = rng.standard_t(df=5, size=n_max)
            draws[fb] = loc + (scale / math.sqrt(5.0 / 3.0)) * t
        elif distribution == "gaussian":
            draws[fb] = rng.normal(loc=loc, scale=scale, size=n_max)
        else:
            raise ValueError(distribution)

    accepted_rung = None
    prev_intervals = None
    rung_snapshots = {}
    for k, n in enumerate(rung_sizes):
        cur_intervals = {str(fb): sr3v3.interval_for_rung(
            [float(v) for v in draws[fb][:n]], z) for fb in fb_sizes}
        rung_snapshots[k + 1] = cur_intervals
        if k > 0:
            stab = sr3v3.stability_check(prev_intervals, cur_intervals,
                                         stability_pct)
            if stab["met_at_every_row"] and accepted_rung is None:
                accepted_rung = k + 1
        prev_intervals = cur_intervals

    terminal_rung = accepted_rung if accepted_rung is not None else len(
        rung_sizes)
    terminal_intervals = rung_snapshots[terminal_rung]
    n_term = rung_sizes[terminal_rung - 1]

    exceed_below = exceed_above = 0
    skews = []
    for fb in fb_sizes:
        iv = terminal_intervals[str(fb)]
        if iv["min_per_seed_ratio"] < iv["interval_low"]:
            exceed_below += 1
        if iv["max_per_seed_ratio"] > iv["interval_high"]:
            exceed_above += 1
        sk = _skewness(draws[fb][:n_term])
        skews.append(sk)

    valid_skews = [s for s in skews if s is not None]
    return {
        "accepted_rung": accepted_rung,
        "terminal_rung": terminal_rung,
        "accepted_by_rung8": accepted_rung is not None,
        "exceed_below_at_terminal": exceed_below,
        "exceed_above_at_terminal": exceed_above,
        "exceed_total_at_terminal": exceed_below + exceed_above,
        "side_asymmetry_at_terminal": exceed_above - exceed_below,
        "skewness_per_row_at_terminal": skews,
        "skewness_mean_at_terminal": (
            float(np.mean(valid_skews)) if valid_skews else None),
        "skewness_median_at_terminal": (
            float(np.median(valid_skews)) if valid_skews else None),
    }


def r4_run(fb_sizes: list, loc_scale: dict, z: float, stability_pct: float,
          master_seed: int, n_replications: int, distribution: str,
          rung_sizes=R4_RUNG_SIZES) -> dict:
    master = np.random.SeedSequence(master_seed)
    rep_seeds = master.spawn(n_replications)
    records = []
    for rep_idx, rep_seed in enumerate(rep_seeds):
        rec = draw_null_object_replication(
            fb_sizes, loc_scale, z, stability_pct, rep_seed, distribution,
            rung_sizes)
        rec["replication"] = rep_idx
        records.append(rec)

    accepted = [r for r in records if r["accepted_by_rung8"]]
    accept_fraction = len(accepted) / len(records) if records else None
    first_accept_hist = {}
    for r in records:
        key = str(r["accepted_rung"]) if r["accepted_rung"] is not None \
            else "not_accepted_by_rung8"
        first_accept_hist[key] = first_accept_hist.get(key, 0) + 1

    def _dist(field):
        vals = [r[field] for r in records if r[field] is not None]
        if not vals:
            return {"n": 0}
        arr = np.asarray(vals, dtype=float)
        s = sorted(vals)
        n = len(s)
        return {"n": n, "mean": float(arr.mean()), "sd": float(arr.std(ddof=1))
                if n > 1 else 0.0, "min": s[0],
                "q25": s[max(0, int(0.25 * (n - 1)))],
                "median": s[n // 2] if n % 2 else (s[n // 2 - 1] + s[n // 2]) / 2,
                "q75": s[min(n - 1, int(0.75 * (n - 1)))], "max": s[-1]}

    return {
        "distribution": distribution,
        "master_seed": master_seed,
        "seed_derivation": (
            "numpy.random.SeedSequence(master_seed).spawn(n_replications) "
            "-> one SeedSequence per replication; each replication further "
            "spawns 13 sub-sequences (one per density row) via "
            "rep_seed.spawn(13). Fully reproducible from master_seed alone."),
        "n_replications_declared": n_replications,
        "n_replications_completed": len(records),
        "rung_sizes": list(rung_sizes),
        "accept_by_rung8_count": len(accepted),
        "accept_by_rung8_fraction": accept_fraction,
        "first_accept_rung_histogram": first_accept_hist,
        "exceed_total_at_terminal_distribution": _dist("exceed_total_at_terminal"),
        "side_asymmetry_at_terminal_distribution": _dist("side_asymmetry_at_terminal"),
        "skewness_mean_at_terminal_distribution": _dist("skewness_mean_at_terminal"),
        "records": records,
        "diagnostic_note": (
            "Skewness and terminal-rung exceedance/side-asymmetry are "
            "DIAGNOSTIC ONLY and gate nothing here, exactly as D2 gates "
            "nothing in the real E9 design. No new pass/fail threshold is "
            "invented on top of them; the raw numbers and their "
            "distribution across replications are reported."),
    }


# --------------------------------------------------------------------------
# emission
# --------------------------------------------------------------------------


def _emit(run_suffix: str, metrics: dict, raw: dict, stdout: str,
          command: str, started: float, finished: float, status: str,
          valid: bool, invalid_reason=None) -> str:
    from harness.runner import RunResult, write_run
    return write_run(EXPERIMENT_ID, RUN_AREA, RunResult(
        run_suffix=run_suffix,
        curve_id="n/a (statistical reanalysis of an already-collected "
                 "reference-sampling distribution, plus a synthetic "
                 "null-object simulation; no curve is enumerated)",
        seed=R4_MASTER_SEED, parameters=raw.get("parameters", {}),
        metrics=metrics, certificate={"kind": "none"},
        valid=valid, invalid_reason=invalid_reason,
        stdout=stdout, stderr="", raw=raw),
        status=status, command=command, started=started, finished=finished)


def _dump(run_id: str, name: str, obj) -> None:
    path = os.path.join(_run_dir(run_id), name)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(obj, f, indent=2, sort_keys=True, default=str)


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(
        description="R3/R4 reanalysis and control (EXP-INSTR-36c8cf, "
                    "TASK-20260811-bc336d)")
    ap.add_argument("--suffix", required=True)
    ap.add_argument("--replications", type=int, default=R4_REPLICATIONS)
    ap.add_argument("--gaussian-replications", type=int,
                    default=R4_GAUSSIAN_REPLICATIONS)
    ap.add_argument("--skip-gaussian-arm", action="store_true",
                    help="skip the OPTIONAL matched-variance Gaussian "
                         "calibration arm; R3 and R4 always run")
    ap.add_argument("--max-seconds", type=int, default=1800)
    args = ap.parse_args(argv)

    started = time.time()
    deadline = started + args.max_seconds
    log: list = []

    def say(msg: str) -> None:
        log.append(msg)
        print(msg, flush=True)

    say(f"{CONTROL_ID} -- {EXPERIMENT_ID} ({TASK_ID})")
    say("R3 (jackknife exceedance reanalysis + stability correlation) and "
        "R4 (Student-t(df=5) null-object control), per RT-20260811-35ab34 "
        "R3/R4 and DEC-20260811-a4c7ec.next_actions.")
    say("")

    say("0. FROZEN INPUTS (read at run time, nothing transcribed)")
    frozen = load_frozen_inputs()
    fb_sizes = frozen["fb_sizes"]
    z = frozen["z"]
    stability_pct = frozen["stability_relative_half_width_pct"]
    say(f"   z_from_coverage(519, 520) = {z}")
    say(f"   stability_relative_half_width_pct = {stability_pct}")
    say(f"   fb_sizes ({len(fb_sizes)} rows) = {fb_sizes}")
    say("")

    say("1. LOADING FAMILY 4001 RUNGS 1-3 FROM THE COMMITTED REFERENCE RUN")
    loaded = load_rung3_family(fb_sizes)
    say(f"   source: {REFERENCE_SAMPLING_JSON}")
    say(f"   sha256: {frozen['source_sha256'][REFERENCE_SAMPLING_JSON]}")
    say("")

    if time.time() > deadline:
        say("WALL-CLOCK BUDGET EXHAUSTED BEFORE R3 STARTED.")
        return _finish_timeout(args, started, log, frozen, {}, {}, {}, {})

    say("2. R3a: LEAVE-ONE-OUT (JACKKNIFE) EXCEEDANCE-RATE REANALYSIS")
    r3a = r3a_analysis(loaded["rung3"], fb_sizes, z)
    say(f"   trials: {r3a['jackknife_total_trials']} (13 rows x 48 seeds)")
    say(f"   jackknife exceedances: below={r3a['jackknife_total_exceed_below']} "
        f"above={r3a['jackknife_total_exceed_above']} "
        f"total={r3a['jackknife_total_exceed']}")
    say(f"   in-sample exceedances: below={r3a['in_sample_total_exceed_below']} "
        f"above={r3a['in_sample_total_exceed_above']} "
        f"total={r3a['in_sample_total_exceed']}")
    say(f"   Gaussian-rule expected count: "
        f"{r3a['gaussian_rule_expected_count']:.4f}")
    say(f"   jackknife exceeds in-sample: {r3a['jackknife_exceeds_in_sample']}")
    say("")

    say("3. R3b: STABILITY-FAILURE CORRELATION (2x2 TABLE, EXACT FISHER TEST)")
    r3b = r3b_analysis(loaded["rung2"], loaded["rung3"], fb_sizes,
                       stability_pct, r3a)
    say(f"   rows failing stability (rung2->rung3): "
        f"{r3b['rows_failing_stability']}")
    ct = r3b["contingency_table"]
    say(f"   table: {ct}")
    say(f"   Fisher's exact two-sided p = "
        f"{r3b['fisher_exact']['p_value_two_sided']:.6f}")
    cross_check = cross_check_against_committed_stability(
        r3b["stability_check_recomputed"])
    say(f"   cross-check vs committed sr3v3-interval-stability.json: "
        f"met_at_every_row agree={cross_check['agree_on_met_at_every_row']} "
        f"rows_failing agree={cross_check['agree_on_rows_failing']}")
    say("")

    if time.time() > deadline:
        say("WALL-CLOCK BUDGET EXHAUSTED BEFORE R4 STARTED.")
        return _finish_timeout(args, started, log, frozen, r3a, r3b,
                               cross_check, {})

    say(f"4. R4: STUDENT-t(df=5) NULL-OBJECT CONTROL, "
        f"{args.replications} REPLICATIONS")
    say(f"   master_seed={R4_MASTER_SEED} (declared, arbitrary, fixed)")
    r4 = r4_run(fb_sizes, loaded["rung3"], z, stability_pct, R4_MASTER_SEED,
               args.replications, "student_t5")
    say(f"   accept-by-rung-8 fraction: {r4['accept_by_rung8_fraction']:.4f} "
        f"({r4['accept_by_rung8_count']}/{r4['n_replications_completed']})")
    say(f"   first-accept-rung histogram: {r4['first_accept_rung_histogram']}")
    say("")

    r4_gaussian = None
    if not args.skip_gaussian_arm and time.time() < deadline:
        say(f"5. OPTIONAL: MATCHED-VARIANCE GAUSSIAN CALIBRATION ARM, "
            f"{args.gaussian_replications} REPLICATIONS")
        say(f"   master_seed={R4_GAUSSIAN_MASTER_SEED} (declared, arbitrary, "
            f"fixed, distinct from the Student-t arm's seed)")
        say("   SUPPLEMENTARY CONTEXT ONLY -- not part of R3/R4's own "
            "required text.")
        r4_gaussian = r4_run(fb_sizes, loaded["rung3"], z, stability_pct,
                             R4_GAUSSIAN_MASTER_SEED,
                             args.gaussian_replications, "gaussian")
        say(f"   accept-by-rung-8 fraction: "
            f"{r4_gaussian['accept_by_rung8_fraction']:.4f} "
            f"({r4_gaussian['accept_by_rung8_count']}/"
            f"{r4_gaussian['n_replications_completed']})")
        say("")
    elif args.skip_gaussian_arm:
        say("5. OPTIONAL GAUSSIAN CALIBRATION ARM SKIPPED (--skip-gaussian-arm)")
        say("")

    finished = time.time()
    import resource as _res
    ru = _res.getrusage(_res.RUSAGE_SELF)
    cpu = round(ru.ru_utime + ru.ru_stime, 3)
    wall = round(finished - started, 3)
    say(f"DONE. wall_seconds={wall} cpu_seconds={cpu}")

    metrics = {
        "control": CONTROL_ID,
        "task_id": TASK_ID,
        "r3a_jackknife_total_exceed": r3a["jackknife_total_exceed"],
        "r3a_in_sample_total_exceed": r3a["in_sample_total_exceed"],
        "r3a_gaussian_rule_expected_count": r3a["gaussian_rule_expected_count"],
        "r3a_jackknife_exceeds_in_sample": r3a["jackknife_exceeds_in_sample"],
        "r3b_fisher_exact_p_two_sided":
            r3b["fisher_exact"]["p_value_two_sided"],
        "r3b_contingency_table": r3b["contingency_table"],
        "r4_student_t5_accept_by_rung8_fraction":
            r4["accept_by_rung8_fraction"],
        "r4_student_t5_first_accept_rung_histogram":
            r4["first_accept_rung_histogram"],
        "r4_gaussian_accept_by_rung8_fraction": (
            r4_gaussian["accept_by_rung8_fraction"] if r4_gaussian else None),
        "wall_seconds": wall,
        "cpu_seconds": cpu,
        "peak_rss_bytes": ru.ru_maxrss * 1024,
        "certificate_note": CERTIFICATE_NOTE,
        "scope": SCOPE_NOTE,
    }
    raw = {
        "control": CONTROL_ID,
        "task_id": TASK_ID,
        "parameters": {
            "reference_run": REFERENCE_RUN_ID,
            "reference_sampling_json": REFERENCE_SAMPLING_JSON,
            "family": FAMILY_PRIME,
            "fb_sizes": fb_sizes,
            "z_computed": z,
            "z_computed_from": "z_from_coverage(519, 520)",
            "stability_relative_half_width_pct": stability_pct,
            "r4_rung_sizes": R4_RUNG_SIZES,
            "r4_student_t5_master_seed": R4_MASTER_SEED,
            "r4_gaussian_master_seed": R4_GAUSSIAN_MASTER_SEED,
            "r4_replications_declared": args.replications,
            "r4_gaussian_replications_declared": (
                None if args.skip_gaussian_arm else args.gaussian_replications),
            "max_seconds": args.max_seconds,
        },
        "frozen_inputs": {k: v for k, v in frozen.items()
                          if k != "amendment_frozen_parameters"},
        "amendment_frozen_parameters": frozen["amendment_frozen_parameters"],
        "r3a": r3a,
        "r3b": r3b,
        "r3b_cross_check_vs_committed_stability_report": cross_check,
        "r4_student_t5": r4,
        "r4_gaussian_calibration_optional": r4_gaussian,
        "scope": SCOPE_NOTE,
        "certificate_note": CERTIFICATE_NOTE,
        "authority_note": (
            "This module records observations only. It does not conclude "
            "that HEUR-INSTR-4 is supported or refuted, does not approve, "
            "reject, withdraw or amend EXP-INSTR-36c8cf amendment v2, and "
            "does not move H-INSTR-444c7b or any other hypothesis status. "
            "That judgement belongs to the Coordinator, after independent "
            "review, in a decision record."),
    }
    cmd = (f"python3 -m harness.exp_instr_36c8cf.ctrl_r3r4 "
           f"--suffix {args.suffix} --replications {args.replications} "
           f"--gaussian-replications {args.gaussian_replications} "
           f"--max-seconds {args.max_seconds}"
           + (" --skip-gaussian-arm" if args.skip_gaussian_arm else ""))
    run_id = _emit(args.suffix, metrics, raw, "\n".join(log) + "\n", cmd,
                   started, finished, "completed", valid=True)
    print(f"wrote {run_id}", flush=True)

    _dump(run_id, "jackknife-exceedance.json", r3a)
    _dump(run_id, "stability-correlation.json", r3b)
    _dump(run_id, "stability-correlation-cross-check.json", cross_check)
    _dump(run_id, "r4-student-t5-nullobject.json", r4)
    if r4_gaussian is not None:
        _dump(run_id, "r4-gaussian-calibration-optional.json", r4_gaussian)
    _dump(run_id, "frozen-inputs.json",
         {k: v for k, v in frozen.items()})
    return 0


def _finish_timeout(args, started, log, frozen, r3a, r3b, cross_check,
                    r4) -> int:
    """Budget exhaustion path: record as infrastructure failure
    (`resource_exhaustion`/`failed_infrastructure`), NEVER as a negative
    result, per AGENTS.md rule 5 and this campaign's stopping-rule SR6.
    """
    finished = time.time()
    say = log.append
    say(f"ABORTED: wall-clock budget of {args.max_seconds}s exhausted.")
    metrics = {"control": CONTROL_ID, "task_id": TASK_ID,
              "aborted": True,
              "wall_seconds": round(finished - started, 3)}
    raw = {"control": CONTROL_ID, "task_id": TASK_ID, "aborted": True,
          "frozen_inputs": frozen, "r3a": r3a, "r3b": r3b,
          "cross_check": cross_check, "r4": r4}
    cmd = (f"python3 -m harness.exp_instr_36c8cf.ctrl_r3r4 "
           f"--suffix {args.suffix} --max-seconds {args.max_seconds}")
    run_id = _emit(args.suffix, metrics, raw, "\n".join(log) + "\n", cmd,
                   started, finished, "failed_infrastructure", valid=False,
                   invalid_reason=(
                       f"wall-clock budget of {args.max_seconds}s exhausted; "
                       f"partial artifacts retained. Infrastructure "
                       f"failure, NEVER negative evidence (AGENTS.md rule 5)."
                   ))
    print(f"wrote {run_id} (ABORTED)", flush=True)
    return 1


if __name__ == "__main__":                                # pragma: no cover
    raise SystemExit(main())

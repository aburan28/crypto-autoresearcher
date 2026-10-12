"""EXP-INSTR-36c8cf: Gaussian-arm null-object cross-check of amendment v3
change E11's D3/D4/D5 diagnostic (TASK-20260811-c5a4d5).

WHAT THIS ANSWERS. `ctrl_r3r4_d5check.py` (TASK-20260811-409237,
RUN-INSTR-d5check-b8faf7) checked whether E11's D3/D4/D5 diagnostic catches
the Student-t(df=5) heavy-tail alternative within T2's own truncated
stopping window (headline: 94/94, 100%), but never checked the matched-shape
GAUSSIAN arm -- the null-object control `docs/inventor-protocol.md` section 3
requires before ANY reported catch-rate is read as evidence rather than an
artifact (a 100%-vs-0% separation on the exceedance-count diagnnostic earlier
in this same batch turned out to be 100%-vs-12.6% once the Gaussian arm was
actually checked). This Coordinator performed a preliminary, OFF-LEDGER, ad
hoc check of the Gaussian arm; both the Validator and Red Team independently
reproduced it from scratch and converged on 21/485 (4.330%) of the Gaussian
arm's own accepted replications also firing D5 (Variant 1, as-implemented
D4), and the Red Team additionally found that recalibrating D4 to the actual
two-sided-selected D3 statistic (not just the sample maximum) drops that
figure to 7/485 (1.443%) while leaving the Student-t headline unchanged at
94/94 (Variant 2, corrected D4). Neither figure previously existed as a
citable, committed record. This module creates that record.

WHAT THIS MODULE DOES NOT DO. It does not edit `ctrl_r3r4_d5check.py`,
`ctrl_r3r4.py`, `sr3v3.py`, or anything under `experiments/`. It does not
touch RUN-INSTR-r3r4-nullobj-d3efd7 or RUN-INSTR-d5check-b8faf7 (both
read-only inputs). It does not approve, reject or amend
`experiments/EXP-INSTR-36c8cf/amendments/v3.yaml`, and does not draft a v4.
It does not move any hypothesis status. `claim_tier: toy`, `sota_delta: 0` on
every axis. It records observations only -- whether E11's own repair is a
genuinely well-calibrated discriminator is the Coordinator's judgement, after
independent review, in a decision record.

KNOWN HAZARD (handoff TASK-20260811-c5a4d5, hit independently by both the
Validator and the Red Team in their own from-scratch reproductions):
`numpy.random.SeedSequence.spawn()` is STATEFUL -- calling `.spawn(k)` on the
SAME SeedSequence object a second time returns DIFFERENT children than the
first call, not the same ones. Both reviewers' first-draft scripts got a
WRONG answer (20/485 instead of 21/485) by sharing a spawned-from
SeedSequence object across a faithfulness spot-check pass and the full pass.
This module follows exactly the pattern `ctrl_r3r4_d5check.py`'s own
`faithfulness_gate()` and `run_full_analysis()` already use correctly: EVERY
function that needs the replication-level seed stream instantiates its OWN
FRESH `numpy.random.SeedSequence(master_seed)` and calls `.spawn()` on it
EXACTLY ONCE. No spawned-from SeedSequence object is ever shared across two
different check passes anywhere in this module.
"""
from __future__ import annotations

import argparse
import json
import math
import os
import time

import numpy as np

from harness.exp_instr_36c8cf import ctrl_r3r4, ctrl_r3r4_d5check, sr3v3
from harness.exp_instr_36c8cf.refvalues import sha256_of

EXPERIMENT_ID = "EXP-INSTR-36c8cf"
RUN_AREA = "INSTR"
CONTROL_ID = "CTRL-D5CHECK-GAUSSIAN-NULLOBJECT"
TASK_ID = "TASK-20260811-c5a4d5"

REFERENCE_RUN_ID = "RUN-INSTR-r3r4-nullobj-d3efd7"
GAUSSIAN_JSON = (f"experiments/{EXPERIMENT_ID}/runs/{REFERENCE_RUN_ID}/"
                 "r4-gaussian-calibration-optional.json")
STUDENT_T_JSON = ctrl_r3r4_d5check.R4_JSON       # read-only, cross-check only

D4_MAXONLY_RUN_ID = "RUN-INSTR-d5check-b8faf7"
D4_MAXONLY_JSON = (f"experiments/{EXPERIMENT_ID}/runs/{D4_MAXONLY_RUN_ID}/"
                   "d4-calibration.json")

AMENDMENT_V3 = f"experiments/{EXPERIMENT_ID}/amendments/v3.yaml"
CTRL_R3R4_MODULE = "harness/exp_instr_36c8cf/ctrl_r3r4.py"
CTRL_R3R4_D5CHECK_MODULE = "harness/exp_instr_36c8cf/ctrl_r3r4_d5check.py"
SR3V3_MODULE = "harness/exp_instr_36c8cf/sr3v3.py"

D3_ROWS = ctrl_r3r4_d5check.D3_ROWS              # [18, 22], imported not retyped

# D4-EXTREME (Variant 2)'s own DECLARED, DISCLOSED master seed for the
# recalibrated Monte Carlo null. MUST be distinct from every seed already in
# use in this contract: R4_MASTER_SEED=314159265 (ctrl_r3r4.py, Student-t(5)
# arm), R4_GAUSSIAN_MASTER_SEED=271828182 (ctrl_r3r4.py, Gaussian arm),
# D4_MASTER_SEED=141421356 (ctrl_r3r4_d5check.py, max-only D4 calibration,
# first nine digits of sqrt(2)). This module's own new declared constant is
# the first nine digits of Euler's constant gamma = 0.5772156649...,
# 577215664: a recognisable fixed integer with no other role anywhere in
# this campaign, following the same naming convention the two prior modules
# already use for their own master seeds.
D4_EXTREME_MASTER_SEED = 577215664
D4_TRIALS_MIN = 20000

CERTIFICATE_NOTE = (
    "certificate.kind: none, EXPLICITLY. This is pure post-hoc statistics "
    "(D3 leave-one-out diagnostic recomputation, reused unmodified from "
    "ctrl_r3r4_d5check.py) and pure numpy simulation (an independent "
    "reimplementation of the Gaussian null-object draw, for the mandatory "
    "faithfulness gate; and a new D4 Monte Carlo null calibration for "
    "Variant 2) over already-committed synthetic null-object simulations. "
    "No discrete logarithm is computed and no factor-base relation is "
    "claimed anywhere in this module, so there is no solve or relation to "
    "certify (docs/claims-and-verification.md).")

SCOPE_NOTE = (
    "Tier TOY. A bounded reanalysis of two already-committed synthetic "
    "null-object simulations (RUN-INSTR-r3r4-nullobj-d3efd7's Gaussian and "
    "Student-t(5) arms) and one already-committed D4 calibration "
    "(RUN-INSTR-d5check-b8faf7's max-only p99 thresholds), computing "
    "amendment v3 change E11's own D3/D4/D5 diagnostic exactly as specified, "
    "truncated to the rung window T2's first-pass-wins rule would actually "
    "have measured before stopping, under two D4 calibration variants. No "
    "ECDLP attack, exponent or speedup claim of any kind. claim_tier toy, "
    "sota_delta 0 on every axis. This module does not approve, reject or "
    "amend EXP-INSTR-36c8cf amendment v3, and does not move any hypothesis "
    "status.")


def _repo() -> str:
    return os.path.dirname(os.path.dirname(os.path.dirname(
        os.path.abspath(__file__))))


def _run_dir(run_id: str) -> str:
    return os.path.join(_repo(), "experiments", EXPERIMENT_ID, "runs", run_id)


def _load_json(rel: str) -> dict:
    with open(os.path.join(_repo(), rel), encoding="utf-8") as fh:
        return json.load(fh)


# --------------------------------------------------------------------------
# frozen inputs, read at run time -- nothing transcribed (standing rule A4).
# Delegated to ctrl_r3r4_d5check's own load_frozen_inputs (imported, not
# retyped); this module adds its own two extra source pins.
# --------------------------------------------------------------------------


def load_frozen_inputs() -> dict:
    frozen = ctrl_r3r4_d5check.load_frozen_inputs()
    frozen = dict(frozen)
    frozen["source_sha256"] = dict(frozen["source_sha256"])
    frozen["source_sha256"][GAUSSIAN_JSON] = sha256_of(GAUSSIAN_JSON)
    frozen["source_sha256"][D4_MAXONLY_JSON] = sha256_of(D4_MAXONLY_JSON)
    return frozen


def _d4_by_n_int_keys(d4_json_by_n: dict) -> dict:
    """Committed D4 calibration JSON round-trips dict keys to strings; the
    analysis code (both ctrl_r3r4_d5check.analyse_replication and this
    module's own analyse_replication_gaussian) indexes d4_by_n[n] with an
    int (a rung's own seed count from R4_RUNG_SIZES). Converts back."""
    return {int(k): v for k, v in d4_json_by_n.items()}


# --------------------------------------------------------------------------
# MANDATORY FAITHFULNESS GATE -- independent reimplementation of the
# Gaussian draw generation, run FIRST, before any D3/D4/D5 code is trusted.
# Structured per the known-hazard warning above: this function instantiates
# its OWN fresh SeedSequence and spawns from it EXACTLY ONCE.
# --------------------------------------------------------------------------


def draw_replication_detailed_gaussian(fb_sizes: list, loc_scale: dict,
                                       z: float, stability_pct: float,
                                       rep_seed, rung_sizes: list) -> dict:
    """Independent reimplementation of ctrl_r3r4.draw_null_object_replication's
    "gaussian" branch accepted_rung/terminal_rung/exceed_total_at_terminal
    logic, for the faithfulness gate. Deliberately NOT calling ctrl_r3r4's
    own function -- the whole point of this gate is to catch a
    transcription/logic drift between an independent reimplementation and
    the committed record, which a direct call could not do. Mirrors
    ctrl_r3r4_d5check.draw_replication_detailed exactly, except the draw
    formula: rng.normal(loc=loc, scale=scale, size=n_max), per ctrl_r3r4.py's
    "gaussian" branch (no rescale needed -- a standard normal already has
    the row's own target variance directly, unlike the Student-t(df=5) arm's
    /sqrt(5/3) rescale)."""
    row_seeds = rep_seed.spawn(len(fb_sizes))
    draws = {}
    for fb, rseed in zip(fb_sizes, row_seeds):
        rng = np.random.default_rng(rseed)
        loc = loc_scale[str(fb)]["mean"]
        scale = loc_scale[str(fb)]["sd_sample_n_minus_1"]
        n_max = rung_sizes[-1]
        draws[fb] = rng.normal(loc=loc, scale=scale, size=n_max)

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
    exceed_below = exceed_above = 0
    for fb in fb_sizes:
        iv = terminal_intervals[str(fb)]
        if iv["min_per_seed_ratio"] < iv["interval_low"]:
            exceed_below += 1
        if iv["max_per_seed_ratio"] > iv["interval_high"]:
            exceed_above += 1

    return {"accepted_rung": accepted_rung, "terminal_rung": terminal_rung,
            "exceed_total_at_terminal": exceed_below + exceed_above}


def faithfulness_gate_gaussian(fb_sizes: list, loc_scale: dict, z: float,
                               stability_pct: float, committed_records: list,
                               check_indices: list) -> dict:
    """ONE fresh SeedSequence, spawned ONCE, for this entire gate pass."""
    master = np.random.SeedSequence(ctrl_r3r4.R4_GAUSSIAN_MASTER_SEED)
    rep_seeds = master.spawn(ctrl_r3r4.R4_GAUSSIAN_REPLICATIONS)
    per_index = []
    all_match = True
    for i in check_indices:
        got = draw_replication_detailed_gaussian(
            fb_sizes, loc_scale, z, stability_pct, rep_seeds[i],
            ctrl_r3r4.R4_RUNG_SIZES)
        want = committed_records[i]
        ok = (got["accepted_rung"] == want["accepted_rung"]
              and got["terminal_rung"] == want["terminal_rung"]
              and got["exceed_total_at_terminal"]
              == want["exceed_total_at_terminal"])
        all_match = all_match and ok
        per_index.append({
            "replication": i,
            "recomputed": got,
            "committed": {
                "accepted_rung": want["accepted_rung"],
                "terminal_rung": want["terminal_rung"],
                "exceed_total_at_terminal": want["exceed_total_at_terminal"],
            },
            "match": ok,
        })
    return {"all_match": all_match, "n_checked": len(check_indices),
            "checked_indices": check_indices,
            "master_seed": ctrl_r3r4.R4_GAUSSIAN_MASTER_SEED,
            "per_index": per_index}


# --------------------------------------------------------------------------
# D3/D5 per-replication analysis for the GAUSSIAN arm, restricted to fb=18
# and fb=22, restricted to the truncated rung window (the Gaussian arm's own
# committed accepted_rung). Reuses ctrl_r3r4_d5check.d3_loo and
# ctrl_r3r4_d5check.window_for_replication UNMODIFIED; only the draw formula
# (Gaussian, not Student-t) differs from ctrl_r3r4_d5check.analyse_replication.
# --------------------------------------------------------------------------


def analyse_replication_gaussian(rep_seed, committed_rec: dict, fb_sizes: list,
                                 loc_scale: dict, z: float, d4_by_n: dict,
                                 rung_sizes: list) -> dict:
    accepted_rung = committed_rec["accepted_rung"]
    terminal_rung = committed_rec["terminal_rung"]
    window = ctrl_r3r4_d5check.window_for_replication(accepted_rung)

    row_seeds = rep_seed.spawn(len(fb_sizes))
    per_row = {}
    for fb in D3_ROWS:
        ridx = fb_sizes.index(fb)
        rseed = row_seeds[ridx]
        rng = np.random.default_rng(rseed)
        loc = loc_scale[str(fb)]["mean"]
        scale = loc_scale[str(fb)]["sd_sample_n_minus_1"]
        n_max = rung_sizes[-1]
        draws = rng.normal(loc=loc, scale=scale, size=n_max)

        rung_records = {}
        exceed_count = 0
        d5_fire_rung = None
        for rung in window:
            n = rung_sizes[rung - 1]
            ratios = [float(v) for v in draws[:n]]
            d3 = ctrl_r3r4_d5check.d3_loo(ratios, z)
            thr = d4_by_n[n]["p99"]
            # Same "two-sided reading" judgment call as
            # ctrl_r3r4_d5check.analyse_replication: abs(D3 loo_z) against
            # D4's own p99 threshold. For Variant 1 that threshold is
            # max-only-calibrated (one-sided by construction, symmetry
            # argument as documented there); for Variant 2 the threshold
            # itself is calibrated on the two-sided extreme-point statistic,
            # so the abs() comparison is exact rather than a symmetry
            # argument -- see compute_d4_calibration_extreme's own docstring.
            exceeds = abs(d3["loo_z"]) > thr
            if exceeds:
                exceed_count += 1
                if exceed_count == 2 and d5_fire_rung is None:
                    d5_fire_rung = rung
            rung_records[rung] = {
                "n": n, "loo_z": d3["loo_z"], "excluded_point":
                    d3["excluded_point"], "row_in_sample_mean":
                    d3["row_in_sample_mean"], "mean_loo": d3["mean_loo"],
                "sd_loo": d3["sd_loo"], "d4_p99_threshold": thr,
                "exceeds_d4_p99_abs": exceeds,
            }
        d5_fired = exceed_count >= 2
        relative = None
        if d5_fired and accepted_rung is not None:
            relative = "at" if d5_fire_rung == accepted_rung else "before"
        per_row[str(fb)] = {
            "rungs": rung_records, "exceed_count_in_window": exceed_count,
            "d5_fired": d5_fired, "d5_fire_rung": d5_fire_rung,
            "d5_fire_rung_relative_to_accepted_rung": relative,
        }

    d5_fired_replication = any(per_row[str(fb)]["d5_fired"] for fb in D3_ROWS)
    return {
        "accepted_rung": accepted_rung, "terminal_rung": terminal_rung,
        "window_rungs": window, "window_size": len(window),
        "per_row": per_row, "d5_fired": d5_fired_replication,
    }


def run_full_analysis_gaussian(fb_sizes: list, loc_scale: dict, z: float,
                               committed_records: list, d4_by_n: dict,
                               rung_sizes: list) -> list:
    """ONE fresh SeedSequence, spawned ONCE, for this entire analysis pass."""
    master = np.random.SeedSequence(ctrl_r3r4.R4_GAUSSIAN_MASTER_SEED)
    rep_seeds = master.spawn(len(committed_records))
    out = []
    for i, rep_seed in enumerate(rep_seeds):
        rec = analyse_replication_gaussian(rep_seed, committed_records[i],
                                           fb_sizes, loc_scale, z, d4_by_n,
                                           rung_sizes)
        rec["replication"] = i
        out.append(rec)
    return out


def summarise_variant(results: list, label: str) -> dict:
    accepted = [r for r in results if r["accepted_rung"] is not None]
    accepted_fired = [r for r in accepted if r["d5_fired"]]
    k = len(accepted_fired)
    n = len(accepted)
    frac = k / n if n else None
    ci = wilson_ci(k, n) if n else None
    return {
        "label": label,
        "n_replications": len(results),
        "n_accepted_rung_set": n,
        "headline": {
            "description": (
                f"Of the {n} replications with accepted_rung set, the "
                f"count/fraction where D5 (per amendment v3 change E11, at "
                f"fb=18 or fb=22, recurrence >= 2 rungs) fires WITHIN the "
                f"truncated rung window, under {label}."),
            "d5_fired_count": k,
            "d5_fired_fraction": frac,
            "n_accepted": n,
            "wilson_95_ci": ci,
        },
    }


# --------------------------------------------------------------------------
# Wilson 95% confidence interval for a binomial proportion.
# --------------------------------------------------------------------------


def wilson_ci(k: int, n: int, z: float = 1.9599639845400545) -> dict:
    """z is Phi^{-1}(0.975), computed at import time from
    statistics.NormalDist (standing rule A4: never transcribed at arbitrary
    precision as a bare literal without also stating how it was obtained).
    The default argument value above is that same computed constant, stated
    as a default so the function is usable standalone; main() always calls
    this with the freshly-computed value from `_z975()`, never relying on
    the default silently.
    """
    if n == 0:
        return {"lower": None, "upper": None, "point": None, "n": 0, "k": 0}
    p = k / n
    denom = 1 + z * z / n
    centre = p + z * z / (2 * n)
    half = z * math.sqrt((p * (1 - p) / n) + (z * z / (4 * n * n)))
    lower = (centre - half) / denom
    upper = (centre + half) / denom
    return {"lower": lower, "upper": upper, "point": p, "n": n, "k": k,
            "z_used": z}


def _z975() -> float:
    from statistics import NormalDist
    return NormalDist().inv_cdf(0.975)


# --------------------------------------------------------------------------
# D4-EXTREME (Variant 2): recalibrated Monte Carlo null, tracking the LOO
# z-score of WHICHEVER point (max or min) is most extreme by absolute
# deviation from the mean -- the exact same selection rule D3 itself uses --
# rather than the sample maximum only (which Variant 1's already-committed
# D4 calibration tracks). Reports the distribution of abs(loo_z) of that
# extreme point, since D3/D5's own comparison (both here and in
# ctrl_r3r4_d5check.analyse_replication) is abs(D3 loo_z) > threshold.
# --------------------------------------------------------------------------


def compute_d4_calibration_extreme(ns: list, master_seed: int,
                                   trials: int) -> dict:
    """For each n: draw n i.i.d. N(0,1) values, find the point most extreme
    by absolute deviation from the sample mean (max OR min, whichever is
    farther -- ties broken toward the first-encountered maximal deviation by
    np.argmax's own tie-break, the same "first occurrence wins" rule
    ctrl_r3r4_d5check.d3_loo documents for its own tie-break via Python's
    max()), recompute mean/sd of the OTHER n-1 points (leave-one-out), score
    the excluded point against that LOO mean/sd, and report the resulting
    ABSOLUTE VALUE's median/90th/99th percentile/max -- because D3/D5's own
    comparison is abs(loo_z) > threshold, not the signed value. `trials`
    independent sub-streams, one per n, spawned once from `master_seed`
    (same declared-choice convention ctrl_r3r4_d5check.compute_d4_calibration
    itself uses: independently spawned sub-streams, not one stream reused
    sequentially)."""
    master = np.random.SeedSequence(master_seed)
    sub_seeds = master.spawn(len(ns))
    out = {}
    for n, sseed in zip(ns, sub_seeds):
        rng = np.random.default_rng(sseed)
        X = rng.standard_normal(size=(trials, n))
        mean_all = X.mean(axis=1, keepdims=True)
        devs = np.abs(X - mean_all)
        extreme_idx = np.argmax(devs, axis=1)
        rows = np.arange(trials)
        extreme_val = X[rows, extreme_idx]
        sum_all = X.sum(axis=1)
        sumsq_all = (X ** 2).sum(axis=1)
        sum_rest = sum_all - extreme_val
        sumsq_rest = sumsq_all - extreme_val ** 2
        m = n - 1
        mean_rest = sum_rest / m
        var_rest = (sumsq_rest - (sum_rest ** 2) / m) / (m - 1)
        sd_rest = np.sqrt(var_rest)
        loo_z = (extreme_val - mean_rest) / sd_rest
        abs_loo_z = np.abs(loo_z)
        out[n] = {
            "n": n,
            "trials": trials,
            "median": float(np.median(abs_loo_z)),
            "p90": float(np.percentile(abs_loo_z, 90)),
            "p99": float(np.percentile(abs_loo_z, 99)),
            "max": float(abs_loo_z.max()),
            "statistic": "abs(LOO z-score) of whichever point (max or min) "
                         "is most extreme by absolute deviation from the "
                         "sample mean -- the same selection rule D3 itself "
                         "uses -- NOT the sample maximum only.",
        }
    return {"master_seed": master_seed,
            "seed_derivation": (
                "numpy.random.SeedSequence(master_seed).spawn(len(ns)) -> "
                "one independent sub-stream per distinct n, in the order ns "
                "is given (rungs 4 through 8's own seed counts, ascending)."),
            "statistic_note": (
                "Tracks abs(LOO z) of the max-or-min extreme point (D3's own "
                "selection rule), not the sample maximum's signed LOO z as "
                "ctrl_r3r4_d5check.compute_d4_calibration (Variant 1's "
                "already-committed calibration) does. Compared against "
                "abs(D3 loo_z) in analyse_replication_gaussian and "
                "ctrl_r3r4_d5check.analyse_replication exactly as Variant "
                "1's threshold is."),
            "by_n": out}


# --------------------------------------------------------------------------
# emission
# --------------------------------------------------------------------------


def _emit(run_suffix: str, metrics: dict, raw: dict, stdout: str,
          command: str, started: float, finished: float, status: str,
          valid: bool, invalid_reason=None) -> str:
    from harness.runner import RunResult, write_run
    return write_run(EXPERIMENT_ID, RUN_AREA, RunResult(
        run_suffix=run_suffix,
        curve_id="n/a (post-hoc statistics and Monte Carlo calibration over "
                 "already-committed synthetic null-object simulations; no "
                 "curve is enumerated)",
        seed=ctrl_r3r4.R4_GAUSSIAN_MASTER_SEED,
        parameters=raw.get("parameters", {}),
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
        description="Gaussian-arm null-object cross-check of D3/D4/D5 "
                    "(EXP-INSTR-36c8cf, TASK-20260811-c5a4d5)")
    ap.add_argument("--suffix", required=True)
    ap.add_argument("--faithfulness-check-count", type=int, default=25,
                    help=">= 25, spread across the 0..499 replication range")
    ap.add_argument("--d4-extreme-trials", type=int, default=D4_TRIALS_MIN,
                    help=">= 20000, trials per n for Variant 2's D4-extreme "
                         "calibration")
    ap.add_argument("--max-seconds", type=int, default=1800)
    args = ap.parse_args(argv)

    if args.faithfulness_check_count < 25:
        raise SystemExit(
            "--faithfulness-check-count must be >= 25 (handoff "
            "TASK-20260811-c5a4d5's mandatory faithfulness gate)")
    if args.d4_extreme_trials < D4_TRIALS_MIN:
        raise SystemExit(
            f"--d4-extreme-trials must be >= {D4_TRIALS_MIN} (handoff "
            f"TASK-20260811-c5a4d5's Variant 2 minimum)")

    started = time.time()
    deadline = started + args.max_seconds
    log: list = []

    def say(msg: str) -> None:
        log.append(msg)
        print(msg, flush=True)

    say(f"{CONTROL_ID} -- {EXPERIMENT_ID} ({TASK_ID})")
    say("Gaussian-arm null-object cross-check of amendment v3 change E11's "
        "D3/D4/D5 diagnostic: Variant 1 (as-implemented, max-only D4, "
        "reused from RUN-INSTR-d5check-b8faf7) and Variant 2 (corrected D4, "
        "recalibrated to D3's own two-sided extreme-point statistic).")
    say("")

    say("0. FROZEN INPUTS (read at run time, nothing transcribed)")
    frozen = load_frozen_inputs()
    fb_sizes = frozen["fb_sizes"]
    z = frozen["z"]
    stability_pct = frozen["stability_relative_half_width_pct"]
    loc_scale = frozen["loc_scale_rung3"]
    say(f"   z_from_coverage(519, 520) = {z}")
    say(f"   fb_sizes ({len(fb_sizes)} rows) = {fb_sizes}")
    say(f"   D3/D4/D5 scoped rows = {D3_ROWS}")
    say(f"   R4_GAUSSIAN_MASTER_SEED (imported, not retyped) = "
        f"{ctrl_r3r4.R4_GAUSSIAN_MASTER_SEED}")
    say(f"   R4_MASTER_SEED (Student-t arm, imported, not retyped) = "
        f"{ctrl_r3r4.R4_MASTER_SEED}")
    say(f"   R4_RUNG_SIZES (imported, not retyped) = {ctrl_r3r4.R4_RUNG_SIZES}")
    say(f"   D4_EXTREME_MASTER_SEED (this module's own, declared) = "
        f"{D4_EXTREME_MASTER_SEED}")
    say("")

    say(f"1. LOADING THE ALREADY-COMMITTED GAUSSIAN-ARM RECORD ({GAUSSIAN_JSON})")
    gaussian_committed = _load_json(GAUSSIAN_JSON)
    gaussian_records = gaussian_committed["records"]
    say(f"   sha256: {frozen['source_sha256'][GAUSSIAN_JSON]}")
    say(f"   n_replications_completed (committed) = "
        f"{gaussian_committed['n_replications_completed']}")
    say(f"   accept_by_rung8_count (committed) = "
        f"{gaussian_committed['accept_by_rung8_count']}")
    say("")

    say(f"2. LOADING THE ALREADY-COMMITTED MAX-ONLY D4 CALIBRATION "
        f"({D4_MAXONLY_JSON})")
    d4_maxonly_committed = _load_json(D4_MAXONLY_JSON)
    d4_maxonly_by_n = _d4_by_n_int_keys(d4_maxonly_committed["by_n"])
    say(f"   sha256: {frozen['source_sha256'][D4_MAXONLY_JSON]}")
    say(f"   master_seed (committed) = {d4_maxonly_committed['master_seed']}")
    for n in sorted(d4_maxonly_by_n):
        say(f"   n={n}: p99={d4_maxonly_by_n[n]['p99']:.4f}")
    say("")

    if time.time() > deadline:
        return _abort(args, started, log, "before faithfulness gate")

    say("3. MANDATORY FAITHFULNESS GATE -- INDEPENDENT REIMPLEMENTATION OF "
        "THE GAUSSIAN DRAW, RUN FIRST")
    check_indices = ctrl_r3r4_d5check.faithfulness_check_indices(
        len(gaussian_records), args.faithfulness_check_count)
    say(f"   checking {len(check_indices)} replication indices, spread "
        f"across 0..{len(gaussian_records) - 1}: {check_indices}")
    gate = faithfulness_gate_gaussian(fb_sizes, loc_scale, z, stability_pct,
                                      gaussian_records, check_indices)
    say(f"   all_match = {gate['all_match']}")
    if not gate["all_match"]:
        mismatches = [p for p in gate["per_index"] if not p["match"]]
        say(f"   FAITHFULNESS GATE FAILED at {len(mismatches)} of "
            f"{gate['n_checked']} checked indices. STOPPING. Not proceeding "
            f"to D3/D4/D5 -- a diagnostic computed on non-reproduced draws "
            f"is worthless.")
        for m in mismatches:
            say(f"     replication {m['replication']}: recomputed="
                f"{m['recomputed']} committed={m['committed']}")
        return _finish_gate_failure(args, started, log, frozen, gate)
    say("   PASS: every checked replication's recomputed accepted_rung, "
        "terminal_rung and exceed_total_at_terminal matches the committed "
        "Gaussian-arm record exactly.")
    say("")

    if time.time() > deadline:
        return _abort(args, started, log, "before Variant 1")

    say("4. VARIANT 1 -- AS-IMPLEMENTED D4 (max-only, REUSED not recomputed, "
        "from RUN-INSTR-d5check-b8faf7)")
    v1_results = run_full_analysis_gaussian(
        fb_sizes, loc_scale, z, gaussian_records, d4_maxonly_by_n,
        ctrl_r3r4.R4_RUNG_SIZES)
    v1_summary = summarise_variant(v1_results, "Variant 1 (max-only D4)")
    h1 = v1_summary["headline"]
    say(f"   HEADLINE: {h1['d5_fired_count']}/{h1['n_accepted']} "
        f"({(h1['d5_fired_fraction'] or 0) * 100:.3f}%), Wilson 95% CI "
        f"[{h1['wilson_95_ci']['lower']:.4f}, "
        f"{h1['wilson_95_ci']['upper']:.4f}]")
    say(f"   expected per two independent prior reproductions: 21/485 "
        f"(4.330%)")
    if h1['d5_fired_count'] != 21 or h1['n_accepted'] != 485:
        say(f"   *** MISMATCH vs the two prior independent reproductions' "
            f"expected 21/485 -- NOT silently reconciled; reported plainly, "
            f"see execution report investigation section. ***")
    else:
        say(f"   MATCHES the two prior independent reproductions' expected "
            f"21/485 exactly.")
    say("")

    if time.time() > deadline:
        return _abort(args, started, log, "before Variant 2 D4-extreme "
                     "calibration")

    say("5. VARIANT 2 -- D4-EXTREME: NEW MONTE CARLO NULL CALIBRATION ON "
        "D3's OWN TWO-SIDED EXTREME-POINT STATISTIC")
    d4_ns = ctrl_r3r4.R4_RUNG_SIZES[3:8]
    say(f"   ns (rungs 4-8's own seed counts) = {d4_ns}")
    say(f"   trials per n = {args.d4_extreme_trials}, master_seed = "
        f"{D4_EXTREME_MASTER_SEED}")
    d4_extreme = compute_d4_calibration_extreme(
        d4_ns, D4_EXTREME_MASTER_SEED, args.d4_extreme_trials)
    for n in d4_ns:
        c = d4_extreme["by_n"][n]
        say(f"   n={n}: median={c['median']:.4f} p90={c['p90']:.4f} "
            f"p99={c['p99']:.4f} max={c['max']:.4f}")
    say("")

    if time.time() > deadline:
        return _abort(args, started, log, "before Variant 2 Gaussian pass")

    say("6. VARIANT 2 -- GAUSSIAN ARM RERUN THROUGH D4-EXTREME")
    d4_extreme_by_n = {n: v for n, v in d4_extreme["by_n"].items()}
    v2_gaussian_results = run_full_analysis_gaussian(
        fb_sizes, loc_scale, z, gaussian_records, d4_extreme_by_n,
        ctrl_r3r4.R4_RUNG_SIZES)
    v2_gaussian_summary = summarise_variant(
        v2_gaussian_results, "Variant 2 (D4-extreme), Gaussian arm")
    h2g = v2_gaussian_summary["headline"]
    say(f"   HEADLINE: {h2g['d5_fired_count']}/{h2g['n_accepted']} "
        f"({(h2g['d5_fired_fraction'] or 0) * 100:.3f}%), Wilson 95% CI "
        f"[{h2g['wilson_95_ci']['lower']:.4f}, "
        f"{h2g['wilson_95_ci']['upper']:.4f}]")
    say(f"   expected per the Red Team's own prior finding: 7/485 (1.443%)")
    if h2g['d5_fired_count'] != 7 or h2g['n_accepted'] != 485:
        say(f"   *** MISMATCH vs the Red Team's expected 7/485 -- NOT "
            f"silently reconciled; reported plainly, see execution report "
            f"investigation section. ***")
    else:
        say(f"   MATCHES the Red Team's expected 7/485 exactly.")
    say("")

    if time.time() > deadline:
        return _abort(args, started, log, "before Variant 2 Student-t "
                     "cross-check")

    say("7. VARIANT 2 -- STUDENT-t(5) ARM RERUN THROUGH D4-EXTREME "
        "(completeness/cross-check, reusing ctrl_r3r4_d5check's own "
        "machinery)")
    student_t_committed = _load_json(STUDENT_T_JSON)
    student_t_records = student_t_committed["records"]
    v2_student_t_raw = ctrl_r3r4_d5check.run_full_analysis(
        fb_sizes, loc_scale, z, student_t_records, d4_extreme_by_n,
        ctrl_r3r4.R4_RUNG_SIZES)
    v2_student_t_summary_full = ctrl_r3r4_d5check.summarise(v2_student_t_raw)
    h2t = v2_student_t_summary_full["headline"]
    k2t = h2t["d5_fired_count"]
    n2t = h2t["n_accepted"]
    ci2t = wilson_ci(k2t, n2t) if n2t else None
    say(f"   HEADLINE: {k2t}/{n2t} "
        f"({(h2t['d5_fired_fraction'] or 0) * 100:.3f}%), Wilson 95% CI "
        f"[{ci2t['lower']:.4f}, {ci2t['upper']:.4f}]" if n2t else
        f"   HEADLINE: {k2t}/{n2t}")
    say(f"   expected per the Red Team's own prior finding: UNCHANGED at "
        f"94/94 (100%)")
    if k2t != 94 or n2t != 94:
        say(f"   *** MISMATCH vs the Red Team's expected UNCHANGED 94/94 -- "
            f"NOT silently reconciled; reported plainly, see execution "
            f"report investigation section. ***")
    else:
        say(f"   MATCHES the Red Team's expected UNCHANGED 94/94 exactly.")
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
        "faithfulness_gate_all_match": gate["all_match"],
        "faithfulness_gate_n_checked": gate["n_checked"],
        "variant1_maxonly_d4_d5_fired_count": h1["d5_fired_count"],
        "variant1_maxonly_d4_d5_fired_fraction": h1["d5_fired_fraction"],
        "variant1_maxonly_d4_n_accepted": h1["n_accepted"],
        "variant1_maxonly_d4_wilson_95_ci": h1["wilson_95_ci"],
        "variant2_extreme_d4_gaussian_d5_fired_count": h2g["d5_fired_count"],
        "variant2_extreme_d4_gaussian_d5_fired_fraction":
            h2g["d5_fired_fraction"],
        "variant2_extreme_d4_gaussian_n_accepted": h2g["n_accepted"],
        "variant2_extreme_d4_gaussian_wilson_95_ci": h2g["wilson_95_ci"],
        "variant2_extreme_d4_student_t_d5_fired_count": k2t,
        "variant2_extreme_d4_student_t_n_accepted": n2t,
        "variant2_extreme_d4_student_t_wilson_95_ci": ci2t,
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
            "reference_run_gaussian": REFERENCE_RUN_ID,
            "gaussian_json": GAUSSIAN_JSON,
            "reference_run_student_t": REFERENCE_RUN_ID,
            "student_t_json": STUDENT_T_JSON,
            "d4_maxonly_run": D4_MAXONLY_RUN_ID,
            "d4_maxonly_json": D4_MAXONLY_JSON,
            "fb_sizes": fb_sizes,
            "d3_rows": D3_ROWS,
            "z_computed": z,
            "z_computed_from": "z_from_coverage(519, 520)",
            "r4_gaussian_master_seed_imported":
                ctrl_r3r4.R4_GAUSSIAN_MASTER_SEED,
            "r4_student_t_master_seed_imported": ctrl_r3r4.R4_MASTER_SEED,
            "r4_rung_sizes_imported": ctrl_r3r4.R4_RUNG_SIZES,
            "d4_extreme_master_seed": D4_EXTREME_MASTER_SEED,
            "d4_extreme_trials_per_n": args.d4_extreme_trials,
            "faithfulness_check_count": args.faithfulness_check_count,
            "max_seconds": args.max_seconds,
        },
        "frozen_inputs": {k: v for k, v in frozen.items()
                          if k != "amendment_frozen_parameters"},
        "amendment_frozen_parameters": frozen["amendment_frozen_parameters"],
        "faithfulness_gate": gate,
        "d4_maxonly_calibration_reused": d4_maxonly_committed,
        "d4_extreme_calibration": d4_extreme,
        "variant1_maxonly_d4": {
            "summary": v1_summary,
            "records": v1_results,
        },
        "variant2_extreme_d4": {
            "gaussian_summary": v2_gaussian_summary,
            "gaussian_records": v2_gaussian_results,
            "student_t_summary": {
                "label": "Variant 2 (D4-extreme), Student-t(5) arm "
                         "(completeness/cross-check)",
                "d5_fired_count": k2t,
                "n_accepted": n2t,
                "d5_fired_fraction": h2t["d5_fired_fraction"],
                "wilson_95_ci": ci2t,
            },
            "student_t_records": v2_student_t_raw,
        },
        "scope": SCOPE_NOTE,
        "certificate_note": CERTIFICATE_NOTE,
        "authority_note": (
            "This module records observations only. It does not conclude "
            "that amendment v3 change E11 closes or fails to close the gap "
            "DEC-20260811-45583f's rationale identifies, does not approve, "
            "reject, withdraw or amend EXP-INSTR-36c8cf amendment v3, and "
            "does not move H-INSTR-444c7b or any other hypothesis status. "
            "That judgement belongs to the Coordinator, after independent "
            "review, in a decision record."),
    }
    cmd = (f"python3 -m harness.exp_instr_36c8cf.ctrl_r3r4_d5check_gaussian "
           f"--suffix {args.suffix} "
           f"--faithfulness-check-count {args.faithfulness_check_count} "
           f"--d4-extreme-trials {args.d4_extreme_trials} "
           f"--max-seconds {args.max_seconds}")
    run_id = _emit(args.suffix, metrics, raw, "\n".join(log) + "\n", cmd,
                   started, finished, "completed", valid=True)
    print(f"wrote {run_id}", flush=True)

    _dump(run_id, "faithfulness-gate.json", gate)
    _dump(run_id, "d4-extreme-calibration.json", d4_extreme)
    _dump(run_id, "d4-maxonly-calibration-reused.json", d4_maxonly_committed)
    _dump(run_id, "variant1-maxonly-d4-per-replication.json", v1_results)
    _dump(run_id, "variant1-maxonly-d4-summary.json", v1_summary)
    _dump(run_id, "variant2-extreme-d4-gaussian-per-replication.json",
         v2_gaussian_results)
    _dump(run_id, "variant2-extreme-d4-gaussian-summary.json",
         v2_gaussian_summary)
    _dump(run_id, "variant2-extreme-d4-student-t-per-replication.json",
         v2_student_t_raw)
    _dump(run_id, "variant2-extreme-d4-student-t-summary.json", {
        "d5_fired_count": k2t, "n_accepted": n2t,
        "d5_fired_fraction": h2t["d5_fired_fraction"],
        "wilson_95_ci": ci2t})
    _dump(run_id, "frozen-inputs.json", frozen)
    return 0


def _abort(args, started, log, where: str) -> int:
    finished = time.time()
    say = log.append
    say(f"ABORTED: wall-clock budget of {args.max_seconds}s exhausted "
        f"{where}.")
    metrics = {"control": CONTROL_ID, "task_id": TASK_ID, "aborted": True,
              "wall_seconds": round(finished - started, 3)}
    raw = {"control": CONTROL_ID, "task_id": TASK_ID, "aborted": True,
          "aborted_at": where}
    cmd = (f"python3 -m harness.exp_instr_36c8cf.ctrl_r3r4_d5check_gaussian "
           f"--suffix {args.suffix} --max-seconds {args.max_seconds}")
    run_id = _emit(args.suffix, metrics, raw, "\n".join(log) + "\n", cmd,
                   started, finished, "failed_infrastructure", valid=False,
                   invalid_reason=(
                       f"wall-clock budget of {args.max_seconds}s exhausted "
                       f"{where}; infrastructure failure (resource_"
                       f"exhaustion), NEVER negative evidence (AGENTS.md "
                       f"rule 5)."))
    print(f"wrote {run_id} (ABORTED)", flush=True)
    return 1


def _finish_gate_failure(args, started, log, frozen, gate) -> int:
    """The faithfulness gate failed: this is a DEFECT in this module's own
    reimplementation, not a negative result about D3/D4/D5. Recorded as
    implementation_error / completed_invalid, per AGENTS.md's certificate/
    claim discipline and the handoff's own explicit instruction to stop."""
    finished = time.time()
    metrics = {"control": CONTROL_ID, "task_id": TASK_ID,
              "faithfulness_gate_all_match": False,
              "wall_seconds": round(finished - started, 3)}
    raw = {"control": CONTROL_ID, "task_id": TASK_ID,
          "faithfulness_gate": gate, "frozen_inputs": frozen,
          "classification": "implementation_error",
          "note": ("Faithfulness gate failed: this module's independent "
                   "reimplementation of the Gaussian draw generation does "
                   "not reproduce RUN-INSTR-r3r4-nullobj-d3efd7's own "
                   "committed accepted_rung/terminal_rung/exceed_total_at_"
                   "terminal for at least one checked replication index. "
                   "D3/D4/D5 were NOT computed for either variant. This is "
                   "a defect in this module, not a negative observation "
                   "about D3/D4/D5's catch rate (AGENTS.md rule 5).")}
    cmd = (f"python3 -m harness.exp_instr_36c8cf.ctrl_r3r4_d5check_gaussian "
           f"--suffix {args.suffix} --max-seconds {args.max_seconds}")
    run_id = _emit(args.suffix, metrics, raw, "\n".join(log) + "\n", cmd,
                   started, finished, "completed_invalid", valid=False,
                   invalid_reason=(
                       "faithfulness gate failed: recomputed accepted_rung/"
                       "terminal_rung/exceed_total_at_terminal did not match "
                       "the already-committed r4-gaussian-calibration-"
                       "optional.json for at least one checked replication "
                       "index. implementation_error -- do not trust any "
                       "D3/D4/D5 figure from this run."))
    print(f"wrote {run_id} (FAITHFULNESS GATE FAILED)", flush=True)
    _dump(run_id, "faithfulness-gate.json", gate)
    return 1


if __name__ == "__main__":                                # pragma: no cover
    raise SystemExit(main())

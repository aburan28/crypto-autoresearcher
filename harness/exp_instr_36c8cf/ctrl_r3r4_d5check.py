"""EXP-INSTR-36c8cf: D3/D4/D5 truncated-window catch-rate check (TASK-20260811-409237).

Dispatched directly from `DEC-20260811-45583f.next_actions` (the PRIMARY
item): a NEW module, producing a NEW immutable run under the EXISTING,
approved EXP-INSTR-36c8cf contract (`specification.yaml` `status: approved`).
No new specification.yaml, no amendment. Follows the same
"not_a_new_experiment_contract" shape as TASK-20260811-bc336d
(`harness/exp_instr_36c8cf/ctrl_r3r4.py`, CTRL-R3R4-JACKKNIFE-NULLOBJECT).

WHAT THIS ANSWERS. `experiments/EXP-INSTR-36c8cf/amendments/v3.yaml` change
E11 adds D3 (a leave-one-out tail diagnostic), D4 (a Monte-Carlo-calibrated
null threshold) and D5 (a recurrence-across-more-than-one-rung trigger),
scoped to fb=18 and fb=22, as a real repair bound into the NOW-APPROVED v3
contract. `DEC-20260811-45583f` paused dispatching a REAL successor run
against v3 because it is not yet known whether E11's D3/D4/D5, as specified,
would actually have caught the kind of alternative
`RUN-INSTR-r3r4-nullobj-d3efd7` already demonstrated slips past v3's
UNCHANGED T2 acceptance rule 18.8% of the time (94/500 replications). This
module answers that question empirically, reusing the EXACT SAME
500-replication Student-t(df=5) simulation (same master seed, same draws --
no new data is drawn for the purpose of accept/reject; only the truncation
window per replication is taken from the ALREADY-COMMITTED
`r4-student-t5-nullobject.json`) by computing D3/D4/D5 exactly as amendment
v3 change E11 specifies, and checking, per replication, whether D5 would have
fired at or before the rung T2 itself would have accepted -- i.e. ONLY using
the rungs T2's own first-pass-wins rule would actually have measured before
stopping (see `_window_for_replication` below, the central point of this
whole task).

WHAT THIS MODULE DOES NOT DO. It does not edit `ctrl_r3r4.py`, `sr3v3.py`,
`refvalues_v2.py`, or anything under `experiments/`. It does not touch
`RUN-INSTR-r3r4-nullobj-d3efd7` or `RUN-INSTR-36c8cf-phaseA-v2-57ca9a` (both
read-only inputs). It does not approve, reject or amend
`experiments/EXP-INSTR-36c8cf/amendments/v3.yaml`, and does not draft a v4.
It does not move any hypothesis status. `claim_tier: toy`, `sota_delta: 0` on
every axis. It records observations only -- whether v3's own repair (E11)
closes the gap `DEC-20260811-45583f`'s rationale identifies is the
Coordinator's judgement, after independent review, in a decision record.
"""
from __future__ import annotations

import argparse
import json
import math
import os
import statistics
import time

import numpy as np

from harness.exp_instr_36c8cf import ctrl_r3r4, sr3v3
from harness.exp_instr_36c8cf.refvalues import sha256_of

EXPERIMENT_ID = "EXP-INSTR-36c8cf"
RUN_AREA = "INSTR"
CONTROL_ID = "CTRL-D5CHECK-TRUNCATED-WINDOW"
TASK_ID = "TASK-20260811-409237"

REFERENCE_RUN_ID = "RUN-INSTR-r3r4-nullobj-d3efd7"
R4_JSON = (f"experiments/{EXPERIMENT_ID}/runs/{REFERENCE_RUN_ID}/"
           "r4-student-t5-nullobject.json")
AMENDMENT_V3 = f"experiments/{EXPERIMENT_ID}/amendments/v3.yaml"
CTRL_R3R4_MODULE = "harness/exp_instr_36c8cf/ctrl_r3r4.py"
SR3V3_MODULE = "harness/exp_instr_36c8cf/sr3v3.py"

# D3/D4/D5 are scoped to fb=18 and fb=22 specifically (amendment v3 change E11).
D3_ROWS = [18, 22]

# D4's own DECLARED, DISCLOSED master seed for the Monte Carlo null
# calibration. Arbitrary fixed integer, distinct from R4_MASTER_SEED
# (314159265, ctrl_r3r4.py's Student-t(5) arm) and R4_GAUSSIAN_MASTER_SEED
# (271828182, ctrl_r3r4.py's optional Gaussian arm): the first nine digits of
# sqrt(2) (1.41421356...), chosen as a recognisable fixed constant with no
# other role anywhere in this campaign, exactly the same declared-constant
# convention ctrl_r3r4.py itself uses for its own two master seeds.
D4_MASTER_SEED = 141421356
D4_TRIALS = 20000

CERTIFICATE_NOTE = (
    "certificate.kind: none, EXPLICITLY. This is pure post-hoc statistics "
    "(D3 leave-one-out diagnostic recomputation) and pure numpy simulation "
    "(D4 Monte Carlo null calibration) over an already-committed synthetic "
    "null-object simulation. No discrete logarithm is computed and no "
    "factor-base relation is claimed anywhere in this module, so there is no "
    "solve or relation to certify (docs/claims-and-verification.md).")

SCOPE_NOTE = (
    "Tier TOY. A bounded reanalysis of an already-committed synthetic "
    "null-object simulation (RUN-INSTR-r3r4-nullobj-d3efd7's "
    "r4-student-t5-nullobject.json), computing amendment v3 change E11's own "
    "D3/D4/D5 diagnostic exactly as specified, truncated to the rung window "
    "T2's first-pass-wins rule would actually have measured before stopping. "
    "No ECDLP attack, exponent or speedup claim of any kind. claim_tier toy, "
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
# frozen inputs, read at run time -- nothing transcribed (standing rule A4)
# --------------------------------------------------------------------------


def load_frozen_inputs() -> dict:
    frozen = ctrl_r3r4.load_frozen_inputs()
    loaded = ctrl_r3r4.load_rung3_family(frozen["fb_sizes"])
    frozen = dict(frozen)
    frozen["loc_scale_rung3"] = loaded["rung3"]
    frozen["source_sha256"] = dict(frozen["source_sha256"])
    frozen["source_sha256"][R4_JSON] = sha256_of(R4_JSON)
    frozen["source_sha256"][AMENDMENT_V3] = sha256_of(AMENDMENT_V3)
    return frozen


# --------------------------------------------------------------------------
# FAITHFULNESS GATE -- reimplement the Student-t(df=5) draw generation
# independently, and check accepted_rung/terminal_rung/exceed_total_at_
# terminal against the already-committed record, for a spread of >= 20
# replication indices. MANDATORY, RUN FIRST, BEFORE ANY D3/D4/D5 CODE IS
# TRUSTED.
# --------------------------------------------------------------------------


def draw_replication_detailed(fb_sizes: list, loc_scale: dict, z: float,
                              stability_pct: float, rep_seed,
                              rung_sizes: list) -> dict:
    """Independent reimplementation of ctrl_r3r4.draw_null_object_replication's
    accepted_rung/terminal_rung/exceed_total_at_terminal logic, for the
    faithfulness gate. Deliberately NOT calling ctrl_r3r4's own function --
    the whole point of this gate is to catch a transcription/logic drift
    between an independent reimplementation and the committed record, which a
    direct call could not do.
    """
    row_seeds = rep_seed.spawn(len(fb_sizes))
    draws = {}
    for fb, rseed in zip(fb_sizes, row_seeds):
        rng = np.random.default_rng(rseed)
        loc = loc_scale[str(fb)]["mean"]
        scale = loc_scale[str(fb)]["sd_sample_n_minus_1"]
        n_max = rung_sizes[-1]
        t = rng.standard_t(df=5, size=n_max)
        draws[fb] = loc + (scale / math.sqrt(5.0 / 3.0)) * t

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


def faithfulness_check_indices(n_total: int, n_check: int) -> list:
    """>= 20 replication indices, spread across the full 0..n_total-1 range,
    not clustered. Evenly spaced via np.linspace, deduplicated, endpoints
    included."""
    raw = np.linspace(0, n_total - 1, n_check)
    idx = sorted(set(int(round(x)) for x in raw))
    return idx


def faithfulness_gate(fb_sizes: list, loc_scale: dict, z: float,
                      stability_pct: float, committed_records: list,
                      check_indices: list) -> dict:
    master = np.random.SeedSequence(ctrl_r3r4.R4_MASTER_SEED)
    rep_seeds = master.spawn(ctrl_r3r4.R4_REPLICATIONS)
    per_index = []
    all_match = True
    for i in check_indices:
        got = draw_replication_detailed(
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
            "master_seed": ctrl_r3r4.R4_MASTER_SEED,
            "per_index": per_index}


# --------------------------------------------------------------------------
# D4: Monte Carlo null calibration, once per distinct n (the five rungs 4-8's
# own seed counts), NOT per replication and NOT per row.
# --------------------------------------------------------------------------


def compute_d4_calibration(ns: list, master_seed: int, trials: int) -> dict:
    """For each n: draw n i.i.d. N(0,1) values, compute the LOO z-score of the
    sample MAXIMUM (mean/sd of the other n-1), repeat `trials` times, report
    median/90th/99th percentile/max. `trials` independent sub-streams, one per
    n, spawned once from `master_seed` (declared choice: independently
    spawned sub-streams, not one stream reused sequentially -- see
    execution report judgment-call section).
    """
    master = np.random.SeedSequence(master_seed)
    sub_seeds = master.spawn(len(ns))
    out = {}
    for n, sseed in zip(ns, sub_seeds):
        rng = np.random.default_rng(sseed)
        X = rng.standard_normal(size=(trials, n))
        max_vals = X.max(axis=1)
        sum_all = X.sum(axis=1)
        sumsq_all = (X ** 2).sum(axis=1)
        sum_rest = sum_all - max_vals
        sumsq_rest = sumsq_all - max_vals ** 2
        m = n - 1
        mean_rest = sum_rest / m
        var_rest = (sumsq_rest - (sum_rest ** 2) / m) / (m - 1)
        sd_rest = np.sqrt(var_rest)
        loo_z = (max_vals - mean_rest) / sd_rest
        out[n] = {
            "n": n,
            "trials": trials,
            "median": float(np.median(loo_z)),
            "p90": float(np.percentile(loo_z, 90)),
            "p99": float(np.percentile(loo_z, 99)),
            "max": float(loo_z.max()),
        }
    return {"master_seed": master_seed,
            "seed_derivation": (
                "numpy.random.SeedSequence(master_seed).spawn(len(ns)) -> "
                "one independent sub-stream per distinct n, in the order ns "
                "is given (rungs 4 through 8's own seed counts, ascending)."),
            "by_n": out}


# --------------------------------------------------------------------------
# D3: per-row, per-rung leave-one-out tail diagnostic.
# --------------------------------------------------------------------------


def d3_loo(ratios: list, z: float) -> dict:
    """The row's single most extreme per-seed ratio at this rung (by absolute
    deviation from the row's own in-sample mean at this rung); recompute
    mean/sd EXCLUDING that point (LOO, via sr3v3.interval_for_rung on the
    remaining n-1 points, same z everywhere); score the excluded point
    against the LOO mean/sd. Ties in "most extreme": broken by first
    occurrence (lowest seed index) -- `max()` over a list naturally returns
    the first-encountered maximal element in Python, so no separate
    tie-break code path is needed; stated explicitly here since the
    amendment text does not specify a tie rule.
    """
    n = len(ratios)
    mean = statistics.mean(ratios)
    devs = [abs(r - mean) for r in ratios]
    extreme_idx = max(range(n), key=lambda i: devs[i])
    excluded_point = ratios[extreme_idx]
    rest = ratios[:extreme_idx] + ratios[extreme_idx + 1:]
    refit = sr3v3.interval_for_rung(rest, z)
    mean_loo = refit["mean"]
    sd_loo = refit["sd_sample_n_minus_1"]
    loo_z = (excluded_point - mean_loo) / sd_loo
    return {"n_seeds": n, "row_in_sample_mean": mean,
            "extreme_idx": extreme_idx, "excluded_point": excluded_point,
            "mean_loo": mean_loo, "sd_loo": sd_loo, "loo_z": loo_z}


# --------------------------------------------------------------------------
# WHAT "STOPPING" MEANS FOR THIS CHECK -- the central point of the task.
# --------------------------------------------------------------------------


def window_for_replication(accepted_rung) -> list:
    """T2's own text (unchanged, adopted by v3 verbatim) says the
    characterisation STOPS at the first rung that passes the unchanged 5%
    rule: rungs after accepted_rung are never even measured, so their D3/D4
    data would never exist. If accepted_rung is set, the window is rungs 4
    through min(accepted_rung, 8) inclusive; otherwise (never accepted by
    rung 8) all five rungs 4-8 are available, since the simulated run would
    have continued measuring through rung 8 before an F4-equivalent fires."""
    end = min(accepted_rung, 8) if accepted_rung is not None else 8
    return list(range(4, end + 1))


# --------------------------------------------------------------------------
# per-replication D3/D4/D5, restricted to fb=18 and fb=22, restricted to the
# truncated rung window
# --------------------------------------------------------------------------


def analyse_replication(rep_seed, committed_rec: dict, fb_sizes: list,
                        loc_scale: dict, z: float, d4_by_n: dict,
                        rung_sizes: list) -> dict:
    accepted_rung = committed_rec["accepted_rung"]
    terminal_rung = committed_rec["terminal_rung"]
    window = window_for_replication(accepted_rung)

    row_seeds = rep_seed.spawn(len(fb_sizes))
    per_row = {}
    for fb in D3_ROWS:
        ridx = fb_sizes.index(fb)
        rseed = row_seeds[ridx]
        rng = np.random.default_rng(rseed)
        loc = loc_scale[str(fb)]["mean"]
        scale = loc_scale[str(fb)]["sd_sample_n_minus_1"]
        n_max = rung_sizes[-1]
        t = rng.standard_t(df=5, size=n_max)
        draws = loc + (scale / math.sqrt(5.0 / 3.0)) * t

        rung_records = {}
        exceed_count = 0
        d5_fire_rung = None
        for rung in window:
            n = rung_sizes[rung - 1]
            ratios = [float(v) for v in draws[:n]]
            d3 = d3_loo(ratios, z)
            thr = d4_by_n[n]["p99"]
            # Two-sided reading, stated explicitly (judgment call): D4
            # calibrates only the LOO z-score of the sample MAXIMUM (a
            # one-sided quantity, always effectively positive), while D3's
            # extreme point can be the row's high OR low tail. Under the null
            # (N(0,1), symmetric) the distribution of the most-extreme-by-
            # absolute-deviation point's LOO z-score has the same magnitude
            # distribution as the maximum's LOO z-score, by the symmetry of
            # "most extreme is the max" vs "most extreme is the min" (each
            # occurs with probability 1/2, and the two conditional
            # distributions are mirror images). Comparing |D3 loo_z| against
            # D4's one-sided p99 threshold is therefore the natural symmetric
            # reading of "exceeds that rung's own D4-calibrated 99th-
            # percentile threshold" and is what is implemented here; see the
            # execution report's judgment-call section.
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


def run_full_analysis(fb_sizes: list, loc_scale: dict, z: float,
                      committed_records: list, d4_by_n: dict,
                      rung_sizes: list) -> list:
    master = np.random.SeedSequence(ctrl_r3r4.R4_MASTER_SEED)
    rep_seeds = master.spawn(ctrl_r3r4.R4_REPLICATIONS)
    out = []
    for i, rep_seed in enumerate(rep_seeds):
        rec = analyse_replication(rep_seed, committed_records[i], fb_sizes,
                                  loc_scale, z, d4_by_n, rung_sizes)
        rec["replication"] = i
        out.append(rec)
    return out


def summarise(results: list) -> dict:
    accepted = [r for r in results if r["accepted_rung"] is not None]
    not_accepted = [r for r in results if r["accepted_rung"] is None]
    accepted_fired = [r for r in accepted if r["d5_fired"]]
    not_accepted_fired = [r for r in not_accepted if r["d5_fired"]]
    window_sizes_accepted = sorted(set(r["window_size"] for r in accepted))
    fewer_than_two_rungs = [r for r in accepted if r["window_size"] < 2]
    return {
        "n_replications": len(results),
        "n_accepted_rung_set": len(accepted),
        "n_not_accepted_by_rung8": len(not_accepted),
        "headline": {
            "description": (
                "Of the 94 replications with accepted_rung set (T2 fired), "
                "the count/fraction where D5 (per amendment v3 change E11, "
                "at fb=18 or fb=22, recurrence >= 2 rungs) fires WITHIN the "
                "truncated rung window T2's own first-pass-wins rule would "
                "actually have measured before stopping."),
            "d5_fired_count": len(accepted_fired),
            "d5_fired_fraction": (len(accepted_fired) / len(accepted)
                                  if accepted else None),
            "n_accepted": len(accepted),
        },
        "accepted_replications_window_sizes_observed": window_sizes_accepted,
        "accepted_replications_with_fewer_than_2_rungs_available": len(
            fewer_than_two_rungs),
        "informational_completeness_not_accepted_by_rung8": {
            "description": (
                "For the 406 replications that never reach accepted_rung by "
                "rung 8, all five rungs 4-8 are available (informational "
                "completeness only, NOT the central question)."),
            "d5_fired_count": len(not_accepted_fired),
            "d5_fired_fraction": (len(not_accepted_fired) / len(not_accepted)
                                  if not_accepted else None),
            "n_not_accepted": len(not_accepted),
        },
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
        curve_id="n/a (post-hoc statistics and Monte Carlo calibration over "
                 "an already-committed synthetic null-object simulation; no "
                 "curve is enumerated)",
        seed=ctrl_r3r4.R4_MASTER_SEED, parameters=raw.get("parameters", {}),
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
        description="D3/D4/D5 truncated-window catch-rate check "
                    "(EXP-INSTR-36c8cf, TASK-20260811-409237)")
    ap.add_argument("--suffix", required=True)
    ap.add_argument("--faithfulness-check-count", type=int, default=25,
                    help=">= 20, spread across the 0..499 replication range")
    ap.add_argument("--d4-trials", type=int, default=D4_TRIALS)
    ap.add_argument("--max-seconds", type=int, default=1800)
    args = ap.parse_args(argv)

    started = time.time()
    deadline = started + args.max_seconds
    log: list = []

    def say(msg: str) -> None:
        log.append(msg)
        print(msg, flush=True)

    say(f"{CONTROL_ID} -- {EXPERIMENT_ID} ({TASK_ID})")
    say("Does amendment v3 change E11's D3/D4/D5 (fb=18/fb=22, recurrence "
        ">= 2 rungs) catch the alternative RUN-INSTR-r3r4-nullobj-d3efd7 "
        "already demonstrated slips past T2 18.8% of the time, WITHIN the "
        "rung window T2's own first-pass-wins rule would actually have "
        "measured before stopping? Per DEC-20260811-45583f.next_actions "
        "(PRIMARY).")
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
    say(f"   R4_MASTER_SEED (imported, not retyped) = {ctrl_r3r4.R4_MASTER_SEED}")
    say(f"   R4_RUNG_SIZES (imported, not retyped) = {ctrl_r3r4.R4_RUNG_SIZES}")
    say(f"   D4_MASTER_SEED (this module's own, declared) = {D4_MASTER_SEED}")
    say("")

    say(f"1. LOADING THE ALREADY-COMMITTED REFERENCE RECORD ({R4_JSON})")
    committed = _load_json(R4_JSON)
    committed_records = committed["records"]
    say(f"   sha256: {frozen['source_sha256'][R4_JSON]}")
    say(f"   n_replications_completed (committed) = "
        f"{committed['n_replications_completed']}")
    say(f"   accept_by_rung8_count (committed) = "
        f"{committed['accept_by_rung8_count']}")
    say("")

    if time.time() > deadline:
        return _abort(args, started, log, "before faithfulness gate")

    say("2. FAITHFULNESS GATE -- MANDATORY, RUN FIRST")
    check_indices = faithfulness_check_indices(
        len(committed_records), args.faithfulness_check_count)
    say(f"   checking {len(check_indices)} replication indices, spread "
        f"across 0..{len(committed_records) - 1}: {check_indices}")
    gate = faithfulness_gate(fb_sizes, loc_scale, z, stability_pct,
                             committed_records, check_indices)
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
        "record exactly.")
    say("")

    if time.time() > deadline:
        return _abort(args, started, log, "before D4 calibration")

    say("3. D4: MONTE CARLO NULL CALIBRATION, ONCE PER DISTINCT n (rungs 4-8)")
    d4_ns = ctrl_r3r4.R4_RUNG_SIZES[3:8]
    say(f"   ns (rungs 4-8's own seed counts) = {d4_ns}")
    say(f"   trials per n = {args.d4_trials}, master_seed = {D4_MASTER_SEED}")
    d4 = compute_d4_calibration(d4_ns, D4_MASTER_SEED, args.d4_trials)
    for n in d4_ns:
        c = d4["by_n"][n]
        say(f"   n={n}: median={c['median']:.4f} p90={c['p90']:.4f} "
            f"p99={c['p99']:.4f} max={c['max']:.4f}")
    say("")

    if time.time() > deadline:
        return _abort(args, started, log, "before D3/D5 per-replication pass")

    say("4. D3/D5: PER-REPLICATION, TRUNCATED TO T2's OWN STOPPING WINDOW")
    results = run_full_analysis(fb_sizes, loc_scale, z, committed_records,
                                d4["by_n"], ctrl_r3r4.R4_RUNG_SIZES)
    summary = summarise(results)
    h = summary["headline"]
    say(f"   HEADLINE: of {h['n_accepted']} replications with accepted_rung "
        f"set, D5 fires within the truncated window in {h['d5_fired_count']} "
        f"({h['d5_fired_fraction']:.4f})")
    say(f"   window sizes observed among accepted replications: "
        f"{summary['accepted_replications_window_sizes_observed']}")
    say(f"   accepted replications with < 2 rungs of D3/D4 data available: "
        f"{summary['accepted_replications_with_fewer_than_2_rungs_available']}")
    ic = summary["informational_completeness_not_accepted_by_rung8"]
    say(f"   informational (not accepted by rung 8): D5 fires in "
        f"{ic['d5_fired_count']}/{ic['n_not_accepted']} "
        f"({ic['d5_fired_fraction']:.4f})")
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
        "headline_d5_fired_count": h["d5_fired_count"],
        "headline_d5_fired_fraction": h["d5_fired_fraction"],
        "headline_n_accepted": h["n_accepted"],
        "informational_not_accepted_d5_fired_count": ic["d5_fired_count"],
        "informational_not_accepted_d5_fired_fraction": ic["d5_fired_fraction"],
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
            "reference_r4_json": R4_JSON,
            "fb_sizes": fb_sizes,
            "d3_rows": D3_ROWS,
            "z_computed": z,
            "z_computed_from": "z_from_coverage(519, 520)",
            "r4_master_seed_imported": ctrl_r3r4.R4_MASTER_SEED,
            "r4_rung_sizes_imported": ctrl_r3r4.R4_RUNG_SIZES,
            "r4_replications_imported": ctrl_r3r4.R4_REPLICATIONS,
            "d4_master_seed": D4_MASTER_SEED,
            "d4_trials_per_n": args.d4_trials,
            "faithfulness_check_count": args.faithfulness_check_count,
            "max_seconds": args.max_seconds,
        },
        "frozen_inputs": {k: v for k, v in frozen.items()
                          if k != "amendment_frozen_parameters"},
        "amendment_frozen_parameters": frozen["amendment_frozen_parameters"],
        "faithfulness_gate": gate,
        "d4_calibration": d4,
        "summary": summary,
        "records": results,
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
    cmd = (f"python3 -m harness.exp_instr_36c8cf.ctrl_r3r4_d5check "
           f"--suffix {args.suffix} "
           f"--faithfulness-check-count {args.faithfulness_check_count} "
           f"--d4-trials {args.d4_trials} --max-seconds {args.max_seconds}")
    run_id = _emit(args.suffix, metrics, raw, "\n".join(log) + "\n", cmd,
                   started, finished, "completed", valid=True)
    print(f"wrote {run_id}", flush=True)

    _dump(run_id, "faithfulness-gate.json", gate)
    _dump(run_id, "d4-calibration.json", d4)
    _dump(run_id, "d3-d5-per-replication.json", results)
    _dump(run_id, "summary.json", summary)
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
    cmd = (f"python3 -m harness.exp_instr_36c8cf.ctrl_r3r4_d5check "
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
                   "reimplementation of the Student-t(df=5) draw generation "
                   "does not reproduce RUN-INSTR-r3r4-nullobj-d3efd7's own "
                   "committed accepted_rung/terminal_rung/exceed_total_at_"
                   "terminal for at least one checked replication index. "
                   "D3/D4/D5 were NOT computed. This is a defect in this "
                   "module, not a negative observation about D3/D4/D5's "
                   "catch rate (AGENTS.md rule 5).")}
    cmd = (f"python3 -m harness.exp_instr_36c8cf.ctrl_r3r4_d5check "
           f"--suffix {args.suffix} --max-seconds {args.max_seconds}")
    run_id = _emit(args.suffix, metrics, raw, "\n".join(log) + "\n", cmd,
                   started, finished, "completed_invalid", valid=False,
                   invalid_reason=(
                       "faithfulness gate failed: recomputed accepted_rung/"
                       "terminal_rung/exceed_total_at_terminal did not match "
                       "the already-committed r4-student-t5-nullobject.json "
                       "for at least one checked replication index. "
                       "implementation_error -- do not trust any D3/D4/D5 "
                       "figure from this run."))
    print(f"wrote {run_id} (FAITHFULNESS GATE FAILED)", flush=True)
    _dump(run_id, "faithfulness-gate.json", gate)
    return 1


if __name__ == "__main__":                                # pragma: no cover
    raise SystemExit(main())

"""EXP-INSTR-36c8cf PHASE A, CONTRACT VERSION 2 driver.

Re-execution of TASK-20260810-c98659 PHASE A against the contract as amended by
experiments/EXP-INSTR-36c8cf/amendments/v1.yaml (amendment ordinal 1, version 1
-> version 2, recorded by DEC-20260810-56db2d).

THIS IS A NEW RUN UNDER A NEW RUN IDENTIFIER. RUN-INSTR-36c8cf-phaseA-2a5cd1
stays in the ledger as `completed_invalid` / `specification_error`, is not
re-scored, not re-keyed and not edited, and its own modules (`refvalues.py`,
`sr1.py`, `phase_a.py`) are left untouched so its code path stays re-executable.

PHASE A SCOPE, unchanged by the amendment:
  1. SR1 as narrowed by change G1 -- the two construction-free quantities only.
  2. The ENTIRE SR3 v3 reference characterisation at the frozen coverage.
NO GEOMETRY-SPECIFIC CELL IS RUN. SR2 forbids it until Stage 1 of
EXP-JINV-bd141d and EXP-VOLC-9f5571 emits the real geometry, and the amendment
names blockers B1 and B2 which leave those cells unexecutable in any case.

EVERY FROZEN PARAMETER IS READ FROM ITS RECORD AT RUN TIME. The coverage, the
quantiles, the seed rungs, the stability rule, the density rows, the target
count, the SR1 tolerance, the budget and the reference run identities are all
parsed from committed files and bound by sha256; z is COMPUTED from the frozen
exact fraction and never transcribed.

Usage:  PYTHONPATH=. python3 -m harness.exp_instr_36c8cf.phase_a_v2 \
            --run-suffix <suffix>
"""
from __future__ import annotations

import argparse
import json
import os
import platform
import resource
import subprocess
import sys
import time

import yaml

from harness import runner
from harness.exp_instr_36c8cf import refvalues, refvalues_v2, sr1_g1, sr3v3

EXP_ID = "EXP-INSTR-36c8cf"
EXP_AREA = "INSTR"
TASK_ID = "TASK-20260810-c98659"
GOAL_ID = "GOAL-ENDO-001"
BATCH_ID = "BATCH-d7e255"
AMENDED_CONTRACT_VERSION = 2
STAGING_ROOT = ("coordination/goals/GOAL-ENDO-001/batches/BATCH-d7e255/"
                "execution/EXP-INSTR-36c8cf")

LOAD_OBSERVATIONS: list[dict] = []


def observe_load(label: str) -> dict:
    one, five, fifteen = os.getloadavg()
    obs = {"label": label, "load_1min": one, "load_5min": five,
           "load_15min": fifteen, "cpu_count": os.cpu_count(),
           "observed_at": sr3v3.timestamp(),
           "elapsed_seconds_since_start": None}
    LOAD_OBSERVATIONS.append(obs)
    return obs


def inference_provenance() -> dict:
    """Agent-level inference provenance (the manifest's own `inference` block is
    harness/runner.py's static deterministic-execution block; runner.py is
    READ-ONLY to this task)."""
    try:
        resolved = subprocess.run(
            [sys.executable, "-m", "orchestration.adapter", "resolve",
             "--role", "executor"],
            cwd=refvalues.REPO, capture_output=True, text=True,
            env={**os.environ, "PYTHONPATH": refvalues.REPO}).stdout.strip()
    except Exception as exc:                                    # pragma: no cover
        resolved = f"adapter probe failed: {type(exc).__name__}: {exc}"
    return {
        "requested_policy": "executor-implementation",
        "adapter_resolution_for_role_executor": resolved,
        "resolved_model_id_that_actually_answered": "claude-opus-5",
        "fallback_used": True,
        "fallback_reason": (
            "AUTORESEARCH_POLICY is unset in this Claude Code harness, so the "
            "adapter-resolved environment was not applied and the session model "
            "answered instead of the policy's resolved model. The dispatching "
            "envelope states the adapter resolves executor-implementation to "
            "anthropic:claude-sonnet-5 (effort=medium) and that a different "
            "model would answer; the model that actually answered is recorded "
            "above. KNOWN AND ALREADY RECORDED as defect D4 of "
            "DEC-20260810-d70ece; the corrective is at harness level and is not "
            "this task's to make. Recorded, never silently substituted "
            "(AGENTS.md rule 11)."),
        "autoresearch_policy_env": os.environ.get("AUTORESEARCH_POLICY"),
        "autoresearch_backend_env": os.environ.get("AUTORESEARCH_BACKEND"),
        "model_verified": False,
        "model_verified_reason": "no adapter probe receipt; the env var is unset",
    }


def budget_from_contract() -> dict:
    with open(os.path.join(refvalues.REPO, refvalues_v2.INSTR_SPEC),
              encoding="utf-8") as fh:
        spec = yaml.safe_load(fh)["experiment"]
    b = dict(spec["budget"])
    b["source_path"] = refvalues_v2.INSTR_SPEC
    b["source_sha256"] = refvalues.sha256_of(refvalues_v2.INSTR_SPEC)
    return b


def git_context() -> dict:
    def sh(*args):
        return subprocess.run(args, cwd=refvalues.REPO, capture_output=True,
                              text=True).stdout.strip()
    return {
        "head_commit": sh("git", "rev-parse", "HEAD"),
        "branch": sh("git", "rev-parse", "--abbrev-ref", "HEAD"),
        "dirty": bool(sh("git", "status", "--porcelain")),
        "origin_main": sh("git", "rev-parse", "origin/main"),
        "merge_base_with_origin_main": sh("git", "merge-base", "HEAD",
                                          "origin/main"),
    }


# --------------------------------------------------------------------------
# CONFLICT-1, DECLARED BEFORE ANY DATA IS GENERATED
# --------------------------------------------------------------------------

CONFLICT_1 = {
    "id": "CONFLICT-1",
    "kind": "protocol_conflict_recorded_for_coordinator_adjudication",
    "between": [
        "the dispatching envelope's standing control 'targets_B "
        "(harness/exp_icinv_fullgroup.py), NEVER targets_uniform'",
        "the frozen contract's inputs.sr3_amendment_v3.characterisation_"
        "procedure, which requires re-measuring THE REFERENCE RUN at ITS OWN "
        "frozen parameters, naming the SAMPLER among them",
    ],
    "what_the_reference_run_s_own_sampler_is": (
        "exp_icinv.targets_uniform, via harness/run_saturation.py. Read at run "
        "time from the reference run's own manifest command and code path, not "
        "assumed."),
    "action_taken": (
        "THE CONTRACT WAS FOLLOWED: the SR3 v3 reference characterisation uses "
        "the reference run's own sampler. Substituting targets_B would "
        "characterise a DIFFERENT estimand -- the sampling distribution of a "
        "different arm -- so it would not be a re-measurement of the reference "
        "run at all, and C-SELF-CONSISTENCY ('a faithful re-measurement of the "
        "reference run at its own parameters compared against its own "
        "interval') would be vacuous."),
    "what_was_NOT_done_and_why": (
        "No targets_B arm was added. Adding an arm the frozen contract does not "
        "declare would be a scope extension forbidden by SR5 without a "
        "versioned amendment filed before the data is generated. The executor "
        "does not write amendments."),
    "what_the_envelope_control_IS_honoured_on": (
        "The stratification half of the same standing control is honoured in "
        "full and additively: every density row is reported stratified by "
        "r = #{x : x^3 + ax + b = 0} (exp_icinv.two_torsion_x_count), wherever "
        "a target is drawn. That reporting gates nothing."),
    "status": "OPEN. Adjudication belongs to the Coordinator, not to this run.",
    "declared_at": "before any measurement in this run was performed",
}

CONFLICT_1_SCOPE_NOTE = (
    "CONFLICT-1 concerns the SR3 v3 reference characterisation only. Phase A "
    "draws targets nowhere else: SR1 under change G1 draws no targets at all, "
    "it permutes committed measured values.")


# --------------------------------------------------------------------------


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--run-suffix", required=True)
    args = ap.parse_args()

    started = time.time()
    staging = os.path.join(refvalues.REPO, STAGING_ROOT,
                           f"staging-{args.run_suffix}")
    os.makedirs(staging, exist_ok=True)
    log_lines: list[str] = []

    def say(msg: str = "") -> None:
        log_lines.append(msg)
        print(msg, flush=True)

    def checkpoint(name: str, obj) -> None:
        """SESSION SURVIVAL: nothing is held only in memory."""
        with open(os.path.join(staging, name), "w", encoding="utf-8") as fh:
            json.dump(obj, fh, indent=2, sort_keys=True, default=str)

    def load(label: str) -> dict:
        obs = observe_load(label)
        obs["elapsed_seconds_since_start"] = round(time.time() - started, 3)
        say(f"[load @ {label}] 1min={obs['load_1min']:.2f} "
            f"5min={obs['load_5min']:.2f} 15min={obs['load_15min']:.2f} "
            f"cpu_count={obs['cpu_count']} "
            f"elapsed={obs['elapsed_seconds_since_start']:.1f}s")
        checkpoint("load-observations.json", LOAD_OBSERVATIONS)
        return obs

    deviations: list[dict] = []
    events: list[dict] = []

    say(f"=== {EXP_ID} PHASE A, contract version {AMENDED_CONTRACT_VERSION} "
        f"({TASK_ID}, {GOAL_ID}, {BATCH_ID}) ===")
    say(f"host: {platform.platform()}  cpu_count={os.cpu_count()}")
    say("single-threaded, sequential; NO internal parallelism, no subprocess "
        "worker, no thread pool")
    load("start")

    # ------------------------------------------------------------------
    # 0. every frozen parameter, read at run time
    # ------------------------------------------------------------------
    say("\n--- 0. FROZEN PARAMETERS, READ FROM THEIR RECORDS AT RUN TIME ---")
    amend = refvalues_v2.amendment_frozen_parameters()
    seeds_rec = refvalues_v2.instr_declared_seeds()
    grid = refvalues_v2.icinv_frozen_grid()
    refruns = refvalues_v2.sr3v3_reference_runs()
    published = refvalues.nullc_published_profile()
    bounds = refvalues.detection_bound_table()
    band = refvalues.superseded_band_slacks()
    data = refvalues.p4001_rate_m3_by_class()
    budget = budget_from_contract()
    gitctx = git_context()

    say(f"amendment {amend['source_path']} ordinal {amend['amendment_ordinal']} "
        f"v{amend['version_from']} -> v{amend['version_to']} "
        f"({amend['source_sha256'][:12]}...), approved_by "
        f"{amend['approved_by']} {amend['approved_at']}, recorded by "
        f"{amend['recorded_by_decision']}")
    say(f"  rows gated: {amend['number_of_density_rows_gated']}   "
        f"family-wise target: {amend['family_wise_error_target']}   "
        f"per-row alpha: "
        f"{amend['per_row_two_sided_alpha_fraction'][0]}/"
        f"{amend['per_row_two_sided_alpha_fraction'][1]}")
    say(f"  per-row central coverage: "
        f"{amend['per_row_central_coverage_fraction'][0]}/"
        f"{amend['per_row_central_coverage_fraction'][1]} = "
        f"{amend['per_row_central_coverage']:.9f}")
    say(f"  interval quantiles: "
        f"{amend['lower_quantile_fraction'][0]}/{amend['lower_quantile_fraction'][1]}"
        f" and {amend['upper_quantile_fraction'][0]}/"
        f"{amend['upper_quantile_fraction'][1]}")
    say(f"  seed rungs {amend['seed_rungs']}, extensions "
        f"{amend['rung2_extension_seed_range']} and "
        f"{amend['rung3_extension_seed_range']}, stability rule "
        f"{amend['stability_relative_half_width_pct']}% relative half-width")

    # z, COMPUTED, never transcribed
    zrec = sr3v3.z_from_coverage(*amend["upper_quantile_fraction"])
    say(f"  z = Phi^-1({zrec['upper_quantile_fraction']}) = {zrec['z']!r}  "
        f"[computed at run time; no reference value transcribed]")

    # the thirteen rows: CITED from the contract that owns them, cross-checked
    rows_match = grid["factor_base_sizes"] == amend["d1_density_rows"]
    T_match = grid["target_count_primary"] == amend["d1_target_count"]
    say(f"density rows from {grid['source_path']}: {grid['factor_base_sizes']} "
        f"at T = {grid['target_count_primary']}")
    say(f"  amendment D1 list agrees: {rows_match}; T agrees: {T_match}; "
        f"count == rows gated: "
        f"{len(grid['factor_base_sizes']) == amend['number_of_density_rows_gated']}")
    if not (rows_match and T_match
            and len(grid["factor_base_sizes"]) == amend["number_of_density_rows_gated"]):
        raise RuntimeError("the frozen density grid and the amendment disagree; "
                           "refusing to choose between them")

    say(f"reference runs, NAMED EXPLICITLY (from "
        f"{refruns['identified_from']['module']}:"
        f"{refruns['identified_from']['symbol']}):")
    for p_s, rec in sorted(refruns["runs"].items()):
        say(f"  p = {p_s}: {rec['experiment_id']} / {rec['run_id']}  "
            f"seed {rec['declared_seed_as_read']}  T = {rec['n_targets']}  "
            f"class trace {rec['trace']}  n_curves {rec['n_curves']}  "
            f"raw sha256 {rec['raw_result_sha256'][:12]}...")
        say(f"      command as recorded: {rec['declared_command']}")
    say(f"budget (read from the contract): {budget['wall_clock_seconds_per_run']} s "
        f"per run, {budget['maximum_memory_gb']} GB, "
        f"{budget['maximum_runs']} runs, {budget['total_cpu_hours']} CPU-hours")
    say(f"git: HEAD {gitctx['head_commit'][:12]} branch {gitctx['branch']} "
        f"dirty={gitctx['dirty']}; origin/main {gitctx['origin_main'][:12]}; "
        f"merge-base {gitctx['merge_base_with_origin_main'][:12]} "
        f"(origin/main is an ancestor of HEAD: "
        f"{gitctx['merge_base_with_origin_main'] == gitctx['origin_main']})")

    say("\nCONFLICT-1 (declared BEFORE any measurement): " + CONFLICT_1["action_taken"])
    say(CONFLICT_1_SCOPE_NOTE)

    frozen = {
        "amendment": amend, "contract_seeds": seeds_rec, "density_grid": grid,
        "z": zrec, "reference_runs": refruns, "budget": budget,
        "git": gitctx, "conflict_1": CONFLICT_1,
    }
    checkpoint("frozen-parameters.json", frozen)

    wall_cap = float(budget["wall_clock_seconds_per_run"])
    mem_cap_bytes = float(budget["maximum_memory_gb"]) * (1024 ** 3)

    def elapsed() -> float:
        return time.time() - started

    def peak_rss_bytes() -> int:
        ru = resource.getrusage(resource.RUSAGE_SELF)
        return ru.ru_maxrss * (1024 if platform.system() == "Linux" else 1)

    # ------------------------------------------------------------------
    # 1. SR1, RUNS FIRST
    # ------------------------------------------------------------------
    say("\n--- 1. SR1 (C-NULLC-REPRODUCTION), as narrowed by change G1 ---")
    if not data["sources_agree_exactly"]:
        raise RuntimeError("the two committed p = 4001 runs disagree on rate_m3")
    say(f"p = 4001 rate_m3 read from {len(data['sources'])} committed runs, "
        f"vectors agree exactly: {data['sources_agree_exactly']}; class sizes "
        f"{data['class_sizes']}")
    pct_decimals = {"one": 1, "two": 2, "three": 3}[
        amend["sr1_pct_of_mean_published_precision_decimals"]]
    t0 = time.time()
    sr1_out = sr1_g1.run(data["groups"], seeds_rec["seeds"], published["rows"],
                         amend["sr1_median_p_abs_tolerance"], pct_decimals)
    sr1_out["wall_seconds"] = round(time.time() - t0, 3)
    sr1_out["published"] = published
    sr1_out["tolerance_provenance"] = (
        "READ from amendment v1 change G1 at run time "
        f"({amend['source_path']}, sha256 {amend['source_sha256'][:12]}...); "
        "adopted there from the version-1 run's executor-declared tolerance.")
    q1, q2 = sr1_out["Q1_delta_zero_median_p"], sr1_out["Q2_pct_of_mean_column"]
    say(f"Q1 median p at delta = 0: measured {q1['measured_median_p']!r} vs "
        f"published {q1['published_median_p']}, |diff| "
        f"{q1['absolute_difference']!r} <= {q1['tolerance']} -> "
        f"{q1['passes']}")
    say(f"Q2 pooled mean of rate_m3 = {q2['pooled_mean_of_rate_m3']!r}")
    for r in q2["rows"]:
        say(f"   delta {r['delta']}: measured {r['pct_of_mean_measured']!r} % "
            f"-> {r['pct_of_mean_measured_rounded']} % vs published "
            f"{r['pct_of_mean_published']} % -> {r['matches']}")
    say(f"Q2 rows matching: {q2['rows_matching']}/{q2['rows_total']} -> "
        f"{q2['passes']}")
    pw = sr1_out["power_at_delta_zero_recorded_not_gated"]
    say(f"power at delta = 0: measured {pw['measured']} vs published "
        f"{pw['published']} -- {pw['status']}")
    say(f"constructions run: {sr1_out['constructions_run']} "
        f"(change G1 forbids selecting one; none was executed)")
    sr1_pass = sr1_out["sr1_discharged_on_construction_free_quantities"]
    say(f"SR1 DISCHARGED ON THE CONSTRUCTION-FREE QUANTITIES: {sr1_pass}")
    say(f"SR1 wall seconds: {sr1_out['wall_seconds']}")
    checkpoint("nullc-reproduction.json", sr1_out)
    load("after SR1")

    sr3_families: dict[str, dict] = {}
    stopped_reason = None

    if not sr1_pass:
        say("\nSR1 FAILED. Under the contract's own stopping rule SR1 the run "
            "STOPS here and characterises nothing.")
        stopped_reason = "SR1 did not discharge; SR1 runs first and stops the run."
        events.append({"kind": "stopping_rule", "rule": "SR1",
                       "effect": "no characterisation was attempted"})
    else:
        # --------------------------------------------------------------
        # 2. THE SR3 v3 REFERENCE CHARACTERISATION
        # --------------------------------------------------------------
        say("\n--- 2. SR3 v3 REFERENCE CHARACTERISATION ---")
        rungs = sr3v3.rung_seed_sets(seeds_rec["seeds"], amend["seed_rungs"],
                                     amend["rung2_extension_seed_range"],
                                     amend["rung3_extension_seed_range"])
        say(f"rung seed sets: " + ", ".join(
            f"rung {r['rung']} n={len(r['seeds'])}" for r in rungs))
        fb_sizes = grid["factor_base_sizes"]
        T = grid["target_count_primary"]

        # ONE PRIME IS ONE FAMILY (amendment G2 family_scope_limit). The primes
        # with a declared SR3 reference run are taken in ascending order; the
        # order is frozen here, before any measurement.
        primes = sorted(int(k) for k in refruns["runs"])
        say(f"families (one prime each, never pooled, never a family across "
            f"primes): {primes}")

        for p in primes:
            fam_key = str(p)
            ref = refruns["runs"][fam_key]
            if elapsed() > wall_cap:
                events.append({
                    "kind": "budget_event", "rule": "SR6",
                    "what": f"wall-clock cap {wall_cap} s reached before the "
                            f"p = {p} family started",
                    "consequence": "recorded as not_measured; never a pass and "
                                   "never negative evidence (AGENTS.md rule 5)"})
                sr3_families[fam_key] = {"status": "not_measured",
                                         "reason": "budget event before start"}
                continue

            say(f"\n=== family: p = {p}, reference run {ref['run_id']} ===")
            load(f"before p={p} class selection")
            t_fam = time.time()
            sel = sr3v3.select_class(p)
            say(f"class selection (reference driver's own rule): trace "
                f"{sel['target_trace']}, order {sel['order']}, "
                f"{sel['n_curves']} curves")
            agree = (sel["target_trace"] == ref["trace"]
                     and sel["order"] == ref["order"]
                     and sel["n_curves"] == ref["n_curves"])
            say(f"  agrees with the reference run's own record "
                f"(trace {ref['trace']}, order {ref['order']}, "
                f"n_curves {ref['n_curves']}): {agree}")
            if not agree:
                raise RuntimeError(
                    f"class selection at p={p} disagrees with the reference "
                    f"run's record; refusing to characterise a different class")

            ref_seed = ref["declared_seed_as_read"]
            all_seeds = list(rungs[-1]["seeds"])
            if ref_seed not in all_seeds:
                all_seeds_plus = all_seeds + [ref_seed]
            else:
                all_seeds_plus = all_seeds
            say(f"  reference run's own declared seed: {ref_seed} "
                f"(in the rung seed sets: {ref_seed in all_seeds}) -- measured "
                f"in addition, because C-SELF-CONSISTENCY requires a faithful "
                f"re-measurement AT THE REFERENCE RUN'S OWN PARAMETERS")

            fam: dict = {
                "prime": p, "reference_run": ref, "class": {
                    k: v for k, v in sel.items() if k != "recs"},
                "T": T, "fb_sizes": fb_sizes,
                "sampler": ("exp_icinv.targets_uniform -- THE REFERENCE RUN'S "
                            "OWN SAMPLER; see CONFLICT-1"),
                "statistic": ("exp_icinv.binomial_null_verdict(...).ratio "
                              "(NULL-B variance ratio of the m = 3 decomposition "
                              "rate), called unmodified"),
                "rungs": [], "load_observations": [],
            }

            # ---- measurement, sharing the seed-independent sum sets ----
            say(f"  measuring {len(all_seeds_plus)} seeds x {len(fb_sizes)} rows "
                f"x {sel['n_curves']} curves, sum sets shared per (curve, row)")
            last = [time.time()]

            def progress(i, n):
                if time.time() - last[0] > 60:
                    last[0] = time.time()
                    say(f"    ... {i}/{n} curves, elapsed "
                        f"{time.time() - t_fam:.0f}s in this family")
                    load(f"p={p} during measurement, curve {i}/{n}")

            meas = sr3v3.measure(sel["recs"], fb_sizes, T, all_seeds_plus,
                                 progress=progress)
            say(f"  measurement wall seconds: {time.time() - t_fam:.1f}")
            load(f"after p={p} measurement")

            # ---- faithfulness of the shared path against the reference driver
            say("  verifying the shared-sum-set path against "
                "run_saturation.measure_at_density, called unmodified")
            checks = [ref_seed, rungs[0]["seeds"][0]]
            verif = [sr3v3.verify_against_reference_driver(
                sel["recs"], fb_sizes, T, s, meas) for s in checks]
            for v in verif:
                say(f"    seed {v['seed']}: all 13 rows exact: "
                    f"{v['all_rows_exact']}")
            if not all(v["all_rows_exact"] for v in verif):
                raise RuntimeError(
                    "the shared-sum-set path does not reproduce the reference "
                    "driver exactly; refusing to report a characterisation")
            fam["faithfulness_verification"] = verif

            cmp_committed = sr3v3.compare_with_committed(
                ref["rows"], meas, T, ref_seed)
            say(f"    re-measurement at the reference run's own seed reproduces "
                f"its committed rows exactly: {cmp_committed['all_rows_exact']}")
            fam["reference_run_reproduction"] = cmp_committed
            if not cmp_committed["all_rows_exact"]:
                deviations.append({
                    "id": f"DEV-refrepro-p{p}",
                    "what": ("the re-measurement at the reference run's own "
                             "declared seed does not reproduce its committed "
                             "per-row variance ratios BIT-EXACTLY"),
                    "max_relative_delta": cmp_committed["max_relative_delta"],
                    "recorded": ("as an observation, with every per-row delta. "
                                 "Nothing in this run gates on bit-exactness "
                                 "against the committed record: the committed "
                                 "run was executed on a different platform and "
                                 "Python build, and the contract specifies a "
                                 "re-measurement, not a byte comparison. The "
                                 "hits are integers and the class, factor "
                                 "bases, sampler, seed and target count are the "
                                 "reference run's own."),
                    "not_an_interpretation": ("this is a recorded observation, "
                                              "not a claim about the reference "
                                              "run, the platform, or any "
                                              "instrument")})

            # ---- rungs ----
            per_seed_rows = {fb: {s: sr3v3.row_statistic(meas["hits"][(fb, s)], T)
                                  for s in all_seeds_plus} for fb in fb_sizes}
            fam["mean_density_3V_over_order"] = {
                str(fb): sum(meas["densities"][fb]) / len(meas["densities"][fb])
                for fb in fb_sizes}
            fam["r_strata_composition"] = {
                str(r): meas["strata"].count(r) for r in sorted(set(meas["strata"]))}
            say(f"  r-strata composition of the class: "
                f"{fam['r_strata_composition']}")

            accepted = None
            prev_intervals = None
            for rung in rungs:
                if elapsed() > wall_cap:
                    events.append({
                        "kind": "budget_event", "rule": "SR6",
                        "what": f"wall-clock cap reached before rung "
                                f"{rung['rung']} of p = {p}",
                        "consequence": "rung recorded as not_measured"})
                    fam["rungs"].append({"rung": rung["rung"],
                                         "status": "not_measured",
                                         "reason": "budget event"})
                    break
                intervals = {}
                for fb in fb_sizes:
                    ratios = [per_seed_rows[fb][s]["variance_ratio"]
                              for s in rung["seeds"]]
                    iv = sr3v3.interval_for_rung(ratios, zrec["z"])
                    if iv["status"] == "computed":
                        pairs = list(zip(rung["seeds"], ratios))
                        iv["argmin_seed"] = min(pairs, key=lambda x: x[1])[0]
                        iv["argmax_seed"] = max(pairs, key=lambda x: x[1])[0]
                        iv["per_seed_ratios"] = {str(s): r for s, r in pairs}
                    iv["stratified_by_r_at_the_first_seed_of_this_rung"] = \
                        sr3v3.stratified_row(
                            meas["hits"][(fb, rung["seeds"][0])],
                            meas["strata"], T)
                    intervals[fb] = iv
                bad = [fb for fb, iv in intervals.items()
                       if iv["status"] != "computed"]
                if bad:
                    raise RuntimeError(
                        f"the variance ratio was not finite at rows {bad} of "
                        f"p={p} rung {rung['rung']}; this is an INVALID "
                        f"MEASUREMENT, not a result, and no interval is "
                        f"reported for a row whose statistic is degenerate")
                rung_rec = {"rung": rung["rung"], "n_seeds": len(rung["seeds"]),
                            "seeds": rung["seeds"], "status": "computed",
                            "intervals": {str(k): v for k, v in intervals.items()}}
                if prev_intervals is not None:
                    stab = sr3v3.stability_check(
                        prev_intervals, intervals,
                        amend["stability_relative_half_width_pct"])
                    rung_rec["stability_vs_previous_rung"] = stab
                    say(f"  rung {rung['rung']} (n={len(rung['seeds'])}): "
                        f"half-width stability vs rung {rung['rung']-1}: "
                        f"met at every row = {stab['met_at_every_row']}"
                        + ("" if stab["met_at_every_row"]
                           else f"; rows failing {stab['rows_failing']}"))
                    if stab["met_at_every_row"] and accepted is None:
                        accepted = rung_rec
                else:
                    say(f"  rung {rung['rung']} (n={len(rung['seeds'])}): "
                        f"first rung, no previous rung to compare against")
                for fb in fb_sizes:
                    iv = intervals[fb]
                    say(f"     fb={fb:3d} mean={iv['mean']:.6f} "
                        f"sd={iv['sd_sample_n_minus_1']:.6f} "
                        f"half={iv['half_width']:.6f} "
                        f"[{iv['interval_low']:.6f}, {iv['interval_high']:.6f}] "
                        f"min={iv['min_per_seed_ratio']:.6f}@"
                        f"{iv['argmin_seed']} max={iv['max_per_seed_ratio']:.6f}@"
                        f"{iv['argmax_seed']}")
                fam["rungs"].append(rung_rec)
                checkpoint(f"sr3v3-family-p{p}.json", fam)
                prev_intervals = intervals
                if accepted is not None:
                    say(f"  E3 STABILITY RULE MET AT RUNG {rung['rung']}: the "
                        f"characterisation stops at this rung, which is the "
                        f"declared stopping point.")
                    break
                load(f"after p={p} rung {rung['rung']}")

            fam["accepted_rung"] = (accepted["rung"] if accepted else None)
            if accepted is None:
                reached = [r["rung"] for r in fam["rungs"]
                           if r.get("status") == "computed"]
                fam["interval_stabilised"] = False
                fam["F4"] = {
                    "fired": True,
                    "statement": ("E3: the interval half-width did not change by "
                                  "less than the declared relative threshold at "
                                  "every row at any rung reached "
                                  f"(rungs reached: {reached}). Under E3 the "
                                  "interval HAS NOT STABILISED, HEUR-INSTR-2 is "
                                  "not validated at those seed counts, "
                                  "falsification criterion F4 fires, THE WORK "
                                  "STOPS and the Coordinator is told. The "
                                  "interval is NOT widened and the coverage is "
                                  "NOT changed."),
                }
                say(f"  E3 NOT MET AT ANY RUNG REACHED. F4 fires for p = {p}. "
                    f"The interval is not widened and nothing is gated with it.")
                fam["self_consistency"] = {
                    "status": "not_evaluated",
                    "reason": ("E3 was not met, so no interval of this family is "
                               "accepted; evaluating self-consistency against a "
                               "non-accepted interval would be gating with an "
                               "interval the protocol does not accept."),
                }
            else:
                fam["interval_stabilised"] = True
                fam["F4"] = {"fired": False}
                # ---- C-SELF-CONSISTENCY at the accepted rung ----
                sc_rows = []
                for fb in fb_sizes:
                    iv = accepted["intervals"][str(fb)]
                    vr = per_seed_rows[fb][ref_seed]["variance_ratio"]
                    inside = iv["interval_low"] <= vr <= iv["interval_high"]
                    cvr = ref["rows"][fb]
                    sc_rows.append({
                        "fb_size": fb,
                        "faithful_re_measurement_variance_ratio": vr,
                        "committed_reference_variance_ratio": cvr,
                        "interval_low": iv["interval_low"],
                        "interval_high": iv["interval_high"],
                        "inside": bool(inside),
                        "committed_reference_inside_reported_not_gated":
                            bool(iv["interval_low"] <= cvr <= iv["interval_high"]),
                    })
                sc_pass = all(r["inside"] for r in sc_rows)
                fam["self_consistency"] = {
                    "status": "evaluated",
                    "rung": accepted["rung"],
                    "seed": ref_seed,
                    "what_was_compared": (
                        "a faithful re-measurement of the reference run at ITS "
                        "OWN parameters and its own declared seed, against the "
                        "row intervals of this family's accepted rung"),
                    "rows": sc_rows,
                    "rows_outside": [r["fb_size"] for r in sc_rows
                                     if not r["inside"]],
                    "passes": bool(sc_pass),
                    "no_widening_rule": (
                        "SR4 is ABSOLUTE. On a failure the interval is NOT "
                        "widened, the coverage is NOT changed, nothing is gated "
                        "with it, and the Coordinator is told."),
                }
                say(f"  C-SELF-CONSISTENCY at rung {accepted['rung']}: inside at "
                    f"{sum(1 for r in sc_rows if r['inside'])}/{len(sc_rows)} "
                    f"rows -> passes = {sc_pass}")
                for r in sc_rows:
                    say(f"     fb={r['fb_size']:3d} re-measured "
                        f"{r['faithful_re_measurement_variance_ratio']:.6f} in "
                        f"[{r['interval_low']:.6f}, {r['interval_high']:.6f}] -> "
                        f"{r['inside']}")
                if not sc_pass:
                    say("  SR4 FIRES: the self-consistency check failed. The "
                        "interval is NOT widened; the work STOPS and the "
                        "Coordinator is told. Reporting this failure IS the "
                        "successful completion of this gate.")

            fam["family_wall_seconds"] = round(time.time() - t_fam, 3)
            fam["peak_rss_bytes_after_family"] = peak_rss_bytes()
            sr3_families[fam_key] = fam
            checkpoint(f"sr3v3-family-p{p}.json", fam)
            load(f"after p={p} family")

            if peak_rss_bytes() > mem_cap_bytes:
                events.append({"kind": "budget_event", "rule": "SR6",
                               "what": "memory cap exceeded",
                               "peak_rss_bytes": peak_rss_bytes()})
                break

            # SR4: a failed self-consistency check stops the work.
            sc = fam.get("self_consistency", {})
            if sc.get("status") == "evaluated" and not sc.get("passes"):
                stopped_reason = (
                    f"SR4: the C-SELF-CONSISTENCY check failed at p = {p}. The "
                    f"work stops, the interval is not widened, and the "
                    f"Coordinator is told.")
                events.append({"kind": "stopping_rule", "rule": "SR4",
                               "prime": p, "effect": "characterisation stopped"})
                break
            if fam.get("F4", {}).get("fired"):
                stopped_reason = (
                    f"F4/E3: the interval did not stabilise at p = {p}. The work "
                    f"stops; the interval is not widened and the coverage is not "
                    f"changed.")
                events.append({"kind": "stopping_rule", "rule": "E3/F4",
                               "prime": p, "effect": "characterisation stopped"})
                break

        primes_not_reached = [p for p in primes if str(p) not in sr3_families]
        for p in primes_not_reached:
            sr3_families[str(p)] = {
                "status": "not_measured",
                "reason": (stopped_reason or "not reached"),
                "blocks": ["the SR3 v3 gate of EXP-ICINV-4d33aa at this prime is "
                           "not evaluable from this run"],
            }

    load("end")
    finished = time.time()
    ru = resource.getrusage(resource.RUSAGE_SELF)
    stdout_text = "\n".join(log_lines)

    # ------------------------------------------------------------------
    # 3. the run record
    # ------------------------------------------------------------------
    families_summary = {}
    for k, f in sr3_families.items():
        if f.get("status") == "not_measured":
            families_summary[k] = {"status": "not_measured",
                                   "reason": f.get("reason")}
            continue
        families_summary[k] = {
            "status": "measured",
            "accepted_rung": f.get("accepted_rung"),
            "interval_stabilised": f.get("interval_stabilised"),
            "self_consistency_passes":
                f.get("self_consistency", {}).get("passes"),
            "self_consistency_rows_outside":
                f.get("self_consistency", {}).get("rows_outside"),
            "F4_fired": f.get("F4", {}).get("fired"),
            "reference_run_id": f["reference_run"]["run_id"],
            "reference_run_reproduced_exactly":
                f.get("reference_run_reproduction", {}).get("all_rows_exact"),
        }

    metrics = {
        "phase": "A",
        "contract_version": AMENDED_CONTRACT_VERSION,
        "sr1_Q1_measured_median_p": sr1_out["Q1_delta_zero_median_p"]["measured_median_p"],
        "sr1_Q1_absolute_difference": sr1_out["Q1_delta_zero_median_p"]["absolute_difference"],
        "sr1_Q1_passes": sr1_out["Q1_delta_zero_median_p"]["passes"],
        "sr1_Q2_rows_matching": sr1_out["Q2_pct_of_mean_column"]["rows_matching"],
        "sr1_Q2_passes": sr1_out["Q2_pct_of_mean_column"]["passes"],
        "sr1_discharged_on_construction_free_quantities": sr1_pass,
        "sr1_constructions_run": 0,
        "sr3v3_families": families_summary,
        "sr3v3_z_computed_at_run_time": zrec["z"],
        "phase_b_status": "not_run (SR2; blockers B1 and B2)",
        "wall_seconds": round(finished - started, 3),
        "cpu_seconds": round(ru.ru_utime + ru.ru_stime, 3),
        "peak_rss_bytes": peak_rss_bytes(),
        "budget_events": [e for e in events if e["kind"] == "budget_event"],
        "load_observations_recorded": len(LOAD_OBSERVATIONS),
    }

    all_measured = [f for f in sr3_families.values()
                    if f.get("status") != "not_measured"]
    valid = bool(sr1_pass and all_measured)
    invalid_reason = None
    if not valid:
        invalid_reason = (stopped_reason or
                          "SR1 did not discharge, so nothing was characterised")

    result = runner.RunResult(
        run_suffix=args.run_suffix,
        curve_id=("TOY: committed p=4001 four-class set (SR1) and the SR3 v3 "
                  "reference classes " + ", ".join(
                      f"p={k} trace={v['class']['target_trace']} "
                      f"n={v['class']['n_curves']}"
                      for k, v in sorted(sr3_families.items())
                      if v.get("status") != "not_measured")),
        seed=seeds_rec["seeds"][0],
        parameters={
            "task_id": TASK_ID, "goal_id": GOAL_ID, "batch_id": BATCH_ID,
            "contract_version": AMENDED_CONTRACT_VERSION,
            "amendment": amend["source_path"],
            "amendment_sha256": amend["source_sha256"],
            "phase": "A",
            "seeds": seeds_rec["seeds"],
            "seed_rungs": amend["seed_rungs"],
            "density_rows": grid["factor_base_sizes"],
            "target_count": grid["target_count_primary"],
            "per_row_central_coverage": amend["per_row_central_coverage"],
            "estimator": "mean +- z*sd, z computed at run time from 519/520",
            "sampler": "the reference run's own (exp_icinv.targets_uniform); "
                       "see CONFLICT-1",
            "statistic_sr1": "harness.exp_icinv.permutation_null (NULL-C)",
            "statistic_sr3v3": "harness.exp_icinv.binomial_null_verdict ratio",
            "parallelism": "none (single-threaded, sequential)",
            "requested_policy": "executor-implementation",
        },
        metrics=metrics,
        certificate={"kind": "none",
                     "statement": {"why": ("pure measurement run: no "
                                           "discrete-log solve and no "
                                           "factor-base relation is claimed "
                                           "anywhere in this run")}},
        valid=valid,
        invalid_reason=invalid_reason,
        stdout=stdout_text,
        stderr="",
        raw={
            "sr1": sr1_out,
            "sr3v3_families": sr3_families,
            "frozen_parameters": frozen,
            "conflict_1": CONFLICT_1,
            "conflict_1_scope_note": CONFLICT_1_SCOPE_NOTE,
            "deviations": deviations,
            "events": events,
            "stopped_reason": stopped_reason,
            "host": {"platform": platform.platform(),
                     "cpu_count": os.cpu_count(),
                     "load_observations": LOAD_OBSERVATIONS},
            "inference_provenance": inference_provenance(),
            "detection_bound_table_recorded_for_phase_b": bounds,
            "superseded_band": band,
            "p4001_rate_m3_sources": data["sources"],
        },
    )

    status = "completed_valid" if valid else "completed_invalid"
    command = (f"PYTHONPATH=. timeout {int(wall_cap)} python3 -m "
               f"harness.exp_instr_36c8cf.phase_a_v2 "
               f"--run-suffix {args.run_suffix}")
    run_id = runner.write_run(EXP_ID, EXP_AREA, result, status=status,
                              command=command, started=started, finished=finished)
    run_dir = os.path.join(refvalues.REPO, "experiments", EXP_ID, "runs", run_id)

    def w(name, obj):
        with open(os.path.join(run_dir, name), "w", encoding="utf-8") as fh:
            json.dump(obj, fh, indent=2, sort_keys=True, default=str)

    w("nullc-reproduction.json", sr1_out)
    w("baseline-provenance.json", {
        "note": ("Every reference value used by this run was READ FROM ITS "
                 "COMMITTED RECORD AT RUN TIME and is bound by the sha256 "
                 "below. No reference value is transcribed into source at any "
                 "precision (EXP-ICINV-4d33aa amendment v2 change A4, "
                 "CORR-20260807-a24675). This includes every number the "
                 "amendment freezes and the interval's z, which is COMPUTED "
                 "from the frozen exact fraction 519/520 at run time."),
        "amendment": amend,
        "contract_seeds": seeds_rec,
        "density_grid_cited_from_the_contract_that_owns_it": grid,
        "sr3v3_reference_runs": refruns,
        "sr3v3_reference_run_ids": {
            k: f"{v['experiment_id']}/{v['run_id']}"
            for k, v in refruns["runs"].items()},
        "z": zrec,
        "nullc_published_profile": published,
        "detection_bound_table": bounds,
        "superseded_band_and_hull_slacks": band,
        "superseded_band_statement": (
            "The superseded [%.1f, %.1f] band was the OUTWARD-ROUNDED HULL of "
            "the committed rows it gated -- floor slack %s, ceiling slack %s, "
            "both read from the committed record at run time. That -- not a "
            "failure of the campaign's finding -- is why literal band "
            "membership is being replaced. The chosen replacement's cost is "
            "recorded in the execution report and in the amendment: the gate "
            "is less sensitive to a small genuine baseline regression, and a "
            "pass is NOT evidence of no regression below its detection floor."
            % (band["band_low"], band["band_high"], band["floor_slack"],
               band["ceiling_slack"])),
        "p4001_rate_m3_sources": data["sources"],
        "p4001_sources_agree_exactly": data["sources_agree_exactly"],
        "git": gitctx,
        "inference_provenance": inference_provenance(),
    })
    w("sr3v3-reference-sampling.json", {
        "phase": "A",
        "what_this_is": (
            "the per-density-row EMPIRICAL SAMPLING DISTRIBUTION of the "
            "variance-ratio statistic for the reference run, re-measured at the "
            "reference run's own frozen parameters across the declared seed "
            "set, with the declared central interval per row"),
        "coverage": {
            "per_row_central_coverage_fraction":
                amend["per_row_central_coverage_fraction"],
            "per_row_central_coverage": amend["per_row_central_coverage"],
            "family_wise_error_target": amend["family_wise_error_target"],
            "per_row_two_sided_alpha": amend["per_row_two_sided_alpha"],
            "realised_family_wise_error_as_declared":
                amend["realised_family_wise_error_as_declared"],
            "family_scope_limit": (
                "ONE PRIME'S THIRTEEN ROWS IS ONE FAMILY. It is not a family "
                "across primes; a joint multi-prime evaluation is not corrected "
                "by this declaration and would need its own amendment."),
        },
        "estimator": {
            "rule": "mean +- z * sd of the row's per-seed variance ratios",
            "sd": "sample standard deviation (n-1)",
            "z": zrec,
        },
        "families": sr3_families,
        "conflict_1": CONFLICT_1,
    })
    w("sr3v3-interval-stability.json", {
        "phase": "A",
        "control": "C-SEED-STABILITY",
        "rule": (f"E3: the characterisation may stop at a rung if the interval "
                 f"half-width changes by less than "
                 f"{amend['stability_relative_half_width_pct']}% relative to the "
                 f"previous rung at EVERY one of the "
                 f"{amend['number_of_density_rows_gated']} rows"),
        "seed_rungs": amend["seed_rungs"],
        "families": {k: {"accepted_rung": f.get("accepted_rung"),
                         "interval_stabilised": f.get("interval_stabilised"),
                         "F4": f.get("F4"),
                         "rungs": [{"rung": r.get("rung"),
                                    "n_seeds": r.get("n_seeds"),
                                    "status": r.get("status"),
                                    "half_widths": {
                                        fb: iv.get("half_width")
                                        for fb, iv in (r.get("intervals") or {}).items()},
                                    "stability_vs_previous_rung":
                                        r.get("stability_vs_previous_rung")}
                                   for r in f.get("rungs", [])]}
                     if f.get("status") != "not_measured" else f
                     for k, f in sr3_families.items()},
    })
    w("sr3v3-self-consistency.json", {
        "phase": "A",
        "control": "C-SELF-CONSISTENCY",
        "rule": ("a faithful re-measurement of the reference run at its own "
                 "frozen parameters, compared against its own accepted interval "
                 "at every row"),
        "no_widening_rule": (
            "SR4 IS ABSOLUTE. On a failure the interval is NOT widened, the "
            "coverage is NOT changed, nothing is gated with it, and the "
            "Coordinator is told. Reporting the failure IS the successful "
            "completion of this gate."),
        "families": {k: {"self_consistency": f.get("self_consistency"),
                         "reference_run_reproduction":
                             f.get("reference_run_reproduction"),
                         "faithfulness_verification":
                             f.get("faithfulness_verification")}
                     if f.get("status") != "not_measured" else f
                     for k, f in sr3_families.items()},
    })
    w("geometry-inputs.json", {
        "phase_a_geometry": {
            "what": ("the SR3 v3 reference characterisation runs at the "
                     "REFERENCE RUN'S OWN geometry, read from its record; it is "
                     "not a geometry of use of EXP-JINV-bd141d or "
                     "EXP-VOLC-9f5571 and is not offered as one"),
            "families": {k: {"class": f.get("class"),
                             "r_strata_composition": f.get("r_strata_composition"),
                             "mean_density_3V_over_order":
                                 f.get("mean_density_3V_over_order"),
                             "reference_run": f["reference_run"]["run_id"]}
                         for k, f in sr3_families.items()
                         if f.get("status") != "not_measured"},
            "sr1_geometry": {
                "what": "the four committed p = 4001 isogeny classes",
                "class_sizes": sr1_out["class_sizes"],
                "sources": [s["path"] for s in data["sources"]],
            },
        },
        "phase_b_geometry": {
            "status": "not_available",
            "reason": ("SR2: Stage 1 of EXP-JINV-bd141d and EXP-VOLC-9f5571 has "
                       "not emitted the real family construction, class census, "
                       "per-level vertex counts or Velu volcano. Substituting an "
                       "assumed geometry is an invalidation rule of this "
                       "contract."),
        },
    })

    phase_b_not_measured = {
        "status": "not_measured", "phase": "B",
        "reason": ("PHASE A ONLY was dispatched. SR2 forbids running any "
                   "geometry-specific control before Stage 1 of EXP-JINV-bd141d "
                   "and EXP-VOLC-9f5571 has emitted the real geometry, and "
                   "amendment v1 names two live blockers that leave those cells "
                   "unexecutable even then."),
        "blockers": {
            "B1": ("the T5 walk-kernel bias ladder is not declared: the "
                   "parameterisation is undefined and the Velu-constructed "
                   "107-volcano does not exist yet. The T5 walk cell is "
                   "not_measured and BLOCKS the T5 reachability conclusion of "
                   "EXP-VOLC-9f5571."),
            "B2": ("the Phase B density rows are not declared: neither "
                   "EXP-JINV-bd141d nor EXP-VOLC-9f5571 declares a numeric "
                   "density grid, so every per-density-row Phase B cell is not "
                   "even ENUMERABLE. Every arm verdict of both contracts is "
                   "BLOCKED under GOAL-ENDO-001 criterion C4."),
        },
        "an_unmeasured_control_is_not_a_passed_control": True,
    }
    for name in ("detection-floors.json", "false-positive-rates.json",
                 "pseudo-crater-control.json", "arbitrary-halves-control.json",
                 "label-permutation-control.json", "nuisance-direction.json",
                 "nullc-matched-order-recharacterisation.json"):
        w(name, phase_b_not_measured)

    w("cell-coverage.json", {
        "phase_a_cells": [
            {"cell": "SR1 / C-NULLC-REPRODUCTION / NULL-C / committed p=4001 "
                     "four-class geometry / Q1 delta = 0 median p",
             "status": "measured",
             "measured": sr1_out["Q1_delta_zero_median_p"]},
            {"cell": "SR1 / C-NULLC-REPRODUCTION / NULL-C / committed p=4001 "
                     "four-class geometry / Q2 'as % of mean' column",
             "status": "measured",
             "measured": {"rows_matching": sr1_out["Q2_pct_of_mean_column"]["rows_matching"],
                          "rows_total": sr1_out["Q2_pct_of_mean_column"]["rows_total"],
                          "passes": sr1_out["Q2_pct_of_mean_column"]["passes"]}},
            {"cell": "SR1 / NULL-C published delta > 0 rows",
             "status": "permanently_unreproducible",
             "reason": ("amendment v1 change G1: the generating construction was "
                        "never recorded. Removed from the gate; no construction "
                        "is selected as canonical."),
             "blocks": []},
        ] + [
            {"cell": f"SR3 v3 reference characterisation / NULL-B variance ratio "
                     f"/ reference run {f['reference_run']['run_id']} geometry "
                     f"(p={k}) / all {len(f['fb_sizes'])} density rows at "
                     f"T={f['T']}",
             "status": "measured",
             "accepted_rung": f.get("accepted_rung"),
             "self_consistency_passes": f.get("self_consistency", {}).get("passes"),
             "F4_fired": f.get("F4", {}).get("fired")}
            if f.get("status") != "not_measured" else
            {"cell": f"SR3 v3 reference characterisation / p={k}",
             "status": "not_measured", "reason": f.get("reason"),
             "blocks": ["the SR3 v3 gate of EXP-ICINV-4d33aa at this prime"]}
            for k, f in sorted(sr3_families.items())
        ],
        "phase_b_cells": {
            "status": "not_enumerable",
            "reason": ("the (statistic, geometry, density row) cells cannot be "
                       "ENUMERATED: Stage 1 of EXP-JINV-bd141d and "
                       "EXP-VOLC-9f5571 has not emitted the real geometry, and "
                       "blocker B2 records that neither contract declares a "
                       "numeric density grid."),
            "blocks": ["every arm verdict of EXP-JINV-bd141d",
                       "every arm verdict of EXP-VOLC-9f5571",
                       "the T5 reachability conclusion of EXP-VOLC-9f5571 (B1)"],
        },
        "primes_with_no_sr3v3_reference_run": {
            "primes_required_by_EXP-ICINV-4d33aa": grid["primes_required"],
            "primes_with_a_declared_reference_run":
                refruns["baseline_primes_declared_by_that_module"],
            "consequence": ("a prime with no declared SR3 reference run is not "
                            "characterised here and no interval exists for it; "
                            "that is recorded, not filled in."),
        },
        "an_unmeasured_control_is_not_a_passed_control": True,
    })
    w("inference-provenance.json", inference_provenance())
    w("load-observations.json", {
        "note": ("ONLY VALUES ACTUALLY OBSERVED BY os.getloadavg() INSIDE THIS "
                 "RUN. CORR-20260810-7cf0e9 was issued in this batch for an "
                 "execution report quoting a load that appeared in no artifact."),
        "observations": LOAD_OBSERVATIONS,
    })
    w("conflict-1.json", CONFLICT_1)

    print(f"\nrun record: {run_dir}")
    print(f"staging (incremental checkpoints): {staging}")
    return 0


if __name__ == "__main__":
    sys.exit(main())

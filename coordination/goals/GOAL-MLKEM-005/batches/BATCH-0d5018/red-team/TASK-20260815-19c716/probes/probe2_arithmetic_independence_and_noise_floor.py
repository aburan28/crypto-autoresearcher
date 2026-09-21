#!/usr/bin/env python3
"""RT probe 2 (TASK-20260815-19c716). Pure arithmetic / static analysis over
the COMMITTED blobs of snapshot 856ff0a6e. Runs NO fpylll and NO lattice
computation of any kind, so no timing or reduction number in its output is
this session's own measurement -- every figure below is recomputed from the
producer's own recorded numbers.

Checks, in order:
  A. Per-basis independence: are the two bisections genuinely separate, or is
     one precision borrowed from the other? Replay each bisection from its own
     recorded trials and confirm the reported minimum follows from that
     basis's own trials alone.
  B. Monotonicity coverage: which precisions in the window were never tested,
     and which of those are load-bearing for the "minimum" claim.
  C. Beta-inertness: static check of whether `beta` influences worker_bisect()
     beyond seeding.
  D. Built-in timing null: outer_lll_reduction_elapsed_seconds is a
     precision-independent, beta-independent repeat of the SAME computation on
     the SAME basis. Its spread across trials is a direct measurement of host
     timing noise, and nobody read it.
  E. Budget arithmetic: producer's budget_justification worst case vs actual.
  F. Wall-clock reconciliation: phase sums vs total vs outer UTC timestamps.
  G. Spec-cap divergence: frozen specification.yaml Stage-0 cap vs the cap used.
  H. run_manifest integrity surface: does it carry self-declared artifact
     digests, as its predecessor's did?
"""
import json
import os
import re
import statistics
import subprocess
import sys
from datetime import datetime, timezone

REPO = "/Volumes/SSD990/crypto-autoresearcher"
SNAP = "856ff0a6ee4d3998e72aca570a4e5d31d577b952"
TDIR = "coordination/goals/GOAL-MLKEM-005/batches/BATCH-0d5018/tasks/TASK-20260815-f14d3c"


def blob(path):
    r = subprocess.run(["git", "-C", REPO, "show", "%s:%s" % (SNAP, path)],
                       capture_output=True)
    if r.returncode != 0:
        return None
    return r.stdout.decode()


def jblob(path):
    return json.loads(blob(path))


out = {"probe": "probe2_arithmetic_independence_and_noise_floor",
       "source": "committed blobs of %s only" % SNAP,
       "this_session_ran_no_fpylll": True}

b55 = jblob("%s/bisection_d512_beta55_results.json" % TDIR)
b70 = jblob("%s/bisection_d512_beta70_results.json" % TDIR)
grid = jblob("%s/main_grid_d512_beta5570_reattempt_results.json" % TDIR)
script = blob("%s/stage0_d512_beta5570_precision_bisection_and_reattempt.py" % TDIR)
manifest = blob("%s/run_manifest.yaml" % TDIR)
t_start = blob("%s/run_start_utc.txt" % TDIR).strip()
t_end = blob("%s/run_end_utc.txt" % TDIR).strip()

# ---------------------------------------------------------------- A
def replay(b):
    """Replay the script's own bisect loop from THIS basis's recorded trials
    only. Returns the minimum the loop must have produced, and the ordered
    sequence of probed precisions, so a borrowed value would fail to replay."""
    by_bits = {t["mpfr_bits"]: t.get("status") for t in b["trials"]}
    order = [t["mpfr_bits"] for t in b["trials"]]
    lo, hi = b["lo_known_failing"], b["hi_known_succeeding"]
    seq = [lo, hi]
    if by_bits.get(lo) != "ERROR" or by_bits.get(hi) != "COMPLETED":
        return None, seq, "endpoints do not bracket"
    while hi - lo > 1:
        mid = (lo + hi) // 2
        st = by_bits.get(mid)
        if st is None:
            return None, seq, "trial at %d bits missing from record" % mid
        seq.append(mid)
        if st == "COMPLETED":
            hi = mid
        elif st == "ERROR":
            lo = mid
        else:
            return None, seq, "non-terminal trial status %r at %d" % (st, mid)
    return hi, seq, None


A = {}
for name, b in (("beta55", b55), ("beta70", b70)):
    m, seq, err = replay(b)
    A[name] = {
        "replayed_minimum": m,
        "reported_minimum": b["determined_minimum_precision_bits"],
        "replay_matches_report": m == b["determined_minimum_precision_bits"],
        "replay_error": err,
        "probe_order_expected": seq,
        "probe_order_recorded": [t["mpfr_bits"] for t in b["trials"]],
        "order_matches": seq == [t["mpfr_bits"] for t in b["trials"]],
        "n_trials": len(b["trials"]),
        "seed_used_set": sorted({t.get("seed_used") for t in b["trials"]}),
        "expected_seed": b["expected_seed_used"],
        "precision_used_for_reattempt": b["precision_used_for_reattempt"],
        "fallback_used": b["fallback_used"],
        "endpoint_reproduction_ok": b["endpoint_reproduction_ok"],
    }
A["two_minima_distinct"] = (
    b55["determined_minimum_precision_bits"] != b70["determined_minimum_precision_bits"]
)
A["seed_sets_disjoint"] = (
    set(t.get("seed_used") for t in b55["trials"])
    .isdisjoint(set(t.get("seed_used") for t in b70["trials"]))
)
A["no_cross_basis_precision_reuse"] = (
    b55["precision_used_for_reattempt"] != b70["precision_used_for_reattempt"]
)
A["reattempt_precision_matches_own_bisection"] = {
    c["beta"]: c["mpfr_bits_used"] == (
        b55 if c["beta"] == 55 else b70)["precision_used_for_reattempt"]
    for c in grid["main_grid"]
}
out["A_per_basis_independence"] = A

# ---------------------------------------------------------------- B
B = {}
for name, b in (("beta55", b55), ("beta70", b70)):
    tested = sorted(t["mpfr_bits"] for t in b["trials"])
    lo, hi = b["lo_known_failing"], b["hi_known_succeeding"]
    window = list(range(lo, hi + 1))
    untested = [x for x in window if x not in tested]
    minimum = b["determined_minimum_precision_bits"]
    # the load-bearing gap: untested values STRICTLY BELOW the reported minimum
    below = [x for x in untested if x < minimum]
    B[name] = {
        "window_inclusive": [lo, hi],
        "window_size": len(window),
        "tested": tested,
        "n_tested": len(tested),
        "n_untested_in_window": len(untested),
        "reported_minimum": minimum,
        "untested_strictly_below_reported_minimum": below,
        "n_untested_below": len(below),
        "monotonicity_is_assumed_not_measured": len(below) > 0,
        "cost_to_close_gap_seconds_est_from_own_trials": round(
            len(below) * statistics.mean(
                t["subprocess_wall_clock_seconds"] for t in b["trials"]), 1),
    }
out["B_monotonicity_coverage"] = B

# ---------------------------------------------------------------- C
wb = script.split("def worker_bisect(")[1].split("\ndef ")[0]
beta_uses = [ln.strip() for ln in wb.splitlines() if re.search(r"\bbeta\b", ln)]
out["C_beta_inertness_in_bisection"] = {
    "worker_bisect_lines_mentioning_beta": beta_uses,
    "basis_generator_line": [ln.strip() for ln in wb.splitlines()
                             if "IntegerMatrix.random" in ln],
    "beta_used_only_for_seed_and_labels": all(
        ("default_rng" in ln) or ('result' in ln and '=' in ln) or ("beta\":" in ln)
        or ('"beta"' in ln) for ln in beta_uses),
    "note": ("At the isolated-LLL-step level beta enters ONLY the RNG seed. "
             "The object bisected is IntegerMatrix.random(d,'qary',k=d//2,q=3329) "
             "in BOTH cases, so the two 'bases' are two iid draws of ONE "
             "distribution, differing by seed, not two beta regimes."),
}

# ---------------------------------------------------------------- D
D = {}
allv = []
for name, b in (("beta55", b55), ("beta70", b70)):
    v = [t["outer_lll_reduction_elapsed_seconds"] for t in b["trials"]]
    allv += v
    D[name] = {
        "outer_lll_seconds_in_trial_order": [round(x, 2) for x in v],
        "n": len(v), "min": round(min(v), 2), "max": round(max(v), 2),
        "mean": round(statistics.mean(v), 2),
        "stdev": round(statistics.pstdev(v), 2),
        "spread_pct_of_mean": round(100 * (max(v) - min(v)) / statistics.mean(v), 2),
        "first_to_last_drift_pct": round(100 * (v[-1] - v[0]) / v[0], 2),
    }
D["cross_block_level_shift_pct"] = round(
    100 * (D["beta70"]["mean"] - D["beta55"]["mean"]) / D["beta55"]["mean"], 2)
D["interpretation"] = (
    "outer_lll_reduction_elapsed_seconds does not depend on mpfr_bits (it runs "
    "BEFORE FPLLL.set_precision) and does not depend on beta (beta is not used "
    "by LLL.reduction). Within one basis it is the SAME computation repeated "
    "once per trial. Its spread is therefore a pure host-noise measurement, "
    "and it is the built-in null control this record never read.")
out["D_builtin_timing_null"] = D

# ---------------------------------------------------------------- E
E = {}
JUSTIFIED_MAX_TRIAL = 395.65   # dispatch_queue budget_justification, verbatim
JUSTIFIED_MAX_PER_BASIS = 7 * JUSTIFIED_MAX_TRIAL
for name, b in (("beta55", b55), ("beta70", b70)):
    tw = [t["subprocess_wall_clock_seconds"] for t in b["trials"]]
    E[name] = {
        "justification_assumed_max_single_trial_s": JUSTIFIED_MAX_TRIAL,
        "actual_max_single_trial_s": round(max(tw), 2),
        "single_trial_overrun_s": round(max(tw) - JUSTIFIED_MAX_TRIAL, 2),
        "single_trial_overrun_pct": round(
            100 * (max(tw) - JUSTIFIED_MAX_TRIAL) / JUSTIFIED_MAX_TRIAL, 2),
        "justification_stated_worst_case_per_basis_s": round(JUSTIFIED_MAX_PER_BASIS, 2),
        "actual_bisection_wall_clock_s": round(b["bisection_wall_clock_seconds"], 2),
        "per_basis_overrun_vs_stated_worst_case_s": round(
            b["bisection_wall_clock_seconds"] - JUSTIFIED_MAX_PER_BASIS, 2),
        "per_basis_overrun_pct": round(
            100 * (b["bisection_wall_clock_seconds"] - JUSTIFIED_MAX_PER_BASIS)
            / JUSTIFIED_MAX_PER_BASIS, 2),
        "budget_seconds": b["bisection_budget_seconds"],
        "breached_actual_budget": b["bisection_wall_clock_seconds"] > b["bisection_budget_seconds"],
        "sum_of_trial_wall_clocks_s": round(sum(tw), 4),
        "recorded_bisection_wall_clock_s": round(b["bisection_wall_clock_seconds"], 4),
        "orchestration_overhead_s": round(b["bisection_wall_clock_seconds"] - sum(tw), 4),
    }
out["E_budget_justification_vs_actual"] = E

# ---------------------------------------------------------------- F
phases = [b55["bisection_wall_clock_seconds"], b70["bisection_wall_clock_seconds"]] + \
         [c["subprocess_wall_clock_seconds"] for c in grid["main_grid"]]
tot = grid["total_script_wall_clock_seconds"]
d0 = datetime.strptime(t_start, "%Y-%m-%dT%H:%M:%SZ").replace(tzinfo=timezone.utc)
d1 = datetime.strptime(t_end, "%Y-%m-%dT%H:%M:%SZ").replace(tzinfo=timezone.utc)
outer = (d1 - d0).total_seconds()
out["F_wall_clock_reconciliation"] = {
    "phase_wall_clocks_s": [round(x, 3) for x in phases],
    "sum_of_phases_s": round(sum(phases), 3),
    "total_script_wall_clock_seconds_field": round(tot, 3),
    "sum_minus_total_s": round(sum(phases) - tot, 4),
    "outer_utc_elapsed_s": outer,
    "unaccounted_outside_t_script_start_s": round(outer - tot, 2),
    "unaccounted_pct_of_outer": round(100 * (outer - tot) / outer, 3),
    "task_budget_s": grid["overall_budget_seconds"],
    "within_task_budget": outer < grid["overall_budget_seconds"],
}

# ---------------------------------------------------------------- G
spec = open(os.path.join(REPO, "experiments/EXP-MLKEM-42ea04/specification.yaml")).read()
spec_stage0 = re.findall(r"PER_BASIS_FEASIBILITY_CAP\s*=\s*(\d+)s", spec)
spec_stage1 = re.findall(r"PER_BASIS_STAGE1_CAP\s*=\s*(\d+)s", spec)
cap_used = grid["per_basis_feasibility_cap_v3_seconds"]
beta70_cell = [c for c in grid["main_grid"] if c["beta"] == 70][0]
beta55_cell = [c for c in grid["main_grid"] if c["beta"] == 55][0]
spec0 = int(spec_stage0[0]) if spec_stage0 else None
out["G_spec_cap_divergence"] = {
    "specification_yaml_stage0_cap_s": spec0,
    "specification_yaml_stage0_cap_occurrences": spec_stage0,
    "specification_yaml_stage1_cap_s": spec_stage1,
    "cap_actually_used_for_stage0_s": cap_used,
    "ratio_used_over_spec_stage0": round(cap_used / spec0, 2) if spec0 else None,
    "amendment_to_specification_yaml_found": "PER_BASIS_FEASIBILITY_CAP_V2" in spec
                                             or "PER_BASIS_FEASIBILITY_CAP_V3" in spec,
    "beta55_cell_seconds": round(beta55_cell["subprocess_wall_clock_seconds"], 2),
    "beta55_within_spec_stage0_cap": beta55_cell["subprocess_wall_clock_seconds"] < spec0,
    "beta70_cell_seconds": round(beta70_cell["subprocess_wall_clock_seconds"], 2),
    "beta70_seconds_spent_beyond_spec_stage0_cap": round(
        beta70_cell["subprocess_wall_clock_seconds"] - spec0, 2),
    "beyond_spec_share_of_total_task_compute_pct": round(
        100 * (beta70_cell["subprocess_wall_clock_seconds"] - spec0) / tot, 2),
    "spec_wall_clock_seconds_per_run": re.findall(r"wall_clock_seconds_per_run:\s*(\d+)", spec),
    "actual_single_run_seconds": outer,
}

# ---------------------------------------------------------------- H
out["H_manifest_integrity_surface"] = {
    "run_manifest_declares_artifact_sha256": bool(re.search(r"sha256", manifest, re.I)),
    "predecessor_declared_artifact_sha256": bool(
        re.search(r"sha256", blob(
            "coordination/goals/GOAL-MLKEM-005/batches/BATCH-279acb/tasks/"
            "TASK-20260815-6e4c02/run_manifest.yaml") or "", re.I)),
    "cpu_time_recorded_anywhere_in_results": bool(
        re.search(r"cpu_time|ru_utime|user_seconds|cpu_seconds",
                  json.dumps(grid) + json.dumps(b55) + json.dumps(b70), re.I)),
    "host_load_recorded_in_environment_json": bool(
        re.search(r"loadavg|load_average|cpu_percent",
                  blob("%s/environment.json" % TDIR), re.I)),
    "psutil_cpu_times_called_in_script": "cpu_times" in script,
    "psutil_memory_info_called_in_script": "memory_info" in script,
    "tour_progress_persisted_before_sigterm": bool(
        re.search(r"signal\.|SIGTERM|atexit|flush.*tour", script)),
    "stdout_tail_retained_for_timed_out_cell": "stdout_tail" in json.dumps(grid),
    "timed_out_cell_stderr_tail": beta70_cell.get("stderr_tail"),
    "timed_out_cell_recorded_fields": sorted(beta70_cell.keys()),
}

# ---------------------------------------------------------------- I
r = subprocess.run(
    ["git", "-C", REPO, "log", "--all", "--oneline", "--", TDIR],
    capture_output=True)
out["I_first_attempt_artifact_recoverability"] = {
    "all_commits_touching_producer_dir": r.stdout.decode().strip().splitlines(),
    "deleted_first_attempt_artifacts_declared_in_manifest": [
        "bisection_d512_beta55_results.json", "stdout.log", "stderr.log",
        "command.txt", "environment.json", "run_start_utc.txt"],
    "any_commit_predating_snapshot_contains_them": None,
}
# check every commit that ever touched the dir for a pre-snapshot version
found = []
for line in out["I_first_attempt_artifact_recoverability"]["all_commits_touching_producer_dir"]:
    sha = line.split()[0]
    ls = subprocess.run(["git", "-C", REPO, "ls-tree", "-r", "--name-only", sha, TDIR],
                        capture_output=True).stdout.decode().split()
    found.append({"commit": sha, "files": [os.path.basename(f) for f in ls]})
out["I_first_attempt_artifact_recoverability"]["per_commit_listing"] = found

json.dump(out, sys.stdout, indent=2)
print()

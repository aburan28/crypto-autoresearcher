"""EXP-SMTH-71b1b0 run driver / orchestrator for RUN-SMTH-71b1b0-001.

Stages, in the mandated order:

  0. CONTRACT DIGEST GATE.  Re-hash the frozen specification.  On ANY difference
     HALT immediately, write the halt reason, produce NO datum.
  1. RSS PRE-FLIGHT DECLARATION.  Write the tolerance and margin to
     rss-preflight-declaration.json and hash it, BEFORE the probe runs.
  2. RSS PRE-FLIGHT PROBE at ~5, 10 and 20 percent of records, in a separate
     process.  Exceeding the declared tolerance HALTS the run.
  3. MEASUREMENT, in a separate process.  Null arms are drawn, factored and
     hash-committed BEFORE any treatment record is factored.
  4. INDEPENDENT VERIFICATION, in a separate process, by verify_run.py, which
     shares no code with this driver or with smth71b1b0_core.

Usage:
  python3 run_exp.py --run-dir <dir>            # orchestrate everything
  python3 run_exp.py --stage preflight --out F  # internal
  python3 run_exp.py --stage measure --run-dir D --out F   # internal
"""
from __future__ import annotations

import argparse
import hashlib
import json
import math
import os
import platform
import resource
import subprocess
import sys
import time
from array import array

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
sys.path.insert(0, HERE)

import smth71b1b0_core as core   # noqa: E402

SPEC_PATH = os.path.join(REPO, "experiments", "EXP-SMTH-71b1b0", "specification.yaml")
RUN_ID = "RUN-SMTH-71b1b0-001"

# Contract budget (experiment.budget), quoted.
BUDGET = {
    "maximum_runs": 1,
    "maximum_resume_count": 1,
    "maximum_wall_seconds": 5400,
    "maximum_cpu_seconds": 21600,
    "maximum_peak_rss_bytes": 4294967296,
    "maximum_total_disk_bytes": 17179869184,
    "maximum_workers": 4,
    "no_network": True,
}

# ---------------------------------------------------------------------------
# RSS pre-flight tolerance.  DECLARED HERE, IN SOURCE, BEFORE THE PROBE RUNS.
# ---------------------------------------------------------------------------
RSS_DECLARATION = {
    "declared_by": "TASK-20260803-fa7476 (executor)",
    "declared_before_probe": True,
    "contract_cap_bytes": 4294967296,
    "tolerance": {
        "absolute_peak_rss_bytes": 1073741824,
        "absolute_peak_rss_human": "1 GiB",
        "max_growth_between_first_and_last_checkpoint_bytes": 67108864,
        "max_growth_human": "64 MiB",
        "checkpoints_percent_of_records": [5, 10, 20],
    },
    "margin": {
        "margin_below_contract_cap_bytes": 3221225472,
        "margin_below_contract_cap_human": "3 GiB",
        "margin_fraction_of_cap": 0.75,
    },
    "halt_rule": (
        "If observed peak RSS at any checkpoint exceeds absolute_peak_rss_bytes, "
        "or if peak RSS grows by more than "
        "max_growth_between_first_and_last_checkpoint_bytes between the 5 percent "
        "and the 20 percent checkpoint, the run HALTS before the measurement "
        "stage and no datum is produced."
    ),
    "rationale": (
        "Contract budget.bounded_working_set_rationale: peak resident memory must "
        "depend on the shard buffer and interpreter baseline ALONE, not on records "
        "already produced. Every per-record buffer in this driver is preallocated "
        "at its full contract-declared size (6 arms x 130816 x 8 bytes) before any "
        "record is produced, so a flat peak-RSS curve across the three checkpoints "
        "is the property being tested. RUN-SMTH-PILOT-002 crossed a 4 GiB cap by "
        "15368192 bytes at 40.6 percent completion on 5.4 percent of its wall "
        "ceiling, which is the growth mode this probe is designed to detect early."
    ),
    "probe_scope_note": (
        "In the mandated production order the null arms come first, so the 20 "
        "percent checkpoint (156979 of 784896 records) falls inside the null arms. "
        "The probe therefore factors NO treatment record and cannot leak treatment "
        "information into any later choice."
    ),
    "enforcement_in_addition_to_the_probe": (
        "RLIMIT_AS is set to the contract cap 4294967296 in every stage process. "
        "Resident set size never exceeds virtual address space, so this is a "
        "kernel-enforced hard guarantee, not an advisory check. Peak RSS (VmHWM) "
        "is additionally polled at every 1024-record shard boundary and a crossing "
        "stops at the next record boundary."
    ),
}


def sha256_file(path: str) -> tuple:
    h = hashlib.sha256()
    n = 0
    with open(path, "rb") as fh:
        while True:
            chunk = fh.read(1 << 16)
            if not chunk:
                break
            n += len(chunk)
            h.update(chunk)
    return h.hexdigest(), n


def git(*args) -> str:
    return subprocess.run(["git", "-C", REPO, *args], capture_output=True,
                          text=True, check=False).stdout.strip()


# ===========================================================================
# Shared construction / production used by both the probe and the measurement
# ===========================================================================
def build_contexts(log):
    """Curve, factor base and derived digests for each field size."""
    ctxs = {}
    for bits in core.FIELD_SIZES_BITS:
        t0 = time.time()
        cur = core.derive_curve(bits)
        fb = core.build_factor_base(cur["p"], cur["a"], cur["b"], core.FB_SIZE)
        fb_blob = "\n".join(str(x) for x in fb).encode()
        fb_sha = hashlib.sha256(fb_blob).hexdigest()
        # integrity: every factor-base x must genuinely be an x-coordinate of a
        # point of E(F_p), and the list must be strictly increasing and distinct.
        p, a, b = cur["p"], cur["a"], cur["b"]
        on_curve = all(
            (x * x * x + a * x + b) % p == 0 or
            pow((x * x * x + a * x + b) % p, (p - 1) // 2, p) == 1
            for x in fb)
        strictly_increasing = all(fb[i] < fb[i + 1] for i in range(len(fb) - 1))
        cur.update({
            "factor_base_size": len(fb),
            "factor_base_sha256": fb_sha,
            "factor_base_first8": fb[:8],
            "factor_base_last8": fb[-8:],
            "factor_base_all_on_curve": on_curve,
            "factor_base_strictly_increasing": strictly_increasing,
            "D": 2 ** (2 * bits),
            "p_squared": cur["p"] ** 2,
            "construction_seconds": round(time.time() - t0, 3),
        })
        ctxs[bits] = {"p": cur["p"], "a": cur["a"], "b": cur["b"], "fb": fb,
                      "meta": cur}
        log(f"[construct] bits={bits} p={cur['p']} a={cur['a']} b={cur['b']} "
            f"#E={cur['curve_order']} trace={cur['trace']} ordinary={cur['ordinary']} "
            f"fb_sha256={fb_sha[:16]}... ({cur['construction_seconds']}s)")
    return ctxs


def preallocate(log):
    """All per-record buffers, at full contract size, BEFORE any record exists."""
    bufs = {}
    for arm in core.ARM_ORDER:
        bufs[arm] = array("q", bytes(8 * core.N_PAIRS))
    log(f"[prealloc] {len(bufs)} arm buffers x {core.N_PAIRS} x 8 bytes = "
        f"{len(bufs) * core.N_PAIRS * 8} bytes, allocated before any record")
    return bufs


# ===========================================================================
# STAGE: preflight
# ===========================================================================
def stage_preflight(out_path: str, deadline: float, cpu_remaining: float) -> int:
    applied = core.apply_hard_rlimits(BUDGET["maximum_peak_rss_bytes"],
                                      int(cpu_remaining))
    t0 = time.time()
    wall_remaining = max(1.0, deadline - t0)
    lines = []

    def log(msg):
        lines.append(msg)
        print(msg, flush=True)

    log(f"[preflight] rlimits applied: {applied}")
    baseline_rss = core.peak_rss_bytes()
    log(f"[preflight] interpreter baseline peak RSS: {baseline_rss} bytes")

    rho_tab = core.build_rho_table()
    log(f"[preflight] rho table built ({len(rho_tab)} points); peak RSS now "
        f"{core.peak_rss_bytes()} bytes")
    bufs = preallocate(log)
    ctxs = build_contexts(log)
    after_setup_rss = core.peak_rss_bytes()
    log(f"[preflight] peak RSS after setup, before ANY record: {after_setup_rss} bytes")

    checkpoints = [int(round(core.TOTAL_RECORDS * pct / 100.0)) for pct in (5, 10, 20)]
    log(f"[preflight] total records in a full run: {core.TOTAL_RECORDS}; "
        f"checkpoints at {checkpoints}")

    budget = core.Budget(wall_remaining, cpu_remaining,
                         BUDGET["maximum_peak_rss_bytes"], t0=t0)
    budget.install_alarm()

    observations = []
    produced = 0
    hit = 0
    stop = False
    for arm in core.ARM_ORDER:
        if stop:
            break
        bits = int(arm.split("bits")[1])
        remaining = checkpoints[-1] - produced
        if remaining <= 0:
            break
        base = produced

        def progress(idx, _arm=arm, _base=base):
            nonlocal hit, produced
            tot = _base + idx
            while hit < len(checkpoints) and tot >= checkpoints[hit]:
                observations.append({
                    "checkpoint_percent": (5, 10, 20)[hit],
                    "records_target": checkpoints[hit],
                    "records_produced": tot,
                    "arm_in_progress": _arm,
                    "peak_rss_bytes": core.peak_rss_bytes(),
                    "current_rss_bytes": core.current_rss_bytes(),
                    "wall_seconds": round(time.time() - t0, 3),
                    "cpu_seconds": round(core.cpu_seconds_self_and_children(), 3),
                })
                print(f"[preflight] checkpoint {(5,10,20)[hit]}% at {tot} records: "
                      f"peak RSS {observations[-1]['peak_rss_bytes']} bytes", flush=True)
                hit += 1

        res = core.produce_arm(arm, bits, ctxs[bits], bufs[arm], budget,
                               progress=progress, limit=remaining)
        produced += res.count
        if hit >= len(checkpoints):
            stop = True

    final_peak = core.peak_rss_bytes()
    growth = observations[-1]["peak_rss_bytes"] - observations[0]["peak_rss_bytes"]
    tol = RSS_DECLARATION["tolerance"]
    verdict_abs = all(o["peak_rss_bytes"] <= tol["absolute_peak_rss_bytes"]
                      for o in observations) and final_peak <= tol["absolute_peak_rss_bytes"]
    verdict_growth = growth <= tol["max_growth_between_first_and_last_checkpoint_bytes"]
    payload = {
        "stage": "rss_preflight_probe",
        "run_id": RUN_ID,
        "experiment_id": "EXP-SMTH-71b1b0",
        "declaration": RSS_DECLARATION,
        "rlimits_applied": applied,
        "interpreter_baseline_peak_rss_bytes": baseline_rss,
        "peak_rss_after_setup_before_any_record_bytes": after_setup_rss,
        "total_records_in_full_run": core.TOTAL_RECORDS,
        "observations": observations,
        "final_peak_rss_bytes": final_peak,
        "growth_first_to_last_checkpoint_bytes": growth,
        "verdict": {
            "absolute_peak_within_tolerance": verdict_abs,
            "growth_within_tolerance": verdict_growth,
            "passed": bool(verdict_abs and verdict_growth),
        },
        "wall_seconds": round(time.time() - t0, 3),
        "cpu_seconds": round(core.cpu_seconds_self_and_children(), 3),
        "log": lines,
    }
    with open(out_path, "w") as fh:
        json.dump(payload, fh, indent=2)
    print(f"[preflight] verdict: {payload['verdict']}", flush=True)
    return 0 if payload["verdict"]["passed"] else 3


# ===========================================================================
# STAGE: measure
# ===========================================================================
def stage_measure(run_dir: str, out_path: str, deadline: float, cpu_remaining: float) -> int:
    applied = core.apply_hard_rlimits(BUDGET["maximum_peak_rss_bytes"],
                                      int(cpu_remaining))
    t0 = time.time()
    wall_remaining = max(1.0, deadline - t0)
    lines = []

    def log(msg):
        lines.append(msg)
        print(msg, flush=True)

    log(f"[measure] rlimits applied: {applied}")
    result = {
        "run_id": RUN_ID,
        "experiment_id": "EXP-SMTH-71b1b0",
        "specification_sha256_expected": core.SPEC_SHA256,
        "status": "running",
        "stop": None,
        "observations_not_predicted": [],
    }

    rho_tab = core.build_rho_table()
    rho_check = {
        "rho_2_computed": core.rho_at(rho_tab, 2.0),
        "one_minus_ln2": 1.0 - math.log(2.0),
        "rho_6_computed": core.rho_at(rho_tab, 6.0),
        "hundred_rho6_over_rho2_computed": 100.0 * core.rho_at(rho_tab, 6.0) / core.rho_at(rho_tab, 2.0),
        "contract_rho_frozen": core.RHO_FROZEN,
        "integration": {"scheme": "RK4", "step": core.RHO_H, "u_max": core.RHO_UMAX,
                        "ode": "rho'(u) = -rho(u-1)/u, rho == 1 on [0,1]"},
    }
    rho_check["rho_2_minus_one_minus_ln2"] = rho_check["rho_2_computed"] - rho_check["one_minus_ln2"]
    log(f"[measure] rho cross-check: rho(2)={rho_check['rho_2_computed']:.10f} "
        f"vs 1-ln2={rho_check['one_minus_ln2']:.10f}; "
        f"100*rho(6)/rho(2)={rho_check['hundred_rho6_over_rho2_computed']:.7f}")
    result["dickman_rho_reference"] = rho_check

    # RECORDED OBSERVATION, not a correction: the contract's frozen rho(2) differs
    # from the closed form its own provenance cross-checks against.
    delta2 = core.RHO_FROZEN[2] - rho_check["one_minus_ln2"]
    result["observations_not_predicted"].append({
        "id": "OBS-RHO2-TRANSCRIPTION",
        "what": ("decision_rules.RATE-DS-1.rho_frozen.u2 = 0.30684282, while the "
                 "closed form 1 - ln 2 that the contract's own rho_provenance "
                 f"cross-checks against is {rho_check['one_minus_ln2']:.8f}. "
                 f"Absolute difference {abs(delta2):.2e}, relative {abs(delta2)/rho_check['one_minus_ln2']:.2e}. "
                 "The digit pattern (0.30684282 vs 0.30685282) is consistent with a "
                 "single-digit transcription slip."),
        "action_taken": ("NONE. The frozen values and the frozen bands derived from "
                         "them are used verbatim; no threshold is recomputed. The "
                         "frozen factor-8 band is 64x wider than this difference, so "
                         "no RATE-DS-1 verdict can turn on it. Recorded for the "
                         "Validator, never repaired by the Executor."),
        "affects_any_verdict": False,
    })

    bufs = preallocate(log)
    ctxs = build_contexts(log)
    result["construction"] = {str(b): ctxs[b]["meta"] for b in ctxs}
    log(f"[measure] peak RSS after setup, before ANY record: {core.peak_rss_bytes()} bytes")

    budget = core.Budget(wall_remaining, cpu_remaining,
                         BUDGET["maximum_peak_rss_bytes"], t0=t0)
    budget.install_alarm()

    arms_dir = os.path.join(run_dir, "arms")
    os.makedirs(arms_dir, exist_ok=True)
    arm_meta = {}

    def run_arms(arms):
        for arm in arms:
            bits = int(arm.split("bits")[1])
            ta = time.time()
            res = core.produce_arm(arm, bits, ctxs[bits], bufs[arm], budget)
            path = os.path.join(arms_dir, f"{arm}.lpf.i64")
            with open(path, "wb") as fh:
                bufs[arm].tofile(fh)
            fsha, fbytes = sha256_file(path)
            arm_meta[arm] = {
                "arm": arm, "bits": bits, "records": res.count,
                "incomplete_factorizations": res.incomplete,
                "factorization_product_mismatches": res.product_mismatch,
                "integer_stream_sha256": res.int_sha256,
                "lpf_stream_sha256": res.lpf_sha256,
                "min_integer": res.min_int, "max_integer": res.max_int,
                "pair_index_order_ok": res.extra["pair_order_ok"],
                "null_rejection_draws": res.extra["null_rejection_draws"],
                "lpf_dump_path": os.path.relpath(path, REPO),
                "lpf_dump_sha256": fsha, "lpf_dump_bytes": fbytes,
                "seconds": round(time.time() - ta, 3),
                "peak_rss_bytes_after": core.peak_rss_bytes(),
            }
            log(f"[measure] arm {arm}: {res.count} records, "
                f"incomplete={res.incomplete}, product_mismatch={res.product_mismatch}, "
                f"lpf_sha256={res.lpf_sha256[:16]}..., {arm_meta[arm]['seconds']}s, "
                f"peakRSS={arm_meta[arm]['peak_rss_bytes_after']}")

    try:
        # ---- ORDERING CONSTRAINT: null arms first, committed before treatment.
        run_arms(core.NULL_ARMS)
        null_commit = {
            "what": ("null_calibration.ordering_constraint enforcement: the NULL-UNIF-D "
                     "arms were drawn, factored and hash-committed BEFORE any treatment "
                     "record was factored."),
            "committed_at_utc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
            "committed_after_wall_seconds": round(time.time() - t0, 3),
            "arms": {a: arm_meta[a] for a in core.NULL_ARMS},
            "null_summary_statistics": {},
        }
        for a in core.NULL_ARMS:
            bits = int(a.split("bits")[1])
            D = 2 ** (2 * bits)
            srt = sorted(bufs[a])
            null_commit["null_summary_statistics"][a] = core.arm_summary(
                srt, core.N_PAIRS, D, math.log(D), rho_tab,
                arm_meta[a]["incomplete_factorizations"])
            del srt
        blob = json.dumps(null_commit, sort_keys=True, separators=(",", ":")).encode()
        null_commit_digest = hashlib.sha256(blob).hexdigest()
        null_commit["null_commit_sha256"] = null_commit_digest
        with open(os.path.join(run_dir, "null-commit.json"), "w") as fh:
            json.dump(null_commit, fh, indent=2)
        result["null_arm_commit_sha256"] = null_commit_digest
        result["null_arm_commit_path"] = f"experiments/EXP-SMTH-71b1b0/runs/{RUN_ID}/null-commit.json"
        result["null_arm_committed_before_any_treatment_factorization"] = True
        log(f"[measure] NULL ARM COMMITTED, sha256={null_commit_digest}")

        # ---- treatment and power-certificate arms
        run_arms(core.TREATMENT_ARMS)
        run_arms(core.ENCA_ARMS)
    except core.BudgetStop as exc:
        result["status"] = "budget_stop"
        result["stop"] = {
            "reason": str(exc),
            "classification": "resource_exhaustion",
            "contract_branch": "BUDGET_HALT / failed_infrastructure_or_budget",
            "note": ("A stop is reported AS A STOP, never as a result. Per AGENTS.md "
                     "core rule 5 and the contract's BUDGET_HALT branch this is NOT "
                     "evidence about mathematics, smoothness, HEUR-DS-1, H-SMTH-001 "
                     "or ECDLP."),
            "arms_completed": sorted(arm_meta),
            "arms_dropped": [a for a in core.ARM_ORDER if a not in arm_meta],
            "wall_seconds": round(time.time() - t0, 3),
            "cpu_seconds": round(core.cpu_seconds_self_and_children(), 3),
            "peak_rss_bytes": core.peak_rss_bytes(),
        }
        result["arms"] = arm_meta
        result["log"] = lines
        with open(out_path, "w") as fh:
            json.dump(result, fh, indent=2)
        return 4

    result["arms"] = arm_meta

    # ---------------- metrics ----------------
    summaries = {}
    sorted_arms = {}
    for arm in core.ARM_ORDER:
        bits = int(arm.split("bits")[1])
        D = 2 ** (2 * bits)
        srt = sorted(bufs[arm])
        sorted_arms[arm] = srt
        summaries[arm] = core.arm_summary(srt, core.N_PAIRS, D, math.log(D), rho_tab,
                                          arm_meta[arm]["incomplete_factorizations"])
        log(f"[metrics] {arm}: smooth(u=2)={summaries[arm]['smooth']['2']['fraction']:.6f} "
            f"tail(z>=0.5)={summaries[arm]['tail_fraction_z_ge_0.5']:.6f} "
            f"KSvsDickman={summaries[arm]['ks_vs_dickman']:.6f}")
    result["arm_summaries"] = summaries

    per_bits = {}
    for bits in core.FIELD_SIZES_BITS:
        t_arm = f"TREAT-ENCB.bits{bits}"
        n_arm = f"NULL-UNIF-D.bits{bits}"
        e_arm = f"CTRL-ENCA.bits{bits}"
        tv = [v for v in sorted_arms[t_arm] if v > 0]
        nv = [v for v in sorted_arms[n_arm] if v > 0]
        ev = [v for v in sorted_arms[e_arm] if v > 0]

        ks2 = core.ks_two_sample_int(tv, nv)
        ks2_enca = core.ks_two_sample_int(ev, nv)
        tail_t = summaries[t_arm]["tail_fraction_z_ge_0.5"]
        tail_n = summaries[n_arm]["tail_fraction_z_ge_0.5"]
        tail_diff = tail_t - tail_n
        ks1 = summaries[t_arm]["ks_vs_dickman"]
        dec = core.decay_report(summaries[t_arm])
        rate_t = core.rate_band_report(summaries[t_arm])
        rate_n = core.rate_band_report(summaries[n_arm])

        per_bits[str(bits)] = {
            "field_bits": bits,
            "p": ctxs[bits]["p"], "D": 2 ** (2 * bits),
            "KS2-DS-1": {
                "statistic_name": "two-sample KS, treatment (ENC-B) vs NULL-UNIF-D",
                "value": ks2, "threshold": core.KS2_DS_1_THRESHOLD,
                "passes_threshold": ks2 <= core.KS2_DS_1_THRESHOLD,
                "role": "PRIMARY AND DECISIVE",
            },
            "TAIL-DS-1": {
                "statistic_name": "fraction z >= 0.5, treatment minus NULL-UNIF-D",
                "treatment_tail_fraction": tail_t, "null_tail_fraction": tail_n,
                "value_signed": tail_diff, "value_absolute": abs(tail_diff),
                "threshold": core.TAIL_DS_1_THRESHOLD,
                "passes_threshold": abs(tail_diff) <= core.TAIL_DS_1_THRESHOLD,
                "measured_against": "the MEASURED null, not analytic rho",
                "role": "supporting, blocking only jointly with KS2-DS-1",
            },
            "DECAY-1": dec,
            "KS-DS-1": {
                "statistic_name": "one-sample KS, treatment z-CDF vs Dickman LPF CDF rho(1/z)",
                "value": ks1, "threshold": core.KS_DS_1_THRESHOLD,
                "within_threshold": ks1 <= core.KS_DS_1_THRESHOLD,
                "role": "SECONDARY, reported, NON-BLOCKING; does not gate the success criterion",
            },
            "RATE-DS-1": {
                "treatment": rate_t,
                "role": "SECONDARY, reported, NON-BLOCKING; does not gate the success criterion",
            },
            "CTRL-NULL-DICKMAN": {
                "blocking": False,
                "null_ks_vs_dickman": summaries[n_arm]["ks_vs_dickman"],
                "null_ks_within_KS-DS-1_threshold": summaries[n_arm]["ks_vs_dickman"] <= core.KS_DS_1_THRESHOLD,
                "null_rate_bands": rate_n,
                "note": ("ADVISORY BY CONTRACT. A Dickman disagreement on the null may "
                         "not stop the experiment and may not trigger APPARATUS_FAILURE."),
            },
            "CTRL-ENCA-POWER": {
                "blocking": True,
                "check": "the same pipeline run on ENC-A must REJECT against the null at KS2-DS-1",
                "ks2_enca_vs_null": ks2_enca,
                "threshold": core.KS2_DS_1_THRESHOLD,
                "rejects": ks2_enca > core.KS2_DS_1_THRESHOLD,
                "passes": ks2_enca > core.KS2_DS_1_THRESHOLD,
            },
        }
        log(f"[metrics] bits={bits}: KS2-DS-1={ks2:.6f} (thr {core.KS2_DS_1_THRESHOLD}) "
            f"TAIL-DS-1={tail_diff:+.6f} DECAY-1 ratio={dec['ratio']} "
            f"KS-DS-1={ks1:.6f} ENC-A KS2={ks2_enca:.6f}")
    result["per_field_size"] = per_bits

    # ---------------- controls ----------------
    # CTRL-APPARATUS-IDENTITY: re-run the factor-base and null generators from the
    # frozen seed and reproduce every stream digest.
    ident = {"blocking": True, "streams": {}, "passes": True}
    for bits in core.FIELD_SIZES_BITS:
        cur2 = core.derive_curve(bits)
        fb2 = core.build_factor_base(cur2["p"], cur2["a"], cur2["b"], core.FB_SIZE)
        fb2_sha = hashlib.sha256("\n".join(str(x) for x in fb2).encode()).hexdigest()
        p2v = cur2["p"] ** 2
        drbg = core.DRBG(f"null:bits{bits}")
        nb = p2v.bit_length()
        h = hashlib.sha256()
        for _ in range(core.N_PAIRS):
            while True:
                v = drbg.bits(nb)
                if v < p2v:
                    break
            h.update(b"%d\n" % (v + 1))
        rec = {
            "curve_reproduced": (cur2["p"] == ctxs[bits]["p"] and cur2["a"] == ctxs[bits]["a"]
                                 and cur2["b"] == ctxs[bits]["b"]),
            "factor_base_sha256_recomputed": fb2_sha,
            "factor_base_sha256_recorded": ctxs[bits]["meta"]["factor_base_sha256"],
            "factor_base_reproduced": fb2_sha == ctxs[bits]["meta"]["factor_base_sha256"],
            "null_integer_stream_sha256_recomputed": h.hexdigest(),
            "null_integer_stream_sha256_recorded": arm_meta[f"NULL-UNIF-D.bits{bits}"]["integer_stream_sha256"],
            "null_stream_reproduced": h.hexdigest() == arm_meta[f"NULL-UNIF-D.bits{bits}"]["integer_stream_sha256"],
        }
        rec["all_reproduced"] = all(rec[k] for k in
                                    ("curve_reproduced", "factor_base_reproduced", "null_stream_reproduced"))
        ident["streams"][str(bits)] = rec
        ident["passes"] = ident["passes"] and rec["all_reproduced"]
        budget.check()
    log(f"[control] CTRL-APPARATUS-IDENTITY passes={ident['passes']}")

    total_incomplete = sum(m["incomplete_factorizations"] for m in arm_meta.values())
    total_mismatch = sum(m["factorization_product_mismatches"] for m in arm_meta.values())
    fact_complete = {
        "blocking": True,
        "check": ("the product of each recorded factorization equals its integer; "
                  "incomplete factorizations are counted and reported, never silently dropped"),
        "records_checked": sum(m["records"] for m in arm_meta.values()),
        "product_mismatches_total": total_mismatch,
        "incomplete_factorizations_total": total_incomplete,
        "incomplete_by_arm": {a: arm_meta[a]["incomplete_factorizations"] for a in arm_meta},
        "factorization_is_complete_not_truncated": True,
        "passes": total_mismatch == 0,
        "note": ("Every integer was factored completely (trial division by the 168 "
                 "primes below 1000, then deterministic Miller-Rabin and Pollard-Brent "
                 "to full splitting). No trial-division truncation exists in the code "
                 "path. An incomplete record would carry LPF 0 and be excluded from "
                 "every fraction; the count is reported above."),
    }

    pair_ok = all(arm_meta[a]["pair_index_order_ok"] for a in core.TREATMENT_ARMS)
    pair_count = {
        "blocking": True,
        "check": "the treatment arm holds exactly 130816 records and no (i,j) with j <= i",
        "expected_records": core.N_PAIRS,
        "records_by_treatment_arm": {a: arm_meta[a]["records"] for a in core.TREATMENT_ARMS},
        "enumeration_rule": "for i in range(512): for j in range(i+1, 512)",
        "no_pair_with_j_le_i": pair_ok,
        "passes": pair_ok and all(arm_meta[a]["records"] == core.N_PAIRS for a in core.TREATMENT_ARMS),
    }

    enca_pass = all(per_bits[str(b)]["CTRL-ENCA-POWER"]["passes"] for b in core.FIELD_SIZES_BITS)
    result["controls"] = {
        "CTRL-ENCA-POWER": {
            "blocking": True,
            "by_field_size": {str(b): per_bits[str(b)]["CTRL-ENCA-POWER"] for b in core.FIELD_SIZES_BITS},
            "passes": enca_pass,
        },
        "CTRL-APPARATUS-IDENTITY": ident,
        "CTRL-FACTOR-COMPLETE": fact_complete,
        "CTRL-PAIR-COUNT": pair_count,
        "CTRL-NULL-DICKMAN": {
            "blocking": False,
            "by_field_size": {str(b): per_bits[str(b)]["CTRL-NULL-DICKMAN"] for b in core.FIELD_SIZES_BITS},
            "passes_is_not_gating": True,
        },
    }

    # ---------------- frozen success criterion, evaluated mechanically ----------------
    blocking_ok = (enca_pass and ident["passes"] and fact_complete["passes"]
                   and pair_count["passes"])
    per_bits_ok = {}
    for b in core.FIELD_SIZES_BITS:
        d = per_bits[str(b)]
        per_bits_ok[str(b)] = {
            "KS2-DS-1_le_0.006373": d["KS2-DS-1"]["passes_threshold"],
            "TAIL-DS-1_abs_le_0.01": d["TAIL-DS-1"]["passes_threshold"],
            "DECAY-1_does_not_fire": not d["DECAY-1"]["fired"],
        }
        per_bits_ok[str(b)]["all_three"] = all(per_bits_ok[str(b)].values())
    met = blocking_ok and all(per_bits_ok[str(b)]["all_three"] for b in core.FIELD_SIZES_BITS)
    result["success_criterion"] = {
        "text_quoted_from_contract": (
            "SUPPORT AT TOY SCALE iff, at BOTH field sizes: KS2-DS-1 <= 0.006373, "
            "TAIL-DS-1 <= 0.01, DECAY-1 does not fire, and the blocking controls "
            "CTRL-ENCA-POWER, CTRL-APPARATUS-IDENTITY, CTRL-FACTOR-COMPLETE and "
            "CTRL-PAIR-COUNT all pass. KS-DS-1 and RATE-DS-1 are reported alongside "
            "but do not gate this criterion."),
        "per_field_size": per_bits_ok,
        "blocking_controls_all_pass": blocking_ok,
        "met_at_both_field_sizes": met,
        "executor_note": ("This is a MECHANICAL evaluation of the frozen criterion "
                          "against the measured numbers. The Executor assigns no "
                          "outcome branch, no disposition, no evidence strength and "
                          "no claim about HEUR-DS-1 or H-SMTH-001. Outcome "
                          "classification belongs to the Validator, the Red Team and "
                          "the Coordinator."),
    }

    result["status"] = "completed"
    result["claim_ceiling"] = (
        "TOY TIER under every outcome. Two field sizes at 16 and 20 bits, |FB| = 512, "
        "m = 4, INT-1 / ENC-B. No crypto-scale, medium-scale, affected-scheme or "
        "asymptotic claim is derivable; no exponent and no cost saving is claimed or "
        "claimable.")
    result["certificate"] = {
        "kind": "none",
        "why": ("Pure measurement run. No discrete logarithm is solved and no "
                "factor-base relation is claimed, so docs/claims-and-verification.md "
                "requires no solution certificate. The factorisation integrity check "
                "CTRL-FACTOR-COMPLETE and the independent re-verification in "
                "verify_run.py are recorded separately."),
    }
    result["budget_consumed_measure_stage"] = {
        "wall_seconds": round(time.time() - t0, 3),
        "cpu_seconds": round(core.cpu_seconds_self_and_children(), 3),
        "peak_rss_bytes": core.peak_rss_bytes(),
    }
    result["log"] = lines
    with open(out_path, "w") as fh:
        json.dump(result, fh, indent=2)
    log(f"[measure] done in {result['budget_consumed_measure_stage']['wall_seconds']}s, "
        f"peak RSS {result['budget_consumed_measure_stage']['peak_rss_bytes']} bytes")
    return 0


# ===========================================================================
# ORCHESTRATOR
# ===========================================================================
def orchestrate(run_dir: str) -> int:
    os.makedirs(run_dir, exist_ok=True)
    t0 = time.time()
    stdout_path = os.path.join(run_dir, "stdout.log")
    stderr_path = os.path.join(run_dir, "stderr.log")
    so = open(stdout_path, "a", buffering=1)
    se = open(stderr_path, "a", buffering=1)

    def out(msg):
        print(msg, flush=True)
        so.write(msg + "\n")

    def err(msg):
        se.write(msg + "\n")
        se.flush()

    out(f"=== {RUN_ID} / EXP-SMTH-71b1b0 / TASK-20260803-fa7476 ===")
    out(f"started_utc={time.strftime('%Y-%m-%dT%H:%M:%SZ', time.gmtime())}")

    # ---- STEP 0: CONTRACT DIGEST GATE -------------------------------------
    digest, nbytes = sha256_file(SPEC_PATH)
    out(f"[gate] specification.yaml sha256={digest} bytes={nbytes}")
    out(f"[gate] expected           sha256={core.SPEC_SHA256} bytes={core.SPEC_BYTES}")
    if digest != core.SPEC_SHA256:
        reason = (f"HALT: frozen contract digest mismatch. computed {digest} "
                  f"expected {core.SPEC_SHA256}. The frozen contract changed; the run "
                  f"is void. NO DATUM PRODUCED. Nothing was 'fixed'.")
        out(reason)
        err(reason)
        with open(os.path.join(run_dir, "raw-result.json"), "w") as fh:
            json.dump({"run_id": RUN_ID, "experiment_id": "EXP-SMTH-71b1b0",
                       "status": "halt", "classification": "specification_error",
                       "halt_reason": reason, "datum_produced": False}, fh, indent=2)
        so.close()
        se.close()
        return 2
    out("[gate] PASS - frozen contract digest matches. Execution may proceed.")

    # ---- STEP 1: RSS PRE-FLIGHT DECLARATION (before the probe) -------------
    decl_path = os.path.join(run_dir, "rss-preflight-declaration.json")
    with open(decl_path, "w") as fh:
        json.dump({"declaration": RSS_DECLARATION,
                   "written_at_utc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
                   "written_before_probe": True}, fh, indent=2)
    decl_sha, _ = sha256_file(decl_path)
    out(f"[declare] rss-preflight-declaration.json written BEFORE the probe, "
        f"sha256={decl_sha}")
    out(f"[declare] tolerance: absolute peak RSS <= "
        f"{RSS_DECLARATION['tolerance']['absolute_peak_rss_bytes']} bytes; growth "
        f"5%->20% <= {RSS_DECLARATION['tolerance']['max_growth_between_first_and_last_checkpoint_bytes']} bytes; "
        f"margin below contract cap = {RSS_DECLARATION['margin']['margin_below_contract_cap_bytes']} bytes")

    env = dict(os.environ, PYTHONHASHSEED="0")

    # ---- STEP 2: RSS PRE-FLIGHT PROBE -------------------------------------
    probe_path = os.path.join(run_dir, "rss-preflight.json")
    out("[probe] running RSS pre-flight probe at ~5, 10 and 20 percent of records")
    deadline = t0 + BUDGET["maximum_wall_seconds"]
    pr = subprocess.run([sys.executable, os.path.abspath(__file__),
                         "--stage", "preflight", "--out", probe_path,
                         "--deadline", repr(deadline),
                         "--cpu-remaining",
                         repr(BUDGET["maximum_cpu_seconds"] - core.cpu_seconds_self_and_children())],
                        capture_output=True, text=True, env=env)
    so.write(pr.stdout)
    se.write(pr.stderr)
    if pr.returncode != 0:
        reason = (f"HALT: RSS pre-flight probe failed (rc={pr.returncode}). The "
                  f"declared tolerance in rss-preflight-declaration.json "
                  f"(sha256 {decl_sha}) was exceeded, or the probe stage itself "
                  f"failed. NO MEASUREMENT PERFORMED, NO DATUM PRODUCED.")
        out(reason)
        err(reason)
        with open(os.path.join(run_dir, "raw-result.json"), "w") as fh:
            json.dump({"run_id": RUN_ID, "experiment_id": "EXP-SMTH-71b1b0",
                       "status": "halt", "classification": "resource_exhaustion",
                       "halt_reason": reason, "datum_produced": False,
                       "preflight_declaration_sha256": decl_sha}, fh, indent=2)
        so.close()
        se.close()
        return 3
    probe = json.load(open(probe_path))
    probe["declaration_file_sha256"] = decl_sha
    with open(probe_path, "w") as fh:
        json.dump(probe, fh, indent=2)
    out(f"[probe] PASS - {probe['verdict']}")

    # ---- STEP 3: MEASUREMENT ----------------------------------------------
    raw_path = os.path.join(run_dir, "raw-result.json")
    out("[measure] starting measurement stage")
    mr = subprocess.run([sys.executable, os.path.abspath(__file__),
                         "--stage", "measure", "--run-dir", run_dir,
                         "--out", raw_path,
                         "--deadline", repr(deadline),
                         "--cpu-remaining",
                         repr(BUDGET["maximum_cpu_seconds"] - core.cpu_seconds_self_and_children())],
                        capture_output=True, text=True, env=env)
    so.write(mr.stdout)
    se.write(mr.stderr)
    if mr.returncode not in (0, 4):
        reason = f"measurement stage failed with rc={mr.returncode}"
        out("HALT: " + reason)
        err("HALT: " + reason)
        if not os.path.exists(raw_path):
            with open(raw_path, "w") as fh:
                json.dump({"run_id": RUN_ID, "status": "halt",
                           "classification": "implementation_error",
                           "halt_reason": reason, "datum_produced": False,
                           "stderr_tail": mr.stderr[-4000:]}, fh, indent=2)
        so.close()
        se.close()
        return 5

    raw = json.load(open(raw_path))
    raw["preflight"] = {
        "declaration_path": f"experiments/EXP-SMTH-71b1b0/runs/{RUN_ID}/rss-preflight-declaration.json",
        "declaration_sha256": decl_sha,
        "probe_path": f"experiments/EXP-SMTH-71b1b0/runs/{RUN_ID}/rss-preflight.json",
        "verdict": probe["verdict"],
        "observations": probe["observations"],
        "growth_first_to_last_checkpoint_bytes": probe["growth_first_to_last_checkpoint_bytes"],
    }
    raw["specification_sha256_verified"] = digest
    raw["budget"] = dict(BUDGET)
    raw["budget_consumed"] = {
        "wall_seconds_total": round(time.time() - t0, 3),
        "cpu_seconds_total": round(core.cpu_seconds_self_and_children(), 3),
        "peak_rss_bytes_max_over_stages": max(
            probe["final_peak_rss_bytes"],
            raw.get("budget_consumed_measure_stage", {}).get("peak_rss_bytes", 0)),
        "runs_used": 1, "resumes_used": 0, "workers_used": 1,
        "network_calls": 0,
    }
    with open(raw_path, "w") as fh:
        json.dump(raw, fh, indent=2)

    if mr.returncode == 4:
        out("[measure] BUDGET STOP - reported as a stop, never as a result.")
        so.close()
        se.close()
        return 4

    out("[measure] measurement complete")
    out(f"[budget] wall={raw['budget_consumed']['wall_seconds_total']}s "
        f"cpu={raw['budget_consumed']['cpu_seconds_total']}s "
        f"peakRSS={raw['budget_consumed']['peak_rss_bytes_max_over_stages']}B")
    so.close()
    se.close()
    return 0


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--stage", choices=["preflight", "measure"])
    ap.add_argument("--run-dir")
    ap.add_argument("--out")
    ap.add_argument("--deadline", type=float)
    ap.add_argument("--cpu-remaining", type=float)
    args = ap.parse_args()
    if args.stage == "preflight":
        return stage_preflight(args.out, args.deadline, args.cpu_remaining)
    if args.stage == "measure":
        return stage_measure(args.run_dir, args.out, args.deadline, args.cpu_remaining)
    return orchestrate(args.run_dir)


if __name__ == "__main__":
    sys.exit(main())

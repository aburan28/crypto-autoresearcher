#!/usr/bin/env python3
"""PART A -- the zero-decoder-call low-k recompute.

TASK-20260817-b4b6e4 (executor) / BATCH-dd0901 / GOAL-HQC-001 /
EXP-HQC-982268 / H-HQC-18d1b4 (stays PROPOSED).
Authorized by DEC-20260817-2b638b via BATCH-dd0901's dispatch queue.
Pre-registered design: design.md, closed before this script ran; its sha256 is
measured here at launch and recorded in the results JSON.

PURE ARITHMETIC ON ALREADY-COMMITTED JSON.  ZERO decoder calls: this script
imports nothing from stage_a.py / matched_pair.py / measure.py at all, so the
strongest possible form of the zero-call guarantee holds here -- the decoder
code is never even loaded into the process.  Part B (coupled_null_control.py)
must load them and installs the call-counting wrappers.

Claim tier: TOY, hard ceiling.  OBSERVATIONS ONLY -- no branch of batch.yaml's
frozen reading rule is applied, named or hinted at here.

Re-run:
    PYTHONDONTWRITEBYTECODE=1 python3 low_k_recompute.py --out-dir .
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

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.abspath(os.path.join(HERE, *([".."] * 7)))

FRESH = os.path.join(
    REPO, "coordination", "goals", "GOAL-HQC-001", "batches", "BATCH-91929e",
    "tasks", "TASK-20260817-c603c0", "cross_regime_arms_results.json")
HIST_A79E4F = os.path.join(
    REPO, "coordination", "goals", "GOAL-HQC-001", "batches", "BATCH-412513",
    "tasks", "TASK-20260809-a79e4f", "matched_pair_results.json")
HIST_8BBDD2 = os.path.join(
    REPO, "coordination", "goals", "GOAL-HQC-001", "batches", "BATCH-0e126d",
    "tasks", "TASK-20260814-8bbdd2", "matched_pair_repeat_results.json")
HIST_E61CCA = os.path.join(
    REPO, "coordination", "goals", "GOAL-HQC-001", "batches", "BATCH-174014",
    "tasks", "TASK-20260815-e61cca",
    "shard_8001_8002_discard_prefix_results.json")

M = 17
K_RANGE = list(range(2, 27))
GATE_TOL = 1e-12


def sha256_file(path):
    h = hashlib.sha256()
    with open(path, "rb") as fh:
        for blk in iter(lambda: fh.read(1 << 20), b""):
            h.update(blk)
    return h.hexdigest()


def core_seconds():
    a = resource.getrusage(resource.RUSAGE_SELF)
    b = resource.getrusage(resource.RUSAGE_CHILDREN)
    return a.ru_utime + a.ru_stime + b.ru_utime + b.ru_stime


def git_state():
    def run(*a):
        try:
            return subprocess.run(a, cwd=REPO, capture_output=True, text=True,
                                  timeout=60).stdout.strip()
        except Exception as exc:                                  # noqa: BLE001
            return f"<unavailable: {exc}>"
    porcelain = run("git", "status", "--porcelain")
    return dict(commit=run("git", "rev-parse", "HEAD"),
                branch=run("git", "rev-parse", "--abbrev-ref", "HEAD"),
                dirty=bool(porcelain), dirty_paths=porcelain.splitlines()[:80])


def log(m):
    print(m, flush=True)


def alpha_from(se_lo, se_hi, t_lo, t_hi):
    """The family's single estimator.  None-safe."""
    if se_lo is None or se_hi is None:
        return None
    if not (np.isfinite(se_lo) and np.isfinite(se_hi)) or se_lo <= 0 or se_hi <= 0:
        return None
    return -(math.log(se_hi) - math.log(se_lo)) / (math.log(t_hi) - math.log(t_lo))


def by_k(node):
    """{k: se_paired} plus the whole per-k block, from a committed array node."""
    ks = node["ks"]
    return dict(ks=ks,
                se_paired={int(k): node["se_paired"][i] for i, k in enumerate(ks)},
                se_unpaired={int(k): node["se_unpaired"][i] for i, k in enumerate(ks)},
                uop={int(k): node["unpaired_over_paired_ratio"][i]
                     for i, k in enumerate(ks)},
                n_batches=node.get("n_batches"))


def ladder_fit(logT, logSE):
    """OLS in log-log; alpha = -slope.  Returns (alpha, resid_rms, slope_se)."""
    x = np.asarray(logT, dtype=np.float64)
    y = np.asarray(logSE, dtype=np.float64)
    n = len(x)
    slope, intercept = np.polyfit(x, y, 1)
    resid = y - (slope * x + intercept)
    resid_rms = float(np.sqrt(np.mean(resid ** 2)))
    sxx = float(np.sum((x - x.mean()) ** 2))
    dof = n - 2
    slope_se = (float(np.sqrt((np.sum(resid ** 2) / dof) / sxx))
                if dof > 0 and sxx > 0 else None)
    return -float(slope), resid_rms, slope_se


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("--out-dir", default=HERE)
    args = ap.parse_args(argv)
    t0, c0 = time.time(), core_seconds()

    design_sha = sha256_file(os.path.join(HERE, "design.md"))
    log(f"[preregistration] design.md sha256 measured at launch = {design_sha}")
    log("[preregistration] NOT independently anchored: this session does not "
        "commit. Content corroboration only, exactly as design.md states.")

    R = {
        "task_id": "TASK-20260817-b4b6e4", "role": "executor", "part": "A",
        "experiment_id": "EXP-HQC-982268", "hypothesis_id": "H-HQC-18d1b4",
        "goal": "GOAL-HQC-001", "batch": "BATCH-dd0901",
        "authorized_by": "DEC-20260817-2b638b", "claim_tier": "toy",
        "status": "pending",
        "what_this_is": (
            "Zero-decoder-call low-k recompute of all eight local-exponent "
            "cells from ALREADY-COMMITTED per-k arrays. Pure arithmetic. No "
            "decoder module is even imported by this script."),
        "scope_statement": (
            "TOY, hard ceiling. PS-R3 only (n=7187, n_e=56, n_2=128, dup=1, "
            "N=7168, k 2..26, m=17). Nothing here is a statement about HQC's "
            "IND-CCA security, its decoding-failure rate, assumption A17 or A5, "
            "or any standardized parameter set."),
        "observations_only_note": (
            "THE EXECUTOR CONCLUDES NOTHING. batch.yaml's frozen reading rule "
            "is NOT applied here, no branch is named, and no judgment is made "
            "about whether the k-explanation is corroborated or refuted."),
        "preregistration": dict(
            design_md_sha256_at_launch=design_sha,
            independently_anchored=False,
            anchoring_claim=("content corroboration only -- the executing "
                             "session does not commit; no pre-fill blob is "
                             "committed by it and no anchor line is "
                             "hand-authored into stdout.log")),
        "design_reference": "design.md, closed before this run",
        "started_at_utc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "command": " ".join([sys.executable] + sys.argv),
        "git": git_state(),
        "environment": dict(python=sys.version, python_executable=sys.executable,
                            platform=platform.platform(),
                            machine=platform.machine(), numpy=np.__version__,
                            cpu_count=os.cpu_count()),
        "decoder_calls_made": 0,
        "decoder_modules_imported_by_this_script": [],
        "zero_decoder_call_basis": (
            "This script imports no pinned decoder module at all, so no call "
            "is possible. Part B loads them and enforces the counter/pin gate."),
    }

    # ---------------- source files, measured ----------------
    src = {}
    for name, path in [("cross_regime_arms_results.json", FRESH),
                       ("matched_pair_results.json (TASK-20260809-a79e4f)", HIST_A79E4F),
                       ("matched_pair_repeat_results.json (TASK-20260814-8bbdd2)", HIST_8BBDD2),
                       ("shard_8001_8002_discard_prefix_results.json (TASK-20260815-e61cca)", HIST_E61CCA)]:
        src[name] = dict(path=os.path.relpath(path, REPO), sha256=sha256_file(path),
                         read_only=True)
    R["source_files"] = src

    fresh = json.load(open(FRESH))
    h_a = json.load(open(HIST_A79E4F))
    h_b = json.load(open(HIST_8BBDD2))
    h_c = json.load(open(HIST_E61CCA))

    # ---------------- FRESH windows ----------------
    WIN_T = {"P1": 5000, "P2": 10000, "N1": 10000, "N2": 20000}
    SHARDS_FRESH = ["shard_5000", "shard_8002"]
    wnodes = {}
    win_meta = {}
    for sh in SHARDS_FRESH:
        for w in ("P1", "P2", "N1", "N2"):
            node = fresh["per_shard_per_window"][sh][w]
            wnodes[(sh, w)] = by_k(node["per_k"])
            win_meta[f"{sh}.{w}"] = dict(
                index_range=node["index_range"], T=node["T"],
                jack_batch_size=node["jack_batch_size"],
                n_batches=node["n_batches"],
                per_k_n_batches=node["per_k"]["n_batches"],
                ks_len=len(node["per_k"]["ks"]),
                ks_min=min(node["per_k"]["ks"]), ks_max=max(node["per_k"]["ks"]))
    R["fresh_window_metadata"] = win_meta
    R["fresh_window_pairs"] = dict(
        regime_P="P1 [30000:35000) T=5000  ->  P2 [35000:45000) T=10000",
        regime_N="N1 [45000:55000) T=10000 ->  N2 [55000:75000) T=20000",
        estimator="alpha(k) = -[log se_paired_hi(k) - log se_paired_lo(k)] / [log T_hi - log T_lo]",
        all_four_T_points_come_from_ONE_call_in_ONE_process_per_shard=True)

    CELLS_FRESH = [("shard_5000", "P"), ("shard_5000", "N"),
                   ("shard_8002", "P"), ("shard_8002", "N")]

    def fresh_alpha(sh, regime, k):
        lo, hi = ("P1", "P2") if regime == "P" else ("N1", "N2")
        a = wnodes[(sh, lo)]["se_paired"].get(k)
        b = wnodes[(sh, hi)]["se_paired"].get(k)
        return alpha_from(a, b, WIN_T[lo], WIN_T[hi])

    fresh_by_k = {}
    for sh, rg in CELLS_FRESH:
        key = f"{sh}_regime_{rg}"
        fresh_by_k[key] = {str(k): fresh_alpha(sh, rg, k) for k in K_RANGE}

    # ---------------- three contrasts ----------------
    def contrasts_at(k):
        a5P = fresh_by_k["shard_5000_regime_P"][str(k)]
        a5N = fresh_by_k["shard_5000_regime_N"][str(k)]
        a8P = fresh_by_k["shard_8002_regime_P"][str(k)]
        a8N = fresh_by_k["shard_8002_regime_N"][str(k)]
        if None in (a5P, a5N, a8P, a8N):
            return dict(regime_main_effect=None, shard_main_effect=None,
                        interaction=None)
        return dict(
            regime_main_effect=(a5P + a8P) / 2.0 - (a5N + a8N) / 2.0,
            shard_main_effect=(a5P + a5N) / 2.0 - (a8P + a8N) / 2.0,
            interaction=(a5P - a5N) - (a8P - a8N))
    contrasts_by_k = {str(k): contrasts_at(k) for k in K_RANGE}

    # ---------------- 4-point ladders ----------------
    ladder_by_k = {}
    for sh in SHARDS_FRESH:
        d = {}
        for k in K_RANGE:
            ses = [wnodes[(sh, w)]["se_paired"].get(k) for w in ("P1", "P2", "N1", "N2")]
            if any(s is None or not np.isfinite(s) or s <= 0 for s in ses):
                d[str(k)] = dict(alpha=None, residual_rms=None, slope_standard_error=None)
                continue
            a, rms, sse = ladder_fit([math.log(WIN_T[w]) for w in ("P1", "P2", "N1", "N2")],
                                     [math.log(s) for s in ses])
            d[str(k)] = dict(alpha=a, residual_rms=rms, slope_standard_error=sse,
                             se_paired_points=dict(zip(("P1", "P2", "N1", "N2"), ses)))
        ladder_by_k[sh] = d

    # ---------------- same-T noise handle ----------------
    noise_by_k = {}
    for k in K_RANGE:
        per = {}
        for sh in SHARDS_FRESH:
            a = wnodes[(sh, "P2")]["se_paired"].get(k)
            b = wnodes[(sh, "N1")]["se_paired"].get(k)
            per[sh] = (abs(math.log2(a / b)) if (a and b and a > 0 and b > 0)
                       else None)
        vals = [v for v in per.values() if v is not None]
        noise_by_k[str(k)] = dict(
            D_shard=per,
            D_RMS=(float(np.sqrt(np.mean(np.array(vals) ** 2))) if len(vals) == len(SHARDS_FRESH) else None))

    # ---------------- HISTORICAL cells + FAIL-CLOSED GATE ----------------
    HIST_MAP = {
        "shard_5000_regime_P": dict(
            shard=5000, regime="P", T_lo=5000, T_hi=10000,
            lo=dict(file="coordination/goals/GOAL-HQC-001/batches/BATCH-412513/tasks/TASK-20260809-a79e4f/matched_pair_results.json",
                    json_path="stage_1.matched_pair.per_shard.shard_5000",
                    node=h_a["stage_1"]["matched_pair"]["per_shard"]["shard_5000"]),
            hi=dict(file="coordination/goals/GOAL-HQC-001/batches/BATCH-0e126d/tasks/TASK-20260814-8bbdd2/matched_pair_repeat_results.json",
                    json_path="matched_pair.per_shard.shard_5000",
                    node=h_b["matched_pair"]["per_shard"]["shard_5000"]),
            committed_alpha_17=2.836,
            committed_source="EV-HQC-469c08 O6 (via BATCH-0e126d review TASK-20260814-a49f1c table)",
            committed_printed_significant_figures=4),
        "shard_6000_regime_P": dict(
            shard=6000, regime="P", T_lo=5000, T_hi=10000,
            lo=dict(file="coordination/goals/GOAL-HQC-001/batches/BATCH-412513/tasks/TASK-20260809-a79e4f/matched_pair_results.json",
                    json_path="stage_1.matched_pair.per_shard.shard_6000",
                    node=h_a["stage_1"]["matched_pair"]["per_shard"]["shard_6000"]),
            hi=dict(file="coordination/goals/GOAL-HQC-001/batches/BATCH-0e126d/tasks/TASK-20260814-8bbdd2/matched_pair_repeat_results.json",
                    json_path="matched_pair.per_shard.shard_6000",
                    node=h_b["matched_pair"]["per_shard"]["shard_6000"]),
            committed_alpha_17=1.402,
            committed_source="EV-HQC-469c08 O6 (via BATCH-0e126d review TASK-20260814-a49f1c table)",
            committed_printed_significant_figures=4),
        "shard_8001_regime_N": dict(
            shard=8001, regime="N", T_lo=10000, T_hi=20000,
            lo=dict(file="coordination/goals/GOAL-HQC-001/batches/BATCH-412513/tasks/TASK-20260809-a79e4f/matched_pair_results.json",
                    json_path="stage_2.matched_pair.per_shard.shard_8001",
                    node=h_a["stage_2"]["matched_pair"]["per_shard"]["shard_8001"]),
            hi=dict(file="coordination/goals/GOAL-HQC-001/batches/BATCH-174014/tasks/TASK-20260815-e61cca/shard_8001_8002_discard_prefix_results.json",
                    json_path="matched_pair.per_shard.shard_8001",
                    node=h_c["matched_pair"]["per_shard"]["shard_8001"]),
            committed_alpha_17=-0.2682495157085447,
            committed_source="EV-HQC-927899 O3-O4; e61cca single_shard_only_local_exponent.shard_8001.local_exponent_alpha",
            committed_printed_significant_figures=16),
        "shard_8002_regime_N": dict(
            shard=8002, regime="N", T_lo=10000, T_hi=20000,
            lo=dict(file="coordination/goals/GOAL-HQC-001/batches/BATCH-412513/tasks/TASK-20260809-a79e4f/matched_pair_results.json",
                    json_path="stage_2.matched_pair.per_shard.shard_8002",
                    node=h_a["stage_2"]["matched_pair"]["per_shard"]["shard_8002"]),
            hi=dict(file="coordination/goals/GOAL-HQC-001/batches/BATCH-174014/tasks/TASK-20260815-e61cca/shard_8001_8002_discard_prefix_results.json",
                    json_path="matched_pair.per_shard.shard_8002",
                    node=h_c["matched_pair"]["per_shard"]["shard_8002"]),
            committed_alpha_17=-0.8662355237627483,
            committed_source="EV-HQC-927899 O3-O4; e61cca single_shard_only_local_exponent.shard_8002.local_exponent_alpha",
            committed_printed_significant_figures=16),
    }

    recon = {
        "task_id": "TASK-20260817-b4b6e4", "part": "A",
        "goal": "GOAL-HQC-001", "batch": "BATCH-dd0901", "claim_tier": "toy",
        "written_unconditionally": True,
        "what_this_is": (
            "THE RECONSTRUCTION GATE. batch.yaml's per-cell array mapping is "
            "the authoring Coordinator's RECONSTRUCTION and is NOT asserted as "
            "fact. Each cell's k=17 alpha is recomputed from the two arrays "
            "ACTUALLY selected and compared to that cell's committed value at "
            "1e-12 absolute BEFORE any low-k value from it is reported."),
        "mapping_source": "coordination/goals/GOAL-HQC-001/batches/BATCH-dd0901/batch.yaml -> the_four_historical_cells_and_their_reconstruction",
        "mapping_was_adjusted_or_searched": False,
        "mapping_adjustment_note": (
            "NO alternative pairing was tried, computed or considered. The "
            "mapping transcribed into design.md section 2.5 is the only one "
            "evaluated, and it was transcribed before any datum existed."),
        "gate_tolerance_absolute": GATE_TOL,
        "comparator_precision_disclosure": (
            "Two comparators (+2.836, +1.402) exist in the committed record "
            "only at four significant figures. A 1e-12 absolute gate against a "
            "four-significant-figure decimal can pass only if the underlying "
            "full-precision value is exactly that decimal. This was declared in "
            "design.md section 2.5 BEFORE the gate was run. The 1e-12 verdict "
            "in `gate_pass` stands as THE verdict; "
            "`residual_vs_printed_precision_halfulp` is a subordinate "
            "diagnostic, is NOT a second gate, and cannot turn a FAIL into a "
            "PASS."),
        "cells": {},
    }

    hist_by_k = {}
    for key, spec in HIST_MAP.items():
        lo = by_k(spec["lo"]["node"])
        hi = by_k(spec["hi"]["node"])
        a17 = alpha_from(lo["se_paired"].get(M), hi["se_paired"].get(M),
                         spec["T_lo"], spec["T_hi"])
        committed = spec["committed_alpha_17"]
        resid = None if a17 is None else abs(a17 - committed)
        gate_pass = bool(resid is not None and resid <= GATE_TOL)
        # subordinate diagnostic only -- see comparator_precision_disclosure
        sig = spec["committed_printed_significant_figures"]
        if committed != 0:
            expo = math.floor(math.log10(abs(committed)))
            halfulp = 0.5 * 10 ** (expo - (sig - 1))
        else:
            halfulp = 0.0
        recon["cells"][key] = dict(
            shard=spec["shard"], regime=spec["regime"],
            T_lo=spec["T_lo"], T_hi=spec["T_hi"],
            lo_array=dict(file=spec["lo"]["file"], json_path=spec["lo"]["json_path"],
                          length=len(lo["ks"]), ks_min=min(lo["ks"]), ks_max=max(lo["ks"]),
                          n_batches=lo["n_batches"],
                          se_paired_k17=lo["se_paired"].get(M)),
            hi_array=dict(file=spec["hi"]["file"], json_path=spec["hi"]["json_path"],
                          length=len(hi["ks"]), ks_min=min(hi["ks"]), ks_max=max(hi["ks"]),
                          n_batches=hi["n_batches"],
                          se_paired_k17=hi["se_paired"].get(M)),
            recomputed_alpha_17=a17,
            committed_alpha_17=committed,
            committed_source=spec["committed_source"],
            absolute_residual=resid,
            gate_tolerance_absolute=GATE_TOL,
            gate_pass=gate_pass,
            verdict=("PASS" if gate_pass else "FAIL"),
            cell_status=("RECONSTRUCTION_VERIFIED" if gate_pass
                         else "DATA_AVAILABILITY_OUTCOME"),
            subordinate_diagnostic_not_a_gate=dict(
                committed_printed_significant_figures=sig,
                half_ulp_of_printed_precision=halfulp,
                residual_vs_printed_precision_halfulp=(
                    None if resid is None else resid - halfulp),
                residual_within_printed_precision=(
                    None if resid is None else bool(resid <= halfulp)),
                note=("Diagnostic only. Reported so the Coordinator can see "
                      "whether a FAIL is a comparator-rounding artifact or a "
                      "mapping error. It is NOT a gate and does not change "
                      "gate_pass or cell_status.")),
            procedural_asymmetry=("the two T-points come from DIFFERENT tasks "
                                  "in DIFFERENT processes"),
        )
        log(f"[gate] {key}: recomputed={a17!r} committed={committed!r} "
            f"resid={resid!r} -> {recon['cells'][key]['verdict']}")
        if gate_pass:
            hist_by_k[key] = {
                str(k): alpha_from(lo["se_paired"].get(k), hi["se_paired"].get(k),
                                   spec["T_lo"], spec["T_hi"]) for k in K_RANGE}
        else:
            hist_by_k[key] = {str(k): None for k in K_RANGE}

    n_pass = sum(1 for c in recon["cells"].values() if c["gate_pass"])
    recon["cells_passing"] = n_pass
    recon["cells_failing"] = 4 - n_pass
    recon["failing_cell_names"] = [k for k, c in recon["cells"].items()
                                   if not c["gate_pass"]]
    recon["low_k_values_reported_for_failing_cells"] = False
    recon["no_conclusion_drawn_note"] = (
        "A gate failure is an INFRASTRUCTURE / DATA-AVAILABILITY outcome under "
        "AGENTS.md rule 5 and is NEVER negative mathematical evidence about k, "
        "the shards, the regimes, or HQC. No branch of the reading rule is "
        "applied or named here.")
    with open(os.path.join(args.out_dir, "historical_cell_reconstruction.json"), "w") as fh:
        json.dump(recon, fh, indent=1)
    log(f"[gate] {n_pass}/4 historical cells PASS at {GATE_TOL:g}")

    # ---------------- eight real cells' unpaired_over_paired ----------------
    uop_by_k = {}
    for k in K_RANGE:
        vals = {}
        for sh in SHARDS_FRESH:
            for w in ("P1", "P2", "N1", "N2"):
                v = wnodes[(sh, w)]["uop"].get(k)
                if v is not None and np.isfinite(v):
                    vals[f"{sh}.{w}"] = v
        finite = sorted(vals.values())
        uop_by_k[str(k)] = dict(
            per_window=vals,
            eight_real_cells_min=(finite[0] if len(finite) == 8 else None),
            eight_real_cells_max=(finite[-1] if len(finite) == 8 else None),
            n_finite=len(finite))

    # ---------------- committed-value verifications ----------------
    V = {}
    exp_fresh17 = {"shard_5000_regime_P": 2.0488128380076307,
                   "shard_5000_regime_N": 2.960737268597787,
                   "shard_8002_regime_P": 0.32362272345795423,
                   "shard_8002_regime_N": 1.5943364808460014}
    V["V1_fresh_cells_k17"] = {
        key: dict(measured=fresh_by_k[key]["17"], committed=exp,
                  residual=(None if fresh_by_k[key]["17"] is None
                            else abs(fresh_by_k[key]["17"] - exp)),
                  tolerance=1e-12,
                  pass_=bool(fresh_by_k[key]["17"] is not None
                             and abs(fresh_by_k[key]["17"] - exp) <= 1e-12))
        for key, exp in exp_fresh17.items()}
    exp_con17 = {"regime_main_effect": -1.091319093989102,
                 "shard_main_effect": 1.545795451150731,
                 "interaction": 0.3587893267978908}
    V["V2_contrasts_k17"] = {
        key: dict(measured=contrasts_by_k["17"][key], committed=exp,
                  residual=abs(contrasts_by_k["17"][key] - exp),
                  tolerance=1e-12,
                  pass_=bool(abs(contrasts_by_k["17"][key] - exp) <= 1e-12))
        for key, exp in exp_con17.items()}
    exp_fresh2 = {"shard_5000_regime_P": 0.580733, "shard_5000_regime_N": 0.506553,
                  "shard_8002_regime_P": 0.628397, "shard_8002_regime_N": 0.511866}
    V["V3_fresh_cells_k2"] = {
        key: dict(measured=fresh_by_k[key]["2"], committed=exp,
                  residual=abs(fresh_by_k[key]["2"] - exp), tolerance=1e-4,
                  pass_=bool(abs(fresh_by_k[key]["2"] - exp) <= 1e-4))
        for key, exp in exp_fresh2.items()}
    exp_lad = {"shard_5000": (0.4734, 1.008), "shard_8002": (0.0115, 0.514)}
    V["V4_ladders_k17"] = {}
    for sh, (ea, erms) in exp_lad.items():
        got = ladder_by_k[sh]["17"]
        V["V4_ladders_k17"][sh] = dict(
            measured_alpha=got["alpha"], committed_alpha=ea,
            alpha_residual=abs(got["alpha"] - ea),
            measured_residual_rms=got["residual_rms"],
            committed_residual_rms=erms,
            residual_rms_residual=abs(got["residual_rms"] - erms),
            measured_slope_standard_error=got["slope_standard_error"],
            tolerance=1e-3,
            pass_=bool(abs(got["alpha"] - ea) <= 1e-3
                       and abs(got["residual_rms"] - erms) <= 1e-3))
    exp_n17 = {"shard_5000": 4.063, "shard_8002": 1.895}
    V["V5_noise_handle_k17"] = {
        sh: dict(measured=noise_by_k["17"]["D_shard"][sh], committed=e,
                 residual=abs(noise_by_k["17"]["D_shard"][sh] - e), tolerance=1e-3,
                 pass_=bool(abs(noise_by_k["17"]["D_shard"][sh] - e) <= 1e-3))
        for sh, e in exp_n17.items()}
    V["V5_noise_handle_k17"]["D_RMS"] = dict(
        measured=noise_by_k["17"]["D_RMS"], committed=3.170,
        residual=abs(noise_by_k["17"]["D_RMS"] - 3.170), tolerance=1e-3,
        pass_=bool(abs(noise_by_k["17"]["D_RMS"] - 3.170) <= 1e-3))
    exp_n2 = {"shard_5000": 0.061, "shard_8002": 0.105}
    V["V6_noise_handle_k2"] = {
        sh: dict(measured=noise_by_k["2"]["D_shard"][sh], committed=e,
                 residual=abs(noise_by_k["2"]["D_shard"][sh] - e), tolerance=1e-3,
                 pass_=bool(abs(noise_by_k["2"]["D_shard"][sh] - e) <= 1e-3))
        for sh, e in exp_n2.items()}
    V["V6_noise_handle_k2"]["D_RMS_reported_not_gated"] = noise_by_k["2"]["D_RMS"]
    V["V7_historical_reconstruction_gate"] = {
        k: dict(verdict=c["verdict"], residual=c["absolute_residual"],
                tolerance=GATE_TOL)
        for k, c in recon["cells"].items()}
    V["nothing_was_tuned_attestation"] = (
        "No array selection, window pairing, tolerance or fit method was "
        "adjusted to make any verification pass. Every tolerance above is the "
        "one design.md froze before this run.")
    R["committed_value_verifications"] = V

    for name, blk in V.items():
        if not isinstance(blk, dict):
            continue
        for sub, val in blk.items():
            if isinstance(val, dict) and "pass_" in val:
                log(f"[verify] {name}.{sub}: {'PASS' if val['pass_'] else 'FAIL'} "
                    f"resid={val.get('residual', val.get('alpha_residual'))!r}")

    # ---------------- assemble ----------------
    def slice_k(d, k):
        return {key: v[str(k)] for key, v in d.items()}

    R["fresh_cells_alpha_by_k"] = fresh_by_k
    R["historical_cells_alpha_by_k"] = hist_by_k
    R["historical_cell_status"] = {k: c["cell_status"] for k, c in recon["cells"].items()}
    R["contrasts_by_k"] = contrasts_by_k
    R["four_point_ladders_by_k"] = ladder_by_k
    R["same_T_noise_handle_by_k"] = noise_by_k
    R["eight_real_cells_unpaired_over_paired_by_k"] = uop_by_k
    R["headline_slices"] = {
        f"k_{k}": dict(fresh_cells=slice_k(fresh_by_k, k),
                       historical_cells=slice_k(hist_by_k, k),
                       contrasts=contrasts_by_k[str(k)],
                       ladders={sh: ladder_by_k[sh][str(k)]["alpha"] for sh in SHARDS_FRESH},
                       D_shard=noise_by_k[str(k)]["D_shard"],
                       D_RMS=noise_by_k[str(k)]["D_RMS"],
                       real_cells_uop_range=[uop_by_k[str(k)]["eight_real_cells_min"],
                                             uop_by_k[str(k)]["eight_real_cells_max"]])
        for k in (2, 5, 10, 17)}
    R["procedural_asymmetry"] = dict(
        fresh="all four T-points per shard sliced from ONE call in ONE process",
        historical="the two T-points of every cell come from DIFFERENT tasks in DIFFERENT processes",
        standing_limitation=("This asymmetry is a standing limitation of any "
                             "fresh-versus-historical comparison made from these "
                             "cells. It is declared here rather than left for a "
                             "reviewer to find."),
        n_batches_per_array_reported_in=("fresh_window_metadata and "
                                         "historical_cell_reconstruction.json"))
    R["persist_per_trial_S_requirement"] = dict(
        binds_on_this_task=False,
        reason=("DEC-20260817-2b638b next_actions item (3) makes it effective "
                "from the NEXT SAMPLING TASK. This task makes zero decoder "
                "calls and samples nothing."),
        carried_forward_to=("the next sampling task in this family, i.e. the "
                            "next task that calls stage_a._t_shard"))
    R["aborted_on_reconstruction_gate"] = False
    R["status"] = "completed"
    R["status_note"] = (
        "Part A ran to completion. Per design.md section 2.5 a per-cell gate "
        "FAIL marks that cell DATA_AVAILABILITY_OUTCOME and suppresses its "
        "low-k values; it does not abort Part A, and cells that pass continue. "
        "`status: aborted_on_reconstruction_gate` is reserved for a Part A that "
        "cannot run at all.")
    wall = time.time() - t0
    core = core_seconds() - c0
    R["timing"] = dict(part="A", wall_clock_seconds=wall, core_seconds=core,
                       wall_clock_authorization_shared=300,
                       core_second_authorization_shared=150, measured=True)
    R["finished_at_utc"] = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
    R["validity"] = dict(
        status=("completed_valid" if n_pass == 4 else
                "completed_valid_with_per_cell_data_availability_outcome"),
        certificate=dict(kind="none",
                         reason=("Pure measurement / re-analysis run. No "
                                 "discrete-log solve and no factor-base "
                                 "relation is claimed, so no solution "
                                 "certificate applies (docs/claims-and-"
                                 "verification.md).")),
        reading_rule_applied=False, branch_named=False,
        conclusion_drawn=False)

    with open(os.path.join(args.out_dir, "low_k_recompute_results.json"), "w") as fh:
        json.dump(R, fh, indent=1)
    log(f"[partA] done wall={wall:.4f}s core={core:.4f}s")
    return 0


if __name__ == "__main__":
    sys.exit(main())

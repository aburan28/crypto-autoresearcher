#!/usr/bin/env python3
"""Inverse-variance-weighted (IVW) combination of already-committed per-shard
matched-pair point estimates, as an alternative to the existing
concatenated-histogram pooled estimate.

TASK-20260815-e61cca (executor) / BATCH-174014 / GOAL-HQC-001 / EXP-HQC-982268,
Part B. Authorized by DEC-20260814-3f429d's next_actions (adopting the Red
Team's required_controls item 1, TASK-20260814-a49f1c). Pre-registered design
in design.md Section 6 (WRITTEN AND FROZEN BEFORE THIS SCRIPT WAS RUN).

PERFORMS NO NEW SAMPLING. Reads ONLY already-committed values from
TASK-20260809-a79e4f's matched_pair_results.json:
  (a) stage_1.matched_pair.per_shard.shard_5000 / shard_6000 (T=5,000 each)
  (b) stage_2.matched_pair.per_shard.shard_8001 / shard_8002 (T=10,000 each)
and computes, at every k in the intersection of the pair's own evaluable_k
ranges:
  w_i        = 1 / se_paired_i^2
  diff_ivw   = sum(w_i * diff_i) / sum(w_i)
  se_ivw     = 1 / sqrt(sum(w_i))
reported ALONGSIDE (never replacing) the existing concatenated-histogram
pooled estimate at the same k (stage_1/stage_2 .matched_pair.primary_cell_k17
.pooled, and the corresponding non-k17 cells via .matched_pair.pooled).

Claim tier: TOY, hard ceiling. PS-R3 only. Observations only -- no
conclusion is drawn about whether the pooling-convention asymmetry
(EV-HQC-469c08 O8) is real bias.

Re-run:
    PYTHONDONTWRITEBYTECODE=1 python3 ivw_pooling_check.py --out-dir .
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import platform
import resource
import subprocess
import sys
import time

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.abspath(os.path.join(HERE, *([".."] * 7)))

PRIOR_RESULTS_JSON = os.path.join(
    REPO, "coordination", "goals", "GOAL-HQC-001", "batches", "BATCH-412513",
    "tasks", "TASK-20260809-a79e4f", "matched_pair_results.json")

M = 17
K_RANGE_AUTHORIZED = list(range(2, 27))


def sha256_file(path: str) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as fh:
        for blk in iter(lambda: fh.read(1 << 20), b""):
            h.update(blk)
    return h.hexdigest()


def core_seconds() -> float:
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
                dirty=bool(porcelain), dirty_paths=porcelain.splitlines()[:40])


def per_shard_by_k(stats: dict) -> dict:
    """{k: dict(diff=..., se_paired=...)} from a matched_pair_stats-shaped
    committed dict."""
    ks = stats["ks"]
    return {k: dict(diff=stats["diff"][i], se_paired=stats["se_paired"][i])
            for i, k in enumerate(ks)}


def ivw_combine(by_k_a: dict, by_k_b: dict, ks_authorized):
    """IVW combination of two shards' own per-k point estimates, at every k
    in the intersection of both shards' own reported ks, intersected with
    ks_authorized. w_i = 1/se_paired_i^2; diff_ivw = sum(w_i*diff_i)/sum(w_i);
    se_ivw = 1/sqrt(sum(w_i))."""
    ks_common = sorted(set(by_k_a) & set(by_k_b) & set(ks_authorized))
    out = {}
    for k in ks_common:
        a = by_k_a[k]
        b = by_k_b[k]
        se_a, se_b = a["se_paired"], b["se_paired"]
        diff_a, diff_b = a["diff"], b["diff"]
        if se_a is None or se_b is None or se_a <= 0 or se_b <= 0 \
                or diff_a is None or diff_b is None:
            out[k] = dict(diff_ivw=None, se_ivw=None, w_a=None, w_b=None,
                          reason="non-finite or non-positive se_paired at this k")
            continue
        w_a = 1.0 / (se_a ** 2)
        w_b = 1.0 / (se_b ** 2)
        diff_ivw = (w_a * diff_a + w_b * diff_b) / (w_a + w_b)
        se_ivw = 1.0 / np.sqrt(w_a + w_b)
        out[k] = dict(diff_ivw=float(diff_ivw), se_ivw=float(se_ivw),
                      w_a=float(w_a), w_b=float(w_b))
    return dict(ks_common=ks_common, by_k=out)


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("--out-dir", default=HERE)
    args = ap.parse_args(argv)
    out_path = os.path.join(args.out_dir, "ivw_pooling_check_results.json")

    t_wall0, c_wall0 = time.time(), core_seconds()
    R = {
        "task_id": "TASK-20260815-e61cca",
        "role": "executor",
        "experiment_id": "EXP-HQC-982268",
        "hypothesis_id": "H-HQC-18d1b4",
        "goal": "GOAL-HQC-001",
        "batch": "BATCH-174014",
        "claim_tier": "toy",
        "part": "B",
        "scope_statement": (
            "TOY, hard ceiling. PS-R3 only. PURE RECOMPUTATION on "
            "already-committed data -- NO new _t_shard call anywhere in "
            "this script. Reads ONLY TASK-20260809-a79e4f's committed "
            "matched_pair_results.json. Observations only; no conclusion "
            "is drawn about whether the pooling-convention asymmetry is "
            "real bias."),
        "design_reference": "design.md Section 6, written and frozen before this run",
        "started_at_utc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "command": " ".join([sys.executable] + sys.argv),
        "git": git_state(),
        "environment": dict(
            python=sys.version, python_executable=sys.executable,
            platform=platform.platform(), machine=platform.machine(),
            numpy=np.__version__, cpu_count=os.cpu_count(),
            affinity=len(os.sched_getaffinity(0))),
        "ivw_formula": "w_i = 1/se_paired_i^2; diff_ivw = sum(w_i*diff_i)/"
                       "sum(w_i); se_ivw = 1/sqrt(sum(w_i))",
        "no_new_sampling": True,
    }

    prior_sha256 = sha256_file(PRIOR_RESULTS_JSON)
    R["provenance"] = dict(
        prior_results_json_path=os.path.relpath(PRIOR_RESULTS_JSON, REPO),
        prior_results_json_sha256=prior_sha256,
        source_note="This sha256 is a self-consistency record only (no "
                     "external pin was pre-declared for this file). It is "
                     "cross-checked against the sha256 Part A "
                     "(shard_8001_8002_discard_prefix.py) measured for the "
                     "SAME file at its own run time, reported in "
                     "run_manifest.yaml.")

    with open(PRIOR_RESULTS_JSON) as fh:
        prior = json.load(fh)

    # ---- (a) shards 5000/6000, stage_1, T=5,000-each ----------------------
    stage1_pershard = prior["stage_1"]["matched_pair"]["per_shard"]
    by_k_5000 = per_shard_by_k(stage1_pershard["shard_5000"])
    by_k_6000 = per_shard_by_k(stage1_pershard["shard_6000"])
    ivw_a = ivw_combine(by_k_5000, by_k_6000, K_RANGE_AUTHORIZED)

    pooled_a_by_k = {}
    pooled_a_stats = prior["stage_1"]["matched_pair"]["pooled"]
    for i, k in enumerate(pooled_a_stats["ks"]):
        pooled_a_by_k[k] = dict(diff=pooled_a_stats["diff"][i],
                                se_paired=pooled_a_stats["se_paired"][i])

    a_report = dict(
        pair="shards_5000_6000", T_each=5000, stage="stage_1",
        source_path="stage_1.matched_pair.per_shard.shard_5000 / shard_6000",
        pooled_source_path="stage_1.matched_pair.primary_cell_k17.pooled "
                           "(k=17) / stage_1.matched_pair.pooled (all k)",
        ks_common=ivw_a["ks_common"],
        by_k=[dict(k=k,
                   diff_ivw=ivw_a["by_k"][k].get("diff_ivw"),
                   se_ivw=ivw_a["by_k"][k].get("se_ivw"),
                   diff_pooled_concatenated=pooled_a_by_k.get(k, {}).get("diff"),
                   se_pooled_concatenated=pooled_a_by_k.get(k, {}).get("se_paired"),
                   se_ivw_over_se_pooled_concatenated=(
                       ivw_a["by_k"][k]["se_ivw"] / pooled_a_by_k[k]["se_paired"]
                       if (k in pooled_a_by_k and ivw_a["by_k"][k].get("se_ivw") is not None
                           and pooled_a_by_k[k]["se_paired"])
                       else None))
              for k in ivw_a["ks_common"]])

    k17_a = next((row for row in a_report["by_k"] if row["k"] == M), None)
    a_report["k17_summary"] = k17_a

    # ---- (b) shards 8001/8002, stage_2, T=10,000-each ----------------------
    stage2_pershard = prior["stage_2"]["matched_pair"]["per_shard"]
    by_k_8001 = per_shard_by_k(stage2_pershard["shard_8001"])
    by_k_8002 = per_shard_by_k(stage2_pershard["shard_8002"])
    ivw_b = ivw_combine(by_k_8001, by_k_8002, K_RANGE_AUTHORIZED)

    pooled_b_by_k = {}
    pooled_b_stats = prior["stage_2"]["matched_pair"]["pooled"]
    for i, k in enumerate(pooled_b_stats["ks"]):
        pooled_b_by_k[k] = dict(diff=pooled_b_stats["diff"][i],
                                se_paired=pooled_b_stats["se_paired"][i])

    b_report = dict(
        pair="shards_8001_8002", T_each=10000, stage="stage_2",
        source_path="stage_2.matched_pair.per_shard.shard_8001 / shard_8002",
        pooled_source_path="stage_2.matched_pair.primary_cell_k17.pooled "
                           "(k=17) / stage_2.matched_pair.pooled (all k), "
                           "'T=20,000-equivalent' because it is the SE of "
                           "the pooled two-shard dataset at T=10,000 each",
        ks_common=ivw_b["ks_common"],
        by_k=[dict(k=k,
                   diff_ivw=ivw_b["by_k"][k].get("diff_ivw"),
                   se_ivw=ivw_b["by_k"][k].get("se_ivw"),
                   diff_pooled_concatenated=pooled_b_by_k.get(k, {}).get("diff"),
                   se_pooled_concatenated=pooled_b_by_k.get(k, {}).get("se_paired"),
                   se_ivw_over_se_pooled_concatenated=(
                       ivw_b["by_k"][k]["se_ivw"] / pooled_b_by_k[k]["se_paired"]
                       if (k in pooled_b_by_k and ivw_b["by_k"][k].get("se_ivw") is not None
                           and pooled_b_by_k[k]["se_paired"])
                       else None))
              for k in ivw_b["ks_common"]])

    k17_b = next((row for row in b_report["by_k"] if row["k"] == M), None)
    b_report["k17_summary"] = k17_b

    R["ivw_a_shards_5000_6000_T5000_each"] = a_report
    R["ivw_b_shards_8001_8002_T10000_each"] = b_report

    spent_core = core_seconds() - c_wall0
    spent_wall = time.time() - t_wall0
    R["budget"] = dict(
        core_seconds_authorized=500.0, core_seconds_spent=round(spent_core, 3),
        wall_seconds_authorized=1800.0, wall_seconds_spent=round(spent_wall, 3),
        note="Part B performs no _t_shard call; spend is pure recomputation "
             "on already-loaded JSON, expected negligible.")

    ok = (k17_a is not None and k17_a["se_ivw"] is not None
          and k17_b is not None and k17_b["se_ivw"] is not None)
    R["validity"] = dict(
        status="valid_measurement" if ok else "invalid_measurement",
        failure_class=(None if ok else "invalid_measurement"),
        reason=("Both IVW combinations produced a finite se_ivw at k=17 "
                "from already-committed, finite per-shard values."
                if ok else
                "One or both IVW combinations could not produce a finite "
                "se_ivw at k=17 from the committed per-shard values -- see "
                "ivw_a_shards_5000_6000_T5000_each / "
                "ivw_b_shards_8001_8002_T10000_each for detail."))

    R["finished_at_utc"] = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
    with open(out_path, "w") as fh:
        json.dump(R, fh, indent=1)
    print(f"[done] -> {out_path}  core-s={spent_core:.4f}  wall={spent_wall:.4f}s  "
          f"validity={R['validity']['status']}", flush=True)
    print(f"[ivw_a k=17] diff_ivw={k17_a['diff_ivw'] if k17_a else None} "
          f"se_ivw={k17_a['se_ivw'] if k17_a else None} "
          f"se_ivw/se_pooled_concatenated="
          f"{k17_a['se_ivw_over_se_pooled_concatenated'] if k17_a else None}",
          flush=True)
    print(f"[ivw_b k=17] diff_ivw={k17_b['diff_ivw'] if k17_b else None} "
          f"se_ivw={k17_b['se_ivw'] if k17_b else None} "
          f"se_ivw/se_pooled_concatenated="
          f"{k17_b['se_ivw_over_se_pooled_concatenated'] if k17_b else None}",
          flush=True)
    return R


if __name__ == "__main__":
    main()

#!/usr/bin/env python3
"""J1 integrity audit + post-seal J2 comparison for TASK-20260907-b8f8a9.

Reads producer bytes via `git show 13bf12d0b:<path>` only. Does not import or
open source_v2/ file bodies. Does not open execution-report-v2.yaml or
TASK-20260907-fe3512.receipt.yaml.
"""
from __future__ import annotations

import hashlib
import json
import math
import os
import subprocess
from collections import defaultdict

import yaml

SNAP = "13bf12d0b0849f51b15d6d196d628d17fb32f154"
PARENT = "438e251c29069bd5be83e7e1a7fafd626ed8668c"
MAIN = "origin/main"
HERE = os.path.dirname(os.path.abspath(__file__))
SEAL = os.path.join(HERE, "..", "j2_sealed.json")

MIXERS = ("splitmix", "murmur3")
MIXER_FULL = {"splitmix": "splitmix64", "murmur3": "murmur3_fmix64"}
SEEDS = list(range(1, 9))
V1_N24 = {
    1: "RUN-ECDLP-869870-011-N24-s1",
    2: "RUN-ECDLP-869870-012-N24-s2",
    3: "RUN-ECDLP-869870-013-N24-s3",
    4: "RUN-ECDLP-869870-014-N24-s4",
    5: "RUN-ECDLP-869870-015-N24-s5",
}
V1_RUNS = [
    "RUN-ECDLP-869870-001-N20-s1",
    "RUN-ECDLP-869870-002-N20-s2",
    "RUN-ECDLP-869870-003-N20-s3",
    "RUN-ECDLP-869870-004-N20-s4",
    "RUN-ECDLP-869870-005-N20-s5",
    "RUN-ECDLP-869870-006-N22-s1",
    "RUN-ECDLP-869870-007-N22-s2",
    "RUN-ECDLP-869870-008-N22-s3",
    "RUN-ECDLP-869870-009-N22-s4",
    "RUN-ECDLP-869870-010-N22-s5",
    "RUN-ECDLP-869870-011-N24-s1",
    "RUN-ECDLP-869870-012-N24-s2",
    "RUN-ECDLP-869870-013-N24-s3",
    "RUN-ECDLP-869870-014-N24-s4",
    "RUN-ECDLP-869870-015-N24-s5",
    "RUN-ECDLP-869870-016-analysis-stages12",
    "RUN-ECDLP-869870-017-N30-s1",
    "RUN-ECDLP-869870-018-N30-s2",
    "RUN-ECDLP-869870-019-N30-s3",
    "RUN-ECDLP-869870-020-curve-search",
    "RUN-ECDLP-869870-021-curve-s1",
    "RUN-ECDLP-869870-022-curve-s2",
    "RUN-ECDLP-869870-023-curve-s3",
    "RUN-ECDLP-869870-024-analysis-all",
]
V1_SOURCE_FILES = [
    "analysis.py",
    "curve.py",
    "IMPLEMENTATION.md",
    "instrument.py",
    "make_execution_report.py",
    "make_inventory.py",
    "model.py",
    "run_curve.py",
    "run_curve_search.py",
    "run_generic_exact.py",
    "run_generic_sampled.py",
    "run.py",
    "verify_certificate.py",
    "diagnostics/walk_quality_check.out",
    "diagnostics/walk_quality_check.py",
]


def git_show(rev, path):
    p = subprocess.run(
        ["git", "show", f"{rev}:{path}"],
        capture_output=True,
        check=True,
    )
    return p.stdout


def git_rev_parse(rev_path):
    p = subprocess.run(
        ["git", "rev-parse", rev_path], capture_output=True, text=True
    )
    return p.stdout.strip() if p.returncode == 0 else None


def sha256_bytes(b: bytes) -> str:
    return hashlib.sha256(b).hexdigest()


def load_cell(mixer_short, seed):
    rid = f"RUN-ECDLP-869870-V2-{mixer_short}-s{seed}"
    base = f"experiments/EXP-ECDLP-869870/runs/{rid}"
    man = yaml.safe_load(git_show(SNAP, f"{base}/manifest.yaml"))
    summary = json.loads(git_show(SNAP, f"{base}/summary.json"))
    raw = json.loads(git_show(SNAP, f"{base}/raw-result.json"))
    receipt = yaml.safe_load(git_show(SNAP, f"{base}/receipt.yaml"))
    return rid, man, summary, raw, receipt


def main():
    out = {
        "task_id": "TASK-20260907-b8f8a9",
        "snapshot": SNAP,
        "binding_commit": "e2b94c2b41356d435462a452722d4a523fba9cf4",
        "j2_sealed_path": "j2_sealed.json",
        "blind_from_opened": False,
    }
    # ---- J1: parse every v2 run ----
    rows = []
    seen_ids = []
    for ms in MIXERS:
        for seed in SEEDS:
            rid, man, summary, raw, receipt = load_cell(ms, seed)
            seen_ids.append(rid)
            r = man["run"]
            inp = r["inputs"]
            cell = summary["cells"]["a=0.25"]
            fx = cell["fixture"]
            raw_cell = raw["cells"]["a=0.25"]
            oth = fx.get("o_theta_correction") or {}
            row = {
                "run_id": rid,
                "status": r.get("status"),
                "valid": r.get("result", {}).get("valid"),
                "mixer_manifest": inp.get("mixer"),
                "mixer_summary": cell.get("mixer"),
                "seed": inp.get("seed"),
                "walk_projection": inp.get("walk_projection") or cell.get("walk_projection"),
                "walk_key_K": inp.get("walk_key_K"),
                "dp_key_K2": inp.get("dp_key_K2"),
                "walk_key_string": inp.get("walk_key_string"),
                "dp_key_string": inp.get("dp_key_string"),
                "N": inp.get("parameters", {}).get("N"),
                "T": inp.get("parameters", {}).get("T"),
                "a": inp.get("parameters", {}).get("a"),
                "cycle_mass": cell.get("cycle_mass"),
                "cycle_mass_raw": raw_cell.get("cycle_mass"),
                "capped_mass_8W": cell.get("capped_mass_8W"),
                "capped_mass_8W_raw": raw_cell.get("capped_mass_8W"),
                "capped_mass_20W": cell.get("capped_mass_20W"),
                "nDP": cell.get("nDP"),
                "scaled_cost_sampled": fx.get("scaled_cost_sampled_this_seed"),
                "scaled_cost_exact": fx.get("scaled_cost_exact_expectation"),
                "scaled_P": fx.get("scaled_precomp_measured"),
                "topT_share_8W": (cell.get("global_oracle") or {}).get("top_T_share_8W"),
                "hits": fx.get("hits"),
                "total_steps": fx.get("total_steps"),
                "M": fx.get("M"),
                "raw_residual_cost": fx.get("residual_sampled_minus_published_raw")
                or fx.get("residual_sampled_minus_published"),
                "o_theta_correction": oth,
                "receipt_run_id": (receipt.get("run") or {}).get("id")
                if isinstance(receipt, dict)
                else None,
                "command": r.get("code", {}).get("command"),
                "source_dir": r.get("code", {}).get("source_dir"),
                "dirty": r.get("code", {}).get("dirty"),
                "commit": r.get("code", {}).get("commit"),
                "wall_seconds": r.get("timing", {}).get("wall_seconds"),
                "peak_rss_bytes": r.get("resources", {}).get("peak_rss_bytes"),
                "timed_out": r.get("timing", {}).get("timed_out"),
                "manifest_sha256": sha256_bytes(
                    git_show(SNAP, f"experiments/EXP-ECDLP-869870/runs/{rid}/manifest.yaml")
                ),
                "raw_sha256": sha256_bytes(
                    git_show(SNAP, f"experiments/EXP-ECDLP-869870/runs/{rid}/raw-result.json")
                ),
                "summary_sha256": sha256_bytes(
                    git_show(SNAP, f"experiments/EXP-ECDLP-869870/runs/{rid}/summary.json")
                ),
            }
            # recompute scaled_cost from raw hits/steps
            hits = fx.get("hits")
            tot = fx.get("total_steps")
            N, T = 1 << 24, 256
            row["scaled_cost_recomputed_from_hits_steps"] = (
                (tot / hits / math.sqrt(N / T)) if hits else None
            )
            rows.append(row)

    out["v2_run_count"] = len(rows)
    out["v2_run_ids"] = seen_ids
    expected = [
        f"RUN-ECDLP-869870-V2-{ms}-s{s}" for ms in MIXERS for s in SEEDS
    ]
    out["expected_ids"] = expected
    out["missing_ids"] = [x for x in expected if x not in seen_ids]
    out["duplicate_ids"] = [x for x in seen_ids if seen_ids.count(x) > 1]
    out["unexpected_ids"] = [x for x in seen_ids if x not in expected]

    # mixer / seed integrity
    by_mixer = defaultdict(list)
    for row in rows:
        by_mixer[row["mixer_manifest"]].append(row["seed"])
    out["seeds_per_mixer"] = {k: sorted(v) for k, v in by_mixer.items()}
    out["seed_set_ok"] = all(sorted(v) == SEEDS for v in by_mixer.values()) and set(
        by_mixer
    ) == {"splitmix64", "murmur3_fmix64"}

    # walk-projection labels
    proj = defaultdict(set)
    for row in rows:
        proj[row["mixer_manifest"]].add(row["walk_projection"])
    out["walk_projection_by_mixer"] = {k: sorted(v) for k, v in proj.items()}
    out["walk_projection_ok"] = (
        proj.get("splitmix64") == {"top_bits"}
        and proj.get("murmur3_fmix64") == {"mod_N"}
    )

    # cycle/capped mass present
    out["cycle_mass_reported_all"] = all(
        r["cycle_mass"] is not None and r["cycle_mass_raw"] is not None for r in rows
    )
    out["capped_mass_reported_all"] = all(
        r["capped_mass_8W"] is not None and r["capped_mass_8W_raw"] is not None
        for r in rows
    )
    out["cycle_mass_summary_matches_raw"] = all(
        r["cycle_mass"] == r["cycle_mass_raw"] for r in rows
    )
    out["capped_mass_summary_matches_raw"] = all(
        r["capped_mass_8W"] == r["capped_mass_8W_raw"] for r in rows
    )
    out["all_completed_valid"] = all(
        r["status"] == "completed_valid" and r["valid"] is True for r in rows
    )
    out["no_timeouts"] = all(r["timed_out"] is False for r in rows)
    out["params_ok"] = all(
        r["N"] == 16777216 and r["T"] == 256 and r["a"] == 0.25 for r in rows
    )

    # snapshot receipt hash match
    receipt_path = (
        "coordination/goals/GOAL-ECDLP-bbc21f/batches/BATCH-1e7251/"
        "archives/TASK-20260907-f515dd/snapshot-receipt.json"
    )
    # receipt is on e2b94c2b4; also present in worktree. Prefer git show of binding commit.
    rec_bytes = git_show("e2b94c2b41356d435462a452722d4a523fba9cf4", receipt_path)
    receipt_doc = json.loads(rec_bytes)
    bound = receipt_doc["path_sha256"]
    hash_mismatches = []
    for row in rows:
        for kind, field in (
            ("manifest.yaml", "manifest_sha256"),
            ("raw-result.json", "raw_sha256"),
            ("summary.json", "summary_sha256"),
        ):
            key = f"experiments/EXP-ECDLP-869870/runs/{row['run_id']}/{kind}"
            expected_h = bound.get(key)
            actual = row[field]
            if expected_h != actual:
                hash_mismatches.append(
                    {"path": key, "receipt": expected_h, "git_show": actual}
                )
    out["snapshot_path_sha256_mismatches"] = hash_mismatches
    out["snapshot_hashes_match_receipt"] = len(hash_mismatches) == 0

    # v1 spec / source / runs untouched
    v1 = {
        "specification.yaml": {
            "snapshot": git_rev_parse(
                f"{SNAP}:experiments/EXP-ECDLP-869870/specification.yaml"
            ),
            "origin_main": git_rev_parse(
                f"{MAIN}:experiments/EXP-ECDLP-869870/specification.yaml"
            ),
            "parent": git_rev_parse(
                f"{PARENT}:experiments/EXP-ECDLP-869870/specification.yaml"
            ),
            "HEAD": git_rev_parse("HEAD:experiments/EXP-ECDLP-869870/specification.yaml"),
        },
        "source_tree": {
            "snapshot": git_rev_parse(f"{SNAP}:experiments/EXP-ECDLP-869870/source"),
            "origin_main": git_rev_parse(f"{MAIN}:experiments/EXP-ECDLP-869870/source"),
            "parent": git_rev_parse(f"{PARENT}:experiments/EXP-ECDLP-869870/source"),
            "HEAD": git_rev_parse("HEAD:experiments/EXP-ECDLP-869870/source"),
        },
        "source_files": {},
        "v1_run_dirs": {},
    }
    for fn in V1_SOURCE_FILES:
        path = f"experiments/EXP-ECDLP-869870/source/{fn}"
        shas = {
            "snapshot": git_rev_parse(f"{SNAP}:{path}"),
            "origin_main": git_rev_parse(f"{MAIN}:{path}"),
            "parent": git_rev_parse(f"{PARENT}:{path}"),
        }
        v1["source_files"][fn] = shas
    v1_run_mismatch = []
    for rid in V1_RUNS:
        path = f"experiments/EXP-ECDLP-869870/runs/{rid}"
        a = git_rev_parse(f"{SNAP}:{path}")
        b = git_rev_parse(f"{MAIN}:{path}")
        c = git_rev_parse(f"{PARENT}:{path}")
        v1["v1_run_dirs"][rid] = {"snapshot": a, "origin_main": b, "parent": c}
        if not (a and a == b == c):
            v1_run_mismatch.append(rid)
    out["v1_bytes"] = v1
    out["v1_spec_matches_origin_main"] = (
        v1["specification.yaml"]["snapshot"]
        and v1["specification.yaml"]["snapshot"]
        == v1["specification.yaml"]["origin_main"]
        == v1["specification.yaml"]["parent"]
    )
    out["v1_source_matches_origin_main"] = (
        v1["source_tree"]["snapshot"]
        and v1["source_tree"]["snapshot"]
        == v1["source_tree"]["origin_main"]
        == v1["source_tree"]["parent"]
    )
    out["v1_source_files_all_match"] = all(
        s["snapshot"] and s["snapshot"] == s["origin_main"] == s["parent"]
        for s in v1["source_files"].values()
    )
    out["v1_run_dirs_rewritten"] = v1_run_mismatch
    out["v1_run_dirs_untouched"] = len(v1_run_mismatch) == 0

    # splitmix seeds 1-5 vs v1 N24
    det = []
    for seed, v1id in V1_N24.items():
        v2 = next(r for r in rows if r["mixer_manifest"] == "splitmix64" and r["seed"] == seed)
        v1_raw = json.loads(
            git_show(SNAP, f"experiments/EXP-ECDLP-869870/runs/{v1id}/raw-result.json")
        )
        v1_sum = json.loads(
            git_show(SNAP, f"experiments/EXP-ECDLP-869870/runs/{v1id}/summary.json")
        )
        v1h = v1_raw["header"]
        v1c = v1_sum["cells"]["a=0.25"]
        v1fx = v1c["fixture"]["2"]
        rec = {
            "seed": seed,
            "v1_run_id": v1id,
            "v2_run_id": v2["run_id"],
            "walk_key_K_v1": v1h.get("walk_key_K"),
            "walk_key_K_v2": v2["walk_key_K"],
            "dp_key_K2_v1": v1h.get("dp_key_K2"),
            "dp_key_K2_v2": v2["dp_key_K2"],
            "cycle_mass_v1": v1c.get("cycle_mass"),
            "cycle_mass_v2": v2["cycle_mass"],
            "capped_mass_8W_v1": v1c.get("capped_mass_8W"),
            "capped_mass_8W_v2": v2["capped_mass_8W"],
            "nDP_v1": v1c.get("nDP"),
            "nDP_v2": v2["nDP"],
            "scaled_cost_sampled_v1": v1fx.get("scaled_cost_sampled_this_seed"),
            "scaled_cost_sampled_v2": v2["scaled_cost_sampled"],
            "scaled_cost_exact_v1": v1fx.get("scaled_cost_exact_expectation"),
            "scaled_cost_exact_v2": v2["scaled_cost_exact"],
            "scaled_P_v1": v1fx.get("scaled_precomp_measured"),
            "scaled_P_v2": v2["scaled_P"],
            "hits_v1": v1fx.get("hits"),
            "hits_v2": v2["hits"],
            "total_steps_v1": v1fx.get("total_steps"),
            "total_steps_v2": v2["total_steps"],
        }
        rec["keys_match"] = (
            rec["walk_key_K_v1"] == rec["walk_key_K_v2"]
            and rec["dp_key_K2_v1"] == rec["dp_key_K2_v2"]
        )
        rec["basin_fields_match"] = (
            rec["cycle_mass_v1"] == rec["cycle_mass_v2"]
            and rec["capped_mass_8W_v1"] == rec["capped_mass_8W_v2"]
            and rec["nDP_v1"] == rec["nDP_v2"]
        )
        rec["exact_cost_match"] = rec["scaled_cost_exact_v1"] == rec["scaled_cost_exact_v2"]
        rec["sampled_cost_match"] = (
            rec["scaled_cost_sampled_v1"] == rec["scaled_cost_sampled_v2"]
        )
        rec["sampled_hits_steps_match"] = (
            rec["hits_v1"] == rec["hits_v2"] and rec["total_steps_v1"] == rec["total_steps_v2"]
        )
        det.append(rec)
    out["splitmix_s1_s5_vs_v1"] = det
    out["splitmix_s1_s5_keys_match_v1"] = all(x["keys_match"] for x in det)
    out["splitmix_s1_s5_basin_match_v1"] = all(x["basin_fields_match"] for x in det)
    out["splitmix_s1_s5_exact_cost_match_v1"] = all(x["exact_cost_match"] for x in det)
    out["splitmix_s1_s5_sampled_cost_match_v1"] = all(x["sampled_cost_match"] for x in det)

    # per-mixer aggregates from executor raw/summary
    mixer_agg = {}
    for full in ("splitmix64", "murmur3_fmix64"):
        sub = [r for r in rows if r["mixer_manifest"] == full]
        costs = [r["scaled_cost_sampled"] for r in sub]
        exacts = [r["scaled_cost_exact"] for r in sub]
        ps = [r["scaled_P"] for r in sub]
        shares = [r["topT_share_8W"] for r in sub]
        mean_c = sum(costs) / len(costs)
        mean_e = sum(exacts) / len(exacts)
        mean_p = sum(ps) / len(ps)
        mean_s = sum(shares) / len(shares)
        raw_res = mean_c - 1.79
        # O(theta): collect per-row correction if present
        oth_vals = []
        oth_status = []
        for r in sub:
            o = r["o_theta_correction"]
            oth_status.append(
                {
                    "run_id": r["run_id"],
                    "keys": list(o) if isinstance(o, dict) else type(o).__name__,
                    "value": o,
                }
            )
            if isinstance(o, dict):
                for key in (
                    "corrected_scaled_cost",
                    "residual_corrected",
                    "correction",
                    "evaluated",
                    "not_evaluated",
                    "status",
                ):
                    if key in o:
                        oth_vals.append((key, o[key]))
        mixer_agg[full] = {
            "n": len(sub),
            "scaled_cost_sampled_values": costs,
            "scaled_cost_sampled_mean": mean_c,
            "scaled_cost_exact_values": exacts,
            "scaled_cost_exact_mean": mean_e,
            "scaled_P_values": ps,
            "scaled_P_mean": mean_p,
            "topT_share_8W_values": shares,
            "topT_share_8W_mean": mean_s,
            "raw_residual_mean_minus_1.79": raw_res,
            "raw_cost_band_0.10_pass": abs(raw_res) <= 0.10,
            "raw_P_rel_residual": (mean_p - 1.24) / 1.24,
            "raw_P_band_0.12_pass": abs((mean_p - 1.24) / 1.24) <= 0.12,
            "C_max_1_4": 0.39,
            "topT_share_minus_Cmax": mean_s - 0.39,
            "o_theta_per_run": oth_status,
            "recomputed_matches_reported": all(
                abs(r["scaled_cost_recomputed_from_hits_steps"] - r["scaled_cost_sampled"])
                < 1e-12
                for r in sub
            ),
        }
    out["executor_mixer_aggregates"] = mixer_agg

    # ---- J2 post-seal compare ----
    with open(SEAL) as fh:
        seal = json.load(fh)
    sealed_mean = seal["aggregates"]["scaled_cost_mean"]
    exec_mean = mixer_agg["murmur3_fmix64"]["scaled_cost_sampled_mean"]
    out["j2_compare"] = {
        "sealed_mean_scaled_cost": sealed_mean,
        "sealed_raw_residual": seal["aggregates"]["raw_residual_mean_minus_1.79"],
        "sealed_values": seal["aggregates"]["scaled_cost_values"],
        "sealed_key_namespace": seal["parameters"]["key_namespace"],
        "executor_mean_scaled_cost_sampled": exec_mean,
        "executor_mean_scaled_cost_exact": mixer_agg["murmur3_fmix64"][
            "scaled_cost_exact_mean"
        ],
        "executor_values_sampled": mixer_agg["murmur3_fmix64"]["scaled_cost_sampled_values"],
        "delta_sealed_minus_executor_sampled": sealed_mean - exec_mean,
        "copied_prior_1.6814": False,
        "note": (
            "Sealed derivation used validator-b8f8a9 key namespace; executor used "
            "ecdlp-869870-v2|murmur3_fmix64|walk|{seed}. Means are independent "
            "8-key samples of the same stated quantity, not a same-key bit match."
        ),
    }

    # per-row compact table for the report
    out["rows"] = [
        {
            "run_id": r["run_id"],
            "mixer": r["mixer_manifest"],
            "seed": r["seed"],
            "walk_projection": r["walk_projection"],
            "status": r["status"],
            "cycle_mass": r["cycle_mass"],
            "capped_mass_8W": r["capped_mass_8W"],
            "nDP": r["nDP"],
            "scaled_cost_sampled": r["scaled_cost_sampled"],
            "scaled_cost_exact": r["scaled_cost_exact"],
            "scaled_P": r["scaled_P"],
            "topT_share_8W": r["topT_share_8W"],
            "raw_residual_cost": r["raw_residual_cost"],
            "o_theta_correction": r["o_theta_correction"],
            "walk_key_K": r["walk_key_K"],
            "dp_key_K2": r["dp_key_K2"],
            "walk_key_string": r["walk_key_string"],
            "hits": r["hits"],
            "total_steps": r["total_steps"],
            "wall_seconds": r["wall_seconds"],
            "peak_rss_bytes": r["peak_rss_bytes"],
            "recomputed_scaled_cost": r["scaled_cost_recomputed_from_hits_steps"],
        }
        for r in rows
    ]

    dest = os.path.join(HERE, "..", "j1_j2_audit.json")
    with open(dest, "w") as fh:
        json.dump(out, fh, indent=2)
        fh.write("\n")
    print("wrote", dest)
    print("v2_run_count", out["v2_run_count"])
    print("missing", out["missing_ids"])
    print("seed_set_ok", out["seed_set_ok"])
    print("walk_projection_ok", out["walk_projection_ok"])
    print("v1_spec", out["v1_spec_matches_origin_main"])
    print("v1_source", out["v1_source_matches_origin_main"])
    print("v1_runs_untouched", out["v1_run_dirs_untouched"])
    print("splitmix_keys", out["splitmix_s1_s5_keys_match_v1"])
    print("splitmix_basin", out["splitmix_s1_s5_basin_match_v1"])
    print("splitmix_exact", out["splitmix_s1_s5_exact_cost_match_v1"])
    print("splitmix_sampled", out["splitmix_s1_s5_sampled_cost_match_v1"])
    print("hashes_match_receipt", out["snapshot_hashes_match_receipt"])
    for full, a in mixer_agg.items():
        print(
            f"{full}: mean_cost={a['scaled_cost_sampled_mean']:.6f} "
            f"raw_res={a['raw_residual_mean_minus_1.79']:.6f} "
            f"band={a['raw_cost_band_0.10_pass']} "
            f"Pmean={a['scaled_P_mean']:.6f} Pband={a['raw_P_band_0.12_pass']}"
        )
    print(
        "J2 sealed",
        sealed_mean,
        "executor murmur3",
        exec_mean,
        "delta",
        sealed_mean - exec_mean,
    )


if __name__ == "__main__":
    main()

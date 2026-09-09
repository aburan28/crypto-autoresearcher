"""RUN-ECDLP-e962f6-007: the Stage 2 read-only residual re-read.

Re-reads the committed summaries and produces the residual table and the
decay checks. NO re-simulation, NO modification. The sha256 of every
committed file read is recorded, and each is checked against the committed
state (git show HEAD:<path>); any mismatch invalidates the run (the read-only
guarantee failed).

Sources (a = 1/4 cells, cap 8W):
  - EXP-ECDLP-869870 RUN-ECDLP-869870-001..005-N20-s1..s5 (N = 2^20, 5 seeds)
  - EXP-ECDLP-869870 RUN-ECDLP-869870-006..010-N22-s1..s5 (N = 2^22, 5 seeds)
  - EXP-ECDLP-869870 RUN-ECDLP-869870-011..015-N24-s1..s5 (N = 2^24, 5 seeds)
    fields: global_oracle.top_T_share_8W, global_oracle.ratio_to_c_max_numeric,
    global_oracle.model.c_max_numeric, basin_law.survival_slope_8W,
    cycle_mass_frac, capped_mass_8W_frac, exact_mean_online_walk_length_8W
  - EXP-ECDLP-612fb1 RUN-ECDLP-612fb1-002 (N = 2^20: basins.top_T_share,
    basins.C_max_model, basins.x_star_model, basins.cycle_mass_frac,
    basins.capped_mass_frac) as the cross-check of the anchor values.
  - the new anchor RUN-ECDLP-e962f6-002 (N = 2^26).

Per (N, seed): the raw ratio (as committed) and the corrected residual
R(N) = (top_T_share + cycle_mass_frac + capped_mass_8W_frac - C_max(a)) /
C_max(a); the cycle and capped mass are added back because they are not in
the model (confounder of the idea).

Decay checks (frozen contract):
  D1: |R(2^26)| <= 0.15 (the decidable-negative band).
  D2: the per-N median |R| is non-increasing across {2^20, 2^22, 2^24, 2^26}
      up to a 2 percentage-point noise floor (|R(N_next)| <= |R(N_prev)| +
      0.02 at each step).
  D3: the log-log slope of the per-N median |R| versus N, over the points
      with |R| > 0.01, lies in [-0.7, -0.1] (consistent with the predicted
      -1/3); if fewer than three points exceed the 0.01 floor, D3 is
      replaced by D2 alone and the substitution is recorded.

Committed calibration points (read from the contract, not re-derived):
  R(2^20) about -0.072 (seed 1), R(2^22) about -0.013 (seed 1),
  R(2^24) about +0.008 (seed 1).

Observations only; no interpretation.
"""
from __future__ import annotations

import hashlib
import json
import math
import os
import resource
import subprocess
import sys
import time

import numpy as np

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import runcommon as RC  # noqa: E402

C_MAX_1_4 = 0.3889120129663709
X_STAR_1_4 = 0.7423409681771704
D1_BAND = 0.15
D2_NOISE_FLOOR = 0.02
D3_SLOPE_LO, D3_SLOPE_HI = -0.7, -0.1
D3_FLOOR = 0.01
CALIBRATION = {
    "2^20": {"seed": 1, "R": -0.072},
    "2^22": {"seed": 1, "R": -0.013},
    "2^24": {"seed": 1, "R": 0.008},
}
# W per N at a = 1/4 (contract definition W = sqrt(a N / T), T per the
# contract's T list 64, 128, 256, 256 at N = 2^20, 2^22, 2^24, 2^26).
W_PER_N = {20: 64.0, 22: math.sqrt(0.25 * 2 ** 22 / 128), 24: 128.0, 26: 256.0}


def _repo_root() -> str:
    out = subprocess.run(["git", "rev-parse", "--show-toplevel"],
                         capture_output=True, text=True)
    if out.returncode != 0:
        raise RuntimeError("not a git repository: " + out.stderr)
    return out.stdout.strip()


REPO = _repo_root()


def jsonable(o):
    if isinstance(o, dict):
        return {str(k): jsonable(v) for k, v in o.items()}
    if isinstance(o, (list, tuple)):
        return [jsonable(v) for v in o]
    if isinstance(o, (np.integer,)):
        return int(o)
    if isinstance(o, (np.floating,)):
        v = float(o)
        return v if math.isfinite(v) else (None if math.isnan(v) else ("inf" if v > 0 else "-inf"))
    if isinstance(o, (np.bool_,)):
        return bool(o)
    if isinstance(o, (int, float, str, bool)) or o is None:
        return o
    return str(o)


def sha256_file(path: str) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as fh:
        for chunk in iter(lambda: fh.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def committed_sha256(relpath: str) -> str:
    """sha256 of the committed blob at HEAD for a repo-relative path."""
    out = subprocess.run(["git", "show", f"HEAD:{relpath}"], capture_output=True, cwd=REPO)
    if out.returncode != 0:
        return None
    return hashlib.sha256(out.stdout).hexdigest()


def read_committed_summary(relpath: str, files: dict) -> dict:
    """Read a committed summary.json, recording its sha256 and checking it
    against the committed state. Returns the parsed dict."""
    abspath = os.path.join(REPO, relpath)
    read_sha = sha256_file(abspath)
    committed_sha = committed_sha256(relpath)
    files[relpath] = {"sha256_at_read": read_sha, "sha256_committed": committed_sha,
                      "match": bool(read_sha == committed_sha)}
    with open(abspath) as fh:
        return json.load(fh)


def main():
    t0 = time.time()
    run_id = "RUN-ECDLP-e962f6-007"
    if "--run-id" in sys.argv:
        run_id = sys.argv[sys.argv.index("--run-id") + 1]
    files = {}
    rows = []

    # --- the 15 committed 869870 cells (a = 1/4) ------------------------------
    for log2N, prefix, run_lo in ((20, "N20", 1), (22, "N22", 6), (24, "N24", 11)):
        for s in range(1, 6):
            run_no = run_lo + (s - 1)
            rel = f"experiments/EXP-ECDLP-869870/runs/RUN-ECDLP-869870-{run_no:03d}-{prefix}-s{s}/summary.json"
            d = read_committed_summary(rel, files)
            c = d["cells"]["a=0.25"]
            top_T = c["global_oracle"]["top_T_share_8W"]
            ratio_committed = c["global_oracle"]["ratio_to_c_max_numeric"]
            c_max = c["global_oracle"]["model"]["c_max_numeric"]
            cyc = c["cycle_mass_frac"]
            cap = c["capped_mass_8W_frac"]
            slope = c["basin_law"]["survival_slope_8W"]
            meanlen = c["exact_mean_online_walk_length_8W"]
            corrected = top_T + cyc + cap
            R = (corrected - c_max) / c_max
            rows.append({
                "source": "EXP-ECDLP-869870",
                "run_id": f"RUN-ECDLP-869870-{run_no:03d}-{prefix}-s{s}",
                "log2N": log2N, "N": 1 << log2N, "seed": s,
                "top_T_share_8W": top_T,
                "raw_ratio_committed": ratio_committed,
                "raw_ratio_recomputed": top_T / c_max,
                "raw_ratio_agree": bool(abs(ratio_committed - top_T / c_max) < 1e-9),
                "c_max_numeric": c_max,
                "cycle_mass_frac": cyc,
                "capped_mass_8W_frac": cap,
                "corrected_top_T_share": corrected,
                "R_corrected_residual": R,
                "abs_R": abs(R),
                "survival_slope_8W": slope,
                "borel_prediction_slope": -0.5,
                "exact_mean_online_walk_length_8W": meanlen,
                "W_model": W_PER_N[log2N],
            })

    # --- the 612fb1-002 anchor cross-check (N = 2^20) --------------------------
    rel = "experiments/EXP-ECDLP-612fb1/runs/RUN-ECDLP-612fb1-002/summary.json"
    d = read_committed_summary(rel, files)
    b = d["basins"]
    anchor_crosscheck = {
        "run_id": "RUN-ECDLP-612fb1-002",
        "N": d["params"]["N"],
        "top_T_share": b["top_T_share"],
        "C_max_model": b["C_max_model"],
        "x_star_model": b["x_star_model"],
        "cycle_mass_frac": b["cycle_mass_frac"],
        "capped_mass_frac": b["capped_mass_frac"],
        "contract_anchor_c_max_1_4": C_MAX_1_4,
        "contract_anchor_x_star_1_4": X_STAR_1_4,
        "C_max_matches_contract": bool(abs(b["C_max_model"] - C_MAX_1_4) < 1e-12),
        "x_star_matches_contract": bool(abs(b["x_star_model"] - X_STAR_1_4) < 1e-12),
    }

    # --- the new anchor RUN-ECDLP-e962f6-002 (N = 2^26) -------------------------
    anchor_rel = "experiments/EXP-ECDLP-e962f6/runs/RUN-ECDLP-e962f6-002/summary.json"
    anchor_abs = os.path.join(REPO, anchor_rel)
    anchor_sha = sha256_file(anchor_abs)
    with open(anchor_abs) as fh:
        a = json.load(fh)
    files[anchor_rel] = {"sha256_at_read": anchor_sha, "sha256_committed": None,
                         "match": None,
                         "note": "new artifact of this task (not committed); sha256 recorded for traceability, no committed-state check"}
    top_T = a["top_T_share_8W"]
    cyc = a["cycle_mass_frac"]
    cap = a["capped_mass_8W_frac"]
    corrected = top_T + cyc + cap
    R26 = (corrected - C_MAX_1_4) / C_MAX_1_4
    rows.append({
        "source": "EXP-ECDLP-e962f6 (new anchor)",
        "run_id": "RUN-ECDLP-e962f6-002",
        "log2N": 26, "N": 1 << 26, "seed": 1,
        "top_T_share_8W": top_T,
        "raw_ratio_committed": None,
        "raw_ratio_recomputed": top_T / C_MAX_1_4,
        "raw_ratio_agree": None,
        "c_max_numeric": C_MAX_1_4,
        "cycle_mass_frac": cyc,
        "capped_mass_8W_frac": cap,
        "corrected_top_T_share": corrected,
        "R_corrected_residual": R26,
        "abs_R": abs(R26),
        "survival_slope_8W": None,
        "borel_prediction_slope": -0.5,
        "exact_mean_online_walk_length_8W": a["mean_walk_length_capped_8W"],
        "W_model": W_PER_N[26],
    })

    # --- read-only guarantee -----------------------------------------------------
    committed_files = {k: v for k, v in files.items() if v["sha256_committed"] is not None}
    all_match = all(v["match"] for v in committed_files.values())
    n_committed = len(committed_files)

    # --- per-N median |R| and decay checks ---------------------------------------
    per_N = {}
    for log2N in (20, 22, 24, 26):
        vals = [r["abs_R"] for r in rows if r["log2N"] == log2N]
        per_N[log2N] = {"N": 1 << log2N, "n_seeds": len(vals),
                        "abs_R_per_seed": vals, "median_abs_R": float(np.median(vals))}

    d1 = bool(abs(R26) <= D1_BAND)
    d2_steps = []
    d2_ok = True
    for prev, nxt in ((20, 22), (22, 24), (24, 26)):
        m_prev = per_N[prev]["median_abs_R"]
        m_nxt = per_N[nxt]["median_abs_R"]
        ok = bool(m_nxt <= m_prev + D2_NOISE_FLOOR)
        d2_ok = d2_ok and ok
        d2_steps.append({"from": f"2^{prev}", "to": f"2^{nxt}",
                         "median_abs_R_from": m_prev, "median_abs_R_to": m_nxt,
                         "noise_floor": D2_NOISE_FLOOR, "non_increasing_within_floor": ok})
    d2 = bool(d2_ok)

    # D3: log-log slope of per-N median |R| vs N over points with |R| > 0.01
    pts = [(per_N[k]["N"], per_N[k]["median_abs_R"]) for k in (20, 22, 24, 26)
           if per_N[k]["median_abs_R"] > D3_FLOOR]
    d3_substituted = False
    if len(pts) < 3:
        d3_substituted = True
        d3 = {"slope": None, "in_band": None, "n_points": len(pts),
              "substituted_by_D2": True,
              "verdict": "D3 replaced by D2 alone (fewer than three points exceed the 0.01 floor); substitution recorded"}
    else:
        x = np.log([p[0] for p in pts])
        y = np.log([p[1] for p in pts])
        A = np.vstack([x, np.ones_like(x)]).T
        sol, *_ = np.linalg.lstsq(A, y, rcond=None)
        slope = float(sol[0])
        in_band = bool(D3_SLOPE_LO <= slope <= D3_SLOPE_HI)
        d3 = {"slope": slope, "in_band": in_band, "n_points": len(pts),
              "points": [{"N": p[0], "median_abs_R": p[1]} for p in pts],
              "substituted_by_D2": False,
              "verdict": ("slope in [-0.7, -0.1]" if in_band else "slope outside [-0.7, -0.1]")}
    d3_band_ok = bool(d3["in_band"]) if not d3_substituted else d2

    # --- largest |corrected residual| cell (tail check) ---------------------------
    largest = max(rows, key=lambda r: r["abs_R"])

    elapsed = time.time() - t0
    peak_rss = resource.getrusage(resource.RUSAGE_SELF).ru_maxrss

    raw = {
        "run_id": run_id,
        "kind": "stage2_residual_reread",
        "read_only": True,
        "files_read": files,
        "read_only_guarantee": {
            "n_committed_files": n_committed,
            "all_sha256_match_committed_state": bool(all_match),
            "mismatches": [k for k, v in committed_files.items() if not v["match"]],
        },
        "residual_table": rows,
        "anchor_crosscheck_612fb1_002": anchor_crosscheck,
        "per_N_median_abs_R": per_N,
        "decay_checks": {
            "D1": {"check": "|R(2^26)| <= 0.15", "abs_R_2_26": abs(R26), "pass": d1},
            "D2": {"check": "per-N median |R| non-increasing up to a 2pp noise floor",
                   "steps": d2_steps, "pass": d2},
            "D3": d3,
        },
        "calibration_points_contract": CALIBRATION,
        "calibration_note": "read from the contract, not re-derived; compared beside the computed seed-1 values",
        "largest_abs_R_cell": {"run_id": largest["run_id"], "log2N": largest["log2N"],
                               "seed": largest["seed"], "abs_R": largest["abs_R"],
                               "R": largest["R_corrected_residual"]},
        "self_reported": {"elapsed_seconds": round(elapsed, 3), "peak_rss_bytes": int(peak_rss)},
    }

    summary = {
        "run_id": run_id,
        "kind": "stage2_residual_reread",
        "read_only_guarantee_all_match": bool(all_match),
        "n_committed_files": n_committed,
        "R_2_26": R26,
        "abs_R_2_26": abs(R26),
        "D1_pass": d1,
        "D2_pass": d2,
        "D2_steps": d2_steps,
        "D3": d3,
        "per_N_median_abs_R": {f"2^{k}": per_N[k]["median_abs_R"] for k in (20, 22, 24, 26)},
        "anchor_crosscheck_612fb1_002": anchor_crosscheck,
        "calibration_points_contract": CALIBRATION,
        "largest_abs_R_cell": raw["largest_abs_R_cell"],
        "self_reported": raw["self_reported"],
    }

    out = sys.argv[sys.argv.index("--out") + 1]
    os.makedirs(out, exist_ok=True)
    with open(os.path.join(out, "raw-result.json"), "w") as fh:
        json.dump(jsonable(raw), fh)
    with open(os.path.join(out, "summary.json"), "w") as fh:
        json.dump(jsonable(summary), fh, indent=1)

    meta = {
        "run_id": run_id,
        "kind": "stage2_residual_reread",
        "stage": 2,
        "status": "completed_valid" if all_match else "completed_invalid",
        "failure_class": None,
        "validity": "valid" if all_match else "invalid",
        "validity_reason": ("read-only guarantee verified: sha256 match on every committed file read"
                            if all_match else
                            "read-only guarantee FAILED: at least one committed file's sha256 at read time differs from the committed state"),
        "note": ("Stage 2 read-only residual re-read; no re-simulation, no modification. "
                 + ("This run (RUN-008) is the re-run that supersedes the defective RUN-007 "
                    "(implementation error: a path bug resolved committed-file paths against the "
                    "experiment directory instead of the repository root; RUN-007 produced no "
                    "results and is preserved, never edited). It uses the contract's spare run slot."
                    if run_id != "RUN-ECDLP-e962f6-007" else "")),
        "seeds": {"stage2": None, "note": "read-only; no seed"},
        "params": {"a": 0.25, "C_max_1_4": C_MAX_1_4, "N_grid": [20, 22, 24, 26]},
        "protocol_deviations": (
            ["SUPERSESSION: this run (RUN-008) supersedes the defective RUN-007 (implementation "
             "error, no results produced; preserved, never edited). The Stage 2 re-read therefore "
             "resides in RUN-008 (the contract's spare run slot) rather than RUN-007 as named in "
             "the contract's required_artifacts. Routed to the Coordinator."]
            if run_id != "RUN-ECDLP-e962f6-007" else []),
        "source_sha256": RC.source_hashes(),
        "self_reported": raw["self_reported"],
    }
    with open(os.path.join(out, "run-meta.json"), "w") as fh:
        json.dump(meta, fh, indent=1)
    print(f"reread done in {elapsed:.2f}s; files={n_committed} all_match={all_match} "
          f"R26={R26:.6f} D1={d1} D2={d2} D3_slope={d3.get('slope')} "
          f"D3_in_band={d3.get('in_band')} substituted={d3_substituted}", flush=True)
    return 0


if __name__ == "__main__":
    sys.exit(main())

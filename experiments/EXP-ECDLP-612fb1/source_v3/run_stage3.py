"""STAGE 3A / STAGE 3B driver for the v2-to-v3 amendment, Section 4.

One run = one seed at one N.  STAGE 3A is N = 2^20 (T = 64, T_sel = 32) and
STAGE 3B is N = 2^24 (T = 256, T_sel = 128); both sweep the frozen a-grid
{1/16, 1/8, 3/16, 1/4} and the frozen r-grid {2, 4, 8}.  One code path, cell
selection by configuration, exactly as `required_implementation_files` says.

The measurement itself is g3_predicate.py (the Section 3 predicate), which in
turn imports experiments/EXP-ECDLP-612fb1/source_v2/instrument.py UNCHANGED
for the walk map, the DP predicate, the exact-basin closure, the pool
procedure and both selection code paths.  Nothing under source_v2/ is edited.

This file is both the driver and its own run wrapper: source_v2/harness_run.py
is FROZEN and knows only v2's own child kinds, and the amendment's
`required_implementation_files` declares exactly five source_v3 modules, so a
separate v3 harness module would be an undeclared sixth file.  The wrapper
therefore re-executes this module as a child (`--child`) under the contract's
machine-protection limits and writes the manifest around it.  Disclosed in
IMPLEMENTATION.md.

Emits that run's NINE declared artifacts:
  command.txt  manifest.yaml  environment.json  raw-result.json  summary.json
  stdout.log   stderr.log     cost_table.json   basin_histogram.json.gz

Observations only.  No interpretive line is written by this module, and the
G3 verdict table is emitted before every other block in stdout and in
summary.json.  Certificate kind: none -- nothing here is solved or certified.
"""
from __future__ import annotations

import argparse
import datetime as dt
import gzip
import hashlib
import json
import os
import platform
import resource
import subprocess
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))
EXP_DIR = os.path.dirname(HERE)
REPO = os.path.abspath(os.path.join(EXP_DIR, "..", ".."))
EXP_ID = "EXP-ECDLP-612fb1"
AMENDMENT = "experiments/EXP-ECDLP-612fb1/amendments/v2_to_v3.yaml"

# Machine protection, copied verbatim from the amendment's Section 10 budget.
WALL_LIMIT = 3600                       # seconds, per run
MEM_LIMIT_BYTES = 8 * (1 << 30)         # 8 GB peak RSS ceiling, per run
WORKERS = 1                             # maximum_workers: 1

if HERE not in sys.path:
    sys.path.insert(0, HERE)
import g3_predicate as G  # noqa: E402

STAGES = {
    "3A": {"n_bits": 20, "name": "N = 2^20 replication anchor"},
    "3B": {"n_bits": 24, "name": "N = 2^24 exact-basin G3 measurement, with all controls"},
}


# ---------------------------------------------------------------------------
# provenance helpers
# ---------------------------------------------------------------------------

def sh(cmd) -> str:
    return subprocess.run(cmd, cwd=REPO, capture_output=True, text=True).stdout.strip()


def git_state() -> dict:
    status = sh(["git", "status", "--porcelain", "--untracked-files=all"])
    files = [l for l in status.splitlines() if l.strip()]
    tracked_dirty = [l for l in files if not l.startswith("??")]
    return {
        "commit": sh(["git", "rev-parse", "HEAD"]),
        "branch": sh(["git", "branch", "--show-current"]),
        "dirty": bool(tracked_dirty),
        "dirty_tracked_files": [l[3:] for l in tracked_dirty],
        "untracked_files_count": len([l for l in files if l.startswith("??")]),
        "untracked_under_this_experiment": [l[3:] for l in files
                                            if l.startswith("??") and EXP_ID in l],
    }


def source_hashes() -> dict:
    """Hash-pin BOTH code paths: the v3 driver and the frozen v2 instrument it
    imports.  The v2 hashes let a reviewer confirm source_v2/ was unchanged."""
    out = {}
    for label, d in (("source_v3", HERE), ("source_v2", os.path.join(EXP_DIR, "source_v2"))):
        for name in sorted(os.listdir(d)):
            p = os.path.join(d, name)
            if os.path.isfile(p) and name.endswith(".py"):
                out[f"{label}/{name}"] = hashlib.sha256(open(p, "rb").read()).hexdigest()
    return out


def environment() -> dict:
    import numpy
    env = {
        "operating_system": platform.platform(),
        "kernel": platform.release(),
        "architecture": platform.machine(),
        "python_version": platform.python_version(),
        "python_executable": sys.executable,
        "sage_version": None,
        "dependencies": {"numpy": numpy.__version__, "pyyaml": __import__("yaml").__version__},
        "cpu_model": None,
        "cpu_count": os.cpu_count(),
        "total_ram_bytes": (os.sysconf("SC_PAGE_SIZE") * os.sysconf("SC_PHYS_PAGES")
                            if hasattr(os, "sysconf") else None),
        "threads": {"OMP_NUM_THREADS": "1", "OPENBLAS_NUM_THREADS": "1", "MKL_NUM_THREADS": "1"},
        "workers": WORKERS,
    }
    try:
        for line in open("/proc/cpuinfo"):
            if line.startswith("model name"):
                env["cpu_model"] = line.split(":", 1)[1].strip()
                break
    except OSError:
        pass
    return env


def inference_block() -> dict:
    """Requested policy, the model that ACTUALLY answered, and whether that was
    a fallback.  Recorded, never asserted: `model_verified` is false because no
    `orchestration.adapter doctor --probe` was run in this session, and the
    resolved identifier is what the executing runtime reports about itself.

    The handoff sets fallback_allowed: false and degraded_allowed: false.  No
    requirement of `executor-implementation` (reasoning_effort medium, tool
    use, structured output, context >= 120k, output >= 24k) is unmet, so
    nothing is degraded and no fallback was taken.  The resolved model sits
    ABOVE the policy's floor rather than below it; that is disclosed here
    rather than silently absorbed, per AGENTS.md core rule 11.
    """
    return {
        "requested_policy": "executor-implementation",
        "canonical_policy": "executor-implementation",
        "runtime": "cursor_cloud_agent",
        "backend": "anthropic",
        "provider": "anthropic",
        "resolved_model_id": "claude-opus-5",
        "model_provenance": "self-reported by the executing runtime session; not probed",
        "model_verified": False,
        "model_verification_note": (
            "python3 -m orchestration.adapter doctor --probe was NOT run in this session; "
            "the identifier is the runtime's own self-report and is unverified configuration"),
        "requested_reasoning_effort": "medium",
        "reasoning_effort_actual": None,
        "reasoning_effort_note": (
            "the task card requests medium; this runtime does not expose a per-task reasoning-effort "
            "setting to the running session, so the actual value is recorded as unknown rather than "
            "asserted to be medium"),
        "policy_requirements_met": True,
        "resolved_above_policy_floor": True,
        "fallback_used": False,
        "fallback_allowed": False,
        "fallback_reason": None,
        "degraded_allowed": False,
        "degraded_requirements": [],
        "independent_session": False,
        "harness_note": ("the run itself is deterministic Python/NumPy seeded by the contract's own "
                         "seed streams; the model wrote and launched the code and read no result "
                         "back into it"),
    }


# ---------------------------------------------------------------------------
# CHILD: the measurement
# ---------------------------------------------------------------------------

def run_child(stage: str, seed: int, outdir: str) -> int:
    n_bits = STAGES[stage]["n_bits"]
    t_run = time.time()

    a_grid = list(G.A_GRID)
    r_grid = list(G.R_GRID)
    P0 = G.make_params(n_bits, a_grid[0], seed)
    T = P0.T
    T_sel = G.t_sel_of(T)

    params = {
        "stage": stage, "stage_name": STAGES[stage]["name"],
        "amendment": AMENDMENT, "amendment_section": "4 (stage_plan) / 3 (g3_predicate)",
        "n_bits": n_bits, "N": P0.N, "T": T, "T_sel": T_sel,
        "T_sel_rule": "floor(T/2)",
        "a_grid": a_grid, "r_grid": r_grid, "seed": seed,
        "declared_seed_set": list(G.SEED_SET),
        "reading": "P1 (frozen v2 instrument)",
        "basins": "exact",
        "g3_threshold": f">= {G.G3_PASS_THRESHOLD} of {len(G.SEED_SET)} seeds (v2's frozen rule)",
        "selection_weight": "w(d) = S_d + 4*W*h_d, ties by seeded key ascending (pool evidence only)",
        "seeds": {
            "walk_key_seed": seed,
            "precomputation_restart_stream": seed,
            "tiebreak_permutation_stream": P0.seed_tiebreak,
            "null_a_relabelling_stream": P0.seed_null_a,
        },
    }

    cells = {}
    histograms = {}
    timings = {}
    for a in a_grid:
        t_a = time.time()
        P = G.make_params(n_bits, a, seed)
        basins = G.exact_basins(P)
        struct = G.basin_structure(basins)
        histograms[f"a={a:.6f}"] = {
            "a": a, "N": P.N, "seed": seed,
            "dp_count": struct["dp_count"],
            "basin_size_histogram_count_by_size": struct["histogram"],
        }
        cell = {
            "a": a,
            "modeled": {"W": P.W, "theta": P.theta, "cap": P.cap},
            "top_share_T_sel": G.top_share(basins, T_sel),
            "top_share_T": G.top_share(basins, T),
            "basin_structure": {k: v for k, v in struct.items() if k != "histogram"},
            "by_r": {},
        }
        for r in r_grid:
            cell["by_r"][str(r)] = G.measure_cell(P, basins, r)
        del basins
        cells[f"a={a:.6f}"] = cell
        timings[f"a={a:.6f}"] = round(time.time() - t_a, 3)
        line = " ".join(
            f"r={r}:margin={cell['by_r'][str(r)]['margin']:+.9f}" for r in r_grid)
        print(f"[measure] a={a:.6f} TopShare(T_sel)={cell['top_share_T_sel']:.9f} {line} "
              f"({timings[f'a={a:.6f}']:.2f}s)", flush=True)

    # --- the G3 verdict table, computed and printed BEFORE every other block
    verdict_rows = []
    for a in a_grid:
        c = cells[f"a={a:.6f}"]
        for r in r_grid:
            m = c["by_r"][str(r)]
            verdict_rows.append({
                "N": P0.N, "a": a, "r": r, "T_sel": T_sel, "seed": seed,
                "top_share_T_sel": m["top_share_T_sel"],
                "static_cov": m["static_cov"],
                "margin": m["margin"],
                "g3_this_seed": m["g3"],
                "note": ("single-seed row; the >= 4-of-5 per-cell verdict is formed in "
                         "STAGE 3C over all five seeds"),
            })

    checks = {
        "exact_coverage_non_exceedance": {
            "requirement": "StaticCov(T,r) and StaticCovNull(T,r) never exceed TopShare(T)",
            "violations": [
                {"a": a, "r": r, "which": which}
                for a in a_grid for r in r_grid
                for which, key in (("static", "exact_coverage_exceeds_top_share_T"),
                                   ("static_null", "exact_coverage_null_exceeds_top_share_T"))
                if cells[f"a={a:.6f}"]["by_r"][str(r)][key]
            ],
        },
        "null_b_set_identity": {
            "requirement": "the two frozen v2 selection code paths select identical DP sets",
            "violations": [
                {"a": a, "r": r}
                for a in a_grid for r in r_grid
                if not cells[f"a={a:.6f}"]["by_r"][str(r)]["null_b_set_identical"]
            ],
        },
        "seed_integrity": {
            "seed_declared": seed,
            "seed_in_declared_set": seed in G.SEED_SET,
            "cells_measured": len(a_grid) * len(r_grid),
            "cells_expected": len(a_grid) * len(r_grid),
        },
    }
    checks["exact_coverage_non_exceedance"]["passed"] = not checks["exact_coverage_non_exceedance"]["violations"]
    checks["null_b_set_identity"]["passed"] = not checks["null_b_set_identity"]["violations"]
    checks["seed_integrity"]["passed"] = bool(
        checks["seed_integrity"]["seed_in_declared_set"]
        and checks["seed_integrity"]["cells_measured"] == checks["seed_integrity"]["cells_expected"])

    print("[g3_verdict_table] " + json.dumps(verdict_rows), flush=True)
    print("[checks] " + json.dumps(checks), flush=True)

    # --- raw-result.json: DETERMINISTIC.  No timing, no timestamp, no path.
    # Two runs at the same seed and commit produce byte-identical content, so
    # its sha256 is itself the determinism check (see analyze_v3.py and the
    # execution report).
    raw = {
        "schema": "EXP-ECDLP-612fb1 v3 measurement run raw result",
        "certificate": {"kind": "none",
                        "note": "pure measurement run; nothing is solved or certified"},
        "params": params,
        "cells": cells,
        "checks": checks,
    }
    with open(os.path.join(outdir, "raw-result.json"), "w") as fh:
        json.dump(raw, fh, indent=1, sort_keys=True)

    # --- summary.json: the SAME cells object, verdict table first ----------
    summary = {
        "g3_verdict_table_single_seed": verdict_rows,
        "checks": checks,
        "certificate": {"kind": "none"},
        "params": params,
        "cells": cells,
        "headline_metrics": {
            f"a={a:.6f}|r={r}": {
                "margin": cells[f"a={a:.6f}"]["by_r"][str(r)]["margin"],
                "top_share_T_sel": cells[f"a={a:.6f}"]["by_r"][str(r)]["top_share_T_sel"],
                "static_cov": cells[f"a={a:.6f}"]["by_r"][str(r)]["static_cov"],
                "margin_null": cells[f"a={a:.6f}"]["by_r"][str(r)]["margin_null"],
                "g3_this_seed": cells[f"a={a:.6f}"]["by_r"][str(r)]["g3"],
            }
            for a in a_grid for r in r_grid
        },
        "timing_seconds_by_a": timings,
        "elapsed_seconds": round(time.time() - t_run, 3),
    }
    with open(os.path.join(outdir, "summary.json"), "w") as fh:
        json.dump(summary, fh, indent=1, sort_keys=True)

    # --- cost_table.json: MEASURED and MODELED never share a column --------
    cost = {
        "note": ("MEASURED and MODELED quantities are kept in separate blocks, per the "
                 "amendment's required_artifacts_per_run note: W, theta and cap are MODELED; "
                 "every count, coverage, margin, bit count and resource measurement is MEASURED."),
        "modeled": {
            f"a={a:.6f}": {
                "W": cells[f"a={a:.6f}"]["modeled"]["W"],
                "theta": cells[f"a={a:.6f}"]["modeled"]["theta"],
                "cap": cells[f"a={a:.6f}"]["modeled"]["cap"],
                "formula": "W = sqrt(a*N/T); theta = 1/W; cap = ceil(8*W)",
            } for a in a_grid
        },
        "measured": {
            f"a={a:.6f}|r={r}": {
                "generating_walks": cells[f"a={a:.6f}"]["by_r"][str(r)]["pool"]["generating_walks"],
                "capped_walks": cells[f"a={a:.6f}"]["by_r"][str(r)]["pool"]["capped_walks"],
                "capped_walk_fraction": cells[f"a={a:.6f}"]["by_r"][str(r)]["pool"]["capped_walk_fraction"],
                "pool_size_distinct_dps": cells[f"a={a:.6f}"]["by_r"][str(r)]["pool"]["pool_size_distinct_dps"],
                "P_group_ops": cells[f"a={a:.6f}"]["by_r"][str(r)]["pool"]["P_group_ops"],
                "P_over_sqrt_NT": cells[f"a={a:.6f}"]["by_r"][str(r)]["pool"]["P_over_sqrt_NT"],
                "selection_int_ops_counted_path": cells[f"a={a:.6f}"]["by_r"][str(r)]["selection_int_ops_counted_path"],
                "top_share_T_sel": cells[f"a={a:.6f}"]["by_r"][str(r)]["top_share_T_sel"],
                "top_share_T": cells[f"a={a:.6f}"]["by_r"][str(r)]["top_share_T"],
                "static_cov": cells[f"a={a:.6f}"]["by_r"][str(r)]["static_cov"],
                "static_cov_null": cells[f"a={a:.6f}"]["by_r"][str(r)]["static_cov_null"],
                "margin": cells[f"a={a:.6f}"]["by_r"][str(r)]["margin"],
                "margin_null": cells[f"a={a:.6f}"]["by_r"][str(r)]["margin_null"],
                **cells[f"a={a:.6f}"]["by_r"][str(r)]["bits"],
            } for a in a_grid for r in r_grid
        },
        "measured_basin_structure": {
            f"a={a:.6f}": cells[f"a={a:.6f}"]["basin_structure"] for a in a_grid
        },
        "measured_timing_seconds_by_a": timings,
    }
    with open(os.path.join(outdir, "cost_table.json"), "w") as fh:
        json.dump(cost, fh, indent=1, sort_keys=True)

    # --- basin_histogram.json.gz (mtime pinned so the file is reproducible)
    payload = json.dumps({"params": {k: params[k] for k in ("stage", "n_bits", "N", "T", "T_sel", "seed")},
                          "histograms_by_a": histograms}, sort_keys=True).encode()
    with open(os.path.join(outdir, "basin_histogram.json.gz"), "wb") as fh:
        with gzip.GzipFile(filename="", mode="wb", fileobj=fh, mtime=0) as gz:
            gz.write(payload)

    print(f"[done] stage={stage} seed={seed} elapsed={summary['elapsed_seconds']:.2f}s", flush=True)
    return 0


# ---------------------------------------------------------------------------
# PARENT: the run wrapper
# ---------------------------------------------------------------------------

def validity(outdir: str) -> tuple:
    """Apply the amendment's own invalidation rules to the child's output."""
    reasons = []
    sp = os.path.join(outdir, "summary.json")
    rp = os.path.join(outdir, "raw-result.json")
    if not os.path.exists(sp) or not os.path.exists(rp):
        return False, "summary.json or raw-result.json missing", {}
    s = json.load(open(sp))
    raw = json.load(open(rp))
    if raw["cells"] != s["cells"]:
        reasons.append("raw-result.json disagrees with summary.json cell for cell "
                       "(invalidation rule 3)")
    ch = s.get("checks", {})
    if not ch.get("exact_coverage_non_exceedance", {}).get("passed"):
        reasons.append("StaticCov or StaticCovNull exceeds TopShare(T): impossible by "
                       "disjointness (invalidation rule 4)")
    if not ch.get("null_b_set_identity", {}).get("passed"):
        reasons.append("NULL_B_G3 selection-set difference: bookkeeping leak "
                       "(invalidation rule 5)")
    if not ch.get("seed_integrity", {}).get("passed"):
        reasons.append("seed integrity check failed (invalidation rule 3)")
    return (len(reasons) == 0), ("; ".join(reasons) if reasons else None), s.get("headline_metrics", {})


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--stage", required=True, choices=sorted(STAGES))
    ap.add_argument("--seed", type=int, required=True)
    ap.add_argument("--run-id")
    ap.add_argument("--child", action="store_true")
    ap.add_argument("--outdir")
    args = ap.parse_args()

    if args.child:
        return run_child(args.stage, args.seed, args.outdir)

    if not args.run_id:
        raise SystemExit("--run-id is required in wrapper mode")
    if args.seed not in G.SEED_SET:
        raise SystemExit(f"seed {args.seed} is outside the contract's declared seed set {G.SEED_SET}")
    outdir = os.path.join(EXP_DIR, "runs", args.run_id)
    if os.path.exists(outdir):
        raise SystemExit(f"refusing to overwrite existing run directory {outdir} "
                         "(run records are immutable)")
    os.makedirs(outdir)

    cmd = [sys.executable, os.path.join(HERE, "run_stage3.py"), "--child",
           "--stage", args.stage, "--seed", str(args.seed), "--outdir", outdir]
    rel = " ".join(c.replace(REPO + "/", "") for c in cmd)
    with open(os.path.join(outdir, "command.txt"), "w") as fh:
        fh.write(f"cd {REPO}\n"
                 f"OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 MKL_NUM_THREADS=1 PYTHONHASHSEED=0 \\\n"
                 f"  timeout {WALL_LIMIT}s {rel}\n"
                 f"# wrapper invocation that produced this run directory:\n"
                 f"# python3 experiments/EXP-ECDLP-612fb1/source_v3/run_stage3.py "
                 f"--run-id {args.run_id} --stage {args.stage} --seed {args.seed}\n")

    gs = git_state()
    envd = environment()
    with open(os.path.join(outdir, "environment.json"), "w") as fh:
        json.dump({**envd, "git": gs, "source_sha256": source_hashes(),
                   "wall_limit_seconds": WALL_LIMIT,
                   "memory_limit_bytes": MEM_LIMIT_BYTES}, fh, indent=1)

    env = dict(os.environ, OMP_NUM_THREADS="1", OPENBLAS_NUM_THREADS="1",
               MKL_NUM_THREADS="1", PYTHONHASHSEED="0")
    started = dt.datetime.now(dt.timezone.utc)
    t0 = time.monotonic()
    r0 = resource.getrusage(resource.RUSAGE_CHILDREN)

    def limits():
        resource.setrlimit(resource.RLIMIT_AS, (MEM_LIMIT_BYTES, MEM_LIMIT_BYTES))

    status, failure, rc = "completed_valid", None, 0
    with open(os.path.join(outdir, "stdout.log"), "w") as so, \
         open(os.path.join(outdir, "stderr.log"), "w") as se:
        try:
            proc = subprocess.run(cmd, cwd=REPO, env=env, stdout=so, stderr=se,
                                  timeout=WALL_LIMIT, preexec_fn=limits)
            rc = proc.returncode
        except subprocess.TimeoutExpired:
            rc = None
            status = "failed_infrastructure"
            failure = (f"wall clock exceeded {WALL_LIMIT} s; process killed "
                       f"(resource_exhaustion). NOT a result and NOT negative evidence "
                       f"(AGENTS.md core rule 5).")
    wall = time.monotonic() - t0
    finished = dt.datetime.now(dt.timezone.utc)
    r1 = resource.getrusage(resource.RUSAGE_CHILDREN)
    peak_rss = int(r1.ru_maxrss * 1024)
    cpu = (r1.ru_utime - r0.ru_utime) + (r1.ru_stime - r0.ru_stime)

    if rc not in (0, None):
        status = "failed_infrastructure"
        failure = (f"child exited with code {rc} (crash / dependency failure). NOT a result "
                   f"and NOT negative evidence (AGENTS.md core rule 5).")

    valid, reason, metrics = False, failure, {}
    if status == "completed_valid":
        valid, reason, metrics = validity(outdir)
        if not valid:
            status = "completed_invalid"

    if peak_rss > MEM_LIMIT_BYTES:
        status = "failed_infrastructure"
        valid = False
        reason = (f"peak RSS {peak_rss} B exceeded the {MEM_LIMIT_BYTES} B ceiling "
                  f"(resource_exhaustion). NOT a result.")

    if not os.path.exists(os.path.join(outdir, "raw-result.json")):
        with open(os.path.join(outdir, "raw-result.json"), "w") as fh:
            json.dump({"status": status, "note": "child produced no raw result",
                       "failure": failure}, fh, indent=1)
    for missing in ("summary.json", "cost_table.json"):
        if not os.path.exists(os.path.join(outdir, missing)):
            with open(os.path.join(outdir, missing), "w") as fh:
                json.dump({"status": status, "note": f"child produced no {missing}",
                           "failure": failure}, fh, indent=1)
    hp = os.path.join(outdir, "basin_histogram.json.gz")
    if not os.path.exists(hp):
        with open(hp, "wb") as fh:
            with gzip.GzipFile(filename="", mode="wb", fileobj=fh, mtime=0) as gz:
                gz.write(json.dumps({"status": status,
                                     "note": "child produced no histogram",
                                     "failure": failure}).encode())

    seeds = None
    sp = os.path.join(outdir, "summary.json")
    if os.path.exists(sp):
        try:
            seeds = json.load(open(sp)).get("params", {}).get("seeds")
        except json.JSONDecodeError:
            seeds = None

    failure_class = None
    if not valid:
        if status == "failed_infrastructure":
            failure_class = "resource_exhaustion" if rc is None or peak_rss > MEM_LIMIT_BYTES \
                else "infrastructure_error"
        else:
            failure_class = "invalid_measurement"

    manifest = {"run": {
        "id": args.run_id,
        "experiment_id": EXP_ID,
        "amendment": AMENDMENT,
        "amendment_status_at_dispatch": "approved (committed on the working branch)",
        "stage": args.stage,
        "stage_name": STAGES[args.stage]["name"],
        "purpose": ("STAGE 3A replication anchor at N = 2^20" if args.stage == "3A"
                    else "STAGE 3B primary G3 measurement at N = 2^24 with all controls"),
        "status": status,
        "task_id": "TASK-20260907-aad514",
        "batch_id": "BATCH-8f3e86",
        "goal_id": "GOAL-ECDLP-bbc21f",
        "code": {
            "commit": gs["commit"], "branch": gs["branch"], "dirty": gs["dirty"],
            "dirty_tracked_files": gs["dirty_tracked_files"],
            "untracked_under_this_experiment": gs["untracked_under_this_experiment"],
            "command": open(os.path.join(outdir, "command.txt")).read().strip(),
            "source_path": "experiments/EXP-ECDLP-612fb1/source_v3/",
            "source_sha256": source_hashes(),
            "reuses_frozen": ("experiments/EXP-ECDLP-612fb1/source_v2/instrument.py imported "
                              "unchanged; source_v2/ hashes are pinned above so a reviewer can "
                              "confirm it was not edited"),
            "note": ("source_v3/ and this run directory are untracked new files at this commit; "
                     "the snapshot archive task commits them. Source files are hash-pinned above."),
        },
        "inference": inference_block(),
        "environment": envd,
        "inputs": {
            "curve_id": None,
            "seed": args.seed,
            "seeds": seeds,
            "parameters": {
                "stage": args.stage, "n_bits": STAGES[args.stage]["n_bits"],
                "a_grid": list(G.A_GRID), "r_grid": list(G.R_GRID),
                "T_sel_rule": "floor(T/2)", "basins": "exact",
                "reading": "P1 (frozen v2 instrument)",
            },
        },
        "timing": {
            "started_at": started.isoformat(), "finished_at": finished.isoformat(),
            "wall_seconds": round(wall, 3), "timing_source": "wrapper monotonic clock",
            "wall_limit_seconds": WALL_LIMIT, "wall_within_limit": bool(wall <= WALL_LIMIT),
        },
        "resources": {
            "peak_rss_bytes": peak_rss, "peak_rss_gib": round(peak_rss / (1 << 30), 4),
            "cpu_seconds": round(cpu, 3),
            "memory_limit_bytes": MEM_LIMIT_BYTES,
            "peak_rss_within_limit": bool(peak_rss <= MEM_LIMIT_BYTES),
            "workers": WORKERS,
            "peak_rss_source": "resource.getrusage(RUSAGE_CHILDREN).ru_maxrss",
        },
        "result": {
            "metrics": metrics, "valid": valid, "validity_status": status,
            "invalid_reason": reason, "failure_class": failure_class,
            "certificate": {"kind": "none", "verified": None, "verifier": None,
                            "note": ("pure measurement run; nothing is solved or certified, so "
                                     "the amendment requires no solution certificate")},
            "interpretation": ("NONE. This record contains observations only; the Coordinator "
                               "interprets after independent review."),
        },
        "artifacts": {
            "command": "command.txt", "manifest": "manifest.yaml",
            "environment": "environment.json", "raw_result": "raw-result.json",
            "summary": "summary.json", "stdout": "stdout.log", "stderr": "stderr.log",
            "cost_table": "cost_table.json", "basin_histogram": "basin_histogram.json.gz",
        },
    }}
    import yaml
    with open(os.path.join(outdir, "manifest.yaml"), "w") as fh:
        yaml.safe_dump(manifest, fh, sort_keys=False, default_flow_style=False, width=100)

    print(f"{args.run_id}: {status} wall={wall:.2f}s cpu={cpu:.2f}s "
          f"peak_rss={peak_rss / (1 << 30):.3f}GiB" + (f" reason={reason}" if reason else ""))
    return 0


if __name__ == "__main__":
    sys.exit(main())

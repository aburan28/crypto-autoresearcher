"""Run one EXP-ECDLP-56117b measurement cell and write the declared artifacts."""

from __future__ import annotations

import gzip
import hashlib
import json
import os
import platform
import resource
import subprocess
import sys
import time
import traceback
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

sys.dont_write_bytecode = True
sys.path.insert(0, str(Path(__file__).resolve().parent))

import numpy as np
import yaml

from g3_predicate import (
    N_FROZEN,
    T_FROZEN,
    T_SEL_FROZEN,
    frozen_params,
    run_cell,
)

REPO_ROOT = Path(__file__).resolve().parents[3]
CELLS: dict[str, dict[str, Any]] = {
    "a16r2": {"a": 0.0625, "r": 2, "null_a": True},
    "a8r2": {"a": 0.125, "r": 2, "null_a": False},
    "a4r2": {"a": 0.25, "r": 2, "null_a": False},
    "a16r4": {"a": 0.0625, "r": 4, "null_a": False},
    "a16r8": {"a": 0.0625, "r": 8, "null_a": False},
    "a8r4": {"a": 0.125, "r": 4, "null_a": False},
    "a8r8": {"a": 0.125, "r": 8, "null_a": False},
}

INFERENCE = {
    "requested_policy": "executor-implementation",
    "canonical_policy": "executor-implementation",
    "backend": "cursor",
    "provider": "cursor",
    "resolved_model_id": "grok-4.6",
    "model_provenance": "operator-supplied",
    "model_verified": False,
    "requested_reasoning_effort": "medium",
    "reasoning_effort": "medium",
    "fallback_used": True,
    "fallback_reason": (
        "Handoff requested executor-implementation (orchestration.adapter "
        "resolve: anthropic:claude-sonnet-5, effort=medium). This executor "
        "session is served by Cursor Grok 4.6. Handoff fallback_allowed is "
        "false; recorded as a protocol_deviation rather than a silent "
        "identifier substitution. Numeric results of this run are produced "
        "by deterministic Python/C with no model in the measurement loop."
    ),
    "degraded_requirements": [],
    "independent_session": False,
    "adapter_version": "1.1.0",
    "config_digest": None,
    "session_model_self_report": "Cursor Grok 4.6",
    "numeric_results": "deterministic_code",
}

FORBIDDEN_PATHS = [
    "experiments/EXP-ECDLP-612fb1/source_v2/",
    "experiments/EXP-ECDLP-612fb1/source_v3/",
    "experiments/EXP-ECDLP-6ac801/source/",
    "any existing instrument.py in this lineage",
]


def utc_now() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%S.%fZ")


def git_state(repo: Path) -> dict[str, Any]:
    def run(args: list[str]) -> str:
        p = subprocess.run(
            args, cwd=str(repo), capture_output=True, text=True, check=False
        )
        return p.stdout.strip()

    commit = run(["git", "rev-parse", "HEAD"])
    porcelain = run(["git", "status", "--porcelain"])
    dirty = bool(porcelain)
    return {
        "commit": commit,
        "dirty": dirty,
        "dirty_tree": porcelain.splitlines() if porcelain else [],
        "branch": run(["git", "rev-parse", "--abbrev-ref", "HEAD"]),
    }


def collect_environment() -> dict[str, Any]:
    deps = {"python": sys.version, "numpy": np.__version__, "pyyaml": yaml.__version__}
    gcc = subprocess.run(["gcc", "--version"], capture_output=True, text=True, check=False)
    return {
        "operating_system": platform.platform(),
        "architecture": platform.machine(),
        "hostname": platform.node(),
        "python_version": platform.python_version(),
        "python_implementation": platform.python_implementation(),
        "numpy_version": np.__version__,
        "gcc_version_head": (gcc.stdout.splitlines() or [""])[0],
        "cpu_count": os.cpu_count(),
        "sage_version": None,
        "dependencies": deps,
        "pid": os.getpid(),
    }


def peak_rss_bytes() -> int:
    rss_kb = resource.getrusage(resource.RUSAGE_SELF).ru_maxrss
    return int(rss_kb) * 1024


def cpu_seconds() -> float:
    ru = resource.getrusage(resource.RUSAGE_SELF)
    return float(ru.ru_utime + ru.ru_stime)


def py_json(obj: Any) -> Any:
    if isinstance(obj, dict):
        return {str(k): py_json(v) for k, v in obj.items()}
    if isinstance(obj, (list, tuple)):
        return [py_json(v) for v in obj]
    if isinstance(obj, (np.integer,)):
        return int(obj)
    if isinstance(obj, (np.floating,)):
        return float(obj)
    if isinstance(obj, (np.bool_,)):
        return bool(obj)
    if isinstance(obj, np.ndarray):
        return py_json(obj.tolist())
    if isinstance(obj, Path):
        return str(obj)
    return obj


def write_json(path: Path, data: Any) -> None:
    path.write_text(json.dumps(py_json(data), indent=2, sort_keys=True) + "\n", encoding="utf-8")


def write_yaml(path: Path, data: Any) -> None:
    path.write_text(
        yaml.safe_dump(py_json(data), sort_keys=False, default_flow_style=False),
        encoding="utf-8",
    )


def independence_attestation() -> dict[str, Any]:
    return {
        "unread_forbidden_paths": FORBIDDEN_PATHS,
        "operations_not_performed": ["read", "import", "copy", "sys.path-insert"],
        "selection_used_true_basin_size": False,
        "map_family": (
            "uniform random function on Z_N plus independent Bernoulli(theta) "
            "DP marking (reading P2). mix64/hash64 was not reproduced."
        ),
    }


def run_id_for(cell: str, seed: int) -> str:
    return f"RUN-ECDLP-56117b-{cell}-s{seed}"


def execute_one(
    cell: str,
    seed: int,
    outdir: Path,
    *,
    determinism_repeat: bool = False,
) -> dict[str, Any]:
    if cell not in CELLS:
        raise ValueError(cell)
    spec = CELLS[cell]
    a = float(spec["a"])
    r = int(spec["r"])
    run_id = outdir.name
    outdir.mkdir(parents=True, exist_ok=True)

    cmd = (
        "python3 experiments/EXP-ECDLP-56117b/source/run_cell.py "
        f"--cell {cell} --seed {seed} --outdir {outdir.as_posix()}"
    )
    if determinism_repeat:
        cmd += " --determinism-repeat"
    (outdir / "command.txt").write_text(cmd + "\n", encoding="utf-8")

    stdout_lines: list[str] = []
    stderr_lines: list[str] = []

    def log(msg: str) -> None:
        stdout_lines.append(msg)
        print(msg, flush=True)

    git = git_state(REPO_ROOT)
    env = collect_environment()
    started = utc_now()
    t0 = time.perf_counter()
    log(f"start {run_id} cell={cell} seed={seed} a={a} r={r} N={N_FROZEN}")
    log(f"git commit={git['commit']} dirty={git['dirty']}")

    status = "completed_valid"
    failure_class = None
    invalid_reason = None
    payload: dict[str, Any] | None = None
    histogram: dict[str, Any] | None = None
    determinism: dict[str, Any] | None = None

    try:
        result = run_cell(
            N=N_FROZEN,
            T=T_FROZEN,
            T_sel=T_SEL_FROZEN,
            a=a,
            r=r,
            seed=int(seed),
            compute_null_a=bool(spec["null_a"]),
        )
        payload = result.payload
        histogram = result.histogram
        if payload.get("exact_coverage_exceedance"):
            status = "completed_invalid"
            failure_class = "invalid_measurement"
            invalid_reason = (
                "StaticCov or StaticCovNull exceeded TopShare(T); "
                "impossible by disjointness"
            )
        wall = time.perf_counter() - t0
        rss = peak_rss_bytes()
        if wall > 3600.0:
            status = "failed_infrastructure"
            failure_class = "resource_exhaustion"
            invalid_reason = f"wall_seconds {wall} exceeded 3600"
        if rss > 8 * (1024**3):
            status = "failed_infrastructure"
            failure_class = "resource_exhaustion"
            invalid_reason = f"peak_rss_bytes {rss} exceeded 8 GiB"

        if determinism_repeat and status == "completed_valid":
            log("determinism repeat starting")
            result2 = run_cell(
                N=N_FROZEN,
                T=T_FROZEN,
                T_sel=T_SEL_FROZEN,
                a=a,
                r=r,
                seed=int(seed),
                compute_null_a=bool(spec["null_a"]),
            )
            keys = [
                "margin",
                "top_share_Tsel",
                "static_cov",
                "g3_s",
                "top_share_Tsel_count",
                "static_cov_count",
                "n_dps",
            ]
            diffs = {}
            for k in keys:
                diffs[k] = {
                    "first": payload.get(k),
                    "second": result2.payload.get(k),
                    "equal": payload.get(k) == result2.payload.get(k),
                }
            if "margin_null" in payload:
                diffs["margin_null"] = {
                    "first": payload["margin_null"],
                    "second": result2.payload.get("margin_null"),
                    "equal": payload["margin_null"] == result2.payload.get("margin_null"),
                }
            all_eq = all(v["equal"] for v in diffs.values())
            determinism = {"compared_keys": keys, "all_equal": all_eq, "diffs": diffs}
            log(f"determinism all_equal={all_eq}")
            if not all_eq:
                status = "completed_invalid"
                failure_class = "invalid_measurement"
                invalid_reason = "determinism repeat disagreed on scored quantities"

        log(
            f"margin={payload['margin']!r} g3_s={payload['g3_s']} "
            f"top_share_Tsel={payload['top_share_Tsel']!r} "
            f"static_cov={payload['static_cov']!r}"
        )
        if "margin_null" in payload:
            log(f"margin_null={payload['margin_null']!r}")
        log(f"wall_seconds={wall:.6f} peak_rss_bytes={rss}")
    except MemoryError as exc:
        wall = time.perf_counter() - t0
        rss = peak_rss_bytes()
        status = "failed_infrastructure"
        failure_class = "resource_exhaustion"
        invalid_reason = f"MemoryError: {exc}"
        stderr_lines.append(traceback.format_exc())
        payload = payload or {}
        histogram = histogram or {"n_dps": 0, "pairs": []}
    except Exception as exc:
        wall = time.perf_counter() - t0
        rss = peak_rss_bytes()
        status = "failed_infrastructure"
        failure_class = "infrastructure_error"
        invalid_reason = f"{type(exc).__name__}: {exc}"
        stderr_lines.append(traceback.format_exc())
        payload = payload or {}
        histogram = histogram or {"n_dps": 0, "pairs": []}

    finished = utc_now()
    rss = peak_rss_bytes()
    cpu = cpu_seconds()
    valid = status == "completed_valid"

    raw = {
        "run_id": run_id,
        "experiment_id": "EXP-ECDLP-56117b",
        "cell": cell,
        "status": status,
        "failure_class": failure_class,
        "invalid_reason": invalid_reason,
        "certificate": {"kind": "none", "verified": None, "verifier": None},
        "claim_tier": "toy",
        "payload": payload,
        "determinism_check": determinism,
        "timing": {
            "started_at": started,
            "finished_at": finished,
            "wall_seconds": wall,
        },
        "resources": {"peak_rss_bytes": rss, "cpu_seconds": cpu},
    }
    summary = {
        "run_id": run_id,
        "cell": cell,
        "seed": int(seed),
        "a": a,
        "r": r,
        "N": N_FROZEN,
        "T": T_FROZEN,
        "T_sel": T_SEL_FROZEN,
        "status": status,
        "valid": valid,
        "margin": None if not payload else payload.get("margin"),
        "top_share_Tsel": None if not payload else payload.get("top_share_Tsel"),
        "static_cov": None if not payload else payload.get("static_cov"),
        "g3_s": None if not payload else payload.get("g3_s"),
        "margin_null": None if not payload else payload.get("margin_null"),
        "static_cov_null": None if not payload else payload.get("static_cov_null"),
        "exact_coverage_exceedance": None
        if not payload
        else payload.get("exact_coverage_exceedance"),
        "cycle_mass_frac": None
        if not payload
        else (payload.get("mass") or {}).get("cycle_mass_frac"),
        "capped_mass_frac": None
        if not payload
        else (payload.get("mass") or {}).get("capped_mass_frac"),
        "P": None if not payload else (payload.get("pool") or {}).get("P"),
        "generating_walks": None
        if not payload
        else (payload.get("pool") or {}).get("generating_walks"),
        "capped_walk_fraction": None
        if not payload
        else (payload.get("pool") or {}).get("capped_walk_fraction"),
        "P_over_sqrt_NT": None
        if not payload
        else (payload.get("pool") or {}).get("P_over_sqrt_NT"),
        "wall_seconds": wall,
        "peak_rss_bytes": rss,
        "cpu_seconds": cpu,
        "resolver": None
        if not payload
        else (payload.get("mass") or {}).get("resolver"),
    }
    modeled = frozen_params(a)
    cost = {
        "run_id": run_id,
        "modeled": {
            "W": modeled["W"],
            "theta": modeled["theta"],
            "cap": modeled["cap"],
            "N": N_FROZEN,
            "T": T_FROZEN,
            "T_sel": T_SEL_FROZEN,
            "a": a,
            "r": r,
            "sqrt_NT": float(np.sqrt(float(N_FROZEN) * float(T_FROZEN))),
        },
        "measured": {
            "margin": summary["margin"],
            "top_share_Tsel": summary["top_share_Tsel"],
            "static_cov": summary["static_cov"],
            "g3_s": summary["g3_s"],
            "margin_null": summary["margin_null"],
            "P": summary["P"],
            "generating_walks": summary["generating_walks"],
            "capped_walk_fraction": summary["capped_walk_fraction"],
            "P_over_sqrt_NT": summary["P_over_sqrt_NT"],
            "cycle_mass_frac": summary["cycle_mass_frac"],
            "capped_mass_frac": summary["capped_mass_frac"],
            "wall_seconds": wall,
            "peak_rss_bytes": rss,
            "cpu_seconds": cpu,
            "n_dps": None if not payload else payload.get("n_dps"),
        },
        "optimistic_assumptions": [],
        "note": (
            "W, theta and cap are MODELED (frozen table). Every count, "
            "coverage, margin and resource number is MEASURED."
        ),
    }
    manifest = {
        "run": {
            "id": run_id,
            "experiment_id": "EXP-ECDLP-56117b",
            "task_id": "TASK-20260907-b407d8",
            "cell": cell,
            "status": status,
            "code": {
                "commit": git["commit"],
                "dirty": git["dirty"],
                "dirty_tree": git["dirty_tree"],
                "branch": git["branch"],
                "command": cmd,
            },
            "inference": INFERENCE,
            "environment": env,
            "inputs": {
                "curve_id": None,
                "instrument_class": "generic keyed random function on Z_N (reading P2)",
                "seed": int(seed),
                "parameters": {
                    "N": N_FROZEN,
                    "T": T_FROZEN,
                    "T_sel": T_SEL_FROZEN,
                    "a": a,
                    "r": r,
                    "W_modeled": modeled["W"],
                    "theta_modeled": modeled["theta"],
                    "cap_modeled": modeled["cap"],
                    "compute_null_a": bool(spec["null_a"]),
                },
                "seed_streams": None if not payload else payload.get("streams"),
            },
            "timing": {
                "started_at": started,
                "finished_at": finished,
                "wall_seconds": wall,
            },
            "resources": {"peak_rss_bytes": rss, "cpu_seconds": cpu},
            "result": {
                "metrics": {
                    "margin": summary["margin"],
                    "top_share_Tsel": summary["top_share_Tsel"],
                    "static_cov": summary["static_cov"],
                    "g3_s": summary["g3_s"],
                    "margin_null": summary["margin_null"],
                },
                "valid": valid,
                "invalid_reason": invalid_reason,
                "failure_class": failure_class,
                "certificate": {"kind": "none", "verified": None, "verifier": None},
            },
            "independence_attestation": independence_attestation(),
            "artifacts": {
                "raw-result.json": "raw-result.json",
                "summary.json": "summary.json",
                "cost_table.json": "cost_table.json",
                "basin_histogram.json.gz": "basin_histogram.json.gz",
            },
            "claim_tier": "toy",
        }
    }

    write_json(outdir / "raw-result.json", raw)
    write_json(outdir / "summary.json", summary)
    write_json(outdir / "cost_table.json", cost)
    write_json(outdir / "environment.json", env)
    write_yaml(outdir / "manifest.yaml", manifest)
    (outdir / "stdout.log").write_text("\n".join(stdout_lines) + "\n", encoding="utf-8")
    (outdir / "stderr.log").write_text(
        "\n".join(stderr_lines) if stderr_lines else "", encoding="utf-8"
    )
    hist_bytes = json.dumps(py_json(histogram), sort_keys=True).encode("utf-8")
    with gzip.open(outdir / "basin_histogram.json.gz", "wb") as fh:
        fh.write(hist_bytes)

    return {"status": status, "summary": summary, "run_id": run_id}


def main(argv: list[str] | None = None) -> int:
    import argparse

    p = argparse.ArgumentParser()
    p.add_argument("--cell", required=True, choices=sorted(CELLS))
    p.add_argument("--seed", type=int, required=True)
    p.add_argument("--outdir", type=Path, required=True)
    p.add_argument("--determinism-repeat", action="store_true")
    args = p.parse_args(argv)
    outdir = args.outdir
    if not outdir.is_absolute():
        outdir = (Path.cwd() / outdir).resolve()
    execute_one(
        args.cell, args.seed, outdir, determinism_repeat=args.determinism_repeat
    )
    return 0


if __name__ == "__main__":
    sys.path.insert(0, str(Path(__file__).resolve().parent))
    raise SystemExit(main())

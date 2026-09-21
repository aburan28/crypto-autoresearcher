#!/usr/bin/env python3
"""Run the frozen noncanonical outer-translator development contract."""
from __future__ import annotations

import argparse
import hashlib
import importlib.util
import json
import os
import platform
import resource
import subprocess
import sys
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


SCRIPT_PATH = Path(__file__).resolve()
EXPERIMENT_ROOT = SCRIPT_PATH.parents[1]
REPO_ROOT = SCRIPT_PATH.parents[3]
GENERATOR_PATH = SCRIPT_PATH.with_name("outer_translator.py")
VERIFIER_PATH = SCRIPT_PATH.with_name("verify_outer_translator.py")
DEVELOPMENT_CONFIG = {
    "bit_sizes": [8, 10, 12],
    "seeds": [3317584535, 2246822507],
    "floor_families": [
        "x_interval",
        "square_map",
        "rational_union",
        "random_x",
        "random_scalar",
        "scalar_progression",
    ],
    "translator_families": [
        "x_interval",
        "square_map",
        "rational_union",
        "random_x",
    ],
    "partial_d3_numerators": [1, 1, 1],
    "partial_d3_denominators": [8, 4, 2],
    "batch_multipliers": [1, 16],
    "batch_replicates": 2,
    "coordinate_targets": 2,
    "occupancy_lambda": 0.5,
    "rho_trials": 2,
}


def load_generator() -> Any:
    name = "outer_translator_run_wrapper_generator"
    spec = importlib.util.spec_from_file_location(name, GENERATOR_PATH)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot load generator: {GENERATOR_PATH}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


GENERATOR = load_generator()


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def write_json_atomic(path: Path, value: Any) -> None:
    temporary = path.with_name(f".{path.name}.tmp")
    temporary.write_text(
        json.dumps(value, indent=2, sort_keys=True, allow_nan=False) + "\n",
        encoding="utf-8",
    )
    os.replace(temporary, path)


def git_output(*args: str) -> str:
    result = subprocess.run(
        ["git", *args],
        cwd=REPO_ROOT,
        check=False,
        capture_output=True,
        text=True,
    )
    if result.returncode != 0:
        raise RuntimeError(f"git {' '.join(args)} failed: {result.stderr.strip()}")
    return result.stdout.rstrip("\n")


def git_snapshot() -> dict[str, Any]:
    status = git_output("status", "--porcelain=v1", "--untracked-files=all")
    return {
        "commit": git_output("rev-parse", "HEAD"),
        "branch": git_output("branch", "--show-current"),
        "status_porcelain": status.splitlines(),
        "clean": not status,
    }


def source_hashes() -> dict[str, str]:
    hashes = GENERATOR.bound_source_hashes()
    expected = sha256_file(SCRIPT_PATH)
    if hashes.get("run_wrapper_sha256") != expected:
        raise AssertionError("generator source binding omits or misbinds run wrapper")
    return hashes


def child_usage() -> dict[str, int | float | str]:
    usage = resource.getrusage(resource.RUSAGE_CHILDREN)
    max_rss_raw = int(usage.ru_maxrss)
    max_rss_bytes = max_rss_raw if sys.platform == "darwin" else max_rss_raw * 1024
    return {
        "user_cpu_seconds": usage.ru_utime,
        "system_cpu_seconds": usage.ru_stime,
        "max_rss_raw": max_rss_raw,
        "max_rss_raw_units": "bytes" if sys.platform == "darwin" else "KiB",
        "max_rss_bytes": max_rss_bytes,
        "minor_page_faults": usage.ru_minflt,
        "major_page_faults": usage.ru_majflt,
        "block_inputs": usage.ru_inblock,
        "block_outputs": usage.ru_oublock,
        "voluntary_context_switches": usage.ru_nvcsw,
        "involuntary_context_switches": usage.ru_nivcsw,
    }


def usage_delta(before: dict[str, Any], after: dict[str, Any]) -> dict[str, Any]:
    cumulative = {
        key: after[key] - before[key]
        for key in (
            "user_cpu_seconds",
            "system_cpu_seconds",
            "minor_page_faults",
            "major_page_faults",
            "block_inputs",
            "block_outputs",
            "voluntary_context_switches",
            "involuntary_context_switches",
        )
    }
    cumulative.update(
        {
            "child_max_rss_after_raw": after["max_rss_raw"],
            "child_max_rss_after_raw_units": after["max_rss_raw_units"],
            "child_max_rss_after_bytes": after["max_rss_bytes"],
            "max_rss_scope": (
                "process-level RUSAGE_CHILDREN high-water mark after command; "
                "not phase-isolated and not subtracted"
            ),
        }
    )
    return cumulative


def generator_command(raw_result: Path) -> list[str]:
    config = DEVELOPMENT_CONFIG
    return [
        sys.executable,
        "-B",
        str(GENERATOR_PATH),
        "--bit-sizes",
        *map(str, config["bit_sizes"]),
        "--seeds",
        *map(str, config["seeds"]),
        "--floor-families",
        *config["floor_families"],
        "--translator-families",
        *config["translator_families"],
        "--partial-d3-numerators",
        *map(str, config["partial_d3_numerators"]),
        "--partial-d3-denominators",
        *map(str, config["partial_d3_denominators"]),
        "--batch-multipliers",
        *map(str, config["batch_multipliers"]),
        "--batch-replicates",
        str(config["batch_replicates"]),
        "--coordinate-targets",
        str(config["coordinate_targets"]),
        "--occupancy-lambda",
        str(config["occupancy_lambda"]),
        "--rho-trials",
        str(config["rho_trials"]),
        "--allow-development",
        "--output",
        str(raw_result),
    ]


def verifier_command(raw_result: Path, receipt: Path) -> list[str]:
    return [
        sys.executable,
        "-B",
        str(VERIFIER_PATH),
        "--input",
        str(raw_result),
        "--output",
        str(receipt),
        "--allow-development",
    ]


def run_child(
    command: list[str],
    environment: dict[str, str],
    stdout_path: Path,
    stderr_path: Path,
) -> dict[str, Any]:
    before = child_usage()
    started_at = utc_now()
    started = time.perf_counter()
    result = subprocess.run(
        command,
        cwd=REPO_ROOT,
        env=environment,
        check=False,
        capture_output=True,
        text=True,
    )
    wall_seconds = time.perf_counter() - started
    after = child_usage()
    stdout_path.write_text(result.stdout, encoding="utf-8")
    stderr_path.write_text(result.stderr, encoding="utf-8")
    return {
        "command": command,
        "started_at_utc": started_at,
        "finished_at_utc": utc_now(),
        "wall_seconds": wall_seconds,
        "exit_code": result.returncode,
        "resource_usage": usage_delta(before, after),
        "stdout": stdout_path.name,
        "stderr": stderr_path.name,
    }


def artifact_hashes(output_dir: Path) -> dict[str, str]:
    return {
        str(path.relative_to(output_dir)): sha256_file(path)
        for path in sorted(output_dir.rglob("*"))
        if path.is_file()
        and path.name != "run-manifest.json"
        and not path.name.startswith("._")
    }


def run_development(output_dir: Path) -> int:
    output_dir = output_dir.resolve()
    if output_dir.exists():
        raise FileExistsError(f"refusing existing run directory: {output_dir}")
    git = git_snapshot()
    if not git["clean"]:
        raise RuntimeError("development wrapper requires a clean git worktree")

    hashes_at_start = source_hashes()
    output_dir.mkdir(parents=True)
    raw_result = output_dir / "raw-result.json"
    receipt = output_dir / "verification-receipt.json"
    generator_stdout = output_dir / "generator.stdout.log"
    generator_stderr = output_dir / "generator.stderr.log"
    verifier_stdout = output_dir / "verifier.stdout.log"
    verifier_stderr = output_dir / "verifier.stderr.log"
    environment = os.environ.copy()
    python_path = [str(REPO_ROOT / "src"), str(SCRIPT_PATH.parent)]
    if environment.get("PYTHONPATH"):
        python_path.append(environment["PYTHONPATH"])
    environment["PYTHONPATH"] = os.pathsep.join(python_path)
    environment["PYTHONDONTWRITEBYTECODE"] = "1"
    generate = generator_command(raw_result)
    verify = verifier_command(raw_result, receipt)
    prelog = {
        "protocol": "EXP-ECDLP-OUTER-TRANSLATOR-001-development-run-v1",
        "created_at_utc": utc_now(),
        "development_only": True,
        "canonical_authorized": False,
        "overwrite_policy": "new output directory required",
        "repository": str(REPO_ROOT),
        "git": git,
        "host": {
            "platform": platform.platform(),
            "python": sys.version,
            "python_executable": sys.executable,
        },
        "environment": {
            "PYTHONDONTWRITEBYTECODE": environment["PYTHONDONTWRITEBYTECODE"],
            "PYTHONPATH": environment["PYTHONPATH"],
        },
        "configuration": DEVELOPMENT_CONFIG,
        "generator_command": generate,
        "verifier_command": verify,
        "source_hashes": hashes_at_start,
    }
    write_json_atomic(output_dir / "prelog.json", prelog)

    overall_usage_before = child_usage()
    overall_started = time.perf_counter()
    generator_run = run_child(
        generate, environment, generator_stdout, generator_stderr
    )
    verifier_run = None
    if generator_run["exit_code"] == 0:
        verifier_run = run_child(
            verify, environment, verifier_stdout, verifier_stderr
        )
    else:
        verifier_stdout.write_text("", encoding="utf-8")
        verifier_stderr.write_text(
            "verifier not run because generator failed\n", encoding="utf-8"
        )
    overall_wall_seconds = time.perf_counter() - overall_started
    overall_usage_after = child_usage()
    hashes_at_end = source_hashes()
    source_stable = hashes_at_end == hashes_at_start

    if generator_run["exit_code"] != 0:
        status = "GENERATOR_FAILED"
        return_code = generator_run["exit_code"] or 1
    elif verifier_run is None or verifier_run["exit_code"] != 0:
        status = "VERIFIER_FAILED"
        return_code = 2
    elif not source_stable:
        status = "SOURCE_DRIFT"
        return_code = 3
    else:
        status = "VERIFIED_DEVELOPMENT_RUN"
        return_code = 0
    manifest = {
        "protocol": "EXP-ECDLP-OUTER-TRANSLATOR-001-development-run-v1",
        "finished_at_utc": utc_now(),
        "status": status,
        "exit_code": return_code,
        "development_only": True,
        "canonical_authorized": False,
        "git": git,
        "generator": generator_run,
        "verifier": verifier_run,
        "overall_wall_seconds": overall_wall_seconds,
        "overall_resource_usage": usage_delta(
            overall_usage_before, overall_usage_after
        ),
        "source_hashes_at_start": hashes_at_start,
        "source_hashes_at_end": hashes_at_end,
        "source_hashes_stable": source_stable,
        "artifact_hashes": artifact_hashes(output_dir),
        "boundary": (
            "Generated toy curves and exact development configuration only; "
            "verified output is not an exponent result or ECDLP break."
        ),
    }
    write_json_atomic(output_dir / "run-manifest.json", manifest)
    print(output_dir / "run-manifest.json")
    return return_code


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output-dir", type=Path, required=True)
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv)
    return run_development(args.output_dir)


if __name__ == "__main__":
    raise SystemExit(main())

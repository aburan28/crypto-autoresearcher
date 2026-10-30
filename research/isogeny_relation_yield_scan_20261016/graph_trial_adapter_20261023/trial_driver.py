"""Supervised adapter for one already prepared graph arm.

The repository trial supervisor owns admission and the run directory. This
adapter never selects an arm, issues a seed, or approves an experiment.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import resource
import signal
import time
import subprocess
import sys
from pathlib import Path

import psutil

STUDY = Path(__file__).resolve().parents[1]
WRAPPER = STUDY / "preparation/execute_graph_prepared.py"
MATERIALIZER = STUDY / "graph_input_schedule_20261023/materialize.py"
SOLVER = STUDY / "graph_solve_candidate_20261023/solve.py"
SOLVE_CHECKER = STUDY / "graph_solve_candidate_20261023/check.py"


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def write_once(path: Path, value: object) -> None:
    with path.open("x", encoding="utf-8") as stream:
        json.dump(value, stream, indent=2, sort_keys=True)
        stream.write("\n")


def run_measured(command: list[str], stdout, stderr, timeout: int) -> tuple[object, dict, bool]:
    """Run a child with bounded wall time and retain its CPU and sampled RSS."""
    started = time.monotonic()
    cpu_before = resource.getrusage(resource.RUSAGE_CHILDREN)
    process = subprocess.Popen(command, stdin=subprocess.DEVNULL, stdout=stdout,
                               stderr=stderr, start_new_session=True)
    observed_cpu = 0.0
    peak_rss = 0
    timed_out = False
    process_handle = psutil.Process(process.pid)
    try:
        while process.poll() is None:
            watched = [process_handle]
            try:
                watched.extend(process_handle.children(recursive=True))
            except (psutil.Error, PermissionError, OSError):
                pass
            current_cpu = 0.0
            current_rss = 0
            for child in watched:
                try:
                    times = child.cpu_times()
                    current_cpu += times.user + times.system
                    current_rss += child.memory_info().rss
                except (psutil.Error, PermissionError, OSError):
                    continue
            observed_cpu = max(observed_cpu, current_cpu)
            peak_rss = max(peak_rss, current_rss)
            if time.monotonic() - started >= timeout:
                os.killpg(process.pid, signal.SIGKILL)
                process.wait()
                timed_out = True
                break
            time.sleep(0.02)
        elapsed = time.monotonic() - started
        cpu_after = resource.getrusage(resource.RUSAGE_CHILDREN)
        # RUSAGE_CHILDREN catches short-lived children; sampled tree CPU is a cross-check.
        child_cpu = cpu_after.ru_utime + cpu_after.ru_stime - cpu_before.ru_utime - cpu_before.ru_stime
        return process, {"wall_seconds": elapsed, "peak_sampled_rss_bytes": peak_rss,
                         "child_process_cpu_seconds": max(child_cpu, observed_cpu)}, timed_out
    finally:
        if process.poll() is None:
            os.killpg(process.pid, signal.SIGKILL)
            process.wait()


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    source = parser.add_mutually_exclusive_group(required=True)
    source.add_argument("--input", type=Path)
    source.add_argument("--arm-key")
    parser.add_argument("--prepared-manifest", type=Path)
    for name in ("collector", "count-verifier", "out"):
        parser.add_argument("--" + name, type=Path, required=True)
    parser.add_argument("--admission", type=Path)
    parser.add_argument("--binding", type=Path)
    parser.add_argument("--prepared-worker-admission", type=Path)
    parser.add_argument("--stage", choices=("discovery", "confirmation", "solve"), default="discovery")
    parser.add_argument("--base-root-file", type=Path)
    parser.add_argument("--target-root-file", type=Path)
    parser.add_argument("--verifier-root-file", type=Path)
    parser.add_argument("--commitment", type=Path)
    parser.add_argument("--control", action="store_true")
    parser.add_argument("--watchdog-seconds", type=int, default=1800)
    parser.add_argument("--memory-gib", type=int, default=4)
    parser.add_argument("--sage", type=Path)
    args = parser.parse_args()
    if args.control == (args.admission is not None or args.prepared_worker_admission is not None):
        parser.error("use --control alone or provide a scientific admission")
    if args.control and args.binding is not None:
        parser.error("control mode does not accept a materializer binding")
    if args.control and args.prepared_worker_admission is not None:
        parser.error("control mode does not accept worker admission")
    if args.control and args.arm_key is not None:
        parser.error("control mode accepts only an existing bounded prepared input")
    if args.input is not None:
        if args.prepared_manifest is None or any(value is not None for value in
                (args.base_root_file, args.target_root_file, args.verifier_root_file, args.commitment)):
            parser.error("prepared-input mode requires --prepared-manifest and no materialization roots")
        if args.prepared_worker_admission is not None:
            if args.admission is not None:
                parser.error("worker admission cannot be combined with private admission")
            if args.binding is None:
                parser.error("worker admission requires a public prepared binding")
            args.admission = args.prepared_worker_admission
    else:
        if (args.prepared_manifest is not None or args.binding is not None or
                any(value is None for value in
                    (args.base_root_file, args.target_root_file, args.verifier_root_file, args.commitment))):
            parser.error("scheduled-arm mode requires three roots and a commitment, without a supplied binding")
    if args.watchdog_seconds < 1 or args.memory_gib < 1:
        parser.error("resource guards must be positive")
    if args.stage == "solve" and (args.sage is None or not args.sage.is_file()):
        parser.error("solve stage requires the bound Sage executable")
    out = args.out.resolve()
    if not out.is_dir() or any(out.iterdir()):
        parser.error("trial supervisor must provide an empty, existing --out directory")
    paths = {name: getattr(args, name.replace("-", "_")).resolve() for name in
             ("collector", "count-verifier")}
    materializer_receipt = None
    if args.arm_key is not None:
        paths.update({name: getattr(args, name.replace("-", "_")).resolve() for name in
                      ("base-root-file", "target-root-file", "verifier-root-file", "commitment")})
        prepared_dir = out / "prepared"
        command = [sys.executable, str(MATERIALIZER), "prepare", "--arm-key", args.arm_key,
                   "--stage", args.stage,
                   "--base-root-file", str(paths["base-root-file"]),
                   "--target-root-file", str(paths["target-root-file"]),
                   "--verifier-root-file", str(paths["verifier-root-file"]),
                   "--commitment", str(paths["commitment"]), "--output-dir", str(prepared_dir)]
        with (out / "materializer.stdout").open("xb") as stdout, (out / "materializer.stderr").open("xb") as stderr:
            process = subprocess.run(command, stdin=subprocess.DEVNULL, stdout=stdout,
                                     stderr=stderr, check=False)
        if process.returncode != 0:
            raise RuntimeError(f"scheduled arm materialization failed with exit {process.returncode}")
        paths["input"] = prepared_dir / "prepared.txt"
        paths["prepared-manifest"] = prepared_dir / "manifest.json"
        paths["binding"] = prepared_dir / "binding.json"
        materializer_receipt = {
            "command": command, "return_code": process.returncode,
            "stdout_sha256": sha(out / "materializer.stdout"),
            "stderr_sha256": sha(out / "materializer.stderr"),
            "binding_sha256": sha(paths["binding"]),
        }
    else:
        paths["input"] = args.input.resolve()
        paths["prepared-manifest"] = args.prepared_manifest.resolve()
    if args.admission is not None:
        paths["admission"] = args.admission.resolve()
        admission_doc = json.loads(paths["admission"].read_text())
        if args.arm_key is not None and admission_doc.get("schema") != "ectd.graph-study-admission.v1":
            parser.error("scheduled-arm materialization requires study-level admission")
        expected_stage = {"discovery": 0, "confirmation": 1, "solve": 2}[args.stage]
        if args.arm_key is not None and admission_doc.get("execution_stage") != expected_stage:
            parser.error("trial stage differs from the admitted execution stage")
        if args.stage == "solve":
            binary = admission_doc.get("binaries", {})
            if (args.sage.resolve() != Path(binary.get("sage_path", "")).resolve() or
                    not args.sage.is_file() or sha(args.sage.resolve()) != binary.get("sage_sha256")):
                parser.error("Sage executable differs from the stage-2 admission")
        if admission_doc.get("schema") == "ectd.graph-study-admission.v1":
            if "binding" not in paths and args.binding is None:
                parser.error("study admission requires the materializer --binding")
            if "binding" not in paths:
                paths["binding"] = args.binding.resolve()
        elif admission_doc.get("schema") == "ectd.graph-worker-admission.v1":
            if args.arm_key is not None or args.binding is None:
                parser.error("worker admission requires prepared input and public binding")
            paths["binding"] = args.binding.resolve()
            if admission_doc.get("execution_stage") != expected_stage:
                parser.error("trial stage differs from the rootless worker admission")
            if args.stage == "solve":
                binary = admission_doc.get("binaries", {})
                sage_path = Path(binary.get("sage_path", "")).resolve()
                if (args.sage.resolve() != sage_path or not sage_path.is_file() or
                        sha(sage_path) != binary.get("sage_sha256")):
                    parser.error("Sage executable differs from the rootless stage-2 admission")
        elif args.binding is not None:
            parser.error("per-arm admission does not accept a materializer binding")
    prepared = json.loads(paths["prepared-manifest"].read_text())
    if prepared.get("input_sha256") != sha(paths["input"]):
        parser.error("prepared input digest differs")
    command = [sys.executable, str(WRAPPER), "--input", str(paths["input"]),
               "--manifest", str(paths["prepared-manifest"]),
               "--collector", str(paths["collector"]),
               "--count-verifier", str(paths["count-verifier"]),
               "--output", str(out / "attempt"),
               "--watchdog-seconds", str(args.watchdog_seconds),
               "--memory-gib", str(args.memory_gib)]
    if args.control:
        command.append("--control")
    else:
        command += ["--admission", str(paths["admission"])]
        if "binding" in paths:
            command += ["--binding", str(paths["binding"])]
    with (out / "driver.stdout").open("xb") as stdout, (out / "driver.stderr").open("xb") as stderr:
        process = subprocess.run(command, stdin=subprocess.DEVNULL, stdout=stdout, stderr=stderr,
                                 check=False)
    attempt = out / "attempt"
    receipt_path = attempt / "receipt.json"
    receipt = json.loads(receipt_path.read_text()) if receipt_path.is_file() else None
    solve_dir = out / "solve"
    solve_result = None
    solve_check = None
    solve_commands = []
    solver_status = "not_started"
    checker_status = "not_started"
    solver_wall_seconds = 0.0
    checker_wall_seconds = 0.0
    solver_resources = checker_resources = None
    if args.stage == "solve" and process.returncode == 0 and receipt is not None:
        solve_dir.mkdir(mode=0o700)
        prepared = json.loads(paths["prepared-manifest"].read_text())
        gx, gy = map(str, prepared["generator"])
        qx, qy = map(str, prepared["Q"])
        solve_path = solve_dir / "solve.json"
        solver_command = [str(args.sage.resolve()), "-python", str(SOLVER),
                          "--input", str(paths["input"]),
                          "--collector", str(attempt / "collector.stdout"),
                          "--count", str(attempt / "count.stdout"),
                          "--gx", gx, "--gy", gy, "--qx", qx, "--qy", qy,
                          "--out", str(solve_path)]
        solve_commands.append(solver_command)
        solver_started = time.monotonic()
        with (solve_dir / "solver.stdout").open("xb") as stdout, (solve_dir / "solver.stderr").open("xb") as stderr:
            try:
                solver_process, solver_resources, timed_out = run_measured(
                    solver_command, stdout, stderr, args.watchdog_seconds)
                solver_status = ("timeout" if timed_out else
                                 "completed" if solver_process.returncode == 0 else "failed")
            except subprocess.TimeoutExpired:
                solver_process = None
                solver_status = "timeout"
        solver_wall_seconds = time.monotonic() - solver_started
        if solver_process is not None and solver_process.returncode == 0 and solve_path.is_file():
            solve_result = json.loads(solve_path.read_text())
            checker_command = [str(args.sage.resolve()), "-python", str(SOLVE_CHECKER),
                               "--input", str(paths["input"]),
                               "--collector", str(attempt / "collector.stdout"),
                               "--count", str(attempt / "count.stdout"),
                               "--solve", str(solve_path)]
            solve_commands.append(checker_command)
            checker_started = time.monotonic()
            with (solve_dir / "checker.stdout").open("xb") as stdout, (solve_dir / "checker.stderr").open("xb") as stderr:
                try:
                    checker_process, checker_resources, timed_out = run_measured(
                        checker_command, stdout, stderr, args.watchdog_seconds)
                    checker_status = ("timeout" if timed_out else
                                      "completed" if checker_process.returncode == 0 else "failed")
                except subprocess.TimeoutExpired:
                    checker_process = None
                    checker_status = "timeout"
            checker_wall_seconds = time.monotonic() - checker_started
            if checker_process is not None and checker_process.returncode == 0:
                solve_check = json.loads((solve_dir / "checker.stdout").read_text())
        else:
            checker_status = "not_started"
            checker_wall_seconds = 0.0
    def phase_json(name: str) -> object | None:
        path = attempt / f"{name}.stdout"
        if not path.is_file() or not path.stat().st_size:
            return None
        try:
            return json.loads(path.read_text())
        except (UnicodeDecodeError, json.JSONDecodeError):
            return None
    result = {
        "schema": "ectd.graph-trial-result.v1",
        "status": receipt.get("status") if receipt else "missing_receipt",
        "mode": "implementation_control" if args.control else "scientific_trial",
        "prepared": {key: prepared[key] for key in ("stratum", "index", "arm", "stage", "target_count")},
        "digests": {name + "_sha256": sha(path) for name, path in paths.items()},
        "wrapper_sha256": sha(WRAPPER),
        "attempt_receipt_sha256": sha(receipt_path) if receipt else None,
        "input_check": phase_json("input_verify"),
        "rank_check": phase_json("rank_verify"),
    }
    if args.stage == "solve":
        solve_artifacts = {name: sha(solve_dir / name) for name in
                           ("solve.json", "solver.stdout", "solver.stderr",
                            "checker.stdout", "checker.stderr")
                           if (solve_dir / name).is_file()}
        result["complete_solve"] = {
            "status": solve_check.get("status") if solve_check else "solve_or_replay_failed",
            "solver_status": solve_result.get("status") if solve_result else None,
            "solver_process_status": solver_status,
            "solver_wall_seconds": solver_wall_seconds,
            "solver_resources": solver_resources,
            "checker_process_status": checker_status,
            "checker_wall_seconds": checker_wall_seconds,
            "checker_resources": checker_resources,
            "checker": solve_check, "commands": solve_commands,
            "artifacts_sha256": solve_artifacts,
            "solver_sha256": sha(SOLVER), "checker_sha256": sha(SOLVE_CHECKER),
            "sage_sha256": sha(args.sage.resolve()),
        }
    if materializer_receipt is not None:
        result["materializer"] = materializer_receipt
    write_once(out / "raw-result.json", result)
    write_once(out / "manifest.yaml", {
        "schema": "ectd.graph-trial-manifest.v1", "status": result["status"],
        "paths": {name: str(path) for name, path in paths.items()},
        "command": command, "subprocess_return_code": process.returncode,
        "raw_result_sha256": sha(out / "raw-result.json"),
        "attempt_receipt_sha256": result["attempt_receipt_sha256"],
        "driver_stdout_sha256": sha(out / "driver.stdout"),
        "driver_stderr_sha256": sha(out / "driver.stderr"),
        "materializer": materializer_receipt,
        "complete_solve": result.get("complete_solve"),
    })
    expected = "completed_control" if args.control else "completed_unreviewed"
    solve_ok = (args.stage != "solve" or
                (solve_check is not None and solve_check.get("status") in
                 ("valid_censored", "valid_verified_scalar")))
    return 0 if process.returncode == 0 and result["status"] == expected and solve_ok else 1


if __name__ == "__main__":
    raise SystemExit(main())

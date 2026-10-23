"""Bounded, write-once SAT model collection for the prepared k11 binary inputs.

This is an implementation entry point, not an approved experiment. A caller
must supply the frozen limits and invoke it through an approved run contract.
Solver assertions of UNSAT have no independent proof here. Every SAT model is
checked against the serialized XCNF before full-point extraction; a rejected
primary assignment is blocked and charged to the same attempt sequence.
"""

from __future__ import annotations

import argparse
import datetime
import gzip
import hashlib
import json
import math
import platform
import shutil
import subprocess
import sys
import time
from pathlib import Path
from typing import Callable

import psutil

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from tools.icperf_binary_circuit_xcnf_verify import parse, verify_arm  # noqa: E402
from tools.icperf_binary_k11_root_certificate import INPUTS, check, load  # noqa: E402


def digest(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def parse_model(stdout: str, nvars: int) -> list[bool]:
    """Require one explicit, consistent value for every XCNF variable."""
    values: dict[int, bool] = {}
    statuses = []
    for line in stdout.splitlines():
        line = line.strip()
        if line.startswith("s "):
            statuses.append(line)
        elif line.startswith("v "):
            for token in line[2:].split():
                lit = int(token)
                if not lit:
                    continue
                var = abs(lit)
                if not 1 <= var <= nvars or (var in values and values[var] != (lit > 0)):
                    raise ValueError("out-of-range or contradictory SAT literal")
                values[var] = lit > 0
    if statuses != ["s SATISFIABLE"] or len(values) != nvars:
        raise ValueError("SAT output lacks one complete model")
    return [False] + [values[i] for i in range(1, nvars + 1)]


def check_xcnf_model(values: list[bool], clauses: list[list[int]],
                     xors: list[tuple[list[int], bool]]) -> None:
    for i, clause in enumerate(clauses):
        if not any(values[abs(lit)] == (lit > 0) for lit in clause):
            raise ValueError(f"SAT model fails CNF clause {i}")
    for i, (row, rhs) in enumerate(xors):
        if bool(sum(values[var] for var in row) & 1) != rhs:
            raise ValueError(f"SAT model fails XOR row {i}")


def primary_bits(values: list[bool], count: int) -> int:
    return sum(1 << (i - 1) for i in range(1, count + 1) if values[i])


def blocked_formula(raw: bytes, primary_count: int, assignments: list[int]) -> bytes:
    """Insert primary blocking clauses before the native XOR rows."""
    lines = raw.splitlines(keepends=True)
    header = lines[0].decode("ascii").split()
    if len(header) != 4 or header[:2] != ["p", "cnf"]:
        raise ValueError("bad XCNF header")
    split = next((i for i, line in enumerate(lines[1:], 1) if line.startswith(b"x")), len(lines))
    nvars, constraints = map(int, header[2:])
    if constraints != len(lines) - 1 or primary_count > nvars:
        raise ValueError("XCNF count or primary width mismatch")
    blocks = []
    for assignment in assignments:
        if not 0 <= assignment < 1 << primary_count:
            raise ValueError("primary assignment out of range")
        blocks.append((" ".join(str(-i if assignment >> (i - 1) & 1 else i)
                                for i in range(1, primary_count + 1)) + " 0\n").encode())
    return (f"p cnf {nvars} {constraints + len(blocks)}\n".encode()
            + b"".join(lines[1:split]) + b"".join(blocks) + b"".join(lines[split:]))


def solver_call(command: list[str], attempt_dir: Path, wall_seconds: float,
                memory_bytes: int) -> dict:
    """Run one local solver process with sampled RSS and wall watchdogs."""
    stdout_path, stderr_path = attempt_dir / "stdout.txt", attempt_dir / "stderr.txt"
    start = time.monotonic()
    peak_rss = 0
    cpu_user = cpu_system = None
    timed_out = False
    memory_out = False
    with stdout_path.open("xb") as stdout, stderr_path.open("xb") as stderr:
        proc = subprocess.Popen(command, stdout=stdout, stderr=stderr)
        observed = psutil.Process(proc.pid)
        while proc.poll() is None:
            try:
                peak_rss = max(peak_rss, observed.memory_info().rss)
                cpu = observed.cpu_times()
                cpu_user, cpu_system = cpu.user, cpu.system
            except psutil.Error:
                pass
            if peak_rss >= memory_bytes:
                memory_out = True
                proc.kill()
                break
            if time.monotonic() - start >= wall_seconds:
                timed_out = True
                proc.kill()
                break
            time.sleep(0.02)
        proc.wait()
    return {"returncode": proc.returncode, "wall_seconds": time.monotonic() - start,
            "sampled_peak_rss_bytes": peak_rss or None, "wall_timeout": timed_out,
            "rss_watchdog_tripped": memory_out, "rss_watchdog_interval_seconds": 0.02,
            "sampled_cpu_user_seconds": cpu_user,
            "sampled_cpu_system_seconds": cpu_system,
            "stdout_sha256": digest(stdout_path.read_bytes()),
            "stderr_sha256": digest(stderr_path.read_bytes())}


def collect(raw: bytes, primary_count: int, solver: Path, wall_seconds: float,
            memory_bytes: int, max_models: int, seed: int, out_dir: Path,
            certify: Callable[[int], dict]) -> dict:
    """Retain each attempt; stop at one certified relation or a declared cap."""
    nvars, clauses, xors = parse(raw)
    if max_models < 1 or not math.isfinite(wall_seconds) or wall_seconds <= 0 or memory_bytes <= 0 or seed < 0:
        raise ValueError("finite positive model, wall and memory limits and a nonnegative seed are required")
    if not out_dir.parent.is_dir():
        raise ValueError("output parent directory must already exist")
    reserve = max_models * (len(raw) + max(1 << 20, nvars * 12)) + 10 * (1 << 20)
    if shutil.disk_usage(out_dir.parent).free < reserve:
        raise OSError("insufficient disk for the declared model cap and raw outputs")
    out_dir.mkdir(exist_ok=False)
    with (out_dir / "intent.json").open("x") as stream:
        json.dump({"input_sha256": digest(raw), "solver_path": str(solver),
                   "solver_sha256": digest(solver.read_bytes()),
                   "source_sha256": digest(Path(__file__).read_bytes()),
                   "wall_seconds": wall_seconds, "memory_bytes": memory_bytes,
                   "max_models": max_models, "seed": seed,
                   "estimated_disk_reserve_bytes": reserve,
                   "rss_watchdog_interval_seconds": 0.02}, stream, indent=2, sort_keys=True)
        stream.write("\n")
    start = time.monotonic()
    blocked: list[int] = []
    attempts = []
    status = "model_cap_censored"
    for i in range(max_models):
        remaining = wall_seconds - (time.monotonic() - start)
        if remaining <= 0:
            status = "wall_censored"
            break
        attempt_dir = out_dir / f"attempt-{i + 1:04d}"
        attempt_dir.mkdir()
        formula = blocked_formula(raw, primary_count, blocked)
        input_path = attempt_dir / "input.xcnf"
        input_path.write_bytes(formula)
        command = [str(solver), "--verb", "0", "--threads", "1", "--maxsol", "1",
                   "--random", str(seed), "--maxtime", str(max(1, math.ceil(remaining))),
                   str(input_path)]
        try:
            call = solver_call(command, attempt_dir, remaining, memory_bytes)
        except (OSError, subprocess.SubprocessError) as exc:
            attempt = {"command": command, "input_sha256": digest(formula),
                       "blocked_primary": len(blocked), "outcome": "solver_launch_failure",
                       "error_type": type(exc).__name__, "error": str(exc)}
            attempts.append(attempt)
            with (attempt_dir / "attempt.json").open("x") as stream:
                json.dump(attempt, stream, indent=2, sort_keys=True)
                stream.write("\n")
            status = "solver_launch_failure"
            break
        stdout = (attempt_dir / "stdout.txt").read_text(errors="replace")
        statuses = [line.strip() for line in stdout.splitlines() if line.startswith("s ")]
        attempt = {"command": command, "input_sha256": digest(formula),
                   "blocked_primary": len(blocked), "process": call,
                   "solver_status_lines": statuses}
        attempts.append(attempt)
        outcome = None
        if call["wall_timeout"]:
            outcome = "wall_censored"
        elif call["rss_watchdog_tripped"]:
            outcome = "memory_censored"
        elif call["returncode"] == 20 and statuses == ["s UNSATISFIABLE"]:
            outcome = "solver_reported_exhausted_unvalidated"
        elif call["returncode"] == 0 and statuses in (["s INDETERMINATE"], ["s UNKNOWN"]):
            outcome = "solver_unknown_censored"
        elif call["returncode"] != 10 or statuses != ["s SATISFIABLE"]:
            outcome = "solver_failure_or_unclassified"
        else:
            try:
                values = parse_model(stdout, nvars)
                check_xcnf_model(values, clauses, xors)
                if any(all(values[j] == bool(old >> (j - 1) & 1)
                           for j in range(1, primary_count + 1)) for old in blocked):
                    raise ValueError("solver returned a blocked primary assignment")
                assignment = primary_bits(values, primary_count)
                attempt["primary_assignment_hex"] = hex(assignment)
                attempt["full_xcnf_model_verified"] = True
                cert = certify(assignment)
                with (attempt_dir / "certificate.json").open("x") as stream:
                    json.dump(cert, stream, indent=2, sort_keys=True)
                    stream.write("\n")
                attempt["certificate_sha256"] = digest((attempt_dir / "certificate.json").read_bytes())
                if cert.get("result", {}).get("certified", False):
                    outcome = ("point_relation_certified" if time.monotonic() - start <= wall_seconds
                               else "point_relation_certified_after_wall_cap")
                else:
                    blocked.append(assignment)
                    if time.monotonic() - start > wall_seconds:
                        outcome = "wall_censored"
            except Exception as exc:
                attempt["validation_error_type"] = type(exc).__name__
                attempt["validation_error"] = str(exc)
                outcome = "invalid_model_or_certificate"
        attempt["outcome"] = outcome or "rejected_primary"
        with (attempt_dir / "attempt.json").open("x") as stream:
            json.dump(attempt, stream, indent=2, sort_keys=True)
            stream.write("\n")
        if outcome is not None:
            status = outcome
            break
    result = {"schema": "icperf-binary-k11-bounded-solver-v1",
              "scope": "bounded solver/model/point extraction; no ECDLP or speed claim",
              "status": status, "input_sha256": digest(raw),
              "limits": {"wall_seconds": wall_seconds, "memory_bytes": memory_bytes,
                         "max_models": max_models, "seed": seed, "threads": 1},
              "total_wall_seconds": time.monotonic() - start,
              "blocked_primary_count": len(blocked), "attempts": attempts}
    return result


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--base-kind", required=True, choices=INPUTS)
    parser.add_argument("--channel", required=True, type=int, choices=range(4))
    found_solver = shutil.which("cryptominisat5")
    parser.add_argument("--solver", type=Path,
                        default=Path(found_solver) if found_solver else None)
    parser.add_argument("--wall-seconds", required=True, type=float)
    parser.add_argument("--memory-mib", required=True, type=int)
    parser.add_argument("--max-models", required=True, type=int)
    parser.add_argument("--seed", required=True, type=int)
    parser.add_argument("--out-dir", required=True, type=Path)
    args = parser.parse_args()
    if args.solver is None or not args.solver.is_file():
        parser.error("CryptoMiniSat executable is unavailable")
    began = time.monotonic()
    started_at = datetime.datetime.now(datetime.timezone.utc).isoformat()
    git_commit = subprocess.run(["git", "rev-parse", "HEAD"], cwd=ROOT,
                                capture_output=True, text=True, check=True).stdout.strip()
    git_dirty = subprocess.run(["git", "status", "--porcelain", "--untracked-files=normal"],
                               cwd=ROOT, capture_output=True, text=True,
                               check=True).stdout.splitlines()
    base, manifest, _ = load(args.base_kind)
    arm = next(row for row in manifest["arms"] if row["channel"] == args.channel)
    verify_arm(arm, base)
    packed = (ROOT / arm["gzip_path"]).read_bytes()
    raw = gzip.decompress(packed)
    if digest(packed) != arm["gzip_sha256"] or digest(raw) != arm["raw_xcnf_sha256"]:
        raise ValueError("frozen XCNF digest mismatch")
    input_preparation_seconds = time.monotonic() - began
    solver_version = subprocess.run([str(args.solver), "--version"],
                                    capture_output=True, timeout=10, check=True)
    result = collect(raw, arm["primary_variables"], args.solver.resolve(),
                     args.wall_seconds, args.memory_mib * 1024 * 1024,
                     args.max_models, args.seed, args.out_dir,
                     lambda assignment: check(args.base_kind, args.channel, assignment))
    result["base_kind"] = args.base_kind
    result["channel"] = args.channel
    result["gzip_sha256"] = digest(packed)
    result["manifest_sha256"] = digest(INPUTS[args.base_kind][1].read_bytes())
    result["solver_sha256"] = digest(args.solver.read_bytes())
    result["solver_version_stdout"] = solver_version.stdout.decode(errors="replace")
    result["solver_version_stderr"] = solver_version.stderr.decode(errors="replace")
    result["source_sha256"] = digest(Path(__file__).read_bytes())
    result["python_version"] = sys.version
    result["psutil_version"] = psutil.__version__
    result["platform"] = platform.platform()
    result["started_at"] = started_at
    result["git_commit"] = git_commit
    result["git_dirty_porcelain_before_run"] = git_dirty
    result["input_preparation_seconds"] = input_preparation_seconds
    result["full_wall_seconds_before_report"] = time.monotonic() - began
    result["finished_at"] = datetime.datetime.now(datetime.timezone.utc).isoformat()
    with (args.out_dir / "summary.json").open("x") as stream:
        json.dump(result, stream, indent=2, sort_keys=True)
        stream.write("\n")
    print(json.dumps({"status": result["status"], "attempts": len(result["attempts"]),
                      "out_dir": str(args.out_dir)}, sort_keys=True))


if __name__ == "__main__":
    main()

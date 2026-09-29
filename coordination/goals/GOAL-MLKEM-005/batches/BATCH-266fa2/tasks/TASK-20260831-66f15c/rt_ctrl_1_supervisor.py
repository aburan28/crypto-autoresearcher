#!/usr/bin/env python3
"""External, hash-chained supervisor for the fixed RT-CTRL-1 target."""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import signal
import subprocess
import sys
import time
from pathlib import Path


def atomic_json(path: Path, value: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temp = path.with_suffix(path.suffix + ".tmp")
    with temp.open("w", encoding="utf-8") as handle:
        json.dump(value, handle, sort_keys=True, indent=2)
        handle.write("\n")
        handle.flush()
        os.fsync(handle.fileno())
    os.replace(temp, path)


def digest_json(value: dict) -> str:
    return hashlib.sha256(json.dumps(value, sort_keys=True, separators=(",", ":")).encode()).hexdigest()


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--worker", required=True, type=Path)
    parser.add_argument("--strategies", required=True, type=Path)
    parser.add_argument("--out", required=True, type=Path)
    parser.add_argument("--wall-clock", type=int, default=21600)
    parser.add_argument("--sample-seconds", type=int, default=30)
    parser.add_argument("--self-test-sigterm-after", type=int, default=None)
    args = parser.parse_args()
    try:
        import psutil
    except ImportError as exc:
        raise SystemExit(f"missing psutil: {exc}")

    args.out.mkdir(parents=True, exist_ok=True)
    state = args.out / "worker_state.json"
    result = args.out / "worker_result.json"
    terminal = args.out / "terminal_receipt.json"
    events = args.out / "events.jsonl"
    manifest = {
        "schema": "crypto.autoresearch.rt_ctrl_1.manifest.v1",
        "worker_sha256": hashlib.sha256(args.worker.read_bytes()).hexdigest(),
        "strategies_sha256": hashlib.sha256(args.strategies.read_bytes()).hexdigest(),
        "d": 512, "beta": 55, "mpfr_bits": 100, "seed_formula": "default_rng([715923,0,d,beta,0,0])",
        "wall_clock_seconds": args.wall_clock,
        "python": sys.executable,
    }
    atomic_json(args.out / "target_manifest.json", manifest)
    manifest_digest = digest_json(manifest)
    prev = manifest_digest

    def event(kind: str, **values: object) -> None:
        nonlocal prev
        body = {"kind": kind, "monotonic_seconds": time.monotonic(), "wall_utc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()), "previous_sha256": prev, **values}
        body["sha256"] = digest_json(body)
        with events.open("a", encoding="utf-8") as handle:
            handle.write(json.dumps(body, sort_keys=True) + "\n")
            handle.flush()
            os.fsync(handle.fileno())
        prev = body["sha256"]

    command = [sys.executable, str(args.worker), "--state", str(state), "--result", str(result), "--strategies", str(args.strategies)]
    if args.self_test_sigterm_after is not None:
        command.append("--self-test")
    process = subprocess.Popen(command, start_new_session=True, stdout=(args.out / "stdout.log").open("w"), stderr=(args.out / "stderr.log").open("w"))
    observed = psutil.Process(process.pid)
    started = time.monotonic()
    event("child_started", pid=process.pid, command=command, target_manifest_sha256=manifest_digest)
    cause = "completed"
    while process.poll() is None:
        elapsed = time.monotonic() - started
        try:
            cpu = observed.cpu_times()
            rss = observed.memory_info().rss
            event("sample", cpu_user_seconds=cpu.user, cpu_system_seconds=cpu.system, rss_bytes=rss, worker_state_exists=state.exists())
        except psutil.Error as exc:
            event("sample_unavailable", error=f"{type(exc).__name__}: {exc}")
        if args.self_test_sigterm_after is not None and elapsed >= args.self_test_sigterm_after:
            cause = "controlled_sigterm"
            os.killpg(process.pid, signal.SIGTERM)
            event("signal_sent", signal="SIGTERM", reason=cause)
            break
        if elapsed >= args.wall_clock:
            cause = "hard_cap"
            os.killpg(process.pid, signal.SIGTERM)
            event("signal_sent", signal="SIGTERM", reason=cause)
            break
        time.sleep(args.sample_seconds)
    try:
        exit_code = process.wait(timeout=120)
    except subprocess.TimeoutExpired:
        cause = "sigterm_grace_expired"
        os.killpg(process.pid, signal.SIGKILL)
        exit_code = process.wait()
        event("signal_sent", signal="SIGKILL", reason=cause)
    receipt = {
        "schema": "crypto.autoresearch.rt_ctrl_1.terminal_receipt.v1",
        "target_manifest_sha256": manifest_digest,
        "terminal_cause": cause,
        "exit_code": exit_code,
        "elapsed_seconds": time.monotonic() - started,
        "last_event_sha256": prev,
        "worker_state_exists": state.exists(),
        "worker_result_exists": result.exists(),
        "terminal": True,
    }
    atomic_json(terminal, receipt)
    event("terminal_receipt_written", terminal_receipt_sha256=hashlib.sha256(terminal.read_bytes()).hexdigest())
    return 0


if __name__ == "__main__":
    sys.exit(main())

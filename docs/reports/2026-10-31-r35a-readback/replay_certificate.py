#!/usr/bin/env python3
"""Replay the pinned R35a dual certificate under local resource admission.

Usage: python3 replay_certificate.py CERTIFICATE_BIN OUTPUT_DIR
The published compressed asset must first be decompressed and SHA-checked.
"""

import fcntl
import hashlib
import json
import os
import signal
import subprocess
import sys
import time
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
ARCHIVE = ROOT / "analysis/semaev-m2-last-fall-degree/submission-20261029/archive"
CHECKER = ROOT / "analysis/semaev-m2-last-fall-degree/verify/cert_check.py"
LOCK = Path("/tmp/crypto-bench.lock")
RESERVE = 16 * 1024**3
ESTIMATED_PEAK = 4_016_352_301
AS_LIMIT = 12 * 1024**3
TIME_LIMIT = 120


def available_memory():
    for line in Path("/proc/meminfo").read_text().splitlines():
        if line.startswith("MemAvailable:"):
            return int(line.split()[1]) * 1024
    raise RuntimeError("MemAvailable missing")


def active_compilers():
    names = {"cargo", "rustc", "lake", "lean", "clippy-driver"}
    active = []
    for item in Path("/proc").iterdir():
        if item.name.isdigit():
            try:
                if (item / "comm").read_text().strip() in names:
                    active.append(int(item.name))
            except (FileNotFoundError, ProcessLookupError, PermissionError):
                pass
    return active


def digest(path):
    sha = hashlib.sha256()
    size = 0
    with path.open("rb") as stream:
        while block := stream.read(1024 * 1024):
            sha.update(block)
            size += len(block)
    return size, sha.hexdigest()


def main(cert_path, out_dir):
    cert_path = Path(cert_path).resolve()
    out_dir = Path(out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)
    receipt = json.loads((ARCHIVE / "R35a.receipt.json").read_text())["result"]
    expected = receipt["artifacts"]["certificate.bin"]
    if digest(cert_path) != (expected["bytes"], expected["sha256"]):
        raise RuntimeError("certificate bytes differ from receipt")
    if digest(CHECKER)[1] != "13d926240a99de4b3eede374932fe245d62e7de65102a4fdf2cccfb0e4463877":
        raise RuntimeError("checker source differs from pinned producer blob")

    argv = list(receipt["steps"]["check"]["argv"])
    if argv[:4] != ["prlimit", "--as=42949672960", "--", "/usr/bin/python3"]:
        raise RuntimeError("historical checker command changed")
    argv[1] = "--as=" + str(AS_LIMIT)
    argv[4] = str(CHECKER)
    argv[5] = str(cert_path)
    with LOCK.open("a+b") as lock:
        fcntl.flock(lock, fcntl.LOCK_EX | fcntl.LOCK_NB)
        admitted_bytes = available_memory()
        compilers = active_compilers()
        if admitted_bytes < RESERVE + ESTIMATED_PEAK or compilers:
            raise RuntimeError("host admission failed: memory or compiler ownership")
        started = time.monotonic()
        process = subprocess.Popen(argv, stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                                   start_new_session=True)
        stopped_for = None
        while True:
            try:
                stdout, stderr = process.communicate(timeout=1)
                break
            except subprocess.TimeoutExpired:
                if active_compilers():
                    stopped_for = "competing compiler started"
                elif available_memory() < RESERVE:
                    stopped_for = "system memory reserve fell below 16 GiB"
                elif time.monotonic() - started > TIME_LIMIT:
                    stopped_for = "120-second timeout"
                if stopped_for:
                    os.killpg(process.pid, signal.SIGTERM)
                    stdout, stderr = process.communicate()
                    break
    (out_dir / "checker.stdout.txt").write_bytes(stdout)
    (out_dir / "checker.stderr.txt").write_bytes(stderr)
    result = {
        "schema": "r35a.certificate-replay/v1",
        "historical_source_commit": receipt["source_commit"],
        "checker_sha256": digest(CHECKER)[1],
        "certificate_sha256": digest(cert_path)[1],
        "argv": argv,
        "admitted_mem_available_bytes": admitted_bytes,
        "estimated_peak_bytes": ESTIMATED_PEAK,
        "reserve_bytes": RESERVE,
        "elapsed_seconds": round(time.monotonic() - started, 3),
        "returncode": process.returncode,
        "stopped_for": stopped_for,
        "stdout_sha256": digest(out_dir / "checker.stdout.txt")[1],
        "stderr_sha256": digest(out_dir / "checker.stderr.txt")[1],
    }
    (out_dir / "replay.json").write_text(json.dumps(result, indent=2, sort_keys=True) + "\n")
    return process.returncode if stopped_for is None else 2


if __name__ == "__main__":
    if len(sys.argv) != 3:
        raise SystemExit(__doc__)
    raise SystemExit(main(sys.argv[1], sys.argv[2]))

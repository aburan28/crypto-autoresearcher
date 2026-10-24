"""Fail-closed, write-once launcher for the exact embedding-degree screen."""
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import subprocess
import sys
import threading
import time

import psutil

HERE = Path(__file__).resolve().parent
WALL_SECONDS = 120
RSS_WATCHDOG_BYTES = 1024**3


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def one(root, name, mode):
    output = root / name
    command = [sys.executable, str(HERE / "compute.py"), "--out", str(output), "--mode", mode]
    before = time.monotonic()
    proc = subprocess.Popen(command, text=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    monitor = psutil.Process(proc.pid)
    stop = threading.Event()
    sampled_peak = 0
    exceeded = False

    def watch():
        nonlocal sampled_peak, exceeded
        while not stop.wait(0.01):
            try:
                resident = monitor.memory_info().rss
            except psutil.NoSuchProcess:
                return
            sampled_peak = max(sampled_peak, resident)
            if resident > RSS_WATCHDOG_BYTES:
                exceeded = True
                proc.kill()
                return

    watcher = threading.Thread(target=watch, daemon=True)
    watcher.start()
    try:
        stdout, stderr = proc.communicate(timeout=WALL_SECONDS)
        timed_out = False
    except subprocess.TimeoutExpired as exc:
        proc.kill()
        stdout, stderr = proc.communicate()
        timed_out = True
    finally:
        stop.set()
        watcher.join(timeout=1)
    returncode = proc.returncode
    (root / f"{name}.stdout").write_text(stdout)
    (root / f"{name}.stderr").write_text(stderr)
    marker = (output / "complete.ok").exists()
    receipt = {"command": command, "returncode": returncode, "timed_out": timed_out,
               "rss_watchdog_exceeded": exceeded, "peak_rss_sampled_bytes": sampled_peak,
               "elapsed_seconds": time.monotonic()-before, "completion_marker": marker,
               "accepted": returncode == 0 and marker and not timed_out and not exceeded,
               "stdout_sha256": sha(root / f"{name}.stdout"),
               "stderr_sha256": sha(root / f"{name}.stderr")}
    return receipt


def main(root):
    if root.exists():
        raise ValueError("run directory already exists")
    source_head = subprocess.check_output(["git", "rev-parse", "HEAD"], text=True).strip()
    source_dirty = bool(subprocess.check_output(["git", "status", "--porcelain"], text=True).strip())
    root.mkdir(parents=True)
    started = {"started_at_utc": datetime.now(timezone.utc).isoformat(),
               "source_git_head": source_head, "source_git_dirty_before_run": source_dirty,
               "launcher_sha256": sha(HERE / "launch.py"),
               "worker_sha256": sha(HERE / "compute.py"),
               "python": sys.version,
               "wall_limit_seconds_per_case": WALL_SECONDS,
               "rss_watchdog_bytes_per_case": RSS_WATCHDOG_BYTES,
               "rss_sample_interval_seconds": 0.01}
    (root / "started.json").write_text(json.dumps(started, indent=2) + "\n")
    receipts = {}
    for name, mode in (("injected_exception", "exception"),
                       ("injected_early_return", "early_return"),
                       ("exact", "normal")):
        receipts[name] = one(root, name, mode)
    (root / "receipts.json").write_text(json.dumps(receipts, indent=2) + "\n")
    if receipts["injected_exception"]["accepted"] or receipts["injected_early_return"]["accepted"]:
        raise RuntimeError("fail-closed controls not rejected")
    if receipts["injected_exception"]["returncode"] == 0:
        raise RuntimeError("injected exception did not cause nonzero exit")
    if receipts["injected_early_return"]["completion_marker"]:
        raise RuntimeError("injected early return wrote success marker")
    if not receipts["exact"]["accepted"]:
        raise RuntimeError("exact run failed or lacks completion marker")
    (root / "complete.ok").write_text("launcher accepted exact run after both fail-closed controls\n")
    print(root)


if __name__ == "__main__":
    if len(sys.argv) != 2:
        raise SystemExit("usage: python launch.py WRITE_ONCE_RUN_DIRECTORY")
    main(Path(sys.argv[1]))

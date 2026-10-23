"""Fail-closed, write-once launcher for the exact embedding-degree screen."""
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import resource
import subprocess
import sys
import time

HERE = Path(__file__).resolve().parent
WALL_SECONDS = 120
ADDRESS_SPACE_BYTES = 1024**3


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def cap_address_space():
    resource.setrlimit(resource.RLIMIT_AS, (ADDRESS_SPACE_BYTES, ADDRESS_SPACE_BYTES))


def one(root, name, mode):
    output = root / name
    command = [sys.executable, str(HERE / "compute.py"), "--out", str(output), "--mode", mode]
    before = time.monotonic()
    try:
        result = subprocess.run(command, text=True, capture_output=True,
                                timeout=WALL_SECONDS, preexec_fn=cap_address_space,
                                check=False)
        returncode, stdout, stderr, timed_out = result.returncode, result.stdout, result.stderr, False
    except subprocess.TimeoutExpired as exc:
        returncode = None
        stdout = exc.stdout.decode(errors="replace") if isinstance(exc.stdout, bytes) else (exc.stdout or "")
        stderr = exc.stderr.decode(errors="replace") if isinstance(exc.stderr, bytes) else (exc.stderr or "")
        timed_out = True
    (root / f"{name}.stdout").write_text(stdout)
    (root / f"{name}.stderr").write_text(stderr)
    marker = (output / "complete.ok").exists()
    receipt = {"command": command, "returncode": returncode, "timed_out": timed_out,
               "elapsed_seconds": time.monotonic()-before, "completion_marker": marker,
               "accepted": returncode == 0 and marker and not timed_out,
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
               "address_space_limit_bytes_per_case": ADDRESS_SPACE_BYTES}
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

"""Serialize the canonical S3 checkpoint gate after an explicit Phase B release.

Importing this module does not launch anything. The helper never substitutes
for scripts/checkpoint.sh gate and has no skip/override path.
"""
from datetime import datetime, timezone
import fcntl
import hashlib
import json
from pathlib import Path
import subprocess
import time


def require_gate(repo, release_path, protocol, task=None):
    """Return an actual canonical gate receipt, refusing missing authorization."""
    repo = Path(repo).resolve()
    release = json.loads(Path(release_path).read_text())
    if release.get("execution_authorized") is not True:
        raise RuntimeError("Root has not released Phase B execution")
    if release.get("checkpoint_gate_passed") is not True:
        raise RuntimeError("Root release lacks a prior successful real S3 gate")
    if task is not None and release.get("task") != task:
        raise RuntimeError("Phase B release belongs to another task")
    expected = protocol.get("freeze", {}).get("protocol_sha256")
    if protocol.get("freeze", {}).get("status") != "frozen" or not expected:
        raise RuntimeError("Experiment protocol is not frozen")
    if protocol["freeze"].get("filed_before_affected_data") is not True:
        raise RuntimeError("Protocol does not record a freeze before affected data")
    body = {key: value for key, value in protocol.items() if key != "freeze"}
    canonical = json.dumps(body, sort_keys=True, separators=(",", ":"),
                           ensure_ascii=False, allow_nan=False).encode("utf-8")
    if hashlib.sha256(canonical).hexdigest() != expected:
        raise RuntimeError("Frozen protocol bytes no longer match their canonical hash")
    if release.get("protocol_sha256") != expected:
        raise RuntimeError("Phase B release does not match this frozen protocol")
    lock = repo / ".resume" / "phase-b-gate.lock"
    lock.parent.mkdir(exist_ok=True)
    with lock.open("a") as handle:
        fcntl.flock(handle, fcntl.LOCK_EX)
        # Canonical checkpoint keys use whole-second stamps. Avoid overwriting
        # a key when serial workers reach the gate within the same second.
        previous = repo / ".resume" / ".last-push"
        if previous.is_file():
            fields = previous.read_text().split()
            if len(fields) >= 2:
                stamp = fields[1].split("-", 1)[0]
                try:
                    last = datetime.strptime(stamp, "%Y%m%dT%H%M%SZ").replace(tzinfo=timezone.utc)
                    pause = 1.1 - (datetime.now(timezone.utc) - last).total_seconds()
                    if 0 < pause < 3:
                        time.sleep(pause)
                except ValueError:
                    pass
        result = subprocess.run(["bash", "scripts/checkpoint.sh", "gate"],
                                cwd=repo, capture_output=True, text=True)
        receipt = {"command": ["bash", "scripts/checkpoint.sh", "gate"],
                   "returncode": result.returncode, "stdout": result.stdout,
                   "stderr": result.stderr,
                   "observed_utc": datetime.now(timezone.utc).isoformat()}
        if result.returncode != 0:
            raise RuntimeError("Canonical checkpoint gate refused launch: " +
                               json.dumps(receipt, ensure_ascii=False))
        if not previous.is_file():
            raise RuntimeError("Canonical gate returned success without its push receipt")
        receipt["last_push"] = previous.read_text().strip()
        return receipt

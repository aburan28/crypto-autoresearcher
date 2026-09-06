#!/usr/bin/env python3
"""Run a single audit payload with a verified Linux memory boundary.

On macOS use a locally available, digest-pinned Linux Docker image. Never
substitute an RSS polling threshold for a hard memory limit. This is an
infrastructure launcher; it does not approve experiments or interpret results.
"""
from __future__ import annotations

import argparse
import datetime
import json
import os
from pathlib import Path
import platform
import resource
import signal
import subprocess
import sys
import time
import uuid


def now():
    return datetime.datetime.now(datetime.timezone.utc).isoformat()


def worker(memory, cpu, command):
    """Linux-only child: fail before exec if either hard limit is unavailable."""
    try:
        if platform.system() != "Linux":
            raise RuntimeError("native hard address-space enforcement requires Linux")
        for key, limit in ((resource.RLIMIT_AS, memory), (resource.RLIMIT_CPU, cpu)):
            soft, hard = resource.getrlimit(key)
            effective = limit if hard == resource.RLIM_INFINITY else min(limit, hard)
            resource.setrlimit(key, (effective, effective))
            if resource.getrlimit(key) != (effective, effective):
                raise RuntimeError("resource-limit readback mismatch")
        os.execvp(command[0], command)
    except Exception as exc:
        print(f"AUDIT_SETUP_ERROR: {type(exc).__name__}: {exc}", file=sys.stderr)
        return 78


def run(command, output, *, cwd=None, seconds=900, memory=8 * 1024**3,
        backend="auto", image=None):
    if not command or seconds <= 0 or memory <= 0:
        raise ValueError("command and positive resource limits are required")
    output = Path(output).resolve()
    output.mkdir(parents=True, exist_ok=False)  # Never overwrite an earlier attempt.
    cwd = str(Path(cwd or os.getcwd()).resolve())
    start = time.monotonic()
    receipt = dict(started_at=now(), command=list(command), cwd=cwd,
                   status="failed_infrastructure", payload_exit_code=None,
                   backend=backend, memory_limit_bytes=memory,
                   wall_limit_seconds=seconds, peak_rss_bytes=None, cpu_seconds=None,
                   unavailable_reason="Payload was not launched", error=None,
                   cleanup_error=None, container_id=None)
    (output / "launch.json").write_text(json.dumps(receipt, indent=2) + "\n")
    previous_term = signal.getsignal(signal.SIGTERM)
    def interrupted(signum, frame):
        raise InterruptedError(f"Supervisor received signal {signum}")
    signal.signal(signal.SIGTERM, interrupted)
    proc = None
    container = None
    cleanup_reserve = min(10, seconds / 2)
    setup_deadline = seconds

    def docker(*args):
        remaining = setup_deadline - (time.monotonic() - start)
        if remaining <= 0:
            raise TimeoutError("wall budget exhausted during setup")
        result = subprocess.run(["docker", *args], capture_output=True, text=True,
                                timeout=min(10, remaining), check=True)
        return result.stdout.strip()

    try:
        chosen = backend if backend != "auto" else (
            "native" if platform.system() == "Linux" else "docker")
        receipt["backend"] = chosen
        if chosen == "native":
            if platform.system() != "Linux":
                raise RuntimeError("Native memory limits are unsupported here; use a Linux container")
            launch = [sys.executable, "-B", str(Path(__file__).resolve()), "--worker",
                      str(memory), str(max(1, int(seconds))), *command]
            receipt["memory_boundary"] = "Linux per-process RLIMIT_AS; single-process payload only"
        elif chosen == "docker":
            setup_deadline = seconds - cleanup_reserve
            # No implicit pulls and no mutable tag substituted after preflight.
            if not image or not image.startswith("sha256:") or len(image) != 71:
                raise ValueError("Docker backend requires a local sha256 image ID")
            int(image[7:], 16)
            if docker("info", "--format", "{{.OSType}}") != "linux":
                raise RuntimeError("Docker daemon is not Linux")
            info = json.loads(docker("image", "inspect", image))[0]
            if info["Id"] != image or info["Os"] != "linux":
                raise RuntimeError("Image identity/OS mismatch")
            # Use a name known before creation, so a setup timeout is cleanable.
            container = "audit-" + uuid.uuid4().hex
            docker("create", "--name", container, "--network=none", "--read-only",
                   "--memory", str(memory), "--memory-swap", str(memory),
                   "--cpus=1", "--pids-limit=64", "--cap-drop=ALL",
                   "--security-opt=no-new-privileges", "--tmpfs", "/tmp:rw,nosuid,nodev",
                   "--mount", f"type=bind,source={cwd},target=/work,readonly",
                   "--workdir", "/work", image, *command)
            config = json.loads(docker("inspect", container))[0]
            host = config["HostConfig"]
            if (host["Memory"] != memory or host["MemorySwap"] != memory
                    or host["NanoCpus"] != 1000000000):
                raise RuntimeError("Container resource-limit readback mismatch")
            receipt["container_id"] = config["Id"]
            receipt["image_id"] = image
            receipt["memory_boundary"] = "Linux container cgroup; RAM limit, swap disabled"
            launch = ["docker", "start", "--attach", container]
        else:
            raise ValueError("unknown backend")
        with (output / "stdout.log").open("xb") as out, (output / "stderr.log").open("xb") as err:
            proc = subprocess.Popen(launch, cwd=cwd, stdout=out, stderr=err,
                                    start_new_session=True)
            receipt["unavailable_reason"] = "Payload telemetry was not captured before interruption"
            timed_out = False
            while True:
                pid, status, usage = os.wait4(proc.pid, os.WNOHANG)
                if pid:
                    proc.returncode = os.waitstatus_to_exitcode(status)
                    break
                if time.monotonic() - start >= setup_deadline:
                    timed_out = True
                    os.killpg(proc.pid, signal.SIGKILL)
                    _, status, usage = os.wait4(proc.pid, 0)
                    proc.returncode = os.waitstatus_to_exitcode(status)
                    break
                time.sleep(min(0.02, max(0, setup_deadline - (time.monotonic() - start))))
            receipt["payload_exit_code"] = proc.returncode
            receipt["status"] = ("resource_exhaustion" if timed_out else
                "completed" if proc.returncode == 0 else "failed_implementation")
            if chosen == "native":
                receipt["peak_rss_bytes"] = usage.ru_maxrss * 1024
                receipt["cpu_seconds"] = usage.ru_utime + usage.ru_stime
                receipt["unavailable_reason"] = None
                if proc.returncode == 78:
                    receipt["status"] = "failed_infrastructure"
            else:
                receipt["unavailable_reason"] = "Docker CLI usage is not payload CPU/RSS; collect payload telemetry separately"
                if not timed_out:
                    state = json.loads(docker("inspect", container))[0]["State"]
                    receipt["payload_exit_code"] = state["ExitCode"]
                    receipt["status"] = ("resource_exhaustion" if state["OOMKilled"] else
                        "completed" if state["ExitCode"] == 0 else "failed_implementation")
    except (Exception, KeyboardInterrupt) as exc:
        receipt["error"] = f"{type(exc).__name__}: {exc}"
        receipt["status"] = ("cancelled" if isinstance(exc, (InterruptedError, KeyboardInterrupt)) else
            "resource_exhaustion" if isinstance(exc, TimeoutError) else "failed_infrastructure")
    finally:
        signal.signal(signal.SIGTERM, signal.SIG_IGN)  # Let bounded cleanup finish.
        if proc is not None and proc.returncode is None:
            try:
                os.killpg(proc.pid, signal.SIGKILL)
                proc.wait(timeout=5)
            except (ProcessLookupError, subprocess.TimeoutExpired):
                pass
        if container:
            try:
                subprocess.run(["docker", "rm", "--force", container], check=True,
                               capture_output=True, timeout=max(0.001, seconds - (time.monotonic() - start)))
            except Exception as exc:
                receipt["cleanup_error"] = f"{type(exc).__name__}: {exc}"
                receipt["status"] = "failed_infrastructure"
        for name in ("stdout.log", "stderr.log"):
            if not (output / name).exists():
                (output / name).touch(exist_ok=False)
        receipt["finished_at"] = now()
        receipt["wall_seconds"] = time.monotonic() - start
        # Includes bounded cleanup; payload/setup share the declared wall budget.
        with (output / "receipt.json").open("x") as f:
            json.dump(receipt, f, indent=2)
            f.write("\n")
        signal.signal(signal.SIGTERM, previous_term)
    return receipt


def main():
    if len(sys.argv) > 1 and sys.argv[1] == "--worker":
        return worker(int(sys.argv[2]), int(sys.argv[3]), sys.argv[4:])
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--output", required=True)
    p.add_argument("--seconds", type=float, default=900)
    p.add_argument("--memory", type=int, default=8 * 1024**3)
    p.add_argument("--backend", choices=["auto", "native", "docker"], default="auto")
    p.add_argument("--image")
    p.add_argument("command", nargs=argparse.REMAINDER)
    args = p.parse_args()
    command = args.command[1:] if args.command[:1] == ["--"] else args.command
    result = run(command, args.output, seconds=args.seconds, memory=args.memory,
                 backend=args.backend, image=args.image)
    print(json.dumps(result))
    return 0 if result["status"] == "completed" else 1


if __name__ == "__main__":
    raise SystemExit(main())

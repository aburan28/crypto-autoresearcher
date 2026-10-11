#!/usr/bin/env python3
"""EXP-SEMBIN-35bf67 run-record helpers: provenance, environment, manifest."""
import glob
import hashlib
import json
import os
import platform
import subprocess
import sys
import time

import yaml

REPO = "/home/user/crypto-autoresearcher"
EXP = os.path.join(REPO, "experiments", "EXP-SEMBIN-35bf67")
IMPL = os.path.join(EXP, "implementation")
M4RI_COMMIT = "d0a1ee18511714a2c33cc0920a068c05c1f0f8fb"


def sha256(p):
    h = hashlib.sha256()
    with open(p, "rb") as fh:
        for b in iter(lambda: fh.read(1 << 20), b""):
            h.update(b)
    return h.hexdigest()


def git_state():
    head = subprocess.run(["git", "-C", REPO, "rev-parse", "HEAD"], capture_output=True, text=True).stdout.strip()
    st = subprocess.run(["git", "-C", REPO, "status", "--porcelain", "--untracked-files=all"],
                        capture_output=True, text=True).stdout
    return {"commit": head, "dirty": bool(st.strip()),
            "dirty_status_sha256": hashlib.sha256(st.encode()).hexdigest(),
            "dirty_paths": sorted(l[3:] for l in st.splitlines())[:400],
            "dirty_note": "Untracked files are this experiment's own implementation/ and stage outputs "
                          "(write_scope); no tracked file is modified."}


def impl_hashes(binroot):
    out = {}
    for p in sorted(glob.glob(os.path.join(IMPL, "*"))):
        if os.path.isfile(p) and p.endswith((".py", ".c", ".h", ".sh")):
            out["implementation/" + os.path.basename(p)] = sha256(p)
    bins = {}
    for b in ("solv4_A", "solv4_B", "sols", "exhaust"):
        p = os.path.join(binroot, b)
        if os.path.exists(p):
            bins[b] = sha256(p)
    lib = os.path.join(binroot, "m4ri-install", "lib", "libm4ri.a")
    if os.path.exists(lib):
        bins["libm4ri.a(static, linked into solv4_A only)"] = sha256(lib)
    return out, bins


def environment(binroot):
    cpu = ""
    try:
        with open("/proc/cpuinfo") as fh:
            for l in fh:
                if l.startswith("model name"):
                    cpu = l.split(":", 1)[1].strip()
                    break
    except OSError:
        pass
    mem = None
    try:
        with open("/proc/meminfo") as fh:
            mem = fh.readline().split()[1] + " kB"
    except OSError:
        pass
    gcc = subprocess.run(["gcc", "--version"], capture_output=True, text=True).stdout.splitlines()[0]
    impl, bins = impl_hashes(binroot)
    return {"operating_system": platform.platform(), "architecture": platform.machine(),
            "cpu_model": cpu, "logical_cpus": os.cpu_count(), "mem_total": mem,
            "python_version": sys.version.split()[0], "gcc": gcc,
            "sage_version": None, "magma": None,
            "m4ri": {"release": "release-20240729", "git_commit": M4RI_COMMIT,
                     "source": "https://github.com/malb/m4ri.git", "build": "implementation/build.sh",
                     "configure": "--enable-openmp=no CFLAGS='-O3 -march=native'",
                     "apt_libm4ri_0.0.20200125_used": False},
            "implementation_sha256": impl, "binary_sha256": bins,
            "build_dir_note": "binaries built by implementation/build.sh into the session scratchpad "
                              "(outside the repository); rebuild with the same script and commit."}


def write_run_files(run_dir, command, binroot):
    os.makedirs(run_dir, exist_ok=True)
    with open(os.path.join(run_dir, "command.txt"), "w") as fh:
        fh.write(command + "\n")
    with open(os.path.join(run_dir, "environment.json"), "w") as fh:
        json.dump(environment(binroot), fh, indent=1)


def write_manifest(run_dir, run_id, purpose, status, started, finished, wall, cpu_seconds,
                   peak_rss, inputs, metrics, valid, invalid_reason, artifacts, notes,
                   binroot, command, deviations=None, extra=None):
    impl, bins = impl_hashes(binroot)
    man = {"run": {
        "id": run_id,
        "experiment_id": "EXP-SEMBIN-35bf67",
        "hypothesis_id": "H-SEMBIN-d895d9",
        "task_id": "TASK-20261002-530540",
        "archival_owner": "TASK-20261005-71d2b9 (DEC-20261005-c83e5a)",
        "purpose": purpose,
        "status": status,
        "code": dict(git_state(), command=command, command_file="command.txt",
                     implementation_sha256=impl, binary_sha256=bins),
        "inference": {"requested_policy": "executor-implementation", "canonical_policy": None,
                      "backend": None, "provider": None, "resolved_model_id": None,
                      "model_provenance": "not-applicable", "model_verified": False,
                      "requested_reasoning_effort": None, "reasoning_effort": None,
                      "fallback_used": False, "fallback_reason": None, "degraded_requirements": [],
                      "independent_session": False, "adapter_version": None, "config_digest": None,
                      "note": "No model is in this run's computational loop. The executing agent "
                              "session (Claude Code executor subagent) wrote and launched the code."},
        "environment": {"file": "environment.json"},
        "inputs": inputs,
        "seeds_and_randomness": "Instance i of cell c, stage s, arm a: random.Random(int(sha256("
                                "'EXP-SEMBIN-35bf67|'+s+'|'+c+'|'+a+'|'+str(i))[:16],16)); "
                                "B then z drawn by getrandbits (primary); T11 null monomials drawn "
                                "by rng.sample (null). DREG anchors use random.Random(2026+n) exactly "
                                "as src/h012_peel_rank.py. Calibration matrices use xorshift64* "
                                "seeded by the recorded seed. No other randomness; the rank arms "
                                "and solution counters are deterministic.",
        "timing": {"started_at": started, "finished_at": finished, "wall_seconds": wall},
        "resources": {"peak_rss_bytes": peak_rss, "cpu_seconds": cpu_seconds,
                      "caps": "per process RLIMIT_CPU 28800 s and 8 GiB RSS watchdog (OP-CAPS)"},
        "result": {"metrics": metrics, "valid": valid, "invalid_reason": invalid_reason,
                   "certificate": {"kind": "none", "verified": None, "verifier": None,
                                   "note": "Measurement run: no discrete-log solve or factor-base "
                                           "relation is claimed. Enumerated solution tuples are "
                                           "re-evaluated against every descended equation by the "
                                           "SOLV4 driver (points_failing_system) and by exhaust.c."}},
        "protocol_deviations": deviations or [],
        "artifacts": artifacts,
        "notes": notes,
    }}
    if extra:
        man["run"].update(extra)
    with open(os.path.join(run_dir, "manifest.yaml"), "w") as fh:
        yaml.safe_dump(man, fh, sort_keys=False, width=100, allow_unicode=True)
    return man


def now_utc():
    return time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())

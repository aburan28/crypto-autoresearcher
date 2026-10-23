#!/usr/bin/env python3
"""Bounded, write-once replay of FreeLIP 1.0 primality calls on seed curves."""
from __future__ import annotations

import argparse
import datetime as dt
import hashlib
import json
import os
import platform
import resource
import subprocess
import sys
import tarfile
import tempfile
import time
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
INPUT = ROOT / "research/nist_seed_skipped_curves_20261016"
TARBALL_SHA = "cd168c2ba0f9052d84072664b559219506050f583fdf58060517d59422f5bccc"
LIPC_SHA = "5c507451e8c13323f106a66b5f76cdf17dfbe9eb7f289eb1ac0c706855625bff"
INPUT_SHAS = {
    "assessed.json": "370e79ce0bff8f26bb437fe37d1756f3f8261a5c00e9062ba41cf70f272e8841",
    "traits.json": "a1102bd487379d223581863fab731d6eb6957bf0e264b450f1c7b298279b0b67",
}
LIMIT_SECONDS = 30.0


def digest(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def now() -> str:
    return dt.datetime.now(dt.timezone.utc).isoformat()


def command(cmd: list[str], timeout: float, cwd: Path | None = None) -> dict:
    start = time.monotonic()
    try:
        p = subprocess.run(cmd, cwd=cwd, text=True, capture_output=True, timeout=timeout)
        return {
            "command": cmd, "exit_code": p.returncode,
            "stdout": p.stdout, "stderr": p.stderr,
            "elapsed_seconds": time.monotonic() - start,
        }
    except subprocess.TimeoutExpired as exc:
        return {
            "command": cmd, "exit_code": None,
            "stdout": (exc.stdout or b"").decode(errors="replace") if isinstance(exc.stdout, bytes) else (exc.stdout or ""),
            "stderr": (exc.stderr or b"").decode(errors="replace") if isinstance(exc.stderr, bytes) else (exc.stderr or ""),
            "elapsed_seconds": time.monotonic() - start, "timeout": True,
        }


def write_json(path: Path, value: object) -> None:
    path.write_text(json.dumps(value, indent=2, sort_keys=True) + "\n")


def rows() -> list[dict]:
    for filename, expected in INPUT_SHAS.items():
        if digest((INPUT / filename).read_bytes()) != expected:
            raise ValueError(f"input digest mismatch: {filename}")
    skipped = json.loads((INPUT / "assessed.json").read_text())["candidate_rows"]
    published = json.loads((INPUT / "traits.json").read_text())["published_controls"]
    if len(skipped) != 11 or len(published) != 10:
        raise ValueError("expected exactly eleven omitted and ten published rows")
    result = []
    for kind, entries in (("omitted", [(r["identity"]["curve_id"], r) for r in skipped]),
                          ("published", list(published.items()))):
        for label, row in entries:
            n = int(row["n_hex"], 16)
            if n != int(row["identity"]["curve"]["subgroup_order"]):
                raise ValueError(f"curve identity/order mismatch: {label}")
            result.append({"label": label, "kind": kind, "n_decimal": str(n), "expected": 1,
                           "curve_uid": row["identity"]["curve_uid"]})
    if len({r["curve_uid"] for r in result}) != 21:
        raise ValueError("duplicate curve identity")
    p192 = int(published["prime192v1"]["n_hex"], 16)
    result.extend([
        {"label": "control_prime_101", "kind": "control", "n_decimal": "101", "expected": 1},
        {"label": "control_composite_15", "kind": "control", "n_decimal": "15", "expected": 0},
        {"label": "control_composite_221", "kind": "control", "n_decimal": "221", "expected": 0},
        {"label": "control_composite_3xprime192v1", "kind": "control", "n_decimal": str(3 * p192), "expected": 0},
    ])
    return result


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--tarball", type=Path, required=True)
    ap.add_argument("--out", type=Path, required=True)
    ap.add_argument("--compat-malloc-shim", action="store_true")
    ap.add_argument("--compat-string-include", action="store_true")
    args = ap.parse_args()
    if args.compat_string_include and not args.compat_malloc_shim:
        ap.error("--compat-string-include requires --compat-malloc-shim")
    out = args.out.resolve()
    out.mkdir(parents=True, exist_ok=False)
    start = time.monotonic()
    record = {
        "schema": ("nist-seed-freelip-primality-replay/v3" if args.compat_string_include else
                   "nist-seed-freelip-primality-replay/v2" if args.compat_malloc_shim else
                   "nist-seed-freelip-primality-replay/v1"), "started_at_utc": now(),
        "host": platform.platform(), "machine": platform.machine(), "python": sys.version,
        "cwd": str(Path.cwd()), "protocol_sha256": digest((HERE / "PROTOCOL.md").read_bytes()),
        "compat_malloc_shim": args.compat_malloc_shim,
        "compat_string_include": args.compat_string_include,
        "protocol_2_sha256": digest((HERE / "PROTOCOL_2.md").read_bytes()) if args.compat_malloc_shim else None,
        "protocol_3_sha256": digest((HERE / "PROTOCOL_3.md").read_bytes()) if args.compat_string_include else None,
        "wrapper_sha256": digest((HERE / "replay.c").read_bytes()),
        "source_tarball_path": str(args.tarball.resolve()),
        "source_tarball_sha256_expected": TARBALL_SHA,
        "git_head": command(["git", "rev-parse", "HEAD"], 5, ROOT),
        "git_status": command(["git", "status", "--short"], 5, ROOT),
        "compiler_version": command(["clang", "--version"], 5),
        "cases": [],
    }
    write_json(out / "started.json", record)
    try:
        if digest(args.tarball.read_bytes()) != TARBALL_SHA:
            raise ValueError("FreeLIP tarball digest mismatch")
        cases = rows()
        with tempfile.TemporaryDirectory(prefix="nist-freelip-build-") as td:
            build = Path(td)
            with tarfile.open(args.tarball, "r:gz") as archive:
                for name in ("lip.c", "lip.h"):
                    member = archive.getmember("freelip-1.0.orig/" + name)
                    content = archive.extractfile(member).read()
                    if name == "lip.c" and digest(content) != LIPC_SHA:
                        raise ValueError("FreeLIP lip.c digest mismatch")
                    (build / name).write_bytes(content)
            (build / "lippar.h").write_text("#define PLAIN 1\n")
            if args.compat_malloc_shim:
                shim_bytes = b"#include <stdlib.h>\n"
                (build / "malloc.h").write_bytes(shim_bytes)
                record["malloc_shim"] = {"content": shim_bytes.decode(), "sha256": digest(shim_bytes)}
            wrapper = build / "replay.c"
            wrapper.write_bytes((HERE / "replay.c").read_bytes())
            executable = build / "replay"
            compile_cmd = [
                "clang", "-std=gnu89", "-O0", "-DSIZEOFLONG=8", "-I", str(build),
            ]
            if args.compat_string_include:
                compile_cmd += ["-include", "string.h"]
            compile_cmd += [str(build / "lip.c"), str(wrapper), "-lm", "-o", str(executable)]
            record["build"] = command(compile_cmd, min(10.0, LIMIT_SECONDS - (time.monotonic() - start)))
            write_json(out / "build.json", record["build"])
            if record["build"]["exit_code"] != 0:
                raise RuntimeError("archival source build failed")
            record["executable_sha256"] = digest(executable.read_bytes())
            for index, case in enumerate(cases):
                remaining = LIMIT_SECONDS - (time.monotonic() - start)
                if remaining <= 0:
                    raise TimeoutError("whole replay watchdog exhausted")
                result = command([str(executable), case["n_decimal"]], min(remaining, 10.0))
                record["cases"].append({**case, **result})
                write_json(out / f"case_{index:02d}.json", record["cases"][-1])
                if result["exit_code"] != 0:
                    raise RuntimeError(f"replay process failed: {case['label']}")
                values = result["stdout"].strip().split()
                if len(values) != 3 or any(v not in {"0", "1"} for v in values):
                    raise RuntimeError(f"unparseable FreeLIP output: {case['label']}")
                record["cases"][-1]["returns"] = [int(v) for v in values]
                if any(int(v) != case["expected"] for v in values):
                    raise RuntimeError(f"unexpected FreeLIP classification: {case['label']}")
        record["finished_at_utc"] = now()
        record["elapsed_seconds"] = time.monotonic() - start
        record["child_maxrss"] = resource.getrusage(resource.RUSAGE_CHILDREN).ru_maxrss
        write_json(out / "results.json", record)
        (out / "complete.ok").write_text(digest((out / "results.json").read_bytes()) + "\n")
        return 0
    except Exception as exc:
        record["failed_at_utc"] = now()
        record["failure"] = f"{type(exc).__name__}: {exc}"
        record["elapsed_seconds"] = time.monotonic() - start
        record["child_maxrss"] = resource.getrusage(resource.RUSAGE_CHILDREN).ru_maxrss
        write_json(out / "failure.json", record)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())

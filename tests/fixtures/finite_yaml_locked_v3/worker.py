"""Fixed benign sentinel. No curve, group, divisor, section or scientific import.

Invoked only by the admitted source-v4 entry with a parent-published case input.
Every data file below is visibly synthetic. No real RUN namespace is accepted.
"""
from __future__ import annotations
import errno
import hashlib
import json
import os
from pathlib import Path
import stat
import sys
import time

MODES = {"success", "failure", "timeout", "memory", "worker-cap", "environment",
         "missing-profile", "extra-output", "alias", "mutate", "barrier"}


def encode(value):
    return (json.dumps(value, sort_keys=True, separators=(",", ":"), allow_nan=False) + "\n").encode()


def new(name, raw):
    if "/" in name or name in ("", ".", "..") or "\\" in name:
        raise ValueError("plain fixture output filename required")
    fd = os.open(name, os.O_WRONLY | os.O_CREAT | os.O_EXCL | os.O_NOFOLLOW, 0o600)
    try:
        view = memoryview(raw)
        while view:
            view = view[os.write(fd, view):]
        os.fsync(fd)
    finally:
        os.close(fd)


def fixture_path(value, root):
    path = Path(value)
    if not path.is_absolute() or not path.is_relative_to(root) or ".." in path.parts:
        raise ValueError("mutation/alias target must be inside the disposable fixture root")
    current = path.parent
    while current != root.parent:
        if current.is_symlink():
            raise ValueError("fixture target has a symlink ancestor")
        current = current.parent
    return path


def run(options, context):
    if not isinstance(options, dict) or options.get("mode") not in MODES:
        raise ValueError("unknown benign fixture mode")
    if options.get("scientific_execution_authorized") is not False:
        raise ValueError("benign fixture must explicitly deny scientific authority")
    root = Path(options["fixture_root"])
    if not root.is_absolute() or not Path.cwd().is_relative_to(root / "fixture-outputs"):
        raise ValueError("no real reserved directory is allowed")
    mode = options["mode"]
    print(json.dumps({"sentinel_entered": True, "scientific_runs": 0, "forwarding": context}, sort_keys=True), flush=True)
    print("finite_yaml_v3_benign_stderr", file=sys.stderr, flush=True)
    if mode == "failure":
        new("fixture-partial.json", encode({"synthetic": True, "before_failure": True}))
        return 7
    if mode == "timeout":
        time.sleep(60)
        return 9
    if mode == "memory":
        # Ceiling is frozen at 64 MiB; touch memory and retain it for sampling.
        payload = []
        for _ in range(64):
            payload.append(bytearray(b"x" * (1024 * 1024)))
            time.sleep(0.02)
        time.sleep(30)
        return 10
    if mode == "worker-cap":
        try:
            pid = os.fork()
        except OSError as exc:
            print(json.dumps({"fork_refused": True, "errno": exc.errno}), flush=True)
        else:
            if pid == 0:
                os._exit(11)
            os.waitpid(pid, 0)
            raise RuntimeError("fork unexpectedly succeeded under zero descendant policy")
    if mode == "environment":
        # Only this deliberately benign canary is inspected, never credentials.
        print(json.dumps({"FINITE_YAML_QA_CANARY": os.environ.get("FINITE_YAML_QA_CANARY")}), flush=True)
    if mode == "mutate":
        target = Path(options["target"])
        bound_mirrors = {Path(value["path"]): value for value in context["authority_mirrors"].values()}
        if target in bound_mirrors:
            # This capability names only the two independently verified copies,
            # never the genuine claim/native originals. Every ancestor is checked.
            mirror_root = Path(context["authority_repository"]) / "coordination/pending-ideas/BATCH-e9d1c7/timing-correction/qa/scratch/authority-mirrors"
            target = fixture_path(str(target), mirror_root)
            if target.is_symlink() or target.stat().st_nlink != 1:
                raise ValueError("mirror mutation target must remain a nonalias regular file")
            expected_identity = bound_mirrors[target]["identity"][:2]
            if [target.stat().st_dev, target.stat().st_ino] != expected_identity:
                raise ValueError("mirror identity changed before the controlled mutation")
        else:
            target = fixture_path(options["target"], root)
        before = target.read_bytes()
        if hashlib.sha256(before).hexdigest() != options["before_sha256"]:
            raise ValueError("named mutation target does not have the frozen before hash")
        raw = options["after_utf8"].encode()
        with target.open("r+b") as stream:
            stream.seek(0)
            stream.write(raw)
            stream.truncate()
            stream.flush()
            os.fsync(stream.fileno())
        print(json.dumps({"mutated": str(target), "before_sha256": hashlib.sha256(before).hexdigest(),
                          "after_sha256": hashlib.sha256(raw).hexdigest()}), flush=True)
    if mode == "barrier":
        ready = fixture_path(options["ready_path"], root)
        release = fixture_path(options["release_path"], root)
        # Parent-created pipes, not additional output filenames or forking.
        if not stat.S_ISFIFO(ready.stat().st_mode) or not stat.S_ISFIFO(release.stat().st_mode):
            raise ValueError("precreated fixture FIFO barriers required")
        with ready.open("w") as stream:
            stream.write("child-ready\n")
        with release.open("r") as stream:
            if stream.readline().strip() != "release":
                raise ValueError("invalid barrier release")
    if mode == "alias":
        target = fixture_path(options["target"], root)
        if hashlib.sha256(target.read_bytes()).hexdigest() != options["target_sha256"]:
            raise ValueError("alias sentinel target mismatch")
        name = options["name"]
        if "/" in name or "\\" in name or name in ("", ".", ".."):
            raise ValueError("alias name must be a leaf")
        if options["alias_kind"] == "symlink":
            os.symlink(target, name)
        elif options["alias_kind"] == "hardlink":
            os.link(target, name)
        else:
            raise ValueError("unknown alias kind")
    for name in context["output_names"]:
        if name in ("manifest.yaml", "stdout.txt", "stderr.txt"):
            continue
        if mode == "missing-profile" and name == options["omitted_name"]:
            continue
        new(name, encode({"synthetic_fixture": True, "scientific_data": False,
                          "name": name, "forwarding": context}))
    if mode == "extra-output":
        new("undeclared-fixture-output.json", encode({"synthetic": True}))
    return 0


if __name__ == "__main__":
    print("fixed benign worker requires the admitted source-v4 descriptor entry", file=sys.stderr)
    raise SystemExit(2)

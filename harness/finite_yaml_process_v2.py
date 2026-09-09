"""Standard-library process and custody primitives for the finite YAML v2 adapter.

No scientific module is imported here. Core private helpers are loaded only after
their closure has been checked by admission. The core _run_child is not reused:
its interface cannot accept an environment or exclusive capture descriptors.
"""
from __future__ import annotations

import dataclasses
import hashlib
import importlib
import json
import math
import os
from pathlib import Path, PurePosixPath
import re
import signal
import stat
import subprocess
import sys
import time


class AdmissionError(ValueError):
    def __init__(self, predicate, detail):
        self.predicate = predicate
        self.detail = str(detail)
        super().__init__(f"{predicate}: {detail}")


def require(condition, predicate, detail):
    if not condition:
        raise AdmissionError(predicate, detail)


def canonical(value):
    return json.dumps(value, sort_keys=True, separators=(",", ":"),
                      ensure_ascii=False, allow_nan=False).encode("utf-8")


def digest(data):
    return hashlib.sha256(data).hexdigest()


def strict_json(raw):
    def pairs(items):
        result = {}
        for key, value in items:
            require(key not in result, "duplicate_keys", key)
            result[key] = value
        return result

    def constant(value):
        raise AdmissionError("nonfinite_number", value)

    def number(value):
        parsed = float(value)
        require(math.isfinite(parsed), "nonfinite_number", value)
        return parsed

    try:
        return json.loads(raw, object_pairs_hook=pairs, parse_constant=constant,
                          parse_float=number)
    except (UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise AdmissionError("json_syntax", exc) from exc


def exact_integer(value, predicate, minimum=0):
    require(type(value) is int and value >= minimum, predicate, "exact integer required")
    return value


def positive_number(value, predicate):
    require(type(value) in (int, float) and math.isfinite(value) and value > 0,
            predicate, "positive finite number required")
    return value


def relative_name(value, *, leaf=False):
    require(isinstance(value, str) and value and "\\" not in value and "\0" not in value,
            "canonical_path", "nonempty POSIX path required")
    path = PurePosixPath(value)
    require(not path.is_absolute() and all(p not in ("", ".", "..") for p in value.split("/"))
            and str(path) == value and (not leaf or len(path.parts) == 1),
            "canonical_path", value)
    return value


def open_directory(path):
    """Walk each ancestor by descriptor; never resolve a symlink silently."""
    path = Path(path)
    require(path.is_absolute() and str(path) == os.path.normpath(str(path)),
            "directory_path", path)
    fd = os.open("/", os.O_RDONLY | os.O_DIRECTORY)
    try:
        for part in path.parts[1:]:
            nxt = os.open(part, os.O_RDONLY | os.O_DIRECTORY | os.O_NOFOLLOW, dir_fd=fd)
            os.close(fd)
            fd = nxt
        return fd
    except BaseException:
        os.close(fd)
        raise


def file_identity(st):
    return (st.st_dev, st.st_ino, st.st_size, st.st_mtime_ns, st.st_ctime_ns, st.st_nlink)


def read_regular(path):
    """Capture bytes and identity from a no-follow, singly-linked ordinary file."""
    path = Path(path)
    directory = open_directory(path.parent)
    fd = None
    try:
        before = os.stat(path.name, dir_fd=directory, follow_symlinks=False)
        require(stat.S_ISREG(before.st_mode) and before.st_nlink == 1,
                "nonalias_regular_file", path)
        fd = os.open(path.name, os.O_RDONLY | os.O_NOFOLLOW, dir_fd=directory)
        first = os.fstat(fd)
        require(file_identity(before) == file_identity(first), "file_identity", path)
        chunks = []
        while True:
            data = os.read(fd, 1024 * 1024)
            if not data:
                break
            chunks.append(data)
        after = os.fstat(fd)
        named = os.stat(path.name, dir_fd=directory, follow_symlinks=False)
        require(file_identity(first) == file_identity(after) == file_identity(named),
                "file_identity", path)
        return b"".join(chunks), file_identity(first)
    except OSError as exc:
        raise AdmissionError("file_access", f"{path}: {exc}") from exc
    finally:
        if fd is not None:
            os.close(fd)
        os.close(directory)


def bind_file(path, expected=None):
    raw, identity = read_regular(path)
    sha = digest(raw)
    if expected is not None:
        require(isinstance(expected, str) and re.fullmatch(r"[0-9a-f]{64}", expected),
                "sha256_format", path)
        require(sha == expected, "file_sha256", path)
    return {"path": str(path), "sha256": sha, "identity": list(identity)}, raw


def unchanged(binding):
    try:
        actual, _ = bind_file(binding["path"], binding["sha256"])
        return actual == binding
    except (OSError, ValueError):
        return False


def exclusive_file(directory_fd, name):
    relative_name(name, leaf=True)
    try:
        fd = os.open(name, os.O_RDWR | os.O_CREAT | os.O_EXCL | os.O_NOFOLLOW,
                     0o600, dir_fd=directory_fd)
    except FileExistsError as exc:
        raise AdmissionError("exclusive_file", name) from exc
    st = os.fstat(fd)
    require(stat.S_ISREG(st.st_mode) and st.st_nlink == 1,
            "exclusive_file_identity", name)
    return fd


def write_exclusive(directory_fd, name, raw):
    fd = exclusive_file(directory_fd, name)
    try:
        view = memoryview(raw)
        while view:
            view = view[os.write(fd, view):]
        os.fsync(fd)
        return file_identity(os.fstat(fd))
    finally:
        os.close(fd)


def read_fd(fd):
    os.lseek(fd, 0, os.SEEK_SET)
    parts = []
    while True:
        part = os.read(fd, 1024 * 1024)
        if not part:
            return b"".join(parts)
        parts.append(part)


def inspect_outputs(path, expected, *, manifest_absent=True):
    expected = set(expected)
    if manifest_absent:
        expected.discard("manifest.yaml")
    directory_fd = open_directory(path)
    artifacts, aliases = {}, []
    try:
        names = set(os.listdir(directory_fd))
        identities = set()
        for name in sorted(names):
            st = os.stat(name, dir_fd=directory_fd, follow_symlinks=False)
            key = (st.st_dev, st.st_ino)
            if not stat.S_ISREG(st.st_mode) or st.st_nlink != 1 or key in identities:
                aliases.append({"name": name, "mode": st.st_mode, "identity": list(file_identity(st)),
                                "symlink_target": os.readlink(name, dir_fd=directory_fd)
                                if stat.S_ISLNK(st.st_mode) else None})
                continue
            identities.add(key)
            if name == "manifest.yaml":
                continue
            binding, data = bind_file(Path(path) / name)
            artifacts[name] = {"sha256": binding["sha256"], "bytes": len(data),
                               "identity": binding["identity"]}
        return {"expected": sorted(expected), "present": sorted(names),
                "missing": sorted(expected - names), "extra": sorted(names - expected),
                "aliases": aliases, "artifacts": artifacts}
    finally:
        os.close(directory_fd)


def git(root, pin, args, env):
    bind_file(pin["path"], pin["sha256"])
    result = subprocess.run([pin["path"], "--no-optional-locks", "-C", str(root), *args],
                            env=env, stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                            timeout=30, check=False)
    require(result.returncode == 0, "git_command", result.stderr.decode("utf-8", "replace"))
    return result.stdout


def tree_clean(root, pin, env, allowed_output=None):
    # -z makes names unambiguous; a pathspec excludes ONLY the exact case output.
    args = ["status", "--porcelain=v1", "-z", "--untracked-files=all", "--ignored=matching", "--", "."]
    if allowed_output is not None:
        relative_name(allowed_output)
        args += [":(top,exclude,literal)" + allowed_output,
                 ":(top,exclude,glob)" + allowed_output + "/**"]
    return not git(root, pin, args, env)


def host_supported(name=None, uid=None, has_nproc=None, has_wait4=None):
    """Optional arguments are metadata tests only; launch calls with no overrides."""
    if name is None:
        name = os.name
    if uid is None:
        uid = os.geteuid() if hasattr(os, "geteuid") else -1
    if has_nproc is None:
        import resource
        has_nproc = hasattr(resource, "RLIMIT_NPROC")
    if has_wait4 is None:
        has_wait4 = hasattr(os, "wait4")
    require(name == "posix" and type(uid) is int and uid > 0 and has_nproc is True
            and has_wait4 is True, "resource_host", "non-root POSIX RLIMIT_NPROC and wait4 required")


def load_core(root):
    # Called only after the mandatory source/dependency closure has been checked.
    if str(root) not in sys.path:
        sys.path.insert(0, str(root))
    module = importlib.import_module("src.crypto_autoresearcher.runner")
    require(Path(module.__file__).resolve() == Path(root) / "src/crypto_autoresearcher/runner.py",
            "import_origin", "core runner was shadowed")
    return module


def run_child(*, root, argv, cwd, env, stdout_fd, stderr_fd, context_fd,
              timeout_seconds, memory_bytes, cpu_seconds=None):
    """Explicit-env replacement for _run_child, reusing inspected low-level APIs."""
    host_supported()
    positive_number(timeout_seconds, "watchdog")
    exact_integer(memory_bytes, "memory_bytes", 1)
    core = load_core(root)
    core._locked_resource_policy(descendant_slots=0)
    limit = math.inf if cpu_seconds is None else positive_number(cpu_seconds, "cpu_limit")
    start = time.monotonic()
    process = None
    values = dict(return_code=None, timed_out=False, memory_killed=False,
                  infrastructure_error=None, stdout="", stderr="", cpu_seconds=0.0,
                  peak_rss_bytes=0, cpu_killed=False, group_quiescent=False, wall_seconds=0.0)
    try:
        process = subprocess.Popen(argv, cwd=cwd, env=dict(env), stdout=stdout_fd,
                                   stderr=stderr_fd, close_fds=True, pass_fds=(context_fd,),
                                   start_new_session=True,
                                   preexec_fn=core._resource_limiter(memory_bytes, limit, 0))
        (values["return_code"], values["timed_out"], values["memory_killed"],
         values["cpu_killed"], values["cpu_seconds"], values["peak_rss_bytes"],
         values["group_quiescent"], values["wall_seconds"]) = core._wait_for_child(
             process, timeout_seconds, memory_bytes, limit)
    except (OSError, subprocess.SubprocessError, ValueError) as exc:
        values["infrastructure_error"] = f"{type(exc).__name__}: {exc}"
        if process is not None:
            try:
                os.killpg(process.pid, signal.SIGKILL)
            except (OSError, ProcessLookupError):
                pass
            try:
                process.wait(timeout=2)
            except (OSError, subprocess.SubprocessError):
                pass
        values["wall_seconds"] = time.monotonic() - start
    os.fsync(stdout_fd)
    os.fsync(stderr_fd)
    values["stdout"] = read_fd(stdout_fd).decode("utf-8", "replace")
    values["stderr"] = read_fd(stderr_fd).decode("utf-8", "replace")
    child = core._ChildResult(**values)
    return child, {"source": "core _wait_for_child process table plus wait4 CPU",
                   "poll_sleep_seconds": 0.01, "sample_count": None,
                   "sample_count_available": False, "monitor_wall_seconds": values["wall_seconds"],
                   "peak_interpretation": "unavailable" if values["infrastructure_error"] else
                   ("observed_zero_with_sampling_limit" if not values["peak_rss_bytes"] else "sampled_lower_bound"),
                   "limitations": "ps duration increases sample spacing; brief RSS peaks may be missed; zero observed RSS is not zero memory; core does not expose sample count or wait4 ru_maxrss"}


def classify(child, postflight=None, output_ok=True):
    """Preserve the primary cause independently from every postflight failure."""
    get = (lambda k, default=None: child.get(k, default)) if isinstance(child, dict) else (
        lambda k, default=None: getattr(child, k, default))
    memory_marker = any(marker in str(get("stderr", "")).lower() for marker in
                        ("memoryerror", "cannot allocate memory", "out of memory", "std::bad_alloc"))
    if get("infrastructure_error") or get("group_quiescent") is not True or type(get("return_code")) is not int:
        base = "failed_infrastructure"
    elif get("timed_out") or get("memory_killed") or get("cpu_killed") or memory_marker:
        base = "resource_exhaustion"
    elif get("return_code") != 0:
        base = "failed_implementation"
    else:
        base = "completed_valid"
    failures = [name for name, passed in (postflight or {}).items() if passed is not True]
    status = base
    if base == "completed_valid":
        status = "failed_infrastructure" if failures else (
            "completed_valid" if output_ok is True else "completed_invalid")
    return {"child_status": base, "status": status, "valid": status == "completed_valid",
            "memory_failure_marker_observed": memory_marker,
            "postflight_failures": failures,
            "invalid_reason": None if status == "completed_valid" else
            "; ".join([base, *failures, *([] if output_ok else ["incomplete_or_invalid_output"])])}

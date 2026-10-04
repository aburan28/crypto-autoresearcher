"""Build and load the native kernels (``_kernels.c``) with ctypes.

The shared object is compiled on first use with the system C compiler and
cached under ``$CRYPTO_AR_GF2_CACHE`` (default ``~/.cache/crypto_autoresearcher/gf2``),
keyed by the sha256 of the source, the compiler command and the machine, so a
changed kernel or flag set never loads a stale binary.

``load()`` returns the ctypes library, or ``None`` when no compiler is
available or ``CRYPTO_AR_GF2_BACKEND=reference`` is set. Callers fall back to
the numpy reference in that case; ``CRYPTO_AR_GF2_BACKEND=native`` makes a
missing native build an error instead.
"""
from __future__ import annotations

import ctypes
import hashlib
import os
import platform
import shutil
import subprocess
import tempfile
from pathlib import Path

_SRC = Path(__file__).with_name("_kernels.c")
# No -march=native: the cache may sit on a home directory shared by machines
# with different CPUs. AVX2/AVX-512 width is selected at run time via
# ``target_clones`` when the compiler is GCC.
_FLAGS = ["-O3", "-fPIC", "-shared", "-std=gnu99"]
# OpenMP threads the trailing update inside one elimination. A compiler or
# runtime without it gets the same kernels single-threaded (same results).
# Prefer GCC: Ubuntu's ``cc`` is often clang, which ships without ``omp.h``
# even when libgomp is present, and silently falls back to one thread.
_OMP_FLAGS = ["-fopenmp"]
_lib = None
_lib_gil = None
_tried = False
build_info: dict = {}


def _cache_dir() -> Path:
    env = os.environ.get("CRYPTO_AR_GF2_CACHE")
    return Path(env) if env else Path.home() / ".cache" / "crypto_autoresearcher" / "gf2"


def _compiler_candidates() -> list[str]:
    """Ordered compilers to try. ``CC`` wins if set; otherwise prefer ``gcc``
    before ``cc``/``clang`` so OpenMP is available on common Ubuntu images."""
    out: list[str] = []
    for cc in (os.environ.get("CC"), "gcc", "cc", "clang"):
        if cc and shutil.which(cc) and cc not in out:
            out.append(cc)
    return out


def _compiler() -> str | None:
    cs = _compiler_candidates()
    return cs[0] if cs else None


def _declare(lib):
    P = ctypes.c_void_p
    i64 = ctypes.c_int64
    lib.gf2_column_pass.restype = P
    lib.gf2_column_pass.argtypes = [P, i64, i64, i64, ctypes.c_int, ctypes.POINTER(i64)]
    lib.gf2_column_pass_blocked.restype = P
    lib.gf2_column_pass_blocked.argtypes = [P, i64, i64, i64, ctypes.c_int, ctypes.POINTER(i64)]
    lib.gf2_column_pass_sb.restype = P
    lib.gf2_column_pass_sb.argtypes = [P, i64, i64, i64, ctypes.c_int, ctypes.POINTER(i64),
                                       ctypes.c_int, ctypes.c_int]
    lib.gf2_column_pass_blocked_mt.restype = P
    lib.gf2_column_pass_blocked_mt.argtypes = [P, i64, i64, i64, ctypes.c_int, ctypes.POINTER(i64),
                                               ctypes.c_int]
    lib.gf2_log_K.restype = i64
    lib.gf2_log_K.argtypes = [P]
    lib.gf2_log_nx.restype = i64
    lib.gf2_log_nx.argtypes = [P]
    lib.gf2_log_copy.restype = None
    lib.gf2_log_copy.argtypes = [P, P, P, P, P]
    lib.gf2_log_copy_meta.restype = None
    lib.gf2_log_copy_meta.argtypes = [P, P, P, P]
    lib.gf2_log_xs.restype = P
    lib.gf2_log_xs.argtypes = [P]
    lib.gf2_log_free.restype = None
    lib.gf2_log_free.argtypes = [P]
    lib.gf2_row_pass.restype = i64
    lib.gf2_row_pass.argtypes = [P, i64, i64, i64, P, P, ctypes.POINTER(i64)]
    lib.gf2_ops_json_bound.restype = i64
    lib.gf2_ops_json_bound.argtypes = [i64, i64]
    lib.gf2_ops_json.restype = i64
    lib.gf2_ops_json.argtypes = [P, P, P, P, i64, P]
    lib.gf2_json_ints.restype = i64
    lib.gf2_json_ints.argtypes = [P, i64, P]
    lib.gf2_json_pairs.restype = i64
    lib.gf2_json_pairs.argtypes = [P, P, i64, P]
    lib.gf2_replay_planes.restype = None
    lib.gf2_replay_planes.argtypes = [P, i64, i64, i64, P, P, P, P, i64, P]
    lib.gf2_replay_direct.restype = None
    lib.gf2_replay_direct.argtypes = [P, i64, i64, P, P, P, P, i64, ctypes.c_int, P]
    lib.gf2_backtrace.restype = None
    lib.gf2_backtrace.argtypes = [P, i64, P, P, P, i64]
    lib.gf2_xor_bits.restype = None
    lib.gf2_xor_bits.argtypes = [P, i64, P, P, i64]
    lib.gf2_xor_rows_prefix.restype = None
    lib.gf2_xor_rows_prefix.argtypes = [P, i64, P, i64, i64, P]
    lib.gf2_products.restype = None
    lib.gf2_products.argtypes = [P, i64, i64, i64, P, i64, P]
    return lib


def load_holding_gil():
    """The same library loaded through ctypes.PyDLL: calls keep the GIL.

    ctypes.CDLL releases the GIL around every call. For a call of a few
    microseconds that is a loss under threads (each release risks waiting a
    whole switch interval to get the GIL back: the convoy effect), so small
    calls use this handle and only large ones release the GIL."""
    return _lib_gil if load() is not None else None


def load():
    """Return the loaded native library or None (see module docstring)."""
    global _lib, _lib_gil, _tried
    if _tried:
        return _lib
    _tried = True
    mode = os.environ.get("CRYPTO_AR_GF2_BACKEND", "auto")
    if mode == "reference":
        build_info.update(backend="reference", reason="CRYPTO_AR_GF2_BACKEND=reference")
        return None
    try:
        _lib = _build_and_load()
        _lib_gil = _declare(ctypes.PyDLL(build_info["so"]))
    except Exception as exc:  # no compiler, compile error, load error
        build_info.update(backend="reference", reason=f"native build unavailable: {exc}")
        if mode == "native":
            raise
        _lib = None
    return _lib


def _build_and_load():
    compilers = _compiler_candidates()
    if not compilers:
        raise RuntimeError("no C compiler found (set CC)")
    src = _SRC.read_bytes()
    errors = []
    # Try every (compiler, flags) pair: OpenMP first on each compiler, then
    # without. GCC+OpenMP is the common win; clang without omp.h used to make
    # the whole OpenMP attempt fail and permanently sit on one thread.
    for cc in compilers:
        for flags in ([*_FLAGS, *_OMP_FLAGS], list(_FLAGS)):
            try:
                so = _compile(cc, src, flags)
                lib = _declare(ctypes.CDLL(str(so)))
            except (RuntimeError, OSError) as exc:
                errors.append(f"{cc} {' '.join(flags)}: {exc}")
                continue
            build_info.update(
                backend="native", so=str(so),
                source_sha256=hashlib.sha256(src).hexdigest(),
                compiler=cc, flags=flags, openmp="-fopenmp" in flags,
            )
            return lib
    raise RuntimeError("; ".join(errors))


def _compile(cc, src, flags):
    key = hashlib.sha256(
        src + " ".join([cc, *flags, platform.machine(), platform.system()]).encode()
    ).hexdigest()[:24]
    d = _cache_dir()
    d.mkdir(parents=True, exist_ok=True)
    so = d / f"gf2kernels-{key}.so"
    if so.exists():
        return so
    # Serialize concurrent first-use builds of the same key. ``os.replace`` is
    # atomic, but without a lock every worker compiles a full -O3 binary.
    lock_path = d / f"gf2kernels-{key}.lock"
    with open(lock_path, "a+b") as lockf:
        try:
            import fcntl
            fcntl.flock(lockf.fileno(), fcntl.LOCK_EX)
        except (ImportError, OSError):
            pass
        if so.exists():
            return so
        with tempfile.TemporaryDirectory(dir=d) as tmp:
            out = Path(tmp) / so.name
            cmd = [cc, *flags, str(_SRC), "-o", str(out)]
            proc = subprocess.run(cmd, capture_output=True, text=True)
            if proc.returncode != 0:
                raise RuntimeError(f"{' '.join(cmd)} failed:\n{proc.stderr}")
            os.replace(out, so)
    return so

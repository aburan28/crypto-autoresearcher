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
# with different CPUs, and the XOR loops vectorise on the baseline ISA.
_FLAGS = ["-O3", "-fPIC", "-shared", "-std=gnu99"]
_lib = None
_lib_gil = None
_tried = False
build_info: dict = {}


def _cache_dir() -> Path:
    env = os.environ.get("CRYPTO_AR_GF2_CACHE")
    return Path(env) if env else Path.home() / ".cache" / "crypto_autoresearcher" / "gf2"


def _compiler() -> str | None:
    for cc in (os.environ.get("CC"), "cc", "gcc", "clang"):
        if cc and shutil.which(cc):
            return cc
    return None


def _declare(lib):
    P = ctypes.c_void_p
    i64 = ctypes.c_int64
    lib.gf2_column_pass.restype = P
    lib.gf2_column_pass.argtypes = [P, i64, i64, i64, ctypes.c_int, ctypes.POINTER(i64)]
    lib.gf2_column_pass_blocked.restype = P
    lib.gf2_column_pass_blocked.argtypes = [P, i64, i64, i64, ctypes.c_int, ctypes.POINTER(i64)]
    lib.gf2_log_K.restype = i64
    lib.gf2_log_K.argtypes = [P]
    lib.gf2_log_nx.restype = i64
    lib.gf2_log_nx.argtypes = [P]
    lib.gf2_log_copy.restype = None
    lib.gf2_log_copy.argtypes = [P, P, P, P, P]
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
    cc = _compiler()
    if cc is None:
        raise RuntimeError("no C compiler found (set CC)")
    src = _SRC.read_bytes()
    key = hashlib.sha256(
        src + " ".join([cc, *_FLAGS, platform.machine(), platform.system()]).encode()
    ).hexdigest()[:24]
    d = _cache_dir()
    d.mkdir(parents=True, exist_ok=True)
    so = d / f"gf2kernels-{key}.so"
    if not so.exists():
        with tempfile.TemporaryDirectory(dir=d) as tmp:
            out = Path(tmp) / so.name
            cmd = [cc, *_FLAGS, str(_SRC), "-o", str(out)]
            proc = subprocess.run(cmd, capture_output=True, text=True)
            if proc.returncode != 0:
                raise RuntimeError(f"{' '.join(cmd)} failed:\n{proc.stderr}")
            os.replace(out, so)  # atomic: concurrent builders race harmlessly
    lib = _declare(ctypes.CDLL(str(so)))
    build_info.update(backend="native", so=str(so), source_sha256=hashlib.sha256(src).hexdigest(),
                      compiler=cc, flags=list(_FLAGS))
    return lib

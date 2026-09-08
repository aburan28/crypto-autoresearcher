"""Shared run-record utilities (artifact writing, hashing). Orchestration
helper, not one of the two independent enumerators."""
from __future__ import annotations

import hashlib
import json
import os
import subprocess
import sys
from datetime import datetime, timezone

import numpy as np


def sha256_file(path: str) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def sha256_bytes(b: bytes) -> str:
    return hashlib.sha256(b).hexdigest()


def sha256_json(obj) -> str:
    return sha256_bytes(json.dumps(obj, sort_keys=True, default=str).encode())


def now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def write_json(path: str, obj):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w") as f:
        json.dump(obj, f, indent=2, default=_default)


def _default(o):
    if isinstance(o, (np.integer,)):
        return int(o)
    if isinstance(o, (np.floating,)):
        return float(o)
    if isinstance(o, np.ndarray):
        return o.tolist()
    return str(o)


def write_array(path: str, arr: np.ndarray) -> str:
    os.makedirs(os.path.dirname(path), exist_ok=True)
    np.save(path, arr)
    npy_path = path if path.endswith(".npy") else path + ".npy"
    return sha256_file(npy_path)


def counter_to_zn_array(counter: dict, N: int, key_to_index) -> np.ndarray:
    """Map a {target_key: count} dict to a length-N int64 array over Z/N
    indices, via key_to_index(key) -> int in [0, N)."""
    arr = np.zeros(N, dtype=np.int64)
    for key, cnt in counter.items():
        idx = key_to_index(key)
        arr[idx] = cnt
    return arr


def git_commit() -> str:
    try:
        return subprocess.check_output(
            ["git", "rev-parse", "HEAD"], cwd=os.path.dirname(__file__)
        ).decode().strip()
    except Exception:
        return "unknown"


def git_dirty() -> bool:
    try:
        out = subprocess.check_output(
            ["git", "status", "--porcelain"], cwd=os.path.dirname(__file__)
        ).decode().strip()
        return len(out) > 0
    except Exception:
        return True


def environment_info() -> dict:
    import platform
    import sympy
    return {
        "operating_system": platform.system(),
        "architecture": platform.machine(),
        "python_version": sys.version,
        "dependencies": {
            "numpy": np.__version__,
            "sympy": sympy.__version__,
        },
        "sampler": "numpy.random.Generator(PCG64(seed64)) seeded per replication.null_draw_derivation",
        "primality_method_for_curve_N": "own deterministic Miller-Rabin (bases 2..37) + trial division to sqrt(N), independent methods (see curve_gen.py); sympy used only for the field-prime p search and prime-power/Bose-Chowla field construction, not for certifying N",
    }

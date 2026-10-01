"""Shared constants and helpers for EXP-CERTBIN-060020 (the n = 19 cell).

Everything here is n = 19-specific or generic plumbing (deterministic gzip
JSONL, hashing, E_hex layout, timing). No engine code.
"""
from __future__ import annotations

import gzip
import hashlib
import io
import json
import os
import resource
import sys
import time
from itertools import combinations
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[3]
EXP = ROOT / "experiments" / "EXP-CERTBIN-060020"
IMPL = EXP / "impl"
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))  # import rule: src/ on sys.path (recorded)

EXPERIMENT_ID = "EXP-CERTBIN-060020"

# ---------------------------------------------------------------------------
# literal parameters (specification inputs.literal_parameters)
# ---------------------------------------------------------------------------
N = 19
MODULUS = 524327  # t^19 + t^5 + t^2 + t + 1
L = 10
NV = 20
NEQ = 19
A = 46693
B = 306147
ORDER = 523646
H = 2
Q = 261823
P_PT = (82737, 282850)
Q_PT = (510336, 243234)
K_Q = 5170
TR_A = 1
TAU_READING = [1 if j in (0, 17) else 0 for j in range(19)]

# n = 17 slice (C-SLICE17)
N17 = 17
MODULUS17 = (1 << 17) | (1 << 3) | 1
L17 = 9
NV17 = 18
NEQ17 = 17

SEEDS = {
    "S_selftest": 2026092460600,
    "S3-PRIMARY": 2026092460601,
    "N-CONV19": 2026092460602,
    "N-ELL19": 2026092460603,
    "N-F219": 2026092460604,
    "N-AFF19": 2026092460605,
    "F-RANDX19": 2026092460606,
}

PINNED_COMMIT = "934bee5"
KERNELS_C_SHA256 = "c8f79d5961fffaf80428cdd29d0a53bfcc1e6d32ab07022931e3aacd926ca745"

# semi-regular references (specification object.ell_and_rc_b (6))
REF_SUB = [0, 0, 18, 360, 3267]
REF_UNSUB = [0, 0, 19, 399, 3819]
REF_T5_W4 = {"one": False, "final_dim": 4427, "dims_by_deg": [0, 1, 38, 551, 4427],
             "iterations_to_fixpoint": 1}
DIM_BP_LE = {-1: 0, 0: 1, 1: 20, 2: 191, 3: 1160}  # dim B'_{<=d}, 19 variables
T4_CONST = 1160

# ---------------------------------------------------------------------------
# monomial layout of a system (object.E_layout)
# ---------------------------------------------------------------------------


def eq_monomials(nv):
    """mu_order(2, nv): degree ascending, then ascending sorted index tuple."""
    out = [()]
    out += [(i,) for i in range(nv)]
    out += list(combinations(range(nv), 2))
    return out


EQ_MONS = eq_monomials(NV)          # 211
NCOL = len(EQ_MONS)
assert NCOL == 211
EQ_MASKS = np.array([sum(1 << i for i in m) for m in EQ_MONS], dtype=np.int64)
COL_OF_MON = {m: c for c, m in enumerate(EQ_MONS)}


def E_to_hex(E):
    """E (neq x ncol uint8) -> list of hex strings, bit j (LSB first) = column j."""
    out = []
    for row in np.asarray(E, dtype=np.uint8):
        v = 0
        for j in np.flatnonzero(row):
            v |= 1 << int(j)
        out.append(format(v, "x"))
    return out


def E_from_hex(hexes, ncol=NCOL):
    E = np.zeros((len(hexes), ncol), dtype=np.uint8)
    for k, h in enumerate(hexes):
        v = int(h, 16)
        j = 0
        while v:
            if v & 1:
                E[k, j] = 1
            v >>= 1
            j += 1
    return E


def E_sha256(E):
    return hashlib.sha256(json.dumps(E_to_hex(E), separators=(",", ":")).encode()).hexdigest()


def E_to_eqs(E, masks=EQ_MASKS):
    """E -> list of lists of monomial masks (engine input)."""
    return [[int(masks[j]) for j in np.flatnonzero(E[k])] for k in range(E.shape[0])]


# ---------------------------------------------------------------------------
# deterministic IO
# ---------------------------------------------------------------------------


def canon(obj):
    return json.dumps(obj, sort_keys=True, separators=(",", ":"))


def jsonl_gz_bytes(records):
    buf = io.BytesIO()
    with gzip.GzipFile(fileobj=buf, mode="wb", mtime=0, filename="", compresslevel=6) as gz:
        for r in records:
            gz.write((canon(r) + "\n").encode())
    return buf.getvalue()


def write_jsonl_gz(path, records):
    data = jsonl_gz_bytes(records)
    tmp = Path(str(path) + ".tmp")
    tmp.write_bytes(data)
    os.replace(tmp, path)
    return hashlib.sha256(data).hexdigest()


def read_jsonl_gz(path):
    with gzip.open(path, "rt") as f:
        return [json.loads(line) for line in f if line.strip()]


def write_json(path, obj):
    tmp = Path(str(path) + ".tmp")
    tmp.write_text(json.dumps(obj, indent=1, sort_keys=True, default=_default) + "\n")
    os.replace(tmp, path)


def _default(o):
    if isinstance(o, (np.integer,)):
        return int(o)
    if isinstance(o, (np.bool_,)):
        return bool(o)
    if isinstance(o, np.ndarray):
        return o.tolist()
    raise TypeError(type(o))


def sha256_file(path):
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def utc_now():
    return time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())


def peak_rss_mib():
    return resource.getrusage(resource.RUSAGE_SELF).ru_maxrss / 1024.0


def impl_module_hashes():
    return {p.name: sha256_file(p) for p in sorted(IMPL.glob("*.py"))}


class PhaseTimer:
    def __init__(self):
        self.records = []

    def __call__(self, name):
        timer = self

        class _Ctx:
            def __enter__(self_inner):
                self_inner.t0 = time.time()
                self_inner.start = utc_now()
                return self_inner

            def __exit__(self_inner, *exc):
                timer.records.append({
                    "phase": name, "start_utc": self_inner.start, "end_utc": utc_now(),
                    "wall_seconds_measured": round(time.time() - self_inner.t0, 3),
                    "process_peak_rss_mib_so_far_measured": round(peak_rss_mib(), 1),
                    "completed": exc[0] is None,
                })
                return False

        return _Ctx()


def log(*a):
    print(f"[{utc_now()}]", *a, flush=True)

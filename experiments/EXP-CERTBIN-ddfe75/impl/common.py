"""Shared constants and helpers for EXP-CERTBIN-ddfe75 (N-CONV).

E layout (specification object.E_layout): a system is 17 rows; row k is f_k,
held here as a Python int of 172 bits, bit j = column j of mu_order(2, 18)
(degree ascending, then ascending sorted index tuple). Column 0 is the
constant, columns 1..18 are v_0..v_17, columns 19..171 are the 153 pairs.
E_hex is the list of the 17 rows as lowercase hex without prefix;
E_sha256 = sha256(json.dumps(E_hex)) (the RC-1 convention of
EXP-CERTBIN-e94b27 instances.py, checked against the archived records).

The engine is IMPORTED from src/ (sys.path insertion; no editable install).
"""
from __future__ import annotations

import datetime as _dt
import gzip
import hashlib
import json
import os
import sys
from itertools import combinations
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
EXP = ROOT / "experiments" / "EXP-CERTBIN-ddfe75"
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

NV = 18
NEQ = 17
NCOL = 172
L = 9  # V = {deg < 9}

# column layout ------------------------------------------------------------
COLS = [()] + [(i,) for i in range(NV)] + list(combinations(range(NV), 2))
assert len(COLS) == NCOL
COL_OF = {m: j for j, m in enumerate(COLS)}
COL_MASK = []
for _m in COLS:
    _s = 0
    for _i in _m:
        _s |= 1 << _i
    COL_MASK.append(_s)
MASK_TO_COL = {m: j for j, m in enumerate(COL_MASK)}
QUAD_COLS = list(range(19, NCOL))
LIN_COLS = list(range(1, 19))
BILINEAR_COLS = [COL_OF[(i, 9 + j)] for i in range(9) for j in range(9)]
QUAD_MASK = 0
for _j in QUAD_COLS:
    QUAD_MASK |= 1 << _j
LOW_MASK = (1 << 19) - 1  # columns 0..18

ARCHIVED_ARMS = ["S3-U62", "S3-C20", "S3-S62", "NULL-AFF62", "NULL-F262", "NELL-A20"]
FRESH_ARMS = ["N-CONV", "N-CONVL", "N-CONV17", "N-ELL144"]
ARM_SEEDS = {"N-CONV": 2026092450101, "N-CONVL": 2026092450102,
             "N-CONV17": 2026092450103, "N-ELL144": 2026092450104}
SEED_SELFTEST = 2026092450199
SET_OF_ARM = {"S3-U62": "U62", "S3-C20": "C20", "S3-S62": "S62",
              "NULL-AFF62": "N-AFF62", "NULL-F262": "N-F262"}
MAX_ATTEMPTS = 256

# DEVELOPMENT-ONLY overrides (pipeline debugging on reduced, differently seeded
# streams in a scratch directory). The driver and the verifier REFUSE to write
# under experiments/ when either is set; the run manifest records that both
# were unset.
DEV_SLOTS = int(os.environ.get("NCONV_DEV_SLOTS", "0") or 0)
DEV_SEED_OFFSET = int(os.environ.get("NCONV_DEV_SEED_OFFSET", "0") or 0)
if DEV_SEED_OFFSET:
    ARM_SEEDS = {k: v + DEV_SEED_OFFSET for k, v in ARM_SEEDS.items()}

INPUT_FILES = {
    "experiments/EXP-CERTBIN-e94b27/runs/RUN-CERTBIN-c417e0/instance-sets.json":
        "64dffd01f693289ac533aec3348319cea6c85ffaaea11c4d63ddcd607cd85a7a",
    "experiments/EXP-CERTBIN-e94b27/runs/RUN-CERTBIN-c417e0/closures.jsonl.gz":
        "d0186e69b8492f65dd51ac5eb10295d90031ec711e4adbb0d62e7b5090ef917a",
    "experiments/EXP-CERTBIN-e94b27/runs/RUN-CERTBIN-c417e0/certificates.jsonl.gz":
        "cb87db676674af28246bd3c8d2631e78d057ad91f48535879294b48a2b8fd53f",
    "experiments/EXP-CERTBIN-4e92d7/runs/RUN-CERTBIN-3b7e05/curve.json":
        "aa3eb4d0f3e9da68d710b8946e2e4c3d13de1b991882f23218d259df9615201d",
    "experiments/EXP-CERTBIN-4e92d7/runs/RUN-CERTBIN-3b7e05/checkpoint/p1-instances.json.gz":
        "5ab5f4b60a983570a1edde9fd40ad4d90fc6683c412b00847ac7db40f7e45f11",
    "coordination/review/certbin-20260924-3d7e1a/reviews/TASK-20260924-d95e70/j9-ptm/n-ell-instances.json":
        "d9f37b17519daff42d462be30200c1f56fb45f87de83aa61e45d393e12ca997b",
    "coordination/review/certbin-20260924-3d7e1a/reviews/TASK-20260924-d95e70/j9-ptm/o2-engine-and-own.json":
        "b39e113f33f846ae5eb4b0f70570efcd736f868fd12dbee7ae56d7e33b471793",
}
P_INSTANCE_SETS = ROOT / "experiments/EXP-CERTBIN-e94b27/runs/RUN-CERTBIN-c417e0/instance-sets.json"
P_RC1_CLOSURES = ROOT / "experiments/EXP-CERTBIN-e94b27/runs/RUN-CERTBIN-c417e0/closures.jsonl.gz"
P_CURVE = ROOT / "experiments/EXP-CERTBIN-4e92d7/runs/RUN-CERTBIN-3b7e05/curve.json"
P_P1 = ROOT / "experiments/EXP-CERTBIN-4e92d7/runs/RUN-CERTBIN-3b7e05/checkpoint/p1-instances.json.gz"
P_NELL = ROOT / "coordination/review/certbin-20260924-3d7e1a/reviews/TASK-20260924-d95e70/j9-ptm/n-ell-instances.json"
P_O2ENG = ROOT / "coordination/review/certbin-20260924-3d7e1a/reviews/TASK-20260924-d95e70/j9-ptm/o2-engine-and-own.json"

KERNELS_C_PIN = "c8f79d5961fffaf80428cdd29d0a53bfcc1e6d32ab07022931e3aacd926ca745"
ENGINE_COMMIT = "934bee5"


# helpers ------------------------------------------------------------------
def now():
    return _dt.datetime.now(_dt.timezone.utc).isoformat()


def sha256_file(p):
    h = hashlib.sha256()
    with open(p, "rb") as f:
        for b in iter(lambda: f.read(1 << 20), b""):
            h.update(b)
    return h.hexdigest()


def sha256_bytes(b):
    return hashlib.sha256(b).hexdigest()


def rows_to_hex(rows):
    return [format(r, "x") for r in rows]


def hex_to_rows(E_hex):
    return [int(h, 16) for h in E_hex]


def e_sha256(E_hex):
    return hashlib.sha256(json.dumps(E_hex).encode()).hexdigest()


def rows_to_eqs(rows):
    """17 row ints -> engine eqs: per row, list of monomial masks."""
    out = []
    for r in rows:
        ms = []
        x = r
        while x:
            b = (x & -x).bit_length() - 1
            ms.append(COL_MASK[b])
            x &= x - 1
        out.append(ms)
    return out


def popcount(x):
    return bin(x).count("1")


def write_json(p, obj):
    p = Path(p)
    tmp = p.with_suffix(p.suffix + ".tmp")
    with open(tmp, "w") as f:
        json.dump(obj, f, indent=1, sort_keys=False, default=_default)
        f.write("\n")
    os.replace(tmp, p)


def _default(o):
    try:
        import numpy as np
        if isinstance(o, np.integer):
            return int(o)
        if isinstance(o, np.bool_):
            return bool(o)
        if isinstance(o, np.ndarray):
            return o.tolist()
    except ImportError:
        pass
    raise TypeError(type(o))


def write_jsonl_gz(p, rows):
    """Deterministic gzip (mtime 0) so hashes are reproducible."""
    p = Path(p)
    tmp = p.with_suffix(p.suffix + ".tmp")
    with open(tmp, "wb") as raw:
        with gzip.GzipFile(filename="", fileobj=raw, mode="wb", mtime=0) as g:
            for r in rows:
                g.write((json.dumps(r, separators=(",", ":"), default=_default) + "\n").encode())
    os.replace(tmp, p)


def read_jsonl_gz(p):
    with gzip.open(p, "rt") as f:
        return [json.loads(l) for l in f if l.strip()]


def jsonl_gz_bytes(rows):
    import io
    buf = io.BytesIO()
    with gzip.GzipFile(filename="", fileobj=buf, mode="wb", mtime=0) as g:
        for r in rows:
            g.write((json.dumps(r, separators=(",", ":"), default=_default) + "\n").encode())
    return buf.getvalue()

"""Shared constants and helpers for EXP-CERTBIN-e94b27 impl/ (C-SRC, hashing,
JSON I/O). Never imported by verifier/."""
import datetime
import gzip
import hashlib
import json
import os

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
EXP_ID = "EXP-CERTBIN-e94b27"
RUN_ID = "RUN-CERTBIN-c417e0"
TASK_ID = "TASK-20260924-41c7be"
SRC_RUN = "experiments/EXP-CERTBIN-4e92d7/runs/RUN-CERTBIN-3b7e05"
RECEIPT = "coordination/design/certbin-trace-20260923-5d0b8e/archives/TASK-20260923-c2e57b/snapshot-receipt.json"
DESIGN_RECEIPT = "coordination/design/certbin-followups-20260924/archives/TASK-20260924-d3a90c/snapshot-receipt.json"
SPEC = "experiments/EXP-CERTBIN-e94b27/specification.yaml"
INPUT_FILES = [
    SRC_RUN + "/curve.json",
    SRC_RUN + "/targets-F-S3.jsonl.gz",
    SRC_RUN + "/checkpoint/p1-instances.json.gz",
    SRC_RUN + "/targets-F-AFF-1.jsonl.gz",
    SRC_RUN + "/targets-F-NULLF2.jsonl.gz",
    "experiments/EXP-CERTBIN-4e92d7/impl/gf2n.py",
    "experiments/EXP-CERTBIN-4e92d7/impl/curve.py",
    "experiments/EXP-CERTBIN-4e92d7/impl/macaulay.py",
    "experiments/EXP-CERTBIN-4e92d7/impl/elim.py",
]
S_SELFTEST = 2026092430099
MEM_LIMIT = 3 * 1024 ** 3
W5_WATCHDOG = 14400
RUN_WATCHDOG = 172800


def now():
    return datetime.datetime.now(datetime.timezone.utc).isoformat()


def sha256_file(p):
    h = hashlib.sha256()
    with open(p, "rb") as f:
        for b in iter(lambda: f.read(1 << 20), b""):
            h.update(b)
    return h.hexdigest()


def jdefault(o):
    if isinstance(o, np.integer):
        return int(o)
    if isinstance(o, np.floating):
        return float(o)
    if isinstance(o, np.bool_):
        return bool(o)
    if isinstance(o, np.ndarray):
        return o.tolist()
    if isinstance(o, (set, tuple)):
        return list(o)
    raise TypeError(type(o))


def dump_json(p, obj):
    tmp = p + ".tmp"
    with open(tmp, "w") as f:
        json.dump(obj, f, indent=1, default=jdefault)
        f.write("\n")
    os.replace(tmp, p)


def dump_json_gz(p, obj):
    tmp = p + ".tmp"
    with gzip.open(tmp, "wt") as f:
        json.dump(obj, f, default=jdefault)
    os.replace(tmp, p)


def load_json_gz(p):
    with gzip.open(p, "rt") as f:
        return json.load(f)


def c_src():
    """C-SRC: sha256 of every input vs the TASK-20260923-c2e57b receipt, plus the
    specification vs the TASK-20260924-d3a90c design receipt."""
    rec = json.load(open(os.path.join(REPO, RECEIPT)))["path_sha256"]
    drec = json.load(open(os.path.join(REPO, DESIGN_RECEIPT)))["path_sha256"]
    rows = []
    ok = True
    for p in INPUT_FILES:
        got = sha256_file(os.path.join(REPO, p))
        exp = rec.get(p)
        m = (exp is not None and got == exp)
        ok &= m
        rows.append({"path": p, "sha256": got, "receipt_sha256": exp, "match": m})
    spec_got = sha256_file(os.path.join(REPO, SPEC))
    spec_exp = drec.get(SPEC)
    spec_ok = spec_got == spec_exp
    return {"control": "C-SRC", "receipt": RECEIPT, "inputs": rows,
            "specification": {"path": SPEC, "sha256": spec_got, "design_receipt": DESIGN_RECEIPT,
                              "design_receipt_sha256": spec_exp, "byte_identical": spec_ok},
            "pass": bool(ok and spec_ok), "checked_at": now()}

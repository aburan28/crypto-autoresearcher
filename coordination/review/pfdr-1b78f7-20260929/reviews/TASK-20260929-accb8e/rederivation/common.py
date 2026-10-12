"""Shared loaders for TASK-20260929-accb8e's blind re-derivation (J2a, J3).

Own code, written from specification.yaml v1 + AMD-20260929-1de84f +
AMD-20260929-430f44 text only. Imports no engine module. Every committed file
opened is logged to checks/read-log.txt through rl.opened()."""
import gzip, json, os, sys, hashlib

W = "/home/user/crypto-autoresearcher/coordination/review/pfdr-1b78f7-20260929/reviews/TASK-20260929-accb8e"
sys.path.insert(0, os.path.join(W, "checks"))
import rl  # noqa: E402

WT = rl.WT
EXP = os.path.join(WT, "experiments", "EXP-PFDR-1b78f7")
RUNS = os.path.join(EXP, "runs")
OUT = os.path.join(W, "rederivation", "out")
os.makedirs(OUT, exist_ok=True)

RUN = {
    "R10": "RUN-PFDR-1b78f7-census-m3",
    "R11": "RUN-PFDR-1b78f7-census-m4",
    "R12": "RUN-PFDR-1b78f7-census-m5",
    "R13": "RUN-PFDR-1b78f7-rho",
    "R14": "RUN-PFDR-1b78f7-j0",
    "R16": "RUN-PFDR-1b78f7-stage-r",
}
MAIN_BITS = [12, 14, 16, 18, 20, 22, 24, 26, 28, 30, 32]
J0_BITS = [12, 14, 16, 18, 20, 22, 24]
MAIN_ARMS = ["subgroup", "dickson", "small_x", "random_sub_r0", "random_sub_r1",
             "random_sub_r2", "random_dick_r0", "random_dick_r1", "random_dick_r2"]
J0_ARMS = ["j0_coset", "j0_random_r0", "j0_random_r1", "j0_random_r2"]
MODES = ["census", "on"]
STRUCT = ["subgroup", "small_x", "dickson"]
RAND = {"subgroup": ["random_sub_r0", "random_sub_r1", "random_sub_r2"],
        "small_x": ["random_sub_r0", "random_sub_r1", "random_sub_r2"],
        "dickson": ["random_dick_r0", "random_dick_r1", "random_dick_r2"]}


def read_jsonl_gz(path, note):
    rl.opened(path, note)
    out = []
    with gzip.open(path, "rt") as f:
        for line in f:
            if line.strip():
                out.append(json.loads(line))
    return out


def read_json(path, note):
    rl.opened(path, note)
    with open(path) as f:
        return json.load(f)


def row_m(r):
    if "m" in r and r["m"] is not None:
        return int(r["m"])
    meth = r.get("method")
    if meth and meth.startswith("ic_m"):
        return int(meth[4:])
    return None


def is_rho(r):
    return r.get("method") == "rho"


def key_of(r):
    if is_rho(r):
        return (r.get("panel"), "rho", r["bits"], r["curve"])
    return (r.get("panel"), row_m(r), r["bits"], r["curve"], r.get("arm"), r.get("mode"))


def sort_key(r):
    if is_rho(r):
        return (r["bits"], r["curve"], 0, "", "")
    return (r["bits"], r["curve"], row_m(r), r.get("arm") or "", r.get("mode") or "")


def stair_key(s):
    return (s["bits"], s["curve"], s["m"], s.get("arm") or "", s.get("mode") or "")


def canon_bytes(records):
    lines = [json.dumps(rec, sort_keys=True, separators=(",", ":")) for rec in records]
    return ("\n".join(lines) + "\n").encode("utf-8") if lines else b""


def sha256_bytes(b):
    return hashlib.sha256(b).hexdigest()


def sha256_file(path):
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def dump(name, obj):
    p = os.path.join(OUT, name)
    with open(p, "w") as f:
        json.dump(obj, f, indent=1, sort_keys=True, default=str)
    return p

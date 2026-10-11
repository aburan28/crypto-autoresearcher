"""Shared helpers for TASK-20260929-575e80 (no engine import; json/gzip/math only).

Reads the canonical rows at 66d6eab71 through the R15 view (AMD-20260929-430f44 M-6).
"""
import gzip
import json
import math
import os

WT = "/tmp/claude-0/-home-user/015c3767-cc03-52db-9b0c-bd2aa6c26537/scratchpad/wt-twfloor-66d6eab71"
RUNS = os.path.join(WT, "experiments", "EXP-PFDR-1b78f7", "runs")
P = "RUN-PFDR-1b78f7-"
HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, "out")
os.makedirs(OUT, exist_ok=True)

CANON = {
    "census-m3": os.path.join(RUNS, P + "census-m3", "rows.jsonl.gz"),
    "census-m4": os.path.join(RUNS, P + "census-m4", "merged", "rows.jsonl.gz"),
    "census-m5": os.path.join(RUNS, P + "census-m5", "rows.jsonl.gz"),
    "j0": os.path.join(RUNS, P + "j0", "rows.jsonl.gz"),
    "rho": os.path.join(RUNS, P + "rho", "rows.jsonl.gz"),
    "stage-r": os.path.join(RUNS, P + "stage-r", "rows.jsonl.gz"),
}
STRUCT = ("subgroup", "dickson", "small_x")
RANDOM_ARMS = ("random_sub_r0", "random_sub_r1", "random_sub_r2",
               "random_dick_r0", "random_dick_r1", "random_dick_r2")
J0_RANDOMS = ("j0_random_r0", "j0_random_r1", "j0_random_r2")
RANDOMS_OF = {"subgroup": ("random_sub_r0", "random_sub_r1", "random_sub_r2"),
              "small_x": ("random_sub_r0", "random_sub_r1", "random_sub_r2"),
              "dickson": ("random_dick_r0", "random_dick_r1", "random_dick_r2")}


def iter_jsonl(path):
    op = gzip.open if path.endswith(".gz") else open
    with op(path, "rt") as fh:
        for line in fh:
            if line.strip():
                yield json.loads(line)


def m_of(r):
    meth = str(r.get("method", ""))
    if meth.startswith("ic_m"):
        return int(meth[4:])
    return r.get("m")


def arm_class(arm):
    if arm in RANDOM_ARMS:
        return "random"
    if arm in STRUCT:
        return "structured"
    if arm == "known_log":
        return "known_log"
    if arm == "j0_coset":
        return "j0_coset"
    if arm in J0_RANDOMS:
        return "j0_random"
    return "other"


def load_panel_rows(names=("census-m3", "census-m4", "census-m5", "j0")):
    """Solver-instance rows (main and j0 panels) of the canonical sets."""
    out = []
    for n in names:
        for r in iter_jsonl(CANON[n]):
            if r.get("panel") in ("main", "j0") and r.get("arm"):
                r["_src"] = n
                out.append(r)
    return out


def unmatched_size_set(rows):
    """AMD-20260929-1de84f C-4 as analyze_census.py implements it: (m, bits, curve, arm) of a
    structured main-panel arm whose fb_size differs from its matched random arms' size."""
    idx = {}
    for r in rows:
        if r.get("panel") == "main":
            idx[(m_of(r), r["bits"], r["curve"], r["arm"], r.get("mode"))] = r
    um = set()
    for r in rows:
        if r.get("panel") != "main" or r.get("arm") not in STRUCT:
            continue
        key = (m_of(r), r["bits"], r["curve"], r["arm"])
        sA = sR = None
        for mode in ("census", "on"):
            a = idx.get(key[:3] + (r["arm"], mode))
            if sA is None and a is not None and a.get("fb_size") is not None:
                sA = a["fb_size"]
            for arm in RANDOMS_OF[r["arm"]]:
                q = idx.get(key[:3] + (arm, mode))
                if sR is None and q is not None and q.get("fb_size") is not None:
                    sR = q["fb_size"]
        if sA is not None and sR is not None and sA != sR:
            um.add(key)
    return um


def r_frozen(r):
    rr = r["relations"]
    if r.get("mode") == "on":
        rr += sum(r["harvest"]["on"]["rows_fed"].values())
    return rr


def evaluable(r, um):
    """A7's own inclusion rule (analyze_census.py lines 795-809)."""
    if r.get("panel") == "main" and (m_of(r), r["bits"], r["curve"], r["arm"]) in um:
        return False, "unmatched_size"
    if not (r.get("status") == "completed_valid" and r.get("harvest") is not None):
        return False, "not_usable"
    if not r.get("k_verified"):
        return False, "no_verified_k"
    if r_frozen(r) <= 0:
        return False, "r_le_0"
    return True, None


def ratio(S, r, N, c=2.0):
    """S / ((1/c) * sqrt(r N)); c = 2 is A7's convention, c = 1 the alternative."""
    return S / ((1.0 / c) * math.sqrt(r * N))


def key_of(r):
    return (r.get("panel"), r["bits"], r["curve"], m_of(r), r["arm"], r.get("mode"))


def dump(name, obj):
    path = os.path.join(OUT, name)
    with open(path, "w") as fh:
        json.dump(obj, fh, indent=1, sort_keys=True, default=str)
    return path

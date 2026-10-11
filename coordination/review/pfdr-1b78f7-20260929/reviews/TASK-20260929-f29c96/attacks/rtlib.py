"""TASK-20260929-f29c96 (red team, review-breakthrough) -- shared helpers.

Reads ONLY the committed package in the detached worktree at a32e70808.
Imports no solver module and no crypto_autoresearcher package module.
stats.py is loaded by file path (RT-6).  The A7 block of analysis.json is
stripped on load and never printed or written (RT-4).
"""
from __future__ import annotations

import gzip
import importlib.util
import json
import math
import os
import statistics

WT = "/tmp/claude-0/-home-user/015c3767-cc03-52db-9b0c-bd2aa6c26537/scratchpad/wt-census-a32e70808"
EXP = os.path.join(WT, "experiments", "EXP-PFDR-1b78f7")
RUNS = os.path.join(EXP, "runs")
P = "RUN-PFDR-1b78f7-"
OUT = os.path.dirname(os.path.abspath(__file__))
SCRATCH = "/tmp/claude-0/-home-user/015c3767-cc03-52db-9b0c-bd2aa6c26537/scratchpad/rt-f29c96"

CLASSES = ("TT", "TB", "SS")
STRUCT = ("subgroup", "small_x", "dickson")
RANDOMS = {"subgroup": ("random_sub_r0", "random_sub_r1", "random_sub_r2"),
           "small_x": ("random_sub_r0", "random_sub_r1", "random_sub_r2"),
           "dickson": ("random_dick_r0", "random_dick_r1", "random_dick_r2")}
RANDOM_ARMS = ("random_sub_r0", "random_sub_r1", "random_sub_r2",
               "random_dick_r0", "random_dick_r1", "random_dick_r2")
RUNGS = (12, 14, 16, 18, 20, 22, 24, 26, 28, 30, 32)
EXCURSIONS = [("subgroup", "TT", 3, 28), ("small_x", "SS", 4, 20),
              ("dickson", "SS", 4, 26), ("subgroup", "TT", 5, 16)]


def load_stats():
    path = os.path.join(WT, "src", "crypto_autoresearcher", "index_calculus", "stats.py")
    spec = importlib.util.spec_from_file_location("rt_f29c96_stats", path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def safe_analysis(path=None):
    """analysis.json with the A7 block removed before anything can print it (RT-4)."""
    path = path or os.path.join(RUNS, P + "analysis", "analysis.json")
    with open(path) as fh:
        d = json.load(fh)
    d.pop("A7_floor", None)
    tw = d.get("outcomes", {}).get("tripwires", {})
    for k in list(tw):
        if k not in ("TW-FLOOR_fired", "TW-ALIVE_fired", "note"):
            tw.pop(k)
    return d


def iter_jsonl(path):
    if not os.path.exists(path) and os.path.exists(path + ".gz"):
        path = path + ".gz"
    op = gzip.open if path.endswith(".gz") else open
    with op(path, "rt") as fh:
        for line in fh:
            if line.strip():
                yield json.loads(line)


def m_of(r):
    meth = str(r.get("method", ""))
    return int(meth[4:]) if meth.startswith("ic_m") else r.get("m")


def canonical_rows(run):
    """The canonical row file the M-6 view points at: merged/ where it exists, else the root."""
    d = os.path.join(RUNS, P + run)
    if os.path.isdir(os.path.join(d, "merged")):
        d = os.path.join(d, "merged")
    return list(iter_jsonl(os.path.join(d, "rows.jsonl.gz")))


def build_index(rows):
    idx = {}
    for r in rows:
        if r.get("panel") in ("main", "j0") and r.get("arm"):
            idx[(r.get("panel"), m_of(r), r["bits"], r["curve"], r["arm"], r.get("mode"))] = r
    return idx


def usable(r):
    return r is not None and r.get("status") == "completed_valid" and r.get("harvest") is not None


def censored(r):
    a = r["harvest"]["SS"].get("at_A_fix")
    return a is None or bool(a.get("censored"))


def count(r, cname, kind="pairs_nonformal", ss_block="at_A_fix"):
    h = r["harvest"]
    if cname == "SS":
        return h["SS"][ss_block][kind]
    return h[cname]["at_stop"][kind]


def kappa_stats(nA, nR, sd_rule="frozen"):
    """A1 as frozen: C_A, C_R = mean of three random sums, V = max(sum_j s_j^2, C_R),
    SD_null = sqrt(4V/3), z = (C_A - C_R)/SD_null, resolved iff C_R >= 10."""
    C_A = float(sum(nA))
    C_R = sum(sum(v) for v in nR) / 3.0
    s2 = sum(statistics.variance(v) for v in nR) if nR else 0.0
    V = max(s2, C_R)
    SD = math.sqrt(V * 4 / 3)
    kappa = C_A / C_R if C_R > 0 else None
    z = (C_A - C_R) / SD if SD > 0 else None
    return {"C_A": C_A, "C_R": C_R, "sum_s2": s2, "V": V, "SD_null": SD, "kappa": kappa,
            "z": z, "resolved": C_R >= 10}


def kappa_cell(idx, m, bits, cname, A, curves, kind="pairs_nonformal", drop_rule="frozen",
               ss_block="at_A_fix"):
    """Reimplementation of the frozen A1 cell (own code).  drop_rule:
    frozen      -- a curve with any of A, R(A) censored/failed/invalid dropped for all four;
    no_drop     -- only failed/invalid/missing drop (censoring ignored);
    affected    -- censoring drops only the censored arm's count (curve kept with 2 randoms
                   when a random is censored; dropped when A is censored)."""
    rands = RANDOMS[A]
    kept = []
    dropped = []
    for j in curves:
        rs = [idx.get(("main", m, bits, j, arm, "census")) for arm in (A,) + tuple(rands)]
        sizes = [r.get("fb_size") if r else None for r in rs]
        if sizes[0] is not None and any(s is not None for s in sizes[1:]):
            sR = next(s for s in sizes[1:] if s is not None)
            if sizes[0] != sR:
                dropped.append((j, "unmatched_size"))
                continue
        if not all(usable(r) for r in rs):
            dropped.append((j, "status"))
            continue
        cens = [censored(r) for r in rs]
        if drop_rule == "frozen" and any(cens):
            dropped.append((j, "censored"))
            continue
        if drop_rule == "affected" and cens[0]:
            dropped.append((j, "censored_A"))
            continue
        kept.append((j, rs, cens))
    nA, nR = [], []
    for j, rs, cens in kept:
        nA.append(count(rs[0], cname, kind, ss_block))
        rv = [count(r, cname, kind, ss_block) for r, c in zip(rs[1:], cens[1:])
              if not (drop_rule == "affected" and c)]
        nR.append(rv)
    return nA, nR, [j for j, _, _ in kept], dropped


def kappa_stats_var(nA, nR):
    """Variant of kappa_stats that accepts 2 or 3 randoms per curve (drop_rule affected):
    C_R = sum_j mean_r n_{r,j}; Var(C_A - C_R) = sum_j V_j (1 + 1/k_j)."""
    C_A = float(sum(nA))
    C_R = sum(sum(v) / len(v) for v in nR)
    s2 = sum(statistics.variance(v) for v in nR if len(v) >= 2)
    var_terms = sum((statistics.variance(v) if len(v) >= 2 else 0.0) * (1 + 1 / len(v)) for v in nR)
    pois_terms = sum((sum(v) / len(v)) * (1 + 1 / len(v)) for v in nR)
    varD = max(var_terms, pois_terms)
    SD = math.sqrt(varD) if varD > 0 else 0.0
    return {"C_A": C_A, "C_R": C_R, "kappa": C_A / C_R if C_R > 0 else None,
            "z": (C_A - C_R) / SD if SD > 0 else None, "resolved": C_R >= 10, "sum_s2": s2}


def dump(name, obj):
    path = os.path.join(OUT, name)
    with open(path, "w") as fh:
        json.dump(obj, fh, indent=1, sort_keys=True, default=str)
    return path

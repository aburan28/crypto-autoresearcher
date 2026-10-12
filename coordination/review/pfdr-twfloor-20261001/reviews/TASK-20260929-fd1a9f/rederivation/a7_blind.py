"""Blind re-derivation of A7 (joint F2, Q1-Q4) for TASK-20260929-fd1a9f.

Implements rederivation/conventions.yaml (sha256 8fb4c00f...) from the frozen
text and the row fields ONLY. Imports nothing from crypto_autoresearcher;
stats.py is loaded by file path for Q4 (it imports only math, random,
collections). Reads only the permitted pre-seal inputs (canonical rows,
attempt rows, retained harvest rows). Writes to rederivation/out/.

usage: python3 a7_blind.py <outdir>
"""
from __future__ import annotations

import collections
import glob
import gzip
import hashlib
import importlib.util
import json
import math
import os
import random
import sys

WT = "/tmp/claude-0/-home-user/015c3767-cc03-52db-9b0c-bd2aa6c26537/scratchpad/wt-twfloor-66d6eab71"
RUNS = WT + "/experiments/EXP-PFDR-1b78f7/runs"
M3, M4, M5 = RUNS + "/RUN-PFDR-1b78f7-census-m3", RUNS + "/RUN-PFDR-1b78f7-census-m4", RUNS + "/RUN-PFDR-1b78f7-census-m5"
J0, SR = RUNS + "/RUN-PFDR-1b78f7-j0", RUNS + "/RUN-PFDR-1b78f7-stage-r"

CANONICAL = {  # tag -> (path, panel default, set)
    "R10": (M3 + "/rows.jsonl.gz", "S15"),
    "R11": (M4 + "/merged/rows.jsonl.gz", "S15"),
    "R12": (M5 + "/rows.jsonl.gz", "S15"),
    "R14": (J0 + "/rows.jsonl.gz", "S15"),
    "R16": (SR + "/rows.jsonl.gz", "S16"),
}
# M-2 resume set of R11 (asserted against the attempt-1 rows below)
R11_RESUME = {(b, c) for b in (12, 14, 16, 18, 20, 22) for c in range(5)} | {(24, 1), (24, 3), (24, 4)}

STRUCT = {"subgroup", "dickson", "small_x"}


def arm_class(arm: str) -> str:
    if arm == "known_log":
        return "known_log"
    if arm == "j0_coset":
        return "j0_coset"
    if arm.startswith("j0_random"):
        return "j0_random"
    if arm in STRUCT:
        return "structured"
    if arm.startswith("random_"):
        return "random"
    raise ValueError(arm)


def key_of(r: dict) -> tuple:
    return (r["panel"], int(r["bits"]), int(r["curve"]), int(r["method"][4:]), r["arm"], r["mode"])


def read_rows(path):
    with gzip.open(path, "rt") as f:
        return [json.loads(l) for l in f]


def solver_rows(rows):
    return [r for r in rows if str(r.get("method", "")).startswith("ic_m")]


# ----------------------------------------------------------------------------
# exact threshold decisions (CV-9)
def below(S: int, r: int, N: int, num: int, den: int, c: int) -> bool:
    """ratio < num/den with ratio = S / ((1/c) * sqrt(r N)) for c in {1, 2}."""
    if c == 2:
        return 4 * S * S * den * den < num * num * r * N
    return S * S * den * den < num * num * r * N


def ratio(S: int, r: int, N: int, c: int) -> float:
    rn = r * N
    return S / (0.5 * math.sqrt(rn)) if c == 2 else S / math.sqrt(rn)


# ----------------------------------------------------------------------------
# r_distinct from retained harvest rows (ALT-distinct)
def norm_raw(coeffs, kcoef, rhs, N):
    ent = []
    for i, c in sorted((int(i), int(c)) for i, c in coeffs):
        v = c % N
        if v:
            ent.append((i, v))
    kv, rv = int(kcoef) % N, int(rhs) % N
    first = ent[0][1] if ent else (kv if kv else rv)
    if first == 0:
        return None
    inv = pow(first, -1, N)
    return (tuple((i, v * inv % N) for i, v in ent), kv * inv % N, rv * inv % N)


class InstAcc:
    __slots__ = ("key", "n", "tt", "tb", "ss", "bad")

    def __init__(self, key):
        self.key = key
        self.n = collections.Counter()
        self.tt = []
        self.tb = []
        self.ss = []  # (attempt, raw, formal_flag, coeffs, kcoef, rhs)
        self.bad = []


def stream_harvest(path, panel, want, done_keys, src_tag, out_counts, on_complete):
    """Stream one harvest-rows file; on-mode instances in `want` are accumulated
    one at a time (they must be contiguous) and handed to on_complete(key, src, acc)
    as soon as the next instance starts, so only one instance is held in memory."""
    cur = None

    def flush(acc):
        if acc is None:
            return
        if acc.key in done_keys:
            raise RuntimeError(f"instance {acc.key} reappears in {path}")
        done_keys.add(acc.key)
        on_complete(acc.key, src_tag, acc)

    with gzip.open(path, "rt") as f:
        for line in f:
            if '"mode": "on"' not in line:
                if '"mode": "census"' in line:
                    out_counts["census_lines"] += 1
                    continue
                d = json.loads(line)
                if d.get("mode") != "on":
                    out_counts["other_lines"] += 1
                    continue
            d = json.loads(line)
            if d["mode"] != "on":
                out_counts["census_lines_after_parse"] += 1
                continue
            out_counts["on_lines"] += 1
            k = (panel, int(d["bits"]), int(d["curve"]), int(d["m"]), d["arm"], "on")
            if k not in want:
                out_counts["on_lines_not_wanted"] += 1
                continue
            if cur is None or cur.key != k:
                flush(cur)
                if k in done_keys:
                    raise RuntimeError(f"instance {k} not contiguous in {path}")
                cur = InstAcc(k)
            cls = d["class"]
            cur.n[cls] += 1
            if not d.get("cert_ok", False):
                cur.bad.append(("cert_ok_false", cls))
            N = want[k]
            raw = norm_raw(d["coeffs"], d["kcoef"], d["rhs"], N)
            keep = d["coeffs"] if d["arm"] == "known_log" else None
            rec = (int(d["attempt"]), raw, bool(d["formal"]), keep, int(d["kcoef"]), int(d["rhs"]))
            if cls == "TT":
                cur.tt.append(rec)
            elif cls == "TB":
                cur.tb.append(rec)
            elif cls == "SS":
                cur.ss.append(rec)
            else:
                cur.bad.append(("unknown_class", cls))
        flush(cur)
    print(f"[a7] streamed {src_tag} {os.path.basename(os.path.dirname(path))}/{os.path.basename(path)} "
          f"on_lines={out_counts['on_lines']}", file=sys.stderr, flush=True)


def k_rule(bits, c, N):
    return random.Random(f"target|{bits}|{c}|0").randrange(1, N)


def finalize_distinct(inst, acc):
    """Return dict with r_distinct_raw / formal counts and checks for one on instance."""
    h = inst["harvest"]
    fed = h["on"]["rows_fed"]
    N = int(inst["N"])
    out = {"checks": {}, "blocked": [], "notes": []}
    nTT, nTB, nSS = len(acc.tt), len(acc.tb), len(acc.ss)
    em = {c: h[c]["at_stop"]["rows_emitted"] for c in ("TT", "TB", "SS")}
    out["retained"] = {"TT": nTT, "TB": nTB, "SS": nSS}
    out["fed"] = dict(fed)
    out["emitted"] = em
    # retention / blocking
    for c, n in (("TT", nTT), ("TB", nTB), ("SS", nSS)):
        if n < fed[c]:
            out["blocked"].append(f"{c}: retained {n} < fed {fed[c]}")
        full = inst["bits"] <= 24 or h[c].get("census_saturated_at_row") is None
        if full and n != em[c]:
            out["checks"][f"{c}_retained_eq_emitted"] = False
            out["blocked"].append(f"{c}: retained {n} != emitted {em[c]} where full retention applies")
        elif full:
            out["checks"][f"{c}_retained_eq_emitted"] = True
    out["checks"]["TT_fed_eq_emitted"] = fed["TT"] == em["TT"]
    out["checks"]["TB_fed_eq_emitted"] = fed["TB"] == em["TB"]
    atts = [a for a, *_ in acc.ss]
    out["checks"]["SS_attempts_nondecreasing"] = all(atts[i] <= atts[i + 1] for i in range(len(atts) - 1))
    if acc.ss:
        last = max(atts)
        unfed = acc.ss[fed["SS"]:]
        out["checks"]["SS_unfed_all_in_last_attempt"] = all(a == last for a, *_ in unfed)
    else:
        out["checks"]["SS_unfed_all_in_last_attempt"] = True
    if not out["checks"]["SS_attempts_nondecreasing"]:
        out["blocked"].append("SS attempts not non-decreasing in file order")
    if not out["checks"]["SS_unfed_all_in_last_attempt"]:
        out["blocked"].append("unfed SS rows outside the last SS attempt")
    if acc.bad:
        out["notes"].append(f"bad: {acc.bad[:5]}")
    fed_rows = acc.tt + acc.tb + acc.ss[: fed["SS"]]
    # raw
    raw = {r[1] for r in fed_rows if r[1] is not None}
    out["zero_rows_raw"] = sum(1 for r in fed_rows if r[1] is None)
    out["distinct_raw_harvested"] = len(raw)
    # formal
    arm = inst["arm"]
    if arm == "known_log":
        # index check on TT/TB rows (formal, must reduce to 0) with 0-based i -> log i+1
        ok0 = ok1 = True
        for a, rw, fl, coeffs, kc, rh in acc.tt + acc.tb:
            s0 = sum(int(c) * (int(i) + 1) for i, c in coeffs) % N
            s1 = sum(int(c) * int(i) for i, c in coeffs) % N
            if (s0 - rh) % N != 0 or kc % N != 0:
                ok0 = False
            if (s1 - rh) % N != 0 or kc % N != 0:
                ok1 = False
        out["checks"]["known_log_index0_log_i_plus_1"] = ok0
        out["checks"]["known_log_index_log_i"] = ok1
        if not ok0:
            out["blocked_formal"] = "known_log index convention check failed"
            out["distinct_formal_harvested"] = None
        else:
            kr = k_rule(inst["bits"], inst["curve"], N)
            vals = set()
            nzero = 0
            kmis = 0
            for a, rw, fl, coeffs, kc, rh in fed_rows:
                s = sum(int(c) * (int(i) + 1) for i, c in coeffs) % N
                kcn = kc % N
                rest = (rh - s) % N
                if kcn == 0:
                    if rest != 0:
                        out["notes"].append("known_log row with kcoef 0 and nonzero residual")
                    nzero += 1
                    continue
                v = rest * pow(kcn, -1, N) % N
                if v != kr:
                    kmis += 1
                vals.add(("k", v))
            out["distinct_formal_harvested"] = len(vals)
            out["formal_zero_rows"] = nzero
            out["known_log_k_values"] = sorted(v for _, v in vals)[:5]
            out["known_log_k_rule"] = kr
            out["known_log_rows_k_mismatch"] = kmis
    elif inst["panel"] == "j0":
        nf = {r[1] for r in fed_rows if (not r[2]) and r[1] is not None}
        out["distinct_formal_harvested"] = len(nf)
        out["formal_flag_rows_dropped"] = sum(1 for r in fed_rows if r[2])
    else:
        nform = sum(1 for r in fed_rows if r[2])
        out["formal_flag_rows_on_generic_arm"] = nform
        out["distinct_formal_harvested"] = len(raw)
    return out


# ----------------------------------------------------------------------------
def build_instances(rows_by_tag):
    inst = {}
    for tag, rows in rows_by_tag.items():
        st = CANONICAL[tag][1]
        for r in solver_rows(rows):
            k = key_of(r)
            if k in inst:
                raise RuntimeError(f"duplicate key {k}")
            r = dict(r)
            r["_tag"], r["_set"] = tag, st
            inst[k] = r
    return inst


def exclusions(inst):
    """CV-2 unmatched_size (primary and CV-2b) and status exclusions."""
    jobs = collections.defaultdict(dict)
    for k, r in inst.items():
        jobs[(r["_set"],) + k[:4]][(k[4], k[5])] = r
    um, um_b = set(), set()
    for jk, d in jobs.items():
        if jk[1] != "main":
            continue
        ssub = {r["fb_size"] for (a, _), r in d.items() if a.startswith("random_sub")}
        sdick = {r["fb_size"] for (a, _), r in d.items() if a.startswith("random_dick")}
        for (a, md), r in d.items():
            ref = ssub if a in ("subgroup", "small_x") else sdick if a == "dickson" else None
            if ref is None:
                continue
            if len(ref) != 1:
                raise RuntimeError(f"random sizes disagree in {jk}: {ref}")
            if r["fb_size"] not in ref:
                k = (jk[1], jk[2], jk[3], jk[4], a, md)
                um.add(k)
                um_b.add(k)
                for (a2, md2) in d:
                    if (a in ("subgroup", "small_x") and a2.startswith("random_sub")) or (a == "dickson" and a2.startswith("random_dick")):
                        um_b.add((jk[1], jk[2], jk[3], jk[4], a2, md2))
    status_ex = {k for k, r in inst.items() if r.get("status") != "completed_valid"}
    return um, um_b, status_ex


def r_values(k, r, inst):
    mode = k[5]
    rel = int(r["relations"])
    rank = int(r["rank"])
    h = r["harvest"]
    out = {"relations": rel, "rank": rank}
    if mode == "on":
        fed = h["on"]["rows_fed"]
        inc = h["on"]["solver_rank_increments"]
        out["rows_fed"] = dict(fed)
        out["rank_incr_sum"] = inc["decomp"] + inc["TT"] + inc["TB"] + inc["SS"]
        out["r_frozen"] = rel + fed["TT"] + fed["TB"] + fed["SS"]
        out["r_rank"] = out["rank_incr_sum"]
        out["rank_agrees"] = out["rank_incr_sum"] == rank
        out["k_determined_by"] = h["on"].get("k_determined_by")
    else:
        out["r_frozen"] = rel
        out["r_rank"] = rank
        out["rank_agrees"] = True
    out["r_rank1"] = out["r_rank"] + 1
    out["r_rel"] = rel
    twin = inst.get(k[:5] + ("census",))
    out["r_census"] = int(twin["relations"]) if twin is not None else None
    out["terminated_by"] = h.get("terminated_by")
    return out


CONVS = ["frozen", "rank", "rank1", "rel", "distinct_raw", "distinct_formal", "census"]


def evaluate(inst, distinct, excl_primary):
    """Per-instance table: every convention in the declared grid."""
    table = {}
    for k, r in inst.items():
        rv = r_values(k, r, inst)
        S = int(r["s3_solves"])
        Ss = int(r["search_s3"])
        if Ss != S - int(r["table_s3_solves"]):
            raise RuntimeError(f"search_s3 identity fails at {k}")
        N = int(r["N"])
        d = distinct.get(k)
        rd_raw = rd_formal = None
        rd_status = "census_mode" if k[5] == "census" else None
        if k[5] == "census":
            rd_raw = rd_formal = rv["relations"]
        elif d is None:
            hh = r["harvest"]
            nfed = sum(hh["on"]["rows_fed"].values())
            nem = sum(hh[c]["at_stop"]["rows_emitted"] for c in ("TT", "TB", "SS"))
            if nfed == 0 and nem == 0:
                rd_status = "ok_no_harvested_rows"
                rd_raw = rd_formal = rv["relations"]
            else:
                rd_status = "blocked: no retained rows found (fed %d, emitted %d)" % (nfed, nem)
        elif d["blocked"]:
            rd_status = "blocked: " + "; ".join(d["blocked"])
        else:
            rd_status = "ok"
            rd_raw = rv["relations"] + d["distinct_raw_harvested"]
            if d.get("distinct_formal_harvested") is not None:
                rd_formal = rv["relations"] + d["distinct_formal_harvested"]
        rmap = {"frozen": rv["r_frozen"], "rank": rv["r_rank"], "rank1": rv["r_rank1"], "rel": rv["r_rel"],
                "distinct_raw": rd_raw, "distinct_formal": rd_formal, "census": rv["r_census"]}
        rec = {"key": list(k), "set": r["_set"], "run": r["_tag"], "arm_class": arm_class(k[4]),
               "N": N, "S3": S, "S_search": Ss, "fb_size": r["fb_size"], "log2N": r["log2N"],
               "status": r.get("status"), "excluded": k in excl_primary, **rv,
               "r_distinct_raw": rd_raw, "r_distinct_formal": rd_formal, "r_distinct_status": rd_status,
               "eval": {}}
        for conv in CONVS:
            rr = rmap[conv]
            for sname, Sv in (("S3", S), ("Ssearch", Ss)):
                for c in (2, 1):
                    tag = f"{conv}|{sname}|c{c}"
                    if k in excl_primary:
                        rec["eval"][tag] = {"state": "excluded"}
                    elif rr is None:
                        rec["eval"][tag] = {"state": "not_evaluable_r_unavailable"}
                    elif rr == 0:
                        rec["eval"][tag] = {"state": "not_evaluable_r_zero"}
                    else:
                        rec["eval"][tag] = {"state": "ok", "ratio": ratio(Sv, rr, N, c),
                                            "lt09": below(Sv, rr, N, 9, 10, c),
                                            "lt10": below(Sv, rr, N, 1, 1, c)}
        table[k] = rec
    return table


def firing_set(table, tag, which="lt09", sets=("S15",)):
    return sorted(tuple(rec["key"]) for rec in table.values()
                  if rec["set"] in sets and rec["eval"][tag]["state"] == "ok" and rec["eval"][tag][which])


def counts_by_group(table, tag):
    g = collections.defaultdict(lambda: collections.Counter())
    for rec in table.values():
        k = rec["key"]
        grp = f"{rec['set']}|{k[0]}|m{k[3]}|{k[5]}|{rec['arm_class']}"
        e = rec["eval"][tag]
        g[grp]["instances"] += 1
        g[grp][e["state"]] += 1
        if e["state"] == "ok":
            g[grp]["fire_lt09"] += int(e["lt09"])
            g[grp]["tail_lt10"] += int(e["lt10"])
    return {k: dict(v) for k, v in sorted(g.items())}


def load_stats():
    p = WT + "/src/crypto_autoresearcher/index_calculus/stats.py"
    spec = importlib.util.spec_from_file_location("ic_stats_frozen_by_path", p)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod, hashlib.sha256(open(p, "rb").read()).hexdigest()


def q4(table, stats):
    out = {}
    for arm in ("small_x", "subgroup", "dickson", "random_sub_r0", "random_sub_r1", "random_sub_r2",
                "random_dick_r0", "random_dick_r1", "random_dick_r2"):
        rows = []
        for rec in table.values():
            k = rec["key"]
            if rec["set"] == "S15" and k[0] == "main" and k[3] == 4 and k[4] == arm and k[5] == "on" and not rec["excluded"]:
                N = rec["N"]
                rows.append({"bits": k[1], "log2N": rec["log2N"], "s3": rec["S3"],
                             "floor_frozen": 0.5 * math.sqrt(rec["r_frozen"] * N),
                             "floor_rank": 0.5 * math.sqrt(rec["r_rank"] * N) if rec["r_rank"] > 0 else None,
                             "floor_rank1": 0.5 * math.sqrt(rec["r_rank1"] * N),
                             "model_sqrt_FN": math.sqrt(rec["fb_size"] * N),
                             "beta": math.log(rec["fb_size"]) / math.log(N)})
        res = {"n": len(rows)}
        for ck in ("s3", "floor_frozen", "floor_rank", "floor_rank1", "model_sqrt_FN"):
            fr = stats.fit_exponent([r for r in rows if r[ck]], ck)
            res[f"fit_{ck}"] = fr
        per_rung = collections.defaultdict(list)
        for r in rows:
            per_rung[r["bits"]].append((1 + r["beta"]) / 2)
        res["model_(1+beta)/2_per_rung"] = {b: sum(v) / len(v) for b, v in sorted(per_rung.items())}
        allv = [x for b, v in per_rung.items() for x in v]
        hi = [x for b, v in per_rung.items() if b >= 20 for x in v]
        res["model_(1+beta)/2_mean_12_32"] = sum(allv) / len(allv) if allv else None
        res["model_(1+beta)/2_mean_20_32"] = sum(hi) / len(hi) if hi else None
        res["asymptotic_(m+1)/(2m)"] = 0.625
        out[arm] = res
    return out


def attempt_rows():
    """MC-3 (ii): canonical rows rebuilt from the attempt files by M-5's rule."""
    rows = {}
    notes = collections.Counter()
    # R10: single invocation, root is attempt 1 and canonical
    # R11 attempt 1 (root) for keys outside the resume set; attempt 2 jobs for the resume set
    a1 = read_rows(M4 + "/rows.jsonl.gz")
    for r in a1:
        m = int(r["method"][4:]) if r.get("method") else int(r["m"])
        k = (r["panel"], int(r["bits"]), int(r["curve"]), m, r["arm"], r["mode"])
        crash = str(r.get("status_reason") or "").startswith("job crashed:")
        inres = (k[1], k[2]) in R11_RESUME
        notes["R11_attempt1_rows"] += 1
        notes["R11_attempt1_crash_rows"] += int(crash)
        if inres != crash:
            notes["R11_resume_set_disagreement"] += 1
        if k[4] == "known_log":
            notes["R11_noncell_known_log_rows"] += 1
            continue
        if not inres:
            if not str(r.get("method", "")).startswith("ic_m"):
                notes["R11_attempt1_nonsolver_row_outside_resume_set"] += 1
                continue
            rows[("R11",) + k] = r
    for p in sorted(glob.glob(M4 + "/attempt-2/jobs/*/rows.jsonl.gz")):
        for r in solver_rows(read_rows(p)):
            k = key_of(r)
            if (k[1], k[2]) not in R11_RESUME:
                notes["R11_attempt2_row_outside_resume_set"] += 1
            if ("R11",) + k in rows:
                notes["R11_duplicate"] += 1
            rows[("R11",) + k] = r
    for tag, base in (("R12", M5), ("R14", J0), ("R16", SR)):
        for p in sorted(glob.glob(base + "/attempt-1/jobs/*/rows.jsonl.gz")):
            for r in solver_rows(read_rows(p)):
                k = key_of(r)
                if (tag,) + k in rows:
                    notes[f"{tag}_duplicate"] += 1
                rows[(tag,) + k] = r
    return rows, dict(notes)


def strip_timing(x):
    if isinstance(x, dict):
        return {k: strip_timing(v) for k, v in x.items()
                if not (k == "seconds" or k.endswith("_seconds") or k in ("worker_maxrss_bytes", "ru_maxrss_bytes"))}
    if isinstance(x, list):
        return [strip_timing(v) for v in x]
    return x


def main():
    outdir = sys.argv[1]
    os.makedirs(outdir, exist_ok=True)
    rows_by_tag = {tag: read_rows(p) for tag, (p, _) in CANONICAL.items()}
    inst = build_instances(rows_by_tag)
    um, um_b, status_ex = exclusions(inst)
    excl_primary = um | status_ex

    # ---- r_distinct: stream retained harvest rows (on mode only)
    want = {k: int(r["N"]) for k, r in inst.items() if k[5] == "on"}
    accs = {}
    hcount = collections.Counter()
    sources = []
    # R10
    sources.append(("R10", M3 + "/harvest-rows.jsonl.gz", "main"))
    # R11 attempt-1 root and attempt-2 jobs
    sources.append(("R11a1", M4 + "/harvest-rows.jsonl.gz", "main"))
    sources += [("R11a2", p, "main") for p in sorted(glob.glob(M4 + "/attempt-2/jobs/*/harvest-rows.jsonl.gz"))]
    sources += [("R12", p, "main") for p in sorted(glob.glob(M5 + "/attempt-1/jobs/*/harvest-rows.jsonl.gz"))]
    sources += [("R14", p, "j0") for p in sorted(glob.glob(J0 + "/attempt-1/jobs/*/harvest-rows.jsonl.gz"))]
    sources += [("R16", p, "main") for p in sorted(glob.glob(SR + "/attempt-1/jobs/*/harvest-rows.jsonl.gz"))]
    # R16 keys share the main-panel key space with curves 5..9; keep them apart by set
    want15 = {k: v for k, v in want.items() if inst[k]["_set"] == "S15"}
    want16 = {k: v for k, v in want.items() if inst[k]["_set"] == "S16"}
    distinct, dinfo, srcmap = {}, {}, {}

    def on_complete(k, src, acc):
        res = finalize_distinct(inst[k], acc)
        res["source"] = src
        distinct[k] = res
        srcmap[k] = src
        dinfo["|".join(map(str, k))] = res

    done15, done16 = set(), set()
    for tag, p, panel in sources:
        if tag == "R16":
            stream_harvest(p, panel, want16, done16, tag, hcount, on_complete)
        else:
            stream_harvest(p, panel, want15, done15, tag, hcount, on_complete)
    # canonical source attempt for R11 keys (M-5 (1), (8))
    src_problems = []
    for k, src in srcmap.items():
        if inst[k]["_tag"] == "R11":
            expect = "R11a2" if (k[1], k[2]) in R11_RESUME else "R11a1"
            if src != expect:
                src_problems.append([list(k), src, expect])
    missing_on = sorted(set(want) - set(distinct))

    table = evaluate(inst, distinct, excl_primary)

    # ---- outputs
    with open(os.path.join(outdir, "instances.jsonl"), "w") as f:
        for k in sorted(table):
            f.write(json.dumps(table[k], sort_keys=True) + "\n")
    tags = [f"{c}|{s}|c{cc}" for c in CONVS for s in ("S3", "Ssearch") for cc in (2, 1)]
    named = {"frozen": "frozen|S3|c2", "r_rank": "rank|S3|c2", "r_rank1": "rank1|S3|c2", "r_rel": "rel|S3|c2",
             "r_distinct_raw": "distinct_raw|S3|c2", "r_distinct_formal": "distinct_formal|S3|c2",
             "r_census": "census|S3|c2", "S_search": "frozen|Ssearch|c2", "c1": "frozen|S3|c1"}
    tables = {"named": {}, "grid": {}}
    for name, tag in named.items():
        tables["named"][name] = {"tag": tag, "by_group": counts_by_group(table, tag),
                                 "fire_S15": [list(x) for x in firing_set(table, tag, "lt09", ("S15",))],
                                 "fire_S16": [list(x) for x in firing_set(table, tag, "lt09", ("S16",))],
                                 "tail_S15": [list(x) for x in firing_set(table, tag, "lt10", ("S15",))],
                                 "tail_S16": [list(x) for x in firing_set(table, tag, "lt10", ("S16",))]}
    for tag in tags:
        g = counts_by_group(table, tag)
        tables["grid"][tag] = {grp: {"fire": v.get("fire_lt09", 0), "tail": v.get("tail_lt10", 0), "ok": v.get("ok", 0),
                                     "n": v["instances"]} for grp, v in g.items()}
    json.dump(tables, open(os.path.join(outdir, "tables.json"), "w"), indent=1, sort_keys=True)

    # alternatives on exclusions/caps (CV-2b, CV-3b)
    fz = "frozen|S3|c2"
    base15 = set(firing_set(table, fz, "lt09", ("S15",)))
    cv2b = sorted(k for k in base15 if k in um_b)
    capped = sorted(tuple(r["key"]) for r in table.values() if r["terminated_by"] != "k_found")
    cv3b = sorted(k for k in base15 if k in set(capped))
    deltas = {"CV-2b_removed_from_firing_set": [list(x) for x in cv2b],
              "CV-2b_extra_excluded_keys": [list(x) for x in sorted(um_b - um)],
              "CV-3b_removed_from_firing_set": [list(x) for x in cv3b],
              "capped_instances": [list(x) for x in capped],
              "unmatched_size_primary": [list(x) for x in sorted(um)],
              "status_excluded": [list(x) for x in sorted(status_ex)]}

    # ---- MC-3 (i) order invariance
    mc3 = {"order": {}, "attempt_files": {}}
    flat = [(tag, r) for tag, rows in rows_by_tag.items() for r in rows]
    ref = {t: (firing_set(table, t, "lt09", ("S15", "S16")), firing_set(table, t, "lt10", ("S15", "S16"))) for t in tags}
    for label, order in [("reversed", list(reversed(flat)))] + [
            (f"shuffle_{s}", (lambda L, s: (random.Random(s).shuffle(L), L)[1])(list(flat), s)) for s in range(1, 6)]:
        rb = collections.defaultdict(list)
        for tag, r in order:
            rb[tag].append(r)
        inst2 = build_instances(rb)
        t2 = evaluate(inst2, distinct, excl_primary)
        same = all((firing_set(t2, t, "lt09", ("S15", "S16")), firing_set(t2, t, "lt10", ("S15", "S16"))) == ref[t] for t in tags)
        mc3["order"][label] = same
    # ---- MC-3 (ii) attempt files
    arows, anotes = attempt_rows()
    mc3["attempt_files"]["notes"] = anotes
    canon_keys = {(r["_tag"],) + k for k, r in inst.items() if r["_tag"] in ("R11", "R12", "R14", "R16")}
    akeys = set(arows)
    mc3["attempt_files"]["keys_missing_in_attempts"] = [list(x) for x in sorted(canon_keys - akeys)]
    mc3["attempt_files"]["keys_extra_in_attempts"] = [list(x) for x in sorted(akeys - canon_keys)]
    ndiff, diffs = 0, []
    for kk in sorted(canon_keys & akeys):
        a = strip_timing(arows[kk])
        c = strip_timing({x: y for x, y in inst[kk[1:]].items() if not x.startswith("_")})
        if a != c:
            ndiff += 1
            if len(diffs) < 10:
                diffs.append([list(kk), sorted(set(a) ^ set(c)) or [x for x in a if a[x] != c.get(x)]])
    mc3["attempt_files"]["rows_compared"] = len(canon_keys & akeys)
    mc3["attempt_files"]["rows_differing_outside_timing"] = ndiff
    mc3["attempt_files"]["examples"] = diffs
    # rebuild instance table from attempt rows (+ R10 canonical) and compare firing sets
    rb = collections.defaultdict(list)
    rb["R10"] = rows_by_tag["R10"]
    for (tag, *k), r in arows.items():
        rb[tag].append(r)
    inst3 = build_instances(rb)
    t3 = evaluate(inst3, distinct, excl_primary)
    mc3["attempt_files"]["firing_sets_equal_all_conventions"] = all(
        (firing_set(t3, t, "lt09", ("S15", "S16")), firing_set(t3, t, "lt10", ("S15", "S16"))) == ref[t] for t in tags)
    vals_equal = all(k in t3 and table[k]["eval"] == t3[k]["eval"] for k in table)
    mc3["attempt_files"]["per_instance_values_equal"] = vals_equal

    stats, stats_sha = load_stats()
    q = q4(table, stats)

    meta = {"harvest_stream_counts": dict(hcount), "R11_source_attempt_problems": src_problems,
            "on_instances_without_retained_rows": [list(x) for x in missing_on],
            "distinct_instances": len(distinct), "on_instances": len(want),
            "stats_py_sha256": stats_sha, "deltas": deltas, "mc3": mc3, "q4": q}
    json.dump(meta, open(os.path.join(outdir, "meta.json"), "w"), indent=1, sort_keys=True, default=str)
    json.dump(dinfo, open(os.path.join(outdir, "distinct-detail.json"), "w"), indent=0, sort_keys=True, default=str)
    print("done", len(table), "instances;", len(distinct), "on instances with retained rows")


if __name__ == "__main__":
    main()

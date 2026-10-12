#!/usr/bin/env python3
"""TASK-20261009-a92ff3 (J-BLIND) -- own CC-1..CC-3 / CC-7 / CC-8 / CC-10 reader.

Written from the clause texts of EXP-PFDR-011cd0 CC-1..CC-10 and EXP-PFDR-0b3699
analysis.statistic only, under readings.yaml (R-1..R-7). Imports no
crypto_autoresearcher module and nothing under experiments/. Deterministic, no
randomness.

Inputs (read-only): design.json (pre-data), per-job rows.jsonl.gz and
harvest-rows.jsonl.gz of RUN-PFDR-0b3699-table/attempt-1/jobs/*, and the run-root
rows.jsonl.gz (cross-check only).

Outputs: <out>/counts.json (summary) and <out>/percurve.json.gz (per-curve counts
of small_x, small_x_offset, r0, r1, r2 with admission flags and mu_model).
"""
from __future__ import annotations

import gzip
import hashlib
import json
import math
import os
import sys
from collections import Counter, defaultdict
from fractions import Fraction

REPO = "/home/user/crypto-autoresearcher"
EXP = os.path.join(REPO, "experiments/EXP-PFDR-0b3699")
DESIGN = os.path.join(EXP, "runs/RUN-PFDR-0b3699-p0-design/design.json")
TABLE = os.path.join(EXP, "runs/RUN-PFDR-0b3699-table")
JOBS = os.path.join(TABLE, "attempt-1/jobs")
ROOT_ROWS = os.path.join(TABLE, "rows.jsonl.gz")

A, M = "small_x", "small_x_offset"
RANDOMS = ("random_sub_r0", "random_sub_r1", "random_sub_r2")
SCORED = (A, M) + RANDOMS
ALL_ARMS = ("subgroup", "small_x", "random_sub_r0", "random_sub_r1", "random_sub_r2",
            "known_null_sub", "planted_sub", "small_x_offset")


def sha256(path: str) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def m4_table(r: dict) -> bool:
    """Census rows carry method ic_m<m> (no m key); harvest rows carry m."""
    m_ok = (r.get("m") == 4) if "m" in r else (r.get("method") == "ic_m4")
    return m_ok and r.get("mode") == "table"


def monic(vec: dict, kc: int, rh: int, N: int):
    """CC-1: reduce mod N; zero -> None; else multiply by the inverse of the first
    nonzero coordinate (base indices ascending, then kcoef, then rhs)."""
    red = {i: v % N for i, v in vec.items() if v % N}
    kc %= N
    rh %= N
    if red:
        lead = red[min(red)]
    elif kc:
        lead = kc
    elif rh:
        lead = rh
    else:
        return None
    inv = pow(lead, -1, N)
    return (tuple(sorted((i, v * inv % N) for i, v in red.items())), kc * inv % N, rh * inv % N)


def recount(groups: dict, N: int):
    """groups: first-element key -> list of star rows (dict, kc, rh) in file order.
    Returns (distinct, pairs, zero_pairs, multiplicity Counter, R_star)."""
    rels = Counter()
    pairs = zero = 0
    star = set()
    for rows in groups.values():
        k = len(rows)
        for j in range(k):
            vj, kj, hj = rows[j]
            cand = [(vj, kj, hj)]
            for i in range(j):
                vi, ki, hi = rows[i]
                d = dict(vj)
                for idx, c in vi.items():
                    d[idx] = d.get(idx, 0) - c
                cand.append((d, kj - ki, hj - hi))
            for t, (v, kc, rh) in enumerate(cand):
                pairs += 1
                mv = monic(v, kc, rh, N)
                if mv is None:
                    zero += 1
                    continue
                rels[mv] += 1
                if t == 0:
                    star.add(mv)
    return len(rels), pairs, zero, Counter(rels.values()), len(star)


def main(out: str) -> None:
    os.makedirs(out, exist_ok=True)
    design = json.load(open(DESIGN))
    curves = {(c["bits"], c["curve"]): c for c in design["curves"]}
    n_b = design["final_n_b"]
    files_read = {DESIGN: sha256(DESIGN)}

    census = {}          # (bits, curve, arm) -> dict
    dup_keys = []
    groups = defaultdict(lambda: defaultdict(list))  # (bits, curve, arm) -> first-el key -> rows
    tt_rows_seen = Counter()
    other_m_or_mode = Counter()
    jobdirs = sorted(os.listdir(JOBS))
    for jd in jobdirs:
        rp = os.path.join(JOBS, jd, "rows.jsonl.gz")
        hp = os.path.join(JOBS, jd, "harvest-rows.jsonl.gz")
        files_read[rp] = sha256(rp)
        files_read[hp] = sha256(hp)
        with gzip.open(rp, "rt") as f:
            for line in f:
                r = json.loads(line)
                if not m4_table(r):
                    other_m_or_mode[(r.get("method"), r.get("mode"))] += 1
                    continue
                key = (r["bits"], r["curve"], r["arm"])
                if key in census:
                    dup_keys.append(list(key))
                    continue
                tt = (r.get("harvest") or {}).get("TT", {}).get("at_stop", {})
                census[key] = {
                    "job": jd, "status": r.get("status"), "fb_size": r.get("fb_size"),
                    "N": r.get("N"), "p": r.get("p"), "a": r.get("a"), "b": r.get("b"),
                    "retain": (r.get("harvest") or {}).get("retain"),
                    "eng_distinct": tt.get("relations_distinct"),
                    "eng_nonformal": tt.get("relations_nonformal"),
                    "eng_pairs": tt.get("relation_pairs"),
                    "eng_pairs_zero": tt.get("relation_pairs_zero"),
                    "eng_R_star": tt.get("R_star"),
                    "eng_rows_emitted": tt.get("rows_emitted"),
                    "eng_star_groups": tt.get("star_groups"),
                    "eng_mult": tt.get("multiplicity_histogram"),
                }
        with gzip.open(hp, "rt") as f:
            for line in f:
                h = json.loads(line)
                if h.get("class") != "TT" or h.get("arm") not in SCORED:
                    continue
                if h.get("m") != 4 or h.get("mode") != "table":
                    other_m_or_mode[("harvest", h.get("m"), h.get("mode"))] += 1
                    continue
                key = (h["bits"], h["curve"], h["arm"])
                g = json.dumps(h["elements"][0], sort_keys=True, separators=(",", ":"))
                vec = {}
                for i, v in h["coeffs"]:
                    vec[i] = vec.get(i, 0) + v
                groups[key][g].append((vec, int(h["kcoef"]), int(h["rhs"])))
                tt_rows_seen[key] += 1

    # ---- coverage of the design and G-CURVE-style binding (for mu_model) ----
    missing, curve_mismatch = [], []
    for (bits, c), d in curves.items():
        for arm in ALL_ARMS:
            k = (bits, c, arm)
            if k not in census:
                missing.append(list(k))
                continue
            row = census[k]
            if (row["N"], row["p"], row["a"], row["b"]) != (d["N"], d["p"], d["a"], d["b"]):
                curve_mismatch.append(list(k))
    extra_keys = [list(k) for k in census if (k[0], k[1]) not in curves]
    status_counts = Counter((k[2], v["status"]) for k, v in census.items())

    # ---- recount per instance (scored arms) ----
    percurve = []
    rec_vs_eng = Counter()
    rec_mismatch = []
    pairs_mismatch = []
    for (bits, c) in sorted(curves):
        d = curves[(bits, c)]
        N = d["N"]
        entry = {"bits": bits, "curve": c, "mu_model": d["mu_model"], "s_sub": d["s_sub"],
                 "height_screened": bool(d.get("height_screened")), "N": N}
        for arm in SCORED:
            k = (bits, c, arm)
            row = census.get(k)
            if row is None:
                entry[arm] = None
                continue
            n, pairs, zero, mult, rstar = recount(groups.get(k, {}), N)
            entry[arm] = {"n": n, "status": row["status"], "fb_size": row["fb_size"],
                          "eng": row["eng_nonformal"]}
            same = (n == row["eng_nonformal"] == row["eng_distinct"])
            rec_vs_eng["equal" if same else "differ"] += 1
            if not same:
                rec_mismatch.append({"key": list(k), "recount": n,
                                     "eng_distinct": row["eng_distinct"],
                                     "eng_nonformal": row["eng_nonformal"]})
            if row["eng_pairs"] is not None and (pairs != row["eng_pairs"] or zero != row["eng_pairs_zero"]
                                                 or rstar != row["eng_R_star"]):
                pairs_mismatch.append({"key": list(k), "pairs": pairs, "eng_pairs": row["eng_pairs"],
                                       "zero": zero, "eng_zero": row["eng_pairs_zero"],
                                       "R_star": rstar, "eng_R_star": row["eng_R_star"]})
        # statuses of every arm (for F2)
        entry["all_arms_valid"] = all(
            census.get((bits, c, arm), {}).get("status") == "completed_valid" for arm in ALL_ARMS)
        percurve.append(entry)

    # ---- cross-check against the merged run-root rows.jsonl.gz ----
    files_read[ROOT_ROWS] = sha256(ROOT_ROWS)
    root_seen = Counter()
    root_mismatch = []
    root_dups = 0
    root_keys = set()
    with gzip.open(ROOT_ROWS, "rt") as f:
        for line in f:
            r = json.loads(line)
            if not m4_table(r):
                root_seen[("other", r.get("method"), r.get("mode"))] += 1
                continue
            key = (r["bits"], r["curve"], r["arm"])
            if key in root_keys:
                root_dups += 1
            root_keys.add(key)
            root_seen["rows"] += 1
            if r["arm"] in SCORED:
                tt = (r.get("harvest") or {}).get("TT", {}).get("at_stop", {})
                pj = census.get(key)
                if pj is None or pj["status"] != r.get("status") or pj["eng_nonformal"] != tt.get("relations_nonformal") \
                        or pj["fb_size"] != r.get("fb_size"):
                    root_mismatch.append(list(key))
    root_missing = len(set(census) - root_keys)

    # ---- admission (R-2 F1 / F2; M admission) ----
    def valid(e, arm):
        return e[arm] is not None and e[arm]["status"] == "completed_valid"

    for e in percurve:
        rs_ok = all(valid(e, r) for r in RANDOMS)
        rsize = {e[r]["fb_size"] for r in RANDOMS if e[r] is not None}
        e["rand_ok"] = rs_ok and len(rsize) == 1
        rsz = next(iter(rsize)) if len(rsize) == 1 else None
        e["A_F1"] = e["rand_ok"] and valid(e, A) and e[A]["fb_size"] == rsz
        e["M_F1"] = (e["rand_ok"] and valid(e, M) and e[M]["fb_size"] == rsz
                     and not e["height_screened"])
        e["A_F2"] = e["A_F1"] and e["all_arms_valid"]
        e["M_F2"] = e["M_F1"] and e["all_arms_valid"]
        e["size_match_s_sub"] = all(e[x] is not None and e[x]["fb_size"] == e["s_sub"] for x in SCORED)

    def cell(sel, arm, rungs=(30, 32)):
        """Exact CC-8 sums over the curves e with sel(e) and bits in rungs."""
        CX = T = Q = 0
        n = 0
        for e in percurve:
            if e["bits"] not in rungs or not sel(e):
                continue
            n += 1
            r = [e[x]["n"] for x in RANDOMS]
            CX += e[arm]["n"] if arm else 0
            T += sum(r)
            Q += 3 * sum(v * v for v in r) - sum(r) ** 2
        C_R = Fraction(T, 3)
        S = Fraction(Q, 6)
        V = max(S, C_R)
        sd = math.sqrt(float(V) * 4 / 3)
        out = {"curves": n, "C_X": CX, "three_C_R": T, "six_sum_s2": Q,
               "C_R": float(C_R), "sum_s2": float(S), "V": float(V),
               "V_is_floor": bool(C_R > S), "SD_null": sd}
        if arm:
            out["kappa_rel"] = float(Fraction(CX) / C_R) if T else None
            out["z"] = float(CX - C_R) / sd if sd else None
            out["SE"] = sd / float(C_R)
        return out, (CX, T, Q)

    selA = lambda e: e["A_F1"]
    selM = lambda e: e["M_F1"]
    selAM = lambda e: e["A_F1"] and e["M_F1"]
    res = {}
    res["A_pooled"], (CA, TA, QA) = cell(selA, A)
    res["A_per_rung"] = {b: cell(selA, A, (b,))[0] for b in (30, 32)}
    res["M_pooled_M1"], (CM, TM, QM) = cell(selM, M)
    res["M_per_rung_M1"] = {b: cell(selM, M, (b,))[0] for b in (30, 32)}
    # R-4 P2 alternative: per-rung floor
    P2 = sum(max(Fraction(res["A_per_rung"][b]["six_sum_s2"], 6), Fraction(res["A_per_rung"][b]["three_C_R"], 3))
             for b in (30, 32))
    res["A_pooled_P2_V"] = float(P2)
    res["A_pooled_P2_z"] = float(Fraction(CA) - Fraction(TA, 3)) / math.sqrt(float(P2) * 4 / 3)
    # M2 alternative: C_M over M curves; C_R, V of the A cell
    res["M_pooled_M2"] = {"C_M": CM,
                          "z": float(Fraction(CM) - Fraction(TA, 3)) / res["A_pooled"]["SD_null"],
                          "kappa_rel": float(Fraction(CM) / Fraction(TA, 3))}
    # z_Delta readings
    am, (CA_am, T_am, Q_am) = cell(selAM, A)
    CM_am = sum(e[M]["n"] for e in percurve if selAM(e))
    V_am = max(Fraction(Q_am, 6), Fraction(T_am, 3))
    VA = max(Fraction(QA, 6), Fraction(TA, 3))
    VM = max(Fraction(QM, 6), Fraction(TM, 3))
    res["z_Delta"] = {
        "curves_where_M_admitted_and_A_admitted": am["curves"],
        "C_A_on_M_curves": CA_am, "C_M_on_M_curves": CM_am,
        "D1_V_own_set": float(V_am), "D1_z": (CA_am - CM_am) / math.sqrt(2 * float(V_am)),
        "D2_V_A_cell": float(VA), "D2_z": (CA_am - CM_am) / math.sqrt(2 * float(VA)),
        "D3_C_A_all_A_curves": CA, "D3_z": (CA - CM) / math.sqrt(2 * float(VA)),
        "D4_V_M_cell": float(VM), "D4_z": (CA_am - CM_am) / math.sqrt(2 * float(VM)),
    }
    res["z_Delta_per_rung_D1"] = {}
    for b in (30, 32):
        sub, (ca, t, q) = cell(selAM, A, (b,))
        cm = sum(e[M]["n"] for e in percurve if selAM(e) and e["bits"] == b)
        vb = max(Fraction(q, 6), Fraction(t, 3))
        res["z_Delta_per_rung_D1"][b] = {"C_A": ca, "C_M": cm, "V": float(vb),
                                         "z": (ca - cm) / math.sqrt(2 * float(vb))}
    # F2 alternative and S2 alternative
    res["A_pooled_F2"] = cell(lambda e: e["A_F2"], A)[0]
    res["M_pooled_F2"] = cell(lambda e: e["M_F2"], M)[0]
    res["randoms_S2"] = cell(lambda e: e["rand_ok"], None)[0]

    admission = {
        "design_curves_per_rung": {b: sum(1 for e in percurve if e["bits"] == b) for b in (30, 32)},
        "final_n_b": n_b,
        "A_admitted_F1": {b: sum(1 for e in percurve if e["bits"] == b and e["A_F1"]) for b in (30, 32)},
        "M_admitted_F1": {b: sum(1 for e in percurve if e["bits"] == b and e["M_F1"]) for b in (30, 32)},
        "A_admitted_F2": {b: sum(1 for e in percurve if e["bits"] == b and e["A_F2"]) for b in (30, 32)},
        "M_admitted_F2": {b: sum(1 for e in percurve if e["bits"] == b and e["M_F2"]) for b in (30, 32)},
        "height_screened": sum(1 for e in percurve if e["height_screened"]),
        "fb_size_equals_s_sub_all_scored_arms": sum(1 for e in percurve if e["size_match_s_sub"]),
    }
    integrity = {
        "job_dirs": len(jobdirs),
        "census_keys_m4_table": len(census),
        "duplicate_census_keys_in_job_files": dup_keys[:20],
        "duplicate_census_key_count": len(dup_keys),
        "rows_other_m_or_mode": {str(k): v for k, v in other_m_or_mode.items()},
        "missing_design_instances": missing[:20], "missing_count": len(missing),
        "extra_keys_not_in_design": extra_keys[:20], "extra_count": len(extra_keys),
        "curve_identity_mismatch_vs_design": curve_mismatch[:20], "curve_mismatch_count": len(curve_mismatch),
        "status_counts": {f"{a}|{s}": n for (a, s), n in sorted(status_counts.items())},
        "retain_values": sorted({str(v["retain"]) for v in census.values()}),
        "recount_vs_engine_relations_distinct_and_nonformal": dict(rec_vs_eng),
        "recount_mismatches": rec_mismatch[:50], "recount_mismatch_count": len(rec_mismatch),
        "pairs_zero_Rstar_mismatch_count": len(pairs_mismatch), "pairs_mismatch_examples": pairs_mismatch[:10],
        "tt_harvest_rows_scored_arms": sum(tt_rows_seen.values()),
        "root_rows": dict((str(k), v) for k, v in root_seen.items()),
        "root_duplicate_keys": root_dups, "root_missing_job_keys": root_missing,
        "root_vs_job_mismatch_count": len(root_mismatch), "root_vs_job_mismatch_examples": root_mismatch[:10],
    }
    summary = {"what": "TASK-20261009-a92ff3 own CC-1..CC-3 recount and CC-8/CC-10 cells (readings R-1..R-7)",
               "admission": admission, "integrity": integrity, "cells": res,
               "files_read_sha256": {os.path.relpath(k, REPO): v for k, v in sorted(files_read.items())}}
    with open(os.path.join(out, "counts.json"), "w") as f:
        json.dump(summary, f, indent=1, sort_keys=False, default=str)
    with gzip.open(os.path.join(out, "percurve.json.gz"), "wt") as f:
        for e in percurve:
            f.write(json.dumps({"bits": e["bits"], "curve": e["curve"], "N": e["N"], "s_sub": e["s_sub"],
                                "mu_model": e["mu_model"], "height_screened": e["height_screened"],
                                "A_F1": e["A_F1"], "M_F1": e["M_F1"], "A_F2": e["A_F2"], "M_F2": e["M_F2"],
                                "rand_ok": e["rand_ok"],
                                "n": {arm: (e[arm]["n"] if e[arm] else None) for arm in SCORED}},
                               sort_keys=True) + "\n")
    print("done", out)


if __name__ == "__main__":
    main(sys.argv[1])

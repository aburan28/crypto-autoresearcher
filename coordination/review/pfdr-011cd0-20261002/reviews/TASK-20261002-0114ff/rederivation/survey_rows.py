#!/usr/bin/env python3
"""Structural survey of the raw harvest rows (R12, R13 attempt-1 jobs).

TASK-20261002-0114ff, written by the validator from the specification text and
the row format only. Reads ONLY harvest-rows.jsonl.gz files and design.json
(both on the card's pre-seal list). Computes NO relation count. It answers the
format questions the counting code depends on, before any count exists:

  * which classes / element types occur in each mode;
  * row orientation: is every row coeffs == eps * (u1 - sigma * u2) with the
    first element's vector u1 entering with a FIXED sign eps per class?
  * star structure: does any element occur as the first element of one row
    and the second element of another within one (instance, class)?
  * instance contiguity of rows in each file;
  * SS 'seq': monotone in file order within an instance; rows with seq >=
    X_fix lie only in the instance's last attempt.

Standard library only.
"""
import collections
import gzip
import json
import math
import os
import sys

WT = "/tmp/claude-0/-home-user/015c3767-cc03-52db-9b0c-bd2aa6c26537/scratchpad/wt-pfdr011cd0-5753edf2e"
EXP = WT + "/experiments/EXP-PFDR-011cd0"
RUNS = {"R12": EXP + "/runs/RUN-PFDR-011cd0-table/attempt-1/jobs",
        "R13": EXP + "/runs/RUN-PFDR-011cd0-search/attempt-1/jobs"}
DESIGN = EXP + "/runs/RUN-PFDR-011cd0-p0-design/attempt-3/design.json"


def vec_add(d, idx, c):
    v = d.get(idx, 0) + c
    if v:
        d[idx] = v
    else:
        d.pop(idx, None)


def elem_key(e):
    if "base" in e:
        return ("B", e["base"])
    if "tail" in e:
        return ("T", tuple(tuple(t) for t in e["tail"]))
    if "enc" in e:
        a, H, j, s = e["enc"]
        return ("E", a, tuple(tuple(h) for h in H), j, s)
    raise ValueError("unknown element " + repr(sorted(e)))


def base_vec(e, hyp):
    """Base-index part of an element's vector. hyp only matters for SS encodings."""
    d = {}
    if "base" in e:
        d[e["base"]] = 1
    elif "tail" in e:
        for i, s in e["tail"]:
            vec_add(d, i, s)
    else:
        a, H, j, s = e["enc"]
        hs = 1 if hyp in ("H+s", "H-s") else -1
        for i, t in H:
            vec_add(d, i, hs * t)
        vec_add(d, j, (1 if hyp in ("H+s", "-H+s") else -1) * s)
    return d


def lin(u, v, a, b):
    out = dict()
    for k, x in u.items():
        vec_add(out, k, a * x)
    for k, x in v.items():
        vec_add(out, k, b * x)
    return out


def main():
    design = json.load(open(DESIGN))
    xfix = {(c["bits"], c["curve"]): c["X_fix"] for c in design["curves"]}
    xfix_mismatch = [(c["bits"], c["curve"]) for c in design["curves"]
                     if c["X_fix"] != 20 * math.isqrt(c["N"])]
    out = {"xfix_design_vs_20isqrtN_mismatches": xfix_mismatch, "runs": {}}
    hyps = ("H+s", "H-s", "-H+s", "-H-s")
    for run, jd in RUNS.items():
        st = collections.Counter()
        orient = collections.Counter()
        orient_ss = {h: collections.Counter() for h in hyps}
        noncontig, star_viol, dup_pairs = [], 0, 0
        ybit_incons = 0
        seq_nonmono, seq_past_xfix_not_last = 0, 0
        seq_stats = []
        jobs = sorted(os.listdir(jd))
        for job in jobs:
            fp = os.path.join(jd, job, "harvest-rows.jsonl.gz")
            if not os.path.exists(fp):
                st["job_without_harvest_rows:" + job] += 1
                continue
            seen_keys, cur = set(), None
            firsts, seconds, pairs = {}, {}, set()
            ybits = {}
            inst_rows = []  # (attempt, seq) for SS

            def flush():
                nonlocal star_viol, seq_nonmono, seq_past_xfix_not_last
                if cur is None:
                    return
                for cls in firsts:
                    star_viol += len(firsts[cls] & seconds.get(cls, set()))
                if inst_rows:
                    last_att = max(a for a, s in inst_rows)
                    prev = -1
                    for a, s in inst_rows:
                        if s <= prev:
                            seq_nonmono += 1
                        prev = s
                    xf = xfix[(cur[0], cur[1])]
                    for a, s in inst_rows:
                        if s >= xf and a != last_att:
                            seq_past_xfix_not_last += 1
                    seq_stats.append({"key": list(cur), "rows": len(inst_rows),
                                      "max_seq": max(s for a, s in inst_rows), "X_fix": xf,
                                      "rows_seq_ge_xfix": sum(1 for a, s in inst_rows if s >= xf),
                                      "last_attempt": last_att})

            with gzip.open(fp, "rt") as fh:
                for line in fh:
                    r = json.loads(line)
                    key = (r["bits"], r["curve"], r["m"], r["arm"], r["mode"])
                    if key != cur:
                        flush()
                        if key in seen_keys:
                            noncontig.append(list(key))
                        seen_keys.add(key)
                        cur = key
                        firsts, seconds, pairs, ybits, inst_rows = {}, {}, set(), {}, []
                    cls = r["class"]
                    e1, e2 = r["elements"]
                    t1 = "base" if "base" in e1 else ("tail" if "tail" in e1 else "enc")
                    t2 = "base" if "base" in e2 else ("tail" if "tail" in e2 else "enc")
                    st[(r["mode"], cls, t1, t2, r["attempt"] == -1)] += 1
                    k1, k2 = elem_key(e1), elem_key(e2)
                    for k, e in ((k1, e1), (k2, e2)):
                        if "ybit" in e:
                            if ybits.setdefault(k, e["ybit"]) != e["ybit"]:
                                ybit_incons += 1
                    firsts.setdefault(cls, set()).add(k1)
                    seconds.setdefault(cls, set()).add(k2)
                    if (cls, k1, k2) in pairs:
                        dup_pairs += 1
                    pairs.add((cls, k1, k2))
                    c = {}
                    for i, x in r["coeffs"]:
                        vec_add(c, i, x)
                    if cls in ("TT", "TB"):
                        u1, u2 = base_vec(e1, None), base_vec(e2, None)
                        hit = [(eps, sg) for eps in (1, -1) for sg in (1, -1)
                               if lin(u1, u2, eps, -eps * sg) == c]
                        orient[(cls, tuple(hit))] += 1
                    else:
                        for h in hyps:
                            u1, u2 = base_vec(e1, h), base_vec(e2, h)
                            hit = [(eps, sg) for eps in (1, -1) for sg in (1, -1)
                                   if lin(u1, u2, eps, -eps * sg) == c]
                            orient_ss[h][tuple(hit)] += 1
                        inst_rows.append((r["attempt"], r["seq"]))
                flush()
        out["runs"][run] = {
            "jobs": len(jobs),
            "row_types": {repr(k): v for k, v in sorted(st.items(), key=lambda kv: repr(kv[0]))},
            "tt_tb_orientation_hits": {repr(k): v for k, v in orient.items()},
            "ss_orientation_hits_by_hypothesis": {h: {repr(k): v for k, v in c.items()}
                                                  for h, c in orient_ss.items()},
            "noncontiguous_instance_keys": noncontig[:50],
            "noncontiguous_count": len(noncontig),
            "star_violations_element_first_and_second": star_viol,
            "duplicate_first_second_pairs": dup_pairs,
            "ybit_inconsistencies": ybit_incons,
            "ss_seq_nonmonotone_steps": seq_nonmono,
            "ss_rows_seq_ge_xfix_not_in_last_attempt": seq_past_xfix_not_last,
            "ss_instances_with_rows": len(seq_stats),
            "ss_instances_max_seq_lt_xfix": sum(1 for s in seq_stats if s["max_seq"] < s["X_fix"]),
            "ss_seq_sample": seq_stats[:5],
        }
    json.dump(out, open(sys.argv[1], "w"), indent=1)


if __name__ == "__main__":
    main()

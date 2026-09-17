#!/usr/bin/env python3
"""summarize.py -- aggregate results.jsonl of RUN-SEMBIN-595308 into the
per-cell table the contract asks for: d_F4 (both readings), closure_D, the
separation closure_D - d_F4, the single-level Macaulay ranks, largest
separation instance, agreements-with-different-profiles, and unreached cells.
Pure aggregation; no interpretation."""
from __future__ import annotations

import json
import sys
from collections import defaultdict
from pathlib import Path


from f4_trace import read_d_f4  # noqa: E402


def reread(r):
    """Re-derive the d_F4 readings from the stored raw rounds with the
    input-degree floor (records written before the floor existed carry
    input_max_degree = None; the floor is then the structure's max_degree,
    or 2 for the planted-point control whose generators are quadratic)."""
    if r.get("instrument") != "f4_trace_msolve" or r.get("status") != "completed":
        return r
    deg = r.get("input_max_degree")
    if deg is None:
        deg = (r.get("structure") or {}).get("max_degree")
    if deg is None and r.get("family") == "known_false_planted_point":
        deg = 2
    if deg is None and r.get("family") == "matched_null":
        deg = (r.get("structure") or {}).get("max_degree")
    d_sem, d_lpr, d_naive, tail = read_d_f4(r.get("rounds", []), deg)
    r["d_F4_semaev_reread"] = d_sem
    r["d_F4_last_productive_round"] = d_lpr
    r["d_F4_semaev"] = d_sem
    r["reread_floor_degree"] = deg
    return r


def posthoc_closure(cl, f4):
    """A closure record whose verdict was 'undetermined' at measurement time
    (|V(I)| unknown because the F4 run had not completed) is re-evaluated when
    a completed F4 record for the SAME system bytes supplies the quotient
    dimension s: the closure record stores its standard-monomial count c, and in
    the Boolean ring G_D is a Groebner basis iff c == s.  The original verdict
    is kept; the post-hoc one is added alongside with its basis."""
    if not cl or not f4 or f4.get("status") != "completed":
        return cl
    s = f4.get("quotient_dimension")
    if s is None or cl.get("input_sha256") != f4.get("input_sha256"):
        return cl
    for pD in cl.get("per_D", []):
        if pD.get("verdict") == "undetermined" and pD.get("status") == "completed":
            c = pD.get("standard_monomials")
            if pD.get("contains_one"):
                pD["verdict_posthoc"], pD["verdict_posthoc_basis"] = "sufficient", "1 in W_D"
            elif c is None:
                pD["verdict_posthoc"] = "insufficient" if s <= 100000 else "undetermined"
                pD["verdict_posthoc_basis"] = f"standard monomials > cap >= |V(I)| = {s} (s from {f4['instance_id']})"
            elif c == s:
                pD["verdict_posthoc"], pD["verdict_posthoc_basis"] = "sufficient", f"standard monomials = |V(I)| = {s} (s from {f4['instance_id']})"
            elif c > s:
                pD["verdict_posthoc"], pD["verdict_posthoc_basis"] = "insufficient", f"standard monomials {c} > |V(I)| = {s}"
            else:
                pD["verdict_posthoc"], pD["verdict_posthoc_basis"] = "error", f"standard monomials {c} < |V(I)| = {s}"
    if cl.get("closure_D") is None:
        suff = [pD["D"] for pD in cl.get("per_D", []) if pD.get("verdict") == "sufficient" or pD.get("verdict_posthoc") == "sufficient"]
        cl["closure_D_posthoc"] = min(suff) if suff else None
    return cl


def load(paths):
    """Load one or more results.jsonl files. Duplicate (instance, instrument)
    records (two workers briefly shared workerB/cells) are resolved by keeping
    the first COMPLETED record, else the first record; every record is counted
    in n_records_raw and the number of duplicates is reported."""
    if isinstance(paths, (str, Path)):
        paths = [paths]
    recs = []
    for path in paths:
        recs.extend(reread(json.loads(l)) for l in open(path) if l.strip())
    by_inst = defaultdict(dict)
    dups = 0
    for r in recs:
        slot = by_inst[r["instance_id"]]
        key = r["instrument"]
        if key in slot:
            dups += 1
            old = slot[key]
            if old.get("status") != "completed" and r.get("status") == "completed":
                slot[key] = r
            elif key == "closure_certificate" and old.get("closure_D") is None and r.get("closure_D") is not None:
                slot[key] = r
            continue
        slot[key] = r
    # heavy-pass records are keyed by the same instance_id with suffix "_heavy": fold their F4 into the base instance
    # and drop the "_heavy" key so the same system is not counted twice in its cell. The folded record keeps the
    # base record's group: a heavy worker started with --cells tags its records "override", and the cell label
    # must follow the system, not the worker that measured it.
    def fold(hv, b):
        hv = dict(hv, heavy_pass=True)
        if b and b.get("group") is not None:
            hv["group"] = b["group"]
        return hv

    for iid in list(by_inst):
        if iid.endswith("_heavy"):
            base = iid[: -len("_heavy")]
            if base not in by_inst:
                continue
            hv = by_inst[iid].get("f4_trace_msolve")
            if hv:
                b = by_inst[base].get("f4_trace_msolve")
                if not b or b.get("status") != "completed":
                    by_inst[base]["f4_trace_msolve"] = fold(hv, b)
            for k in ("closure_certificate",):
                if k in by_inst[iid] and (k not in by_inst[base] or by_inst[base][k].get("closure_D") is None):
                    by_inst[base][k] = fold(by_inst[iid][k], by_inst[base].get(k))
            del by_inst[iid]
    for iid, ins in by_inst.items():
        if "closure_certificate" in ins:
            ins["closure_certificate"] = posthoc_closure(ins["closure_certificate"], ins.get("f4_trace_msolve"))
    load.duplicates = dups
    return recs, by_inst


def key(r):
    return (r.get("n"), r.get("m"), r.get("t"), r.get("k"), r.get("subspace"), r.get("B_mode"))


def main():
    paths = [Path(a) for a in sys.argv[1:]]
    recs, by_inst = load(paths)
    cells = defaultdict(list)
    for iid, ins in by_inst.items():
        f4 = ins.get("f4_trace_msolve")
        cl = ins.get("closure_certificate")
        if not f4:
            continue
        cells[(f4.get("group"), key(f4))].append((iid, f4, cl, ins.get("macaulay_single_level_DREG")))
    table = []
    max_sep = None
    agree_diff_profile = []
    for (group, k), rows in sorted(cells.items(), key=lambda x: (str(x[0][0]), str(x[0][1]))):
        d_sem = [r[1]["d_F4_semaev"] for r in rows if r[1]["status"] == "completed"]
        d_nai = [r[1]["d_F4_naive"] for r in rows if r[1]["status"] == "completed"]
        def cdv(r):
            return r[2].get("closure_D") if r[2].get("closure_D") is not None else r[2].get("closure_D_posthoc")
        cD = [cdv(r) for r in rows if r[2] and cdv(r) is not None]
        seps = [(cdv(r) - r[1]["d_F4_semaev"], r[0]) for r in rows if r[2] and cdv(r) is not None and r[1]["d_F4_semaev"] is not None]
        quot = [r[1]["quotient_dimension"] for r in rows if r[1]["status"] == "completed"]
        unreached_f4 = [r[0] for r in rows if r[1]["status"] != "completed"]
        unreached_cl = [r[0] for r in rows if r[2] and cdv(r) is None]
        closure_measured = sum(1 for r in rows if r[2])
        wall_f4 = [r[1]["wall_s"] for r in rows]
        single = defaultdict(list)
        for r in rows:
            if r[3]:
                for p in r[3]["per_D"]:
                    if p.get("rank") is not None:
                        single[p["D"]].append((p["rank"], p["rows"], p["cols"], p["deficit_vs_semiregular"]))
        entry = {
            "group": group, "n": k[0], "m": k[1], "t": k[2], "k": k[3], "subspace": k[4], "B_mode": k[5],
            "instances": len(rows), "closure_measured_instances": closure_measured,
            "d_F4_semaev_values": sorted(set(d_sem)), "d_F4_naive_values": sorted(set(d_nai)),
            "closure_D_values": sorted(set(cD)),
            "separation_values": sorted(set(s for s, _ in seps)),
            "n_consistent_instances": sum(1 for q in quot if q not in (0, None)),
            "quotient_dimensions": sorted(set(q for q in quot if q is not None), key=int) + ([None] if any(q is None for q in quot) else []),
            "f4_unreached": unreached_f4, "closure_unreached": unreached_cl,
            "f4_wall_s_min_max": [round(min(wall_f4), 1), round(max(wall_f4), 1)] if wall_f4 else None,
            "single_level": {str(D): {"rank_min_max": [min(v[0] for v in vals), max(v[0] for v in vals)],
                                      "rows": vals[0][1], "cols": vals[0][2],
                                      "deficit_min_max": [min(v[3] for v in vals), max(v[3] for v in vals)]} for D, vals in single.items()},
        }
        table.append(entry)
        for s, iid in seps:
            if max_sep is None or s > max_sep[0]:
                max_sep = (s, iid)
        for r in rows:
            if r[2] and cdv(r) is not None and r[1]["d_F4_semaev"] == cdv(r):
                # profiles: F4 productive degrees vs closure per-D verdict sequence
                f4_prod_degs = sorted(set(x["deg"] for x in r[1]["rounds"] if x["new"] > 0))
                cl_degs = [p["D"] for p in r[2]["per_D"] if p.get("status") == "completed"]
                agree_diff_profile.append({"instance_id": r[0], "f4_productive_degrees": f4_prod_degs,
                                           "closure_D_sequence": cl_degs, "f4_tail": r[1]["f4_empty_step_degrees"]})
    out = {"cells": table, "largest_separation": max_sep,
           "n_instances": len(by_inst), "n_records_raw": len(recs), "duplicate_records_resolved": load.duplicates,
           "agreements": len(agree_diff_profile),
           "agreement_profiles_sample": agree_diff_profile[:5]}
    print(json.dumps(out, indent=2, default=str))


if __name__ == "__main__":
    main()

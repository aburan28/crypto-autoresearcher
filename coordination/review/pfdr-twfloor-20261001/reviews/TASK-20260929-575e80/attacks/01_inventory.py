"""01 -- instance inventory and frozen A7 ratios as INPUT (G-0, G-1, F3-2).

Writes out/instances.jsonl (one compact record per main/j0 solver instance of
R10-R12, R14 and R16) and out/01_inventory.json (counts; equality of my sub-0.9
key set with the producer's below_0_9 list; rank == sum(solver_rank_increments)
check). No randomness.
"""
import json
import os
import sys
from collections import Counter

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from lib575 import (CANON, OUT, RUNS, P, arm_class, dump, evaluable, iter_jsonl, key_of,  # noqa: E402
                    load_panel_rows, m_of, r_frozen, ratio, unmatched_size_set)

CLS = ("TT", "TB", "SS")


def compact(r, um, src):
    ok, why = evaluable(r, um)
    h = r.get("harvest") or {}
    rec = {"panel": r.get("panel"), "bits": r["bits"], "curve": r["curve"], "m": m_of(r),
           "arm": r["arm"], "mode": r.get("mode"), "cls": arm_class(r["arm"]), "src": src,
           "status": r.get("status"), "evaluable": ok, "excl_reason": why}
    if not h:
        return rec
    rec.update({
        "N": r["N"], "p": r["p"], "B": r["fb_size"], "S": r["s3_solves"],
        "table_s3": r["table_s3_solves"], "search_s3": r["s3_solves"] - r["table_s3_solves"],
        "table_entries": r["table_entries"], "h": r["table_arity"], "attempts": r["attempts"],
        "relations": r["relations"], "rank": r["rank"], "k_verified": r.get("k_verified"),
        "terminated_by": h.get("terminated_by"), "formal_kind": h.get("formal_basis_kind"),
        "formal_rank": h.get("formal_basis_rank"), "U": h.get("U"),
        "enc_rec": h["ss_store"]["encodings_recorded"],
        "search_charged": h["ss_store"]["search_s3_charged"],
        "degenerate": h["ss_store"]["degenerate_roots"],
        "identity_ok": h["ss_store"]["identity_ok"],
        "E_t": h["table"]["formally_distinct_tails"],
        "attempt_cap": r.get("attempt_cap"),
    })
    for c in CLS:
        st = h[c]["at_stop"]
        rec[f"mu_{c}"] = st["poisson_mean"]
        rec[f"pairs_{c}"] = st["pairs_raw"]
        rec[f"rows_{c}"] = st["rows_emitted"]
        rec[f"rowsformal_{c}"] = st["rows_formal"]
        rec[f"inforank_{c}"] = st["informative_rank"]
    ss_fix = h["SS"].get("at_A_fix") or {}
    rec["X_s_distinct_stop"] = h["ss_store"]["encodings_recorded"]  # recorded (before dups)
    rec["ss_fix_censored"] = ss_fix.get("censored")
    if r.get("mode") == "on":
        on = h["on"]
        rec["fed"] = dict(on["rows_fed"])
        rec["incr"] = dict(on["solver_rank_increments"])
        rec["k_by"] = on["k_determined_by"]
    rec["r_frozen"] = r_frozen(r)
    if ok:
        rec["ratio"] = ratio(r["s3_solves"], rec["r_frozen"], r["N"])
    return rec


def main():
    rows = load_panel_rows()
    um = unmatched_size_set(rows)
    recs = [compact(r, um, r["_src"]) for r in rows]
    # stage R (R16) rows: same rule, own set
    srows = [r for r in iter_jsonl(CANON["stage-r"]) if r.get("panel") == "main" and r.get("arm")]
    um_s = unmatched_size_set(srows)
    srecs = [compact(r, um_s, "stage-r") for r in srows]
    with open(os.path.join(OUT, "instances.jsonl"), "w") as fh:
        for rec in recs + srecs:
            fh.write(json.dumps(rec, sort_keys=True) + "\n")

    ev = [x for x in recs if x["evaluable"]]
    mine = sorted((x["panel"], x["bits"], x["curve"], x["m"], x["arm"], x["mode"])
                  for x in ev if x["ratio"] < 0.9)
    an = json.load(open(os.path.join(RUNS, P + "analysis", "analysis.json")))
    prod = sorted((x["panel"], x["bits"], x["curve"], x["m"], x["arm"], x["mode"])
                  for x in an["A7_floor"]["below_0_9"])
    prod_ratio = {(x["panel"], x["bits"], x["curve"], x["m"], x["arm"], x["mode"]): x["ratio"]
                  for x in an["A7_floor"]["below_0_9"]}
    my_ratio = {(x["panel"], x["bits"], x["curve"], x["m"], x["arm"], x["mode"]): x["ratio"]
                for x in ev}
    maxdiff = max(abs(prod_ratio[k] - my_ratio[k]) for k in prod_ratio) if prod_ratio else None
    rank_check = Counter()
    for x in recs:
        if x.get("mode") == "on" and "incr" in x:
            rank_check["equal" if sum(x["incr"].values()) == x["rank"] else "differ"] += 1
    sev = [x for x in srecs if x["evaluable"]]
    out = {
        "instances_main_j0": len(recs),
        "evaluable": len(ev),
        "excluded_by_reason": dict(Counter(x["excl_reason"] for x in recs if not x["evaluable"])),
        "excluded_by_reason_and_arm": dict(Counter(f"{x['excl_reason']}|{x['arm']}|{x['mode']}"
                                                   for x in recs if not x["evaluable"])),
        "producer_A7_instances": an["A7_floor"]["instances"],
        "producer_excluded_no_verified_k_or_r0": an["A7_floor"]["excluded_no_verified_k_or_r0"],
        "producer_excluded_unmatched_size": an["A7_floor"]["excluded_unmatched_size"],
        "my_below_0_9": len(mine), "producer_below_0_9": len(prod),
        "below_0_9_key_sets_equal": mine == prod,
        "max_abs_ratio_diff_on_firing_keys": maxdiff,
        "rank_equals_sum_increments_on_mode": dict(rank_check),
        "firing_by_class_mode_m": dict(Counter(f"{x['cls']}|{x['mode']}|m{x['m']}"
                                               for x in ev if x["ratio"] < 0.9)),
        "evaluable_by_class_mode_m": dict(Counter(f"{x['cls']}|{x['mode']}|m{x['m']}" for x in ev)),
        "stage_r_instances": len(srecs), "stage_r_evaluable": len(sev),
        "stage_r_below_0_9": sum(1 for x in sev if x["ratio"] < 0.9),
        "stage_r_producer_below_0_9": None,
    }
    sr = json.load(open(os.path.join(RUNS, P + "stage-r", "analysis.json")))
    a7s = sr.get("A7_floor") or {}
    out["stage_r_producer_below_0_9"] = len(a7s.get("below_0_9", [])) if a7s else "no A7 block"
    out["stage_r_producer_A7_instances"] = a7s.get("instances") if a7s else None
    dump("01_inventory.json", out)
    print(json.dumps({k: v for k, v in out.items() if not k.startswith("excluded_by_reason_and")}, indent=1))


if __name__ == "__main__":
    main()

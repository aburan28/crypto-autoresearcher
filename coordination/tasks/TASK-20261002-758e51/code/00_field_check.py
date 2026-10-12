"""00 -- FIELD CHECK (recorded preparation, not the analysis attempt).

Verifies, before the single analysis attempt (01_analysis.py):
  (1) the replica row counts and selection: m = 4 and m = 5, mode = on,
      bits 12..24, PRIMARY stop present, rank > 0, r_frozen > 0;
  (2) N and B are constant per rung (all rows of a rung share the rung prime
      and the factor-base size -- licenses the stratified-by-rung bootstrap
      and its exact per-stratum-sum form);
  (3) the per-rung aggregate T point values RECONCILE with the round's
      descriptive 09b_ptm5_agg_by_rung.json (same formula, same rows, both
      r conventions, all 14 cells) -- the completion gate requires this;
  (4) the ratio definitions per attacks/07_ptm5_analysis.py ratios();
  (5) the replica's m = 4 on-mode ratio levels under r_rank (for the level
      comparison against the engine's 2.10-3.63, EV-PFDR-d90ccd OBS-8).

Field mapping (licensed by attacks/07_ptm5_analysis.py, ratios() and the
aggregate_T block, and by attacks/ptm5_engine.py snapshot()):
  S_3     = stop["S"]            (= table_s3 + search_s3; table included)
  r_frozen = stop["r_frozen"]    (= relations + sum(rows_fed) in on mode)
  r_rank   = stop["rank"]        (the solver rank; independent relations)
  N        = row["N"],  B = row["B"]
  stop     = row["primary"]      (first row determining k; the engine-stop
                                  analogue; the stop 09b and 07 both read)

No engine/solver code is imported or executed; only the archived JSONL rows
are read. Deterministic: no randomness.
"""
import json
import math
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
TASK = os.path.dirname(HERE)
WT = os.path.dirname(os.path.dirname(os.path.dirname(TASK)))
REPL = os.path.join(WT, "coordination/review/pfdr-twfloor-20261001/reviews/"
                        "TASK-20260929-575e80/attacks/out")
ROWS = os.path.join(REPL, "ptm5_results.jsonl")
AGG09B = os.path.join(REPL, "09b_ptm5_agg_by_rung.json")


def main():
    recs = [json.loads(l) for l in open(ROWS)]
    out = {"total_rows": len(recs), "source": ROWS}
    from collections import Counter
    cells = Counter((r["m"], r["bits"], r["mode"]) for r in recs)
    out["cells_all_200"] = all(v == 200 for v in cells.values())
    out["n_cells"] = len(cells)

    sel = {}
    for m in (4, 5):
        rows = [r for r in recs if r["m"] == m and r["mode"] == "on"
                and 12 <= r["bits"] <= 24]
        ok = [r for r in rows if r["primary"] is not None]
        bad_rank = [r for r in ok if not r["primary"]["rank"]]
        bad_rf = [r for r in ok if not r["primary"]["r_frozen"]]
        per_rung = Counter(r["bits"] for r in ok)
        Ns, Bs = {}, {}
        for r in ok:
            Ns.setdefault(r["bits"], set()).add(r["N"])
            Bs.setdefault(r["bits"], set()).add(r["B"])
        sel[f"m{m}"] = {
            "rows_12_24_on": len(rows), "primary_present": len(ok),
            "rank_zero": len(bad_rank), "r_frozen_zero": len(bad_rf),
            "per_rung_counts": dict(sorted(per_rung.items())),
            "N_distinct_per_rung": {str(b): len(s) for b, s in sorted(Ns.items())},
            "B_distinct_per_rung": {str(b): len(s) for b, s in sorted(Bs.items())},
            "N_per_rung": {str(b): sorted(s)[0] for b, s in sorted(Ns.items())},
            "B_per_rung": {str(b): sorted(s)[0] for b, s in sorted(Bs.items())},
        }
    out["selection"] = sel

    # (3) reconciliation with the round's descriptive 09b per-rung T
    agg = json.load(open(AGG09B))
    recon, maxdiff = {}, 0.0
    for m in (4, 5):
        for b in range(12, 25, 2):
            rs = [r for r in recs if r["m"] == m and r["bits"] == b
                  and r["mode"] == "on" and r["primary"]]
            num = sum(r["primary"]["S"] ** 2 / (r["N"] * r["B"]) for r in rs)
            cell = {"n": len(rs)}
            for conv, key in (("frozen", "r_frozen"), ("rank", "rank")):
                den = sum(r["primary"][key] * r["N"] / 4 / (r["N"] * r["B"]) for r in rs)
                T = num / den
                ref = agg[f"m{m}|b{b}"][conv]
                d = abs(T - ref)
                maxdiff = max(maxdiff, d)
                cell[conv] = {"T": T, "ref_09b": ref, "absdiff": d}
            recon[f"m{m}|b{b}"] = cell
    out["reconciliation_with_09b"] = recon
    out["reconciliation_max_absdiff"] = maxdiff

    # (4)+(5) ratio levels on the m = 4 on-mode series (primary stop)
    lv = {"rank": [], "frozen": []}
    for r in recs:
        if r["m"] != 4 or r["mode"] != "on" or not 12 <= r["bits"] <= 24:
            continue
        p = r["primary"]
        if p is None:
            continue
        N = r["N"]
        if p["rank"]:
            lv["rank"].append(p["S"] / (0.5 * math.sqrt(p["rank"] * N)))
        if p["r_frozen"]:
            lv["frozen"].append(p["S"] / (0.5 * math.sqrt(p["r_frozen"] * N)))
    out["m4_on_series"] = {
        "n": len(lv["rank"]),
        "ratio_rank_min_max": [min(lv["rank"]), max(lv["rank"])],
        "ratio_frozen_min_max": [min(lv["frozen"]), max(lv["frozen"])],
        "engine_level_range_r_rank_OBS8": [2.10, 3.63],
    }
    json.dump(out, open(os.path.join(TASK, "out", "00_field_check.json"), "w"),
              indent=1, sort_keys=True)
    print(json.dumps(out, indent=1, sort_keys=True))


if __name__ == "__main__":
    sys.exit(main())

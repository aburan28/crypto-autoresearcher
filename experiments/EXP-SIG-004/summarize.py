# Build EXP-SIG-004 summary.json from run raw.json receipts.
import json
from pathlib import Path

EXP = Path("/Volumes/Volume/crypto-autoresearcher/experiments/EXP-SIG-004")

OLD = {9: {1: 23, 2: 23, 3: 23},
       12: {2: 9, 4: 9, 5: 9, 6: 9, 7: 9},
       15: {1: 10, 3: 10, 4: 10, 5: 10, 6: 10},
       18: {1: 13, 2: 13, 3: 13},
       21: {1: 14, 2: 14, 3: 14}}

cells = []
gate = None
run_controls = {}
for rd in sorted(EXP.glob("runs/RUN-EXP-SIG-004-*")):
    raw = json.loads((rd / "raw.json").read_text())
    if raw.get("mode") == "gate":
        gate = {"run": rd.name, "gate": raw.get("gate")}
        for c in raw.get("cells", []):
            if c.get("kind") == "C3_t2_anchor":
                gate["c3_t2_anchor"] = {
                    "residual_pinned": c["v3_multiples_at_D4"]["residual_pinned"],
                    "residual_canonical": c["v3_multiples_at_D4"]["residual_canonical"]}
            if c.get("kind") == "C4a_rerun_check":
                gate["c4a_inrun_determinism_identical"] = c["identical"]
        continue
    if raw.get("kind") == "determinism_compare":
        run_controls[rd.name] = {"kind": "determinism_compare",
                                 "identical": raw.get("identical"),
                                 "cell": raw.get("cell"),
                                 "run_a": raw.get("run_a"), "run_b": raw.get("run_b")}
        continue
    run_controls[rd.name] = raw.get("controls")
    for c in raw.get("cells", []):
        if c.get("status") != "completed":
            cells.append({"run": rd.name, "n": c.get("n"), "seed": c.get("seed"),
                          "arm": c.get("arm"), "status": c.get("status")})
            continue
        v3 = c["v3_multiples_at_D4"]
        cells.append({
            "run": rd.name, "n": c["n"], "seed": c["seed"], "arm": c["arm"],
            "status": "completed",
            "standard": c["filter"]["standard"],
            "filter": c["filter"],
            "d3_deficit": c["D3"]["deficit"], "d3_extra": c["D3"]["extra"],
            "d4_deficit": c["D4"]["deficit"], "d4_extra": c["D4"]["extra"],
            "d4_rankK": c["D4"]["rankK"],
            "n_mult_images": v3["n_mult_images"],
            "rank_mod_K4_pinned": v3["rank_mod_K4_pinned"],
            "rank_mod_K4_canonical": v3["rank_mod_K4_canonical"],
            "union_crosscheck_rank": v3["union_crosscheck_rank"],
            "residual_pinned": v3["residual_pinned"],
            "residual_canonical": v3["residual_canonical"],
            "delta": v3["delta_corrected_minus_pinned"],
            "exp_sig_002_anchor": OLD.get(c["n"], {}).get(c["seed"]),
            "controls": c["controls"],
        })

sem_std = [c for c in cells if c.get("arm") == "sem" and c.get("standard")
           and c.get("status") == "completed"]
series = {}
for n in (9, 12, 15, 18, 21):
    sub = sorted([c for c in sem_std if c["n"] == n], key=lambda c: c["seed"])
    series[str(n)] = {
        "seeds": [c["seed"] for c in sub],
        "residual_pinned_per_seed": [c["residual_pinned"] for c in sub],
        "residual_canonical_per_seed": [c["residual_canonical"] for c in sub],
        "d4_deficit_per_seed": [c["d4_deficit"] for c in sub],
        "d3_non_koszul_per_seed": [c["d3_extra"] for c in sub],
        "residual_pinned": sorted(set(c["residual_pinned"] for c in sub)),
        "residual_canonical": sorted(set(c["residual_canonical"] for c in sub)),
    }

corr = {n: series[str(n)]["residual_canonical"] for n in (9, 12, 15, 18, 21)}
old_s = {n: series[str(n)]["residual_pinned"] for n in (9, 12, 15, 18, 21)}
mono_corr = all(corr[a][0] < corr[b][0] for a, b in ((12, 15), (15, 18), (18, 21)))
mono_old = all(old_s[a][0] < old_s[b][0] for a, b in ((12, 15), (15, 18), (18, 21)))
inc = [corr[b][0] - corr[a][0] for a, b in ((12, 15), (15, 18), (18, 21))]

checks = {
    "continuity_holds_all_cells": all(c["delta"] >= 0 for c in cells
                                      if c.get("status") == "completed"),
    "union_crosscheck_matches_canonical_all_cells": all(
        c["union_crosscheck_rank"] == c["rank_mod_K4_canonical"]
        for c in cells if c.get("status") == "completed"),
    "pinned_reproduces_exp_sig_002_all_standard_sem": all(
        c["residual_pinned"] == c["exp_sig_002_anchor"] for c in sem_std),
    "null_residual_zero_all_null_cells": all(
        c["residual_canonical"] == 0 and c["residual_pinned"] == 0
        and c["d3_extra"] == 0 and c["d4_extra"] == 0
        for c in cells if c.get("arm") == "null"
        and c.get("status") == "completed"),
    "t2_8n_over_3_all_standard_sem_n_ge_12": all(
        c["d4_deficit"] == (8 * c["n"]) // 3 for c in sem_std if c["n"] >= 12),
    "d3_non_koszul_eq_1_all_standard_sem": all(
        c["d3_extra"] == 1 and c["d3_deficit"] == 1 for c in sem_std),
    "n9_d4_deficit_41_replicates": all(
        c["d4_deficit"] == 41 for c in sem_std if c["n"] == 9),
}

out = {
    "experiment": "EXP-SIG-004",
    "gate": gate,
    "run_controls": run_controls,
    "series": series,
    "corrected_series_n9_21": [corr[n][0] for n in (9, 12, 15, 18, 21)],
    "old_series_n9_21": [old_s[n][0] for n in (9, 12, 15, 18, 21)],
    "monotone_n12_21_corrected": mono_corr,
    "monotone_n12_21_old": mono_old,
    "corrected_increments_n12_21": inc,
    "n9_exception_persists": bool(corr[9][0] > corr[12][0]),
    "delta_per_size": {str(n): corr[n][0] - old_s[n][0] for n in (9, 12, 15, 18, 21)},
    "aggregate_checks": checks,
    "cells": cells,
}
(EXP / "summary.json").write_text(json.dumps(out, indent=1) + "\n")
print("corrected series (n=9..21):", out["corrected_series_n9_21"])
print("old series (n=9..21):      ", out["old_series_n9_21"])
print("delta per size:", out["delta_per_size"])
print("monotone 12..21 corrected:", mono_corr, "increments:", inc)
print("n9 exception persists:", out["n9_exception_persists"])
print("checks:", json.dumps(checks, indent=1))

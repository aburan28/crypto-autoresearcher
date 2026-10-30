"""Aggregate PTM-1 (ptm1-results.json) and PTM-2..PTM-5 (ptm-cells/*.json) into ptm-results.json, with the frozen
classification each object receives and pass/fail against the review plan's proves_too_much.failure_signature."""
import glob
import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import common as C  # noqa: E402

SIG = ("PTM-1, PTM-2 (at 1.15), PTM-3 and PTM-5 must be flagged, with the correct sign, at every powered cell tested, "
       "and PTM-1 must reach O-STRUCT through the pseudo-replication; at 1.10 the flag rate across tested cells must be "
       "at least the 0.95 the design claims, or the shortfall localizes the cells where a 10% departure of H1 can hide. "
       "On PTM-4 the instrument is expected to read null; the inference passes only if it refuses to conclude anything "
       "about label-describability or membership predicates from a null.")


def main():
    p1 = json.load(open(os.path.join(C.OUT, "ptm1-results.json")))
    cells = {}
    for f in sorted(glob.glob(os.path.join(C.OUT, "ptm-cells", "*.json"))):
        d = json.load(open(f))
        cells[d["cell"]] = d
    objs = {}
    for cid, d in cells.items():
        for o, runs in d["objects"].items():
            objs.setdefault(o, []).append((cid, d, runs))

    def summarize(o, want_sign=None, must_flag=False):
        rows, ok = [], True
        for cid, d, runs in objs.get(o, []):
            for r in runs:
                row = {"cell": cid, "curves": d["curves"], "n": d["n"], "mu_per_set": d["mu_per_set"], "rep": r["rep"],
                       "kappa": r["kappa"], "z": r["z"], "ci95": r["ci95"], "cls": r["cls"], "sign": r["sign"],
                       "labels_sha256": r["labels_sha256"]}
                for k in ("realized_internal_fraction", "curves_with_ap", "m_range", "k_rule", "k_range"):
                    if k in r:
                        row[k] = r[k]
                if must_flag:
                    row["pass"] = r["cls"] == "flagged" and (want_sign is None or r["sign"] == want_sign)
                    ok = ok and row["pass"]
                rows.append(row)
        return rows, ok

    out = {"task": "TASK-20261029-11526b", "plan_failure_signature": SIG,
           "inputs": ["outputs/ptm1-results.json"] + sorted("outputs/ptm-cells/" + os.path.basename(f)
                                                            for f in glob.glob(os.path.join(C.OUT, "ptm-cells", "*.json"))),
           "cells_tested_ptm2_to_ptm5": sorted(cells),
           "cell_selection": ("per bits, the lowest-power r at n = 256 and at n = 4096 (largest sigma_kappa in "
                              "power-table.json): b20-r3-n256, b24-r1-n256, b28-r2-n256, b20-r2-n4096, b24-r1-n4096, "
                              "b28-r3-n4096; plus the lowest-power cell overall (b28-r1-n512) and the widest-interval cell "
                              "(b28-r1-n256)"),
           "objects": {}}
    R0 = p1["R0_all_curves_no_replication"]
    R1 = p1["R1_even_discovery_odd_pseudo_replication"]
    out["objects"]["PTM-1"] = {
        "construction": p1["construction"], "cells": "all 44 powered cells (R0); 45 half-cells (R1)",
        "R0": {"flagged": R0["flagged_cells"], "powered": R0["powered_cells"], "correct_sign": R0["flagged_with_correct_sign"],
               "min_kappa": R0["min_kappa_powered"], "min_z": R0["min_z_powered"],
               "reading_own": R0["own"]["reading"]["outcome"], "headline_own": R0["own"]["reading"]["headline"],
               "reading_producer": R0["producer"]["outcome"], "headline_producer": R0["producer"]["headline"],
               "class_agreement": R0["class_agreement_own_vs_producer"]},
        "R1": {"flagged": len(R1["own"]["reading"]["flagged"]), "surviving": len(R1["own"]["reading"]["surviving"]),
               "discovery_underpowered": R1["discovery_underpowered_cells"], "discovery_invalid": R1["discovery_invalid_cells"],
               "reading_own": R1["own"]["reading"]["outcome"], "headline_own": R1["own"]["reading"]["headline"],
               "reading_producer": R1["producer"]["outcome"], "headline_producer": R1["producer"]["headline"],
               "class_agreement": R1["class_agreement_own_vs_producer"]},
        "pass": (R0["flagged_cells"] == R0["powered_cells"] == R0["flagged_with_correct_sign"]
                 and R1["own"]["reading"]["outcome"] == "O-STRUCT" and R1["producer"]["outcome"] == "O-STRUCT")}
    for o, sign in (("PTM-2@0.15", "+"), ("PTM-5s", "+"), ("PTM-5h", "+")):
        rows, ok = summarize(o, sign, must_flag=True)
        out["objects"][o] = {"runs": rows, "all_flagged_correct_sign": ok, "pass": ok and len(rows) > 0}
    rows, _ = summarize("PTM-3", "-", must_flag=True)
    for (cid, d, runs) in objs.get("PTM-3", []):
        for r, row in zip(runs, [x for x in rows if x["cell"] == cid]):
            row["pilot_note"] = r.get("pilot_note")
            row["kappa_counting_floor"] = r.get("kappa_counting_floor")
            row["built_as_specified"] = r["kappa"] <= 0.90
            if not row["built_as_specified"]:
                row["k_rule"] = "k = n (kappa = 0.85 not constructible; see pilot_note)"
                row.pop("pass", None)
    spec = [r for r in rows if r["built_as_specified"]]
    out["objects"]["PTM-3"] = {
        "runs": rows, "built_as_specified_at": [r["cell"] for r in spec],
        "not_built_as_specified_at": {r["cell"]: r["pilot_note"] for r in rows if not r["built_as_specified"]},
        "all_built_flagged_correct_sign": all(r["pass"] for r in spec),
        "substitutes_read": {r["cell"]: [r["cls"], r["kappa"], r["z"]] for r in rows if not r["built_as_specified"]},
        "pass": all(r["pass"] for r in spec) and len(spec) > 0,
        "pass_scope": ("pass at every cell where the specified object exists; at b20-r2-n4096 no set of 4096 residues "
                       "can have kappa below the counting floor 0.912, and at b24-r1-n4096 the specified greedy saturates "
                       "near 0.95; the substitute deficit sets (kappa 0.990 and 0.954, |z| 466 and 534) lie inside the "
                       "5% null margin and are read null, a margin property, not a sensitivity defect")}
    rows, _ = summarize("PTM-2@0.10")
    nflag = sum(r["cls"] == "flagged" for r in rows)
    per_cell = {}
    for r in rows:
        pc = per_cell.setdefault(r["cell"], {"runs": 0, "flagged": 0, "intermediate": 0, "null": 0, "kappa": []})
        pc["runs"] += 1
        pc[r["cls"]] = pc.get(r["cls"], 0) + 1
        pc["kappa"].append(r["kappa"])
    for pc in per_cell.values():
        pc["mean_kappa"] = sum(pc["kappa"]) / len(pc["kappa"])
        pc["flag_rate"] = pc["flagged"] / pc["runs"]
        del pc["kappa"]
    out["objects"]["PTM-2@0.10"] = {
        "runs": rows, "flag_rate": nflag / len(rows) if rows else None, "realizations": len(rows),
        "read_null_count": sum(r["cls"] == "null" for r in rows), "per_cell": per_cell,
        "pass_design_claim_0.95": (nflag / len(rows) >= 0.95) if rows else None,
        "note": ("kappa_true of the construction is 1 + f(1 - eps): eps ~ 0.04 at b20 n=4096 (dense regime: the fill "
                 "cannot land on AP labels, removing 3+1 cross coincidences in proportion to n/p), ~0 elsewhere; the "
                 "realized AP-internal fraction is 0.100 in every run.")}
    for o in ("PTM-4a", "PTM-4b", "PTM-4c"):
        rows, _ = summarize(o)
        out["objects"][o] = {"runs": rows, "classes": {c: sum(r["cls"] == c for r in rows) for c in sorted({r["cls"] for r in rows})},
                             "instrument_reads_null_at": [r["cell"] for r in rows if r["cls"] == "null"],
                             "instrument_does_not_read_null_at": [r["cell"] for r in rows if r["cls"] != "null"]}
    nulls_4 = out["objects"]["PTM-4a"]["instrument_reads_null_at"] + out["objects"]["PTM-4c"]["instrument_reads_null_at"]
    out["objects"]["PTM-4_inference"] = {
        "label_describable_objects_read_null": len(nulls_4),
        "inference_sentence_tested": ("decision_impact.on_positive: 'the reading is a scoped closure of label-describable "
                                      "rank <= 3 log-GAP bases' and 'the implicit-membership route of KN-OPEN-020 ... is "
                                      "then not opened by a label predicate at these sizes'"),
        "pass": False if nulls_4 else None,
        "finding": ("The frozen instrument returns the null class on label-describable objects (PTM-4a: membership in L "
                    "is decided by chi(f(x)); PTM-4c: membership decided by one inversion and one comparison, a "
                    "polynomial-time label predicate at every p). A null reading therefore cannot license any statement "
                    "about label-describability or membership predicates; the two sentences prove too much.")}
    cons = {
        "PTM-2@0.10": "label AP x0 + k w (x0, w uniform; first m labels in L) + n - m uniform labels of L; m per curve by error diffusion so cumulative AP-internal C tracks 0.10 x cumulative recorded null mean (m = 0 allowed); 8 realizations per cell",
        "PTM-2@0.15": "as PTM-2@0.10 with f = 0.15; 2 realizations per cell",
        "PTM-3": "uniform (n + k)-subset of L; exact greedy removal (label in most coincidences, incremental bookkeeping verified by recount) of k labels; k per curve by error diffusion toward 0.85 x null mean (mu < 100) or fixed per cell by pilot on curve 0 (doubling k from n/16 to n, log-linear interpolation); first-version pilot (secant on curves 0-1) at b20-r3-n256",
        "PTM-4a": "uniform n-subset of L, reviewer stream",
        "PTM-4b": "x0 g^k, g a primitive root mod p (reviewer stream), k = 0, 1, ..., first n terms in L",
        "PTM-4c": "x = k^-1 mod p for k = t, t+1, ... (t uniform), first n in L",
        "PTM-5s": "uniform n-subset of L inside [t, t + 4n) mod p",
        "PTM-5h": "uniform n-subset of L inside [t, t + floor(p/2)) mod p",
        "common": "every set: exactly n distinct labels of L (checked); counted exactly by the reviewer kernel; read against the RECORDED null arm of the cell (M, V from 20 recorded null counts per curve, factor 1.05); class by the frozen first-match rules with the recorded plant recovery; 2000-resample curve-cluster bootstrap with a reviewer seed; RNG streams sha256('TASK-20261029-11526b|<object>|<cell>|<c>|<rep>'); label-set and count sha256 per run in ptm-cells/<cell>.json"}
    for o, txt in cons.items():
        if o in out["objects"]:
            out["objects"][o]["construction"] = txt
    out["construction_common"] = cons["common"]
    out["summary"] = {o: v.get("pass") for o, v in out["objects"].items() if "pass" in v}
    C.write_json("ptm-results.json", out, sig=6)
    print(json.dumps(out["summary"]), out["objects"]["PTM-2@0.10"]["flag_rate"], out["objects"]["PTM-2@0.10"]["per_cell"])
    for o in ("PTM-4a", "PTM-4b", "PTM-4c"):
        print(o, out["objects"][o]["classes"], out["objects"][o]["instrument_does_not_read_null_at"])


if __name__ == "__main__":
    main()

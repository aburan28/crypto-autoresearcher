"""PTM-1: the recorded planted label AP routed through the full frozen classifier, and through the
replication rule with an even/odd pseudo-replication (no new curves; the replication seed block is never touched).

In memory only: every main-census record keeps its null arm and plant arm; its gap_C (and gap_D) is replaced by
plant_C (plant_D). Known false: these sets are additively structured (a true label AP of m labels with internal
count >= 0.30 x the curve's null mean, plus uniform fill).

Routes, each with the reviewer's own implementation of the frozen rules (common.classify plus the gate and
reading below) and with the producer's bound analyze path run.analyze_records called in-process:
  R0  all main curves, replication file empty (as recorded at analyze-final): the frozen reading for flagged
      cells without replication;
  R1  discovery = even-index curves, pseudo-replication = odd-index curves, each half renumbered 0..h-1 with
      h = min(#even, #odd) planned curves per cell (the rule's completeness check is applied to the half).
Producer outputs go to outputs/ only. Writes outputs/ptm1-results.json, outputs/ptm1-producer-R0.json,
outputs/ptm1-producer-R1.json.
"""
import copy
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import math  # noqa: E402
import statistics  # noqa: E402

import numpy as np  # noqa: E402

import common as C  # noqa: E402

IMPL = os.path.join(C.EXPD, "implementation")


def own_cell(rs, arm="gap_C", boot_label=""):
    g, m, s2, nulls = C.curve_arrays(rs, arm)
    st = C.cell_stats_np(g, m, s2)
    ci, _ = C.bootstrap_ci(g, m, 2000, C.review_np_rng("ptm1-boot", boot_label))
    gp, mp, sp, _ = C.curve_arrays(rs, "plant_C")
    pst = C.cell_stats_np(gp, mp, sp)
    plant_ok = all(r["plant_feasible"] for r in rs) and pst["kappa"] >= 1.15 and pst["z"] > 4
    o = nulls[:, 1:]
    zc = float((nulls[:, 0] - o.mean(axis=1)).sum() / math.sqrt(o.var(axis=1, ddof=1).sum() * (1 + 1 / 19)))
    cls = C.classify(st["M"], st["kappa"], st["z"], ci, plant_ok)
    return {"curves": len(rs), "M": st["M"], "kappa": st["kappa"], "z": st["z"], "ci95": ci, "cls": cls,
            "z_cal": zc, "powered": st["M"] >= C.TARGET}


def own_reading(rows, rep_rows):
    zc = [r["z_cal"] for r in rows.values() if r.get("powered")]
    sd = statistics.pstdev(zc) if len(zc) > 1 else None
    mean = statistics.fmean(zc) if zc else None
    cal_pass = sd is not None and 0.75 <= sd <= 1.25 and abs(mean) <= 0.35
    classes = [r["cls"] for r in rows.values()]
    frac = sum(c in ("null", "flagged", "intermediate") for c in classes) / 45
    surv, pend = [], []
    for cid, r in rows.items():
        if r["cls"] != "flagged":
            continue
        rp = rep_rows.get(cid)
        if rp is None or rp.get("status") != "complete":
            pend.append(cid)
            continue
        same = (rp["kappa"] - 1) * (r["kappa"] - 1) > 0
        rp["survives"] = bool(same and abs(rp["z"]) > 3 and abs(rp["kappa"] - 1) >= 0.05)
        if rp["survives"]:
            surv.append(cid)
    if not cal_pass or frac < 0.5:
        out = "O-INVALID"
    elif surv:
        out = "O-STRUCT"
    elif pend:
        out = "O-PENDING-REPLICATION"
    elif all(c == "null" for c in classes if c in ("null", "flagged", "intermediate")) and frac >= 0.8:
        out = "O-NULL"
    else:
        out = "O-MIXED"
    head = {"O-STRUCT": "FALSIFY_SCOPED", "O-INVALID": "NOT_EVIDENCE", "O-NULL": "SUPPORT_SCOPED"}.get(out, "INCONCLUSIVE")
    return {"calibration": {"n": len(zc), "mean": mean, "sd": sd, "pass": cal_pass}, "fraction_valid": frac,
            "flagged": [c for c, r in rows.items() if r["cls"] == "flagged"], "surviving": surv, "pending": pend,
            "outcome": out, "headline": head}


def swap(rec):
    r = copy.deepcopy(rec)
    if r["status"] == "ok":
        r["gap_C"], r["gap_D"] = r["plant_C"], r["plant_D"]
    return r


def main():
    recs = [swap(r) for r in C.load_jobs()]
    design = C.load_design()["toy_cells"]
    by = {}
    for r in recs:
        by.setdefault(r["cell"], []).append(r)
    # ---------------- R0 (own)
    rows0 = {}
    for d in design:
        ok = sorted([r for r in by[d["cell"]] if r["status"] == "ok"], key=lambda r: r["c"])
        if len(ok) < d["n_curves"]:
            rows0[d["cell"]] = {"cls": "invalid", "curves": len(ok)}
            continue
        rows0[d["cell"]] = own_cell(ok, boot_label=d["cell"] + "|R0")
    read0 = own_reading(rows0, {})
    # ---------------- R1 (own)
    rows1, rep1, half_design, main_half, rep_half = {}, {}, [], [], []
    for d in design:
        allr = sorted(by[d["cell"]], key=lambda r: r["c"])
        ev = [r for r in allr if r["c"] % 2 == 0]
        od = [r for r in allr if r["c"] % 2 == 1]
        h = min(sum(1 for r in allr if r["c"] % 2 == 0 and r["c"] < d["n_curves"]),
                sum(1 for r in allr if r["c"] % 2 == 1 and r["c"] < d["n_curves"]))
        evh = [dict(r, c=i, block="main") for i, r in enumerate(ev[:h])]
        odh = [dict(r, c=i, block="rep") for i, r in enumerate(od[:h])]
        half_design.append(dict(d, n_curves=h))
        main_half += evh
        rep_half += odh
        evok = [r for r in evh if r["status"] == "ok"]
        odok = [r for r in odh if r["status"] == "ok"]
        if len(evok) < h:
            rows1[d["cell"]] = {"cls": "invalid", "curves": len(evok), "half_planned": h}
            continue
        rows1[d["cell"]] = own_cell(evok, boot_label=d["cell"] + "|R1-even")
        rows1[d["cell"]]["half_planned"] = h
        if rows1[d["cell"]]["cls"] == "flagged":
            if len(odok) < h:
                rep1[d["cell"]] = {"status": "incomplete", "curves": len(odok)}
            else:
                rr = own_cell(odok, boot_label=d["cell"] + "|R1-odd")
                rep1[d["cell"]] = {"status": "complete", "curves": rr["curves"], "kappa": rr["kappa"], "z": rr["z"]}
    read1 = own_reading(rows1, rep1)
    # ---------------- producer path in-process
    sys.path.insert(0, IMPL)
    import run  # noqa: E402  (bound analyze path; called in-process, writes nothing)
    prod0 = run.analyze_records(design, recs, [], "final")
    prod1 = run.analyze_records(half_design, main_half, rep_half, "final")
    for name, an in (("ptm1-producer-R0.json", prod0), ("ptm1-producer-R1.json", prod1)):
        slim = {k: v for k, v in an.items() if k != "cells"}
        slim["cells"] = [{k: c.get(k) for k in ("cell", "cls", "curves", "kappa", "z", "ci95", "plant_kappa", "plant_z",
                                                 "powered", "replication")} for c in an["cells"]]
        C.write_json(name, slim, sig=8)
    agree0 = all(prod0["cells"][i]["cls"] == rows0[d["cell"]]["cls"] for i, d in enumerate(design))
    agree1 = all(prod1["cells"][i]["cls"] == rows1[d["cell"]]["cls"] for i, d in enumerate(design))
    powered0 = [c for c, r in rows0.items() if r.get("powered")]
    flagged0 = [c for c, r in rows0.items() if r["cls"] == "flagged"]
    out = {
        "task": "TASK-20261029-11526b", "object": "PTM-1", "method": __doc__.strip(),
        "inputs": [C.rel(C.JOBS), C.rel(C.DESIGN), C.rel(os.path.join(IMPL, "run.py")) + " (analyze_records, in-process)"],
        "construction": "gap arm := recorded plant arm (plant_C, plant_D) in every ok main-census record; no new set built",
        "known_false_because": "the planted sets contain a true label AP with internal coincidences >= 0.30 x the null mean",
        "R0_all_curves_no_replication": {
            "own": {"cells": {c: {k: r.get(k) for k in ("cls", "curves", "kappa", "z", "ci95")} for c, r in rows0.items()},
                    "reading": read0},
            "producer": {"outcome": prod0["outcome"], "headline": prod0["headline"], "flagged": len(prod0["flagged_cells"]),
                         "reading_note": prod0["reading_note"],
                         "replication_status": sorted({c["replication"]["status"] for c in prod0["cells"] if c.get("replication")})},
            "class_agreement_own_vs_producer": agree0,
            "powered_cells": len(powered0), "flagged_cells": len(flagged0),
            "flagged_with_correct_sign": sum(1 for c in flagged0 if rows0[c]["kappa"] > 1),
            "powered_not_flagged": [c for c in powered0 if c not in flagged0],
            "min_kappa_powered": min(rows0[c]["kappa"] for c in powered0),
            "min_z_powered": min(rows0[c]["z"] for c in powered0)},
        "R1_even_discovery_odd_pseudo_replication": {
            "own": {"cells": {c: {k: r.get(k) for k in ("cls", "curves", "half_planned", "kappa", "z")} for c, r in rows1.items()},
                    "replication": rep1, "reading": read1},
            "producer": {"outcome": prod1["outcome"], "headline": prod1["headline"], "flagged": len(prod1["flagged_cells"]),
                         "surviving": [c["cell"] for c in prod1["cells"] if c.get("replication") and c["replication"].get("survives")],
                         "replication_status": {c["cell"]: c["replication"]["status"] for c in prod1["cells"] if c.get("replication")}},
            "class_agreement_own_vs_producer": agree1,
            "discovery_underpowered_cells": [c for c, r in rows1.items() if r["cls"] == "inconclusive_underpowered"],
            "discovery_invalid_cells": [c for c, r in rows1.items() if r["cls"] == "invalid"]},
    }
    C.write_json("ptm1-results.json", out, sig=7)
    print("R0 own", read0["outcome"], read0["headline"], len(flagged0), "of", len(powered0), "| producer", prod0["outcome"], prod0["headline"], agree0)
    print("R1 own", read1["outcome"], read1["headline"], len(read1["flagged"]), "surv", len(read1["surviving"]), "| producer", prod1["outcome"], prod1["headline"], len(out["R1_even_discovery_odd_pseudo_replication"]["producer"]["surviving"]), agree1)
    print("underpowered halves", out["R1_even_discovery_odd_pseudo_replication"]["discovery_underpowered_cells"])
    print("min kappa/z", out["R0_all_curves_no_replication"]["min_kappa_powered"], out["R0_all_curves_no_replication"]["min_z_powered"])


if __name__ == "__main__":
    main()

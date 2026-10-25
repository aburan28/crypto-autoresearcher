"""Archived vs legacy-rerun vs repaired-rerun extraction for EXP-SEMAEV-93d5cc.

``extract(cell, source)`` reads one source of a cell (``archived`` from the
archived run directories, or an arm directory) into the same flat summary;
``compare(cell, run_dir)`` builds the frozen per-cell table: the three
summaries, the CTRL-LEGACY-REPRO verdict (legacy rerun vs archive) and the
recorded-conclusion fields with their per-arm values.  Pure reads; arithmetic
only on recorded values.
"""
from __future__ import annotations

import json
from collections import Counter
from pathlib import Path

HERE = Path(__file__).resolve().parent
REPO = HERE.parents[2]
ICINV_RUN = REPO / "experiments/EXP-ICINV-e0cd8f/runs/RUN-ICINV-e0cd8f-m3class"
FIB_RUNS = REPO / "experiments/EXP-FIB-001/runs"
MTIC_RUNS = REPO / "experiments/EXP-MTIC-001/runs"
COUNT_TOLERANCE = 2  # frozen: budget-truncated counts may differ by <= 2 (cap jitter)
M4_FIELDS = ("s4_support", "singular_locus_dim", "singular_locus_degree",
             "singular_locus_is_unit_ideal")


def _load(path: Path):
    return json.loads(path.read_text())


# ------------------------------------------------------------------- ICINV
def _icinv_records(source):
    if source == "archived":
        out = {}
        for set_name, fname in (("control", "control-set-invariants.json"),
                                ("class", "per-curve-invariants.json")):
            for i, c in enumerate(_load(ICINV_RUN / fname)["curves"]):
                out[(set_name, i, "base")] = c["m4"]
                out[(set_name, i, "gauge")] = c["gauge"]["m4"]
        return out
    doc = _load(Path(source) / "m4-records.json")
    return {(r["set"], r["index"], r["role"]): r["m4"] for r in doc["records"]}


def _icinv_summary(recs):
    tup = {k: tuple(v.get(f) for f in M4_FIELDS) for k, v in recs.items()}
    out = {"n_records": len(recs),
           "n_error": sum(1 for v in recs.values() if v.get("returncode") != 0),
           "max_wall_seconds": max((v.get("wall_seconds") or 0) for v in recs.values())}
    for set_name in ("control", "class"):
        sub = [t for k, t in tup.items() if k[0] == set_name]
        out[f"{set_name}_s4_support_counts"] = dict(sorted(Counter(t[0] for t in sub).items(),
                                                           key=lambda kv: str(kv[0])))
        out[f"{set_name}_singular_locus_dim_degree_counts"] = {
            f"{d}/{g}": n for (d, g), n in sorted(Counter((t[1], t[2]) for t in sub).items(),
                                                   key=lambda kv: str(kv[0]))}
        out[f"{set_name}_unit_ideal_count"] = sum(1 for t in sub if t[3])
    gauge_agree = sum(1 for (s, i, r), t in tup.items()
                      if r == "base" and tup.get((s, i, "gauge")) == t)
    out["gauge_m4_agree"] = gauge_agree
    out["gauge_m4_pairs"] = sum(1 for k in tup if k[2] == "base")
    cls = {t for k, t in tup.items() if k[0] == "class"}
    ctl = {t for k, t in tup.items() if k[0] == "control"}
    out["class_m4_tuple_distinct"] = len(cls)
    out["class_and_control_m4_tuple_sets_equal"] = cls == ctl
    return out, tup


# --------------------------------------------------------------------- FIB
def _fib_measure(raw):
    out = {}
    for cid, pc in raw["per_curve"].items():
        meas = pc["measurements"]
        solved = [m for m in meas if not m["capped"]]
        costs = sorted(m["cost_seconds"] for m in meas)
        out[cid] = {"n_measured": pc["n_measured"], "n_capped": pc["n_capped"],
                    "n_solved": len(solved),
                    "resource_exhaustion": pc["resource_exhaustion"],
                    "stop_reason": pc["stop_reason"],
                    "median_cost_seconds": costs[len(costs) // 2] if costs else None,
                    "n_trivial_ideal": sum(1 for m in solved if m["is_trivial_ideal"]),
                    "basis_size_counts": dict(Counter(str(m["groebner_basis_size"]) for m in solved)),
                    "basis_max_degree_counts": dict(Counter(str(m["groebner_basis_max_degree"]) for m in solved)),
                    "per_target": [(m["target_index"], m["capped"], m["groebner_basis_size"],
                                    m["groebner_basis_max_degree"], m["is_trivial_ideal"])
                                   for m in meas]}
    return out


def _fib_decision_summary(summary6c, raw6c, decision):
    rho = {}
    for cid, v in (raw6c.get("per_curve") or {}).items():
        corr = v.get("correlation") if isinstance(v, dict) else None
        if isinstance(corr, dict):
            rho[cid] = {k: corr.get(k) for k in ("rho_s", "p_value", "n", "null_band_95_half_width")}
    return {"correlation_gate_pass_overall": summary6c.get("correlation_gate_pass_overall"),
            "correlation_gate_curves_passing": summary6c.get("correlation_gate_curves_passing"),
            "per_curve_status": summary6c.get("per_curve_status"),
            "CTRL-LABEL-SHUFFLE_pass": summary6c.get("CTRL-LABEL-SHUFFLE_pass"),
            "per_curve_correlation": rho, **(decision or {})}


# -------------------------------------------------------------------- MTIC
def _mtic_descent(raw):
    out = {}
    for bits, st in raw["metrics"]["instances"].items():
        out[bits] = {k: st[k] for k in ("n_targets", "n_attempted", "n_capped", "n_trivial_ideal",
                                        "n_cancelled_by_budget", "n_aux_decomposition_found",
                                        "ideal_enumeration_disagreements")}
        out[bits]["t_desc_median_seconds"] = st["t_desc_seconds"]["median"]
        out[bits]["t_desc_uncapped_median_seconds"] = st["t_desc_seconds_uncapped_only"]["median"]
        out[bits]["n_uncapped"] = st["n_attempted"] - st["n_capped"]
        out[bits]["per_target"] = [(r["index"], r["capped"], r["basis_size"], r["basis_max_degree"],
                                    r["trivial_ideal"]) for r in raw["raw"]["per_target"][bits]]
    return out


def _mtic_010b(raw):
    m = raw["metrics"]
    out = {"decision_matrix": {}, "ablation": {}}
    for bits, d in m["decision_matrix"].items():
        out["decision_matrix"][bits] = {
            "t_desc_seconds_median": d["t_desc_seconds_median"],
            "t_desc_n_attempted": d["t_desc_n_attempted"], "t_desc_n_capped": d["t_desc_n_capped"],
            "n_uncensored_solves": d["n_uncensored_solves"],
            "regime_per_accounting": d["regime_per_accounting"],
            "below_frontier_observed_any_accounting": d["below_frontier_observed_any_accounting"],
            "K_star_per_accounting": {k: v.get("K_star") for k, v in d["accountings"].items()
                                      if isinstance(v, dict) and "K_star" in v}}
    for kind, a in m["ablation"].items():
        out["ablation"][kind] = {k: a[k] for k in ("B", "t_desc_median_seconds", "t_desc_n_attempted",
                                                   "t_desc_n_capped", "K_star_per_accounting")}
    return out


# ---------------------------------------------------------------- dispatch
def _arm_dir(run_dir: Path, arm: str) -> Path:
    return Path(run_dir) / "arms" / arm


def extract(cell: str, source):
    """source: 'archived' or an arm directory."""
    arch = source == "archived"
    if cell == "icinv-m4":
        return _icinv_summary(_icinv_records(source))
    if cell in ("fib-004", "fib-005"):
        rid = {"fib-004": "RUN-FIB-004", "fib-005": "RUN-FIB-005"}[cell]
        base = FIB_RUNS if arch else Path(source) / "runs"
        return _fib_measure(_load(base / rid / "raw.json"))
    if cell == "fib-decision":
        base = FIB_RUNS if arch else Path(source) / "runs"
        if arch:  # archived gate values as recorded by resume2 (execution-report.yaml)
            import yaml
            rep = yaml.safe_load((FIB_RUNS.parent / "execution-report.yaml").read_text())
            ratios = rep["predictor_cost_ratios"]
            cost_curves = [c for c, r in ratios.items() if r is not None and r <= 0.1]
            decision = {"predictor_cost_ratios": ratios, "cost_gate_curves": cost_curves,
                        "predictor_cost_gate_pass": len(cost_curves) >= 3,
                        "gate_pass": rep["gate_pass"],
                        "run_fib_008_outcome": "would_run" if rep["gate_pass"] else "cancelled_by_gate"}
        else:
            decision = _load(Path(source) / "decision.json")
        return _fib_decision_summary(_load(base / "RUN-FIB-006C" / "summary.json"),
                                     _load(base / "RUN-FIB-006C" / "raw.json"), decision)
    rid = {"mtic-007": "RUN-MTIC-007", "mtic-008": "RUN-MTIC-008", "mtic-010b": "RUN-MTIC-010b"}[cell]
    base = MTIC_RUNS if arch else Path(source) / "out-root" / "runs"
    raw = _load(base / rid / "raw.json")
    return _mtic_010b(raw) if cell == "mtic-010b" else _mtic_descent(raw)


def _prefix_equal(a, b):
    """Per-target solver tuples equal on the targets present in both lists."""
    bi = {t[0]: t for t in b}
    common = [t for t in a if t[0] in bi]
    return all(bi[t[0]] == t for t in common), len(common)


def legacy_control(cell: str, arch, leg) -> dict:
    """CTRL-LEGACY-REPRO, frozen per cell (specification controls)."""
    checks = {}
    if cell == "icinv-m4":
        (_, ta), (_, tl) = arch, leg
        same = sum(1 for k, v in ta.items() if tl.get(k) == v)
        checks["records_equal"] = f"{same}/{len(ta)}"
        ok = same == len(ta) == len(tl)
    elif cell in ("fib-004", "fib-005"):
        ok = True
        for cid, a in arch.items():
            l = leg[cid]
            eq, n = _prefix_equal(a["per_target"], l["per_target"])
            c = {"per_target_equal_on_common": eq, "n_common": n,
                 "resource_exhaustion_equal": a["resource_exhaustion"] == l["resource_exhaustion"],
                 "n_measured_diff": l["n_measured"] - a["n_measured"],
                 "all_capped_pattern_equal": (a["n_capped"] == a["n_measured"]) == (l["n_capped"] == l["n_measured"])}
            c["pass"] = (eq and c["resource_exhaustion_equal"] and c["all_capped_pattern_equal"]
                         and abs(c["n_measured_diff"]) <= COUNT_TOLERANCE)
            ok = ok and c["pass"]
            checks[cid] = c
    elif cell == "fib-decision":
        keys = ("correlation_gate_pass_overall", "correlation_gate_curves_passing", "per_curve_status")
        for k in keys:
            checks[k] = arch.get(k) == leg.get(k)
        ok = all(checks.values())
    elif cell in ("mtic-007", "mtic-008"):
        ok = True
        for bits, a in arch.items():
            l = leg[bits]
            eq, n = _prefix_equal(a["per_target"], l["per_target"])
            c = {"per_target_equal_on_common": eq, "n_common": n,
                 "n_attempted_diff": l["n_attempted"] - a["n_attempted"],
                 "uncapped_equal": a["n_uncapped"] == l["n_uncapped"]}
            c["pass"] = eq and c["uncapped_equal"] and abs(c["n_attempted_diff"]) <= COUNT_TOLERANCE
            ok = ok and c["pass"]
            checks[bits] = c
    else:  # mtic-010b
        ok = True
        for bits, a in arch["decision_matrix"].items():
            l = leg["decision_matrix"][bits]
            c = {"regime_equal": a["regime_per_accounting"] == l["regime_per_accounting"],
                 "K_star_equal": a["K_star_per_accounting"] == l["K_star_per_accounting"],
                 "n_uncensored_equal": a["n_uncensored_solves"] == l["n_uncensored_solves"]}
            c["pass"] = all(c.values())
            ok = ok and c["pass"]
            checks[f"decision_matrix.{bits}"] = c
        for kind, a in arch["ablation"].items():
            l = leg["ablation"][kind]
            c = {"K_star_equal": a["K_star_per_accounting"] == l["K_star_per_accounting"],
                 "n_capped_eq_attempted_pattern": (a["t_desc_n_capped"] == a["t_desc_n_attempted"])
                 == (l["t_desc_n_capped"] == l["t_desc_n_attempted"]),
                 "n_attempted_diff": l["t_desc_n_attempted"] - a["t_desc_n_attempted"]}
            c["pass"] = (c["K_star_equal"] and c["n_capped_eq_attempted_pattern"]
                         and abs(c["n_attempted_diff"]) <= COUNT_TOLERANCE)
            ok = ok and c["pass"]
            checks[f"ablation.{kind}"] = c
    return {"pass": bool(ok), "checks": checks}


def conclusion_fields(cell: str, s) -> dict:
    """The recorded-conclusion fields (specification ``conclusion_rules``)."""
    if cell == "icinv-m4":
        s = s[0]
        return {"m4_s4_support_values": sorted({*s["control_s4_support_counts"], *s["class_s4_support_counts"]}, key=str),
                "m4_singular_locus_dim_degree_values": sorted({*s["control_singular_locus_dim_degree_counts"],
                                                              *s["class_singular_locus_dim_degree_counts"]}),
                "gauge_m4_all_agree": s["gauge_m4_agree"] == s["gauge_m4_pairs"],
                "class_and_control_m4_tuple_sets_equal": s["class_and_control_m4_tuple_sets_equal"]}
    if cell in ("fib-004", "fib-005"):
        return {cid: {"resource_exhaustion": v["resource_exhaustion"],
                      "all_measured_capped": v["n_capped"] == v["n_measured"]} for cid, v in s.items()}
    if cell == "fib-decision":
        return {k: s.get(k) for k in ("correlation_gate_pass_overall", "correlation_gate_curves_passing",
                                      "per_curve_status", "predictor_cost_gate_pass", "gate_pass",
                                      "run_fib_008_outcome")}
    if cell in ("mtic-007", "mtic-008"):
        return {b: {"all_attempted_capped": v["n_capped"] == v["n_attempted"],
                    "t_desc_median_at_cap": v["t_desc_median_seconds"] == 60.0} for b, v in s.items()}
    return {**{f"regime.{b}": v["regime_per_accounting"] for b, v in s["decision_matrix"].items()},
            **{f"K_star.{b}": v["K_star_per_accounting"] for b, v in s["decision_matrix"].items()},
            **{f"ablation_K_star.{k}": v["K_star_per_accounting"] for k, v in s["ablation"].items()}}


def _strip(cell, s):
    if cell == "icinv-m4":
        return s[0]
    if cell in ("fib-004", "fib-005"):
        return {cid: {k: v for k, v in d.items() if k != "per_target"} for cid, d in s.items()}
    if cell in ("mtic-007", "mtic-008"):
        return {b: {k: v for k, v in d.items() if k != "per_target"} for b, d in s.items()}
    return s


def compare(cell: str, run_dir) -> dict:
    arch = extract(cell, "archived")
    leg = extract(cell, _arm_dir(run_dir, "legacy"))
    rep = extract(cell, _arm_dir(run_dir, "repaired"))
    out = {"cell": cell,
           "archived": _strip(cell, arch), "legacy": _strip(cell, leg), "repaired": _strip(cell, rep),
           "ctrl_legacy_repro": legacy_control(cell, arch, leg)}
    ca, cl, cr = (conclusion_fields(cell, x) for x in (arch, leg, rep))
    out["conclusion_fields"] = {"archived": ca, "legacy": cl, "repaired": cr}
    out["conclusion_changed_repaired_vs_archived"] = {k: cr.get(k) != v for k, v in ca.items()}
    out["conclusion_changed_repaired_vs_legacy"] = {k: cr.get(k) != v for k, v in cl.items()}
    if cell == "icinv-m4":
        tl, tr = leg[1], rep[1]
        out["records_differing_repaired_vs_legacy"] = sum(1 for k in tl if tl[k] != tr.get(k))
    return out

#!/usr/bin/env python3
"""Stage-2 leaf census for EXP-BINSTD-b94ec8 after Semaev m=4 export AMD.

Arms: 3 curves × {stable_V5, stable_V6, window_deg_5, window_deg_6}.
Per arm: 50 UNSAT + 20 planted SAT. Window arms use TRIMOSKA weill + WDSat;
stable (phi31_ker) arms use semaev_export + numpy conflict census.

Writes only under stage2/r3-semaev/ (prior stage2/ and r2-phi31ker/ immutable).
"""
from __future__ import annotations

import json
import random
import time
from pathlib import Path
from typing import Any

from curve import Curve
from gf2 import Field
from leaf_census import build_wdsat, median, numpy_conflict_census, run_wdsat
from phi31_ker import build_phi31_ker_bases
from semaev_export import descend_s4, export_instance
from trimoska_export import export_window_instance

M_ARITY = 4
UNSAT_TARGETS_PER_ARM = 50
PLANTED_SAT_PER_ARM = 20
RATIO_BAND = [0.8, 1.25]
WITHDRAWN_RATIO = 1.0 / 31.0


def _write_json(path: Path, obj: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    if path.exists():
        raise FileExistsError(f"refusing overwrite: {path}")
    path.write_text(json.dumps(obj, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def _plant_one(curve: Curve, V: list[int], rng: random.Random) -> dict[str, Any] | None:
    xs: list[int] = []
    pts = []
    for _ in range(M_ARITY - 1):
        x = V[rng.randrange(len(V))]
        P = curve.lift_x(x)
        if P is None:
            return None
        xs.append(x)
        pts.append(P)
    R = None
    for P in pts:
        R = curve.add(R, P)
    if R is None:
        return None
    return {"witness_x": xs, "R_x": R[0], "R_y": R[1]}


def _enumerate_V(basis: list[int]) -> list[int]:
    out = []
    for mask in range(1 << len(basis)):
        v = 0
        for i, b in enumerate(basis):
            if (mask >> i) & 1:
                v ^= b
        out.append(v)
    return out


def run_census(
    *,
    exp_root: Path,
    repo_root: Path,
    run_dir: Path,
    out_dir: Path,
    master_seed: int,
    amd_id: str,
    refine_dec: str,
    expand_dec: str,
    task_id: str,
) -> dict[str, Any]:
    t0 = time.time()
    out_dir.mkdir(parents=True, exist_ok=True)
    # Instance ANFs live under the run dir (not ledger stage2/) to avoid bloating
    # immutable stage artifacts; leaf-counts.jsonl carries the census rows.
    instances_dir = run_dir / "instances"
    instances_dir.mkdir(exist_ok=True)

    bases_path = exp_root / "stage1" / "curves-and-bases.json"
    phi_path = exp_root / "stage1" / "phi31-ker-bases.json"
    bases_doc = json.loads(bases_path.read_text(encoding="utf-8"))
    modulus = int(bases_doc["modulus"], 16)
    F = Field(modulus)
    n = F.n

    phi = build_phi31_ker_bases(seed_factor_index=0)
    if phi_path.exists():
        on_disk = json.loads(phi_path.read_text(encoding="utf-8"))
        if on_disk.get("kind") != "phi31_ker":
            raise RuntimeError("phi31-ker-bases.json corrupted")
    else:
        persist = json.loads(json.dumps(phi))
        for _n, meta in persist["bases"].items():
            meta.pop("basis", None)
        _write_json(phi_path, persist)

    basis_table: dict[str, dict[str, Any]] = {
        "stable_V5": {
            "kind": "phi31_ker",
            "l": 5,
            "basis": [int(h, 16) for h in phi["bases"]["stable_V5"]["basis_hex"]],
            "exporter": "semaev_export_python",
        },
        "stable_V6": {
            "kind": "phi31_ker",
            "l": 6,
            "basis": [int(h, 16) for h in phi["bases"]["stable_V6"]["basis_hex"]],
            "exporter": "semaev_export_python",
        },
        "window_deg_5": {
            "kind": "window_deg",
            "l": 5,
            "basis": [1 << i for i in range(5)],
            "exporter": "trimoska_weil_descent_c",
        },
        "window_deg_6": {
            "kind": "window_deg",
            "l": 6,
            "basis": [1 << i for i in range(6)],
            "exporter": "trimoska_weil_descent_c",
        },
    }

    curves = {
        "koblitz_a0": Curve(F, 0, 1),
        "koblitz_a1": Curve(F, 1, 1),
        "ordinary": Curve(F, 3, 1),
    }

    wdsat_src = repo_root / "inputs" / "TRIMOSKA-WDSAT-2024" / "upstream" / "src"
    wdsat = build_wdsat(wdsat_src, run_dir / "builds" / "wdsat_stage2_census")
    if not wdsat.get("build_ok"):
        reason = f"WDSat census build failed: {wdsat.get('error')}"
        summary = {
            "outcome": "O-IMPEDIMENT",
            "reason": reason,
            "leaf_census_attempted": False,
            "impediments": ["wdsat_census_build_failed"],
            "wdsat": {
                "build_ok": False,
                "binary_sha256": wdsat.get("binary_sha256"),
                "error": wdsat.get("error"),
            },
            "amd": amd_id,
            "refine_decision": refine_dec,
            "expand_decision": expand_dec,
            "task_id": task_id,
            "amazon_bedrock": "NOT_USED",
            "claims": {"break": False, "exponent_move": False, "deployed_attack": False},
        }
        leaf_path = out_dir / "leaf-counts.jsonl"
        if not leaf_path.exists():
            leaf_path.write_text("", encoding="utf-8")
        if not (out_dir / "arm-summaries.json").exists():
            _write_json(out_dir / "arm-summaries.json", summary)
        results_path = out_dir / "RESULTS.md"
        if not results_path.exists():
            results_path.write_text(
                "\n".join(
                    [
                        f"# RESULTS — EXP-BINSTD-b94ec8 (Stage 2 Semaev census / {amd_id})",
                        "",
                        "Outcome: **O-IMPEDIMENT**",
                        "",
                        reason,
                        "",
                        "Amazon Bedrock: NOT_USED. No Magma/Sage/AUXIN.",
                        "",
                    ]
                ),
                encoding="utf-8",
            )
        return {
            "status": "failed_infrastructure",
            "outcome": "O-IMPEDIMENT",
            "reason": reason,
            "impediments": ["wdsat_census_build_failed"],
            "wdsat": wdsat,
            "wdsat_build_ok": False,
            "wdsat_binary_sha256": wdsat.get("binary_sha256"),
            "leaf_census_attempted": False,
            "summary": summary,
        }

    weil_work = run_dir / "builds" / "weil_descent_work"
    leaf_rows: list[dict[str, Any]] = []
    arm_stats: dict[str, Any] = {}
    impediments: list[str] = []

    arm_names = [
        f"{cname}__{bname}"
        for cname in ("koblitz_a0", "koblitz_a1", "ordinary")
        for bname in ("stable_V5", "stable_V6", "window_deg_5", "window_deg_6")
    ]

    for arm_i, arm in enumerate(arm_names):
        cname, bname = arm.split("__", 1)
        curve = curves[cname]
        bmeta = basis_table[bname]
        basis = bmeta["basis"]
        l = bmeta["l"]
        V = _enumerate_V(basis)
        rng = random.Random((master_seed ^ (arm_i * 0x9E3779B9)) & 0xFFFFFFFF)
        conflicts_unsat: list[int] = []
        conflicts_sat: list[int] = []
        sat_ok = 0
        unsat_ok = 0
        export_errors = 0

        # --- UNSAT targets: random xR ---
        for ti in range(UNSAT_TARGETS_PER_ARM):
            xR = rng.randrange(F.q)
            row: dict[str, Any] = {
                "arm": arm,
                "curve": cname,
                "base": bname,
                "base_kind": bmeta["kind"],
                "l": l,
                "target_kind": "UNSAT",
                "target_index": ti,
                "xR": xR,
            }
            try:
                if bmeta["exporter"] == "trimoska_weil_descent_c":
                    inst = export_window_instance(
                        n=n,
                        l=l,
                        modulus=modulus,
                        xR=xR,
                        work_dir=weil_work,
                        formats=("anf",),
                    )
                    anf_path = instances_dir / f"{arm}__U{ti:02d}.anf"
                    if not anf_path.exists():
                        anf_path.write_text(inst["formats"]["anf"], encoding="utf-8")
                    sol = run_wdsat(Path(wdsat["binary"]), anf_path)
                else:
                    n_vars, eqs = descend_s4(F, basis, xR, a6=1)
                    sol = numpy_conflict_census(n_vars, eqs)
                    # Dense ANF is ~0.8MB/instance; keep only under run_dir sample.
                    if ti == 0:
                        exp = export_instance(F, basis, xR, a6=1, formats=("anf",))
                        anf_path = instances_dir / f"{arm}__U{ti:02d}.anf"
                        if not anf_path.exists():
                            anf_path.write_text(exp["formats"]["anf"], encoding="utf-8")
                row.update(sol)
                if sol.get("ok") and sol.get("conflicts") is not None:
                    conflicts_unsat.append(int(sol["conflicts"]))
                    unsat_ok += 1
                else:
                    export_errors += 1
            except Exception as exc:  # noqa: BLE001
                row["error"] = f"{type(exc).__name__}: {exc}"
                export_errors += 1
            leaf_rows.append(row)

        # --- planted SAT ---
        planted = 0
        attempts = 0
        while planted < PLANTED_SAT_PER_ARM and attempts < 200_000:
            attempts += 1
            plant = _plant_one(curve, V, rng)
            if plant is None:
                continue
            xR = plant["R_x"]
            ti = planted
            row = {
                "arm": arm,
                "curve": cname,
                "base": bname,
                "base_kind": bmeta["kind"],
                "l": l,
                "target_kind": "SAT",
                "target_index": ti,
                "xR": xR,
                "witness_x": plant["witness_x"],
            }
            try:
                if bmeta["exporter"] == "trimoska_weil_descent_c":
                    # TRIMOSKA window encoder only certifies window witnesses.
                    inst = export_window_instance(
                        n=n,
                        l=l,
                        modulus=modulus,
                        xR=xR,
                        work_dir=weil_work,
                        formats=("anf",),
                    )
                    anf_path = instances_dir / f"{arm}__S{ti:02d}.anf"
                    if not anf_path.exists():
                        anf_path.write_text(inst["formats"]["anf"], encoding="utf-8")
                    sol = run_wdsat(Path(wdsat["binary"]), anf_path)
                else:
                    n_vars, eqs = descend_s4(F, basis, xR, a6=1)
                    sol = numpy_conflict_census(n_vars, eqs)
                    if ti == 0:
                        exp = export_instance(F, basis, xR, a6=1, formats=("anf",))
                        anf_path = instances_dir / f"{arm}__S{ti:02d}.anf"
                        if not anf_path.exists():
                            anf_path.write_text(exp["formats"]["anf"], encoding="utf-8")
                row.update(sol)
                if sol.get("ok") and sol.get("conflicts") is not None:
                    conflicts_sat.append(int(sol["conflicts"]))
                    sat_ok += 1
                else:
                    export_errors += 1
            except Exception as exc:  # noqa: BLE001
                row["error"] = f"{type(exc).__name__}: {exc}"
                export_errors += 1
            leaf_rows.append(row)
            planted += 1

        arm_stats[arm] = {
            "curve": cname,
            "base": bname,
            "base_kind": bmeta["kind"],
            "exporter": bmeta["exporter"],
            "l": l,
            "unsat_ok": unsat_ok,
            "sat_ok": sat_ok,
            "export_errors": export_errors,
            "median_unsat_conflicts": median(conflicts_unsat),
            "median_sat_conflicts": median(conflicts_sat),
            "plant_attempts": attempts,
            "planted": planted,
        }
        if unsat_ok < UNSAT_TARGETS_PER_ARM or sat_ok < PLANTED_SAT_PER_ARM:
            impediments.append(f"incomplete_arm_{arm}")

    # Ratios at fixed (V,m,l): median Koblitz / median ordinary
    def arm_med(curve: str, base: str) -> float | None:
        return arm_stats.get(f"{curve}__{base}", {}).get("median_unsat_conflicts")

    ratios: dict[str, Any] = {}
    for bname in ("stable_V5", "stable_V6", "window_deg_5", "window_deg_6"):
        k0 = arm_med("koblitz_a0", bname)
        k1 = arm_med("koblitz_a1", bname)
        ord_m = arm_med("ordinary", bname)
        k_vals = [v for v in (k0, k1) if v is not None]
        k_med = median(k_vals) if k_vals else None
        ratio = None
        if k_med is not None and ord_m not in (None, 0):
            ratio = k_med / ord_m
        ratios[bname] = {
            "koblitz_a0_median": k0,
            "koblitz_a1_median": k1,
            "koblitz_combined_median": k_med,
            "ordinary_median": ord_m,
            "koblitz_ordinary_median_leaf_ratio": ratio,
        }

    # Primary: mean of ratios over the four bases (or null if incomplete)
    primary_ratios = [
        ratios[b]["koblitz_ordinary_median_leaf_ratio"]
        for b in ratios
        if ratios[b]["koblitz_ordinary_median_leaf_ratio"] is not None
    ]
    primary = median(primary_ratios) if primary_ratios else None

    # window vs stable at same l
    window_stable = {}
    for l, sname, wname in ((5, "stable_V5", "window_deg_5"), (6, "stable_V6", "window_deg_6")):
        # compare ordinary medians as a shape-independent base-kind contrast
        s = arm_med("ordinary", sname)
        w = arm_med("ordinary", wname)
        window_stable[f"l{l}"] = {
            "stable_ordinary_median": s,
            "window_ordinary_median": w,
            "window_stable_ratio": (w / s) if (s not in (None, 0) and w is not None) else None,
            "note": "same curve=ordinary; instruments differ (numpy vs WDSat) — disclosed",
        }

    # Outcome label
    outcome = "O-IMPEDIMENT"
    reason = ""
    if impediments:
        outcome = "O-IMPEDIMENT"
        reason = "Incomplete leaf census on one or more arms: " + ", ".join(impediments[:6])
    elif primary is None:
        outcome = "O-IMPEDIMENT"
        reason = "Primary koblitz/ordinary ratio undefined (zero/missing medians)"
    elif abs(primary - WITHDRAWN_RATIO) < 1e-12:
        outcome = "O-DIVISOR"
        reason = f"Primary ratio {primary} equals withdrawn 1/n comparator"
    elif RATIO_BAND[0] <= primary <= RATIO_BAND[1]:
        outcome = "O-NULL"
        reason = f"Primary koblitz/ordinary median leaf ratio {primary:.6g} in band {RATIO_BAND}"
    else:
        # Distinguish shape vs artifact lightly: if both koblitz replicates agree direction
        outcome = "O-SHAPE"
        reason = (
            f"Primary koblitz/ordinary median leaf ratio {primary:.6g} outside band "
            f"{RATIO_BAND} (curve-shape signal under disclosed instruments)"
        )

    summary = {
        "n": n,
        "m": M_ARITY,
        "unsat_targets_per_arm": UNSAT_TARGETS_PER_ARM,
        "planted_sat_per_arm": PLANTED_SAT_PER_ARM,
        "ratio_band": RATIO_BAND,
        "withdrawn_ratio_comparator": WITHDRAWN_RATIO,
        "outcome": outcome,
        "reason": reason,
        "leaf_census_attempted": True,
        "koblitz_ordinary_median_leaf_ratio": primary,
        "per_base_ratios": ratios,
        "window_stable": window_stable,
        "arms": arm_stats,
        "wdsat": {
            "build_ok": wdsat.get("build_ok"),
            "binary_sha256": wdsat.get("binary_sha256"),
            "config": wdsat.get("config"),
        },
        "amd": amd_id,
        "refine_decision": refine_dec,
        "expand_decision": expand_dec,
        "task_id": task_id,
        "impediments": impediments,
        "amazon_bedrock": "NOT_USED",
        "claims": {"break": False, "exponent_move": False, "deployed_attack": False},
    }

    leaf_path = out_dir / "leaf-counts.jsonl"
    if not leaf_path.exists():
        with leaf_path.open("w", encoding="utf-8") as fh:
            for row in leaf_rows:
                fh.write(json.dumps(row, sort_keys=True) + "\n")
    if not (out_dir / "arm-summaries.json").exists():
        _write_json(out_dir / "arm-summaries.json", summary)

    results = "\n".join(
        [
            f"# RESULTS — EXP-BINSTD-b94ec8 (Stage 2 Semaev census / {amd_id})",
            "",
            f"Outcome: **{outcome}**",
            "",
            reason,
            "",
            f"Primary koblitz_ordinary_median_leaf_ratio: {primary}",
            f"WDSat build_ok: {wdsat.get('build_ok')}",
            f"leaf rows: {len(leaf_rows)}",
            f"impediments: {impediments}",
            "",
            "Window arms: TRIMOSKA weill CNF-XOR/ANF + WDSat.",
            "Stable phi31_ker arms: semaev_export.py + numpy conflict census.",
            "Prior stage2/ and r2-phi31ker/ bytes immutable.",
            "Amazon Bedrock: NOT_USED. No Magma/Sage/AUXIN.",
            "",
        ]
    )
    if not (out_dir / "RESULTS.md").exists():
        (out_dir / "RESULTS.md").write_text(results, encoding="utf-8")

    return {
        "status": "completed" if outcome != "O-IMPEDIMENT" else "failed_infrastructure",
        "outcome": outcome,
        "reason": reason,
        "leaf_census_attempted": True,
        "koblitz_ordinary_median_leaf_ratio": primary,
        "window_stable_ratio": window_stable,
        "impediments": impediments,
        "wdsat_build_ok": wdsat.get("build_ok"),
        "wdsat_binary_sha256": wdsat.get("binary_sha256"),
        "n_leaf_rows": len(leaf_rows),
        "wall_clock_seconds": time.time() - t0,
        "amd": amd_id,
        "summary": summary,
    }

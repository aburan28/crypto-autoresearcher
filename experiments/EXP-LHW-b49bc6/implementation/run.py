#!/usr/bin/env python3
"""EXP-LHW-b49bc6 Stages 0-1: closed-form freeze then dual-route sumset millirho.

Observations only. No Magma/Sage/AUXIN/Bedrock. No walk on a curve. No ECDLP solve.
"""
from __future__ import annotations

import argparse
import json
import sys
import time
from pathlib import Path
from typing import Any

_IMPL = Path(__file__).resolve().parent
if str(_IMPL) not in sys.path:
    sys.path.insert(0, str(_IMPL))

import freeze as F  # noqa: E402
from route_a import card_sumset_a, comb_a, next_prime_a  # noqa: E402
from route_b import card_sumset_b, comb_b, next_prime_b  # noqa: E402
from walks import (  # noqa: E402
    decay_set,
    jump_sums,
    millirho,
    rng_subset,
    weight_class,
)

EXP_ROOT = Path(__file__).resolve().parents[1]


def write_json(path: Path, obj: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    if path.exists():
        raise FileExistsError(f"refusing overwrite: {path}")
    path.write_text(json.dumps(obj, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def write_text(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    if path.exists():
        raise FileExistsError(f"refusing overwrite: {path}")
    path.write_text(text, encoding="utf-8")


def write_yaml_manifest(path: Path, obj: dict) -> None:
    lines = []
    for key, value in obj.items():
        if isinstance(value, bool):
            lines.append(f"{key}: {'true' if value else 'false'}")
        elif value is None:
            lines.append(f"{key}: null")
        else:
            lines.append(f"{key}: {value}")
    write_text(path, "\n".join(lines) + "\n")


def frontier_rows() -> list[dict[str, int | str | bool]]:
    rows = []
    for m, w in F.CELLS:
        c_a, c_b = comb_a(m, w), comb_b(m, w)
        l_a = next_prime_a(1 << (m + 2))
        l_b = next_prime_b(1 << (m + 2))
        rows.append({
            "m": m,
            "w": w,
            "binom_a": c_a,
            "binom_b": c_b,
            "binom_freeze": F.BINOM[(m, w)],
            "l_a": l_a,
            "l_b": l_b,
            "l_freeze": F.L_PRIME[m],
            "pow2m": F.POW2M[m],
            "gap_cell": F.is_gap_cell(m, w),
            "routes_agree": int(c_a == c_b == F.BINOM[(m, w)] and l_a == l_b == F.L_PRIME[m]),
        })
    return rows


def stage0(run_dir: Path) -> dict[str, Any]:
    rows = frontier_rows()
    twin_ok = all(r["routes_agree"] == 1 for r in rows)
    pred = {
        "amazon_bedrock": F.AMAZON_BEDROCK,
        "approved_by": F.APPROVED_BY,
        "e1_max_millirho": F.E1_MAX_MILLIRHO,
        "e1_t_min": F.E1_T_MIN,
        "e2_min_millirho": F.E2_MIN_MILLIRHO,
        "e2_t": F.E2_T,
        "e2_t_rise": F.E2_T_RISE,
        "experiment_id": F.EXPERIMENT_ID,
        "families": list(F.FAMILIES),
        "gap_den": F.GAP_DEN,
        "gap_num": F.GAP_NUM,
        "hypothesis_id": F.HYPOTHESIS_ID,
        "q_pcts": list(F.Q_PCTS),
        "source_idea": F.SOURCE_IDEA,
        "t_grid": list(F.T_GRID),
        "walk_count": F.WALK_COUNT,
        "walk_seed0": F.WALK_SEED0,
        "wap_min_millirho_t1024": F.WAP_MIN_MILLIRHO_T1024,
        "wprime_count": F.WPRIME_COUNT,
        "wprime_seed0": F.WPRIME_SEED0,
        "xover_den": F.XOVER_DEN,
        "xover_num": F.XOVER_NUM,
    }
    table = {"amazon_bedrock": F.AMAZON_BEDROCK, "rows": rows, "twin_ok": twin_ok}
    write_json(EXP_ROOT / "stage0" / "preregistered-predictions.json", pred)
    write_json(EXP_ROOT / "stage0" / "frontier-table.json", table)
    outcome = "O-STAGE0-OK" if twin_ok else "O-ARTIFACT"
    raw = {
        "amazon_bedrock": "NOT_USED",
        "claims": {"break": False, "exponent_move": False},
        "experiment_id": F.EXPERIMENT_ID,
        "outcome": outcome,
        "stage": 0,
        "twin_ok": twin_ok,
        "row_count": len(rows),
    }
    write_json(run_dir / "raw-result.json", raw)
    write_yaml_manifest(run_dir / "manifest.yaml", {
        "experiment_id": F.EXPERIMENT_ID,
        "stage": 0,
        "outcome": outcome,
        "amazon_bedrock": "NOT_USED",
        "validity": "valid" if twin_ok else "invalid",
    })
    return raw


def _count_pair(xs: tuple[int, ...], js: tuple[int, ...], lo: int, hi: int) -> tuple[int, int, bool]:
    ca = card_sumset_a(xs, js, lo, hi)
    cb = card_sumset_b(xs, js, lo, hi)
    return ca, cb, ca == cb


def stage1(run_dir: Path) -> dict[str, Any]:
    pred_path = EXP_ROOT / "stage0" / "preregistered-predictions.json"
    table_path = EXP_ROOT / "stage0" / "frontier-table.json"
    if not pred_path.is_file() or not table_path.is_file():
        raw = {
            "amazon_bedrock": "NOT_USED",
            "claims": {"break": False, "exponent_move": False},
            "experiment_id": F.EXPERIMENT_ID,
            "outcome": "O-IMPEDIMENT",
            "stage": 1,
            "detail": "missing Stage-0 freeze",
        }
        write_json(run_dir / "raw-result.json", raw)
        write_yaml_manifest(run_dir / "manifest.yaml", {
            "experiment_id": F.EXPERIMENT_ID, "stage": 1, "outcome": "O-IMPEDIMENT",
            "amazon_bedrock": "NOT_USED", "validity": "incomplete",
        })
        return raw

    panels: dict[str, Any] = {}
    controls: dict[str, Any] = {"amazon_bedrock": F.AMAZON_BEDROCK, "cells": {}}
    artifact = False
    e2_hits = 0
    e1_ok_cells = 0

    for m, w in F.CELLS:
        key = f"m{m}_w{w}"
        W = weight_class(m, w)
        if len(W) != F.BINOM[(m, w)]:
            artifact = True
        lo, hi = -F.BITMAP_HALF[m], F.BITMAP_HALF[m]
        Wap = tuple(range(F.WAP_START, F.WAP_START + len(W)))
        Wps = [rng_subset(m, len(W), F.WPRIME_SEED0 + s) for s in range(F.WPRIME_COUNT)]
        cell_rows = []
        millirhos: dict[str, dict[int, list[int]]] = {fam: {t: [] for t in F.T_GRID} for fam in F.FAMILIES}
        wap_mrho: dict[str, dict[int, list[int]]] = {fam: {t: [] for t in F.T_GRID} for fam in F.FAMILIES}
        decay_pts: list[dict[str, int | str]] = []
        for fam in F.FAMILIES:
            for t in F.T_GRID:
                for wi in range(F.WALK_COUNT):
                    js = jump_sums(fam, m, t, F.WALK_SEED0 + wi)
                    cW_a, cW_b, okW = _count_pair(W, js, lo, hi)
                    if not okW:
                        artifact = True
                    cW = cW_a
                    wp_cards = []
                    for Wp in Wps:
                        c_a, c_b, ok = _count_pair(Wp, js, lo, hi)
                        if not ok:
                            artifact = True
                        wp_cards.append(c_a)
                    med_wp = sorted(wp_cards)[len(wp_cards) // 2]
                    mrho = millirho(cW, med_wp)
                    millirhos[fam][t].append(mrho)
                    cA_a, cA_b, okA = _count_pair(Wap, js, lo, hi)
                    if not okA:
                        artifact = True
                    # Def(W_ap)/Def(W') = |W'+J|/|Wap+J| at matched |X|.
                    wap_mrho[fam][t].append(millirho(cA_a, med_wp))
                    if fam == "Jd_unit" and t == F.E2_T and wi == 0:
                        for q in F.Q_PCTS:
                            Wq = decay_set(W, m, q, F.WALK_SEED0)
                            cq_a, cq_b, okq = _count_pair(Wq, js, lo, hi)
                            if not okq:
                                artifact = True
                            decay_pts.append({
                                "q_pct": q,
                                "millirho": millirho(cq_a, med_wp),
                                "card": cq_a,
                            })
                    cell_rows.append({
                        "family": fam,
                        "t": t,
                        "walk": wi,
                        "j_card": len(js),
                        "card_W": cW,
                        "millirho_vs_Wprime_median": mrho,
                    })
        summaries = {}
        cell_e1 = True
        cell_e2 = False
        for fam in F.FAMILIES:
            summaries[fam] = {}
            for t in F.T_GRID:
                vals = millirhos[fam][t]
                med = sorted(vals)[len(vals) // 2]
                summaries[fam][str(t)] = {"median_millirho": med, "n": len(vals)}
                if t >= F.E1_T_MIN and med > F.E1_MAX_MILLIRHO:
                    cell_e1 = False
            m1024 = summaries[fam][str(F.E2_T)]["median_millirho"]
            m4096 = summaries[fam][str(F.E2_T_RISE)]["median_millirho"]
            if m1024 >= F.E2_MIN_MILLIRHO and m4096 > m1024:
                cell_e2 = True
        wap_med = sorted(wap_mrho["Jd_unit"][F.E2_T])[len(wap_mrho["Jd_unit"][F.E2_T]) // 2]
        if wap_med < F.WAP_MIN_MILLIRHO_T1024:
            artifact = True
        decay_ok = True
        if decay_pts:
            prev = 10**12
            for pt in decay_pts:
                if int(pt["millirho"]) > prev:
                    decay_ok = False
                prev = int(pt["millirho"])
            if not decay_ok:
                artifact = True
        if cell_e1:
            e1_ok_cells += 1
        if cell_e2:
            e2_hits += 1
        panels[key] = {
            "m": m,
            "w": w,
            "gap_cell": F.is_gap_cell(m, w),
            "summaries": summaries,
            "wap_median_millirho_Jd_t1024": wap_med,
            "decay": decay_pts,
            "decay_monotone": decay_ok,
            "e1_flat": cell_e1,
            "e2_growth": cell_e2,
        }
        controls["cells"][key] = {
            "twin_ok": not artifact,
            "wap_control_pass": wap_med >= F.WAP_MIN_MILLIRHO_T1024,
            "n_rows": len(cell_rows),
        }

    if artifact:
        outcome = "O-ARTIFACT"
    elif e2_hits >= 2:
        outcome = "O-E2"
    elif e1_ok_cells == len(F.CELLS):
        outcome = "O-E1"
    else:
        outcome = "O-INCONCLUSIVE"

    write_json(EXP_ROOT / "stage1" / "panels.json", panels)
    write_json(EXP_ROOT / "stage1" / "control-table.json", controls)
    results = "\n".join([
        f"# EXP-LHW-b49bc6 Stages 0-1 RESULTS",
        f"",
        f"outcome: {outcome}",
        f"e1_ok_cells: {e1_ok_cells}",
        f"e2_hits: {e2_hits}",
        f"amazon_bedrock: NOT_USED",
        f"claims.break: false",
        f"claims.exponent_move: false",
        f"",
        f"Exactly one O-* label. Toy integer sumsets on W(m,w). No ECDLP solve.",
        f"",
    ])
    write_text(EXP_ROOT / "RESULTS.md", results)
    raw = {
        "amazon_bedrock": "NOT_USED",
        "claims": {"break": False, "exponent_move": False},
        "e1_ok_cells": e1_ok_cells,
        "e2_hits": e2_hits,
        "experiment_id": F.EXPERIMENT_ID,
        "hypothesis_id": F.HYPOTHESIS_ID,
        "outcome": outcome,
        "stage": 1,
    }
    write_json(run_dir / "raw-result.json", raw)
    write_yaml_manifest(run_dir / "manifest.yaml", {
        "experiment_id": F.EXPERIMENT_ID,
        "stage": 1,
        "outcome": outcome,
        "amazon_bedrock": "NOT_USED",
        "validity": "invalid" if outcome == "O-ARTIFACT" else "valid",
    })
    return raw


def main() -> int:
    p = argparse.ArgumentParser()
    p.add_argument("--stage", type=int, required=True, choices=(0, 1))
    p.add_argument("--trial-plan", required=True)
    p.add_argument("--run-dir", required=True)
    args = p.parse_args()
    run_dir = Path(args.run_dir)
    run_dir.mkdir(parents=True, exist_ok=True)
    t0 = time.time()
    if args.stage == 0:
        raw = stage0(run_dir)
    else:
        raw = stage1(run_dir)
    raw["wall_clock_seconds"] = round(time.time() - t0, 3)
    print(json.dumps({"outcome": raw.get("outcome"), "stage": args.stage}, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

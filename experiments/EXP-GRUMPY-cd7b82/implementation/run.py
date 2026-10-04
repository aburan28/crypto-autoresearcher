#!/usr/bin/env python3
"""EXP-GRUMPY-cd7b82 Stages 0–1 driver. Dual meters: envelope vs covered-set.

Observations only. No ECDLP solve, no exponent, no n≥131 field, no Bedrock.
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

_IMPL = Path(__file__).resolve().parent
if str(_IMPL) not in sys.path:
    sys.path.insert(0, str(_IMPL))
from covered import covered_size_dual, grow_lists
from envelope import class_counts, envelope_amqm_bound, floor_numerator, floor_survival_terms, pair_count

EXPERIMENT_ID = "EXP-GRUMPY-cd7b82"
HYPOTHESIS_ID = "H-GRUMPY-62b749"
PRIMES = [101, 257]
N_MAX_FLOOR = 80
SCHEDULES = {
    "bsgs_interleaved": {"rates": (1, 1), "k": 2, "n_free": 2, "betas": (0, 1), "step": (1, None)},
    "grumpy_eq_s2": {"rates": (1, 1, 1), "k": 3, "n_free": 3, "betas": (0, 1, 2), "step": (1, None, None)},
}


def _m(ell: int) -> int:
    r = int(round(ell**0.5))
    return max(1, r)


def _steps(ell: int, k: int) -> tuple[int, ...]:
    m = _m(ell)
    if k == 2:
        return (1, m)
    return (1, m, m + 1)


def write_json(path: Path, obj: object) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(obj, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def stage0(exp_root: Path, run_dir: Path) -> dict:
    floor_rows: list[dict] = []
    floor_summary: list[dict] = []
    for ell in PRIMES:
        for name, spec in SCHEDULES.items():
            rows = floor_survival_terms(ell, spec["k"], spec["n_free"], N_MAX_FLOOR)
            for r in rows:
                r["schedule"] = name
            floor_rows.extend(rows)
            num = floor_numerator(rows)
            floor_summary.append(
                {
                    "l": int(ell),
                    "schedule": name,
                    "k": spec["k"],
                    "n_free": spec["n_free"],
                    "floor_numerator": int(num),
                    "floor_denominator": int(ell),
                    "n_rows": len(rows),
                }
            )
    freeze = {
        "amazon_bedrock": "NOT SELECTED",
        "experiment_id": EXPERIMENT_ID,
        "hypothesis_id": HYPOTHESIS_ID,
        "primes": [int(p) for p in PRIMES],
        "rows": floor_rows,
        "schema": "crypto.autoresearch.grumpy_floor_table.v1",
        "summary": floor_summary,
    }
    pred = {
        "amazon_bedrock": "NOT SELECTED",
        "claim_tier": "heuristic_validation",
        "delta_ovl_e1_min": 0.03,
        "delta_ovl_e2_max": 0.01,
        "experiment_id": EXPERIMENT_ID,
        "m1": "E(l) >= F(l) on every authorized (l, schedule) with |C_n| <= P_n <= envelope_bound",
        "m2": "BSGS k=2: |C_n| == P_n until P_n >= l (zero overlap before saturation)",
        "no_break": True,
        "no_exponent": True,
        "primes": [int(p) for p in PRIMES],
        "schema": "crypto.autoresearch.preregistered_predictions.v1",
        "stage1_schedules": ["bsgs_interleaved", "grumpy_eq_s2"],
        "stage1_convention": "PLAIN",
    }
    write_json(exp_root / "stage0" / "floor-table.json", freeze)
    write_json(exp_root / "stage0" / "preregistered-predictions.json", pred)
    write_json(run_dir / "raw-result.json", {
        "amazon_bedrock": "NOT_USED",
        "claims": {"break": False, "exponent_move": False},
        "experiment_id": EXPERIMENT_ID,
        "floor_row_count": len(floor_rows),
        "outcome": "O-STAGE0-OK",
        "primes": [int(p) for p in PRIMES],
        "stage": 0,
        "summary": floor_summary,
    })
    (run_dir / "manifest.yaml").write_text(
        f"id: RUN-GRUMPY-9df12c\nexperiment_id: {EXPERIMENT_ID}\nstage: 0\nstatus: completed\n",
        encoding="utf-8",
    )
    return {"outcome": "O-STAGE0-OK"}


def _mean_and_decomp(ell: int, spec: dict) -> dict:
    k = spec["k"]
    n_free = spec["n_free"]
    rates = spec["rates"]
    betas = spec["betas"]
    steps = _steps(ell, k)
    n_max = 0
    while envelope_amqm_bound(n_max, k, n_free) < ell and n_max < 4 * ell:
        n_max += 1
    rows = []
    survival = 0
    last_c = 0
    for n in range(0, n_max + 1):
        counts = class_counts(n, rates, n_free)
        p_n = pair_count(counts)
        bound = envelope_amqm_bound(n, k, n_free)
        lists = grow_lists(n, rates, n_free, ell, steps)
        c_a, c_b, ok = covered_size_dual(lists, ell, betas)
        if not ok or c_a != c_b:
            return {"artifact": True, "reason": f"dual covered mismatch at n={n}"}
        c_n = c_a
        if c_n > p_n or p_n > bound:
            return {"artifact": True, "reason": f"|C| or P exceeds envelope at n={n}"}
        imb = bound - p_n
        ovl = p_n - c_n
        if imb < 0 or ovl < 0:
            return {"artifact": True, "reason": f"negative deficit at n={n}"}
        term = max(0, ell - c_n)
        survival += term
        last_c = c_n
        rows.append(
            {
                "l": int(ell),
                "n": int(n),
                "k": int(k),
                "n0": int(counts[0] if len(counts) > 0 else 0),
                "n1": int(counts[1] if len(counts) > 1 else 0),
                "n2": int(counts[2] if len(counts) > 2 else 0),
                "P_n": int(p_n),
                "C_n": int(c_n),
                "envelope_bound": int(bound),
                "imbalance": int(imb),
                "overlap": int(ovl),
            }
        )
        if c_n >= ell:
            break
    e_num = survival
    floor_rows = floor_survival_terms(ell, k, n_free, n_max)
    f_num = floor_numerator(floor_rows)
    return {
        "artifact": False,
        "l": int(ell),
        "k": int(k),
        "E_numerator": int(e_num),
        "F_numerator": int(f_num),
        "denominator": int(ell),
        "E_ge_F": e_num >= f_num,
        "final_C": int(last_c),
        "rows": rows,
    }


def stage1(exp_root: Path, run_dir: Path) -> dict:
    freeze_path = exp_root / "stage0" / "floor-table.json"
    if not freeze_path.is_file():
        raw = {
            "amazon_bedrock": "NOT_USED",
            "claims": {"break": False, "exponent_move": False},
            "experiment_id": EXPERIMENT_ID,
            "outcome": "O-IMPEDIMENT",
            "reason": "missing Stage-0 floor-table.json",
            "stage": 1,
        }
        write_json(run_dir / "raw-result.json", raw)
        (run_dir / "manifest.yaml").write_text(
            f"id: RUN-GRUMPY-a8ec76\nexperiment_id: {EXPERIMENT_ID}\nstage: 1\nstatus: failed_infrastructure\n",
            encoding="utf-8",
        )
        return raw
    panels = []
    all_rows = []
    artifact = False
    m1_ok = True
    m2_ok = True
    for ell in PRIMES:
        for name, spec in SCHEDULES.items():
            block = _mean_and_decomp(ell, spec)
            if block.get("artifact"):
                artifact = True
                panels.append({"l": ell, "schedule": name, "error": block.get("reason")})
                continue
            for r in block["rows"]:
                r["schedule"] = name
            all_rows.extend(block["rows"])
            e_ge_f = bool(block["E_ge_F"])
            m1_ok = m1_ok and e_ge_f
            if name == "bsgs_interleaved":
                sat = False
                for r in block["rows"]:
                    if r["P_n"] >= ell:
                        sat = True
                        break
                    if r["C_n"] != r["P_n"]:
                        m2_ok = False
                        break
            panels.append(
                {
                    "l": int(ell),
                    "schedule": name,
                    "E_numerator": block["E_numerator"],
                    "F_numerator": block["F_numerator"],
                    "denominator": block["denominator"],
                    "E_ge_F": e_ge_f,
                    "row_count": len(block["rows"]),
                }
            )
    if artifact:
        outcome = "O-ARTIFACT"
    elif not m1_ok:
        outcome = "O-FAIL-M1"
    elif not m2_ok:
        outcome = "O-FAIL-M2"
    else:
        outcome = "O-SUPPORT-M12"
    control = {
        "amazon_bedrock": "NOT SELECTED",
        "m1_ok": m1_ok,
        "m2_ok": m2_ok,
        "outcome": outcome,
        "panels": panels,
    }
    write_json(exp_root / "stage1" / "decomposition-rows.json", {
        "amazon_bedrock": "NOT SELECTED",
        "experiment_id": EXPERIMENT_ID,
        "rows": all_rows,
        "schema": "crypto.autoresearch.grumpy_decomp_rows.v1",
    })
    write_json(exp_root / "stage1" / "control-table.json", control)
    (exp_root / "RESULTS.md").write_text(
        f"# EXP-GRUMPY-cd7b82 RESULTS\n\noutcome: {outcome}\n\n"
        "PLAIN matching only. Dual meters envelope vs covered-set. "
        "No break. No exponent. No n>=131 transfer.\n",
        encoding="utf-8",
    )
    raw = {
        "amazon_bedrock": "NOT_USED",
        "claims": {"break": False, "exponent_move": False},
        "experiment_id": EXPERIMENT_ID,
        "m1_ok": m1_ok,
        "m2_ok": m2_ok,
        "outcome": outcome,
        "panels": panels,
        "stage": 1,
    }
    write_json(run_dir / "raw-result.json", raw)
    (run_dir / "manifest.yaml").write_text(
        f"id: RUN-GRUMPY-a8ec76\nexperiment_id: {EXPERIMENT_ID}\nstage: 1\nstatus: completed\n",
        encoding="utf-8",
    )
    return raw


def main() -> int:
    p = argparse.ArgumentParser()
    p.add_argument("--stage", required=True, type=int, choices=[0, 1])
    p.add_argument("--trial-plan", required=True)
    p.add_argument("--run-dir", required=True)
    args = p.parse_args()
    run_dir = Path(args.run_dir)
    run_dir.mkdir(parents=True, exist_ok=True)
    exp_root = Path(__file__).resolve().parents[1]
    if args.stage == 0:
        stage0(exp_root, run_dir)
    else:
        stage1(exp_root, run_dir)
    print("OK")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

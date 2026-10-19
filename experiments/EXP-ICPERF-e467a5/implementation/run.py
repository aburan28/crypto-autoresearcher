#!/usr/bin/env python3
"""Stage-0 instrument for EXP-ICPERF-e467a5.

Exact integer check that the Bernstein-Lange price ratio does not depend
on r or A. Writes observations only.
"""

from __future__ import annotations

import argparse
import json
import math
import time
from pathlib import Path

C_PROBE_NS = 370
C_STATE_NS = 2100
C_STEP_NS = 40
BL_NUM = 21
BL_DEN = 10
STATES = 10
CELLS = (
    ("r1000_a2", 1000, 2),
    ("r4000_a2", 4000, 2),
    ("r1000_a4", 1000, 4),
)


def div_exact(numerator: int, denominator: int, label: str) -> int:
    if denominator == 0 or numerator % denominator != 0:
        raise RuntimeError(f"{label} is not an integer: {numerator}/{denominator}")
    return numerator // denominator


def reduced(numerator: int, denominator: int) -> tuple[int, int]:
    if denominator <= 0:
        raise RuntimeError("denominator must be positive")
    factor = math.gcd(numerator, denominator)
    return numerator // factor, denominator // factor


def price_ratio() -> tuple[int, int]:
    return reduced(
        C_PROBE_NS * C_STATE_NS * BL_DEN,
        BL_NUM * C_STEP_NS * C_STEP_NS,
    )


def cell(name: str, subgroup_order: int, classes: int) -> dict:
    probes = div_exact(subgroup_order, classes * STATES, f"{name} probes")
    precomputation_steps = div_exact(STATES * C_STATE_NS, C_STEP_NS, f"{name} precomputation")
    bl_steps = div_exact(
        BL_NUM * subgroup_order,
        BL_DEN * classes * precomputation_steps,
        f"{name} BL steps",
    )
    bl_online_ns = bl_steps * C_STEP_NS
    ic_online_ns = probes * C_PROBE_NS
    ratio_num, ratio_den = reduced(ic_online_ns, bl_online_ns)
    bsgs_probes = div_exact(subgroup_order // classes, STATES, f"{name} BSGS probes")
    price_num, price_den = price_ratio()
    return {
        "name": name,
        "r": subgroup_order,
        "A": classes,
        "states": STATES,
        "probes": probes,
        "bsgs_probes": bsgs_probes,
        "matches_bsgs_probes": probes == bsgs_probes,
        "precomputation_steps": precomputation_steps,
        "bl_online_ns": bl_online_ns,
        "ic_online_ns": ic_online_ns,
        "ratio_num": ratio_num,
        "ratio_den": ratio_den,
        "matches_price_ratio": (ratio_num, ratio_den) == (price_num, price_den),
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--stage", type=int, required=True)
    parser.add_argument("--trial-id", required=True)
    parser.add_argument("--trial-plan", required=True)
    parser.add_argument("--run-dir", required=True)
    args = parser.parse_args()
    if args.stage != 0:
        raise SystemExit("this runner implements stage 0 only")
    if args.trial_id != "price-ratio-identity":
        raise SystemExit("trial id is not the preregistered cell")
    run_dir = Path(args.run_dir)
    run_dir.mkdir(parents=True, exist_ok=True)
    started = time.perf_counter()
    price_num, price_den = price_ratio()
    rows = [cell(name, subgroup_order, classes) for name, subgroup_order, classes in CELLS]
    ratios = {(row["ratio_num"], row["ratio_den"]) for row in rows}
    elapsed = time.perf_counter() - started
    payload = {
        "schema": "crypto.autoresearch.exp-icperf-e467a5.stage0.v1",
        "experiment_id": "EXP-ICPERF-e467a5",
        "hypothesis_id": "H-ICPERF-2f52d1",
        "trial_id": args.trial_id,
        "run_id": "RUN-ICPERF-943efa",
        "stage": 0,
        "c_probe_ns": C_PROBE_NS,
        "c_state_ns": C_STATE_NS,
        "c_step_ns": C_STEP_NS,
        "bl_num": BL_NUM,
        "bl_den": BL_DEN,
        "states": STATES,
        "price_ratio_num": price_num,
        "price_ratio_den": price_den,
        "cells": rows,
        "ratios_agree": len(ratios) == 1 and ratios.pop() == (price_num, price_den),
        "all_match_bsgs": all(row["matches_bsgs_probes"] for row in rows),
        "elapsed_seconds": elapsed,
        "claim_boundary": (
            "integer identity on three toy price cells; not a measurement "
            "of the n=83 Bernstein-Lange arm and not a statement about any deployed curve"
        ),
    }
    (run_dir / "raw-result.json").write_text(
        json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )
    manifest = "\n".join(
        [
            "run:",
            "  id: RUN-ICPERF-943efa",
            "  experiment_id: EXP-ICPERF-e467a5",
            "  status: observation",
            "  stage: 0",
            f"  price_ratio_num: {payload['price_ratio_num']}",
            f"  price_ratio_den: {payload['price_ratio_den']}",
            f"  ratios_agree: {str(payload['ratios_agree']).lower()}",
            f"  all_match_bsgs: {str(payload['all_match_bsgs']).lower()}",
            "",
        ]
    )
    (run_dir / "manifest.yaml").write_text(manifest, encoding="utf-8")
    lines = [
        "# EXP-ICPERF-e467a5 stage 0 observations",
        "",
        "This file records the integer identity. It does not confirm the n=83 measurement.",
        "",
        f"- price ratio: {payload['price_ratio_num']}/{payload['price_ratio_den']}",
        f"- ratios_agree: {payload['ratios_agree']}",
        f"- all_match_bsgs: {payload['all_match_bsgs']}",
    ]
    for row in rows:
        lines.append(
            f"- {row['name']}: probes {row['probes']}, "
            f"ratio {row['ratio_num']}/{row['ratio_den']}, "
            f"matches_price_ratio {row['matches_price_ratio']}"
        )
    lines.append(f"- elapsed_seconds: {payload['elapsed_seconds']}")
    lines.append("")
    (run_dir / "RESULTS.md").write_text("\n".join(lines), encoding="utf-8")


if __name__ == "__main__":
    main()

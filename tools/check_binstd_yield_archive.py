#!/usr/bin/env python3
"""Check the committed BINSTD ell=8/9 yield records against their run pins.

This is a static archive check. It does not replay the runner, independently
implement elliptic-curve arithmetic, or authenticate historical execution.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import sys
from fractions import Fraction
from pathlib import Path


EXPERIMENT = "EXP-BINSTD-8bdf86"
SOLVER = "exhaustive_fb_sum_m3_stdlib_gf2"
PANELS = (
    ("RUN-BINSTD-43abd4", "ell89", (16, 40)),
    ("RUN-BINSTD-a2a24c", "ell89r1", (20, 40)),
)


def require(condition: bool, message: str) -> None:
    if not condition:
        raise ValueError(message)


def read_json(path: Path) -> tuple[dict, str]:
    data = path.read_bytes()
    parsed = json.loads(data)
    require(isinstance(parsed, dict), f"{path}: expected JSON object")
    return parsed, hashlib.sha256(data).hexdigest()


def natural(value: object, label: str) -> int:
    require(type(value) is int and value >= 0, f"{label}: expected nonnegative integer")
    return value


def rational(value: object, label: str) -> Fraction:
    require(type(value) in (int, float), f"{label}: expected number")
    return Fraction(str(value))


def check_panel(root: Path, run_id: str, tag: str, expected_hits: tuple[int, int]) -> dict:
    base = root / "experiments" / EXPERIMENT
    run = base / "runs" / run_id
    stage = base / f"stage1-{tag}"
    raw, raw_hash = read_json(run / "raw-result.json")
    receipt, _ = read_json(run / "execution-receipt.json")
    matrix, matrix_hash = read_json(stage / "yield-matrix.json")
    dims, dims_hash = read_json(stage / "admissible-phi-dims.json")

    result = raw["result"]
    require(result["experiment_id"] == EXPERIMENT, f"{run_id}: experiment ID")
    require(type(result["stage"]) is int and result["stage"] == 1
            and result["status"] == "completed_valid", f"{run_id}: stage/status")
    require(result["outcome"] == "E-TAU-NOT-RICHER", f"{run_id}: outcome")
    pins = result["artifact_sha256"]
    require(pins["stage1/yield-matrix.json"] == matrix_hash, f"{run_id}: yield matrix digest")
    require(pins["stage1/admissible-phi-dims.json"] == dims_hash, f"{run_id}: dimensions digest")
    require(receipt["run_id"] == run_id, f"{run_id}: receipt run ID")
    require(receipt["status"] == "output_validated", f"{run_id}: receipt status")
    require(type(receipt["returncode"]) is int and type(receipt["check_returncode"]) is int
            and receipt["returncode"] == 0 and receipt["check_returncode"] == 0,
            f"{run_id}: producer/checker exit codes")
    require(receipt["artifact_sha256"]["raw-result.json"] == raw_hash,
            f"{run_id}: raw result digest")

    require(matrix["experiment_id"] == EXPERIMENT and matrix["artifact_tag"] == tag,
            f"{run_id}: matrix identity")
    require(matrix["solver_pin"] == SOLVER, f"{run_id}: matrix solver pin")
    require(matrix["ells"] == [8, 9], f"{run_id}: ell set")
    require(rational(matrix["band"], f"{run_id}: band") == Fraction(5, 4), f"{run_id}: band value")
    require(matrix["admissible_phi_dims"] == dims, f"{run_id}: dimensions content")
    cells = matrix["cells"]
    summaries = result["cells_summary"]
    require(isinstance(cells, list) and len(cells) == 2, f"{run_id}: expected two cells")
    require(isinstance(summaries, list) and len(summaries) == 2, f"{run_id}: expected two summaries")
    checked = []
    for index, (cell, summary, tau_expected) in enumerate(zip(cells, summaries, expected_hits)):
        label = f"{run_id}: cell {index}"
        require(cell["ell"] == (8, 9)[index] and cell["n"] == 17, f"{label}: identity")
        targets = natural(cell["target_count"], f"{label}: target count")
        tau = natural(cell["hits_tau"], f"{label}: tau hits")
        opened = natural(cell["hits_open"], f"{label}: open hits")
        require(targets == 40 and tau == tau_expected and opened == 40, f"{label}: archived counts")
        require(tau <= targets and opened == targets, f"{label}: hit bounds")
        require(cell["status"] == "ok" and cell["solver_pin"] == SOLVER, f"{label}: status/solver")
        require(cell["cell_label"] == "E-TAU-NOT-RICHER", f"{label}: outcome label")
        require(rational(cell["band"], f"{label}: band") == Fraction(5, 4), f"{label}: band")
        require(rational(cell["R_tau"], f"{label}: tau rate") == Fraction(tau, targets),
                f"{label}: tau rate arithmetic")
        require(rational(cell["R_open"], f"{label}: open rate") == Fraction(opened, targets),
                f"{label}: open rate arithmetic")
        ratio = Fraction(tau, opened)
        require(rational(cell["ratio_tau_over_open"], f"{label}: ratio") == ratio,
                f"{label}: ratio arithmetic")
        require(4 * tau < 5 * opened, f"{label}: 1.25 ceiling")
        require(cell["both_arms_nonzero"] is True and cell["band_applicable"] is True
                and cell["meets_band"] is False, f"{label}: band flags")
        require(summary["ell"] == cell["ell"] and summary["status"] == cell["status"]
                and summary["cell_label"] == cell["cell_label"], f"{label}: raw summary identity")
        require(rational(summary["ratio"], f"{label}: raw ratio") == ratio,
                f"{label}: raw summary ratio")
        checked.append({"ell": cell["ell"], "tau_hits": tau, "open_hits": opened,
                        "targets": targets, "ratio": str(ratio)})
    return {"run_id": run_id, "tag": tag, "raw_result_sha256": raw_hash,
            "yield_matrix_sha256": matrix_hash, "cells": checked}


def check_archive(root: Path) -> dict:
    return {"schema": "binstd-yield-archive-check/v1",
            "scope": "Static committed records and arithmetic; no runner or EC replay",
            "panels": [check_panel(root, *panel) for panel in PANELS]}


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=Path(__file__).resolve().parents[1])
    args = parser.parse_args(argv)
    try:
        print(json.dumps(check_archive(args.root), indent=2))
    except (OSError, ValueError, KeyError, TypeError, ZeroDivisionError, json.JSONDecodeError) as exc:
        print(f"BINSTD archive check failed: {exc}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

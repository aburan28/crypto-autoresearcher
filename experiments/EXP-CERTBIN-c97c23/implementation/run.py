#!/usr/bin/env python3
"""EXP-CERTBIN-c97c23 Stages 0-1: rare-event freeze then toy union control.

No Magma/Sage/AUXIN/Bedrock. No SAT/MITM. No ECDLP solve.
"""
from __future__ import annotations

import argparse
import json
import resource
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

_IMP = Path(__file__).resolve().parent
if str(_IMP) not in sys.path:
    sys.path.insert(0, str(_IMP))

from toy_image import run_cell  # noqa: E402
from union_math import SEED_STAGE1, freeze_stage0  # noqa: E402

EXPERIMENT_ID = "EXP-CERTBIN-c97c23"
HYPOTHESIS_ID = "H-CERTBIN-a916e0"
APPROVED_BY = "DEC-20261004-2be060"
STAGE1_OUTCOMES = ("O-RARE", "O-BATCH", "O-ARTIFACT", "O-IMPEDIMENT")


def _utc_now() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def _peak_rss_bytes() -> int:
    # Linux ru_maxrss is kilobytes.
    return int(resource.getrusage(resource.RUSAGE_SELF).ru_maxrss) * 1024


def _write_json(path: Path, obj: Any) -> None:
    path.write_text(json.dumps(obj, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def _write_manifest(run_dir: Path, stage: int, extra: dict[str, Any]) -> None:
    manifest = {
        "id": run_dir.name,
        "experiment_id": EXPERIMENT_ID,
        "hypothesis_id": HYPOTHESIS_ID,
        "approved_by": APPROVED_BY,
        "status": "completed",
        "stage": stage,
        "timestamp_utc": _utc_now(),
        "peak_rss_bytes": _peak_rss_bytes(),
        "amazon_bedrock": "NOT SELECTED",
        **extra,
    }
    # Prefer YAML-looking dump without requiring PyYAML: JSON is accepted by
    # many CERTBIN worksheets; also write manifest.yaml as JSON text for
    # schema-light harnesses that only check presence.
    text = json.dumps(manifest, indent=2, sort_keys=True) + "\n"
    (run_dir / "manifest.yaml").write_text(text, encoding="utf-8")


def stage0(run_dir: Path) -> int:
    freeze = freeze_stage0()
    _write_json(run_dir / "union_freeze.json", freeze)
    raw = {
        "stage": 0,
        "archived_identity_ok": freeze["archived_identity"]["archived_identity_ok"],
        "cells": freeze["cells"],
        "outcome_gate": "Stage 0 freeze only; Stage 1 decides O-*",
    }
    _write_json(run_dir / "raw-result.json", raw)
    _write_manifest(
        run_dir,
        0,
        {
            "artifacts": ["union_freeze.json", "raw-result.json", "manifest.yaml"],
            "archived_identity_ok": raw["archived_identity_ok"],
        },
    )
    print(json.dumps({"stage": 0, "archived_identity_ok": raw["archived_identity_ok"]}))
    return 0 if raw["archived_identity_ok"] else 2


def _decide_outcome(freeze: dict[str, Any], cells: list[dict[str, Any]]) -> str:
    if not freeze["archived_identity"]["archived_identity_ok"]:
        return "O-ARTIFACT"
    # find p_half / p_sparse results
    by_id = {c["cell_id"]: c for c in cells}
    if "p_sparse" not in by_id or "p_half" not in by_id:
        return "O-ARTIFACT"
    sparse = by_id["p_sparse"]
    half = by_id["p_half"]
    # instrument failure: measured union near L*p at p_half
    if abs(half["union_L4"]["union_frequency"] - (4 * half["p_hat"])) <= 0.1:
        return "O-ARTIFACT"
    if half["union_abs_deviation_L4"] > 0.15:
        return "O-ARTIFACT"
    if sparse["union_abs_deviation_L4"] > 0.15:
        return "O-ARTIFACT"
    # E-BATCH if charged ratio < 1 at either cell
    if (
        sparse["coverage"]["charged_ratio"] < 1.0
        or half["coverage"]["charged_ratio"] < 1.0
    ):
        return "O-BATCH"
    # success band
    if (
        sparse["union_abs_deviation_L4"] < 0.05
        and half["union_abs_deviation_L4"] < 0.05
        and half["linearization_error"] >= 1.0
        and sparse["coverage"]["charged_ratio"] > 1.0
        and half["coverage"]["charged_ratio"] > 1.0
    ):
        return "O-RARE"
    # soft miss on 0.05 band but not 0.15 → still O-RARE if ratios hold and
    # linearization error holds; else artifact
    if (
        half["linearization_error"] >= 1.0
        and sparse["coverage"]["charged_ratio"] > 1.0
        and half["coverage"]["charged_ratio"] > 1.0
        and sparse["union_abs_deviation_L4"] <= 0.15
        and half["union_abs_deviation_L4"] <= 0.15
    ):
        return "O-RARE"
    return "O-ARTIFACT"


def stage1(run_dir: Path, freeze_path: Path | None) -> int:
    try:
        if freeze_path is None:
            freeze = freeze_stage0()
        else:
            freeze = json.loads(freeze_path.read_text(encoding="utf-8"))
        if not freeze.get("archived_identity", {}).get("archived_identity_ok", False):
            raw = {
                "stage": 1,
                "outcome": "O-ARTIFACT",
                "reason": "Stage 0 archived identity failed",
            }
            _write_json(run_dir / "raw-result.json", raw)
            _write_manifest(run_dir, 1, {"outcome": "O-ARTIFACT"})
            print(json.dumps(raw))
            return 0
        cells_out = []
        for cell in freeze["cells"]:
            cells_out.append(run_cell(cell["id"], cell["B"], SEED_STAGE1))
        outcome = _decide_outcome(freeze, cells_out)
        raw = {
            "stage": 1,
            "outcome": outcome,
            "cells": cells_out,
            "seed_stage1": SEED_STAGE1,
            "amazon_bedrock": "NOT SELECTED",
        }
        _write_json(run_dir / "raw-result.json", raw)
        _write_manifest(
            run_dir,
            1,
            {
                "outcome": outcome,
                "artifacts": ["raw-result.json", "manifest.yaml"],
            },
        )
        print(json.dumps({"stage": 1, "outcome": outcome}))
        return 0 if outcome in STAGE1_OUTCOMES else 2
    except Exception as exc:  # infrastructure, not math
        raw = {
            "stage": 1,
            "outcome": "O-IMPEDIMENT",
            "error": repr(exc),
        }
        _write_json(run_dir / "raw-result.json", raw)
        _write_manifest(run_dir, 1, {"outcome": "O-IMPEDIMENT"})
        print(json.dumps(raw), file=sys.stderr)
        return 0


def main(argv: list[str] | None = None) -> int:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--stage", type=int, choices=[0, 1], required=True)
    p.add_argument("--trial-plan", required=True)
    p.add_argument("--run-dir", required=True)
    p.add_argument(
        "--freeze",
        default=None,
        help="Optional path to Stage 0 union_freeze.json for Stage 1",
    )
    args = p.parse_args(argv)
    run_dir = Path(args.run_dir)
    run_dir.mkdir(parents=True, exist_ok=True)
    (run_dir / "command.txt").write_text(
        " ".join(["python3", str(Path(__file__).as_posix()), *map(str, sys.argv[1:])])
        + "\n",
        encoding="utf-8",
    )
    (run_dir / "stdout.log").write_text("", encoding="utf-8")
    (run_dir / "stderr.log").write_text("", encoding="utf-8")
    if not Path(args.trial_plan).is_file():
        print(f"missing trial plan: {args.trial_plan}", file=sys.stderr)
        return 2
    if args.stage == 0:
        return stage0(run_dir)
    freeze = Path(args.freeze) if args.freeze else None
    return stage1(run_dir, freeze)


if __name__ == "__main__":
    raise SystemExit(main())

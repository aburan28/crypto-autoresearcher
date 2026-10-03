#!/usr/bin/env python3
"""Independent checker for EXP-CERTBIN-1bfef5 Stages 0-1 run artifacts."""
from __future__ import annotations

import json
import sys
from pathlib import Path

_IMPL = Path(__file__).resolve().parent
if str(_IMPL) not in sys.path:
    sys.path.insert(0, str(_IMPL))

from run import EXPERIMENT_ID, OUTCOMES, PINNED, REPO, sha256_file  # noqa: E402

EXP_ROOT = Path(__file__).resolve().parents[1]


def main() -> int:
    if len(sys.argv) != 2:
        print("usage: check.py <run_dir>", file=sys.stderr)
        return 2
    run_dir = Path(sys.argv[1])
    errs: list[str] = []
    raw_path = run_dir / "raw-result.json"
    man_path = run_dir / "manifest.yaml"
    if not raw_path.is_file() or raw_path.stat().st_size == 0:
        errs.append("missing/empty raw-result.json")
    if not man_path.is_file() or man_path.stat().st_size == 0:
        errs.append("missing/empty manifest.yaml")
    if errs:
        print("FAIL:", *errs, sep="\n  ")
        return 1

    raw = json.loads(raw_path.read_text(encoding="utf-8"))
    if raw.get("experiment_id") != EXPERIMENT_ID:
        errs.append("experiment_id mismatch")
    if raw.get("amazon_bedrock") not in ("NOT_USED", "NOT SELECTED"):
        errs.append("Bedrock marker missing/invalid")
    claims = raw.get("claims") or {}
    if claims.get("break") or claims.get("exponent_move"):
        errs.append("forbidden break/exponent claim present")

    stage = raw.get("stage")
    if stage == 0:
        for rel in (
            "stage0/preregistered-predictions.json",
            "stage0/propositions-note.md",
            "stage0/precommit-hashes.json",
            "stage0/instrument-pins.json",
            "stage0/seed-stream.json",
        ):
            if not (EXP_ROOT / rel).is_file():
                errs.append(f"missing freeze file {rel}")
        if not raw.get("worksheet_ok"):
            errs.append("worksheet_ok is not true")
        for rel, want in PINNED.items():
            path = REPO / rel
            if not path.is_file() or sha256_file(path) != want:
                errs.append(f"pinned instrument drift: {rel}")
    elif stage == 1:
        outcome = raw.get("outcome")
        if outcome not in OUTCOMES:
            errs.append(f"outcome {outcome!r} not in {OUTCOMES}")
        results = EXP_ROOT / "RESULTS.md"
        if outcome in OUTCOMES:
            if not results.is_file():
                errs.append("missing RESULTS.md")
            else:
                text = results.read_text(encoding="utf-8")
                hits = [lab for lab in OUTCOMES if f"**{lab}**" in text]
                if len(hits) != 1:
                    errs.append(
                        f"RESULTS.md must name exactly one O-* label, found {hits}"
                    )
                elif hits[0] != outcome:
                    errs.append("RESULTS.md label disagrees with raw-result outcome")
        if (
            (EXP_ROOT / "stage0/precommit-hashes.json").is_file()
            and raw.get("reason") != "Stage-0 freeze artifacts missing"
        ):
            for rel in (
                "stage1/c-pin.json",
                "stage1/c-self.json",
                "stage1/archived-label-census.json",
                "stage1/arm-a-admission.json",
            ):
                if not (EXP_ROOT / rel).is_file():
                    errs.append(f"missing {rel}")
            # After AMD-20261003-9ef431, executed arm-(a) must leave a basis-swap receipt.
            admission = json.loads(
                (EXP_ROOT / "stage1/arm-a-admission.json").read_text(encoding="utf-8")
            )
            if admission.get("arm_a_executed") is True:
                if not (run_dir / "arm-a-basis-swap.json").is_file() and not (
                    EXP_ROOT / "stage1/arm-a-basis-swap.json"
                ).is_file():
                    errs.append("arm_a_executed true but arm-a-basis-swap.json missing")
                if raw.get("arm_a_agreement") in (None, ""):
                    errs.append("arm_a_executed true but arm_a_agreement unset in raw-result")
            if claims.get("break") or claims.get("exponent_move"):
                errs.append("forbidden break/exponent after arm-(a)")
            if outcome == "O-ARM-A-PASS" and raw.get("arm_a_agreement") != "288/288":
                errs.append("O-ARM-A-PASS requires arm_a_agreement 288/288")
            if outcome == "O-E-SET":
                errs.append(
                    "O-E-SET forbidden under Stages 0-1 card (Stage 2 not authorized)"
                )
    else:
        errs.append(f"unknown stage {stage!r}")

    if errs:
        print("FAIL:", *errs, sep="\n  ")
        return 1
    print("PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

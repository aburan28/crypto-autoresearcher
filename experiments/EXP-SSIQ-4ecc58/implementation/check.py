#!/usr/bin/env python3
"""Independent checker for EXP-SSIQ-4ecc58 run artifacts."""
from __future__ import annotations

import json
import sys
from pathlib import Path

_IMPL = Path(__file__).resolve().parent
if str(_IMPL) not in sys.path:
    sys.path.insert(0, str(_IMPL))

from meters import cayley_holonomy_zn  # noqa: E402
from ntheory import miller_rabin, split_ij  # noqa: E402

EXPERIMENT_ID = "EXP-SSIQ-4ecc58"
OUTCOMES = {
    "O-CLOSED",
    "O-OPEN",
    "O-MIXED",
    "O-INCONCLUSIVE",
    "O-ARTIFACT",
    "O-IMPEDIMENT",
    "O-STAGE0-OK",
}


def main() -> int:
    if len(sys.argv) != 2:
        print("usage: check.py <run_dir>", file=sys.stderr)
        return 2
    run_dir = Path(sys.argv[1])
    raw_path, man_path = run_dir / "raw-result.json", run_dir / "manifest.yaml"
    errs: list[str] = []
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
    root = Path(__file__).resolve().parents[1]
    if stage == 0:
        for rel in ("stage0/preregistered-predictions.json", "stage0/fixtures.json"):
            if not (root / rel).is_file():
                errs.append(f"missing freeze file {rel}")
        if (root / "stage0" / "preregistered-predictions.json").is_file():
            pred = json.loads((root / "stage0" / "preregistered-predictions.json").read_text())
            if pred.get("stage2_authorized") or pred.get("crypto_deuring_authorized"):
                errs.append("Stage 2 / Deuring must not be authorized under this card")
            cells = pred.get("cells")
            if not isinstance(cells, list):
                errs.append("cells must be a list (integer fields, not string-keyed n map)")
            else:
                for cell in cells:
                    if not isinstance(cell.get("N"), int) or not isinstance(cell.get("p"), int):
                        errs.append(f"cell {cell.get('id')} N/p must be ints")
            primes = pred.get("panel_primes") or []
            if not primes or not all(isinstance(p, int) and miller_rabin(p) for p in primes):
                errs.append("panel_primes must be ints passing Miller-Rabin")
            formula = pred.get("formula") or ""
            if "E-CLOSED" not in formula:
                errs.append("formula mismatch")
        if (root / "stage0" / "fixtures.json").is_file():
            fx = json.loads((root / "stage0" / "fixtures.json").read_text())
            cay = cayley_holonomy_zn(12, [1, 5])
            if not cay.get("abelian") or not cay.get("full"):
                errs.append("checker Cayley fixture failed")
            rec = fx.get("cayley_z12") or {}
            if rec.get("order") != cay.get("order"):
                errs.append("cayley order mismatch vs independent recompute")
            iso = fx.get("iso_pN") or {}
            p, N = int(iso.get("p") or 0), int(iso.get("N") or 0)
            if p and N and split_ij(N, p) is None:
                errs.append("iso split_ij failed on frozen p,N")
        if raw.get("outcome") not in ("O-STAGE0-OK", "O-ARTIFACT"):
            errs.append(f"bad stage0 outcome {raw.get('outcome')!r}")
    elif stage == 1:
        for rel in ("stage1/panels.json", "stage1/control-table.json", "RESULTS.md"):
            if not (root / rel).is_file():
                errs.append(f"missing {rel}")
        outcome = raw.get("outcome")
        if outcome not in OUTCOMES:
            errs.append(f"bad outcome {outcome!r}")
        if outcome in ("O-CLOSED", "O-OPEN", "O-MIXED"):
            if not (root / "stage0" / "preregistered-predictions.json").is_file():
                errs.append("scientific outcome without Stage-0 freeze")
        md = (root / "RESULTS.md").read_text(encoding="utf-8") if (root / "RESULTS.md").is_file() else ""
        if md and outcome and f"outcome: {outcome}" not in md:
            errs.append("RESULTS.md does not name raw outcome")
    else:
        errs.append(f"bad stage {stage!r}")
    if errs:
        print("FAIL:", *errs, sep="\n  ")
        return 1
    print("OK")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

#!/usr/bin/env python3
"""Independent checker for EXP-SSIQ-c0a99a run artifacts."""
from __future__ import annotations

import json
import sys
from pathlib import Path

_IMPL = Path(__file__).resolve().parent
if str(_IMPL) not in sys.path:
    sys.path.insert(0, str(_IMPL))

from meters import cover_formula, k_both  # noqa: E402
from ntheory import miller_rabin, split_window_x  # noqa: E402

EXPERIMENT_ID = "EXP-SSIQ-c0a99a"
OUTCOMES = {
    "O-REPRESENTATION",
    "O-NEGLIGIBLE",
    "O-MIXED",
    "O-INCONCLUSIVE",
    "O-ARTIFACT",
    "O-IMPEDIMENT",
    "O-STAGE0-OK",
}
P_I = 5 * (1 << 248) - 1
P_REG = (1 << 40) - 87
B20 = 1 << 20


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
            if pred.get("arm_ii_authorized") or pred.get("arm_iii_authorized"):
                errs.append("Arm II/III must not be authorized under this card")
            cells = pred.get("cells")
            if not isinstance(cells, list):
                errs.append("cells must be a list (integer fields, not string-keyed n map)")
            else:
                for cell in cells:
                    if not isinstance(cell.get("B"), int) or not isinstance(cell.get("p"), int):
                        errs.append(f"cell {cell.get('id')} B/p must be ints")
            if pred.get("formula") != "P_cover = 1 - (1 - rho^2)^{k/2}":
                errs.append("formula mismatch")
            if not miller_rabin(int(pred.get("p_i") or 0)):
                errs.append("p_i not prime")
        if (root / "stage0" / "fixtures.json").is_file():
            fx = json.loads((root / "stage0" / "fixtures.json").read_text())
            k2 = fx.get("k2") or {}
            if not k2.get("twin_ok"):
                errs.append("k2 fixture twin_ok false")
            fac = [(int(p), int(e)) for p, e in k2.get("factors") or []]
            d = int(k2.get("d") or 0)
            X = int(k2.get("X") or split_window_x(P_I, B20))
            met = k_both(fac, d, X)
            if not met["agree"] or met["k_a"] != 2:
                errs.append("stage0 k2 recompute failed")
            formula = cover_formula(2, 0.2)
            if abs(formula - (0.2**2)) > 1e-12:
                errs.append("k=2 formula is not rho^2")
        if raw.get("outcome") not in ("O-STAGE0-OK", "O-ARTIFACT"):
            errs.append(f"bad stage0 outcome {raw.get('outcome')!r}")
    elif stage == 1:
        for rel in ("stage1/panels.json", "stage1/control-table.json", "RESULTS.md"):
            if not (root / rel).is_file():
                errs.append(f"missing {rel}")
        outcome = raw.get("outcome")
        if outcome not in OUTCOMES:
            errs.append(f"bad outcome {outcome!r}")
        if outcome in ("O-REPRESENTATION", "O-NEGLIGIBLE", "O-MIXED"):
            if not (root / "stage0" / "preregistered-predictions.json").is_file():
                errs.append("scientific outcome without Stage-0 freeze")
        md = (root / "RESULTS.md").read_text(encoding="utf-8") if (root / "RESULTS.md").is_file() else ""
        labels = [o for o in OUTCOMES if f"outcome: {o}" in md or f"**{o}**" in md]
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

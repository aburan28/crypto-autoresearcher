#!/usr/bin/env python3
"""Independent checker for EXP-BINSTD-cec99c. Recomputes both orbit meters."""
from __future__ import annotations

import json
import sys
from pathlib import Path

_IMPL = Path(__file__).resolve().parent
if str(_IMPL) not in sys.path:
    sys.path.insert(0, str(_IMPL))

from curve import Curve  # noqa: E402
from gf2 import field_for  # noqa: E402
from orbit_a import unique_orbit_count_a  # noqa: E402
from orbit_b import unique_orbit_count_b  # noqa: E402

EXPERIMENT_ID = "EXP-BINSTD-cec99c"
OUTCOMES = {
    "O-SUPPORT",
    "O-FAIL-BAND",
    "O-INCONCLUSIVE",
    "O-ARTIFACT",
    "O-IMPEDIMENT",
    "O-STAGE0-OK",
}
RHO_NUM, RHO_DEN = 1, 2


def digit_keys(obj, path="$", errs=None):
    if errs is None:
        errs = []
    if isinstance(obj, dict):
        for k, v in obj.items():
            if isinstance(k, str) and k.isdigit():
                errs.append(f"{path}: n-as-object-key {k!r}")
            digit_keys(v, f"{path}.{k}", errs)
    elif isinstance(obj, list):
        for i, v in enumerate(obj):
            digit_keys(v, f"{path}[{i}]", errs)
    return errs


def main() -> int:
    if len(sys.argv) != 2:
        print("usage: check.py <run_dir>", file=sys.stderr)
        return 2
    run_dir = Path(sys.argv[1])
    raw_path, man_path = run_dir / "raw-result.json", run_dir / "manifest.yaml"
    errs = []
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
    if claims.get("break") or claims.get("exponent_move") or claims.get("n_ge_131"):
        errs.append("forbidden break/exponent/n>=131 claim present")
    stage = raw.get("stage")
    root = Path(__file__).resolve().parents[1]
    if stage == 0:
        for rel in ("stage0/preregistered-predictions.json", "stage0/v-catalog.json"):
            p = root / rel
            if not p.is_file():
                errs.append(f"missing freeze file {rel}")
                continue
            doc = json.loads(p.read_text(encoding="utf-8"))
            errs.extend(digit_keys(doc, rel))
        catp = root / "stage0" / "v-catalog.json"
        if catp.is_file():
            cat = json.loads(catp.read_text(encoding="utf-8"))
            cells = cat.get("cells")
            if not isinstance(cells, list):
                errs.append("v-catalog.cells must be a list")
            else:
                ns = []
                for i, cell in enumerate(cells):
                    n = cell.get("n")
                    if not isinstance(n, int) or isinstance(n, bool):
                        errs.append(f"cells[{i}].n must be JSON integer, got {n!r}")
                    else:
                        ns.append(n)
                    if not isinstance(cell.get("fb_size"), int):
                        errs.append(f"cells[{i}].fb_size not int")
                if ns != [17, 23, 31]:
                    errs.append(f"freeze n list {ns} != [17,23,31]")
                row = next((c for c in cells if c.get("n") == 17), None)
                if row:
                    F = field_for(17)
                    curve = Curve(F, row["curve_A"], row["curve_B"])
                    fb = [(p["x"], p["y"]) for p in row["fb_points"]]
                    if fb:
                        rels = [tuple(sorted(fb[: min(3, len(fb))]))]
                        if unique_orbit_count_a(F, 17, rels) != unique_orbit_count_b(F, 17, rels):
                            errs.append("stage0 twin orbit recompute disagree")
                        if not curve.on_curve(fb[0]):
                            errs.append("fb[0] not on curve")
        predp = root / "stage0" / "preregistered-predictions.json"
        if predp.is_file():
            pred = json.loads(predp.read_text(encoding="utf-8"))
            rho = pred.get("rho") or {}
            if rho.get("numer") != RHO_NUM or rho.get("denom") != RHO_DEN:
                errs.append("rho not frozen at 1/2")
            if not isinstance(pred.get("surplus_multipliers"), list):
                errs.append("surplus_multipliers must be a list")
        if raw.get("outcome") not in OUTCOMES:
            errs.append(f"bad outcome {raw.get('outcome')!r}")
        if raw.get("outcome") == "O-STAGE0-OK" and not raw.get("twin_ok"):
            errs.append("O-STAGE0-OK without twin_ok")
    elif stage == 1:
        for rel in ("stage1/panels.json", "stage1/control-table.json", "RESULTS.md"):
            if not (root / rel).is_file():
                errs.append(f"missing {rel}")
        outcome = raw.get("outcome")
        if outcome not in OUTCOMES:
            errs.append(f"bad outcome {outcome!r}")
        panp = root / "stage1" / "panels.json"
        if panp.is_file():
            panels = json.loads(panp.read_text(encoding="utf-8"))
            errs.extend(digit_keys(panels, "stage1/panels.json"))
            cells = panels.get("cells")
            if not isinstance(cells, list):
                errs.append("panels.cells must be a list")
            else:
                F = field_for(17)
                for i, cell in enumerate(cells):
                    if cell.get("n") != 17 or not isinstance(cell.get("n"), int):
                        errs.append(f"panels[{i}].n must be integer 17")
                    if cell.get("unique_a") != cell.get("unique_b"):
                        errs.append(f"panels[{i}] twin unique disagree")
                    if outcome in ("O-SUPPORT", "O-FAIL-BAND"):
                        ua, rawc = cell.get("unique_a"), cell.get("raw")
                        if not isinstance(ua, int) or not isinstance(rawc, int) or rawc < 1:
                            errs.append(f"panels[{i}] missing counts")
                        else:
                            holds = ua * RHO_DEN >= rawc * RHO_NUM
                            if bool(cell.get("band_holds")) != holds:
                                errs.append(f"panels[{i}] band_holds mismatch vs 1/2")
                            if outcome == "O-SUPPORT" and not holds:
                                errs.append("O-SUPPORT but a cell fails ρ=1/2")
                    if not cell.get("null_R_is_one") and outcome in ("O-SUPPORT", "O-FAIL-BAND"):
                        errs.append(f"panels[{i}] null identity R != 1")
        if outcome in ("O-SUPPORT", "O-FAIL-BAND") and not raw.get("twin_ok"):
            errs.append("band outcome without twin_ok")
        if outcome in ("O-SUPPORT", "O-FAIL-BAND") and not raw.get("surplus_met"):
            errs.append("band outcome without surplus floor")
    else:
        errs.append(f"unknown stage {stage!r}")
    if errs:
        print("FAIL:", *errs, sep="\n  ")
        return 1
    print("OK")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

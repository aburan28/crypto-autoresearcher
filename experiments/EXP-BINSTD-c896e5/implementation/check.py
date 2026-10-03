#!/usr/bin/env python3
"""Independent checker for EXP-BINSTD-c896e5. Recomputes TableField yield."""
from __future__ import annotations

import json
import sys
from pathlib import Path

_IMPL = Path(__file__).resolve().parent
if str(_IMPL) not in sys.path:
    sys.path.insert(0, str(_IMPL))

from curve import Curve  # noqa: E402
from gf2 import field_for  # noqa: E402
from yield_meter import collect_relations, unique_count  # noqa: E402

EXPERIMENT_ID = "EXP-BINSTD-c896e5"
OUTCOMES = {
    "O-SUPPORT",
    "O-FAIL-BAND",
    "O-INCONCLUSIVE",
    "O-ARTIFACT",
    "O-IMPEDIMENT",
    "O-STAGE0-OK",
}
RHO_NUM, RHO_DEN = 1, 1


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
                ns_ells = []
                for i, cell in enumerate(cells):
                    n = cell.get("n")
                    ell = cell.get("ell")
                    if not isinstance(n, int) or isinstance(n, bool):
                        errs.append(f"cells[{i}].n must be JSON integer, got {n!r}")
                    if not isinstance(ell, int) or isinstance(ell, bool):
                        errs.append(f"cells[{i}].ell must be JSON integer, got {ell!r}")
                    else:
                        ns_ells.append((n, ell))
                    if not isinstance(cell.get("fb_size"), int):
                        errs.append(f"cells[{i}].fb_size not int")
                if ns_ells != [(17, 3), (17, 4), (19, 3), (19, 4), (23, 3), (23, 4)]:
                    errs.append(f"freeze cells {ns_ells} mismatch")
                row = next((c for c in cells if c.get("n") == 17 and c.get("ell") == 3), None)
                if row:
                    F = field_for(17, table=True)
                    curve = Curve(F, row["curve_A"], row["curve_B"])
                    fb = [(p["x"], p["y"]) for p in row["fb_points"]]
                    if fb:
                        if not curve.on_curve(fb[0]):
                            errs.append("fb[0] not on curve")
                        ra = collect_relations(curve, fb, 17, nagao_only=False)
                        rb = collect_relations(
                            Curve(field_for(17, table=False), row["curve_A"], row["curve_B"]),
                            fb,
                            17,
                            nagao_only=False,
                        )
                        if unique_count(ra) != unique_count(rb) or ra != rb:
                            errs.append("stage0 twin chained recompute disagree")
        predp = root / "stage0" / "preregistered-predictions.json"
        if predp.is_file():
            pred = json.loads(predp.read_text(encoding="utf-8"))
            rho = pred.get("rho") or {}
            if rho.get("numer") != RHO_NUM or rho.get("denom") != RHO_DEN:
                errs.append("rho not frozen at 1/1")
            ac = pred.get("authorized_stage1_cells")
            if not isinstance(ac, list) or not ac or ac[0].get("n") != 17:
                errs.append("authorized_stage1_cells must be a list with n=17")
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
            if not isinstance(cells, list) or len(cells) != 1:
                errs.append("panels.cells must be a one-row list")
            else:
                cell = cells[0]
                if cell.get("n") != 17 or not isinstance(cell.get("n"), int):
                    errs.append("panels[0].n must be integer 17")
                if cell.get("ell") != 3 or not isinstance(cell.get("ell"), int):
                    errs.append("panels[0].ell must be integer 3")
                catp = root / "stage0" / "v-catalog.json"
                if catp.is_file():
                    cat = json.loads(catp.read_text(encoding="utf-8"))
                    row = next(
                        c for c in cat["cells"] if c.get("n") == 17 and c.get("ell") == 3
                    )
                    F = field_for(17, table=True)
                    curve = Curve(F, row["curve_A"], row["curve_B"])
                    fb = [(p["x"], p["y"]) for p in row["fb_points"]]
                    nagao = collect_relations(curve, fb, 17, nagao_only=True)
                    chained = collect_relations(curve, fb, 17, nagao_only=False)
                    if unique_count(nagao) != cell.get("nagao_unique"):
                        errs.append("nagao unique mismatch vs TableField recompute")
                    if unique_count(chained) != cell.get("chained_unique"):
                        errs.append("chained unique mismatch vs TableField recompute")
                if outcome in ("O-SUPPORT", "O-FAIL-BAND"):
                    rps_n, rps_c = cell.get("nagao_rps"), cell.get("chained_rps")
                    if not isinstance(rps_n, (int, float)) or not isinstance(rps_c, (int, float)):
                        errs.append("missing rps")
                    elif rps_c > 0:
                        holds = rps_n * RHO_DEN >= rps_c * RHO_NUM
                        if bool(cell.get("band_holds")) != holds:
                            errs.append("band_holds mismatch vs ρ=1")
                        if outcome == "O-SUPPORT" and not holds:
                            errs.append("O-SUPPORT but R < ρ")
                        if outcome == "O-FAIL-BAND" and holds:
                            errs.append("O-FAIL-BAND but R >= ρ")
        if outcome in ("O-SUPPORT", "O-FAIL-BAND") and not raw.get("twin_ok"):
            errs.append("band outcome without twin_ok")
        if outcome == "O-INCONCLUSIVE" and not raw.get("both_zero"):
            errs.append("O-INCONCLUSIVE without both-zero relations")
    else:
        errs.append(f"unknown stage {stage!r}")
    if errs:
        print("FAIL:", *errs, sep="\n  ")
        return 1
    print("OK")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

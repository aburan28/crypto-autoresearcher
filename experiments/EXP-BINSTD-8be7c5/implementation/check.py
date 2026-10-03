#!/usr/bin/env python3
"""Independent checker for EXP-BINSTD-8be7c5. Does not import run.py orchestration."""
from __future__ import annotations

import json
import sys
from pathlib import Path

_IMPL = Path(__file__).resolve().parent
if str(_IMPL) not in sys.path:
    sys.path.insert(0, str(_IMPL))

from encode_s3 import encode_n_var  # noqa: E402
from gf2n import Field  # noqa: E402
from product_space import dim_vv_agree, poly_basis  # noqa: E402

EXPERIMENT_ID = "EXP-BINSTD-8be7c5"
OUTCOMES = {
    "O-SUPPORT",
    "O-FAIL-BAND",
    "O-INCONCLUSIVE",
    "O-ARTIFACT",
    "O-IMPEDIMENT",
    "O-STAGE0-OK",
    "O-NULL-FAIL",
}
MODULI = {
    17: (1 << 17) | (1 << 3) | 1,
    19: (1 << 19) | (1 << 5) | (1 << 2) | (1 << 1) | 1,
}
CURVE_B = {17: 1, 19: 1}
XR = {17: 0x1A3F, 19: 0x2B41}
BAND = 0.5


def binom(n: int, k: int) -> int:
    if k < 0 or k > n:
        return 0
    k = min(k, n - k)
    acc = 1
    for t in range(k):
        acc = acc * (n - t) // (t + 1)
    return acc


def combinadic(sorted_combo: list[int]) -> int:
    return sum(binom(c, i + 1) for i, c in enumerate(sorted_combo))


def median_a(xs: list[float]) -> float | None:
    if not xs:
        return None
    ys = sorted(xs)
    m = len(ys)
    return float(ys[m // 2]) if m % 2 else 0.5 * (ys[m // 2 - 1] + ys[m // 2])


def median_b(xs: list[float]) -> float | None:
    if not xs:
        return None
    ys = list(xs)
    n = len(ys)
    for i in range(n):
        j = i
        v = ys[i]
        while j > 0 and ys[j - 1] > v:
            ys[j] = ys[j - 1]
            j -= 1
        ys[j] = v
    return float(ys[n // 2]) if n % 2 else 0.5 * (ys[n // 2 - 1] + ys[n // 2])


def main() -> int:
    if len(sys.argv) != 2:
        print("usage: check.py <run_dir>", file=sys.stderr)
        return 2
    run_dir = Path(sys.argv[1])
    raw_path = run_dir / "raw-result.json"
    man_path = run_dir / "manifest.yaml"
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
    if claims.get("break") or claims.get("exponent_move") or claims.get("ecdlp_solve"):
        errs.append("forbidden break/exponent/solve claim present")

    stage = raw.get("stage")
    root = Path(__file__).resolve().parents[1]
    outcome = raw.get("outcome")
    if outcome not in OUTCOMES:
        errs.append(f"outcome not in set: {outcome!r}")

    if stage == 0:
        for rel in (
            "stage0/preregistered-predictions.json",
            "stage0/v-catalog.json",
            "stage0/target-catalog.json",
            "stage0/launcher-probe.json",
        ):
            if not (root / rel).is_file():
                errs.append(f"missing freeze file {rel}")
        pred_p = root / "stage0" / "preregistered-predictions.json"
        if pred_p.is_file():
            pred = json.loads(pred_p.read_text())
            if pred.get("band") != BAND:
                errs.append("frozen band is not 0.5")
            if not pred.get("written_before_any_scientific_timing"):
                errs.append("band not marked pre-registered")
        vcat_p = root / "stage0" / "v-catalog.json"
        tcat_p = root / "stage0" / "target-catalog.json"
        if vcat_p.is_file():
            cell = json.loads(vcat_p.read_text())["cells"]["n17_l3"]
            F = Field(17, MODULI[17])
            basis = cell["basis"]
            if basis != poly_basis(3):
                errs.append("frozen V is not poly ell=3")
            da, db, dok = dim_vv_agree(basis, F)
            na, nb, nok, _ = encode_n_var(F, CURVE_B[17], basis, XR[17])
            if not (dok and nok):
                errs.append("independent twin disagree on stage0 probe")
            if cell.get("probe_dimVV", {}).get("a") != da:
                errs.append("stage0 probe_dimVV mismatch vs independent recompute")
        if tcat_p.is_file():
            tcat = json.loads(tcat_p.read_text())
            ids = [t["target_id"] for t in tcat["targets"]]
            if len(ids) < 20:
                errs.append("target catalog < 20")
            r = combinadic(ids)
            if tcat.get("combinadic", {}).get("a") != r:
                errs.append("combinadic twin mismatch vs independent recompute")
    elif stage == 1:
        for rel in ("stage1/timings.json", "stage1/control-table.json", "RESULTS.md"):
            if not (root / rel).is_file():
                errs.append(f"missing {rel}")
        timings_p = root / "stage1" / "timings.json"
        if timings_p.is_file():
            timings = json.loads(timings_p.read_text())
            if timings.get("admitted"):
                xs = timings.get("T_n1") or []
                if xs:
                    if median_a(xs) != median_b(xs):
                        errs.append("dual median aggregators disagree on T_n1")
            else:
                if outcome not in {"O-IMPEDIMENT", "O-ARTIFACT"}:
                    errs.append("missing launchers must be O-IMPEDIMENT/O-ARTIFACT, not a band verdict")
        results = (root / "RESULTS.md").read_text(encoding="utf-8") if (root / "RESULTS.md").is_file() else ""
        if outcome and outcome not in results:
            errs.append("RESULTS.md missing outcome label")
    elif stage == 2:
        for rel in ("stage2/timings.json", "stage2/null-control.json", "stage2/RESULTS.md"):
            if not (root / rel).is_file():
                errs.append(f"missing {rel}")
        if outcome in {"O-SUPPORT", "O-FAIL-BAND"} and not json.loads(
            (root / "stage2" / "timings.json").read_text()
        ).get("admitted"):
            errs.append("band verdict without admitted launchers")
    else:
        errs.append(f"unknown stage {stage!r}")

    if errs:
        print("FAIL:", *errs, sep="\n  ")
        return 1
    print("OK")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

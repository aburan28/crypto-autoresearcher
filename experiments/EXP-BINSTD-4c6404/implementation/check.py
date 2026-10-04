#!/usr/bin/env python3
"""Independent checker for EXP-BINSTD-4c6404. Does not import run.py orchestration."""
from __future__ import annotations

import json
import sys
from pathlib import Path

_IMPL = Path(__file__).resolve().parent
if str(_IMPL) not in sys.path:
    sys.path.insert(0, str(_IMPL))

from gf2la import dense_ge_solve, matrix_sha256, matvec, median_insert, median_sort  # noqa: E402
from matrices import R_N, ROW_WEIGHT, SURPLUS  # noqa: E402

EXPERIMENT_ID = "EXP-BINSTD-4c6404"
TAU = 1.0
OUTCOMES = {
    "O-SUPPORT",
    "O-FAIL-BAND",
    "O-INCONCLUSIVE",
    "O-ARTIFACT",
    "O-IMPEDIMENT",
    "O-STAGE0-OK",
    "O-NULL-FAIL",
}


def combinadic(sorted_combo: list[int]) -> int:
    def binom(n: int, k: int) -> int:
        if k < 0 or k > n:
            return 0
        k = min(k, n - k)
        acc = 1
        for t in range(k):
            acc = acc * (n - t) // (t + 1)
        return acc

    return sum(binom(c, i + 1) for i, c in enumerate(sorted_combo))


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
    if raw.get("magma_sage_auxin") not in ("NOT_USED", None):
        errs.append("Magma/Sage/AUXIN must not be a success path")

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
            if pred.get("tau") != TAU:
                errs.append("frozen tau is not 1.0")
            if not pred.get("written_before_any_scientific_timing"):
                errs.append("tau not marked pre-registered")
            if pred.get("r_n") != R_N:
                errs.append("r_n freeze mismatch")
            if pred.get("row_weight") != ROW_WEIGHT:
                errs.append("row_weight freeze mismatch")
        tcat_p = root / "stage0" / "target-catalog.json"
        if tcat_p.is_file():
            tcat = json.loads(tcat_p.read_text())
            ids = sorted(t["target_id"] for t in tcat["targets"])
            r = combinadic(ids)
            if tcat.get("combinadic", {}).get("a") != r:
                errs.append("combinadic twin mismatch vs independent recompute")
        probe_p = root / "stage0" / "launcher-probe.json"
        if probe_p.is_file():
            probe = json.loads(probe_p.read_text())
            if not probe.get("python_dense_ge") or not probe.get("python_wiedemann"):
                errs.append("python dual solvers not admitted at freeze")
            if probe.get("magma") or probe.get("sage") or probe.get("auxin"):
                errs.append("forbidden solver marked present")
        if outcome != "O-STAGE0-OK":
            if outcome not in {"O-ARTIFACT"}:
                errs.append("stage0 outcome must be O-STAGE0-OK or O-ARTIFACT")
    elif stage in (1, 2):
        rel = "stage1/timings.json" if stage == 1 else "stage2/timings.json"
        timings_p = root / rel
        if not timings_p.is_file():
            errs.append(f"missing {rel}")
        else:
            timings = json.loads(timings_p.read_text())
            if not timings.get("admitted"):
                if outcome not in {"O-IMPEDIMENT", "O-ARTIFACT"}:
                    errs.append("unadmitted solvers must not yield a band verdict")
            races = timings.get("races") or []
            for rec in races:
                n = rec.get("n")
                rdim = rec.get("r")
                if rdim != R_N.get(n):
                    errs.append(f"r mismatch for n={n}")
                    break
                # Re-verify stored solution against stored b using GE on a dummy
                # cannot restore A from hash alone; check dual medians and tau use.
            cells = timings.get("cells") or []
            for c in cells:
                xs_w = [
                    x["wall_wiedemann_perf"]
                    for x in races
                    if x.get("n") == c.get("n") and x.get("surplus") == c.get("surplus")
                ]
                xs_d = [
                    x["wall_dense_perf"]
                    for x in races
                    if x.get("n") == c.get("n") and x.get("surplus") == c.get("surplus")
                ]
                if xs_w:
                    if median_sort(xs_w) != median_insert(xs_w):
                        errs.append("dual median aggregators disagree on Wiedemann")
                    if median_sort(xs_w) != c.get("median_w_sort"):
                        errs.append("reported Wiedemann median mismatch")
                if xs_d:
                    if median_sort(xs_d) != median_insert(xs_d):
                        errs.append("dual median aggregators disagree on dense GE")
                    md = median_sort(xs_d)
                    if md not in (None, 0) and c.get("ratio") is not None:
                        expected = median_sort(xs_w) / md
                        if abs(expected - c["ratio"]) > 1e-12:
                            errs.append("ratio mismatch vs independent recompute")
            if outcome in {"O-SUPPORT", "O-FAIL-BAND"} and not timings.get("admitted"):
                errs.append("band verdict without admitted solvers")
        if stage == 1:
            for rel2 in ("stage1/control-table.json", "RESULTS.md"):
                if not (root / rel2).is_file():
                    errs.append(f"missing {rel2}")
            results = (root / "RESULTS.md").read_text(encoding="utf-8") if (root / "RESULTS.md").is_file() else ""
            if outcome and outcome not in results:
                errs.append("RESULTS.md missing outcome label")
        else:
            for rel2 in ("stage2/null-control.json", "stage2/RESULTS.md"):
                if not (root / rel2).is_file():
                    errs.append(f"missing {rel2}")
            results = (
                (root / "stage2" / "RESULTS.md").read_text(encoding="utf-8")
                if (root / "stage2" / "RESULTS.md").is_file()
                else ""
            )
            if outcome and outcome not in results:
                errs.append("stage2/RESULTS.md missing outcome label")
    else:
        errs.append(f"unknown stage {stage!r}")

    if errs:
        print("FAIL:", *errs, sep="\n  ")
        return 1
    print("OK")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

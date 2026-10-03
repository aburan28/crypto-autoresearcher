#!/usr/bin/env python3
"""EXP-BINSTD-eb9e5e — delta-RSS / allocator-probe refine above OS RSS floor.

Successor of EXP-BINSTD-ff5050 / H-BINSTD-ce918e after EV-BINSTD-0fed43
(decision refine, DEC-20261003-e86acd) and EV-BINSTD-375f15. Keeps frozen
(α,M₀)=(1.0,16777216), twin N_var meters, and shared XOR-SAT pin.

Instrument refine (NA-1 of DEC-20261003-e86acd):
  * process-isolated baseline worker (import + Field only)
  * process-isolated encode+solve worker
  * delta_rss_bytes = max(0, peak_encode - peak_baseline)
  * Stage-0 allocator calibration recovering known bytearray sizes
  * Stage-1 cells n=17, ℓ∈{3,4,5,6} (larger ℓ to push encode above floor)

Primary band continuity: peak_rss ≤ M₀·2^{α·ℓ} (inherited).
Mechanism gate: instrument_clears_floor must be true before O-SUPPORT
may be read as ℓ-channel evidence (tail_check; no support/KN-FIND here).

Memory instrument only. No Magma/Sage/AUXIN/Bedrock. No ECDLP solve.
No n≥131 transfer. No re-run of EXP-BINSTD-ff5050 / cb15a4.
"""
from __future__ import annotations

import argparse
import json
import os
import random
import resource
import statistics
import subprocess
import sys
import time
from pathlib import Path
from typing import Any

_IMPL = Path(__file__).resolve().parent
if str(_IMPL) not in sys.path:
    sys.path.insert(0, str(_IMPL))

from encode_s3 import descend_s3, encode_n_var, n_var_from_eqs  # noqa: E402
from gf2n import Field  # noqa: E402
from product_space import geometric_basis, poly_basis, random_basis  # noqa: E402

EXPERIMENT_ID = "EXP-BINSTD-eb9e5e"
HYPOTHESIS_ID = "H-BINSTD-ce918e"
PARENT_EXP = "EXP-BINSTD-ff5050"
GRANDPARENT_EXP = "EXP-BINSTD-cb15a4"
APPROVED_BY = "DEC-20261003-53838e"
EVIDENCE_CITED = ["EV-BINSTD-0fed43", "EV-BINSTD-375f15"]
PARENT_DECISION = "DEC-20261003-e86acd"
EXP_ROOT = Path(__file__).resolve().parents[1]

MODULI = {
    17: (1 << 17) | (1 << 3) | 1,
    19: (1 << 19) | (1 << 5) | (1 << 2) | (1 << 1) | 1,
    23: (1 << 23) | (1 << 5) | 1,
    29: (1 << 29) | (1 << 2) | 1,
    31: (1 << 31) | (1 << 3) | 1,
}
CURVE_B = {17: 1, 19: 1, 23: 1, 29: 1, 31: 1}
XR = {17: 0x1A3F, 19: 0x2B41, 23: 0x55, 29: 0x71, 31: 0x13}

ALPHA = 1.0
M0_BYTES = 16 * 1024 * 1024
CATALOG_SEED = 2026100343342
STAGE1_CELLS = [(17, 3), (17, 4), (17, 5), (17, 6)]
ALLOCATOR_PROBE_SIZES = [2 * 1024 * 1024, 8 * 1024 * 1024, 16 * 1024 * 1024]
ALLOCATOR_RECOVERY_FRAC = 0.50
CLEAR_FLOOR_DELTA_BYTES = 256 * 1024
CLEAR_FLOOR_MARGIN_BYTES = 512 * 1024
BASELINE_REPEATS = 5
RSS_PROBE = (
    "subprocess RUSAGE_SELF.ru_maxrss*1024 (process-isolated); "
    "delta_rss = max(0, encode_peak - baseline_peak)"
)


def peak_rss_bytes() -> int:
    return int(resource.getrusage(resource.RUSAGE_SELF).ru_maxrss) * 1024


def band_bytes(ell: int) -> int:
    return int(M0_BYTES * (2.0 ** (ALPHA * ell)))


def write_json(path: Path, obj: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    if path.exists():
        raise FileExistsError(f"refusing overwrite: {path}")
    path.write_text(json.dumps(obj, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def write_text(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    if path.exists():
        raise FileExistsError(f"refusing overwrite: {path}")
    path.write_text(text, encoding="utf-8")


def write_yaml_manifest(path: Path, obj: dict) -> None:
    lines = []
    for k, v in obj.items():
        if isinstance(v, bool):
            lines.append(f"{k}: {'true' if v else 'false'}")
        elif isinstance(v, (int, float)):
            lines.append(f"{k}: {v}")
        elif v is None:
            lines.append(f"{k}: null")
        else:
            s = str(v).replace("\n", " ")
            lines.append(f'{k}: "{s}"')
    write_text(path, "\n".join(lines) + "\n")


class _IntRng:
    def __init__(self, seed: int) -> None:
        self._r = random.Random(seed)

    def integers(self, low: int, high: int) -> int:
        return self._r.randrange(low, high)


def frozen_basis(n: int, ell: int) -> list[int]:
    del n
    b = poly_basis(ell)
    if len(b) != ell:
        raise RuntimeError("poly_basis dimension mismatch")
    return b


def encode_and_solve_once(F: Field, B: int, basis: list[int], xR: int) -> dict:
    rss_before = peak_rss_bytes()
    eqs, meta = descend_s3(F, B, basis, xR)
    n_a, n_b, twin_ok, det = n_var_from_eqs(eqs, meta["nv"])
    lin_rows = []
    nv = meta["nv"]
    for row in eqs:
        dense = [0] * nv
        for mask in row:
            if mask == 0:
                continue
            if mask & (mask - 1) == 0:
                idx = mask.bit_length() - 1
                if 0 <= idx < nv:
                    dense[idx] ^= 1
        if any(dense):
            lin_rows.append(dense)
    rank = 0
    nrows = len(lin_rows)
    for col in range(nv):
        pivot = None
        for r in range(rank, nrows):
            if lin_rows[r][col]:
                pivot = r
                break
        if pivot is None:
            continue
        lin_rows[rank], lin_rows[pivot] = lin_rows[pivot], lin_rows[rank]
        for r in range(nrows):
            if r != rank and lin_rows[r][col]:
                for c in range(nv):
                    lin_rows[r][c] ^= lin_rows[rank][c]
        rank += 1
    rss_after = peak_rss_bytes()
    return {
        "N_var_a": n_a,
        "N_var_b": n_b,
        "twin_ok": twin_ok,
        "lin_rank_solve": rank,
        "nv0": meta["nv"],
        "neq": meta["neq"],
        "rss_before_bytes": rss_before,
        "peak_rss_bytes": rss_after,
        "det": {k: det[k] for k in ("lin_rank_a", "lin_rank_b", "nv0") if k in det},
    }


def _worker(payload: dict) -> dict:
    kind = payload["kind"]
    if kind == "baseline":
        n = int(payload["n"])
        _F = Field(n, MODULI[n])
        del _F
        peak = peak_rss_bytes()
        return {
            "kind": "baseline",
            "peak_rss_bytes": peak,
            "rss_mode": "process_isolated",
            "pid": os.getpid(),
            "n": n,
        }
    if kind == "alloc":
        size = int(payload["size"])
        buf = bytearray(size)
        buf[0] = 1
        buf[-1] = 2
        peak = peak_rss_bytes()
        _keep = len(buf)
        del _keep
        return {
            "kind": "alloc",
            "size": size,
            "peak_rss_bytes": peak,
            "rss_mode": "process_isolated",
            "pid": os.getpid(),
        }
    if kind == "real":
        n = int(payload["n"])
        ell = int(payload["ell"])
        basis = list(payload["basis"])
        F = Field(n, MODULI[n])
        na0, nb0, tok0, _ = encode_n_var(F, CURVE_B[n], basis, XR[n])
        measured = encode_and_solve_once(F, CURVE_B[n], basis, XR[n])
        band = band_bytes(ell)
        peak = measured["peak_rss_bytes"]
        return {
            "kind": "real",
            "n": n,
            "ell": ell,
            "basis_shape": "poly",
            "twin_ok": bool(tok0 and measured["twin_ok"]),
            "N_var_a": na0,
            "N_var_b": nb0,
            "peak_rss_bytes": peak,
            "band_bytes": band,
            "band_holds": peak <= band,
            "lin_rank_solve": measured["lin_rank_solve"],
            "nv0": measured["nv0"],
            "neq": measured["neq"],
            "rss_before_bytes": measured["rss_before_bytes"],
            "rss_mode": "process_isolated",
            "pid": os.getpid(),
        }
    raise ValueError(f"unknown worker kind {kind!r}")


def measure_isolated(payload: dict) -> dict:
    cmd = [
        sys.executable,
        str(Path(__file__).resolve()),
        "--worker-json",
        json.dumps(payload, separators=(",", ":")),
    ]
    proc = subprocess.run(
        cmd,
        check=False,
        capture_output=True,
        text=True,
        cwd=str(EXP_ROOT.parents[1]),
    )
    if proc.returncode != 0:
        raise RuntimeError(
            f"isolated worker failed rc={proc.returncode}: {proc.stderr[-2000:]}"
        )
    line = proc.stdout.strip().splitlines()[-1]
    return json.loads(line)


def measure_delta_real(n: int, ell: int, basis: list[int]) -> dict:
    baseline = measure_isolated({"kind": "baseline", "n": n})
    encode = measure_isolated({"kind": "real", "n": n, "ell": ell, "basis": basis})
    base_peak = int(baseline["peak_rss_bytes"])
    enc_peak = int(encode["peak_rss_bytes"])
    delta = max(0, enc_peak - base_peak)
    band = band_bytes(ell)
    return {
        **encode,
        "baseline_peak_rss_bytes": base_peak,
        "delta_rss_bytes": delta,
        "band_bytes": band,
        "band_holds": enc_peak <= band,
        "delta_band_holds": delta <= band,
        "rss_mode": "process_isolated_delta",
        "baseline_pid": baseline.get("pid"),
    }


def stage0(run_dir: Path) -> dict:
    t0 = time.time()
    cells: dict[str, Any] = {}
    twin_ok = True
    rss_probe_ok = True
    allocator_ok = True
    probe_err = None
    baselines: list[int] = []
    alloc_results: list[dict] = []
    os_rss_floor = None

    try:
        for _ in range(BASELINE_REPEATS):
            b = measure_isolated({"kind": "baseline", "n": 17})
            baselines.append(int(b["peak_rss_bytes"]))
        os_rss_floor = int(statistics.median(baselines))
        for size in ALLOCATOR_PROBE_SIZES:
            base = measure_isolated({"kind": "baseline", "n": 17})
            alloc = measure_isolated({"kind": "alloc", "size": size})
            delta = max(0, int(alloc["peak_rss_bytes"]) - int(base["peak_rss_bytes"]))
            recovered = delta >= int(ALLOCATOR_RECOVERY_FRAC * size)
            row = {
                "size": size,
                "baseline_peak_rss_bytes": int(base["peak_rss_bytes"]),
                "alloc_peak_rss_bytes": int(alloc["peak_rss_bytes"]),
                "delta_rss_bytes": delta,
                "recovery_frac_required": ALLOCATOR_RECOVERY_FRAC,
                "recovered": recovered,
            }
            alloc_results.append(row)
            if not recovered and size == ALLOCATOR_PROBE_SIZES[-1]:
                allocator_ok = False
        if not alloc_results:
            rss_probe_ok = False
            probe_err = "no allocator probes"
    except Exception as exc:  # noqa: BLE001
        rss_probe_ok = False
        twin_ok = False
        allocator_ok = False
        probe_err = str(exc)

    for n, ell in STAGE1_CELLS:
        if n not in MODULI:
            continue
        key = f"n{n}_l{ell}"
        F = Field(n, MODULI[n])
        basis = frozen_basis(n, ell)
        catalog = [
            {"shape": "poly", "basis": basis},
            {"shape": "geometric", "basis": geometric_basis(ell, F, seed_elem=3)},
            {
                "shape": "random",
                "basis": random_basis(ell, n, _IntRng(CATALOG_SEED + n * 100 + ell)),
            },
        ]
        na, nb, ok, _det = encode_n_var(F, CURVE_B[n], basis, XR[n])
        twin_ok = twin_ok and ok
        cells[key] = {
            "n": n,
            "ell": ell,
            "catalog": catalog,
            "probe_N_var": {"a": na, "b": nb, "agree": ok},
            "band_bytes": band_bytes(ell),
        }

    prereg = {
        "experiment_id": EXPERIMENT_ID,
        "hypothesis_id": HYPOTHESIS_ID,
        "approved_by": APPROVED_BY,
        "parent_experiment": PARENT_EXP,
        "grandparent_experiment": GRANDPARENT_EXP,
        "evidence_cited": EVIDENCE_CITED,
        "parent_decision": PARENT_DECISION,
        "alpha": ALPHA,
        "M0_bytes": M0_BYTES,
        "band_formula": "peak_rss <= M0_bytes * 2**(alpha * ell)",
        "delta_formula": "delta_rss = max(0, encode_peak - baseline_peak)",
        "catalog_seed": CATALOG_SEED,
        "parent_catalog_seed": 2026100375050,
        "v1_catalog_seed": 202610032056,
        "rss_probe": RSS_PROBE,
        "rss_probe_ok": rss_probe_ok,
        "rss_probe_error": probe_err,
        "os_rss_floor_bytes": os_rss_floor,
        "baseline_repeats": BASELINE_REPEATS,
        "baseline_peaks": baselines,
        "allocator_probe": alloc_results,
        "allocator_ok": allocator_ok,
        "clear_floor_delta_bytes": CLEAR_FLOOR_DELTA_BYTES,
        "clear_floor_margin_bytes": CLEAR_FLOOR_MARGIN_BYTES,
        "authorized_stage1_cells": [{"n": n, "ell": ell} for n, ell in STAGE1_CELLS],
        "encoder_pin": {
            "family": "Weil-descended Semaev S_3",
            "N_var_twins": ["encode_s3 path A", "encode_s3 path B"],
            "solve": "dense GF(2) row reduction of pure-linear slice (stdlib pin)",
            "moduli": {str(k): MODULI[k] for k in MODULI},
            "curve_B": CURVE_B,
            "xR": XR,
            "inherited_from": PARENT_EXP,
        },
        "prediction": (
            "FORALL Stage-1 (n,ell) in [(17,3),(17,4),(17,5),(17,6)]: "
            f"process-isolated peak_rss(encode+solve) <= {M0_BYTES} * 2**({ALPHA}*ell). "
            "Primary instrument is baseline-subtracted delta_rss; "
            "instrument_clears_floor must hold before any mechanism reading. "
            "Cites EV-BINSTD-0fed43 / EV-BINSTD-375f15 (floor_dominant refine)."
        ),
        "amazon_bedrock": "NOT SELECTED",
        "no_parent_rerun": True,
    }
    write_json(EXP_ROOT / "stage0" / "preregistered-predictions.json", prereg)
    write_json(
        EXP_ROOT / "stage0" / "v-catalog.json",
        {
            "cells": cells,
            "twin_ok": twin_ok,
            "rss_probe_ok": rss_probe_ok,
            "allocator_ok": allocator_ok,
            "os_rss_floor_bytes": os_rss_floor,
            "catalog_seed": CATALOG_SEED,
        },
    )

    outcome = "O-STAGE0-OK"
    if not rss_probe_ok:
        outcome = "O-IMPEDIMENT"
    elif not allocator_ok:
        outcome = "O-IMPEDIMENT"
    elif not twin_ok:
        outcome = "O-ARTIFACT"

    raw = {
        "experiment_id": EXPERIMENT_ID,
        "hypothesis_id": HYPOTHESIS_ID,
        "approved_by": APPROVED_BY,
        "evidence_cited": EVIDENCE_CITED,
        "stage": 0,
        "status": "ok" if outcome == "O-STAGE0-OK" else "stop",
        "outcome": outcome,
        "twin_ok": twin_ok,
        "rss_probe_ok": rss_probe_ok,
        "allocator_ok": allocator_ok,
        "os_rss_floor_bytes": os_rss_floor,
        "alpha": ALPHA,
        "M0_bytes": M0_BYTES,
        "catalog_seed": CATALOG_SEED,
        "peak_rss_bytes": peak_rss_bytes() if rss_probe_ok else None,
        "wall_clock_seconds": time.time() - t0,
        "artifacts": {
            "preregistered_predictions": "stage0/preregistered-predictions.json",
            "v_catalog": "stage0/v-catalog.json",
        },
        "claims": {"break": False, "exponent_move": False},
        "amazon_bedrock": "NOT_USED",
    }
    write_json(run_dir / "raw-result.json", raw)
    write_yaml_manifest(
        run_dir / "manifest.yaml",
        {
            "experiment_id": EXPERIMENT_ID,
            "stage": 0,
            "outcome": outcome,
            "approved_by": APPROVED_BY,
            "amazon_bedrock": "NOT_USED",
        },
    )
    return raw


def _require_stage0() -> tuple[dict, dict] | dict:
    cat_path = EXP_ROOT / "stage0" / "v-catalog.json"
    pre_path = EXP_ROOT / "stage0" / "preregistered-predictions.json"
    if not cat_path.is_file() or not pre_path.is_file():
        return {
            "experiment_id": EXPERIMENT_ID,
            "status": "impediment",
            "outcome": "O-IMPEDIMENT",
            "reason": "Stage-0 freeze missing",
            "claims": {"break": False, "exponent_move": False},
            "amazon_bedrock": "NOT_USED",
        }
    cat = json.loads(cat_path.read_text(encoding="utf-8"))
    pre = json.loads(pre_path.read_text(encoding="utf-8"))
    return cat, pre


def stage1(run_dir: Path) -> dict:
    t0 = time.time()
    loaded = _require_stage0()
    if isinstance(loaded, dict) and loaded.get("status") == "impediment":
        loaded["stage"] = 1
        write_json(run_dir / "raw-result.json", loaded)
        write_yaml_manifest(
            run_dir / "manifest.yaml",
            {"experiment_id": EXPERIMENT_ID, "stage": 1, "status": "impediment"},
        )
        return loaded
    cat, pre = loaded  # type: ignore[misc]

    panels: list[dict] = []
    if not cat.get("rss_probe_ok", False) or not cat.get("allocator_ok", False):
        outcome = "O-IMPEDIMENT"
    elif not cat.get("twin_ok", False):
        outcome = "O-ARTIFACT"
    else:
        for n, ell in STAGE1_CELLS:
            key = f"n{n}_l{ell}"
            cell = cat["cells"][key]
            basis = cell["catalog"][0]["basis"]
            panels.append(measure_delta_real(n, ell, basis))
        if any(not p["twin_ok"] for p in panels):
            outcome = "O-ARTIFACT"
        elif any(p["peak_rss_bytes"] is None for p in panels):
            outcome = "O-INCONCLUSIVE"
        else:
            # Provisional; refined below after diagnostics.
            outcome = "O-SUPPORT" if all(p["band_holds"] for p in panels) else "O-FAIL-BAND"

    deltas = [int(p["delta_rss_bytes"]) for p in panels if p.get("delta_rss_bytes") is not None]
    peaks = [int(p["peak_rss_bytes"]) for p in panels if p.get("peak_rss_bytes") is not None]
    floor = int(pre.get("os_rss_floor_bytes") or 0)
    med_delta = int(statistics.median(deltas)) if deltas else 0
    max_peak = max(peaks) if peaks else 0
    instrument_clears_floor = (
        med_delta >= CLEAR_FLOOR_DELTA_BYTES
        or (max_peak - floor) >= CLEAR_FLOOR_MARGIN_BYTES
    )
    by_ell: dict[int, list[int]] = {}
    for p in panels:
        by_ell.setdefault(int(p["ell"]), []).append(int(p["delta_rss_bytes"]))
    ell_med = {e: int(statistics.median(v)) for e, v in by_ell.items()} if by_ell else {}
    if ell_med:
        lo = min(ell_med.values())
        hi = max(ell_med.values())
        delta_ell_spread = (hi - lo) / max(1, lo) if lo > 0 else float(hi > lo)
    else:
        delta_ell_spread = 0.0
    floor_dominant_delta = bool(
        panels and delta_ell_spread < 0.05 and med_delta < CLEAR_FLOOR_DELTA_BYTES
    )
    peak_band_holds_all = bool(panels) and all(p.get("band_holds") for p in panels)

    if panels and outcome in ("O-SUPPORT", "O-FAIL-BAND"):
        if not instrument_clears_floor or floor_dominant_delta:
            outcome = "O-INCONCLUSIVE"

    write_json(
        EXP_ROOT / "stage1" / "panels.json",
        {
            "panels": panels,
            "instrument_clears_floor": instrument_clears_floor,
            "floor_dominant_delta": floor_dominant_delta,
            "delta_ell_spread": delta_ell_spread,
            "median_delta_rss_bytes": med_delta,
            "os_rss_floor_bytes": floor,
            "peak_band_holds_all": peak_band_holds_all,
        },
    )
    control = {
        "alpha": pre["alpha"],
        "M0_bytes": pre["M0_bytes"],
        "catalog_seed": pre["catalog_seed"],
        "rss_probe": pre["rss_probe"],
        "twin_ok": cat.get("twin_ok"),
        "allocator_ok": cat.get("allocator_ok"),
        "cells_checked": [f"({p['n']},{p['ell']})" for p in panels],
        "band_holds": [p.get("band_holds") for p in panels],
        "delta_rss_bytes": [p.get("delta_rss_bytes") for p in panels],
        "instrument_clears_floor": instrument_clears_floor,
        "floor_dominant_delta": floor_dominant_delta,
        "delta_ell_spread": delta_ell_spread,
        "parent_evidence": EVIDENCE_CITED,
        "rss_mode": "process_isolated_delta",
    }
    write_json(EXP_ROOT / "stage1" / "control-table.json", control)

    lines = [
        f"# RESULTS — {EXPERIMENT_ID} Stage-1",
        "",
        f"- Hypothesis: {HYPOTHESIS_ID}",
        f"- Approved by: {APPROVED_BY}",
        f"- Parent: {PARENT_EXP} / EV-BINSTD-0fed43 / {PARENT_DECISION}",
        f"- Also cites: EV-BINSTD-375f15",
        f"- Outcome: **{outcome}**",
        f"- α={pre['alpha']}, M₀={pre['M0_bytes']} bytes, catalog_seed={pre['catalog_seed']}",
        f"- RSS mode: process-isolated delta (baseline-subtracted)",
        f"- os_rss_floor_bytes: {floor}",
        f"- median_delta_rss_bytes: {med_delta}",
        f"- instrument_clears_floor: {instrument_clears_floor}",
        f"- floor_dominant_delta: {floor_dominant_delta}",
        f"- delta_ell_spread: {delta_ell_spread}",
        f"- peak_band_holds_all: {peak_band_holds_all}",
        "",
        "## Stage-1 panels (delta-RSS refine)",
        "",
    ]
    for p in panels:
        lines.append(
            f"- n={p['n']} ℓ={p['ell']}: peak_rss={p['peak_rss_bytes']} "
            f"baseline={p.get('baseline_peak_rss_bytes')} "
            f"delta_rss={p.get('delta_rss_bytes')} "
            f"band={p['band_bytes']} holds={p['band_holds']} twin_ok={p['twin_ok']} "
            f"pid={p.get('pid')}"
        )
    lines += [
        "",
        "## Claims",
        "",
        "- break: false",
        "- exponent_move: false",
        "- n>=131 transfer: not claimed",
        "- support/KN-FIND: not claimed (floor gate applies)",
        "- parent re-run: false",
        "",
        "Amazon Bedrock: NOT_USED",
        "",
    ]
    write_text(EXP_ROOT / "RESULTS.md", "\n".join(lines))

    raw = {
        "experiment_id": EXPERIMENT_ID,
        "hypothesis_id": HYPOTHESIS_ID,
        "approved_by": APPROVED_BY,
        "evidence_cited": EVIDENCE_CITED,
        "stage": 1,
        "stage_label": "1_delta_rss_refine",
        "status": "ok",
        "outcome": outcome,
        "panels": panels,
        "instrument_clears_floor": instrument_clears_floor,
        "floor_dominant_delta": floor_dominant_delta,
        "delta_ell_spread": delta_ell_spread,
        "median_delta_rss_bytes": med_delta,
        "os_rss_floor_bytes": floor,
        "peak_band_holds_all": peak_band_holds_all,
        "catalog_seed": pre["catalog_seed"],
        "peak_rss_bytes": peak_rss_bytes(),
        "wall_clock_seconds": time.time() - t0,
        "claims": {"break": False, "exponent_move": False},
        "amazon_bedrock": "NOT_USED",
    }
    write_json(run_dir / "raw-result.json", raw)
    write_yaml_manifest(
        run_dir / "manifest.yaml",
        {
            "experiment_id": EXPERIMENT_ID,
            "stage": 1,
            "outcome": outcome,
            "approved_by": APPROVED_BY,
            "amazon_bedrock": "NOT_USED",
        },
    )
    return raw


def main(argv: list[str] | None = None) -> int:
    p = argparse.ArgumentParser()
    p.add_argument("--stage", type=int, choices=[0, 1])
    p.add_argument("--trial-plan", type=str, default="")
    p.add_argument("--run-dir", type=str, default="")
    p.add_argument("--worker-json", type=str, default="")
    args = p.parse_args(argv)

    if args.worker_json:
        out = _worker(json.loads(args.worker_json))
        print(json.dumps(out, separators=(",", ":")))
        return 0

    if not args.run_dir:
        print("--run-dir required", file=sys.stderr)
        return 2
    run_dir = Path(args.run_dir)
    run_dir.mkdir(parents=True, exist_ok=True)

    if args.stage == 0:
        stage0(run_dir)
    elif args.stage == 1:
        stage1(run_dir)
    else:
        print("stage required", file=sys.stderr)
        return 2
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

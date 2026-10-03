#!/usr/bin/env python3
"""EXP-BINSTD-a33de2 — Stage-1R shared-baseline densified delta-RSS replication.

Independent Stage-1R of EXP-BINSTD-9001b3 / H-BINSTD-ce918e after
EV-BINSTD-c45564 / DEC-20261003-4706a8 (decision: replicate).
Same shared-baseline densified protocol; NEW catalog_seed.
Keeps frozen (α,M₀)=(1.0,16777216), twin N_var meters, shared XOR-SAT pin,
density_batch≥32 package-median floor-clear gate, process-isolated shared baseline.

Replication (NA-1 of DEC-20261003-4706a8):
  * Stage 0 re-freeze pin/(α,M₀) + NEW catalog_seed + SHARED baseline
    + allocator probes + package-median density-batch calibration (≥32)
  * Stage 1R cells unchanged: (n,ℓ)∈{(23,6),(23,8),(29,8),(29,10),(31,10),(31,12)}
  * No per-cell paired baseline. instrument_clears_floor gate before band reading.
  * Expand (Stage-2 null) deferred until this replication is reviewed.

Memory instrument only. No Magma/Sage/AUXIN/Bedrock. No ECDLP solve.
No n≥131 transfer. No re-run of 9001b3 / 55feb5 / eb9e5e / ff5050 / cb15a4.
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

EXPERIMENT_ID = "EXP-BINSTD-a33de2"
HYPOTHESIS_ID = "H-BINSTD-ce918e"
PARENT_EXP = "EXP-BINSTD-9001b3"
GRANDPARENT_EXP = "EXP-BINSTD-55feb5"
APPROVED_BY = "DEC-20261003-a57c49"
EVIDENCE_CITED = ["EV-BINSTD-c45564", "EV-BINSTD-602614"]
PARENT_DECISION = "DEC-20261003-4706a8"
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
CATALOG_SEED = 2026100388923
PARENT_CATALOG_SEED = 2026100390013
GRANDPARENT_CATALOG_SEED = 2026100377593
EB9E5E_CATALOG_SEED = 2026100343342
V1_CATALOG_SEED = 202610032056
FF5050_CATALOG_SEED = 2026100375050
FORBIDDEN_SEEDS = {
    PARENT_CATALOG_SEED,
    GRANDPARENT_CATALOG_SEED,
    EB9E5E_CATALOG_SEED,
    V1_CATALOG_SEED,
    FF5050_CATALOG_SEED,
}
assert CATALOG_SEED not in FORBIDDEN_SEEDS
STAGE1_CELLS = [(23, 6), (23, 8), (29, 8), (29, 10), (31, 10), (31, 12)]
# Parent Stage-1 zeros were (29,8) and (29,10); include smallest + those + largest.
PACKAGE_CALIB_CELLS = [(23, 6), (29, 8), (29, 10), (31, 12)]
START_DENSITY_BATCH = 32
MAX_DENSITY_BATCH = 2048
ALLOCATOR_PROBE_SIZES = [2 * 1024 * 1024, 8 * 1024 * 1024, 16 * 1024 * 1024]
ALLOCATOR_RECOVERY_FRAC = 0.50
CLEAR_FLOOR_DELTA_BYTES = 256 * 1024
CLEAR_FLOOR_MARGIN_BYTES = 512 * 1024
SHARED_BASELINE_REPEATS = 7
RSS_PROBE = (
    "subprocess RUSAGE_SELF.ru_maxrss*1024 (process-isolated); "
    "delta_rss = max(0, encode_peak - shared_baseline_rss); "
    "shared_baseline_rss frozen at Stage 0 as median of isolated Field-import workers; "
    "density_batch retained encode+solve artifacts in one worker"
)
RSS_MODE = "process_isolated_delta_shared_baseline"


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
        "eqs": eqs,
        "lin_rows": lin_rows,
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
        density_batch = max(1, int(payload.get("density_batch", 1)))
        seed = int(payload.get("seed", CATALOG_SEED))
        F = Field(n, MODULI[n])
        retention: list[Any] = []
        twin_ok = True
        n_a = n_b = 0
        lin_rank = 0
        nv0 = 0
        neq = 0
        rss_before = peak_rss_bytes()
        for i in range(density_batch):
            if i == 0:
                basis = list(payload["basis"])
            else:
                basis = random_basis(ell, n, _IntRng(seed + 10007 * i + n * 17 + ell))
            na0, nb0, tok0, _ = encode_n_var(F, CURVE_B[n], basis, XR[n])
            measured = encode_and_solve_once(F, CURVE_B[n], basis, XR[n])
            twin_ok = twin_ok and bool(tok0 and measured["twin_ok"])
            if i == 0:
                n_a, n_b = na0, nb0
                lin_rank = measured["lin_rank_solve"]
                nv0 = measured["nv0"]
                neq = measured["neq"]
            retention.append(
                {
                    "basis": list(basis),
                    "eqs": measured["eqs"],
                    "lin_rows": measured["lin_rows"],
                }
            )
        band = band_bytes(ell)
        peak = peak_rss_bytes()
        retained_bytes_est = sum(
            sys.getsizeof(item["eqs"])
            + sys.getsizeof(item["lin_rows"])
            + sum(sys.getsizeof(r) for r in item["lin_rows"])
            for item in retention
        )
        return {
            "kind": "real",
            "n": n,
            "ell": ell,
            "basis_shape": "poly_plus_random_batch",
            "density_batch": density_batch,
            "retained_instances": len(retention),
            "retained_bytes_est": retained_bytes_est,
            "twin_ok": twin_ok,
            "N_var_a": n_a,
            "N_var_b": n_b,
            "peak_rss_bytes": peak,
            "band_bytes": band,
            "band_holds": peak <= band,
            "lin_rank_solve": lin_rank,
            "nv0": nv0,
            "neq": neq,
            "rss_before_bytes": rss_before,
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


def measure_delta_real(
    n: int,
    ell: int,
    basis: list[int],
    density_batch: int,
    seed: int,
    shared_baseline: int,
) -> dict:
    encode = measure_isolated(
        {
            "kind": "real",
            "n": n,
            "ell": ell,
            "basis": basis,
            "density_batch": density_batch,
            "seed": seed,
        }
    )
    enc_peak = int(encode["peak_rss_bytes"])
    delta = max(0, enc_peak - int(shared_baseline))
    band = band_bytes(ell)
    return {
        **encode,
        "baseline_peak_rss_bytes": int(shared_baseline),
        "shared_baseline_rss_bytes": int(shared_baseline),
        "delta_rss_bytes": delta,
        "band_bytes": band,
        "band_holds": enc_peak <= band,
        "delta_band_holds": delta <= band,
        "rss_mode": RSS_MODE,
        "baseline_source": "stage0_shared_frozen",
    }


def _clears_floor(med_delta: int, max_peak: int, floor: int) -> bool:
    return med_delta >= CLEAR_FLOOR_DELTA_BYTES or (
        max_peak - floor
    ) >= CLEAR_FLOOR_MARGIN_BYTES


def calibrate_density_batch(shared_baseline: int) -> dict:
    """Double density_batch from START until PACKAGE-median gate + no clamp."""
    trials: list[dict] = []
    chosen = None
    batch = START_DENSITY_BATCH
    while batch <= MAX_DENSITY_BATCH:
        rows = []
        for n, ell in PACKAGE_CALIB_CELLS:
            basis = frozen_basis(n, ell)
            row = measure_delta_real(
                n, ell, basis, batch, CATALOG_SEED + batch + n * 17 + ell, shared_baseline
            )
            rows.append(row)
        deltas = [int(r["delta_rss_bytes"]) for r in rows]
        peaks = [int(r["peak_rss_bytes"]) for r in rows]
        med = int(statistics.median(deltas))
        max_peak = max(peaks)
        n_clamped = sum(1 for d in deltas if d == 0)
        clears = _clears_floor(med, max_peak, shared_baseline) and n_clamped == 0
        entry = {
            "density_batch": batch,
            "cells": [
                {
                    "n": int(r["n"]),
                    "ell": int(r["ell"]),
                    "delta_rss_bytes": int(r["delta_rss_bytes"]),
                    "peak_rss_bytes": int(r["peak_rss_bytes"]),
                    "twin_ok": bool(r["twin_ok"]),
                    "retained_bytes_est": r.get("retained_bytes_est"),
                }
                for r in rows
            ],
            "median_delta_rss_bytes": med,
            "max_encode_peak_rss_bytes": max_peak,
            "shared_baseline_rss_bytes": shared_baseline,
            "margin_bytes": max_peak - shared_baseline,
            "n_clamped_zero": n_clamped,
            "instrument_clears_floor": clears,
        }
        trials.append(entry)
        if clears and chosen is None:
            chosen = batch
            break
        batch *= 2
    return {
        "calib_cells": [{"n": n, "ell": ell} for n, ell in PACKAGE_CALIB_CELLS],
        "start_density_batch": START_DENSITY_BATCH,
        "trials": trials,
        "density_batch_size": chosen,
        "floor_clear_calibration_ok": chosen is not None,
        "max_density_batch": MAX_DENSITY_BATCH,
        "clear_floor_delta_bytes": CLEAR_FLOOR_DELTA_BYTES,
        "clear_floor_margin_bytes": CLEAR_FLOOR_MARGIN_BYTES,
        "rss_mode": RSS_MODE,
        "no_paired_baseline": True,
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
    shared_baseline = None
    calibration: dict[str, Any] = {}

    try:
        for _ in range(SHARED_BASELINE_REPEATS):
            b = measure_isolated({"kind": "baseline", "n": 31})
            baselines.append(int(b["peak_rss_bytes"]))
        shared_baseline = int(statistics.median(baselines))
        for size in ALLOCATOR_PROBE_SIZES:
            alloc = measure_isolated({"kind": "alloc", "size": size})
            delta = max(0, int(alloc["peak_rss_bytes"]) - shared_baseline)
            recovered = delta >= int(ALLOCATOR_RECOVERY_FRAC * size)
            row = {
                "size": size,
                "shared_baseline_rss_bytes": shared_baseline,
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
        if rss_probe_ok and allocator_ok and shared_baseline is not None:
            calibration = calibrate_density_batch(shared_baseline)
    except Exception as exc:  # noqa: BLE001
        rss_probe_ok = False
        twin_ok = False
        allocator_ok = False
        probe_err = str(exc)
        calibration = {
            "floor_clear_calibration_ok": False,
            "density_batch_size": None,
            "error": probe_err,
        }

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

    floor_clear_ok = bool(calibration.get("floor_clear_calibration_ok"))
    density_batch_size = calibration.get("density_batch_size")

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
        "delta_formula": "delta_rss = max(0, encode_peak - shared_baseline_rss)",
        "density_batch_formula": (
            "Stage-0 doubles density_batch from 32 on PACKAGE_CALIB_CELLS "
            "until median ΔRSS vs frozen shared baseline clears "
            "instrument_clears_floor AND n_clamped_zero=0; "
            "Stage-1 retains that many encode+solve artifacts per cell"
        ),
        "catalog_seed": CATALOG_SEED,
        "parent_catalog_seed": PARENT_CATALOG_SEED,
        "grandparent_catalog_seed": GRANDPARENT_CATALOG_SEED,
        "eb9e5e_catalog_seed": EB9E5E_CATALOG_SEED,
        "ff5050_catalog_seed": FF5050_CATALOG_SEED,
        "v1_catalog_seed": V1_CATALOG_SEED,
        "rss_probe": RSS_PROBE,
        "rss_mode": RSS_MODE,
        "rss_probe_ok": rss_probe_ok,
        "rss_probe_error": probe_err,
        "os_rss_floor_bytes": shared_baseline,
        "shared_baseline_rss_bytes": shared_baseline,
        "shared_baseline_repeats": SHARED_BASELINE_REPEATS,
        "baseline_peaks": baselines,
        "allocator_probe": alloc_results,
        "allocator_ok": allocator_ok,
        "clear_floor_delta_bytes": CLEAR_FLOOR_DELTA_BYTES,
        "clear_floor_margin_bytes": CLEAR_FLOOR_MARGIN_BYTES,
        "start_density_batch": START_DENSITY_BATCH,
        "density_batch_calibration": calibration,
        "density_batch_size": density_batch_size,
        "floor_clear_calibration_ok": floor_clear_ok,
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
            "FORALL Stage-1 (n,ell) in "
            "[(23,6),(23,8),(29,8),(29,10),(31,10),(31,12)]: "
            f"process-isolated peak_rss(encode+solve batch) <= {M0_BYTES} * 2**({ALPHA}*ell). "
            "Stage-0 must freeze shared_baseline_rss and a density_batch_size that "
            "clears the PACKAGE instrument_clears_floor gate (median ΔRSS ≥ 262144 "
            "or max_encode − shared_baseline ≥ 524288) with no ΔRSS=0 clamp before "
            "Stage-1 band reading. Cites EV-BINSTD-602614 / EV-BINSTD-cd47a8."
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
            "floor_clear_calibration_ok": floor_clear_ok,
            "density_batch_size": density_batch_size,
            "os_rss_floor_bytes": shared_baseline,
            "shared_baseline_rss_bytes": shared_baseline,
            "rss_mode": RSS_MODE,
            "catalog_seed": CATALOG_SEED,
        },
    )

    outcome = "O-STAGE0-OK"
    if not rss_probe_ok:
        outcome = "O-IMPEDIMENT"
    elif not allocator_ok:
        outcome = "O-IMPEDIMENT"
    elif not floor_clear_ok:
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
        "floor_clear_calibration_ok": floor_clear_ok,
        "density_batch_size": density_batch_size,
        "os_rss_floor_bytes": shared_baseline,
        "shared_baseline_rss_bytes": shared_baseline,
        "rss_mode": RSS_MODE,
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

    density_batch = pre.get("density_batch_size")
    shared_baseline = pre.get("shared_baseline_rss_bytes")
    if shared_baseline is None:
        shared_baseline = pre.get("os_rss_floor_bytes")
    panels: list[dict] = []
    if (
        not cat.get("rss_probe_ok", False)
        or not cat.get("allocator_ok", False)
        or not cat.get("floor_clear_calibration_ok", False)
        or not density_batch
        or shared_baseline is None
    ):
        outcome = "O-IMPEDIMENT"
    elif not cat.get("twin_ok", False):
        outcome = "O-ARTIFACT"
    else:
        for n, ell in STAGE1_CELLS:
            key = f"n{n}_l{ell}"
            cell = cat["cells"][key]
            basis = cell["catalog"][0]["basis"]
            panels.append(
                measure_delta_real(
                    n,
                    ell,
                    basis,
                    int(density_batch),
                    CATALOG_SEED + n * 1000 + ell,
                    int(shared_baseline),
                )
            )
        if any(not p["twin_ok"] for p in panels):
            outcome = "O-ARTIFACT"
        elif any(p["peak_rss_bytes"] is None for p in panels):
            outcome = "O-INCONCLUSIVE"
        else:
            outcome = (
                "O-SUPPORT" if all(p["band_holds"] for p in panels) else "O-FAIL-BAND"
            )

    deltas = [int(p["delta_rss_bytes"]) for p in panels if p.get("delta_rss_bytes") is not None]
    peaks = [int(p["peak_rss_bytes"]) for p in panels if p.get("peak_rss_bytes") is not None]
    floor = int(shared_baseline or pre.get("os_rss_floor_bytes") or 0)
    med_delta = int(statistics.median(deltas)) if deltas else 0
    max_peak = max(peaks) if peaks else 0
    n_clamped = sum(1 for d in deltas if d == 0)
    instrument_clears_floor = _clears_floor(med_delta, max_peak, floor) and n_clamped == 0
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
            "n_clamped_zero": n_clamped,
            "os_rss_floor_bytes": floor,
            "shared_baseline_rss_bytes": floor,
            "peak_band_holds_all": peak_band_holds_all,
            "density_batch_size": density_batch,
            "rss_mode": RSS_MODE,
        },
    )
    control = {
        "alpha": pre["alpha"],
        "M0_bytes": pre["M0_bytes"],
        "catalog_seed": pre["catalog_seed"],
        "rss_probe": pre["rss_probe"],
        "twin_ok": cat.get("twin_ok"),
        "allocator_ok": cat.get("allocator_ok"),
        "floor_clear_calibration_ok": cat.get("floor_clear_calibration_ok"),
        "density_batch_size": density_batch,
        "cells_checked": [f"({p['n']},{p['ell']})" for p in panels],
        "band_holds": [p.get("band_holds") for p in panels],
        "delta_rss_bytes": [p.get("delta_rss_bytes") for p in panels],
        "instrument_clears_floor": instrument_clears_floor,
        "floor_dominant_delta": floor_dominant_delta,
        "delta_ell_spread": delta_ell_spread,
        "n_clamped_zero": n_clamped,
        "parent_evidence": EVIDENCE_CITED,
        "rss_mode": RSS_MODE,
    }
    write_json(EXP_ROOT / "stage1" / "control-table.json", control)

    lines = [
        f"# RESULTS — {EXPERIMENT_ID} Stage-1",
        "",
        f"- Hypothesis: {HYPOTHESIS_ID}",
        f"- Approved by: {APPROVED_BY}",
        f"- Parent: {PARENT_EXP} / EV-BINSTD-c45564 / {PARENT_DECISION}",
        f"- Also cites: EV-BINSTD-cd47a8",
        f"- Outcome: **{outcome}**",
        f"- α={pre['alpha']}, M₀={pre['M0_bytes']} bytes, catalog_seed={pre['catalog_seed']}",
        f"- density_batch_size: {density_batch}",
        f"- RSS mode: {RSS_MODE}",
        f"- shared_baseline_rss_bytes: {floor}",
        f"- median_delta_rss_bytes: {med_delta}",
        f"- n_clamped_zero: {n_clamped}",
        f"- instrument_clears_floor: {instrument_clears_floor}",
        f"- floor_dominant_delta: {floor_dominant_delta}",
        f"- delta_ell_spread: {delta_ell_spread}",
        f"- peak_band_holds_all: {peak_band_holds_all}",
        "",
        "## Stage-1 panels (shared-baseline package-median floor-clear successor)",
        "",
    ]
    for p in panels:
        lines.append(
            f"- n={p['n']} ℓ={p['ell']}: peak_rss={p['peak_rss_bytes']} "
            f"shared_baseline={p.get('shared_baseline_rss_bytes')} "
            f"delta_rss={p.get('delta_rss_bytes')} "
            f"batch={p.get('density_batch')} "
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
        "stage_label": "1R_shared_baseline_densified_replication",
        "status": "ok",
        "outcome": outcome,
        "panels": panels,
        "density_batch_size": density_batch,
        "instrument_clears_floor": instrument_clears_floor,
        "floor_dominant_delta": floor_dominant_delta,
        "delta_ell_spread": delta_ell_spread,
        "median_delta_rss_bytes": med_delta,
        "n_clamped_zero": n_clamped,
        "os_rss_floor_bytes": floor,
        "shared_baseline_rss_bytes": floor,
        "peak_band_holds_all": peak_band_holds_all,
        "rss_mode": RSS_MODE,
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

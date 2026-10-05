#!/usr/bin/env python3
"""EXP-BINSTD-ff5050 — independent Stage-1R replication + Stage-2 multi-n/null.

Successor of EXP-BINSTD-cb15a4 / H-BINSTD-ce918e after EV-BINSTD-375f15
(decision replicate, DEC-20261003-c14256). Keeps frozen (α,M₀)=(1.0,16777216),
twin N_var meters, and shared XOR-SAT pin. New catalog_seed for independence.
Stage-1R measures peak RSS in a fresh subprocess (process-isolated getrusage).
Stage-2 extends to n∈{19,23,29,31} with matched random-Boolean null.

Memory instrument only. No Magma/Sage/AUXIN/Bedrock. No ECDLP solve.
No n≥131 transfer. No v1 re-run of EXP-BINSTD-cb15a4.
"""
from __future__ import annotations

import argparse
import json
import os
import random
import resource
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

EXPERIMENT_ID = "EXP-BINSTD-ff5050"
HYPOTHESIS_ID = "H-BINSTD-ce918e"
PARENT_EXP = "EXP-BINSTD-cb15a4"
APPROVED_BY = "DEC-20261003-953dd5"
EVIDENCE_CITED = "EV-BINSTD-375f15"
PARENT_DECISION = "DEC-20261003-c14256"
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

# Inherited from v1 Stage-0 freeze (EV-BINSTD-375f15); not post-hoc.
ALPHA = 1.0
M0_BYTES = 16 * 1024 * 1024
# Independent replication seed (distinct from v1 catalog_seed 202610032056).
CATALOG_SEED = 2026100375050
STAGE1R_CELLS = [(17, 3), (17, 4)]
STAGE2_CELLS = [
    (19, 3),
    (19, 4),
    (23, 3),
    (23, 4),
    (29, 3),
    (29, 4),
    (31, 3),
    (31, 4),
]
RSS_PROBE = "subprocess RUSAGE_SELF.ru_maxrss*1024 (process-isolated)"


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


def gaussian_rank(lin_rows: list[list[int]], nv: int) -> int:
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
    return rank


def null_random_boolean_solve(nv: int, neq: int, seed: int) -> dict:
    """Matched-N_var random Boolean linear system; RSS independent of n by construction."""
    rng = random.Random(seed)
    rss_before = peak_rss_bytes()
    rows = [[rng.getrandbits(1) for _ in range(nv)] for _ in range(neq)]
    rank = gaussian_rank(rows, nv)
    rss_after = peak_rss_bytes()
    return {
        "nv": nv,
        "neq": neq,
        "lin_rank_solve": rank,
        "rss_before_bytes": rss_before,
        "peak_rss_bytes": rss_after,
        "kind": "random_boolean_matched_Nvar",
    }


def worker_measure(payload: dict) -> dict:
    """Child-process entry: measure one real or null cell; report own peak RSS."""
    kind = payload["kind"]
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
            "rss_mode": "process_isolated",
            "pid": os.getpid(),
        }
    if kind == "null":
        out = null_random_boolean_solve(
            int(payload["nv"]), int(payload["neq"]), int(payload["seed"])
        )
        out["rss_mode"] = "process_isolated"
        out["pid"] = os.getpid()
        out["n"] = payload.get("n")
        out["ell"] = payload.get("ell")
        return out
    raise ValueError(f"unknown worker kind {kind!r}")


def measure_isolated(payload: dict) -> dict:
    """Spawn a fresh Python process so getrusage is not contaminated by parent RSS."""
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


def stage0(run_dir: Path) -> dict:
    t0 = time.time()
    cells: dict[str, Any] = {}
    twin_ok = True
    rss_probe_ok = True
    probe_err = None
    try:
        # Process-isolated probe on a tiny cell.
        probe = measure_isolated(
            {
                "kind": "real",
                "n": 17,
                "ell": 3,
                "basis": frozen_basis(17, 3),
            }
        )
        if probe.get("peak_rss_bytes") is None:
            rss_probe_ok = False
            probe_err = "isolated probe returned no peak_rss"
    except Exception as exc:  # noqa: BLE001
        rss_probe_ok = False
        twin_ok = False
        probe_err = str(exc)
        probe = None

    catalog_cells = STAGE1R_CELLS + STAGE2_CELLS
    for n, ell in catalog_cells:
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
        "evidence_cited": EVIDENCE_CITED,
        "parent_decision": PARENT_DECISION,
        "alpha": ALPHA,
        "M0_bytes": M0_BYTES,
        "band_formula": "peak_rss <= M0_bytes * 2**(alpha * ell)",
        "catalog_seed": CATALOG_SEED,
        "parent_catalog_seed": 202610032056,
        "rss_probe": RSS_PROBE,
        "rss_probe_ok": rss_probe_ok,
        "rss_probe_error": probe_err,
        "isolated_probe": probe,
        "authorized_stage1r_cells": [
            {"n": n, "ell": ell} for n, ell in STAGE1R_CELLS
        ],
        "authorized_stage2_cells": [
            {"n": n, "ell": ell} for n, ell in STAGE2_CELLS
        ],
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
            "FORALL Stage-1R (n,ell) in [(17,3),(17,4)]: process-isolated "
            f"peak_rss(encode+solve) <= {M0_BYTES} * 2**({ALPHA}*ell). "
            "Stage-2: same band on multi-n cells; null_random_boolean RSS "
            "n-insensitive by construction (floor separation)."
        ),
        "amazon_bedrock": "NOT SELECTED",
        "no_v1_rerun": True,
    }
    write_json(EXP_ROOT / "stage0" / "preregistered-predictions.json", prereg)
    write_json(
        EXP_ROOT / "stage0" / "v-catalog.json",
        {
            "cells": cells,
            "twin_ok": twin_ok,
            "rss_probe_ok": rss_probe_ok,
            "catalog_seed": CATALOG_SEED,
        },
    )

    outcome = "O-STAGE0-OK"
    if not rss_probe_ok:
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


def stage1r(run_dir: Path) -> dict:
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

    if not cat.get("rss_probe_ok", False):
        outcome = "O-IMPEDIMENT"
        panels: list[dict] = []
    elif not cat.get("twin_ok", False):
        outcome = "O-ARTIFACT"
        panels = []
    else:
        panels = []
        for n, ell in STAGE1R_CELLS:
            key = f"n{n}_l{ell}"
            cell = cat["cells"][key]
            basis = cell["catalog"][0]["basis"]
            panels.append(
                measure_isolated({"kind": "real", "n": n, "ell": ell, "basis": basis})
            )
        if any(not p["twin_ok"] for p in panels):
            outcome = "O-ARTIFACT"
        elif any(p["peak_rss_bytes"] is None for p in panels):
            outcome = "O-INCONCLUSIVE"
        elif all(p["band_holds"] for p in panels):
            outcome = "O-SUPPORT"
        else:
            outcome = "O-FAIL-BAND"

    # Floor confound diagnostic (does not override O-* band label).
    peaks = [p.get("peak_rss_bytes") for p in panels if p.get("peak_rss_bytes") is not None]
    floor_identical = len(peaks) >= 2 and len(set(peaks)) == 1

    write_json(EXP_ROOT / "stage1r" / "panels.json", {"panels": panels, "floor_identical_across_ell": floor_identical})
    control = {
        "alpha": pre["alpha"],
        "M0_bytes": pre["M0_bytes"],
        "catalog_seed": pre["catalog_seed"],
        "rss_probe": pre["rss_probe"],
        "twin_ok": cat.get("twin_ok"),
        "cells_checked": [f"({p['n']},{p['ell']})" for p in panels],
        "band_holds": [p.get("band_holds") for p in panels],
        "floor_identical_across_ell": floor_identical,
        "parent_evidence": EVIDENCE_CITED,
        "rss_mode": "process_isolated",
    }
    write_json(EXP_ROOT / "stage1r" / "control-table.json", control)

    lines = [
        f"# RESULTS — {EXPERIMENT_ID} Stage-1R",
        "",
        f"- Hypothesis: {HYPOTHESIS_ID}",
        f"- Approved by: {APPROVED_BY}",
        f"- Parent: {PARENT_EXP} / {EVIDENCE_CITED} / {PARENT_DECISION}",
        f"- Outcome: **{outcome}**",
        f"- α={pre['alpha']}, M₀={pre['M0_bytes']} bytes, catalog_seed={pre['catalog_seed']}",
        f"- RSS mode: process-isolated",
        f"- floor_identical_across_ell: {floor_identical}",
        "",
        "## Stage-1R panels (independent replication)",
        "",
    ]
    for p in panels:
        lines.append(
            f"- n={p['n']} ℓ={p['ell']}: peak_rss={p['peak_rss_bytes']} "
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
        "- v1 re-run: false",
        "",
        "Amazon Bedrock: NOT_USED",
        "",
    ]
    write_text(EXP_ROOT / "RESULTS-stage1r.md", "\n".join(lines))

    raw = {
        "experiment_id": EXPERIMENT_ID,
        "hypothesis_id": HYPOTHESIS_ID,
        "approved_by": APPROVED_BY,
        "evidence_cited": EVIDENCE_CITED,
        "stage": 1,
        "stage_label": "1R_independent_replication",
        "status": "ok",
        "outcome": outcome,
        "panels": panels,
        "floor_identical_across_ell": floor_identical,
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


def stage2(run_dir: Path) -> dict:
    t0 = time.time()
    loaded = _require_stage0()
    if isinstance(loaded, dict) and loaded.get("status") == "impediment":
        loaded["stage"] = 2
        write_json(run_dir / "raw-result.json", loaded)
        write_yaml_manifest(
            run_dir / "manifest.yaml",
            {"experiment_id": EXPERIMENT_ID, "stage": 2, "status": "impediment"},
        )
        return loaded
    cat, pre = loaded  # type: ignore[misc]

    if not cat.get("rss_probe_ok", False):
        outcome = "O-IMPEDIMENT"
        panels = []
        nulls: list[dict] = []
    elif not cat.get("twin_ok", False):
        outcome = "O-ARTIFACT"
        panels = []
        nulls = []
    else:
        panels = []
        nulls = []
        for n, ell in STAGE2_CELLS:
            key = f"n{n}_l{ell}"
            cell = cat["cells"][key]
            basis = cell["catalog"][0]["basis"]
            real = measure_isolated(
                {"kind": "real", "n": n, "ell": ell, "basis": basis}
            )
            panels.append(real)
            null = measure_isolated(
                {
                    "kind": "null",
                    "nv": int(real["nv0"]),
                    "neq": int(real.get("neq") or real["nv0"]),
                    "seed": CATALOG_SEED + 10_000 * n + ell,
                    "n": n,
                    "ell": ell,
                }
            )
            null["band_bytes"] = band_bytes(ell)
            null["band_holds"] = null["peak_rss_bytes"] <= null["band_bytes"]
            nulls.append(null)

        if any(not p["twin_ok"] for p in panels):
            outcome = "O-ARTIFACT"
        elif any(p["peak_rss_bytes"] is None for p in panels):
            outcome = "O-INCONCLUSIVE"
        elif all(p["band_holds"] for p in panels):
            outcome = "O-SUPPORT"
        else:
            outcome = "O-FAIL-BAND"

    # Floor vs ℓ-channel separation diagnostics.
    real_by_ell: dict[int, list[int]] = {}
    null_by_n: dict[int, list[int]] = {}
    for p in panels:
        real_by_ell.setdefault(int(p["ell"]), []).append(int(p["peak_rss_bytes"]))
    for nu in nulls:
        null_by_n.setdefault(int(nu["n"]), []).append(int(nu["peak_rss_bytes"]))

    def _spread(vals: list[int]) -> float:
        if not vals:
            return 0.0
        return (max(vals) - min(vals)) / max(1, min(vals))

    ell_spreads = {str(k): _spread(v) for k, v in sorted(real_by_ell.items())}
    null_n_spread = _spread([x for xs in null_by_n.values() for x in xs])
    real_n_spread = _spread([int(p["peak_rss_bytes"]) for p in panels]) if panels else 0.0
    # Floor reading: real RSS nearly constant across n and ℓ, and null matches that floor.
    floor_dominant = bool(panels) and real_n_spread < 0.05 and all(
        s < 0.05 for s in ell_spreads.values()
    )
    null_n_insensitive = null_n_spread < 0.05

    write_json(
        EXP_ROOT / "stage2" / "panels.json",
        {
            "panels": panels,
            "nulls": nulls,
            "ell_spreads": ell_spreads,
            "real_n_spread": real_n_spread,
            "null_n_spread": null_n_spread,
            "floor_dominant": floor_dominant,
            "null_n_insensitive": null_n_insensitive,
        },
    )
    write_json(
        EXP_ROOT / "stage2" / "control-table.json",
        {
            "alpha": pre["alpha"],
            "M0_bytes": pre["M0_bytes"],
            "catalog_seed": pre["catalog_seed"],
            "cells_checked": [f"({p['n']},{p['ell']})" for p in panels],
            "band_holds": [p.get("band_holds") for p in panels],
            "null_control": "random_boolean_matched_Nvar",
            "floor_dominant": floor_dominant,
            "null_n_insensitive": null_n_insensitive,
            "parent_evidence": EVIDENCE_CITED,
            "rss_mode": "process_isolated",
        },
    )

    lines = [
        f"# RESULTS — {EXPERIMENT_ID} Stage-2",
        "",
        f"- Hypothesis: {HYPOTHESIS_ID}",
        f"- Approved by: {APPROVED_BY}",
        f"- Parent: {PARENT_EXP} / {EVIDENCE_CITED}",
        f"- Outcome: **{outcome}**",
        f"- floor_dominant: {floor_dominant}",
        f"- null_n_insensitive: {null_n_insensitive}",
        f"- real_n_spread: {real_n_spread}",
        f"- null_n_spread: {null_n_spread}",
        "",
        "## Stage-2 real panels",
        "",
    ]
    for p in panels:
        lines.append(
            f"- n={p['n']} ℓ={p['ell']}: peak_rss={p['peak_rss_bytes']} "
            f"band={p['band_bytes']} holds={p['band_holds']} twin_ok={p['twin_ok']}"
        )
    lines += ["", "## Stage-2 null panels (matched N_var)", ""]
    for nu in nulls:
        lines.append(
            f"- n={nu.get('n')} ℓ={nu.get('ell')}: null_peak_rss={nu['peak_rss_bytes']} "
            f"nv={nu.get('nv')} neq={nu.get('neq')}"
        )
    lines += [
        "",
        "## Claims",
        "",
        "- break: false",
        "- exponent_move: false",
        "- n>=131 transfer: not claimed",
        "",
        "Amazon Bedrock: NOT_USED",
        "",
    ]
    write_text(EXP_ROOT / "RESULTS-stage2.md", "\n".join(lines))

    # Combined RESULTS.md names Stage-2 package outcome (final authorized stage).
    write_text(
        EXP_ROOT / "RESULTS.md",
        "\n".join(
            [
                f"# RESULTS — {EXPERIMENT_ID}",
                "",
                f"- Hypothesis: {HYPOTHESIS_ID}",
                f"- Approved by: {APPROVED_BY}",
                f"- Evidence cited: {EVIDENCE_CITED}",
                f"- Final package outcome: **{outcome}**",
                f"- Stage-1R artifacts: stage1r/ + RESULTS-stage1r.md",
                f"- Stage-2 artifacts: stage2/ + RESULTS-stage2.md",
                f"- floor_dominant: {floor_dominant}",
                f"- null_n_insensitive: {null_n_insensitive}",
                "",
                "Amazon Bedrock: NOT_USED",
                "",
            ]
        ),
    )

    raw = {
        "experiment_id": EXPERIMENT_ID,
        "hypothesis_id": HYPOTHESIS_ID,
        "approved_by": APPROVED_BY,
        "evidence_cited": EVIDENCE_CITED,
        "stage": 2,
        "stage_label": "2_multi_n_null",
        "status": "ok",
        "outcome": outcome,
        "panels": panels,
        "nulls": nulls,
        "floor_dominant": floor_dominant,
        "null_n_insensitive": null_n_insensitive,
        "real_n_spread": real_n_spread,
        "null_n_spread": null_n_spread,
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
            "stage": 2,
            "outcome": outcome,
            "approved_by": APPROVED_BY,
            "amazon_bedrock": "NOT_USED",
        },
    )
    return raw


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--stage", type=int, choices=[0, 1, 2])
    ap.add_argument("--trial-plan")
    ap.add_argument("--run-dir")
    ap.add_argument("--worker-json", default=None, help=argparse.SUPPRESS)
    args = ap.parse_args()

    if args.worker_json is not None:
        out = worker_measure(json.loads(args.worker_json))
        print(json.dumps(out, separators=(",", ":"), sort_keys=True))
        return 0

    if args.stage is None or not args.trial_plan or not args.run_dir:
        print("usage: run.py --stage {0,1,2} --trial-plan PATH --run-dir PATH", file=sys.stderr)
        return 2

    run_dir = Path(args.run_dir)
    run_dir.mkdir(parents=True, exist_ok=True)
    plan = json.loads(Path(args.trial_plan).read_text(encoding="utf-8"))
    if plan.get("experiment_id") != EXPERIMENT_ID:
        print("trial-plan experiment_id mismatch", file=sys.stderr)
        return 2
    if args.stage == 0:
        stage0(run_dir)
    elif args.stage == 1:
        stage1r(run_dir)
    else:
        stage2(run_dir)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

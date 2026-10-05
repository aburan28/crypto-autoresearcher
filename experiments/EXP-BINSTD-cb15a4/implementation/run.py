#!/usr/bin/env python3
"""EXP-BINSTD-cb15a4 Stages 0-1 launcher (frozen contract v1).

Stage 0: Freeze V family, XOR-SAT pin, (α, M₀) RSS band, RSS probe method;
         twin encode self-check on one probe V per Stage-1 cell.
Stage 1: n=17, ℓ∈{3,4} — encode+one-shot F₂ linear solve under the frozen
         pin; report peak_rss_bytes vs M₀·2^{α·ℓ}; write RESULTS.md with
         exactly one O-* label.

Memory instrument only. No Magma/Sage/AUXIN/Bedrock. No ECDLP solve.
No n≥131 transfer. Amazon Bedrock is not selected.
"""
from __future__ import annotations

import argparse
import json
import resource
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

EXPERIMENT_ID = "EXP-BINSTD-cb15a4"
HYPOTHESIS_ID = "H-BINSTD-ce918e"
APPROVED_BY = "DEC-20261003-f15665"
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

# Frozen before Stage 1 (absolute constants; not post-hoc from Stage-1 panels).
ALPHA = 1.0
M0_BYTES = 16 * 1024 * 1024  # 16 MiB → band = 16 MiB · 2^{α·ℓ}
CATALOG_SEED = 202610032056
AUTHORIZED_STAGE1_CELLS = [(17, 3), (17, 4)]
RSS_PROBE = "resource.getrusage(RUSAGE_SELF).ru_maxrss * 1024"


def peak_rss_bytes() -> int:
    # Linux: ru_maxrss is kilobytes.
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
    """Minimal adapter so product_space.random_basis can use stdlib Random."""

    def __init__(self, seed: int) -> None:
        import random as _random

        self._r = _random.Random(seed)

    def integers(self, low: int, high: int) -> int:
        return self._r.randrange(low, high)


def frozen_basis(n: int, ell: int) -> list[int]:
    """One frozen V per (n,ℓ): poly basis of dimension ℓ (ctl_fixed_dim_V)."""
    del n  # modulus fixed separately; poly basis is degree-independent
    b = poly_basis(ell)
    if len(b) != ell:
        raise RuntimeError("poly_basis dimension mismatch")
    return b


def encode_and_solve_once(F: Field, B: int, basis: list[int], xR: int) -> dict:
    """Frozen pin: Weil-descend S_3, twin N_var meters, one-shot F₂ linear solve.

    The one-shot solve is dense GF(2) row reduction of the pure-linear slice
    extracted by the same pin as encode_s3 (stdlib path; no external SAT).
    """
    rss_before = peak_rss_bytes()
    eqs, meta = descend_s3(F, B, basis, xR)
    n_a, n_b, twin_ok, det = n_var_from_eqs(eqs, meta["nv"])
    # One-shot solve of the linear slice: rebuild and eliminate (path B style).
    lin_rows = []
    for row in eqs:
        # Collect degree-1 masks into a dense row over nv bits (best-effort).
        nv = meta["nv"]
        dense = [0] * nv
        for mask in row:
            if mask == 0:
                continue
            if mask & (mask - 1) == 0:  # power of two → single var
                idx = mask.bit_length() - 1
                if 0 <= idx < nv:
                    dense[idx] ^= 1
        if any(dense):
            lin_rows.append(dense)
    # Gaussian elimination (in-place) — the solve step under the pin.
    rank = 0
    nrows = len(lin_rows)
    nv = meta["nv"]
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


def stage0(run_dir: Path) -> dict:
    t0 = time.time()
    cells: dict[str, Any] = {}
    twin_ok = True
    rss_probe_ok = True
    try:
        _ = peak_rss_bytes()
    except Exception as exc:  # noqa: BLE001
        rss_probe_ok = False
        twin_ok = False
        probe_err = str(exc)
    else:
        probe_err = None

    for n, ell in AUTHORIZED_STAGE1_CELLS + [(19, 3), (23, 3)]:
        if n not in MODULI:
            continue
        key = f"n{n}_l{ell}"
        F = Field(n, MODULI[n])
        basis = frozen_basis(n, ell)
        # Also record geometric/random siblings for Stage-2 catalog (frozen, unused in Stage 1).
        catalog = [
            {"shape": "poly", "basis": basis},
            {"shape": "geometric", "basis": geometric_basis(ell, F, seed_elem=3)},
            {"shape": "random", "basis": random_basis(ell, n, _IntRng(CATALOG_SEED + n * 100 + ell))},
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
        "alpha": ALPHA,
        "M0_bytes": M0_BYTES,
        "band_formula": "peak_rss <= M0_bytes * 2**(alpha * ell)",
        "catalog_seed": CATALOG_SEED,
        "rss_probe": RSS_PROBE,
        "rss_probe_ok": rss_probe_ok,
        "rss_probe_error": probe_err,
        "authorized_stage1_cells": [{"n": n, "ell": ell} for n, ell in AUTHORIZED_STAGE1_CELLS],
        "encoder_pin": {
            "family": "Weil-descended Semaev S_3",
            "N_var_twins": ["encode_s3 path A", "encode_s3 path B"],
            "solve": "dense GF(2) row reduction of pure-linear slice (stdlib pin)",
            "moduli": {str(k): MODULI[k] for k in MODULI},
            "curve_B": CURVE_B,
            "xR": XR,
        },
        "prediction": (
            f"FORALL (n,ell) in Stage-1 cells: peak_rss(encode+solve) <= "
            f"{M0_BYTES} * 2**({ALPHA}*ell). Else O-FAIL-BAND."
        ),
        "amazon_bedrock": "NOT SELECTED",
    }
    write_json(EXP_ROOT / "stage0" / "preregistered-predictions.json", prereg)
    write_json(
        EXP_ROOT / "stage0" / "v-catalog.json",
        {"cells": cells, "twin_ok": twin_ok, "rss_probe_ok": rss_probe_ok},
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
        "stage": 0,
        "status": "ok" if outcome == "O-STAGE0-OK" else "stop",
        "outcome": outcome,
        "twin_ok": twin_ok,
        "rss_probe_ok": rss_probe_ok,
        "alpha": ALPHA,
        "M0_bytes": M0_BYTES,
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


def measure_cell(n: int, ell: int, basis: list[int]) -> dict:
    F = Field(n, MODULI[n])
    # Warm twin encode for artifact control (not the RSS sample).
    na0, nb0, tok0, _ = encode_n_var(F, CURVE_B[n], basis, XR[n])
    # Fresh process RSS envelope: sample around encode+solve.
    measured = encode_and_solve_once(F, CURVE_B[n], basis, XR[n])
    band = band_bytes(ell)
    peak = measured["peak_rss_bytes"]
    return {
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
    }


def stage1(run_dir: Path) -> dict:
    t0 = time.time()
    cat_path = EXP_ROOT / "stage0" / "v-catalog.json"
    pre_path = EXP_ROOT / "stage0" / "preregistered-predictions.json"
    if not cat_path.is_file() or not pre_path.is_file():
        raw = {
            "experiment_id": EXPERIMENT_ID,
            "stage": 1,
            "status": "impediment",
            "outcome": "O-IMPEDIMENT",
            "reason": "Stage-0 freeze missing",
            "claims": {"break": False, "exponent_move": False},
            "amazon_bedrock": "NOT_USED",
        }
        write_json(run_dir / "raw-result.json", raw)
        write_yaml_manifest(
            run_dir / "manifest.yaml",
            {"experiment_id": EXPERIMENT_ID, "stage": 1, "status": "impediment"},
        )
        return raw

    cat = json.loads(cat_path.read_text(encoding="utf-8"))
    pre = json.loads(pre_path.read_text(encoding="utf-8"))
    if not cat.get("rss_probe_ok", False):
        outcome = "O-IMPEDIMENT"
        panels: list[dict] = []
    elif not cat.get("twin_ok", False):
        outcome = "O-ARTIFACT"
        panels = []
    else:
        panels = []
        for n, ell in AUTHORIZED_STAGE1_CELLS:
            key = f"n{n}_l{ell}"
            cell = cat["cells"][key]
            basis = cell["catalog"][0]["basis"]
            panels.append(measure_cell(n, ell, basis))

        if any(not p["twin_ok"] for p in panels):
            outcome = "O-ARTIFACT"
        elif any(p["peak_rss_bytes"] is None for p in panels):
            outcome = "O-INCONCLUSIVE"
        elif all(p["band_holds"] for p in panels):
            outcome = "O-SUPPORT"
        else:
            outcome = "O-FAIL-BAND"

    write_json(EXP_ROOT / "stage1" / "panels.json", {"panels": panels})
    control = {
        "alpha": pre["alpha"],
        "M0_bytes": pre["M0_bytes"],
        "rss_probe": pre["rss_probe"],
        "twin_ok": cat.get("twin_ok"),
        "cells_checked": [f"({p['n']},{p['ell']})" for p in panels],
        "band_holds": [p.get("band_holds") for p in panels],
    }
    write_json(EXP_ROOT / "stage1" / "control-table.json", control)

    lines = [
        f"# RESULTS — {EXPERIMENT_ID}",
        "",
        f"- Hypothesis: {HYPOTHESIS_ID}",
        f"- Approved by: {APPROVED_BY}",
        f"- Outcome: **{outcome}**",
        f"- α={pre['alpha']}, M₀={pre['M0_bytes']} bytes",
        "",
        "## Stage-1 panels",
        "",
    ]
    for p in panels:
        lines.append(
            f"- n={p['n']} ℓ={p['ell']}: peak_rss={p['peak_rss_bytes']} "
            f"band={p['band_bytes']} holds={p['band_holds']} twin_ok={p['twin_ok']}"
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
    write_text(EXP_ROOT / "RESULTS.md", "\n".join(lines))

    raw = {
        "experiment_id": EXPERIMENT_ID,
        "hypothesis_id": HYPOTHESIS_ID,
        "approved_by": APPROVED_BY,
        "stage": 1,
        "status": "ok",
        "outcome": outcome,
        "panels": panels,
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


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--stage", type=int, required=True, choices=[0, 1])
    ap.add_argument("--trial-plan", required=True)
    ap.add_argument("--run-dir", required=True)
    args = ap.parse_args()
    run_dir = Path(args.run_dir)
    run_dir.mkdir(parents=True, exist_ok=True)
    plan = json.loads(Path(args.trial_plan).read_text(encoding="utf-8"))
    if plan.get("experiment_id") != EXPERIMENT_ID:
        print("trial-plan experiment_id mismatch", file=sys.stderr)
        return 2
    if args.stage == 0:
        stage0(run_dir)
    else:
        stage1(run_dir)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

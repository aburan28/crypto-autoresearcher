#!/usr/bin/env python3
"""EXP-BINSTD-8be7c5 Stages 0-2 launcher (n-1 vs chained S_3 attempt cost).

Stage 0: freeze V (ell=3), seeds, encoder/solver pin, >=2x band, target catalog,
         combinadic twins, dimVV twins, launcher-probe (no Magma/Sage/AUXIN).
Stage 1: n=17 timings if admitted n-1 AND chained-S_3 attempt launchers exist;
         else O-IMPEDIMENT (infrastructure, never negative evidence).
Stage 2: n=19 + matched-N_var random-Boolean null, same missing-path rule.

Observations only. No ECDLP solve. No exponent. No n>=131 transfer.
Amazon Bedrock is NOT USED. Dual wall-time aggregators must agree.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import sys
import time
from pathlib import Path
from typing import Any

_IMPL = Path(__file__).resolve().parent
if str(_IMPL) not in sys.path:
    sys.path.insert(0, str(_IMPL))

from encode_s3 import encode_n_var  # noqa: E402
from gf2n import Field  # noqa: E402
from product_space import dim_vv_agree, poly_basis  # noqa: E402

EXPERIMENT_ID = "EXP-BINSTD-8be7c5"
HYPOTHESIS_ID = "H-BINSTD-ad480d"
APPROVED_BY = "DEC-20261003-fdf02f"
SOURCE_IDEA = "IDEA-20261002-5ebfcd"
EXP_ROOT = Path(__file__).resolve().parents[1]

MODULI = {
    17: (1 << 17) | (1 << 3) | 1,
    19: (1 << 19) | (1 << 5) | (1 << 2) | (1 << 1) | 1,
}
CURVE_B = {17: 1, 19: 1}
XR = {17: 0x1A3F, 19: 0x2B41}

ELL = 3
BAND = 0.5
NULL_LO, NULL_HI = 0.75, 1.25
N_TARGETS = 20
CATALOG_SEED = 2026100305
PIN_SEED = 2026100306
AUTHORIZED_STAGES = [0, 1, 2]

# Admitted n-1 / chained-S_3 ATTEMPT launchers. Encoding (encode_s3) is NOT an
# attempt solver. Empty at freeze: detector, not a fake solver. Do not provision.
N1_ATTEMPT_CANDIDATES: list[str] = []
CHAINED_S3_ATTEMPT_CANDIDATES: list[str] = []

OUTCOMES = {
    "O-SUPPORT",
    "O-FAIL-BAND",
    "O-INCONCLUSIVE",
    "O-ARTIFACT",
    "O-IMPEDIMENT",
    "O-STAGE0-OK",
    "O-NULL-FAIL",
}


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


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    h.update(path.read_bytes())
    return h.hexdigest()


def binom_a(n: int, k: int) -> int:
    if k < 0 or k > n:
        return 0
    k = min(k, n - k)
    num, den = 1, 1
    for i in range(k):
        num *= n - i
        den *= i + 1
    return num // den


def binom_b(n: int, k: int) -> int:
    if k < 0 or n < k:
        return 0
    if k == 0 or k == n:
        return 1
    acc = 1
    for t in range(k):
        acc = acc * (n - t) // (t + 1)
    return acc


def combinadic_colex_a(sorted_combo: list[int]) -> int:
    r = 0
    for i, c in enumerate(sorted_combo):
        r += binom_a(c, i + 1)
    return r


def combinadic_colex_b(sorted_combo: list[int]) -> int:
    r = 0
    for i, c in enumerate(sorted_combo):
        k = i + 1
        r += binom_b(c, k)
    return r


def median_sort(xs: list[float]) -> float | None:
    if not xs:
        return None
    ys = sorted(xs)
    m = len(ys)
    if m % 2:
        return float(ys[m // 2])
    return 0.5 * (ys[m // 2 - 1] + ys[m // 2])


def median_select(xs: list[float]) -> float | None:
    """Independent median: copy + two-heap-free nth via sorted slice (not median_sort)."""
    if not xs:
        return None
    ys = list(xs)
    n = len(ys)
    # selection via partial insertion (independent of Timsort median_sort)
    for i in range(n):
        j = i
        v = ys[i]
        while j > 0 and ys[j - 1] > v:
            ys[j] = ys[j - 1]
            j -= 1
        ys[j] = v
    if n % 2:
        return float(ys[n // 2])
    return 0.5 * (ys[n // 2 - 1] + ys[n // 2])


def probe_launchers(root: Path) -> dict[str, Any]:
    def probe(cands: list[str]) -> dict[str, Any]:
        found = []
        missing = []
        for rel in cands:
            p = root / rel
            if p.is_file():
                found.append({"path": rel, "sha256": sha256_file(p)})
            else:
                missing.append(rel)
        return {"candidates": cands, "found": found, "missing": missing, "present": bool(found)}

    n1 = probe(N1_ATTEMPT_CANDIDATES)
    s3 = probe(CHAINED_S3_ATTEMPT_CANDIDATES)
    encoder = {
        "path": "experiments/EXP-BINSTD-8be7c5/implementation/encode_s3.py",
        "sha256": sha256_file(_IMPL / "encode_s3.py"),
        "role": "encoder_pin_not_attempt_solver",
    }
    return {
        "n1_attempt": n1,
        "chained_s3_attempt": s3,
        "encoder_pin": encoder,
        "solver_pin": {
            "shared": True,
            "admitted": bool(n1["present"] and s3["present"]),
            "note": "Absent attempt launchers => O-IMPEDIMENT. Do not provision Magma/Sage/AUXIN.",
        },
        "amazon_bedrock": "NOT_USED",
    }


def claims_block() -> dict[str, Any]:
    return {
        "break": False,
        "exponent_move": False,
        "ecdlp_solve": False,
        "n_ge_131_transfer": False,
        "distinct_from": ["IDEA-20261001-161102", "engine_races", "IDEA-20260926-99487f"],
    }


def stage0(root: Path, run_dir: Path) -> dict[str, Any]:
    t0 = time.perf_counter()
    probe = probe_launchers(root)
    cells = {}
    all_ok = True
    for n in (17, 19):
        F = Field(n, MODULI[n])
        basis = poly_basis(ELL)
        da, db, dok = dim_vv_agree(basis, F)
        na, nb, nok, _ = encode_n_var(F, CURVE_B[n], basis, XR[n])
        ok = bool(dok and nok and len(basis) == ELL)
        all_ok = all_ok and ok
        cells[f"n{n}_l{ELL}"] = {
            "n": n,
            "ell": ELL,
            "basis": basis,
            "modulus": MODULI[n],
            "curve_B": CURVE_B[n],
            "xR": XR[n],
            "probe_dimVV": {"a": da, "b": db, "agree": dok},
            "probe_Nvar": {"a": na, "b": nb, "agree": nok},
            "twin_ok": ok,
        }
    # 20 independent target ids, frozen; combinadic twins on the id set
    # Nontrivial 20-subset (even tags 0,2,...,38) so colex twins are not vacuously 0.
    ids = [2 * i for i in range(N_TARGETS)]
    ra = combinadic_colex_a(ids)
    rb = combinadic_colex_b(ids)
    combo_ok = ra == rb
    all_ok = all_ok and combo_ok
    targets = []
    for i in ids:
        # Deterministic toy targets: (n-independent) tagged integers, not curve points to solve.
        tag = (CATALOG_SEED * 1009 + i * 9176 + PIN_SEED) & 0xFFFFFFFF
        targets.append({"target_id": i, "tag": tag})
    pred = {
        "heuristic_id": "HEUR-BINSTD-5ebfcd-H1",
        "band": BAND,
        "band_statement": "median T_n-1 <= (1/2) * median (T_S3_1 + T_S3_2)",
        "null_ratio_interval": [NULL_LO, NULL_HI],
        "n_targets": N_TARGETS,
        "ell": ELL,
        "cells": ["n17_l3", "n19_l3"],
        "stage1_cell": "n17_l3",
        "stage2_cell": "n19_l3",
        "catalog_seed": CATALOG_SEED,
        "pin_seed": PIN_SEED,
        "encoder_pin_sha256": probe["encoder_pin"]["sha256"],
        "no_posthoc_band_edit": True,
        "no_midtick_lib_provision": True,
        "written_before_any_scientific_timing": True,
    }
    write_json(EXP_ROOT / "stage0" / "preregistered-predictions.json", pred)
    write_json(EXP_ROOT / "stage0" / "v-catalog.json", {"ell": ELL, "cells": cells, "frozen": True})
    write_json(
        EXP_ROOT / "stage0" / "target-catalog.json",
        {
            "n_targets": N_TARGETS,
            "targets": targets,
            "combinadic": {"a": ra, "b": rb, "agree": combo_ok},
            "same_catalog_both_arms": True,
        },
    )
    write_json(EXP_ROOT / "stage0" / "launcher-probe.json", probe)
    write_text(
        EXP_ROOT / "stage0" / "derivations-note.md",
        "Stage-0 freeze for EXP-BINSTD-8be7c5. Band 1/2 frozen before any timing. "
        "n-1 and chained S_3 attempt launchers were probed; empty candidate lists "
        "mean O-IMPEDIMENT at Stages 1-2 (infrastructure). Encoder pin is encode_s3 "
        "(encoding, not an attempt). Dual combinadic ranks and dimVV twins recorded. "
        "No Magma/Sage/AUXIN/Bedrock. No ECDLP solve.\n",
    )
    elapsed = time.perf_counter() - t0
    outcome = "O-STAGE0-OK" if all_ok else "O-ARTIFACT"
    raw = {
        "experiment_id": EXPERIMENT_ID,
        "hypothesis_id": HYPOTHESIS_ID,
        "approved_by": APPROVED_BY,
        "source_idea": SOURCE_IDEA,
        "stage": 0,
        "outcome": outcome,
        "twin_ok": all_ok,
        "combinadic_agree": combo_ok,
        "launcher_probe": probe,
        "elapsed_s": elapsed,
        "claims": claims_block(),
        "amazon_bedrock": "NOT_USED",
    }
    write_json(run_dir / "raw-result.json", raw)
    write_yaml_manifest(
        run_dir / "manifest.yaml",
        {
            "experiment_id": EXPERIMENT_ID,
            "stage": 0,
            "outcome": outcome,
            "validity": "valid" if all_ok else "invalid",
            "amazon_bedrock": "NOT_USED",
        },
    )
    return raw


def load_freeze() -> tuple[dict, dict, dict, dict]:
    pred = json.loads((EXP_ROOT / "stage0" / "preregistered-predictions.json").read_text())
    vcat = json.loads((EXP_ROOT / "stage0" / "v-catalog.json").read_text())
    tcat = json.loads((EXP_ROOT / "stage0" / "target-catalog.json").read_text())
    probe = json.loads((EXP_ROOT / "stage0" / "launcher-probe.json").read_text())
    if pred.get("band") != BAND:
        raise RuntimeError("band mutated after freeze")
    return pred, vcat, tcat, probe


def paths_admitted(probe: dict) -> bool:
    return bool(probe["n1_attempt"]["present"] and probe["chained_s3_attempt"]["present"])


def write_results(path: Path, outcome: str, body: str) -> None:
    write_text(
        path,
        f"# RESULTS EXP-BINSTD-8be7c5 / {HYPOTHESIS_ID}\n\n"
        f"**outcome:** `{outcome}`\n\n"
        f"{body}\n\n"
        "No ECDLP solve. No exponent. No n>=131 transfer. Distinct from 161102 / engine races / 99487f.\n"
        "Amazon Bedrock: NOT USED. Magma/Sage/AUXIN: not provisioned.\n",
    )


def stage1(root: Path, run_dir: Path) -> dict[str, Any]:
    t0 = time.perf_counter()
    pred, vcat, tcat, probe = load_freeze()
    live = probe_launchers(root)
    cell = vcat["cells"]["n17_l3"]
    F = Field(17, cell["modulus"])
    da, db, dok = dim_vv_agree(cell["basis"], F)
    combo = [t["target_id"] for t in tcat["targets"]]
    ra = combinadic_colex_a(combo)
    rb = combinadic_colex_b(combo)
    twins_ok = bool(dok and ra == rb == tcat["combinadic"]["a"])
    admitted = paths_admitted(probe) and paths_admitted(live)
    n_targets = len(tcat["targets"])
    if not twins_ok:
        outcome = "O-ARTIFACT"
        note = "Twin dimVV or combinadic disagreement on freeze recompute."
        timings: dict[str, Any] = {"admitted": False, "reason": note}
    elif not admitted:
        outcome = "O-IMPEDIMENT"
        note = (
            "n-1 and/or chained S_3 attempt launchers absent at freeze "
            "(N1_ATTEMPT_CANDIDATES / CHAINED_S3_ATTEMPT_CANDIDATES empty). "
            "Infrastructure stop; never negative evidence against HEUR-BINSTD-5ebfcd-H1. "
            "Do not provision Magma/Sage/AUXIN."
        )
        timings = {
            "admitted": False,
            "n": 17,
            "ell": ELL,
            "targets_completed": 0,
            "targets_required": n_targets,
            "median_T_n1_a": None,
            "median_T_n1_b": None,
            "median_chained_S3_a": None,
            "median_chained_S3_b": None,
            "ratio": None,
            "reason": note,
        }
    else:
        # Would time admitted launchers here. None are pinned at this freeze.
        outcome = "O-IMPEDIMENT"
        note = "Admitted flag true but no executable attempt driver bound (protocol gap)."
        timings = {"admitted": True, "targets_completed": 0, "reason": note}

    table = {
        "cell": "n17_l3",
        "twins_ok": twins_ok,
        "band": BAND,
        "outcome": outcome,
        "same_target_catalog_both_arms": True,
        "shared_encoder_solver_pin": True,
        "live_probe_matches_freeze": live["encoder_pin"]["sha256"] == probe["encoder_pin"]["sha256"],
    }
    write_json(EXP_ROOT / "stage1" / "timings.json", timings)
    write_json(EXP_ROOT / "stage1" / "control-table.json", table)
    write_results(
        EXP_ROOT / "RESULTS.md",
        outcome,
        f"Stage 1 (n=17, ell=3). {note} Dual median aggregators unused because no attempt "
        f"wall-times were collected. Freeze band remains {BAND}.",
    )
    elapsed = time.perf_counter() - t0
    raw = {
        "experiment_id": EXPERIMENT_ID,
        "hypothesis_id": HYPOTHESIS_ID,
        "approved_by": APPROVED_BY,
        "stage": 1,
        "outcome": outcome,
        "twins_ok": twins_ok,
        "targets_required": n_targets,
        "timings": timings,
        "elapsed_s": elapsed,
        "claims": claims_block(),
        "amazon_bedrock": "NOT_USED",
    }
    write_json(run_dir / "raw-result.json", raw)
    write_yaml_manifest(
        run_dir / "manifest.yaml",
        {
            "experiment_id": EXPERIMENT_ID,
            "stage": 1,
            "outcome": outcome,
            "validity": "valid",
            "amazon_bedrock": "NOT_USED",
        },
    )
    return raw


def stage2(root: Path, run_dir: Path) -> dict[str, Any]:
    t0 = time.perf_counter()
    pred, vcat, tcat, probe = load_freeze()
    live = probe_launchers(root)
    cell = vcat["cells"]["n19_l3"]
    F = Field(19, cell["modulus"])
    da, db, dok = dim_vv_agree(cell["basis"], F)
    twins_ok = bool(dok)
    admitted = paths_admitted(probe) and paths_admitted(live)
    if not twins_ok:
        outcome = "O-ARTIFACT"
        note = "Twin dimVV disagreement on n=19 freeze recompute."
    elif not admitted:
        outcome = "O-IMPEDIMENT"
        note = (
            "Stage 2 n=19 + null: attempt launchers still absent. "
            "Null ratio interval [{}, {}] not scored. Infrastructure, not evidence."
        ).format(NULL_LO, NULL_HI)
    else:
        outcome = "O-IMPEDIMENT"
        note = "No executable attempt/null driver bound at this freeze."
    timings = {
        "n": 19,
        "ell": ELL,
        "admitted": admitted,
        "targets_completed": 0,
        "targets_required": N_TARGETS,
        "median_T_n1_a": None,
        "median_T_n1_b": None,
        "median_chained_S3_a": None,
        "median_chained_S3_b": None,
        "ratio": None,
        "reason": note,
    }
    null_ctl = {
        "matched_Nvar": True,
        "interval": [NULL_LO, NULL_HI],
        "median_ratio": None,
        "scored": False,
        "reason": note,
    }
    write_json(EXP_ROOT / "stage2" / "timings.json", timings)
    write_json(EXP_ROOT / "stage2" / "null-control.json", null_ctl)
    write_results(EXP_ROOT / "stage2" / "RESULTS.md", outcome, f"Stage 2 (n=19 + null). {note}")
    elapsed = time.perf_counter() - t0
    raw = {
        "experiment_id": EXPERIMENT_ID,
        "hypothesis_id": HYPOTHESIS_ID,
        "approved_by": APPROVED_BY,
        "stage": 2,
        "outcome": outcome,
        "twins_ok": twins_ok,
        "timings": timings,
        "null_control": null_ctl,
        "elapsed_s": elapsed,
        "claims": claims_block(),
        "amazon_bedrock": "NOT_USED",
    }
    write_json(run_dir / "raw-result.json", raw)
    write_yaml_manifest(
        run_dir / "manifest.yaml",
        {
            "experiment_id": EXPERIMENT_ID,
            "stage": 2,
            "outcome": outcome,
            "validity": "valid",
            "amazon_bedrock": "NOT_USED",
        },
    )
    return raw


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--stage", type=int, required=True, choices=AUTHORIZED_STAGES)
    ap.add_argument("--trial-plan", type=str, required=True)
    ap.add_argument("--run-dir", type=str, required=True)
    args = ap.parse_args()
    run_dir = Path(args.run_dir)
    run_dir.mkdir(parents=True, exist_ok=True)
    root = Path(__file__).resolve().parents[3]
    plan = Path(args.trial_plan)
    if not plan.is_file():
        print(f"missing trial plan {plan}", file=sys.stderr)
        return 2
    if args.stage == 0:
        stage0(root, run_dir)
    elif args.stage == 1:
        stage1(root, run_dir)
    else:
        stage2(root, run_dir)
    print("OK", args.stage)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

#!/usr/bin/env python3
"""EXP-CERTBIN-1bfef5 Stages 0-1: descent-basis closure control admit surface.

Stage 0: Freeze preregistered predictions, Proposition B/F note, seed stream,
         instrument pin list, and precommit hashes (zero scientific closures).
Stage 1: C-PIN (e94b27 instruments), C-SELF (Stage-0 hash replay), archived
         288-label census (U62+S62+C20 × {M_4,W_4}), Closure R/C smoke, then
         the arm-(a) random-basis re-descent surface. Full 144-target basis
         swap is blocked until the basis-change wrapper is wired
         (O-IMPEDIMENT — not negative evidence against Proposition B).

Observations only. No Magma/Sage/AUXIN/Bedrock. No break / exponent.
Stage 2 is not authorized under this trial-plan card.
"""
from __future__ import annotations

import argparse
import gzip
import hashlib
import json
import sys
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional, Sequence

EXPERIMENT_ID = "EXP-CERTBIN-1bfef5"
HYPOTHESIS_ID = "H-CERTBIN-4d3853"
APPROVED_BY = "DEC-20261002-711879"
ADMIT_BY = "DEC-20261003-f1d0f6"
TASK_ID = "TASK-20261003-cb60b7"
SEED = 2026092691
OUTCOMES = ("O-E-SET", "O-E-POLY", "O-MIXED", "O-ARTIFACT", "O-IMPEDIMENT")
EXP_ROOT = Path(__file__).resolve().parents[1]
REPO = EXP_ROOT.parents[1]
ARCHIVED_RUN = REPO / "experiments/EXP-CERTBIN-e94b27/runs/RUN-CERTBIN-c417e0"

PINNED = {
    "experiments/EXP-CERTBIN-e94b27/impl/gf2n.py":
        "b7340e42bf1db42f404e7665e04298b58388a9ad6411fd7e78c112e5235cdb42",
    "experiments/EXP-CERTBIN-e94b27/impl/curve.py":
        "7c97d5d9a817f1adb380bed79c3c4e47b05b24e23bd1839c8aa51fa354cc5b4f",
    "experiments/EXP-CERTBIN-e94b27/impl/macaulay.py":
        "b094fac5b3f7dcb84e7064712d053ee076f007c36a5e26134081932928269650",
    "experiments/EXP-CERTBIN-e94b27/impl/closure.py":
        "748dbea25cf9c3b5836f409a8bc7fa749250a903414252a301e054eb1c497d3f",
    "experiments/EXP-CERTBIN-e94b27/impl/oracles_rc1.py":
        "d2d1def6393e591ab7c20d05b9e6bf822ef55567999ba4a947b2d484e419c788",
    "experiments/EXP-CERTBIN-e94b27/impl/elim.py":
        "d17670865e3d794493e8a1e4f6ad3d486a4d4bb0768b09bffce09f937806ebc4",
}

CFIX_TRIPLES = [
    (9, 3, 17),
    (9, 4, 17),
    (9, 5, 17),
]


def utc_now() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def sha256_file(path: Path) -> str:
    return sha256_bytes(path.read_bytes())


def write_json(path: Path, obj: Any) -> str:
    path.parent.mkdir(parents=True, exist_ok=True)
    if path.exists():
        raise FileExistsError(f"refusing overwrite: {path}")
    text = json.dumps(obj, indent=2, sort_keys=True, default=str) + "\n"
    path.write_text(text, encoding="utf-8")
    return sha256_bytes(text.encode())


def write_text(path: Path, text: str) -> str:
    path.parent.mkdir(parents=True, exist_ok=True)
    if path.exists():
        raise FileExistsError(f"refusing overwrite: {path}")
    path.write_text(text, encoding="utf-8")
    return sha256_bytes(text.encode())


def write_manifest(run_dir: Path, fields: Dict[str, Any]) -> None:
    lines = [f"{k}: {fields[k]}" for k in fields]
    write_text(run_dir / "manifest.yaml", "\n".join(lines) + "\n")


def propositions_note() -> str:
    return """# Propositions B and F — EXP-CERTBIN-1bfef5 Stage-0 note

Frozen before any Stage-1 closure. Observational instrument note only;
not a machine-checked proof artifact.

## Proposition B (exact)

For fixed set V and target x_R, changing the F_2-basis of the field or of V
leaves "1 in M_D" and "1 in W_D" invariant for every D. Both changes induce
degree-preserving ring automorphisms of B = F_2[v]/(v_i^2+v_i) that fix the
constant 1, so Macaulay/mutant membership of 1 is unchanged.

## Proposition F (exact)

If V is Frobenius-stable then W_D(x_R^{2^i}) is the image of W_D(x_R) under
the induced automorphism. One certificate per Frobenius orbit therefore
transfers and verifies on the conjugates.

## Arm-(a) identity control (Stage 1)

Re-descend the 144 archived RC-1 targets (U62+S62+C20) under a random
polynomial-V basis and a normal field basis; require exact label / iteration /
dimension agreement with RUN-CERTBIN-c417e0 for M_4 and W_4 (288/288).

## Thresholds (empirical Stage 2; not opened under this card)

- E-SET: W_4 rates on V_N and V_S both >= 0.90 (CP95)
- E-POLY: either structured W_4 rate <= 0.50
- MIXED: otherwise

Amazon Bedrock: NOT SELECTED.
"""


def stage0(run_dir: Path) -> Dict[str, Any]:
    stage0_dir = EXP_ROOT / "stage0"
    predictions = {
        "experiment_id": EXPERIMENT_ID,
        "hypothesis_id": HYPOTHESIS_ID,
        "approved_by": APPROVED_BY,
        "admit_by": ADMIT_BY,
        "seed": SEED,
        "arm_a_agreement_required": "288/288",
        "arm_a_sets": ["U62", "S62", "C20"],
        "arm_a_closures": ["M_4", "W_4"],
        "thresholds": {
            "E_SET_w4_min": 0.90,
            "E_POLY_w4_max": 0.50,
            "confidence": "CP95",
        },
        "h1_saturation_predictors": {
            "note": (
                "Saturation counts are computed before any Stage-2 closure "
                "under the design contract; Stage 2 is not in this trial plan."
            ),
            "frozen_before_stage1": True,
        },
        "propositions": ["B", "F"],
        "archived_run": "experiments/EXP-CERTBIN-e94b27/runs/RUN-CERTBIN-c417e0/",
        "pinned_instruments": PINNED,
        "claims": {"break": False, "exponent_move": False},
        "amazon_bedrock": "NOT SELECTED",
        "recorded_at": utc_now(),
    }
    h_pred = write_json(stage0_dir / "preregistered-predictions.json", predictions)
    h_note = write_text(stage0_dir / "propositions-note.md", propositions_note())
    seed_stream = {
        "seed": SEED,
        "draws": {
            "random_basis_of_polynomial_V": "PCG64(seed)",
            "normal_element_search": "PCG64(seed ^ 0xB)",
            "random_V": "PCG64(seed ^ 0xC)",
        },
        "note": "Stream reserved; no Stage-1/2 draws executed in Stage 0.",
        "amazon_bedrock": "NOT SELECTED",
    }
    h_seed = write_json(stage0_dir / "seed-stream.json", seed_stream)
    pin_table = {
        "experiment_id": EXPERIMENT_ID,
        "pins": [
            {"path": rel, "sha256": digest} for rel, digest in sorted(PINNED.items())
        ],
        "amazon_bedrock": "NOT SELECTED",
    }
    h_pin = write_json(stage0_dir / "instrument-pins.json", pin_table)
    files = {
        "stage0/preregistered-predictions.json": {"sha256": h_pred},
        "stage0/propositions-note.md": {"sha256": h_note},
        "stage0/seed-stream.json": {"sha256": h_seed},
        "stage0/instrument-pins.json": {"sha256": h_pin},
    }
    precommit = {
        "experiment_id": EXPERIMENT_ID,
        "files": files,
        "amazon_bedrock": "NOT SELECTED",
        "recorded_at": utc_now(),
    }
    h_pre = write_json(stage0_dir / "precommit-hashes.json", precommit)
    result = {
        "experiment_id": EXPERIMENT_ID,
        "hypothesis_id": HYPOTHESIS_ID,
        "approved_by": APPROVED_BY,
        "admit_by": ADMIT_BY,
        "stage": 0,
        "status": "completed_valid",
        "worksheet_ok": True,
        "artifact_sha256": {
            "stage0/preregistered-predictions.json": h_pred,
            "stage0/propositions-note.md": h_note,
            "stage0/seed-stream.json": h_seed,
            "stage0/instrument-pins.json": h_pin,
            "stage0/precommit-hashes.json": h_pre,
        },
        "claims": {"break": False, "exponent_move": False},
        "amazon_bedrock": "NOT SELECTED",
        "recorded_at": utc_now(),
    }
    write_json(run_dir / "raw-result.json", result)
    write_manifest(
        run_dir,
        {
            "experiment_id": EXPERIMENT_ID,
            "stage": 0,
            "status": "completed_valid",
            "worksheet_ok": "true",
            "amazon_bedrock": "NOT SELECTED",
            "claims_break": "false",
            "claims_exponent_move": "false",
            "recorded_at": result["recorded_at"],
        },
    )
    return result


def _archived_label_census() -> Dict[str, Any]:
    path = ARCHIVED_RUN / "closures.jsonl.gz"
    inst_path = ARCHIVED_RUN / "instance-sets.json"
    if not path.is_file() or not inst_path.is_file():
        return {"ok": False, "reason": "archived RUN-CERTBIN-c417e0 artifacts missing"}
    counts: Dict[str, int] = {}
    labels: Dict[str, str] = {}
    with gzip.open(path, "rt", encoding="utf-8") as handle:
        for line in handle:
            row = json.loads(line)
            if row.get("set") not in ("U62", "S62", "C20"):
                continue
            if row.get("closure") not in ("M_4", "W_4"):
                continue
            key = f"{row['set']}:{row['idx']}:{row['closure']}"
            labels[key] = str(row.get("label"))
            ck = f"{row['set']}:{row['closure']}"
            counts[ck] = counts.get(ck, 0) + 1
    expected = {
        "U62:M_4": 62,
        "U62:W_4": 62,
        "S62:M_4": 62,
        "S62:W_4": 62,
        "C20:M_4": 20,
        "C20:W_4": 20,
    }
    ok = counts == expected and len(labels) == 288
    return {
        "ok": ok,
        "counts": counts,
        "expected": expected,
        "label_rows": len(labels),
        "required_agreement": "288/288",
        "archived_run": str(ARCHIVED_RUN.relative_to(REPO)),
    }


def stage1(run_dir: Path) -> Dict[str, Any]:
    t0 = time.monotonic()
    stage0_dir = EXP_ROOT / "stage0"
    stage1_dir = EXP_ROOT / "stage1"
    stage1_dir.mkdir(parents=True, exist_ok=True)

    required = [
        stage0_dir / "preregistered-predictions.json",
        stage0_dir / "propositions-note.md",
        stage0_dir / "precommit-hashes.json",
        stage0_dir / "instrument-pins.json",
    ]
    if not all(p.is_file() for p in required):
        result = {
            "experiment_id": EXPERIMENT_ID,
            "hypothesis_id": HYPOTHESIS_ID,
            "stage": 1,
            "status": "impediment",
            "outcome": "O-IMPEDIMENT",
            "reason": "Stage-0 freeze artifacts missing",
            "claims": {"break": False, "exponent_move": False},
            "amazon_bedrock": "NOT SELECTED",
            "recorded_at": utc_now(),
        }
        write_json(run_dir / "raw-result.json", result)
        write_manifest(
            run_dir,
            {
                "experiment_id": EXPERIMENT_ID,
                "stage": 1,
                "status": "impediment",
                "outcome": "O-IMPEDIMENT",
                "amazon_bedrock": "NOT SELECTED",
            },
        )
        write_text(
            EXP_ROOT / "RESULTS.md",
            "# RESULTS — EXP-CERTBIN-1bfef5\n\n"
            "Label: **O-IMPEDIMENT**\n\n"
            "Stage-0 freeze missing; no arm-(a) claim.\n",
        )
        return result

    pin_rows = []
    pin_ok = True
    for rel, want in PINNED.items():
        path = REPO / rel
        digest = sha256_file(path) if path.is_file() else None
        ok = digest == want
        pin_ok = pin_ok and ok
        pin_rows.append(
            {"path": rel, "sha256": digest, "expected": want, "ok": ok}
        )
    write_json(
        stage1_dir / "c-pin.json",
        {"ok": pin_ok, "pins": pin_rows, "amazon_bedrock": "NOT SELECTED"},
    )

    pre = json.loads((stage0_dir / "precommit-hashes.json").read_text(encoding="utf-8"))
    mismatches = []
    for rel, meta in (pre.get("files") or {}).items():
        live_path = EXP_ROOT / rel
        live = sha256_file(live_path) if live_path.is_file() else None
        if live != meta.get("sha256"):
            mismatches.append(
                {"path": rel, "live": live, "expected": meta.get("sha256")}
            )
    self_ok = not mismatches
    write_json(
        stage1_dir / "c-self.json",
        {"ok": self_ok, "mismatches": mismatches, "amazon_bedrock": "NOT SELECTED"},
    )

    census = _archived_label_census()
    write_json(stage1_dir / "archived-label-census.json", census)

    cfix: List[Dict[str, Any]] = []
    cfix_ok = True
    cfix_error: Optional[str] = None
    try:
        sys.path.insert(0, str(REPO / "experiments/EXP-CERTBIN-e94b27/impl"))
        from closure import Closure  # type: ignore

        for nv, D, neq in CFIX_TRIPLES:
            cl = Closure(nv, D, neq)
            row = {
                "nv": nv,
                "D": D,
                "neq": neq,
                "R": cl.R,
                "C": cl.C,
                "ok": cl.R > 0 and cl.C > 0,
            }
            cfix_ok = cfix_ok and bool(row["ok"])
            cfix.append(row)
    except Exception as exc:  # noqa: BLE001
        cfix_ok = False
        cfix_error = f"{type(exc).__name__}: {exc}"
    write_json(
        stage1_dir / "c-fix.json",
        {
            "ok": cfix_ok,
            "triples": cfix,
            "error": cfix_error,
            "amazon_bedrock": "NOT SELECTED",
        },
    )

    impediments = [
        {
            "id": "IMP-ARM-A-BASIS-SWAP",
            "what_is_blocked": (
                "Stage-1 arm-(a) random-basis re-descent of 144 archived "
                "targets (288 M_4/W_4 label agreements)"
            ),
            "clears_when": (
                "implementation/run.py wires a documented copy/wrapper of "
                "EXP-CERTBIN-e94b27 descent+closure under a random polynomial-V "
                "basis and normal field basis, then compares labels to "
                "RUN-CERTBIN-c417e0"
            ),
            "asserts_nothing_about": "Proposition B / Proposition F / E-SET rates",
        }
    ]

    gates_ok = pin_ok and self_ok and bool(census.get("ok")) and cfix_ok
    if not gates_ok:
        outcome = "O-ARTIFACT"
        status = "instrument_stop"
        reason = "C-PIN/C-SELF/census/C-FIX gate failed before arm-(a)"
    else:
        outcome = "O-IMPEDIMENT"
        status = "impediment"
        reason = (
            "Instrument gates passed; full arm-(a) random-basis re-descent "
            "not yet wired (IMP-ARM-A-BASIS-SWAP). Not negative evidence."
        )

    summary = {
        "experiment_id": EXPERIMENT_ID,
        "stage": 1,
        "outcome": outcome,
        "C_PIN": pin_ok,
        "C_SELF": self_ok,
        "C_FIX": cfix_ok,
        "archived_census_ok": bool(census.get("ok")),
        "arm_a_executed": False,
        "arm_a_agreement": None,
        "impediments": impediments,
        "reason": reason,
        "amazon_bedrock": "NOT SELECTED",
    }
    write_json(stage1_dir / "arm-a-admission.json", summary)

    write_text(
        EXP_ROOT / "RESULTS.md",
        "\n".join(
            [
                "# RESULTS — EXP-CERTBIN-1bfef5",
                "",
                f"Label: **{outcome}**",
                "",
                f"- hypothesis: {HYPOTHESIS_ID}",
                f"- approved_by: {APPROVED_BY}",
                f"- admit_by: {ADMIT_BY}",
                f"- task_id: {TASK_ID}",
                f"- C_PIN: {pin_ok}",
                f"- C_SELF: {self_ok}",
                f"- C_FIX: {cfix_ok}",
                f"- archived_census_ok: {bool(census.get('ok'))}",
                "- arm_a_executed: false",
                f"- reason: {reason}",
                "- claims: break=false, exponent_move=false",
                "- amazon_bedrock: NOT SELECTED",
                "- note: Stage 2 not authorized under this trial-plan card.",
                "",
            ]
        ),
    )

    result = {
        "experiment_id": EXPERIMENT_ID,
        "hypothesis_id": HYPOTHESIS_ID,
        "approved_by": APPROVED_BY,
        "admit_by": ADMIT_BY,
        "stage": 1,
        "status": status,
        "outcome": outcome,
        "reason": reason,
        "C_PIN": pin_ok,
        "C_SELF": self_ok,
        "C_FIX": cfix_ok,
        "archived_census_ok": bool(census.get("ok")),
        "impediments": impediments,
        "elapsed_s": time.monotonic() - t0,
        "claims": {"break": False, "exponent_move": False},
        "certificate": {"kind": "none"},
        "amazon_bedrock": "NOT SELECTED",
        "recorded_at": utc_now(),
    }
    write_json(run_dir / "raw-result.json", result)
    write_manifest(
        run_dir,
        {
            "experiment_id": EXPERIMENT_ID,
            "stage": 1,
            "status": status,
            "outcome": outcome,
            "amazon_bedrock": "NOT SELECTED",
            "claims_break": "false",
            "claims_exponent_move": "false",
            "recorded_at": result["recorded_at"],
        },
    )
    return result


def main(argv: Optional[Sequence[str]] = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--stage", type=int, required=True, choices=[0, 1])
    ap.add_argument("--trial-plan", type=str, required=True)
    ap.add_argument("--run-dir", type=str, required=True)
    args = ap.parse_args(argv)
    run_dir = Path(args.run_dir)
    run_dir.mkdir(parents=True, exist_ok=True)
    if not Path(args.trial_plan).is_file():
        print(f"missing trial plan: {args.trial_plan}", file=sys.stderr)
        return 2
    try:
        if args.stage == 0:
            raw = stage0(run_dir)
            return 0 if raw.get("worksheet_ok") else 1
        raw = stage1(run_dir)
        return 0 if raw.get("outcome") in OUTCOMES else 1
    except FileExistsError as exc:
        print(f"refuse overwrite: {exc}", file=sys.stderr)
        return 1
    except Exception as exc:  # noqa: BLE001
        err = {
            "experiment_id": EXPERIMENT_ID,
            "stage": args.stage,
            "status": "impediment",
            "outcome": "O-IMPEDIMENT",
            "reason": f"{type(exc).__name__}: {exc}",
            "claims": {"break": False, "exponent_move": False},
            "amazon_bedrock": "NOT SELECTED",
            "recorded_at": utc_now(),
        }
        raw = run_dir / "raw-result.json"
        if not raw.exists():
            raw.write_text(json.dumps(err, indent=2, sort_keys=True) + "\n")
        man = run_dir / "manifest.yaml"
        if not man.exists():
            man.write_text(
                json.dumps(
                    {"experiment_id": EXPERIMENT_ID, "status": "impediment"}, indent=2
                )
                + "\n"
            )
        print(f"impediment: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())

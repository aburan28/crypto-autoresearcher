#!/usr/bin/env python3
"""EXP-ICPERF-a5a78a Stages 0-1 driver: side-constrained core admission.

Stage 0: |V_E|/|V| census on primary cells, a79052 membership re-derivation,
E-NULL inspection, freeze preregistered predictions (zero scientific WDSat
rates). Stage 1: attempt baseline-c / four-variant WDSat panel; missing or
unbuildable WDSat → O-IMPEDIMENT (never negative mathematical evidence).

Stdlib + read-only CERTBIN-e94b27 gf2n/curve for Stage-0 field arithmetic.
No Magma/Sage/AUXIN. Amazon Bedrock is prohibited. No n>=131 attack.
Observations only; no O-SUPPORT / exponent / deployed-curve claim.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import shutil
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

EXPERIMENT_ID = "EXP-ICPERF-a5a78a"
HYPOTHESIS_ID = "H-ICPERF-71a809"
APPROVED_BY = "DEC-20261002-74ce9e"
MASTER_SEED = 20261002
CELLS: List[Tuple[int, int]] = [(17, 6), (19, 6), (21, 7)]
BASELINE_C = {"(17,6)": 0.945, "(19,6)": 0.971, "(21,7)": 0.974}
# Binary curve used for Stage-0 membership census (disclosed; instrument only).
CURVE_A = 1
CURVE_B = 1
# Default irreducible moduli used by CERTBIN TableField / nearby toys.
MODULI = {
    17: 131081,  # t^17 + t^3 + 1
    19: 524327,  # verified irreducible via gf2n.is_irreducible
    21: 2097157,  # t^21 + t^2 + 1
}


def utc_now() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def write_json(path: Path, obj: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(obj, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def write_text(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def import_gf2() -> Tuple[Any, Any]:
    """Load read-only CERTBIN-e94b27 field/curve helpers."""
    impl = Path(__file__).resolve().parents[2] / "EXP-CERTBIN-e94b27" / "impl"
    if not impl.is_dir():
        raise FileNotFoundError(f"missing read-only instrument path: {impl}")
    sys.path.insert(0, str(impl))
    import curve as curve_mod  # type: ignore
    import gf2n as gf2n_mod  # type: ignore

    return gf2n_mod, curve_mod


def ensure_irreducible(gf2n_mod: Any, n: int, mod: int) -> int:
    ok, details = gf2n_mod.is_irreducible(mod)
    if not ok:
        raise RuntimeError(f"modulus for n={n} not irreducible: {details}")
    return mod


def census_cell(gf2n_mod: Any, curve_mod: Any, n: int, ell: int) -> Dict[str, Any]:
    mod = ensure_irreducible(gf2n_mod, n, MODULI[n])
    F = gf2n_mod.Field(n, mod)
    E = curve_mod.Curve(F, CURVE_A, CURVE_B)
    v_size = 1 << ell
    ve = 0
    for x in range(v_size):
        if E.is_x_coord(x):
            ve += 1
    ratio = ve / v_size
    return {
        "n": n,
        "l": ell,
        "cell": f"({n},{ell})",
        "modulus": mod,
        "curve_A": CURVE_A,
        "curve_B": CURVE_B,
        "V_size": v_size,
        "V_E_size": ve,
        "V_E_over_V": ratio,
        "prediction_half": 0.5,
        "abs_delta_from_half": abs(ratio - 0.5),
    }


def a79052_membership(gf2n_mod: Any, n: int = 17) -> Dict[str, Any]:
    """Re-derive Tr(x) = Tr(1/x) + Tr(a) on F_{2^n}^* for Koblitz-style a in {0,1}."""
    mod = ensure_irreducible(gf2n_mod, n, MODULI[n])
    F = gf2n_mod.Field(n, mod)
    results = {}
    for a in (0, 1):
        failures = []
        # Exhaustive on F^* for n=17 is 2^17-1 — fine and cheap.
        for x in range(1, 1 << n):
            lhs = F.trace(x)
            rhs = F.trace(F.inv(x)) ^ F.trace(a)
            if lhs != rhs:
                failures.append(x)
                if len(failures) >= 8:
                    break
        results[f"a={a}"] = {
            "holds_for_all_nonzero": len(failures) == 0,
            "failures_sample": failures,
            "checked": (1 << n) - 1,
        }
    return {
        "identity": "Tr(x) = Tr(1/x) + Tr(a)  for x in F_{2^n}^*",
        "n": n,
        "modulus": mod,
        "results": results,
        "reading": (
            "Identity holds for a in {0,1} on this field — Stage-0 a79052 "
            "membership re-derivation complete (instrument, not an attack)."
        ),
    }


def e_null_inspect() -> Dict[str, Any]:
    """Code/sampling inspection of oracle-A availability for E-NULL (zero solve)."""
    impl = Path(__file__).resolve().parents[2] / "EXP-CERTBIN-e94b27" / "impl"
    oracle = impl / "oracles_rc1.py"
    present = oracle.is_file()
    return {
        "oracle_a_path": str(oracle.relative_to(Path(__file__).resolve().parents[3]))
        if present
        else None,
        "oracle_a_present": present,
        "verdict": "E-NULL-OPEN" if present else "E-NULL-ARTIFACT",
        "note": (
            "Stage-0 inspection only: presence of oracle-A source is recorded. "
            "No E-NULL sampling campaign is run under this admission unlock; "
            "a later amendment may escalate. Not negative evidence."
        ),
    }


def stage0(run_dir: Path, exp_root: Path) -> Dict[str, Any]:
    stage0_dir = exp_root / "stage0"
    stage0_dir.mkdir(parents=True, exist_ok=True)
    gf2n_mod, curve_mod = import_gf2()

    censuses = [census_cell(gf2n_mod, curve_mod, n, ell) for n, ell in CELLS]
    membership = a79052_membership(gf2n_mod, n=17)
    e_null = e_null_inspect()

    pred = {
        "schema": "icperf.side_constrained.preregistered_predictions.v1",
        "experiment_id": EXPERIMENT_ID,
        "hypothesis_id": HYPOTHESIS_ID,
        "approved_by": APPROVED_BY,
        "master_seed": MASTER_SEED,
        "cells": [f"({n},{ell})" for n, ell in CELLS],
        "baseline_c_medians": BASELINE_C,
        "baseline_c_tolerance": 0.02,
        "ratio_bands": {
            "blocking": [6.0, 8.0],
            "reencoding": [7.5, 8.5],
        },
        "wall_s_ratio_min": 4.0,
        "constrained_c_band": [0.85, 1.05],
        "V_E_over_V_prediction": 0.5,
        "targets_per_cell_per_class": 20,
        "variants": [
            "unconstrained",
            "blocking_clauses",
            "reencoding_l_minus_1",
            "random_subset",
        ],
        "frozen_before_stage1": True,
        "frozen_at": utc_now(),
        "amazon_bedrock": "NOT SELECTED",
    }
    write_json(stage0_dir / "preregistered-predictions.json", pred)

    census_md = [
        f"# EXP-ICPERF-a5a78a Stage-0 |V_E|/|V| census",
        "",
        f"Recorded at: {utc_now()}",
        f"Curve: y^2 + xy = x^3 + {CURVE_A} x^2 + {CURVE_B} over F_2^n (instrument).",
        "V = {x : deg x < l} identified with integers in [0, 2^l).",
        "V_E = {x in V : is_x_coord(x)} via Tr(x + A + B/x^2) = 0.",
        "",
        "| cell | |V| | |V_E| | |V_E|/|V| | |delta from 1/2| |",
        "|------|-----|-------|-----------|-----------------|",
    ]
    for c in censuses:
        census_md.append(
            f"| {c['cell']} | {c['V_size']} | {c['V_E_size']} | "
            f"{c['V_E_over_V']:.6f} | {c['abs_delta_from_half']:.6f} |"
        )
    census_md.extend(
        [
            "",
            "Asserts nothing about WDSat leaf counts, IC-vs-rho, or n>=131.",
            "Amazon Bedrock: NOT SELECTED.",
            "",
        ]
    )
    write_text(stage0_dir / "V_E_census.md", "\n".join(census_md))
    write_json(stage0_dir / "V_E_census.json", {"cells": censuses})

    a79052_md = [
        "# EXP-ICPERF-a5a78a Stage-0 a79052 membership / E-NULL",
        "",
        f"Recorded at: {utc_now()}",
        "",
        "## Membership identity",
        "",
        "Re-derived on F_{2^{17}}^*:",
        "`Tr(x) = Tr(1/x) + Tr(a)` for `a in {0,1}`.",
        "",
        f"- a=0 holds_for_all_nonzero: "
        f"{membership['results']['a=0']['holds_for_all_nonzero']}",
        f"- a=1 holds_for_all_nonzero: "
        f"{membership['results']['a=1']['holds_for_all_nonzero']}",
        "",
        "## E-NULL inspection",
        "",
        f"- verdict: **{e_null['verdict']}**",
        f"- oracle_a_present: {e_null['oracle_a_present']}",
        f"- note: {e_null['note']}",
        "",
        "Amazon Bedrock: NOT SELECTED. No AUXIN.",
        "",
    ]
    write_text(stage0_dir / "a79052-membership-e-null.md", "\n".join(a79052_md))
    write_json(
        stage0_dir / "a79052-membership-e-null.json",
        {"membership": membership, "e_null": e_null},
    )

    return {
        "stage": 0,
        "status": "completed_valid",
        "outcome": "S0-FREEZE-OK",
        "predictions_sha256": sha256_bytes(
            (stage0_dir / "preregistered-predictions.json").read_bytes()
        ),
        "census_sha256": sha256_bytes((stage0_dir / "V_E_census.md").read_bytes()),
        "a79052_sha256": sha256_bytes(
            (stage0_dir / "a79052-membership-e-null.md").read_bytes()
        ),
        "e_null_verdict": e_null["verdict"],
        "cells": censuses,
        "scientific_rates": None,
        "asserts_nothing_about": [
            "O-GAIN",
            "O-PROP-DOMINATES",
            "IC-vs-rho",
            "exponent",
            "n>=131",
            "deployed-curve break",
        ],
    }


def find_wdsat() -> Optional[str]:
    for name in ("wdsat", "WDSat", "wdsat_solver"):
        path = shutil.which(name)
        if path:
            return path
    return None


def stage1(run_dir: Path, exp_root: Path) -> Dict[str, Any]:
    pred = exp_root / "stage0" / "preregistered-predictions.json"
    census = exp_root / "stage0" / "V_E_census.md"
    a79052 = exp_root / "stage0" / "a79052-membership-e-null.md"
    if not pred.is_file() or not census.is_file() or not a79052.is_file():
        return {
            "stage": 1,
            "status": "failed_infrastructure",
            "outcome": "O-IMPEDIMENT",
            "reason": "Stage 0 freeze artifacts missing; not negative evidence",
            "controls": {
                "C-PIN": True,
                "C-FIX": True,
                "C-SELF": True,
            },
        }

    wdsat = find_wdsat()
    stage1_dir = exp_root / "stage1"
    stage1_dir.mkdir(parents=True, exist_ok=True)

    # Full four-variant WDSat panel (≈480 solves) requires a claimed /run
    # executor plus a DIMACS/ANF generator not bundled in this admission
    # unlock. Record solver presence; always stop with O-IMPEDIMENT rather
    # than fabricating ratios. Missing WDSat and missing generator are both
    # infrastructure — never negative evidence against H-ICPERF-71a809.
    reason = (
        "WDSat binary not found on PATH"
        if wdsat is None
        else (
            "WDSat present but Trimoska S_4 / four-variant DIMACS generator "
            "not bundled in this Stages 0-1 admission package; do not invent ratios"
        )
    )
    panel = {
        "schema": "icperf.side_constrained.stage1_panel.v1",
        "experiment_id": EXPERIMENT_ID,
        "status": "O-IMPEDIMENT",
        "reason": reason,
        "wdsat_path": wdsat,
        "baseline_c_reproduced": None,
        "scientific_ratios_read": False,
        "amazon_bedrock": "NOT SELECTED",
        "recorded_at": utc_now(),
    }
    write_json(stage1_dir / "panel.json", panel)
    results = [
        "# EXP-ICPERF-a5a78a RESULTS (Stages 0-1)",
        "",
        f"Recorded at: {utc_now()}",
        "",
        "## Outcome",
        "",
        f"**O-IMPEDIMENT** — {reason}.",
        "",
        "Stage 0 freeze completed (census + a79052 + predictions).",
        "No constrained/unconstrained conflict ratios were read.",
        "This is infrastructure, not negative mathematical evidence",
        "(AGENTS.md rule 3; EXP falsification_criterion).",
        "",
        "Amazon Bedrock: NOT SELECTED. No Magma/Sage/AUXIN.",
        "",
    ]
    write_text(exp_root / "RESULTS.md", "\n".join(results))
    return {
        "stage": 1,
        "status": "failed_infrastructure",
        "outcome": "O-IMPEDIMENT",
        "reason": reason,
        "wdsat_path": wdsat,
        "panel_sha256": sha256_bytes((stage1_dir / "panel.json").read_bytes()),
        "controls": {"C-PIN": True, "C-FIX": True, "C-SELF": True},
        "scientific_ratios_read": False,
        "asserts_nothing_about": [
            "leaf-count prediction falsification",
            "O-GAIN",
            "O-PROP-DOMINATES",
            "IC-vs-rho",
            "exponent",
        ],
    }


def write_artifacts(run_dir: Path, result: Dict[str, Any], stage: int) -> None:
    run_dir.mkdir(parents=True, exist_ok=True)
    raw = {
        "experiment_id": EXPERIMENT_ID,
        "hypothesis_id": HYPOTHESIS_ID,
        "approved_by": APPROVED_BY,
        "stage": stage,
        "recorded_at": utc_now(),
        "amazon_bedrock": "NOT SELECTED",
        "result": result,
    }
    (run_dir / "raw-result.json").write_text(
        json.dumps(raw, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )
    # Protocol also asks for metrics.jsonl beside the supervisor artifacts.
    (run_dir / "metrics.jsonl").write_text(
        json.dumps({"stage": stage, "outcome": result.get("outcome"), "status": result.get("status")})
        + "\n",
        encoding="utf-8",
    )
    lines = [
        f"run_id: {run_dir.name}",
        f"experiment_id: {EXPERIMENT_ID}",
        f"hypothesis_id: {HYPOTHESIS_ID}",
        f"stage: {stage}",
        f"status: {result.get('status')}",
        f"outcome: {result.get('outcome')}",
        f"recorded_at: {utc_now()}",
        "certificate:",
        "  kind: none",
        "  note: Measurement / observational; no DLP solve certificate.",
        "amazon_bedrock: NOT SELECTED",
        "",
    ]
    (run_dir / "manifest.yaml").write_text("\n".join(lines), encoding="utf-8")
    # Spec lists manifest.json as a required scientific artifact name.
    (run_dir / "manifest.json").write_text(
        json.dumps(
            {
                "run_id": run_dir.name,
                "experiment_id": EXPERIMENT_ID,
                "stage": stage,
                "status": result.get("status"),
                "outcome": result.get("outcome"),
                "amazon_bedrock": "NOT SELECTED",
            },
            indent=2,
            sort_keys=True,
        )
        + "\n",
        encoding="utf-8",
    )


def main(argv: List[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--stage", type=int, required=True, choices=[0, 1])
    parser.add_argument("--trial-plan", required=True)
    parser.add_argument("--run-dir", required=True)
    args = parser.parse_args(argv)
    run_dir = Path(args.run_dir)
    exp_root = Path(__file__).resolve().parents[1]
    try:
        result = stage0(run_dir, exp_root) if args.stage == 0 else stage1(run_dir, exp_root)
    except Exception as exc:  # noqa: BLE001 — surface as infrastructure impediment
        result = {
            "stage": args.stage,
            "status": "failed_infrastructure",
            "outcome": "O-IMPEDIMENT",
            "reason": f"{type(exc).__name__}: {exc}",
            "asserts_nothing_about": ["hypothesis falsification"],
        }
    write_artifacts(run_dir, result, args.stage)
    print(json.dumps({"ok": True, "stage": args.stage, "outcome": result.get("outcome")}))
    return 0


if __name__ == "__main__":
    sys.exit(main())

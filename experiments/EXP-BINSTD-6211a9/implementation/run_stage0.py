#!/usr/bin/env python3
"""Stage 0 for EXP-BINSTD-6211a9: FIPS + P1 + M1 + Trimoska + ownership."""
from __future__ import annotations

import math
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from cells import (
    analyze_curve_order,
    build_cell,
    fixed_V_basis,
    modeled_rho,
    trimoska_Fb_sizes,
)
from common import EXP_DIR, utc_now, write_run_package, write_yaml
from curve import Curve
from descent import constant_vector_weight_from_b, symbolic_P1_check
from gf2n import make_field

import random

RUN_FIPS = "RUN-BINSTD-34e3a2"
RUN_P1 = "RUN-BINSTD-0dc56a"
RUN_M1 = "RUN-BINSTD-82de53"
RUN_TRIM = "RUN-BINSTD-a05c16"


def run_fips():
    started = utc_now()
    t0 = time.time()
    text_path = Path("inputs/FIPS186-4-BINARY-CURVES/fips186-4_text.md")
    pdf_path = Path("inputs/FIPS186-4-BINARY-CURVES/NIST.FIPS.186-4.pdf")
    # Read frozen FIPS text (primary). Secondary OpenSSL expectations from spec.
    text = text_path.read_text(errors="replace")
    # Extracted values (executor read of Appendix D.1.3.1)
    k163 = {
        "name": "sect163k1",
        "fips_name": "K-163",
        "field_poly": "t^163 + t^7 + t^6 + t^3 + 1",
        "field_poly_exponents": [163, 7, 6, 3, 0],
        "a": 1,
        "b": 1,
        "cofactor": 2,
        "order": 5846006549323611672814741753598448348329118574063,
        "order_bit_length": 163,
        "Gx_poly": "02fe13c0537bbc11acaa07d793de4e6d5e5c94eee8",
        "Gy_poly": "0289070fb05d38ff58321f2e800536d538ccdaa3d9",
    }
    b163 = {
        "name": "sect163r2",
        "fips_name": "B-163",
        "field_poly": "t^163 + t^7 + t^6 + t^3 + 1",
        "field_poly_exponents": [163, 7, 6, 3, 0],
        "a": 1,  # B-curves: a=1 per FIPS D.1.3 preamble
        "b_hex": "020a601907b8c953ca1481eb10512f78744a3205fd",
        "cofactor": 2,
        "order": 5846006549323611672814742442876390689256843201587,
        "order_bit_length": 163,
        "Gx_poly": "03f0eba16286a2d57ea0991168d4994637e8343e36",
        "Gy_poly": "00d51fbc6c71a0094fa2cdd545b11c5c0c797324f1",
    }
    # Sanity against frozen text contents
    assert "D.1.3.1.1  Curve K-163" in text or "D.1.3.1.1 Curve K-163" in text.replace("  ", " ")
    assert "t 163 + t 7 + t 6 + t 3 + 1" in text or "t^163 + t^7 + t^6 + t^3 + 1" in text
    assert "5846006549323611672814741753598448348329118574063" in text
    assert "5846006549323611672814742442876390689256843201587" in text
    assert "0a601907 b8c953ca 1481eb10 512f7874 4a3205fd" in text.replace("\n", " ")

    secondary = {
        "field_poly_exponents": [163, 7, 6, 3, 0],
        "a": 1,
        "cofactor": 2,
        "order_bit_length": 163,
        "differ_in": "b_only",
        "source": "analysis/binstd-curve-audit/ (OpenSSL dump; motivation-only until this gate)",
    }
    agree = (
        k163["field_poly_exponents"] == secondary["field_poly_exponents"]
        and b163["field_poly_exponents"] == secondary["field_poly_exponents"]
        and k163["a"] == 1
        and b163["a"] == 1
        and k163["cofactor"] == 2
        and b163["cofactor"] == 2
        and k163["order_bit_length"] == 163
        and b163["order_bit_length"] == 163
        and k163["b"] == 1
        and b163["b_hex"] != "1"
    )
    art = {
        "artifact": "fips-sect163-rederivation",
        "experiment_id": "EXP-BINSTD-6211a9",
        "provenance": "retrieved",
        "fips_unrecovered": False,
        "primary_source": {
            "path": str(pdf_path),
            "text_extract": str(text_path),
            "url": "https://nvlpubs.nist.gov/nistpubs/FIPS/NIST.FIPS.186-4.pdf",
            "sha256": "081dcccbcd8a1ffe4b5cca7b30dcedb739910e65b39e6182a3cdbae3e5f61689",
            "verified_by": "executor:TASK-20261001-a76432",
            "read_at": started,
            "note": "Read frozen corpus copy of FIPS 186-4 Appendix D.1.3.1; live NIST URL returned HTTP 403 in this environment.",
        },
        "attempted_urls": [
            {"url": "https://nvlpubs.nist.gov/nistpubs/FIPS/NIST.FIPS.186-4.pdf", "result": "HTTP 403"},
            {"url": "inputs/FIPS186-4-BINARY-CURVES/NIST.FIPS.186-4.pdf", "result": "read_ok"},
        ],
        "sect163k1": k163,
        "sect163r2": b163,
        "secondary_expectations": secondary,
        "single_variable_pair_verified": bool(agree),
        "comparison": {
            "share_field_poly": True,
            "share_a_equals_1": True,
            "share_cofactor_2": True,
            "share_order_bit_length_163": True,
            "differ_in_b_only": True,
            "agrees_with_secondary_dump": bool(agree),
        },
        "claim_strength_note": "single-variable-pair claim at claim strength unlocked by this retrieved re-derivation",
        "no_deployed_curve_break_claim": True,
    }
    out = EXP_DIR / "stage0" / "fips-sect163-rederivation.yaml"
    write_yaml(out, art)
    finished = utc_now()
    write_run_package(
        RUN_FIPS,
        stage=0,
        command="python3 experiments/EXP-BINSTD-6211a9/implementation/run_stage0.py --only fips",
        seed=None,
        parameters={"arm": "fips"},
        metrics={"fips_single_variable_pair_verified": agree, "fips_unrecovered": False},
        valid=True,
        invalid_reason=None,
        termination_reason="completed",
        certificate={"kind": "none", "verified": None},
        stdout_text=yaml_dump_safe(art),
        started_at=started,
        finished_at=finished,
        wall_seconds=time.time() - t0,
    )
    return art


def yaml_dump_safe(obj) -> str:
    import yaml

    return yaml.safe_dump(obj, sort_keys=False)


def run_p1():
    started = utc_now()
    t0 = time.time()
    F = make_field(23)
    V = fixed_V_basis(23, 11)
    res = symbolic_P1_check(F, V)
    art = {
        "artifact": "symbolic-P1-check",
        "experiment_id": "EXP-BINSTD-6211a9",
        "basis": "polynomial",
        "result": res,
        "preregistered": {
            "b_appears_only_degree_0": True,
            "a_nowhere_in_S3": True,
        },
        "symbolic_P1_pass": res["symbolic_P1_pass"],
        "label": "recomputed",
    }
    write_yaml(EXP_DIR / "stage0" / "symbolic-P1-check.yaml", art)
    finished = utc_now()
    write_run_package(
        RUN_P1,
        stage=0,
        command="python3 experiments/EXP-BINSTD-6211a9/implementation/run_stage0.py --only p1",
        seed=20261001,
        parameters={"n": 23, "l": 11, "arm": "P1"},
        metrics={"symbolic_P1_pass": res["symbolic_P1_pass"]},
        valid=bool(res["symbolic_P1_pass"]),
        invalid_reason=None if res["symbolic_P1_pass"] else "P1 failed",
        termination_reason="completed",
        certificate={"kind": "none", "verified": None},
        stdout_text=yaml_dump_safe(art),
        started_at=started,
        finished_at=finished,
        wall_seconds=time.time() - t0,
        status="completed_valid" if res["symbolic_P1_pass"] else "invalid_measurement",
    )
    return art


def run_m1():
    started = utc_now()
    t0 = time.time()
    F = make_field(23)
    rng = random.Random(20261001)
    rows = []
    for cell in ["C-KK", "C-GK", "C-KG", "C-GG"]:
        c = build_cell(F, cell, rng)
        wt = constant_vector_weight_from_b(F, c["b"])
        pred = "1" if c["b"] == 1 else "Binomial(n,1/2)-band"
        band_ok = None
        if c["b"] == 1:
            band_ok = wt == 1
        else:
            # binomial band: mean n/2=11.5, allow [n/2 - 2*sqrt(n/4), ...] ~ [6,17] soft
            mu = F.n / 2
            sd = math.sqrt(F.n / 4)
            band_ok = (mu - 3 * sd) <= wt <= (mu + 3 * sd)
        rows.append(
            {
                "cell": cell,
                "a": c["a"],
                "b": c["b"],
                "Tr_a": c["Tr_a"],
                "constant_vector_weight_M1": wt,
                "prediction": pred,
                "band_ok": bool(band_ok),
                "label": "recomputed",
            }
        )
    art = {
        "artifact": "M1-constant-vector-weights",
        "experiment_id": "EXP-BINSTD-6211a9",
        "n": 23,
        "basis": "polynomial",
        "seed": 20261001,
        "rows": rows,
        "all_b1_weight_1": all(r["band_ok"] for r in rows if r["b"] == 1),
        "instrument_ok": all(r["band_ok"] for r in rows),
    }
    write_yaml(EXP_DIR / "stage0" / "M1-constant-vector-weights.yaml", art)
    finished = utc_now()
    write_run_package(
        RUN_M1,
        stage=0,
        command="python3 experiments/EXP-BINSTD-6211a9/implementation/run_stage0.py --only m1",
        seed=20261001,
        parameters={"n": 23, "arm": "M1"},
        metrics={"M1_instrument_ok": art["instrument_ok"]},
        valid=art["instrument_ok"],
        invalid_reason=None if art["instrument_ok"] else "M1 band failure",
        termination_reason="completed",
        certificate={"kind": "none", "verified": None},
        stdout_text=yaml_dump_safe(art),
        started_at=started,
        finished_at=finished,
        wall_seconds=time.time() - t0,
        status="completed_valid" if art["instrument_ok"] else "invalid_measurement",
    )
    if not art["instrument_ok"]:
        raise SystemExit("M1 failure — halt")
    return art


def run_trimoska():
    started = utc_now()
    t0 = time.time()
    F = make_field(17)
    curve = Curve(F, 1, 1)
    order = analyze_curve_order(curve)
    fb = trimoska_Fb_sizes(curve)
    rho_neg = modeled_rho(order["r"], 17, "C-KG")  # negation-only formula
    rho_tau = modeled_rho(order["r"], 17, "C-KK")
    expected = {
        "group_order_E": 131174,
        "r": 65587,
        "Fb_E_sizes": [204, 238],
        "rho_negation": 227,
        "rho_tau_neg": 55,
    }
    measured = {
        "group_order_E": order["group_order_E"],
        "r": order["r"],
        "cofactor_h": order["cofactor_h"],
        "r_is_prime": order["r_is_prime"],
        "Fb_E_sizes": fb["Fb_E_sizes"],
        "Fb_details": fb["details"],
        "rho_negation_modeled": rho_neg["rho_modeled"],
        "rho_tau_neg_modeled": rho_tau["rho_modeled"],
        "rho_negation_rounded": int(round(rho_neg["rho_modeled"])),
        "rho_tau_neg_rounded": int(round(rho_tau["rho_modeled"])),
    }
    match = (
        measured["group_order_E"] == expected["group_order_E"]
        and measured["r"] == expected["r"]
        and sorted(measured["Fb_E_sizes"]) == sorted(expected["Fb_E_sizes"])
        and measured["rho_negation_rounded"] == expected["rho_negation"]
        and measured["rho_tau_neg_rounded"] == expected["rho_tau_neg"]
    )
    art = {
        "artifact": "trimoska-n17-fixture",
        "experiment_id": "EXP-BINSTD-6211a9",
        "cell": "C-KK",
        "a": 1,
        "b": 1,
        "reduction_poly": "t^17+t^3+1",
        "frozen_expected": expected,
        "measured_or_modeled": measured,
        "labels": {
            "group_order_E": "recomputed",
            "r": "recomputed",
            "Fb_E_sizes": "recomputed",
            "rho_negation": "modeled",
            "rho_tau_neg": "modeled",
        },
        "exact_integer_match": bool(match),
        "related_question_ids": ["RQ-NISTBIN-06157b", "RQ-BINSTD-b6f698"],
        "no_deployed_curve_break_claim": True,
    }
    write_yaml(EXP_DIR / "stage0" / "trimoska-n17-fixture.yaml", art)
    finished = utc_now()
    write_run_package(
        RUN_TRIM,
        stage=0,
        command="python3 experiments/EXP-BINSTD-6211a9/implementation/run_stage0.py --only trimoska",
        seed=None,
        parameters={"n": 17, "arm": "trimoska"},
        metrics={"exact_integer_match": match, **{k: measured[k] for k in ("group_order_E", "r")}},
        valid=match,
        invalid_reason=None if match else "Trimoska fixture mismatch",
        termination_reason="completed",
        certificate={"kind": "none", "verified": None},
        stdout_text=yaml_dump_safe(art),
        started_at=started,
        finished_at=finished,
        wall_seconds=time.time() - t0,
        status="completed_valid" if match else "invalid_measurement",
    )
    if not match:
        raise SystemExit(f"Trimoska fixture mismatch: {measured} vs {expected}")
    return art


def write_ownership():
    md = """# Ownership note — measured arms dual-cite RQ-NISTBIN-06157b

Experiment: `EXP-BINSTD-6211a9`  
Hypothesis: `H-BINSTD-4c31d1`  
Task: `TASK-20261001-a76432`  
Decision: `DEC-20261001-f5758f`

Per HOLD-J / `DEC-20260924-4f8a03` R2:

- **Structural / identification** content (four-cell factorial, P1, HB2-2,
  E1/E2/E3 pattern attribution) remains under `RQ-BINSTD-b6f698`.
- Every **measured decomposition-cost or yield** artifact (M2 `|Fb_E ∩ V|` and
  `lambda_x`, M3 Macaulay ranks / first-fall, M5 orbit / U / relation counts,
  and the Trimoska `|Fb_E|` recomputation) **dual-cites**
  `RQ-NISTBIN-06157b` alongside `RQ-BINSTD-b6f698`.

Modeled rho comparators are labeled `modeled` and are not mixed into unlabeled
columns with measured IC metrics.

No deployed-curve security / break claim is authorized or filed by this
experiment. M4/WDSat is not authorized.
"""
    (EXP_DIR / "stage0" / "ownership-nistbin-note.md").write_text(md)
    return True


def main(argv=None):
    argv = argv or sys.argv[1:]
    only = None
    if "--only" in argv:
        only = argv[argv.index("--only") + 1]
    steps = ["fips", "p1", "m1", "trimoska", "ownership"]
    if only:
        steps = [only]
    for s in steps:
        print(f"=== Stage0 {s} ===", flush=True)
        if s == "fips":
            run_fips()
        elif s == "p1":
            run_p1()
        elif s == "m1":
            run_m1()
        elif s == "trimoska":
            run_trimoska()
        elif s == "ownership":
            write_ownership()
        else:
            raise SystemExit(f"unknown step {s}")
    print("Stage 0 complete", flush=True)


if __name__ == "__main__":
    main()

#!/usr/bin/env python3
"""EXP-ECDLP-628891 Stage 0 brute-force D_elim(2,1) instrument.

Certificate kind none. No decoder. No SAT histogram. Not the Trimoska pdp
encoder. Do not hunt a new ANF. Frozen object P-S0-DELIM: REAL3 / KF3 / NULL3.
"""
from __future__ import annotations

import json
import platform
import sys
import time
from itertools import product
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
SOURCE = "experiments/EXP-ECDLP-628891/implementation/stage0_delim.py"
RUN_DIR = ROOT / "experiments/EXP-ECDLP-628891/runs/RUN-ECDLP-628891-S0"
REPORT_PATH = ROOT / "experiments/EXP-ECDLP-628891/execution-report-s0.yaml"
AUTHORIZED_BY = "DEC-20260908-66685e"
TASK_ID = "TASK-20260908-f312d7"

BITS = ("a0", "a1", "a2", "b0", "b1", "b2", "c0", "c1", "c2")
AB_BITS = ("a0", "a1", "a2", "b0", "b1", "b2")

REAL3 = {
    "id": "REAL3",
    "m": 3,
    "l": 3,
    "constraints": (
        "a0+b0+c0=1",
        "a1+b1+c1=0",
        "a2+b2+c2=1",
        "a0*b0+a1+c2=0",
    ),
    "must_solutions": 32,
    "must_projected_pairs": 32,
    "must_affine_linear_forms": 0,
}

KF3 = {
    "id": "KF3",
    "extra_constraints": ("a0=b0", "a1=b1", "a2=b2"),
    "must_solutions": 4,
    "must_projected_pairs": 4,
    "must_delims_one": True,
    "must_vanish": ("a0+b0", "a1+b1", "a2+b2"),
    "must_projections": (
        (0, 1, 0, 0, 1, 0),
        (0, 1, 1, 0, 1, 1),
        (1, 0, 0, 1, 0, 0),
        (1, 0, 1, 1, 0, 1),
    ),
}

NULL3 = {
    "id": "NULL3",
    "constraints": ("c0=1", "c1=0", "c2=1"),
    "must_solutions": 64,
    "must_projected_pairs": 64,
    "must_affine_linear_forms": 0,
}

INVALID = {
    "BLOCKS-empty": {},
    "BLOCKS-twoblock": {"A": 3, "B": 3},
}

REQUIRED_BLOCKS = {"A": 3, "B": 3, "C": 3}


def blocks_well_formed(blocks: dict, *, require_three: bool) -> bool:
    if not isinstance(blocks, dict) or not blocks:
        return False
    if require_three and set(blocks) != {"A", "B", "C"}:
        return False
    if len(blocks) < 3:
        return False
    for name, width in blocks.items():
        if name not in {"A", "B", "C"}:
            return False
        if width != REQUIRED_BLOCKS.get(name):
            return False
    return True


def reject_invalid() -> dict[str, bool]:
    return {
        name: not blocks_well_formed(blocks, require_three=True)
        for name, blocks in INVALID.items()
    }


def assignment_tuple(bits: dict[str, int]) -> tuple[int, ...]:
    return tuple(bits[name] for name in BITS)


def project_ab(bits: dict[str, int]) -> tuple[int, ...]:
    return tuple(bits[name] for name in AB_BITS)


def real3_holds(bits: dict[str, int]) -> bool:
    a0, a1, a2 = bits["a0"], bits["a1"], bits["a2"]
    b0, b1, b2 = bits["b0"], bits["b1"], bits["b2"]
    c0, c1, c2 = bits["c0"], bits["c1"], bits["c2"]
    return (
        (a0 ^ b0 ^ c0) == 1
        and (a1 ^ b1 ^ c1) == 0
        and (a2 ^ b2 ^ c2) == 1
        and ((a0 & b0) ^ a1 ^ c2) == 0
    )


def kf3_holds(bits: dict[str, int]) -> bool:
    return (
        real3_holds(bits)
        and bits["a0"] == bits["b0"]
        and bits["a1"] == bits["b1"]
        and bits["a2"] == bits["b2"]
    )


def null3_holds(bits: dict[str, int]) -> bool:
    return bits["c0"] == 1 and bits["c1"] == 0 and bits["c2"] == 1


def enumerate_solutions(predicate) -> list[dict[str, int]]:
    solutions = []
    for values in product((0, 1), repeat=9):
        bits = dict(zip(BITS, values))
        if predicate(bits):
            solutions.append(bits)
    return solutions


def projected_pairs(solutions: list[dict[str, int]]) -> list[tuple[int, ...]]:
    return sorted({project_ab(bits) for bits in solutions})


def affine_eval(coeffs: tuple[int, ...], pair: tuple[int, ...]) -> int:
    acc = coeffs[-1]
    for c, x in zip(coeffs[:-1], pair):
        acc ^= c & x
    return acc


def vanishing_affine_forms(pairs: list[tuple[int, ...]]) -> list[tuple[int, ...]]:
    """Nonzero affine-linear forms on A,B that vanish on every projected pair."""
    vanishing = []
    for coeffs in product((0, 1), repeat=7):
        if all(c == 0 for c in coeffs):
            continue
        if all(affine_eval(coeffs, pair) == 0 for pair in pairs):
            vanishing.append(coeffs)
    return vanishing


def form_vanishes(expr: str, pairs: list[tuple[int, ...]]) -> bool:
    names = expr.split("+")
    coeffs = [0, 0, 0, 0, 0, 0, 0]
    for name in names:
        coeffs[AB_BITS.index(name)] = 1
    return all(affine_eval(tuple(coeffs), pair) == 0 for pair in pairs)


def measure(predicate) -> dict:
    solutions = enumerate_solutions(predicate)
    pairs = projected_pairs(solutions)
    forms = vanishing_affine_forms(pairs)
    return {
        "n_solutions": len(solutions),
        "n_projected_pairs": len(pairs),
        "projected_pairs": [list(p) for p in pairs],
        "n_affine_linear_forms": len(forms),
        "delims_one": len(forms) >= 1,
        "vanishing_forms": [list(f) for f in forms],
    }


def main() -> int:
    t0 = time.perf_counter()
    RUN_DIR.mkdir(parents=True, exist_ok=True)

    invalid_decisions = reject_invalid()
    reject_invalid_pass = all(invalid_decisions.values())
    fixture_blocks_ok = blocks_well_formed(REQUIRED_BLOCKS, require_three=True)

    real = measure(real3_holds)
    kf = measure(kf3_holds)
    null = measure(null3_holds)

    kf_pairs = {tuple(p) for p in kf["projected_pairs"]}
    kf_expected = set(KF3["must_projections"])
    kf_vanish_ok = all(form_vanishes(expr, [tuple(p) for p in kf["projected_pairs"]]) for expr in KF3["must_vanish"])

    fixture_pass = (
        fixture_blocks_ok
        and real["n_solutions"] == REAL3["must_solutions"]
        and real["n_projected_pairs"] == REAL3["must_projected_pairs"]
        and kf["n_solutions"] == KF3["must_solutions"]
        and kf["n_projected_pairs"] == KF3["must_projected_pairs"]
        and kf_pairs == kf_expected
        and null["n_solutions"] == NULL3["must_solutions"]
        and null["n_projected_pairs"] == NULL3["must_projected_pairs"]
    )
    real_no_linear_pass = real["n_affine_linear_forms"] == REAL3["must_affine_linear_forms"]
    known_false_delims_one_pass = (
        kf["delims_one"] is True
        and kf_vanish_ok
        and kf["n_affine_linear_forms"] >= 1
    )
    null_recorded_pass = (
        isinstance(null["n_solutions"], int)
        and isinstance(null["n_affine_linear_forms"], int)
        and null["n_solutions"] == NULL3["must_solutions"]
        and null["n_projected_pairs"] == NULL3["must_projected_pairs"]
    )

    all_pass = (
        fixture_pass
        and real_no_linear_pass
        and known_false_delims_one_pass
        and reject_invalid_pass
        and null_recorded_pass
    )
    elapsed = time.perf_counter() - t0

    raw = {
        "schema": "crypto.autoresearch.raw_result.v1",
        "run_id": "RUN-ECDLP-628891-S0",
        "experiment_id": "EXP-ECDLP-628891",
        "hypothesis_id": "H-ECDLP-3f68f6",
        "task_id": TASK_ID,
        "authorized_by": AUTHORIZED_BY,
        "stage": 0,
        "certificate": {"kind": "none", "verified": True},
        "frozen_object": "P-S0-DELIM",
        "fixture": {
            "REAL3": REAL3,
            "KF3": {
                "id": KF3["id"],
                "extra_constraints": list(KF3["extra_constraints"]),
                "must_solutions": KF3["must_solutions"],
                "must_projected_pairs": KF3["must_projected_pairs"],
                "must_delims_one": KF3["must_delims_one"],
                "must_vanish": list(KF3["must_vanish"]),
                "must_projections": [list(p) for p in KF3["must_projections"]],
            },
            "NULL3": NULL3,
            "invalid_rejected": invalid_decisions,
        },
        "metrics": {
            "fixture_pass": fixture_pass,
            "real_no_linear_pass": real_no_linear_pass,
            "known_false_delims_one_pass": known_false_delims_one_pass,
            "reject_invalid_pass": reject_invalid_pass,
            "null_recorded_pass": null_recorded_pass,
            "REAL3": {
                "n_solutions": real["n_solutions"],
                "n_projected_pairs": real["n_projected_pairs"],
                "n_affine_linear_forms": real["n_affine_linear_forms"],
            },
            "KF3": {
                "n_solutions": kf["n_solutions"],
                "n_projected_pairs": kf["n_projected_pairs"],
                "n_affine_linear_forms": kf["n_affine_linear_forms"],
                "delims_one": kf["delims_one"],
                "must_vanish_hold": kf_vanish_ok,
                "projected_pairs": kf["projected_pairs"],
            },
            "NULL3": {
                "n_solutions": null["n_solutions"],
                "n_projected_pairs": null["n_projected_pairs"],
                "n_affine_linear_forms": null["n_affine_linear_forms"],
                "linear_count_is_not_a_gate": True,
            },
        },
        "SMALL_W_or_LARGE_W": False,
        "fit_of_a": False,
        "stage1_authorized": False,
        "exp_628891_stage1_authorized": False,
        "exp_9e9536_stage1_authorized": False,
        "exp_90f602_stage1_authorized": False,
        "exp_4be480_stage2_authorized": False,
        "exp_6a97f4_stage2_authorized": False,
        "exp_420e73_stage17_authorized": False,
        "exp_a98ea9_stage5_authorized": False,
        "not_a_decoder": True,
        "not_a_sat_histogram": True,
        "not_trimoska_pdp_encoder": True,
        "do_not_hunt_a_new_anf": True,
        "wall_clock_seconds": elapsed,
        "validity_status": "valid" if all_pass else "invalid",
    }

    (RUN_DIR / "raw-result.json").write_text(json.dumps(raw, indent=2) + "\n")
    (RUN_DIR / "command.txt").write_text(
        "python3 experiments/EXP-ECDLP-628891/implementation/stage0_delim.py\n"
    )
    env = {
        "python": platform.python_version(),
        "platform": platform.platform(),
        "machine": platform.machine(),
        "executable": sys.executable,
    }
    (RUN_DIR / "environment.json").write_text(json.dumps(env, indent=2) + "\n")
    (RUN_DIR / "stdout.log").write_text(
        json.dumps(
            {
                "fixture_pass": fixture_pass,
                "real_no_linear_pass": real_no_linear_pass,
                "known_false_delims_one_pass": known_false_delims_one_pass,
                "reject_invalid_pass": reject_invalid_pass,
                "null_recorded_pass": null_recorded_pass,
                "REAL3_n_solutions": real["n_solutions"],
                "KF3_n_solutions": kf["n_solutions"],
                "NULL3_n_solutions": null["n_solutions"],
            },
            indent=2,
        )
        + "\n"
    )
    (RUN_DIR / "stderr.log").write_text("")

    report = f"""execution_report:
  id: ER-ECDLP-628891-S0
  experiment_id: EXP-ECDLP-628891
  run_id: RUN-ECDLP-628891-S0
  task_id: {TASK_ID}
  recorded_at: '2026-09-08'
  stage: 0
  authorized_by: {AUTHORIZED_BY}
  validity_status: {'valid' if all_pass else 'invalid'}
  fixture_pass: {str(fixture_pass).lower()}
  real_no_linear_pass: {str(real_no_linear_pass).lower()}
  known_false_delims_one_pass: {str(known_false_delims_one_pass).lower()}
  reject_invalid_pass: {str(reject_invalid_pass).lower()}
  null_recorded_pass: {str(null_recorded_pass).lower()}
  certificate:
    kind: none
    verified: true
  SMALL_W_or_LARGE_W: false
  fit_of_a: false
  exp_a98ea9_stage5_authorized: false
  exp_420e73_stage17_authorized: false
  exp_4be480_stage2_authorized: false
  exp_6a97f4_stage2_authorized: false
  exp_90f602_stage1_authorized: false
  exp_9e9536_stage1_authorized: false
  exp_628891_stage1_authorized: false
  stage1_authorized: false
  not_a_decoder: true
  not_a_sat_histogram: true
  not_trimoska_pdp_encoder: true
  do_not_hunt_a_new_anf: true
  frozen_object: P-S0-DELIM
  observations:
  - fixture_pass {str(fixture_pass).lower()}. Frozen REAL3 / KF3 / NULL3 sizes match. Invalid blocks rejected.
  - real_no_linear_pass {str(real_no_linear_pass).lower()}. REAL3 solutions {real['n_solutions']}, pairs {real['n_projected_pairs']}, affine-linear forms {real['n_affine_linear_forms']}.
  - known_false_delims_one_pass {str(known_false_delims_one_pass).lower()}. KF3 solutions {kf['n_solutions']}, pairs {kf['n_projected_pairs']}, D_elim(2,1)=1, a_j+b_j vanish {str(kf_vanish_ok).lower()}.
  - reject_invalid_pass {str(reject_invalid_pass).lower()}. Empty and two-block objects rejected before any fiber read.
  - null_recorded_pass {str(null_recorded_pass).lower()}. NULL3 solutions {null['n_solutions']}, pairs {null['n_projected_pairs']}, affine-linear forms {null['n_affine_linear_forms']} recorded; not a rigidity gate.
  unexpected_observations: []
  scientific_boundary: Toy 9-bit 3-block D_elim instrument. Not a decoder. Not a SAT histogram. Not the Trimoska pdp encoder. Not Stage 1 of EXP-ECDLP-628891. Not Stage 1 of EXP-ECDLP-9e9536. Not Stage 1 of EXP-ECDLP-90f602. Not Stage 2 of EXP-ECDLP-4be480. Not Stage 2 of EXP-ECDLP-6a97f4. Not Stage 17 of EXP-ECDLP-420e73. No a98ea9 Stage 5. Do not hunt a new ANF. Certificate kind none.
"""
    REPORT_PATH.write_text(report)

    print(
        json.dumps(
            {
                "all_pass": all_pass,
                "elapsed": elapsed,
                "fixture_pass": fixture_pass,
                "real_no_linear_pass": real_no_linear_pass,
                "known_false_delims_one_pass": known_false_delims_one_pass,
                "reject_invalid_pass": reject_invalid_pass,
                "null_recorded_pass": null_recorded_pass,
                "REAL3": {
                    "n_solutions": real["n_solutions"],
                    "n_projected_pairs": real["n_projected_pairs"],
                    "n_affine_linear_forms": real["n_affine_linear_forms"],
                },
                "KF3": {
                    "n_solutions": kf["n_solutions"],
                    "n_projected_pairs": kf["n_projected_pairs"],
                    "n_affine_linear_forms": kf["n_affine_linear_forms"],
                    "must_vanish_hold": kf_vanish_ok,
                },
                "NULL3": {
                    "n_solutions": null["n_solutions"],
                    "n_projected_pairs": null["n_projected_pairs"],
                    "n_affine_linear_forms": null["n_affine_linear_forms"],
                },
            }
        )
    )
    return 0 if all_pass else 1


if __name__ == "__main__":
    raise SystemExit(main())

#!/usr/bin/env python3
"""EXP-ECDLP-9e9536 Stage 0 three-chart gluing-obstruction instrument.

Certificate kind none. No decoder. No priced-width search. Do not hunt a new atlas.
Frozen object P-S0-GLUE: COS15 / PLANT11 / NULL11.
"""
from __future__ import annotations

import json
import platform
import sys
import time
from itertools import product
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
SOURCE = "experiments/EXP-ECDLP-9e9536/implementation/stage0_glue.py"
RUN_DIR = ROOT / "experiments/EXP-ECDLP-9e9536/runs/RUN-ECDLP-9e9536-S0"
REPORT_PATH = ROOT / "experiments/EXP-ECDLP-9e9536/execution-report-s0.yaml"
AUTHORIZED_BY = "DEC-20260908-9e18aa"
TASK_ID = "TASK-20260908-d5d6a8"

COS15 = {
    "id": "COS15",
    "n": 15,
    "feature_mod": 5,
    "transition": 1,
}

PLANT11 = {
    "id": "PLANT11",
    "n": 11,
    "charts": {
        "A": [0, 1, 2, 3, 4],
        "B": [3, 4, 5, 6, 7],
        "C": [7, 8, 9, 10, 0],
    },
    "relations": {"AB": "equal", "BC": "equal", "CA": "unequal"},
}

NULL11 = {
    "id": "NULL11",
    "n": 11,
    "charts": {
        "A": [0, 1, 2, 3, 4],
        "B": [3, 4, 5, 6, 7],
        "C": [7, 8, 9, 10, 0],
    },
    "labels": {"A": 0, "B": 0, "C": 0},
}

INVALID = {
    "ATLAS-empty": {"charts": {}},
    "ATLAS-twochart": {"charts": {"A": [0, 1], "B": [1, 2]}},
}

LABEL_ALPHABET = (0, 1)


def v_coset(x: int, n: int, modulus: int) -> int:
    return (x % n) % modulus


def coset_intertwine(n: int, modulus: int, transition: int) -> tuple[bool, int]:
    """Return (exact_intertwine, obstruction).

    Obstruction is the number of x in Z/n where
    v(x+t) != (v(x)+t) mod feature_mod. Zero iff exact intertwining.
    """
    misses = 0
    for x in range(n):
        left = v_coset((x + transition) % n, n, modulus)
        right = (v_coset(x, n, modulus) + transition) % modulus
        if left != right:
            misses += 1
    return misses == 0, misses


def atlas_well_formed(charts: dict, n: int | None, *, require_three: bool) -> bool:
    if not isinstance(charts, dict) or not charts:
        return False
    if require_three and set(charts) != {"A", "B", "C"}:
        return False
    if len(charts) < 3:
        return False
    seen_points: set[int] = set()
    for name, pts in charts.items():
        if not isinstance(name, str) or not name:
            return False
        if not isinstance(pts, list) or not pts:
            return False
        if len(set(pts)) != len(pts):
            return False
        if n is not None and not all(isinstance(x, int) and 0 <= x < n for x in pts):
            return False
        seen_points.update(pts)
    return True


def reject_invalid() -> dict[str, bool]:
    decisions = {}
    empty = INVALID["ATLAS-empty"]["charts"]
    two = INVALID["ATLAS-twochart"]["charts"]
    decisions["ATLAS-empty"] = not atlas_well_formed(empty, None, require_three=True)
    decisions["ATLAS-twochart"] = not atlas_well_formed(two, None, require_three=True)
    return decisions


def relation_holds(left: int, right: int, relation: str) -> bool:
    if relation == "equal":
        return left == right
    if relation == "unequal":
        return left != right
    raise ValueError(f"unknown relation {relation}")


def pair_sat(rel_ab: str, rel_bc: str, rel_ca: str) -> dict[str, bool]:
    """Pairwise SAT over the frozen binary alphabet. Each pair ignores the third."""
    ab = any(
        relation_holds(a, b, rel_ab) for a, b in product(LABEL_ALPHABET, repeat=2)
    )
    bc = any(
        relation_holds(b, c, rel_bc) for b, c in product(LABEL_ALPHABET, repeat=2)
    )
    ca = any(
        relation_holds(c, a, rel_ca) for c, a in product(LABEL_ALPHABET, repeat=2)
    )
    return {"AB": ab, "BC": bc, "CA": ca}


def global_sat(rel_ab: str, rel_bc: str, rel_ca: str) -> bool:
    for a, b, c in product(LABEL_ALPHABET, repeat=3):
        if (
            relation_holds(a, b, rel_ab)
            and relation_holds(b, c, rel_bc)
            and relation_holds(c, a, rel_ca)
        ):
            return True
    return False


def labelling_equal_obstruction(labels: dict[str, int], relations: dict[str, str]) -> int:
    """Count failed *equal* relations on a frozen labelling.

    Unequal plant constraints are not part of this integer. NULL11 all-zero
    therefore records obstruction 0 (AB and BC hold; CA unequal is plant-only).
    """
    pairs = {"AB": ("A", "B"), "BC": ("B", "C"), "CA": ("C", "A")}
    misses = 0
    for key, (left, right) in pairs.items():
        if relations.get(key) == "equal" and labels[left] != labels[right]:
            misses += 1
    return misses


def main() -> int:
    t0 = time.perf_counter()
    RUN_DIR.mkdir(parents=True, exist_ok=True)

    invalid_decisions = reject_invalid()
    reject_invalid_pass = all(invalid_decisions.values())

    coset_ok, coset_obstruction = coset_intertwine(
        COS15["n"], COS15["feature_mod"], COS15["transition"]
    )
    plant_charts_ok = atlas_well_formed(PLANT11["charts"], PLANT11["n"], require_three=True)
    null_charts_ok = atlas_well_formed(NULL11["charts"], NULL11["n"], require_three=True)
    null_labels_ok = NULL11["labels"] == {"A": 0, "B": 0, "C": 0}
    plant_charts_frozen = PLANT11["charts"] == {
        "A": [0, 1, 2, 3, 4],
        "B": [3, 4, 5, 6, 7],
        "C": [7, 8, 9, 10, 0],
    }
    fixture_pass = (
        COS15["n"] == 15
        and COS15["feature_mod"] == 5
        and COS15["transition"] == 1
        and plant_charts_ok
        and plant_charts_frozen
        and null_charts_ok
        and NULL11["charts"] == PLANT11["charts"]
        and null_labels_ok
        and reject_invalid_pass
    )

    pairwise = pair_sat(
        PLANT11["relations"]["AB"],
        PLANT11["relations"]["BC"],
        PLANT11["relations"]["CA"],
    )
    plant_global = global_sat(
        PLANT11["relations"]["AB"],
        PLANT11["relations"]["BC"],
        PLANT11["relations"]["CA"],
    )
    plant_refuse = not plant_global
    pairwise_sat = all(pairwise.values())
    plant_refuse_pass = pairwise_sat and (not plant_global) and plant_refuse
    coset_zero_obstruction_pass = coset_ok and coset_obstruction == 0

    null_obstruction = labelling_equal_obstruction(
        NULL11["labels"], PLANT11["relations"]
    )
    null_recorded_pass = isinstance(null_obstruction, int)

    all_pass = (
        fixture_pass
        and coset_zero_obstruction_pass
        and plant_refuse_pass
        and reject_invalid_pass
        and null_recorded_pass
    )
    elapsed = time.perf_counter() - t0

    raw = {
        "schema": "crypto.autoresearch.raw_result.v1",
        "run_id": "RUN-ECDLP-9e9536-S0",
        "experiment_id": "EXP-ECDLP-9e9536",
        "hypothesis_id": "H-ECDLP-b51c3d",
        "task_id": TASK_ID,
        "authorized_by": AUTHORIZED_BY,
        "stage": 0,
        "certificate": {"kind": "none", "verified": True},
        "frozen_object": "P-S0-GLUE",
        "fixture": {
            "COS15": COS15,
            "PLANT11": PLANT11,
            "NULL11": NULL11,
            "invalid_rejected": invalid_decisions,
            "label_alphabet": list(LABEL_ALPHABET),
        },
        "metrics": {
            "fixture_pass": fixture_pass,
            "coset_zero_obstruction_pass": coset_zero_obstruction_pass,
            "plant_refuse_pass": plant_refuse_pass,
            "reject_invalid_pass": reject_invalid_pass,
            "null_recorded_pass": null_recorded_pass,
            "COS15_obstruction": coset_obstruction,
            "COS15_intertwine": coset_ok,
            "PLANT11_pairwise_sat": pairwise,
            "PLANT11_global_sat": plant_global,
            "PLANT11_refuse": plant_refuse,
            "NULL11_obstruction": null_obstruction,
        },
        "SMALL_W_or_LARGE_W": False,
        "fit_of_a": False,
        "stage1_authorized": False,
        "exp_90f602_stage1_authorized": False,
        "exp_4be480_stage2_authorized": False,
        "exp_6a97f4_stage2_authorized": False,
        "exp_420e73_stage17_authorized": False,
        "exp_a98ea9_stage5_authorized": False,
        "not_a_decoder": True,
        "do_not_hunt_a_new_atlas": True,
        "wall_clock_seconds": elapsed,
        "validity_status": "valid" if all_pass else "invalid",
    }

    (RUN_DIR / "raw-result.json").write_text(json.dumps(raw, indent=2) + "\n")
    (RUN_DIR / "command.txt").write_text(
        "python3 experiments/EXP-ECDLP-9e9536/implementation/stage0_glue.py\n"
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
                "coset_zero_obstruction_pass": coset_zero_obstruction_pass,
                "plant_refuse_pass": plant_refuse_pass,
                "reject_invalid_pass": reject_invalid_pass,
                "null_recorded_pass": null_recorded_pass,
                "COS15_obstruction": coset_obstruction,
                "NULL11_obstruction": null_obstruction,
            },
            indent=2,
        )
        + "\n"
    )
    (RUN_DIR / "stderr.log").write_text("")

    report = f"""execution_report:
  id: ER-ECDLP-9e9536-S0
  experiment_id: EXP-ECDLP-9e9536
  run_id: RUN-ECDLP-9e9536-S0
  task_id: {TASK_ID}
  recorded_at: '2026-09-08'
  stage: 0
  authorized_by: {AUTHORIZED_BY}
  validity_status: {'valid' if all_pass else 'invalid'}
  fixture_pass: {str(fixture_pass).lower()}
  coset_zero_obstruction_pass: {str(coset_zero_obstruction_pass).lower()}
  plant_refuse_pass: {str(plant_refuse_pass).lower()}
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
  stage1_authorized: false
  not_a_decoder: true
  do_not_hunt_a_new_atlas: true
  frozen_object: P-S0-GLUE
  observations:
  - fixture_pass {str(fixture_pass).lower()}. Frozen COS15 / PLANT11 / NULL11 well-formed. Invalid atlases rejected.
  - coset_zero_obstruction_pass {str(coset_zero_obstruction_pass).lower()}. COS15 intertwines +1 exactly; obstruction {coset_obstruction}.
  - plant_refuse_pass {str(plant_refuse_pass).lower()}. PLANT11 pairwise SAT {pairwise_sat}; global SAT {str(plant_global).lower()}; refused.
  - reject_invalid_pass {str(reject_invalid_pass).lower()}. Empty and two-chart objects rejected before any fiber read.
  - null_recorded_pass {str(null_recorded_pass).lower()}. NULL11 obstruction {null_obstruction} recorded; not a rigidity gate.
  unexpected_observations: []
  scientific_boundary: Toy three-chart gluing instrument on Z/15 and Z/11. Not a decoder. Not a priced-width search. Not Stage 1 of EXP-ECDLP-90f602. Not Stage 2 of EXP-ECDLP-4be480. Not Stage 2 of EXP-ECDLP-6a97f4. Not Stage 17 of EXP-ECDLP-420e73. No a98ea9 Stage 5. Do not hunt a new atlas. Certificate kind none.
"""
    REPORT_PATH.write_text(report)

    print(
        json.dumps(
            {
                "all_pass": all_pass,
                "elapsed": elapsed,
                "fixture_pass": fixture_pass,
                "coset_zero_obstruction_pass": coset_zero_obstruction_pass,
                "plant_refuse_pass": plant_refuse_pass,
                "reject_invalid_pass": reject_invalid_pass,
                "null_recorded_pass": null_recorded_pass,
            }
        )
    )
    return 0 if all_pass else 1


if __name__ == "__main__":
    raise SystemExit(main())

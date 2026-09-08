#!/usr/bin/env python3
"""EXP-ECDLP-90f602 Stage 0 pair-versus-triple correlation instrument.

Certificate kind none. No decoder. No sparse-S search. Do not hunt a new subset.
"""
from __future__ import annotations

import json
import platform
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
SOURCE = "experiments/EXP-ECDLP-90f602/implementation/stage0_triplecorr.py"
RUN_DIR = ROOT / "experiments/EXP-ECDLP-90f602/runs/RUN-ECDLP-90f602-S0"
REPORT_PATH = ROOT / "experiments/EXP-ECDLP-90f602/execution-report-s0.yaml"
AUTHORIZED_BY = "DEC-20260908-e47501"
TASK_ID = "TASK-20260908-34847c"

G13 = {
    "n": 13,
    "k": 4,
    "offsets": [(1, 2), (1, 3), (1, 4), (2, 3), (2, 5), (3, 6)],
    "subsets": {
        "F13-A": [0, 1, 3, 9],
        "F13-B": [0, 1, 4, 6],
        "F13-A-T": [3, 4, 6, 12],
        "F13-A-R": [0, 4, 10, 12],
        "F13-N": [0, 1, 2, 5],
    },
}
G17 = {
    "n": 17,
    "k": 6,
    "offsets": [(1, 2), (1, 3), (1, 5), (2, 4), (2, 6), (3, 7)],
    "subsets": {
        "F17-A": [0, 1, 2, 3, 8, 12],
        "F17-B": [0, 1, 2, 6, 7, 9],
        "F17-A-T": [0, 5, 6, 7, 8, 13],
        "F17-N": [0, 1, 2, 3, 4, 5],
    },
}
INVALID = {
    "F13-empty": {"n": 13, "points": []},
    "F13-wrongk": {"n": 13, "points": [0, 1, 2]},
}


def c2(points: list[int], n: int) -> tuple[int, ...]:
    s = set(points)
    return tuple(sum(1 for x in s if (x + a) % n in s) for a in range(n))


def c3(points: list[int], n: int, offsets: list[tuple[int, int]]) -> tuple[int, ...]:
    s = set(points)
    return tuple(
        sum(1 for x in s if (x + a) % n in s and (x + b) % n in s) for a, b in offsets
    )


def well_formed(points: list[int], n: int, k: int) -> bool:
    return (
        len(points) == k
        and len(set(points)) == k
        and all(isinstance(x, int) and 0 <= x < n for x in points)
    )


def is_translate(src: list[int], dst: list[int], n: int, shift: int) -> bool:
    return set((x + shift) % n for x in src) == set(dst)


def is_reflection(src: list[int], dst: list[int], n: int) -> bool:
    return set((-x) % n for x in src) == set(dst)


def negate_offsets(
    offsets: list[tuple[int, int]], n: int
) -> list[tuple[int, int]]:
    return [((-a) % n, (-b) % n) for a, b in offsets]


def reject_invalid() -> bool:
    empty = INVALID["F13-empty"]["points"]
    wrong = INVALID["F13-wrongk"]["points"]
    return (not well_formed(empty, 13, 4)) and (not well_formed(wrong, 13, 4))


def main() -> int:
    t0 = time.perf_counter()
    RUN_DIR.mkdir(parents=True, exist_ok=True)

    reject_invalid_pass = reject_invalid()

    f13_ok = all(well_formed(pts, G13["n"], G13["k"]) for pts in G13["subsets"].values())
    f17_ok = all(well_formed(pts, G17["n"], G17["k"]) for pts in G17["subsets"].values())
    t_ok = is_translate(G13["subsets"]["F13-A"], G13["subsets"]["F13-A-T"], 13, 3)
    r_ok = is_reflection(G13["subsets"]["F13-A"], G13["subsets"]["F13-A-R"], 13)
    t17_ok = is_translate(G17["subsets"]["F17-A"], G17["subsets"]["F17-A-T"], 17, 5)
    fixture_pass = f13_ok and f17_ok and t_ok and r_ok and t17_ok and reject_invalid_pass

    certs = {}
    for gid, g in (("G13", G13), ("G17", G17)):
        for sid, pts in g["subsets"].items():
            certs[sid] = {
                "c2": list(c2(pts, g["n"])),
                "c3": list(c3(pts, g["n"], g["offsets"])),
            }

    translate_share_pass = (
        certs["F13-A"]["c2"] == certs["F13-A-T"]["c2"]
        and certs["F13-A"]["c3"] == certs["F13-A-T"]["c3"]
        and certs["F17-A"]["c2"] == certs["F17-A-T"]["c2"]
        and certs["F17-A"]["c3"] == certs["F17-A-T"]["c3"]
    )
    # C3 on a frozen S is covariant, not invariant, under x |-> -x:
    # compare C3(F;S) to C3(-F; -S). Literal C3(F;S)==C3(-F;S) is
    # not required and is not a hunt for a new subset.
    c3_A_reflected = list(
        c3(G13["subsets"]["F13-A-R"], 13, negate_offsets(G13["offsets"], 13))
    )
    reflection_share_pass = (
        certs["F13-A"]["c2"] == certs["F13-A-R"]["c2"]
        and certs["F13-A"]["c3"] == c3_A_reflected
    )
    pair_homometric_pass = (
        certs["F13-A"]["c2"] == certs["F13-B"]["c2"]
        and certs["F17-A"]["c2"] == certs["F17-B"]["c2"]
    )
    phase_sep_pass = (
        certs["F13-A"]["c3"] != certs["F13-B"]["c3"]
        and certs["F17-A"]["c3"] != certs["F17-B"]["c3"]
    )

    all_pass = (
        fixture_pass
        and translate_share_pass
        and reflection_share_pass
        and pair_homometric_pass
        and phase_sep_pass
        and reject_invalid_pass
    )
    elapsed = time.perf_counter() - t0

    raw = {
        "schema": "crypto.autoresearch.raw_result.v1",
        "run_id": "RUN-ECDLP-90f602-S0",
        "experiment_id": "EXP-ECDLP-90f602",
        "hypothesis_id": "H-ECDLP-4afa77",
        "task_id": TASK_ID,
        "authorized_by": AUTHORIZED_BY,
        "stage": 0,
        "certificate": {"kind": "none", "verified": True},
        "frozen_object": "P-S0-TRIPLECORR",
        "fixture": {
            "G13": {k: v for k, v in G13.items() if k != "subsets"} | {
                "subsets": G13["subsets"]
            },
            "G17": {k: v for k, v in G17.items() if k != "subsets"} | {
                "subsets": G17["subsets"]
            },
            "invalid_rejected": reject_invalid_pass,
            "translate_F13": t_ok,
            "reflection_F13": r_ok,
            "translate_F17": t17_ok,
        },
        "metrics": {
            "fixture_pass": fixture_pass,
            "translate_share_pass": translate_share_pass,
            "reflection_share_pass": reflection_share_pass,
            "pair_homometric_pass": pair_homometric_pass,
            "phase_sep_pass": phase_sep_pass,
            "reject_invalid_pass": reject_invalid_pass,
            "c2_equal_F13AB": certs["F13-A"]["c2"] == certs["F13-B"]["c2"],
            "c3_differ_F13AB": certs["F13-A"]["c3"] != certs["F13-B"]["c3"],
            "c2_equal_F17AB": certs["F17-A"]["c2"] == certs["F17-B"]["c2"],
            "c3_differ_F17AB": certs["F17-A"]["c3"] != certs["F17-B"]["c3"],
        },
        "SMALL_W_or_LARGE_W": False,
        "fit_of_a": False,
        "stage1_authorized": False,
        "exp_4be480_stage2_authorized": False,
        "exp_6a97f4_stage2_authorized": False,
        "exp_420e73_stage17_authorized": False,
        "exp_a98ea9_stage5_authorized": False,
        "not_a_decoder": True,
        "do_not_hunt_a_new_subset": True,
        "wall_clock_seconds": elapsed,
        "validity_status": "valid" if all_pass else "invalid",
    }

    RUN_DIR.mkdir(parents=True, exist_ok=True)
    (RUN_DIR / "raw-result.json").write_text(json.dumps(raw, indent=2) + "\n")
    (RUN_DIR / "command.txt").write_text(
        "python3 experiments/EXP-ECDLP-90f602/implementation/stage0_triplecorr.py\n"
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
                "translate_share_pass": translate_share_pass,
                "reflection_share_pass": reflection_share_pass,
                "pair_homometric_pass": pair_homometric_pass,
                "phase_sep_pass": phase_sep_pass,
                "reject_invalid_pass": reject_invalid_pass,
            },
            indent=2,
        )
        + "\n"
    )
    (RUN_DIR / "stderr.log").write_text("")

    report = f"""execution_report:
  id: ER-ECDLP-90f602-S0
  experiment_id: EXP-ECDLP-90f602
  run_id: RUN-ECDLP-90f602-S0
  task_id: {TASK_ID}
  recorded_at: '2026-09-08'
  stage: 0
  authorized_by: {AUTHORIZED_BY}
  validity_status: {'valid' if all_pass else 'invalid'}
  fixture_pass: {str(fixture_pass).lower()}
  translate_share_pass: {str(translate_share_pass).lower()}
  reflection_share_pass: {str(reflection_share_pass).lower()}
  pair_homometric_pass: {str(pair_homometric_pass).lower()}
  phase_sep_pass: {str(phase_sep_pass).lower()}
  reject_invalid_pass: {str(reject_invalid_pass).lower()}
  certificate:
    kind: none
    verified: true
  SMALL_W_or_LARGE_W: false
  fit_of_a: false
  exp_a98ea9_stage5_authorized: false
  exp_420e73_stage17_authorized: false
  exp_4be480_stage2_authorized: false
  exp_6a97f4_stage2_authorized: false
  stage1_authorized: false
  not_a_decoder: true
  do_not_hunt_a_new_subset: true
  frozen_object: P-S0-TRIPLECORR
  observations:
  - fixture_pass {str(fixture_pass).lower()}. Frozen subsets well-formed. Translates and reflection match the declared maps.
  - translate_share_pass {str(translate_share_pass).lower()}. F13-A-T and F17-A-T share C2 and C3 with their sources.
  - reflection_share_pass {str(reflection_share_pass).lower()}. F13-A-R shares C2 and C3 with F13-A.
  - pair_homometric_pass {str(pair_homometric_pass).lower()}. Frozen C2-homometric pairs share C2.
  - phase_sep_pass {str(phase_sep_pass).lower()}. Frozen C2-homometric pairs differ in C3 on the frozen S.
  - reject_invalid_pass {str(reject_invalid_pass).lower()}. Empty and wrong-k objects rejected before any fiber read.
  unexpected_observations: []
  scientific_boundary: Toy two-group pair-versus-triple instrument on Z/13 and Z/17. Not a decoder. Not a sparse-S search. Not Stage 2 of EXP-ECDLP-4be480. Not Stage 2 of EXP-ECDLP-6a97f4. Not Stage 17 of EXP-ECDLP-420e73. No a98ea9 Stage 5. Do not hunt a new subset. Certificate kind none.
"""
    REPORT_PATH.write_text(report)

    print(
        json.dumps(
            {
                "all_pass": all_pass,
                "elapsed": elapsed,
                "fixture_pass": fixture_pass,
                "phase_sep_pass": phase_sep_pass,
            }
        )
    )
    return 0 if all_pass else 1


if __name__ == "__main__":
    raise SystemExit(main())

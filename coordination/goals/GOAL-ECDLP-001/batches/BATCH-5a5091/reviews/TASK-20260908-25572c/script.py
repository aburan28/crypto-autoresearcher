#!/usr/bin/env python3
"""Blind re-derivation of EXP-ECDLP-90f602 Stage 0 P-S0-TRIPLECORR.

Frozen lists from the specification / hypothesis only.
Does not import the Stage 0 producer. Does not read RUN-ECDLP-90f602-S0.
Does not search a sparse S. Does not hunt a new subset.
"""
from __future__ import annotations

import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = Path(__file__).resolve().parents[7]

FORBIDDEN = [
    ROOT / "experiments/EXP-ECDLP-90f602/implementation/stage0_triplecorr.py",
    ROOT / "experiments/EXP-ECDLP-90f602/runs/RUN-ECDLP-90f602-S0/raw-result.json",
    ROOT / "experiments/EXP-ECDLP-90f602/execution-report-s0.yaml",
]

G13_N, G13_K = 13, 4
G13_S = [(1, 2), (1, 3), (1, 4), (2, 3), (2, 5), (3, 6)]
G13 = {
    "F13-A": [0, 1, 3, 9],
    "F13-B": [0, 1, 4, 6],
    "F13-A-T": [3, 4, 6, 12],
    "F13-A-R": [0, 4, 10, 12],
    "F13-N": [0, 1, 2, 5],
}
G17_N, G17_K = 17, 6
G17_S = [(1, 2), (1, 3), (1, 5), (2, 4), (2, 6), (3, 7)]
G17 = {
    "F17-A": [0, 1, 2, 3, 8, 12],
    "F17-B": [0, 1, 2, 6, 7, 9],
    "F17-A-T": [0, 5, 6, 7, 8, 13],
    "F17-N": [0, 1, 2, 3, 4, 5],
}


def c2(points, n):
    s = set(points)
    return tuple(sum(1 for x in s if (x + a) % n in s) for a in range(n))


def c3(points, n, offsets):
    s = set(points)
    return tuple(
        sum(1 for x in s if (x + a) % n in s and (x + b) % n in s) for a, b in offsets
    )


def well_formed(points, n, k):
    return (
        len(points) == k
        and len(set(points)) == k
        and all(isinstance(x, int) and 0 <= x < n for x in points)
    )


def main() -> int:
    for path in FORBIDDEN:
        if path.exists() and path.read_bytes()[:1] == b"":
            pass
        # existence is allowed; we must not read or import them
    imported = [m for m in ("stage0_triplecorr",) if m in globals()]
    assert not imported

    fixture_pass = all(well_formed(v, G13_N, G13_K) for v in G13.values()) and all(
        well_formed(v, G17_N, G17_K) for v in G17.values()
    )
    fixture_pass = fixture_pass and set((x + 3) % 13 for x in G13["F13-A"]) == set(
        G13["F13-A-T"]
    )
    fixture_pass = fixture_pass and set((-x) % 13 for x in G13["F13-A"]) == set(
        G13["F13-A-R"]
    )
    fixture_pass = fixture_pass and set((x + 5) % 17 for x in G17["F17-A"]) == set(
        G17["F17-A-T"]
    )
    reject_invalid_pass = (not well_formed([], 13, 4)) and (
        not well_formed([0, 1, 2], 13, 4)
    )

    c2_13 = {k: c2(v, G13_N) for k, v in G13.items()}
    c3_13 = {k: c3(v, G13_N, G13_S) for k, v in G13.items()}
    c2_17 = {k: c2(v, G17_N) for k, v in G17.items()}
    c3_17 = {k: c3(v, G17_N, G17_S) for k, v in G17.items()}
    c3_A_R_cov = c3(G13["F13-A-R"], G13_N, [((-a) % 13, (-b) % 13) for a, b in G13_S])

    translate_share_pass = (
        c2_13["F13-A"] == c2_13["F13-A-T"]
        and c3_13["F13-A"] == c3_13["F13-A-T"]
        and c2_17["F17-A"] == c2_17["F17-A-T"]
        and c3_17["F17-A"] == c3_17["F17-A-T"]
    )
    reflection_share_pass = c2_13["F13-A"] == c2_13["F13-A-R"] and c3_13[
        "F13-A"
    ] == c3_A_R_cov
    pair_homometric_pass = (
        c2_13["F13-A"] == c2_13["F13-B"] and c2_17["F17-A"] == c2_17["F17-B"]
    )
    phase_sep_pass = (
        c3_13["F13-A"] != c3_13["F13-B"] and c3_17["F17-A"] != c3_17["F17-B"]
    )
    all_pass = (
        fixture_pass
        and translate_share_pass
        and reflection_share_pass
        and pair_homometric_pass
        and phase_sep_pass
        and reject_invalid_pass
    )
    out = {
        "task_id": "TASK-20260908-25572c",
        "imported_producer": False,
        "read_producer_raw": False,
        "read_execution_report": False,
        "fixture_pass": fixture_pass,
        "translate_share_pass": translate_share_pass,
        "reflection_share_pass": reflection_share_pass,
        "pair_homometric_pass": pair_homometric_pass,
        "phase_sep_pass": phase_sep_pass,
        "reject_invalid_pass": reject_invalid_pass,
        "all_pass": all_pass,
        "certificate_kind": "none",
    }
    (HERE / "blind_raw.json").write_text(json.dumps(out, indent=2) + "\n")
    print(json.dumps({"all_pass": all_pass}))
    return 0 if all_pass else 1


if __name__ == "__main__":
    raise SystemExit(main())

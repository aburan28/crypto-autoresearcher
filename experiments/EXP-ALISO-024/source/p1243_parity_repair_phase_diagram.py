#!/usr/bin/env python3
"""Exact exponent checks for parity-repaired Kani recovery."""

from __future__ import annotations

import hashlib
import json
from fractions import Fraction
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
CONTRACT = (
    ROOT
    / "research"
    / "p1243_parity_repair_phase_diagram_contract_20260729.md"
)
OUTPUT = (
    ROOT
    / "experiments"
    / "ecdlp_isogeny"
    / "p1243_parity_repair_phase_diagram_result.json"
)
R_VALUES = (
    Fraction(0),
    Fraction(1, 4),
    Fraction(1, 2),
    Fraction(3, 4),
    Fraction(1),
)


def encode(value: Fraction) -> str:
    return f"{value.numerator}/{value.denominator}"


def source_known(a: Fraction) -> Fraction:
    return max(10 * a, (1 - 3 * a) / 4)


def source_full(a: Fraction) -> Fraction:
    return max(10 * a, (1 - a) / 4)


def candidate_known(
    a: Fraction, r: Fraction, s: Fraction
) -> Fraction:
    return max(
        6 * a,
        (1 + (-3 + 2 * r + 4 * s) * a) / 4,
    )


def candidate_full_no_reuse(
    a: Fraction, r: Fraction, s: Fraction
) -> Fraction:
    return max(
        Fraction(13, 2) * a,
        (1 + (-1 + 2 * r + 4 * s) * a) / 4,
    )


def candidate_full_reuse(
    a: Fraction, r: Fraction, s: Fraction
) -> Fraction:
    return max(
        6 * a,
        (1 + (-1 + 2 * r + 4 * s) * a) / 4,
    )


def candidate_guess(
    a: Fraction,
    r: Fraction,
    s: Fraction,
    full: bool,
) -> Fraction:
    linear = -1 if full else -3
    return (1 + (linear + 2 * r + 4 * s) * a) / 4


def audit_boundary(
    r: Fraction,
    s: Fraction,
    onset: Fraction,
    crossover: Fraction,
    source,
    candidate,
    first_coefficient: Fraction,
    full: bool,
) -> dict[str, object]:
    epsilon = Fraction(1, 10_000_000)
    below = onset - epsilon
    above = onset + epsilon
    first = first_coefficient * crossover
    guess = candidate_guess(crossover, r, s, full)
    mutated = Fraction(
        crossover.numerator, crossover.denominator + 1
    )
    gates = {
        "equal_at_onset": (
            candidate(onset, r, s) == source(onset)
        ),
        "not_strict_below": (
            candidate(below, r, s) >= source(below)
        ),
        "strict_above": (
            candidate(above, r, s) < source(above)
        ),
        "candidate_terms_equal_at_crossover": first == guess,
        "mutated_crossover_rejected": (
            first_coefficient * mutated
            != candidate_guess(mutated, r, s, full)
        ),
    }
    return {
        "onset": encode(onset),
        "candidate_crossover": encode(crossover),
        "source_at_onset": encode(source(onset)),
        "candidate_at_onset": encode(candidate(onset, r, s)),
        "candidate_crossover_exponent": encode(
            candidate(crossover, r, s)
        ),
        "gates": gates,
    }


def audit_mode(r: Fraction, s: Fraction) -> dict[str, object]:
    known_onset = Fraction(1, 1) / (43 - 2 * r - 4 * s)
    full_onset = Fraction(1, 1) / (41 - 2 * r - 4 * s)
    shared_cross = Fraction(1, 1) / (27 - 2 * r - 4 * s)
    reuse_cross = Fraction(1, 1) / (25 - 2 * r - 4 * s)
    return {
        "r": encode(r),
        "s": encode(s),
        "known_target": audit_boundary(
            r,
            s,
            known_onset,
            shared_cross,
            source_known,
            candidate_known,
            Fraction(6),
            False,
        ),
        "full_volcano_no_reuse": audit_boundary(
            r,
            s,
            full_onset,
            shared_cross,
            source_full,
            candidate_full_no_reuse,
            Fraction(13, 2),
            True,
        ),
        "full_volcano_reuse_hypothesis": audit_boundary(
            r,
            s,
            full_onset,
            reuse_cross,
            source_full,
            candidate_full_reuse,
            Fraction(6),
            True,
        ),
    }


def main() -> None:
    rows = []
    for r in R_VALUES:
        modes = (("subpoly_field", Fraction(0)),)
        if r:
            modes += (("maximal_field", r),)
        for label, s in modes:
            rows.append({"field_mode": label, **audit_mode(r, s)})

    def find(r_text: str, s_text: str) -> dict[str, object]:
        return next(
            row
            for row in rows
            if row["r"] == r_text and row["s"] == s_text
        )

    r0 = find("0/1", "0/1")
    r1s0 = find("1/1", "0/1")
    r1s1 = find("1/1", "1/1")
    controls = {
        "r0_known_onset": (
            r0["known_target"]["onset"] == "1/43"
        ),
        "r0_known_crossover": (
            r0["known_target"]["candidate_crossover"] == "1/27"
        ),
        "r0_full_onset": (
            r0["full_volcano_no_reuse"]["onset"] == "1/41"
        ),
        "r0_full_no_reuse_crossover": (
            r0["full_volcano_no_reuse"]["candidate_crossover"]
            == "1/27"
        ),
        "r0_full_reuse_crossover": (
            r0["full_volcano_reuse_hypothesis"][
                "candidate_crossover"
            ]
            == "1/25"
        ),
        "r1s0_known_onset": (
            r1s0["known_target"]["onset"] == "1/41"
        ),
        "r1s0_known_crossover": (
            r1s0["known_target"]["candidate_crossover"] == "1/25"
        ),
        "r1s1_known_onset": (
            r1s1["known_target"]["onset"] == "1/37"
        ),
        "r1s1_known_crossover": (
            r1s1["known_target"]["candidate_crossover"] == "1/21"
        ),
        "r1s1_full_onset": (
            r1s1["full_volcano_no_reuse"]["onset"] == "1/35"
        ),
        "r1s1_full_crossover": (
            r1s1["full_volcano_no_reuse"]["candidate_crossover"]
            == "1/21"
        ),
    }
    all_pass = all(controls.values()) and all(
        all(section["gates"].values())
        for row in rows
        for section in (
            row["known_target"],
            row["full_volcano_no_reuse"],
            row["full_volcano_reuse_hypothesis"],
        )
    )
    scientific = {
        "schema": "p1243-parity-repair-phase-diagram-v2",
        "claim_status": (
            "HEURISTIC COMPLEXITY CONSEQUENCE / "
            "EXACT RATIONAL-ARITHMETIC CHECK"
        ),
        "rows": rows,
        "controls": controls,
    }
    blob = json.dumps(
        scientific, sort_keys=True, separators=(",", ":")
    ).encode()
    result = {
        **scientific,
        "all_pass": all_pass,
        "scientific_data_sha256": hashlib.sha256(blob).hexdigest(),
        "artifact_hashes": {
            "contract_sha256": hashlib.sha256(
                CONTRACT.read_bytes()
            ).hexdigest(),
            "source_sha256": hashlib.sha256(
                Path(__file__).read_bytes()
            ).hexdigest(),
        },
    }
    OUTPUT.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n")
    print(json.dumps(result, indent=2, sort_keys=True))
    if not all_pass:
        raise SystemExit(1)


if __name__ == "__main__":
    main()

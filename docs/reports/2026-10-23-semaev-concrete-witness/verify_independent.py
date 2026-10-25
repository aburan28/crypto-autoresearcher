#!/usr/bin/env python3
"""Independent, read-only replay of one archived Boolean Semaev draw."""

from __future__ import annotations

import hashlib
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
ARCHIVE = ROOT / "docs/reports/2026-10-22-semaev-first-fall-replay/evidence/draws.json"
LEAN = ROOT / "formal/CryptoResearch/Semaev/ConcreteFirstFallWitness.lean"
WITNESS_ROWS = 1321682796735964
EXPECTED_EQUATIONS_SHA = "89ab8e668c510572bbf9307f105b2eaf46858ad900f0b6b4a2fce8803e0ba6eb"


def check(condition: bool, message: str) -> None:
    if not condition:
        raise ValueError(message)


def gf16_mul(left: int, right: int) -> int:
    """Shift-and-reduce in F2[X]/(X^4+X+1), independent of Lean's carryless pass."""
    product = 0
    for _ in range(4):
        if right & 1:
            product ^= left
        right >>= 1
        left <<= 1
        if left & 16:
            left ^= 19
    return product


def rank(vectors: list[int]) -> int:
    """Binary elimination from the *lowest* column, unlike the source checker."""
    pivots: dict[int, int] = {}
    for value in vectors:
        while value:
            column = (value & -value).bit_length() - 1
            if column not in pivots:
                pivots[column] = value
                break
            value ^= pivots[column]
    return len(pivots)


def degree(mask: int) -> int:
    return bin(mask).count("1")


def main() -> None:
    raw = ARCHIVE.read_bytes()
    document = json.loads(raw)
    matches = [entry for entry in document["draws"] if
               (entry["n"], entry["nprime"], entry["draw"], entry["seed"],
                entry["xR"], entry["basis"]) ==
               (4, 4, 1, 32201, 1, [9, 3, 2, 12])]
    check(len(matches) == 1, "archived draw is absent or ambiguous")
    entry = matches[0]
    equations = entry["equations"]
    canonical_sha = hashlib.sha256(json.dumps(equations, separators=(",", ":")).encode()).hexdigest()
    check(canonical_sha == EXPECTED_EQUATIONS_SHA == entry["equations_sha256"],
          "equation hash changed")
    check(len(equations) == 4 and all(all(0 <= mask < 256 for mask in eq) for eq in equations),
          "equation shape changed")
    lean_source = LEAN.read_text()
    lean_combo = re.search(r"def comboMask\s*:\s*Nat\s*:=\s*(\d+)", lean_source)
    lean_witness = re.search(r"def witnessNat\s*:\s*Nat\s*:=\s*(\d+)", lean_source)
    check(lean_combo is not None and int(lean_combo[1]) == WITNESS_ROWS,
          "Lean row-selection literal changed")
    check(lean_witness is not None, "Lean witness literal absent")

    # Check that this is a field and derive the four Boolean equations anew
    # from every S3 assignment, using a Moebius transform for ANF coefficients.
    check(all(any(gf16_mul(a, b) == 1 for b in range(1, 16)) for a in range(1, 16)),
          "the degree-four quotient is not a field")
    outputs = [[0] * 256 for _ in range(4)]
    for assignment in range(256):
        x1 = x2 = 0
        for bit, basis_element in enumerate(entry["basis"]):
            if assignment & (1 << bit):
                x1 ^= basis_element
            if assignment & (1 << (bit + 4)):
                x2 ^= basis_element
        x1x2 = gf16_mul(x1, x2)
        e2 = x1x2 ^ x1 ^ x2  # frozen xR = 1
        s3 = gf16_mul(e2, e2) ^ x1x2 ^ 1  # a6 = 1
        for component in range(4):
            outputs[component][assignment] = (s3 >> component) & 1
    derived = []
    for values in outputs:
        coefficients = values.copy()
        for bit in range(8):
            for mask in range(256):
                if mask & (1 << bit):
                    coefficients[mask] ^= coefficients[mask ^ (1 << bit)]
        derived.append([mask for mask, coefficient in enumerate(coefficients) if coefficient])
    check([set(eq) for eq in equations] == [set(eq) for eq in derived],
          "archived equations differ from independent S3 ANF")

    def rows(max_degree: int) -> list[int]:
        result = []
        for eq in equations:
            for multiplier in range(256):
                poly = 0
                for monomial in eq:
                    poly ^= 1 << (monomial | multiplier)
                if all(degree(mask) <= max_degree for mask in range(256)
                       if (poly >> mask) & 1):
                    result.append(poly)
        return result

    r1, r2, r3 = (rows(degree) for degree in (1, 2, 3))
    top2 = sum(1 << mask for mask in range(256) if degree(mask) == 2)
    top3 = sum(1 << mask for mask in range(256) if degree(mask) == 3)
    d1, d2, d3 = (rank(matrix) for matrix in (r1, r2, r3))
    low2 = d2 - rank([row & top2 for row in r2])
    low3 = d3 - rank([row & top3 for row in r3])
    check((len(r2), len(r3), d1, d2, d3, low2, low3) == (28, 80, 1, 11, 53, 1, 12),
          "finite row-space result differs")
    check(low2 - d1 == 0 and low3 - d2 == 1, "first-fall grade differs")

    selected = [index for index in range(len(r3)) if WITNESS_ROWS & (1 << index)]
    witness = 0
    for index in selected:
        witness ^= r3[index]
    check(witness == int(lean_witness[1]), "derived witness differs from Lean literal")
    check(len(selected) == 23, "witness row count differs")
    check(all(degree(mask) <= 2 for mask in range(256) if (witness >> mask) & 1),
          "witness has a high-degree monomial")
    sep = lambda row: ((row >> 80) & 1) ^ ((row >> 192) & 1)
    check(all(sep(row) == 0 for row in r2) and sep(witness) == 1,
          "separator does not exclude degree-two span")
    check(rank(r2 + [witness]) == 12 and rank(r3 + [witness]) == 53,
          "witness span dimensions differ")

    print(json.dumps({
        "scope": "one finite n=4,nprime=4,draw=1,seed=32201,xR=1 Boolean Semaev sample",
        "archive_sha256": hashlib.sha256(raw).hexdigest(),
        "lean_sha256": hashlib.sha256(LEAN.read_bytes()).hexdigest(),
        "equations_sha256": canonical_sha,
        "field_nonzero_elements_invertible": 15,
        "s3_assignments_checked": 256,
        "anf_components_derived": len(derived),
        "rows_degree_two": len(r2), "rows_degree_three": len(r3),
        "rank_degree_one": d1, "rank_degree_two": d2, "rank_degree_three": d3,
        "lowdim_degree_two": low2, "lowdim_degree_three": low3,
        "new_falls_degree_two": low2 - d1, "new_falls_degree_three": low3 - d2,
        "selected_witness_rows": len(selected),
        "witness_bits": witness,
        "separator": [80, 192],
        "result": "finite counterexample independently reproduced",
        "limit": "No generic first-fall, solving-degree, or ECDLP cost claim",
    }, indent=2))


if __name__ == "__main__":
    main()

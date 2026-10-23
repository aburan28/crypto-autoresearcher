#!/usr/bin/env python3
"""Independently bind the finite Lean witness to the archived Boolean draw."""

from __future__ import annotations

import argparse
import hashlib
import json
import re
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
DRAW = ROOT / "docs/reports/2026-10-22-semaev-first-fall-replay/evidence/draws.json"
FINITE = ROOT / "formal/CryptoResearch/Semaev/BooleanParityFiniteCertificate.lean"
WITNESS = ROOT / "formal/CryptoResearch/Semaev/ConcreteFirstFallWitness.lean"
EQUATIONS_SHA256 = "89ab8e668c510572bbf9307f105b2eaf46858ad900f0b6b4a2fce8803e0ba6eb"
COMBO_MASK = 1321682796735964
WITNESS_BITS = 6277101735386703064921270320751746415339343215057222047510


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def lean_list(source: str) -> list[list[int]]:
    match = re.search(r"def equations\s*:\s*List \(List Nat\)\s*:=\s*(\[\[.*?\]\])", source, re.S)
    assert match, "could not find Lean's equation literal"
    return json.loads(match.group(1))


def lean_nat(source: str, name: str) -> int:
    match = re.search(rf"def {name}\s*:\s*Nat\s*:=\s*(\d+)", source)
    assert match, f"could not find Lean's {name} literal"
    return int(match.group(1))


def product(equation: list[int], multiplier: int, *, parity: bool) -> int:
    row = 0
    for monomial in equation:
        bit = 1 << (monomial | multiplier)
        row = row ^ bit if parity else row | bit
    return row


def rows(equations: list[list[int]], max_degree: int) -> list[tuple[int, int, int]]:
    result = []
    for i, equation in enumerate(equations):
        for multiplier in range(256):
            row = product(equation, multiplier, parity=True)
            if all(m.bit_count() <= max_degree for m in range(256) if row >> m & 1):
                result.append((i, multiplier, row))
    return result


def rank(vectors: list[int]) -> int:
    pivots: dict[int, int] = {}
    for vector in vectors:
        while vector:
            high = vector.bit_length() - 1
            if high not in pivots:
                pivots[high] = vector
                break
            vector ^= pivots[high]
    return len(pivots)


def main() -> None:
    if not __debug__:
        raise RuntimeError("source binding requires enabled Python assertions")
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()

    source = json.loads(DRAW.read_text())
    matches = [item for item in source["draws"] if
               (item["n"], item["nprime"], item["draw"], item["seed"], item["xR"], item["basis"])
               == (4, 4, 1, 32201, 1, [9, 3, 2, 12])]
    assert len(matches) == 1, "source draw is absent or ambiguous"
    draw = matches[0]
    equations = draw["equations"]
    canonical = json.dumps(equations, separators=(",", ":")).encode()
    assert hashlib.sha256(canonical).hexdigest() == draw["equations_sha256"] == EQUATIONS_SHA256
    assert equations == lean_list(FINITE.read_text()), "Lean equations differ from archived draw"

    lean_source = WITNESS.read_text()
    assert lean_nat(lean_source, "comboMask") == COMBO_MASK
    assert lean_nat(lean_source, "witnessNat") == WITNESS_BITS
    degree_two = rows(equations, 2)
    degree_three = rows(equations, 3)
    assert len(degree_two) == 28 and len(degree_three) == 80
    selected = [(i, eq, multiplier) for i, (eq, multiplier, _) in enumerate(degree_three)
                if COMBO_MASK >> i & 1]
    witness = 0
    for i, _, _ in selected:
        witness ^= degree_three[i][2]
    assert witness == WITNESS_BITS, "selected rows do not yield Lean's witness"
    assert all(m.bit_count() <= 2 for m in range(256) if witness >> m & 1)
    separator = lambda value: (value >> 80 & 1) ^ (value >> 192 & 1)
    assert all(separator(row) == 0 for _, _, row in degree_two)
    assert separator(witness) == 1
    assert rank([row for _, _, row in degree_two]) == 11
    assert rank([row for _, _, row in degree_three]) == 53
    assert rank([row for _, _, row in degree_three] + [witness]) == 53
    assert rank([row for _, _, row in degree_two] + [witness]) == 12
    assert product(equations[0], 1, parity=False) ^ product(equations[0], 1, parity=True) == (1 << 1) | (1 << 17) | (1 << 129)

    receipt = {
        "scope": "one archived n=4,nprime=4,draw=1,seed=32201,xR=1 Boolean Semaev sample",
        "draw_path": str(DRAW.relative_to(ROOT)),
        "draw_sha256": sha256(DRAW),
        "equations_sha256": EQUATIONS_SHA256,
        "finite_lean_path": str(FINITE.relative_to(ROOT)),
        "finite_lean_sha256": sha256(FINITE),
        "witness_lean_path": str(WITNESS.relative_to(ROOT)),
        "witness_lean_sha256": sha256(WITNESS),
        "degree_two_rows": len(degree_two),
        "degree_three_rows": len(degree_three),
        "degree_two_rank": 11,
        "degree_three_rank": 53,
        "selected_rows": selected,
        "selected_row_count": len(selected),
        "combo_mask": COMBO_MASK,
        "witness_bits": WITNESS_BITS,
        "witness_monomial_masks": [m for m in range(256) if witness >> m & 1],
        "separator_monomial_masks": [80, 192],
        "separator_on_all_degree_two_rows": 0,
        "separator_on_witness": 1,
        "rank_degree_two_plus_witness": 12,
        "archived_set_product_extra_masks": [1, 17, 129],
    }
    payload = json.dumps(receipt, indent=2) + "\n"
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(payload)
    print(payload, end="")


if __name__ == "__main__":
    main()

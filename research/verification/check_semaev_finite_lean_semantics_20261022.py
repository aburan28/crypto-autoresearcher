"""Compare Lean's 16x16 field table and 256 S3 values with the Python reference.

Generate the input log from the fixed, pinned Lean module:

    lake env lean /path/to/evidence/finite-equation-lean-eval.lean > LOG

The Lean evaluator file imports FiniteEquationSemantics and evaluates
``(List.range 16).flatMap ... fieldMul`` and
``(List.range 256).map semaevS3`` in that order. This checker does not rely on
the Boolean component equations or Lean's rank routine.
"""

from __future__ import annotations

import argparse
import ast
from pathlib import Path
import re

from replay_ffd_semaev_20261022 import MODS, mul_ref


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("lean_eval_log", type=Path)
    args = parser.parse_args()
    text = args.lean_eval_log.read_text(encoding="utf-8")
    chunks = re.findall(r"\[[\s\d,]+\]", text)
    assert len(chunks) == 2, f"expected two Lean evaluation lists, got {len(chunks)}"
    field_table, s3_values = (ast.literal_eval(chunk) for chunk in chunks)
    assert len(field_table) == len(s3_values) == 256
    assert MODS[4] == 0b10011

    expected_field_table = [mul_ref(a, b, 4) for a in range(16) for b in range(16)]
    assert field_table == expected_field_table, "Lean field multiplication differs"

    basis = (9, 3, 2, 12)
    expected_s3_values = []
    for assignment in range(256):
        x1 = 0
        x2 = 0
        for j, coefficient in enumerate(basis):
            if assignment >> j & 1:
                x1 ^= coefficient
            if assignment >> (j + 4) & 1:
                x2 ^= coefficient
        x1x2 = mul_ref(x1, x2, 4)
        e2 = x1x2 ^ x1 ^ x2
        expected_s3_values.append(mul_ref(e2, e2, 4) ^ x1x2 ^ 1)
    assert s3_values == expected_s3_values, "Lean S3 evaluation differs"
    print("PASS: 256 Lean GF(16) products and 256 S3 values match the independent Python reference")


if __name__ == "__main__":
    main()

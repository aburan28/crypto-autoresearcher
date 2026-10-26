#!/usr/bin/env python3
"""Independent, read-only check of the three frozen C5 quotient matrices.

This checks archive bytes, polynomial arithmetic and Lean matrix literals. It
does not execute or verify the historical Sage driver or amend its run record.
"""

from __future__ import annotations

import hashlib
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
RUN = ROOT / "experiments/EXP-FROB-91ee9c/runs/TASK-20260914-7119f2"
REPLAY_DIR = ROOT / "docs/reports/2026-10-22-frob-c5-factor-kernels"
LEAN = ROOT / "formal/CryptoResearch/FrobTrace/QuotientMatrices.lean"
REPLAY_SHA256 = "22bcbdbdc6dd8c020456549cb1aa2edf887422cb10912105d9fa0508a6ee1005"
LEAN_SHA256 = "9de7bc465a4a12f6e325ddd61b67dd275d8ef6f622307bd2244707aaf081c39b"
CELLS = {
    "FROB-SPLIT-q11n5": (11, 2),
    "FROB-NOLATTICE-q13n5": (13, 8),
    "FROB-EQDEG-q19n5": (19, 3),
}


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def trim(poly: list[int]) -> list[int]:
    while len(poly) > 1 and poly[-1] == 0:
        poly.pop()
    return poly


def remainder(poly: list[int], divisor: list[int], q: int) -> list[int]:
    result = trim([value % q for value in poly])
    divisor = trim([value % q for value in divisor])
    assert divisor != [0]
    inverse = pow(divisor[-1], -1, q)
    while len(result) >= len(divisor) and result != [0]:
        offset = len(result) - len(divisor)
        factor = result[-1] * inverse % q
        for i, value in enumerate(divisor):
            result[offset + i] = (result[offset + i] - factor * value) % q
        trim(result)
    return result


def product_mod(a: list[int], b: list[int], modulus: list[int], q: int) -> list[int]:
    result = [0] * (len(a) + len(b) - 1)
    for i, x in enumerate(a):
        for j, y in enumerate(b):
            result[i + j] = (result[i + j] + x * y) % q
    return remainder(result, modulus, q)


def power_mod(base: list[int], exponent: int, modulus: list[int], q: int) -> list[int]:
    result = [1]
    while exponent:
        if exponent & 1:
            result = product_mod(result, base, modulus, q)
        base = product_mod(base, base, modulus, q)
        exponent >>= 1
    return result


def monic_gcd(a: list[int], b: list[int], q: int) -> list[int]:
    while b != [0]:
        a, b = b, remainder(a, b, q)
    inverse = pow(a[-1], -1, q)
    return [(value * inverse) % q for value in a]


def is_irreducible_degree_five(modulus: list[int], q: int) -> bool:
    # Rabin's criterion: 5 is prime, so gcd(f, X^q-X)=1 and X^(q^5)=X mod f.
    xq = power_mod([0, 1], q, modulus, q)
    difference = xq + [0] * max(0, 2 - len(xq))
    difference[1] = (difference[1] - 1) % q
    return monic_gcd(modulus, trim(difference), q) == [1] and (
        power_mod([0, 1], q**5, modulus, q) == [0, 1]
    )


def matrix_literal(source: str, q: int) -> list[list[int]]:
    match = re.search(
        rf"\bdef frobeniusMatrix{q}\b[^\n]*:=\s*!!\[(.*?)\]",
        source,
        flags=re.DOTALL,
    )
    assert match is not None, f"missing Lean matrix literal for q={q}"
    rows = [[int(value.strip()) for value in row.split(",")]
            for row in match.group(1).split(";")]
    assert len(rows) == 5 and all(len(row) == 5 for row in rows)
    return rows


def raw_payload(path: Path) -> dict:
    raw = path.read_bytes()
    begin, end = b"RESULT_JSON_BEGIN\n", b"\nRESULT_JSON_END\n"
    assert raw.startswith(begin) and raw.endswith(end)
    assert raw.count(begin) == 1 and raw.count(end) == 1
    return json.loads(raw[len(begin):-len(end)])


def check() -> dict:
    if not __debug__:
        raise RuntimeError("the cross-check requires Python assertions")
    assert sha256(REPLAY_DIR / "c5-matrix-replay.json") == REPLAY_SHA256
    assert sha256(LEAN) == LEAN_SHA256
    replay = json.loads((REPLAY_DIR / "c5-matrix-replay.json").read_text())
    assert replay["schema"] == "frob-c5-source-bound-matrix-replay/v1"
    assert replay["source_run"] == "RUN-FROB-91ee9c-7119f2"
    bindings = {
        ROOT / "experiments/EXP-FROB-91ee9c/specification.yaml": "specification_sha256",
        RUN / "fixtures.json": "fixtures_sha256",
        RUN / "work/core.py": "sage_core_sha256",
        RUN / "work/lattice.py": "sage_lattice_sha256",
        RUN / "implementation.py": "sage_driver_sha256",
        RUN / "checker.py": "archived_checker_sha256",
        REPLAY_DIR / "recheck_matrix.py": "source_sha256",
    }
    for path, field in bindings.items():
        assert sha256(path) == replay[field], f"source hash mismatch: {path}"
    source = LEAN.read_text()
    assert len(replay["cells"]) == 3
    results = {}
    for cell in replay["cells"]:
        name = cell["cell"]
        assert name in CELLS and name not in results
        q, a = CELLS[name]
        modulus = [1, 0, 0, 0, a, 1]
        assert cell["q"] == q and cell["n"] == 5
        assert cell["field_modulus"] == f"x^5 + {a}*x^4 + 1"
        raw_path = RUN / "work" / f"{name}.out.json"
        assert sha256(raw_path) == cell["archived_output_sha256"]
        raw = raw_payload(raw_path)
        assert raw["cell"] == name and raw["q"] == q and raw["n"] == 5
        assert raw["field_modulus"] == cell["field_modulus"]
        assert "frobenius_matrix" not in raw, "raw schema changed; revisit provenance"
        assert is_irreducible_degree_five(modulus, q)
        # Constant coefficient is the slowest-changing tuple component. All
        # earlier tuples either have zero constant or use a smaller X^4 term.
        for smaller_a in range(a):
            assert not is_irreducible_degree_five([1, 0, 0, 0, smaller_a, 1], q)
        matrix = matrix_literal(source, q)
        assert matrix == cell["frobenius_matrix"]
        for j in range(5):
            xqj = power_mod([0, 1], q * j, modulus, q)
            for i in range(5):
                assert matrix[i][j] == (xqj[i] if i < len(xqj) else 0), (
                    f"matrix mismatch: {name} row={i} column={j}"
                )
        results[name] = {"q": q, "entries_checked": 25,
                         "irreducible": True, "lex_first": True,
                         "raw_output_sha256": cell["archived_output_sha256"]}
    assert set(results) == set(CELLS)
    return {"schema": "crypto.audit.frob_c5_quotient_crosscheck.v1",
            "replay_sha256": sha256(REPLAY_DIR / "c5-matrix-replay.json"),
            "lean_source_sha256": sha256(LEAN), "source_hashes_checked": len(bindings),
            "results": results,
            "scope": "raw bytes, quotient arithmetic and Lean literals; no historical Sage execution or field isomorphism proof"}


if __name__ == "__main__":
    print(json.dumps(check(), indent=2, sort_keys=True))

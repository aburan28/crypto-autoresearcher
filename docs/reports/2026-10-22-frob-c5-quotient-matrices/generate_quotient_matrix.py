#!/usr/bin/env python3
"""Generate Lean quotient-basis Frobenius certificates from the frozen C5 replay.

The generator is independent of the archived Sage implementation and of the
replay's quotient arithmetic. Lean checks every emitted division identity.
"""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
REPLAY_DIR = ROOT / "docs/reports/2026-10-22-frob-c5-factor-kernels"
REPLAY = REPLAY_DIR / "c5-matrix-replay.json"
CHECKER = REPLAY_DIR / "recheck_matrix.py"
OUTPUT = ROOT / "formal/CryptoResearch/FrobTrace/QuotientMatrices.lean"
REPLAY_SHA256 = "22bcbdbdc6dd8c020456549cb1aa2edf887422cb10912105d9fa0508a6ee1005"
CELLS = [
    ("FROB-SPLIT-q11n5", 11, 2, "x^5 + 2*x^4 + 1"),
    ("FROB-NOLATTICE-q13n5", 13, 8, "x^5 + 8*x^4 + 1"),
    ("FROB-EQDEG-q19n5", 19, 3, "x^5 + 3*x^4 + 1"),
]


def digest(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def polynomial_expression(coefficients: list[int], prime: int) -> str:
    terms = []
    for power, coefficient in reversed(list(enumerate(coefficients))):
        if coefficient == 0:
            continue
        if coefficient > prime // 2:
            coefficient -= prime
        monomial = "1" if power == 0 else ("X" if power == 1 else f"X^{power}")
        magnitude = abs(coefficient)
        term = (monomial if magnitude == 1 and power else
                str(magnitude) if power == 0 else f"{magnitude}*{monomial}")
        terms.append(("-" if coefficient < 0 else "+", term))
    expression = ""
    for sign, term in terms:
        expression += (("-" if sign == "-" else "") + term) if not expression else f" {sign} {term}"
    return expression or "0"


def divide_monomial(exponent: int, modulus: list[int], prime: int) -> tuple[list[int], list[int]]:
    """Long division over F_p, constant coefficient first."""
    degree = len(modulus) - 1
    dividend = [0] * exponent + [1]
    quotient = [0] * max(0, len(dividend) - degree)
    for power in range(exponent, degree - 1, -1):
        coefficient = dividend[power] % prime
        quotient[power - degree] = coefficient
        for i, g_coefficient in enumerate(modulus):
            dividend[power - degree + i] = (
                dividend[power - degree + i] - coefficient * g_coefficient
            ) % prime
    return quotient, dividend[:degree]


def integer_residual(quotient: list[int], remainder: list[int],
                     modulus: list[int], exponent: int, prime: int) -> list[int]:
    """Integer coefficients left after centering Q,R and subtracting X^e."""
    centered = lambda values: [v - prime if v > prime // 2 else v for v in values]
    q_coefficients, r_coefficients = centered(quotient), centered(remainder)
    result = [0] * (exponent + 1)
    for i, value in enumerate(r_coefficients):
        result[i] += value
    for i, value in enumerate(q_coefficients):
        for j, g_coefficient in enumerate(modulus):
            result[i + j] += value * g_coefficient
    result[exponent] -= 1
    assert all(value % prime == 0 for value in result)
    return result


def cast_zero(prime: int, multiple: int) -> str:
    name = f"cast{prime}_{multiple}"
    if multiple == prime:
        proof = f"""  change C ({prime} : ZMod {prime}) = 0
  rw [← C_0]
  congr 1"""
    else:
        proof = f"""  calc
    ({multiple} : (ZMod {prime})[X]) = ({prime} : (ZMod {prime})[X]) * {multiple // prime} := by norm_num
    _ = 0 := by simp [cast{prime}_{prime}]"""
    return f"private theorem {name} : ({multiple} : (ZMod {prime})[X]) = 0 := by\n{proof}\n"


def cell_source(cell: dict, name: str, prime: int, x4: int, modulus_string: str) -> str:
    assert cell["cell"] == name and cell["q"] == prime and cell["n"] == 5
    assert cell["field_modulus"] == modulus_string
    assert cell["field_modulus_irreducible"] is True
    assert cell["lexicographically_first_irreducible"] is True
    matrix = cell["frobenius_matrix"]
    assert len(matrix) == 5 and all(len(row) == 5 for row in matrix)
    assert all(isinstance(value, int) and 0 <= value < prime
               for row in matrix for value in row)
    modulus = [1, 0, 0, 0, x4, 1]
    certificates = []
    multiples = set()
    for j in range(1, 5):
        quotient, remainder = divide_monomial(prime * j, modulus, prime)
        assert remainder == [matrix[i][j] for i in range(5)]
        residual = integer_residual(quotient, remainder, modulus, prime * j, prime)
        needed = sorted({abs(value) for value in residual if value})
        assert all(value % prime == 0 for value in needed)
        multiples.update(needed)
        certificates.append((j, quotient, remainder, needed))
    assert [matrix[i][0] for i in range(5)] == [1, 0, 0, 0, 0]
    block = [f"""local instance : Fact (Nat.Prime {prime}) := ⟨by decide⟩

/-- Frozen monic quotient modulus for {name}; coefficients are constant first in the replay. -/
noncomputable def modulus{prime} : (ZMod {prime})[X] := X^5 + ({x4} * X^4 + 1)

private theorem modulus{prime}_low : degree ({x4} * X^4 + 1 : (ZMod {prime})[X]) < 5 := by
  have h4 : degree ({x4} * X^4 : (ZMod {prime})[X]) ≤ 4 := by
    calc
      degree ({x4} * X^4 : (ZMod {prime})[X]) ≤ degree ({x4} : (ZMod {prime})[X]) + degree (X^4) := degree_mul_le _ _
      _ ≤ 4 := by simpa using add_le_add (degree_natCast_le (R := ZMod {prime}) {x4}) (show degree (X^4 : (ZMod {prime})[X]) ≤ 4 by simp)
  have h1 : degree (1 : (ZMod {prime})[X]) ≤ 4 := by simp
  exact lt_of_le_of_lt ((degree_add_le _ _).trans (max_le h4 h1)) (by norm_num)

theorem modulus{prime}_monic : (modulus{prime}).Monic := by
  unfold modulus{prime}
  exact monic_X_pow_add modulus{prime}_low

private theorem modulus{prime}_degree : degree modulus{prime} = 5 := by
  unfold modulus{prime}
  have hlow : degree ({x4} * X^4 + 1 : (ZMod {prime})[X]) < degree (X^5 : (ZMod {prime})[X]) := by simpa using modulus{prime}_low
  rw [degree_add_eq_left_of_degree_lt hlow, degree_X_pow]
  norm_num

private theorem modulus{prime}_natDegree : modulus{prime}.natDegree = 5 :=
  natDegree_eq_of_degree_eq_some modulus{prime}_degree
"""]
    multiples.add(prime)
    block.extend(cast_zero(prime, value) for value in sorted(multiples))
    for j, quotient, remainder, needed in certificates:
        casts = ", ".join(f"cast{prime}_{value}" for value in needed)
        block.append(f"""
private noncomputable def quotient{prime}_{j} : (ZMod {prime})[X] := {polynomial_expression(quotient, prime)}
private noncomputable def remainder{prime}_{j} : (ZMod {prime})[X] := {polynomial_expression(remainder, prime)}

private theorem remainder{prime}_{j}_degree : degree remainder{prime}_{j} < degree modulus{prime} := by
  rw [modulus{prime}_degree]
  unfold remainder{prime}_{j}
  compute_degree; norm_num

private theorem division{prime}_{j} :
    remainder{prime}_{j} + modulus{prime} * quotient{prime}_{j} = X^{prime*j} := by
  unfold remainder{prime}_{j} modulus{prime} quotient{prime}_{j}
  ring_nf
  simp [{casts}]

private theorem remainder{prime}_{j}_exact :
    (X^{prime*j} : (ZMod {prime})[X]) %ₘ modulus{prime} = remainder{prime}_{j} :=
  (div_modByMonic_unique quotient{prime}_{j} remainder{prime}_{j}
    modulus{prime}_monic ⟨division{prime}_{j}, remainder{prime}_{j}_degree⟩).2
""")
    rows = ";\n     ".join(", ".join(map(str, row)) for row in matrix)
    mod_lemmas = ", ".join(f"remainder{prime}_{j}_exact" for j in range(1, 5))
    remainders = ", ".join(f"remainder{prime}_{j}" for j in range(1, 5))
    block.append(f"""
/-- The exact archived 5×5 matrix, with q-power images as columns. -/
def frobeniusMatrix{prime} : Matrix (Fin 5) (Fin 5) (ZMod {prime}) :=
  !![{rows}]

private theorem remainder{prime}_matrix : ∀ i j : Fin 5,
    ((X^({prime} * (j : ℕ)) : (ZMod {prime})[X]) %ₘ modulus{prime}).coeff (i : ℕ) =
      frobeniusMatrix{prime} i j := by
  intro i j
  have hzero : (1 : (ZMod {prime})[X]) %ₘ modulus{prime} = 1 := by
    apply (Polynomial.modByMonic_eq_self_iff modulus{prime}_monic).2
    rw [modulus{prime}_degree]
    norm_num
  fin_cases j <;> fin_cases i <;>
    simp [hzero, {mod_lemmas},
      {remainders}, frobeniusMatrix{prime},
      Polynomial.coeff_add, Polynomial.coeff_sub,
      Polynomial.coeff_X_pow, Polynomial.coeff_X, Polynomial.coeff_one] <;> decide

/-- Every entry of the frozen Frobenius matrix equals the q-power operation
on the corresponding archived quotient-basis monomial. -/
theorem quotient_frobenius_matrix{prime} (i j : Fin 5) :
    (AdjoinRoot.powerBasisAux' modulus{prime}_monic).repr
      ((AdjoinRoot.root modulus{prime}) ^ ({prime} * (j : ℕ)))
      (Fin.cast modulus{prime}_natDegree.symm i) = frobeniusMatrix{prime} i j := by
  rw [AdjoinRoot.powerBasisAux'_repr_apply_to_fun]
  have hroot : (AdjoinRoot.root modulus{prime}) ^ ({prime} * (j : ℕ)) =
      AdjoinRoot.mk modulus{prime} (X ^ ({prime} * (j : ℕ))) := by
    rw [← AdjoinRoot.mk_X]
    exact (map_pow (AdjoinRoot.mk modulus{prime}) X _).symm
  rw [hroot, AdjoinRoot.modByMonicHom_mk]
  simpa using remainder{prime}_matrix i j
""")
    return "\n".join(block)


def main() -> None:
    if not __debug__:
        raise RuntimeError("quotient matrix generation requires Python assertions")
    parser = argparse.ArgumentParser()
    parser.add_argument("--check", action="store_true", help="Require byte-identical generated Lean source")
    args = parser.parse_args()
    replay_bytes = REPLAY.read_bytes()
    assert digest(replay_bytes) == REPLAY_SHA256, "C5 replay bytes changed"
    replay = json.loads(replay_bytes)
    assert replay["source_sha256"] == digest(CHECKER.read_bytes()), "C5 replay checker changed"
    assert replay["schema"] == "frob-c5-source-bound-matrix-replay/v1"
    assert replay["source_run"] == "RUN-FROB-91ee9c-7119f2"
    assert len(replay["cells"]) == len(CELLS)
    source = f"""import Mathlib.RingTheory.AdjoinRoot
import Mathlib.Tactic

/-!
Exact archived-quotient Frobenius matrices for EXP-FROB-91ee9c C5.
Generated from the immutable source-bound replay receipt SHA-256
{REPLAY_SHA256}. Lean checks the polynomial divisions and basis entries.
This does not verify the historical Sage implementation or original source custody.
-/

open Polynomial
set_option maxRecDepth 4000
namespace CryptoResearch.FrobTrace.QuotientMatrices

"""
    source += "\n".join(cell_source(cell, *config) for cell, config in zip(replay["cells"], CELLS))
    claims = []
    for _, prime, _, _ in CELLS:
        claims.append(f"""(∀ i j : Fin 5,
      (AdjoinRoot.powerBasisAux' modulus{prime}_monic).repr
        ((AdjoinRoot.root modulus{prime}) ^ ({prime} * (j : ℕ)))
        (Fin.cast modulus{prime}_natDegree.symm i) = frobeniusMatrix{prime} i j)""")
    source += "\n/-- The three exact archived-quotient Frobenius matrices. -/\n"
    source += "theorem all_quotient_frobenius_matrices :\n  "
    source += " ∧\n  ".join(claims)
    source += " := by\n  exact ⟨quotient_frobenius_matrix11, quotient_frobenius_matrix13, "
    source += "quotient_frobenius_matrix19⟩\n"
    source += "\nend CryptoResearch.FrobTrace.QuotientMatrices\n"
    encoded = source.encode("utf-8")
    if args.check:
        assert OUTPUT.read_bytes() == encoded, "quotient matrix Lean source differs"
        print("byte-exact Lean quotient matrix source match")
    else:
        assert not OUTPUT.exists(), "refusing to overwrite an existing Lean source"
        OUTPUT.parent.mkdir(parents=True, exist_ok=True)
        OUTPUT.write_bytes(encoded)
        print(OUTPUT)


if __name__ == "__main__":
    main()

"""Generate Lean matrix-rank witnesses for one frozen Semaev toy draw.

The Python elimination proposes row transforms. The generated Lean file checks
the exact source rows, transform invertibility and pivots, then uses Mathlib's
rank theorem. The generator is deterministic and writes only --output.
"""

import argparse
from hashlib import sha256
import json
from pathlib import Path

from replay_ffd_semaev_20261022 import parity_rows_for_degree

root = Path(__file__).resolve().parents[2]
draw_path = root / 'docs/reports/2026-10-22-semaev-first-fall-replay/evidence/draws.json'
record = json.loads(draw_path.read_text(encoding='utf-8'))
draw = next(row for row in record['draws']
            if (row['n'], row['nprime'], row['draw']) == (4, 4, 1))
encoded = json.dumps(draw['equations'], separators=(',', ':')).encode()
assert draw['equations_sha256'] == sha256(encoded).hexdigest()
assert draw['equations_sha256'] == '89ab8e668c510572bbf9307f105b2eaf46858ad900f0b6b4a2fce8803e0ba6eb'
eqs = [frozenset(f) for f in draw['equations']]


def echelon(rows, ncols):
    current = rows.copy()
    size = len(current)
    transform = [1 << i for i in range(size)]
    pivots = []
    next_row = 0
    for col in range(ncols):
        choice = next((j for j in range(next_row, size) if current[j] >> col & 1), None)
        if choice is None:
            continue
        current[next_row], current[choice] = current[choice], current[next_row]
        transform[next_row], transform[choice] = transform[choice], transform[next_row]
        for j in range(next_row + 1, size):
            if current[j] >> col & 1:
                current[j] ^= current[next_row]
                transform[j] ^= transform[next_row]
        pivots.append(col)
        next_row += 1
        if next_row == size:
            break
    assert all(row == 0 for row in current[next_row:])
    return transform, pivots, current


def inverse(rows):
    size = len(rows)
    current = rows.copy()
    result = [1 << i for i in range(size)]
    for col in range(size):
        choice = next((j for j in range(col, size) if current[j] >> col & 1), None)
        assert choice is not None
        current[col], current[choice] = current[choice], current[col]
        result[col], result[choice] = result[choice], result[col]
        for j in range(size):
            if j != col and current[j] >> col & 1:
                current[j] ^= current[col]
                result[j] ^= result[col]
    assert current == [1 << i for i in range(size)]
    return result
sections = []
for name, degree, project in [('one', 1, False), ('two', 2, False),
                              ('twoProjected', 2, True)]:
    rows = parity_rows_for_degree(eqs, 8, degree)
    if project:
        mask = sum(1 << j for j in range(256) if j.bit_count() == degree)
        rows = [value & mask for value in rows]
    U, pivots, echelon_rows = echelon(rows, 256)
    V = inverse(U)
    size, rank = len(rows), len(pivots)
    assert (size, rank) == {'one': (17, 1), 'two': (28, 11),
                            'twoProjected': (28, 10)}[name]
    for transformed, coefficients in zip(echelon_rows, U):
        expected = 0
        for i, original_row in enumerate(rows):
            if coefficients >> i & 1:
                expected ^= original_row
        assert transformed == expected
    print(name, size, rank, pivots)

    def ns(values):
        return '[' + ', '.join(map(str, values)) + ']'

    pitems = [f'(({p} : Fin 256) : WithTop (Fin 256))' for p in pivots]
    pitems += ['⊤'] * (size - rank)
    s=f'''
namespace {name}
private def literalRows : List Nat := {ns(rows)}
private theorem literalRows_eq : literalRows = {"((rows 2).map (fun row => Nat.land row (degreeMask 2)))" if project else f"rows {degree}"} := by decide
private def Urows : List Nat := {ns(U)}
private def Vrows : List Nat := {ns(V)}
private def pivots : List (WithTop (Fin 256)) := [{', '.join(pitems)}]
private def A : Matrix (Fin {size}) (Fin 256) (ZMod 2) := matrixOfRows {size} literalRows
private def U : Matrix (Fin {size}) (Fin {size}) (ZMod 2) :=
  fun i j => if (Urows[i.val]!).testBit j.val then 1 else 0
private def V : Matrix (Fin {size}) (Fin {size}) (ZMod 2) :=
  fun i j => if (Vrows[i.val]!).testBit j.val then 1 else 0
private def pivot (i : Fin {size}) : WithTop (Fin 256) := pivots[i.val]!
private theorem leftInverse : V * U = 1 := by decide
private theorem isPivoted : (U * A).IsPivotedBy pivot := by decide
private theorem pivotCount : #{{i : Fin {size} | pivot i ≠ ⊤}} = {rank} := by decide
theorem actualRank : A.rank = {rank} := by
  have hdet : IsUnit U.det := Matrix.isUnit_det_of_left_inverse leftInverse
  have h := isPivoted.rank_eq
  rw [Matrix.rank_mul_eq_right_of_isUnit_det U A hdet, pivotCount] at h
  exact h
theorem sourceRank : (matrixOfRows {size} {"((rows 2).map (fun row => Nat.land row (degreeMask 2)))" if project else f"(rows {degree})"}).rank = {rank} := by
  rw [← literalRows_eq]
  exact actualRank
end {name}
'''
    sections.append(s)
header='''import Mathlib
import CryptoResearch.Semaev.BooleanParityFiniteCertificate

/-!
# Matrix-rank semantics for one Semaev Boolean-parity draw

The fixed n=4, n'=4, s=1, x_R=1 component equations have JSON SHA-256
89ab8e668c510572bbf9307f105b2eaf46858ad900f0b6b4a2fce8803e0ba6eb.
Literal rows are proved equal to the source Boolean-parity routine. Python
proposed elimination matrices; Lean checks their inverse and pivot properties.
Mathlib's rank theorem then identifies the three ranks with F₂ row-space
dimensions. This proves the degree-two rank bridge for this one sample.
The general rankOn theorem and degree-three rank semantics remain open.
-/

set_option maxRecDepth 1000000
set_option maxHeartbeats 0
open CryptoResearch.Semaev.BooleanParityFiniteCertificate
open Matrix
open scoped Finset
namespace CryptoResearch.Semaev.BooleanParitySemanticRankCertificate

def matrixOfRows (m : Nat) (rs : List Nat) : Matrix (Fin m) (Fin 256) (ZMod 2) :=
  fun i j => if (rs[i.val]!).testBit j.val then 1 else 0
'''
footer='''
theorem sourceRowSpaceDimOne :
    Module.finrank (ZMod 2)
      (Submodule.span (ZMod 2) (Set.range (matrixOfRows 17 (rows 1)).row)) = 1 := by
  rw [← Matrix.rank_eq_finrank_span_row]
  exact one.sourceRank

theorem sourceRowSpaceDimTwo :
    Module.finrank (ZMod 2)
      (Submodule.span (ZMod 2) (Set.range (matrixOfRows 28 (rows 2)).row)) = 11 := by
  rw [← Matrix.rank_eq_finrank_span_row]
  exact two.sourceRank

theorem sourceProjectedRowSpaceDimTwo :
    Module.finrank (ZMod 2)
      (Submodule.span (ZMod 2)
        (Set.range (matrixOfRows 28 ((rows 2).map
          (fun row => Nat.land row (degreeMask 2)))).row)) = 10 := by
  rw [← Matrix.rank_eq_finrank_span_row]
  exact twoProjected.sourceRank

/-- This rank difference uses actual F₂ matrix row-space dimensions. -/
theorem semanticNoFallTwo :
    (matrixOfRows 28 (rows 2)).rank -
    (matrixOfRows 28 ((rows 2).map (fun row => Nat.land row (degreeMask 2)))).rank -
    (matrixOfRows 17 (rows 1)).rank = 0 := by
  rw [two.sourceRank, twoProjected.sourceRank, one.sourceRank]

/-- The finite executable rank counts equal Mathlib matrix ranks here. -/
theorem executableRankMatchesSemantic :
    rank (rows 1) = (matrixOfRows 17 (rows 1)).rank ∧
    rank (rows 2) = (matrixOfRows 28 (rows 2)).rank ∧
    projectedRank 2 =
      (matrixOfRows 28 ((rows 2).map (fun row => Nat.land row (degreeMask 2)))).rank := by
  rw [rank_one, rank_two, projected_rank_two, one.sourceRank, two.sourceRank, twoProjected.sourceRank]
  decide

end CryptoResearch.Semaev.BooleanParitySemanticRankCertificate
'''
parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument('--output', type=Path, required=True)
args = parser.parse_args()
args.output.parent.mkdir(parents=True, exist_ok=True)
args.output.write_text(header + '\n'.join(sections) + footer, encoding='utf-8')
print(f'wrote {args.output}: source-bound rows 17/28, ranks 1/11/10')

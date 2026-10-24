"""Generate degree-three Lean matrix-rank witnesses for one frozen Semaev draw.

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
for name, degree, project in [('three', 3, False), ('threeProjected', 3, True)]:
    rows = parity_rows_for_degree(eqs, 8, degree)
    if project:
        mask = sum(1 << j for j in range(256) if j.bit_count() == degree)
        rows = [value & mask for value in rows]
    U, pivots, echelon_rows = echelon(rows, 256)
    V = inverse(U)
    size, rank = len(rows), len(pivots)
    assert (size, rank) == {'three': (80, 53), 'threeProjected': (80, 41)}[name]
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
private theorem literalRows_eq : literalRows = {"((rows 3).map (fun row => Nat.land row (degreeMask 3)))" if project else "rows 3"} := by decide
private def Urows : List Nat := {ns(U)}
private def Vrows : List Nat := {ns(V)}
private def pivots : List (WithTop (Fin 256)) := [{', '.join(pitems)}]
private def A : Matrix (Fin {size}) (Fin 256) (ZMod 2) := matrixOfRows {size} literalRows
private def U : Matrix (Fin {size}) (Fin {size}) (ZMod 2) :=
  fun i j => if (Urows[i.val]!).testBit j.val then 1 else 0
private def V : Matrix (Fin {size}) (Fin {size}) (ZMod 2) :=
  fun i j => if (Vrows[i.val]!).testBit j.val then 1 else 0
private def pivot (i : Fin {size}) : WithTop (Fin 256) := pivots[i.val]!
private def Erows : List Nat := {ns(echelon_rows)}
private def E : Matrix (Fin {size}) (Fin 256) (ZMod 2) := matrixOfRows {size} Erows
private theorem rowXor_Erows (i : Fin {size}) :
    rowXor (Urows[i.val]!) literalRows {size} = Erows[i.val]! := by
  fin_cases i <;> decide
private theorem transformedRows : U * A = E := by
  rw [show U = matrixOfCoeffs {size} Urows by rfl,
      show A = matrixOfRows {size} literalRows by rfl,
      matrixMul_eq_rowXor]
  funext i j
  rw [rowXor_Erows i]
  rfl
private theorem leftInverse : V * U = 1 := by
  funext i
  fin_cases i <;> decide
private theorem echelonPivoted : E.IsPivotedBy pivot := by decide
private theorem isPivoted : (U * A).IsPivotedBy pivot := by
  rw [transformedRows]
  exact echelonPivoted
private theorem pivotCount : #{{i : Fin {size} | pivot i ≠ ⊤}} = {rank} := by decide
theorem actualRank : A.rank = {rank} := by
  have hdet : IsUnit U.det := Matrix.isUnit_det_of_left_inverse leftInverse
  have h := isPivoted.rank_eq
  rw [Matrix.rank_mul_eq_right_of_isUnit_det U A hdet, pivotCount] at h
  exact h
theorem sourceRank : (matrixOfRows {size} {"((rows 3).map (fun row => Nat.land row (degreeMask 3)))" if project else "(rows 3)"}).rank = {rank} := by
  rw [← literalRows_eq]
  exact actualRank
end {name}
'''
    sections.append(s)
header='''import Mathlib
import CryptoResearch.Semaev.BooleanParityFiniteCertificate
import CryptoResearch.Semaev.BooleanParitySemanticRankCertificate

/-!
# Degree-three matrix-rank semantics for one Semaev Boolean-parity draw

The fixed n=4, n'=4, s=1, x_R=1 component equations have JSON SHA-256
89ab8e668c510572bbf9307f105b2eaf46858ad900f0b6b4a2fce8803e0ba6eb.
Literal rows are proved equal to the source Boolean-parity routine. Python
proposed elimination matrices; Lean checks their inverse, transformed rows,
and pivots. Mathlib's rank theorem identifies full and projected degree-three
ranks with F₂ row-space dimensions for this one sample. The generic rankOn
theorem, filtration identity, and symbolic S₃ descent remain open.
-/

set_option maxRecDepth 1000000
set_option maxHeartbeats 0
open CryptoResearch.Semaev.BooleanParityFiniteCertificate
open Matrix
open scoped Finset
namespace CryptoResearch.Semaev.BooleanParityDegreeThreeRankCertificate

def matrixOfRows (m : Nat) (rs : List Nat) : Matrix (Fin m) (Fin 256) (ZMod 2) :=
  fun i j => if (rs[i.val]!).testBit j.val then 1 else 0

private def bitVec (a : Nat) (j : Fin 256) : ZMod 2 :=
  if a.testBit j.val then 1 else 0

private theorem bitVec_xor (a b : Nat) (j : Fin 256) :
    bitVec (Nat.xor a b) j = bitVec a j + bitVec b j := by
  change (if (a ^^^ b).testBit j.val then (1 : ZMod 2) else 0) =
    (if a.testBit j.val then 1 else 0) +
    (if b.testBit j.val then 1 else 0)
  rw [Nat.testBit_xor]
  cases h1 : a.testBit j.val <;> cases h2 : b.testBit j.val <;>
    simp_all <;> decide

private def rowXor (cs : Nat) (rs : List Nat) : Nat → Nat
  | 0 => 0
  | n + 1 => Nat.xor (rowXor cs rs n) (if cs.testBit n then rs[n]! else 0)

private theorem bitVec_rowXor (cs : Nat) (rs : List Nat) (n : Nat) (j : Fin 256) :
    bitVec (rowXor cs rs n) j =
      ∑ k ∈ Finset.range n, (if cs.testBit k then bitVec (rs[k]!) j else 0) := by
  induction n with
  | zero => simp [rowXor, bitVec]
  | succ n ih =>
      simp only [rowXor, bitVec_xor, Finset.sum_range_succ]
      rw [ih]
      by_cases h : cs.testBit n <;> simp_all [bitVec]

private def matrixOfCoeffs (m : Nat) (cs : List Nat) : Matrix (Fin m) (Fin m) (ZMod 2) :=
  fun i k => if (cs[i.val]!).testBit k.val then 1 else 0

private theorem matrixMul_eq_rowXor (m : Nat) (cs rs : List Nat) :
    matrixOfCoeffs m cs * matrixOfRows m rs =
      (fun i j => bitVec (rowXor (cs[i.val]!) rs m) j) := by
  funext i j
  change (∑ k : Fin m,
    (if (cs[i.val]!).testBit k.val then (1 : ZMod 2) else 0) *
      bitVec (rs[k.val]!) j) = bitVec (rowXor (cs[i.val]!) rs m) j
  rw [Finset.sum_fin_eq_sum_range, bitVec_rowXor]
  apply Finset.sum_congr rfl
  intro k hk
  have hkm : k < m := Finset.mem_range.mp hk
  by_cases h : (cs[i.val]!).testBit k <;> simp_all
'''
footer='''
theorem sourceRowSpaceDimThree :
    Module.finrank (ZMod 2)
      (Submodule.span (ZMod 2) (Set.range (matrixOfRows 80 (rows 3)).row)) = 53 := by
  rw [← Matrix.rank_eq_finrank_span_row]
  exact three.sourceRank

theorem sourceProjectedRowSpaceDimThree :
    Module.finrank (ZMod 2)
      (Submodule.span (ZMod 2)
        (Set.range (matrixOfRows 80 ((rows 3).map
          (fun row => Nat.land row (degreeMask 3)))).row)) = 41 := by
  rw [← Matrix.rank_eq_finrank_span_row]
  exact threeProjected.sourceRank

/-- For this one sample, the actual degree-three rank increment is one. -/
theorem semanticOneNewFallThree :
    (matrixOfRows 80 (rows 3)).rank -
    (matrixOfRows 80 ((rows 3).map (fun row => Nat.land row (degreeMask 3)))).rank -
    (matrixOfRows 28 (rows 2)).rank = 1 := by
  rw [three.sourceRank, threeProjected.sourceRank]
  have htwo := CryptoResearch.Semaev.BooleanParitySemanticRankCertificate.two.sourceRank
  change (matrixOfRows 28 (rows 2)).rank = 11 at htwo
  rw [htwo]

/-- The executable degree-three rank counts agree with actual matrix ranks here. -/
theorem executableRankMatchesSemanticThree :
    rank (rows 3) = (matrixOfRows 80 (rows 3)).rank ∧
    projectedRank 3 =
      (matrixOfRows 80 ((rows 3).map
        (fun row => Nat.land row (degreeMask 3)))).rank := by
  rw [rank_three, projected_rank_three, three.sourceRank, threeProjected.sourceRank]
  decide

end CryptoResearch.Semaev.BooleanParityDegreeThreeRankCertificate
'''
parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument('--output', type=Path, required=True)
args = parser.parse_args()
args.output.parent.mkdir(parents=True, exist_ok=True)
args.output.write_text(header + '\n'.join(sections) + footer, encoding='utf-8')
print(f'wrote {args.output}: source-bound rows 80/80, ranks 53/41')

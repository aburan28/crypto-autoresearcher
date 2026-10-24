import Mathlib
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

namespace one
private def literalRows : List Nat := [340282366920938463463374607431768277250, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
private theorem literalRows_eq : literalRows = rows 1 := by decide
private def Urows : List Nat := [1, 2, 4, 8, 16, 32, 64, 128, 256, 512, 1024, 2048, 4096, 8192, 16384, 32768, 65536]
private def Vrows : List Nat := [1, 2, 4, 8, 16, 32, 64, 128, 256, 512, 1024, 2048, 4096, 8192, 16384, 32768, 65536]
private def pivots : List (WithTop (Fin 256)) := [((1 : Fin 256) : WithTop (Fin 256)), ⊤, ⊤, ⊤, ⊤, ⊤, ⊤, ⊤, ⊤, ⊤, ⊤, ⊤, ⊤, ⊤, ⊤, ⊤, ⊤]
private def A : Matrix (Fin 17) (Fin 256) (ZMod 2) := matrixOfRows 17 literalRows
private def U : Matrix (Fin 17) (Fin 17) (ZMod 2) :=
  fun i j => if (Urows[i.val]!).testBit j.val then 1 else 0
private def V : Matrix (Fin 17) (Fin 17) (ZMod 2) :=
  fun i j => if (Vrows[i.val]!).testBit j.val then 1 else 0
private def pivot (i : Fin 17) : WithTop (Fin 256) := pivots[i.val]!
private theorem leftInverse : V * U = 1 := by decide
private theorem isPivoted : (U * A).IsPivotedBy pivot := by decide
private theorem pivotCount : #{i : Fin 17 | pivot i ≠ ⊤} = 1 := by decide
theorem actualRank : A.rank = 1 := by
  have hdet : IsUnit U.det := Matrix.isUnit_det_of_left_inverse leftInverse
  have h := isPivoted.rank_eq
  rw [Matrix.rank_mul_eq_right_of_isUnit_det U A hdet, pivotCount] at h
  exact h
theorem sourceRank : (matrixOfRows 17 (rows 1)).rank = 1 := by
  rw [← literalRows_eq]
  exact actualRank
end one


namespace two
private def literalRows : List Nat := [89494262500206815891236456637218953560327, 5784800237655953883894882714406237634816, 87452568298681185110400868759247557820694, 340282366920938463463374607431768277250, 680564733841876926926749214863536554498, 1361129467683753853853498429727073109000, 5444517870735015415413993718908292436000, 87112285931760246646623899502532678910720, 22300745198530623141535718272648361522954240, 1461501637330902918203684832716283302239010816000, 6277101735386680763835789423207667629787435030110273536000, 22388878331563146203572732295973189472747520, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
private theorem literalRows_eq : literalRows = rows 2 := by decide
private def Urows : List Nat := [1, 4, 12, 32, 64, 2, 26, 152, 512, 1024, 408, 2456, 4096, 8192, 16384, 32768, 65536, 131072, 262144, 524288, 1048576, 2097152, 4194304, 8388608, 16777216, 33554432, 67108864, 134217728]
private def Vrows : List Nat := [1, 32, 2, 6, 102, 8, 16, 224, 1152, 256, 512, 3072, 4096, 8192, 16384, 32768, 65536, 131072, 262144, 524288, 1048576, 2097152, 4194304, 8388608, 16777216, 33554432, 67108864, 134217728]
private def pivots : List (WithTop (Fin 256)) := [((0 : Fin 256) : WithTop (Fin 256)), ((1 : Fin 256) : WithTop (Fin 256)), ((2 : Fin 256) : WithTop (Fin 256)), ((3 : Fin 256) : WithTop (Fin 256)), ((5 : Fin 256) : WithTop (Fin 256)), ((8 : Fin 256) : WithTop (Fin 256)), ((9 : Fin 256) : WithTop (Fin 256)), ((16 : Fin 256) : WithTop (Fin 256)), ((33 : Fin 256) : WithTop (Fin 256)), ((65 : Fin 256) : WithTop (Fin 256)), ((128 : Fin 256) : WithTop (Fin 256)), ⊤, ⊤, ⊤, ⊤, ⊤, ⊤, ⊤, ⊤, ⊤, ⊤, ⊤, ⊤, ⊤, ⊤, ⊤, ⊤, ⊤]
private def A : Matrix (Fin 28) (Fin 256) (ZMod 2) := matrixOfRows 28 literalRows
private def U : Matrix (Fin 28) (Fin 28) (ZMod 2) :=
  fun i j => if (Urows[i.val]!).testBit j.val then 1 else 0
private def V : Matrix (Fin 28) (Fin 28) (ZMod 2) :=
  fun i j => if (Vrows[i.val]!).testBit j.val then 1 else 0
private def pivot (i : Fin 28) : WithTop (Fin 256) := pivots[i.val]!
private theorem leftInverse : V * U = 1 := by decide
private theorem isPivoted : (U * A).IsPivotedBy pivot := by decide
private theorem pivotCount : #{i : Fin 28 | pivot i ≠ ⊤} = 11 := by decide
theorem actualRank : A.rank = 11 := by
  have hdet : IsUnit U.det := Matrix.isUnit_det_of_left_inverse leftInverse
  have h := isPivoted.rank_eq
  rw [Matrix.rank_mul_eq_right_of_isUnit_det U A hdet, pivotCount] at h
  exact h
theorem sourceRank : (matrixOfRows 28 (rows 2)).rank = 11 := by
  rw [← literalRows_eq]
  exact actualRank
end two


namespace twoProjected
private def literalRows : List Nat := [89153980133285877427773082029782890315776, 5444517870735015420431508106974469423104, 87112285931760246646919047407737785024512, 0, 680564733841876926926749214863536554496, 1361129467683753853853498429727073109000, 5444517870735015415413993718908292436000, 87112285931760246646623899502532678910464, 22300745198530623141535718272648361522888704, 1461501637330902918203684832716283302239010816000, 6277101735386680763835789423207667629787435030110273536000, 22388538049196225265109268921365757704536064, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
private theorem literalRows_eq : literalRows = ((rows 2).map (fun row => Nat.land row (degreeMask 2))) := by decide
private def Urows : List Nat := [32, 64, 16, 1, 4, 3, 512, 145, 1024, 400, 8, 2448, 4096, 8192, 16384, 32768, 65536, 131072, 262144, 524288, 1048576, 2097152, 4194304, 8388608, 16777216, 33554432, 67108864, 134217728]
private def Vrows : List Nat := [8, 40, 16, 1024, 4, 1, 2, 140, 648, 64, 256, 2560, 4096, 8192, 16384, 32768, 65536, 131072, 262144, 524288, 1048576, 2097152, 4194304, 8388608, 16777216, 33554432, 67108864, 134217728]
private def pivots : List (WithTop (Fin 256)) := [((3 : Fin 256) : WithTop (Fin 256)), ((5 : Fin 256) : WithTop (Fin 256)), ((9 : Fin 256) : WithTop (Fin 256)), ((17 : Fin 256) : WithTop (Fin 256)), ((18 : Fin 256) : WithTop (Fin 256)), ((24 : Fin 256) : WithTop (Fin 256)), ((33 : Fin 256) : WithTop (Fin 256)), ((34 : Fin 256) : WithTop (Fin 256)), ((65 : Fin 256) : WithTop (Fin 256)), ((129 : Fin 256) : WithTop (Fin 256)), ⊤, ⊤, ⊤, ⊤, ⊤, ⊤, ⊤, ⊤, ⊤, ⊤, ⊤, ⊤, ⊤, ⊤, ⊤, ⊤, ⊤, ⊤]
private def A : Matrix (Fin 28) (Fin 256) (ZMod 2) := matrixOfRows 28 literalRows
private def U : Matrix (Fin 28) (Fin 28) (ZMod 2) :=
  fun i j => if (Urows[i.val]!).testBit j.val then 1 else 0
private def V : Matrix (Fin 28) (Fin 28) (ZMod 2) :=
  fun i j => if (Vrows[i.val]!).testBit j.val then 1 else 0
private def pivot (i : Fin 28) : WithTop (Fin 256) := pivots[i.val]!
private theorem leftInverse : V * U = 1 := by decide
private theorem isPivoted : (U * A).IsPivotedBy pivot := by decide
private theorem pivotCount : #{i : Fin 28 | pivot i ≠ ⊤} = 10 := by decide
theorem actualRank : A.rank = 10 := by
  have hdet : IsUnit U.det := Matrix.isUnit_det_of_left_inverse leftInverse
  have h := isPivoted.rank_eq
  rw [Matrix.rank_mul_eq_right_of_isUnit_det U A hdet, pivotCount] at h
  exact h
theorem sourceRank : (matrixOfRows 28 ((rows 2).map (fun row => Nat.land row (degreeMask 2)))).rank = 10 := by
  rw [← literalRows_eq]
  exact actualRank
end twoProjected

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

import Mathlib
import CryptoResearch.Semaev.BooleanParityDegreeThreeRankCertificate

/-!
# Finite Semaev filtration identity for one Boolean draw

The frozen n=4, n'=4, s=1, x_R=1 draw has equation hash
89ab8e668c510572bbf9307f105b2eaf46858ad900f0b6b4a2fce8803e0ba6eb.
This module proves a generic row-space projection rank-nullity identity,
then checks the source-generated finite degree-two and degree-three rows.
It identifies the degree-three projection kernel with the degree-at-most-two
subspace, proves its dimension is 12, and proves a new vector exists outside
the degree-two row space. The theorem is finite; it does not generalize to
other Semaev systems or imply an ECDLP cost bound.
-/

namespace CryptoResearch.Semaev.BooleanParityFiltrationCertificate

open CryptoResearch.Semaev.BooleanParityFiniteCertificate
open CryptoResearch.Semaev.BooleanParityDegreeThreeRankCertificate

universe u v w
variable {K : Type u} {V : Type v} {W : Type w}
variable [Field K] [AddCommGroup V] [Module K V] [AddCommGroup W] [Module K W]

private theorem submodule_intersection_finrank_add_image_finrank
    (S : Submodule K V) [FiniteDimensional K S] (f : V →ₗ[K] W) :
    Module.finrank K ↥(S ⊓ LinearMap.ker f) + Module.finrank K (S.map f) =
      Module.finrank K S := by
  have h := (f.domRestrict S).finrank_range_add_finrank_ker
  rw [LinearMap.range_domRestrict] at h
  have hker : Module.finrank K ↥(S ⊓ LinearMap.ker f) =
      Module.finrank K (LinearMap.ker (f.domRestrict S)) := by
    rw [← Submodule.map_comap_subtype S (LinearMap.ker f),
      ← LinearMap.ker_domRestrict, Submodule.finrank_map_subtype_eq]
  omega

variable {m n : Type*} [Fintype m] [Fintype n]

private theorem row_space_projection_rank_nullity
    (A B : Matrix m n K) (f : (n → K) →ₗ[K] (n → K))
    (hrow : ∀ i, f (A.row i) = B.row i) :
    Module.finrank K ↥(Submodule.span K (Set.range A.row) ⊓ LinearMap.ker f) =
      A.rank - B.rank := by
  let S := Submodule.span K (Set.range A.row)
  have himage : S.map f = Submodule.span K (Set.range B.row) := by
    change (Submodule.span K (Set.range A.row)).map f = _
    rw [Submodule.map_span]
    congr 1
    ext x
    simp [Set.mem_image, Set.mem_range, hrow]
  have h := submodule_intersection_finrank_add_image_finrank S f
  rw [himage, ← Matrix.rank_eq_finrank_span_row A,
    ← Matrix.rank_eq_finrank_span_row B] at h
  change Module.finrank K ↥(S ⊓ LinearMap.ker f) = A.rank - B.rank
  omega

namespace FiniteSemaev

def maskProjection (mask : Nat) :
    (Fin 256 → ZMod 2) →ₗ[ZMod 2] (Fin 256 → ZMod 2) where
  toFun v j := if mask.testBit j.val then v j else 0
  map_add' := by
    intro v w
    funext j
    by_cases h : mask.testBit j.val <;> simp [h]
  map_smul' := by
    intro a v
    funext j
    by_cases h : mask.testBit j.val <;> simp [h]

def fullRows3 : Matrix (Fin 80) (Fin 256) (ZMod 2) := matrixOfRows 80 (rows 3)
def projectedRows3 : Matrix (Fin 80) (Fin 256) (ZMod 2) :=
  matrixOfRows 80 ((rows 3).map (fun row => Nat.land row (degreeMask 3)))

private theorem projectedRow_eq (i : Fin 80) :
    maskProjection (degreeMask 3) (fullRows3.row i) = projectedRows3.row i := by
  funext j
  dsimp [maskProjection, fullRows3, projectedRows3, matrixOfRows]
  have hlen : (rows 3).length = 80 := by decide
  have hi : i.val < (rows 3).length := by simp [hlen]
  have hm : (List.map (fun row => row &&& degreeMask 3) (rows 3))[i.val]! =
      ((rows 3)[i.val]!) &&& degreeMask 3 := by
    simp [getElem!_pos, hi]
  rw [hm, Nat.testBit_and]
  by_cases h : (degreeMask 3).testBit j.val <;> simp [h]

theorem projection_kernel_dim_three :
    Module.finrank (ZMod 2) ↥(Submodule.span (ZMod 2) (Set.range fullRows3.row) ⊓
      LinearMap.ker (maskProjection (degreeMask 3))) = 12 := by
  have h := row_space_projection_rank_nullity fullRows3 projectedRows3
    (maskProjection (degreeMask 3)) projectedRow_eq
  change _ = 12
  rw [show fullRows3.rank = 53 from three.sourceRank,
      show projectedRows3.rank = 41 from threeProjected.sourceRank] at h
  omega
end FiniteSemaev

private theorem rows3_high_zero :
    ∀ row ∈ rows 3, Nat.land row (upperMask 3) = 0 := by decide

namespace FiniteSemaev
private theorem fullRows3_killed_above_three (i : Fin 80) :
    maskProjection (upperMask 3) (fullRows3.row i) = 0 := by
  have hlen : (rows 3).length = 80 := by decide
  have hi : i.val < (rows 3).length := by simp [hlen]
  have hmem : (rows 3)[i.val]! ∈ rows 3 := by
    rw [getElem!_pos (rows 3) i.val hi]
    exact List.getElem_mem hi
  have hz := rows3_high_zero ((rows 3)[i.val]!) hmem
  funext j
  have hbit := congrArg (fun n : Nat => n.testBit j.val) hz
  rw [Nat.land_eq, Nat.testBit_and, Nat.zero_testBit] at hbit
  change (if (upperMask 3).testBit j.val then
    (if ((rows 3)[i.val]!).testBit j.val then (1 : ZMod 2) else 0) else 0) = 0
  by_cases hu : (upperMask 3).testBit j.val <;> simp_all

private theorem rowSpace3_killed_above_three :
    Submodule.span (ZMod 2) (Set.range fullRows3.row) ≤
      LinearMap.ker (maskProjection (upperMask 3)) := by
  apply Submodule.span_le.mpr
  rintro v ⟨i, rfl⟩
  exact fullRows3_killed_above_three i
end FiniteSemaev

namespace FiniteSemaev
private theorem upperMask_partition :
    upperMask 2 = (degreeMask 3 ||| upperMask 3) := by decide

private theorem upperProjection_iff_degreeProjection_zero
    (v : Fin 256 → ZMod 2)
    (hhigh : maskProjection (upperMask 3) v = 0) :
    maskProjection (upperMask 2) v = 0 ↔
      maskProjection (degreeMask 3) v = 0 := by
  constructor
  · intro hu
    funext j
    have hju := congrFun hu j
    change (if (degreeMask 3).testBit j.val then v j else 0) = 0
    change (if (upperMask 2).testBit j.val then v j else 0) = 0 at hju
    rw [upperMask_partition, Nat.testBit_or] at hju
    by_cases hd : (degreeMask 3).testBit j.val <;> simp_all
  · intro hd0
    funext j
    have hjd := congrFun hd0 j
    have hjh := congrFun hhigh j
    change (if (upperMask 2).testBit j.val then v j else 0) = 0
    change (if (degreeMask 3).testBit j.val then v j else 0) = 0 at hjd
    change (if (upperMask 3).testBit j.val then v j else 0) = 0 at hjh
    rw [upperMask_partition, Nat.testBit_or]
    by_cases hd : (degreeMask 3).testBit j.val <;>
      by_cases hh : (upperMask 3).testBit j.val <;> simp_all
end FiniteSemaev

namespace FiniteSemaev
/-- Degree-at-most-two vectors inside the 256-coordinate Boolean monomial space. -/
def lowDegreeAtMostTwo : Submodule (ZMod 2) (Fin 256 → ZMod 2) :=
  LinearMap.ker (maskProjection (upperMask 2))

private theorem degreeThreeKernel_eq_lowDegreeIntersection :
    (Submodule.span (ZMod 2) (Set.range fullRows3.row) ⊓
      LinearMap.ker (maskProjection (degreeMask 3))) =
    (Submodule.span (ZMod 2) (Set.range fullRows3.row) ⊓ lowDegreeAtMostTwo) := by
  apply le_antisymm
  · rintro v ⟨hvS, hvD⟩
    have hhigh := rowSpace3_killed_above_three hvS
    exact ⟨hvS, (upperProjection_iff_degreeProjection_zero v hhigh).mpr hvD⟩
  · rintro v ⟨hvS, hvLow⟩
    have hhigh := rowSpace3_killed_above_three hvS
    exact ⟨hvS, (upperProjection_iff_degreeProjection_zero v hhigh).mp hvLow⟩

theorem lowDegreeIntersectionDimThree :
    Module.finrank (ZMod 2) ↥(Submodule.span (ZMod 2) (Set.range fullRows3.row) ⊓
      lowDegreeAtMostTwo) = 12 := by
  rw [← degreeThreeKernel_eq_lowDegreeIntersection]
  exact projection_kernel_dim_three
end FiniteSemaev

namespace FiniteSemaev
def fullRows2 : Matrix (Fin 28) (Fin 256) (ZMod 2) := matrixOfRows 28 (rows 2)

private theorem rows2_subset_rows3 : ∀ row ∈ rows 2, row ∈ rows 3 := by decide
private theorem rows2_high_zero :
    ∀ row ∈ rows 2, Nat.land row (upperMask 2) = 0 := by decide

private theorem rowSpace2_le_rowSpace3 :
    Submodule.span (ZMod 2) (Set.range fullRows2.row) ≤
      Submodule.span (ZMod 2) (Set.range fullRows3.row) := by
  apply Submodule.span_le.mpr
  rintro v ⟨i, rfl⟩
  have hlen2 : (rows 2).length = 28 := by decide
  have hi : i.val < (rows 2).length := by simp [hlen2]
  have hmem2 : (rows 2)[i.val]! ∈ rows 2 := by
    rw [getElem!_pos (rows 2) i.val hi]
    exact List.getElem_mem hi
  have hmem3 := rows2_subset_rows3 ((rows 2)[i.val]!) hmem2
  obtain ⟨j, hj, heq⟩ := List.mem_iff_getElem.mp hmem3
  have hlen3 : (rows 3).length = 80 := by decide
  have hj80 : j < 80 := by simpa [hlen3] using hj
  have hrow : fullRows2.row i = fullRows3.row ⟨j, hj80⟩ := by
    funext k
    change (if ((rows 2)[i.val]!).testBit k.val then (1 : ZMod 2) else 0) =
      (if ((rows 3)[j]!).testBit k.val then 1 else 0)
    rw [getElem!_pos (rows 3) j hj, heq]
  exact Submodule.subset_span ⟨⟨j, hj80⟩, hrow.symm⟩

private theorem fullRows2_killed_above_two (i : Fin 28) :
    maskProjection (upperMask 2) (fullRows2.row i) = 0 := by
  have hlen : (rows 2).length = 28 := by decide
  have hi : i.val < (rows 2).length := by simp [hlen]
  have hmem : (rows 2)[i.val]! ∈ rows 2 := by
    rw [getElem!_pos (rows 2) i.val hi]
    exact List.getElem_mem hi
  have hz := rows2_high_zero ((rows 2)[i.val]!) hmem
  funext j
  have hbit := congrArg (fun n : Nat => n.testBit j.val) hz
  rw [Nat.land_eq, Nat.testBit_and, Nat.zero_testBit] at hbit
  change (if (upperMask 2).testBit j.val then
    (if ((rows 2)[i.val]!).testBit j.val then (1 : ZMod 2) else 0) else 0) = 0
  by_cases hu : (upperMask 2).testBit j.val <;> simp_all

private theorem rowSpace2_le_lowDegree :
    Submodule.span (ZMod 2) (Set.range fullRows2.row) ≤ lowDegreeAtMostTwo := by
  apply Submodule.span_le.mpr
  rintro v ⟨i, rfl⟩
  exact fullRows2_killed_above_two i

private theorem rowSpace2_le_lowDegreeIntersection :
    Submodule.span (ZMod 2) (Set.range fullRows2.row) ≤
      (Submodule.span (ZMod 2) (Set.range fullRows3.row) ⊓ lowDegreeAtMostTwo) := by
  exact le_inf rowSpace2_le_rowSpace3 rowSpace2_le_lowDegree

theorem oneNewFallDimensionThree :
    Module.finrank (ZMod 2) ↥(Submodule.span (ZMod 2) (Set.range fullRows3.row) ⊓
      lowDegreeAtMostTwo) -
    Module.finrank (ZMod 2) ↥(Submodule.span (ZMod 2) (Set.range fullRows2.row)) = 1 := by
  rw [lowDegreeIntersectionDimThree]
  have htwo := CryptoResearch.Semaev.BooleanParitySemanticRankCertificate.sourceRowSpaceDimTwo
  change Module.finrank (ZMod 2) ↥(Submodule.span (ZMod 2) (Set.range fullRows2.row)) = 11 at htwo
  rw [htwo]
end FiniteSemaev

namespace FiniteSemaev
def rowSpaceTwo : Submodule (ZMod 2) (Fin 256 → ZMod 2) :=
  Submodule.span (ZMod 2) (Set.range fullRows2.row)
abbrev lowDegreePartThree : Submodule (ZMod 2) (Fin 256 → ZMod 2) :=
  Submodule.span (ZMod 2) (Set.range fullRows3.row) ⊓ lowDegreeAtMostTwo

theorem existsNewLowDegreeVector :
    ∃ v : Fin 256 → ZMod 2, v ∈ lowDegreePartThree ∧ v ∉ rowSpaceTwo := by
  by_contra h
  push Not at h
  have hle : lowDegreePartThree ≤ rowSpaceTwo := by
    intro v hv
    exact h v hv
  have heq : lowDegreePartThree = rowSpaceTwo :=
    le_antisymm hle rowSpace2_le_lowDegreeIntersection
  have hlow : Module.finrank (ZMod 2) lowDegreePartThree = 12 :=
    lowDegreeIntersectionDimThree
  have htwo := CryptoResearch.Semaev.BooleanParitySemanticRankCertificate.sourceRowSpaceDimTwo
  change Module.finrank (ZMod 2) rowSpaceTwo = 11 at htwo
  rw [heq] at hlow
  omega
end FiniteSemaev

end CryptoResearch.Semaev.BooleanParityFiltrationCertificate

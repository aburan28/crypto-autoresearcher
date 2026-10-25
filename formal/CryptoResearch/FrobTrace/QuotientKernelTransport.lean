import CryptoResearch.FrobTrace.QuotientFrobeniusMap
import CryptoResearch.FrobTrace.QuotientMatrixKernels
import CryptoResearch.FrobTrace.FactorKernel
import Mathlib.Tactic

/-!
The frozen C5 factor-kernel and trace-dimension controls transported from
exact quotient-basis matrices to the actual q-power endomorphisms of the
three archived polynomial quotient algebras. This does not prove historical
Sage refinement, original source custody, or C8.
-/

open Polynomial Module
namespace CryptoResearch.FrobTrace.QuotientKernelTransport
open QuotientMatrices QuotientFrobeniusMap QuotientMatrixKernels

local instance : Fact (Nat.Prime 11) := ⟨by decide⟩

private noncomputable def e11 : Fin modulus11.natDegree ≃ Fin 5 := finCongr modulus11_natDegree_five

private noncomputable def E11 :
    Module.End (ZMod 11) (AdjoinRoot modulus11) ≃ₐ[ZMod 11]
      Matrix (Fin 5) (Fin 5) (ZMod 11) :=
  (LinearMap.toMatrixAlgEquiv basis11).trans
    (Matrix.reindexAlgEquiv (ZMod 11) (ZMod 11) e11)

private theorem E11_F : E11 frobeniusEnd11 = frobeniusMatrix11 := by
  ext i j
  change ((LinearMap.toMatrix basis11 basis11 frobeniusEnd11).reindex e11 e11) i j = _
  simpa only [Matrix.reindex_apply, Matrix.submatrix_apply, e11, finCongr_symm_apply]
    using full_frobenius_matrix11 i j

private theorem E11_trace :
    E11 (CryptoResearch.FrobTrace.trace5 frobeniusEnd11) =
      1 + frobeniusMatrix11 + frobeniusMatrix11 ^ 2 +
      frobeniusMatrix11 ^ 3 + frobeniusMatrix11 ^ 4 := by
  simp only [CryptoResearch.FrobTrace.trace5, map_add, map_pow, map_one, E11_F]

private theorem q11_trace_range_finrank_one :
    Module.finrank (ZMod 11)
      (CryptoResearch.FrobTrace.trace5 frobeniusEnd11).range = 1 := by
  let A := LinearMap.toMatrix basis11 basis11
    (CryptoResearch.FrobTrace.trace5 frobeniusEnd11)
  have hmatrix : A.reindex e11 e11 =
      1 + frobeniusMatrix11 + frobeniusMatrix11 ^ 2 +
      frobeniusMatrix11 ^ 3 + frobeniusMatrix11 ^ 4 := by
    have h := E11_trace
    change A.reindex e11 e11 = _ at h
    exact h
  have hrank : A.rank = 1 := by
    rw [← Matrix.rank_reindex e11 e11 A, hmatrix]
    exact q11_trace_matrix_rank_one
  have hR := Matrix.rank_eq_finrank_range_toLin A basis11 basis11
  rw [Matrix.toLin_toMatrix] at hR
  exact hR.symm.trans hrank

theorem q11_quotient_trace_kernel_dim_four : Module.finrank (ZMod 11)
    (CryptoResearch.FrobTrace.trace5 frobeniusEnd11).ker = 4 := by
  haveI : FiniteDimensional (ZMod 11) (AdjoinRoot modulus11) :=
    basis11.finiteDimensional_of_finite
  have h := (CryptoResearch.FrobTrace.trace5 frobeniusEnd11).finrank_range_add_finrank_ker
  rw [q11_trace_range_finrank_one, Module.finrank_eq_card_basis basis11] at h
  have hcard : Fintype.card (Fin modulus11.natDegree) = 5 := by
    simp [modulus11_natDegree_five]
  rw [hcard] at h
  omega

theorem q11_quotient_frobenius_fifth_power : frobeniusEnd11 ^ 5 = 1 := by
  apply E11.injective
  rw [map_pow, map_one, E11_F]
  exact q11_matrix_fifth_power

theorem q11_quotient_fixed_kernel_dim_one :
    Module.finrank (ZMod 11) (frobeniusEnd11 - 1).ker = 1 := by
  have h5 : (5 : ZMod 11) ≠ 0 := by decide
  have hrange : Module.finrank (ZMod 11) (frobeniusEnd11 - 1).range = 4 := by
    rw [← CryptoResearch.FrobTrace.ker_trace5_eq_range_sub
      frobeniusEnd11 q11_quotient_frobenius_fifth_power h5]
    exact q11_quotient_trace_kernel_dim_four
  haveI : FiniteDimensional (ZMod 11) (AdjoinRoot modulus11) :=
    basis11.finiteDimensional_of_finite
  have h := (frobeniusEnd11 - 1).finrank_range_add_finrank_ker
  rw [hrange, Module.finrank_eq_card_basis basis11] at h
  simp [modulus11_natDegree_five] at h
  omega

theorem q11_quotient_fixed_trace_disjoint :
    Disjoint (frobeniusEnd11 - 1).ker
      (CryptoResearch.FrobTrace.trace5 frobeniusEnd11).ker := by
  apply disjoint_iff_inf_le.mpr
  intro x hx
  have hfixed : frobeniusEnd11 x = x := by
    have hzero : (frobeniusEnd11 - 1) x = 0 := hx.1
    exact sub_eq_zero.mp (by simpa using hzero)
  have hzero := CryptoResearch.FrobTrace.fixed_trace5_eq_zero frobeniusEnd11
    (by decide) x hfixed hx.2
  simpa using hzero

local instance : Fact (Nat.Prime 13) := ⟨by decide⟩

private noncomputable def e13 : Fin modulus13.natDegree ≃ Fin 5 := finCongr modulus13_natDegree_five

private noncomputable def E13 :
    Module.End (ZMod 13) (AdjoinRoot modulus13) ≃ₐ[ZMod 13]
      Matrix (Fin 5) (Fin 5) (ZMod 13) :=
  (LinearMap.toMatrixAlgEquiv basis13).trans
    (Matrix.reindexAlgEquiv (ZMod 13) (ZMod 13) e13)

private theorem E13_F : E13 frobeniusEnd13 = frobeniusMatrix13 := by
  ext i j
  change ((LinearMap.toMatrix basis13 basis13 frobeniusEnd13).reindex e13 e13) i j = _
  simpa only [Matrix.reindex_apply, Matrix.submatrix_apply, e13, finCongr_symm_apply]
    using full_frobenius_matrix13 i j

private theorem E13_trace :
    E13 (CryptoResearch.FrobTrace.trace5 frobeniusEnd13) =
      1 + frobeniusMatrix13 + frobeniusMatrix13 ^ 2 +
      frobeniusMatrix13 ^ 3 + frobeniusMatrix13 ^ 4 := by
  simp only [CryptoResearch.FrobTrace.trace5, map_add, map_pow, map_one, E13_F]

private theorem q13_trace_range_finrank_one :
    Module.finrank (ZMod 13)
      (CryptoResearch.FrobTrace.trace5 frobeniusEnd13).range = 1 := by
  let A := LinearMap.toMatrix basis13 basis13
    (CryptoResearch.FrobTrace.trace5 frobeniusEnd13)
  have hmatrix : A.reindex e13 e13 =
      1 + frobeniusMatrix13 + frobeniusMatrix13 ^ 2 +
      frobeniusMatrix13 ^ 3 + frobeniusMatrix13 ^ 4 := by
    have h := E13_trace
    change A.reindex e13 e13 = _ at h
    exact h
  have hrank : A.rank = 1 := by
    rw [← Matrix.rank_reindex e13 e13 A, hmatrix]
    exact q13_trace_matrix_rank_one
  have hR := Matrix.rank_eq_finrank_range_toLin A basis13 basis13
  rw [Matrix.toLin_toMatrix] at hR
  exact hR.symm.trans hrank

theorem q13_quotient_trace_kernel_dim_four : Module.finrank (ZMod 13)
    (CryptoResearch.FrobTrace.trace5 frobeniusEnd13).ker = 4 := by
  haveI : FiniteDimensional (ZMod 13) (AdjoinRoot modulus13) :=
    basis13.finiteDimensional_of_finite
  have h := (CryptoResearch.FrobTrace.trace5 frobeniusEnd13).finrank_range_add_finrank_ker
  rw [q13_trace_range_finrank_one, Module.finrank_eq_card_basis basis13] at h
  have hcard : Fintype.card (Fin modulus13.natDegree) = 5 := by
    simp [modulus13_natDegree_five]
  rw [hcard] at h
  omega

theorem q13_quotient_frobenius_fifth_power : frobeniusEnd13 ^ 5 = 1 := by
  apply E13.injective
  rw [map_pow, map_one, E13_F]
  exact q13_matrix_fifth_power

theorem q13_quotient_fixed_kernel_dim_one :
    Module.finrank (ZMod 13) (frobeniusEnd13 - 1).ker = 1 := by
  have h5 : (5 : ZMod 13) ≠ 0 := by decide
  have hrange : Module.finrank (ZMod 13) (frobeniusEnd13 - 1).range = 4 := by
    rw [← CryptoResearch.FrobTrace.ker_trace5_eq_range_sub
      frobeniusEnd13 q13_quotient_frobenius_fifth_power h5]
    exact q13_quotient_trace_kernel_dim_four
  haveI : FiniteDimensional (ZMod 13) (AdjoinRoot modulus13) :=
    basis13.finiteDimensional_of_finite
  have h := (frobeniusEnd13 - 1).finrank_range_add_finrank_ker
  rw [hrange, Module.finrank_eq_card_basis basis13] at h
  simp [modulus13_natDegree_five] at h
  omega

theorem q13_quotient_fixed_trace_disjoint :
    Disjoint (frobeniusEnd13 - 1).ker
      (CryptoResearch.FrobTrace.trace5 frobeniusEnd13).ker := by
  apply disjoint_iff_inf_le.mpr
  intro x hx
  have hfixed : frobeniusEnd13 x = x := by
    have hzero : (frobeniusEnd13 - 1) x = 0 := hx.1
    exact sub_eq_zero.mp (by simpa using hzero)
  have hzero := CryptoResearch.FrobTrace.fixed_trace5_eq_zero frobeniusEnd13
    (by decide) x hfixed hx.2
  simpa using hzero

local instance : Fact (Nat.Prime 19) := ⟨by decide⟩

private noncomputable def e19 : Fin modulus19.natDegree ≃ Fin 5 := finCongr modulus19_natDegree_five

private noncomputable def E19 :
    Module.End (ZMod 19) (AdjoinRoot modulus19) ≃ₐ[ZMod 19]
      Matrix (Fin 5) (Fin 5) (ZMod 19) :=
  (LinearMap.toMatrixAlgEquiv basis19).trans
    (Matrix.reindexAlgEquiv (ZMod 19) (ZMod 19) e19)

private theorem E19_F : E19 frobeniusEnd19 = frobeniusMatrix19 := by
  ext i j
  change ((LinearMap.toMatrix basis19 basis19 frobeniusEnd19).reindex e19 e19) i j = _
  simpa only [Matrix.reindex_apply, Matrix.submatrix_apply, e19, finCongr_symm_apply]
    using full_frobenius_matrix19 i j

private theorem E19_trace :
    E19 (CryptoResearch.FrobTrace.trace5 frobeniusEnd19) =
      1 + frobeniusMatrix19 + frobeniusMatrix19 ^ 2 +
      frobeniusMatrix19 ^ 3 + frobeniusMatrix19 ^ 4 := by
  simp only [CryptoResearch.FrobTrace.trace5, map_add, map_pow, map_one, E19_F]

private theorem q19_trace_range_finrank_one :
    Module.finrank (ZMod 19)
      (CryptoResearch.FrobTrace.trace5 frobeniusEnd19).range = 1 := by
  let A := LinearMap.toMatrix basis19 basis19
    (CryptoResearch.FrobTrace.trace5 frobeniusEnd19)
  have hmatrix : A.reindex e19 e19 =
      1 + frobeniusMatrix19 + frobeniusMatrix19 ^ 2 +
      frobeniusMatrix19 ^ 3 + frobeniusMatrix19 ^ 4 := by
    have h := E19_trace
    change A.reindex e19 e19 = _ at h
    exact h
  have hrank : A.rank = 1 := by
    rw [← Matrix.rank_reindex e19 e19 A, hmatrix]
    exact q19_trace_matrix_rank_one
  have hR := Matrix.rank_eq_finrank_range_toLin A basis19 basis19
  rw [Matrix.toLin_toMatrix] at hR
  exact hR.symm.trans hrank

theorem q19_quotient_trace_kernel_dim_four : Module.finrank (ZMod 19)
    (CryptoResearch.FrobTrace.trace5 frobeniusEnd19).ker = 4 := by
  haveI : FiniteDimensional (ZMod 19) (AdjoinRoot modulus19) :=
    basis19.finiteDimensional_of_finite
  have h := (CryptoResearch.FrobTrace.trace5 frobeniusEnd19).finrank_range_add_finrank_ker
  rw [q19_trace_range_finrank_one, Module.finrank_eq_card_basis basis19] at h
  have hcard : Fintype.card (Fin modulus19.natDegree) = 5 := by
    simp [modulus19_natDegree_five]
  rw [hcard] at h
  omega
theorem q19_quotient_frobenius_fifth_power : frobeniusEnd19 ^ 5 = 1 := by
  apply E19.injective
  rw [map_pow, map_one, E19_F]
  exact q19_matrix_fifth_power

theorem q19_quotient_fixed_kernel_dim_one :
    Module.finrank (ZMod 19) (frobeniusEnd19 - 1).ker = 1 := by
  have h5 : (5 : ZMod 19) ≠ 0 := by decide
  have hrange : Module.finrank (ZMod 19) (frobeniusEnd19 - 1).range = 4 := by
    rw [← CryptoResearch.FrobTrace.ker_trace5_eq_range_sub
      frobeniusEnd19 q19_quotient_frobenius_fifth_power h5]
    exact q19_quotient_trace_kernel_dim_four
  haveI : FiniteDimensional (ZMod 19) (AdjoinRoot modulus19) :=
    basis19.finiteDimensional_of_finite
  have h := (frobeniusEnd19 - 1).finrank_range_add_finrank_ker
  rw [hrange, Module.finrank_eq_card_basis basis19] at h
  simp [modulus19_natDegree_five] at h
  omega

theorem q19_quotient_fixed_trace_disjoint :
    Disjoint (frobeniusEnd19 - 1).ker
      (CryptoResearch.FrobTrace.trace5 frobeniusEnd19).ker := by
  apply disjoint_iff_inf_le.mpr
  intro x hx
  have hfixed : frobeniusEnd19 x = x := by
    have hzero : (frobeniusEnd19 - 1) x = 0 := hx.1
    exact sub_eq_zero.mp (by simpa using hzero)
  have hzero := CryptoResearch.FrobTrace.fixed_trace5_eq_zero frobeniusEnd19
    (by decide) x hfixed hx.2
  simpa using hzero

def q11QuotientFactorClaim : Prop :=
    let F := frobeniusEnd11
    Disjoint (aeval F (X + 2 : (ZMod 11)[X])).ker
      (aeval F (X + 6 : (ZMod 11)[X])).ker ∧
    Disjoint ((aeval F (X + 2 : (ZMod 11)[X])).ker ⊔
      (aeval F (X + 6 : (ZMod 11)[X])).ker)
      (aeval F (X + 7 : (ZMod 11)[X])).ker ∧
    Disjoint (((aeval F (X + 2 : (ZMod 11)[X])).ker ⊔
      (aeval F (X + 6 : (ZMod 11)[X])).ker) ⊔
      (aeval F (X + 7 : (ZMod 11)[X])).ker)
      (aeval F (X + 8 : (ZMod 11)[X])).ker ∧
    ((((aeval F (X + 2 : (ZMod 11)[X])).ker ⊔
      (aeval F (X + 6 : (ZMod 11)[X])).ker) ⊔
      (aeval F (X + 7 : (ZMod 11)[X])).ker) ⊔
      (aeval F (X + 8 : (ZMod 11)[X])).ker) =
      (CryptoResearch.FrobTrace.trace5 F).ker

def q13QuotientFactorClaim : Prop :=
    let F := frobeniusEnd13
    (aeval F (X^4 + X^3 + X^2 + X + 1 : (ZMod 13)[X])).ker =
      (CryptoResearch.FrobTrace.trace5 F).ker

def q19QuotientFactorClaim : Prop :=
    let F := frobeniusEnd19
    Disjoint (aeval F (X^2 + 5 * X + 1 : (ZMod 19)[X])).ker
      (aeval F (X^2 + 15 * X + 1 : (ZMod 19)[X])).ker ∧
    (aeval F (X^2 + 5 * X + 1 : (ZMod 19)[X])).ker ⊔
      (aeval F (X^2 + 15 * X + 1 : (ZMod 19)[X])).ker =
      (CryptoResearch.FrobTrace.trace5 F).ker

/-- The q=11 quotient Frobenius has the four direct factor kernels. -/
theorem q11_quotient_factor_kernels : q11QuotientFactorClaim := by
  exact FactorKernel.q11_kernel_direct_sum frobeniusEnd11

/-- The q=13 quotient Frobenius quartic factor kernel is its trace kernel. -/
theorem q13_quotient_factor_kernel : q13QuotientFactorClaim := by
  exact congrArg LinearMap.ker (FactorKernel.h13_aeval frobeniusEnd13)

/-- The q=19 quotient Frobenius has the two direct quadratic factor kernels. -/
theorem q19_quotient_factor_kernels : q19QuotientFactorClaim := by
  exact FactorKernel.q19_kernel_direct_sum frobeniusEnd19

/-- The exact q-power quotient endomorphisms satisfy the frozen C5
factor-kernel, trace, fifth-power, and fixed-line controls. -/
theorem all_quotient_C5_controls :
    q11QuotientFactorClaim ∧ q13QuotientFactorClaim ∧ q19QuotientFactorClaim ∧
    (Module.finrank (ZMod 11)
      (CryptoResearch.FrobTrace.trace5 frobeniusEnd11).ker = 4) ∧
    (Module.finrank (ZMod 13)
      (CryptoResearch.FrobTrace.trace5 frobeniusEnd13).ker = 4) ∧
    (Module.finrank (ZMod 19)
      (CryptoResearch.FrobTrace.trace5 frobeniusEnd19).ker = 4) ∧
    (frobeniusEnd11 ^ 5 = 1) ∧ (frobeniusEnd13 ^ 5 = 1) ∧
    (frobeniusEnd19 ^ 5 = 1) ∧
    (Module.finrank (ZMod 11) (frobeniusEnd11 - 1).ker = 1) ∧
    (Module.finrank (ZMod 13) (frobeniusEnd13 - 1).ker = 1) ∧
    (Module.finrank (ZMod 19) (frobeniusEnd19 - 1).ker = 1) ∧
    Disjoint (frobeniusEnd11 - 1).ker
      (CryptoResearch.FrobTrace.trace5 frobeniusEnd11).ker ∧
    Disjoint (frobeniusEnd13 - 1).ker
      (CryptoResearch.FrobTrace.trace5 frobeniusEnd13).ker ∧
    Disjoint (frobeniusEnd19 - 1).ker
      (CryptoResearch.FrobTrace.trace5 frobeniusEnd19).ker := by
  exact ⟨q11_quotient_factor_kernels, q13_quotient_factor_kernel,
    q19_quotient_factor_kernels, q11_quotient_trace_kernel_dim_four,
    q13_quotient_trace_kernel_dim_four, q19_quotient_trace_kernel_dim_four,
    q11_quotient_frobenius_fifth_power, q13_quotient_frobenius_fifth_power,
    q19_quotient_frobenius_fifth_power, q11_quotient_fixed_kernel_dim_one,
    q13_quotient_fixed_kernel_dim_one, q19_quotient_fixed_kernel_dim_one,
    q11_quotient_fixed_trace_disjoint, q13_quotient_fixed_trace_disjoint,
    q19_quotient_fixed_trace_disjoint⟩

end CryptoResearch.FrobTrace.QuotientKernelTransport

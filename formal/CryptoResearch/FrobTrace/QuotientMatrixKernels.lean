import CryptoResearch.FrobTrace.QuotientMatrices
import CryptoResearch.FrobTrace.FactorKernel
import Mathlib.Tactic

/-!
The archived quotient-basis Frobenius matrices satisfy the C5 factor-kernel
identities and have four-dimensional five-term trace kernels. This is a
matrix-model statement; historical Sage execution and source custody are
separate obligations.
-/

open Polynomial
set_option maxHeartbeats 1000000
namespace CryptoResearch.FrobTrace.QuotientMatrixKernels

local instance : Fact (Nat.Prime 11) := ⟨by decide⟩

private abbrev M11 : Matrix (Fin 5) (Fin 5) (ZMod 11) :=
  QuotientMatrices.frobeniusMatrix11

theorem q11_matrix_fifth_power : M11 ^ 5 = 1 := by decide

private def T11 : Matrix (Fin 5) (Fin 5) (ZMod 11) :=
  1 + M11 + M11 ^ 2 + M11 ^ 3 + M11 ^ 4

theorem q11_trace_matrix : T11 =
    !![5, 9, 4, 3, 5;
       0, 0, 0, 0, 0;
       0, 0, 0, 0, 0;
       0, 0, 0, 0, 0;
       0, 0, 0, 0, 0] := by decide

private def D11 : Matrix (Fin 5) (Fin 5) (ZMod 11) :=
  Matrix.diagonal (fun i => if i = 0 then 1 else 0)
private def U11 : Matrix (Fin 5) (Fin 5) (ZMod 11) :=
  !![5, 9, 4, 3, 5;
     0, 1, 0, 0, 0;
     0, 0, 1, 0, 0;
     0, 0, 0, 1, 0;
     0, 0, 0, 0, 1]

theorem q11_trace_matrix_rank_one : T11.rank = 1 := by
  have hTU : T11 = D11 * U11 := by decide
  have htri : U11.IsUpperTriangular := by decide
  have hdet : U11.det ≠ 0 := by
    rw [Matrix.det_of_isUpperTriangular htri]
    decide
  rw [hTU, Matrix.rank_mul_eq_left_of_det_ne_zero U11 D11 hdet]
  unfold D11
  rw [Matrix.rank_diagonal]
  decide

theorem q11_trace_matrix_kernel_dim_four :
    Module.finrank (ZMod 11) (Matrix.toLin' T11).ker = 4 := by
  have hR := Matrix.rank_eq_finrank_range_toLin T11
    (Pi.basisFun (ZMod 11) (Fin 5)) (Pi.basisFun (ZMod 11) (Fin 5))
  rw [Matrix.toLin_eq_toLin'] at hR
  have hrange : Module.finrank (ZMod 11) (Matrix.toLin' T11).range = 1 := by
    calc
      Module.finrank (ZMod 11) (Matrix.toLin' T11).range = T11.rank := hR.symm
      _ = 1 := q11_trace_matrix_rank_one
  have h := (Matrix.toLin' T11).finrank_range_add_finrank_ker
  rw [hrange, Module.finrank_fin_fun] at h
  omega

theorem q11_matrix_frobenius_trace_kernel_dim_four :
    Module.finrank (ZMod 11)
      (CryptoResearch.FrobTrace.trace5 (Matrix.toLin' M11)).ker = 4 := by
  have htrace : CryptoResearch.FrobTrace.trace5 (Matrix.toLin' M11) =
      Matrix.toLin' T11 := by
    simp [CryptoResearch.FrobTrace.trace5, T11, Matrix.toLin'_pow]
    rfl
  rw [htrace]
  exact q11_trace_matrix_kernel_dim_four

local instance : Fact (Nat.Prime 13) := ⟨by decide⟩
private abbrev M13 : Matrix (Fin 5) (Fin 5) (ZMod 13) :=
  QuotientMatrices.frobeniusMatrix13

theorem q13_matrix_fifth_power : M13 ^ 5 = 1 := by decide
private def T13 : Matrix (Fin 5) (Fin 5) (ZMod 13) :=
  1 + M13 + M13 ^ 2 + M13 ^ 3 + M13 ^ 4
theorem q13_trace_matrix : T13 =
    !![5, 5, 12, 8, 1;
       0, 0, 0, 0, 0;
       0, 0, 0, 0, 0;
       0, 0, 0, 0, 0;
       0, 0, 0, 0, 0] := by decide

private def D13 : Matrix (Fin 5) (Fin 5) (ZMod 13) :=
  Matrix.diagonal (fun i => if i = 0 then 1 else 0)
private def U13 : Matrix (Fin 5) (Fin 5) (ZMod 13) :=
  !![5, 5, 12, 8, 1;
     0, 1, 0, 0, 0;
     0, 0, 1, 0, 0;
     0, 0, 0, 1, 0;
     0, 0, 0, 0, 1]
theorem q13_trace_matrix_rank_one : T13.rank = 1 := by
  have hTU : T13 = D13 * U13 := by decide
  have htri : U13.IsUpperTriangular := by decide
  have hdet : U13.det ≠ 0 := by
    rw [Matrix.det_of_isUpperTriangular htri]
    decide
  rw [hTU, Matrix.rank_mul_eq_left_of_det_ne_zero U13 D13 hdet]
  unfold D13
  rw [Matrix.rank_diagonal]
  decide
theorem q13_trace_matrix_kernel_dim_four :
    Module.finrank (ZMod 13) (Matrix.toLin' T13).ker = 4 := by
  have hR := Matrix.rank_eq_finrank_range_toLin T13
    (Pi.basisFun (ZMod 13) (Fin 5)) (Pi.basisFun (ZMod 13) (Fin 5))
  rw [Matrix.toLin_eq_toLin'] at hR
  have hrange : Module.finrank (ZMod 13) (Matrix.toLin' T13).range = 1 := by
    calc
      Module.finrank (ZMod 13) (Matrix.toLin' T13).range = T13.rank := hR.symm
      _ = 1 := q13_trace_matrix_rank_one
  have h := (Matrix.toLin' T13).finrank_range_add_finrank_ker
  rw [hrange, Module.finrank_fin_fun] at h
  omega

theorem q13_matrix_frobenius_trace_kernel_dim_four :
    Module.finrank (ZMod 13)
      (CryptoResearch.FrobTrace.trace5 (Matrix.toLin' M13)).ker = 4 := by
  have htrace : CryptoResearch.FrobTrace.trace5 (Matrix.toLin' M13) =
      Matrix.toLin' T13 := by
    simp [CryptoResearch.FrobTrace.trace5, T13, Matrix.toLin'_pow]
    rfl
  rw [htrace]
  exact q13_trace_matrix_kernel_dim_four

local instance : Fact (Nat.Prime 19) := ⟨by decide⟩
private abbrev M19 : Matrix (Fin 5) (Fin 5) (ZMod 19) :=
  QuotientMatrices.frobeniusMatrix19

theorem q19_matrix_fifth_power : M19 ^ 5 = 1 := by decide
private def T19 : Matrix (Fin 5) (Fin 5) (ZMod 19) :=
  1 + M19 + M19 ^ 2 + M19 ^ 3 + M19 ^ 4
theorem q19_trace_matrix : T19 =
    !![5, 16, 9, 11, 5;
       0, 0, 0, 0, 0;
       0, 0, 0, 0, 0;
       0, 0, 0, 0, 0;
       0, 0, 0, 0, 0] := by decide

private def D19 : Matrix (Fin 5) (Fin 5) (ZMod 19) :=
  Matrix.diagonal (fun i => if i = 0 then 1 else 0)
private def U19 : Matrix (Fin 5) (Fin 5) (ZMod 19) :=
  !![5, 16, 9, 11, 5;
     0, 1, 0, 0, 0;
     0, 0, 1, 0, 0;
     0, 0, 0, 1, 0;
     0, 0, 0, 0, 1]
theorem q19_trace_matrix_rank_one : T19.rank = 1 := by
  have hTU : T19 = D19 * U19 := by decide
  have htri : U19.IsUpperTriangular := by decide
  have hdet : U19.det ≠ 0 := by
    rw [Matrix.det_of_isUpperTriangular htri]
    decide
  rw [hTU, Matrix.rank_mul_eq_left_of_det_ne_zero U19 D19 hdet]
  unfold D19
  rw [Matrix.rank_diagonal]
  decide
theorem q19_trace_matrix_kernel_dim_four :
    Module.finrank (ZMod 19) (Matrix.toLin' T19).ker = 4 := by
  have hR := Matrix.rank_eq_finrank_range_toLin T19
    (Pi.basisFun (ZMod 19) (Fin 5)) (Pi.basisFun (ZMod 19) (Fin 5))
  rw [Matrix.toLin_eq_toLin'] at hR
  have hrange : Module.finrank (ZMod 19) (Matrix.toLin' T19).range = 1 := by
    calc
      Module.finrank (ZMod 19) (Matrix.toLin' T19).range = T19.rank := hR.symm
      _ = 1 := q19_trace_matrix_rank_one
  have h := (Matrix.toLin' T19).finrank_range_add_finrank_ker
  rw [hrange, Module.finrank_fin_fun] at h
  omega

theorem q19_matrix_frobenius_trace_kernel_dim_four :
    Module.finrank (ZMod 19)
      (CryptoResearch.FrobTrace.trace5 (Matrix.toLin' M19)).ker = 4 := by
  have htrace : CryptoResearch.FrobTrace.trace5 (Matrix.toLin' M19) =
      Matrix.toLin' T19 := by
    simp [CryptoResearch.FrobTrace.trace5, T19, Matrix.toLin'_pow]
    rfl
  rw [htrace]
  exact q19_trace_matrix_kernel_dim_four

/-- The four nontrivial linear factor kernels of the exact q=11 matrix are
successively disjoint and sum to its five-term trace kernel. -/
def q11MatrixFactorClaim : Prop :=
    let F := Matrix.toLin' QuotientMatrices.frobeniusMatrix11
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

theorem q11_matrix_factor_kernels : q11MatrixFactorClaim := by
  exact FactorKernel.q11_kernel_direct_sum _

/-- The q=13 irreducible quartic factor kernel is exactly the trace kernel
of the archived quotient-basis Frobenius matrix. -/
def q13MatrixFactorClaim : Prop :=
    let F := Matrix.toLin' QuotientMatrices.frobeniusMatrix13
    (aeval F (X^4 + X^3 + X^2 + X + 1 : (ZMod 13)[X])).ker =
      (CryptoResearch.FrobTrace.trace5 F).ker

theorem q13_matrix_factor_kernel : q13MatrixFactorClaim := by
  exact congrArg LinearMap.ker (FactorKernel.h13_aeval _)

/-- The two nontrivial quadratic factor kernels of the exact q=19 matrix
are disjoint and sum to its five-term trace kernel. -/
def q19MatrixFactorClaim : Prop :=
    let F := Matrix.toLin' QuotientMatrices.frobeniusMatrix19
    Disjoint (aeval F (X^2 + 5 * X + 1 : (ZMod 19)[X])).ker
      (aeval F (X^2 + 15 * X + 1 : (ZMod 19)[X])).ker ∧
    (aeval F (X^2 + 5 * X + 1 : (ZMod 19)[X])).ker ⊔
      (aeval F (X^2 + 15 * X + 1 : (ZMod 19)[X])).ker =
      (CryptoResearch.FrobTrace.trace5 F).ker

theorem q19_matrix_factor_kernels : q19MatrixFactorClaim := by
  exact FactorKernel.q19_kernel_direct_sum _

/-- The exact three quotient-basis matrix controls have direct factor-kernel
sums equal to four-dimensional trace kernels. -/
theorem all_matrix_C5_controls :
    q11MatrixFactorClaim ∧ q13MatrixFactorClaim ∧ q19MatrixFactorClaim ∧
    (Module.finrank (ZMod 11)
      (CryptoResearch.FrobTrace.trace5
        (Matrix.toLin' QuotientMatrices.frobeniusMatrix11)).ker = 4) ∧
    (Module.finrank (ZMod 13)
      (CryptoResearch.FrobTrace.trace5
        (Matrix.toLin' QuotientMatrices.frobeniusMatrix13)).ker = 4) ∧
    (Module.finrank (ZMod 19)
      (CryptoResearch.FrobTrace.trace5
        (Matrix.toLin' QuotientMatrices.frobeniusMatrix19)).ker = 4) := by
  exact ⟨q11_matrix_factor_kernels, q13_matrix_factor_kernel,
    q19_matrix_factor_kernels, q11_matrix_frobenius_trace_kernel_dim_four,
    q13_matrix_frobenius_trace_kernel_dim_four,
    q19_matrix_frobenius_trace_kernel_dim_four⟩

end CryptoResearch.FrobTrace.QuotientMatrixKernels

import CryptoResearch.FrobTrace.QuotientMatrices
import Mathlib.FieldTheory.Finite.Basic
import Mathlib.LinearAlgebra.Matrix.ToLin
import Mathlib.Tactic

/-!
The full q-power Frobenius algebra endomorphism of each archived polynomial
quotient is linear over its base field and has the exact frozen 5×5 matrix.
This mathematical map theorem does not validate historical Sage execution,
original source custody, or irreducibility of the three quotient moduli.
-/

open Polynomial Module
set_option maxHeartbeats 1000000
namespace CryptoResearch.FrobTrace.QuotientFrobeniusMap
open QuotientMatrices

local instance : Fact (Nat.Prime 11) := ⟨by decide⟩

theorem modulus11_natDegree_five : modulus11.natDegree = 5 := by
  unfold modulus11
  compute_degree <;> norm_num

noncomputable def basis11 : Basis (Fin modulus11.natDegree) (ZMod 11) (AdjoinRoot modulus11) :=
  AdjoinRoot.powerBasisAux' modulus11_monic

noncomputable def frobeniusEnd11 : AdjoinRoot modulus11 →ₗ[ZMod 11] AdjoinRoot modulus11 :=
  (FiniteField.frobeniusAlgHom (ZMod 11) (AdjoinRoot modulus11)).toLinearMap

/-- The full ZMod 11-linear q-power endomorphism has the exact frozen matrix
in the archived quotient power basis. -/
theorem full_frobenius_matrix11 (i j : Fin 5) :
    LinearMap.toMatrix basis11 basis11 frobeniusEnd11
      (Fin.cast modulus11_natDegree_five.symm i)
      (Fin.cast modulus11_natDegree_five.symm j) = frobeniusMatrix11 i j := by
  rw [LinearMap.toMatrix_apply]
  have hb : basis11 (Fin.cast modulus11_natDegree_five.symm j) =
      (AdjoinRoot.root modulus11) ^ (j : ℕ) := by
    calc
      basis11 (Fin.cast modulus11_natDegree_five.symm j) =
          (AdjoinRoot.root modulus11) ^ ((Fin.cast modulus11_natDegree_five.symm j : Fin modulus11.natDegree) : ℕ) := by
        exact (AdjoinRoot.powerBasis' modulus11_monic).basis_eq_pow _
      _ = (AdjoinRoot.root modulus11) ^ (j : ℕ) := by rfl
  rw [hb]
  simp only [frobeniusEnd11, AlgHom.toLinearMap_apply, FiniteField.frobeniusAlgHom_apply]
  change basis11.repr (((AdjoinRoot.root modulus11) ^ (j : ℕ)) ^ 11)
    (Fin.cast modulus11_natDegree_five.symm i) = _
  rw [← pow_mul]
  simpa only [basis11, mul_comm] using quotient_frobenius_matrix11 i j

local instance : Fact (Nat.Prime 13) := ⟨by decide⟩

theorem modulus13_natDegree_five : modulus13.natDegree = 5 := by
  unfold modulus13
  compute_degree <;> norm_num

noncomputable def basis13 : Basis (Fin modulus13.natDegree) (ZMod 13) (AdjoinRoot modulus13) :=
  AdjoinRoot.powerBasisAux' modulus13_monic

noncomputable def frobeniusEnd13 : AdjoinRoot modulus13 →ₗ[ZMod 13] AdjoinRoot modulus13 :=
  (FiniteField.frobeniusAlgHom (ZMod 13) (AdjoinRoot modulus13)).toLinearMap

/-- The full ZMod 13-linear q-power endomorphism has the exact frozen matrix
in the archived quotient power basis. -/
theorem full_frobenius_matrix13 (i j : Fin 5) :
    LinearMap.toMatrix basis13 basis13 frobeniusEnd13
      (Fin.cast modulus13_natDegree_five.symm i)
      (Fin.cast modulus13_natDegree_five.symm j) = frobeniusMatrix13 i j := by
  rw [LinearMap.toMatrix_apply]
  have hb : basis13 (Fin.cast modulus13_natDegree_five.symm j) =
      (AdjoinRoot.root modulus13) ^ (j : ℕ) := by
    calc
      basis13 (Fin.cast modulus13_natDegree_five.symm j) =
          (AdjoinRoot.root modulus13) ^ ((Fin.cast modulus13_natDegree_five.symm j : Fin modulus13.natDegree) : ℕ) := by
        exact (AdjoinRoot.powerBasis' modulus13_monic).basis_eq_pow _
      _ = (AdjoinRoot.root modulus13) ^ (j : ℕ) := by rfl
  rw [hb]
  simp only [frobeniusEnd13, AlgHom.toLinearMap_apply, FiniteField.frobeniusAlgHom_apply]
  change basis13.repr (((AdjoinRoot.root modulus13) ^ (j : ℕ)) ^ 13)
    (Fin.cast modulus13_natDegree_five.symm i) = _
  rw [← pow_mul]
  simpa only [basis13, mul_comm] using quotient_frobenius_matrix13 i j

local instance : Fact (Nat.Prime 19) := ⟨by decide⟩

theorem modulus19_natDegree_five : modulus19.natDegree = 5 := by
  unfold modulus19
  compute_degree <;> norm_num

noncomputable def basis19 : Basis (Fin modulus19.natDegree) (ZMod 19) (AdjoinRoot modulus19) :=
  AdjoinRoot.powerBasisAux' modulus19_monic

noncomputable def frobeniusEnd19 : AdjoinRoot modulus19 →ₗ[ZMod 19] AdjoinRoot modulus19 :=
  (FiniteField.frobeniusAlgHom (ZMod 19) (AdjoinRoot modulus19)).toLinearMap

/-- The full ZMod 19-linear q-power endomorphism has the exact frozen matrix
in the archived quotient power basis. -/
theorem full_frobenius_matrix19 (i j : Fin 5) :
    LinearMap.toMatrix basis19 basis19 frobeniusEnd19
      (Fin.cast modulus19_natDegree_five.symm i)
      (Fin.cast modulus19_natDegree_five.symm j) = frobeniusMatrix19 i j := by
  rw [LinearMap.toMatrix_apply]
  have hb : basis19 (Fin.cast modulus19_natDegree_five.symm j) =
      (AdjoinRoot.root modulus19) ^ (j : ℕ) := by
    calc
      basis19 (Fin.cast modulus19_natDegree_five.symm j) =
          (AdjoinRoot.root modulus19) ^ ((Fin.cast modulus19_natDegree_five.symm j : Fin modulus19.natDegree) : ℕ) := by
        exact (AdjoinRoot.powerBasis' modulus19_monic).basis_eq_pow _
      _ = (AdjoinRoot.root modulus19) ^ (j : ℕ) := by rfl
  rw [hb]
  simp only [frobeniusEnd19, AlgHom.toLinearMap_apply, FiniteField.frobeniusAlgHom_apply]
  change basis19.repr (((AdjoinRoot.root modulus19) ^ (j : ℕ)) ^ 19)
    (Fin.cast modulus19_natDegree_five.symm i) = _
  rw [← pow_mul]
  simpa only [basis19, mul_comm] using quotient_frobenius_matrix19 i j
/-- All three full q-power endomorphisms have the certified frozen
quotient-basis matrix, not just the correct basis images individually. -/
theorem all_full_frobenius_matrices :
  (∀ i j : Fin 5,
      LinearMap.toMatrix basis11 basis11 frobeniusEnd11
        (Fin.cast modulus11_natDegree_five.symm i)
        (Fin.cast modulus11_natDegree_five.symm j) = frobeniusMatrix11 i j) ∧
  (∀ i j : Fin 5,
      LinearMap.toMatrix basis13 basis13 frobeniusEnd13
        (Fin.cast modulus13_natDegree_five.symm i)
        (Fin.cast modulus13_natDegree_five.symm j) = frobeniusMatrix13 i j) ∧
  (∀ i j : Fin 5,
      LinearMap.toMatrix basis19 basis19 frobeniusEnd19
        (Fin.cast modulus19_natDegree_five.symm i)
        (Fin.cast modulus19_natDegree_five.symm j) = frobeniusMatrix19 i j) := by
  exact ⟨full_frobenius_matrix11, full_frobenius_matrix13,
    full_frobenius_matrix19⟩

end CryptoResearch.FrobTrace.QuotientFrobeniusMap

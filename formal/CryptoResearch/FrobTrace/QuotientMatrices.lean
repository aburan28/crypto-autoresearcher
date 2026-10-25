import Mathlib.RingTheory.AdjoinRoot
import Mathlib.Tactic

/-!
Exact archived-quotient Frobenius matrices for EXP-FROB-91ee9c C5.
Generated from the immutable source-bound replay receipt SHA-256
22bcbdbdc6dd8c020456549cb1aa2edf887422cb10912105d9fa0508a6ee1005. Lean checks the polynomial divisions and basis entries.
This does not verify the historical Sage implementation or original source custody.
-/

open Polynomial
set_option maxRecDepth 4000
namespace CryptoResearch.FrobTrace.QuotientMatrices

local instance : Fact (Nat.Prime 11) := ⟨by decide⟩

/-- Frozen monic quotient modulus for FROB-SPLIT-q11n5; coefficients are constant first in the replay. -/
noncomputable def modulus11 : (ZMod 11)[X] := X^5 + (2 * X^4 + 1)

private theorem modulus11_low : degree (2 * X^4 + 1 : (ZMod 11)[X]) < 5 := by
  have h4 : degree (2 * X^4 : (ZMod 11)[X]) ≤ 4 := by
    calc
      degree (2 * X^4 : (ZMod 11)[X]) ≤ degree (2 : (ZMod 11)[X]) + degree (X^4) := degree_mul_le _ _
      _ ≤ 4 := by simpa using add_le_add (degree_natCast_le (R := ZMod 11) 2) (show degree (X^4 : (ZMod 11)[X]) ≤ 4 by simp)
  have h1 : degree (1 : (ZMod 11)[X]) ≤ 4 := by simp
  exact lt_of_le_of_lt ((degree_add_le _ _).trans (max_le h4 h1)) (by norm_num)

theorem modulus11_monic : (modulus11).Monic := by
  unfold modulus11
  exact monic_X_pow_add modulus11_low

private theorem modulus11_degree : degree modulus11 = 5 := by
  unfold modulus11
  have hlow : degree (2 * X^4 + 1 : (ZMod 11)[X]) < degree (X^5 : (ZMod 11)[X]) := by simpa using modulus11_low
  rw [degree_add_eq_left_of_degree_lt hlow, degree_X_pow]
  norm_num

private theorem modulus11_natDegree : modulus11.natDegree = 5 :=
  natDegree_eq_of_degree_eq_some modulus11_degree

private theorem cast11_11 : (11 : (ZMod 11)[X]) = 0 := by
  change C (11 : ZMod 11) = 0
  rw [← C_0]
  congr 1


private noncomputable def quotient11_1 : (ZMod 11)[X] := X^6 - 2*X^5 + 4*X^4 + 3*X^3 + 5*X^2 + 2
private noncomputable def remainder11_1 : (ZMod 11)[X] := 3*X^4 - 3*X^3 - 5*X^2 - 2

private theorem remainder11_1_degree : degree remainder11_1 < degree modulus11 := by
  rw [modulus11_degree]
  unfold remainder11_1
  compute_degree; norm_num

private theorem division11_1 :
    remainder11_1 + modulus11 * quotient11_1 = X^11 := by
  unfold remainder11_1 modulus11 quotient11_1
  ring_nf
  simp [cast11_11]

private theorem remainder11_1_exact :
    (X^11 : (ZMod 11)[X]) %ₘ modulus11 = remainder11_1 :=
  (div_modByMonic_unique quotient11_1 remainder11_1
    modulus11_monic ⟨division11_1, remainder11_1_degree⟩).2


private noncomputable def quotient11_2 : (ZMod 11)[X] := X^17 - 2*X^16 + 4*X^15 + 3*X^14 + 5*X^13 + 2*X^11 + 3*X^10 + 2*X^9 + 2*X^8 - 4*X^7 - 5*X^6 - 4*X^5 - 5*X^4 - 3*X^3 - X^2 - 4*X + 1
private noncomputable def remainder11_2 : (ZMod 11)[X] := 3*X^4 + 3*X^3 + X^2 + 4*X - 1

private theorem remainder11_2_degree : degree remainder11_2 < degree modulus11 := by
  rw [modulus11_degree]
  unfold remainder11_2
  compute_degree; norm_num

private theorem division11_2 :
    remainder11_2 + modulus11 * quotient11_2 = X^22 := by
  unfold remainder11_2 modulus11 quotient11_2
  ring_nf
  simp [cast11_11]

private theorem remainder11_2_exact :
    (X^22 : (ZMod 11)[X]) %ₘ modulus11 = remainder11_2 :=
  (div_modByMonic_unique quotient11_2 remainder11_2
    modulus11_monic ⟨division11_2, remainder11_2_degree⟩).2


private noncomputable def quotient11_3 : (ZMod 11)[X] := X^28 - 2*X^27 + 4*X^26 + 3*X^25 + 5*X^24 + 2*X^22 + 3*X^21 + 2*X^20 + 2*X^19 - 4*X^18 - 5*X^17 - 4*X^16 - 5*X^15 - 3*X^14 - X^13 - 4*X^12 + X^11 + 3*X^10 - 3*X^9 - 4*X^8 + X^7 - 3*X^6 + 3*X^5 - 3*X^4 - X^3 + X^2 + X - 5
private noncomputable def remainder11_3 : (ZMod 11)[X] := 2*X^4 + X^3 - X^2 - X + 5

private theorem remainder11_3_degree : degree remainder11_3 < degree modulus11 := by
  rw [modulus11_degree]
  unfold remainder11_3
  compute_degree; norm_num

private theorem division11_3 :
    remainder11_3 + modulus11 * quotient11_3 = X^33 := by
  unfold remainder11_3 modulus11 quotient11_3
  ring_nf
  simp [cast11_11]

private theorem remainder11_3_exact :
    (X^33 : (ZMod 11)[X]) %ₘ modulus11 = remainder11_3 :=
  (div_modByMonic_unique quotient11_3 remainder11_3
    modulus11_monic ⟨division11_3, remainder11_3_degree⟩).2


private noncomputable def quotient11_4 : (ZMod 11)[X] := X^39 - 2*X^38 + 4*X^37 + 3*X^36 + 5*X^35 + 2*X^33 + 3*X^32 + 2*X^31 + 2*X^30 - 4*X^29 - 5*X^28 - 4*X^27 - 5*X^26 - 3*X^25 - X^24 - 4*X^23 + X^22 + 3*X^21 - 3*X^20 - 4*X^19 + X^18 - 3*X^17 + 3*X^16 - 3*X^15 - X^14 + X^13 + X^12 - 5*X^11 + 2*X^10 - 3*X^9 + 5*X^8 + 5*X^6 - X^5 + 5*X^4 - 4*X^3 - 3*X^2 + X - 1
private noncomputable def remainder11_4 : (ZMod 11)[X] := -3*X^4 + 4*X^3 + 3*X^2 - X + 1

private theorem remainder11_4_degree : degree remainder11_4 < degree modulus11 := by
  rw [modulus11_degree]
  unfold remainder11_4
  compute_degree; norm_num

private theorem division11_4 :
    remainder11_4 + modulus11 * quotient11_4 = X^44 := by
  unfold remainder11_4 modulus11 quotient11_4
  ring_nf
  simp [cast11_11]

private theorem remainder11_4_exact :
    (X^44 : (ZMod 11)[X]) %ₘ modulus11 = remainder11_4 :=
  (div_modByMonic_unique quotient11_4 remainder11_4
    modulus11_monic ⟨division11_4, remainder11_4_degree⟩).2


/-- The exact archived 5×5 matrix, with q-power images as columns. -/
def frobeniusMatrix11 : Matrix (Fin 5) (Fin 5) (ZMod 11) :=
  !![1, 9, 10, 5, 1;
     0, 0, 4, 10, 10;
     0, 6, 1, 10, 3;
     0, 8, 3, 1, 4;
     0, 3, 3, 2, 8]

private theorem remainder11_matrix : ∀ i j : Fin 5,
    ((X^(11 * (j : ℕ)) : (ZMod 11)[X]) %ₘ modulus11).coeff (i : ℕ) =
      frobeniusMatrix11 i j := by
  intro i j
  have hzero : (1 : (ZMod 11)[X]) %ₘ modulus11 = 1 := by
    apply (Polynomial.modByMonic_eq_self_iff modulus11_monic).2
    rw [modulus11_degree]
    norm_num
  fin_cases j <;> fin_cases i <;>
    simp [hzero, remainder11_1_exact, remainder11_2_exact, remainder11_3_exact, remainder11_4_exact,
      remainder11_1, remainder11_2, remainder11_3, remainder11_4, frobeniusMatrix11,
      Polynomial.coeff_add, Polynomial.coeff_sub,
      Polynomial.coeff_X_pow, Polynomial.coeff_X, Polynomial.coeff_one] <;> decide

/-- Every entry of the frozen Frobenius matrix equals the q-power operation
on the corresponding archived quotient-basis monomial. -/
theorem quotient_frobenius_matrix11 (i j : Fin 5) :
    (AdjoinRoot.powerBasisAux' modulus11_monic).repr
      ((AdjoinRoot.root modulus11) ^ (11 * (j : ℕ)))
      (Fin.cast modulus11_natDegree.symm i) = frobeniusMatrix11 i j := by
  rw [AdjoinRoot.powerBasisAux'_repr_apply_to_fun]
  have hroot : (AdjoinRoot.root modulus11) ^ (11 * (j : ℕ)) =
      AdjoinRoot.mk modulus11 (X ^ (11 * (j : ℕ))) := by
    rw [← AdjoinRoot.mk_X]
    exact (map_pow (AdjoinRoot.mk modulus11) X _).symm
  rw [hroot, AdjoinRoot.modByMonicHom_mk]
  simpa using remainder11_matrix i j

local instance : Fact (Nat.Prime 13) := ⟨by decide⟩

/-- Frozen monic quotient modulus for FROB-NOLATTICE-q13n5; coefficients are constant first in the replay. -/
noncomputable def modulus13 : (ZMod 13)[X] := X^5 + (8 * X^4 + 1)

private theorem modulus13_low : degree (8 * X^4 + 1 : (ZMod 13)[X]) < 5 := by
  have h4 : degree (8 * X^4 : (ZMod 13)[X]) ≤ 4 := by
    calc
      degree (8 * X^4 : (ZMod 13)[X]) ≤ degree (8 : (ZMod 13)[X]) + degree (X^4) := degree_mul_le _ _
      _ ≤ 4 := by simpa using add_le_add (degree_natCast_le (R := ZMod 13) 8) (show degree (X^4 : (ZMod 13)[X]) ≤ 4 by simp)
  have h1 : degree (1 : (ZMod 13)[X]) ≤ 4 := by simp
  exact lt_of_le_of_lt ((degree_add_le _ _).trans (max_le h4 h1)) (by norm_num)

theorem modulus13_monic : (modulus13).Monic := by
  unfold modulus13
  exact monic_X_pow_add modulus13_low

private theorem modulus13_degree : degree modulus13 = 5 := by
  unfold modulus13
  have hlow : degree (8 * X^4 + 1 : (ZMod 13)[X]) < degree (X^5 : (ZMod 13)[X]) := by simpa using modulus13_low
  rw [degree_add_eq_left_of_degree_lt hlow, degree_X_pow]
  norm_num

private theorem modulus13_natDegree : modulus13.natDegree = 5 :=
  natDegree_eq_of_degree_eq_some modulus13_degree

private theorem cast13_13 : (13 : (ZMod 13)[X]) = 0 := by
  change C (13 : ZMod 13) = 0
  rw [← C_0]
  congr 1

private theorem cast13_26 : (26 : (ZMod 13)[X]) = 0 := by
  calc
    (26 : (ZMod 13)[X]) = (13 : (ZMod 13)[X]) * 2 := by norm_num
    _ = 0 := by simp [cast13_13]

private theorem cast13_39 : (39 : (ZMod 13)[X]) = 0 := by
  calc
    (39 : (ZMod 13)[X]) = (13 : (ZMod 13)[X]) * 3 := by norm_num
    _ = 0 := by simp [cast13_13]

private theorem cast13_52 : (52 : (ZMod 13)[X]) = 0 := by
  calc
    (52 : (ZMod 13)[X]) = (13 : (ZMod 13)[X]) * 4 := by norm_num
    _ = 0 := by simp [cast13_13]


private noncomputable def quotient13_1 : (ZMod 13)[X] := X^8 + 5*X^7 - X^6 - 5*X^5 + X^4 + 4*X^3 + 2*X^2 - 2*X - 5
private noncomputable def remainder13_1 : (ZMod 13)[X] := -4*X^3 - 2*X^2 + 2*X + 5

private theorem remainder13_1_degree : degree remainder13_1 < degree modulus13 := by
  rw [modulus13_degree]
  unfold remainder13_1
  compute_degree; norm_num

private theorem division13_1 :
    remainder13_1 + modulus13 * quotient13_1 = X^13 := by
  unfold remainder13_1 modulus13 quotient13_1
  ring_nf
  simp [cast13_13, cast13_26, cast13_39]

private theorem remainder13_1_exact :
    (X^13 : (ZMod 13)[X]) %ₘ modulus13 = remainder13_1 :=
  (div_modByMonic_unique quotient13_1 remainder13_1
    modulus13_monic ⟨division13_1, remainder13_1_degree⟩).2


private noncomputable def quotient13_2 : (ZMod 13)[X] := X^21 + 5*X^20 - X^19 - 5*X^18 + X^17 + 4*X^16 + 2*X^15 - 2*X^14 - 5*X^13 - 4*X^11 + 4*X^10 - 4*X^9 - 2*X^8 + 3*X^7 + 6*X^6 + 4*X^4 - 4*X^3 + 3*X^2 - 4*X + 6
private noncomputable def remainder13_2 : (ZMod 13)[X] := 4*X^3 - 3*X^2 + 4*X - 6

private theorem remainder13_2_degree : degree remainder13_2 < degree modulus13 := by
  rw [modulus13_degree]
  unfold remainder13_2
  compute_degree; norm_num

private theorem division13_2 :
    remainder13_2 + modulus13 * quotient13_2 = X^26 := by
  unfold remainder13_2 modulus13 quotient13_2
  ring_nf
  simp [cast13_13, cast13_26, cast13_39, cast13_52]

private theorem remainder13_2_exact :
    (X^26 : (ZMod 13)[X]) %ₘ modulus13 = remainder13_2 :=
  (div_modByMonic_unique quotient13_2 remainder13_2
    modulus13_monic ⟨division13_2, remainder13_2_degree⟩).2


private noncomputable def quotient13_3 : (ZMod 13)[X] := X^34 + 5*X^33 - X^32 - 5*X^31 + X^30 + 4*X^29 + 2*X^28 - 2*X^27 - 5*X^26 - 4*X^24 + 4*X^23 - 4*X^22 - 2*X^21 + 3*X^20 + 6*X^19 + 4*X^17 - 4*X^16 + 3*X^15 - 4*X^14 + 6*X^13 + 4*X^11 + 4*X^10 - 2*X^9 - 3*X^8 - 2*X^7 - X^6 + 4*X^5 - 4*X^4 - 4*X^3 - 5*X^2 + 2*X + 6
private noncomputable def remainder13_3 : (ZMod 13)[X] := -5*X^4 + 4*X^3 + 5*X^2 - 2*X - 6

private theorem remainder13_3_degree : degree remainder13_3 < degree modulus13 := by
  rw [modulus13_degree]
  unfold remainder13_3
  compute_degree; norm_num

private theorem division13_3 :
    remainder13_3 + modulus13 * quotient13_3 = X^39 := by
  unfold remainder13_3 modulus13 quotient13_3
  ring_nf
  simp [cast13_13, cast13_26, cast13_39, cast13_52]

private theorem remainder13_3_exact :
    (X^39 : (ZMod 13)[X]) %ₘ modulus13 = remainder13_3 :=
  (div_modByMonic_unique quotient13_3 remainder13_3
    modulus13_monic ⟨division13_3, remainder13_3_degree⟩).2


private noncomputable def quotient13_4 : (ZMod 13)[X] := X^47 + 5*X^46 - X^45 - 5*X^44 + X^43 + 4*X^42 + 2*X^41 - 2*X^40 - 5*X^39 - 4*X^37 + 4*X^36 - 4*X^35 - 2*X^34 + 3*X^33 + 6*X^32 + 4*X^30 - 4*X^29 + 3*X^28 - 4*X^27 + 6*X^26 + 4*X^24 + 4*X^23 - 2*X^22 - 3*X^21 - 2*X^20 - X^19 + 4*X^18 - 4*X^17 - 4*X^16 - 5*X^15 + 2*X^14 + 6*X^13 - 5*X^12 + 5*X^11 + 4*X^10 + 5*X^9 + 6*X^8 - 4*X^7 + X^6 + X^5 - 6*X^3 - X - 6
private noncomputable def remainder13_4 : (ZMod 13)[X] := -4*X^4 + 6*X^3 + X + 6

private theorem remainder13_4_degree : degree remainder13_4 < degree modulus13 := by
  rw [modulus13_degree]
  unfold remainder13_4
  compute_degree; norm_num

private theorem division13_4 :
    remainder13_4 + modulus13 * quotient13_4 = X^52 := by
  unfold remainder13_4 modulus13 quotient13_4
  ring_nf
  simp [cast13_13, cast13_26, cast13_39, cast13_52]

private theorem remainder13_4_exact :
    (X^52 : (ZMod 13)[X]) %ₘ modulus13 = remainder13_4 :=
  (div_modByMonic_unique quotient13_4 remainder13_4
    modulus13_monic ⟨division13_4, remainder13_4_degree⟩).2


/-- The exact archived 5×5 matrix, with q-power images as columns. -/
def frobeniusMatrix13 : Matrix (Fin 5) (Fin 5) (ZMod 13) :=
  !![1, 5, 7, 7, 6;
     0, 2, 4, 11, 1;
     0, 11, 10, 5, 0;
     0, 9, 4, 4, 6;
     0, 0, 0, 8, 9]

private theorem remainder13_matrix : ∀ i j : Fin 5,
    ((X^(13 * (j : ℕ)) : (ZMod 13)[X]) %ₘ modulus13).coeff (i : ℕ) =
      frobeniusMatrix13 i j := by
  intro i j
  have hzero : (1 : (ZMod 13)[X]) %ₘ modulus13 = 1 := by
    apply (Polynomial.modByMonic_eq_self_iff modulus13_monic).2
    rw [modulus13_degree]
    norm_num
  fin_cases j <;> fin_cases i <;>
    simp [hzero, remainder13_1_exact, remainder13_2_exact, remainder13_3_exact, remainder13_4_exact,
      remainder13_1, remainder13_2, remainder13_3, remainder13_4, frobeniusMatrix13,
      Polynomial.coeff_add, Polynomial.coeff_sub,
      Polynomial.coeff_X_pow, Polynomial.coeff_X, Polynomial.coeff_one] <;> decide

/-- Every entry of the frozen Frobenius matrix equals the q-power operation
on the corresponding archived quotient-basis monomial. -/
theorem quotient_frobenius_matrix13 (i j : Fin 5) :
    (AdjoinRoot.powerBasisAux' modulus13_monic).repr
      ((AdjoinRoot.root modulus13) ^ (13 * (j : ℕ)))
      (Fin.cast modulus13_natDegree.symm i) = frobeniusMatrix13 i j := by
  rw [AdjoinRoot.powerBasisAux'_repr_apply_to_fun]
  have hroot : (AdjoinRoot.root modulus13) ^ (13 * (j : ℕ)) =
      AdjoinRoot.mk modulus13 (X ^ (13 * (j : ℕ))) := by
    rw [← AdjoinRoot.mk_X]
    exact (map_pow (AdjoinRoot.mk modulus13) X _).symm
  rw [hroot, AdjoinRoot.modByMonicHom_mk]
  simpa using remainder13_matrix i j

local instance : Fact (Nat.Prime 19) := ⟨by decide⟩

/-- Frozen monic quotient modulus for FROB-EQDEG-q19n5; coefficients are constant first in the replay. -/
noncomputable def modulus19 : (ZMod 19)[X] := X^5 + (3 * X^4 + 1)

private theorem modulus19_low : degree (3 * X^4 + 1 : (ZMod 19)[X]) < 5 := by
  have h4 : degree (3 * X^4 : (ZMod 19)[X]) ≤ 4 := by
    calc
      degree (3 * X^4 : (ZMod 19)[X]) ≤ degree (3 : (ZMod 19)[X]) + degree (X^4) := degree_mul_le _ _
      _ ≤ 4 := by simpa using add_le_add (degree_natCast_le (R := ZMod 19) 3) (show degree (X^4 : (ZMod 19)[X]) ≤ 4 by simp)
  have h1 : degree (1 : (ZMod 19)[X]) ≤ 4 := by simp
  exact lt_of_le_of_lt ((degree_add_le _ _).trans (max_le h4 h1)) (by norm_num)

theorem modulus19_monic : (modulus19).Monic := by
  unfold modulus19
  exact monic_X_pow_add modulus19_low

private theorem modulus19_degree : degree modulus19 = 5 := by
  unfold modulus19
  have hlow : degree (3 * X^4 + 1 : (ZMod 19)[X]) < degree (X^5 : (ZMod 19)[X]) := by simpa using modulus19_low
  rw [degree_add_eq_left_of_degree_lt hlow, degree_X_pow]
  norm_num

private theorem modulus19_natDegree : modulus19.natDegree = 5 :=
  natDegree_eq_of_degree_eq_some modulus19_degree

private theorem cast19_19 : (19 : (ZMod 19)[X]) = 0 := by
  change C (19 : ZMod 19) = 0
  rw [← C_0]
  congr 1

private theorem cast19_38 : (38 : (ZMod 19)[X]) = 0 := by
  calc
    (38 : (ZMod 19)[X]) = (19 : (ZMod 19)[X]) * 2 := by norm_num
    _ = 0 := by simp [cast19_19]


private noncomputable def quotient19_1 : (ZMod 19)[X] := X^14 - 3*X^13 + 9*X^12 - 8*X^11 + 5*X^10 + 3*X^9 - 6*X^8 + 9*X^7 - 5*X^5 - 7*X^4 + 8*X^3 + 5*X^2 + 4*X - 7
private noncomputable def remainder19_1 : (ZMod 19)[X] := 9*X^4 - 8*X^3 - 5*X^2 - 4*X + 7

private theorem remainder19_1_degree : degree remainder19_1 < degree modulus19 := by
  rw [modulus19_degree]
  unfold remainder19_1
  compute_degree; norm_num

private theorem division19_1 :
    remainder19_1 + modulus19 * quotient19_1 = X^19 := by
  unfold remainder19_1 modulus19 quotient19_1
  ring_nf
  simp [cast19_19, cast19_38]

private theorem remainder19_1_exact :
    (X^19 : (ZMod 19)[X]) %ₘ modulus19 = remainder19_1 :=
  (div_modByMonic_unique quotient19_1 remainder19_1
    modulus19_monic ⟨division19_1, remainder19_1_degree⟩).2


private noncomputable def quotient19_2 : (ZMod 19)[X] := X^33 - 3*X^32 + 9*X^31 - 8*X^30 + 5*X^29 + 3*X^28 - 6*X^27 + 9*X^26 - 5*X^24 - 7*X^23 + 8*X^22 + 5*X^21 + 4*X^20 - 7*X^19 + 9*X^18 + 3*X^17 + 5*X^16 + 7*X^14 + 8*X^13 - 8*X^12 - 7*X^9 - 6*X^8 + 7*X^7 - 2*X^6 + 6*X^5 + 8*X^4 + X^3 + 9*X^2 - 6*X - 7
private noncomputable def remainder19_2 : (ZMod 19)[X] := -6*X^4 - X^3 - 9*X^2 + 6*X + 7

private theorem remainder19_2_degree : degree remainder19_2 < degree modulus19 := by
  rw [modulus19_degree]
  unfold remainder19_2
  compute_degree; norm_num

private theorem division19_2 :
    remainder19_2 + modulus19 * quotient19_2 = X^38 := by
  unfold remainder19_2 modulus19 quotient19_2
  ring_nf
  simp [cast19_19, cast19_38]

private theorem remainder19_2_exact :
    (X^38 : (ZMod 19)[X]) %ₘ modulus19 = remainder19_2 :=
  (div_modByMonic_unique quotient19_2 remainder19_2
    modulus19_monic ⟨division19_2, remainder19_2_degree⟩).2


private noncomputable def quotient19_3 : (ZMod 19)[X] := X^52 - 3*X^51 + 9*X^50 - 8*X^49 + 5*X^48 + 3*X^47 - 6*X^46 + 9*X^45 - 5*X^43 - 7*X^42 + 8*X^41 + 5*X^40 + 4*X^39 - 7*X^38 + 9*X^37 + 3*X^36 + 5*X^35 + 7*X^33 + 8*X^32 - 8*X^31 - 7*X^28 - 6*X^27 + 7*X^26 - 2*X^25 + 6*X^24 + 8*X^23 + X^22 + 9*X^21 - 6*X^20 - 7*X^19 - 6*X^18 - 2*X^17 - 3*X^16 - 4*X^15 + 6*X^13 + 3*X^12 - 6*X^11 + 3*X^10 - 9*X^9 + 2*X^8 - 9*X^7 - 5*X^6 - 7*X^5 - 8*X^4 + 3*X^3 + 5*X - 8
private noncomputable def remainder19_3 : (ZMod 19)[X] := -6*X^4 - 3*X^3 - 5*X + 8

private theorem remainder19_3_degree : degree remainder19_3 < degree modulus19 := by
  rw [modulus19_degree]
  unfold remainder19_3
  compute_degree; norm_num

private theorem division19_3 :
    remainder19_3 + modulus19 * quotient19_3 = X^57 := by
  unfold remainder19_3 modulus19 quotient19_3
  ring_nf
  simp [cast19_19, cast19_38]

private theorem remainder19_3_exact :
    (X^57 : (ZMod 19)[X]) %ₘ modulus19 = remainder19_3 :=
  (div_modByMonic_unique quotient19_3 remainder19_3
    modulus19_monic ⟨division19_3, remainder19_3_degree⟩).2


private noncomputable def quotient19_4 : (ZMod 19)[X] := X^71 - 3*X^70 + 9*X^69 - 8*X^68 + 5*X^67 + 3*X^66 - 6*X^65 + 9*X^64 - 5*X^62 - 7*X^61 + 8*X^60 + 5*X^59 + 4*X^58 - 7*X^57 + 9*X^56 + 3*X^55 + 5*X^54 + 7*X^52 + 8*X^51 - 8*X^50 - 7*X^47 - 6*X^46 + 7*X^45 - 2*X^44 + 6*X^43 + 8*X^42 + X^41 + 9*X^40 - 6*X^39 - 7*X^38 - 6*X^37 - 2*X^36 - 3*X^35 - 4*X^34 + 6*X^32 + 3*X^31 - 6*X^30 + 3*X^29 - 9*X^28 + 2*X^27 - 9*X^26 - 5*X^25 - 7*X^24 - 8*X^23 + 3*X^22 + 5*X^20 - 8*X^19 - 6*X^18 - 4*X^17 - 7*X^16 - 3*X^15 - 2*X^14 - 7*X^13 + 6*X^12 + 8*X^11 - 2*X^10 + 8*X^9 + 2*X^8 + 7*X^7 + 9*X^6 - 6*X^5 - 9*X^4 + 6*X^3 - 6*X^2 + 9*X - 2
private noncomputable def remainder19_4 : (ZMod 19)[X] := -4*X^4 - 6*X^3 + 6*X^2 - 9*X + 2

private theorem remainder19_4_degree : degree remainder19_4 < degree modulus19 := by
  rw [modulus19_degree]
  unfold remainder19_4
  compute_degree; norm_num

private theorem division19_4 :
    remainder19_4 + modulus19 * quotient19_4 = X^76 := by
  unfold remainder19_4 modulus19 quotient19_4
  ring_nf
  simp [cast19_19, cast19_38]

private theorem remainder19_4_exact :
    (X^76 : (ZMod 19)[X]) %ₘ modulus19 = remainder19_4 :=
  (div_modByMonic_unique quotient19_4 remainder19_4
    modulus19_monic ⟨division19_4, remainder19_4_degree⟩).2


/-- The exact archived 5×5 matrix, with q-power images as columns. -/
def frobeniusMatrix19 : Matrix (Fin 5) (Fin 5) (ZMod 19) :=
  !![1, 7, 7, 8, 2;
     0, 15, 6, 14, 10;
     0, 14, 10, 0, 6;
     0, 11, 18, 16, 13;
     0, 9, 13, 13, 15]

private theorem remainder19_matrix : ∀ i j : Fin 5,
    ((X^(19 * (j : ℕ)) : (ZMod 19)[X]) %ₘ modulus19).coeff (i : ℕ) =
      frobeniusMatrix19 i j := by
  intro i j
  have hzero : (1 : (ZMod 19)[X]) %ₘ modulus19 = 1 := by
    apply (Polynomial.modByMonic_eq_self_iff modulus19_monic).2
    rw [modulus19_degree]
    norm_num
  fin_cases j <;> fin_cases i <;>
    simp [hzero, remainder19_1_exact, remainder19_2_exact, remainder19_3_exact, remainder19_4_exact,
      remainder19_1, remainder19_2, remainder19_3, remainder19_4, frobeniusMatrix19,
      Polynomial.coeff_add, Polynomial.coeff_sub,
      Polynomial.coeff_X_pow, Polynomial.coeff_X, Polynomial.coeff_one] <;> decide

/-- Every entry of the frozen Frobenius matrix equals the q-power operation
on the corresponding archived quotient-basis monomial. -/
theorem quotient_frobenius_matrix19 (i j : Fin 5) :
    (AdjoinRoot.powerBasisAux' modulus19_monic).repr
      ((AdjoinRoot.root modulus19) ^ (19 * (j : ℕ)))
      (Fin.cast modulus19_natDegree.symm i) = frobeniusMatrix19 i j := by
  rw [AdjoinRoot.powerBasisAux'_repr_apply_to_fun]
  have hroot : (AdjoinRoot.root modulus19) ^ (19 * (j : ℕ)) =
      AdjoinRoot.mk modulus19 (X ^ (19 * (j : ℕ))) := by
    rw [← AdjoinRoot.mk_X]
    exact (map_pow (AdjoinRoot.mk modulus19) X _).symm
  rw [hroot, AdjoinRoot.modByMonicHom_mk]
  simpa using remainder19_matrix i j

/-- The three exact archived-quotient Frobenius matrices. -/
theorem all_quotient_frobenius_matrices :
  (∀ i j : Fin 5,
      (AdjoinRoot.powerBasisAux' modulus11_monic).repr
        ((AdjoinRoot.root modulus11) ^ (11 * (j : ℕ)))
        (Fin.cast modulus11_natDegree.symm i) = frobeniusMatrix11 i j) ∧
  (∀ i j : Fin 5,
      (AdjoinRoot.powerBasisAux' modulus13_monic).repr
        ((AdjoinRoot.root modulus13) ^ (13 * (j : ℕ)))
        (Fin.cast modulus13_natDegree.symm i) = frobeniusMatrix13 i j) ∧
  (∀ i j : Fin 5,
      (AdjoinRoot.powerBasisAux' modulus19_monic).repr
        ((AdjoinRoot.root modulus19) ^ (19 * (j : ℕ)))
        (Fin.cast modulus19_natDegree.symm i) = frobeniusMatrix19 i j) := by
  exact ⟨quotient_frobenius_matrix11, quotient_frobenius_matrix13, quotient_frobenius_matrix19⟩

end CryptoResearch.FrobTrace.QuotientMatrices

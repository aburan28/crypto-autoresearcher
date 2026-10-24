import Mathlib.RingTheory.Polynomial.Basic
import Mathlib.RingTheory.Polynomial.Cyclotomic.Factorization
import Mathlib.Tactic
import CryptoResearch.FrobTrace.FiniteFieldTrace

open Polynomial

/-!
The mathematical factor-kernel portion of EXP-FROB-91ee9c control C5.
The q=11,13,19 factor polynomials are shown to be the nontrivial
irreducible factors of X^5-1; their Frobenius kernels form direct sums
(or one kernel in the q=13 case) equal to the field-trace kernel of
K-dimension four. These statements use canonical GaloisField models,
not the archived quotient-field encoding or executable matrix.
-/

namespace CryptoResearch.FrobTrace.FactorKernel
local instance : Fact (Nat.Prime 19) := ⟨by decide⟩

private noncomputable def p19 : (ZMod 19)[X] := X^2 + 5 * X + 1
private noncomputable def q19 : (ZMod 19)[X] := X^2 + 15 * X + 1
private noncomputable def h19 : (ZMod 19)[X] := X^4 + X^3 + X^2 + X + 1

private theorem n20 : (20 : (ZMod 19)[X]) = 1 := by
  change C (20 : ZMod 19) = C (1 : ZMod 19)
  congr 1
private theorem n77 : (77 : (ZMod 19)[X]) = 1 := by
  change C (77 : ZMod 19) = C (1 : ZMod 19)
  congr 1
private theorem n209 : (209 : (ZMod 19)[X]) = 0 := by
  change C (209 : ZMod 19) = 0
  simp [show (209 : ZMod 19) = 0 by decide]
private theorem n285 : (285 : (ZMod 19)[X]) = 0 := by
  change C (285 : ZMod 19) = 0
  simp [show (285 : ZMod 19) = 0 by decide]
private theorem n19 : (19 : (ZMod 19)[X]) = 0 := by
  change C (19 : ZMod 19) = 0
  simp [show (19 : ZMod 19) = 0 by decide]

theorem factor19 : p19 * q19 = h19 := by
  unfold p19 q19 h19
  ring_nf
  rw [n20, n77]
  ring

theorem coprime19 : IsCoprime p19 q19 := by
  refine ⟨11 + 2 * X, 9 + 17 * X, ?_⟩
  unfold p19 q19
  ring_nf
  rw [n20, n209, n285, n19]
  ring

theorem h19_aeval {V : Type*} [AddCommGroup V] [Module (ZMod 19) V]
    (F : Module.End (ZMod 19) V) :
    aeval F h19 = CryptoResearch.FrobTrace.trace5 F := by
  simp [h19, CryptoResearch.FrobTrace.trace5]
  abel

theorem q19_kernel_direct_sum {V : Type*} [AddCommGroup V] [Module (ZMod 19) V]
    (F : Module.End (ZMod 19) V) :
    Disjoint (aeval F p19).ker (aeval F q19).ker ∧
      (aeval F p19).ker ⊔ (aeval F q19).ker =
        (CryptoResearch.FrobTrace.trace5 F).ker := by
  constructor
  · exact Polynomial.disjoint_ker_aeval_of_isCoprime F coprime19
  · rw [Polynomial.sup_ker_aeval_eq_ker_aeval_mul_of_coprime F coprime19,
        factor19, h19_aeval]

theorem q19_field_factor_kernel :
    (aeval (CryptoResearch.FrobTrace.FiniteField.frobeniusEnd
      (K := ZMod 19) (L := GaloisField 19 5)) p19).ker ⊔
    (aeval (CryptoResearch.FrobTrace.FiniteField.frobeniusEnd
      (K := ZMod 19) (L := GaloisField 19 5)) q19).ker =
      (Algebra.trace (ZMod 19) (GaloisField 19 5)).ker := by
  rw [← CryptoResearch.FrobTrace.FiniteField.ker_trace5_eq_field_trace_ker
    (GaloisField.finrank 19 (by decide))]
  exact (q19_kernel_direct_sum
    (CryptoResearch.FrobTrace.FiniteField.frobeniusEnd
      (K := ZMod 19) (L := GaloisField 19 5))).2

local instance : Fact (Nat.Prime 11) := ⟨by decide⟩
private noncomputable def h11 : (ZMod 11)[X] := X^4 + X^3 + X^2 + X + 1

theorem factor11 :
    (X + 2 : (ZMod 11)[X]) * (X + 6) * (X + 7) * (X + 8) = h11 := by
  unfold h11
  ring_nf
  have h672 : (672 : (ZMod 11)[X]) = 1 := by
    change C (672 : ZMod 11) = C (1 : ZMod 11)
    congr 1
  have h628 : (628 : (ZMod 11)[X]) = 1 := by
    change C (628 : ZMod 11) = C (1 : ZMod 11)
    congr 1
  have h188 : (188 : (ZMod 11)[X]) = 1 := by
    change C (188 : ZMod 11) = C (1 : ZMod 11)
    congr 1
  have h23 : (23 : (ZMod 11)[X]) = 1 := by
    change C (23 : ZMod 11) = C (1 : ZMod 11)
    congr 1
  rw [h672, h628, h188, h23]
  ring

private theorem linear11_coprime (a b : ZMod 11) (hab : a ≠ b) :
    IsCoprime (X + C a) (X + C b) := by
  have h : IsUnit ((-a) - (-b)) :=
    (sub_ne_zero.mpr (by intro h; exact hab (neg_injective h))).isUnit
  simpa only [map_neg, sub_neg_eq_add] using
    (Polynomial.isCoprime_X_sub_C_of_isUnit_sub h)

private noncomputable abbrev a11 : (ZMod 11)[X] := X + 2
private noncomputable abbrev b11 : (ZMod 11)[X] := X + 6
private noncomputable abbrev c11 : (ZMod 11)[X] := X + 7
private noncomputable abbrev d11 : (ZMod 11)[X] := X + 8

private theorem c2 : (C (2 : ZMod 11) : (ZMod 11)[X]) = 2 := C_eq_natCast 2
private theorem c6 : (C (6 : ZMod 11) : (ZMod 11)[X]) = 6 := C_eq_natCast 6
private theorem c7 : (C (7 : ZMod 11) : (ZMod 11)[X]) = 7 := C_eq_natCast 7
private theorem c8 : (C (8 : ZMod 11) : (ZMod 11)[X]) = 8 := C_eq_natCast 8

private theorem coprime11_ab : IsCoprime a11 b11 := by
  simpa only [a11, b11, c2, c6, c7, c8] using linear11_coprime 2 6 (by decide)
private theorem coprime11_ac : IsCoprime a11 c11 := by
  simpa only [a11, c11, c2, c6, c7, c8] using linear11_coprime 2 7 (by decide)
private theorem coprime11_bc : IsCoprime b11 c11 := by
  simpa only [b11, c11, c2, c6, c7, c8] using linear11_coprime 6 7 (by decide)
private theorem coprime11_ad : IsCoprime a11 d11 := by
  simpa only [a11, d11, c2, c6, c7, c8] using linear11_coprime 2 8 (by decide)
private theorem coprime11_bd : IsCoprime b11 d11 := by
  simpa only [b11, d11, c2, c6, c7, c8] using linear11_coprime 6 8 (by decide)
private theorem coprime11_cd : IsCoprime c11 d11 := by
  simpa only [c11, d11, c2, c6, c7, c8] using linear11_coprime 7 8 (by decide)

private theorem coprime11_abc : IsCoprime (a11 * b11) c11 :=
  coprime11_ac.mul_left coprime11_bc
private theorem coprime11_abcd : IsCoprime ((a11 * b11) * c11) d11 :=
  (coprime11_ad.mul_left coprime11_bd).mul_left coprime11_cd

theorem h11_aeval {V : Type*} [AddCommGroup V] [Module (ZMod 11) V]
    (F : Module.End (ZMod 11) V) :
    aeval F h11 = CryptoResearch.FrobTrace.trace5 F := by
  simp [h11, CryptoResearch.FrobTrace.trace5]
  abel

theorem q11_kernel_direct_sum {V : Type*} [AddCommGroup V] [Module (ZMod 11) V]
    (F : Module.End (ZMod 11) V) :
    Disjoint (aeval F a11).ker (aeval F b11).ker ∧
    Disjoint ((aeval F a11).ker ⊔ (aeval F b11).ker) (aeval F c11).ker ∧
    Disjoint (((aeval F a11).ker ⊔ (aeval F b11).ker) ⊔ (aeval F c11).ker)
      (aeval F d11).ker ∧
    (((aeval F a11).ker ⊔ (aeval F b11).ker) ⊔ (aeval F c11).ker) ⊔
      (aeval F d11).ker = (CryptoResearch.FrobTrace.trace5 F).ker := by
  refine ⟨Polynomial.disjoint_ker_aeval_of_isCoprime F coprime11_ab, ?_, ?_, ?_⟩
  · rw [Polynomial.sup_ker_aeval_eq_ker_aeval_mul_of_coprime F coprime11_ab]
    exact Polynomial.disjoint_ker_aeval_of_isCoprime F coprime11_abc
  · rw [Polynomial.sup_ker_aeval_eq_ker_aeval_mul_of_coprime F coprime11_ab,
        Polynomial.sup_ker_aeval_eq_ker_aeval_mul_of_coprime F coprime11_abc]
    exact Polynomial.disjoint_ker_aeval_of_isCoprime F coprime11_abcd
  · rw [Polynomial.sup_ker_aeval_eq_ker_aeval_mul_of_coprime F coprime11_ab,
        Polynomial.sup_ker_aeval_eq_ker_aeval_mul_of_coprime F coprime11_abc,
        Polynomial.sup_ker_aeval_eq_ker_aeval_mul_of_coprime F coprime11_abcd]
    change (aeval F (a11 * b11 * c11 * d11)).ker = _
    rw [show a11 * b11 * c11 * d11 = h11 by simpa [a11, b11, c11, d11] using factor11,
        h11_aeval]

theorem q11_field_factor_kernel :
    ((((aeval (CryptoResearch.FrobTrace.FiniteField.frobeniusEnd
      (K := ZMod 11) (L := GaloisField 11 5)) a11).ker ⊔
      (aeval (CryptoResearch.FrobTrace.FiniteField.frobeniusEnd
      (K := ZMod 11) (L := GaloisField 11 5)) b11).ker) ⊔
      (aeval (CryptoResearch.FrobTrace.FiniteField.frobeniusEnd
      (K := ZMod 11) (L := GaloisField 11 5)) c11).ker) ⊔
      (aeval (CryptoResearch.FrobTrace.FiniteField.frobeniusEnd
      (K := ZMod 11) (L := GaloisField 11 5)) d11).ker) =
      (Algebra.trace (ZMod 11) (GaloisField 11 5)).ker := by
  rw [← CryptoResearch.FrobTrace.FiniteField.ker_trace5_eq_field_trace_ker
    (GaloisField.finrank 11 (by decide))]
  exact (q11_kernel_direct_sum
    (CryptoResearch.FrobTrace.FiniteField.frobeniusEnd
      (K := ZMod 11) (L := GaloisField 11 5))).2.2.2

local instance : Fact (Nat.Prime 13) := ⟨by decide⟩
private noncomputable def h13 : (ZMod 13)[X] := X^4 + X^3 + X^2 + X + 1

theorem h13_aeval {V : Type*} [AddCommGroup V] [Module (ZMod 13) V]
    (F : Module.End (ZMod 13) V) :
    aeval F h13 = CryptoResearch.FrobTrace.trace5 F := by
  simp [h13, CryptoResearch.FrobTrace.trace5]
  abel

theorem q13_field_factor_kernel :
    (aeval (CryptoResearch.FrobTrace.FiniteField.frobeniusEnd
      (K := ZMod 13) (L := GaloisField 13 5)) h13).ker =
      (Algebra.trace (ZMod 13) (GaloisField 13 5)).ker := by
  rw [← CryptoResearch.FrobTrace.FiniteField.ker_trace5_eq_field_trace_ker
    (GaloisField.finrank 13 (by decide)), h13_aeval]

local instance : Fact (Nat.Prime 5) := ⟨by decide⟩

theorem h13_cyclotomic : h13 = cyclotomic 5 (ZMod 13) := by
  unfold h13
  rw [cyclotomic_prime]
  simp [Finset.sum_range_succ]
  ring

private theorem order13_mod5 :
    orderOf (ZMod.unitOfCoprime 13 (by decide : Nat.Coprime 13 5)) = 4 := by
  apply (orderOf_eq_iff (by decide : 0 < 4)).2
  constructor
  · decide
  · intro m hm hm0
    interval_cases m <;> decide

theorem h13_irreducible : Irreducible h13 := by
  apply ZMod.irreducible_of_dvd_cyclotomic_of_natDegree (p := 13) (n := 5) (by decide)
  · rw [← h13_cyclotomic]
  · rw [h13_cyclotomic, natDegree_cyclotomic]
    rw [order13_mod5]
    decide

theorem h19_cyclotomic : h19 = cyclotomic 5 (ZMod 19) := by
  unfold h19
  rw [cyclotomic_prime]
  simp [Finset.sum_range_succ]
  ring

private theorem order19_mod5 :
    orderOf (ZMod.unitOfCoprime 19 (by decide : Nat.Coprime 19 5)) = 2 := by
  apply (orderOf_eq_iff (by decide : 0 < 2)).2
  constructor
  · decide
  · intro m hm hm0
    interval_cases m; decide

private theorem p19_natDegree : p19.natDegree = 2 := by
  unfold p19
  compute_degree!
private theorem q19_natDegree : q19.natDegree = 2 := by
  unfold q19
  compute_degree!

theorem p19_irreducible : Irreducible p19 := by
  apply ZMod.irreducible_of_dvd_cyclotomic_of_natDegree (p := 19) (n := 5) (by decide)
  · refine ⟨q19, ?_⟩
    exact (factor19.trans h19_cyclotomic).symm
  · rw [p19_natDegree, order19_mod5]

theorem q19_irreducible : Irreducible q19 := by
  apply ZMod.irreducible_of_dvd_cyclotomic_of_natDegree (p := 19) (n := 5) (by decide)
  · refine ⟨p19, ?_⟩
    rw [mul_comm]
    exact (factor19.trans h19_cyclotomic).symm
  · rw [q19_natDegree, order19_mod5]

theorem a11_irreducible : Irreducible a11 := by
  change Irreducible (X + 2 : (ZMod 11)[X])
  rw [← c2]
  exact irreducible_of_degree_eq_one (degree_X_add_C (2 : ZMod 11))
theorem b11_irreducible : Irreducible b11 := by
  change Irreducible (X + 6 : (ZMod 11)[X])
  rw [← c6]
  exact irreducible_of_degree_eq_one (degree_X_add_C (6 : ZMod 11))
theorem c11_irreducible : Irreducible c11 := by
  change Irreducible (X + 7 : (ZMod 11)[X])
  rw [← c7]
  exact irreducible_of_degree_eq_one (degree_X_add_C (7 : ZMod 11))
theorem d11_irreducible : Irreducible d11 := by
  change Irreducible (X + 8 : (ZMod 11)[X])
  rw [← c8]
  exact irreducible_of_degree_eq_one (degree_X_add_C (8 : ZMod 11))

theorem h11_cyclotomic : h11 = cyclotomic 5 (ZMod 11) := by
  unfold h11
  rw [cyclotomic_prime]
  simp [Finset.sum_range_succ]
  ring

theorem q11_factor_kernel_finrank_four :
    Module.finrank (ZMod 11)
      ↥(((((aeval (CryptoResearch.FrobTrace.FiniteField.frobeniusEnd
        (K := ZMod 11) (L := GaloisField 11 5)) a11).ker ⊔
        (aeval (CryptoResearch.FrobTrace.FiniteField.frobeniusEnd
        (K := ZMod 11) (L := GaloisField 11 5)) b11).ker) ⊔
        (aeval (CryptoResearch.FrobTrace.FiniteField.frobeniusEnd
        (K := ZMod 11) (L := GaloisField 11 5)) c11).ker) ⊔
        (aeval (CryptoResearch.FrobTrace.FiniteField.frobeniusEnd
        (K := ZMod 11) (L := GaloisField 11 5)) d11).ker)) = 4 := by
  rw [q11_field_factor_kernel]
  exact CryptoResearch.FrobTrace.FiniteField.field_trace_ker_finrank_four
    (GaloisField.finrank 11 (by decide))

theorem q13_factor_kernel_finrank_four :
    Module.finrank (ZMod 13)
      (aeval (CryptoResearch.FrobTrace.FiniteField.frobeniusEnd
        (K := ZMod 13) (L := GaloisField 13 5)) h13).ker = 4 := by
  rw [q13_field_factor_kernel]
  exact CryptoResearch.FrobTrace.FiniteField.field_trace_ker_finrank_four
    (GaloisField.finrank 13 (by decide))

theorem q19_factor_kernel_finrank_four :
    Module.finrank (ZMod 19)
      ↥((aeval (CryptoResearch.FrobTrace.FiniteField.frobeniusEnd
        (K := ZMod 19) (L := GaloisField 19 5)) p19).ker ⊔
       (aeval (CryptoResearch.FrobTrace.FiniteField.frobeniusEnd
        (K := ZMod 19) (L := GaloisField 19 5)) q19).ker) = 4 := by
  rw [q19_field_factor_kernel]
  exact CryptoResearch.FrobTrace.FiniteField.field_trace_ker_finrank_four
    (GaloisField.finrank 19 (by decide))

end CryptoResearch.FrobTrace.FactorKernel

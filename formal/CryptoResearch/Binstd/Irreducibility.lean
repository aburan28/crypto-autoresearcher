import CryptoResearch.Binstd.Factorization
import Mathlib.RingTheory.Polynomial.Cyclotomic.Factorization
import Mathlib.Tactic

/-!
Irreducibility of the two degree-eight factors recorded by
EXP-BINSTD-8bdf86 at n=17.

The product identity is imported from Factorization. The proof uses
Mathlib's cyclotomic factor-degree criterion: 2 has multiplicative
order 8 modulo 17, both factors have degree 8, and both divide the
17th cyclotomic polynomial over F₂.

This does not yet establish that the archived field's Frobenius
representation is the cyclic module F₂[X]/(X^17+1), or classify every
Frobenius-invariant subspace of that field.
-/

namespace CryptoResearch.Binstd

open Polynomial

local instance : Fact (Nat.Prime 2) := ⟨by decide⟩
local instance : Fact (Nat.Prime 17) := ⟨by decide⟩

private theorem coprime_two_seventeen : Nat.Coprime 2 17 := by decide
private noncomputable def twoUnit : (ZMod 17)ˣ :=
  ZMod.unitOfCoprime 2 coprime_two_seventeen

private theorem twoUnit_order : orderOf twoUnit = 8 := by
  apply orderOf_eq_of_pow_and_pow_div_prime (by decide)
  · decide
  · intro p hp hpd
    have hpd2 : p ∣ 2 ^ 3 := by simpa using hpd
    have hp2 : p = 2 := Nat.prime_eq_prime_of_dvd_pow hp (by decide) hpd2
    subst p
    decide

theorem factor8a_natDegree : factor8a.natDegree = 8 := by
  unfold factor8a
  compute_degree <;> norm_num

theorem factor8b_natDegree : factor8b.natDegree = 8 := by
  unfold factor8b
  compute_degree <;> norm_num

/-- The degree-eight product is the seventeenth cyclotomic polynomial over F₂. -/
theorem factor8_product_eq_cyclotomic :
    factor8a * factor8b = cyclotomic 17 F2 := by
  have hz : (2 : F2) = 0 := by decide
  have hp : (2 : F2[X]) = 0 := by
    change C (2 : F2) = 0
    simp [hz]
  have hneg : -(1 : F2[X]) = 1 := by
    calc
      -(1 : F2[X]) = 1 - 2 := by ring
      _ = 1 := by rw [hp]; ring
  have hcyc : cyclotomic 17 F2 * (X + 1) = X ^ 17 + 1 := by
    simpa only [sub_eq_add_neg, hneg] using
      (cyclotomic_prime_mul_X_sub_one F2 17)
  have hfac : factor8a * factor8b * (X + 1) = X ^ 17 + 1 := by
    calc
      _ = factor1 * factor8a * factor8b := by unfold factor1; ring
      _ = _ := x17_factorization
  have hne : (X + 1 : F2[X]) ≠ 0 := by
    simpa using (X_add_C_ne_zero (1 : F2))
  apply mul_right_cancel₀ hne
  rw [hfac, hcyc]

theorem factor8a_irreducible : Irreducible factor8a := by
  have hpn : ¬ 2 ∣ 17 := by decide
  have hdiv : factor8a ∣ cyclotomic 17 F2 := by
    rw [← factor8_product_eq_cyclotomic]
    exact ⟨factor8b, rfl⟩
  have hdeg : factor8a.natDegree =
      orderOf (ZMod.unitOfCoprime 2 ((Fact.out : Nat.Prime 2).coprime_iff_not_dvd.mpr hpn)) := by
    rw [factor8a_natDegree]
    simpa [twoUnit] using twoUnit_order.symm
  exact ZMod.irreducible_of_dvd_cyclotomic_of_natDegree hpn hdiv hdeg

theorem factor8b_irreducible : Irreducible factor8b := by
  have hpn : ¬ 2 ∣ 17 := by decide
  have hdiv : factor8b ∣ cyclotomic 17 F2 := by
    rw [← factor8_product_eq_cyclotomic]
    exact ⟨factor8a, by ring⟩
  have hdeg : factor8b.natDegree =
      orderOf (ZMod.unitOfCoprime 2 ((Fact.out : Nat.Prime 2).coprime_iff_not_dvd.mpr hpn)) := by
    rw [factor8b_natDegree]
    simpa [twoUnit] using twoUnit_order.symm
  exact ZMod.irreducible_of_dvd_cyclotomic_of_natDegree hpn hdiv hdeg

/-- Both archived degree-eight factors are irreducible over F₂. -/
theorem factor8_irreducible_pair :
    Irreducible factor8a ∧ Irreducible factor8b :=
  ⟨factor8a_irreducible, factor8b_irreducible⟩

end CryptoResearch.Binstd

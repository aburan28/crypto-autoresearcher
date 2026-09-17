/-
q-th powering collapses to coefficientwise Frobenius, modulo the field equations.

Source: research/THM_SEMAEV_FALL1.md
Target: formal/targets/semaev-frobenius-collapse.yaml
Claim:  THM-SEMAEV-FALL1-LEMMA-1

This is the structural reason the Weil-descended Semaev systems are not
semi-regular: the Frobenius conjugates making up the system are redundant
modulo q-th powers and the field equations, at a degree that does not grow
with n.

IT IS AN IDENTITY, NOT A BOUND. Nothing here says anything about how the
solving degree grows, or about the first fall degree. A semantic-fidelity
review that reads this as supporting a subexponential claim has misread it.
-/
import Mathlib.RingTheory.MvPolynomial.Basic
import Mathlib.Algebra.CharP.Lemmas
import Mathlib.Algebra.CharP.Frobenius
import Mathlib.RingTheory.Ideal.Quotient.Defs

namespace CryptoResearch.Semaev

open MvPolynomial

variable {σ K : Type*} [CommRing K]

/-- The field equations ideal `I_q = (x_i^q - x_i : i)`. -/
noncomputable def fieldEquations (σ : Type*) (K : Type*) [CommRing K] (q : ℕ) :
    Ideal (MvPolynomial σ K) :=
  Ideal.span (Set.range fun i : σ => X i ^ q - X i)

theorem X_pow_sub_X_mem_fieldEquations (q : ℕ) (i : σ) :
    (X i : MvPolynomial σ K) ^ q - X i ∈ fieldEquations σ K q :=
  Ideal.subset_span ⟨i, rfl⟩

/-- **`g^q ≡ g^φ` modulo the field equations**, where `q = p^e` and `φ` is the
`q`-power Frobenius applied to each coefficient.

The proof is the freshman's dream plus one substitution: `q`-th powering is a
ring endomorphism in characteristic `p`, so it distributes over sums and
products and fixes nothing but the coefficients, where it acts as `φ`; each
variable is then pulled back down by its own field equation `x_i^q = x_i`. -/
theorem pow_q_eq_frobeniusTwist_mod_fieldEquations
    (p e : ℕ) [ExpChar K p] (g : MvPolynomial σ K) :
    g ^ p ^ e - map (iterateFrobenius K p e) g ∈ fieldEquations σ K (p ^ e) := by
  rw [← Ideal.Quotient.eq]
  induction g using MvPolynomial.induction_on with
  | C a => rw [← C_pow, map_C, iterateFrobenius_def]
  | add f g hf hg =>
      rw [add_pow_expChar_pow, map_add, map_add, map_add, hf, hg]
  | mul_X f i hf =>
      have hXi : Ideal.Quotient.mk (fieldEquations σ K (p ^ e))
            ((X i : MvPolynomial σ K) ^ p ^ e)
          = Ideal.Quotient.mk _ (X i) :=
        Ideal.Quotient.eq.2 (X_pow_sub_X_mem_fieldEquations _ i)
      rw [mul_pow, map_mul, map_mul, map_X, map_mul, hf, hXi]

end CryptoResearch.Semaev

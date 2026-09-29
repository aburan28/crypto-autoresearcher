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
import Mathlib.Algebra.MvPolynomial.NoZeroDivisors
import Mathlib.Algebra.CharP.Reduced

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

/-! ## Corollary 1: the free degree fall, with the drop quantified

Lemma 1 is an identity. This section turns it into a BOUND: it says where the
fall lands and exactly how far it falls. -/

section FreeDegreeFall

variable {σ K : Type*} [CommRing K] [IsDomain K] {p e : ℕ} [ExpChar K p]

/-- Over a domain, powering multiplies total degree exactly. Mathlib's
`totalDegree_pow` is only an inequality; the equality is what makes the drop
below exact rather than merely an upper bound. -/
theorem totalDegree_pow_eq {g : MvPolynomial σ K} (hg : g ≠ 0) :
    ∀ n : ℕ, (g ^ n).totalDegree = n * g.totalDegree
  | 0 => by simp
  | (n + 1) => by
      rw [pow_succ, totalDegree_mul_of_isDomain (pow_ne_zero n hg) hg,
        totalDegree_pow_eq hg n]
      ring

/-- The twist is degree-PRESERVING: coefficientwise Frobenius is injective on a
reduced ring, so it moves no exponent vector and the support is unchanged. -/
@[simp] theorem totalDegree_map_iterateFrobenius (g : MvPolynomial σ K) :
    (map (iterateFrobenius K p e) g).totalDegree = g.totalDegree := by
  rw [totalDegree, totalDegree,
    support_map_of_injective g (iterateFrobenius_inj K p e)]

omit [IsDomain K] in
/-- **Corollary 1, membership.** Any ideal containing the field equations is
closed under the twist. This is the "free" part: `g^φ` costs nothing beyond a
`q`-th power and a reduction.

No domain hypothesis: this half holds over any commutative ring of exponential
characteristic `p`. Only the DEGREE statements below need `IsDomain`. -/
theorem frobeniusTwist_mem_of_fieldEquations_le (J : Ideal (MvPolynomial σ K))
    (hIJ : fieldEquations σ K (p ^ e) ≤ J) {g : MvPolynomial σ K} (hg : g ∈ J) :
    map (iterateFrobenius K p e) g ∈ J := by
  have hpow : g ^ p ^ e ∈ J :=
    Ideal.pow_mem_of_mem J hg _ (pow_pos (expChar_pos K p) e)
  have hsub : g ^ p ^ e - map (iterateFrobenius K p e) g ∈ J :=
    hIJ (pow_q_eq_frobeniusTwist_mod_fieldEquations p e g)
  simpa using J.sub_mem hpow hsub

/-- **Corollary 1, the drop.** The element that enters is `g^q` at degree
`q * deg g`; the element that comes out is `g^φ` at degree `deg g`. Both are
EQUALITIES, so the fall is exactly `(q - 1) * deg g` -- not at most that. -/
theorem free_degree_fall {g : MvPolynomial σ K} (hg : g ≠ 0) :
    (g ^ p ^ e).totalDegree = p ^ e * g.totalDegree ∧
      (map (iterateFrobenius K p e) g).totalDegree = g.totalDegree ∧
      (g ^ p ^ e).totalDegree - (map (iterateFrobenius K p e) g).totalDegree
        = (p ^ e - 1) * g.totalDegree :=
  ⟨totalDegree_pow_eq hg _, totalDegree_map_iterateFrobenius g, by
    rw [totalDegree_pow_eq hg, totalDegree_map_iterateFrobenius,
      ← Nat.sub_one_mul]⟩

end FreeDegreeFall

end CryptoResearch.Semaev

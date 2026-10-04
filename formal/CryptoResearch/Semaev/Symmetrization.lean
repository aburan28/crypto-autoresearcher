/-
Symmetrization does not increase total degree.

Source: research/THM_SEMAEV_FALL1.md, Lemma 2
Target: formal/targets/semaev-symmetrization-degree.yaml
Claim:  THM-SEMAEV-FALL1-LEMMA-2

Rewriting a symmetric polynomial `S` in elementary symmetric coordinates as
`S = T(e_1, ..., e_m)` preserves WEIGHTED degree (weight `i` on `e_i`) and does
not increase TOTAL degree.

THIS BOUNDS THE DEGREE OF THE REPRESENTATION, AND NOTHING ELSE. It says nothing
about the Groebner solving degree of the symmetrized ideal, which is the
quantity FGHR measured and the only one bearing on cost. Reading a green build
here as explaining the observed symmetrization speedup is exactly the lossy
projection docs/inventor-protocol.md warns against. See THM_SEMAEV_FALL1
Remark 2.

Mathlib supplied the fundamental theorem of symmetric polynomials
(`esymmAlgHom`, its injectivity and surjectivity) but NOT the graded form that
this lemma is about: `esymm` is not recorded as homogeneous and the
substitution is not recorded as degree-tracking. Both are proved here.
-/
import Mathlib.RingTheory.MvPolynomial.Symmetric.FundamentalTheorem
import Mathlib.RingTheory.MvPolynomial.Homogeneous
import Mathlib.RingTheory.MvPolynomial.WeightedHomogeneous

namespace CryptoResearch.Semaev

open MvPolynomial Finset

variable {σ R : Type*} [CommSemiring R] [Fintype σ]

theorem esymm_isHomogeneous (k : ℕ) : (esymm σ R k).IsHomogeneous k := by
  classical
  rw [esymm]
  refine IsHomogeneous.sum _ _ _ fun t ht => ?_
  have h : (∏ i ∈ t, (X i : MvPolynomial σ R)).IsHomogeneous (∑ _i ∈ t, 1) :=
    IsHomogeneous.prod _ _ _ fun i _ => isHomogeneous_X R i
  simpa [Finset.sum_const, (Finset.mem_powersetCard.mp ht).2] using h

/-- The weight assigning `e_i` its degree `i`. -/
def esymmWeight (n : ℕ) : Fin n → ℕ := fun i => (i : ℕ) + 1

/-- The substitution `x_i ↦ e_{i+1}`, as a plain algebra map into the big ring. -/
noncomputable def esymmSub (σ R : Type*) [CommSemiring R] [Fintype σ] (n : ℕ) :
    MvPolynomial (Fin n) R →ₐ[R] MvPolynomial σ R :=
  aeval (fun i : Fin n => esymm σ R ((i : ℕ) + 1))

theorem esymmSub_monomial_isHomogeneous {n : ℕ} (t : Fin n →₀ ℕ) (r : R) :
    (esymmSub σ R n (monomial t r)).IsHomogeneous
      (Finsupp.weight (esymmWeight n) t) := by
  rw [esymmSub, aeval_monomial, Finsupp.weight_apply, algebraMap_eq]
  have hprod : (t.prod fun i k => (esymm σ R ((i : ℕ) + 1)) ^ k).IsHomogeneous
      (∑ i ∈ t.support, ((i : ℕ) + 1) * t i) :=
    IsHomogeneous.prod _ _ _ fun i _ => (esymm_isHomogeneous ((i : ℕ) + 1)).pow (t i)
  have : (∑ i ∈ t.support, ((i : ℕ) + 1) * t i)
      = Finsupp.sum t fun i c => c • esymmWeight n i := by
    simp [Finsupp.sum, esymmWeight, mul_comm]
  rw [← this]
  exact hprod.C_mul r

omit [Fintype σ] in
theorem isHomogeneous_totalDegree_le {φ : MvPolynomial σ R} {d : ℕ}
    (h : φ.IsHomogeneous d) : φ.totalDegree ≤ d := by
  rcases eq_or_ne φ 0 with rfl | hφ
  · simp
  · exact (h.totalDegree hφ).le

/-- Push the substitution through the monomial decomposition once, so the
expensive rewrite happens on a sum of monomials rather than under `aeval`. -/
theorem esymmSub_eq_sum {n : ℕ} (T : MvPolynomial (Fin n) R) :
    esymmSub σ R n T
      = ∑ t ∈ T.support, esymmSub σ R n (monomial t (T.coeff t)) := by
  rw [← map_sum]
  congr 1
  exact T.as_sum

theorem esymmSub_isHomogeneous {n d : ℕ} {T : MvPolynomial (Fin n) R}
    (hT : IsWeightedHomogeneous (esymmWeight n) T d) :
    (esymmSub σ R n T).IsHomogeneous d := by
  classical
  rw [esymmSub_eq_sum]
  refine IsHomogeneous.sum _ _ _ fun t ht => ?_
  have hw : Finsupp.weight (esymmWeight n) t = d := hT (mem_support_iff.mp ht)
  simpa [hw] using esymmSub_monomial_isHomogeneous (σ := σ) t (T.coeff t)

theorem totalDegree_esymmSub_le {n : ℕ} (T : MvPolynomial (Fin n) R) :
    (esymmSub σ R n T).totalDegree ≤ weightedTotalDegree (esymmWeight n) T := by
  classical
  rw [esymmSub_eq_sum]
  refine (totalDegree_finsetSum _ _).trans (Finset.sup_le fun t ht => ?_)
  exact (isHomogeneous_totalDegree_le
    (esymmSub_monomial_isHomogeneous t (T.coeff t))).trans
    (le_weightedTotalDegree _ ht)

section Ring
variable {σ R : Type*} [CommRing R] [Fintype σ]

theorem esymmSub_injective {n : ℕ} (hn : n ≤ Fintype.card σ) :
    Function.Injective (esymmSub σ R n) := by
  intro a b hab
  refine esymmAlgHom_injective R hn (Subtype.ext ?_)
  rw [esymmAlgHom_apply, esymmAlgHom_apply]
  exact hab

/-- **Lemma 2(a).** The substitution is degree-exact: the total degree of the
image equals the WEIGHTED degree of the preimage. The `≤` half is termwise; the
`≥` half is where no-cancellation is needed, and it comes from injectivity
applied to the top weighted-homogeneous component. -/
theorem totalDegree_esymmSub {n : ℕ} (hn : n ≤ Fintype.card σ)
    {T : MvPolynomial (Fin n) R} (hT : T ≠ 0) :
    (esymmSub σ R n T).totalDegree = weightedTotalDegree (esymmWeight n) T := by
  classical
  refine le_antisymm (totalDegree_esymmSub_le T) ?_
  set w := esymmWeight n with hw
  set D := weightedTotalDegree w T with hDdef
  set TD := weightedHomogeneousComponent w D T with hTDdef
  -- The top weighted component is nonzero: the sup is attained on the support.
  have hsupp : T.support.Nonempty := support_nonempty.mpr hT
  obtain ⟨t₀, ht₀, ht₀D⟩ := Finset.exists_mem_eq_sup T.support hsupp (Finsupp.weight w)
  have hTDne : TD ≠ 0 := by
    intro h
    have hcond : Finsupp.weight w t₀ = D := by rw [hDdef, weightedTotalDegree, ht₀D]
    have : TD.coeff t₀ = T.coeff t₀ := by
      rw [hTDdef, coeff_weightedHomogeneousComponent]
      simp [hcond]
    rw [h] at this
    exact (mem_support_iff.mp ht₀) this.symm
  have hhom : (esymmSub σ R n TD).IsHomogeneous D :=
    esymmSub_isHomogeneous (weightedHomogeneousComponent_isWeightedHomogeneous D T)
  have hne : esymmSub σ R n TD ≠ 0 := fun h =>
    hTDne (esymmSub_injective hn (by simpa using h))
  obtain ⟨m, hm⟩ := support_nonempty.mpr hne
  have hmdeg : m.degree = D := by
    by_contra hcon
    exact (mem_support_iff.mp hm) (hhom.coeff_eq_zero hcon)
  -- Coefficients at `m` agree: every other weighted layer is homogeneous of a
  -- different degree, so it cannot contribute to a degree-`D` monomial.
  have hTD_eq : esymmSub σ R n TD
      = ∑ t ∈ T.support.filter (fun t => Finsupp.weight w t = D),
          esymmSub σ R n (monomial t (T.coeff t)) := by
    rw [hTDdef, weightedHomogeneousComponent_apply, map_sum]
  have hagree : (esymmSub σ R n T).coeff m = (esymmSub σ R n TD).coeff m := by
    rw [esymmSub_eq_sum, hTD_eq, coeff_sum, coeff_sum]
    refine (Finset.sum_subset (Finset.filter_subset _ _) ?_).symm
    intro t ht hnot
    have hweight : Finsupp.weight w t ≠ D := by
      simpa [Finset.mem_filter, ht] using hnot
    exact (esymmSub_monomial_isHomogeneous t (T.coeff t)).coeff_eq_zero (by
      rw [hmdeg]; exact fun hc => hweight hc.symm)
  have : (esymmSub σ R n T).coeff m ≠ 0 := by
    rw [hagree]; exact mem_support_iff.mp hm
  calc D = m.degree := hmdeg.symm
    _ ≤ (esymmSub σ R n T).totalDegree := le_totalDegree (mem_support_iff.mpr this)

end Ring

section Bound
variable {σ R : Type*} [CommRing R] [Fintype σ]

theorem degree_le_weight {n : ℕ} (d : Fin n →₀ ℕ) :
    (d.sum fun _ e => e) ≤ Finsupp.weight (esymmWeight n) d := by
  rw [Finsupp.weight_apply]
  refine Finset.sum_le_sum fun i _ => ?_
  simpa [esymmWeight] using Nat.le_mul_of_pos_right (d i) (Nat.succ_pos (i : ℕ))

theorem totalDegree_le_weightedTotalDegree {n : ℕ} (T : MvPolynomial (Fin n) R) :
    T.totalDegree ≤ weightedTotalDegree (esymmWeight n) T :=
  Finset.sup_mono_fun fun d _ => degree_le_weight d

/-- **Lemma 2(b), the bound.** Rewriting a symmetric polynomial in elementary
symmetric coordinates does not INCREASE total degree. -/
theorem totalDegree_symmetricRewrite_le {n : ℕ} (hn : n ≤ Fintype.card σ)
    {T : MvPolynomial (Fin n) R} (hT : T ≠ 0) :
    T.totalDegree ≤ (esymmSub σ R n T).totalDegree := by
  rw [totalDegree_esymmSub hn hT]
  exact totalDegree_le_weightedTotalDegree T

end Bound

/-- **The claim in the form the target states it.** For a symmetric `S`, the
elementary-symmetric rewrite exists and its total degree is at most that of
`S`. Existence is Mathlib's surjectivity; the degree bound is Lemma 2(b). -/
theorem exists_symmetricRewrite_totalDegree_le {σ R : Type*} [CommRing R]
    [Fintype σ] {S : MvPolynomial σ R} (hS : S.IsSymmetric) (hS0 : S ≠ 0) :
    ∃ T : MvPolynomial (Fin (Fintype.card σ)) R,
      esymmSub σ R (Fintype.card σ) T = S ∧ T.totalDegree ≤ S.totalDegree := by
  obtain ⟨T, hT⟩ := esymmAlgHom_surjective (R := R) (σ := σ)
    (n := Fintype.card σ) le_rfl ⟨S, hS⟩
  have hTS : esymmSub σ R (Fintype.card σ) T = S := by
    rw [esymmSub, ← esymmAlgHom_apply, hT]
  refine ⟨T, hTS, ?_⟩
  have hT0 : T ≠ 0 := by
    intro h
    apply hS0
    rw [← hTS, h, map_zero]
  rw [← hTS]
  exact totalDegree_symmetricRewrite_le le_rfl hT0

end CryptoResearch.Semaev

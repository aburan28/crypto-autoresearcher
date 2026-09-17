/-
The last fall degree IS the largest degree at which a degree fall occurs.

Source: research/THM_FALLDEG_INVARIANTS1.md section 2
Target: formal/targets/lastfall-is-max-degree-fall.yaml
Claim:  THM-FALLDEG-INVARIANTS1-THM-2-8

Caminata-Gorla Theorem 2.8. This is the statement that licenses reading a
per-degree Macaulay rank profile as the last fall degree ITSELF rather than as
a proxy for it.

Scope, and it is narrow. This is a theorem about the INVARIANT `d_F`, proved
from Definition 1.5 and nothing else. It says nothing about Semaev systems,
bounds nothing about any particular family, and is not evidence toward the
growth question in RQ-DREG-bd6c86. It is also unrelated to the solving degree
(CORR-20260916-0c9c0a).

Finiteness of `d_F` is an explicit HYPOTHESIS here, not a theorem. Caminata and
Gorla get it from the existence of a Groebner basis; reproving that would drag
in exactly the machinery this target was chosen to avoid, so it is assumed and
said out loud.

NON-VACUITY IS NOT ESTABLISHED. The theorem is conditional on `hfin` and
`hfall`, and nothing in this file exhibits an `F` satisfying them. A witness
would have to show `f ∉ V F d` for every `d` below the fall, which is a lower
bound on the closure and is real work, not bookkeeping. Until someone supplies
one, this is a true implication whose hypotheses are known to be satisfiable
only from the literature, not from anything machine-checked here.
-/
import Mathlib.RingTheory.MvPolynomial.Basic
import Mathlib.RingTheory.Ideal.Span

namespace CryptoResearch.FallDegree

open MvPolynomial

variable {σ k : Type*} [Field k]

/-- **Definition 1.5.** `V F i` is the smallest `k`-subspace of the polynomial
ring that contains every element of `F` of total degree at most `i` and is
closed under multiplying by anything that keeps the total degree within `i`.

The closure condition is written `f.totalDegree + g.totalDegree ≤ i` rather
than `g.totalDegree ≤ i - f.totalDegree`. On `ℕ` that subtraction TRUNCATES, so
the second form would become satisfiable by every `g` as soon as
`f.totalDegree > i` -- a different, and wrong, closure. -/
noncomputable def V (F : Set (MvPolynomial σ k)) (i : ℕ) : Submodule k (MvPolynomial σ k) :=
  sInf {W : Submodule k (MvPolynomial σ k) |
    (∀ f ∈ F, f.totalDegree ≤ i → f ∈ W) ∧
    (∀ f ∈ W, ∀ g : MvPolynomial σ k,
      f.totalDegree + g.totalDegree ≤ i → f * g ∈ W)}

/-- The family is monotone: a larger budget admits more. Both defining
conditions weaken as `i` grows, so the constraint set shrinks and its
infimum grows. -/
theorem V_mono (F : Set (MvPolynomial σ k)) {i j : ℕ} (hij : i ≤ j) :
    V F i ≤ V F j := by
  refine sInf_le_sInf ?_
  rintro W ⟨hF, hmul⟩
  exact ⟨fun f hf hdeg => hF f hf (hdeg.trans hij),
         fun f hfW g hdeg => hmul f hfW g (hdeg.trans hij)⟩

/-- `V F i` lives inside the polynomials of total degree at most `i`: that
subspace itself satisfies both defining conditions. -/
theorem V_le_restrictTotalDegree (F : Set (MvPolynomial σ k)) (i : ℕ) :
    V F i ≤ restrictTotalDegree σ k i := by
  refine sInf_le ⟨fun f _ hdeg => (mem_restrictTotalDegree ..).2 hdeg, ?_⟩
  intro f hf g hdeg
  exact (mem_restrictTotalDegree ..).2 ((totalDegree_mul f g).trans hdeg)

/-- Hence `d_f ≥ deg f` always, which is what makes a "degree fall" a real
condition rather than a vacuous one. -/
theorem totalDegree_le_of_mem_V {F : Set (MvPolynomial σ k)} {i : ℕ}
    {f : MvPolynomial σ k} (hf : f ∈ V F i) : f.totalDegree ≤ i :=
  (mem_restrictTotalDegree ..).1 (V_le_restrictTotalDegree F i hf)

/-- The degrees at which `f` has appeared. -/
def fallSet (F : Set (MvPolynomial σ k)) (f : MvPolynomial σ k) : Set ℕ :=
  {d | f ∈ V F d}

/-- `d_f`, the least `d` with `f ∈ V F d`.

`Nat.sInf` is `0` on the empty set, so every use below is guarded by a
nonemptiness fact derived from the finiteness hypothesis rather than assumed. -/
noncomputable def degreeFall (F : Set (MvPolynomial σ k))
    (f : MvPolynomial σ k) : ℕ := sInf (fallSet F f)

/-- The `d` witnessing the last fall degree: every element of the ideal appears
by degree `max d (deg f)`. -/
def lastFallSet (F : Set (MvPolynomial σ k)) : Set ℕ :=
  {d | ∀ f ∈ Ideal.span F, f ∈ V F (max d f.totalDegree)}

/-- `d_F`, the last fall degree. -/
noncomputable def lastFallDegree (F : Set (MvPolynomial σ k)) : ℕ :=
  sInf (lastFallSet F)

theorem degreeFall_le {F : Set (MvPolynomial σ k)} {f : MvPolynomial σ k}
    {d : ℕ} (h : f ∈ V F d) : degreeFall F f ≤ d := Nat.sInf_le h

theorem mem_V_degreeFall {F : Set (MvPolynomial σ k)} {f : MvPolynomial σ k}
    (h : (fallSet F f).Nonempty) : f ∈ V F (degreeFall F f) := Nat.sInf_mem h

/-- **Caminata-Gorla, Theorem 2.8.** Assuming `d_F` is finite and `F` has a
degree fall, the last fall degree is exactly the largest degree at which a
degree fall occurs -- and that largest degree is attained. -/
theorem lastFallDegree_eq_max_degreeFall {F : Set (MvPolynomial σ k)}
    (hfin : (lastFallSet F).Nonempty)
    (hfall : ∃ f ∈ Ideal.span F, f.totalDegree < degreeFall F f) :
    IsGreatest
      {d | ∃ f ∈ Ideal.span F, degreeFall F f = d ∧ f.totalDegree < d}
      (lastFallDegree F) := by
  set S := {d | ∃ f ∈ Ideal.span F, degreeFall F f = d ∧ f.totalDegree < d}
    with hSdef
  have hD : lastFallDegree F ∈ lastFallSet F := Nat.sInf_mem hfin
  -- Finiteness of `d_F` is what makes `d_f` meaningful at all.
  have hne : ∀ f ∈ Ideal.span F, (fallSet F f).Nonempty :=
    fun f hf => ⟨max (lastFallDegree F) f.totalDegree, hD f hf⟩
  -- `d_F` bounds every fall degree.
  have hub : ∀ d ∈ S, d ≤ lastFallDegree F := by
    rintro d ⟨f, hf, rfl, hdeg⟩
    have h1 : degreeFall F f ≤ max (lastFallDegree F) f.totalDegree :=
      degreeFall_le (hD f hf)
    rcases max_choice (lastFallDegree F) f.totalDegree with h | h <;> rw [h] at h1
    · exact h1
    · omega
  have hSne : S.Nonempty := by
    obtain ⟨f, hf, hlt⟩ := hfall
    exact ⟨degreeFall F f, f, hf, rfl, hlt⟩
  have hbdd : BddAbove S := ⟨lastFallDegree F, hub⟩
  have hmem : sSup S ∈ S := Nat.sSup_mem hSne hbdd
  -- The maximum itself witnesses the last fall degree, giving `d_F ≤ max`.
  have hlast : sSup S ∈ lastFallSet F := by
    intro f hf
    have hdf : degreeFall F f ≤ max (sSup S) f.totalDegree := by
      rcases lt_or_ge f.totalDegree (degreeFall F f) with hlt | hge
      · exact (le_csSup hbdd ⟨f, hf, rfl, hlt⟩).trans (le_max_left _ _)
      · exact hge.trans (le_max_right _ _)
    exact V_mono F hdf (mem_V_degreeFall (hne f hf))
  have heq : lastFallDegree F = sSup S :=
    le_antisymm (Nat.sInf_le hlast) (hub _ hmem)
  exact ⟨by rw [heq]; exact hmem, hub⟩

end CryptoResearch.FallDegree

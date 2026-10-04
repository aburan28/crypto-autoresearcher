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

/-! ### The defining properties of `V`

`V F i` is an INFIMUM, so it is not automatic that it satisfies the two
conditions defining the family it is the infimum of. Both are preserved by
intersection, which is what makes "the smallest such subspace" well posed and
what makes `V` usable rather than opaque. -/

theorem mem_V_of_mem_of_totalDegree_le {F : Set (MvPolynomial σ k)} {i : ℕ}
    {f : MvPolynomial σ k} (hf : f ∈ F) (hdeg : f.totalDegree ≤ i) :
    f ∈ V F i := by
  rw [V, Submodule.mem_sInf]
  rintro W ⟨hW, -⟩
  exact hW f hf hdeg

theorem mul_mem_V {F : Set (MvPolynomial σ k)} {i : ℕ} {f g : MvPolynomial σ k}
    (hf : f ∈ V F i) (hdeg : f.totalDegree + g.totalDegree ≤ i) :
    f * g ∈ V F i := by
  rw [V, Submodule.mem_sInf]
  intro W hW
  have hfW : f ∈ W := by
    rw [V, Submodule.mem_sInf] at hf
    exact hf W hW
  exact hW.2 f hfW g hdeg

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

/-- **Lower bound on `d_F` from a single exhibited fall.** If some `f` in the
ideal falls -- `d_f > deg f` -- then `d_F` is at least `d_f`.

This is the direction the measurement programme uses: a fall observed at degree
`D` in a per-degree Macaulay rank profile certifies `d_F ≥ D`, with no need to
know `d_F` in advance. -/
theorem le_lastFallDegree_of_degreeFall {F : Set (MvPolynomial σ k)}
    (hfin : (lastFallSet F).Nonempty) {f : MvPolynomial σ k}
    (hf : f ∈ Ideal.span F) (hfall : f.totalDegree < degreeFall F f) :
    degreeFall F f ≤ lastFallDegree F := by
  have hD : lastFallDegree F ∈ lastFallSet F := Nat.sInf_mem hfin
  have h1 : degreeFall F f ≤ max (lastFallDegree F) f.totalDegree :=
    degreeFall_le (hD f hf)
  rcases max_choice (lastFallDegree F) f.totalDegree with h | h <;> rw [h] at h1
  · exact h1
  · omega

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
    exact le_lastFallDegree_of_degreeFall hfin hf hdeg
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

/-! ## Bounds on `d_F`

Theorem 2.8 identifies `d_F`; it does not bound it. These do, in both
directions, and both from Definition 1.5 alone -- no Groebner machinery. -/

/-- `F` admits ideal-membership representations of degree at most `D`: every
`f` in the ideal is `∑ c_g · g` over generators `g ∈ F`, with every term's
degree inside `max D (deg f)`.

SOME representation always exists -- that is `Submodule.mem_span_set` and is
just what generating the ideal means. All the content here is the DEGREE BOUND
on it. -/
def RepresentationDegreeLe (F : Set (MvPolynomial σ k)) (D : ℕ) : Prop :=
  ∀ f ∈ Ideal.span F, ∃ c : MvPolynomial σ k →₀ MvPolynomial σ k,
    (c.support : Set (MvPolynomial σ k)) ⊆ F ∧
    (c.sum fun g r => r • g) = f ∧
    ∀ g ∈ c.support, g.totalDegree + (c g).totalDegree ≤ max D f.totalDegree

theorem mem_V_of_representationDegreeLe {F : Set (MvPolynomial σ k)} {D : ℕ}
    (h : RepresentationDegreeLe F D) {f : MvPolynomial σ k}
    (hf : f ∈ Ideal.span F) : f ∈ V F (max D f.totalDegree) := by
  obtain ⟨c, hsub, hsum, hdeg⟩ := h f hf
  have hmem : (c.sum fun g r => r • g) ∈ V F (max D f.totalDegree) := by
    rw [Finsupp.sum]
    refine Submodule.sum_mem _ fun g hg => ?_
    have hgF : g ∈ F := hsub (Finset.mem_coe.mpr hg)
    have hbound := hdeg g hg
    have hmul : g * c g ∈ V F (max D f.totalDegree) :=
      mul_mem_V (mem_V_of_mem_of_totalDegree_le hgF
        (le_trans (Nat.le_add_right _ _) hbound)) hbound
    simpa [smul_eq_mul, mul_comm] using hmul
  rwa [hsum] at hmem

/-- **Upper bound on the last fall degree.** `d_F` is at most any degree in
which ideal membership can be certified.

The bound is real but it is not small: the representation degree is itself a
hard quantity, doubly exponential in the worst case by effective
Nullstellensatz. What this buys is that `d_F` never exceeds it -- the last fall
degree cannot be worse than writing the membership down. -/
theorem lastFallDegree_le_of_representationDegreeLe {F : Set (MvPolynomial σ k)}
    {D : ℕ} (h : RepresentationDegreeLe F D) : lastFallDegree F ≤ D :=
  Nat.sInf_le fun _ hf => mem_V_of_representationDegreeLe h hf

/-- **Finiteness of `d_F` stops being an assumption.** Theorem 2.8 takes
`(lastFallSet F).Nonempty` as a hypothesis, which Caminata-Gorla obtain from the
existence of a Groebner basis. A representation-degree bound gives it directly,
so Theorem 2.8 can be applied from a checkable hypothesis instead of an assumed
one. -/
theorem lastFallSet_nonempty_of_representationDegreeLe
    {F : Set (MvPolynomial σ k)} {D : ℕ} (h : RepresentationDegreeLe F D) :
    (lastFallSet F).Nonempty :=
  ⟨D, fun _ hf => mem_V_of_representationDegreeLe h hf⟩

/-- **The sandwich.** Every exhibited fall bounds `d_F` below; any
representation degree bounds it above. -/
theorem degreeFall_le_lastFallDegree_le {F : Set (MvPolynomial σ k)} {D : ℕ}
    (h : RepresentationDegreeLe F D) {f : MvPolynomial σ k}
    (hf : f ∈ Ideal.span F) (hfall : f.totalDegree < degreeFall F f) :
    degreeFall F f ≤ lastFallDegree F ∧ lastFallDegree F ≤ D :=
  ⟨le_lastFallDegree_of_degreeFall
      (lastFallSet_nonempty_of_representationDegreeLe h) hf hfall,
    lastFallDegree_le_of_representationDegreeLe h⟩

end CryptoResearch.FallDegree

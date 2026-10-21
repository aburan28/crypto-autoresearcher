/-
Translations that descend through a degree-2 quotient of an elliptic curve.

Source:  research/THM_QUOTIENT_DESCENT1.md, Lemma and "Formal target"
Target:  formal/targets/quotient-translation-descent.yaml

For S, T in E, write ι_S(P) = -(P + S) (the involution [-1] ∘ τ_S) and
τ_T(P) = P + T. Translation by T commutes with ι_S, which for a degree-2
quotient is exactly "τ_T descends through E/⟨ι_S⟩", if and only if 2T = 0.

WHAT IS PROVED. The group-law identity above, in any additive commutative
group. It is stated for every S: the note's earlier hypothesis 2•S = 0 is not
used by the proof and is dropped, which makes this statement STRONGER than the
one first written (an S of any order gives an involution ι_S). This replaces
the unchecked statement stub that was research/THM_QUOTIENT_DESCENT1.lean.

WHAT IS NOT PROVED. That every degree-2 map E → P^1 is such a quotient, and
that "descends" is equivalent to "commutes with ι_S" (the fibre argument in
the note's proof). Those are algebraic geometry, argued in prose in the note,
and are not formalized here; nor is the note's corollary on summation
polynomials.
-/
import Mathlib.Tactic.Abel

universe u

namespace CryptoResearch.Quotient

/-- Translation by `T` commutes with `ι_S = [-1] ∘ τ_S` (i.e. descends through
the degree-2 quotient by `ι_S`) if and only if `2 • T = 0`, for every `S`. -/
theorem translation_descends_iff_two_torsion {E : Type u} [AddCommGroup E] (S T : E) :
    (∀ P : E, -(P + S) + T = -(P + T + S)) ↔ (2 : ℕ) • T = 0 := by
  constructor
  · intro h
    -- At P = 0: -S + T = -(T + S), and the difference of the two sides is 2 • T.
    have key : (2 : ℕ) • T = (-((0 : E) + S) + T) - -((0 : E) + T + S) := by abel
    first
      | rw [key, h 0, sub_self]
      | (rw [key, h 0]; abel)
  · intro hT P
    have key : -(P + S) + T = -(P + T + S) + (2 : ℕ) • T := by abel
    first
      | rw [key, hT, add_zero]
      | (rw [key, hT]; abel)

end CryptoResearch.Quotient

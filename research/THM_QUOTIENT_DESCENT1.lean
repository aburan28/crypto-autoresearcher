/-
  THM_QUOTIENT_DESCENT1 — statement stub matching
  research/THM_QUOTIENT_DESCENT1.md § Formal target.
  Not yet checked against a Lean/mathlib toolchain.
  Coordinator mints: CryptoResearch.Quotient.translation_descends_iff_two_torsion
-/

/-- Translation by `T` descends through the degree-2 quotient by ι_S
    (ι_S = [-1] ∘ τ_S) if and only if `2•T = 0`. -/
axiom translation_descends_iff_two_torsion
    {E : Type*} [AddCommGroup E]
    (S T : E)
    (hS : 2 • S = 0) :
    (∀ P : E, -(P + S) + T = -(P + T + S)) ↔ (2 • T = 0)

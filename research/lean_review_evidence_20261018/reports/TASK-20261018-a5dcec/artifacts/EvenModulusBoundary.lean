import CryptoResearch.NCP.CommutatorIdeal
set_option autoImplicit false
namespace IndependentJ2Even
open CryptoResearch.NCP

def t : WordAlgebra 1 := FreeAlgebra.ι ℤ (some 0)
def sourceFiniteJ : TwoSidedIdeal (WordAlgebra 1) := TwoSidedIdeal.span
  {z | z = negLetter 1 ^ 2 - 1 ∨ z = (negLetter 1 * t) ^ 2 - 1 ∨ z = t ^ 2 - 1}
def parityEval : WordAlgebra 1 →ₐ[ℤ] ℤ :=
  FreeAlgebra.lift ℤ (fun i => match i with | none => -1 | some _ => 1)

theorem extra_action_relation :
    negLetter 1 - 1 ∈ TwoSidedIdeal.ker
      (actionEvaluation (fun _ : Fin 1 => (1 : ZMod 2))).toRingHom := by
  have hn : affineNeg 2 = 1 := by
    apply Subtype.ext
    ext x
    exact (by decide : ∀ z : ZMod 2, -z = z) x
  rw [TwoSidedIdeal.mem_ker, map_sub, map_one]
  simp [actionEvaluation, negLetter, hn]
  change (1 : MonoidAlgebra ℤ (affineGroup 2)) - 1 = 0
  exact sub_self _

theorem extra_relation_not_in_sourceFiniteJ : negLetter 1 - 1 ∉ sourceFiniteJ := by
  have hle : sourceFiniteJ ≤ TwoSidedIdeal.ker parityEval.toRingHom := by
    apply TwoSidedIdeal.span_le.mpr
    rintro z (rfl | rfl | rfl) <;>
      apply (TwoSidedIdeal.mem_ker parityEval.toRingHom).mpr <;>
      norm_num [parityEval, negLetter, t]
  intro h
  have hz := (TwoSidedIdeal.mem_ker parityEval.toRingHom).mp (hle h)
  norm_num [parityEval, negLetter] at hz

#print axioms extra_action_relation
#print axioms extra_relation_not_in_sourceFiniteJ
end IndependentJ2Even

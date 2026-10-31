import CryptoResearch.NCP.Reachability
import CryptoResearch.NCP.PointAction

set_option autoImplicit false
namespace CryptoResearch.NCP.Controls
open CryptoResearch.NCP

theorem empty_positive :
    ∃ w : List (Letter 0), w.length ≤ 0 ∧ shadowSign w = 1 ∧
      ∀ i : Fin 0, signedCount w i = 0 := by
  rw [shadow_reachable_iff 1 (fun _ : Fin 0 => (0 : Int)) (Or.inl rfl) 0]
  decide

theorem empty_negative :
    ∃ w : List (Letter 0), w.length ≤ 1 ∧ shadowSign w = -1 ∧
      ∀ i : Fin 0, signedCount w i = 0 := by
  rw [shadow_reachable_iff (-1) (fun _ : Fin 0 => (0 : Int)) (Or.inr rfl) 1]
  decide

private def mixedVector : Fin 2 → Int := fun i => if i.val = 0 then -1 else 2

theorem mixed_positive_minimum :
    vectorWeight mixedVector + shadowPenalty 1 mixedVector = 5 := by decide

theorem mixed_negative_minimum :
    vectorWeight mixedVector + shadowPenalty (-1) mixedVector = 4 := by decide

theorem mixed_positive_unreachable_at_four :
    ¬ ∃ w : List (Letter 2), w.length ≤ 4 ∧ shadowSign w = 1 ∧
      ∀ i : Fin 2, signedCount w i = mixedVector i := by
  rw [shadow_reachable_iff 1 mixedVector (Or.inl rfl) 4]
  decide

/-- Negation and translation expose a reversed composition convention. -/
theorem chronological_order_matters :
    wordPointAction (fun _ : Fin 1 => (1 : Int)) [.trans 0, .neg] 0 = -1 ∧
    wordPointAction (fun _ : Fin 1 => (1 : Int)) [.neg, .trans 0] 0 = 1 := by decide
end CryptoResearch.NCP.Controls

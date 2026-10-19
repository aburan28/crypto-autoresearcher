import CryptoResearch.NCP.Reachability
import CryptoResearch.NCP.PointAction

set_option autoImplicit false
namespace CryptoResearch.NCP.Controls
open CryptoResearch.NCP

theorem empty_positive :
    (shadowWord 1 (fun _ : Fin 0 => (0 : ℤ))).length = 0 := by decide

theorem empty_negative :
    (shadowWord (-1) (fun _ : Fin 0 => (0 : ℤ))).length = 1 := by decide

theorem mixed_positive_minimum :
    shadowL1 (![(-1 : ℤ), 2] : Fin 2 → ℤ) + minNegations 1 ![-1, 2] = 5 := by decide

theorem mixed_negative_minimum :
    shadowL1 (![(-1 : ℤ), 2] : Fin 2 → ℤ) + minNegations (-1) ![-1, 2] = 4 := by decide

theorem mixed_positive_unreachable_at_four :
    ¬ ∃ w : List (Letter 2), w.length ≤ 4 ∧ wordSign w = 1 ∧ signedCounts w = ![-1, 2] := by
  rw [shadow_reachable_iff 1 ![-1, 2] (Or.inl rfl) 4]
  decide

/-- Negation and translation expose a reversed composition convention. -/
theorem chronological_order_matters :
    wordPointAction (fun _ : Fin 1 => (1 : ℤ)) [.translate 0, .negate] 0 = -1 ∧
    wordPointAction (fun _ : Fin 1 => (1 : ℤ)) [.negate, .translate 0] 0 = 1 := by decide
end CryptoResearch.NCP.Controls

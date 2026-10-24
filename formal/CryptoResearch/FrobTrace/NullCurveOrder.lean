import Mathlib.Tactic

/-!
Arithmetic uniqueness certificates for the five FROB C4 null-curve candidates.

Each theorem assumes an independently checked Hasse interval and a divisor of
the elliptic-curve order obtained from point-order witnesses. It proves only
that those premises force the archived order. The field, curve, point-order,
and Hasse premises are not constructed or proved by this module.
-/

namespace CryptoResearch.FrobTrace.NullCurveOrder

theorem q11_accepted {order : ℕ}
    (hlo : 160250 ≤ order) (hhi : order ≤ 161854)
    (hpoint : 40161 ∣ order) : order = 160644 := by
  rcases hpoint with ⟨k, rfl⟩
  omega

theorem q13_rejected {order : ℕ}
    (hlo : 370076 ≤ order) (hhi : order ≤ 372512)
    (hpoint : 370778 ∣ order) : order = 370778 := by
  rcases hpoint with ⟨k, rfl⟩
  omega

theorem q13_accepted {order : ℕ}
    (hlo : 370076 ≤ order) (hhi : order ≤ 372512)
    (hpoint : 92605 ∣ order) : order = 370420 := by
  rcases hpoint with ⟨k, rfl⟩
  omega

theorem q19_rejected {order : ℕ}
    (hlo : 2472953 ≤ order) (hhi : order ≤ 2479247)
    (hpoint : 1237500 ∣ order) : order = 2475000 := by
  rcases hpoint with ⟨k, rfl⟩
  omega

theorem q19_accepted {order : ℕ}
    (hlo : 2472953 ≤ order) (hhi : order ≤ 2479247)
    (hpoint : 619165 ∣ order) : order = 2476660 := by
  rcases hpoint with ⟨k, rfl⟩
  omega

/-- One target bundles the five conditional certificates for exact theorem audit. -/
theorem all_five_unique :
    (∀ order : ℕ, 160250 ≤ order → order ≤ 161854 → 40161 ∣ order → order = 160644) ∧
    (∀ order : ℕ, 370076 ≤ order → order ≤ 372512 → 370778 ∣ order → order = 370778) ∧
    (∀ order : ℕ, 370076 ≤ order → order ≤ 372512 → 92605 ∣ order → order = 370420) ∧
    (∀ order : ℕ, 2472953 ≤ order → order ≤ 2479247 → 1237500 ∣ order → order = 2475000) ∧
    (∀ order : ℕ, 2472953 ≤ order → order ≤ 2479247 → 619165 ∣ order → order = 2476660) := by
  refine ⟨?_, ?_, ?_, ?_, ?_⟩
  · intro order hlo hhi hpoint
    exact q11_accepted hlo hhi hpoint
  · intro order hlo hhi hpoint
    exact q13_rejected hlo hhi hpoint
  · intro order hlo hhi hpoint
    exact q13_accepted hlo hhi hpoint
  · intro order hlo hhi hpoint
    exact q19_rejected hlo hhi hpoint
  · intro order hlo hhi hpoint
    exact q19_accepted hlo hhi hpoint

end CryptoResearch.FrobTrace.NullCurveOrder

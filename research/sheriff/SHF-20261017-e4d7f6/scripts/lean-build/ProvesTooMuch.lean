/- Proves-too-much controls (sheriff re-audit). Each is FALSE in general and
   reuses the producer's proof script verbatim; each must FAIL to elaborate. -/
import Mathlib.Tactic.Abel
universe u
-- (a) 3 instead of 2: false in Z/2 (T = 1: commutation holds, 3•1 = 1 ≠ 0).
theorem ptm_three {E : Type u} [AddCommGroup E] (S T : E) :
    (∀ P : E, -(P + S) + T = -(P + T + S)) ↔ (3 : ℕ) • T = 0 := by
  constructor
  · intro h
    have key : (3 : ℕ) • T = (-((0 : E) + S) + T) - -((0 : E) + T + S) := by abel
    first
      | rw [key, h 0, sub_self]
      | (rw [key, h 0]; abel)
  · intro hT P
    have key : -(P + S) + T = -(P + T + S) + (3 : ℕ) • T := by abel
    first
      | rw [key, hT, add_zero]
      | (rw [key, hT]; abel)
-- (b) T = 0 instead of 2•T = 0: false in Z/2 (T = 1).
theorem ptm_zero {E : Type u} [AddCommGroup E] (S T : E) :
    (∀ P : E, -(P + S) + T = -(P + T + S)) ↔ T = 0 := by
  constructor
  · intro h
    have key : T = (-((0 : E) + S) + T) - -((0 : E) + T + S) := by abel
    first
      | rw [key, h 0, sub_self]
      | (rw [key, h 0]; abel)
  · intro hT P
    have key : -(P + S) + T = -(P + T + S) + T := by abel
    first
      | rw [key, hT, add_zero]
      | (rw [key, hT]; abel)

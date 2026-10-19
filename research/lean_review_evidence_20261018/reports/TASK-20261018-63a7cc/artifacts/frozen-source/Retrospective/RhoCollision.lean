import Mathlib.Algebra.Field.ZMod
import Mathlib.Tactic.Ring

set_option autoImplicit false

namespace Retrospective.Rho

/-- The coefficient relation in src/rho.c, sign=0. Over a prime-order scalar
field, every collision with distinct b coefficients determines the scalar. -/
theorem recover {F : Type*} [Field F] (a₁ b₁ a₂ b₂ x : F)
    (h : a₁ + b₁ * x = a₂ + b₂ * x) (hb : b₁ ≠ b₂) :
    x = (a₂ - a₁) / (b₁ - b₂) := by
  apply (eq_div_iff (sub_ne_zero.mpr hb)).mpr
  calc
    x * (b₁ - b₂) = (a₁ + b₁ * x) - (a₂ + b₂ * x) + (a₂ - a₁) := by ring
    _ = a₂ - a₁ := by rw [h]; ring

/-- The negation-orbit branch, with its different sign and denominator. -/
theorem recover_negated {F : Type*} [Field F] (a₁ b₁ a₂ b₂ x : F)
    (h : a₁ + b₁ * x = -(a₂ + b₂ * x)) (hb : b₁ + b₂ ≠ 0) :
    x = -(a₁ + a₂) / (b₁ + b₂) := by
  apply (eq_div_iff hb).mpr
  calc
    x * (b₁ + b₂) = (a₁ + b₁ * x) + (a₂ + b₂ * x) - (a₁ + a₂) := by ring
    _ = -(a₁ + a₂) := by rw [h]; ring

/-- The collision equation comes from actual cyclic group arithmetic through
an injective additive embedding of the prime-order scalar field. -/
theorem group_collision_recover (p : ℕ) [Fact p.Prime]
    {A : Type*} [AddCommGroup A] (encode : ZMod p →+ A)
    (hinj : Function.Injective encode) (a₁ b₁ a₂ b₂ x : ZMod p)
    (h : encode a₁ + encode (b₁ * x) = encode a₂ + encode (b₂ * x))
    (hb : b₁ ≠ b₂) : x = (a₂ - a₁) / (b₁ - b₂) := by
  apply recover a₁ b₁ a₂ b₂ x _ hb
  apply hinj
  simpa using h

/-- Proves-too-much control: removing the nonzero-coefficient condition
would incorrectly claim scalar recovery for this noninjective map. -/
theorem zero_coefficient_not_injective :
    ¬ Function.Injective (fun x : ZMod 7 => 0 + 0*x) := by
  intro h
  have h01 : (0 : ZMod 7) = 1 := h (by simp)
  exact (by decide : (0 : ZMod 7) ≠ 1) h01

end Retrospective.Rho

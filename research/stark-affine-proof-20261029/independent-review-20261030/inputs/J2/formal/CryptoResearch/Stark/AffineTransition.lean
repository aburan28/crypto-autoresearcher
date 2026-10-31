import Mathlib.Algebra.Ring.Basic
import Mathlib.Data.ZMod.Basic

/-!
Source: research/stark-affine-proof-20261029/CLAIMS.md.
Models the field-valued expression in crypto's typed AffineTransition API.
No theorem here proves Rust execution, byte encoding, or STARK soundness.
-/
namespace CryptoResearch.Stark.AffineTransition

variable {R : Type*} [CommRing R]

def evaluate (a b c x y : R) : R := a * x + b * y + c

/-- The three designated evaluations recover the complete coefficient tuple. -/
theorem recover_coefficients (a b c : R) :
    (evaluate a b c 1 0 - evaluate a b c 0 0,
     evaluate a b c 0 1 - evaluate a b c 0 0,
     evaluate a b c 0 0) = (a, b, c) := by
  simp [evaluate]

theorem coefficients_eq_of_probes (a b c a' b' c' : R)
    (h00 : evaluate a b c 0 0 = evaluate a' b' c' 0 0)
    (h10 : evaluate a b c 1 0 = evaluate a' b' c' 1 0)
    (h01 : evaluate a b c 0 1 = evaluate a' b' c' 0 1) :
    (a, b, c) = (a', b', c') := by
  calc
    (a, b, c) =
        (evaluate a b c 1 0 - evaluate a b c 0 0,
         evaluate a b c 0 1 - evaluate a b c 0 0,
         evaluate a b c 0 0) := (recover_coefficients a b c).symm
    _ = (evaluate a' b' c' 1 0 - evaluate a' b' c' 0 0,
         evaluate a' b' c' 0 1 - evaluate a' b' c' 0 0,
         evaluate a' b' c' 0 0) := by rw [h00, h10, h01]
    _ = (a', b', c') := recover_coefficients a' b' c'

/-- Equality on the three designated probes implies equality everywhere. -/
theorem three_probe_extensionality (a b c a' b' c' : R)
    (h00 : evaluate a b c 0 0 = evaluate a' b' c' 0 0)
    (h10 : evaluate a b c 1 0 = evaluate a' b' c' 1 0)
    (h01 : evaluate a b c 0 1 = evaluate a' b' c' 0 1) :
    ∀ x y : R, evaluate a b c x y = evaluate a' b' c' x y := by
  have h := coefficients_eq_of_probes a b c a' b' c' h00 h10 h01
  have ha : a = a' := congrArg Prod.fst h
  have hb : b = b' := congrArg (fun p : R × R × R => p.2.1) h
  have hc : c = c' := congrArg (fun p : R × R × R => p.2.2) h
  intro x y
  simp only [evaluate, ha, hb, hc]

/-- Global nonagreement, proved using the historical four designated points. -/
theorem multiplication_not_affine [Nontrivial R] (a b c : R) :
    ¬ (∀ x y : R, evaluate a b c x y = x * y) := by
  intro h
  have hc : c = 0 := by simpa [evaluate] using h 0 0
  have ha : a = 0 := by simpa [evaluate, hc] using h 1 0
  have hb : b = 0 := by simpa [evaluate, hc] using h 0 1
  have hbad : (0 : R) = 1 := by simpa [evaluate, ha, hb, hc] using h 1 1
  exact zero_ne_one hbad

/-- The exact finite-point obstruction asserted by the historical Rust test. -/
theorem multiplication_not_affine_on_four_probes [Nontrivial R] (a b c : R) :
    ¬ (evaluate a b c 0 0 = 0 * 0 ∧
       evaluate a b c 1 0 = 1 * 0 ∧
       evaluate a b c 0 1 = 0 * 1 ∧
       evaluate a b c 1 1 = 1 * 1) := by
  intro h
  have hc : c = 0 := by simpa [evaluate] using h.1
  have ha : a = 0 := by simpa [evaluate, hc] using h.2.1
  have hb : b = 0 := by simpa [evaluate, hc] using h.2.2.1
  have hbad : (0 : R) = 1 := by simpa [evaluate, ha, hb, hc] using h.2.2.2
  exact zero_ne_one hbad

/-- Removing the third probe permits distinct affine transitions. -/
theorem two_probes_insufficient [Nontrivial R] :
    evaluate (0 : R) 0 0 0 0 = evaluate 0 1 0 0 0 ∧
    evaluate (0 : R) 0 0 1 0 = evaluate 0 1 0 1 0 ∧
    evaluate (0 : R) 0 0 0 1 ≠ evaluate 0 1 0 0 1 := by
  simp [evaluate]

/-- Nontriviality cannot be removed from the multiplication obstruction. -/
theorem zero_ring_product_control (x y : ZMod 1) :
    evaluate 0 0 0 x y = x * y := by
  exact Subsingleton.elim _ _

set_option pp.universes true
set_option pp.explicit true
#check @recover_coefficients
#check @coefficients_eq_of_probes
#check @three_probe_extensionality
#check @multiplication_not_affine
#check @two_probes_insufficient
#check @zero_ring_product_control
#check @multiplication_not_affine_on_four_probes

-- Native negative control: this application would prove False in the zero ring
-- if the multiplication obstruction did not require Nontrivial R.
-- #check_failure itself fails elaboration if the term is accepted.
#check_failure
  (multiplication_not_affine (R := ZMod 1) 0 0 0
    (fun x y => zero_ring_product_control x y) : False)

#check_failure
  (multiplication_not_affine_on_four_probes (R := ZMod 1) 0 0 0
    ⟨zero_ring_product_control 0 0, zero_ring_product_control 1 0,
     zero_ring_product_control 0 1, zero_ring_product_control 1 1⟩ : False)

#print axioms recover_coefficients
#print axioms coefficients_eq_of_probes
#print axioms three_probe_extensionality
#print axioms multiplication_not_affine
#print axioms two_probes_insufficient
#print axioms zero_ring_product_control
#print axioms multiplication_not_affine_on_four_probes

end CryptoResearch.Stark.AffineTransition

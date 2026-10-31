import CryptoResearch.NCP.AffineNormalForm
import Mathlib.Tactic.Abel

set_option autoImplicit false
namespace CryptoResearch.NCP
variable {B : ℕ} {A : Type*} [AddCommGroup A]

/-- The same chronological word, executed on actual additive-group points. -/
def wordPointAction (points : Fin B → A) : List (Letter B) → A → A
  | [], X => X
  | .trans i :: w, X => wordPointAction points w (X + points i)
  | .neg :: w, X => wordPointAction points w (-X)

theorem wordPointAction_append (points : Fin B → A) (u v : List (Letter B)) (X : A) :
    wordPointAction points (u ++ v) X = wordPointAction points v (wordPointAction points u X) := by
  induction u generalizing X with
  | nil => rfl
  | cons l u ih => cases l <;> simp only [List.cons_append, wordPointAction, ih]

private theorem wordPointAction_eq_groupWordAction (points : Fin B → A)
    (w : List (Letter B)) (X : A) :
    wordPointAction points w X = groupWordAction points w X := by
  induction w generalizing X with
  | nil => rfl
  | cons l w ih =>
    cases l with
    | trans i =>
      change wordPointAction points w (X + points i) = groupWordAction points w (X + points i)
      exact ih (X + points i)
    | neg =>
      change wordPointAction points w (-X) = groupWordAction points w (-X)
      exact ih (-X)

theorem word_point_affine_normal_form (points : Fin B → A) (w : List (Letter B)) (X : A) :
    wordPointAction points w X = shadowSign w • X + ∑ i, signedCount w i • points i := by
  rw [wordPointAction_eq_groupWordAction]
  exact group_word_action_affine_normal_form points w X

/-- Soundness of the scalar instrument under an additive encoding; the
encoding's construction and injectivity are separate, explicit obligations. -/
theorem word_action_encode {n : ℕ} (encode : ZMod n →+ A)
    (s : Fin B → ZMod n) (w : List (Letter B)) (x : ZMod n) :
    wordPointAction (fun i => encode (s i)) w (encode x) = encode (wordAction s w x) := by
  induction w generalizing x with
  | nil => rfl
  | cons l w ih =>
    cases l with
    | trans i =>
      simpa only [wordPointAction, wordAction, actLetter, List.foldl_cons, map_add] using ih (x + s i)
    | neg =>
      simpa only [wordPointAction, wordAction, actLetter, List.foldl_cons, map_neg] using ih (-x)
end CryptoResearch.NCP

import CryptoResearch.NCP.AffineNormalForm
import Mathlib.Tactic.Abel

set_option autoImplicit false
namespace CryptoResearch.NCP
variable {B : ℕ} {A : Type*} [AddCommGroup A]

/-- The same chronological word, executed on actual additive-group points. -/
def wordPointAction (points : Fin B → A) : List (Letter B) → A → A
  | [], X => X
  | .translate i :: w, X => wordPointAction points w (X + points i)
  | .negate :: w, X => wordPointAction points w (-X)

theorem wordPointAction_append (points : Fin B → A) (u v : List (Letter B)) (X : A) :
    wordPointAction points (u ++ v) X = wordPointAction points v (wordPointAction points u X) := by
  induction u generalizing X with
  | nil => rfl
  | cons l u ih => cases l <;> simp only [List.cons_append, wordPointAction, ih]

theorem word_point_affine_normal_form (points : Fin B → A) (w : List (Letter B)) (X : A) :
    wordPointAction points w X = wordSign w • X + ∑ i, signedCounts w i • points i := by
  induction w generalizing X with
  | nil => simp [wordPointAction, wordSign, signedCounts]
  | cons l w ih =>
    cases l with
    | translate j =>
      rw [wordPointAction, ih]
      simp only [wordSign, signedCounts, add_zsmul, zsmul_add, ite_smul,
        zero_zsmul, Finset.sum_add_distrib]
      simp only [Finset.sum_ite_eq, Finset.mem_univ, ite_true]
      abel
    | negate =>
      rw [wordPointAction, ih]
      simp [wordSign, signedCounts]

/-- Soundness of the scalar instrument under any additive encoding; the
encoding's construction and injectivity are separate, explicit obligations. -/
theorem word_action_encode {R : Type*} [CommRing R] (encode : R →+ A)
    (s : Fin B → R) (w : List (Letter B)) (x : R) :
    wordPointAction (fun i => encode (s i)) w (encode x) = encode (wordAction s w x) := by
  induction w generalizing x with
  | nil => rfl
  | cons l w ih =>
    cases l with
    | translate i => simpa only [wordPointAction, wordAction, map_add] using ih (x + s i)
    | negate => simpa only [wordPointAction, wordAction, map_neg] using ih (-x)
end CryptoResearch.NCP

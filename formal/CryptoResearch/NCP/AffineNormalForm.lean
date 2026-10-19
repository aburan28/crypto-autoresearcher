import Mathlib.Algebra.Field.ZMod
import Mathlib.Tactic.Ring

set_option autoImplicit false

namespace CryptoResearch.NCP

inductive Letter (B : ℕ) where
  | translate (i : Fin B)
  | negate
  deriving DecidableEq

variable {B : ℕ}

/-- Letters execute left to right, as in the source note and frozen instrument. -/
def wordAction {R : Type*} [CommRing R] (s : Fin B → R) : List (Letter B) → R → R
  | [], x => x
  | .translate i :: w, x => wordAction s w (x + s i)
  | .negate :: w, x => wordAction s w (-x)

def wordSign : List (Letter B) → ℤ
  | [] => 1
  | .translate _ :: w => wordSign w
  | .negate :: w => -wordSign w

/-- Each translation occurrence contributes the sign of its suffix. Thus an
occurrence is signed by the number of negations strictly to its right. -/
def signedCounts : List (Letter B) → Fin B → ℤ
  | [], _ => 0
  | .translate i :: w, j => signedCounts w j + if i = j then wordSign w else 0
  | .negate :: w, j => signedCounts w j

theorem wordSign_eq_negOne_pow (w : List (Letter B)) :
    wordSign w = (-1 : ℤ) ^ w.count .negate := by
  induction w with
  | nil => simp [wordSign]
  | cons a w ih =>
    cases a <;> simp [wordSign, ih, pow_succ]

/-- Lemma 1, for every word, every starting scalar and every commutative
ring, in particular ZMod n for every positive n. -/
theorem word_action_affine_normal_form {R : Type*} [CommRing R]
    (s : Fin B → R) (w : List (Letter B)) (x : R) :
    wordAction s w x = (wordSign w : R) * x +
      ∑ i, (signedCounts w i : R) * s i := by
  induction w generalizing x with
  | nil => simp [wordAction, wordSign, signedCounts]
  | cons a w ih =>
    cases a with
    | translate j =>
      rw [wordAction, ih]
      simp only [wordSign, signedCounts, Int.cast_add, Int.cast_ite,
        Int.cast_zero, add_mul, Finset.sum_add_distrib]
      simp only [ite_mul, zero_mul, Finset.sum_ite_eq, Finset.mem_univ, ite_true]
      ring
    | negate =>
      rw [wordAction, ih]
      simp only [wordSign, signedCounts, Int.cast_neg]
      ring

theorem same_shadow_same_action {R : Type*} [CommRing R]
    (s : Fin B → R) (w w' : List (Letter B))
    (he : wordSign w = wordSign w') (ha : signedCounts w = signedCounts w') :
    wordAction s w = wordAction s w' := by
  funext x
  rw [word_action_affine_normal_form, word_action_affine_normal_form, he, ha]

theorem orbit_value {n : ℕ} (s : Fin B → ZMod n) (w : List (Letter B)) :
    wordAction s w 1 = (wordSign w : ZMod n) +
      ∑ i, (signedCounts w i : ZMod n) * s i := by
  simpa using word_action_affine_normal_form s w 1

end CryptoResearch.NCP

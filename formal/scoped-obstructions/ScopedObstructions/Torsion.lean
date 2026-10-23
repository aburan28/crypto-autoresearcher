/- Odd torsion translation under explicit additive laws. No elliptic-curve bridge is assumed. -/
namespace ScopedObstructions

structure AdditiveModel (A : Type u) where
  zero : A
  add : A → A → A
  zero_add : ∀ a, add zero a = a
  add_zero : ∀ a, add a zero = a
  assoc : ∀ a b c, add (add a b) c = add a (add b c)
  comm : ∀ a b, add a b = add b a

namespace AdditiveModel
variable {A : Type u} (M : AdditiveModel A)

def multiple (M : AdditiveModel A) : Nat → A → A
  | 0, _ => M.zero
  | n + 1, a => M.add (multiple M n a) a

theorem interchange (a b c d : A) :
    M.add (M.add a b) (M.add c d) = M.add (M.add a c) (M.add b d) := by
  rw [M.assoc a b (M.add c d), ← M.assoc b c d, M.comm b c,
      M.assoc c b d, ← M.assoc a c (M.add b d)]

theorem multiple_zero (n : Nat) : M.multiple n M.zero = M.zero := by
  induction n with
  | zero => rfl
  | succ n ih =>
    change M.add (M.multiple n M.zero) M.zero = M.zero
    rw [ih, M.zero_add]

theorem multiple_sum (n : Nat) (a b : A) :
    M.multiple n (M.add a b) = M.add (M.multiple n a) (M.multiple n b) := by
  induction n with
  | zero => exact (M.zero_add M.zero).symm
  | succ n ih =>
    change M.add (M.multiple n (M.add a b)) (M.add a b) =
      M.add (M.add (M.multiple n a) a) (M.add (M.multiple n b) b)
    rw [ih, M.interchange]

theorem multiple_add (n m : Nat) (a : A) :
    M.multiple (n + m) a = M.add (M.multiple n a) (M.multiple m a) := by
  induction m with
  | zero => exact (M.add_zero (M.multiple n a)).symm
  | succ m ih =>
    change M.add (M.multiple (n + m) a) a =
      M.add (M.multiple n a) (M.add (M.multiple m a) a)
    rw [ih, M.assoc]

theorem odd_multiple_of_two_torsion (k : Nat) (T : A)
    (two_T : M.add T T = M.zero) : M.multiple (k + k + 1) T = T := by
  have doubled : M.add (M.multiple k T) (M.multiple k T) = M.zero := by
    calc
      M.add (M.multiple k T) (M.multiple k T) = M.multiple k (M.add T T) :=
        (M.multiple_sum k T T).symm
      _ = M.multiple k M.zero := congrArg (M.multiple k) two_T
      _ = M.zero := M.multiple_zero k
  change M.add (M.multiple (k + k) T) T = T
  rw [M.multiple_add, doubled, M.zero_add]

/-- An odd scalar sends P+T to T when it annihilates P and 2T=0. -/
theorem odd_translation (r : Nat) (P T : A)
    (odd_r : ∃ k, r = k + k + 1)
    (annihilates_P : M.multiple r P = M.zero)
    (two_T : M.add T T = M.zero) : M.multiple r (M.add P T) = T := by
  obtain ⟨k, rfl⟩ := odd_r
  rw [M.multiple_sum, annihilates_P, M.odd_multiple_of_two_torsion k T two_T,
      M.zero_add]

/-- P+T is outside the zero-kernel of the odd scalar when T is nonzero. -/
theorem odd_translation_outside_kernel (r : Nat) (P T : A)
    (odd_r : ∃ k, r = k + k + 1)
    (annihilates_P : M.multiple r P = M.zero)
    (two_T : M.add T T = M.zero) (T_nonzero : T ≠ M.zero) :
    M.multiple r (M.add P T) ≠ M.zero := by
  rw [M.odd_translation r P T odd_r annihilates_P two_T]
  exact T_nonzero

end AdditiveModel

/-- A non-vacuous two-element additive model. -/
def xorModel : AdditiveModel Bool where
  zero := false
  add := Bool.xor
  zero_add := by intro a; cases a <;> rfl
  add_zero := by intro a; cases a <;> rfl
  assoc := by intro a b c; cases a <;> cases b <;> cases c <;> rfl
  comm := by intro a b; cases a <;> cases b <;> rfl

theorem positive_control :
    xorModel.multiple 3 (xorModel.add false true) ≠ xorModel.zero :=
  xorModel.odd_translation_outside_kernel 3 false true
    ⟨1, rfl⟩ rfl rfl (by decide)

/-- Oddness matters: the even scalar instead annihilates T. -/
theorem even_scalar_control :
    xorModel.multiple 2 (xorModel.add false true) = xorModel.zero := rfl

end ScopedObstructions

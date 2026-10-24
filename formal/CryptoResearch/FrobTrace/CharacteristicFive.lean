import Mathlib.Tactic

/-!
A characteristic-five negative control for the EXP-FROB-91ee9c C5
factor-kernel argument. In characteristic five, `X^5 - 1` has one
repeated root, so the coprime-factor kernel decomposition used for the
archived q=11, 13, and 19 cells cannot be copied to q=5.

These polynomial facts do not check the archived quotient-field code or
change any empirical result.
-/

open Polynomial

namespace CryptoResearch.FrobTrace.CharacteristicFive

local instance : Fact (Nat.Prime 5) := ⟨by decide⟩

/-- In characteristic five, the fifth roots of unity collapse to a
single root of multiplicity five. -/
theorem x_pow_five_sub_one_repeated :
    (X - 1 : (ZMod 5)[X]) ^ 5 = X ^ 5 - 1 := by
  simpa using (sub_pow_char (p := 5) (x := (X : (ZMod 5)[X])) (y := 1))

/-- The nontrivial degree-four factor also has a repeated root. -/
theorem nontrivial_factor_repeated :
    (X - 1 : (ZMod 5)[X]) ^ 4 = X ^ 4 + X ^ 3 + X ^ 2 + X + 1 := by
  ring_nf
  have h4 : (4 : (ZMod 5)[X]) = -1 := by
    calc
      (4 : (ZMod 5)[X]) = C (4 : ZMod 5) := (C_eq_natCast 4).symm
      _ = C (-1 : ZMod 5) := congrArg C (by decide)
      _ = -1 := by simp
  have h6 : (6 : (ZMod 5)[X]) = 1 := by
    calc
      (6 : (ZMod 5)[X]) = C (6 : ZMod 5) := (C_eq_natCast 6).symm
      _ = C (1 : ZMod 5) := congrArg C (by decide)
      _ = 1 := by simp
  rw [h4, h6]
  ring

/-- The exact squarefreeness premise behind a coprime-factor argument
fails at characteristic five. -/
theorem x_pow_five_sub_one_not_squarefree :
    ¬ Squarefree (X ^ 5 - 1 : (ZMod 5)[X]) := by
  intro h
  have hu : IsUnit (X - 1 : (ZMod 5)[X]) := h (X - 1) (by
    rw [← x_pow_five_sub_one_repeated]
    refine ⟨(X - 1) ^ 3, ?_⟩
    ring)
  have hdeg : (X - 1 : (ZMod 5)[X]).natDegree = 1 := by
    simpa using (natDegree_X_sub_C (1 : ZMod 5))
  exact (not_isUnit_of_natDegree_pos (X - 1 : (ZMod 5)[X]) (by omega)) hu

end CryptoResearch.FrobTrace.CharacteristicFive

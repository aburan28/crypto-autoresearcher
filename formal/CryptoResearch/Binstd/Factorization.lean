import Mathlib.Algebra.Polynomial.Basic
import Mathlib.Data.ZMod.Basic
import Mathlib.Tactic.Ring
import Mathlib.Tactic.NormNum

/-!
The exact polynomial product recorded by EXP-BINSTD-8bdf86 at toy n=17.

The Stage-1 admissible-dimension files list the bitmask factors 3, 313,
and 471 for x^17 - 1 over F₂. These definitions are those same monic
polynomials. This theorem certifies their product in F₂[X].

It does not prove either degree-eight factor irreducible, identify the
Frobenius representation on F_{2^17}, classify all invariant subspaces,
or establish the experiment's empirical relation-yield ratios.
-/

namespace CryptoResearch.Binstd

open Polynomial

abbrev F2 := ZMod 2

noncomputable def factor1 : F2[X] := X + 1
noncomputable def factor8a : F2[X] := X^8 + X^5 + X^4 + X^3 + 1
noncomputable def factor8b : F2[X] := X^8 + X^7 + X^6 + X^4 + X^2 + X + 1

/-- The three archived bitmask factors multiply to x^17 + 1 in F₂[X]. -/
theorem x17_factorization : factor1 * factor8a * factor8b = X^17 + 1 := by
  unfold factor1 factor8a factor8b
  have hz : (2 : F2) = 0 := by decide
  have hp : (2 : F2[X]) = 0 := by
    change C (2 : F2) = 0
    simp [hz]
  have h4 : (4 : F2[X]) = 0 := by
    calc
      (4 : F2[X]) = 2 * 2 := by ring
      _ = 0 := by rw [hp]; simp
  have h6 : (6 : F2[X]) = 0 := by
    calc
      (6 : F2[X]) = 2 * 3 := by ring
      _ = 0 := by rw [hp]; simp
  ring_nf
  simp only [hp, h4, h6, mul_zero, add_zero]

end CryptoResearch.Binstd

import CryptoResearch.Binstd.Irreducibility
import Mathlib.FieldTheory.Finite.GaloisField
import Mathlib.Tactic

/-!
The canonical field of cardinality 2^17 has a Frobenius linear map
whose minimal polynomial is the exact product of the factors recorded
by EXP-BINSTD-8bdf86. This uses Mathlib's finite-field theorem and
the source-bound factor identity.

The canonical `GaloisField 2 17` is not yet identified with the
archived runner's polynomial-basis implementation. This theorem also
does not classify the invariant subspaces or check relation yields.
-/

namespace CryptoResearch.Binstd

open Polynomial

local instance : Fact (Nat.Prime 2) := ⟨by decide⟩

abbrev CanonicalField17 := GaloisField 2 17

theorem canonicalField17_finrank :
    Module.finrank (ZMod 2) CanonicalField17 = 17 := by
  exact GaloisField.finrank 2 (by decide)

theorem canonicalFrobenius_order :
    orderOf (FiniteField.frobeniusAlgHom (ZMod 2) CanonicalField17) = 17 := by
  rw [FiniteField.orderOf_frobeniusAlgHom, canonicalField17_finrank]

theorem canonicalFrobenius_minpoly :
    minpoly (ZMod 2)
      (FiniteField.frobeniusAlgHom (ZMod 2) CanonicalField17).toLinearMap =
      factor1 * factor8a * factor8b := by
  rw [FiniteField.minpoly_frobeniusAlgHom, canonicalField17_finrank,
    x17_factorization]
  have htwo : (2 : ZMod 2) = 0 := by decide
  have hz : (2 : F2[X]) = 0 := by
    change C (2 : ZMod 2) = 0
    simp [htwo]
  calc
    (X : F2[X]) ^ 17 - 1 = X ^ 17 + 1 - 2 := by ring
    _ = X ^ 17 + 1 := by rw [hz]; ring

/-- Abstract field Frobenius has order 17 and the source-bound factor product as minimal polynomial. -/
theorem canonicalFrobenius_order_and_minpoly :
    orderOf (FiniteField.frobeniusAlgHom (ZMod 2) CanonicalField17) = 17 ∧
    minpoly (ZMod 2)
      (FiniteField.frobeniusAlgHom (ZMod 2) CanonicalField17).toLinearMap =
      factor1 * factor8a * factor8b :=
  ⟨canonicalFrobenius_order, canonicalFrobenius_minpoly⟩

end CryptoResearch.Binstd

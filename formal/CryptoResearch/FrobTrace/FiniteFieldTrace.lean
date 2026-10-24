import Mathlib.FieldTheory.Finite.Trace
import CryptoResearch.FrobTrace.OrderFive

/-!
The finite-field part of EXP-FROB-91ee9c control C5.

For every degree-five extension of finite fields, the five-term Frobenius
polynomial is the embedded field trace. Its kernel has dimension four. When
the characteristic is not five, the kernel is also the range of Frobenius
minus the identity. The three archived prime fields are instantiated below.

This does not prove the archived quotient-field implementation correct, or
decompose the trace kernel as the direct sum of the kernels of the nontrivial
irreducible factors of X^5 - 1. Those are separate C5 obligations.
-/

namespace CryptoResearch.FrobTrace.FiniteField

variable {K L : Type*} [Field K] [Fintype K] [Field L] [Algebra K L]
  [Algebra.IsAlgebraic K L]

/-- The `K`-linear Frobenius map on a finite-field extension. -/
noncomputable abbrev frobeniusEnd : Module.End K L :=
  (FiniteField.frobeniusAlgEquivOfAlgebraic K L).toLinearMap

private theorem frobeniusEnd_pow_apply (i : ℕ) (x : L) :
    (frobeniusEnd (K := K) (L := L) ^ i) x = x ^ (Fintype.card K ^ i) := by
  change (((FiniteField.frobeniusAlgEquivOfAlgebraic K L).toLinearMap) ^ i) x = _
  rw [← AlgEquiv.pow_toLinearMap]
  change (FiniteField.frobeniusAlgEquivOfAlgebraic K L ^ i) x = _
  rw [AlgEquiv.coe_pow, FiniteField.coe_frobeniusAlgEquivOfAlgebraic_iterate]

variable [Finite L]

/-- The five-term Frobenius polynomial is the embedded field trace. -/
theorem trace5_apply_eq_field_trace (hfin : Module.finrank K L = 5) (x : L) :
    trace5 (frobeniusEnd (K := K) (L := L)) x =
      algebraMap K L (Algebra.trace K L x) := by
  rw [FiniteField.algebraMap_trace_eq_sum_pow K L x, hfin]
  simp [trace5, Finset.sum_range_succ, frobeniusEnd_pow_apply, frobeniusEnd]

/-- The five-term polynomial and the field trace have the same kernel. -/
theorem ker_trace5_eq_field_trace_ker (hfin : Module.finrank K L = 5) :
    (trace5 (frobeniusEnd (K := K) (L := L))).ker =
      (Algebra.trace K L).ker := by
  ext x
  change trace5 (frobeniusEnd (K := K) (L := L)) x = 0 ↔
    Algebra.trace K L x = 0
  rw [trace5_apply_eq_field_trace hfin x]
  constructor
  · intro h
    apply (FaithfulSMul.algebraMap_injective K L)
    simpa using h
  · intro h
    simp [h]

/-- A degree-five finite-field trace has a four-dimensional kernel. -/
theorem field_trace_ker_finrank_four (hfin : Module.finrank K L = 5) :
    Module.finrank K (Algebra.trace K L).ker = 4 := by
  have hsurj := Algebra.trace_surjective K L
  have hrange : (Algebra.trace K L).range = ⊤ := LinearMap.range_eq_top.mpr hsurj
  have h := (Algebra.trace K L).finrank_range_add_finrank_ker
  have hrank : Module.finrank K (Algebra.trace K L).range = 1 := by
    rw [hrange]
    simp
  rw [hrank, hfin] at h
  omega

/-- The five-term Frobenius kernel has dimension four. -/
theorem trace5_ker_finrank_four (hfin : Module.finrank K L = 5) :
    Module.finrank K (trace5 (frobeniusEnd (K := K) (L := L))).ker = 4 := by
  rw [ker_trace5_eq_field_trace_ker hfin]
  exact field_trace_ker_finrank_four hfin

private theorem frobeniusEnd_pow_five (hfin : Module.finrank K L = 5) :
    frobeniusEnd (K := K) (L := L) ^ 5 = 1 := by
  have horder : orderOf (FiniteField.frobeniusAlgEquivOfAlgebraic K L) = 5 := by
    rw [FiniteField.orderOf_frobeniusAlgEquivOfAlgebraic, hfin]
  have hpow : (FiniteField.frobeniusAlgEquivOfAlgebraic K L) ^ 5 = 1 := by
    rw [← horder]
    exact pow_orderOf_eq_one _
  change ((FiniteField.frobeniusAlgEquivOfAlgebraic K L).toLinearMap) ^ 5 = 1
  rw [← AlgEquiv.pow_toLinearMap, hpow]
  simp

/-- In characteristic other than five, trace-zero elements are Frobenius
coboundaries. -/
theorem field_trace_ker_eq_frobenius_difference_range
    (hfin : Module.finrank K L = 5) (h5 : (5 : K) ≠ 0) :
    (Algebra.trace K L).ker = (frobeniusEnd (K := K) (L := L) - 1).range := by
  rw [← ker_trace5_eq_field_trace_ker hfin]
  exact ker_trace5_eq_range_sub _ (frobeniusEnd_pow_five hfin) h5

/-- Exact finite-field C5 algebraic core, with its characteristic assumption. -/
theorem finite_field_c5_core
    (hfin : Module.finrank K L = 5) (h5 : (5 : K) ≠ 0) :
    (∀ x : L, trace5 (frobeniusEnd (K := K) (L := L)) x =
      algebraMap K L (Algebra.trace K L x)) ∧
    (trace5 (frobeniusEnd (K := K) (L := L))).ker = (Algebra.trace K L).ker ∧
    Module.finrank K (Algebra.trace K L).ker = 4 ∧
    (Algebra.trace K L).ker = (frobeniusEnd (K := K) (L := L) - 1).range := by
  exact ⟨trace5_apply_eq_field_trace hfin,
    ker_trace5_eq_field_trace_ker hfin,
    field_trace_ker_finrank_four hfin,
    field_trace_ker_eq_frobenius_difference_range hfin h5⟩

-- Concrete finite-field instances of the three archived base primes.
local instance : Fact (Nat.Prime 11) := ⟨by decide⟩
local instance : Fact (Nat.Prime 13) := ⟨by decide⟩
local instance : Fact (Nat.Prime 19) := ⟨by decide⟩

theorem q11_trace5_ker_finrank_four :
    Module.finrank (ZMod 11)
      (trace5 (frobeniusEnd (K := ZMod 11) (L := GaloisField 11 5))).ker = 4 := by
  exact trace5_ker_finrank_four (GaloisField.finrank 11 (by decide))

theorem q13_trace5_ker_finrank_four :
    Module.finrank (ZMod 13)
      (trace5 (frobeniusEnd (K := ZMod 13) (L := GaloisField 13 5))).ker = 4 := by
  exact trace5_ker_finrank_four (GaloisField.finrank 13 (by decide))

theorem q19_trace5_ker_finrank_four :
    Module.finrank (ZMod 19)
      (trace5 (frobeniusEnd (K := ZMod 19) (L := GaloisField 19 5))).ker = 4 := by
  exact trace5_ker_finrank_four (GaloisField.finrank 19 (by decide))

end CryptoResearch.FrobTrace.FiniteField

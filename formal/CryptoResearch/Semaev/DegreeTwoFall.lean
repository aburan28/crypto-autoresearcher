/-
The uniform degree-2 fall of the Weil-descended Semaev `S_3` system.

Source: research/FFD_SEMAEV_MEASUREMENT1.md section 3a
Target: formal/targets/semaev-s3-degree2-fall-witness.yaml
Claim:  FFD-SEMAEV-MEASUREMENT1-THM-WITNESS

FFD_SEMAEV_MEASUREMENT1 measured the first-fall degree of the descended system
pinned at 2, uniformly in the extension degree `n`, the factor-base dimension
`n'` and the subspace `V`. This file proves the mechanism behind that pinning.

The degree-2 coefficients of the descended system are `t^2 + t*x` with
`t = v_j v_k` and `x` the target abscissa. The content is that scaling by
`x⁻¹^2` turns every one of them into an ARTIN-SCHREIER element `z^2 + z`,
and any Frobenius-invariant additive map kills `z^2 + z` in characteristic 2.

Scope. This proves a degree-2 fall EXISTS, uniformly. It says nothing about the
solving degree (which is provably unrelated to the first fall degree in either
direction -- see CORR-20260916-0c9c0a), about propagation to higher degrees, or
about ECDLP cost.
-/
-- Minimal imports: this proof needs field algebra and additive maps only.
-- Importing all of Mathlib is unnecessary here and does not fit the disk
-- allowance of this container.
import Mathlib.Algebra.Field.Basic
import Mathlib.Algebra.Group.Hom.Defs
import Mathlib.Tactic.FieldSimp
import Mathlib.Tactic.Ring
import Mathlib.Tactic.Linarith
import Mathlib.Tactic.LinearCombination

namespace CryptoResearch.Semaev

variable {K : Type*} [Field K]

/-- **Artin–Schreier normalisation.** Scaling a degree-2 coefficient
`t^2 + t*x` of the descended system by `x⁻¹^2` produces `z^2 + z` with
`z = x⁻¹ * t`.

No characteristic assumption is needed here: this is an identity in any field
with `x ≠ 0`. -/
theorem witness_normalisation (x t : K) (hx : x ≠ 0) :
    (x⁻¹) ^ 2 * (t ^ 2 + t * x) = (x⁻¹ * t) ^ 2 + (x⁻¹ * t) := by
  field_simp

/-- **The witness annihilates every degree-2 coefficient.**

`T` is any additive map that is invariant under squaring -- the absolute trace
of a finite field of characteristic 2 is the intended instance -- landing in a
group of exponent 2.

For every nonzero `x` and *every* `t`, the functional `T (x⁻¹^2 * -)`
annihilates `t^2 + t*x`. Uniformity in `t` is the whole point: the coefficients
of the descended system are `t = v_j v_k` for a basis `v_1 .. v_n'` of the
factor-base subspace, so one and the same functional kills all of them at once,
for every extension degree, every factor-base dimension and every subspace. -/
theorem trace_witness_annihilates_degree_two_part
    {L : Type*} [AddCommGroup L] (T : K →+ L)
    (hT : ∀ z : K, T (z ^ 2) = T z) (hL : ∀ y : L, y + y = 0)
    (x t : K) (hx : x ≠ 0) :
    T ((x⁻¹) ^ 2 * (t ^ 2 + t * x)) = 0 := by
  rw [witness_normalisation x t hx, map_add, hT]
  exact hL _

/-- The degeneracy equation `μ^(1/2) + μ * x = 0`, in the square-free form
`μ = μ^2 * x^2`, has `x⁻¹^2` as its unique nonzero root.

This is the statement that IS unique. The annihilating functional is NOT unique
in general: when the products `v_j v_k` span a proper subspace, accidental
annihilators exist (7 at `n = 9, n' = 3`, 63 at `n = 9, n' = 2` -- see
`research/verification/ffd_frobenius_witness.py`). Do not strengthen this. -/
theorem degeneracy_root_unique (x : K) (hx : x ≠ 0) (μ : K) (hμ : μ ≠ 0) :
    μ = μ ^ 2 * x ^ 2 ↔ μ = (x⁻¹) ^ 2 := by
  have hx2 : x ^ 2 ≠ 0 := pow_ne_zero 2 hx
  constructor
  · intro h
    -- μ = μ²x²  ⟹  μ(μx² − 1) = 0, and μ ≠ 0, so μx² = 1.
    have key : μ * (μ * x ^ 2 - 1) = 0 := by linear_combination -h
    have h1 : μ * x ^ 2 - 1 = 0 := by
      rcases mul_eq_zero.mp key with h0 | h1
      · exact absurd h0 hμ
      · exact h1
    have hmul : μ * x ^ 2 = 1 := by linear_combination h1
    field_simp
    linear_combination hmul
  · intro h
    rw [h]
    field_simp

end CryptoResearch.Semaev

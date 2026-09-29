/-
The uniform degree-2 fall of the Weil-descended Semaev `S_3` system.

Source: research/FFD_SEMAEV_MEASUREMENT1.md section 3a
Target: formal/targets/semaev-s3-degree2-fall-witness.yaml
Claim:  FFD-SEMAEV-MEASUREMENT1-THM-WITNESS

FFD_SEMAEV_MEASUREMENT1 measured the first-fall degree of the descended system
pinned at 2, uniformly in the extension degree `n`, the factor-base dimension
`n'` and the subspace `V`.

The degree-2 coefficients of the descended system are `t^2 + t*x` with
`t = v_j v_k` and `x` the target abscissa. The content is that scaling by
`x⁻¹^2` turns every one of them into an ARTIN-SCHREIER element `z^2 + z`,
and any Frobenius-invariant additive map kills `z^2 + z` in characteristic 2.
`absTrace` supplies an instance -- the absolute trace of a field of order
`2^n` -- so the hypotheses are discharged rather than assumed.

SCOPE, WRITTEN TO MATCH WHAT IS ACTUALLY PROVED. This file proves that the
degree-2 part is ANNIHILATED, uniformly in `n`, `n'` and `V`.

That is ONE HALF of a degree fall. The other half -- that the surviving
degree-<=1 residue is NONZERO -- is NOT proved here and does not follow from
anything here; without it the cancellation is equally consistent with the
trivial relation `0 = 0`. `absTrace_witness_kills_every_element` records the
reason to be careful about reading more into it: the same functional
annihilates EVERY element of `K` under this map, so the argument never inspects
the factor base and cannot distinguish the Semaev setting from any other.

So this file does not establish that a degree-2 fall exists. It establishes the
cancellation such a fall requires. Bridging that to the measurement is the
semantic-fidelity question, and it is open. The target YAML is a frozen record
and still reads more strongly than this; per the immutability rule it is
superseded here rather than edited.

It also says nothing about the solving degree (provably unrelated to the first
fall degree in either direction -- see CORR-20260916-0c9c0a), about propagation
to higher degrees, or about ECDLP cost.
-/
-- Named imports rather than `import Mathlib`: they are the honest dependency
-- list of this file, and they keep the build small enough that the CI proof
-- gate is cheap to run on every change.
import Mathlib.Algebra.Field.Basic
import Mathlib.Algebra.Group.Hom.Defs
import Mathlib.Algebra.BigOperators.Group.Finset.Basic
import Mathlib.Algebra.CharP.Lemmas
import Mathlib.Algebra.CharP.Two
import Mathlib.FieldTheory.Finite.Basic
import Mathlib.Tactic.FieldSimp
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

/-! ## The intended instance

Everything above is stated for an ABSTRACT `T` carrying two hypotheses. On its
own that is not a statement about finite fields: nothing there says the
hypotheses are satisfiable at all, let alone satisfied by the absolute trace of
`F_{2^n}`. This section discharges them, so `hT` and `hL` stop being
assumptions and become theorems about a concrete field.

The split below is deliberate. Squaring-invariance follows from ONE fact about
the field -- `z ^ 2 ^ n = z` -- and nothing else; `absTrace_sq_of_pow` proves it
from that alone, and `pow_two_pow_card` is the only place the order of the
field is used. -/

section AbsoluteTrace

variable {K : Type*} [Field K] [CharP K 2]

/-- The absolute trace of a field of order `2 ^ n`, written out rather than
taken from an API: `z + z^2 + z^4 + ... + z^(2^(n-1))`. -/
def absTrace (n : ℕ) (z : K) : K := ∑ i ∈ Finset.range n, z ^ 2 ^ i

omit [CharP K 2] in
@[simp] lemma absTrace_zero (n : ℕ) : absTrace n (0 : K) = 0 :=
  Finset.sum_eq_zero fun i _ => zero_pow (Nat.two_pow_pos i).ne'

/-- Additivity: in characteristic 2 the Frobenius is additive, termwise. -/
lemma absTrace_add (n : ℕ) (a b : K) :
    absTrace n (a + b) = absTrace n a + absTrace n b := by
  have : Fact (Nat.Prime 2) := ⟨Nat.prime_two⟩
  simp only [absTrace, ← Finset.sum_add_distrib]
  exact Finset.sum_congr rfl fun i _ => add_pow_char_pow a b 2 i

/-- The absolute trace as an additive homomorphism, which is the shape
`trace_witness_annihilates_degree_two_part` takes. -/
def absTraceHom (n : ℕ) : K →+ K where
  toFun := absTrace n
  map_zero' := absTrace_zero n
  map_add' := absTrace_add n

omit [CharP K 2] in
/-- **`hT` discharged, from the field-order fact alone.** Characteristic is not
needed here: the telescoping is valid in any commutative ring. Squaring shifts the
sum by one place; `z ^ 2 ^ n = z` closes the cycle, so the shifted sum and the
original differ by nothing. -/
lemma absTrace_sq_of_pow {n : ℕ} (hpow : ∀ w : K, w ^ 2 ^ n = w) (z : K) :
    absTrace n (z ^ 2) = absTrace n z := by
  have shift : ∀ i : ℕ, (z ^ 2) ^ 2 ^ i = z ^ 2 ^ (i + 1) := by
    intro i
    rw [← pow_mul]
    congr 1
    ring
  have key := Finset.sum_range_succ' (fun i => z ^ 2 ^ i) n
  rw [Finset.sum_range_succ] at key
  simp only [pow_zero, pow_one, hpow] at key
  simp only [absTrace, shift]
  exact (add_right_cancel key).symm

end AbsoluteTrace

section FiniteInstance

variable {K : Type*} [Field K] [Fintype K] [CharP K 2]

omit [CharP K 2] in
/-- The only place the ORDER of the field is used: in a field of order `2 ^ n`
every element satisfies `z ^ 2 ^ n = z`. -/
lemma pow_two_pow_card {n : ℕ} (hcard : Fintype.card K = 2 ^ n) (z : K) :
    z ^ 2 ^ n = z := by
  have h := FiniteField.pow_card z
  rwa [hcard] at h

/-- **The witness theorem with no hypotheses left to discharge.** For a field of
order `2 ^ n`, its absolute trace annihilates `x⁻¹^2 * (t^2 + t*x)` for every
nonzero `x` and every `t`. -/
theorem absTrace_witness_annihilates {n : ℕ} (hcard : Fintype.card K = 2 ^ n)
    (x t : K) (hx : x ≠ 0) :
    absTrace n ((x⁻¹) ^ 2 * (t ^ 2 + t * x)) = 0 :=
  trace_witness_annihilates_degree_two_part (absTraceHom n)
    (absTrace_sq_of_pow (pow_two_pow_card hcard))
    (fun y => CharTwo.add_self_eq_zero y) x t hx

/-! ### The object the claim is about

`t` above is a bare field element. The descended system's degree-2 coefficients
are pairwise products of a factor-base family, so name them and state the
annihilation for those, quantified over the index type and the family. That is
what "uniformly in `n'` and in `V`" means, as a quantifier rather than prose. -/

/-- The degree-2 coefficients of the descended system built on a factor-base
family `v`: the pairwise products `v j * v k`. -/
def degreeTwoCoeff {ι : Type*} (v : ι → K) (j k : ι) : K := v j * v k

/-- **One functional annihilates every degree-2 coefficient at once.** The
functional depends only on `x`; the statement is quantified over the index type
`ι`, the family `v`, and the pair `(j, k)`. -/
theorem absTrace_witness_annihilates_degree_two_coeffs {n : ℕ} {ι : Type*}
    (hcard : Fintype.card K = 2 ^ n) (v : ι → K) (x : K) (hx : x ≠ 0) (j k : ι) :
    absTrace n ((x⁻¹) ^ 2 *
      (degreeTwoCoeff v j k ^ 2 + degreeTwoCoeff v j k * x)) = 0 :=
  absTrace_witness_annihilates hcard x _ hx

/-- **The limitation, as a checked statement rather than a caveat in prose.**

The same functional annihilates `t^2 + t*x` for EVERY `t : K`, not only for
factor-base products. So the uniformity above is cheap: the argument never
inspects `v`, `ι`, the subspace or its dimension, and could not tell a factor
base from an arbitrary family.

Two consequences, both reasons NOT to read any of this as a degree-2 fall.
Annihilating the degree-2 part is one HALF of a fall; the other half is that
the surviving degree-<=1 residue is NONZERO, which is not proved anywhere in
this file and does not follow from anything in it. And a functional that kills
all of `K` under this map carries no information about the system, so nothing
here distinguishes the Semaev setting from any other. -/
theorem absTrace_witness_kills_every_element {n : ℕ}
    (hcard : Fintype.card K = 2 ^ n) (x : K) (hx : x ≠ 0) :
    ∀ t : K, absTrace n ((x⁻¹) ^ 2 * (t ^ 2 + t * x)) = 0 :=
  fun t => absTrace_witness_annihilates hcard x t hx

end FiniteInstance


end CryptoResearch.Semaev

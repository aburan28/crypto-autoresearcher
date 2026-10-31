/-
Source: ledger/proposals/IDEA-20261024-a2b05d.notes.md @ branch lead-discovery/20261024-mythos-ecdlp (commit recorded in the PR)
Target: formal/targets/ic-arity-oracle-threshold-20261024.yaml
Claim: Write r for the group order, B = r^β (0 < β) for the factor-base size,
  m ≥ 2 for the decomposition arity and k ≥ 0 for the enumeration order of the
  decomposition oracle (one attempt costs B^k · r^{o(1)}).  Under H1–H4 the
  cost exponent (base r) of Semaev-style index calculus is
     costAll(m, β, k) = max( max(0, 1 − β(m−1)) + kβ , 2β )
  when one attempt returns every decomposition of its target, and
     costOne(m, β, k) = max( max(0, 1 − βm) + β + kβ , 2β )
  when one attempt returns at most one decomposition.  Then
  (a) inf_β costAll = 2/(m+1−k) for 0 ≤ k ≤ 2 (k ≤ m−2), = k/(m−1) for
      2 ≤ k ≤ m−1, and ≥ 1 for k ≥ m−1; the infima are attained at
      β = 1/(m+1−k), resp. β = 1/(m−1);
  (b) inf_β costOne = 2/(m+1−k) for 0 ≤ k ≤ 1 and (1+k)/m for 1 ≤ k ≤ m−1,
      attained at β = 1/(m+1−k), resp. 1/m; and costOne ≥ costAll always;
  (c) costAll is below the generic exponent 1/2 iff (k ≤ 2 and m > k + 3) or
      (k ≥ 2 and 2k < m − 1); every meet-in-the-middle oracle (k ≥ m/2) and
      the exhaustive oracle (k = m − 1) stays strictly above, resp. at or
      above, 1/2 at every arity; a free oracle (k = 0) needs m ≥ 4, a linear
      oracle (k = 1) needs m ≥ 5, a quadratic oracle (k = 2) needs m ≥ 6.
  This is the two-term cost model of IDEA-20260803-fa9839 with the
  B-dependent oracle cost of IDEA-20260808-2ef5c8 (θ there is k here), made
  exact and machine-checked, plus the one-decomposition variant.
WHAT IS PROVED: the real-number algebra above for real m ≥ 2, real k ≥ 0 and
  real β > 0: every lower bound, its attainment, the threshold equivalences,
  the meet-in-the-middle and exhaustive corollaries, the comparison
  costOne ≥ costAll, the non-vacuity witness (m, β, k) = (5, 1/5, 1) with
  costAll = 2/5, and one proves-too-much control per modelling hypothesis.
WHAT IS NOT PROVED: that any implementation has this cost; H1–H4 are
  hypotheses of the model, not formalised; nothing about curve points, Semaev
  polynomials, group orders, GAE counts, o(1) terms, constants or any finite
  size; nothing about which oracles exist (the open class k < (m−1)/2 is a
  statement about the model, not an existence claim).
Heuristics taken as hypotheses (numbered in the source note):
  H1 yield: the expected number of decompositions of a random target into m
     factor-base points is B^m/(m!·r) · r^{o(1)} (random-model mean; the
     conservation identity KN-FIND-007 fixes the mean for every base of size B);
  H2 relations: the linear-algebra stage needs B · r^{o(1)} relations, so the
     number of attempts is max(1, r/B^{m−1}) · r^{o(1)} (all-decompositions
     oracle) or at least B · r^{o(1)} (one-decomposition oracle);
  H3 linear algebra: sparse elimination over B unknowns costs B^2 · r^{o(1)};
  H4 oracle: one attempt costs B^k · r^{o(1)}.
Data: none (no numerical data enters; `decide` is not used).
-/
import Mathlib.Basic.Real.Basic
import Mathlib.Tactic.Linarith
import Mathlib.Tactic.Positivity
import Mathlib.Tactic.FieldSimp
import Mathlib.Tactic.Ring
import Mathlib.Tactic.NormNum
import Mathlib.Tactic.Push

set_option autoImplicit false

namespace CryptoResearch.IC.ArityOracleThreshold

/-! ### The model -/

/-- Exponent (base `r`) of the number of attempts when one attempt returns every
decomposition of its target: `r / B^(m-1)` attempts collect `B` relations (H1, H2),
and never fewer than one attempt. -/
noncomputable def attemptsAll (m β : ℝ) : ℝ := max 0 (1 - β * (m - 1))

/-- Exponent of the number of attempts when one attempt returns at most one
decomposition: one attempt per needed relation (`β`) times the inverse success
probability (`max 0 (1 - β m)`). -/
noncomputable def attemptsOne (m β : ℝ) : ℝ := max 0 (1 - β * m) + β

/-- Total cost exponent, all-decompositions oracle of order `k` (H3, H4). -/
noncomputable def costAll (m β k : ℝ) : ℝ := max (attemptsAll m β + k * β) (2 * β)

/-- Total cost exponent, one-decomposition oracle of order `k` (H3, H4). -/
noncomputable def costOne (m β k : ℝ) : ℝ := max (attemptsOne m β + k * β) (2 * β)

/-! ### Lower bounds for the all-decompositions oracle -/

/-- Orders `0 ≤ k ≤ 2`, `k ≤ m - 2`: the exponent is at least `2/(m+1-k)`. -/
theorem costAll_ge_small (m β k : ℝ) (hm : 2 ≤ m) (hβ : 0 < β) (hk0 : 0 ≤ k) (hk2 : k ≤ 2)
    (hkm : k ≤ m - 2) : 2 / (m + 1 - k) ≤ costAll m β k := by
  unfold costAll attemptsAll
  have hpos : 0 < m + 1 - k := by linarith
  by_cases h : β ≤ 1 / (m + 1 - k)
  · have hβc : β * (m + 1 - k) ≤ 1 := by
      have := (le_div_iff₀ hpos).mp h
      linarith
    have h1 : 1 - β * (m - 1) ≤ max 0 (1 - β * (m - 1)) := le_max_right _ _
    have h2 : 2 / (m + 1 - k) ≤ 1 - β * (m - 1) + k * β := by
      rw [div_le_iff₀ hpos]
      nlinarith
    calc 2 / (m + 1 - k) ≤ 1 - β * (m - 1) + k * β := h2
      _ ≤ max 0 (1 - β * (m - 1)) + k * β := by linarith
      _ ≤ max (max 0 (1 - β * (m - 1)) + k * β) (2 * β) := le_max_left _ _
  · push Not at h
    have h2 : 2 / (m + 1 - k) ≤ 2 * β := by
      rw [div_le_iff₀ hpos]
      have := (div_lt_iff₀ hpos).mp h
      linarith
    calc 2 / (m + 1 - k) ≤ 2 * β := h2
      _ ≤ max (max 0 (1 - β * (m - 1)) + k * β) (2 * β) := le_max_right _ _

/-- Orders `0 ≤ k ≤ m - 1`: the exponent is at least `k/(m-1)` (sharp for `k ≥ 2`). -/
theorem costAll_ge_large (m β k : ℝ) (hm : 2 ≤ m) (hβ : 0 < β) (hk0 : 0 ≤ k)
    (hkm : k ≤ m - 1) : k / (m - 1) ≤ costAll m β k := by
  unfold costAll attemptsAll
  have hpos : 0 < m - 1 := by linarith
  by_cases h : β ≤ 1 / (m - 1)
  · have hβc : β * (m - 1) ≤ 1 := by
      have := (le_div_iff₀ hpos).mp h
      linarith
    have h1 : 1 - β * (m - 1) ≤ max 0 (1 - β * (m - 1)) := le_max_right _ _
    have h2 : k / (m - 1) ≤ 1 - β * (m - 1) + k * β := by
      rw [div_le_iff₀ hpos]
      nlinarith
    calc k / (m - 1) ≤ 1 - β * (m - 1) + k * β := h2
      _ ≤ max 0 (1 - β * (m - 1)) + k * β := by linarith
      _ ≤ max (max 0 (1 - β * (m - 1)) + k * β) (2 * β) := le_max_left _ _
  · push Not at h
    have h0 : 0 ≤ max 0 (1 - β * (m - 1)) := le_max_left _ _
    have hβc : 1 < β * (m - 1) := by
      have := (div_lt_iff₀ hpos).mp h
      linarith
    have h2 : k / (m - 1) ≤ k * β := by
      rw [div_le_iff₀ hpos]
      nlinarith
    calc k / (m - 1) ≤ k * β := h2
      _ ≤ max 0 (1 - β * (m - 1)) + k * β := by linarith
      _ ≤ max (max 0 (1 - β * (m - 1)) + k * β) (2 * β) := le_max_left _ _

/-- Orders `k ≥ m - 1` (exhaustive and worse): the exponent is at least 1. -/
theorem costAll_ge_one (m β k : ℝ) (hm : 2 ≤ m) (hβ : 0 < β) (hkm : m - 1 ≤ k) :
    1 ≤ costAll m β k := by
  unfold costAll attemptsAll
  have hpos : 0 < m - 1 := by linarith
  by_cases h : β * (m - 1) ≤ 1
  · have h1 : 1 - β * (m - 1) ≤ max 0 (1 - β * (m - 1)) := le_max_right _ _
    have h2 : 1 ≤ 1 - β * (m - 1) + k * β := by nlinarith
    calc (1 : ℝ) ≤ 1 - β * (m - 1) + k * β := h2
      _ ≤ max 0 (1 - β * (m - 1)) + k * β := by linarith
      _ ≤ max (max 0 (1 - β * (m - 1)) + k * β) (2 * β) := le_max_left _ _
  · push Not at h
    have h0 : 0 ≤ max 0 (1 - β * (m - 1)) := le_max_left _ _
    have h2 : 1 ≤ k * β := by nlinarith
    calc (1 : ℝ) ≤ k * β := h2
      _ ≤ max 0 (1 - β * (m - 1)) + k * β := by linarith
      _ ≤ max (max 0 (1 - β * (m - 1)) + k * β) (2 * β) := le_max_left _ _

/-! ### Attainment -/

/-- The small-order bound is attained at `β = 1/(m+1-k)`. -/
theorem costAll_small_attained (m k : ℝ) (hm : 2 ≤ m) (hk0 : 0 ≤ k) (hk2 : k ≤ 2)
    (hkm : k ≤ m - 2) : costAll m (1 / (m + 1 - k)) k = 2 / (m + 1 - k) := by
  unfold costAll attemptsAll
  have hpos : 0 < m + 1 - k := by linarith
  have hne : m + 1 - k ≠ 0 := ne_of_gt hpos
  have key : 1 - 1 / (m + 1 - k) * (m - 1) = (2 - k) / (m + 1 - k) := by
    field_simp
    ring
  rw [key]
  have hnn : (0 : ℝ) ≤ (2 - k) / (m + 1 - k) := by
    apply div_nonneg <;> linarith
  rw [max_eq_right hnn]
  have h1 : (2 - k) / (m + 1 - k) + k * (1 / (m + 1 - k)) = 2 / (m + 1 - k) := by
    rw [mul_one_div, ← add_div]
    congr 1
    ring
  have h2 : 2 * (1 / (m + 1 - k)) = 2 / (m + 1 - k) := by ring
  rw [h1, h2, max_self]

/-- The large-order bound is attained at `β = 1/(m-1)` for `k ≥ 2`. -/
theorem costAll_large_attained (m k : ℝ) (hm : 2 ≤ m) (hk2 : 2 ≤ k) :
    costAll m (1 / (m - 1)) k = k / (m - 1) := by
  unfold costAll attemptsAll
  have hpos : 0 < m - 1 := by linarith
  have hne : m - 1 ≠ 0 := ne_of_gt hpos
  have key : 1 - 1 / (m - 1) * (m - 1) = 0 := by rw [one_div_mul_cancel hne, sub_self]
  rw [key, max_self, zero_add]
  have h1 : k * (1 / (m - 1)) = k / (m - 1) := by ring
  have h2 : 2 * (1 / (m - 1)) = 2 / (m - 1) := by ring
  rw [h1, h2]
  have : 2 / (m - 1) ≤ k / (m - 1) := by
    apply div_le_div_of_nonneg_right _ hpos.le
    linarith
  exact max_eq_left this

/-! ### Thresholds against the generic exponent 1/2 -/

/-- Small orders: below 1/2 iff `m > k + 3`. -/
theorem small_threshold (m k : ℝ) (hm : 2 ≤ m) (hkm : k ≤ m - 2) :
    2 / (m + 1 - k) < 1 / 2 ↔ k + 3 < m := by
  have hpos : 0 < m + 1 - k := by linarith
  rw [div_lt_iff₀ hpos]
  constructor <;> intro h <;> linarith

/-- Large orders: below 1/2 iff `2k < m - 1`. -/
theorem large_threshold (m k : ℝ) (hm : 2 ≤ m) :
    k / (m - 1) < 1 / 2 ↔ 2 * k < m - 1 := by
  have hpos : 0 < m - 1 := by linarith
  rw [div_lt_iff₀ hpos]
  constructor <;> intro h <;> linarith

/-- Free oracle (`k = 0`): the exponent is at least `2/(m+1)`, below 1/2 iff `m > 3`. -/
theorem free_oracle (m β : ℝ) (hm : 2 ≤ m) (hβ : 0 < β) :
    2 / (m + 1) ≤ costAll m β 0 ∧ (2 / (m + 1) < 1 / 2 ↔ 3 < m) := by
  have h := costAll_ge_small m β 0 hm hβ le_rfl (by norm_num) (by linarith)
  have t := small_threshold m 0 hm (by linarith)
  simp only [sub_zero, zero_add] at h t
  exact ⟨h, t⟩

/-- Linear oracle (`k = 1`, one pass over the base per attempt): at least `2/m`,
below 1/2 iff `m > 4`. -/
theorem linear_oracle (m β : ℝ) (hm : 3 ≤ m) (hβ : 0 < β) :
    2 / m ≤ costAll m β 1 ∧ (2 / m < 1 / 2 ↔ 4 < m) := by
  have h := costAll_ge_small m β 1 (by linarith) hβ (by norm_num) (by norm_num) (by linarith)
  have t := small_threshold m 1 (by linarith) (by linarith)
  have e : m + 1 - 1 = m := by ring
  rw [e] at h t
  constructor
  · exact h
  · rw [t]; constructor <;> intro hh <;> linarith

/-- Quadratic oracle (`k = 2`): at least `2/(m-1)`, below 1/2 iff `m > 5`. -/
theorem quadratic_oracle (m β : ℝ) (hm : 4 ≤ m) (hβ : 0 < β) :
    2 / (m - 1) ≤ costAll m β 2 ∧ (2 / (m - 1) < 1 / 2 ↔ 5 < m) := by
  have h := costAll_ge_small m β 2 (by linarith) hβ (by norm_num) le_rfl (by linarith)
  have t := small_threshold m 2 (by linarith) (by linarith)
  have e : m + 1 - 2 = m - 1 := by ring
  rw [e] at h t
  constructor
  · exact h
  · rw [t]; constructor <;> intro hh <;> linarith

/-- Meet-in-the-middle oracles (`k ≥ m/2`) never reach the generic exponent:
the cost exponent is strictly above 1/2 at every arity. -/
theorem mitm_never_sub_generic (m β k : ℝ) (hm : 2 ≤ m) (hβ : 0 < β) (hk : m / 2 ≤ k) :
    1 / 2 < costAll m β k := by
  have hpos : 0 < m - 1 := by linarith
  have hk0 : 0 ≤ k := by linarith
  by_cases hkm : k ≤ m - 1
  · have h := costAll_ge_large m β k hm hβ hk0 hkm
    have : 1 / 2 < k / (m - 1) := by
      rw [lt_div_iff₀ hpos]
      linarith
    linarith
  · push Not at hkm
    have h := costAll_ge_one m β k hm hβ hkm.le
    linarith

/-- The exhaustive oracle (`k = m - 1`) costs at least the full exponent 1. -/
theorem exhaustive_ge_one (m β : ℝ) (hm : 2 ≤ m) (hβ : 0 < β) :
    1 ≤ costAll m β (m - 1) :=
  costAll_ge_one m β (m - 1) hm hβ le_rfl

/-- Arity 3 with a free oracle exactly ties the generic exponent. -/
theorem arity_three_free_ties (β : ℝ) (hβ : 0 < β) :
    1 / 2 ≤ costAll 3 β 0 := by
  have h := (free_oracle 3 β (by norm_num) hβ).1
  norm_num at h
  exact h

/-! ### The one-decomposition oracle -/

/-- A one-decomposition oracle never needs fewer attempts than an
all-decompositions oracle (equality below saturation `βm ≤ 1`). -/
theorem attemptsAll_le_attemptsOne (m β : ℝ) (hβ : 0 < β) :
    attemptsAll m β ≤ attemptsOne m β := by
  unfold attemptsAll attemptsOne
  have e : 1 - β * (m - 1) = (1 - β * m) + β := by ring
  rw [e]
  by_cases h : 0 ≤ 1 - β * m
  · rw [max_eq_right h]
    have : 0 ≤ (1 - β * m) + β := by linarith
    rw [max_eq_right this]
  · push Not at h
    rw [max_eq_left h.le]
    have h2 : 1 - β * m + β ≤ β := by linarith
    calc max 0 (1 - β * m + β) ≤ max 0 β := max_le_max le_rfl h2
      _ = β := max_eq_right hβ.le
      _ = 0 + β := by ring

/-- Hence the one-decomposition cost exponent is never below the all-decompositions one. -/
theorem costAll_le_costOne (m β k : ℝ) (hβ : 0 < β) (hk : 0 ≤ k) :
    costAll m β k ≤ costOne m β k := by
  unfold costAll costOne
  have h := attemptsAll_le_attemptsOne m β hβ
  exact max_le_max (by linarith) le_rfl

/-- One-decomposition oracle, `1 ≤ k ≤ m - 1`: the exponent is at least `(1+k)/m`
(strictly worse than the all-decompositions `k/(m-1)` for `k ≥ 2`, `m ≥ 3`). -/
theorem costOne_ge_enum (m β k : ℝ) (hm : 2 ≤ m) (hβ : 0 < β) (hk : 1 ≤ k) (hkm : k ≤ m - 1) :
    (1 + k) / m ≤ costOne m β k := by
  unfold costOne attemptsOne
  have hm0 : 0 < m := by linarith
  by_cases h : β ≤ 1 / m
  · have hβm : β * m ≤ 1 := by
      have := (le_div_iff₀ hm0).mp h
      linarith
    have h1 : 1 - β * m ≤ max 0 (1 - β * m) := le_max_right _ _
    have h2 : (1 + k) / m ≤ 1 - β * m + β + k * β := by
      rw [div_le_iff₀ hm0]
      nlinarith
    calc (1 + k) / m ≤ 1 - β * m + β + k * β := h2
      _ ≤ max 0 (1 - β * m) + β + k * β := by linarith
      _ ≤ max (max 0 (1 - β * m) + β + k * β) (2 * β) := le_max_left _ _
  · push Not at h
    have hβm : 1 < β * m := by
      have := (div_lt_iff₀ hm0).mp h
      linarith
    have h0 : 0 ≤ max 0 (1 - β * m) := le_max_left _ _
    have h2 : (1 + k) / m ≤ β + k * β := by
      rw [div_le_iff₀ hm0]
      nlinarith
    calc (1 + k) / m ≤ β + k * β := h2
      _ ≤ max 0 (1 - β * m) + β + k * β := by linarith
      _ ≤ max (max 0 (1 - β * m) + β + k * β) (2 * β) := le_max_left _ _

/-- One-decomposition oracle, orders `0 ≤ k ≤ 1`: the exponent is at least `2/(m+1-k)`
(this interpolates between the free-oracle value `2/(m+1)` and the linear value `2/m`). -/
theorem costOne_ge_small (m β k : ℝ) (hm : 2 ≤ m) (hβ : 0 < β) (hk0 : 0 ≤ k) (hk1 : k ≤ 1) :
    2 / (m + 1 - k) ≤ costOne m β k := by
  unfold costOne attemptsOne
  have hpos : 0 < m + 1 - k := by linarith
  by_cases h : β ≤ 1 / (m + 1 - k)
  · have hβc : β * (m + 1 - k) ≤ 1 := by
      have := (le_div_iff₀ hpos).mp h
      linarith
    have h1 : 1 - β * m ≤ max 0 (1 - β * m) := le_max_right _ _
    have h2 : 2 / (m + 1 - k) ≤ 1 - β * m + β + k * β := by
      rw [div_le_iff₀ hpos]
      nlinarith
    calc 2 / (m + 1 - k) ≤ 1 - β * m + β + k * β := h2
      _ ≤ max 0 (1 - β * m) + β + k * β := by linarith
      _ ≤ max (max 0 (1 - β * m) + β + k * β) (2 * β) := le_max_left _ _
  · push Not at h
    have h2 : 2 / (m + 1 - k) ≤ 2 * β := by
      rw [div_le_iff₀ hpos]
      have := (div_lt_iff₀ hpos).mp h
      linarith
    calc 2 / (m + 1 - k) ≤ 2 * β := h2
      _ ≤ max (max 0 (1 - β * m) + β + k * β) (2 * β) := le_max_right _ _

/-- One-decomposition oracle, small orders: the bound is attained at `β = 1/(m+1-k)`. -/
theorem costOne_small_attained (m k : ℝ) (hm : 2 ≤ m) (hk0 : 0 ≤ k) (hk1 : k ≤ 1) :
    costOne m (1 / (m + 1 - k)) k = 2 / (m + 1 - k) := by
  unfold costOne attemptsOne
  have hpos : 0 < m + 1 - k := by linarith
  have hne : m + 1 - k ≠ 0 := ne_of_gt hpos
  have key : 1 - 1 / (m + 1 - k) * m = (1 - k) / (m + 1 - k) := by
    field_simp
    ring
  rw [key]
  have hnn : (0 : ℝ) ≤ (1 - k) / (m + 1 - k) := by
    apply div_nonneg <;> linarith
  rw [max_eq_right hnn]
  have h1 : (1 - k) / (m + 1 - k) + 1 / (m + 1 - k) + k * (1 / (m + 1 - k)) = 2 / (m + 1 - k) := by
    rw [mul_one_div, ← add_div, ← add_div]
    congr 1
    ring
  have h2 : 2 * (1 / (m + 1 - k)) = 2 / (m + 1 - k) := by ring
  rw [h1, h2, max_self]

/-- One-decomposition oracle, the bound is attained at `β = 1/m`. -/
theorem costOne_enum_attained (m k : ℝ) (hm : 2 ≤ m) (hk : 1 ≤ k) :
    costOne m (1 / m) k = (1 + k) / m := by
  unfold costOne attemptsOne
  have hm0 : 0 < m := by linarith
  have hne : m ≠ 0 := ne_of_gt hm0
  have key : 1 - 1 / m * m = 0 := by rw [one_div_mul_cancel hne, sub_self]
  rw [key, max_self, zero_add]
  have h1 : 1 / m + k * (1 / m) = (1 + k) / m := by
    rw [mul_one_div, ← add_div]
  have h2 : 2 * (1 / m) = 2 / m := by ring
  rw [h1, h2]
  have : 2 / m ≤ (1 + k) / m := by
    apply div_le_div_of_nonneg_right _ hm0.le
    linarith
  exact max_eq_left this

/-! ### Non-vacuity -/

/-- The hypotheses of `costAll_ge_small` hold together at `(m, β, k) = (5, 1/5, 1)`,
and there the model exponent is `2/5 < 1/2`: in the model, a linear-cost oracle at
arity 5 is sub-generic. -/
theorem main_hyps_satisfiable :
    (2 : ℝ) ≤ 5 ∧ (0 : ℝ) < 1 / 5 ∧ (0 : ℝ) ≤ 1 ∧ (1 : ℝ) ≤ 2 ∧ (1 : ℝ) ≤ 5 - 2 ∧
      costAll 5 (1 / 5) 1 = 2 / 5 ∧ (2 : ℝ) / 5 < 1 / 2 := by
  refine ⟨by norm_num, by norm_num, by norm_num, by norm_num, by norm_num, ?_, by norm_num⟩
  unfold costAll attemptsAll
  norm_num

/-! ### Proves-too-much controls (one per modelling hypothesis)

At `m = 3, k = 0` the full model ties the generic exponent (`arity_three_free_ties`).
Each control drops one hypothesis and exhibits a `β` with exponent below 1/2, so
each hypothesis is load-bearing. -/

/-- Dropping H3 (the linear-algebra term): attempts alone can be `1/3 < 1/2` at `m = 3`. -/
theorem needs_H3_linear_algebra :
    ∃ β : ℝ, 0 < β ∧ attemptsAll 3 β + 0 * β < 1 / 2 := by
  refine ⟨1 / 3, by norm_num, ?_⟩
  unfold attemptsAll
  norm_num

/-- Dropping H1 (the failure term `max 0 (1 - β(m-1))`): the exponent `max(kβ, 2β)`
is below 1/2 at `β = 1/8` for any order `k ≤ 2`. -/
theorem needs_H1_failure_term (k : ℝ) (hk : 0 ≤ k) (hk2 : k ≤ 2) :
    ∃ β : ℝ, 0 < β ∧ max (k * β) (2 * β) < 1 / 2 := by
  refine ⟨1 / 8, by norm_num, ?_⟩
  have : k * (1 / 8) ≤ 2 * (1 / 8) := by nlinarith
  rw [max_eq_right this]
  norm_num

/-- Dropping H2 (relations needed `B`, i.e. using `max 0 (1 - βm)` as the attempt
exponent): the exponent `max(max 0 (1 - βm), 2β)` is `2/5 < 1/2` at `m = 3, β = 1/5`. -/
theorem needs_H2_relation_count :
    ∃ β : ℝ, 0 < β ∧ max (max 0 (1 - β * 3) + 0 * β) (2 * β) < 1 / 2 := by
  refine ⟨1 / 5, by norm_num, ?_⟩
  norm_num

/-- H4 is load-bearing in the other direction: the free-oracle exponent `2/5` at
`m = 4` becomes `≥ 1/2` as soon as the oracle has order `k = 1`. -/
theorem needs_H4_oracle_order (β : ℝ) (hβ : 0 < β) :
    costAll 4 (1 / 5) 0 = 2 / 5 ∧ 1 / 2 ≤ costAll 4 β 1 := by
  constructor
  · have h := costAll_small_attained 4 0 (by norm_num) le_rfl (by norm_num) (by norm_num)
    norm_num at h ⊢
    exact h
  · have h := (linear_oracle 4 β (by norm_num) hβ).1
    norm_num at h
    exact h

#print axioms costAll_ge_small
#print axioms costAll_ge_large
#print axioms costAll_ge_one
#print axioms costAll_small_attained
#print axioms costAll_large_attained
#print axioms small_threshold
#print axioms large_threshold
#print axioms free_oracle
#print axioms linear_oracle
#print axioms quadratic_oracle
#print axioms mitm_never_sub_generic
#print axioms exhaustive_ge_one
#print axioms attemptsAll_le_attemptsOne
#print axioms costAll_le_costOne
#print axioms costOne_ge_small
#print axioms costOne_small_attained
#print axioms costOne_ge_enum
#print axioms costOne_enum_attained
#print axioms main_hyps_satisfiable

end CryptoResearch.IC.ArityOracleThreshold

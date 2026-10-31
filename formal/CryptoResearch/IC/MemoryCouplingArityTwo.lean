/-
Source: ledger/proposals/IDEA-20261024-a2b05d.notes.md, section 8 @ branch lead-discovery/20261024-mythos-ecdlp (commit recorded in the PR)
Target: formal/targets/ic-memory-coupling-arity-two-20261024.yaml
Claim: At arity 2 a free (k = 0) all-decompositions oracle over an unstructured
  factor base of size B = r^β is a sumset-membership query answered from a
  precomputed table of the B^2 pair sums (IDEA-20260830-4ab603), so in exponents
     time2(β) = max(1 − β, 2β),   mem2(β) = 2β.
  For every β: time2(β) ≥ 2/3, with equality only at β = 1/3; there mem2 = 2/3,
  so the time-optimal point (2/3, 2/3) is dominated by BSGS at (1/2, 1/2) on both
  axes; for every β the time exponent is strictly above 1/2; and if mem2 ≤ 1/2
  then time2 ≥ 3/4.  Control: charging memory at β instead of 2β (the
  uncorrected IDEA-20260829-b5a2c8 reading) gives (2/3, 1/3), which BSGS does
  not dominate on the memory axis.
WHAT IS PROVED: the real-number algebra above for real β (the lower bound for
  all β, uniqueness of the minimiser, the memory value at the minimiser, the
  strict-above-1/2 statement, the memory-time trade statement, and the
  control).
WHAT IS NOT PROVED: that any implementation has these exponents; H1–H3 of the
  main file and H5 (the pair-sum table is the only way to make the m = 2 oracle
  free) are hypotheses; nothing about curve points, measured counts, o(1) terms,
  or any finite size; nothing about structured bases.
Heuristics taken as hypotheses: H1 yield, H2 relations, H3 sparse linear algebra
  (as in ArityOracleThreshold.lean), and
  H5 table: a free m = 2 oracle over an unstructured base stores Θ(B^2) pair sums.
Data: none.
-/
import Mathlib.Basic.Real.Basic
import Mathlib.Tactic.Linarith
import Mathlib.Tactic.NormNum

set_option autoImplicit false

namespace CryptoResearch.IC.MemoryCouplingArityTwo

/-- Time exponent at arity 2 with a free all-decompositions oracle: attempts
`r / B` (H1, H2) against sparse linear algebra `B^2` (H3). -/
noncomputable def time2 (β : ℝ) : ℝ := max (1 - β) (2 * β)

/-- Memory (and precomputation) exponent of the pair-sum table (H5). -/
noncomputable def mem2 (β : ℝ) : ℝ := 2 * β

/-- The time exponent is at least `2/3` for every `β`. -/
theorem time2_ge (β : ℝ) : 2 / 3 ≤ time2 β := by
  unfold time2
  by_cases h : β ≤ 1 / 3
  · have : 2 / 3 ≤ 1 - β := by linarith
    exact le_trans this (le_max_left _ _)
  · push Not at h
    have : 2 / 3 ≤ 2 * β := by linarith
    exact le_trans this (le_max_right _ _)

/-- The bound is attained at `β = 1/3`. -/
theorem time2_attained : time2 (1 / 3) = 2 / 3 := by
  unfold time2
  norm_num

/-- The minimiser is unique: `time2 β = 2/3` forces `β = 1/3`. -/
theorem time2_min_unique (β : ℝ) (h : time2 β = 2 / 3) : β = 1 / 3 := by
  unfold time2 at h
  have h1 : 1 - β ≤ 2 / 3 := by rw [← h]; exact le_max_left _ _
  have h2 : 2 * β ≤ 2 / 3 := by rw [← h]; exact le_max_right _ _
  linarith

/-- At the time-optimal point the memory exponent is `2/3`. -/
theorem mem2_at_optimum : mem2 (1 / 3) = 2 / 3 := by
  unfold mem2
  norm_num

/-- BSGS at `(1/2, 1/2)` dominates the time-optimal point `(2/3, 2/3)` on both axes. -/
theorem bsgs_dominates_optimum :
    (1 : ℝ) / 2 < time2 (1 / 3) ∧ (1 : ℝ) / 2 < mem2 (1 / 3) := by
  rw [time2_attained, mem2_at_optimum]
  norm_num

/-- For every `β` the time exponent is strictly above the generic `1/2`: no point
of the family beats rho (or BSGS) in time. -/
theorem time2_gt_half (β : ℝ) : 1 / 2 < time2 β := by
  have h := time2_ge β
  linarith

/-- Spending at most the BSGS memory (`mem2 ≤ 1/2`, i.e. `β ≤ 1/4`) costs time at least `3/4`. -/
theorem time2_ge_of_mem2_le (β : ℝ) (h : mem2 β ≤ 1 / 2) : 3 / 4 ≤ time2 β := by
  unfold mem2 at h
  unfold time2
  have : 3 / 4 ≤ 1 - β := by linarith
  exact le_trans this (le_max_left _ _)

/-- Non-vacuity: the point `β = 1/3` exists with `time2 = mem2 = 2/3`. -/
theorem main_hyps_satisfiable : ∃ β : ℝ, 0 < β ∧ β ≤ 1 ∧ time2 β = 2 / 3 ∧ mem2 β = 2 / 3 :=
  ⟨1 / 3, by norm_num, by norm_num, time2_attained, mem2_at_optimum⟩

/-- Proves-too-much control for H5: charging memory at `β` (the factor base only)
puts the optimum at `(2/3, 1/3)`, which BSGS does not dominate on the memory axis. -/
theorem needs_H5_table_charge : time2 (1 / 3) = 2 / 3 ∧ (1 : ℝ) / 3 < 1 / 2 := by
  exact ⟨time2_attained, by norm_num⟩

#print axioms time2_ge
#print axioms time2_attained
#print axioms time2_min_unique
#print axioms bsgs_dominates_optimum
#print axioms time2_gt_half
#print axioms time2_ge_of_mem2_le
#print axioms main_hyps_satisfiable

end CryptoResearch.IC.MemoryCouplingArityTwo

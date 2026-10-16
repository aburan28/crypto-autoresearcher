/-
Baby-step giant-step coverage: the premise the runbook conformance example
(`examples/runbooks/toy-ecdlp-bsgs/`) relies on when it treats an unsolved
instance as a defect rather than an observation.

Source:  examples/runbooks/toy-ecdlp-bsgs/README.md ("Why `solved` is a
         validity condition"); the solver is solve.py (`bsgs`: a table of
         `j*G` for `0 ≤ j < m`, giant steps `Q - i*(m*G)` for `0 ≤ i < m`).
Target:  formal/targets/runbook-example-bsgs-coverage.yaml

WHAT IS PROVED (core Lean: `Nat`).
* `coverage`: for `0 < m` and `k < m * m`, the decomposition
  `k = (k / m) * m + k % m` has both digits below `m`. So with `m` baby steps
  and `m` giant steps every exponent `k < m * m` is reached, and the giant step
  at which it is reached is `k / m` (the solver reports `giant_steps = k / m + 1`).

WHAT IS NOT PROVED. Nothing about the group, the curve, the solver's code, or
its cost: this is the counting identity alone. That the example picks
`m = isqrt(n - 1) + 1`, so `n ≤ m * m` and every `k < n` is covered, is
checked numerically by `check.py`, not here.
-/

namespace CryptoResearch.Runbook.BsgsCoverage

/-- Every exponent below `m * m` is `i * m + j` with `i, j < m`. -/
theorem coverage (m k : Nat) (hm : 0 < m) (hk : k < m * m) :
    k / m < m ∧ k % m < m ∧ k = k / m * m + k % m := by
  refine ⟨?_, Nat.mod_lt k hm, ?_⟩
  · -- `m * (k / m) ≤ k < m * m`, so `k / m < m`. The alternatives are the same
    -- step under the lemma names different core releases carry.
    first
      | exact Nat.div_lt_of_lt_mul hk
      | exact (Nat.div_lt_iff_lt_mul hm).2 hk
      | exact Nat.lt_of_mul_lt_mul_left (Nat.lt_of_le_of_lt (Nat.mul_div_le k m) hk)
  · calc k = m * (k / m) + k % m := (Nat.div_add_mod k m).symm
      _ = k / m * m + k % m := by rw [Nat.mul_comm]

end CryptoResearch.Runbook.BsgsCoverage

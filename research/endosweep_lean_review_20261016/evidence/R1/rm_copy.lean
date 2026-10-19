/-!
# 2 is inert in `ℤ[φ]`: the 2-adic valuation of a golden-ratio norm is even

Source: `research/endosweep_rm_qcurves_20261008/README.md`, item 7
("2 is inert in Z[φ], so v₂(#J) is always even").

For `φ² + φ − 1 = 0` the norm form of `ℤ[φ]` is
`N(a + bφ) = a² − ab − b²` (equivalently `a² + ab − b²` after `φ ↦ −φ̄`;
both forms are covered below).  The theorem: for `(a, b) ≠ (0, 0)` the norm
is `4^k · m` with `m` odd.

What this does NOT prove: that `#J(F_p)` is such a norm.  That is the
factorisation of the Frobenius characteristic polynomial over `ℚ(√5)`
(Tautz–Top–Verberkmoes RM), which the research measured for every member and
is an input here, not a Lean theorem.
-/

namespace CryptoResearch.Endosweep.RMGoldenNorm

/-- If `a` and `b` are not both even, `a² + ab − b²` is odd. -/
theorem norm_odd_of_not_both_even (a b : Int) (h : ¬ (2 ∣ a ∧ 2 ∣ b)) :
    (a * a + a * b - b * b) % 2 = 1 := by
  have ha : a % 2 = 0 ∨ a % 2 = 1 := by omega
  have hb : b % 2 = 0 ∨ b % 2 = 1 := by omega
  have key : (a * a + a * b - b * b) % 2
      = ((a % 2) * (a % 2) + (a % 2) * (b % 2) - (b % 2) * (b % 2)) % 2 := by
    rw [Int.sub_emod, Int.add_emod, Int.mul_emod a a, Int.mul_emod a b, Int.mul_emod b b]
    conv => rhs; rw [Int.sub_emod, Int.add_emod]
  rw [key]
  rcases ha with ha | ha <;> rcases hb with hb | hb
  · exact absurd ⟨Int.dvd_of_emod_eq_zero ha, Int.dvd_of_emod_eq_zero hb⟩ h
  all_goals (rw [ha, hb]; decide)

/-- Halving both coordinates divides the norm by 4. -/
theorem norm_double (a b : Int) :
    (2 * a) * (2 * a) + (2 * a) * (2 * b) - (2 * b) * (2 * b) = 4 * (a * a + a * b - b * b) := by
  grind

/-- **Main theorem.** For `(a, b) ≠ (0, 0)`, `a² + ab − b² = 4^k · m` with `m` odd.
Hence its 2-adic valuation is `2k`, which is even. -/
theorem norm_eq_four_pow_mul_odd :
    ∀ (n : Nat) (a b : Int), a.natAbs + b.natAbs ≤ n → (a ≠ 0 ∨ b ≠ 0) →
      ∃ k : Nat, ∃ m : Int, a * a + a * b - b * b = 4 ^ k * m ∧ m % 2 = 1 := by
  intro n
  induction n with
  | zero =>
    intro a b hn hne
    exfalso; omega
  | succ n ih =>
    intro a b hn hne
    by_cases h : 2 ∣ a ∧ 2 ∣ b
    · obtain ⟨⟨a', rfl⟩, ⟨b', rfl⟩⟩ := h
      have hne' : a' ≠ 0 ∨ b' ≠ 0 := by omega
      have hn' : a'.natAbs + b'.natAbs ≤ n := by omega
      obtain ⟨k, m, hk, hm⟩ := ih a' b' hn' hne'
      refine ⟨k + 1, m, ?_, hm⟩
      rw [norm_double, hk, Int.pow_succ]
      grind
    · exact ⟨0, a * a + a * b - b * b, by simp, norm_odd_of_not_both_even a b h⟩

/-- The same statement for the other sign convention `a² − ab − b²`
(`N(a + bφ)` with `φ² = 1 − φ`'s conjugate), by `b ↦ −b`. -/
theorem norm_eq_four_pow_mul_odd' (a b : Int) (hne : a ≠ 0 ∨ b ≠ 0) :
    ∃ k : Nat, ∃ m : Int, a * a - a * b - b * b = 4 ^ k * m ∧ m % 2 = 1 := by
  obtain ⟨k, m, hk, hm⟩ :=
    norm_eq_four_pow_mul_odd (a.natAbs + (-b).natAbs) a (-b) (Nat.le_refl _) (by omega)
  exact ⟨k, m, by rw [← hk]; grind, hm⟩

end CryptoResearch.Endosweep.RMGoldenNorm

#print axioms CryptoResearch.Endosweep.RMGoldenNorm.norm_eq_four_pow_mul_odd
#print axioms CryptoResearch.Endosweep.RMGoldenNorm.norm_eq_four_pow_mul_odd'
#check @CryptoResearch.Endosweep.RMGoldenNorm.norm_eq_four_pow_mul_odd

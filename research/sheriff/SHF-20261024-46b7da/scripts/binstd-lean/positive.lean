import CryptoResearch.Binstd.YieldCeiling

#print axioms CryptoResearch.Binstd.YieldCeiling.saturated_open_below_band
#print axioms CryptoResearch.Binstd.YieldCeiling.archived_counts_below_band

example : 0 < (40 : Nat) ∧ (40 : Nat) = 40 ∧ (40 : Nat) ≤ 40 := by decide
example : 4 * (40 : Nat) < 5 * 40 := by
  exact CryptoResearch.Binstd.YieldCeiling.saturated_open_below_band 40 40 40 (by decide) rfl (by decide)

/-
Arithmetic ceiling for the archived BINSTD Stage-1 ell=8/9 toy panels.

Source: knowledge/findings/KN-FIND-48f0ae.md, committed at
        3bed4d891777a15a44ecd577958c99279483696b.
Target: formal/targets/binstd-yield-ceiling.yaml.

The theorem treats the hit counts as hypotheses. It does not check the
experiment, elliptic-curve arithmetic, or the provenance of the JSON panels.
The frozen band 1.25 is represented exactly by 5 / 4: with a positive open
count, a tau/open ratio below 5 / 4 is equivalent to 4*tau < 5*open.
-/

import Mathlib.Tactic

namespace CryptoResearch.Binstd.YieldCeiling

/-- If the open arm reaches every target, no tau hit count bounded by the
number of targets can reach the frozen 1.25 tau/open band. -/
theorem saturated_open_below_band
    (targets tauHits openHits : Nat)
    (targets_pos : 0 < targets)
    (open_saturated : openHits = targets)
    (tau_bounded : tauHits ≤ targets) :
    4 * tauHits < 5 * openHits := by
  omega

/-- Arithmetic instantiation for the four archived hit-count pairs, in
panel order: ell89/ell8, ell89/ell9, ell89r1/ell8, ell89r1/ell9. -/
theorem archived_counts_below_band :
    4 * (16 : Nat) < 5 * 40 ∧
    4 * (40 : Nat) < 5 * 40 ∧
    4 * (20 : Nat) < 5 * 40 ∧
    4 * (40 : Nat) < 5 * 40 := by
  constructor
  · exact saturated_open_below_band 40 16 40 (by decide) rfl (by decide)
  constructor
  · exact saturated_open_below_band 40 40 40 (by decide) rfl (by decide)
  constructor
  · exact saturated_open_below_band 40 20 40 (by decide) rfl (by decide)
  · exact saturated_open_below_band 40 40 40 (by decide) rfl (by decide)

end CryptoResearch.Binstd.YieldCeiling

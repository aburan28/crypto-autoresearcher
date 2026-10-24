import CryptoResearch.Binstd.YieldCeiling

-- Known false when tauHits = openHits = targets = 40.
example (targets tauHits openHits : Nat)
    (targets_pos : 0 < targets)
    (open_saturated : openHits = targets)
    (tau_bounded : tauHits ≤ targets) :
    5 * tauHits < 5 * openHits := by
  omega

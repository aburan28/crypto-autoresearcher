/- Engineering controls for the verifier. These are not research findings. -/
namespace CryptoResearch.Smoke

theorem add_zero (n : Nat) : n + 0 = n := Nat.add_zero n

theorem eq_transitive {a b c : Nat} (hab : a = b) (hbc : b = c) : a = c :=
  Eq.trans hab hbc

end CryptoResearch.Smoke

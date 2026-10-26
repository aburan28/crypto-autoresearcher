import Init

/-!
An exact, finite certificate for the three bitmask polynomials in the archived
BINSTD n=17 toy inputs. Bit `i` of a natural number represents the coefficient
of `X^i` over F₂. The archived field modulus is `131081 = 2^17 + 2^3 + 1`;
the two degree-eight masks are `313` and `471`.

`remFuel` performs the recorded XOR-and-shift reduction on natural-number
encodings. `noSmallMonicDivisor` tries every monic encoded divisor of degree
one through half the encoded polynomial's degree. Its three concrete
equalities below are checked by Lean's kernel through `decide`.

This file does not prove that `remFuel` equals Euclidean remainder in
`(ZMod 2)[X]`, nor that the bitmasks denote the polynomials in
`Factorization.lean`. Consequently these equalities are finite encoded
certificates, not Lean irreducibility theorems or a Frobenius-model bridge.
-/

namespace CryptoResearch.Binstd.EncodedDivisors

/-- XOR reduction with enough fuel for the archived concrete inputs. -/
def remFuel : Nat → Nat → Nat → Nat
  | 0, p, _ => p
  | fuel + 1, p, d =>
      if d == 0 || p == 0 || Nat.log2 p < Nat.log2 d then p
      else remFuel fuel (Nat.xor p (d <<< (Nat.log2 p - Nat.log2 d))) d

/-- Test every monic bitmask divisor up to half the encoded degree. -/
def noSmallMonicDivisor (p : Nat) : Bool :=
  ((List.range (Nat.log2 p / 2)).all fun i =>
    let deg := i + 1
    ((List.range (2 ^ deg)).all fun lower =>
      remFuel (Nat.log2 p + 1) p (2 ^ deg + lower) != 0))

/-- Number of monic candidates traversed by `noSmallMonicDivisor`. -/
def trialCount (p : Nat) : Nat :=
  ((List.range (Nat.log2 p / 2)).map fun i => 2 ^ (i + 1)).foldl (· + ·) 0

set_option maxRecDepth 4096

/-- The archived field-modulus encoding survives all 510 finite trials. -/
theorem modulus17_no_small_monic_divisor :
    noSmallMonicDivisor 131081 = true := by decide

/-- The first archived degree-eight factor encoding survives 30 trials. -/
theorem factor8a_no_small_monic_divisor :
    noSmallMonicDivisor 313 = true := by decide

/-- The second archived degree-eight factor encoding survives 30 trials. -/
theorem factor8b_no_small_monic_divisor :
    noSmallMonicDivisor 471 = true := by decide

/-- The exact finite search sizes are part of the certificate. -/
theorem archived_trial_counts :
    trialCount 131081 = 510 ∧
    trialCount 313 = 30 ∧
    trialCount 471 = 30 := by decide

/-- One target declaration binds all three exact encoded trial results. -/
theorem archived_no_small_monic_divisors :
    noSmallMonicDivisor 131081 = true ∧
    noSmallMonicDivisor 313 = true ∧
    noSmallMonicDivisor 471 = true ∧
    trialCount 131081 = 510 ∧
    trialCount 313 = 30 ∧
    trialCount 471 = 30 := by
  exact ⟨modulus17_no_small_monic_divisor,
    factor8a_no_small_monic_divisor,
    factor8b_no_small_monic_divisor,
    archived_trial_counts⟩

end CryptoResearch.Binstd.EncodedDivisors

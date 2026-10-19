/- R1 semantic-fidelity scratch checks (never part of the repo). -/
import CryptoResearch.Endosweep.NistCertificates
import CryptoResearch.Endosweep.Koblitz

open CryptoResearch.Endosweep
open CryptoResearch.Endosweep.Discriminant

/-! ## A. Statements as the kernel sees them -/
#check @Discriminant.isFundamental_of_primes
#check @Discriminant.minNonscalarDegree_isLeast
#check @Discriminant.prod_mul_bound_le_of_eq_mul_sq
#check @NistCertificates.B571.abs_DK_lower_bound
#check @NistCertificates.exact_discriminants
#check @NistCertificates.finding3_bounds
#check @NistCertificates.koblitz_discriminants
#check @Koblitz.koblitz_certificates
#check @Koblitz.norm_delta
#check @Koblitz.norm_one_sub_tau_pow
#check @Koblitz.min_norm_nonscalar
#check @Koblitz.ztau_iso_order_neg_seven

/-! ## B. Axioms -/
#print axioms Discriminant.isFundamental_of_primes
#print axioms Discriminant.minNonscalarDegree_isLeast
#print axioms Discriminant.prod_mul_bound_le_of_eq_mul_sq
#print axioms NistCertificates.B571.abs_DK_lower_bound
#print axioms NistCertificates.exact_discriminants
#print axioms NistCertificates.finding3_bounds
#print axioms NistCertificates.koblitz_discriminants
#print axioms Koblitz.koblitz_certificates
#print axioms Koblitz.norm_delta
#print axioms Koblitz.norm_one_sub_tau_pow
#print axioms Koblitz.min_norm_nonscalar
#print axioms Koblitz.ztau_iso_order_neg_seven

/-! ## C. Definitions vs quadorder.py / binary.py (numeric spot checks) -/
-- (D, Tr ω, N ω, minNonscalarDegree, brute-force min of norm over |a| ≤ 40, 1 ≤ |b| ≤ 3)
def bruteMin (D : Int) : Int := Id.run do
  let mut best : Int := 1000000000
  for a in List.range 81 do
    for b in [-3, -2, -1, 1, 2, 3] do
      let v := norm D ((a : Int) - 40) b
      if v < best then best := v
  return best

#eval [-3, -4, -7, -8, -11, -12, -15, -16, -19, -20, -23, -24, -27, -28, -31, -35, -40, -51, -52, -99, -100, -163].map
  fun D => (D, omegaTrace D, omegaNorm D, minNonscalarDegree D, bruteMin D, decide (IsDisc D))

-- all discriminants down to -2000: minNonscalarDegree equals brute force (true/false)
#eval ((List.range 2000).map (fun (k : Nat) => -((k : Int) + 1))).filter (fun D => decide (IsDisc D))
  |>.all (fun D => minNonscalarDegree D == bruteMin D)

-- Lucas sequence vs binary.lucas_trace, mu = +-1, m = 0..12
#eval (List.range 13).map fun m => (m, Koblitz.lucasV 1 m, Koblitz.lucasV (-1) m)

-- IsFundamental is decidable only via its pieces; check the standard small list by hand
-- -3,-4,-7,-8,-11,-15,-19,-20,-23,-24 are fundamental; -12,-16,-27,-28 are not.

/-! ## D. Satisfiability witnesses for the hypothesis sets -/

-- isFundamental_of_primes, branch D ≡ 1 (mod 4): core = 3·5, D = -15
example : IsFundamental (-15) :=
  isFundamental_of_primes [3, 5] (by decide)
    (fun p hp => by
      simp only [List.mem_cons, List.mem_nil_iff, or_false] at hp
      rcases hp with rfl | rfl
      · exact isPrimeNat_of_trial 2 (by decide) (by decide) (by decide)
      · exact isPrimeNat_of_trial 3 (by decide) (by decide) (by decide))
    (-15) (.inl ⟨by decide, by decide⟩)

-- isFundamental_of_primes, branch D = -4·core: core = 5 (−5 ≡ 3 mod 4), D = -20
example : IsFundamental (-20) :=
  isFundamental_of_primes [5] (by decide)
    (fun p hp => by
      simp only [List.mem_singleton] at hp
      subst hp
      exact isPrimeNat_of_trial 3 (by decide) (by decide) (by decide))
    (-20) (.inr ⟨by decide, .inr (by decide)⟩)

-- isFundamental_of_primes, branch D = -4·core with −core ≡ 2: core = 2, D = -8
example : IsFundamental (-8) :=
  isFundamental_of_primes [2] (by decide)
    (fun p hp => by
      simp only [List.mem_singleton] at hp
      subst hp
      exact isPrimeNat_of_trial 2 (by decide) (by decide) (by decide))
    (-8) (.inr ⟨by decide, .inl (by decide)⟩)

-- minNonscalarDegree_isLeast: IsDisc is satisfiable (D = -7, -8, -20)
example : IsDisc (-7) ∧ IsDisc (-8) ∧ IsDisc (-20) := by decide

-- prod_mul_bound_le_of_eq_mul_sq: P = 2·3² = 18 (2 to an odd power, 3 to an even power),
-- C = 35 = 5·7 (not a square, no divisor in (1, 5)), B = 5, N = 630 = 70·3².
example : [2].prod * 5 ≤ 70 :=
  prod_mul_bound_le_of_eq_mul_sq 18 35 5 [2] (by decide) (by decide)
    (not_square_of_between (r := 5) (by decide) (by decide))
    (fun d h1 h2 hd => by
      have : d = 2 ∨ d = 3 ∨ d = 4 := by omega
      rcases this with rfl | rfl | rfl <;> exact absurd hd (by decide))
    (by decide)
    (fun p hp => by
      simp only [List.mem_singleton] at hp
      subst hp
      exact isPrimeNat_of_trial 2 (by decide) (by decide) (by decide))
    (fun p hp => by
      simp only [List.mem_singleton] at hp
      subst hp
      exact ⟨1, 9, by decide, by decide, by decide⟩)
    70 3 (by decide)

-- and the bound is tight-ish / non-trivial: the squarefree part 70 = 2·5·7 ≥ 2·5
-- B-571: the D,f premise is satisfiable (D = t² − 4q, f = 1), so under (i),(ii) the
-- conclusion is about an actual integer, not vacuous.
example (hlarge : ∀ p ∈ [5608493523058319, 3563521804312876303], IsPrimeNat p)
    (htrial : ∀ d, 1 < d → d < NistCertificates.B571.B → ¬ d ∣ NistCertificates.B571.C) :
    NistCertificates.B571.absDKAtLeast ≤
      (NistCertificates.B571.t ^ 2 - 4 * NistCertificates.B571.q).natAbs :=
  (NistCertificates.B571.abs_DK_lower_bound hlarge htrial _ 1 (by simp)).1

-- B-571 (ii) restricted to small d is provable here (sanity: the hypothesis is not false
-- on an initial segment); the full range is checked by R1's Python trial division.
example : NistCertificates.noDivBelow NistCertificates.B571.C 2000 = true := by decide +kernel

-- norm_delta: hypothesis satisfiable for m = 1 (δ = 1) and by every KCert
example (μ : Int) : Koblitz.Zt.mul μ Koblitz.Zt.one (Koblitz.Zt.sub Koblitz.Zt.tau Koblitz.Zt.one)
    = Koblitz.Zt.sub (Koblitz.Zt.pow μ Koblitz.Zt.tau 1) Koblitz.Zt.one := by
  simp [Koblitz.Zt.mul, Koblitz.Zt.one, Koblitz.Zt.sub, Koblitz.Zt.tau, Koblitz.Zt.pow]

/-! ## E. Data spot checks (independent of the generator) -/
#eval (NistCertificates.K163.q == 2 ^ 163, NistCertificates.K571.q == 2 ^ 571,
       NistCertificates.B571.q == 2 ^ 571)
#eval Koblitz.koblitzCerts.map fun c => (c.m, c.μ, c.h, c.n.toNat.log2)

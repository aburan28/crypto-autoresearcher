/-
Imaginary quadratic orders as the endosweep uses them: the smallest norm of a
non-scalar element, fundamental discriminants from a prime factorisation, and
the lower bound on a squarefree part that a partial factorisation proves.

Sources:  harness/endosweep/quadorder.py (`min_nonscalar_degree`),
          harness/endosweep/nist.py (`exact_discriminant`, `partial_factorization`),
          research/endosweep_nist_20261006/README.md ("What is checked", finding 4,
          and the "Lean verification" section).
Targets:  formal/targets/endosweep-disc-min-nonscalar-degree.yaml
          formal/targets/endosweep-disc-fundamental-from-primes.yaml
          formal/targets/endosweep-disc-squarefree-part-bound.yaml

Core Lean only (no Mathlib): every statement here is about `Int`/`Nat`.
Primality is the explicit predicate `IsPrimeNat` defined below (the textbook
definition), so the primality of a 40-digit factor is always a HYPOTHESIS of
a theorem in this lane, never something this file asserts.

WHAT IS NOT PROVED HERE.  The bridge from elliptic curves to orders --
End(E) is an order of Q(sqrt(t^2 - 4q)) containing Z[pi], deg = norm, and the
order of a fundamental discriminant is the maximal one -- is classical theory
(Deuring, Waterhouse) and is not formalised.  Neither is the uniqueness of the
fundamental discriminant in a square class.  What is proved is the arithmetic
the sweeper does on top of that theory.
-/

namespace CryptoResearch.Endosweep.Discriminant

/-! ## 1. The norm form of the order of discriminant `D` and its least non-scalar value -/

/-- `Tr ω = D mod 2`, with `ω = (τ + √D)/2`.  Python's `D % 2` for `D < 0` is
Lean's `Int.emod`, so this is literally `quadorder.omega_trace_norm`'s `tau`. -/
def omegaTrace (D : Int) : Int := D % 2

/-- `N ω = (τ² − D)/4`, as in `quadorder.omega_trace_norm`. -/
def omegaNorm (D : Int) : Int := (omegaTrace D * omegaTrace D - D) / 4

/-- `N(a + bω) = a² + abτ + b²·N(ω)`, as in `quadorder.norm`. -/
def norm (D a b : Int) : Int := a * a + a * b * omegaTrace D + b * b * omegaNorm D

/-- `quadorder.min_nonscalar_degree`: `(|D| + (D mod 2)) // 4`. -/
def minNonscalarDegree (D : Int) : Int := ((D.natAbs : Int) + D % 2) / 4

/-- A negative discriminant: `D < 0` and `D ≡ 0, 1 (mod 4)` (`quadorder.is_discriminant`). -/
def IsDisc (D : Int) : Prop := D < 0 ∧ (D % 4 = 0 ∨ D % 4 = 1)

instance (D : Int) : Decidable (IsDisc D) := inferInstanceAs (Decidable (_ ∧ _))

private theorem trace_cases {D : Int} (hD : IsDisc D) :
    (omegaTrace D = 0 ∧ 4 * omegaNorm D = -D) ∨ (omegaTrace D = 1 ∧ 4 * omegaNorm D = 1 - D) := by
  unfold omegaNorm omegaTrace
  rcases hD with ⟨_, h | h⟩
  · left
    have h2 : D % 2 = 0 := by omega
    rw [h2]; omega
  · right
    have h2 : D % 2 = 1 := by omega
    rw [h2]; omega

/-- Completing the square: `4·N(a + bω) = (2a + bτ)² + b²·|D|`. -/
theorem four_mul_norm {D : Int} (hD : IsDisc D) (a b : Int) :
    4 * norm D a b = (2 * a + b * omegaTrace D) * (2 * a + b * omegaTrace D) + b * b * (-D) := by
  unfold norm
  rcases trace_cases hD with ⟨ht, hn⟩ | ⟨ht, hn⟩
  · rw [ht]
    have : 4 * (a * a + a * b * 0 + b * b * omegaNorm D)
        = 4 * a * a + b * b * (4 * omegaNorm D) := by grind
    rw [this, hn]; grind
  · rw [ht]
    have : 4 * (a * a + a * b * 1 + b * b * omegaNorm D)
        = 4 * a * a + 4 * a * b + b * b * (4 * omegaNorm D) := by grind
    rw [this, hn]; grind

private theorem one_le_mul_self {b : Int} (hb : b ≠ 0) : 1 ≤ b * b := by
  rcases Int.lt_or_gt_of_ne hb with h | h
  · have h' : 0 < -b := by omega
    have := Int.mul_pos h' h'
    rw [Int.neg_mul_neg] at this
    omega
  · have := Int.mul_pos h h
    omega

private theorem natAbs_of_disc {D : Int} (hD : IsDisc D) : (D.natAbs : Int) = -D :=
  Int.ofNat_natAbs_of_nonpos (by have := hD.1; omega)

/-- `4 · min_nonscalar_degree(D) ≥ |D|`, i.e. the degree bound is at least `|D|/4`. -/
theorem natAbs_le_four_mul_minNonscalarDegree {D : Int} (hD : IsDisc D) :
    (D.natAbs : Int) ≤ 4 * minNonscalarDegree D := by
  unfold minNonscalarDegree
  rw [natAbs_of_disc hD]
  rcases hD with ⟨_, h | h⟩ <;> omega

/-- **The least norm of a non-scalar element.**  For every negative discriminant
`D` (`D < 0`, `D ≡ 0, 1 mod 4`), every element `a + bω` of the order of
discriminant `D` with `b ≠ 0` has norm at least `(|D| + (D mod 2))/4`, and
`ω` itself (`a = 0`, `b = 1`) attains it.  So `min_nonscalar_degree(D)` is
exactly the minimum of `N(a + bω)` over `b ≠ 0`, as its docstring derives.

Not proved here: that the degree of an endomorphism is the norm of the
corresponding element of End(E) (standard theory, not formalised). -/
theorem minNonscalarDegree_isLeast {D : Int} (hD : IsDisc D) :
    (∀ a b : Int, b ≠ 0 → minNonscalarDegree D ≤ norm D a b) ∧
      norm D 0 1 = minNonscalarDegree D := by
  have habs := natAbs_of_disc hD
  constructor
  · intro a b hb
    have h4 := four_mul_norm hD a b
    have hsq : 0 ≤ (2 * a + b * omegaTrace D) * (2 * a + b * omegaTrace D) := by
      have := Int.sq_nonneg (2 * a + b * omegaTrace D); rw [Int.pow_succ, Int.pow_one] at this; exact this
    have hbb := one_le_mul_self hb
    have hpos : 0 < -D := by have := hD.1; omega
    have hge : -D ≤ b * b * (-D) := by
      have := Int.mul_nonneg (show 0 ≤ b * b - 1 by omega) (Int.le_of_lt hpos)
      rw [Int.sub_mul, Int.one_mul] at this
      omega
    unfold minNonscalarDegree
    rw [habs]
    rcases hD with ⟨_, h | h⟩ <;> omega
  · unfold norm minNonscalarDegree
    rw [habs]
    rcases trace_cases hD with ⟨ht, hn⟩ | ⟨ht, hn⟩
    · rw [ht]; unfold omegaTrace at ht; omega
    · rw [ht]; unfold omegaTrace at ht; omega

/-! ## 2. Primes, squarefree numbers, fundamental discriminants -/

/-- The textbook definition of a prime, stated in core Lean. -/
def IsPrimeNat (p : Nat) : Prop := 2 ≤ p ∧ ∀ d, d ∣ p → d = 1 ∨ d = p

/-- `n` is squarefree: the only `m` with `m² ∣ n` is `m = 1`. -/
def SqFree (n : Nat) : Prop := ∀ m, m * m ∣ n → m = 1

/-- A fundamental (field) discriminant `D < 0`: either `D ≡ 1 (mod 4)` and
squarefree, or `D = 4m` with `m ≡ 2, 3 (mod 4)` and `m` squarefree
(`quadorder.is_fundamental`). -/
def IsFundamental (D : Int) : Prop :=
  D < 0 ∧ ((D % 4 = 1 ∧ SqFree D.natAbs) ∨
    (D % 4 = 0 ∧ ((D / 4) % 4 = 2 ∨ (D / 4) % 4 = 3) ∧ SqFree (D / 4).natAbs))

theorem IsPrimeNat.pos {p : Nat} (hp : IsPrimeNat p) : 0 < p := by have := hp.1; omega

theorem IsPrimeNat.not_dvd_one {p : Nat} (hp : IsPrimeNat p) : ¬ p ∣ 1 := by
  intro h; have := Nat.le_of_dvd Nat.one_pos h; have := hp.1; omega

theorem IsPrimeNat.coprime_of_not_dvd {p a : Nat} (hp : IsPrimeNat p) (h : ¬ p ∣ a) :
    Nat.Coprime p a := by
  rcases hp.2 _ (Nat.gcd_dvd_left p a) with h1 | h1
  · exact h1
  · exact absurd (h1 ▸ Nat.gcd_dvd_right p a) h

/-- Euclid's lemma. -/
theorem IsPrimeNat.dvd_mul {p a b : Nat} (hp : IsPrimeNat p) (h : p ∣ a * b) : p ∣ a ∨ p ∣ b := by
  by_cases ha : p ∣ a
  · exact .inl ha
  · exact .inr ((hp.coprime_of_not_dvd ha).dvd_of_dvd_mul_left h)

theorem IsPrimeNat.dvd_of_dvd_pow {p a : Nat} (hp : IsPrimeNat p) : ∀ e, p ∣ a ^ e → p ∣ a
  | 0, h => absurd (by simpa using h) hp.not_dvd_one
  | e + 1, h => by
    rw [Nat.pow_succ] at h
    rcases hp.dvd_mul h with h | h
    · exact hp.dvd_of_dvd_pow e h
    · exact h

theorem IsPrimeNat.eq_of_dvd {p q : Nat} (hp : IsPrimeNat p) (hq : IsPrimeNat q) (h : p ∣ q) :
    p = q := by
  rcases hq.2 p h with h1 | h1
  · have := hp.1; omega
  · exact h1

theorem IsPrimeNat.mem_of_dvd_prod {p : Nat} (hp : IsPrimeNat p) :
    ∀ (l : List Nat), (∀ q ∈ l, IsPrimeNat q) → p ∣ l.prod → p ∈ l
  | [], _, h => absurd (by simpa using h) hp.not_dvd_one
  | q :: l, hl, h => by
    rw [List.prod_cons] at h
    rcases hp.dvd_mul h with h | h
    · exact (hp.eq_of_dvd (hl q (by simp)) h) ▸ (by simp)
    · exact List.mem_cons_of_mem q (hp.mem_of_dvd_prod l (fun r hr => hl r (by simp [hr])) h)

/-- A product of distinct primes is squarefree. -/
theorem sqFree_prod : ∀ (l : List Nat), l.Nodup → (∀ p ∈ l, IsPrimeNat p) → SqFree l.prod
  | [], _, _ => by
    intro m hm
    exact Nat.eq_one_of_dvd_one (Nat.dvd_trans (Nat.dvd_mul_right m m) (by simpa using hm))
  | p :: l, hd, hp => by
    intro m hm
    rw [List.nodup_cons] at hd
    have hpp : IsPrimeNat p := hp p (by simp)
    have hl : ∀ q ∈ l, IsPrimeNat q := fun q hq => hp q (by simp [hq])
    rw [List.prod_cons] at hm
    by_cases hpm : p ∣ m
    · obtain ⟨k, rfl⟩ := hpm
      have h1 : p * (p * (k * k)) ∣ p * l.prod := by
        have : p * k * (p * k) = p * (p * (k * k)) := by grind
        rw [← this]; exact hm
      have h2 : p * (k * k) ∣ l.prod := Nat.dvd_of_mul_dvd_mul_left hpp.pos h1
      exact absurd (hpp.mem_of_dvd_prod l hl (Nat.dvd_trans (Nat.dvd_mul_right p _) h2)) hd.1
    · have hc : Nat.Coprime (m * m) p :=
        (Nat.Coprime.mul_right (hpp.coprime_of_not_dvd hpm) (hpp.coprime_of_not_dvd hpm)).symm
      exact sqFree_prod l hd.2 hl m (hc.dvd_of_dvd_mul_left hm)

/-- **D_K from a factorisation** (`nist.exact_discriminant`).  If `core` is a
product of distinct primes and `D = −core` with `D ≡ 1 (mod 4)`, or
`D = −4·core` with `−core ≡ 2, 3 (mod 4)`, then `D` is a fundamental
discriminant.  The primality of the factors is a hypothesis. -/
theorem isFundamental_of_primes (os : List Nat) (hd : os.Nodup) (hp : ∀ p ∈ os, IsPrimeNat p)
    (D : Int)
    (hD : (D = -(os.prod : Int) ∧ D % 4 = 1) ∨
      (D = -4 * (os.prod : Int) ∧ ((-(os.prod : Int)) % 4 = 2 ∨ (-(os.prod : Int)) % 4 = 3))) :
    IsFundamental D := by
  have hsq := sqFree_prod os hd hp
  rcases hD with ⟨rfl, h⟩ | ⟨rfl, h⟩
  · refine ⟨by omega, .inl ⟨h, ?_⟩⟩
    rw [Int.natAbs_neg, Int.natAbs_natCast]; exact hsq
  · refine ⟨by omega, .inr ⟨by omega, ?_, ?_⟩⟩
    · rw [show -4 * (os.prod : Int) = 4 * (-(os.prod : Int)) by omega,
        Int.mul_ediv_cancel_left _ (by decide)]
      exact h
    · rw [show -4 * (os.prod : Int) = 4 * (-(os.prod : Int)) by omega,
        Int.mul_ediv_cancel_left _ (by decide), Int.natAbs_neg, Int.natAbs_natCast]
      exact hsq

/-- Trial division up to `r` with `p < r²` proves primality.  Used to discharge
the primality of the small factors by `decide`; large factors stay hypotheses. -/
theorem isPrimeNat_of_trial {p : Nat} (r : Nat) (h2 : 2 ≤ p) (hr : p < r * r)
    (h : ∀ d, d < r → 2 ≤ d → p % d ≠ 0) : IsPrimeNat p := by
  refine ⟨h2, fun d hd => ?_⟩
  obtain ⟨e, he⟩ := hd
  have hd0 : d ≠ 0 := by rintro rfl; omega
  have he0 : e ≠ 0 := by rintro rfl; omega
  by_cases hd1 : d = 1
  · exact .inl hd1
  by_cases he1 : e = 1
  · subst he1; exact .inr (by omega)
  exfalso
  by_cases hdr : d < r
  · exact h d hdr (by omega) (Nat.mod_eq_zero_of_dvd ⟨e, he⟩)
  by_cases her : e < r
  · exact h e her (by omega) (Nat.mod_eq_zero_of_dvd ⟨d, by rw [he, Nat.mul_comm]⟩)
  have : r * r ≤ d * e := Nat.mul_le_mul (by omega) (by omega)
  omega

/-! ## 3. What a partial factorisation proves about the squarefree part -/

/-- A prime dividing `N = s·k²` to an odd exact power divides `s`. -/
theorem dvd_of_odd_exponent {p : Nat} (hp : IsPrimeNat p) :
    ∀ (e M s k : Nat), ¬ p ∣ M → e % 2 = 1 → p ^ e * M = s * (k * k) → p ∣ s := by
  intro e
  induction e using Nat.strongRecOn with
  | ind e ih =>
    intro M s k hM he h
    apply Classical.byContradiction
    intro hs
    have hpe : p ∣ p ^ e * M := by
      obtain ⟨e', rfl⟩ : ∃ e', e = e' + 1 := ⟨e - 1, by omega⟩
      rw [Nat.pow_succ]
      exact Nat.dvd_trans (Nat.dvd_mul_left p _) (Nat.dvd_mul_right _ M)
    rw [h] at hpe
    have hk : p ∣ k := by
      rcases hp.dvd_mul hpe with h' | h'
      · exact absurd h' hs
      · rcases hp.dvd_mul h' with h'' | h'' <;> exact h''
    obtain ⟨k', rfl⟩ := hk
    have h' : p ^ e * M = p * (p * (s * (k' * k'))) := by rw [h]; grind
    by_cases he1 : e = 1
    · subst he1
      rw [Nat.pow_one] at h'
      have : M = p * (s * (k' * k')) := Nat.eq_of_mul_eq_mul_left hp.pos h'
      exact hM ⟨_, this⟩
    · obtain ⟨e2, rfl⟩ : ∃ e2, e = e2 + 2 := ⟨e - 2, by omega⟩
      have h'' : p * (p * (p ^ e2 * M)) = p * (p * (s * (k' * k'))) := by
        rw [← h']; grind
      have h3 : p ^ e2 * M = s * (k' * k') :=
        Nat.eq_of_mul_eq_mul_left hp.pos (Nat.eq_of_mul_eq_mul_left hp.pos h'')
      exact hs (ih e2 (by omega) M s k' hM (by omega) h3)

theorem exists_prime_dvd : ∀ n, 2 ≤ n → ∃ p, IsPrimeNat p ∧ p ∣ n := by
  intro n
  induction n using Nat.strongRecOn with
  | ind n ih =>
    intro hn
    by_cases hpn : IsPrimeNat n
    · exact ⟨n, hpn, Nat.dvd_refl n⟩
    · have : ∃ d, d ∣ n ∧ d ≠ 1 ∧ d ≠ n := by
        apply Classical.byContradiction
        intro hno
        exact hpn ⟨hn, fun d hd => by
          apply Classical.byContradiction
          intro hne
          exact hno ⟨d, hd, fun h => hne (.inl h), fun h => hne (.inr h)⟩⟩
      obtain ⟨d, hd, hd1, hdn⟩ := this
      have hd0 : d ≠ 0 := by rintro rfl; have := Nat.eq_zero_of_zero_dvd hd; omega
      have hlt : d < n := by have := Nat.le_of_dvd (by omega) hd; omega
      obtain ⟨p, hp, hpd⟩ := ih d hlt (by omega)
      exact ⟨p, hp, Nat.dvd_trans hpd hd⟩

theorem exists_pow_mul {q : Nat} (hq : 2 ≤ q) :
    ∀ n, 0 < n → ∃ e M, n = q ^ e * M ∧ ¬ q ∣ M := by
  intro n
  induction n using Nat.strongRecOn with
  | ind n ih =>
    intro hn
    by_cases hqn : q ∣ n
    · obtain ⟨n', rfl⟩ := hqn
      have hn' : 0 < n' := by
        rcases Nat.eq_zero_or_pos n' with h | h
        · subst h; omega
        · exact h
      have hlt : n' < q * n' := by
        have : 2 * n' ≤ q * n' := Nat.mul_le_mul_right n' hq
        omega
      obtain ⟨e, M, h1, h2⟩ := ih n' hlt hn'
      exact ⟨e + 1, M, by rw [h1, Nat.pow_succ]; grind, h2⟩
    · exact ⟨0, n, by simp, hqn⟩

/-- A number `C > 1` that is not a perfect square and has no divisor `d` with
`1 < d < B` has a prime factor `q ≥ B` to an odd exact power. -/
theorem exists_large_odd_prime (B : Nat) :
    ∀ C, 1 < C → (∀ r, r * r ≠ C) → (∀ d, 1 < d → d < B → ¬ d ∣ C) →
      ∃ q e M, IsPrimeNat q ∧ B ≤ q ∧ C = q ^ e * M ∧ ¬ q ∣ M ∧ e % 2 = 1 := by
  intro C
  induction C using Nat.strongRecOn with
  | ind C ih =>
    intro hC hnsq hsmall
    obtain ⟨q, hq, hqC⟩ := exists_prime_dvd C hC
    have hBq : B ≤ q := by
      apply Classical.byContradiction
      intro hlt
      exact hsmall q (by have := hq.1; omega) (by omega) hqC
    obtain ⟨e, M, hCM, hqM⟩ := exists_pow_mul hq.1 C (by omega)
    have he0 : e ≠ 0 := by
      rintro rfl
      rw [Nat.pow_zero, Nat.one_mul] at hCM
      exact hqM (hCM ▸ hqC)
    by_cases hodd : e % 2 = 1
    · exact ⟨q, e, M, hq, hBq, hCM, hqM, hodd⟩
    obtain ⟨j, rfl⟩ : ∃ j, e = 2 * j := ⟨e / 2, by omega⟩
    have hsq : q ^ (2 * j) = q ^ j * q ^ j := by rw [Nat.two_mul, Nat.pow_add]
    have hM0 : 0 < M := by
      rcases Nat.eq_zero_or_pos M with h | h
      · subst h; rw [Nat.mul_zero] at hCM; omega
      · exact h
    have hM1 : 1 < M := by
      apply Classical.byContradiction
      intro h
      have : M = 1 := by omega
      subst this
      exact hnsq (q ^ j) (by rw [hCM, Nat.mul_one, hsq])
    have hMsq : ∀ r, r * r ≠ M := by
      intro r hr
      exact hnsq (q ^ j * r) (by rw [hCM, hsq, ← hr]; grind)
    have hMlt : M < C := by
      have h1 : q ≤ q ^ (2 * j) := by
        obtain ⟨j', hj'⟩ : ∃ j', 2 * j = j' + 1 := ⟨2 * j - 1, by omega⟩
        rw [hj', Nat.pow_succ]
        exact Nat.le_mul_of_pos_left q (Nat.pow_pos hq.pos)
      have h2 : 2 * M ≤ q ^ (2 * j) * M := Nat.mul_le_mul_right M (by have := hq.1; omega)
      omega
    have hMsmall : ∀ d, 1 < d → d < B → ¬ d ∣ M := by
      intro d h1 h2 hd
      exact hsmall d h1 h2 (hCM ▸ Nat.dvd_trans hd (Nat.dvd_mul_left M _))
    obtain ⟨q', e', M', hq', hBq', hMM', hq'M', hodd'⟩ := ih M hMlt hM1 hMsq hMsmall
    refine ⟨q', e', q ^ (2 * j) * M', hq', hBq', ?_, ?_, hodd'⟩
    · rw [hCM, hMM']; grind
    · intro hdiv
      rcases hq'.dvd_mul hdiv with h | h
      · have hqq : q' = q := hq'.eq_of_dvd hq (hq'.dvd_of_dvd_pow _ h)
        have : q' ∣ M := by
          rw [hMM']
          obtain ⟨e'', rfl⟩ : ∃ e'', e' = e'' + 1 := ⟨e' - 1, by omega⟩
          rw [Nat.pow_succ]
          exact Nat.dvd_trans (Nat.dvd_mul_left q' _) (Nat.dvd_mul_right _ M')
        exact hqM (hqq ▸ this)
      · exact hq'M' h

/-- Distinct primes that all divide `s` have their product dividing `s`. -/
theorem prod_dvd_of_primes {s : Nat} :
    ∀ (l : List Nat), l.Nodup → (∀ p ∈ l, IsPrimeNat p) → (∀ p ∈ l, p ∣ s) → l.prod ∣ s
  | [], _, _, _ => by simp
  | p :: l, hd, hp, hdiv => by
    rw [List.nodup_cons] at hd
    rw [List.prod_cons]
    have hpp : IsPrimeNat p := hp p (by simp)
    have hl : ∀ q ∈ l, IsPrimeNat q := fun q hq => hp q (by simp [hq])
    have hc : Nat.Coprime p l.prod :=
      hpp.coprime_of_not_dvd (fun h => hd.1 (hpp.mem_of_dvd_prod l hl h))
    exact hc.mul_dvd_of_dvd_of_dvd (hdiv p (by simp))
      (prod_dvd_of_primes l hd.2 hl (fun q hq => hdiv q (by simp [hq])))

/-- **The squarefree-part bound of a partial factorisation** (README finding 4,
`nist.partial_factorization`).  Let `N = P·C` with `gcd(P, C) = 1`, where
`C > 1` is not a perfect square and has no divisor `d` with `1 < d < B`, and
let `os` be distinct primes each dividing `P` to an odd exact power.  Then
every way of writing `N = s·k²` has `s ≥ (∏ os)·B`.  In particular the
squarefree part of `N` -- and `|D_K|` whenever `4q − t² = |D_K|·f²` -- is at
least `(∏ os)·B`. -/
theorem prod_mul_bound_le_of_eq_mul_sq (P C B : Nat) (os : List Nat)
    (hcop : Nat.Coprime P C) (hC : 1 < C) (hnsq : ∀ r, r * r ≠ C)
    (hsmall : ∀ d, 1 < d → d < B → ¬ d ∣ C)
    (hos : os.Nodup) (hprime : ∀ p ∈ os, IsPrimeNat p)
    (hodd : ∀ p ∈ os, ∃ e M, P = p ^ e * M ∧ ¬ p ∣ M ∧ e % 2 = 1)
    (s k : Nat) (h : P * C = s * (k * k)) : os.prod * B ≤ s := by
  have hP : P ≠ 0 := by
    rintro rfl
    rw [Nat.Coprime, Nat.gcd_zero_left] at hcop
    omega
  have hs : 0 < s := by
    rcases Nat.eq_zero_or_pos s with h0 | h0
    · subst h0
      rw [Nat.zero_mul] at h
      rcases Nat.mul_eq_zero.mp h with h1 | h1 <;> omega
    · exact h0
  -- a prime p dividing both P and C would divide gcd(P, C) = 1
  have hnot_both : ∀ p, IsPrimeNat p → p ∣ P → ¬ p ∣ C := by
    intro p hp hpP hpC
    have := Nat.dvd_gcd hpP hpC
    rw [hcop.gcd_eq_one] at this
    exact hp.not_dvd_one this
  obtain ⟨q, e, M, hq, hBq, hCM, hqM, hodd_q⟩ := exists_large_odd_prime B C hC hnsq hsmall
  have hqC : q ∣ C := by
    rw [hCM]
    obtain ⟨e', rfl⟩ : ∃ e', e = e' + 1 := ⟨e - 1, by omega⟩
    rw [Nat.pow_succ]
    exact Nat.dvd_trans (Nat.dvd_mul_left q _) (Nat.dvd_mul_right _ M)
  have hqP : ¬ q ∣ P := fun hqP => hnot_both q hq hqP hqC
  have hqs : q ∣ s := by
    refine dvd_of_odd_exponent hq e (M * P) s k ?_ hodd_q (by rw [← h, hCM]; grind)
    intro hdiv
    rcases hq.dvd_mul hdiv with h1 | h1
    · exact hqM h1
    · exact hqP h1
  have hps : ∀ p ∈ os, p ∣ s := by
    intro p hpos
    obtain ⟨e, M, hPM, hpM, hoddp⟩ := hodd p hpos
    have hpp := hprime p hpos
    have hpP : p ∣ P := by
      rw [hPM]
      obtain ⟨e', rfl⟩ : ∃ e', e = e' + 1 := ⟨e - 1, by omega⟩
      rw [Nat.pow_succ]
      exact Nat.dvd_trans (Nat.dvd_mul_left p _) (Nat.dvd_mul_right _ M)
    refine dvd_of_odd_exponent hpp e (M * C) s k ?_ hoddp (by rw [← h, hPM]; grind)
    intro hdiv
    rcases hpp.dvd_mul hdiv with h1 | h1
    · exact hpM h1
    · exact hnot_both p hpp hpP h1
  have hqos : q ∉ os := by
    intro hmem
    obtain ⟨e, M, hPM, _, hoddp⟩ := hodd q hmem
    apply hqP
    rw [hPM]
    obtain ⟨e', rfl⟩ : ∃ e', e = e' + 1 := ⟨e - 1, by omega⟩
    rw [Nat.pow_succ]
    exact Nat.dvd_trans (Nat.dvd_mul_left q _) (Nat.dvd_mul_right _ M)
  have hall : (q :: os).prod ∣ s :=
    prod_dvd_of_primes (q :: os) (List.nodup_cons.mpr ⟨hqos, hos⟩)
      (fun p hp => by
        rcases List.mem_cons.mp hp with rfl | hp
        · exact hq
        · exact hprime p hp)
      (fun p hp => by
        rcases List.mem_cons.mp hp with rfl | hp
        · exact hqs
        · exact hps p hp)
  rw [List.prod_cons] at hall
  have h1 : q * os.prod ≤ s := Nat.le_of_dvd hs hall
  have h2 : os.prod * B ≤ os.prod * q := Nat.mul_le_mul_left _ hBq
  rw [Nat.mul_comm q] at h1
  omega

/-- The bound transported to a discriminant: if `4q − t² = P·C` as above and
`t² − 4q = D·f²` for integers `D, f`, then `|D| ≥ (∏ os)·B`, and if `D` is a
discriminant every non-scalar element of its order has norm at least
`(∏ os)·B / 4`. -/
theorem disc_bound_of_partial_factorisation (q t D f : Int) (P C B : Nat) (os : List Nat)
    (hcop : Nat.Coprime P C) (hC : 1 < C) (hnsq : ∀ r, r * r ≠ C)
    (hsmall : ∀ d, 1 < d → d < B → ¬ d ∣ C)
    (hos : os.Nodup) (hprime : ∀ p ∈ os, IsPrimeNat p)
    (hodd : ∀ p ∈ os, ∃ e M, P = p ^ e * M ∧ ¬ p ∣ M ∧ e % 2 = 1)
    (hN : 4 * q - t ^ 2 = ((P * C : Nat) : Int)) (hDf : t ^ 2 - 4 * q = D * f ^ 2) :
    os.prod * B ≤ D.natAbs ∧
      (IsDisc D → ((os.prod * B : Nat) : Int) ≤ 4 * minNonscalarDegree D) := by
  have hPC : P * C = D.natAbs * (f.natAbs * f.natAbs) := by
    have : ((P * C : Nat) : Int) = -(D * f ^ 2) := by omega
    have h2 := congrArg Int.natAbs this
    rw [Int.natAbs_natCast, Int.natAbs_neg, Int.natAbs_mul, Int.natAbs_pow, Nat.pow_two] at h2
    exact h2
  have hb := prod_mul_bound_le_of_eq_mul_sq P C B os hcop hC hnsq hsmall hos hprime hodd
    D.natAbs f.natAbs hPC
  refine ⟨hb, fun hD => ?_⟩
  have := natAbs_le_four_mul_minNonscalarDegree hD
  have hb' : ((os.prod * B : Nat) : Int) ≤ (D.natAbs : Int) := Int.ofNat_le.mpr hb
  omega

/-- The non-square test used on a certificate: if `r² < C < (r+1)²` then `C` is
not a perfect square. -/
theorem not_square_of_between {C r : Nat} (h1 : r * r < C) (h2 : C < (r + 1) * (r + 1)) :
    ∀ x, x * x ≠ C := by
  intro x hx
  by_cases hxr : x ≤ r
  · have : x * x ≤ r * r := Nat.mul_le_mul hxr hxr
    omega
  · have : (r + 1) * (r + 1) ≤ x * x := Nat.mul_le_mul (by omega) (by omega)
    omega

end CryptoResearch.Endosweep.Discriminant

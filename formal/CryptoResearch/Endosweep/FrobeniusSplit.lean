/-
Why `q = 4, t = -3` never gives a prime `n` (at the README's sizes): the
Lucas-sequence split through the F_2-Koblitz curves.

Source:  research/endosweep_frob_blinding_20261008/README.md (Item 9, Finding 4,
         and the appended "Lean verification" section); sequences from
         harness/endosweep/frobenius.py (`lucas_V`, `instance`,
         `q4_koblitz_split`).
Targets: formal/targets/endosweep-frob-*.yaml

frobenius.py: `V_0 = 2, V_1 = t, V_j = t V_{j-1} - q V_{j-2}`,
`#E(F_{q^m}) = q^m + 1 - V_m`, `n = #E(F_{q^m}) / #E(F_q)`. `q4_koblitz_split`
asserts, for odd `m`, `n4 = (4^m + 1 - V_m(4, -3)) // 8` equals
`n_a · n_b` with `n_a = (2^m + 1 - V_m(2, 1)) // 2`,
`n_b = (2^m + 1 - V_m(2, -1)) // 4` and `n_a, n_b > 1`; the README: "q = 4 with
t = −3 can never have prime n ... n = [#E(F_{2^m})/#E(F_2)]·[#E'(F_{2^m})/#E'(F_2)]
... checked for all 28 primes m in 67–199".

WHAT IS PROVED (core Lean, all `m`, not only the 28 checked):
* `cassini`: `V_{m+1}² - t V_m V_{m+1} + q V_m² = (4q - t²) q^m`.
* `V_double`: `V_{2m} = V_m² - 2q^m` (and `V_{2m+1} = V_m V_{m+1} - t q^m`).
* `order_double` (the Lucas identity):
  `#E(F_{q^{2m}}) = #E(F_{q^m}) · (q^m + 1 + V_m)`.
* `V_frobenius_square`: `V_k(t² - 2q, q²) = V_{2k}(t, q)`: the `q²`-Frobenius
  `φ²` has trace `V_2 = t² - 2q`. For `q = 2`: an F_2 curve of trace `t₂` has F_4
  trace `t₂² - 4` (`F4_trace`), which is `-3` iff `t₂ = ±1`
  (`F4_trace_eq_neg_three_iff`), and `#E(F_{4^m}) = #E(F_{2^{2m}})`.
* `V_neg_odd`: for odd `m`, `V_m(-t) = -V_m(t)`, so the quadratic twist over
  `F_{2^m}` has order `2^m + 1 + V_m`.
* `order_dvd`: `#E(F_q) ∣ #E(F_{q^k})` for all `k` (so `n` is an integer).
* `hasse`: if `t² < 4q` then `V_k² ≤ 4 q^k`.
* `q4_split` (the claim, precisely): for EVERY odd `m ≥ 5`,
  `n4 = n_a · n_b` with `n_a > 1` and `n_b > 1` (and the three `//` are exact),
  so `n4` is not prime (`q4_not_prime`).
* `q4_small_m`: the bound `m ≥ 5` is needed: `m = 3` gives `n4 = 7` with
  `n_b = 1`, and `m = 2` gives `n4 = 2`; both are primes. These lie far
  outside the README's range (`m` prime in 67–201), so its finding stands for
  every `m` it considers, but "never" is literally false for `m ∈ {2, 3}`.

WHAT IS NOT PROVED. That these integers are the group orders of actual curves
(the Frobenius characteristic polynomial / Weil-conjecture facts
`#E(F_{q^m}) = q^m + 1 - V_m` and Hasse's theorem `t² ≤ 4q` are the standard
inputs the harness also uses; here `hasse` is the purely arithmetic consequence
for the sequences), that the `t = -3` class over F_4 consists of the F_2-Koblitz
curves (the README's identification), and anything about other `(q, t)`:
BPSW probable primes, costs, digit statistics.
-/

namespace CryptoResearch.Endosweep.FrobeniusSplit

/-- frobenius.py `lucas_V(q, t, m)`. -/
def V (t q : Int) : Nat → Int
  | 0 => 2
  | 1 => t
  | k + 2 => t * V t q (k + 1) - q * V t q k

/-- `#E(F_{q^m}) = q^m + 1 - V_m`. -/
def order (q t : Int) (m : Nat) : Int := q ^ m + 1 - V t q m

theorem V_succ_succ (t q : Int) (k : Nat) : V t q (k + 2) = t * V t q (k + 1) - q * V t q k := rfl

/-- Cassini-type identity for the norm form. -/
theorem cassini (t q : Int) : ∀ m : Nat,
    V t q (m + 1) ^ 2 - t * V t q m * V t q (m + 1) + q * V t q m ^ 2 = (4 * q - t ^ 2) * q ^ m
  | 0 => by simp [V]; grind
  | m + 1 => by
    have ih := cassini t q m
    rw [V_succ_succ]
    have e : q ^ (m + 1) = q ^ m * q := Int.pow_succ q m
    rw [e]
    grind

/-- Doubling formulas: `V_{2m} = V_m² - 2q^m`, `V_{2m+1} = V_m V_{m+1} - t q^m`. -/
theorem V_double (t q : Int) : ∀ m : Nat,
    V t q (2 * m) = V t q m ^ 2 - 2 * q ^ m ∧
    V t q (2 * m + 1) = V t q m * V t q (m + 1) - t * q ^ m
  | 0 => by simp [V]; grind
  | m + 1 => by
    obtain ⟨h0, h1⟩ := V_double t q m
    have hc := cassini t q m
    have e2 : 2 * (m + 1) = 2 * m + 2 := by omega
    have e3 : 2 * (m + 1) + 1 = (2 * m + 1) + 2 := by omega
    have eq : q ^ (m + 1) = q ^ m * q := Int.pow_succ q m
    have hA : V t q (2 * m + 2) = V t q (m + 1) ^ 2 - 2 * q ^ (m + 1) := by
      rw [V_succ_succ, h1, h0, eq]; grind
    refine ⟨by rw [e2]; exact hA, ?_⟩
    rw [e3, V_succ_succ, hA, h1, eq, V_succ_succ t q m]
    grind

/-- **The Lucas identity** `#E(F_{q^{2m}}) = #E(F_{q^m}) · (q^m + 1 + V_m)`. -/
theorem order_double (q t : Int) (m : Nat) :
    order q t (2 * m) = order q t m * (q ^ m + 1 + V t q m) := by
  have h := (V_double t q m).1
  have e : q ^ (2 * m) = q ^ m * q ^ m := by rw [Nat.two_mul, Int.pow_add]
  simp only [order]; rw [h, e]; grind

/-- `V_{n+4} = (t² - 2q) V_{n+2} - q² V_n`. -/
theorem V_shift_two (t q : Int) (n : Nat) :
    V t q (n + 4) = (t ^ 2 - 2 * q) * V t q (n + 2) - q ^ 2 * V t q n := by
  have e1 : V t q (n + 4) = t * V t q (n + 3) - q * V t q (n + 2) := V_succ_succ t q (n + 2)
  have e2 : V t q (n + 3) = t * V t q (n + 2) - q * V t q (n + 1) := V_succ_succ t q (n + 1)
  have e3 : V t q (n + 2) = t * V t q (n + 1) - q * V t q n := V_succ_succ t q n
  rw [e1, e2]; grind

/-- The trace of the `q²`-Frobenius: `V_2 = t² - 2q`. -/
theorem V_two (t q : Int) : V t q 2 = t ^ 2 - 2 * q := by simp [V]; grind

/-- `V_k(t² - 2q, q²) = V_{2k}(t, q)`. -/
theorem V_frobenius_square (t q : Int) : ∀ k : Nat,
    V (t ^ 2 - 2 * q) (q ^ 2) k = V t q (2 * k) ∧
    V (t ^ 2 - 2 * q) (q ^ 2) (k + 1) = V t q (2 * k + 2)
  | 0 => by
    refine ⟨rfl, ?_⟩
    show t ^ 2 - 2 * q = V t q 2
    rw [V_two]
  | k + 1 => by
    obtain ⟨h0, h1⟩ := V_frobenius_square t q k
    refine ⟨by rw [h1, show 2 * (k + 1) = 2 * k + 2 by omega], ?_⟩
    rw [V_succ_succ, h1, h0]
    have e : 2 * (k + 1) + 2 = 2 * k + 4 := by omega
    rw [e, V_shift_two]

/-- Over F_2 with trace `t₂`, the F_4 trace is `t₂² - 4`. -/
theorem F4_trace (t2 : Int) : V t2 2 2 = t2 ^ 2 - 4 := by rw [V_two]; grind

theorem F4_trace_eq_neg_three_iff (t2 : Int) : t2 ^ 2 - 4 = -3 ↔ t2 = 1 ∨ t2 = -1 := by
  constructor
  · intro h
    have h1 : (t2 - 1) * (t2 + 1) = 0 := by grind
    rcases Int.mul_eq_zero.mp h1 with h | h
    · left; omega
    · right; omega
  · rintro (h | h) <;> subst h <;> decide

/-- `#E(F_{4^m})` for the F_4 trace `t₂² - 4` is `#E(F_{2^{2m}})`. -/
theorem order_F4_eq (t2 : Int) (m : Nat) : order 4 (t2 ^ 2 - 4) m = order 2 t2 (2 * m) := by
  have h := (V_frobenius_square t2 2 m).1
  have e1 : t2 ^ 2 - 2 * 2 = t2 ^ 2 - 4 := by grind
  have e2 : (2 : Int) ^ 2 = 4 := by decide
  rw [e1, e2] at h
  simp only [order]
  rw [h, Int.pow_mul, e2]

/-- `V_m(-t) = (-1)^m V_m(t)`, in the form needed: even and odd indices. -/
theorem V_neg (t q : Int) : ∀ k : Nat,
    V (-t) q (2 * k) = V t q (2 * k) ∧ V (-t) q (2 * k + 1) = -V t q (2 * k + 1)
  | 0 => by simp [V]
  | k + 1 => by
    obtain ⟨h0, h1⟩ := V_neg t q k
    have e2 : 2 * (k + 1) = 2 * k + 2 := by omega
    have e3 : 2 * (k + 1) + 1 = 2 * k + 3 := by omega
    have hA : V (-t) q (2 * k + 2) = V t q (2 * k + 2) := by
      rw [V_succ_succ, V_succ_succ t q, h0, h1]; grind
    refine ⟨by rw [e2]; exact hA, ?_⟩
    rw [e3, V_succ_succ, V_succ_succ t q (2 * k + 1), hA, h1]; grind

theorem V_neg_odd (t q : Int) (m : Nat) (hm : m % 2 = 1) : V (-t) q m = -V t q m := by
  obtain ⟨k, rfl⟩ : ∃ k, m = 2 * k + 1 := ⟨m / 2, by omega⟩
  exact (V_neg t q k).2

/-- `#E(F_q) ∣ #E(F_{q^k})`: with `d = q + 1 - t`, `d ∣ V_k - 1 - q^k`. -/
theorem order_dvd (q t : Int) : ∀ k : Nat,
    (q + 1 - t) ∣ order q t k ∧ (q + 1 - t) ∣ order q t (k + 1)
  | 0 => by
    refine ⟨⟨0, by simp [order, V]⟩, ⟨1, by simp [order, V]; grind⟩⟩
  | k + 1 => by
    obtain ⟨⟨a, ha⟩, ⟨c, hc⟩⟩ := order_dvd q t k
    refine ⟨⟨c, hc⟩, ?_⟩
    -- order_{k+2} = (q+1)·order_{k+1} - q·order_k + d·V_{k+1}
    refine ⟨(q + 1) * c - q * a + V t q (k + 1), ?_⟩
    simp only [order] at ha hc ⊢
    rw [V_succ_succ]
    have e1 : q ^ (k + 2) = q ^ (k + 1) * q := Int.pow_succ q (k + 1)
    have e0 : q ^ (k + 1) = q ^ k * q := Int.pow_succ q k
    rw [e1]
    rw [e0] at hc ⊢
    grind

/-- **Hasse, for the sequence**: if `t² < 4q` then `V_k² ≤ 4 q^k`. -/
theorem hasse (t q : Int) (h : t ^ 2 < 4 * q) : ∀ k : Nat, V t q k ^ 2 ≤ 4 * q ^ k
  | 0 => by simp [V]
  | k + 1 => by
    have hc := cassini t q k
    have hq : 0 < q := by have := Int.sq_nonneg t; omega
    have hd : 0 < 4 * q - t ^ 2 := by omega
    -- 4q·F = (2q x - t y)² + (4q - t²) y² with F = (4q - t²) q^k
    have key : 4 * q * ((4 * q - t ^ 2) * q ^ k)
        = (2 * q * V t q k - t * V t q (k + 1)) ^ 2 + (4 * q - t ^ 2) * V t q (k + 1) ^ 2 := by
      rw [← hc]; grind
    have hs := Int.sq_nonneg (2 * q * V t q k - t * V t q (k + 1))
    have e : q ^ (k + 1) = q ^ k * q := Int.pow_succ q k
    rw [e]
    apply Classical.byContradiction
    intro hlt
    have hlt' : 4 * (q ^ k * q) < V t q (k + 1) ^ 2 := by omega
    have := Int.mul_lt_mul_of_pos_left hlt' hd
    grind

/-! ## The q = 4, t = -3 split -/

/-- frobenius.py's `n4`, `n_a`, `n_b`. -/
def n4 (m : Nat) : Int := order 4 (-3) m / 8
def na (m : Nat) : Int := order 2 1 m / 2
def nb (m : Nat) : Int := order 2 (-1) m / 4

theorem two_pow_ge (m : Nat) (hm : 5 ≤ m) : (32 : Int) ≤ 2 ^ m := by
  have h : (2 : Nat) ^ 5 ≤ 2 ^ m := Nat.pow_le_pow_right (by decide) hm
  have : ((2 : Nat) ^ m : Nat) = (2 : Int) ^ m := Int.natCast_pow 2 m
  omega

/-- The two Hasse-type bounds used for `m ≥ 5` (`Q = 2^m ≥ 32`, `v = V_m`). -/
theorem hasse_bounds (Q v : Int) (hQ : 32 ≤ Q) (hH : v ^ 2 ≤ 4 * Q) :
    v ≤ Q - 3 ∧ 7 - Q ≤ v := by
  have hup : v ≤ Q - 3 := by
    apply Classical.byContradiction; intro hc
    have hc' : Q - 3 < v := by omega
    have hsq : v ^ 2 = v * v := by grind
    have hb2 : (Q - 3) * (Q - 3) ≥ 4 * Q + 1 := by
      have : (Q - 3) * (Q - 3) = Q * Q - 6 * Q + 9 := by grind
      have : Q * Q ≥ 32 * Q := by
        have := Int.mul_le_mul_of_nonneg_right hQ (by omega : (0 : Int) ≤ Q); omega
      omega
    have : (Q - 3) * (Q - 3) < v * v := by
      have := Int.mul_lt_mul_of_pos_left hc' (by omega : (0 : Int) < Q - 3)
      have h2 : (Q - 3) * v ≤ v * v :=
        Int.mul_le_mul_of_nonneg_right (Int.le_of_lt hc') (by omega)
      omega
    omega
  have hlo : 7 - Q ≤ v := by
    apply Classical.byContradiction; intro hc
    have hc' : Q - 7 < -v := by omega
    have hsq : v ^ 2 = (-v) * (-v) := by grind
    have hb2 : (Q - 7) * (Q - 7) ≥ 4 * Q + 1 := by
      have : (Q - 7) * (Q - 7) = Q * Q - 14 * Q + 49 := by grind
      have : Q * Q ≥ 32 * Q := by
        have := Int.mul_le_mul_of_nonneg_right hQ (by omega : (0 : Int) ≤ Q); omega
      omega
    have : (Q - 7) * (Q - 7) < (-v) * (-v) := by
      have := Int.mul_lt_mul_of_pos_left hc' (by omega : (0 : Int) < Q - 7)
      have h2 : (Q - 7) * (-v) ≤ (-v) * (-v) :=
        Int.mul_le_mul_of_nonneg_right (Int.le_of_lt hc') (by omega)
      omega
    omega
  exact ⟨hup, hlo⟩

/-- **`q = 4, t = -3`: `n` splits.** For every odd `m ≥ 5`, the three divisions
of `q4_koblitz_split` are exact, `n4 = n_a · n_b`, and `n_a, n_b > 1`. -/
theorem q4_split (m : Nat) (hodd : m % 2 = 1) (hm : 5 ≤ m) :
    8 * n4 m = order 4 (-3) m ∧ 2 * na m = order 2 1 m ∧ 4 * nb m = order 2 (-1) m ∧
    n4 m = na m * nb m ∧ 1 < na m ∧ 1 < nb m := by
  -- divisibility
  obtain ⟨a, ha⟩ := (order_dvd 2 1 m).1
  obtain ⟨b, hb⟩ := (order_dvd 2 (-1) m).1
  have ha' : order 2 1 m = 2 * a := by rw [ha]; grind
  have hb' : order 2 (-1) m = 4 * b := by rw [hb]; grind
  -- the F_4 order is the F_{2^{2m}} order, which factors
  have h4 : order 4 (-3) m = order 2 1 m * order 2 (-1) m := by
    have e : (-3 : Int) = 1 ^ 2 - 4 := by decide
    rw [e, order_F4_eq, order_double]
    simp only [order]
    rw [V_neg_odd 1 2 m hodd]; grind
  have hna : na m = a := by simp only [na]; rw [ha']; omega
  have hnb : nb m = b := by simp only [nb]; rw [hb']; omega
  have hn4 : n4 m = a * b := by
    simp only [n4]; rw [h4, ha', hb']
    have : 2 * a * (4 * b) = 8 * (a * b) := by grind
    rw [this]; omega
  -- Hasse bounds
  have hH := hasse 1 2 (by decide) m
  have hQ := two_pow_ge m hm
  have hVneg : V (-1) 2 m = -V 1 2 m := V_neg_odd 1 2 m hodd
  have hoa : order 2 1 m = 2 ^ m + 1 - V 1 2 m := rfl
  have hob : order 2 (-1) m = 2 ^ m + 1 + V 1 2 m := by
    simp only [order]; rw [hVneg]; grind
  obtain ⟨hup, hlo⟩ := hasse_bounds (2 ^ m) (V 1 2 m) hQ hH
  refine ⟨?_, ?_, ?_, ?_, ?_, ?_⟩
  · rw [hn4, h4, ha', hb']; grind
  · rw [hna, ha']
  · rw [hnb, hb']
  · rw [hn4, hna, hnb]
  · rw [hna]; rw [hoa] at ha'
    generalize (2 : Int) ^ m = Q at *; generalize V 1 2 m = v at *; omega
  · rw [hnb]; rw [hob] at hb'
    generalize (2 : Int) ^ m = Q at *; generalize V 1 2 m = v at *; omega

/-- Primality in the elementary sense: `n > 1` and its only positive divisors
are `1` and `n`. -/
def IsPrime (n : Int) : Prop := 1 < n ∧ ∀ d : Int, 0 < d → d ∣ n → d = 1 ∨ d = n

/-- **So `n4` is never prime for odd `m ≥ 5`.** -/
theorem q4_not_prime (m : Nat) (hodd : m % 2 = 1) (hm : 5 ≤ m) : ¬ IsPrime (n4 m) := by
  obtain ⟨-, -, -, h, ha, hb⟩ := q4_split m hodd hm
  rintro ⟨-, hp⟩
  rcases hp (na m) (by omega) ⟨nb m, h⟩ with h1 | h1
  · omega
  · -- na = na * nb with nb > 1 and na > 1 is impossible
    rw [h] at h1
    have : na m * nb m ≥ na m * 2 := Int.mul_le_mul_of_nonneg_left (by omega) (by omega)
    omega

/-- The bound `m ≥ 5` cannot be dropped: at `m = 3`, `n4 = 7` (with `n_b = 1`)
and at `m = 2`, `n4 = 2`; both prime. -/
theorem q4_small_m :
    n4 3 = 7 ∧ na 3 = 7 ∧ nb 3 = 1 ∧ n4 2 = 2 ∧ IsPrime 7 ∧ IsPrime 2 := by
  refine ⟨by decide, by decide, by decide, by decide, ?_, ?_⟩
  · refine ⟨by decide, fun d hd hdvd => ?_⟩
    have hle : d ≤ 7 := Int.le_of_dvd (by decide) hdvd
    have : d = 1 ∨ d = 2 ∨ d = 3 ∨ d = 4 ∨ d = 5 ∨ d = 6 ∨ d = 7 := by omega
    rcases this with h | h | h | h | h | h | h <;> subst h <;> simp_all <;> contradiction
  · refine ⟨by decide, fun d hd hdvd => ?_⟩
    have hle : d ≤ 2 := Int.le_of_dvd (by decide) hdvd
    omega

end CryptoResearch.Endosweep.FrobeniusSplit

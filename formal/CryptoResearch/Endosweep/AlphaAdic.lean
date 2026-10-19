/-
α-adic expansions on chain curves: the termination argument of
`harness/endosweep/alphaadic.py`.

Source: research/endosweep_msm_20261008/README.md, Item 2 ("Termination is
proved, or refuted, per digit rule") and its appended subsection
"Lean verification: α-adic".
Targets: formal/targets/endosweep-alphaadic-norm-decrease.yaml
         formal/targets/endosweep-alphaadic-termination-from-disk.yaml
         formal/targets/endosweep-alphaadic-int-rule-4plusw.yaml
         formal/targets/endosweep-alphaadic-int-rule-4plusw-cp6.yaml
         formal/targets/endosweep-alphaadic-int-rule-1plus4w-cycle.yaml

The README: "`|T(z)| ≤ (|z| + R)/|α|` with `R` the largest digit, so every
orbit enters and stays in the disk `|z| ≤ R/(|α| − 1)`; every element of that
disk is iterated to 0. 84 of the 94 rules terminate. The 10 `int` rules for
elements with `|b| ≥ 2` … do not: a cycle is found in the disk."
Here `T(z) = (z − d(z))/α` and `|z| = √N(z)`.

Everything is stated with INTEGER norms; no square root appears. With
`A = N(z)`, `R = max N(d)` (the square of the README's `R`) and `N(α)`:

* `triangle_sq` -- `(N(z − d) − N(z) − N(d))² ≤ 4·N(z)·N(d)`: the squared form
  of `|z − d| ≤ |z| + |d|` (Cauchy–Schwarz for the norm form; it is the ring
  identity `4N(z)N(d) − B² = (4m − τ²)·det(z, d)²`). Since
  `N(α)·N(T z) = N(z − d)`, this is the README's step bound.
* `norm_decrease` -- if `Outside N(α) R A`, i.e. `A + R < N(α)·A` and
  `4AR < (N(α)·A − A − R)²` (which is `√A·(√N(α) − 1) > √R` squared out,
  i.e. `|z| > R/(|α| − 1)` in the README's notation), then
  `N(T z) < N(z)`.
* `terminates_of_disk` -- if every `z` OUTSIDE that condition (the closed
  disk) reaches `0` under `T`, then every `z ∈ O` does, and
  `expansion_of_iterate`: when `T^[k] z = 0`, `z = Σ dᵢ αⁱ` with the digits
  produced along the orbit (Horner form).
* `cryptoProB_int_rule_terminates`, `cp6_782_int_rule_terminates` -- the
  balanced-integer digit rule (`int_rule`) for `α = 4 + ω` on CryptoPro-B
  (`D = −619`, `N(α) = 175`, digits `|d| ≤ 87`) and on CP6-782 (`D = −339`,
  `N(α) = 105`, `|d| ≤ 52`) terminates on EVERY `z ∈ O`, and the expansion
  reconstructs `z`. Here the disk is exhausted in Lean, not by the harness: it
  is `{N(z) ≤ 50}` (resp. `≤ 31`), whose elements are the integers `|x| ≤ 7`
  (resp. `≤ 5`), each its own digit (15 resp. 11 elements, as in
  `alphaadic.json`).
* `cp6_782_int_rule_1plus4w_cycle` -- the non-termination side for one of
  the 10 refuted rules: for `α = 1 + 4ω` on CP6-782 (`N(α) = 1365`) the
  balanced-integer rule fixes `z = −2 + 2ω` (digit 680, `α·z = z − 680`), so
  its expansion never terminates: the `cycle_example` `[-2, 2]` of
  `alphaadic.json`.

NOT PROVED HERE: the exhaustion of the disk for the other 82 terminating rules
(computed by `termination_certificate` in the harness, floating-point radius
included) and the cycles of the other 9 non-terminating ones; that the
`voronoi`/`naf` digit tables are minimal-norm residue systems; that the
digit and quotient defined here coincide with `alphaadic.py`'s (the digit is
the balanced integer `≡ z (mod α)`, which is what `int_rule` tabulates, and an
exact quotient is unique, but the Python is not formalized); the "stays in the
disk" half of the README sentence (not needed for termination); any digit
statistic, length or cost (measured/modelled).
-/
import Mathlib.Tactic.Ring

namespace CryptoResearch.Endosweep.AlphaAdic

/-- An element `x + y·ω` of `O = Z[ω]`, `ω² = τω − m`. -/
abbrev O := Int × Int

/-- `N(x + yω) = x² + xyτ + y²m` (`QO.norm`). -/
def nrm (τ m : Int) (z : O) : Int := z.1 * z.1 + z.1 * z.2 * τ + z.2 * z.2 * m

/-- Multiplication in `O` (`QO.multiply`). -/
def mul (τ m : Int) (x y : O) : O :=
  (x.1 * y.1 - x.2 * y.2 * m, x.1 * y.2 + y.1 * x.2 + x.2 * y.2 * τ)

def add (x y : O) : O := (x.1 + y.1, x.2 + y.2)
def sub (x y : O) : O := (x.1 - y.1, x.2 - y.2)

/-! ## The norm form -/

theorem nrm_mul (τ m : Int) (x y : O) : nrm τ m (mul τ m x y) = nrm τ m x * nrm τ m y := by
  simp only [nrm, mul]; ring

theorem sq_nonneg' (x : Int) : 0 ≤ x * x := by
  rcases Int.le_total 0 x with h | h
  · exact Int.mul_nonneg h h
  · have := Int.mul_nonneg (Int.neg_nonneg_of_nonpos h) (Int.neg_nonneg_of_nonpos h)
    rwa [Int.neg_mul_neg] at this

theorem four_nrm (τ m : Int) (z : O) :
    4 * nrm τ m z = (2 * z.1 + τ * z.2) * (2 * z.1 + τ * z.2) + (4 * m - τ * τ) * (z.2 * z.2) := by
  simp only [nrm]; ring

theorem nrm_nonneg {τ m : Int} (hdisc : τ * τ < 4 * m) (z : O) : 0 ≤ nrm τ m z := by
  have h1 := four_nrm τ m z
  have h2 := sq_nonneg' (2 * z.1 + τ * z.2)
  have h3 : 0 ≤ (4 * m - τ * τ) * (z.2 * z.2) :=
    Int.mul_nonneg (by omega) (sq_nonneg' z.2)
  omega

/-- **Squared triangle inequality** (Cauchy–Schwarz for the norm form):
`(N(z − d) − N(z) − N(d))² ≤ 4·N(z)·N(d)`, i.e. `|z − d| ≤ |z| + |d|`. -/
theorem triangle_sq {τ m : Int} (hdisc : τ * τ < 4 * m) (z d : O) :
    (nrm τ m (sub z d) - nrm τ m z - nrm τ m d) * (nrm τ m (sub z d) - nrm τ m z - nrm τ m d)
      ≤ 4 * nrm τ m z * nrm τ m d := by
  have key : 4 * nrm τ m z * nrm τ m d
      - (nrm τ m (sub z d) - nrm τ m z - nrm τ m d) * (nrm τ m (sub z d) - nrm τ m z - nrm τ m d)
      = (4 * m - τ * τ) * ((z.1 * d.2 - z.2 * d.1) * (z.1 * d.2 - z.2 * d.1)) := by
    simp only [nrm, sub]; ring
  have : 0 ≤ (4 * m - τ * τ) * ((z.1 * d.2 - z.2 * d.1) * (z.1 * d.2 - z.2 * d.1)) :=
    Int.mul_nonneg (by omega) (sq_nonneg' _)
  omega

/-- The region outside the absorbing disk, without square roots:
`A + R < Nα·A` and `4·A·R < (Nα·A − A − R)²`; for `A, R ≥ 0` this is
`√A·(√Nα − 1) > √R`. -/
def Outside (Nα R A : Int) : Prop :=
  A + R < Nα * A ∧ 4 * A * R < (Nα * A - A - R) * (Nα * A - A - R)

/-- **Strict decrease outside the disk.** If `α·q = z − d` with `N(d) ≤ R` and
`N(z)` is outside the disk, then `N(q) < N(z)`. -/
theorem norm_decrease {τ m : Int} (hdisc : τ * τ < 4 * m) (α z d q : O) (R : Int)
    (hq : mul τ m α q = sub z d) (hd : nrm τ m d ≤ R)
    (hout : Outside (nrm τ m α) R (nrm τ m z)) : nrm τ m q < nrm τ m z := by
  obtain ⟨h1, h2⟩ := hout
  have hC : nrm τ m (sub z d) = nrm τ m α * nrm τ m q := by rw [← hq, nrm_mul]
  have hA := nrm_nonneg hdisc z
  have hα := nrm_nonneg hdisc α
  have hD := nrm_nonneg hdisc d
  have hT := triangle_sq hdisc z d
  rw [hC] at hT
  refine Int.lt_of_not_ge fun hge => ?_
  -- N(α)·N(q) ≥ N(α)·N(z)
  have hmono : nrm τ m α * nrm τ m z ≤ nrm τ m α * nrm τ m q :=
    Int.mul_le_mul_of_nonneg_left hge hα
  -- 0 < v ≤ w where w is the cross term
  have hv : 0 < nrm τ m α * nrm τ m z - nrm τ m z - R := by omega
  have hvw : nrm τ m α * nrm τ m z - nrm τ m z - R
      ≤ nrm τ m α * nrm τ m q - nrm τ m z - nrm τ m d := by omega
  have hsq := Int.mul_le_mul hvw hvw (Int.le_of_lt hv) (by omega)
  have hR : 4 * nrm τ m z * nrm τ m d ≤ 4 * nrm τ m z * R :=
    Int.mul_le_mul_of_nonneg_left hd (by omega)
  omega

/-! ## Termination from a finite disk check, and the expansion -/

/-- **Termination from the disk.** Let `T` be a digit step: `α·T(z) = z − dig(z)`
with `N(dig z) ≤ R`. If every `z` not `Outside` (the closed disk) reaches `0`,
then every `z ∈ O` reaches `0`. -/
theorem terminates_of_disk {τ m : Int} (hdisc : τ * τ < 4 * m) (α : O) (R : Int)
    (dig T : O → O) (hstep : ∀ z, mul τ m α (T z) = sub z (dig z))
    (hdig : ∀ z, nrm τ m (dig z) ≤ R)
    (hdisk : ∀ z, ¬ Outside (nrm τ m α) R (nrm τ m z) → ∃ k : Nat, T^[k] z = (0, 0)) :
    ∀ z, ∃ k : Nat, T^[k] z = (0, 0) := by
  have main : ∀ (n : Nat) (z : O), (nrm τ m z).toNat ≤ n → ∃ k : Nat, T^[k] z = (0, 0) := by
    intro n
    induction n with
    | zero =>
      intro z hz
      by_cases ho : Outside (nrm τ m α) R (nrm τ m z)
      · have := norm_decrease hdisc α z (dig z) (T z) R (hstep z) (hdig z) ho
        have := nrm_nonneg hdisc (T z)
        omega
      · exact hdisk z ho
    | succ n ih =>
      intro z hz
      by_cases ho : Outside (nrm τ m α) R (nrm τ m z)
      · have hlt := norm_decrease hdisc α z (dig z) (T z) R (hstep z) (hdig z) ho
        have := nrm_nonneg hdisc (T z)
        obtain ⟨k, hk⟩ := ih (T z) (by omega)
        exact ⟨k + 1, by rw [Function.iterate_succ_apply]; exact hk⟩
      · exact hdisk z ho
  exact fun z => main _ z le_rfl

/-- The digits produced along the first `k` steps of the orbit of `z`. -/
def digits (dig T : O → O) : Nat → O → List O
  | 0, _ => []
  | k + 1, z => dig z :: digits dig T k (T z)

/-- Horner evaluation `d₀ + α(d₁ + α(d₂ + …))`. -/
def horner (τ m : Int) (α : O) : List O → O
  | [] => (0, 0)
  | d :: ds => add d (mul τ m α (horner τ m α ds))

/-- **The expansion reconstructs `z`.** If `T^[k] z = 0` then
`z = Σ_{i<k} dᵢ αⁱ` for the digits `dᵢ = dig(T^[i] z)`. -/
theorem expansion_of_iterate {τ m : Int} (α : O) (dig T : O → O)
    (hstep : ∀ z, mul τ m α (T z) = sub z (dig z)) :
    ∀ (k : Nat) (z : O), T^[k] z = (0, 0) → z = horner τ m α (digits dig T k z) := by
  intro k
  induction k with
  | zero => intro z hz; simpa [digits, horner] using hz
  | succ k ih =>
    intro z hz
    rw [Function.iterate_succ_apply] at hz
    have h := ih (T z) hz
    simp only [digits, horner]
    rw [← h, hstep z]
    simp only [add, sub]; ext <;> simp

/-! ## The balanced-integer digit rule for `α = a + ω` -/

/-- Balanced representative: `r ∈ [0, N)` ↦ `r` if `r ≤ N/2`, else `r − N`
(`int_rule`: `d = r if r <= N // 2 else r - N`). -/
def bal (N r : Int) : Int := if r ≤ N / 2 then r else r - N

/-- `N(a + ω)`. -/
def normA (τ m a : Int) : Int := a * a + a * τ + m

/-- The `int` digit of `z = x + yω` for `α = a + ω`: the balanced integer
congruent to `z` modulo `α` (`ω ≡ −a (mod α)`, so `z ≡ x − a·y`). -/
def digit1 (τ m a : Int) (z : O) : O := (bal (normA τ m a) ((z.1 - a * z.2) % normA τ m a), 0)

/-- The exact quotient `(z − d)/α` for `α = a + ω`. -/
def step1 (τ m a : Int) (z : O) : O :=
  let w := sub z (digit1 τ m a z)
  let t := (w.1 - a * w.2) / normA τ m a
  (w.2 + t * (a + τ), -t)

theorem step1_spec (τ m a : Int) (hN : normA τ m a ≠ 0) (z : O) :
    mul τ m (a, 1) (step1 τ m a z) = sub z (digit1 τ m a z) := by
  -- N divides (x − a y) − d
  have hdiv : normA τ m a ∣ (sub z (digit1 τ m a z)).1 - a * (sub z (digit1 τ m a z)).2 := by
    simp only [sub, digit1, Int.sub_zero, bal]
    have hr := Int.emod_add_ediv_mul (z.1 - a * z.2) (normA τ m a)
    generalize (z.1 - a * z.2) % normA τ m a = r at hr ⊢
    generalize (z.1 - a * z.2) / normA τ m a = q at hr ⊢
    generalize normA τ m a = N at hr ⊢
    split
    · exact ⟨q, by rw [Int.mul_comm N q]; omega⟩
    · exact ⟨q + 1, by rw [Int.mul_comm N (q + 1), Int.add_mul, Int.one_mul]; omega⟩
  obtain ⟨t, ht⟩ := hdiv
  have htq : ((sub z (digit1 τ m a z)).1 - a * (sub z (digit1 τ m a z)).2) / normA τ m a = t := by
    rw [ht, Int.mul_ediv_cancel_left _ hN]
  simp only [step1, htq]
  generalize hw : sub z (digit1 τ m a z) = w at ht ⊢
  simp only [mul, normA] at ht ⊢
  ext
  · simp only; rw [show w.1 = a * w.2 + (a * a + a * τ + m) * t by omega]; ring
  · simp only; ring

/-! ### `α = 4 + ω` on GOST CryptoPro-B, `D = −619` (`τ = 1`, `m = 155`, `N(α) = 175`) -/

theorem sq_le_of_abs_le {d c : Int} (h1 : -c ≤ d) (h2 : d ≤ c) : d * d ≤ c * c := by
  have := Int.mul_nonneg (show 0 ≤ c - d by omega) (show 0 ≤ c + d by omega)
  have e : (c - d) * (c + d) = c * c - d * d := by ring
  omega

theorem le_of_sq_le {x c : Int} (hc : 0 ≤ c) (h : x * x < (c + 1) * (c + 1)) : -c ≤ x ∧ x ≤ c := by
  constructor
  · refine Int.not_lt.1 fun hx => ?_
    have := Int.mul_le_mul (show c + 1 ≤ -x by omega) (show c + 1 ≤ -x by omega)
      (by omega) (by omega)
    rw [Int.neg_mul_neg] at this; omega
  · refine Int.not_lt.1 fun hx => ?_
    have := Int.mul_le_mul (show c + 1 ≤ x by omega) (show c + 1 ≤ x by omega)
      (by omega) (by omega)
    omega

theorem y_eq_zero_of_small_norm {m B : Int} {z : O} (hm : 1 ≤ m) (hB : 4 * B < 4 * m - 1)
    (h : nrm 1 m z ≤ B) : z.2 = 0 := by
  have h4 := four_nrm 1 m z
  have hs := sq_nonneg' (2 * z.1 + 1 * z.2)
  refine Classical.byContradiction fun hy => ?_
  have hy1 : 1 ≤ z.2 * z.2 := by
    rcases Int.lt_or_gt_of_ne hy with hy | hy
    · have := Int.mul_le_mul (show 1 ≤ -z.2 by omega) (show 1 ≤ -z.2 by omega) (by omega) (by omega)
      rw [Int.neg_mul_neg] at this; omega
    · have := Int.mul_le_mul (show 1 ≤ z.2 by omega) (show 1 ≤ z.2 by omega) (by omega) (by omega)
      omega
  have := Int.mul_le_mul_of_nonneg_left hy1 (show 0 ≤ 4 * m - 1 * 1 by omega)
  omega

/-- The disk for CryptoPro-B: outside fails only when `N(z) ≤ 50`. -/
theorem cpb_inside {A : Int} (h : ¬ Outside 175 7569 A) : A ≤ 50 := by
  refine Int.not_lt.1 fun hA51 => h ⟨by omega, ?_⟩
  have hu : 1305 ≤ 175 * A - A - 7569 := by omega
  have := Int.mul_le_mul_of_nonneg_right hu (show 0 ≤ 175 * A - A - 7569 by omega)
  omega

/-- **The `int` rule for `4 + ω` on CryptoPro-B terminates on every `z ∈ O`,
and the expansion reconstructs `z`.** -/
theorem cryptoProB_int_rule_terminates :
    ∀ z : O, ∃ k : Nat, (step1 1 155 4)^[k] z = (0, 0) ∧
      z = horner 1 155 (4, 1) (digits (digit1 1 155 4) (step1 1 155 4) k z) := by
  have hN : normA 1 155 4 = 175 := by decide
  have hstep := step1_spec 1 155 4 (by rw [hN]; decide)
  have hdig : ∀ z, nrm 1 155 (digit1 1 155 4 z) ≤ 7569 := by
    intro z
    simp only [nrm, digit1, hN, bal]
    have h0 := Int.emod_nonneg (z.1 - 4 * z.2) (show (175 : Int) ≠ 0 by decide)
    have h1 := Int.emod_lt_of_pos (z.1 - 4 * z.2) (show (0 : Int) < 175 by decide)
    split
    · have := sq_le_of_abs_le (c := 87) (d := (z.1 - 4 * z.2) % 175) (by omega) (by omega)
      simp only [Int.mul_zero]; omega
    · have := sq_le_of_abs_le (c := 87) (d := (z.1 - 4 * z.2) % 175 - 175) (by omega) (by omega)
      simp only [Int.mul_zero]; omega
  have hα : nrm 1 155 ((4 : Int), (1 : Int)) = 175 := by decide
  have hdisk : ∀ z, ¬ Outside (nrm 1 155 (4, 1)) 7569 (nrm 1 155 z) →
      ∃ k : Nat, (step1 1 155 4)^[k] z = (0, 0) := by
    intro z hz
    rw [hα] at hz
    have hA := cpb_inside hz
    have hy := y_eq_zero_of_small_norm (m := 155) (B := 50) (by decide) (by decide) hA
    obtain ⟨x, y⟩ := z
    simp only at hy; subst hy
    have hx : x * x < (7 + 1) * (7 + 1) := by simp only [nrm] at hA; omega
    have hx' := le_of_sq_le (by decide) hx
    refine ⟨1, ?_⟩
    have hd : digit1 1 155 4 (x, 0) = (x, 0) := by
      simp only [digit1, hN, bal]
      split <;> ext <;> simp only <;> omega
    simp only [Function.iterate_one, step1, hd, sub, hN]
    simp
  intro z
  obtain ⟨k, hk⟩ := terminates_of_disk (by decide) (4, 1) 7569 _ _ hstep hdig hdisk z
  exact ⟨k, hk, expansion_of_iterate _ _ _ hstep k z hk⟩

/-! ### `α = 4 + ω` on CP6-782 `G1`, `D = −339` (`τ = 1`, `m = 85`, `N(α) = 105`) -/

/-- The disk for CP6-782: outside fails only when `N(z) ≤ 31`. -/
theorem cp6_inside {A : Int} (h : ¬ Outside 105 2704 A) : A ≤ 31 := by
  refine Int.not_lt.1 fun hA32 => h ⟨by omega, ?_⟩
  have hu : 624 ≤ 105 * A - A - 2704 := by omega
  have := Int.mul_le_mul_of_nonneg_right hu (show 0 ≤ 105 * A - A - 2704 by omega)
  omega

/-- **The `int` rule for `4 + ω` on CP6-782 terminates on every `z ∈ O`, and
the expansion reconstructs `z`.** -/
theorem cp6_782_int_rule_terminates :
    ∀ z : O, ∃ k : Nat, (step1 1 85 4)^[k] z = (0, 0) ∧
      z = horner 1 85 (4, 1) (digits (digit1 1 85 4) (step1 1 85 4) k z) := by
  have hN : normA 1 85 4 = 105 := by decide
  have hstep := step1_spec 1 85 4 (by rw [hN]; decide)
  have hdig : ∀ z, nrm 1 85 (digit1 1 85 4 z) ≤ 2704 := by
    intro z
    simp only [nrm, digit1, hN, bal]
    have h0 := Int.emod_nonneg (z.1 - 4 * z.2) (show (105 : Int) ≠ 0 by decide)
    have h1 := Int.emod_lt_of_pos (z.1 - 4 * z.2) (show (0 : Int) < 105 by decide)
    split
    · have := sq_le_of_abs_le (c := 52) (d := (z.1 - 4 * z.2) % 105) (by omega) (by omega)
      simp only [Int.mul_zero]; omega
    · have := sq_le_of_abs_le (c := 52) (d := (z.1 - 4 * z.2) % 105 - 105) (by omega) (by omega)
      simp only [Int.mul_zero]; omega
  have hα : nrm 1 85 ((4 : Int), (1 : Int)) = 105 := by decide
  have hdisk : ∀ z, ¬ Outside (nrm 1 85 (4, 1)) 2704 (nrm 1 85 z) →
      ∃ k : Nat, (step1 1 85 4)^[k] z = (0, 0) := by
    intro z hz
    rw [hα] at hz
    have hA := cp6_inside hz
    have hy := y_eq_zero_of_small_norm (m := 85) (B := 31) (by decide) (by decide) hA
    obtain ⟨x, y⟩ := z
    simp only at hy; subst hy
    have hx : x * x < (5 + 1) * (5 + 1) := by simp only [nrm] at hA; omega
    have hx' := le_of_sq_le (by decide) hx
    refine ⟨1, ?_⟩
    have hd : digit1 1 85 4 (x, 0) = (x, 0) := by
      simp only [digit1, hN, bal]
      split <;> ext <;> simp only <;> omega
    simp only [Function.iterate_one, step1, hd, sub, hN]
    simp
  intro z
  obtain ⟨k, hk⟩ := terminates_of_disk (by decide) (4, 1) 2704 _ _ hstep hdig hdisk z
  exact ⟨k, hk, expansion_of_iterate _ _ _ hstep k z hk⟩

/-! ## A non-terminating rule: `α = 1 + 4ω` on CP6-782 -/

/-- The `int` digit for a general primitive `α = a + bω` of norm `N`, given
`μ` with `a + bμ ≡ 0 (mod N)` (so `ω ≡ μ (mod α)` and `z ≡ x + yμ`). -/
def digitInt (N μ : Int) (z : O) : O := (bal N ((z.1 + z.2 * μ) % N), 0)

/-- `(z − d)·ᾱ / N`, `ᾱ = (a + bτ) − bω`; equal to `(z − d)/α` when exact. -/
def stepInt (τ m : Int) (α : O) (N μ : Int) (z : O) : O :=
  let c := mul τ m (sub z (digitInt N μ z)) (α.1 + α.2 * τ, -α.2)
  (c.1 / N, c.2 / N)

/-- **`1 + 4ω` on CP6-782: the `int` rule has a fixed point `−2 + 2ω`.**
`N(1 + 4ω) = 1365`, `μ = 341` satisfies `1 + 4μ ≡ 0`, the digit of `−2 + 2ω`
is `680` (the balanced residue of `−2 + 2·341`), the quotient is exact
(`α·T(z) = z − 680`) and equals `z`; hence `T^[k] z = z ≠ 0` for every `k`:
the expansion of `−2 + 2ω` never terminates. -/
theorem cp6_782_int_rule_1plus4w_cycle :
    nrm 1 85 (1, 4) = 1365 ∧ (1 + 4 * 341) % 1365 = 0 ∧
    digitInt 1365 341 (-2, 2) = (680, 0) ∧
    mul 1 85 (1, 4) (stepInt 1 85 (1, 4) 1365 341 (-2, 2)) = sub (-2, 2) (digitInt 1365 341 (-2, 2)) ∧
    stepInt 1 85 (1, 4) 1365 341 (-2, 2) = (-2, 2) ∧
    ∀ k : Nat, (stepInt 1 85 (1, 4) 1365 341)^[k] (-2, 2) = (-2, 2) ∧ ((-2, 2) : O) ≠ (0, 0) := by
  have hfix : stepInt 1 85 (1, 4) 1365 341 (-2, 2) = (-2, 2) := by decide
  refine ⟨by decide, by decide, by decide, by decide, hfix, fun k => ⟨?_, by decide⟩⟩
  induction k with
  | zero => rfl
  | succ k ih => rw [Function.iterate_succ_apply, hfix, ih]

end CryptoResearch.Endosweep.AlphaAdic

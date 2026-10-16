/-
The closed-form identities behind "endomorphisms in Pippenger MSM".

Source:  research/endosweep_msm_20261008/README.md (Item 1: the hypothesis,
         Finding 1, the `C*` definition, and the appended "Lean verification"
         section); formulas from harness/endosweep/msm.py (`model_1d`:
         `W = bits // c + 1` windows, `(W - 1)·c` doublings, `W - 1` combine
         additions; `sweep_curve`: `glv_total = glv0 + N·ce`,
         `C* = (plain - glv0)/N`, `gain = 100·(plain - glv_total)/plain`).
Targets: formal/targets/endosweep-msm-*.yaml

WHAT IS PROVED (core Lean: `Nat`, `Rat`).
* `bit_conservation`: `(b/c)·N = ((b/2)/c)·(2N)` in `ℚ`: a GLV split
  (`N × b → 2N × b/2`) leaves the ceiling-free count of window-digit slots,
  hence of bucket accumulations, unchanged.
* `window_slots` (with msm.py's exact floors, plain coefficients of `2h` bits,
  GLV coefficients of `h` bits, window `c ≥ 1`): with `W(B) = B / c + 1`,
  `N·W(2h) ≤ 2N·W(h) ≤ N·W(2h) + N`, and `2·W(h) = W(2h)` exactly when
  `c ≤ 2·(h mod c)`; otherwise the split costs one extra window per point.
  `window_slots_examples`: `h = 128` gives equality at `c = 13` (20 = 20) and
  the extra window at `c = 16` (18 vs 17; "256 = 16·16 leaves plain a 17th
  window").
* `doublings_halved`: the split's window-combination doublings `(W(h) - 1)·c`
  are at most half of plain's `(W(2h) - 1)·c`.
* `glv_wins_iff` / `gain_pos_iff` (msm.py's break-even, exact): for `N > 0`,
  `glv0 + N·C_α < plain ↔ C_α < (plain - glv0)/N = C*`, and for `plain > 0`
  the gain `100·(plain - glv_total)/plain` is positive iff `C_α < C*`
  (`gain_zero_iff`: zero iff `C_α = C*`).
* `ideal_*` (a ceiling-free, saturated-bucket common-window model, `b/c`
  windows of `N·A` accumulation, `2^c·R` aggregation, `c` doublings at `D` and
  one combine addition at `C` each): the accumulation term is unchanged by the
  split, the aggregation term is halved, and the exact break-even is
  `C* = (b/(2c))·(2^c R + c D + C)/N`, which exceeds the aggregation-only
  saving `(b/(2c))·2^c R / N` by exactly `((b/2)·D + (b/(2c))·C)/N`: the halved
  window-combination work that the README says the hypothesis leaves out.

WHAT IS NOT PROVED. Every number in the README tables: the modelled `C*(N)`
values, the gains in %, the validation errors, and the optimal windows depend on
msm.py's occupancy expectations and window search and are measured/modelled,
not Lean claims. The hypothesis's approximation `C* ≈ b·A/(c(c+1))` is not
derived (the README itself finds it "mostly low"). Item 2 (α-adic) is not
formalised.
-/

namespace CryptoResearch.Endosweep.Pippenger

/-! ## Bit conservation -/

/-- `(b/c)·N = ((b/2)/c)·(2N)`: the GLV split conserves digit slots. -/
theorem bit_conservation (b c N : Rat) :
    (b / c) * N = ((b / 2) / c) * (2 * N) := by
  grind

/-- msm.py's window count `bits // c + 1`. -/
def windows (bits c : Nat) : Nat := bits / c + 1

/-- The key floor identity: `2h / c = 2·(h / c) + (2·(h mod c)) / c`, the last
term being `1` iff `c ≤ 2·(h mod c)`. -/
theorem two_mul_div (h c : Nat) (hc : 0 < c) :
    (2 * h) / c = 2 * (h / c) + (if c ≤ 2 * (h % c) then 1 else 0) := by
  have hdm := Nat.div_add_mod h c
  have hr : h % c < c := Nat.mod_lt h hc
  have e : 2 * h = 2 * (h % c) + c * (2 * (h / c)) := by
    have : c * (2 * (h / c)) = 2 * (c * (h / c)) := by
      rw [← Nat.mul_assoc, Nat.mul_comm c 2, Nat.mul_assoc]
    omega
  rw [e, Nat.add_mul_div_left _ _ hc]
  split
  · next hle =>
    have : 2 * (h % c) / c = 1 := by
      apply Nat.div_eq_of_lt_le <;> omega
    omega
  · next hlt =>
    have : 2 * (h % c) / c = 0 := Nat.div_eq_of_lt (by omega)
    omega

/-- **Window slots with msm.py's floors.** Plain: `N` points of `2h` bits; GLV:
`2N` points of `h` bits. -/
theorem window_slots (h c N : Nat) (hc : 0 < c) :
    N * windows (2 * h) c ≤ 2 * N * windows h c ∧
    2 * N * windows h c ≤ N * windows (2 * h) c + N ∧
    (2 * windows h c = windows (2 * h) c ↔ c ≤ 2 * (h % c)) := by
  have key := two_mul_div h c hc
  unfold windows
  have hw : 2 * N * (h / c + 1) = N * (2 * (h / c) + 2) := by
    rw [Nat.mul_comm 2 N, Nat.mul_assoc]; congr 1
  refine ⟨?_, ?_, ?_⟩
  · rw [hw]; apply Nat.mul_le_mul_left; split at key <;> omega
  · rw [hw]
    have : N * ((2 * h) / c + 1) + N = N * ((2 * h) / c + 2) := by
      rw [Nat.mul_add, Nat.mul_add]; omega
    rw [this]; apply Nat.mul_le_mul_left; split at key <;> omega
  · split at key <;> constructor <;> intro hh <;> omega

/-- The README's two cases at `h = 128`: `c = 13` (equality, 20 windows of
plain against 2 × 10) and `c = 16` (plain 17, the split 2 × 9 = 18). -/
theorem window_slots_examples :
    windows 256 13 = 20 ∧ 2 * windows 128 13 = 20 ∧
    windows 256 16 = 17 ∧ 2 * windows 128 16 = 18 := by
  decide

/-- The split's window-combination doublings are at most half of plain's. -/
theorem doublings_halved (h c : Nat) (hc : 0 < c) :
    2 * ((windows h c - 1) * c) ≤ (windows (2 * h) c - 1) * c := by
  have key := two_mul_div h c hc
  unfold windows
  rw [← Nat.mul_assoc]
  apply Nat.mul_le_mul_right
  split at key <;> omega

/-! ## msm.py's break-even, exact -/

/-- **GLV wins iff the image costs less than `C*`.** `plain` and `glv0` are the
totals of the plain and the image-free GLV MSM, `ce` the cost of one image;
msm.py sets `glv_total = glv0 + N·ce` and `C* = (plain - glv0)/N`. -/
theorem glv_wins_iff (plain glv0 ce N : Rat) (hN : 0 < N) :
    glv0 + N * ce < plain ↔ ce < (plain - glv0) / N := by
  rw [Rat.lt_div_iff' hN]
  constructor <;> intro h <;> grind

/-- The gain `100·(plain - glv_total)/plain` (msm.py's `glv_gain_pct`) is
positive iff `ce < C*`. -/
theorem gain_pos_iff (plain glv0 ce N : Rat) (hN : 0 < N) (hP : 0 < plain) :
    0 < 100 * (plain - (glv0 + N * ce)) / plain ↔ ce < (plain - glv0) / N := by
  rw [← glv_wins_iff plain glv0 ce N hN, Rat.lt_div_iff hP]
  constructor <;> intro h <;> grind

/-- The gain is zero iff `ce = C*`. -/
theorem gain_zero_iff (plain glv0 ce N : Rat) (hN : 0 < N) (hP : 0 < plain) :
    100 * (plain - (glv0 + N * ce)) / plain = 0 ↔ ce = (plain - glv0) / N := by
  have hP0 : plain ≠ 0 := by grind
  have hN0 : N ≠ 0 := by grind
  constructor
  · intro h
    have h1 : 100 * (plain - (glv0 + N * ce)) = 0 := by
      have := congrArg (· * plain) h
      grind
    grind
  · intro h
    rw [h]
    have : glv0 + N * ((plain - glv0) / N) = plain := by grind
    rw [this]; grind

/-! ## The ceiling-free common-window model -/

/-- Plain: `b/c` windows, each `N` accumulations (`A`), `2^c` aggregation
additions (`R`), `c` doublings (`D`) and one combine addition (`C`). -/
def idealPlain (b c N A R D C : Rat) (twoPowC : Rat) : Rat :=
  (b / c) * (N * A + twoPowC * R + c * D + C)

/-- GLV at the same window: `(b/2)/c` windows over `2N` points, plus `N` images
at `Cα`. -/
def idealGLV (b c N A R D C : Rat) (twoPowC Cα : Rat) : Rat :=
  ((b / 2) / c) * (2 * N * A + twoPowC * R + c * D + C) + N * Cα

/-- The accumulation term is unchanged and the per-window remainder is halved:
`plain - (glv - N·Cα) = (b/(2c))·(2^c R + c D + C)`. -/
theorem ideal_saving (b c N A R D C twoPowC Cα : Rat) (hc : c ≠ 0) :
    (b / c) * (N * A) = ((b / 2) / c) * (2 * N * A) ∧
    idealPlain b c N A R D C twoPowC - (idealGLV b c N A R D C twoPowC Cα - N * Cα)
      = (b / (2 * c)) * (twoPowC * R + c * D + C) := by
  constructor
  · grind
  · simp only [idealPlain, idealGLV]; grind

/-- **Break-even in the common-window model.** -/
theorem ideal_glv_wins_iff (b c N A R D C twoPowC Cα : Rat) (hc : c ≠ 0) (hN : 0 < N) :
    idealGLV b c N A R D C twoPowC Cα < idealPlain b c N A R D C twoPowC ↔
      Cα < (b / (2 * c)) * (twoPowC * R + c * D + C) / N := by
  have hs := (ideal_saving b c N A R D C twoPowC Cα hc).2
  have e : idealGLV b c N A R D C twoPowC Cα =
      (idealGLV b c N A R D C twoPowC Cα - N * Cα) + N * Cα := by grind
  rw [e, ← hs]
  have := glv_wins_iff (idealPlain b c N A R D C twoPowC)
    (idealGLV b c N A R D C twoPowC Cα - N * Cα) Cα N hN
  grind

/-- The break-even exceeds the aggregation-only saving by exactly the halved
window-combination work `((b/2)·D + (b/(2c))·C)/N`. -/
theorem ideal_cstar_decomposition (b c N R D C twoPowC : Rat) (hc : c ≠ 0) :
    (b / (2 * c)) * (twoPowC * R + c * D + C) / N
      = (b / (2 * c)) * twoPowC * R / N + ((b / 2) * D + (b / (2 * c)) * C) / N := by
  grind

end CryptoResearch.Endosweep.Pippenger

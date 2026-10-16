/-
The x-only conjugate trick for 2-D GLV (candidate C1).

Source:  research/endosweep_xonly_20261008/README.md ("Question", Finding 7,
         and the appended "Lean verification" section)
Targets: formal/targets/endosweep-xonly-*.yaml

The README's mechanism: a 2-D differential addition chain on the x-line needs
the difference `x(P - βP)`. "If `Tr β = 1` then `β - 1 = -β̄`, so
`x(βP - P) = x(β̄P)`"; the cheapest trace-one element is `ω = (1 + √D_K)/2`,
and on the order-`n` subgroup `ω̄` acts as `[1 - λ]`. Finding 7: the trick
"needs `β + β̄ = 1`, an element of odd trace", "for `D ≡ 0 mod 4` every trace
is even and the trick does not exist", and "`β - 1 = β̄` would need
`β - β̄ = 1`, which is impossible for a non-real `β`".

WHAT IS PROVED (core Lean only; no Mathlib).
* `sub_one_eq_neg_conj`: in any commutative ring, `β + β̄ = 1 → β - 1 = -β̄`.
* `conj_root_of_trace_one`: if `ω² = ω + m` then `ω̄ := 1 - ω` satisfies
  `ω̄² = ω̄ + m` (the conjugate is a root of the same polynomial).
* `eigen_conj_mod`: `n ∣ λ² - λ - m → n ∣ (1-λ)² - (1-λ) - m`.
* `conj_eigenvalue`: in any `ℤ`-module, if `ω̄ P = P - ω P` (i.e. `ω̄ = 1 - ω`)
  and `ω P = [λ]P`, then `ω̄ P = [1 - λ]P`.
* `xonly_difference_eq_conj` (THE TRICK): for maps `β, β̄` with
  `βP + β̄P = P` and ANY `x` with `x(-Q) = x(Q)`, `x(βP - P) = x(β̄P)`.
  `xonly_sum_eq_conj` is the trace `-1` variant, `x(βP + P) = x(β̄P)`.
* `QuadOrder D`: the quadratic order of discriminant `D` as `ℤ²` in the
  basis `1, w` with `w = (D + √D)/2`, `w² = D·w + (D - D²)/4`, conjugation
  `w̄ = D - w`. `add_conj` shows `β + β̄` is the rational integer
  `trace β = 2a + bD`. `trace_even_of_D_even`: if `D` is even (in particular
  `D ≡ 0 mod 4`) every trace is even, so no `β` has `β + β̄ = ±1`
  (`no_trace_pm_one_of_D_even`). `trace_one_exists_iff_D_odd`: a trace-one
  element exists iff `D` is odd. `sub_conj_ne_one`: `β - β̄ = 1` has no
  solution in the order, for every `D`.
* `omega_norms`: `N(ω) = (1 - D)/4` is 155, 85 and 1039 for `D = -619, -339,
  -4155` (CryptoPro-B, CP6-782, Tom-256), and `N(-5 + 11ω) = 125 689` on
  Tom-256, each element of trace 1: closed arithmetic checked by `decide`.

WHAT IS NOT PROVED. Nothing about the curves themselves: that the x-only
rational maps realise `ω` and `ω̄` (checked on points by `xonly.py`), that `x`
on a Weierstrass curve satisfies `x(-P) = x(P)` (true, but a hypothesis on an
abstract `x` here), that `β̄` is the conjugate CHAIN of the same cost, the
operation counts, the ratio `R`, and novelty. The norms' factorisations
(`155 = 5·31` etc.) are not restated.
-/

namespace CryptoResearch.Endosweep.XOnlyConjugate

/-! ## Ring and congruence identities -/

/-- `β + β̄ = 1` gives `β - 1 = -β̄`, in any commutative ring. -/
theorem sub_one_eq_neg_conj {R : Type _} [Lean.Grind.CommRing R] (β βbar : R)
    (h : β + βbar = 1) : β - 1 = -βbar := by
  grind

/-- If `ω² = ω + m` (a trace-one root of `X² - X - m`), then `ω̄ = 1 - ω` is a
root of the same polynomial. -/
theorem conj_root_of_trace_one {R : Type _} [Lean.Grind.CommRing R] (ω m : R)
    (h : ω ^ 2 = ω + m) : (1 - ω) ^ 2 = (1 - ω) + m := by
  grind

/-- The eigenvalue congruence passes to `1 - λ`: if `λ² ≡ λ + m (mod n)` then
`(1 - λ)² ≡ (1 - λ) + m (mod n)`. -/
theorem eigen_conj_mod (n l m : Int) (h : n ∣ l ^ 2 - l - m) :
    n ∣ (1 - l) ^ 2 - (1 - l) - m := by
  have : (1 - l) ^ 2 - (1 - l) - m = l ^ 2 - l - m := by grind
  rw [this]; exact h

/-! ## Endomorphisms on an abstract group -/

/-- If `ω̄ = 1 - ω` and `ω` acts on `P` as `[λ]`, then `ω̄` acts on `P` as
`[1 - λ]`. -/
theorem conj_eigenvalue {G : Type _} [Lean.Grind.IntModule G] (ω ωbar : G → G) (l : Int)
    (P : G) (hbar : ωbar P = P - ω P) (heig : ω P = l • P) :
    ωbar P = (1 - l) • P := by
  have h1 : (1 - l) • P = (1 : Int) • P + (-l) • P := by
    rw [← Lean.Grind.IntModule.add_zsmul]; congr 1
  have h2 : (-l) • P + l • P = 0 := by
    rw [← Lean.Grind.IntModule.add_zsmul, Int.add_left_neg, Lean.Grind.IntModule.zero_zsmul]
  rw [hbar, heig, h1, Lean.Grind.IntModule.one_zsmul]
  grind

/-- **The x-only conjugate trick.** Let `β, β̄` be maps on a group with
`βP + β̄P = P` (that is, `β + β̄ = 1` evaluated at `P`) and let `x` be any map
that cannot see the sign, `x(-Q) = x(Q)`. Then the difference point needed by
the 2-D differential chain is the conjugate image: `x(βP - P) = x(β̄P)`. -/
theorem xonly_difference_eq_conj {G X : Type _} [Lean.Grind.IntModule G]
    (β βbar : G → G) (x : G → X) (hx : ∀ Q, x (-Q) = x Q) (P : G)
    (htr : β P + βbar P = P) : x (β P - P) = x (βbar P) := by
  have : β P - P = -(βbar P) := by grind
  rw [this, hx]

/-- The trace `-1` variant: if `βP + β̄P = -P`, then `x(βP + P) = x(β̄P)`. -/
theorem xonly_sum_eq_conj {G X : Type _} [Lean.Grind.IntModule G]
    (β βbar : G → G) (x : G → X) (hx : ∀ Q, x (-Q) = x Q) (P : G)
    (htr : β P + βbar P = -P) : x (β P + P) = x (βbar P) := by
  have : β P + P = -(βbar P) := by grind
  rw [this, hx]

/-! ## The quadratic order of discriminant `D` -/

/-- `a + b·w` in the order of discriminant `D`, `w = (D + √D)/2`. -/
structure QuadOrder (D : Int) where
  a : Int
  b : Int
deriving DecidableEq

namespace QuadOrder

variable {D : Int}

/-- `w² = D·w + (D - D²)/4`; `(D - D²)/4` is an integer when `D ≡ 0, 1 (mod 4)`. -/
def mul (x y : QuadOrder D) : QuadOrder D :=
  ⟨x.a * y.a + x.b * y.b * ((D - D ^ 2) / 4), x.a * y.b + x.b * y.a + x.b * y.b * D⟩

def add (x y : QuadOrder D) : QuadOrder D := ⟨x.a + y.a, x.b + y.b⟩
def sub (x y : QuadOrder D) : QuadOrder D := ⟨x.a - y.a, x.b - y.b⟩
def one : QuadOrder D := ⟨1, 0⟩
def ofInt (k : Int) : QuadOrder D := ⟨k, 0⟩

/-- Conjugation: `w̄ = D - w`, so `a + b w ↦ (a + bD) - b w`. -/
def conj (x : QuadOrder D) : QuadOrder D := ⟨x.a + x.b * D, -x.b⟩

/-- The trace `β + β̄` as a rational integer. -/
def trace (x : QuadOrder D) : Int := 2 * x.a + x.b * D

/-- The norm `β β̄` as a rational integer. -/
def norm (x : QuadOrder D) : Int := x.a ^ 2 + x.a * x.b * D + x.b ^ 2 * ((D ^ 2 - D) / 4)

/-- `β + β̄` is the rational integer `trace β`. -/
theorem add_conj (x : QuadOrder D) : add x (conj x) = ofInt (trace x) := by
  simp only [add, conj, ofInt, trace, QuadOrder.mk.injEq]; constructor <;> omega

/-- `w̄` is the other root: `w + w̄ = D`, so `conj` is the nontrivial
automorphism (`w ↦ D - w`). -/
theorem conj_w : add (⟨0, 1⟩ : QuadOrder D) (conj ⟨0, 1⟩) = ofInt D := by
  simp [add, conj, ofInt]

/-- If `D` is even (in particular `D ≡ 0 mod 4`), every element has even
trace. -/
theorem trace_even_of_D_even (hD : D % 2 = 0) (x : QuadOrder D) : trace x % 2 = 0 := by
  obtain ⟨k, hk⟩ : ∃ k, D = 2 * k := ⟨D / 2, by omega⟩
  have : x.b * D = 2 * (x.b * k) := by
    have e : x.b * D = x.b * (2 * k) := congrArg (x.b * ·) hk
    rw [e]; grind
  simp only [trace]; omega

/-- So for even `D` no element has `β + β̄ = 1` or `β + β̄ = -1`: the trick
does not exist. -/
theorem no_trace_pm_one_of_D_even (hD : D % 2 = 0) (x : QuadOrder D) :
    add x (conj x) ≠ one ∧ add x (conj x) ≠ ofInt (-1) := by
  have h := trace_even_of_D_even hD x
  rw [add_conj]
  constructor <;> intro he <;> simp [ofInt, one] at he <;> omega

/-- A trace-one element exists iff `D` is odd; for odd `D` it is
`ω = (1 - D)/2 + w = (1 + √D)/2`. -/
theorem trace_one_exists_iff_D_odd :
    (∃ x : QuadOrder D, trace x = 1) ↔ D % 2 = 1 := by
  constructor
  · rintro ⟨x, hx⟩
    by_cases h : D % 2 = 0
    · have := trace_even_of_D_even h x; omega
    · omega
  · intro h
    refine ⟨⟨(1 - D) / 2, 1⟩, ?_⟩
    simp only [trace]; omega

/-- `β - β̄ = 1` has no solution in the order, for any `D`: the `w`-coordinate
of `β - β̄` is `2b`, which forces `b = 0` and then `β - β̄ = 0`. -/
theorem sub_conj_ne_one (x : QuadOrder D) : sub x (conj x) ≠ one := by
  intro h
  simp only [sub, conj, one, QuadOrder.mk.injEq] at h
  obtain ⟨h1, h2⟩ := h
  have hb : x.b = 0 := by omega
  rw [hb] at h1; simp at h1

/-- The trace-one elements quoted in the README, with their norms:
`ω = (1 + √D)/2` has `N(ω) = (1 - D)/4` = 155 (CryptoPro-B, `D = -619`),
85 (CP6-782, `D = -339`), 1039 (Tom-256, `D = -4155`); on Tom-256
`-5 + 11ω` has trace 1 and norm 125 689. -/
theorem omega_norms :
    let ω619 : QuadOrder (-619) := ⟨(1 - (-619)) / 2, 1⟩
    let ω339 : QuadOrder (-339) := ⟨(1 - (-339)) / 2, 1⟩
    let ω4155 : QuadOrder (-4155) := ⟨(1 - (-4155)) / 2, 1⟩
    let β : QuadOrder (-4155) := ⟨-5 + 11 * ((1 - (-4155)) / 2), 11⟩
    trace ω619 = 1 ∧ norm ω619 = 155 ∧
    trace ω339 = 1 ∧ norm ω339 = 85 ∧
    trace ω4155 = 1 ∧ norm ω4155 = 1039 ∧
    trace β = 1 ∧ norm β = 125689 := by
  decide

end QuadOrder

end CryptoResearch.Endosweep.XOnlyConjugate

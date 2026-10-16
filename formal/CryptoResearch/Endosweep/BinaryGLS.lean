/-
The binary GLS endomorphism ψ of gls.py: ψ² = -1, ψ preserves the curve, ψ
commutes with the affine group law, and its λ-forms.

Source:  research/endosweep_lambda_20261008/README.md (Results §3 "ψ", and
         the appended "Lean verification" section); maps transcribed from
         harness/endosweep/gls.py (`psi_affine`, `psi_lambda_affine`,
         `psi_lambda`, `Fq2.conj`), affine law from harness/endosweep/binary.py.
Targets: formal/targets/endosweep-gls-*.yaml

Setting of gls.py: `K = F_{q²} = F_q[u]/(u² + u + 1)`, `q = 2^m`, `m` odd, the
curve `Ẽ : y² + xy = x³ + u·x² + b` with `b ∈ F_q`, `σ` the `q`-power
Frobenius of `K` (so `σ² = id`, `σ(u) = u^q = u + 1`, `σ(b) = b`) and
`ψ(x, y) = (σx, σy + u·σx)`; in λ-affine form `(σx, σλ + u)`, in
λ-projective form `(σX, σL + u·σZ, σZ)`. The README: "ψ² = −1 holds on random
points, and ψ is additive."

WHAT IS PROVED, for ANY field `K` of characteristic 2 with a map `σ` that is
additive, multiplicative, fixes 1 and is an involution, any `u` with
`u² + u + 1 = 0` and `σ u = u + 1`, and any `b` with `σ b = b`:
* `psi_psi`: `ψ(ψ P) = -P` for every `P = (x, y)` (`-P = (x, x + y)`), i.e.
  ψ² = -1 as maps on affine points (curve membership is not even needed).
* `psi_onCurve`: `ψ` maps `Ẽ(K)` to `Ẽ(K)`.
* `psi_add`, `psi_dbl`: `ψ` commutes with the affine chord and tangent formulas
  of binary.py in their generic branches (`x_P ≠ x_Q`; `x ≠ 0`), so it is a
  group endomorphism on the points those branches cover.
* `psi_lambda_affine`, `psi_lambda_proj`: the λ-affine `(σx, σλ + u)` and
  λ-projective `(σX, σL + uσZ, σZ)` forms used by the code represent `ψ P`.
* `twist_iso_onCurve`, `conj_by_twist`: the origin of ψ. For any field `L` of
  characteristic 2 and any ring endomorphism `τ` of `L`, `φ_s(x, y) = (x, y + s x)`
  maps `y² + xy = x³ + a x² + b` to the curve with `a + s² + s`, is its own
  inverse, and `φ_s ∘ τ ∘ φ_s⁻¹ = (τx, τy + (s + τ s)·τx)`. With
  `s + τ s = u` this is gls.py's ψ (`psi_eq_conj_by_twist`).

WHAT IS NOT PROVED. That the concrete tower of gls.py is a field with these
properties (`x^127 + x^63 + 1` irreducible, `u² + u + 1` irreducible over F_q
for odd m: checked by the harness, standard); the degenerate branches of the
group law (`P = ±Q`, `O`); the eigenvalue `δ`, the group order, `r` prime,
the AGM trace, the 2-GLV lattice and every operation count.
-/

set_option linter.unusedSectionVars false

namespace CryptoResearch.Endosweep.BinaryGLS

variable {K : Type _} [Lean.Grind.Field K] [Lean.Grind.IsCharP K 2]

/-! ## The affine reference (binary.py), with general `a` -/

def OnCurve (a b : K) (P : K × K) : Prop :=
  P.2 ^ 2 + P.1 * P.2 = P.1 ^ 3 + a * P.1 ^ 2 + b

def affineAdd (a : K) (P Q : K × K) : K × K :=
  let lam := (P.2 + Q.2) / (P.1 + Q.1)
  let x3 := lam ^ 2 + lam + P.1 + Q.1 + a
  (x3, lam * (P.1 + x3) + x3 + P.2)

def affineDbl (a : K) (P : K × K) : K × K :=
  let lam := P.1 + P.2 / P.1
  let x3 := lam ^ 2 + lam + a
  (x3, P.1 ^ 2 + lam * x3 + x3)

def affineNeg (P : K × K) : K × K := (P.1, P.1 + P.2)

/-- `LambdaCurve.to_affine`. -/
def toAffine (P : K × K × K) : K × K :=
  let x := P.1 / P.2.2
  (x, x * (P.2.1 / P.2.2 + x))

/-- `(x, y) ↦ (x, λ = x + y/x)`. -/
def toLambdaAffine (P : K × K) : K × K := (P.1, P.1 + P.2 / P.1)

/-! ## The field automorphism `σ` -/

/-- An additive, multiplicative, unital involution of `K`: the `q`-power
Frobenius of `F_{q²}` is one. -/
structure Involution (σ : K → K) : Prop where
  map_add : ∀ p q, σ (p + q) = σ p + σ q
  map_mul : ∀ p q, σ (p * q) = σ p * σ q
  map_one : σ 1 = 1
  invol : ∀ p, σ (σ p) = p

namespace Involution

variable {σ : K → K} (hσ : Involution σ)
include hσ

theorem map_zero : σ 0 = 0 := by
  have h := hσ.map_add 0 0
  have : (0 : K) + 0 = 0 := by grind
  rw [this] at h; grind

theorem map_pow (p : K) : ∀ n : Nat, σ (p ^ n) = σ p ^ n
  | 0 => by rw [Lean.Grind.Semiring.pow_zero, Lean.Grind.Semiring.pow_zero, hσ.map_one]
  | n + 1 => by
    rw [Lean.Grind.Semiring.pow_succ, Lean.Grind.Semiring.pow_succ, hσ.map_mul, map_pow p n]

theorem map_inv (p : K) : σ (p⁻¹) = (σ p)⁻¹ := by
  by_cases hp : p = 0
  · rw [hp, Lean.Grind.Field.inv_zero, hσ.map_zero, Lean.Grind.Field.inv_zero]
  · have hsp : σ p ≠ 0 := by
      intro h; apply hp; rw [← hσ.invol p, h, hσ.map_zero]
    have h1 : σ p * σ (p⁻¹) = 1 := by
      rw [← hσ.map_mul, Lean.Grind.Field.mul_inv_cancel hp, hσ.map_one]
    grind

theorem map_div (p q : K) : σ (p / q) = σ p / σ q := by
  rw [Lean.Grind.Field.div_eq_mul_inv, Lean.Grind.Field.div_eq_mul_inv, hσ.map_mul, hσ.map_inv]

theorem ne_zero {p : K} (hp : p ≠ 0) : σ p ≠ 0 := by
  intro h; apply hp; rw [← hσ.invol p, h, hσ.map_zero]

end Involution

/-! ## ψ -/

/-- gls.py `psi_affine`: `ψ(x, y) = (σx, σy + u·σx)`. -/
def psi (σ : K → K) (u : K) (P : K × K) : K × K := (σ P.1, σ P.2 + u * σ P.1)

/-- gls.py `psi_lambda_affine`: `(x, λ) ↦ (σx, σλ + u)`. -/
def psiLambdaAffine (σ : K → K) (u : K) (P : K × K) : K × K := (σ P.1, σ P.2 + u)

/-- gls.py `psi_lambda`: `(X, L, Z) ↦ (σX, σL + u·σZ, σZ)`. -/
def psiLambda (σ : K → K) (u : K) (P : K × K × K) : K × K × K :=
  (σ P.1, σ P.2.1 + u * σ P.2.2, σ P.2.2)

variable {σ : K → K} {u b : K}

/-- **ψ² = -1** on affine points. -/
theorem psi_psi (hσ : Involution σ) (hu : σ u = u + 1) (P : K × K) :
    psi σ u (psi σ u P) = affineNeg P := by
  obtain ⟨x, y⟩ := P
  simp only [psi, affineNeg, hσ.map_add, hσ.map_mul, hσ.invol, hu, Prod.mk.injEq, true_and]
  grind

/-- ψ maps `Ẽ : y² + xy = x³ + u x² + b` (`σ b = b`) to itself. -/
theorem psi_onCurve (hσ : Involution σ) (hu : σ u = u + 1) (hu2 : u ^ 2 + u + 1 = 0)
    (hb : σ b = b) (P : K × K) (hP : OnCurve u b P) : OnCurve u b (psi σ u P) := by
  obtain ⟨x, y⟩ := P
  simp only [OnCurve, psi] at hP ⊢
  have h := congrArg σ hP
  simp only [hσ.map_add, hσ.map_mul, hσ.map_pow, hu, hb] at h
  grind

/-- ψ commutes with the generic affine addition. -/
theorem psi_add (hσ : Involution σ) (hu : σ u = u + 1) (hu2 : u ^ 2 + u + 1 = 0)
    (P Q : K × K) (h : P.1 + Q.1 ≠ 0) :
    psi σ u (affineAdd u P Q) = affineAdd u (psi σ u P) (psi σ u Q) := by
  obtain ⟨x1, y1⟩ := P
  obtain ⟨x2, y2⟩ := Q
  simp only at h
  have h' : σ x1 + σ x2 ≠ 0 := by rw [← hσ.map_add]; exact hσ.ne_zero h
  simp only [psi, affineAdd, hσ.map_add, hσ.map_mul, hσ.map_pow, hσ.map_div, hu]
  -- the new slope is σ s + u
  have hs : (σ y1 + u * σ x1 + (σ y2 + u * σ x2)) / (σ x1 + σ x2) = (σ y1 + σ y2) / (σ x1 + σ x2) + u := by
    grind
  rw [hs]
  generalize (σ y1 + σ y2) / (σ x1 + σ x2) = t
  simp only [Prod.mk.injEq]
  constructor <;> grind

/-- ψ commutes with the generic affine doubling. -/
theorem psi_dbl (hσ : Involution σ) (hu : σ u = u + 1) (hu2 : u ^ 2 + u + 1 = 0)
    (P : K × K) (h : P.1 ≠ 0) :
    psi σ u (affineDbl u P) = affineDbl u (psi σ u P) := by
  obtain ⟨x, y⟩ := P
  simp only at h
  have h' : σ x ≠ 0 := hσ.ne_zero h
  simp only [psi, affineDbl, hσ.map_add, hσ.map_mul, hσ.map_pow, hσ.map_div, hu]
  have hs : σ x + (σ y + u * σ x) / σ x = σ x + σ y / σ x + u := by grind
  rw [hs]
  generalize σ x + σ y / σ x = t
  simp only [Prod.mk.injEq]
  constructor <;> grind

/-- The λ-affine form `(σx, σλ + u)` of gls.py is ψ in λ-coordinates. -/
theorem psi_lambda_affine (hσ : Involution σ) (P : K × K) (h : P.1 ≠ 0) :
    toLambdaAffine (psi σ u P) = psiLambdaAffine σ u (toLambdaAffine P) := by
  obtain ⟨x, y⟩ := P
  simp only at h
  have h' : σ x ≠ 0 := hσ.ne_zero h
  simp only [toLambdaAffine, psi, psiLambdaAffine, hσ.map_add, hσ.map_div, Prod.mk.injEq, true_and]
  grind

/-- The λ-projective form `(σX, σL + uσZ, σZ)` of gls.py represents ψ. -/
theorem psi_lambda_proj (hσ : Involution σ) (X L Z : K) (hZ : Z ≠ 0) :
    toAffine (psiLambda σ u (X, L, Z)) = psi σ u (toAffine (X, L, Z)) := by
  have h' : σ Z ≠ 0 := hσ.ne_zero hZ
  simp only [toAffine, psiLambda, psi, hσ.map_mul, hσ.map_add, hσ.map_div, Prod.mk.injEq, true_and]
  grind

/-! ## Where ψ comes from: conjugating Frobenius by the twist isomorphism -/

section Twist

variable {L : Type _} [Lean.Grind.Field L] [Lean.Grind.IsCharP L 2]

/-- `φ_s(x, y) = (x, y + s·x)`. -/
def twistIso (s : L) (P : L × L) : L × L := (P.1, P.2 + s * P.1)

omit [Lean.Grind.IsCharP K 2] in
/-- `φ_s` maps `y² + xy = x³ + a x² + b` to `y² + xy = x³ + (a + s² + s) x² + b`. -/
theorem twist_iso_onCurve (a b s : L) (P : L × L) (hP : OnCurve a b P) :
    OnCurve (a + s ^ 2 + s) b (twistIso s P) := by
  obtain ⟨x, y⟩ := P
  simp only [OnCurve, twistIso] at hP ⊢
  grind

/-- `φ_s` is its own inverse in characteristic 2. -/
theorem twist_iso_invol (s : L) (P : L × L) : twistIso s (twistIso s P) = P := by
  obtain ⟨x, y⟩ := P
  simp only [twistIso, Prod.mk.injEq, true_and]
  grind

/-- `φ_s ∘ τ ∘ φ_s⁻¹ = (τx, τy + (s + τ s)·τx)` for any additive, multiplicative
`τ` (the `q`-power Frobenius of `F_{q⁴}`). -/
theorem conj_by_twist (τ : L → L) (hadd : ∀ p q, τ (p + q) = τ p + τ q)
    (hmul : ∀ p q, τ (p * q) = τ p * τ q) (s : L) (P : L × L) :
    twistIso s ((fun Q : L × L => (τ Q.1, τ Q.2)) (twistIso s P)) =
      (τ P.1, τ P.2 + (s + τ s) * τ P.1) := by
  obtain ⟨x, y⟩ := P
  simp only [twistIso, hadd, hmul, Prod.mk.injEq, true_and]
  grind

/-- With `s + τ s = u`, the conjugate is gls.py's `ψ(x, y) = (τx, τy + u·τx)`. -/
theorem psi_eq_conj_by_twist (τ : L → L) (hadd : ∀ p q, τ (p + q) = τ p + τ q)
    (hmul : ∀ p q, τ (p * q) = τ p * τ q) (s u : L) (hs : s + τ s = u) (P : L × L) :
    twistIso s ((fun Q : L × L => (τ Q.1, τ Q.2)) (twistIso s P)) = psi τ u P := by
  rw [conj_by_twist τ hadd hmul s P, hs]; rfl

end Twist

end CryptoResearch.Endosweep.BinaryGLS

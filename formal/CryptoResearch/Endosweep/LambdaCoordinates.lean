/-
λ-projective formulas on binary curves, against the affine group law.

Source:  research/endosweep_lambda_20261008/README.md ("What is checked",
         Results §1 remark on the alternative doubling, and the appended
         "Lean verification" section); formulas transcribed from
         harness/endosweep/lambdacoord.py (`LambdaCurve.dbl`, `add`, `madd`,
         `dbl_add`, `to_affine`, `neg`, `frobenius`), which implements Oliveira, López,
         Aranha, Rodríguez-Henríquez, "Lambda coordinates for binary elliptic
         curves", CHES 2013, Theorems 1-3; the affine reference is
         harness/endosweep/binary.py (`BinaryCurve.add`, `dbl`, `neg`).
Targets: formal/targets/endosweep-lambda-*.yaml

The curve is `E : y² + xy = x³ + a x² + b` over a field `K` of characteristic 2
(core `Lean.Grind.Field` + `Lean.Grind.IsCharP K 2`; every Mathlib field of
characteristic 2 is an instance). A point `(x, y)` with `x ≠ 0` has
`λ = x + y/x`; a λ-projective triple `(X, L, Z)` with `Z ≠ 0` stands for
`x = X/Z`, `λ = L/Z`, and `to_affine` returns `(x, x·(λ + x))`.

WHAT IS PROVED. With every operation written exactly as in lambdacoord.py
(XOR = `+`), and under exactly the nondegeneracy conditions under which the
code takes the generic branch (it raises or branches otherwise):
* `curve_equation_iff`: for `X, Z ≠ 0`, the λ-projective equation
  `(L² + LZ + aZ²)X² = X⁴ + bZ⁴` holds iff `to_affine (X, L, Z)` is on `E`.
* `dbl_main_correct` (Theorem 1): for `X, Z ≠ 0` and `T = L² + LZ + aZ² ≠ 0`,
  `to_affine (dbl_main P) = affine_dbl (to_affine P)` and the output has
  `Z ≠ 0`. No curve equation is needed.
* `alt_T_eq` (the README's "subtlety"): `L(L + Z) + aZ² = L² + LZ + aZ²`, so
  the alternative doubling's `T` is Theorem 1's `T`.
* `dbl_alt_eq_dbl_main`: on the curve, the alternative doubling
  `L_2P = (L+X)²((L+X)² + T + Z²) + T² + (a+1)TZ² + (a²+b)Z⁴` returns
  EXACTLY the same triple as Theorem 1; `dbl_alt_correct` follows.
* `add_correct` (Theorem 2, 11M + 2S form): for `P, Q` on the curve with
  `X, Z ≠ 0`, `x_P ≠ x_Q` (the code's `Bs ≠ 0`) and `X₃ ≠ 0` (the code raises
  otherwise), `to_affine (add P Q) = affine_add (to_affine P) (to_affine Q)`.
* `madd_correct` (Theorem 2 with `Z_P = 1`, the code's `madd`): the same with
  `P` λ-affine.
* `dbl_add_correct` (Theorem 3, `dbl_add`, 10M + 6S + m_a): for `Q` on the
  curve (`X, Z ≠ 0`), `P` λ-affine on the curve, and the code's nonzero
  conditions `T ≠ 0`, `B ≠ 0`, `A ≠ 0`,
  `to_affine (dbl_add Q P) = affine_add (affine_dbl (to_affine Q)) P`.
  (`affineDbl_onCurve`: doubling preserves the curve.)
* `neg_correct`, `frobenius_correct`: `(X, L + Z, Z)` is `-P` and
  `(X², L², Z²)` is `(x², y²)`.

WHAT IS NOT PROVED. The degenerate branches (`P = ±Q`, `O`, `x = 0`) are not formalised (the code
handles them by branching); operation COUNTS (Table 3 reproduced) are measured,
not Lean claims; that `affine_add`/`affine_dbl` are the group law of `E` is
the standard chord-tangent law and is taken as the reference, as the harness
does.
-/

namespace CryptoResearch.Endosweep.LambdaCoordinates

variable {K : Type _} [Lean.Grind.Field K] [Lean.Grind.IsCharP K 2]

/-! ## The affine reference (binary.py) -/

/-- `y² + xy = x³ + a x² + b`. -/
def OnCurve (a b : K) (P : K × K) : Prop :=
  P.2 ^ 2 + P.1 * P.2 = P.1 ^ 3 + a * P.1 ^ 2 + b

/-- `BinaryCurve.add`, generic branch `x_P ≠ x_Q`. -/
def affineAdd (a : K) (P Q : K × K) : K × K :=
  let lam := (P.2 + Q.2) / (P.1 + Q.1)
  let x3 := lam ^ 2 + lam + P.1 + Q.1 + a
  (x3, lam * (P.1 + x3) + x3 + P.2)

/-- `BinaryCurve.dbl`, generic branch `x ≠ 0`. -/
def affineDbl (a : K) (P : K × K) : K × K :=
  let lam := P.1 + P.2 / P.1
  let x3 := lam ^ 2 + lam + a
  (x3, P.1 ^ 2 + lam * x3 + x3)

/-- `BinaryCurve.neg`: `(x, x + y)`. -/
def affineNeg (P : K × K) : K × K := (P.1, P.1 + P.2)

/-! ## λ-coordinates (lambdacoord.py) -/

/-- `LambdaCurve.to_affine`: `zi = 1/Z, x = X·zi, y = x·(L·zi + x)`. -/
def toAffine (P : K × K × K) : K × K :=
  let x := P.1 / P.2.2
  (x, x * (P.2.1 / P.2.2 + x))

/-- `LambdaCurve.from_lambda_affine`: `(x, λ) ↦ (x, x(λ + x))`. -/
def fromLambdaAffine (P : K × K) : K × K := (P.1, P.1 * (P.2 + P.1))

/-- The λ-projective curve equation `(L² + LZ + aZ²)X² = X⁴ + bZ⁴`. -/
def OnCurveProj (a b : K) (P : K × K × K) : Prop :=
  (P.2.1 ^ 2 + P.2.1 * P.2.2 + a * P.2.2 ^ 2) * P.1 ^ 2 = P.1 ^ 4 + b * P.2.2 ^ 4

/-- Theorem 1 doubling (`dbl`, formula "main"). -/
def dblMain (a : K) (P : K × K × K) : K × K × K :=
  let X := P.1; let L := P.2.1; let Z := P.2.2
  let LZ := L * Z
  let Z2 := Z ^ 2
  let T := L ^ 2 + LZ + a * Z2
  let X2 := T ^ 2
  let Z2P := T * Z2
  (X2, (X * Z) ^ 2 + X2 + T * LZ + Z2P, Z2P)

/-- The alternative doubling (`dbl`, formula "alt"), with `T = L(L + Z) + aZ²`.
The code skips the last term when `a² + b = 0`; adding `0·Z⁴` is the same. -/
def dblAlt (a b : K) (P : K × K × K) : K × K × K :=
  let X := P.1; let L := P.2.1; let Z := P.2.2
  let Z2 := Z ^ 2
  let T := L * (L + Z) + a * Z2
  let X2 := T ^ 2
  let Z2P := T * Z2
  let LX2 := (L + X) ^ 2
  (X2, LX2 * (LX2 + T + Z2) + X2 + (a + 1) * Z2P + (a ^ 2 + b) * Z2 ^ 2, Z2P)

/-- Theorem 2 full addition (`add`, 11M + 2S). -/
def add (P Q : K × K × K) : K × K × K :=
  let XP := P.1; let LP := P.2.1; let ZP := P.2.2
  let XQ := Q.1; let LQ := Q.2.1; let ZQ := Q.2.2
  let XPZQ := XP * ZQ
  let XQZP := XQ * ZP
  let A := LP * ZQ + LQ * ZP
  let Bs := XPZQ + XQZP
  let B := Bs ^ 2
  let AXQZP := A * XQZP
  let X3 := AXQZP * (A * XPZQ)
  let ABZQ := A * B * ZQ
  let L3 := (AXQZP + B) ^ 2 + ABZQ * (LP + ZP)
  (X3, L3, ABZQ * ZP)

/-- Mixed addition `madd Q P`: `Q` λ-projective, `P = (x_P, λ_P)` λ-affine
(Theorem 2 with `Z_P = 1`, 8M + 2S). -/
def madd (Q : K × K × K) (P : K × K) : K × K × K :=
  let XQ := Q.1; let LQ := Q.2.1; let ZQ := Q.2.2
  let xP := P.1; let lP := P.2
  let XPZQ := xP * ZQ
  let A := lP * ZQ + LQ
  let Bs := XPZQ + XQ
  let B := Bs ^ 2
  let AXQ := A * XQ
  let X3 := AXQ * (A * XPZQ)
  let ABZQ := A * B * ZQ
  let L3 := (AXQ + B) ^ 2 + ABZQ * (lP + 1)
  (X3, L3, ABZQ)

/-- Theorem 3 doubling-and-addition `dbl_add Q P = 2Q + P`: `Q` λ-projective,
`P = (x_P, λ_P)` λ-affine (10M + 6S + m_a). -/
def dblAdd (a : K) (Q : K × K × K) (P : K × K) : K × K × K :=
  let XQ := Q.1; let LQ := Q.2.1; let ZQ := Q.2.2
  let xP := P.1; let lP := P.2
  let LQ2 := LQ ^ 2
  let ZQ2 := ZQ ^ 2
  let T := LQ2 + LQ * ZQ + a * ZQ2
  let A := XQ ^ 2 * ZQ2 + T * (LQ2 + (a + 1 + lP) * ZQ2)
  let xZ := xP * ZQ2
  let Bs := xZ + T
  let B := Bs ^ 2
  let X := xZ * A ^ 2
  let Z := A * B * ZQ2
  (X, T * (A + B) ^ 2 + (lP + 1) * Z, Z)

/-- `LambdaCurve.neg`: `(X, L + Z, Z)`. -/
def neg (P : K × K × K) : K × K × K := (P.1, P.2.1 + P.2.2, P.2.2)

/-- `LambdaCurve.frobenius`: `(X², L², Z²)`. -/
def frobenius (P : K × K × K) : K × K × K := (P.1 ^ 2, P.2.1 ^ 2, P.2.2 ^ 2)

/-! ## Helper lemmas -/

theorem mul_div_cancel' (x Z : K) (hZ : Z ≠ 0) : x * Z / Z = x := by grind

/-- Every λ-projective triple with `Z ≠ 0` is `(xZ, λZ, Z)`. -/
theorem exists_rep (X Z : K) (hZ : Z ≠ 0) : ∃ x, X = x * Z := ⟨X / Z, by grind⟩

theorem toAffine_rep (x l Z : K) (hZ : Z ≠ 0) :
    toAffine (x * Z, l * Z, Z) = (x, x * (l + x)) := by
  simp only [toAffine, mul_div_cancel' x Z hZ, mul_div_cancel' l Z hZ]

/-- A triple `(X, L, Z)` with `Z ≠ 0`, `X = x₃Z` and `L·x₃ = (x₃² + y₃)Z`
(i.e. `L/Z = x₃ + y₃/x₃`, the λ of `(x₃, y₃)`) returns `(x₃, y₃)`. -/
theorem toAffine_of_rep (X L Z x3 y3 : K) (hZ : Z ≠ 0) (hx : x3 ≠ 0) (h1 : X = x3 * Z)
    (h2 : L * x3 = (x3 ^ 2 + y3) * Z) : toAffine (X, L, Z) = (x3, y3) := by
  have e1 : X / Z = x3 := by grind
  have e2 : L / Z = (x3 ^ 2 + y3) / x3 := by grind
  simp only [toAffine, e1, e2, Prod.mk.injEq, true_and]
  grind

omit [Lean.Grind.IsCharP K 2] in
theorem ne_zero_of_mul_ne_zero_left (p q : K) (h : p * q ≠ 0) : p ≠ 0 := by
  intro hp; apply h; rw [hp]; grind

omit [Lean.Grind.IsCharP K 2] in
theorem mul_ne_zero' {p q : K} (hp : p ≠ 0) (hq : q ≠ 0) : p * q ≠ 0 := by
  intro h
  have : p⁻¹ * (p * q) = q := by grind
  grind

omit [Lean.Grind.IsCharP K 2] in
theorem pow_ne_zero' {p : K} (hp : p ≠ 0) : ∀ n : Nat, p ^ n ≠ 0
  | 0 => by rw [Lean.Grind.Semiring.pow_zero]; exact Lean.Grind.Field.zero_ne_one.symm
  | n + 1 => by rw [Lean.Grind.Semiring.pow_succ]; exact mul_ne_zero' (pow_ne_zero' hp n) hp

/-! ## The curve equation -/

/-- For `X, Z ≠ 0`, the λ-projective equation is the curve equation of
`to_affine (X, L, Z)`. -/
theorem curve_equation_iff (a b X L Z : K) (hZ : Z ≠ 0) (hX : X ≠ 0) :
    OnCurveProj a b (X, L, Z) ↔ OnCurve a b (toAffine (X, L, Z)) := by
  obtain ⟨x, rfl⟩ := exists_rep X Z hZ
  obtain ⟨l, rfl⟩ := exists_rep L Z hZ
  have hx : x ≠ 0 := ne_zero_of_mul_ne_zero_left x Z hX
  rw [toAffine_rep x l Z hZ]
  simp only [OnCurveProj, OnCurve]
  have hZ4 : Z ^ 4 ≠ 0 := by intro h; apply hZ; grind
  have hx2 : x ^ 2 ≠ 0 := by intro h; apply hx; grind
  have e : (l * Z) ^ 2 + l * Z * Z + a * Z ^ 2 = (l ^ 2 + l + a) * Z ^ 2 := by grind
  rw [e]
  constructor
  · intro h
    have h' : ((l ^ 2 + l + a) * x ^ 2) * Z ^ 4 = (x ^ 4 + b) * Z ^ 4 := by grind
    have h'' : (l ^ 2 + l + a) * x ^ 2 = x ^ 4 + b := by
      have := congrArg (· * (Z ^ 4)⁻¹) h'
      grind
    grind
  · intro h
    have h' : (l ^ 2 + l + a) * x ^ 2 = x ^ 4 + b := by grind
    grind

/-! ## Doubling -/

/-- **Theorem 1 doubling is correct.** -/
theorem dbl_main_correct (a X L Z : K) (hZ : Z ≠ 0) (hX : X ≠ 0)
    (hT : L ^ 2 + L * Z + a * Z ^ 2 ≠ 0) :
    (dblMain a (X, L, Z)).2.2 ≠ 0 ∧
    toAffine (dblMain a (X, L, Z)) = affineDbl a (toAffine (X, L, Z)) := by
  obtain ⟨x, rfl⟩ := exists_rep X Z hZ
  obtain ⟨l, rfl⟩ := exists_rep L Z hZ
  have hx : x ≠ 0 := ne_zero_of_mul_ne_zero_left x Z hX
  rw [toAffine_rep x l Z hZ]
  have hlam : x + x * (l + x) / x = l := by grind
  have hx3 : l ^ 2 + l + a ≠ 0 := by
    intro h; apply hT; grind
  have hZ2 : Z ^ 2 ≠ 0 := by intro h; apply hZ; grind
  simp only [dblMain, affineDbl, hlam]
  have hZout : ((l * Z) ^ 2 + l * Z * Z + a * Z ^ 2) * Z ^ 2 ≠ 0 := by
    intro h
    have : (l ^ 2 + l + a) * (Z ^ 2 * Z ^ 2) = 0 := by grind
    have hh : (Z ^ 2 * Z ^ 2) ≠ 0 := by intro h; apply hZ2; grind
    apply hx3; grind
  refine ⟨hZout, ?_⟩
  apply toAffine_of_rep _ _ _ _ _ hZout hx3 <;> grind

/-- The README's subtlety: the alternative doubling's `T = L(L + Z) + aZ²` is
Theorem 1's `T = L² + LZ + aZ²` (one multiplication instead of a squaring and
a multiplication). -/
theorem alt_T_eq (a L Z : K) : L * (L + Z) + a * Z ^ 2 = L ^ 2 + L * Z + a * Z ^ 2 := by
  grind

/-- On the curve, the alternative doubling returns exactly Theorem 1's triple. -/
theorem dbl_alt_eq_dbl_main (a b X L Z : K) (hC : OnCurveProj a b (X, L, Z)) :
    dblAlt a b (X, L, Z) = dblMain a (X, L, Z) := by
  simp only [OnCurveProj] at hC
  simp only [dblAlt, dblMain, Prod.mk.injEq]
  refine ⟨by grind, ?_, by grind⟩
  grind

/-- **The alternative doubling is correct** on the curve. -/
theorem dbl_alt_correct (a b X L Z : K) (hZ : Z ≠ 0) (hX : X ≠ 0)
    (hC : OnCurveProj a b (X, L, Z)) (hT : L * (L + Z) + a * Z ^ 2 ≠ 0) :
    (dblAlt a b (X, L, Z)).2.2 ≠ 0 ∧
    toAffine (dblAlt a b (X, L, Z)) = affineDbl a (toAffine (X, L, Z)) := by
  rw [dbl_alt_eq_dbl_main a b X L Z hC]
  exact dbl_main_correct a X L Z hZ hX (by rw [← alt_T_eq]; exact hT)

/-! ## Addition -/

/-- The affine core of Theorem 2: with `s(x₁ + x₂) = y₁ + y₂` and both points
on the curve, `x₃ (x₁ + x₂)² = x₁ x₂ (λ₁ + λ₂)` where `y_i = x_i(λ_i + x_i)`. -/
theorem affine_add_x (a b x1 l1 x2 l2 s : K)
    (c1 : OnCurve a b (x1, x1 * (l1 + x1))) (c2 : OnCurve a b (x2, x2 * (l2 + x2)))
    (hs : s * (x1 + x2) = x1 * (l1 + x1) + x2 * (l2 + x2)) :
    (s ^ 2 + s + x1 + x2 + a) * (x1 + x2) ^ 2 = x1 * x2 * (l1 + l2) := by
  simp only [OnCurve] at c1 c2
  have e : (s ^ 2 + s + x1 + x2 + a) * (x1 + x2) ^ 2 =
      (s * (x1 + x2)) ^ 2 + (s * (x1 + x2)) * (x1 + x2) + (x1 + x2) ^ 3 + a * (x1 + x2) ^ 2 := by
    grind
  rw [e, hs]; grind

omit [Lean.Grind.IsCharP K 2] in
/-- The x-part of the bridge: `(λ₁+λ₂)² x₁x₂ W = x₃ · (λ₁+λ₂)(x₁+x₂)² W`. -/
theorem add_x_identity (x1 l1 x2 l2 x3 W : K)
    (F1 : x3 * (x1 + x2) ^ 2 = x1 * x2 * (l1 + l2)) :
    (l1 + l2) ^ 2 * (x1 * x2) * W = x3 * ((l1 + l2) * (x1 + x2) ^ 2 * W) := by
  have : x3 * ((l1 + l2) * (x1 + x2) ^ 2 * W) = (x3 * (x1 + x2) ^ 2) * ((l1 + l2) * W) := by grind
  rw [this, F1]; grind

/-- The λ-part of the bridge (no curve equation needed beyond `F1`). -/
theorem add_lambda_identity (x1 l1 x2 l2 x3 y3 : K)
    (F1 : x3 * (x1 + x2) ^ 2 = x1 * x2 * (l1 + l2))
    (Fy : y3 * (x1 + x2) = (x1 * (l1 + x1) + x2 * (l2 + x2)) * (x1 + x3)
      + (x3 + x1 * (l1 + x1)) * (x1 + x2)) :
    (((l1 + l2) * x2 + (x1 + x2) ^ 2) ^ 2 + (l1 + l2) * (l1 + 1) * (x1 + x2) ^ 2) * x3
      = (x3 ^ 2 + y3) * ((l1 + l2) * (x1 + x2) ^ 2) := by
  grind

/-- **Theorem 2 full addition is correct**, generic case. -/
theorem add_correct (a b XP LP ZP XQ LQ ZQ : K)
    (hZP : ZP ≠ 0) (hZQ : ZQ ≠ 0) (hXP : XP ≠ 0) (hXQ : XQ ≠ 0)
    (cP : OnCurveProj a b (XP, LP, ZP)) (cQ : OnCurveProj a b (XQ, LQ, ZQ))
    (hB : XP * ZQ + XQ * ZP ≠ 0)
    (hX3 : (add (XP, LP, ZP) (XQ, LQ, ZQ)).1 ≠ 0) :
    (add (XP, LP, ZP) (XQ, LQ, ZQ)).2.2 ≠ 0 ∧
    toAffine (add (XP, LP, ZP) (XQ, LQ, ZQ)) =
      affineAdd a (toAffine (XP, LP, ZP)) (toAffine (XQ, LQ, ZQ)) := by
  have aP := (curve_equation_iff a b XP LP ZP hZP hXP).1 cP
  have aQ := (curve_equation_iff a b XQ LQ ZQ hZQ hXQ).1 cQ
  obtain ⟨x1, rfl⟩ := exists_rep XP ZP hZP
  obtain ⟨l1, rfl⟩ := exists_rep LP ZP hZP
  obtain ⟨x2, rfl⟩ := exists_rep XQ ZQ hZQ
  obtain ⟨l2, rfl⟩ := exists_rep LQ ZQ hZQ
  rw [toAffine_rep x1 l1 ZP hZP] at aP ⊢
  rw [toAffine_rep x2 l2 ZQ hZQ] at aQ ⊢
  have hD : x1 + x2 ≠ 0 := by
    intro h; apply hB
    have : x2 = x1 := by grind
    rw [this]; grind
  -- the affine side
  generalize hs : (x1 * (l1 + x1) + x2 * (l2 + x2)) / (x1 + x2) = s
  have hs' : s * (x1 + x2) = x1 * (l1 + x1) + x2 * (l2 + x2) := by rw [← hs]; grind
  have F1 := affine_add_x a b x1 l1 x2 l2 s aP aQ hs'
  simp only [affineAdd, hs]
  generalize hx3 : s ^ 2 + s + x1 + x2 + a = x3
  rw [hx3] at F1
  generalize hy3 : s * (x1 + x3) + x3 + x1 * (l1 + x1) = y3
  have Fy : y3 * (x1 + x2) = (x1 * (l1 + x1) + x2 * (l2 + x2)) * (x1 + x3)
      + (x3 + x1 * (l1 + x1)) * (x1 + x2) := by
    rw [← hy3]; grind
  -- the projective side
  simp only [add] at hX3 ⊢
  have eX3 : (l1 * ZP * ZQ + l2 * ZQ * ZP) * (x2 * ZQ * ZP) * ((l1 * ZP * ZQ + l2 * ZQ * ZP) * (x1 * ZP * ZQ))
      = (l1 + l2) ^ 2 * (x1 * x2) * (ZP * ZQ) ^ 4 := by grind
  have hl : l1 + l2 ≠ 0 := by
    intro h; apply hX3; grind
  have hx1 : x1 ≠ 0 := ne_zero_of_mul_ne_zero_left x1 ZP hXP
  have hx2 : x2 ≠ 0 := ne_zero_of_mul_ne_zero_left x2 ZQ hXQ
  have hW : (ZP * ZQ) ^ 4 ≠ 0 := pow_ne_zero' (mul_ne_zero' hZP hZQ) 4
  have hx3ne : x3 ≠ 0 := by
    intro h; rw [h] at F1
    exact mul_ne_zero' (mul_ne_zero' hx1 hx2) hl (by grind)
  have hZout : (l1 * ZP * ZQ + l2 * ZQ * ZP) * (x1 * ZP * ZQ + x2 * ZQ * ZP) ^ 2 * ZQ * ZP ≠ 0 := by
    have e : (l1 * ZP * ZQ + l2 * ZQ * ZP) * (x1 * ZP * ZQ + x2 * ZQ * ZP) ^ 2 * ZQ * ZP
        = (l1 + l2) * (x1 + x2) ^ 2 * (ZP * ZQ) ^ 4 := by grind
    rw [e]
    exact mul_ne_zero' (mul_ne_zero' hl (pow_ne_zero' hD 2)) hW
  refine ⟨hZout, ?_⟩
  have eZ3 : (l1 * ZP * ZQ + l2 * ZQ * ZP) * (x1 * ZP * ZQ + x2 * ZQ * ZP) ^ 2 * ZQ * ZP
      = (l1 + l2) * (x1 + x2) ^ 2 * (ZP * ZQ) ^ 4 := by grind
  have eL3 : ((l1 * ZP * ZQ + l2 * ZQ * ZP) * (x2 * ZQ * ZP) + (x1 * ZP * ZQ + x2 * ZQ * ZP) ^ 2) ^ 2
      + (l1 * ZP * ZQ + l2 * ZQ * ZP) * (x1 * ZP * ZQ + x2 * ZQ * ZP) ^ 2 * ZQ * (l1 * ZP + ZP)
      = (((l1 + l2) * x2 + (x1 + x2) ^ 2) ^ 2 + (l1 + l2) * (l1 + 1) * (x1 + x2) ^ 2)
        * (ZP * ZQ) ^ 4 := by grind
  have hlam := add_lambda_identity x1 l1 x2 l2 x3 y3 F1 Fy
  have hx := add_x_identity x1 l1 x2 l2 x3 ((ZP * ZQ) ^ 4) F1
  apply toAffine_of_rep _ _ _ _ _ hZout hx3ne
  · rw [eX3, eZ3]; exact hx
  · rw [eL3, eZ3]
    have : (((l1 + l2) * x2 + (x1 + x2) ^ 2) ^ 2 + (l1 + l2) * (l1 + 1) * (x1 + x2) ^ 2)
        * (ZP * ZQ) ^ 4 * x3
        = ((((l1 + l2) * x2 + (x1 + x2) ^ 2) ^ 2 + (l1 + l2) * (l1 + 1) * (x1 + x2) ^ 2) * x3)
        * (ZP * ZQ) ^ 4 := by grind
    rw [this, hlam]; grind

/-! ## Mixed addition -/

/-- The affine law is symmetric in the generic case. -/
theorem affineAdd_comm (a : K) (P Q : K × K) (h : P.1 + Q.1 ≠ 0) :
    affineAdd a P Q = affineAdd a Q P := by
  obtain ⟨x1, y1⟩ := P
  obtain ⟨x2, y2⟩ := Q
  simp only at h
  simp only [affineAdd, Prod.mk.injEq]
  have e1 : (y1 + y2) / (x1 + x2) = (y2 + y1) / (x2 + x1) := by grind
  rw [← e1]
  generalize hs : (y1 + y2) / (x1 + x2) = s
  have hs' : s * (x1 + x2) = y1 + y2 := by rw [← hs]; grind
  constructor
  · grind
  · grind

omit [Lean.Grind.IsCharP K 2] in
/-- `madd Q P` is the full addition of `(x_P, λ_P, 1)` and `Q`. -/
theorem madd_eq_add (Q : K × K × K) (P : K × K) :
    madd Q P = add (P.1, P.2, 1) Q := by
  obtain ⟨XQ, LQ, ZQ⟩ := Q
  obtain ⟨xP, lP⟩ := P
  simp only [madd, add, Prod.mk.injEq]
  refine ⟨by grind, by grind, by grind⟩

/-- **Mixed addition (Theorem 2 with `Z_P = 1`) is correct**, generic case:
`to_affine (madd Q P) = affine_add (to_affine Q) (from_lambda_affine P)`. -/
theorem madd_correct (a b XQ LQ ZQ xP lP : K)
    (hZQ : ZQ ≠ 0) (hXQ : XQ ≠ 0) (hxP : xP ≠ 0)
    (cQ : OnCurveProj a b (XQ, LQ, ZQ)) (cP : OnCurve a b (fromLambdaAffine (xP, lP)))
    (hB : xP * ZQ + XQ ≠ 0)
    (hX3 : (madd (XQ, LQ, ZQ) (xP, lP)).1 ≠ 0) :
    (madd (XQ, LQ, ZQ) (xP, lP)).2.2 ≠ 0 ∧
    toAffine (madd (XQ, LQ, ZQ) (xP, lP)) =
      affineAdd a (toAffine (XQ, LQ, ZQ)) (fromLambdaAffine (xP, lP)) := by
  have h1 : (1 : K) ≠ 0 := Lean.Grind.Field.zero_ne_one.symm
  have eP : toAffine (xP, lP, (1 : K)) = fromLambdaAffine (xP, lP) := by
    have := toAffine_rep xP lP 1 h1
    simp only [fromLambdaAffine]
    have e1 : xP * 1 = xP := by grind
    have e2 : lP * 1 = lP := by grind
    rw [e1, e2] at this; rw [this]
  have cP' : OnCurveProj a b (xP, lP, 1) := by
    rw [curve_equation_iff a b xP lP 1 h1 hxP, eP]; exact cP
  rw [madd_eq_add] at hX3 ⊢
  have hB' : xP * ZQ + XQ * 1 ≠ 0 := by
    have : XQ * 1 = XQ := by grind
    rw [this]; exact hB
  obtain ⟨hz, hc⟩ := add_correct a b xP lP 1 XQ LQ ZQ h1 hZQ hxP hXQ cP' cQ hB' hX3
  refine ⟨hz, ?_⟩
  rw [hc, eP, affineAdd_comm]
  -- the x-coordinates differ
  obtain ⟨x, rfl⟩ := exists_rep XQ ZQ hZQ
  obtain ⟨l, rfl⟩ := exists_rep LQ ZQ hZQ
  rw [toAffine_rep x l ZQ hZQ]
  simp only [fromLambdaAffine]
  intro h; apply hB
  have : x = xP := by grind
  rw [this]; grind

/-! ## Negation and Frobenius -/

/-- `(X, L + Z, Z)` is `-P`: negation is `λ ↦ λ + 1`. -/
theorem neg_correct (X L Z : K) (hZ : Z ≠ 0) :
    toAffine (neg (X, L, Z)) = affineNeg (toAffine (X, L, Z)) := by
  obtain ⟨x, rfl⟩ := exists_rep X Z hZ
  obtain ⟨l, rfl⟩ := exists_rep L Z hZ
  have e : l * Z + Z = (l + 1) * Z := by grind
  simp only [neg, e, toAffine_rep x _ Z hZ, affineNeg, Prod.mk.injEq, true_and]
  grind

/-- `(X², L², Z²)` is the image of `P` under the 2-power Frobenius `(x², y²)`. -/
theorem frobenius_correct (X L Z : K) (hZ : Z ≠ 0) :
    toAffine (frobenius (X, L, Z)) =
      ((toAffine (X, L, Z)).1 ^ 2, (toAffine (X, L, Z)).2 ^ 2) := by
  obtain ⟨x, rfl⟩ := exists_rep X Z hZ
  obtain ⟨l, rfl⟩ := exists_rep L Z hZ
  have hZ2 : Z ^ 2 ≠ 0 := pow_ne_zero' hZ 2
  have e1 : (x * Z) ^ 2 = x ^ 2 * Z ^ 2 := by grind
  have e2 : (l * Z) ^ 2 = l ^ 2 * Z ^ 2 := by grind
  simp only [frobenius, e1, e2, toAffine_rep _ _ _ hZ2, toAffine_rep x l Z hZ, Prod.mk.injEq,
    true_and]
  grind

/-! ## Doubling-and-addition (Theorem 3) -/

/-- Doubling preserves the curve (affine, generic branch `x ≠ 0`). -/
theorem affineDbl_onCurve (a b x l : K) (hx : x ≠ 0) (c : OnCurve a b (x, x * (l + x))) :
    OnCurve a b (affineDbl a (x, x * (l + x))) := by
  have hlam : x + x * (l + x) / x = l := by grind
  simp only [OnCurve] at c
  have c' : (l ^ 2 + l + a) * x ^ 2 = x ^ 4 + b := by grind
  simp only [affineDbl, hlam, OnCurve]
  grind

/-- **Theorem 3 doubling-and-addition is correct**, generic case:
`to_affine (dbl_add Q P) = affine_add (affine_dbl (to_affine Q)) P` when
`T ≠ 0` (2Q has `x ≠ 0`), `B ≠ 0` (`x_{2Q} ≠ x_P`) and `A ≠ 0` (the code
raises otherwise). -/
theorem dbl_add_correct (a b XQ LQ ZQ xP lP : K)
    (hZQ : ZQ ≠ 0) (hXQ : XQ ≠ 0) (hxP : xP ≠ 0)
    (cQ : OnCurveProj a b (XQ, LQ, ZQ)) (cP : OnCurve a b (fromLambdaAffine (xP, lP)))
    (hT : LQ ^ 2 + LQ * ZQ + a * ZQ ^ 2 ≠ 0)
    (hB : xP * ZQ ^ 2 + (LQ ^ 2 + LQ * ZQ + a * ZQ ^ 2) ≠ 0)
    (hA : XQ ^ 2 * ZQ ^ 2 + (LQ ^ 2 + LQ * ZQ + a * ZQ ^ 2) *
        (LQ ^ 2 + (a + 1 + lP) * ZQ ^ 2) ≠ 0) :
    (dblAdd a (XQ, LQ, ZQ) (xP, lP)).2.2 ≠ 0 ∧
    toAffine (dblAdd a (XQ, LQ, ZQ) (xP, lP)) =
      affineAdd a (affineDbl a (toAffine (XQ, LQ, ZQ))) (fromLambdaAffine (xP, lP)) := by
  have aQ := (curve_equation_iff a b XQ LQ ZQ hZQ hXQ).1 cQ
  obtain ⟨x, rfl⟩ := exists_rep XQ ZQ hZQ
  obtain ⟨l, rfl⟩ := exists_rep LQ ZQ hZQ
  rw [toAffine_rep x l ZQ hZQ] at aQ ⊢
  have hx : x ≠ 0 := ne_zero_of_mul_ne_zero_left x ZQ hXQ
  -- R = 2Q, affine
  have aR := affineDbl_onCurve a b x l hx aQ
  have hlam : x + x * (l + x) / x = l := by grind
  generalize hR : affineDbl a (x, x * (l + x)) = R at aR ⊢
  obtain ⟨xR, yR⟩ := R
  have hxR : xR = l ^ 2 + l + a := by
    simp only [affineDbl, hlam, Prod.mk.injEq] at hR; exact hR.1.symm
  have hyR : yR = x ^ 2 + l * xR + xR := by
    simp only [affineDbl, hlam, Prod.mk.injEq] at hR; rw [← hR.2, hR.1]
  have hZ2 : ZQ ^ 2 ≠ 0 := pow_ne_zero' hZQ 2
  have hTe : (l * ZQ) ^ 2 + l * ZQ * ZQ + a * ZQ ^ 2 = xR * ZQ ^ 2 := by rw [hxR]; grind
  have hxRne : xR ≠ 0 := by
    intro h; apply hT; rw [hTe, h]; grind
  -- λ of R
  generalize hlR : xR + yR / xR = lR
  have hyR' : yR = xR * (lR + xR) := by rw [← hlR]; grind
  rw [hyR'] at aR
  simp only [fromLambdaAffine] at cP ⊢
  rw [hyR']
  -- A, B, T in affine terms
  have hD : xP + xR ≠ 0 := by
    intro h; apply hB; rw [hTe]
    have : xR = xP := by grind
    rw [this]; grind
  have hAe : (x * ZQ) ^ 2 * ZQ ^ 2 + xR * ZQ ^ 2 * ((l * ZQ) ^ 2 + (a + 1 + lP) * ZQ ^ 2)
      = xR * (lP + lR) * (ZQ ^ 2) ^ 2 := by
    have e1 : lR * xR = xR ^ 2 + yR := by rw [← hlR]; grind
    rw [hyR] at e1
    have e2 : xR * (lP + lR) = xR * lP + (xR ^ 2 + (x ^ 2 + l * xR + xR)) := by grind
    rw [e2, hxR]; grind
  rw [hTe] at hA
  rw [hAe] at hA
  have hl : lP + lR ≠ 0 := by intro h; apply hA; rw [h]; grind
  -- the affine addition P + R, in the symmetric form
  rw [affineAdd_comm a _ _ (by simp only; intro h; apply hD; grind)]
  generalize hs : (xP * (lP + xP) + xR * (lR + xR)) / (xP + xR) = s
  have hs' : s * (xP + xR) = xP * (lP + xP) + xR * (lR + xR) := by rw [← hs]; grind
  have F1 := affine_add_x a b xP lP xR lR s cP aR hs'
  simp only [affineAdd, hs]
  generalize hx3 : s ^ 2 + s + xP + xR + a = x3
  rw [hx3] at F1
  generalize hy3 : s * (xP + x3) + x3 + xP * (lP + xP) = y3
  have Fy : y3 * (xP + xR) = (xP * (lP + xP) + xR * (lR + xR)) * (xP + x3)
      + (x3 + xP * (lP + xP)) * (xP + xR) := by
    rw [← hy3]; grind
  have hx3ne : x3 ≠ 0 := by
    intro h; rw [h] at F1
    exact mul_ne_zero' (mul_ne_zero' hxP hxRne) hl (by grind)
  -- the projective output, normalised
  simp only [dblAdd]
  rw [hTe, hAe]
  have W := pow_ne_zero' hZ2 5
  have eZ : xR * (lP + lR) * (ZQ ^ 2) ^ 2 * (xP * ZQ ^ 2 + xR * ZQ ^ 2) ^ 2 * ZQ ^ 2
      = xR * ((lP + lR) * (xP + xR) ^ 2 * (ZQ ^ 2) ^ 5) := by grind
  have eX : xP * ZQ ^ 2 * (xR * (lP + lR) * (ZQ ^ 2) ^ 2) ^ 2
      = xR * ((lP + lR) ^ 2 * (xP * xR) * (ZQ ^ 2) ^ 5) := by grind
  have eL : xR * ZQ ^ 2 * (xR * (lP + lR) * (ZQ ^ 2) ^ 2 + (xP * ZQ ^ 2 + xR * ZQ ^ 2) ^ 2) ^ 2
      + (lP + 1) * (xR * (lP + lR) * (ZQ ^ 2) ^ 2 * (xP * ZQ ^ 2 + xR * ZQ ^ 2) ^ 2 * ZQ ^ 2)
      = xR * ((((lP + lR) * xR + (xP + xR) ^ 2) ^ 2 + (lP + lR) * (lP + 1) * (xP + xR) ^ 2)
        * (ZQ ^ 2) ^ 5) := by grind
  rw [eL, eZ, eX]
  have hZout : xR * ((lP + lR) * (xP + xR) ^ 2 * (ZQ ^ 2) ^ 5) ≠ 0 :=
    mul_ne_zero' hxRne (mul_ne_zero' (mul_ne_zero' hl (pow_ne_zero' hD 2)) W)
  refine ⟨hZout, ?_⟩
  have hlam3 := add_lambda_identity xP lP xR lR x3 y3 F1 Fy
  have hx' := add_x_identity xP lP xR lR x3 ((ZQ ^ 2) ^ 5) F1
  apply toAffine_of_rep _ _ _ _ _ hZout hx3ne
  · rw [hx']; grind
  · have : xR * ((((lP + lR) * xR + (xP + xR) ^ 2) ^ 2 + (lP + lR) * (lP + 1) * (xP + xR) ^ 2)
        * (ZQ ^ 2) ^ 5) * x3
        = ((((lP + lR) * xR + (xP + xR) ^ 2) ^ 2 + (lP + lR) * (lP + 1) * (xP + xR) ^ 2) * x3)
          * (xR * (ZQ ^ 2) ^ 5) := by grind
    rw [this, hlam3]; grind

end CryptoResearch.Endosweep.LambdaCoordinates

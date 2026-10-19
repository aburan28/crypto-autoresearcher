import CryptoResearch.Endosweep.LambdaCoordinates
import CryptoResearch.Endosweep.BinaryGLS
import CryptoResearch.Endosweep.XOnlyConjugate
import CryptoResearch.Endosweep.Pippenger
namespace R2

inductive GF4 | z | o | u | v   -- 0, 1, u, u+1
  deriving DecidableEq, Repr

namespace GF4

def add : GF4 → GF4 → GF4
  | z, x => x | x, z => x
  | o, o => z | o, u => v | o, v => u
  | u, o => v | u, u => z | u, v => o
  | v, o => u | v, u => o | v, v => z

def mul : GF4 → GF4 → GF4
  | z, _ => z | _, z => z
  | o, x => x | x, o => x
  | u, u => v | u, v => o
  | v, u => o | v, v => u

def inv : GF4 → GF4
  | z => z | o => o | u => v | v => u

def natc (n : Nat) : GF4 := if n % 2 = 0 then z else o
def intc (i : Int) : GF4 := if i % 2 = 0 then z else o

def npow (a : GF4) : Nat → GF4
  | 0 => o
  | n + 1 => mul (npow a n) a

def zpow (a : GF4) : Int → GF4
  | Int.ofNat n => npow a n
  | Int.negSucc n => inv (npow a (n + 1))

instance : Add GF4 := ⟨add⟩
instance : Mul GF4 := ⟨mul⟩
instance : Neg GF4 := ⟨id⟩
instance : Sub GF4 := ⟨add⟩
instance : Inv GF4 := ⟨inv⟩
instance : Div GF4 := ⟨fun a b => mul a (inv b)⟩
instance : NatCast GF4 := ⟨natc⟩
instance : IntCast GF4 := ⟨intc⟩
instance (n : Nat) : OfNat GF4 n := ⟨natc n⟩
instance : SMul Nat GF4 := ⟨fun n a => mul (natc n) a⟩
instance : SMul Int GF4 := ⟨fun i a => mul (intc i) a⟩
instance : HPow GF4 Nat GF4 := ⟨npow⟩
instance : HPow GF4 Int GF4 := ⟨zpow⟩

theorem natc_cases (n : Nat) : natc n = z ∧ n % 2 = 0 ∨ natc n = o ∧ n % 2 = 1 := by
  unfold natc; by_cases h : n % 2 = 0
  · left; simp [h]
  · right; simp [h]; omega

theorem intc_natCast (n : Nat) : intc (n : Int) = natc n := by
  unfold intc natc
  by_cases h : n % 2 = 0
  · have : (n : Int) % 2 = 0 := by omega
    simp [h, this]
  · have : ¬ (n : Int) % 2 = 0 := by omega
    simp [h, this]

theorem intc_neg (i : Int) : intc (-i) = intc i := by
  unfold intc
  by_cases h : i % 2 = 0
  · have : (-i) % 2 = 0 := by omega
    simp [h, this]
  · have : ¬ (-i) % 2 = 0 := by omega
    simp [h, this]

instance : Lean.Grind.Field GF4 where
  add_zero := by intro a; cases a <;> rfl
  add_comm := by intro a b; cases a <;> cases b <;> rfl
  add_assoc := by intro a b c; cases a <;> cases b <;> cases c <;> rfl
  mul_assoc := by intro a b c; cases a <;> cases b <;> cases c <;> rfl
  mul_one := by intro a; cases a <;> rfl
  one_mul := by intro a; cases a <;> rfl
  left_distrib := by intro a b c; cases a <;> cases b <;> cases c <;> rfl
  right_distrib := by intro a b c; cases a <;> cases b <;> cases c <;> rfl
  zero_mul := by intro a; cases a <;> rfl
  mul_zero := by intro a; cases a <;> rfl
  pow_zero := by intro a; rfl
  pow_succ := by intro a n; rfl
  ofNat_succ := by
    intro n
    show natc (n + 1) = add (natc n) (natc 1)
    rcases natc_cases n with ⟨h1, h2⟩ | ⟨h1, h2⟩ <;>
    rcases natc_cases (n + 1) with ⟨h3, h4⟩ | ⟨h3, h4⟩ <;>
    first | omega | (rw [h1, h3]; rfl)
  ofNat_eq_natCast := by intro n; rfl
  nsmul_eq_natCast_mul := by intro n a; rfl
  neg_add_cancel := by intro a; cases a <;> rfl
  sub_eq_add_neg := by intro a b; cases a <;> cases b <;> rfl
  neg_zsmul := by
    intro i a
    show mul (intc (-i)) a = mul (intc i) a
    rw [intc_neg]
  zsmul_natCast_eq_nsmul := by
    intro n a
    show mul (intc (n : Int)) a = mul (natc n) a
    rw [intc_natCast]
  intCast_ofNat := by
    intro n
    show intc (n : Int) = natc n
    exact intc_natCast n
  intCast_neg := by
    intro i
    show intc (-i) = intc i
    exact intc_neg i
  mul_comm := by intro a b; cases a <;> cases b <;> rfl
  div_eq_mul_inv := by intro a b; rfl
  zero_ne_one := by decide
  inv_zero := rfl
  mul_inv_cancel := by intro a h; cases a <;> first | rfl | exact absurd rfl h
  zpow_zero := by intro a; rfl
  zpow_succ := by intro a n; rfl
  zpow_neg := by
    intro a i
    cases i with
    | ofNat n =>
      cases n with
      | zero => cases a <;> rfl
      | succ k => rfl
    | negSucc k =>
      show npow a (k + 1) = inv (inv (npow a (k + 1)))
      generalize npow a (k + 1) = w
      cases w <;> rfl

instance : Lean.Grind.IsCharP GF4 2 where
  ofNat_ext_iff := by
    intro x y
    show natc x = natc y ↔ x % 2 = y % 2
    rcases natc_cases x with ⟨h1, h2⟩ | ⟨h1, h2⟩ <;>
    rcases natc_cases y with ⟨h3, h4⟩ | ⟨h3, h4⟩ <;>
    rw [h1, h3] <;> simp <;> omega

end GF4
end R2

/-! # Satisfiability witnesses (R2). GF4 encoding: z = 0, o = 1, u, v = u + 1. -/
namespace R2.W
open R2 R2.GF4
open CryptoResearch.Endosweep

section Lambda
open CryptoResearch.Endosweep.LambdaCoordinates

-- curve E : y^2 + xy = x^3 + 0*x^2 + 1 over GF(4)  (a = 0, b = 1, nonsingular)
-- Q = (X, L, Z) = (1, 1, u)  ->  x = u+1, λ = u+1 ; P = (1, 0, 1) -> x = 1, λ = 0 ; P' = (u, u) λ-affine
theorem w_curve_eq : OnCurveProj (K := GF4) z o (o, o, u) := by unfold OnCurveProj; decide
theorem w_curve_eq_P : OnCurveProj (K := GF4) z o (o, z, o) := by unfold OnCurveProj; decide
theorem w_P'_on : OnCurve (K := GF4) z o (fromLambdaAffine (u, u)) := by
  unfold OnCurve fromLambdaAffine; decide
theorem w_P1_on : OnCurve (K := GF4) z o (fromLambdaAffine (o, z)) := by
  unfold OnCurve fromLambdaAffine; decide

-- curve_equation_iff: hypotheses X, Z ≠ 0
example := curve_equation_iff (K := GF4) z o o o u (by decide) (by decide)

-- dbl_main_correct: X, Z ≠ 0, T ≠ 0 (and the point is on the curve, although not required)
example := dbl_main_correct (K := GF4) z o o u (by decide) (by decide) (by decide)

-- dbl_alt_eq_dbl_main: on the curve
example := dbl_alt_eq_dbl_main (K := GF4) z o o o u w_curve_eq
example := dbl_alt_correct (K := GF4) z o o o u (by decide) (by decide) w_curve_eq (by decide)

-- add_correct: P = (1,0,1), Q = (1,1,u): x_P = 1 ≠ x_Q = u+1, X3 ≠ 0
example := add_correct (K := GF4) z o o z o o o u (by decide) (by decide) (by decide) (by decide)
  w_curve_eq_P w_curve_eq (by decide) (by decide)

-- madd_correct: Q = (1,1,u), P = (1, 0) λ-affine
example := madd_correct (K := GF4) z o o o u o z (by decide) (by decide) (by decide)
  w_curve_eq w_P1_on (by decide) (by decide)

-- dbl_add_correct: Q = (1,1,u), P = (u, u) λ-affine; T, B, A ≠ 0
example := dbl_add_correct (K := GF4) z o o o u u u (by decide) (by decide) (by decide)
  w_curve_eq w_P'_on (by decide) (by decide) (by decide)

-- sanity: the outputs are concrete, nondegenerate points
#eval (dblMain (K := GF4) z (o, o, u), toAffine (K := GF4) (dblMain z (o, o, u)), affineDbl (K := GF4) z (toAffine (o, o, u)))
#eval (toAffine (K := GF4) (add (o, z, o) (o, o, u)), affineAdd (K := GF4) z (toAffine (o, z, o)) (toAffine (o, o, u)))
#eval (toAffine (K := GF4) (dblAdd z (o, o, u) (u, u)), affineAdd (K := GF4) z (affineDbl z (toAffine (o, o, u))) (fromLambdaAffine (u, u)))
end Lambda

section GLS
open CryptoResearch.Endosweep.BinaryGLS

/-- σ = the q-power Frobenius of F_{q^2} = GF(4) with q = 2 (m = 1, odd). -/
def frob (x : GF4) : GF4 := x * x

theorem frob_inv : Involution frob where
  map_add := by intro p q; cases p <;> cases q <;> rfl
  map_mul := by intro p q; cases p <;> cases q <;> rfl
  map_one := rfl
  invol := by intro p; cases p <;> rfl

theorem hu : frob u = u + 1 := by decide
theorem hu2 : (u : GF4) ^ 2 + u + 1 = 0 := by decide
theorem hb : frob o = o := by decide

example := psi_psi frob_inv hu (u, o)
example := psi_onCurve frob_inv hu hu2 hb (z, o) (by unfold OnCurve; decide)
example := psi_add frob_inv hu hu2 (o, z) (u, o) (by decide)
example := psi_dbl frob_inv hu hu2 (o, u) (by decide)

-- twist conjugation: τ = Frobenius of GF(4), s = u: s + τ s = u + (u+1) = 1 (so `u` := 1 in the statement)
example := psi_eq_conj_by_twist (L := GF4) frob frob_inv.map_add frob_inv.map_mul u o (by decide) (o, u)
example := psi_lambda_affine (u := u) frob_inv (o, u) (by decide)
example := psi_lambda_proj (u := u) frob_inv o u v (by decide)
example := twist_iso_onCurve (L := GF4) z o u (z, o) (by unfold OnCurve; decide)
-- psi really is (σx, σy + uσx) with σ = Frobenius and u the root of u^2+u+1: concrete values
#eval (psi frob u (u, o), psi frob u (psi frob u (u, o)), affineNeg (u, o))
end GLS

section Pip
open CryptoResearch.Endosweep.Pippenger
#eval (windows 256 13, windows 128 13, windows 256 16, windows 128 16, windows 255 16, windows 127 16, windows 256 0)
example := glv_wins_iff 10 7 2 1 (by decide)
example := ideal_glv_wins_iff 256 13 1024 6 6 7 6 8192 1 (by decide) (by decide)
example := window_slots 128 13 1000 (by decide)
end Pip

section XOnly
open CryptoResearch.Endosweep.XOnlyConjugate
-- G = Int, x = natAbs (sign-blind), β = (·*3), β̄ = (·*(-2)): β + β̄ = 1
example := xonly_difference_eq_conj (G := Int) (fun P => 3 * P) (fun P => -2 * P) Int.natAbs
  (fun Q => Int.natAbs_neg Q) 5 (by decide)
example := conj_eigenvalue (G := Int) (fun P => 3 * P) (fun P => -2 * P) 3 5 (by decide) (by decide)
example := XOnlyConjugate.eigen_conj_mod 7 3 (-1) (by decide)
example : ∃ x : XOnlyConjugate.QuadOrder (-619), XOnlyConjugate.QuadOrder.trace x = 1 :=
  (XOnlyConjugate.QuadOrder.trace_one_exists_iff_D_odd).2 (by decide)
example := (XOnlyConjugate.QuadOrder.no_trace_pm_one_of_D_even (D := -8) (by decide) ⟨3, 1⟩)
end XOnly
end R2.W

/- R2 scratch: GF(4) = F_2[u]/(u^2+u+1) as a core `Lean.Grind.Field` of characteristic 2,
   used to instantiate the hypotheses of the Endosweep λ-coordinate and GLS theorems. -/
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

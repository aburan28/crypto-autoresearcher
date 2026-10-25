/-!
# Finite steps behind the `n = 7` cover-genus derivations (EXP-PEXT-212d5c, H-PEXT-d536a1)

No Mathlib, no `sorry`, no `native_decide`, no custom axioms. Toolchain as the sibling
`research/ghs_cover_census_n5_20261013/lean` (v4.34.1). What is formalized here:

* `Orbit.*`: the return-set lemmas of the sibling file, unchanged, plus
  `Orbit.period_three_or_twentyone` (a root of an irreducible cubic over `K = F_{q^7}` has
  Frobenius orbit 3 or 21) and `Orbit.period_two_or_fourteen` (a conjugate pair: orbit 2 or 14).
  Used in Lemma O7 and in the orbit step of Lemma E7.
* `Rot7.span_sizes`: in `F_2^7` with the cyclic shift, the span of the seven rotations of any
  vector has 1, 2, 8, 16, 64 or 128 elements (dimension 0, 1, 3, 4, 6, 7: Lemma M7 for one free
  7-orbit), checked by `decide` over all 128 vectors.
* `Rot7.weight4_dim3`: exactly 14 weight-4 vectors have a 3-dimensional span, and they are the
  14 nonzero words of the two `[7,3,4]` cyclic codes (`{0,2,3,4}` and `{0,1,2,4}` with their
  rotations); `Rot7.weight4_dim3_or_6`: every other weight-4 vector spans dimension 6.
* `Spectrum.*`: the genus arithmetic `2^(m-2)(r-4)+1` over the allowed `(m, r)` lists of
  `spectrum.py 7` per 2-torsion type: split floor 7 only at `(3, 7)`; `E(K)[2] = Z/2` floor 161;
  odd order genera `{193, 577, 769}`.

Not formalized: Lang's theorem; Lemma M7 for an arbitrary sigma-set (module decomposition over
orbits); the placement enumeration of `spectrum.py` (checked by the census, not by Lean); the
simple transitivity in O7; the cross-ratio invariant of Proposition T; the genus formula.
-/

namespace Orbit

variable {α : Type} (f : α → α)

def iter : Nat → α → α
  | 0, x => x
  | n + 1, x => iter n (f x)

theorem iter_add (a b : Nat) (x : α) : iter f (a + b) x = iter f b (iter f a x) := by
  induction a generalizing x with
  | zero => simp [iter]
  | succ a ih => rw [Nat.succ_add]; exact ih (f x)

/-- `x` returns after `a` steps. -/
def Ret (a : Nat) (x : α) : Prop := iter f a x = x

theorem ret_add {a b : Nat} {x : α} (ha : Ret f a x) (hb : Ret f b x) : Ret f (a + b) x := by
  unfold Ret at *; rw [iter_add, ha, hb]

theorem ret_sub {a b : Nat} {x : α} (ha : Ret f a x) (hab : Ret f (a + b) x) : Ret f b x := by
  unfold Ret at *; rw [iter_add, ha] at hab; exact hab

theorem ret_mul {a : Nat} {x : α} (ha : Ret f a x) : ∀ k, Ret f (k * a) x
  | 0 => by simp [Ret, iter]
  | k + 1 => by rw [Nat.succ_mul]; exact ret_add f (ret_mul ha k) ha

theorem ret_mod {a b : Nat} {x : α} (ha : Ret f a x) (hb : Ret f b x) : Ret f (b % a) x := by
  have h := Nat.div_add_mod b a
  have hm : Ret f (a * (b / a)) x := by rw [Nat.mul_comm]; exact ret_mul f ha _
  exact ret_sub f hm (by rw [h]; exact hb)

/-- Returns are closed under `gcd`. -/
theorem ret_gcd {x : α} : ∀ a b, Ret f a x → Ret f b x → Ret f (Nat.gcd a b) x := by
  intro a
  induction a using Nat.strongRecOn with
  | _ a ih =>
    intro b ha hb
    cases a with
    | zero => rw [Nat.gcd_zero_left]; exact hb
    | succ a =>
      rw [Nat.gcd_rec]
      exact ih (b % (a + 1)) (Nat.mod_lt _ (Nat.succ_pos a)) (a + 1) (ret_mod f ha hb) ha

/-- Lemma O7, orbit step: if `τ²¹ θ = θ` and `τ⁷ θ ≠ θ` (θ a root of an irreducible cubic over
`F_{q^7}`, τ the `q`-Frobenius), every return before 21 steps is a multiple of 3 and `θ` is not
fixed: its orbit has 3 or 21 points. -/
theorem period_three_or_twentyone {x : α} (h21 : Ret f 21 x) (h7 : ¬ Ret f 7 x) :
    ¬ Ret f 1 x ∧ ∀ k, 0 < k → k < 21 → Ret f k x → k % 3 = 0 := by
  have one : ¬ Ret f 1 x := fun h => h7 (ret_mul f h 7)
  refine ⟨one, ?_⟩
  intro k hk0 hk21 hk
  have hg := ret_gcd f k 21 hk h21
  have hkcases : k = 1 ∨ k = 2 ∨ k = 3 ∨ k = 4 ∨ k = 5 ∨ k = 6 ∨ k = 7 ∨
      k = 8 ∨ k = 9 ∨ k = 10 ∨ k = 11 ∨ k = 12 ∨ k = 13 ∨ k = 14 ∨
      k = 15 ∨ k = 16 ∨ k = 17 ∨ k = 18 ∨ k = 19 ∨ k = 20 := by omega
  rcases hkcases with hk1 | hk2 | hk3 | hk4 | hk5 | hk6 | hk7 | hk8 | hk9 | hk10 |
    hk11 | hk12 | hk13 | hk14 | hk15 | hk16 | hk17 | hk18 | hk19 | hk20
  · subst k
    exact absurd hg one
  · subst k
    exact absurd hg one
  · subst k
    rfl
  · subst k
    exact absurd hg one
  · subst k
    exact absurd hg one
  · subst k
    rfl
  · subst k
    exact absurd hg h7
  · subst k
    exact absurd hg one
  · subst k
    rfl
  · subst k
    exact absurd hg one
  · subst k
    exact absurd hg one
  · subst k
    rfl
  · subst k
    exact absurd hg one
  · subst k
    exact absurd hg h7
  · subst k
    rfl
  · subst k
    exact absurd hg one
  · subst k
    exact absurd hg one
  · subst k
    rfl
  · subst k
    exact absurd hg one
  · subst k
    exact absurd hg one

/-- Lemma E7, orbit step for a conjugate pair: if `τ¹⁴ β = β` and `τ⁷ β ≠ β`, every return
before 14 steps is even and `β` is not fixed: its orbit has 2 or 14 points. -/
theorem period_two_or_fourteen {x : α} (h14 : Ret f 14 x) (h7 : ¬ Ret f 7 x) :
    ¬ Ret f 1 x ∧ ∀ k, 0 < k → k < 14 → Ret f k x → k % 2 = 0 := by
  have one : ¬ Ret f 1 x := fun h => h7 (ret_mul f h 7)
  refine ⟨one, ?_⟩
  intro k hk0 hk14 hk
  have hg := ret_gcd f k 14 hk h14
  match k, hk0, hk14 with
  | 1, _, _ => exact absurd hk one
  | 2, _, _ => rfl
  | 3, _, _ => exact absurd hg one
  | 4, _, _ => rfl
  | 5, _, _ => exact absurd hg one
  | 6, _, _ => rfl
  | 7, _, _ => exact absurd hk h7
  | 8, _, _ => rfl
  | 9, _, _ => exact absurd hg one
  | 10, _, _ => rfl
  | 11, _, _ => exact absurd hg one
  | 12, _, _ => rfl
  | 13, _, _ => exact absurd hg one

end Orbit

namespace Rot7

/-- cyclic shift on 7-bit vectors -/
def rot (v : Nat) : Nat := ((v <<< 1) ||| (v >>> 6)) &&& 127

def iter : Nat → Nat → Nat
  | 0, v => v
  | k + 1, v => iter k (rot v)

def rots (v : Nat) : List Nat := (List.range 7).map (fun k => iter k v)

/-- adjoin `g` to a subspace given as the list of its elements -/
def adjoin (S : List Nat) (g : Nat) : List Nat :=
  if S.contains g then S else S ++ S.map (fun s => s ^^^ g)

/-- elements of the `F_2`-span of the seven rotations of `v` -/
def span (v : Nat) : List Nat := (rots v).foldl adjoin [0]

def spanSize (v : Nat) : Nat := (span v).length

def weight (v : Nat) : Nat := (List.range 7).foldl (fun acc i => acc + (v >>> i) % 2) 0

set_option maxRecDepth 8192 in
theorem span_sizes : ∀ v, v < 128 →
    spanSize v = 1 ∨ spanSize v = 2 ∨ spanSize v = 8 ∨ spanSize v = 16 ∨
    spanSize v = 64 ∨ spanSize v = 128 := by
  decide

/-- the 14 weight-4 vectors with a 3-dimensional span: rotations of 29 = {0,2,3,4} and 23 = {0,1,2,4} -/
theorem weight4_dim3 :
    (List.range 128).filter (fun v => weight v == 4 && spanSize v == 8) =
      [23, 29, 39, 46, 57, 58, 75, 78, 83, 92, 101, 105, 114, 116] := by
  decide

set_option maxRecDepth 8192 in
theorem weight4_dim3_or_6 : ∀ v, v < 128 → weight v = 4 → spanSize v = 8 ∨ spanSize v = 64 := by
  decide

end Rot7

namespace Spectrum

def genus (m r : Nat) : Nat := 2 ^ (m - 2) * (r - 4) + 1

/-- allowed (m, r) with m >= 2 per type, as printed by `spectrum.py 7` -/
def split : List (Nat × Nat) :=
  [(3, 7), (4, 8), (6, 7), (6, 14), (7, 8), (7, 9), (7, 10), (7, 14), (7, 15), (7, 16), (7, 21),
   (7, 22), (7, 28)]
def z2 : List (Nat × Nat) := [(7, 9), (7, 10), (7, 16), (7, 21), (7, 22), (7, 28)]
def odd : List (Nat × Nat) := [(7, 10), (7, 22), (7, 28)]

theorem split_floor : split.all (fun p => genus p.1 p.2 ≥ 7 && (genus p.1 p.2 == 7) == (p == (3, 7))) = true := by
  decide

theorem z2_floor : z2.all (fun p => genus p.1 p.2 ≥ 161) = true ∧ genus 7 9 = 161 ∧ genus 7 10 = 193 := by
  decide

theorem odd_support : odd.map (fun p => genus p.1 p.2) = [193, 577, 769] := by
  decide

end Spectrum

#print axioms Orbit.period_three_or_twentyone
#print axioms Orbit.period_two_or_fourteen
#print axioms Rot7.span_sizes
#print axioms Rot7.weight4_dim3
#print axioms Rot7.weight4_dim3_or_6
#print axioms Spectrum.split_floor
#print axioms Spectrum.z2_floor
#print axioms Spectrum.odd_support

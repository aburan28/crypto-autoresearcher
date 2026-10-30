import Mathlib.Data.List.Sublists
import Mathlib.Data.List.Count
import Mathlib.Tactic.IntervalCases

/-!
# Finite `F_2` counterexample certificate for Nagao 2015/984 Lemma 4 (inside form)

Source: `knowledge/findings/KN-FIND-936151.md`, certificate
`tools/lemma4_inside_form.py` (witness B) and
`coordination/goals/GOAL-SEMBIN-fcb7a2/batches/BATCH-e0a0c1/read-nagao-2013-549/recheck.py`
(witness A).

## The reading that is formalized (and no other)

* Ground field `F_2`, polynomial ring `F_2[X_1..X_n]` (NOT the Boolean quotient):
  the field equations `X_i^2 + X_i` are *generators* of the true system.
* A polynomial is a duplicate-free list of exponent vectors (a set of monomials).
* **Equality reading** of condition (1) of Definitions 5 and 6: a fall at degree
  `D` for a system `S` is a cofactor tuple `(g_s)` with
    (1) every product `g_s * s` of degree `<= D` and at least one of degree exactly `D`,
    (2) the sum `sum_s g_s * s` nonzero,
    (3) that sum of degree `< D`.
  Under the literal `>=` printed in 2015/984 the lemma is true and empty
  (finding, section 3); that reading is NOT formalized and nothing here says
  anything about it.
* True first fall degree `d_F(S)`: least `D >= 1` with a fall over unreduced
  products. Fake first fall degree `d'_F(S)`: the same with every product and
  the sum taken modulo `S_fe` (each exponent clamped to `<= 1`, over `F_2`),
  cofactors multilinear.
* **Inside form** (the one the finding refutes): both quantities are taken of the
  same system `S = F ++ S_fe`. `Lemma4Inside S` is the statement `d_F(S) <= d'_F(S)`.

## What is proved

For each of two systems `S` (witness A in `F_2[X,Y]`, non-multilinear; witness B
in `F_2[X_1,X_2,X_3]`, multilinear) the exact negation `¬ Lemma4Inside S`, by
exhibiting `d_F = 3` and `d'_F = 2` with `decide +kernel` (no `native_decide`).

## What is NOT proved (each is a `proof_map` prerequisite of the target spec)

* That this list-of-exponent-vectors model is Nagao's Definitions 5 and 6
  (the transcription step); in particular the choice of the equality reading.
* Cofactor domain: cofactors range over polynomials whose monomials have degree
  `<= D` (multilinear on the fake side). Over a domain, `deg (g s) = deg g + deg s`
  so any cofactor with product degree `<= D` has degree `<= D`; this
  leading-form argument is not a Lean theorem here. It matches the Python
  certificate, which enumerates the same domain.
* Dropping the generators that reduce to zero mod `S_fe` on the fake side
  (inertness, finding section 2). Only `reduce_fe_zero_*` below is checked.
* Anything about Nagao's Proposition 5, Semaev's Assumption 1, `p >= 3`,
  `N > 3` variables, the `>=` reading, or any elliptic curve.
-/

namespace CryptoResearch.Nagao.Lemma4Witness

/-- Exponent vector. -/
abbrev Mono := List Nat
/-- A polynomial over `F_2`: a set of monomials, as a list. -/
abbrev Poly := List Mono

/-- Keep exactly the monomials occurring an odd number of times (`F_2` coefficients). -/
def norm (l : List Mono) : Poly := (l.filter fun m => l.count m % 2 == 1).dedup

def monoMul (a b : Mono) : Mono := List.zipWith (· + ·) a b

def mul (p q : Poly) : Poly := norm (p.flatMap fun a => q.map (monoMul a))

/-- Reduction modulo `S_fe`: clamp every exponent to `<= 1` (`X^2 = X` over `F_2`). -/
def reduceFe (p : Poly) : Poly := norm (p.map fun m => m.map (min 1))

def prep (fake : Bool) (p : Poly) : Poly := if fake then reduceFe p else p

/-- All exponent vectors of length `n`, each exponent `<= e`, total degree `<= D`. -/
def monsAux : Nat → Nat → Nat → List Mono
  | 0, _, _ => [[]]
  | n + 1, e, D =>
      (List.range (min e D + 1)).flatMap fun a => (monsAux n e (D - a)).map (a :: ·)

def mons (n D : Nat) (fake : Bool) : List Mono := monsAux n (if fake then 1 else D) D

def DegLe (p : Poly) (D : Nat) : Prop := ∀ m ∈ p, m.sum ≤ D

instance (p : Poly) (D : Nat) : Decidable (DegLe p D) := by unfold DegLe; infer_instance

/-- Cofactor `g` is admissible for generator `s` at degree `D`. -/
def Adm (n D : Nat) (fake : Bool) (g s : Poly) : Prop :=
  g.Sublist (mons n D fake) ∧ DegLe (prep fake (mul g s)) D

instance (n D fake g s) : Decidable (Adm n D fake g s) := by unfold Adm; infer_instance

/-- The equality-reading conditions (1)-(3) on a cofactor tuple. -/
def Cond (fake : Bool) (D : Nat) (gs S : List Poly) : Prop :=
  let P := List.zipWith (fun g s => prep fake (mul g s)) gs S
  let total := prep fake (norm P.flatten)
  (∀ p ∈ P, DegLe p D) ∧ (∃ p ∈ P, ∃ m ∈ p, m.sum = D) ∧
    total ≠ [] ∧ (∀ m ∈ total, m.sum < D)

/-- The generators seen by the fake quantity: reduce, drop those that become zero. -/
def gens (fake : Bool) (S : List Poly) : List Poly :=
  if fake then (S.map reduceFe).filter (· ≠ []) else S

/-- A fall at degree `D`. -/
def FallAt (n : Nat) (fake : Bool) (S : List Poly) (D : Nat) : Prop :=
  ∃ gs : List Poly, List.Forall₂ (Adm n D fake) gs (gens fake S) ∧ Cond fake D gs (gens fake S)

/-- `D` is the first fall degree (`d_F` if `fake = false`, `d'_F` if `true`). -/
def FirstFall (n : Nat) (fake : Bool) (S : List Poly) (D : Nat) : Prop :=
  FallAt n fake S D ∧ ∀ D', 1 ≤ D' → D' < D → ¬ FallAt n fake S D'

/-- Nagao 2015/984 Lemma 4, inside form, for one system. -/
def Lemma4Inside (n : Nat) (S : List Poly) : Prop :=
  ∀ d d', FirstFall n false S d → FirstFall n true S d' → d ≤ d'

/-- The field equations `X_i^2 + X_i` as generators. -/
def fieldEqs (n : Nat) : List Poly :=
  (List.range n).map fun i =>
    [(List.range n).map fun j => if j = i then 2 else 0,
     (List.range n).map fun j => if j = i then 1 else 0]

/-! ### Decision procedure: enumerate admissible cofactor tuples -/

def allowed (n D : Nat) (fake : Bool) (s : Poly) : List Poly :=
  ((mons n D fake).sublists).filter fun g => decide (DegLe (prep fake (mul g s)) D)

def tuples (n D : Nat) (fake : Bool) : List Poly → List (List Poly)
  | [] => [[]]
  | s :: S => (allowed n D fake s).flatMap fun g => (tuples n D fake S).map (g :: ·)

theorem mem_allowed {n D fake g s} : g ∈ allowed n D fake s ↔ Adm n D fake g s := by
  simp [allowed, Adm, List.mem_sublists]

theorem mem_tuples {n D fake} :
    ∀ {S gs}, gs ∈ tuples n D fake S ↔ List.Forall₂ (Adm n D fake) gs S
  | [], gs => by
      cases gs <;> simp [tuples]
  | s :: S, gs => by
      cases gs with
      | nil => simp [tuples]
      | cons g gs =>
          simp only [tuples, List.mem_flatMap, List.mem_map, List.cons.injEq,
            List.forall₂_cons, mem_allowed]
          constructor
          · rintro ⟨g', hg', gs', hgs', rfl, rfl⟩
            exact ⟨hg', mem_tuples.1 hgs'⟩
          · rintro ⟨hg, hgs⟩
            exact ⟨g, hg, gs, mem_tuples.2 hgs, rfl, rfl⟩

theorem fallAt_iff {n fake S D} :
    FallAt n fake S D ↔ ∃ gs ∈ tuples n D fake (gens fake S), Cond fake D gs (gens fake S) := by
  simp only [FallAt, mem_tuples]

instance (fake D gs S) : Decidable (Cond fake D gs S) := by unfold Cond; infer_instance

/-- Decidable form of "no fall at `D`". -/
def NoFallDec (n : Nat) (fake : Bool) (S : List Poly) (D : Nat) : Prop :=
  ¬ ∃ gs ∈ tuples n D fake (gens fake S), Cond fake D gs (gens fake S)

instance (n fake S D) : Decidable (NoFallDec n fake S D) := by unfold NoFallDec; infer_instance

theorem noFall {n fake S D} (h : NoFallDec n fake S D) : ¬ FallAt n fake S D :=
  fun hf => h (fallAt_iff.1 hf)

/-! ### Witness A: `F_2[X,Y]`, `f_1 = X^2 Y`, `f_2 = X Y + X` (not multilinear) -/

def fA₁ : Poly := [[2, 1]]
def fA₂ : Poly := [[1, 1], [1, 0]]
/-- The inside system `{f_1, f_2} ∪ S_fe`. -/
def SA : List Poly := [fA₁, fA₂] ++ fieldEqs 2

/-- Fake fall at 2: `g_1 = XY`, `g_2 = X`. -/
def gA_fake : List Poly := [[[1, 1]], [[1, 0]]]
/-- True fall at 3: `g_2 = X`, `g_{fe_1} = Y`, others `0`. -/
def gA_true : List Poly := [[], [[1, 0]], [[0, 1]], []]

theorem A_fake_fall2 : FallAt 2 true SA 2 :=
  ⟨gA_fake, by unfold gens SA fA₁ fA₂ fieldEqs gA_fake; decide +kernel,
    by unfold gens SA fA₁ fA₂ fieldEqs gA_fake; decide +kernel⟩

theorem A_fake_nofall1 : ¬ FallAt 2 true SA 1 :=
  noFall (by unfold NoFallDec gens SA fA₁ fA₂ fieldEqs; decide +kernel)

theorem A_true_fall3 : FallAt 2 false SA 3 :=
  ⟨gA_true, by unfold gens SA fA₁ fA₂ fieldEqs gA_true; decide +kernel,
    by unfold gens SA fA₁ fA₂ fieldEqs gA_true; decide +kernel⟩

theorem A_true_nofall1 : ¬ FallAt 2 false SA 1 :=
  noFall (by unfold NoFallDec gens SA fA₁ fA₂ fieldEqs; decide +kernel)

theorem A_true_nofall2 : ¬ FallAt 2 false SA 2 :=
  noFall (by unfold NoFallDec gens SA fA₁ fA₂ fieldEqs; decide +kernel)

theorem A_dF : FirstFall 2 false SA 3 := by
  refine ⟨A_true_fall3, fun D' h1 h2 => ?_⟩
  interval_cases D'
  · exact A_true_nofall1
  · exact A_true_nofall2

theorem A_dF' : FirstFall 2 true SA 2 := by
  refine ⟨A_fake_fall2, fun D' h1 h2 => ?_⟩
  interval_cases D'
  exact A_fake_nofall1

/-- **Nagao 2015/984 Lemma 4, inside form, is false at witness A** (`d_F = 3 > 2 = d'_F`). -/
theorem lemma4_inside_false_A : ¬ Lemma4Inside 2 SA := fun h => by
  have := h 3 2 A_dF A_dF'
  omega

/-! ### Witness B: `F_2[X_1,X_2,X_3]`, `f_1 = X_1X_2 + X_3`, `f_2 = X_1X_3 + X_2` -/

def fB₁ : Poly := [[1, 1, 0], [0, 0, 1]]
def fB₂ : Poly := [[1, 0, 1], [0, 1, 0]]
def SB : List Poly := [fB₁, fB₂] ++ fieldEqs 3

/-- (Cofactors are listed in the order of `mons`, which `Sublist` needs.)
Fake fall at 2: `g_1 = 1`, `g_2 = X_1 + 1`. -/
def gB_fake : List Poly := [[[0, 0, 0]], [[0, 0, 0], [1, 0, 0]]]
/-- True fall at 3: `1*f_1 + (X_1+1)*f_2 + X_3*(X_1^2+X_1)`. -/
def gB_true : List Poly := [[[0, 0, 0]], [[0, 0, 0], [1, 0, 0]], [[0, 0, 1]], [], []]

theorem B_fake_fall2 : FallAt 3 true SB 2 :=
  ⟨gB_fake, by unfold gens SB fB₁ fB₂ fieldEqs gB_fake; decide +kernel,
    by unfold gens SB fB₁ fB₂ fieldEqs gB_fake; decide +kernel⟩

theorem B_fake_nofall1 : ¬ FallAt 3 true SB 1 :=
  noFall (by unfold NoFallDec gens SB fB₁ fB₂ fieldEqs; decide +kernel)

theorem B_true_fall3 : FallAt 3 false SB 3 :=
  ⟨gB_true, by unfold gens SB fB₁ fB₂ fieldEqs gB_true; decide +kernel,
    by unfold gens SB fB₁ fB₂ fieldEqs gB_true; decide +kernel⟩

theorem B_true_nofall1 : ¬ FallAt 3 false SB 1 :=
  noFall (by unfold NoFallDec gens SB fB₁ fB₂ fieldEqs; decide +kernel)

theorem B_true_nofall2 : ¬ FallAt 3 false SB 2 :=
  noFall (by unfold NoFallDec gens SB fB₁ fB₂ fieldEqs; decide +kernel)

theorem B_dF : FirstFall 3 false SB 3 := by
  refine ⟨B_true_fall3, fun D' h1 h2 => ?_⟩
  interval_cases D'
  · exact B_true_nofall1
  · exact B_true_nofall2

theorem B_dF' : FirstFall 3 true SB 2 := by
  refine ⟨B_fake_fall2, fun D' h1 h2 => ?_⟩
  interval_cases D'
  exact B_fake_nofall1

/-- **Nagao 2015/984 Lemma 4, inside form, is false at witness B** (`d_F = 3 > 2 = d'_F`). -/
theorem lemma4_inside_false_B : ¬ Lemma4Inside 3 SB := fun h => by
  have := h 3 2 B_dF B_dF'
  omega

/-- Both witnesses at once: the universal statement over finite `F_2` systems is false. -/
theorem lemma4_inside_false :
    ¬ (∀ (n : Nat) (S : List Poly), Lemma4Inside n S) := fun h =>
  lemma4_inside_false_A (h 2 SA)

/-- Sanity: the field equations reduce to zero mod `S_fe` (inertness of `S_fe` on the fake side). -/
theorem reduce_fe_zero_2 : ∀ p ∈ fieldEqs 2, reduceFe p = [] := by decide +kernel
theorem reduce_fe_zero_3 : ∀ p ∈ fieldEqs 3, reduceFe p = [] := by decide +kernel

end CryptoResearch.Nagao.Lemma4Witness

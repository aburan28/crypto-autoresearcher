import Mathlib.AlgebraicGeometry.EllipticCurve.Affine.Point
import Mathlib.GroupTheory.OrderOfElement
import Mathlib.Algebra.Field.ZMod
import Mathlib.LinearAlgebra.Span.Basic
import Mathlib.Tactic.LinearCombination
import Mathlib.Tactic.NormNum
import Mathlib.Tactic.Ring

/- Independent statement-only controls. No producer modules are imported.
   All arithmetic controls use kernel-checked `decide` or ordinary proof tactics.
   No native_decide, sorry, or added axioms. -/
namespace BlindJ4

instance : Fact (Nat.Prime 7) := ⟨by decide⟩

abbrev F := ZMod 7

theorem ordinary_iff {K : Type*} [Field K] (a₁ b₁ a₂ b₂ x : K)
    (hd : b₁ - b₂ ≠ 0) :
    a₁ + b₁ * x = a₂ + b₂ * x ↔ x = (a₂ - a₁) / (b₁ - b₂) := by
  constructor
  · intro h
    apply (eq_div_iff hd).2
    linear_combination h
  · intro h
    have hm := (eq_div_iff hd).1 h
    linear_combination hm

theorem negated_iff {K : Type*} [Field K] (a₁ b₁ a₂ b₂ x : K)
    (hd : b₁ + b₂ ≠ 0) :
    a₁ + b₁ * x = -(a₂ + b₂ * x) ↔ x = -(a₁ + a₂) / (b₁ + b₂) := by
  constructor
  · intro h
    apply (eq_div_iff hd).2
    linear_combination h
  · intro h
    have hm := (eq_div_iff hd).1 h
    linear_combination hm

theorem ordinary_requested (x : F) : 1 + 2 * x = 2 + 0 * x ↔ x = 4 := by
  have hd : (2 : F) - 0 ≠ 0 := by decide
  have hv : ((2 : F) - 1) / ((2 : F) - 0) = 4 := by
    apply (div_eq_iff hd).2
    decide
  simpa only [hv] using ordinary_iff (1 : F) 2 2 0 x hd

theorem negated_requested (x : F) : 1 + 2 * x = -(3 + 4 * x) ↔ x = 4 := by
  have hd : (2 : F) + 4 ≠ 0 := by decide
  have hv : -((1 : F) + 3) / ((2 : F) + 4) = 4 := by
    apply (div_eq_iff hd).2
    decide
  simpa only [hv] using negated_iff (1 : F) 2 3 4 x hd

theorem ordinary_equal_coefficients_not_unique :
    ¬ ∃! x : F, 1 + 2 * x = 1 + 2 * x := by
  simp only [ExistsUnique]
  decide

theorem ordinary_equal_coefficients_no_solution :
    ∀ x : F, ¬ (1 + 2 * x = 2 + 2 * x) := by decide

theorem ordinary_zero_denominator_formula_false :
    ∃ x : F, (1 + 2 * x = 1 + 2 * x) ∧ x ≠ ((1 : F) - 1) / ((2 : F) - 2) := by
  refine ⟨1, rfl, ?_⟩
  norm_num

theorem negated_zero_denominator_not_unique :
    ¬ ∃! x : F, 1 + 2 * x = -(6 + 5 * x) := by
  simp only [ExistsUnique]
  decide

inductive Letter (R : Type*)
  | tr : R → Letter R
  | v : Letter R

def run {R : Type*} [CommRing R] : List (Letter R) → R → R
  | [], x => x
  | .tr s :: w, x => run w (x + s)
  | .v :: w, x => run w (-x)

def vcount {R : Type*} : List (Letter R) → ℕ
  | [] => 0
  | .tr _ :: w => vcount w
  | .v :: w => vcount w + 1

/-- Every list entry corresponds to one translation occurrence. Its sign is
    determined by v letters strictly to that occurrence's right. -/
def signedTranslations {R : Type*} [CommRing R] : List (Letter R) → List R
  | [] => []
  | .tr s :: w => ((-1 : R) ^ vcount w * s) :: signedTranslations w
  | .v :: w => signedTranslations w

theorem affine_suffix_formula {R : Type*} [CommRing R] (w : List (Letter R)) (x : R) :
    run w x = (-1 : R) ^ vcount w * x + (signedTranslations w).sum := by
  induction w generalizing x with
  | nil => simp [run, vcount, signedTranslations]
  | cons a w ih =>
    cases a with
    | tr s => simp only [run, vcount, signedTranslations, List.sum_cons, ih]; ring
    | v => simp only [run, vcount, signedTranslations, ih, pow_succ]; ring

theorem affine_requested : run [.tr (2 : F), .v] 1 = 4 := by decide

theorem affine_wrong_sign_is_false :
    run [.tr (2 : F), .v] 1 ≠ (-1 : F) ^ vcount [.tr (2 : F), .v] * 1 + 2 := by decide

theorem affine_empty_word {R : Type*} [CommRing R] (x : R) : run [] x = x := rfl

theorem transport_injective_of_coprime {S T : Type*} [AddGroup S] [Finite S]
    (d : ℕ) (f : S → T) (back : T → S)
    (h : ∀ p, back (f p) = d • p) (hc : (Nat.card S).Coprime d) :
    Function.Injective f := by
  have hd : Function.Injective (fun p : S => d • p) :=
    (Nat.Coprime.nsmul_right_bijective hc).injective
  intro p q hpq
  apply hd
  change d • p = d • q
  rw [← h p, ← h q, hpq]

def zeroMap : F → F := fun _ => 0

theorem transport_bad_composition : ∀ p : F, zeroMap (zeroMap p) = 7 • p := by decide

theorem transport_bad_not_injective : ¬ Function.Injective zeroMap := by decide

theorem transport_bad_not_coprime : ¬ (Nat.card F).Coprime 7 := by
  norm_num [Nat.card_eq_fintype_card]

def doubleMap : F → F := fun p => 2 * p

theorem transport_good_composition : ∀ p : F, id (doubleMap p) = 2 • p := by
  intro p
  simp [doubleMap, nsmul_eq_mul]

theorem transport_good_injective : Function.Injective doubleMap := by decide

theorem transport_good_coprime : (Nat.card F).Coprime 2 := by
  norm_num [Nat.card_eq_fintype_card]
  decide

theorem transport_same_bad_degree_can_be_injective :
    (∀ p : F, zeroMap (id p) = 7 • p) ∧ Function.Injective (id : F → F) := by
  constructor
  · decide
  · exact Function.injective_id

def E : WeierstrassCurve.Affine F where
  a₁ := 0
  a₂ := 0
  a₃ := 0
  a₄ := 0
  a₆ := 1

theorem raw_origin_not_on_curve : ¬ E.Equation 0 0 := by
  rw [WeierstrassCurve.Affine.equation_iff]
  decide

theorem raw_origin_not_nonsingular : ¬ E.Nonsingular 0 0 := by
  intro h
  exact raw_origin_not_on_curve h.1

theorem p_nonsingular : E.Nonsingular 0 1 := by
  rw [WeierstrassCurve.Affine.nonsingular_iff, WeierstrassCurve.Affine.equation_iff]
  decide

theorem q_nonsingular : E.Nonsingular 0 6 := by
  rw [WeierstrassCurve.Affine.nonsingular_iff, WeierstrassCurve.Affine.equation_iff]
  decide

def P : E.Point := .some 0 1 p_nonsingular
def Q : E.Point := .some 0 6 q_nonsingular

theorem p_ne_identity : P ≠ 0 :=
  WeierstrassCurve.Affine.Point.some_ne_zero p_nonsingular

theorem supplied_pair_sum : P + Q = 0 := by
  apply WeierstrassCurve.Affine.Point.add_of_Y_eq rfl
  change (1 : F) = -6 - 0 * 0 - 0
  decide

/-- A typed Point carries nonsingularity evidence. The zero constructor is
    excluded because certificate entries must be affine points. -/
def affineXIn (U : Submodule F F) : E.Point → Prop
  | .zero => False
  | .some x _ _ => x ∈ U

def accepts (U : Submodule F F) (entries : List E.Point) (target : E.Point) : Prop :=
  (∀ p ∈ entries, affineXIn U p) ∧ entries.sum = target

def emptySpan : Submodule F F := Submodule.span F (∅ : Set F)

theorem empty_span_exact (x : F) : x ∈ emptySpan ↔ x = 0 := by
  simp [emptySpan]

theorem empty_tuple_exact (U : Submodule F F) (target : E.Point) :
    accepts U [] target ↔ target = 0 := by
  simp [accepts, eq_comm]

theorem empty_tuple_accepts_identity : accepts emptySpan [] 0 := by
  rw [empty_tuple_exact]

theorem empty_tuple_rejects_p : ¬ accepts emptySpan [] P := by
  rw [empty_tuple_exact]
  exact p_ne_identity

theorem supplied_pair_accepts_identity : accepts emptySpan [P, Q] 0 := by
  constructor
  · simp [affineXIn, P, Q, emptySpan]
  · simpa using supplied_pair_sum

theorem supplied_pair_rejects_p : ¬ accepts emptySpan [P, Q] P := by
  intro h
  have hzero : (0 : E.Point) = P := by simpa [supplied_pair_sum] using h.2
  exact p_ne_identity hzero.symm

theorem singleton_p_accepts_p : accepts emptySpan [P] P := by
  simp [accepts, affineXIn, P, emptySpan]

theorem identity_entry_rejected (U : Submodule F F) (target : E.Point) :
    ¬ accepts U [0] target := by
  simp [accepts, affineXIn]

#print axioms ordinary_iff
#print axioms negated_iff
#print axioms ordinary_requested
#print axioms negated_requested
#print axioms ordinary_equal_coefficients_not_unique
#print axioms ordinary_equal_coefficients_no_solution
#print axioms ordinary_zero_denominator_formula_false
#print axioms negated_zero_denominator_not_unique
#print axioms affine_suffix_formula
#print axioms affine_requested
#print axioms affine_empty_word
#print axioms affine_wrong_sign_is_false
#print axioms transport_injective_of_coprime
#print axioms transport_bad_composition
#print axioms transport_bad_not_injective
#print axioms transport_bad_not_coprime
#print axioms transport_good_composition
#print axioms transport_good_injective
#print axioms transport_good_coprime
#print axioms transport_same_bad_degree_can_be_injective
#print axioms raw_origin_not_on_curve
#print axioms raw_origin_not_nonsingular
#print axioms p_nonsingular
#print axioms q_nonsingular
#print axioms p_ne_identity
#print axioms supplied_pair_sum
#print axioms empty_span_exact
#print axioms empty_tuple_exact
#print axioms empty_tuple_accepts_identity
#print axioms empty_tuple_rejects_p
#print axioms supplied_pair_accepts_identity
#print axioms supplied_pair_rejects_p
#print axioms singleton_p_accepts_p
#print axioms identity_entry_rejected

end BlindJ4

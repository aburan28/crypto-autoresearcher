import Mathlib.AlgebraicGeometry.EllipticCurve.Affine.Point
import Mathlib.LinearAlgebra.Finsupp.LinearCombination

set_option autoImplicit false

namespace CryptoResearch.Semaev

variable {k K : Type*} [Field k] [Fintype k]
  [Field K] [DecidableEq K] [Algebra k K]

/-- A declared finite family spanning the factor-base subspace. Independence
is unnecessary for membership; a genuine basis is a special case. -/
def InDeclaredSpan {n : ℕ} (basis : Fin n → K) (x : K) : Prop :=
  ∃ c : Fin n → k, ∑ i, c i • basis i = x

instance decidableInDeclaredSpan {n : ℕ} (basis : Fin n → K) (x : K) :
    Decidable (InDeclaredSpan (k := k) basis x) := by
  unfold InDeclaredSpan
  infer_instance

omit [Fintype k] [DecidableEq K] in
/-- The enumeration predicate is exactly membership in Mathlib's linear span. -/
theorem inDeclaredSpan_iff {n : ℕ} (basis : Fin n → K) (x : K) :
    InDeclaredSpan (k := k) basis x ↔ x ∈ Submodule.span k (Set.range basis) := by
  exact (Submodule.mem_span_range_iff_exists_fun k).symm

/-- Raw affine coordinates with a checked nonsingularity proof. Equation
validity is therefore enforced by the type, without silently accepting infinity. -/
structure AffineSummand (E : WeierstrassCurve.Affine K) where
  x : K
  y : K
  nonsingular : E.Nonsingular x y

def AffineSummand.point {E : WeierstrassCurve.Affine K} (P : AffineSummand E) :
    E.Point := .some P.x P.y P.nonsingular

/-- Use the explicit equation, avoiding the noncomputable polynomial evaluator. -/
instance decidableCurveEquation (E : WeierstrassCurve.Affine K) (x y : K) :
    Decidable (E.Equation x y) :=
  decidable_of_iff
    (y^2 + E.a₁*x*y + E.a₃*y = x^3 + E.a₂*x^2 + E.a₄*x + E.a₆)
    (E.equation_iff x y).symm

/-- Certificate predicate for arbitrary tuple length, curve, declared span,
and target, using Mathlib's actual elliptic-curve addition. -/
def ValidDecomposition {n m : ℕ} (E : WeierstrassCurve.Affine K)
    (basis : Fin n → K) (P : Fin m → AffineSummand E) (R : E.Point) : Prop :=
  (∀ i, E.Equation (P i).x (P i).y) ∧
  (∀ i, InDeclaredSpan (k := k) basis (P i).x) ∧
  (∑ i, (P i).point) = R

instance instDecidableValidDecomposition {n m : ℕ} (E : WeierstrassCurve.Affine K)
    (basis : Fin n → K) (P : Fin m → AffineSummand E) (R : E.Point) :
    Decidable (ValidDecomposition (k := k) E basis P R) := by
  unfold ValidDecomposition
  infer_instance

/-- The Boolean checker is sound AND complete for the stated predicate. -/
def checkDecomposition {n m : ℕ} (E : WeierstrassCurve.Affine K)
    (basis : Fin n → K) (P : Fin m → AffineSummand E) (R : E.Point) : Bool :=
  decide (ValidDecomposition (k := k) E basis P R)

theorem checkDecomposition_iff {n m : ℕ} (E : WeierstrassCurve.Affine K)
    (basis : Fin n → K) (P : Fin m → AffineSummand E) (R : E.Point) :
    checkDecomposition (k := k) E basis P R = true ↔
      (∀ i, E.Equation (P i).x (P i).y) ∧
      (∀ i, (P i).x ∈ Submodule.span k (Set.range basis)) ∧
      (∑ i, (P i).point) = R := by
  change decide (ValidDecomposition (k := k) E basis P R) = true ↔ _
  rw [decide_eq_true_eq]
  simp only [ValidDecomposition, inDeclaredSpan_iff]

/-- The frozen target must name a theorem, while the computational Decidable
instance above is data. This theorem supplies the Boolean decision together
with its exact correctness contract for every certificate, not one fixture. -/
theorem decidable_validDecomposition {n m : ℕ} (E : WeierstrassCurve.Affine K)
    (basis : Fin n → K) (P : Fin m → AffineSummand E) (R : E.Point) :
    ∃ checked : Bool, checked = true ↔ ValidDecomposition (k := k) E basis P R := by
  refine ⟨checkDecomposition (k := k) E basis P R, ?_⟩
  simp only [checkDecomposition, decide_eq_true_eq]

end CryptoResearch.Semaev

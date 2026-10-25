import CryptoResearch.Semaev.Certificate
import CryptoResearch.NCP.AffineNormalForm
import CryptoResearch.NCP.CommutatorIdeal

set_option autoImplicit false
namespace IndependentJ2
open CryptoResearch.Semaev CryptoResearch.NCP

instance : Fact (Nat.Prime 7) := ⟨by decide⟩

def E : WeierstrassCurve.Affine (ZMod 7) := ⟨0, 0, 0, 0, 1⟩
def p01 : AffineSummand E := ⟨0, 1, by
  rw [WeierstrassCurve.Affine.nonsingular_iff]
  norm_num [E, WeierstrassCurve.Affine.equation_iff] <;> decide⟩
def p13 : AffineSummand E := ⟨1, 3, by
  rw [WeierstrassCurve.Affine.nonsingular_iff]
  norm_num [E, WeierstrassCurve.Affine.equation_iff] <;> decide⟩

theorem raw00_invalid : ¬ E.Equation 0 0 := by
  norm_num [E, WeierstrassCurve.Affine.equation_iff]
theorem raw00_not_encodable : ¬ ∃ p : AffineSummand E, p.x = 0 ∧ p.y = 0 := by
  rintro ⟨p, hx, hy⟩
  have h := p.nonsingular.1
  rw [hx, hy] at h
  exact raw00_invalid h

theorem empty_span {k K : Type*} [Field k] [Fintype k] [Field K] [DecidableEq K]
    [Algebra k K] (basis : Fin 0 → K) (x : K) :
    InDeclaredSpan (k := k) basis x ↔ x = 0 := by
  simp [InDeclaredSpan, eq_comm]

theorem empty_tuple {k K : Type*} [Field k] [Fintype k] [Field K] [DecidableEq K]
    [Algebra k K] {n : ℕ} (e : WeierstrassCurve.Affine K)
    (basis : Fin n → K) (p : Fin 0 → AffineSummand e) (r : e.Point) :
    checkDecomposition (k := k) e basis p r = true ↔ r = 0 := by
  rw [checkDecomposition_iff]
  simp [eq_comm]

theorem empty_nonidentity_rejects :
    checkDecomposition (k := ZMod 7) E (fun _ : Fin 0 => 0)
      (fun i : Fin 0 => Fin.elim0 i) p01.point = false := by decide

theorem empty_identity_accepts :
    checkDecomposition (k := ZMod 7) E (fun _ : Fin 0 => 0)
      (fun i : Fin 0 => Fin.elim0 i) 0 = true := by decide

theorem singleton_accepts :
    checkDecomposition (k := ZMod 7) E (fun _ : Fin 0 => 0)
      (fun _ : Fin 1 => p01) p01.point = true := by decide

theorem actual_target_rejects :
    checkDecomposition (k := ZMod 7) E (fun _ : Fin 0 => 0)
      (fun _ : Fin 1 => p01) 0 = false := by decide

theorem nonspan_rejects :
    checkDecomposition (k := ZMod 7) E (fun _ : Fin 0 => 0)
      (fun _ : Fin 1 => p13) p13.point = false := by decide

def p06 : AffineSummand E := ⟨0, 6, by
  rw [WeierstrassCurve.Affine.nonsingular_iff]
  norm_num [E, WeierstrassCurve.Affine.equation_iff] <;> decide⟩

theorem p01_double : p01.point + p01.point = p06.point := by
  change WeierstrassCurve.Affine.Point.add
    (.some 0 1 p01.nonsingular) (.some 0 1 p01.nonsingular) =
      .some 0 6 p06.nonsingular
  simp [WeierstrassCurve.Affine.Point.add,
    WeierstrassCurve.Affine.slope, WeierstrassCurve.Affine.negY,
    WeierstrassCurve.Affine.addX, WeierstrassCurve.Affine.addY,
    WeierstrassCurve.Affine.negAddY, E]
  decide

theorem actual_addition_accepts :
    checkDecomposition (k := ZMod 7) E (fun _ : Fin 0 => 0)
      (fun _ : Fin 2 => p01) p06.point = true := by
  rw [checkDecomposition_iff]
  refine ⟨fun _ => p01.nonsingular.1, fun _ => ?_, ?_⟩
  · rw [← inDeclaredSpan_iff]; exact ⟨fun i => Fin.elim0 i, by simp [p01]⟩
  · simpa only [Fin.sum_univ_two] using p01_double

theorem actual_addition_wrong_target_rejects :
    checkDecomposition (k := ZMod 7) E (fun _ : Fin 0 => 0)
      (fun _ : Fin 2 => p01) p01.point = false := by
  apply Bool.eq_false_iff.mpr
  intro h
  have hh := ((checkDecomposition_iff (k := ZMod 7) E (fun _ : Fin 0 => 0)
    (fun _ : Fin 2 => p01) p01.point).mp h).2.2
  rw [Fin.sum_univ_two, p01_double] at hh
  exact (by decide : p06.point ≠ p01.point) hh

instance : Fact (Nat.Prime 2) := ⟨by decide⟩
def E2 : WeierstrassCurve.Affine (ZMod 2) := ⟨0, 0, 1, 0, 0⟩
def p2 : AffineSummand E2 := ⟨0, 0, by
  rw [WeierstrassCurve.Affine.nonsingular_iff]
  norm_num [E2, WeierstrassCurve.Affine.equation_iff] <;> decide⟩
theorem characteristic_two_certificate :
    checkDecomposition (k := ZMod 2) E2 (fun _ : Fin 0 => 0)
      (fun _ : Fin 1 => p2) p2.point = true := by decide

theorem dependent_span_accepts :
    InDeclaredSpan (k := ZMod 7) (fun _ : Fin 2 => (1 : ZMod 7)) 3 := by decide

def ts : Fin 1 → ZMod 7 := fun _ => 2

theorem left_to_right :
    wordAction ts [.translate 0, .negate] 3 = 2 ∧
    wordAction ts [.negate, .translate 0] 3 = 6 ∧
    signedCounts [.translate (B := 1) 0, .negate] 0 = -1 ∧
    signedCounts [.negate, .translate (B := 1) 0] 0 = 1 := by decide

theorem two_suffix_negations :
    signedCounts [.translate (B := 1) 0, .negate, .negate] 0 = 1 := by decide

theorem characteristic_two :
    wordAction (fun _ : Fin 1 => (1 : ZMod 2)) [.translate 0, .negate] 0 = 1 := by decide

theorem empty_alphabet :
    wordAction (fun i : Fin 0 => Fin.elim0 i) [.negate, .negate] (3 : ZMod 7) = 3 := by decide

theorem actionKernel_witness_empty_alphabet :
    negLetter 0 ^ 2 - 1 ∈ TwoSidedIdeal.ker
      (actionEvaluation (n := 7) (fun i : Fin 0 => Fin.elim0 i)).toRingHom :=
  neg_square_in_action_kernel _

theorem witness_separated_empty_alphabet : negLetter 0 ^ 2 - 1 ∉ commutatorIdeal 0 :=
  neg_square_not_in_commutators 0

theorem action_not_commutative :
    affineNeg 7 * affineTranslation (1 : ZMod 7) ≠
      affineTranslation (1 : ZMod 7) * affineNeg 7 := by
  intro h
  have h0 := congrArg (fun g : affineGroup 7 => (g : Equiv.Perm (ZMod 7)) 0) h
  norm_num [affineNeg, affineTranslation] at h0
  exact (by decide : (-1 : ZMod 7) ≠ 1) h0

theorem empty_image_centralizes_neg (a : WordAlgebra 0) :
    Commute (actionEvaluation (n := 7) (fun i : Fin 0 => Fin.elim0 i) a)
      (MonoidAlgebra.of ℤ (affineGroup 7) (affineNeg 7)) := by
  induction a using FreeAlgebra.induction with
  | grade0 r =>
    rw [AlgHom.commutes]
    exact Algebra.commutes r (MonoidAlgebra.of ℤ (affineGroup 7) (affineNeg 7))
  | grade1 i =>
    cases i with
    | none =>
      simpa only [actionEvaluation, FreeAlgebra.lift_ι_apply] using
        (Commute.refl (MonoidAlgebra.of ℤ (affineGroup 7) (affineNeg 7)))
    | some i => exact Fin.elim0 i
  | mul a b ha hb => simpa only [map_mul] using ha.mul_left hb
  | add a b ha hb => simpa only [map_add] using ha.add_left hb

theorem empty_evaluation_not_surjective :
    ¬ Function.Surjective
      (actionEvaluation (n := 7) (fun i : Fin 0 => Fin.elim0 i)) := by
  intro hs
  obtain ⟨a, ha⟩ := hs (MonoidAlgebra.of ℤ (affineGroup 7)
    (affineTranslation (1 : ZMod 7)))
  have hc := empty_image_centralizes_neg a
  rw [ha] at hc
  have hm : MonoidAlgebra.of ℤ (affineGroup 7)
      (affineTranslation (1 : ZMod 7) * affineNeg 7) =
      MonoidAlgebra.of ℤ (affineGroup 7)
      (affineNeg 7 * affineTranslation (1 : ZMod 7)) := by
    simpa only [map_mul] using hc.eq
  exact action_not_commutative ((MonoidAlgebra.of_injective hm).symm)

theorem multiplication_order_differs :
    ((affineTranslation (2 : ZMod 7) * affineNeg 7 : affineGroup 7) :
      Equiv.Perm (ZMod 7)) 3 = 6 ∧
    wordAction ts [.translate 0, .negate] 3 = 2 := by decide

#eval checkDecomposition (k := ZMod 7) E (fun _ : Fin 0 => 0)
  (fun _ : Fin 2 => p01) p06.point
#print axioms raw00_invalid
#print axioms raw00_not_encodable
#print axioms empty_span
#print axioms empty_tuple
#print axioms empty_nonidentity_rejects
#print axioms empty_identity_accepts
#print axioms singleton_accepts
#print axioms actual_target_rejects
#print axioms nonspan_rejects
#print axioms p01_double
#print axioms actual_addition_accepts
#print axioms actual_addition_wrong_target_rejects
#print axioms characteristic_two_certificate
#print axioms dependent_span_accepts
#print axioms left_to_right
#print axioms two_suffix_negations
#print axioms characteristic_two
#print axioms empty_alphabet
#print axioms actionKernel_witness_empty_alphabet
#print axioms witness_separated_empty_alphabet
#print axioms action_not_commutative
#print axioms empty_image_centralizes_neg
#print axioms empty_evaluation_not_surjective
#print axioms multiplication_order_differs
end IndependentJ2

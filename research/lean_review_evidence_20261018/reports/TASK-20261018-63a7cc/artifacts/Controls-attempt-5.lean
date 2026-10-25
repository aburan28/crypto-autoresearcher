import Retrospective.Transport
import Retrospective.RhoCollision
import Mathlib.Tactic.NormNum
import Mathlib.Algebra.Group.Subgroup.Finite

set_option autoImplicit false
namespace ReviewerControls

instance : Fact (Nat.Prime 7) := ⟨by decide⟩

def double7 : ZMod 7 →+ ZMod 7 where
  toFun x := 2 * x
  map_zero' := by simp
  map_add' := by intro a b; ring

def triple7 : ZMod 7 →+ ZMod 7 where
  toFun x := 3 * x
  map_zero' := by simp
  map_add' := by intro a b; ring

theorem top7_card : Nat.card (⊤ : AddSubgroup (ZMod 7)) = 7 := by
  rw [AddSubgroup.card_top, Nat.card_eq_fintype_card, ZMod.card]

theorem reverse6 (P : (⊤ : AddSubgroup (ZMod 7))) :
    triple7 (double7 P) = 6 • (P : ZMod 7) := by
  change (3 : ZMod 7) * (2 * (P : ZMod 7)) = 6 • (P : ZMod 7)
  simp only [nsmul_eq_mul]
  ring

theorem nontrivial_transport_injective :
    Function.Injective (fun P : (⊤ : AddSubgroup (ZMod 7)) => double7 P) := by
  apply Retrospective.Transport.injective_on_subgroup (⊤ : AddSubgroup (ZMod 7))
    double7 triple7 6
  · rw [top7_card]; decide
  · exact reverse6

theorem nontrivial_transport_dlog (G Q : (⊤ : AddSubgroup (ZMod 7))) (k : ℤ) :
    k • double7 (G : ZMod 7) = double7 (Q : ZMod 7) ↔ k • G = Q := by
  apply Retrospective.Transport.dlog_transport_iff _ double7 triple7 6
  · rw [top7_card]; decide
  · exact reverse6

theorem zero_map_reverse7 :
    ∀ P : (⊤ : AddSubgroup (ZMod 7)),
      (0 : ZMod 7 →+ ZMod 7) ((0 : ZMod 7 →+ ZMod 7) P) = 7 • (P : ZMod 7) := by
  intro P
  simp [nsmul_eq_mul, show (7 : ZMod 7) = 0 by decide]

theorem noncoprime_zero_map_counterexample :
    ¬ Function.Injective (fun P : (⊤ : AddSubgroup (ZMod 7)) =>
      (0 : ZMod 7 →+ ZMod 7) P) := by
  intro h
  have bad := congrArg (fun P : (⊤ : AddSubgroup (ZMod 7)) => (P : ZMod 7))
    (h (a₁ := ⟨0, by simp⟩) (a₂ := ⟨1, by simp⟩) (by simp))
  exact (by decide : (0 : ZMod 7) ≠ 1) bad

theorem noncoprime_transport_false :
    (0 : ℤ) • (0 : ZMod 7 →+ ZMod 7) 0 = (0 : ZMod 7 →+ ZMod 7) 1 ∧
    ¬ (0 : ℤ) • (0 : ZMod 7) = 1 := by
  decide

theorem zero_degree_nontrivial_fails :
    ¬ (Nat.card (⊤ : AddSubgroup (ZMod 7))).Coprime 0 := by
  rw [top7_card]; decide

theorem empty_subgroup_permits_zero_map :
    Function.Injective (fun P : (⊥ : AddSubgroup (ZMod 7)) =>
      (0 : ZMod 7 →+ ZMod 7) P) := by
  apply Retrospective.Transport.injective_on_subgroup _ 0 0 0
  · simp
  · intro P; simp

def axis : ZMod 7 →+ (ZMod 7 × ZMod 7) where
  toFun x := (x, 0)
  map_zero' := rfl
  map_add' := by intro a b; rfl

theorem first_axis_base_in_range : ({axis 1} : Set (ZMod 7 × ZMod 7)) ⊆ axis.range := by
  intro z hz
  obtain rfl := Set.mem_singleton_iff.mp hz
  exact ⟨1, rfl⟩

theorem second_axis_outside : ((0, 1) : ZMod 7 × ZMod 7) ∉ axis.range := by
  rintro ⟨z, hz⟩
  have bad : (0 : ZMod 7) = 1 := congrArg Prod.snd hz
  exact (by decide : (0 : ZMod 7) ≠ 1) bad

theorem proper_range_closure :
    AddSubgroup.closure ({axis 1} : Set (ZMod 7 × ZMod 7)) ≤ axis.range :=
  Retrospective.Transport.closure_le_range axis _ first_axis_base_in_range

theorem proper_range_target_excluded :
    ((0, 1) : ZMod 7 × ZMod 7) ∉ AddSubgroup.closure ({axis 1} : Set (ZMod 7 × ZMod 7)) :=
  Retrospective.Transport.outside_range_not_in_closure axis _ first_axis_base_in_range _ second_axis_outside

theorem rho_ordinary_example : (4 : ZMod 7) = ((3 : ZMod 7) - 1) / (2 - 5) := by
  apply Retrospective.Rho.recover
  · decide
  · decide

theorem rho_negated_example : (4 : ZMod 7) = -((1 : ZMod 7) + 1) / (2 + 1) := by
  apply Retrospective.Rho.recover_negated
  · decide
  · decide

theorem rho_group_identity_example : (4 : ZMod 7) = ((3 : ZMod 7) - 1) / (2 - 5) := by
  apply Retrospective.Rho.group_collision_recover 7 (AddMonoidHom.id (ZMod 7))
    (fun _ _ h => h)
  · decide
  · decide

theorem zero_denominator_ordinary_counterexample :
    (0 : ZMod 7) + 0 * 1 = 0 + 0 * 1 ∧
    (0 : ZMod 7) + 0 * 2 = 0 + 0 * 2 ∧
    (1 : ZMod 7) ≠ ((0 : ZMod 7) - 0) / (0 - 0) ∧ (1 : ZMod 7) ≠ 2 := by norm_num

theorem zero_denominator_negated_counterexample :
    (1 : ZMod 7) + 2 * 4 = -(6 + 5 * 4) ∧
    (1 : ZMod 7) + 2 * 3 = -(6 + 5 * 3) ∧
    (2 : ZMod 7) + 5 = 0 ∧ (4 : ZMod 7) ≠ -((1 : ZMod 7) + 6) / (2 + 5) := by norm_num

theorem noninjective_encoding_counterexample :
    (0 : ZMod 7 →+ ZMod 7) 0 + (0 : ZMod 7 →+ ZMod 7) (1 * 4) =
      (0 : ZMod 7 →+ ZMod 7) 0 + (0 : ZMod 7 →+ ZMod 7) (0 * 4) ∧
    (1 : ZMod 7) ≠ 0 ∧ (4 : ZMod 7) ≠ ((0 : ZMod 7) - 0) / (1 - 0) := by norm_num

theorem composite_nonzero_coefficient_nonunique :
    (2 : ZMod 8) ≠ 0 ∧
    (2 : ZMod 8) * 1 = 2 ∧ (2 : ZMod 8) * 5 = 2 ∧
    (1 : ZMod 8) ≠ 5 := by decide

def curve7 : WeierstrassCurve.Affine (ZMod 7) := ⟨0, 0, 0, 0, 1⟩

theorem curve7_nonsingular_point : curve7.Nonsingular 0 1 := by
  rw [WeierstrassCurve.Affine.nonsingular_iff', WeierstrassCurve.Affine.equation_iff]
  norm_num [curve7]

def curve7_point : curve7.Point :=
  WeierstrassCurve.Affine.Point.some 0 1 curve7_nonsingular_point

theorem curve7_point_ne_zero : curve7_point ≠ 0 :=
  WeierstrassCurve.Affine.Point.some_ne_zero curve7_nonsingular_point

instance : Finite curve7.Point :=
  Finite.of_equiv (WithZero {xy : ZMod 7 × ZMod 7 // curve7.Nonsingular xy.1 xy.2})
    curve7.nonsingularPointEquiv.symm

theorem curve_transport_nonempty (G Q : (⊤ : AddSubgroup curve7.Point)) (k : ℤ) :
    k • (G : curve7.Point) = (Q : curve7.Point) ↔ k • G = Q := by
  exact Retrospective.Transport.curve_dlog_transport_iff curve7 curve7 _
    (AddMonoidHom.id _) (AddMonoidHom.id _) 1 (by simp) (by intro P; simp) G Q k

end ReviewerControls

import Retrospective.Transport
import Retrospective.RhoCollision
import Mathlib.Tactic.NormNum
import Mathlib.Algebra.Group.Subgroup.Finite

set_option autoImplicit false
namespace ReviewerControls

def double7 : ZMod 7 →+ ZMod 7 where
  toFun x := 2 * x
  map_zero' := by simp
  map_add' := by intro a b; ring

def triple7 : ZMod 7 →+ ZMod 7 where
  toFun x := 3 * x
  map_zero' := by simp
  map_add' := by intro a b; ring

theorem top7_card : Nat.card (⊤ : AddSubgroup (ZMod 7)) = 7 := by
  rw [AddSubgroup.card_top, ZMod.card]

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
  simp [nsmul_eq_mul]

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
  norm_num

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

theorem second_axis_outside : (0, 1 : ZMod 7 × ZMod 7) ∉ axis.range := by
  rintro ⟨z, hz⟩
  have bad : (0 : ZMod 7) = 1 := congrArg Prod.snd hz
  exact (by decide : (0 : ZMod 7) ≠ 1) bad

theorem proper_range_closure :
    AddSubgroup.closure ({axis 1} : Set (ZMod 7 × ZMod 7)) ≤ axis.range :=
  Retrospective.Transport.closure_le_range axis _ first_axis_base_in_range

theorem proper_range_target_excluded :
    (0, 1 : ZMod 7 × ZMod 7) ∉ AddSubgroup.closure ({axis 1} : Set (ZMod 7 × ZMod 7)) :=
  Retrospective.Transport.outside_range_not_in_closure axis _ first_axis_base_in_range _ second_axis_outside

theorem rho_ordinary_example : (4 : ZMod 7) = (3 - 1) / (2 - 5) := by
  apply Retrospective.Rho.recover
  · decide
  · decide

theorem rho_negated_example : (4 : ZMod 7) = -(1 + 1) / (2 + 1) := by
  apply Retrospective.Rho.recover_negated
  · decide
  · decide

theorem rho_group_identity_example : (4 : ZMod 7) = (3 - 1) / (2 - 5) := by
  apply Retrospective.Rho.group_collision_recover 7 (AddMonoidHom.id (ZMod 7))
    (fun _ _ h => h)
  · decide
  · decide

theorem zero_denominator_ordinary_counterexample :
    (0 : ZMod 7) + 0 * 1 = 0 + 0 * 1 ∧
    (0 : ZMod 7) + 0 * 2 = 0 + 0 * 2 ∧
    (1 : ZMod 7) ≠ (0 - 0) / (0 - 0) ∧ (1 : ZMod 7) ≠ 2 := by decide

theorem zero_denominator_negated_counterexample :
    (1 : ZMod 7) + 2 * 4 = -(6 + 5 * 4) ∧
    (1 : ZMod 7) + 2 * 3 = -(6 + 5 * 3) ∧
    (2 : ZMod 7) + 5 = 0 ∧ (4 : ZMod 7) ≠ -(1 + 6) / (2 + 5) := by decide

theorem noninjective_encoding_counterexample :
    (0 : ZMod 7 →+ ZMod 7) 0 + (0 : ZMod 7 →+ ZMod 7) (1 * 4) =
      (0 : ZMod 7 →+ ZMod 7) 0 + (0 : ZMod 7 →+ ZMod 7) (0 * 4) ∧
    (1 : ZMod 7) ≠ 0 ∧ (4 : ZMod 7) ≠ (0 - 0) / (1 - 0) := by decide

theorem composite_nonzero_coefficient_nonunique :
    (2 : ZMod 8) ≠ 0 ∧
    (2 : ZMod 8) * 1 = 2 ∧ (2 : ZMod 8) * 5 = 2 ∧
    (1 : ZMod 8) ≠ 5 := by decide

end ReviewerControls

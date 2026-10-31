import CryptoResearch.NCP.CommutatorIdeal

set_option autoImplicit false
namespace CryptoResearch.NCP

def translateLetter {B : ℕ} (i : Fin B) : NCAlgebra B := transGenerator B i

theorem neg_translate_square_not_in_commutators {B : ℕ} (i : Fin B) :
    (negGenerator B * translateLetter i)^2 - 1 ∉ commutatorIdeal B := by
  let ev : NCAlgebra B →ₐ[ℤ] ℤ := FreeAlgebra.lift ℤ (fun _ => 0)
  have hle : commutatorIdeal B ≤ TwoSidedIdeal.ker ev.toRingHom := by
    apply (TwoSidedIdeal.span_le).2
    rintro z ⟨x, y, rfl⟩
    apply (TwoSidedIdeal.mem_ker ev.toRingHom).2
    simp [mul_comm]
  intro h
  have hz := (TwoSidedIdeal.mem_ker ev.toRingHom).mp (hle h)
  norm_num [ev, negGenerator, translateLetter, transGenerator, map_sub, map_pow,
    FreeAlgebra.lift_ι_apply] at hz

theorem neg_translate_square_in_action_kernel {B n : ℕ} (s : Fin B → ZMod n) (i : Fin B) :
    (negGenerator B * translateLetter i)^2 - 1 ∈ TwoSidedIdeal.ker (evalRho B n s) := by
  rw [TwoSidedIdeal.mem_ker, map_sub, map_pow, map_one]
  have hnt : (negElement (ZMod n) * translationElement (s i))^2 = 1 := by
    apply Subtype.ext
    ext x
    simp [pow_two, negElement, translationElement, Equiv.addRight,
      add_comm, add_left_comm, add_assoc]
  have hv : evalRho B n s (negGenerator B * translateLetter i) =
      MonoidAlgebra.of ℤ (affineGroup (ZMod n))
        (negElement (ZMod n) * translationElement (s i)) := by
    simp [translateLetter, evalRho_neg, evalRho_trans]
  change (evalRho B n s (negGenerator B * translateLetter i))^2 - 1 = 0
  rw [hv, ← map_pow (MonoidAlgebra.of ℤ (affineGroup (ZMod n)))
    (negElement (ZMod n) * translationElement (s i)) 2, hnt, map_one]
  simp
end CryptoResearch.NCP

import CryptoResearch.NCP.CommutatorIdeal

set_option autoImplicit false
namespace CryptoResearch.NCP

def translateLetter {B : ℕ} (i : Fin B) : WordAlgebra B := FreeAlgebra.ι ℤ (some i)

theorem neg_translate_square_not_in_commutators {B : ℕ} (i : Fin B) :
    (negLetter B * translateLetter i)^2 - 1 ∉ commutatorIdeal B := by
  let ev : WordAlgebra B →ₐ[ℤ] ℤ := FreeAlgebra.lift ℤ (fun _ => 2)
  have hle : commutatorIdeal B ≤ TwoSidedIdeal.ker ev.toRingHom := by
    apply TwoSidedIdeal.span_le.mpr
    rintro z ⟨x, y, rfl⟩
    apply (TwoSidedIdeal.mem_ker ev.toRingHom).mpr
    simp [mul_comm]
  intro h
  have hz := (TwoSidedIdeal.mem_ker ev.toRingHom).mp (hle h)
  norm_num [ev, negLetter, translateLetter, map_sub, map_pow, FreeAlgebra.lift_ι_apply] at hz

theorem neg_translate_square_in_action_kernel {B n : ℕ} (s : Fin B → ZMod n) (i : Fin B) :
    (negLetter B * translateLetter i)^2 - 1 ∈ TwoSidedIdeal.ker (actionEvaluation s).toRingHom := by
  rw [TwoSidedIdeal.mem_ker, map_sub, map_pow, map_one]
  have hnt : (affineNeg n * affineTranslation (s i))^2 = 1 := by
    apply Subtype.ext
    ext x
    simp [pow_two, affineNeg, affineTranslation]
  have hv : actionEvaluation s (negLetter B * translateLetter i) =
      MonoidAlgebra.of ℤ (affineGroup n) (affineNeg n * affineTranslation (s i)) := by
    simp [actionEvaluation, negLetter, translateLetter]
  change (actionEvaluation s (negLetter B * translateLetter i))^2 - 1 = 0
  rw [hv, ← map_pow, hnt, map_one, sub_self]
end CryptoResearch.NCP

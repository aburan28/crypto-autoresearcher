import Mathlib.Algebra.Module.LinearMap.End
import Mathlib.Algebra.Module.Submodule.Ker
import Mathlib.Algebra.Module.Submodule.Range
import Mathlib.Tactic.NoncommRing
import Mathlib.Tactic.Abel

/-!
The order-five trace identity used by EXP-FROB-91ee9c C5.

For any linear endomorphism F with F^5 = 1 over a field where 5 is nonzero,
the trace 1 + F + F² + F³ + F⁴ has kernel equal to the image of F - 1.
The fixed space intersects that kernel only at zero. This algebraic theorem
does not identify F with the Frobenius on any archived finite-field cell, prove
the reported dimensions, or decompose the trace kernel into factor kernels.
-/

open LinearMap

namespace CryptoResearch.FrobTrace

variable {R V : Type*} [Field R] [AddCommGroup V] [Module R V]

/-- The five-term trace polynomial of an endomorphism. -/
def trace5 (F : Module.End R V) : Module.End R V :=
  1 + F + F ^ 2 + F ^ 3 + F ^ 4

private theorem trace5_mul_sub (F : Module.End R V) (hF : F ^ 5 = 1) :
    trace5 F * (F - 1) = 0 := by
  unfold trace5
  calc
    (1 + F + F ^ 2 + F ^ 3 + F ^ 4) * (F - 1) = F ^ 5 - 1 := by noncomm_ring
    _ = 0 := by rw [hF]; simp

private theorem trace5_sub_five (F : Module.End R V) :
    trace5 F - 5 • (1 : Module.End R V) =
      (F - 1) * (4 • (1 : Module.End R V) + 3 • F + 2 • F ^ 2 + F ^ 3) := by
  unfold trace5
  noncomm_ring

/-- The trace-zero vectors are precisely `F - 1` coboundaries when `F^5 = 1`
and five is invertible. -/
theorem trace5_eq_zero_iff_exists (F : Module.End R V) (hF : F ^ 5 = 1)
    (h5 : (5 : R) ≠ 0) (u : V) :
    trace5 F u = 0 ↔ ∃ v : V, (F - 1) v = u := by
  constructor
  · intro hu
    let P : Module.End R V := 4 • 1 + 3 • F + 2 • F ^ 2 + F ^ 3
    have hid := congrArg (fun g : Module.End R V => g u) (trace5_sub_five F)
    have hcast : (5 : ℕ) • u = (5 : R) • u :=
      (Nat.cast_smul_eq_nsmul R 5 u).symm
    have hPu : (F - 1) (P u) = -((5 : R) • u) := by
      simpa [P, hu, hcast] using hid.symm
    refine ⟨(5 : R)⁻¹ • -(P u), ?_⟩
    rw [map_smul, map_neg, hPu]
    simp [smul_smul, h5]
  · rintro ⟨v, rfl⟩
    have h := congrArg (fun g : Module.End R V => g v) (trace5_mul_sub F hF)
    simpa only [Module.End.mul_apply, LinearMap.zero_apply] using h

/-- The trace kernel is the image of `F - 1`. -/
theorem ker_trace5_eq_range_sub (F : Module.End R V) (hF : F ^ 5 = 1)
    (h5 : (5 : R) ≠ 0) :
    (trace5 F).ker = (F - 1).range := by
  ext u
  exact trace5_eq_zero_iff_exists F hF h5 u

/-- A fixed vector with zero five-term trace is zero in characteristic not five. -/
theorem fixed_trace5_eq_zero (F : Module.End R V) (h5 : (5 : R) ≠ 0)
    (u : V) (hfixed : F u = u) (htrace : trace5 F u = 0) : u = 0 := by
  have hp (n : ℕ) : (F ^ n) u = u := by
    induction n with
    | zero => simp
    | succ n ih => rw [pow_succ, Module.End.mul_apply, hfixed, ih]
  have htrace5 : trace5 F u = (5 : R) • u := by
    simp only [trace5, LinearMap.add_apply, Module.End.one_apply, hp]
    rw [hfixed]
    have hn : (5 : R) • u = (5 : ℕ) • u := Nat.cast_smul_eq_nsmul R 5 u
    rw [hn]
    abel
  rw [htrace5] at htrace
  have hu := congrArg (fun x : V => (5 : R)⁻¹ • x) htrace
  simpa [smul_smul, h5] using hu

end CryptoResearch.FrobTrace

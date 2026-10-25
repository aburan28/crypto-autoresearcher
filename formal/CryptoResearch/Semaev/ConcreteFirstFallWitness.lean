import CryptoResearch.Semaev.BooleanParityFiltrationCertificate

/-!
# Concrete finite first-fall witness for one source-bound Semaev draw

For the frozen Boolean draw n=4, n'=4, seed index 1, x_R=1, basis
[9,3,2,12], with canonical component-equation SHA-256
89ab8e668c510572bbf9307f105b2eaf46858ad900f0b6b4a2fce8803e0ba6eb,
this module checks a particular XOR combination of the 80 compatible
degree-three rows. The resulting 256-bit coefficient vector has degree at
most two. The coefficient sum at monomial masks 80 and 192 vanishes on
every degree-two row but is one on the witness, so it is outside their span.

This proves one finite Boolean-model counterexample to uniform degree-two
first fall. It does not prove a generic S₃ descent or a cryptanalytic cost.
-/

set_option maxRecDepth 1000000
set_option maxHeartbeats 0

namespace CryptoResearch.Semaev.ConcreteFirstFallWitness
open CryptoResearch.Semaev.BooleanParityFiltrationCertificate.FiniteSemaev
open CryptoResearch.Semaev.BooleanParityFiniteCertificate

/-- Bit i selects row i of the source-generated degree-three matrix. -/
def comboMask : Nat := 1321682796735964
/-- The XOR result, encoded by bit j for squarefree monomial mask j. -/
def witnessNat : Nat := 6277101735386703064921270320751746415339343215057222047510

def xorRows : Nat → Nat
  | 0 => 0
  | n + 1 => Nat.xor (xorRows n) (if comboMask.testBit n then (rows 3)[n]! else 0)

theorem xorRows_eq_witnessNat : xorRows 80 = witnessNat := by
  decide

def bitVec (a : Nat) (j : Fin 256) : ZMod 2 :=
  if a.testBit j.val then 1 else 0

private theorem bitVec_zero : bitVec 0 = 0 := by
  funext j
  simp [bitVec]

private theorem bitVec_xor (a b : Nat) (j : Fin 256) :
    bitVec (Nat.xor a b) j = bitVec a j + bitVec b j := by
  change (if (a ^^^ b).testBit j.val then (1 : ZMod 2) else 0) =
    (if a.testBit j.val then 1 else 0) +
    (if b.testBit j.val then 1 else 0)
  rw [Nat.testBit_xor]
  cases h1 : a.testBit j.val <;> cases h2 : b.testBit j.val <;>
    simp_all; decide

def witnessVec : Fin 256 → ZMod 2 := bitVec witnessNat
def rowSpaceThree : Submodule (ZMod 2) (Fin 256 → ZMod 2) :=
  Submodule.span (ZMod 2) (Set.range fullRows3.row)

private theorem bitVec_xorRows_mem (n : Nat) : n ≤ 80 →
    bitVec (xorRows n) ∈ rowSpaceThree := by
  induction n with
  | zero =>
      intro _
      rw [xorRows, bitVec_zero]
      exact Submodule.zero_mem _
  | succ n ih =>
      intro hn
      have hn80 : n < 80 := by omega
      have hprev := ih (by omega)
      have hrow : bitVec ((rows 3)[n]!) = fullRows3.row ⟨n, hn80⟩ := by rfl
      have hx : bitVec (xorRows (n + 1)) =
          bitVec (xorRows n) + bitVec (if comboMask.testBit n then (rows 3)[n]! else 0) := by
        funext j
        exact bitVec_xor (xorRows n) (if comboMask.testBit n then (rows 3)[n]! else 0) j
      rw [hx]
      apply Submodule.add_mem _ hprev
      by_cases hc : comboMask.testBit n
      · simp only [hc, ite_true, hrow]
        exact Submodule.subset_span ⟨⟨n, hn80⟩, rfl⟩
      · simp [hc, bitVec_zero]

theorem witnessVec_mem_rowSpaceThree : witnessVec ∈ rowSpaceThree := by
  change bitVec witnessNat ∈ rowSpaceThree
  rw [← xorRows_eq_witnessNat]
  exact bitVec_xorRows_mem 80 (by omega)

private theorem witness_high_zero : witnessNat &&& upperMask 2 = 0 := by
  decide

theorem witnessVec_low : witnessVec ∈ lowDegreeAtMostTwo := by
  change maskProjection (upperMask 2) witnessVec = 0
  funext j
  have hz := congrArg (fun n : Nat => n.testBit j.val) witness_high_zero
  rw [Nat.testBit_and, Nat.zero_testBit] at hz
  change (if (upperMask 2).testBit j.val then witnessVec j else 0) = 0
  by_cases hu : (upperMask 2).testBit j.val <;> simp_all [witnessVec, bitVec]

private def j80 : Fin 256 := ⟨80, by decide⟩
private def j192 : Fin 256 := ⟨192, by decide⟩

/-- A linear functional that annihilates every degree-two row. -/
def separator : (Fin 256 → ZMod 2) →ₗ[ZMod 2] ZMod 2 where
  toFun v := v j80 + v j192
  map_add' := by
    intro v w
    simp [Pi.add_apply, add_left_comm, add_comm]
  map_smul' := by
    intro a v
    simp [Pi.smul_apply, smul_eq_mul, mul_add]

private theorem separator_rows2 : ∀ i : Fin 28,
    separator (fullRows2.row i) = 0 := by decide

private theorem rowSpaceTwo_le_separator_ker :
    rowSpaceTwo ≤ LinearMap.ker separator := by
  change Submodule.span (ZMod 2) (Set.range fullRows2.row) ≤ _
  apply Submodule.span_le.mpr
  rintro v ⟨i, rfl⟩
  exact separator_rows2 i

private theorem separator_witness : separator witnessVec = 1 := by decide

/-- This explicit vector is a new low-degree class at degree three. -/
theorem concreteNewFall :
    witnessVec ∈ lowDegreePartThree ∧ witnessVec ∉ rowSpaceTwo := by
  constructor
  · exact ⟨witnessVec_mem_rowSpaceThree, witnessVec_low⟩
  · intro h
    have hzero : separator witnessVec = 0 := rowSpaceTwo_le_separator_ker h
    rw [separator_witness] at hzero
    norm_num at hzero

#print axioms xorRows_eq_witnessNat
#print axioms separator_rows2
#print axioms concreteNewFall

end CryptoResearch.Semaev.ConcreteFirstFallWitness

import CryptoResearch.Semaev.BooleanParityFiniteCertificate

/-!
# Finite S₃ equation semantics for the parity certificate

The field is F₂[X]/(X⁴+X+1), encoded by four-bit integers. The source
sample uses x_R=1 and the ordered factor-base basis [9,3,2,12]. This file
checks all 256 Boolean assignments: the four literal component polynomials
in `BooleanParityFiniteCertificate.equations` evaluate to the corresponding
bits of S₃(x₁,x₂,1)=e₂²+e₃+1. The check binds the input equations to a direct
finite-field model. It does not establish a general S₃ descent theorem.
-/

set_option maxRecDepth 1000000
set_option maxHeartbeats 0

namespace CryptoResearch.Semaev.FiniteEquationSemantics

open BooleanParityFiniteCertificate

/-- Carryless multiplication of degree-at-most-three binary polynomials. -/
def carryless (a b : Nat) : Nat :=
  (List.range 4).foldl (fun acc i =>
    if b.testBit i then Nat.xor acc (a * 2 ^ i) else acc) 0

/-- Reduction by X⁴+X+1, encoded by the integer 19. -/
def reduce (p : Nat) : Nat :=
  (List.range 3).reverse.foldl (fun acc i =>
    if acc.testBit (i + 4) then Nat.xor acc (19 * 2 ^ i) else acc) p

def fieldMul (a b : Nat) : Nat := reduce (carryless a b)

def basis : List Nat := [9, 3, 2, 12]

/-- The first and second input are linear combinations of the same basis. -/
def fieldInput (assignment offset : Nat) : Nat :=
  (List.range 4).foldl (fun acc i =>
    if assignment.testBit (offset + i) then Nat.xor acc (basis[i]!) else acc) 0

/-- S₃(x₁,x₂,1)=e₂²+e₃+1 for the binary curve coefficient a₆=1. -/
def semaevS3 (assignment : Nat) : Nat :=
  let x₁ := fieldInput assignment 0
  let x₂ := fieldInput assignment 4
  let x₁x₂ := fieldMul x₁ x₂
  let e₂ := Nat.xor (Nat.xor x₁x₂ x₁) x₂
  Nat.xor (Nat.xor (fieldMul e₂ e₂) x₁x₂) 1

def monomialValue (monomial assignment : Nat) : Nat :=
  if Nat.land monomial assignment == monomial then 1 else 0

def polynomialValue (f : List Nat) (assignment : Nat) : Nat :=
  f.foldl (fun acc monomial => Nat.xor acc (monomialValue monomial assignment)) 0

/-- Four component-polynomial values, packed into the polynomial-basis bits. -/
def descendedS3 (assignment : Nat) : Nat :=
  (List.range 4).foldl (fun acc bit =>
    Nat.xor acc ((polynomialValue (equations[bit]!) assignment) * 2 ^ bit)) 0

/-- Independent field arithmetic stays inside the chosen 16-element field. -/
theorem fieldMul_closed :
    ∀ a ∈ List.range 16, ∀ b ∈ List.range 16, fieldMul a b < 16 := by decide

/-- Every literal input equation agrees with direct S₃ field evaluation. -/
theorem all_component_equations_match_s3 :
    ∀ assignment ∈ List.range 256,
      descendedS3 assignment = semaevS3 assignment := by decide

end CryptoResearch.Semaev.FiniteEquationSemantics

import Init

/-!
# Finite Boolean-parity certificate for one archived Semaev draw

This module checks the exact component-equation masks for `n=4`, `n'=4`,
seed index `s=1`, `xR=1`, basis `[9,3,2,12]` in the 2026-10-22 replay.
Their canonical JSON SHA-256 is
`89ab8e668c510572bbf9307f105b2eaf46858ad900f0b6b4a2fce8803e0ba6eb`.
The F₂ Boolean monomials are indexed by eight-bit masks. Multiplication
combines masks by OR and *adds coefficients by XOR*, so duplicate terms cancel.

The theorems compute a finite Gaussian-elimination certificate with Lean's
kernel. They do not prove a general theorem identifying this executable
`rankOn` routine with vector-space dimension, and they do not derive the
component equations from the abstract S₃ polynomial inside Lean. Those
semantic links and any general first-fall statement remain separate tasks.
-/

set_option maxRecDepth 1000000
set_option maxHeartbeats 0

namespace CryptoResearch.Semaev.BooleanParityFiniteCertificate

/-- Four nonzero component equations, each as its squarefree monomial masks. -/
def equations : List (List Nat) :=
  [[0,1,2,8,16,17,24,32,34,36,40,66,68,128,129,130,136],
   [8,17,34,68,72,128,132],
   [1,2,4,8,16,18,32,33,34,64,68,128,136],
   [1,8,16,128]]

/-- Degree of an eight-variable Boolean monomial. -/
def degree (m : Nat) : Nat :=
  (List.range 8).foldl (fun count bit => count + if m.testBit bit then 1 else 0) 0

/-- Correct F₂ Boolean product by one monomial: equal output masks cancel. -/
def parityProductRow (f : List Nat) (multiplier : Nat) : Nat :=
  f.foldl (fun row m => Nat.xor row (2 ^ Nat.lor m multiplier)) 0

/-- The archived set semantics, encoded as bitwise OR for comparison only. -/
def archivedProductRow (f : List Nat) (multiplier : Nat) : Nat :=
  f.foldl (fun row m => Nat.lor row (2 ^ Nat.lor m multiplier)) 0

/-- The first component equation is the witness for the set-versus-XOR error. -/
def firstEquation : List Nat :=
  [0,1,2,8,16,17,24,32,34,36,40,66,68,128,129,130,136]

theorem firstEquation_matches_input : equations.head! = firstEquation := by decide

/-- The archived product has exactly these three extra monomials. -/
theorem archived_product_extra_masks :
    Nat.xor (archivedProductRow firstEquation 1)
      (parityProductRow firstEquation 1) =
      2 ^ 1 + 2 ^ 17 + 2 ^ 129 := by decide

theorem archived_product_differs :
    archivedProductRow firstEquation 1 ≠ parityProductRow firstEquation 1 := by decide

/-- Bits above degree `D` in the 256-dimensional Boolean monomial space. -/
def upperMask (D : Nat) : Nat :=
  ((List.range 256).filter fun m => degree m > D).foldl
    (fun row m => Nat.xor row (2 ^ m)) 0

/-- Include a multiplier exactly when its *parity-corrected* product has
actual Boolean degree at most `D`; the zero product is harmless. -/
def compatible (f : List Nat) (multiplier D : Nat) : Bool :=
  Nat.land (parityProductRow f multiplier) (upperMask D) == 0

/-- All degree-compatible Boolean monomial multiples of the input equations. -/
def rows (D : Nat) : List Nat :=
  equations.flatMap fun f =>
    ((List.range 256).filter fun m => compatible f m D).map (parityProductRow f)

/-- Binary row elimination, sweeping the 256 monomial columns high to low. -/
def rankOn (columns : List Nat) (rs : List Nat) : Nat :=
  (columns.foldl (fun state pivotColumn =>
    let (count, remaining) := state
    match remaining.find? (fun row => row.testBit pivotColumn) with
    | none => (count, remaining)
    | some pivotRow =>
      let rest := remaining.erase pivotRow
      (count + 1, rest.map fun row =>
        if row.testBit pivotColumn then Nat.xor row pivotRow else row))
    (0, rs)).1

def rank (rs : List Nat) : Nat := rankOn (List.range 256).reverse rs

/-- Projection onto the homogeneous degree-`D` columns. -/
def degreeMask (D : Nat) : Nat :=
  ((List.range 256).filter fun m => degree m == D).foldl
    (fun row m => Nat.xor row (2 ^ m)) 0

def projectedRank (D : Nat) : Nat :=
  rank ((rows D).map fun row => Nat.land row (degreeMask D))

/-- Exact kernel-evaluated ranks for this source-bound finite system. -/
theorem rank_one : rank (rows 1) = 1 := by decide
theorem projected_rank_one : projectedRank 1 = 1 := by decide
theorem rank_two : rank (rows 2) = 11 := by decide
theorem projected_rank_two : projectedRank 2 = 10 := by decide
theorem rank_three : rank (rows 3) = 53 := by decide
theorem projected_rank_three : projectedRank 3 = 41 := by decide

/-- Executable counterpart of the historical `new_falls(D)` formula. -/
def newFalls (D : Nat) : Nat :=
  rank (rows D) - projectedRank D - (if D = 0 then 0 else rank (rows (D - 1)))

theorem no_fall_one : newFalls 1 = 0 := by
  unfold newFalls
  rw [rank_one, projected_rank_one]
  decide

theorem no_fall_two : newFalls 2 = 0 := by
  unfold newFalls
  rw [rank_two, projected_rank_two, rank_one]
  decide

theorem first_new_fall_three : newFalls 3 = 1 := by
  unfold newFalls
  rw [rank_three, projected_rank_three, rank_two]
  decide

/-- The first positive value of the executable fall count is at degree three. -/
theorem exact_first_fall_at_three :
    newFalls 1 = 0 ∧ newFalls 2 = 0 ∧ newFalls 3 = 1 :=
  ⟨no_fall_one, no_fall_two, first_new_fall_three⟩

end CryptoResearch.Semaev.BooleanParityFiniteCertificate

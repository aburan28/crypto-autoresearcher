import CryptoResearch.NCP.AffineNormalForm
import Mathlib.Tactic.Linarith
import Mathlib.Algebra.BigOperators.Fin

set_option autoImplicit false
namespace CryptoResearch.NCP
variable {B : ℕ}

def shadowL1 (a : Fin B → ℤ) : ℕ := ∑ i, (a i).natAbs

def minNegations (e : ℤ) (a : Fin B → ℤ) : ℕ :=
  if e = -1 then 1 else if ∀ i, 0 ≤ a i then 0 else 2

theorem wordSign_cases (w : List (Letter B)) : wordSign w = 1 ∨ wordSign w = -1 := by
  induction w with
  | nil => simp [wordSign]
  | cons l w ih =>
    cases l with
    | translate i => simpa [wordSign] using ih
    | negate => rcases ih with h | h <;> simp [wordSign, h]

theorem shadowL1_translate (a : Fin B → ℤ) (e : ℤ) (j : Fin B)
    (he : e = 1 ∨ e = -1) :
    shadowL1 (fun i => a i + if j = i then e else 0) ≤ shadowL1 a + 1 := by
  unfold shadowL1
  have hpoint : ∀ i, (a i + if j = i then e else 0).natAbs ≤
      (a i).natAbs + if j = i then 1 else 0 := by
    intro i
    split_ifs with h
    · have htri := Int.natAbs_add_le (a i) e
      rcases he with rfl | rfl <;> simpa using htri
    · simp
  calc
    _ ≤ ∑ i, ((a i).natAbs + if j = i then 1 else 0) := Finset.sum_le_sum (fun i _ => hpoint i)
    _ = _ := by simp [Finset.sum_add_distrib]

theorem minNegations_translate (a : Fin B → ℤ) (e : ℤ) (j : Fin B)
    (he : e = 1 ∨ e = -1) :
    minNegations e (fun i => a i + if j = i then e else 0) ≤ minNegations e a := by
  rcases he with rfl | rfl
  · by_cases ha : ∀ i, 0 ≤ a i
    · have hnew : ∀ i, 0 ≤ a i + if j = i then (1 : ℤ) else 0 := by
        intro i; split_ifs <;> have := ha i <;> omega
      simp [minNegations, ha, hnew]
    · simp [minNegations, ha]; split_ifs <;> omega
  · simp [minNegations]

theorem minNegations_negate (a : Fin B → ℤ) (e : ℤ) (he : e = 1 ∨ e = -1) :
    minNegations (-e) a ≤ minNegations e a + 1 := by
  rcases he with rfl | rfl <;> by_cases ha : ∀ i, 0 ≤ a i <;>
    simp [minNegations, ha]

theorem shadow_cost_le_length (w : List (Letter B)) :
    shadowL1 (signedCounts w) + minNegations (wordSign w) (signedCounts w) ≤ w.length := by
  induction w with
  | nil => simp [shadowL1, signedCounts, minNegations, wordSign]
  | cons l w ih =>
    cases l with
    | translate j =>
      have h1 := shadowL1_translate (signedCounts w) (wordSign w) j (wordSign_cases w)
      have h2 := minNegations_translate (signedCounts w) (wordSign w) j (wordSign_cases w)
      simp only [signedCounts, wordSign, List.length_cons]
      omega
    | negate =>
      have hm := minNegations_negate (signedCounts w) (wordSign w) (wordSign_cases w)
      change shadowL1 (signedCounts w) + minNegations (-wordSign w) (signedCounts w) ≤ w.length + 1
      omega

theorem wordSign_append (u v : List (Letter B)) :
    wordSign (u ++ v) = wordSign u * wordSign v := by
  induction u with
  | nil => simp [wordSign]
  | cons l u ih => cases l <;> simp [wordSign, ih, neg_mul]

theorem signedCounts_append (u v : List (Letter B)) (j : Fin B) :
    signedCounts (u ++ v) j = signedCounts u j * wordSign v + signedCounts v j := by
  induction u with
  | nil => simp [signedCounts]
  | cons l u ih =>
    cases l with
    | negate => simpa [signedCounts] using ih
    | translate i =>
      simp only [List.cons_append, signedCounts, wordSign_append, ih]
      split_ifs <;> ring

def translationBlock (c : Fin B → ℕ) : List (Letter B) :=
  (List.ofFn fun i => List.replicate (c i) (.translate i : Letter B)).flatten

theorem translationBlock_length (c : Fin B → ℕ) :
    (translationBlock c).length = ∑ i, c i := by
  simp [translationBlock, List.length_flatten, List.map_ofFn, List.sum_ofFn]

theorem translationBlock_no_negate (c : Fin B → ℕ) :
    .negate ∉ translationBlock c := by
  simp [translationBlock]

theorem translationBlock_sign (c : Fin B → ℕ) : wordSign (translationBlock c) = 1 := by
  rw [wordSign_eq_negOne_pow, List.count_eq_zero.mpr (translationBlock_no_negate c)]
  simp

theorem signedCounts_eq_count (w : List (Letter B)) (h : .negate ∉ w) (j : Fin B) :
    signedCounts w j = (w.count (.translate j) : ℤ) := by
  induction w with
  | nil => simp [signedCounts]
  | cons l w ih =>
    cases l with
    | negate => simp at h
    | translate i =>
      have hw : wordSign w = 1 := by
        rw [wordSign_eq_negOne_pow, List.count_eq_zero.mpr (by simpa using h)]
        simp
      simp only [signedCounts, hw]
      rw [ih (by simpa using h)]
      by_cases hij : i = j
      · subst i; simp
      · have hji : j ≠ i := Ne.symm hij
        simp [hij]

theorem translationBlock_counts (c : Fin B → ℕ) (j : Fin B) :
    signedCounts (translationBlock c) j = (c j : ℤ) := by
  rw [signedCounts_eq_count _ (translationBlock_no_negate c)]
  congr 1
  simp [translationBlock, List.count_flatten, List.map_ofFn, List.sum_ofFn,
    List.count_replicate]


theorem int_parts_abs (z : ℤ) : z.toNat + (-z).toNat = z.natAbs := by
  omega

def positiveBlock (a : Fin B → ℤ) : List (Letter B) := translationBlock (fun i => (a i).toNat)
def negativeBlock (a : Fin B → ℤ) : List (Letter B) := translationBlock (fun i => (-a i).toNat)

theorem parts_length (a : Fin B → ℤ) :
    (positiveBlock a).length + (negativeBlock a).length = shadowL1 a := by
  simp only [positiveBlock, negativeBlock, translationBlock_length, shadowL1]
  rw [← Finset.sum_add_distrib]
  exact Finset.sum_congr rfl (fun i _ => int_parts_abs (a i))

/-- An explicit shortest representative, including empty bases. -/
def shadowWord (e : ℤ) (a : Fin B → ℤ) : List (Letter B) :=
  if e = -1 then negativeBlock a ++ [.negate] ++ positiveBlock a
  else if ∀ i, 0 ≤ a i then positiveBlock a
  else [.negate] ++ negativeBlock a ++ [.negate] ++ positiveBlock a

theorem shadowWord_sign (e : ℤ) (a : Fin B → ℤ) (he : e = 1 ∨ e = -1) :
    wordSign (shadowWord e a) = e := by
  rcases he with rfl | rfl <;> by_cases ha : ∀ i, 0 ≤ a i <;>
    simp [shadowWord, ha, wordSign_append, wordSign, positiveBlock, negativeBlock,
      translationBlock_sign]

theorem shadowWord_counts (e : ℤ) (a : Fin B → ℤ) (j : Fin B) :
    signedCounts (shadowWord e a) j = a j := by
  by_cases he : e = -1
  · simp [shadowWord, he, signedCounts_append, wordSign,
      signedCounts, positiveBlock, negativeBlock, translationBlock_sign,
      translationBlock_counts]
    have h := Int.toNat_sub_toNat_neg (a j)
    omega
  · by_cases ha : ∀ i, 0 ≤ a i
    · simp [shadowWord, he, ha, positiveBlock, translationBlock_counts,
        Int.toNat_of_nonneg (ha j)]
    · simp [shadowWord, he, ha, signedCounts_append, wordSign,
        signedCounts, positiveBlock, negativeBlock, translationBlock_sign,
        translationBlock_counts]
      have h := Int.toNat_sub_toNat_neg (a j)
      omega

theorem shadowWord_length (e : ℤ) (a : Fin B → ℤ) :
    (shadowWord e a).length = shadowL1 a + minNegations e a := by
  have hparts := parts_length a
  by_cases he : e = -1
  · simp only [shadowWord, minNegations, ite_eq_left he, List.length_append, List.length_singleton]
    omega
  · by_cases ha : ∀ i, 0 ≤ a i
    · have hz : (negativeBlock a).length = 0 := by
        have hzero : ∀ i, (-a i).toNat = 0 := fun i => Int.toNat_eq_zero.mpr (by linarith [ha i])
        simp [negativeBlock, translationBlock_length, hzero]
      simp only [shadowWord, minNegations, ite_eq_right he, ite_eq_left ha, add_zero]
      omega
    · simp only [shadowWord, minNegations, ite_eq_right he, ite_eq_right ha, List.length_append, List.length_singleton]
      omega

/-- Lemma 2(b): existence at every length bound iff the exact L1 cost plus
its necessary sign overhead fits. Both directions use the original word
alphabet, not an assumed shadow-group representation. -/
theorem shadow_reachable_iff (e : ℤ) (a : Fin B → ℤ) (he : e = 1 ∨ e = -1) (d : ℕ) :
    (∃ w : List (Letter B), w.length ≤ d ∧ wordSign w = e ∧ signedCounts w = a) ↔
      shadowL1 a + minNegations e a ≤ d := by
  constructor
  · rintro ⟨w, hlen, rfl, rfl⟩
    exact (shadow_cost_le_length w).trans hlen
  · intro h
    exact ⟨shadowWord e a, by rwa [shadowWord_length], shadowWord_sign e a he,
      funext (shadowWord_counts e a)⟩

end CryptoResearch.NCP

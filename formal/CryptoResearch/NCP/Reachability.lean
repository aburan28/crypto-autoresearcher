/-
Source: research/THM_COMMUTATOR_KERNEL1.md, Lemma 2(b).
Target: formal/targets/ncp-reachability.yaml.

This is the exact shortest-word criterion for the signed-count shadow of
translation/negation words. `signedCount` and `shadowSign` are imported from
the affine-normal-form proof, preserving its left-to-right action convention
and signs from negations to the right of each translation.

The lower bound charges one word position per unit of signed-count L1 weight
and the necessary zero, one, or two negations. The construction realizes the
bound by listing positive and negative translations around those negations.
It concerns word combinatorics; it does not measure NC search cost or prove
the path-algebra kernel ideal.
-/
import CryptoResearch.NCP.AffineNormalForm

namespace CryptoResearch.NCP

private theorem negCount_append {B : Nat} (u v : List (Letter B)) :
    negCount (u ++ v) = negCount u + negCount v := by
  induction u with
  | nil => simp [negCount]
  | cons l u ih =>
      cases l <;> simp [negCount, ih, Nat.add_comm, Nat.add_left_comm]

private theorem signedCount_append {B : Nat} (u v : List (Letter B))
    (i : Fin B) :
    signedCount (u ++ v) i =
      (-1 : Int) ^ negCount v * signedCount u i + signedCount v i := by
  induction u with
  | nil => simp [signedCount]
  | cons l u ih =>
      cases l with
      | neg => simpa [signedCount] using ih
      | trans j =>
          simp only [List.cons_append, signedCount, negCount_append, pow_add]
          rw [ih]
          split_ifs <;> ring

private theorem negCount_replicate_trans {B : Nat} (n : Nat) (j : Fin B) :
    negCount (List.replicate n (.trans j)) = 0 := by
  induction n with
  | zero => simp [negCount]
  | succ n ih => simp [List.replicate, negCount, ih]

private theorem signedCount_replicate_trans {B : Nat} (n : Nat) (j i : Fin B) :
    signedCount (List.replicate n (.trans j)) i =
      if i = j then (n : Int) else 0 := by
  induction n with
  | zero => simp [signedCount]
  | succ n ih =>
      simp only [List.replicate_succ, signedCount, negCount_replicate_trans,
        pow_zero, ih]
      split_ifs <;> simp

private theorem pureWord_on_set {B : Nat} (s : Finset (Fin B))
    (k : Fin B → Nat) :
    ∃ w : List (Letter B), negCount w = 0 ∧
      (∀ i : Fin B, signedCount w i = if i ∈ s then (k i : Int) else 0) ∧
      w.length = ∑ i ∈ s, k i := by
  classical
  induction s using Finset.induction_on with
  | empty =>
      refine ⟨[], ?_, ?_, ?_⟩
      · rfl
      · intro i; simp [signedCount]
      · simp
  | @insert j s hj ih =>
      obtain ⟨w, hneg, hcount, hlen⟩ := ih
      let block : List (Letter B) := List.replicate (k j) (.trans j)
      refine ⟨block ++ w, ?_, ?_, ?_⟩
      · simp [negCount_append, negCount_replicate_trans, hneg, block]
      · intro i
        rw [signedCount_append, hneg, pow_zero, one_mul]
        rw [signedCount_replicate_trans, hcount]
        by_cases hij : i = j
        · subst i
          simp [Finset.mem_insert, hj]
        · simp [Finset.mem_insert, hij]
      · simp [block, List.length_append, hlen, Finset.sum_insert, hj]

def shadowWeight {B : Nat} (w : List (Letter B)) : Nat :=
  ∑ i : Fin B, (signedCount w i).natAbs

private theorem weight_cons_trans_le {B : Nat} (j : Fin B)
    (w : List (Letter B)) :
    shadowWeight (.trans j :: w) ≤ shadowWeight w + 1 := by
  classical
  calc
    shadowWeight (.trans j :: w) =
        ∑ i : Fin B,
          (signedCount w i + if i = j then (-1 : Int) ^ negCount w else 0).natAbs := by
            rfl
    _ ≤ ∑ i : Fin B,
          ((signedCount w i).natAbs +
            (if i = j then (-1 : Int) ^ negCount w else 0).natAbs) := by
          apply Finset.sum_le_sum
          intro i hi
          exact Int.natAbs_add_le _ _
    _ = shadowWeight w + 1 := by
          rw [Finset.sum_add_distrib]
          simp [shadowWeight, apply_ite]

private theorem weight_plus_negs_le_length {B : Nat} (w : List (Letter B)) :
    shadowWeight w + negCount w ≤ w.length := by
  induction w with
  | nil => simp [shadowWeight, negCount, signedCount]
  | cons l w ih =>
      cases l with
      | trans j =>
          have h := weight_cons_trans_le j w
          simp only [List.length_cons, negCount] at *
          omega
      | neg =>
          change shadowWeight w + (negCount w + 1) ≤ w.length + 1
          omega

private theorem count_nonneg_of_no_neg {B : Nat} (w : List (Letter B))
    (h : negCount w = 0) :
    ∀ i : Fin B, 0 ≤ signedCount w i := by
  induction w with
  | nil => intro i; simp [signedCount]
  | cons l w ih =>
      cases l with
      | trans j =>
          have hw : negCount w = 0 := by simpa [negCount] using h
          intro i
          have htail := ih hw i
          simp only [signedCount, hw, pow_zero]
          split_ifs <;> omega
      | neg =>
          simp [negCount] at h

def shadowPenalty {B : Nat} (e : Int) (a : Fin B → Int) : Nat :=
  if e = 1 then if ∀ i, 0 ≤ a i then 0 else 2 else 1

private theorem shadow_length_lower {B : Nat} (w : List (Letter B)) :
    shadowWeight w + shadowPenalty (shadowSign w) (signedCount w) ≤ w.length := by
  classical
  have hbase := weight_plus_negs_le_length w
  by_cases hs : shadowSign w = 1
  · by_cases hall : ∀ i : Fin B, 0 ≤ signedCount w i
    · simp [shadowPenalty, hs, hall]
      omega
    · push Not at hall
      obtain ⟨i, hi⟩ := hall
      have h0 : negCount w ≠ 0 := by
        intro heq
        have hn := count_nonneg_of_no_neg w heq i
        omega
      have h1 : negCount w ≠ 1 := by
        intro heq
        simp [shadowSign, heq] at hs
      have htwo : 2 ≤ negCount w := by omega
      simp [shadowPenalty, hs, show ¬∀ i : Fin B, 0 ≤ signedCount w i from by
        push Not; exact ⟨i, hi⟩]
      omega
  · have hneg : shadowSign w = -1 :=
      (shadowSign_eq_one_or_neg_one w).resolve_left hs
    have h0 : negCount w ≠ 0 := by
      intro heq
      simp [shadowSign, heq] at hneg
    have hone : 1 ≤ negCount w := by omega
    simp [shadowPenalty, hs]
    omega

def vectorWeight {B : Nat} (a : Fin B → Int) : Nat :=
  ∑ i : Fin B, (a i).natAbs

private theorem int_parts (z : Int) :
    (z.toNat : Int) - ((-z).toNat : Int) = z ∧
      z.natAbs = z.toNat + (-z).toNat := by
  constructor <;> omega

private theorem vectorWeight_parts {B : Nat} (a : Fin B → Int) :
    vectorWeight a =
      (∑ i : Fin B, (a i).toNat) + (∑ i : Fin B, (-(a i)).toNat) := by
  unfold vectorWeight
  rw [← Finset.sum_add_distrib]
  apply Finset.sum_congr rfl
  intro i hi
  exact (int_parts (a i)).2

private theorem pureWord {B : Nat} (k : Fin B → Nat) :
    ∃ w : List (Letter B), negCount w = 0 ∧
      (∀ i : Fin B, signedCount w i = (k i : Int)) ∧
      w.length = ∑ i : Fin B, k i := by
  simpa using pureWord_on_set (Finset.univ : Finset (Fin B)) k

private theorem oneNeg_count {B : Nat} (n p : List (Letter B))
    (hn : negCount n = 0) (hp : negCount p = 0) :
    negCount (n ++ (.neg :: p)) = 1 := by
  simp [negCount_append, negCount, hn, hp]

private theorem oneNeg_signed {B : Nat} (n p : List (Letter B))
    (hp : negCount p = 0) (i : Fin B) :
    signedCount (n ++ (.neg :: p)) i =
      signedCount p i - signedCount n i := by
  rw [signedCount_append]
  simp [negCount, hp, signedCount]
  ring

private theorem twoNeg_count {B : Nat} (p n : List (Letter B))
    (hp : negCount p = 0) (hn : negCount n = 0) :
    negCount (p ++ (.neg :: (n ++ [.neg]))) = 2 := by
  simp [negCount_append, negCount, hp, hn]

private theorem twoNeg_signed {B : Nat} (p n : List (Letter B))
    (hn : negCount n = 0) (i : Fin B) :
    signedCount (p ++ (.neg :: (n ++ [.neg]))) i =
      signedCount p i - signedCount n i := by
  rw [signedCount_append]
  have hcount : negCount (n ++ [.neg]) = 1 := by
    simp [negCount_append, negCount, hn]
  have hsigned : signedCount (n ++ [.neg]) i = -signedCount n i := by
    simpa [signedCount] using (oneNeg_signed n ([] : List (Letter B)) (by rfl) i)
  simp [negCount, hcount, signedCount, hsigned]
  ring

private theorem shadow_realized_with_length {B : Nat} (e : Int)
    (a : Fin B → Int) (he : e = 1 ∨ e = -1) :
    ∃ w : List (Letter B), shadowSign w = e ∧
      (∀ i : Fin B, signedCount w i = a i) ∧
      w.length = vectorWeight a + shadowPenalty e a := by
  classical
  obtain ⟨p, hp0, hpc, hplen⟩ := pureWord (fun i => (a i).toNat)
  obtain ⟨n, hn0, hnc, hnlen⟩ := pureWord (fun i => (-a i).toNat)
  have hweight := vectorWeight_parts a
  rcases he with he | he
  · subst e
    by_cases hall : ∀ i : Fin B, 0 ≤ a i
    · have hnegSum : (∑ i : Fin B, (-a i).toNat) = 0 := by
        apply Finset.sum_eq_zero
        intro i hi
        have hn := hall i
        omega
      refine ⟨p, ?_, ?_, ?_⟩
      · simp [shadowSign, hp0]
      · intro i
        rw [hpc i]
        have hn := hall i
        omega
      · simp [shadowPenalty, hall]
        omega
    · let w : List (Letter B) := p ++ (.neg :: (n ++ [.neg]))
      refine ⟨w, ?_, ?_, ?_⟩
      · simp [w, shadowSign, twoNeg_count p n hp0 hn0]
      · intro i
        rw [show signedCount w i = signedCount p i - signedCount n i from
          twoNeg_signed p n hn0 i, hpc i, hnc i]
        exact (int_parts (a i)).1
      · simp [w, hplen, hnlen, shadowPenalty, hall]
        omega
  · subst e
    let w : List (Letter B) := n ++ (.neg :: p)
    refine ⟨w, ?_, ?_, ?_⟩
    · simp [w, shadowSign, oneNeg_count n p hn0 hp0]
    · intro i
      rw [show signedCount w i = signedCount p i - signedCount n i from
        oneNeg_signed n p hp0 i, hpc i, hnc i]
      exact (int_parts (a i)).1
    · simp [w, hplen, hnlen, shadowPenalty]
      omega

/-- Exact shortest-word criterion for the translation/negation shadow.
The hypothesis says the sign belongs to the two-element parity factor. -/
theorem shadow_reachable_iff {B : Nat} (e : Int) (a : Fin B → Int)
    (he : e = 1 ∨ e = -1) (d : Nat) :
    (∃ w : List (Letter B), w.length ≤ d ∧ shadowSign w = e ∧
      ∀ i : Fin B, signedCount w i = a i) ↔
      vectorWeight a + shadowPenalty e a ≤ d := by
  constructor
  · rintro ⟨w, hlen, hsign, hcount⟩
    have hlower := shadow_length_lower w
    have ha : signedCount w = a := funext hcount
    have hw : shadowWeight w = vectorWeight a := by
      simp [shadowWeight, vectorWeight, hcount]
    rw [hw, hsign, ha] at hlower
    omega
  · intro hbound
    obtain ⟨w, hsign, hcount, hlen⟩ := shadow_realized_with_length e a he
    refine ⟨w, ?_, hsign, hcount⟩
    omega

end CryptoResearch.NCP

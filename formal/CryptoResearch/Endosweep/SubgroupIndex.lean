/-
Subgroup membership and cofactor clearing: the lattice index behind
`harness/endosweep/subgroup.py`.

Source: research/endosweep_subgroup_20261008/README.md ("The algebra" and the
appended "Lean verification" section)
Targets: formal/targets/endosweep-subgroup-index-gcd-minors.yaml
         formal/targets/endosweep-subgroup-ideal-index.yaml
         formal/targets/endosweep-subgroup-cp6-782-certificate.yaml
         formal/targets/endosweep-subgroup-bls12-381-control.yaml

The README turns membership tests and clearing maps into one exact integer
computation: for `β` in an imaginary quadratic order `O = Z[ω]` and
`I = (π - 1)O`, the index `[O : βO + I]` "is the gcd of the 2×2 minors of
`{β, βω, π−1, (π−1)ω}`" (`element_index`), and `β` is a valid membership test
iff it lies in `𝔯` and this index is `r`, a valid clearing map iff it is `h`.

WHAT IS PROVED HERE.

* `index_eq_minorGcd` -- for ANY finite list of vectors in `Z²` whose 2×2
  minors have nonzero gcd `d` (the quantity `element_index` computes), the
  quotient of `Z²` by their `Z`-span has exactly `d` classes: an explicit map
  `rep : Z² → ℕ` lands in `[0, d)`, hits every value, and identifies two
  vectors iff their difference lies in the span. This is `[Z² : L] = d`,
  stated with an explicit complete residue system instead of a cardinal.
* `ideal_index_eq_elementIndex` -- for `O = Z[ω]`, `ω² = τω − n`, and any
  `β, γ ∈ O`, the `Z`-span of `{β, βω, γ, γω}` is exactly the ideal
  `βO + γO`, so `O/(βO + γO)` has exactly `elementIndex τ n [β, γ]` classes.
  This is the correctness of `element_index` / `kernel_order`.
* `cp6_782_certificate`, `bls12_381_control` -- the recorded numbers of
  `subgroup.json`, checked by kernel evaluation (`decide`): `N(π) = p`,
  `Tr π = t`, `N(π − 1) = h·r`; for the chosen and the shortest membership
  elements `[O : βO + (π−1)O] = r`, `N(β) = r`, and `β` acts as 0 on `G`
  (`β ∈ 𝔯`); for the chosen and the shortest clearing elements and for the
  effective cofactor `e` the index is `h`; the module predictions
  `#E(F_p)[ℓ] = [O : ℓO + (π−1)O]` for the small `ℓ | h`; and for BLS12-381
  the control identities `N(u² + φ) = u⁴ − u² + 1 = r`, `φ` acting as `−u²`,
  `h = (u − 1)²/3`, and `1 − u` having index `h`.

WHAT IS NOT PROVED HERE.

* Lenstra's theorem `E(F_q) ≅ O/(π − 1)O` (an INPUT, cited as unverified in
  the README) and therefore anything about points: that `|ker β| = r` on the
  curve, that the tests are correct on `E(F_p)`, or the torsion counts.
* The finite-module step `|ker(β on O/I)| = [O : βO + I]` (first isomorphism
  theorem and Lagrange for the finite group `O/I`).
* That `End(E) = O_K`, that `π` is the Frobenius of the curve (only that the
  recorded `π` has norm `p` and trace `t`), and primality of `r` or `p`.
* Any cost, ratio or timing in the README: those are modelled counts.
-/
import Mathlib.Tactic.Ring

namespace CryptoResearch.Endosweep.SubgroupIndex

/-! ## Vectors of `Z²` and their spans -/

/-- A vector of `Z²`; in an order `Z[ω]` the pair `(a, b)` is `a + b·ω`. -/
abbrev V := Int × Int

/-- Vector addition. -/
def vadd (u v : V) : V := (u.1 + v.1, u.2 + v.2)
/-- Scalar multiplication by an integer. -/
def vsmul (k : Int) (u : V) : V := (k * u.1, k * u.2)
/-- Vector subtraction. -/
def vsub (u v : V) : V := (u.1 - v.1, u.2 - v.2)
/-- The 2×2 minor `det [u v]`. -/
def det2 (u v : V) : Int := u.1 * v.2 - u.2 * v.1

/-- `InSpan gs v`: `v` is an integer combination of the vectors in `gs`. -/
inductive InSpan (gs : List V) : V → Prop
  | zero : InSpan gs (0, 0)
  | gen {g : V} : g ∈ gs → InSpan gs g
  | add {u v : V} : InSpan gs u → InSpan gs v → InSpan gs (vadd u v)
  | smul (k : Int) {u : V} : InSpan gs u → InSpan gs (vsmul k u)

/-- gcd of the minors `det [g h]` for `h` in `hs`. -/
def rowGcd (g : V) : List V → Nat
  | [] => 0
  | h :: hs => Nat.gcd (det2 g h).natAbs (rowGcd g hs)

/-- gcd of all 2×2 minors `det [gᵢ gⱼ]`, `i < j`, of a list of vectors: the
quantity `element_index` in `harness/endosweep/subgroup.py` computes. -/
def minorGcd : List V → Nat
  | [] => 0
  | g :: gs => Nat.gcd (rowGcd g gs) (minorGcd gs)

/-! ### Elementary facts -/

theorem natCast_dvd_of_dvd_natAbs {d : Nat} {z : Int} (h : d ∣ z.natAbs) : (d : Int) ∣ z := by
  rcases h with ⟨k, hk⟩
  rcases Int.natAbs_eq z with hz | hz
  · exact ⟨k, by rw [hz, hk]; simp⟩
  · exact ⟨-(k : Int), by rw [hz, hk]; simp⟩

theorem dvd_natAbs_of_natCast_dvd {d : Nat} {z : Int} (h : (d : Int) ∣ z) : d ∣ z.natAbs := by
  rcases h with ⟨k, hk⟩
  exact ⟨k.natAbs, by rw [hk, Int.natAbs_mul]; simp⟩

theorem det2_self (g : V) : det2 g g = 0 := by simp only [det2]; ring

theorem det2_swap (g h : V) : det2 h g = -det2 g h := by simp only [det2]; ring

theorem det2_add_right (g u v : V) : det2 g (vadd u v) = det2 g u + det2 g v := by
  simp only [det2, vadd]; ring

theorem det2_smul_right (g : V) (k : Int) (u : V) : det2 g (vsmul k u) = k * det2 g u := by
  simp only [det2, vsmul]; ring

theorem det2_zero_right (g : V) : det2 g (0, 0) = 0 := by simp [det2]

theorem rowGcd_dvd (g : V) : ∀ {hs : List V} {h : V}, h ∈ hs → (rowGcd g hs : Int) ∣ det2 g h
  | [], _, hm => by simp at hm
  | h' :: hs, h, hm => by
    simp only [rowGcd]
    rcases List.mem_cons.1 hm with rfl | hm
    · exact natCast_dvd_of_dvd_natAbs (Nat.gcd_dvd_left _ _)
    · exact Int.dvd_trans (Int.natCast_dvd_natCast.2 (Nat.gcd_dvd_right _ _)) (rowGcd_dvd g hm)

theorem minorGcd_dvd : ∀ {gs : List V} {g h : V}, g ∈ gs → h ∈ gs →
    (minorGcd gs : Int) ∣ det2 g h
  | [], _, _, hg, _ => by simp at hg
  | g' :: gs, g, h, hg, hh => by
    simp only [minorGcd]
    have hl : ((Nat.gcd (rowGcd g' gs) (minorGcd gs) : Nat) : Int) ∣ (rowGcd g' gs : Int) :=
      Int.natCast_dvd_natCast.2 (Nat.gcd_dvd_left _ _)
    have hr : ((Nat.gcd (rowGcd g' gs) (minorGcd gs) : Nat) : Int) ∣ (minorGcd gs : Int) :=
      Int.natCast_dvd_natCast.2 (Nat.gcd_dvd_right _ _)
    rcases List.mem_cons.1 hg with rfl | hg' <;> rcases List.mem_cons.1 hh with rfl | hh'
    · rw [det2_self]; exact Int.dvd_zero _
    · exact Int.dvd_trans hl (rowGcd_dvd _ hh')
    · rw [det2_swap]; exact Int.dvd_neg.2 (Int.dvd_trans hl (rowGcd_dvd _ hg'))
    · exact Int.dvd_trans hr (minorGcd_dvd hg' hh')

theorem dvd_rowGcd {d : Nat} (g : V) : ∀ {hs : List V},
    (∀ h ∈ hs, (d : Int) ∣ det2 g h) → d ∣ rowGcd g hs
  | [], _ => Nat.dvd_zero _
  | h :: hs, H => by
    simp only [rowGcd]
    exact Nat.dvd_gcd (dvd_natAbs_of_natCast_dvd (H h (List.mem_cons_self ..)))
      (dvd_rowGcd g fun h' hh' => H h' (List.mem_cons_of_mem _ hh'))

theorem dvd_minorGcd {d : Nat} : ∀ {gs : List V},
    (∀ g ∈ gs, ∀ h ∈ gs, (d : Int) ∣ det2 g h) → d ∣ minorGcd gs
  | [], _ => Nat.dvd_zero _
  | g :: gs, H => by
    simp only [minorGcd]
    exact Nat.dvd_gcd
      (dvd_rowGcd g fun h hh => H g (List.mem_cons_self ..) h (List.mem_cons_of_mem _ hh))
      (dvd_minorGcd fun a ha b hb => H a (List.mem_cons_of_mem _ ha) b (List.mem_cons_of_mem _ hb))

/-! ### The minor gcd is an invariant of the lattice -/

theorem InSpan.mono {gs hs : List V} (H : ∀ g ∈ gs, InSpan hs g) {v : V} :
    InSpan gs v → InSpan hs v := by
  intro h
  induction h with
  | zero => exact InSpan.zero
  | gen hg => exact H _ hg
  | add _ _ ihu ihv => exact InSpan.add ihu ihv
  | smul k _ ih => exact InSpan.smul k ih

theorem InSpan.congr {gs : List V} {u v : V} (h : InSpan gs u) (e : u = v) : InSpan gs v :=
  e ▸ h

theorem InSpan.lin {gs : List V} {u v : V} (hu : InSpan gs u) (hv : InSpan gs v) (k l : Int) :
    InSpan gs (vadd (vsmul k u) (vsmul l v)) :=
  InSpan.add (InSpan.smul k hu) (InSpan.smul l hv)

theorem det2_span_dvd_right {gs : List V} {d : Int} {g : V}
    (H : ∀ h ∈ gs, d ∣ det2 g h) {w : V} (hw : InSpan gs w) : d ∣ det2 g w := by
  induction hw with
  | zero => rw [det2_zero_right]; exact Int.dvd_zero _
  | gen hh => exact H _ hh
  | add _ _ ihu ihv => rw [det2_add_right]; exact Int.dvd_add ihu ihv
  | smul k _ ih => rw [det2_smul_right]; exact Int.dvd_trans ih (Int.dvd_mul_left _ _)

/-- Every minor of two vectors OF THE LATTICE is a multiple of the minor gcd of
any generating list. -/
theorem minorGcd_dvd_det2_of_mem {gs : List V} {u w : V}
    (hu : InSpan gs u) (hw : InSpan gs w) : (minorGcd gs : Int) ∣ det2 u w := by
  have step : ∀ g ∈ gs, (minorGcd gs : Int) ∣ det2 g w := fun g hg =>
    det2_span_dvd_right (fun h hh => minorGcd_dvd hg hh) hw
  have step' : ∀ g ∈ gs, (minorGcd gs : Int) ∣ det2 w g := fun g hg => by
    rw [det2_swap]; exact Int.dvd_neg.2 (step g hg)
  rw [det2_swap]
  exact Int.dvd_neg.2 (det2_span_dvd_right step' hu)

/-- Two generating lists of the same lattice. -/
def SpanEq (gs hs : List V) : Prop :=
  (∀ g ∈ gs, InSpan hs g) ∧ (∀ h ∈ hs, InSpan gs h)

theorem SpanEq.symm {gs hs : List V} (h : SpanEq gs hs) : SpanEq hs gs := ⟨h.2, h.1⟩

theorem SpanEq.trans {gs hs ks : List V} (h1 : SpanEq gs hs) (h2 : SpanEq hs ks) :
    SpanEq gs ks :=
  ⟨fun g hg => InSpan.mono h2.1 (h1.1 g hg), fun k hk => InSpan.mono h1.2 (h2.2 k hk)⟩

theorem SpanEq.iff {gs hs : List V} (h : SpanEq gs hs) (v : V) : InSpan gs v ↔ InSpan hs v :=
  ⟨InSpan.mono h.1, InSpan.mono h.2⟩

theorem InSpan.of_subset {gs hs : List V} (H : ∀ g ∈ gs, g ∈ hs) {v : V} (h : InSpan gs v) :
    InSpan hs v :=
  InSpan.mono (fun g hg => InSpan.gen (H g hg)) h

theorem SpanEq.append {gs hs ks ls : List V} (h1 : SpanEq gs hs) (h2 : SpanEq ks ls) :
    SpanEq (gs ++ ks) (hs ++ ls) := by
  constructor
  · intro g hg
    rcases List.mem_append.1 hg with hg | hg
    · exact InSpan.of_subset (fun x hx => List.mem_append_left _ hx) (h1.1 g hg)
    · exact InSpan.of_subset (fun x hx => List.mem_append_right _ hx) (h2.1 g hg)
  · intro g hg
    rcases List.mem_append.1 hg with hg | hg
    · exact InSpan.of_subset (fun x hx => List.mem_append_left _ hx) (h1.2 g hg)
    · exact InSpan.of_subset (fun x hx => List.mem_append_right _ hx) (h2.2 g hg)

theorem SpanEq.refl (gs : List V) : SpanEq gs gs :=
  ⟨fun _ hg => InSpan.gen hg, fun _ hg => InSpan.gen hg⟩

/-- The minor gcd depends only on the lattice, not on the generating list. -/
theorem minorGcd_eq_of_spanEq {gs hs : List V} (h : SpanEq gs hs) :
    minorGcd gs = minorGcd hs :=
  Nat.dvd_antisymm
    (dvd_minorGcd fun _ hg _ hh => minorGcd_dvd_det2_of_mem (h.2 _ hg) (h.2 _ hh))
    (dvd_minorGcd fun _ hg _ hh => minorGcd_dvd_det2_of_mem (h.1 _ hg) (h.1 _ hh))

/-! ### Reduction to a triangular basis (Euclid on one coordinate) -/

/-- Euclid on a linear functional `f`: any two vectors span the same lattice as
two vectors the second of which `f` kills. -/
theorem reduce_pair (f : V → Int) (hadd : ∀ u v, f (vadd u v) = f u + f v)
    (hsmul : ∀ k u, f (vsmul k u) = k * f u) :
    ∀ (n : Nat) (u w : V), (f w).natAbs ≤ n → ∃ u' w', f w' = 0 ∧ SpanEq [u, w] [u', w'] := by
  intro n
  induction n with
  | zero =>
    intro u w hw
    exact ⟨u, w, Int.natAbs_eq_zero.1 (Nat.le_zero.1 hw), SpanEq.refl _⟩
  | succ n ih =>
    intro u w hw
    by_cases h0 : f w = 0
    · exact ⟨u, w, h0, SpanEq.refl _⟩
    · -- r = u - q*w with f r = f u % f w
      let q := f u / f w
      let r : V := vadd u (vsmul (-q) w)
      have hfr : f r = f u % f w := by
        simp only [r, hadd, hsmul]
        simp only [q]
        rw [Int.emod_def]; ring
      have hlt : (f r).natAbs ≤ n := by
        have h1 := Int.emod_lt (f u) h0
        have h2 := Int.emod_nonneg (f u) h0
        rw [hfr]; omega
      obtain ⟨u', w', hw', hs⟩ := ih w r hlt
      refine ⟨u', w', hw', SpanEq.trans ?_ hs⟩
      have hu : InSpan [w, r] u := by
        refine (InSpan.lin (InSpan.gen (List.mem_cons_of_mem _ (List.mem_cons_self ..)))
          (InSpan.gen (List.mem_cons_self ..)) 1 q).congr ?_
        simp only [r, vadd, vsmul]; ext <;> simp
      have hr : InSpan [u, w] r :=
        InSpan.add (InSpan.gen (List.mem_cons_self ..))
          (InSpan.smul _ (InSpan.gen (List.mem_cons_of_mem _ (List.mem_cons_self ..))))
      constructor
      · intro g hg
        simp only [List.mem_cons, List.not_mem_nil, or_false] at hg
        rcases hg with rfl | rfl
        · exact hu
        · exact InSpan.gen (List.mem_cons_self ..)
      · intro g hg
        simp only [List.mem_cons, List.not_mem_nil, or_false] at hg
        rcases hg with rfl | rfl
        · exact InSpan.gen (List.mem_cons_of_mem _ (List.mem_cons_self ..))
        · exact hr

theorem fst_eq_zero_of_inSpan {gs : List V} (H : ∀ g ∈ gs, g.1 = 0) {v : V}
    (h : InSpan gs v) : v.1 = 0 := by
  induction h with
  | zero => rfl
  | gen hg => exact H _ hg
  | add _ _ ihu ihv => simp [vadd, ihu, ihv]
  | smul k _ ih => simp [vsmul, ih]

/-- Every finite list of vectors spans the same lattice as a triangular pair
`(a, b), (0, c)` (Hermite normal form up to signs and reduction of `b`). -/
theorem exists_triangular : ∀ gs : List V, ∃ a b c : Int, SpanEq gs [(a, b), (0, c)]
  | [] => ⟨0, 0, 0, fun _ hg => by simp at hg, fun _ hg => by
      simp only [List.mem_cons, List.not_mem_nil, or_false] at hg
      rcases hg with rfl | rfl <;> exact InSpan.zero⟩
  | g :: gs => by
    obtain ⟨a, b, c, h⟩ := exists_triangular gs
    -- step 1: g :: gs  ~  [g, (a,b), (0,c)]
    have h1 : SpanEq (g :: gs) ([g] ++ [(a, b), (0, c)]) :=
      SpanEq.append (SpanEq.refl [g]) h
    -- step 2: reduce g, (a,b) on the first coordinate
    obtain ⟨u', w', hw', hred⟩ := reduce_pair (fun v => v.1) (fun _ _ => rfl) (fun _ _ => rfl)
      _ g (a, b) le_rfl
    have h2 : SpanEq ([g, (a, b)] ++ [(0, c)]) ([u', w'] ++ [(0, c)]) :=
      SpanEq.append hred (SpanEq.refl _)
    -- step 3: reduce w', (0,c) on the second coordinate
    obtain ⟨u'', w'', hw'', hred2⟩ := reduce_pair (fun v => v.2) (fun _ _ => rfl) (fun _ _ => rfl)
      _ w' (0, c) le_rfl
    have hfst : ∀ x ∈ [w', ((0 : Int), c)], x.1 = 0 := by
      intro x hx
      simp only [List.mem_cons, List.not_mem_nil, or_false] at hx
      rcases hx with rfl | rfl
      · exact hw'
      · rfl
    have hu1 : u''.1 = 0 :=
      fst_eq_zero_of_inSpan hfst (hred2.2 _ (List.mem_cons_self ..))
    have hw1 : w''.1 = 0 :=
      fst_eq_zero_of_inSpan hfst (hred2.2 _ (List.mem_cons_of_mem _ (List.mem_cons_self ..)))
    have h3 : SpanEq ([u'] ++ [w', (0, c)]) ([u'] ++ [u'', w'']) :=
      SpanEq.append (SpanEq.refl _) hred2
    -- step 4: drop w'' = 0
    have hw0 : w'' = (0, 0) := Prod.ext hw1 hw''
    have hu0 : u'' = (0, u''.2) := Prod.ext hu1 rfl
    have h4 : SpanEq [u', u'', w''] [(u'.1, u'.2), (0, u''.2)] := by
      constructor
      · intro x hx
        simp only [List.mem_cons, List.not_mem_nil, or_false] at hx
        rcases hx with rfl | rfl | rfl
        · exact InSpan.gen (List.mem_cons_self ..)
        · rw [hu0]; exact InSpan.gen (List.mem_cons_of_mem _ (List.mem_cons_self ..))
        · rw [hw0]; exact InSpan.zero
      · intro x hx
        simp only [List.mem_cons, List.not_mem_nil, or_false] at hx
        rcases hx with rfl | rfl
        · exact InSpan.gen (List.mem_cons_self ..)
        · rw [← hu0]; exact InSpan.gen (List.mem_cons_of_mem _ (List.mem_cons_self ..))
    exact ⟨u'.1, u'.2, u''.2, h1.trans (h2.trans (h3.trans h4))⟩

/-! ### The index of a triangular lattice -/

theorem inSpan_tri_iff (a b c : Int) (v : V) :
    InSpan [(a, b), (0, c)] v ↔ ∃ m n : Int, v = (m * a, m * b + n * c) := by
  constructor
  · intro h
    induction h with
    | zero => exact ⟨0, 0, by simp⟩
    | gen hg =>
      simp only [List.mem_cons, List.not_mem_nil, or_false] at hg
      rcases hg with rfl | rfl
      · exact ⟨1, 0, by simp⟩
      · exact ⟨0, 1, by simp⟩
    | add _ _ ihu ihv =>
      obtain ⟨m1, n1, rfl⟩ := ihu
      obtain ⟨m2, n2, rfl⟩ := ihv
      exact ⟨m1 + m2, n1 + n2, by simp only [vadd]; ext <;> simp <;> ring⟩
    | smul k _ ih =>
      obtain ⟨m, n, rfl⟩ := ih
      exact ⟨k * m, k * n, by simp only [vsmul]; ext <;> simp <;> ring⟩
  · rintro ⟨m, n, rfl⟩
    refine (InSpan.lin (InSpan.gen (List.mem_cons_self ..))
      (InSpan.gen (List.mem_cons_of_mem _ (List.mem_cons_self ..))) m n).congr ?_
    simp only [vadd, vsmul]; ext <;> simp

/-- Flipping the signs of the two triangular generators does not change the
lattice. -/
theorem tri_normalize (a b c : Int) :
    ∃ a' b' c' : Int, 0 ≤ a' ∧ 0 ≤ c' ∧ (a * c).natAbs = (a' * c').natAbs ∧
      SpanEq [(a, b), (0, c)] [(a', b'), (0, c')] := by
  have key : ∀ s t : Int, s * s = 1 → t * t = 1 →
      SpanEq [(a, b), (0, c)] [(s * a, s * b), (0, t * c)] := by
    intro s t hs ht
    have e1 : InSpan [(a, b), ((0 : Int), c)] (s * a, s * b) :=
      (InSpan.smul s (InSpan.gen (List.mem_cons_self ..))).congr rfl
    have e2 : InSpan [(a, b), ((0 : Int), c)] (0, t * c) :=
      (InSpan.smul t (InSpan.gen (List.mem_cons_of_mem _ (List.mem_cons_self ..)))).congr
        (by simp [vsmul])
    have f1 : InSpan [(s * a, s * b), ((0 : Int), t * c)] (a, b) :=
      (InSpan.smul s (InSpan.gen (List.mem_cons_self ..))).congr
        (by simp only [vsmul]; ext <;> simp <;> rw [← Int.mul_assoc, hs, Int.one_mul])
    have f2 : InSpan [(s * a, s * b), ((0 : Int), t * c)] (0, c) :=
      (InSpan.smul t (InSpan.gen (List.mem_cons_of_mem _ (List.mem_cons_self ..)))).congr
        (by simp only [vsmul, Int.mul_zero, ← Int.mul_assoc, ht, Int.one_mul])
    constructor
    · intro g hg
      simp only [List.mem_cons, List.not_mem_nil, or_false] at hg
      rcases hg with rfl | rfl
      · exact f1
      · exact f2
    · intro g hg
      simp only [List.mem_cons, List.not_mem_nil, or_false] at hg
      rcases hg with rfl | rfl
      · exact e1
      · exact e2
  have sgn : ∀ z : Int, ∃ s : Int, s * s = 1 ∧ 0 ≤ s * z := by
    intro z
    rcases Int.le_total 0 z with hz | hz
    · exact ⟨1, rfl, by omega⟩
    · exact ⟨-1, rfl, by omega⟩
  obtain ⟨s, hs, has⟩ := sgn a
  obtain ⟨t, ht, hct⟩ := sgn c
  refine ⟨s * a, s * b, t * c, has, hct, ?_, key s t hs ht⟩
  have : s * a * (t * c) = (s * t) * (a * c) := by ring
  rw [this, Int.natAbs_mul (s * t)]
  have hst : (s * t).natAbs = 1 := by
    have : (s * t) * (s * t) = 1 := by
      calc (s * t) * (s * t) = (s * s) * (t * t) := by ring
        _ = 1 := by rw [hs, ht]; rfl
    have h2 := congrArg Int.natAbs this
    rw [Int.natAbs_mul] at h2
    exact Nat.eq_one_of_mul_eq_one_right h2
  rw [hst, Nat.one_mul]

/-- The residue map of the triangular lattice `Z(a,b) + Z(0,c)`, `a, c > 0`:
`(x, y) ↦ c·(x mod a) + ((y − ⌊x/a⌋·b) mod c)`. -/
def triRep (a b c : Int) (v : V) : Nat :=
  c.toNat * (v.1 % a).toNat + ((v.2 - (v.1 / a) * b) % c).toNat

theorem exists_of_emod_eq {x y c : Int} (h : x % c = y % c) : ∃ n : Int, x - y = n * c := by
  have hx := Int.emod_add_ediv_mul x c
  have hy := Int.emod_add_ediv_mul y c
  exact ⟨x / c - y / c, by rw [Int.sub_mul]; omega⟩

theorem triRep_spec (a b c : Int) (ha : 0 < a) (hc : 0 < c) :
    (∀ v, triRep a b c v < (a * c).natAbs) ∧
    (∀ k, k < (a * c).natAbs → ∃ v, triRep a b c v = k) ∧
    (∀ v w, triRep a b c v = triRep a b c w ↔ InSpan [(a, b), (0, c)] (vsub v w)) := by
  have ha0 : a ≠ 0 := by omega
  have hc0 : c ≠ 0 := by omega
  have hA : (a.toNat : Int) = a := Int.toNat_of_nonneg (by omega)
  have hC : (c.toNat : Int) = c := Int.toNat_of_nonneg (by omega)
  have hCpos : 0 < c.toNat := by omega
  have hAC : (a * c).natAbs = c.toNat * a.toNat := by
    have : a * c = ((c.toNat * a.toNat : Nat) : Int) := by
      rw [Int.natCast_mul, hA, hC, Int.mul_comm]
    rw [this, Int.natAbs_natCast]
  -- bounds on the two digits
  have hi : ∀ x : Int, (x % a).toNat < a.toNat := fun x => by
    have := Int.emod_lt_of_pos x ha; have := Int.emod_nonneg x ha0; omega
  have hj : ∀ y : Int, (y % c).toNat < c.toNat := fun y => by
    have := Int.emod_lt_of_pos y hc; have := Int.emod_nonneg y hc0; omega
  -- decoding
  have dec : ∀ i j : Nat, j < c.toNat →
      (c.toNat * i + j) / c.toNat = i ∧ (c.toNat * i + j) % c.toNat = j := by
    intro i j hj
    refine ⟨?_, ?_⟩
    · rw [Nat.mul_add_div hCpos, Nat.div_eq_of_lt hj, Nat.add_zero]
    · rw [Nat.mul_add_mod, Nat.mod_eq_of_lt hj]
  refine ⟨?_, ?_, ?_⟩
  · intro v
    simp only [triRep]
    rw [hAC]
    have h1 := hi v.1
    have h2 := hj (v.2 - v.1 / a * b)
    calc c.toNat * (v.1 % a).toNat + ((v.2 - v.1 / a * b) % c).toNat
        < c.toNat * (v.1 % a).toNat + c.toNat := Nat.add_lt_add_left h2 _
      _ = c.toNat * ((v.1 % a).toNat + 1) := by rw [Nat.mul_add, Nat.mul_one]
      _ ≤ c.toNat * a.toNat := Nat.mul_le_mul_left _ h1
  · intro k hk
    rw [hAC] at hk
    have hq : k / c.toNat < a.toNat := by
      rw [Nat.div_lt_iff_lt_mul hCpos, Nat.mul_comm]; exact hk
    have hr : k % c.toNat < c.toNat := Nat.mod_lt _ hCpos
    refine ⟨((k / c.toNat : Nat), (k % c.toNat : Nat)), ?_⟩
    have q0 : (0 : Int) ≤ ((k / c.toNat : Nat) : Int) := Int.natCast_nonneg _
    have q1 : ((k / c.toNat : Nat) : Int) < a := by
      rw [← hA]; exact Int.ofNat_lt.2 hq
    have r0 : (0 : Int) ≤ ((k % c.toNat : Nat) : Int) := Int.natCast_nonneg _
    have r1 : ((k % c.toNat : Nat) : Int) < c := by
      rw [← hC]; exact Int.ofNat_lt.2 hr
    have e1 : ((k / c.toNat : Nat) : Int) % a = ((k / c.toNat : Nat) : Int) :=
      Int.emod_eq_of_lt q0 q1
    have e2 : ((k / c.toNat : Nat) : Int) / a = 0 := Int.ediv_eq_zero_of_lt q0 q1
    have e3 : ((k % c.toNat : Nat) : Int) % c = ((k % c.toNat : Nat) : Int) :=
      Int.emod_eq_of_lt r0 r1
    simp only [triRep, e1, e2, Int.zero_mul, Int.sub_zero, e3, Int.toNat_natCast]
    exact Nat.div_add_mod k c.toNat
  · intro v w
    rw [inSpan_tri_iff]
    obtain ⟨x, y⟩ := v
    obtain ⟨x', y'⟩ := w
    simp only [triRep, vsub]
    constructor
    · intro h
      have d1 := dec (x % a).toNat _ (hj (y - x / a * b))
      have d2 := dec (x' % a).toNat _ (hj (y' - x' / a * b))
      have hi' : (x % a).toNat = (x' % a).toNat := by rw [← d1.1, ← d2.1, h]
      have hj' : ((y - x / a * b) % c).toNat = ((y' - x' / a * b) % c).toNat := by
        rw [← d1.2, ← d2.2, h]
      have hi'' : x % a = x' % a := by
        have := Int.emod_nonneg x ha0; have := Int.emod_nonneg x' ha0; omega
      have hj'' : (y - x / a * b) % c = (y' - x' / a * b) % c := by
        have := Int.emod_nonneg (y - x / a * b) hc0
        have := Int.emod_nonneg (y' - x' / a * b) hc0; omega
      obtain ⟨n, hn⟩ := exists_of_emod_eq hj''
      have hx := Int.emod_add_ediv_mul x a
      have hx' := Int.emod_add_ediv_mul x' a
      refine ⟨x / a - x' / a, n, ?_⟩
      ext
      · simp only [Int.sub_mul]; omega
      · simp only [Int.sub_mul]; rw [← hn]; ring
    · rintro ⟨m, n, hmn⟩
      simp only [Prod.mk.injEq] at hmn
      obtain ⟨h1, h2⟩ := hmn
      have hx : x = x' + m * a := by omega
      have hq : x / a = x' / a + m := by rw [hx, Int.add_mul_ediv_right _ _ ha0]
      have hr : x % a = x' % a := by rw [hx, Int.add_mul_emod_self_right]
      have hy : y - x / a * b = (y' - x' / a * b) + n * c := by
        rw [hq]
        have : y = y' + m * b + n * c := by omega
        rw [this]; ring
      rw [hr, hy, Int.add_mul_emod_self_right]

/-! ## The index theorem -/

/-- **Index = gcd of the 2×2 minors.** For any finite list `gs` of vectors in
`Z²` whose 2×2 minors have nonzero gcd `d = minorGcd gs`, the lattice `L`
spanned by `gs` has index `d` in `Z²`: `rep` is a complete residue system for
`Z²/L` with exactly the values `0, …, d − 1`. -/
theorem index_eq_minorGcd (gs : List V) (hd : minorGcd gs ≠ 0) :
    ∃ rep : V → Nat,
      (∀ v, rep v < minorGcd gs) ∧
      (∀ k, k < minorGcd gs → ∃ v, rep v = k) ∧
      (∀ v w, rep v = rep w ↔ InSpan gs (vsub v w)) := by
  obtain ⟨a0, b0, c0, h0⟩ := exists_triangular gs
  obtain ⟨a, b, c, ha, hc, habs, hn⟩ := tri_normalize a0 b0 c0
  have h := h0.trans hn
  have he : minorGcd gs = (a * c).natAbs := by
    rw [minorGcd_eq_of_spanEq h]
    simp [minorGcd, rowGcd, det2]
  rw [he] at hd ⊢
  have ha' : 0 < a := by
    rcases Int.lt_or_eq_of_le ha with h1 | h1
    · exact h1
    · exact absurd (by rw [← h1]; simp) hd
  have hc' : 0 < c := by
    rcases Int.lt_or_eq_of_le hc with h1 | h1
    · exact h1
    · exact absurd (by rw [← h1]; simp) hd
  obtain ⟨h1, h2, h3⟩ := triRep_spec a b c ha' hc'
  exact ⟨triRep a b c, h1, h2, fun v w => (h3 v w).trans (h.iff _).symm⟩

/-! ## Ideals of an imaginary quadratic order -/

/-- Multiplication in `Z[ω]` with `ω² = τω − n` (`QO.multiply` with
`τ = D mod 2`, `n = (τ² − D)/4`). -/
def omul (τ n : Int) (x y : V) : V :=
  (x.1 * y.1 - x.2 * y.2 * n, x.1 * y.2 + y.1 * x.2 + x.2 * y.2 * τ)

/-- `QO.norm`: `N(a + bω) = a² + abτ + b²n`. -/
def onorm (τ n : Int) (x : V) : Int := x.1 * x.1 + x.1 * x.2 * τ + x.2 * x.2 * n

/-- `QO.trace`: `Tr(a + bω) = 2a + bτ`. -/
def otrace (τ : Int) (x : V) : Int := 2 * x.1 + x.2 * τ

/-- The vectors `g, gω` for each generator `g`, in the order `element_index`
lists them. -/
def idealVecs (τ n : Int) : List V → List V
  | [] => []
  | g :: gs => g :: omul τ n g (0, 1) :: idealVecs τ n gs

/-- `element_index` of `harness/endosweep/subgroup.py`. -/
def elementIndex (τ n : Int) (gens : List V) : Nat := minorGcd (idealVecs τ n gens)

/-- The `Z`-span of `{β, βω, γ, γω}` is the ideal `βO + γO`. -/
theorem inSpan_idealVecs_iff (τ n : Int) (β γ v : V) :
    InSpan (idealVecs τ n [β, γ]) v ↔ ∃ x y : V, v = vadd (omul τ n β x) (omul τ n γ y) := by
  constructor
  · intro h
    induction h with
    | zero => exact ⟨(0, 0), (0, 0), by simp [vadd, omul]⟩
    | gen hg =>
      simp only [idealVecs, List.mem_cons, List.not_mem_nil, or_false] at hg
      rcases hg with rfl | rfl | rfl | rfl
      · exact ⟨(1, 0), (0, 0), by simp only [vadd, omul]; ext <;> simp⟩
      · exact ⟨(0, 1), (0, 0), by simp only [vadd, omul]; ext <;> simp⟩
      · exact ⟨(0, 0), (1, 0), by simp only [vadd, omul]; ext <;> simp⟩
      · exact ⟨(0, 0), (0, 1), by simp only [vadd, omul]; ext <;> simp⟩
    | add _ _ ihu ihv =>
      obtain ⟨x1, y1, rfl⟩ := ihu
      obtain ⟨x2, y2, rfl⟩ := ihv
      exact ⟨vadd x1 x2, vadd y1 y2, by simp only [vadd, omul]; ext <;> simp <;> ring⟩
    | smul k _ ih =>
      obtain ⟨x, y, rfl⟩ := ih
      exact ⟨vsmul k x, vsmul k y, by simp only [vadd, vsmul, omul]; ext <;> simp <;> ring⟩
  · rintro ⟨⟨x1, x2⟩, ⟨y1, y2⟩, rfl⟩
    have g1 : InSpan (idealVecs τ n [β, γ]) β := InSpan.gen (by simp [idealVecs])
    have g2 : InSpan (idealVecs τ n [β, γ]) (omul τ n β (0, 1)) := InSpan.gen (by simp [idealVecs])
    have g3 : InSpan (idealVecs τ n [β, γ]) γ := InSpan.gen (by simp [idealVecs])
    have g4 : InSpan (idealVecs τ n [β, γ]) (omul τ n γ (0, 1)) := InSpan.gen (by simp [idealVecs])
    refine (InSpan.add (InSpan.lin g1 g2 x1 x2) (InSpan.lin g3 g4 y1 y2)).congr ?_
    simp only [vadd, vsmul, omul]; ext <;> simp <;> ring

/-- **Correctness of `element_index`.** For `β, γ` in `O = Z[ω]`, the quotient
`O/(βO + γO)` has exactly `elementIndex τ n [β, γ]` elements (when that is
nonzero): an explicit complete residue system. With `γ = π − 1` this is
`[O : βO + (π − 1)O]`, the quantity the README equates (via Lenstra's theorem,
NOT proved here) with `|ker β|` on `E(F_p)`. -/
theorem ideal_index_eq_elementIndex (τ n : Int) (β γ : V) (hd : elementIndex τ n [β, γ] ≠ 0) :
    ∃ rep : V → Nat,
      (∀ v, rep v < elementIndex τ n [β, γ]) ∧
      (∀ k, k < elementIndex τ n [β, γ] → ∃ v, rep v = k) ∧
      (∀ v w, rep v = rep w ↔ ∃ x y : V, vsub v w = vadd (omul τ n β x) (omul τ n γ y)) := by
  obtain ⟨rep, h1, h2, h3⟩ := index_eq_minorGcd (idealVecs τ n [β, γ]) hd
  exact ⟨rep, h1, h2, fun v w => (h3 v w).trans (inSpan_idealVecs_iff τ n β γ _)⟩

/-! ## Certificates for the recorded numbers (`subgroup.json`) -/

/-- `ω`'s trace for discriminant `D` (`QO.omega_trace_norm`). -/
def tauOf (D : Int) : Int := D % 2
/-- `ω`'s norm for discriminant `D`. -/
def nOf (D : Int) : Int := (tauOf D * tauOf D - D) / 4

/-! ### CP6-782 `G1`, `D = −339`, `α = 4 + ω` -/

namespace CP6

def D : Int := -339
def p : Int := 22369874298875696930346742206501054934775599465297184582183496627646774052458024540232479018147881220178054575403841904557897715222633333372134756426301062487682326574958588001132586331462553235407484089304633076250782629492557320825577
def r : Nat := 258664426012969094010652733694893533536393512754914660539884262666720468348340822774968888139573360124440321458177
def h : Nat := 86482221941698704497288378992285180119495364068003923046442785886272123124361700722982503222189455144364945735564951561028
def t : Int := 506464946133393486072777102926336625944849939610982267859828541006717966526573193706126370441346337661774335955699622
/-- `frobenius_in_O`. -/
def π : V := (509744978661319424131034070458523524277623607989291912034856950816825688315936961537798605328846203764079951636685059, -513025011189245362189291037990710422610397276367601556209885360626933410105300729369470840216346069866385567317670496)
def πm1 : V := (π.1 - 1, π.2)
/-- Eigenvalue of `α = 4 + ω` on `G` (`alpha.eigenvalue_on_G`). -/
def eα : Int := 43186290853954104629959174814933800890023549350211976988520814413901288501501318337259731161331116354215679741852
/-- `membership.chosen` (= `membership.shortest_valid`), `c0 + c1·α` with
`α = 4 + ω`, in `ω`-coordinates `(c0 + 4c1, c1)`. -/
def βmem : V := (-163015164859774491961626922044298380559301266097940651976 + 4 * 54517352290541778070718755726316304749147014769548935281, 54517352290541778070718755726316304749147014769548935281)
/-- `clearing.chosen`, `ω`-coordinates. -/
def βclr : V := (-11266769352321137173002500725640202284914883084052120948171534 + 4 * (-21632520577218387815520058795300607569361015830815655446835854), -21632520577218387815520058795300607569361015830815655446835854)
/-- `clearing.shortest_valid`, `ω`-coordinates. -/
def βclrShort : V := (-8108400932813260286696260277569970834770899834575782634520702 + 4 * (-216628748463674689685101529606426635992768646466563607111778), -216628748463674689685101529606426635992768646466563607111778)
/-- `effective_cofactor`. -/
def e : Int := 14413703656949784082881396498714196686582560678000653841073797647712020520726950120497083870364909190727490955927491926838

end CP6

/-- **CP6-782 certificate.** The recorded `π` has norm `p`, trace `t` and
`N(π − 1) = h·r`; the chosen membership element has norm `r`, acts as `0` on
`G` and has `[O : βO + (π−1)O] = r`; the chosen and shortest clearing elements
and the effective cofactor `e = h/6` have index `h`; and the module predictions
for `ℓ = 2, 3, 7, 29` are `4, 9, 7, 29`. -/
theorem cp6_782_certificate :
    tauOf CP6.D = 1 ∧ nOf CP6.D = 85 ∧
    onorm 1 85 CP6.π = CP6.p ∧ otrace 1 CP6.π = CP6.t ∧
    onorm 1 85 CP6.πm1 = (CP6.h : Int) * CP6.r ∧
    ((CP6.eα - 4) * (CP6.eα - 4) - (CP6.eα - 4) + 85) % (CP6.r : Int) = 0 ∧
    onorm 1 85 CP6.βmem = CP6.r ∧
    (CP6.βmem.1 + CP6.βmem.2 * (CP6.eα - 4)) % (CP6.r : Int) = 0 ∧
    elementIndex 1 85 [CP6.βmem, CP6.πm1] = CP6.r ∧
    elementIndex 1 85 [CP6.βclr, CP6.πm1] = CP6.h ∧
    elementIndex 1 85 [CP6.βclrShort, CP6.πm1] = CP6.h ∧
    (CP6.h : Int) = 6 * CP6.e ∧
    elementIndex 1 85 [(CP6.e, 0), CP6.πm1] = CP6.h ∧
    elementIndex 1 85 [(2, 0), CP6.πm1] = 4 ∧
    elementIndex 1 85 [(3, 0), CP6.πm1] = 9 ∧
    elementIndex 1 85 [(7, 0), CP6.πm1] = 7 ∧
    elementIndex 1 85 [(29, 0), CP6.πm1] = 29 := by
  decide

/-! ### BLS12-381 `G1` control, `D = −3`, `φ = ζ₃ = −1 + ω` -/

namespace BLS

def D : Int := -3
/-- arkworks `X = -0xd201000000010000`. -/
def u : Int := -0xd201000000010000
def p : Int := 4002409555221667393417789825735904156556882819939007885332058136124031650490837864442687629129015664037894272559787
def r : Nat := 52435875175126190479447740508185965837690552500527637822603658699938581184513
def h : Nat := 76329603384216526031706109802092473003
def t : Int := -15132376222941642751
def π : V := (-1155048275357884106335086113613464118783412807316232579754, 2310096550715768212670172227226928237551693238409523516757)
def πm1 : V := (π.1 - 1, π.2)
/-- `φ = −1 + ω` (`alpha`: `s = −1`, `b = 1`). -/
def φ : V := (-1, 1)
/-- `alpha.eigenvalue_on_G`. -/
def eφ : Int := 52435875175126190479447740508185965837461563690374988244538805122978187051009
/-- `−(u² + φ)` in `ω`-coordinates. -/
def βmem : V := (-(u * u - 1), -1)
/-- `membership.shortest_valid` (`c0 = −1`, `c1 = u² − 1`, i.e. `−1 + (u² − 1)φ`). -/
def βmemShort : V := (-1 - (u * u - 1), u * u - 1)

end BLS

/-- **BLS12-381 control.** `r = u⁴ − u² + 1 = N(u² + φ)`, `h = (u − 1)²/3`;
the recorded `π` has norm `p`, trace `t`, `N(π − 1) = h·r`; `φ` acts on `G` as
`−u²` (a root of `x² + x + 1`); `u² + φ ∈ 𝔯`; `−(u² + φ)` and the shortest
element `−1 + (u² − 1)φ` both have index `r`; `1 − u` has index `h`
(clearing) and is not in `𝔯`; module predictions `ℓ = 3 ↦ 3`, `ℓ = 11 ↦ 121`. -/
theorem bls12_381_control :
    tauOf BLS.D = 1 ∧ nOf BLS.D = 1 ∧
    (BLS.r : Int) = BLS.u ^ 4 - BLS.u ^ 2 + 1 ∧
    3 * (BLS.h : Int) = (BLS.u - 1) ^ 2 ∧
    onorm 1 1 (BLS.u * BLS.u + BLS.φ.1, BLS.φ.2) = BLS.r ∧
    onorm 1 1 BLS.βmem = BLS.r ∧
    onorm 1 1 BLS.π = BLS.p ∧ otrace 1 BLS.π = BLS.t ∧
    onorm 1 1 BLS.πm1 = (BLS.h : Int) * BLS.r ∧
    (BLS.eφ + BLS.u * BLS.u) % (BLS.r : Int) = 0 ∧
    (BLS.eφ * BLS.eφ + BLS.eφ + 1) % (BLS.r : Int) = 0 ∧
    (BLS.u * BLS.u + BLS.eφ - BLS.r) % (BLS.r : Int) = 0 ∧
    elementIndex 1 1 [BLS.βmem, BLS.πm1] = BLS.r ∧
    elementIndex 1 1 [BLS.βmemShort, BLS.πm1] = BLS.r ∧
    elementIndex 1 1 [(1 - BLS.u, 0), BLS.πm1] = BLS.h ∧
    (1 - BLS.u) % (BLS.r : Int) ≠ 0 ∧
    elementIndex 1 1 [(3, 0), BLS.πm1] = 3 ∧
    elementIndex 1 1 [(11, 0), BLS.πm1] = 121 := by
  decide

end CryptoResearch.Endosweep.SubgroupIndex

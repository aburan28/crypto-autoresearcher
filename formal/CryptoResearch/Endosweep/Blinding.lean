/-
Scalar blinding and GLV decomposition (item 10, "C5"): why `k + r·n` is erased,
and why lattice-vector blinding still reconstructs `k`.

Source:  research/endosweep_frob_blinding_20261008/README.md (Item 10, Finding 1,
         "Reconstruction", and the appended "Lean verification" section);
         harness/endosweep/blinding.py (`Decomposer.decompose_unreduced`,
         `blind`, `reconstructs`) and harness/endosweep/lattice.py
         (`ReducedLattice.decompose`).
Targets: formal/targets/endosweep-blinding-*.yaml

The README: "Classical scalar blinding k + r·n is erased by GLV decomposition,
because Babai depends only on k mod n"; "Decomposing k + r·n gave exactly v(k)
in 40 000 of 40 000 cases"; "Every blinded vector satisfies Σ x_i λ_i ≡ k
(mod n)". blinding.py's docstring gives the reason for the unreduced Babai
the erasure test actually runs: "(n, 0, ..., 0) is in L, so its coordinates in
the basis are integers and rounding commutes with the shift".

WHAT IS PROVED (core Lean; dimension `d` arbitrary).
* `decompose_mod_erases`: lattice.py's `decompose` starts from `k % n`, so ANY
  decomposition that is a function of `k mod n` returns the same vector for
  `k` and `k + r·n`.
* `babai_unreduced_erases` (the stronger fact, about `decompose_unreduced`,
  the routine the 40 000 erasure checks run): with rounding
  `c_i(K) = ⌊(2K·num_i + den_i)/(2·den_i)⌋` (`den_i > 0`; `num_i/den_i` is the
  first row of `B⁻¹`) and `v(K) = (K, 0, …, 0) - Σ_i c_i(K)·b_i`, if
  `(n, 0, …, 0) = Σ_i z_i b_i` with integer coordinates `z_i = n·num_i/den_i`,
  then `v(K + r·n) = v(K)` for every integer `r` and `K`.
* `blind_reconstructs` (C5 and naive alike): if `Σ v_i λ_i ≡ k (mod n)` and
  every basis vector `b_j` is in the relation lattice (`Σ_i b_{j,i} λ_i ≡ 0`),
  then `x = v + Σ_j r_j b_j` satisfies `Σ x_i λ_i ≡ k (mod n)` for ALL
  integers `r_j` (so for any bit sizes `e_j`).

WHAT IS NOT PROVED. The cost and distribution results are measurements, not
Lean claims: the extra `e/d` bits per coefficient, the doubling ratios
`d` and `(b+e)/(b/d+e)`, the min-entropy values (exact at `λ₁^∞`, the bound
`e - log₂ N(B)`, the `e = 16` enumerations), the MSB statistics, and the
on-point checks. Also not proved: that the harness's basis is LLL-reduced or
that `num_i/den_i` really is `B⁻¹`'s first row (that is the hypothesis
`(n, 0, …, 0) = Σ z_i b_i` with `z_i = n·num_i/den_i`).
-/

namespace CryptoResearch.Endosweep.Blinding

/-! ## Sums over `Fin d` (as lists, core only) -/

/-- `Σ_{i < d} f i`. -/
def vsum {d : Nat} (f : Fin d → Int) : Int := ((List.finRange d).map f).sum

theorem lsum_add {α : Type _} (l : List α) (f g : α → Int) :
    (l.map (fun i => f i + g i)).sum = (l.map f).sum + (l.map g).sum := by
  induction l with
  | nil => simp
  | cons a l ih => simp only [List.map_cons, List.sum_cons, ih]; omega

theorem lsum_mul {α : Type _} (l : List α) (c : Int) (f : α → Int) :
    (l.map (fun i => c * f i)).sum = c * (l.map f).sum := by
  induction l with
  | nil => simp
  | cons a l ih => simp only [List.map_cons, List.sum_cons, ih, Int.mul_add]

theorem lsum_zero {α : Type _} (l : List α) : (l.map (fun _ => (0 : Int))).sum = 0 := by
  induction l with
  | nil => simp
  | cons a l ih => simp only [List.map_cons, List.sum_cons, ih]; omega

theorem lsum_comm {α β : Type _} (l1 : List α) (l2 : List β) (F : α → β → Int) :
    (l1.map (fun i => (l2.map (fun j => F i j)).sum)).sum
      = (l2.map (fun j => (l1.map (fun i => F i j)).sum)).sum := by
  induction l1 with
  | nil => simp only [List.map_nil, List.sum_nil]; rw [lsum_zero]
  | cons a l ih =>
    simp only [List.map_cons, List.sum_cons]
    rw [ih, lsum_add]

theorem lsum_dvd {α : Type _} (n : Int) (l : List α) (f : α → Int) (h : ∀ i, n ∣ f i) :
    n ∣ (l.map f).sum := by
  induction l with
  | nil => simp
  | cons a l ih => simp only [List.map_cons, List.sum_cons]; exact Int.dvd_add (h a) ih

theorem vsum_add {d : Nat} (f g : Fin d → Int) :
    vsum (fun i => f i + g i) = vsum f + vsum g := lsum_add _ f g

theorem vsum_mul {d : Nat} (c : Int) (f : Fin d → Int) :
    vsum (fun i => c * f i) = c * vsum f := lsum_mul _ c f

theorem vsum_comm {d e : Nat} (F : Fin d → Fin e → Int) :
    vsum (fun i => vsum (fun j => F i j)) = vsum (fun j => vsum (fun i => F i j)) :=
  lsum_comm _ _ F

/-! ## (a) Decomposition of `k mod n` -/

/-- lattice.py's `decompose` begins with `k % n`; any decomposition of that form
returns the same vector for `k` and `k + r·n`. -/
theorem decompose_mod_erases {V : Type _} (dec : Int → V) (n k r : Int) :
    dec ((k + r * n) % n) = dec (k % n) := by
  rw [Int.add_mul_emod_self_right]

/-! ## (b) Unreduced Babai rounding commutes with the shift by `n` -/

variable {d : Nat}

/-- blinding.py's rounding `c = (2·K·num + den) // (2·den)` (round half up). -/
def roundCoeff (K num den : Int) : Int := (2 * K * num + den) / (2 * den)

/-- `decompose_unreduced`: `v(K) = (K, 0, …, 0) - Σ_i c_i(K)·b_i`, coordinate `j`
of `d + 1` (the loop of blinding.py subtracts the same terms one at a time). -/
def decomposeUnreduced (num den : Fin (d + 1) → Int) (b : Fin (d + 1) → Fin (d + 1) → Int)
    (K : Int) (j : Fin (d + 1)) : Int :=
  (if j = 0 then K else 0) - vsum (fun i => roundCoeff K (num i) (den i) * b i j)

theorem roundCoeff_shift (K num den z r n : Int) (hden : 0 < den) (hz : n * num = den * z) :
    roundCoeff (K + r * n) num den = roundCoeff K num den + r * z := by
  unfold roundCoeff
  have e : 2 * (K + r * n) * num + den = (2 * K * num + den) + (r * z) * (2 * den) := by
    have : 2 * (K + r * n) * num = 2 * K * num + 2 * r * (n * num) := by grind
    rw [this, hz]; grind
  rw [e, Int.add_mul_ediv_right _ _ (by omega)]

/-- **Classical blinding is erased by unreduced Babai rounding.** If
`(n, 0, …, 0) = Σ_i z_i b_i` with `n·num_i = den_i·z_i` (the coordinates of
`(n, 0, …, 0)` in the basis are the integers `z_i = n·num_i/den_i`), then
`decompose_unreduced (K + r·n) = decompose_unreduced K`. -/
theorem babai_unreduced_erases (num den z : Fin (d + 1) → Int)
    (b : Fin (d + 1) → Fin (d + 1) → Int) (n : Int)
    (hden : ∀ i, 0 < den i) (hz : ∀ i, n * num i = den i * z i)
    (hlat : ∀ j, vsum (fun i => z i * b i j) = if j = 0 then n else 0)
    (K r : Int) (j : Fin (d + 1)) :
    decomposeUnreduced num den b (K + r * n) j = decomposeUnreduced num den b K j := by
  unfold decomposeUnreduced
  have hshift : (fun i => roundCoeff (K + r * n) (num i) (den i) * b i j)
      = (fun i => roundCoeff K (num i) (den i) * b i j + r * (z i * b i j)) := by
    funext i
    rw [roundCoeff_shift K (num i) (den i) (z i) r n (hden i) (hz i)]
    grind
  rw [hshift, vsum_add, vsum_mul, hlat j]
  split <;> grind

/-! ## (c) Lattice-vector blinding reconstructs `k` -/

/-- `Σ_i x_i λ_i`. -/
def dot (x l : Fin d → Int) : Int := vsum (fun i => x i * l i)

/-- `v + Σ_j r_j b_j` (blinding.py `blind`). -/
def blind {e : Nat} (v : Fin d → Int) (r : Fin e → Int) (b : Fin e → Fin d → Int) :
    Fin d → Int :=
  fun i => v i + vsum (fun j => r j * b j i)

theorem dot_blind {e : Nat} (v l : Fin d → Int) (r : Fin e → Int) (b : Fin e → Fin d → Int) :
    dot (blind v r b) l = dot v l + vsum (fun j => r j * dot (b j) l) := by
  unfold dot blind
  have e1 : (fun i => (v i + vsum (fun j => r j * b j i)) * l i)
      = (fun i => v i * l i + vsum (fun j => r j * b j i * l i)) := by
    funext i
    have : vsum (fun j => r j * b j i) * l i = vsum (fun j => r j * b j i * l i) := by
      rw [Int.mul_comm, ← vsum_mul]; congr 1; funext j; grind
    rw [Int.add_mul, this]
  rw [e1, vsum_add, vsum_comm]
  congr 1; congr 1; funext j
  rw [← vsum_mul]; congr 1; funext i; grind

/-- **Blinding by any relation-lattice combination preserves reconstruction.** -/
theorem blind_reconstructs {e : Nat} (n k : Int) (v l : Fin d → Int) (r : Fin e → Int)
    (b : Fin e → Fin d → Int) (hv : n ∣ dot v l - k) (hb : ∀ j, n ∣ dot (b j) l) :
    n ∣ dot (blind v r b) l - k := by
  rw [dot_blind]
  have hs : n ∣ vsum (fun j => r j * dot (b j) l) :=
    lsum_dvd n _ _ (fun j => by obtain ⟨c, hc⟩ := hb j; exact ⟨r j * c, by rw [hc]; grind⟩)
  have : dot v l + vsum (fun j => r j * dot (b j) l) - k
      = (dot v l - k) + vsum (fun j => r j * dot (b j) l) := by omega
  rw [this]; exact Int.dvd_add hv hs

end CryptoResearch.Endosweep.Blinding

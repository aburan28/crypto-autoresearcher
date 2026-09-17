/-
A degree-`q·deg f` upper bound on where the Frobenius twist of a system
generator appears in the field-equation filtration -- uniform in the number of
variables.

WHAT IS PROVED. Over a field `k` of exponential characteristic `p`, with
`q = p^e` and `FE = {x_i^q - x_i}` the degree-`q` field equations:

  `frobenius_degree_fall`      `g^q - g^{(q)} ∈ V FE (q · deg g)` for every `g`
  `frobeniusTwist_mem_V`       `f^{(q)} ∈ V (F ∪ FE) (q · deg f)` for `f ∈ F`
  `degreeFall_frobeniusTwist_le`  hence `d_{f^{(q)}} ≤ q · deg f`
  `totalDegree_frobeniusTwist` and `deg f^{(q)} = deg f`

Here `f^{(q)} = map (iterateFrobenius k p e) f` is the coefficientwise Frobenius
twist, and `V` is the Caminata-Gorla Definition 1.5 filtration from
`CryptoResearch.FallDegree.LastFall`.

WHY THIS IS THE "BOUNDED" STATEMENT. The variable type `σ` is arbitrary and
appears nowhere on the right-hand side of any bound. For a Weil descent to
`F_{2^n}` one takes `σ = Fin (n · m)`, and the bound stays `q · deg f`. So the
degree at which this particular fall is produced does not grow with `n`. That is
the whole n-independence content, and it is exactly that much.

WHAT IS NOT PROVED, and each of these is load-bearing.

1. NON-VACUITY. The theorems are upper bounds: `f^{(q)}` appears BY degree
   `q · deg f`. Nothing here shows it does not appear earlier, so nothing here
   exhibits a fall of any particular size. A genuine fall needs
   `f^{(q)} ∉ V (F ∪ FE) d` for `d < q · deg f`, a lower bound on the closure,
   and that is not proved -- the same gap flagged in `LastFall.lean`.

2. THIS IS `D_ff`, NOT `D_ff^max`. The quantity bounded is the plain
   Petit-style first fall degree (definition 1 of the four inequivalent ones
   catalogued in `KN-OPEN-7f0511`). Nagao's `D_ff^max` -- the maximum over
   invertible recombinations `M` of the generators, which is the definition
   relevant to F4 and the one he states on the record he could not establish
   for Weil-descent systems -- is NOT bounded here. `D_ff^max ≥ D_ff`, so a
   bound on `D_ff` says nothing about it.

3. NO LINK TO THE SOLVING DEGREE. The step from a first fall degree to the
   solving degree is refuted in general (Caminata-Gorla section 4, recorded in
   `CORR-20260916-0c9c0a`). Nothing here repairs it.

4. `deg f` IS AN INPUT. The bound is uniform in the variable count but linear in
   `deg f`. Whether the generators of the descended Semaev system have
   `n`-independent total degree is a separate fact about that system, not
   formalised here.

Source: research/THM_SEMAEV_FALL1.md (Corollary 1), extended to a degree-bounded
        membership statement.
Depends on: CryptoResearch.FallDegree.LastFall (Definition 1.5, `V`).
-/
import CryptoResearch.FallDegree.LastFall
import Mathlib.Algebra.MvPolynomial.CommRing
import Mathlib.Algebra.CharP.Frobenius
import Mathlib.Algebra.CharP.Reduced

namespace CryptoResearch.FallDegree

open MvPolynomial

variable {σ k : Type*} [Field k]

/-- The field equations `x_i^q - x_i`, as a generating set. -/
def fieldEqGens (σ k : Type*) [Field k] (q : ℕ) : Set (MvPolynomial σ k) :=
  Set.range fun i : σ => (X i : MvPolynomial σ k) ^ q - X i

/-- Total weight of an exponent vector. -/
def wt (s : σ →₀ ℕ) : ℕ := s.sum fun _ e => e

theorem fe_mem_V {q : ℕ} (hq : 1 ≤ q) (i : σ) :
    ((X i : MvPolynomial σ k) ^ q - X i) ∈ V (fieldEqGens σ k q) q := by
  refine mem_V_of_mem_of_totalDegree_le ⟨i, rfl⟩ ?_
  refine (totalDegree_sub _ _).trans ?_
  simp [totalDegree_X_pow, hq]

theorem X_pow_sub_mem_V {q : ℕ} (hq : 1 ≤ q) (i : σ) (a : ℕ) :
    ((X i : MvPolynomial σ k) ^ (q * a) - X i ^ a) ∈ V (fieldEqGens σ k q) (q * a) := by
  induction a with
  | zero => simp
  | succ a ih =>
    have hkey : ((X i : MvPolynomial σ k) ^ (q * (a + 1)) - X i ^ (a + 1))
        = ((X i : MvPolynomial σ k) ^ q - X i) * X i ^ (q * a)
          + ((X i : MvPolynomial σ k) ^ (q * a) - X i ^ a) * X i := by
      rw [Nat.mul_succ]
      ring
    rw [hkey]
    refine Submodule.add_mem _ ?_ ?_
    · have hmem := V_mono (fieldEqGens σ k q) (Nat.le_mul_of_pos_right q (Nat.succ_pos a))
        (fe_mem_V hq i)
      refine mul_mem_V hmem ?_
      have h1 : ((X i : MvPolynomial σ k) ^ q - X i).totalDegree ≤ q :=
        totalDegree_le_of_mem_V (fe_mem_V hq i)
      have h2 : ((X i : MvPolynomial σ k) ^ (q * a)).totalDegree = q * a := by
        simp [totalDegree_X_pow]
      have h3 : q * (a + 1) = q * a + q := by ring
      omega
    · have hmem := V_mono (fieldEqGens σ k q)
        (Nat.mul_le_mul_left q (Nat.le_succ a)) ih
      refine mul_mem_V hmem ?_
      have h1 := totalDegree_le_of_mem_V ih
      have h2 : ((X i : MvPolynomial σ k)).totalDegree = 1 := totalDegree_X i
      have : q * a + q = q * (a + 1) := by ring
      omega

theorem wt_zero : wt (0 : σ →₀ ℕ) = 0 := rfl

theorem wt_single_add {i : σ} {a : ℕ} {t : σ →₀ ℕ} :
    wt (Finsupp.single i a + t) = a + wt t := by
  unfold wt
  rw [Finsupp.sum_add_index' (fun _ => rfl) (fun _ _ _ => rfl),
    Finsupp.sum_single_index rfl]

theorem wt_smul (q : ℕ) (s : σ →₀ ℕ) : wt (q • s) = q * wt s := by
  unfold wt
  rw [Finsupp.sum_smul_index (fun _ => rfl), Finsupp.mul_sum]

theorem totalDegree_monomial_one (s : σ →₀ ℕ) :
    (monomial s (1 : k)).totalDegree = wt s := totalDegree_monomial s one_ne_zero

/-- **The monomial degree fall.** `x^{q·s} - x^{s}` lies in the field-equation
filtration already at degree `q · wt s`. -/
theorem monomial_sub_mem_V {q : ℕ} (hq : 1 ≤ q) (s : σ →₀ ℕ) :
    ((monomial (q • s) (1 : k)) - monomial s 1) ∈ V (fieldEqGens σ k q) (q * wt s) := by
  induction s using Finsupp.induction with
  | zero => simp
  | single_add i a t _ _ ih =>
    have hsmul : q • (Finsupp.single i a + t) = Finsupp.single i (q * a) + q • t := by
      rw [smul_add, Finsupp.smul_single, smul_eq_mul]
    have hA : (monomial (q • (Finsupp.single i a + t)) (1 : k))
        = (X i : MvPolynomial σ k) ^ (q * a) * monomial (q • t) 1 := by
      rw [hsmul, monomial_single_add]
    have hB : (monomial (Finsupp.single i a + t) (1 : k))
        = (X i : MvPolynomial σ k) ^ a * monomial t 1 := monomial_single_add
    have hkey : (monomial (q • (Finsupp.single i a + t)) (1 : k)) - monomial (Finsupp.single i a + t) 1
        = ((monomial (q • t) (1 : k)) - monomial t 1) * (X i : MvPolynomial σ k) ^ a
          + ((X i : MvPolynomial σ k) ^ (q * a) - X i ^ a) * monomial (q • t) 1 := by
      rw [hA, hB]; ring
    rw [hkey, wt_single_add]
    have hwt : q * (a + wt t) = q * a + q * wt t := by ring
    refine Submodule.add_mem _ ?_ ?_
    · have hmem := V_mono (fieldEqGens σ k q)
        (show q * wt t ≤ q * (a + wt t) by omega) ih
      refine mul_mem_V hmem ?_
      have h1 := totalDegree_le_of_mem_V ih
      have h2 : ((X i : MvPolynomial σ k) ^ a).totalDegree = a := by simp [totalDegree_X_pow]
      have h3 : a ≤ q * a := Nat.le_mul_of_pos_left a hq
      omega
    · have hmem := V_mono (fieldEqGens σ k q)
        (show q * a ≤ q * (a + wt t) by omega) (X_pow_sub_mem_V hq i a)
      refine mul_mem_V hmem ?_
      have h1 := totalDegree_le_of_mem_V (X_pow_sub_mem_V (k := k) hq i a)
      have h2 : ((monomial (q • t) (1 : k))).totalDegree = q * wt t := by
        rw [totalDegree_monomial_one, wt_smul]
      omega

theorem V_mono_set {F G : Set (MvPolynomial σ k)} (h : F ⊆ G) (i : ℕ) :
    V F i ≤ V G i := by
  refine sInf_le_sInf ?_
  rintro W ⟨hG, hmul⟩
  exact ⟨fun f hf hdeg => hG f (h hf) hdeg, hmul⟩

theorem pow_mem_V {F : Set (MvPolynomial σ k)} {f : MvPolynomial σ k} {d n : ℕ}
    (hf : f ∈ F) (hdeg : f.totalDegree ≤ d) (hn : 1 ≤ n) :
    f ^ n ∈ V F (n * d) := by
  induction n with
  | zero => omega
  | succ n ih =>
    rcases Nat.eq_zero_or_pos n with rfl | hn'
    · simpa using
        V_mono F (by omega) (mem_V_of_mem_of_totalDegree_le (i := f.totalDegree) hf le_rfl)
    · have hbase : f ∈ V F ((n + 1) * d) :=
        mem_V_of_mem_of_totalDegree_le hf (hdeg.trans (Nat.le_mul_of_pos_left d (by omega)))
      have hprev : (f ^ n).totalDegree ≤ n * d :=
        (totalDegree_pow f n).trans (Nat.mul_le_mul_left n hdeg)
      have : f * f ^ n ∈ V F ((n + 1) * d) := by
        refine mul_mem_V hbase ?_
        have : (n + 1) * d = d + n * d := by ring
        omega
      simpa [pow_succ, mul_comm] using this


section Frobenius

variable {p e : ℕ} [ExpChar k p]

theorem frobenius_degree_fall (g : MvPolynomial σ k) :
    g ^ p ^ e - map (iterateFrobenius k p e) g
      ∈ V (fieldEqGens σ k (p ^ e)) (p ^ e * g.totalDegree) := by
  have hq : 1 ≤ p ^ e := Nat.one_le_pow _ _ (expChar_pos k p)
  have hpow : g ^ p ^ e = ∑ s ∈ g.support, monomial ((p ^ e) • s) ((g.coeff s) ^ p ^ e) := by
    conv_lhs => rw [g.as_sum]
    rw [← iterateFrobenius_def, map_sum]
    exact Finset.sum_congr rfl fun s _ => by
      rw [iterateFrobenius_def, monomial_pow]
  have hmap : map (iterateFrobenius k p e) g
      = ∑ s ∈ g.support, monomial s ((g.coeff s) ^ p ^ e) := by
    conv_lhs => rw [g.as_sum]
    rw [map_sum]
    exact Finset.sum_congr rfl fun s _ => by
      rw [map_monomial, iterateFrobenius_def]
  rw [hpow, hmap, ← Finset.sum_sub_distrib]
  refine Submodule.sum_mem _ fun s hs => ?_
  have hterm : (monomial ((p ^ e) • s) ((g.coeff s) ^ p ^ e) - monomial s ((g.coeff s) ^ p ^ e))
      = ((g.coeff s) ^ p ^ e) • ((monomial ((p ^ e) • s) (1 : k)) - monomial s 1) := by
    rw [smul_sub, smul_monomial, smul_monomial, smul_eq_mul, mul_one]
  rw [hterm]
  refine Submodule.smul_mem _ _ ?_
  refine V_mono (fieldEqGens σ k (p ^ e)) ?_ (monomial_sub_mem_V hq s)
  exact Nat.mul_le_mul_left _ (le_totalDegree hs)

/-- **The first fall is bounded, and the bound does not mention the number of
variables.**

For any generator `f` of a system over a field of exponential characteristic
`p`, the Frobenius twist `f^{(q)}` (`q = p^e`, Frobenius applied to the
coefficients) is produced by the system together with the degree-`q` field
equations at working degree `q · deg f`, while `deg f^{(q)} = deg f`.

`σ` is an arbitrary type, so this bound is uniform in the number of variables:
the only quantities on the right are `q` and `deg f`. -/
theorem frobeniusTwist_mem_V {F : Set (MvPolynomial σ k)} {f : MvPolynomial σ k}
    (hf : f ∈ F) :
    map (iterateFrobenius k p e) f
      ∈ V (F ∪ fieldEqGens σ k (p ^ e)) (p ^ e * f.totalDegree) := by
  have hq : 1 ≤ p ^ e := Nat.one_le_pow _ _ (expChar_pos k p)
  have hpow : f ^ p ^ e ∈ V (F ∪ fieldEqGens σ k (p ^ e)) (p ^ e * f.totalDegree) :=
    pow_mem_V (Set.mem_union_left _ hf) le_rfl hq
  have hfall : f ^ p ^ e - map (iterateFrobenius k p e) f
      ∈ V (F ∪ fieldEqGens σ k (p ^ e)) (p ^ e * f.totalDegree) :=
    V_mono_set Set.subset_union_right _ (frobenius_degree_fall f)
  simpa using Submodule.sub_mem _ hpow hfall

/-- The same, read off as a bound on `d_f`. -/
theorem degreeFall_frobeniusTwist_le {F : Set (MvPolynomial σ k)}
    {f : MvPolynomial σ k} (hf : f ∈ F) :
    degreeFall (F ∪ fieldEqGens σ k (p ^ e)) (map (iterateFrobenius k p e) f)
      ≤ p ^ e * f.totalDegree :=
  degreeFall_le (frobeniusTwist_mem_V hf)

/-- The degree of the element produced. Over a domain the Frobenius twist has
exactly the degree of `f`, so the drop from the working degree `q · deg f` is
`(q - 1) · deg f`: linear in `deg f` and independent of the variable count. -/
theorem totalDegree_frobeniusTwist (f : MvPolynomial σ k) :
    (map (iterateFrobenius k p e) f).totalDegree = f.totalDegree :=
  by rw [totalDegree, totalDegree, support_map_of_injective f (iterateFrobenius_inj k p e)]


end Frobenius

end CryptoResearch.FallDegree

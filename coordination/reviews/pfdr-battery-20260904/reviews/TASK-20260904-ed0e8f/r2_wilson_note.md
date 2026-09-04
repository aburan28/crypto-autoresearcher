# R2 — exactness, the Wilson dependence, and the scope of the refutation of
# IDEA-20260830-84cdb7 H1

Task TASK-20260904-ed0e8f (red team), joint R2. Derivation note (labelled
derivation, never proved). Numbers from `r2_results.json` (`r2_wilson.py`).
Scope: d = 2, the tested (m, s, p).

Result of the joint: **breaks (narrowly)** — the exactness conclusion survives
and is strengthened, but (D4)'s stated REASON for it is false, and
"refuted by derivation" over-states what the s ≤ 8 check contributes.

---

## 1. Which bound does the refutation need?

84cdb7 H1: *there is a constant D_0 depending on m and d but not on s, p or the
curve with `d_ff(m,d,s) ≤ D_0` for every s with `d^s ≤ p`.*

* The **upper** bound `d_ff ≤ m e + floor((s-e)/2) + 1` (dimension count, given
  H-TOP) is unconditional and **cannot refute H1**: a bounded `d_ff` is
  perfectly compatible with an upper bound that grows.
* Refuting H1 needs a **lower** bound growing in s, i.e. that no annihilator of
  `S~_top` exists in degrees `j ≤ (s-e)/2`, i.e. that
  `m_{ell^e} : A_j → A_{j+e}` has maximal rank there. That is exactly H-WIL /
  Wilson's rank formula. **The refutation is carried entirely by the lower
  bound.**
* Consequently "**refuted at s ≤ 8 unconditionally**" is not a refutation at
  all: no finite set of s can refute a boundedness statement. The unconditional
  content of the s ≤ 8 check is "d_ff is not constant on 2 ≤ s ≤ 8 and takes
  the closed-form values there". Correct wording: **"H1 is refuted at d = 2,
  m = 2 conditional on H-WIL (equivalently on Wilson's rank theorem), with
  H-WIL verified unconditionally at s ≤ 8, e = 2, p ∈ {4099, 65537}."**

## 2. The reason (D4) gives for full rank is FALSE; the conclusion is right

(D4) says: *"multiplication by (sum a_i)^e from degree j to j+e is e! times the
transpose of the inclusion matrix W_{j,j+e}, and for p > s every
binom(k−i, t−i) is a positive integer below p, so the rank is binom(s,j)."*

With `t = j`, `k = j + e` the diagonal entries are `binom(j+e-i, j-i)
= binom(r+e, e)` for `r = 0..j`, whose maximum is `binom(j+e, e) ≤ binom(s, e)`.
For s ≥ 5 and e = 2 this can exceed p while still p > s. **Witness, computed:**
s = 10, j = 4, e = 2, p = 11: the diagonal entries are 1, 3, 6, 10, **15 ≥ p**,
so "below p" is false; the rank is nevertheless **210 = min(C(10,4), C(10,6))**,
full, for both `ell = Σ2^i a_i` and `ell = Σ a_i` (and likewise at p = 13).

The correct reason is **Kummer/Lucas**: every diagonal entry is
`binom(r+e, e)` with `r + e ≤ s < p`, and `p ∤ binom(N, K)` whenever `N < p`
(no carries in base p). Two further invertibility facts (D4) does not state but
needs, both implied by `p > s ≥ e`: `e! ≢ 0 (mod p)` (its prime factors are
≤ e ≤ s), and the rescaling `a_i ↦ 2^{-i} a_i` used to turn `Σ2^i a_i` into
`Σ a_i` is a graded automorphism of A only because 2 is invertible.

Under the hypothesis's own standing assumption `2^s ≤ p` the stated reason
happens to be true (all binomials `binom(N,K)` with `N ≤ s` are `< 2^s ≤ p`),
so the defect is in the parenthetical "for p > s", not in anything the
experiment used. It should be corrected rather than relied on.

## 3. The H-WIL control's dynamic range — and what the package could not see

The 112-cell table is at p ∈ {4099, 65537}, where `2^s ≤ p` at every s tested.
The parameter that is supposed to destroy the signal is p. Sweeping it (own
code, `e = 2`, s = 2..10, all j, p ∈ {2,3,5,7,11,13,4099}):

* **79 cells with rank strictly below `min(C(s,j), C(s,j+2))`** — 45 at p = 2,
  28 at p = 3, 6 at p = 5. Smallest: s = 4, j = 1, p = 3: rank 3 instead of 4,
  because the diagonal entry `binom(3,2) = 3 ≡ 0 (mod 3)`.
* **Zero drops at any cell with p > s.**
* At `e = 4` (never checked by the package; see R0-OBS-2): 32 drops, all at
  p ≤ s; zero drops at p > s; all 56 cells at p = 65537, s = 4..10, both `ell`
  kinds, full rank.

So (i) H-WIL is a real condition with dynamic range, not an identity — the
control could have failed and does fail for p ≤ s; (ii) the producer's two
primes sit so far inside the safe region that the table could not have failed,
which is a fact about the table's diagnosticity, not an error; (iii) the
condition `p > s` is sufficient but not necessary (e.g. s = 6, j = 2, p = 5 is
full rank, since 1, 3, 6 are all nonzero mod 5).

The producer's 112-cell table was independently reproduced cell for cell by
`r2_wilson.py` (112/112 at the maximum).

## 4. e = 4 and the m = 3 cells

The direct check covers `e = 2` only, so the *unconditional* part of the
exactness claim is `m = 2`. The two m = 3 cells do not need e = 4 exactness:
at (3,2,4) and (3,2,5) the claimed `a_0` is 1, which requires only
`ell^4 ≠ 0` in A (true for s ≥ 4) plus a kernel in degree 1 (automatic since
`C(s,1) > C(s,5)` at s = 4, 5). So nothing at m = 3 in this package rests on
H-WIL at all. For the closed form at m = 3 and **larger** s, e = 4 exactness is
required and was untested by the package; my sweep supplies it for s ≤ 10 at
p ∈ {7, 11, 13, 65537} (no drop with p > s).

## 5. Quantifier check

`quantifier_order` claims for ALL s with `2^{m-1} ≤ s` and `2^s ≤ p`. Coverage:

| claim component | unconditional coverage established | conditional beyond |
|---|---|---|
| upper bound `a_0 ≤ floor((s-e)/2)+1` | all s (dimension count), given H-TOP | H-TOP at m ≥ 5 (see R3: m ≤ 4 now checked) |
| lower bound (exactness) at e = 2 | s ≤ 10, p ∈ {2,…,13, 4099, 65537} with the p > s pattern; producer: s ≤ 8, two primes | Wilson's theorem for all s |
| lower bound at e = 4 | s ≤ 10 (this review) | Wilson for all s |
| refutation of H1 | none (a finite s-range cannot refute boundedness) | entirely Wilson |

## 6. Tensor-kernel identity and minimal-degree bookkeeping (checked)

`ker(M_1 ⊗ … ⊗ M_m) = Σ_k A_1 ⊗ … ⊗ ker M_k ⊗ … ⊗ A_m` for linear maps over a
field is elementary and correct, and gives `AI_p = min_k a_0(A_k, ell_k^e)`; in
the graded setting the degree-`a_0` part of the kernel is
`⊕_k (ker M_k)_{a_0} ⊗ (degree-0 parts of the other blocks)`, m summands of
dimension `C(s,a_0) − C(s,a_0+e)` each, hence
`m[C(s,a_0) − C(s,a_0+e)]`. This matches the frozen `fall_dim` arithmetic and
the measured `top_rank` at every cell (e.g. (3,2,5): rows 15, top_rank 3,
15 − 3 = 12 = 3[C(5,1) − C(5,5)]). The bookkeeping is correct; the identity's
translation into the METER's `fall_dim` is what fails (R1).

## 7. Provenance of Wilson (1990)

`H-PFDR-4148b8` records HEUR-002's support as "retrieved, SNIPPET LEVEL ONLY
(WebSearch by the idea-generator, 2026-09-03); the paper was not fetched."
This task performed an **independent second retrieval on 2026-09-04**
(WebSearch), which returned the same statement — R. M. Wilson, *A diagonal form
for the incidence matrix of t-subsets vs. k-subsets*, European J. Combin. 11
(1990) 609–615: for `t ≤ min(k, v−k)` the diagonal entries are
`binom(k−i, t−i)` with multiplicity `binom(v,i) − binom(v,i−1)`, and the mod-p
rank is the sum of those multiplicities over the i with `p ∤ binom(k−i, t−i)`.
**The primary text was still not opened**: ScienceDirect returned HTTP 403, and
two open-access secondary sources (an Electronic J. Combinatorics note by
de Caen; arXiv:1612.08124) were fetched but their PDFs could not be
text-extracted in this environment (no `pdftotext`, no `pdfminer`). Provenance
therefore remains **snippet level, now doubly sourced**, and the record's
disclosure is accurate. The *used consequence* no longer depends on the
citation for s ≤ 10, e ∈ {2,4}: it is directly computed here.

# R1 — the fall_dim identity, the row-independence hypothesis, and the
# boundary-cell block-factored-null anomaly

Task TASK-20260904-ed0e8f (red team), joint R1. **Everything below labelled
"derivation" is a derivation, not a proof reviewed by anyone else** (per
`docs/claims-and-verification.md`, "Refutation artifacts", item 2). Every
number is from `r1_results.json`, `r1b_results.json`, `r1c_results.json`,
computed with the independent meter `rt_meter.py`. Scope: d = 2, the tested
(m, s, p).

Result of the joint: **breaks** — (D4)'s fall_dim identity and (D6)'s "the
block-factored null reproduces d_ff and fall_dim exactly" are false as written,
in two independent ways, one of which the producer did not observe.

---

## 1. Derivation: what `fall_dim` measures

Let `B = F_p[a_1..a_n]/(a_i^2 - a_i)` with squarefree monomials indexed by
subsets, and `A = F_p[a]/(a_i^2)` the associated graded algebra. For subsets
u, v: `x^u x^v = x^{u ∪ v}` in B, of degree `|u ∪ v| ≤ |u| + |v|` with equality
iff `u ∩ v = ∅`; in A the product is `x^{u ∪ v}` if disjoint and 0 otherwise.
Hence `gr(B) = A` and, for any g of degree δ with top part `g_top ∈ A_δ`:

* **(1)** the degree-D component of `x^μ g` (|μ| = D − δ) equals `x^μ · g_top`
  computed in A. So the "top matrix" `H_D` of the meter is exactly the matrix
  of `m_{g_top} : A_{D-δ} → A_D`, and
  `top_rank(D) = rank(m_{g_top}|A_{D-δ})`.
* **(2)** `full_rank(D) = dim span_B {x^μ g : |μ| = D − δ} ≤ C(n, D-δ)`.
* **(3)** therefore
  `fall_dim(D) = full_rank(D) − top_rank(D)
              = dim ker(m_{g_top}|A_{D-δ}) − dim Rel_D`,
  where `Rel_D = { h ∈ span{monomials of degree D−δ} : h·g = 0 in B }`.

**(D4)'s identity `fall_dim(d_ff) = m[C(s,a_0) − C(s,a_0+e)]` therefore holds
iff `Rel_{d_ff} = 0`, i.e. iff the rows are linearly independent in B. (D4) as
written contains no such hypothesis.**

* **(4) Exact characterisation of `Rel_D`.** B is the ring of functions
  `{0,1}^n → F_p` (pointwise product). So `h·g = 0` in B iff `h` vanishes on
  `supp(g) = {ω ∈ {0,1}^n : g(ω) ≠ 0}`. Writing `N_sol = 2^n − |supp(g)|` (for
  the Semaev arm, the number of digit-vector decompositions of the target — the
  covariate of `IDEA-20260806-7ea402`, recorded per draw as `N_sol`):

  > `Rel_D = { h of squarefree degree exactly D − δ : h|_{supp(g)} = 0 }`,
  > and `full_rank(D) ≤ |supp(g)| = 2^n − N_sol`.

  This is the ONE channel through which the curve, the target and the ideal's
  solution set reach the meter. It is invisible in `top_rank`, which depends
  only on `g_top` and hence (by H-TOP) not on (a, b, x_R, p) at all.

* **(5) A rigorous sufficient condition.** A nonzero multilinear polynomial of
  degree k over any field is nonzero at ≥ `2^{n-k}` points of `{0,1}^n`. So if
  `N_sol < 2^{n-(D-δ)}` then no nonzero h of degree D−δ can vanish on
  `supp(g)`, `Rel_D = 0`, and the identity holds. At the first fall
  `D − δ = a_0`, so:

  > **(D4-fixed)** If `N_sol < 2^{ms - a_0}` then
  > `fall_dim(d_ff) = m[C(s,a_0) − C(s,a_0+e)]`.

  At every tested cell the margin is enormous — required
  `N_sol < 8, 32, 64, 256, 512, 2^11, 2^14` at (2,2,2), (2,2,3), (2,2,4),
  (2,2,5), (2,2,6), (3,2,4), (3,2,5); observed `N_sol ∈ {1, 2, 6}`. Verified
  post hoc directly in the run records: `full_rank == rows` at **272 of 272**
  Semaev layers and **1490 of 1490** NULL-1 layers, and fails at **35 of 240**
  NULL-2 layers (all of them the homogeneous block-factored null at the
  boundary cells). So the missing hypothesis is TRUE at every Semaev draw in
  the package; it is the statement, not the measurement, that is wrong.

## 2. Why the homogeneous block-factored null collapses at s = e

At a boundary cell (`s = e`, i.e. (2,2,2) and (3,2,4)) each block form
`q_k` of degree e in s = e variables is `c_k` times the single squarefree
monomial `a_{k,0}···a_{k,s-1}`, so `g = c · x^{[n]}`. As a function on
`{0,1}^n`, `x^{[n]}` is nonzero only at the all-ones point, so
`|supp(g)| = 1`, `N_sol = 2^n − 1`, and by (2)+(4) `full_rank(D) = 1` for every
D. Hence `fall_dim = 1` at the first fall, against the Semaev arm's 4 and 12 —
**not by an approximation, but forced**: no homogeneous block-factored null can
give any other value at s = e. The producer's frozen prediction P3 ("FORCED 0
difference at every cell") was mathematically impossible at two of its seven
cells.

Measured (my objects, own RNG seed 20260904, producer null seeds not reused):

| cell | homogeneous block-factored null | inhomogeneous block-factored null | Semaev |
|---|---|---|---|
| (2,2,2), p = 4099 and 65537 | (5, **1**), full_rank 1 of 4 rows, 2 reps each | (5, **4**), rows independent (densities 1.0 and 0.25; 2 reps each) | (5, 4) |
| (3,2,4), p = 65537 | (13, **1**), full_rank 1 of 12 rows, 2 reps | (13, **12**) at densities 1.0, 0.25, 0.05, 2 reps each | (13, 12) |
| (2,2,3) | (5, 4) | (5, 4) | (5, 4) |
| (3,2,5) | (13, 12) | (13, 12) | (13, 12) |

**Conclusion for F2.** The boundary discrepancy is HOMOGENEITY, not curve
information: a curve-free, target-free, x_R-free block-factored null with
random sub-top terms reproduces (5, 4) and (13, 12) exactly. **F2 ("the first
fall carries curve or target information") is NOT live**, and the
curve-independence conclusion survives for d_ff everywhere tested and for
fall_dim at the strict-early-fall cells.

At very sparse sub-top density (0.05) the inhomogeneous null at (2,2,2)
sometimes returns fall_dim 1 or 2 — fall_dim at the boundary is a continuous
function of how much sub-top structure the object carries, which is the
positive statement of the same fact.

## 3. The boundary cells have NO dynamic range (the producer did not say this)

The executor recorded that NULL-2 fails to reproduce `fall_dim` at the boundary
cells. The sharper fact is that at those cells nothing could have failed on the
`d_ff` side:

* At (2,2,2), δ = 4 = n, so `A_4` is one-dimensional: **every** generator of
  degree 4 has the same top form up to a scalar, and `A_5 = 0`, so
  `top_rank(5) = 0` and `d_ff = 5` for every generator of degree 4 whatsoever.
  The Semaev arm, the support-matched null (measured 5 at 60/60) and the
  block-factored null are the same object as far as `d_ff` is concerned.
* At (3,2,4), δ = 12 = n and the same argument gives `d_ff = 13` for every
  degree-12 generator. Both cells are `d_ff = n + 1`: **degree exhaustion, not
  a degree fall.**
* Control run: a dense random polynomial with **no block structure at all**
  returns (5, 4) at (2,2,2) and (13, 12) at (3,2,4) (2 reps each, both primes)
  — the agreement of NULL-2 with the Semaev arm at the boundary cells is not
  evidence about block structure.

So the two cells where P3 "failed" are exactly the two cells that carry no
information about the mechanism, and the five cells where P3 held are the ones
that do. This does not weaken the claim; it re-scopes what the boundary cells
were ever able to support.

## 4. A NEW null the package did not run, and what it shows

Holding the generator degree and the inhomogeneity fixed and varying ONLY the
block factorisation of the top form (`generic_homogeneous_top`: a uniformly
random homogeneous degree-δ form in all ms variables plus dense sub-top terms):

| cell | block-factored | generic degree-δ top form | Semaev | D_null |
|---|---|---|---|---|
| (2,2,3) | (5, 4) | **(6, 14)**, 2 reps × 2 primes | (5, 4) | 6 |
| (3,2,5) | (13, 12) | **(14, 90)**, 2 reps | (13, 12) | 14 |

This is a cleaner control than NULL-1: NULL-1 matches S~'s monomial SUPPORT
(and so changes the degree profile as well), whereas this object changes only
the block factorisation. It separates by one degree at both strict cells, which
strengthens the mechanism claim. Recommended as a required control for any
successor.

## 5. A counterexample INSIDE the hypothesis's own quantifier

`H-PFDR-4148b8.proof_search_map.quantifier_order` claims, for all p > 3, all s
with `2^{m-1} ≤ s` and `2^s ≤ p`, all non-singular E/F_p and all affine targets.
The experiment tested p ∈ {4099, 65537} only. `r1b_rowdep_sweep.py` sweeps the
SMALLEST primes the hypothesis itself allows, **exhaustively over every
non-singular curve and every affine target**:

* s = 2, p ∈ {5,7,11,13,17,19,23,29,31,37,41}: 195,094 instances;
* s = 3, p ∈ {11,13,17,19,23}: 26,000 instances.

**Two instances deviate, both at s = 2:**

| p | a | b | x_R | 4a³+27b² | d_ff | fall_dim | frozen fall_dim | N_sol |
|---|---|---|---|---|---|---|---|---|
| 13 | 12 | 3 | 11 | 5 (non-singular; a,b ≠ 0 so j ∉ {0,1728}) | 5 | **3** | 4 | 8 |
| 19 | 2 | 15 | 9 | 8 (non-singular; a,b ≠ 0) | 5 | **3** | 4 | 8 |

Both instances are inside the hypothesis's declared range AND inside the
experiment's own generic-j curve class. At p = 13 all four window
x-coordinates {0,1,2,3} are on the curve (the experiment's own curve filter
requires a ≠ 0, b ≠ 0, non-singular and **at least two** on-curve x in [0,4);
this curve passes all four conditions) and x_R = 11 has 8 digit decompositions,
so it is a plantable target of exactly the kind the experiment draws. Verified two independent ways: polynomial arithmetic in B, and direct
numeric evaluation of `S_3(u_1, u_2, x_R)` at all 16 digit points (agreement
checked point by point).

**Mechanism, exactly as predicted by (4)+(5) above:** at p = 13 the generator
vanishes precisely on the 8 points with `a_{1,0} ≠ a_{2,0}`, so the linear form
`h = a_{1,0} − a_{2,0}` vanishes on `supp(S~)`, `dim Rel_5 = 1`, and
`fall_dim = 4 − 1 = 3`. The sufficient condition of (5) requires
`N_sol < 2^{4-1} = 8`; the counterexample sits at `N_sol = 8` exactly, so **the
bound is sharp**.

`d_ff` is unaffected (5 in both cases), and no deviation was found at s = 3 in
26,000 exhaustive instances, nor at s = 2 for p ≥ 23. The exception is rare
(2 in 195,094 at s = 2) and rarer as p grows, which is exactly why the
experiment's two large primes could not have found it and why an exhaustive
small-p sweep is the cheapest discriminating control.

## 6. Corrected statements

* **(D4-fixed).** `d_ff(m,2,s) = m 2^{m-1} + floor((s-2^{m-1})/2) + 1` under
  H-TOP and H-WIL, as claimed (no counterexample found; see R2). The second
  clause becomes: `fall_dim(d_ff) = m[C(s,a_0) − C(s,a_0+e)] − dim Rel_{d_ff}`,
  with `Rel_{d_ff} = {h of degree a_0 vanishing on supp(S~)}`, which is zero
  whenever `N_sol < 2^{ms - a_0}` — a condition that holds at every tested
  Semaev draw and fails at two exhaustively-found instances at (2,2,2).
* **Where the false clause entered.** `IDEA-20260903-e1e38b` (D6) claims only
  that the block-factored null *"reproduces d_ff = m e + floor((s−e)/2) + 1
  exactly"*, with a genericity reason ("a random degree-e form in A_k has the
  same maximal-rank multiplication maps as ell_k^e in degrees where either has
  full rank") that says nothing about fall_dim. `H-PFDR-4148b8` (D6) states
  *"reproduces d_ff **and fall_dim** exactly"*, and prediction P3 freezes
  "FORCED 0 at every cell" for both integers. **The clause that fails was added
  between the proposal and the hypothesis record.** (The row-independence gap in
  the fall_dim identity itself is present in both, in (D4).)
* **(D6-fixed).** "the block-factored null reproduces d_ff and fall_dim
  exactly" holds for `d_ff` at every tested cell, and for `fall_dim` at the
  strict-early-fall cells only. At `s = e` the HOMOGENEOUS block-factored null
  necessarily gives `fall_dim = 1`; the inhomogeneous one reproduces the
  Semaev value. Neither statement is about the curve.
* **P3 as frozen** ("FORCED 0 at every cell") is false at (2,2,2) and (3,2,4)
  and was unsatisfiable there by construction. P3 survives, restated, at the
  five strict-early-fall cells, where it is 0/0 on 10 (m = 2) resp. 5 (m = 3)
  distinct null objects per cell.
* **Curve-independence** should be stated as: the first fall degree is
  curve-independent because `S~_top` is (H-TOP); the fall DIMENSION is
  curve-independent only away from the row-collapse locus, which is an
  ideal-level (solution-count) condition and is not vacuous.

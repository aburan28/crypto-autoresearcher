---
id: KN-OPEN-7f0511
type: open_problem
title: >-
  Nagao names the first-fall-degree definition under which his own assumption is
  plausible -- the maximum over invertible recombinations of the generators --
  and says on the record that he cannot prove Weil-descent systems satisfy it.
  Which of the four inequivalent definitions now in this corpus does a degree-4
  GF(2) Macaulay rank actually bound, and does the O(1) slack his Assumption 1
  carries and 2015/984's drops change the exponent of the polynomial-time claim?
tags: [nagao, first-fall-degree, fake-first-fall-degree, degree-of-regularity,
  solving-degree, macaulay, groebner, f4, weil-descent, field-equations,
  basis-change, definitional-gap, assumption-1, instrument-validity,
  asymptotic-exponent, characteristic-two, ecdlp, open]
confidence: reported
status: open
source_refs: [KN-LIT-c5dceb, KN-LIT-ebd657, KN-LIT-71b758, KN-LIT-fa346d,
  KN-OPEN-d218ec, RQ-SEMBIN-9e8f82]
added: 2026-09-13
superseded_by: null
---

## Statement

Reading Nagao ePrint 2013/549 (`KN-LIT-c5dceb`, frozen at
`inputs/NAGAO-2013-549/`) beside ePrint 2015/984 (`KN-LIT-71b758`) puts **four
inequivalent quantities** in this corpus, all called "the first fall degree", all
carrying an assumption of the same name, and all being cited interchangeably:

1. **`D_ff` (Petit-style).** 2013/549 Definition 1, page 3. The minimal `D` such
   that some `Σ g_i f_i` is nonzero, of degree `< D`, with `max_i deg(g_i f_i) =
   D`. No field equations enter.
2. **`D_ff^max := max_M D_ff(M)`.** 2013/549 page 3, same section. For any
   invertible `l × l` matrix `M` over the base field, set `(f^{(M)}_i) := M(f_i)`
   and define `D_ff(M)` for the recombined generators; take the maximum over all
   `M`. Nagao introduces it because the plain version has known counterexamples,
   and says the assumption "seems to be true" for this one.
3. **`d_F` (true).** 2015/984 Definition 5. Petit-style again, but stated over
   `F_p[X_1..X_N]` for the descended system.
4. **`d'_F` (fake).** 2015/984 Definition 6. The same, with every degree taken
   **modulo the field equations** `S_fe`. This is the only one of the four a
   Macaulay-rank computation over GF(2) can produce, because it is the only one
   whose degrees are degrees of reduced representatives.

Three things about this set are open, and each is checkable.

**(A) The definition the author believes is the one he could not discharge.**
2013/549, page 3, in Nagao's own words: *"For my opinion, if there are many
`l`-ple `(g_1, ..., g_l)` ... satisfying the definition of first fall degree,
assumption seems to be true. For example, for any `l × l` size invertible matrix
`M`, put ... Put first fall degree `D_ff := max_M D_ff(M)`. **However, by using
this new assumption, I can not prove that the equations system coming from Weil
descent have low first fall degree in strict way and it remains a future
work.**"* Two pages earlier, on the plain version he then proceeds to use: *"This
assumption has some counter examples and Petit et al. assume that the polynomials
`f_1, ..., f_l` are general polynomials. However, if `f_1, ..., f_l` are randomly
chosen, the value of `D_ff` seems to be very large. In our situation, we treat
only the cases that `D_ff ~ max_i deg f_i` and so, `f_1, ..., f_l` cannot be
randomly chosen."* So the author states (i) that the assumption he uses has
counterexamples, (ii) that his systems are deliberately outside the genericity
hypothesis under which it is normally assumed, and (iii) that the repaired
version he finds credible is one he cannot establish for exactly the systems at
issue. **Nobody has taken up that future work, and nothing in this repository
records whether `D_ff^max` is bounded for a Weil-descended Semaev system at any
parameters at all.**

`D_ff^max >= D_ff` by construction (the identity matrix is one `M`), so the
recombination version is the *harder* condition — and it is the one relevant to
an algorithm, because F4 recombines generators. A measurement of `D_ff` that
comes out at 4 says nothing about `D_ff^max`.

**(B) Which quantity a degree-4 Macaulay rank bounds.** The instrument this
program is designing measures `d'_F` — the fake degree — because that is what a
GF(2) Macaulay matrix at a fixed degree can see. The chain that carries a
measurement back to a claim is:

> `d'_F` measured → `d_F <= d'_F` (2015/984 **Lemma 4**, stated with **no proof
> printed**) → `d_F` bounded → Assumption 1 applied to `d_F` → cost.

`KN-LIT-c5dceb` establishes that the *ingredient* for Lemma 4 is genuinely proved
in 2013/549 (its Lemma 2, page 4, proof pages 4–5: an element of the
field-equation ideal of degree `D` can be rewritten with coefficients of degree
`<= D − p`). What is **not** anywhere in either frozen paper is the assembled
inequality `d_F <= d'_F` with an argument. And **nothing at all** connects either
of them to `D_ff^max`. So the measured quantity is three unproved or unexamined
steps away from the quantity the assumption is about, and the steps are not the
same steps in the two papers.

**(C) The `O(1)` that one paper carries and the other drops.** 2013/549's
Assumption 1 (page 3) reads: *"Upper bound of the degree of the polynomial for
computing Gröbner basis of `f_1, ..., f_l` of F4 algorithm is `D_ff + O(1)`"*,
and its Lemma 1 (page 3) charges `O(N^{D_ff·C+O(1)})`. 2015/984's Assumption 1
reads *"is `<= d_F`"* and its Lemma 2 charges `O(N^{d_F w})`. Against 2013/549's
own subexponential target the slack is invisible: `N^{O(1)}` disappears into
`exp(n^{2/3+o(1)})`. Against 2015/984's Theorem 1 it is not invisible, because
that theorem *names an exponent*: under the assumption as the cited predecessor
states it, `O(n^{8w+1})` becomes `O(n^{8w+1+O(1)})` with the `O(1)` unquantified.
The claim stays polynomial either way — that is not in question — but **the
exponent 2015/984 reports is not determined by the assumption 2013/549 states**,
and every concrete cost this program computes from `8w+1` inherits that.

## Why it matters here

`RQ-SEMBIN-9e8f82` exists to audit a claim that ECDLP over `F_{2^n}` is
polynomial. The audit's cheap, load-bearing target is 2015/984's Proposition 5,
and the instrument for it is a degree-4 Macaulay rank. If (B) resolves badly —
if the measured `d'_F` does not control the quantity the cost model charges — then
a `d'_F <= 4` measurement supports nothing, and only the refutation direction
survives: `d'_F > 4` would still refute Proposition 5, since `d_F <= d'_F` is the
direction the paper needs and a violated upper bound is a violated upper bound.
That asymmetry is worth knowing *before* the instrument is built, because it
determines which outcomes the experiment can claim.

(A) matters for a different reason. It is an author-declared open problem sitting
directly under a published polynomial-time claim, and it is the kind of gap that
a proof-architecture audit is supposed to find: the step from "there exist many
low-degree syzygies" to "F4 does not exceed that degree" is precisely where
`D_ff^max` lives, and Nagao says he cannot make it.

## How this differs from `KN-OPEN-d218ec`

`KN-OPEN-d218ec` asks two Semaev-side questions: **where** in `(n, m, t, k)`
Semaev's Assumption 1 fails, and whether Semaev's `d_F4` (read off MAGMA
per-step verbosity) is the same quantity `GOAL-DREG-001`'s Macaulay-rank
instrument has been measuring. That is a boundary question plus an
instrument-versus-solver question, both about the Semaev paper
(`KN-LIT-fa346d`).

This record is prior to both and about a different axis: **the definitions
themselves**, as they appear in the Nagao pair. `D_ff^max` does not appear in
`KN-OPEN-d218ec` at all — it is not in Semaev's paper. Neither does the
true/fake split, nor the `+O(1)` exponent question. The two records meet at one
point: both would be partly settled by running several degree definitions against
one instance family, so an experiment serving one should be designed to serve the
other. Neither subsumes the other and neither should be closed by the other's
resolution.

## Resolution criterion

Partial resolutions are useful and should be recorded separately rather than
bundled:

- **(C) is settleable by reading alone**, at zero compute: state explicitly, in
  whatever record prices Theorem 1, which Assumption 1 is being used, and if it
  is 2015/984's then record that its cited predecessor's version carries an
  unquantified `O(1)` in the exponent. This is a disclosure obligation, not a
  research result, and it is the cheapest item here.
- **(B) is settleable by construction and small-scale computation.** For a
  Weil-descended chained Semaev system at `n` small enough to enumerate, compute
  the fake first fall degree from a GF(2) Macaulay rank and, independently,
  exhibit or exclude a true first fall at each degree `<= 4` by explicit syzygy
  search over unreduced representatives. Agreement at every tested cell is
  evidence that the substitution is safe *at those parameters*; a single
  disagreement localises the defect to 2015/984's unproved Lemma 4. Neither
  outcome requires a Gröbner engine.
- **(A) is the genuinely hard one and should not be conflated with the others.**
  A resolution is either a proof that a Weil-descended system has `D_ff^max`
  bounded by `max_i deg f_i + O(1)` — which would be discharging the future work
  Nagao names, and a substantial result — or an exhibited invertible
  recombination `M` at concrete parameters for which `D_ff(M)` exceeds the plain
  `D_ff`, which would show the two quantities separate on exactly the system
  class at issue and is a far cheaper and more likely first target. The second is
  a bounded search at small `n` and is the recommended first attempt.

Every result here is scoped to the tested `p`, `n`, `n_0`, `d`, chain topology
and representative choice, and transfers to cryptographic parameters only under
an explicitly stated assumption.

## What this record does not assert

That any of the four definitions is the "right" one, that `D_ff^max` is or is not
bounded for descent systems, that 2015/984's Lemma 4 is false, or that the
`+O(1)` discrepancy invalidates anything. It asserts that the four quantities are
distinct, that the frozen sources use them non-interchangeably while citing each
other, that the author of the polynomial-time claim recorded his inability to
discharge the version he found credible, and that none of this has been checked
here. Nothing above bears on the security of any deployed curve in either
direction.

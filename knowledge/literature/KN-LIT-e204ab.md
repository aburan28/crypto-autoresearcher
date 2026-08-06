---
id: KN-LIT-e204ab
type: literature
title: "A Polynomial-Time Quantum Algorithm for the Dihedral Coset Problem (Simon 2026, preliminary draft)"
authors:
  - "Daniel R. Simon"
year: 2026
venue: "IACR Cryptology ePrint Archive (preprint, unrefereed)"
identifiers:
  eprint: "iacr:2026/1591"
  doi: null
  arxiv: null
  url: "https://eprint.iacr.org/2026/1591"
tags: [quantum, dihedral-coset-problem, dcp, dsp, hidden-subgroup, lattice, lwe, svp, mlwe, ml-kem, ml-dsa, pqc, post-quantum, cryptanalysis, unverified-claim, preliminary-draft, adjacent]
confidence: unverified
citation_verified: read
source_freeze: SRC-DCP-SIMON-2026
added: 2026-08-06
superseded_by: null
---

## Status first

This entry records a **claim that was three days old and unverified when it was
written**. The draft is dated 2026-07-31, was received by ePrint 2026-08-03 and
approved 2026-08-06 — the same day this entry was added. The author labels it
"[Preliminary Draft]", and its four substantive results (Lemma 1, Lemma 3, that
lemma's corollary, and Lemma 4) are each labelled "(Sketch)". No independent
verification, refutation, or peer review existed at the time of recording, and
none is asserted here.

`confidence: unverified` is deliberate and is *not* a judgement that the result
is wrong. It means exactly what the corpus rules say it means: nobody in or out
of this program has checked it.

## Contribution (as claimed)

A polynomial-time quantum algorithm for the **Dihedral Coset Problem (DCP)**.
Given samples of the superposition

    (|0, x> + |1, x + d mod N>) / sqrt(2)

with `d` fixed and `x` fresh per sample, recover `d` — where with probability
`1/a(n)` a sample is *faulty* (a random bit and a random value instead of the
correct superposition).

Regev (2004) already gave a polynomial-time quantum algorithm for the
noise-free Dihedral Subgroup Problem, but it calls a **subset sum oracle** to
erase the sample bits `b_i`, so it is not an algorithm. Simon's claimed
contribution is a replacement for that erasure step that uses no oracle, and
that tolerates a faulty-sample rate as high as `1/O(log n)`.

Composed with Regev's reduction from lattice problems to DCP — with the
quadratic dimension blow-up removed by Brakerski–Kirshanova–Stehlé–Wen
(KN-LIT-4706) — the claimed consequence is:

- polynomial-time quantum **SVP** at approximation factor `sqrt(n) polylog(n)`;
- polynomial-time quantum **LWE** at "`alpha = sqrt(n) polylog(n)`" (see the
  notation caveat below).

The noise tolerance is the whole point of the composition. Kuperberg's sieve
(the prior best DCP algorithm, `2^{O(sqrt(log N))}`) needs error-free input, so
composing *it* with Regev's reduction yields only a `2^{O(sqrt n)}`
approximation factor — no better than classical BKZ.

## Mechanism (as described)

Regev's oracle-based algorithm: take ~n samples, Fourier-transform the
`x + b_i d` registers and measure, leaving each sample as a two-state
superposition whose branches differ in phase by `w^{y_i d}`; compute the subset
sum `z = sum b_i y_i`; measure all of `z` but its top bit `h`. Since
`N = 2^n`, the surviving phase is `w^{z'd} · (-1)^{h·d_n}`, so `h` carries the
last bit of `d` in the *relative phase* of its two branches. But the `b_i`
registers are still entangled with `h`, so `h` cannot simply be
Hadamard-measured. Regev used the subset sum oracle to find the unique
preimage for each of `h = 0, 1` and erase the `b_i`.

Simon's replacement erases the `b_i` by **Hadamard-transforming and measuring
them**, which costs a phase `(-1)^{sum b_j b'_j}` — and then keeps only the
groups where that cost is zero:

1. Use `Q = k·n^{c+1}` samples instead of ~n, partitioned into groups of
   `c log n`.
2. Per group `g_j`, compute `s_j` = the top `log n` bits of the group subset sum
   `r_j = sum_{g_j} b_i y_i`.
3. Hadamard-transform and measure the `b_i` in each group. Groups whose measured
   `b'` is **all zero** pick up no phase — collect `a = n/log n` of these into
   set **A**; everything else goes to set **B** (whose `s_j` are then measured).
4. Build `h*` = top bit of `z* = sum_A b_i y_i` from the `s_j` of A, and transfer
   the `d_n` phase encoding from `h` onto `h*` by computing and measuring
   `h' = h XOR h*`, then erasing `h`.
5. Hadamard-measure `h*` to read `d_n`; recurse for the remaining bits.

The correctness burden this creates is: **the amplitudes of `h* = 0` and
`h* = 1` must be nearly equal**, or the Hadamard measurement reads amplitude
imbalance instead of the phase that encodes `d_n`. Lemma 2 (the one clean,
non-sketch step) shows B's contribution `C` depends only on the low `n-1` bits
of `z*` and not on `h*`, because `2^{n-1}` can be added to both `z*` and
`z' + 2^{n-1}h` without changing the constraint mod `N`. Lemmas 3 and 4 then
try to show the *counts* of A-side state-portions for the two values of `h*`
are close enough, via pairwise independence of subset sums and a balls-in-bins
argument.

## What was actually checked here

Only internal arithmetic consistency of the stated bounds, by re-deriving them.
This is **not** a verification of the algorithm — the substantive quantum
argument (Lemma 3) was not verified.

- **Lemma 1's sample budget is consistent.** A group of `c log n` bits is
  all-zero with probability `n^{-c}`, and there are `Q/(c log n) = k n^{c+1}/(c log n)`
  groups, giving `(k/c)·(n/log n)` expected all-zero groups. That meets the
  required `a = n/log n` exactly when `k >= c`, which matches the paper's
  stated condition `k > c`.
- **Lemma 4's balls-in-bins arithmetic is consistent.** `n^c` balls into `n`
  bins: mean `n^{c-1}`, sd `n^{(c-1)/2}`; Chebyshev at `kappa = n` plus a union
  bound over `n` bins gives deviation `<= n^{((c-1)/2)+1}` except with
  probability `1/n`; relative deviation `n^{-(((c-1)/2)-1)}`, as stated.
- **The final accounting has a discrepancy that does not appear fatal.** The
  concluding paragraph multiplies `n/2` pairs of `z*_h` values by an amplitude
  bound of "at most `n`" and Lemma 4's relative deviation, obtaining
  `O(n^{-(((c-1)/2)-3)})`. But the corollary to Lemma 3 bounds that amplitude by
  `n^{3/2}`, not `n`. Using `n^{3/2}` gives `O(n^{-(((c-1)/2)-3.5))})`, which at
  the paper's `c >= 12` is still `n^{-2} <= 1/n`, so the conclusion survives —
  but the chain as written is inconsistent.

## Where the argument is thin (reviewer assessment, not refutation)

1. **Lemma 3 is the load-bearing step and is the least complete.** The final
   amplitude gap is `sum_{z*} (|A_{(0,z*)}| - |A_{(1,z*)}|) · C_{z*}`. Lemma 4
   bounds the *relative* count difference, but the `C` values are **signed** and
   `sum |C|` can vastly exceed `|sum C|`. So the whole result rests on the `C`
   values not being "so huge and mutually canceling" — the paper's own phrasing —
   which Lemma 3's "well-behaved" definition is what tries to control. Its proof
   is a sketch.
2. **Conditioning is not addressed.** Lemma 3 argues that phases are pairwise
   independent *over choices of `D`*, but `D` is measured, and the algorithm
   post-selects hard: on Lemma 1's event, on `l_{s*} = 0`, and on the
   Hadamard-transformed `s̄*` reading all zeroes (probability `2/n`). The draft
   does not show that the independence used survives that conditioning.
3. **The corollary rescales by analogy.** It re-runs Lemma 3 "with `z*_h`
   replacing `z*` and `n` substituting for `2^n`", dropping the failure
   probability from `O(2^-n)` to `O(1/n)`. Concentration is far weaker in that
   regime, and asserting the same argument structure carries over is precisely
   the kind of step that needs to be written out.
4. **The bias is asserted, not quantified.** The conclusion is that measuring
   `h*` yields `d_n` "with probability significantly greater than 1/2". No
   explicit bias is derived, so the repetition count is unquantified (though any
   inverse-polynomial bias keeps the total polynomial).
5. **Only `d_n` is proved.** The theorem recovers the last bit. The recursion for
   the remaining bits is described in the overview by analogy with Regev's, but
   is not shown to be compatible with the new erasure technique — in particular
   the interaction with the faulty-sample rate and the group structure at each
   recursive level.
6. **Notation caveat on the LWE parameter.** Both the abstract and the closing
   corollary state LWE instances with `alpha = sqrt(n) polylog(n)`. In the
   standard convention `alpha` is a noise-to-modulus ratio in `(0,1)`, so a value
   above 1 does not parse; the intended quantity is presumably its inverse or a
   differently normalised parameter. This is flagged as needing clarification,
   **not** resolved here — see KN-OPEN-8a5965.

## Why this is not dismissible

- The author is Daniel R. Simon of Simon's problem (1994), whose algorithm is
  the direct ancestor of Shor's. This is not an outsider's manuscript.
- The acknowledgements name Sanketh Menda, Daniele Micciancio, Seyoon Ragavan,
  Vinod Vaikuntanathan and Thomas Vidick — i.e. the draft has already been in
  front of several lattice and quantum specialists.
- The claimed technique is a *specific, checkable* replacement for one step of a
  known-correct reduction, not a new framework. That makes it unusually fast to
  verify or refute.

## Why it is not believable yet either

The base rate for this exact claim shape is poor and recent. In April 2024
Yilei Chen posted a claimed polynomial-time quantum algorithm for LWE with
polynomial modulus-noise ratio (ePrint 2024/555, KN-LIT-52ce4c); within about
ten days Hongxun Wu and, independently, **Thomas Vidick** found a bug in Step 9
that Chen could not fix, and the claim was retracted. Vidick is in this draft's
acknowledgements, which is informative in both directions — it means the draft
has had informed eyes on it, and it means the most relevant precedent is a
withdrawal found by one of those eyes.

## If it holds, what would actually follow

Stated carefully, because the gap between "polynomial" and "practical" is large
and the gap between LWE and the deployed schemes is real:

- **Asymptotic significance would be total.** A polynomial-time quantum
  algorithm for `sqrt(n) polylog(n)`-SVP falsifies the worst-case hardness
  foundation that lattice cryptography is built on. Unlike a speedup, it cannot
  be answered by enlarging parameters.
- **Concrete significance would be much smaller *at first*.** The algorithm
  needs `Q = k·n^{c+1}` samples with `c >= 12` and `k > c`, i.e. upwards of
  `12·n^13` DSP samples, each requiring quantum-coherent operations. That is
  polynomial and astronomically impractical simultaneously.
- **It would not immediately follow that ML-KEM / ML-DSA are broken.** Those
  rest on *Module*-LWE at fixed small rank and concrete parameters, not on
  asymptotic unstructured LWE. Whether the reduction chain reaches them —
  including whether the module structure admits the analogous EDCP form
  (cf. KN-LIT-1744 on IP-M-EDCP) and whether the faulty-sample rate
  `1/O(log n)` is achievable at those parameters — is a separate question that
  this paper does not answer. It is recorded as KN-OPEN-8a5965.

## Relevance to this program

Adjacent to the ECDLP mission, but directly load-bearing for the program's
post-quantum goals: GOAL-MLKEM-001..005 and GOAL-MLDSA-001..002 all assume
MLWE hardness. If this claim survives scrutiny, the threat model for those
goals changes at the root; if it is refuted, the refutation is itself the
useful artifact and should be recorded against this entry. Either way the
program should not restate the claim without its status.

Background on the problem family and the prior algorithms this modifies:
KN-TECH-d1bc4f. Foundational sources: Regev 2004 (KN-LIT-21383c), Kuperberg
2005 (KN-LIT-2c8264), BKSW 2018 (KN-LIT-4706).

## Not verified here

The algorithm's correctness. The frozen text is a lossy automated extraction
(SRC-DCP-SIMON-2026) in which mathematical notation is mangled, so the
re-derivations above were done against the source PDF's structure and should
be redone by anyone relying on them. No claim of this program's own is made,
and no experiment has been run against this paper.

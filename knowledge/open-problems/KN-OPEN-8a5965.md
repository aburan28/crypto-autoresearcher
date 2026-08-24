---
id: KN-OPEN-8a5965
type: open_problem
title: Does Simon's claimed polynomial-time DCP algorithm survive scrutiny, and if so does it reach the concrete Module-LWE parameters of ML-KEM / ML-DSA?
tags: [quantum, dcp, dihedral, lattice, lwe, mlwe, ml-kem, ml-dsa, svp, verification, unverified-claim, pqc, post-quantum, open, adjacent]
confidence: unverified
status: open
source_refs: [KN-LIT-e204ab, KN-TECH-d1bc4f, KN-LIT-21383c, KN-LIT-2c8264, KN-LIT-4706, KN-LIT-1744, KN-LIT-52ce4c]
added: 2026-08-06
superseded_by: null
---

## Statement

Simon (ePrint 2026/1591, KN-LIT-e204ab, frozen as SRC-DCP-SIMON-2026) claims a
polynomial-time quantum algorithm for the Dihedral Coset Problem tolerating a
faulty-sample rate of `1/O(log n)`, which composed with Regev's reduction as
improved by BKSW would give polynomial-time quantum `sqrt(n) polylog(n)`-SVP
and the corresponding LWE.

Two questions, in strict order. **Q2 is worth no effort until Q1 resolves.**

**Q1. Is the proof correct?** Specifically, which of the following survives?

**Q2. If it is correct, does the consequence reach deployed schemes?**

## Q1 — the checkable sub-questions

Ranked by how load-bearing they are. All four substantive lemmas in the draft
are labelled "(Sketch)"; these are the specific places the sketch has to become
an argument.

1. **Lemma 3, the no-catastrophic-cancellation step.** The final amplitude gap
   between `h* = 0` and `h* = 1` is
   `sum_{z*} (|A_{(0,z*)}| - |A_{(1,z*)}|) · C_{z*}`. Lemma 4 bounds the
   *relative* difference in the counts `|A|`, but the `C_{z*}` are **signed**,
   and `sum |C|` may greatly exceed `|sum C|`. The paper's "well-behaved"
   definition is what rules out the destructive case, and its justification is
   the sketch most in need of completion. *This is the analogue of Step 9 in
   Chen 2024 (KN-LIT-52ce4c) — the single step where a claim of this shape has
   previously failed.*
2. **Does the pairwise-independence argument survive the conditioning?**
   Lemma 3 treats state phases as pairwise independent over choices of the
   measured `D`, but the algorithm post-selects on several events before that
   point: Lemma 1's all-zero-group count, `l_{s*} = 0`, and the
   Hadamard-transformed `s̄*` reading all zeroes (probability `2/n`). The draft
   does not show independence is preserved under that conditioning.
3. **Does the corollary to Lemma 3 actually rescale?** It re-runs the lemma
   "with `z*_h` replacing `z*` and `n` substituting for `2^n`", weakening the
   failure probability from `O(2^{-n})` to `O(1/n)`. Concentration is far
   weaker in that regime; the substitution is asserted by analogy, not derived.
4. **What is the bias?** The conclusion states that measuring `h*` yields `d_n`
   "with probability significantly greater than 1/2" without deriving the bias,
   so the required repetition count is unquantified. Any inverse-polynomial
   bias keeps the algorithm polynomial, so this is a completeness gap rather
   than a suspected error.
5. **Does the recursion go through?** The theorem proves recovery of `d_n`
   only. Recursion to the remaining bits of `d` is asserted by analogy with
   Regev's, without checking compatibility with the new erasure technique, the
   faulty-sample rate, or the group structure at each level.
6. **A stated-but-minor inconsistency.** The concluding accounting uses an
   amplitude bound of `n` where the corollary proves `n^{3/2}`. Re-derived at
   `c >= 12` the conclusion survives either way (`n^{-2} <= 1/n`), so this is
   an erratum, not a defect — recorded so a future reader does not mistake it
   for one.

## Q2 — the reach question, conditional on Q1

Even granting the result, "poly-time quantum LWE" and "ML-KEM is broken" are
not the same statement, and the program should not collapse them.

- **What does `alpha = sqrt(n) polylog(n)` denote?** In the standard convention
  `alpha` is a noise-to-modulus ratio in `(0,1)`, so the stated value does not
  parse; presumably the inverse or a different normalisation is meant. Until
  this is pinned down, the LWE regime actually covered is unknown. Resolvable
  by reading Regev 2004 (KN-LIT-21383c) and BKSW (KN-LIT-4706) directly.
- **Unstructured LWE vs Module-LWE.** ML-KEM and ML-DSA rest on MLWE at fixed
  small rank and concrete parameters. The bridge would be the structured
  extrapolated variants — IP-M-EDCP (KN-LIT-1744) — and whether the claimed DCP
  algorithm applies through that structure is unaddressed.
- **Is the `1/O(log n)` noise tolerance enough at those parameters?** The whole
  result turns on this rate (KN-TECH-d1bc4f); the concrete instantiation is a
  different computation from the asymptotic one.
- **Concrete cost.** `Q = k·n^{c+1}` samples with `c >= 12`, `k > c` — on the
  order of `12·n^13` coherent DSP samples. Polynomial and astronomically
  impractical at once. Asymptotically this does not matter (a poly-time
  algorithm cannot be escaped by enlarging parameters); for near-term risk
  assessment it matters a great deal, and conflating the two would be an
  overclaim in either direction.

## Why it matters here

GOAL-MLKEM-001..005 and GOAL-MLDSA-001..002 all rest on MLWE hardness. This is
the first claim since Chen 2024 that would, if correct, change those goals'
threat model at the root rather than at the margin.

It is also a live test of the program's own honesty rules. The claim is
simultaneously credible enough not to dismiss (Simon of Simon's problem;
acknowledgements spanning several lattice and quantum specialists; a specific
replacement for one step of a known-correct reduction) and unproven enough not
to act on (three days old, unrefereed, self-labelled preliminary, every
substantive lemma a sketch, and the closest precedent a retraction found within
ten days by someone in this draft's own acknowledgements).

The correct posture is therefore: **record, do not re-plan.** No goal status,
threat model, or prioritisation should move on this entry until Q1 resolves.
A refutation is as valuable an outcome as a confirmation and should be recorded
against KN-LIT-e204ab either way.

## Current state

Open. As of 2026-08-06 no independent verification or refutation was known to
this program, and none was sought beyond confirming that the preprint exists
and says what it is recorded as saying. No experiment has been run. No result
of this program is claimed.

## Cheapest next step

Do not re-derive the paper. Watch for the community's verdict, which the Chen
2024 precedent suggests arrives within days to weeks, and check the ePrint
record for a revision or withdrawal notice before any use of KN-LIT-e204ab. If
the program does invest, sub-question 1 above is the entire game — a single
reader deciding whether the `C_{z*}` cancellation is controlled settles it far
more cheaply than a full read.

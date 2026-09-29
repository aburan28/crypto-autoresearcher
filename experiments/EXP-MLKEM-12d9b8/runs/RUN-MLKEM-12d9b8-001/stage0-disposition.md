# Stage 0 disposition: noise-variance-to-faulty-rate conversion chain

Required artifact per specification.yaml required_artifacts item 3 and
gating_rule (`inputs.stage_0_conversion_chain.gating_rule`).

## What was required

A citable, checkable formula or argument converting a given self-reduction
noise-variance inflation (from combining k_mlkem <= 4 real Module-LWE rows
into a virtual sample, per `inputs.self_reduction_model`) into an effective
approximation factor `a(n)` (equivalently an effective DCP faulty rate
`1/a(n)`), comparable against Simon's stated `1/O(log n)` tolerance.

## Genuine attempt made within this run's budget

Before reporting a disposition, this run re-read, within the stage-0 budget
share, all four sources specification.yaml names as currently available:

1. `inputs/DCP-SIMON-2026/paper_extracted_text.txt` -- grepped for
   `faulty|a(n)|approx|variance|noise rate|1/O`. Result: the paper states the
   qualitative fact "a polynomial-time reduction from solving a(n)-SVP to
   solving [DSP], but with a faulty sample probability of 1/a(n)" (lines
   76-79, 86-99 of the extracted text) -- i.e. Regev's own reduction's
   noise/approximation trade-off, restated by Simon. It states NO formula
   converting an arbitrary noise-variance inflation (of the kind this
   contract's self-reduction model would introduce by combining k_mlkem real
   rows with coefficient bound B) into a value of `a(n)`. The paper's own
   variance discussion (lines 1074-1421) concerns internal concentration
   bounds of Simon's own DSP-sample-counting argument, not a variance-to-`a(n)`
   conversion for an externally supplied noisy LWE self-reduction.
2. `knowledge/literature/KN-LIT-21383c.md` (Regev 2004 summary) --
   confirms the qualitative relationship ("noise rate tied to the
   approximation factor: better approximation costs a higher faulty-sample
   rate") but is explicitly marked "Paper not read... the noise-rate
   trade-off [is] relayed from Simon 2026's description of it", i.e. no
   formula-level content beyond what item 1 already gave.
3. `knowledge/techniques/KN-TECH-d1bc4f.md` -- states the relationship in
   the same qualitative form ("Regev's reduction converts `a(n)`-approximate
   lattice problems into DCP instances with faulty-sample rate `1/a(n)`"),
   again without a formula for computing `a(n)` from an arbitrary combined-
   sample noise variance. Its own text (`applicability_limits`) explicitly
   flags this as unresolved: "Reaching ML-KEM / ML-DSA requires the *module*
   variants ... which is a separate step."
4. `knowledge/open-problems/KN-OPEN-8a5965.md` -- independently confirms the
   same gap from the open-problem side: "What does `alpha = sqrt(n)
   polylog(n)` denote? ... the LWE regime actually covered is unknown ...
   Resolvable by reading Regev 2004 ... and BKSW ... directly" -- i.e. this
   program's own knowledge base already records that the underlying
   Regev/BKSW derivations (not just their summaries) would need to be read to
   get the formula, and that reading has not happened (`KN-LIT-21383c.md`:
   "Regev 2004's and BKSW's full derivations are NOT staged in this
   repository's inputs/ as of this filing").

No fifth source was substituted and no formula was approximated, guessed, or
asserted by analogy: doing so would misrepresent an estimate as a citable
derivation, which AGENTS.md rule 5 and this contract's `invalidation_rules`
both forbid.

## Disposition

**NOT COMPUTED: conversion chain unavailable from available sources.**

The required object (a formula or self-contained derivation mapping this
contract's self-reduction noise-variance inflation to an effective
`a(n)`/faulty-rate) is not present, at formula level, in any of the four
sources named as currently available in specification.yaml, nor in
`inputs/DCP-SIMON-2026/paper_extracted_text.txt` itself. Per the gating_rule,
stages 1-3 (variance formula, Q computation, combinatorial ceiling) proceed
and are reported on their own terms in `raw-result.json` and the metrics
table in the run's manifest. This disposition is stage 0's own outcome only;
it does not default to either the REALIZABLE or UNREALIZABLE verdict on the
combinatorial-ceiling axis, which is computed and reported independently
below (F4 is never a falsification of anything, per
specification.yaml `falsification_criterion`).

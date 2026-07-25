---
id: KN-LIT-111
type: literature
title: Does the Dual-Sieve Attack on Learning with Errors even Work?
authors: [Ducas Leo, Pulles Ludo]
year: 2023
venue: CRYPTO 2023 (ePrint 2023/302)
identifiers:
  eprint: iacr:2023/302
  doi: null
  url: https://eprint.iacr.org/2023/302
tags: [dual-attack, dual-sieve, heuristics, falsification, lwe, bdd, fft, waterfall-floor, contested, negative-result, lattice]
confidence: reported
citation_verified: read
added: 2026-07-24
superseded_by: null
---

## Contribution
A systematic attack on the *analysis* of the dual-sieve attack family
(KN-LIT-109, KN-LIT-110). The paper first generalises the Guo-Johansson FFT
trick to arbitrary Bounded Distance Decoding instances -- improving the attack --
and then argues that the heuristics the whole family rests on are false, with
the consequence that the recent claimed success probabilities are presumably
significantly overestimated.

## Key claims (as reported)
- The underlying heuristics contradict formal, unconditional theorems in some
  regimes, and contradict well-tested heuristics in others. The specific
  instantiations in the recent literature fall into the second regime.
- The contradictions are confirmed experimentally, documenting phenomena the
  existing analysis does not predict, including a "waterfall-floor" behaviour
  reminiscent of LDPC decoding failure.
- Conclusion: the success probabilities of the recent Dual-Sieve-FFT attacks are
  presumably significantly overestimated. The paper discusses how to fix the
  attack and its analysis rather than declaring the approach dead.
- Framing point the authors make: the prior works are "painfully specific" to
  LWE although the dual-sieve principle is general, and the heuristics had
  received very little theoretical or experimental attention.

## Relevance to this program
This is the single most directly transferable paper in the lattice corpus for
this program's methodology, and it should be read as a model of the red-team
role the program's own contract requires. The pattern is exact: a claimed
improvement over a baseline, resting on an unexamined heuristic, propagated
into headline security numbers, and falsified not by finding an error in the
algorithm but by testing the heuristic against theorems and experiments. Note
also what the paper does *not* claim -- it does not say the dual attack fails,
it says the analysis is unsound and the numbers are unsupported. That
distinction between "mechanism refuted" and "evidence insufficient" is one the
program's decision vocabulary already makes, and this is a high-quality worked
example of the latter. See KN-OPEN-016 for the residual open question.

## Not verified here
The ePrint abstract was fetched and read. The contradiction arguments, the
generalisation to BDD, and the waterfall-floor experiments were not reproduced,
and the specific regimes in which the heuristics fail are not restated here in
technical detail. Whether subsequent work has repaired the analysis was not
checked as of this entry's date.

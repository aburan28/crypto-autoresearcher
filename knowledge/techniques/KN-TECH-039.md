---
id: KN-TECH-039
type: technique
title: The dual attack on LWE and the dual-sieve dispute
tags: [dual-attack, dual-sieve, distinguisher, fft, lwe, bdd, heuristics, contested, security-estimate, falsification, lattice]
confidence: reported
complexity: cost of BKZ at the block size giving a distinguishing advantage eps; claimed FFT-accelerated variants are faster than the primal attack, and those claims are disputed
applicability: decision-LWE and LWE-derived instances; in principle general BDD, though the recent improved variants were developed specifically for LWE
source_refs: [KN-LIT-107, KN-LIT-109, KN-LIT-110, KN-LIT-111, KN-LIT-105, KN-TECH-038]
added: 2026-07-24
superseded_by: null
---

## Method
Rather than recovering the secret, distinguish LWE samples from uniform. Find a
short vector in the dual lattice `{ (x, y) in Z^m x Z^n : A^t x = y mod q }`;
given such a vector of length `l`, the inner product with the sample is
distributed as a narrow Gaussian if the input is LWE and uniform mod `q`
otherwise. KN-LIT-107 gives the advantage as `eps = 4 exp(-2 pi^2 tau^2)` with
`tau = sigma * l / q`, so the required block size follows from demanding a
usable `eps`. That paper also records that a preliminary version of itself had a
wrong formula for `eps` which under-costed the dual attack -- an early warning
that this attack's analysis is error-prone.

## Why this entry exists mainly as a caution
The dual attack was long considered the weaker sibling of the primal attack.
From 2021 that reversed, on paper:

- **KN-LIT-109** (Guo-Johansson) combined "dimensions for free" (KN-LIT-105)
  with bulk short-vector output from sieving and an FFT distinguisher, claiming
  the dual attack now beats the primal attack and that Kyber-768 falls below its
  claimed security level.
- **KN-LIT-110** (MATZOV) independently claimed similar improvements plus
  cheaper sieving gate counts, putting Kyber, Saber and Dilithium below NIST's
  thresholds -- Kyber by 4 to 14 bits.
- **KN-LIT-111** (Ducas-Pulles) then argued the heuristics under this entire
  family contradict unconditional theorems in some regimes and well-tested
  heuristics in others, confirmed the contradictions experimentally including a
  "waterfall-floor" phenomenon, and concluded the success probabilities are
  presumably significantly overestimated.

The correct current summary is therefore: **the improved dual attacks' claimed
advantage over the primal attack is not established.** It has not been refuted
either -- KN-LIT-111 attacks the analysis, not the algorithm, and discusses how
to repair it. See KN-OPEN-016.

## Applicability limits
A distinguishing advantage is not a key recovery, and converting one to the
other costs more; a "break" stated as a distinguisher must say so. Costs in this
family are quoted in RAM-model gate counts rather than core-SVP units, so they
are not directly comparable with numbers computed under KN-TECH-040 without
restating the convention. Most importantly, every claimed figure here is an
extrapolation to parameters far beyond any executed experiment.

## Verified vs reported
The dual lattice construction, the advantage formula, and the bogus-formula note
are read directly from KN-LIT-107. The claimed improvements are reported from
KN-LIT-109's publisher abstract and KN-LIT-110's report text (whose Table 1
figures were read); the objections are reported from KN-LIT-111's abstract.
Nothing in this dispute has been independently checked by this program, and this
entry deliberately takes no side beyond recording that the claims are contested.

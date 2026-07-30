---
id: KN-OPEN-016
type: open_problem
title: Does the improved dual attack on LWE actually beat the primal attack, once its heuristics are repaired?
tags: [dual-attack, dual-sieve, fft, heuristics, lwe, kyber, contested, concrete-security, falsification, open, lattice]
confidence: reported
status: open
source_refs: [KN-LIT-109, KN-LIT-110, KN-LIT-111, KN-TECH-039, KN-TECH-040]
added: 2026-07-24
superseded_by: null
---

## Statement
Between 2021 and 2023 the dual attack on LWE was claimed to overtake the primal
attack and to push NIST finalists below their required security levels, and
then the analysis supporting those claims was argued to be unsound. The open
question is narrow and quantitative: **after the heuristics are repaired, what
is the dual attack's actual cost relative to the primal attack, and does any
deployed parameter set lose security?**

## Current state (as reported)
- **Claim.** Guo-Johansson (KN-LIT-109) combine dimensions-for-free with bulk
  short-vector output and an FFT distinguisher, claiming the dual attack beats
  the primal attack and that Kyber-768 falls below its claimed level. MATZOV
  (KN-LIT-110) independently claims Kyber 4 to 14 bits below the NIST cutoff,
  partly from attack improvements and partly from **re-costing sieving gate
  counts** relative to KN-LIT-122.
- **Objection.** Ducas-Pulles (KN-LIT-111) show the family's heuristics
  contradict unconditional theorems in some regimes and well-tested heuristics
  in others, confirm this experimentally including an unpredicted
  "waterfall-floor" phenomenon, and conclude the success probabilities are
  presumably significantly overestimated. They generalise the FFT trick to
  arbitrary BDD in the same work, so the objection is not a dismissal of the
  approach.
- **Not settled by that objection.** KN-LIT-111 attacks the analysis, not the
  algorithm, and explicitly discusses the way forward. Whether subsequent work
  has repaired the analysis, and what the repaired numbers are, has not been
  checked by this program as of this entry's date.

## Why it matters here
This is the live case study of the exact failure mode the program's contract is
built to prevent: a claimed advantage over a baseline, resting on an unexamined
heuristic, propagated into headline security numbers, published by independent
groups, and then falsified at the level of the heuristic rather than the code.
It supplies three transferable rules. A cost-model revision can masquerade as an
attack -- separate them (KN-TECH-040). Independent replication of a *claim* is
not independent validation of its *heuristics*, since two groups made related
assumptions. And "the analysis is unsound" is a different verdict from "the
mechanism fails," a distinction the program's decision vocabulary already makes
and should keep making.

## What would close it
A repaired analysis with experimental support at dimensions where the prediction
can be checked, plus a statement of the primal/dual comparison in a single named
cost convention. Absent that, any program document citing dual-attack security
figures must mark them contested.

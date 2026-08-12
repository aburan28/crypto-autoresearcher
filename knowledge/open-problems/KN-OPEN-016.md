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
- **Post-objection dual claim.** Carrier–Meyer-Hilfiger–Shen–Tillich
  (KN-LIT-7617, ePrint 2022/1750 rev. 2025) claim a coding-theoretic MATZOV
  variant that avoids the contested independence assumptions and again puts
  Kyber-512/768/1024 3.5 / 11.9 / 12.3 bits below NIST cutoffs.
- **Program measurement (KN-FIND-015 / EV-MLKEM-015, 2026-07-31).** Under
  pinned lattice-estimator MATZOV costing, `dual_hybrid+fft` does **not** beat
  `primal_bdd` on Kyber-512/768/1024, and neither Carrier nor MATZOV-2022 dual
  headlines are reproduced by that public dual instrument (gaps of roughly
  4–16 bits). Separately, `primal_bdd` under MATZOV already sits 2.8 / 6.0 /
  1.3 bits below NIST classical cutoffs.
- **Carrier table arithmetic (KN-FIND-016 / EV-MLKEM-016, 2026-07-31).**
  Table 5.1 Algorithm-3.1 costs (including abstract CC shortfalls
  3.5/11.9/12.3) match Theorem 4.1 and the authors' optimizer pickle; Table
  C.2 CN/Kyber-512 `log2(Tsample)=143.30` is a transcription error for
  ≈134.30.
- **Pwrong coverage gap (KN-FIND-012 / EV-MLKEM-011, 2026-07-31).** Fig 4.1
  archived Pwrong CDFs stop near T≈1800 (log2≈−36), while all 4000 Pgood
  scores for the same left-panel parameters lie at T≥6668 (median ≈11964).
  The Pgood≈½ threshold is outside the measured Pwrong T-range; Kyber-512 CC
  `log2(Pwrong)=−119.57` is ~84 bits below that toy floor.
- **Brittleness (KN-FIND-013 / EV-MLKEM-012, 2026-07-31).** Under HEUR-S1
  (Pwrong miss of Δ bits paid in the FFT/decode term), only ≈9.46/14.36/14.76
  bits of Δ erase the CC NIST shortfalls for Kyber-512/768/1024.
- **Score-scale audit (KN-FIND-014 / EV-MLKEM-013, 2026-07-31).** verifyModel
  Pwrong uses FFT/k_fft while Pgood uses raw cosine sums; after aligning by
  k_fft the Fig 4.1 coverage gap remains (fraction_inside=0). Residual open
  piece: measure Pwrong near the aligned operating threshold, or replace
  HEUR-S1 with a defended re-optimization.

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

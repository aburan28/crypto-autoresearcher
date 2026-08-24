---
id: KN-LIT-52ce4c
type: literature
title: "Quantum Algorithms for Lattice Problems (Chen 2024) — main LWE claim RETRACTED"
authors:
  - "Yilei Chen"
year: 2024
venue: "IACR Cryptology ePrint Archive (preprint; main claim withdrawn by the author)"
identifiers:
  eprint: "iacr:2024/555"
  doi: null
  arxiv: null
  url: https://eprint.iacr.org/2024/555
tags: [quantum, lattice, lwe, sis, cryptanalysis, retracted, withdrawn-claim, complex-gaussian, windowed-qft, pqc, post-quantum, base-rate, adjacent]
confidence: reported
citation_verified: web
added: 2026-08-06
superseded_by: null
---

## Contribution
Posted 2024-04-10 claiming a **polynomial-time quantum algorithm for LWE with
polynomial modulus-noise ratio** — i.e. a break of the hardness assumption
under most NIST post-quantum standards. The techniques introduced were complex
Gaussian states and a windowed quantum Fourier transform.

## Outcome: the main claim does not hold
Within roughly ten days the author posted that **Step 9 of the algorithm
contains a bug**, which he did not know how to fix, crediting Hongxun Wu and,
independently, **Thomas Vidick** with finding it. The polynomial-time LWE claim
was withdrawn. Chen left the remainder of the paper posted, with a clarification
to Step 8, in the hope that the complex-Gaussian and windowed-QFT machinery
would find other uses.

## Why this entry exists
Not for its result — it has none — but as the **base rate** for claims of this
shape, recorded so the program never has to reconstruct it from memory when the
next one appears. The reference case is concrete: a credentialed author, a
specific and checkable algorithm, enormous stakes, and a fatal defect located
in a single step within two weeks by readers.

It is cited directly by KN-LIT-e204ab (Simon 2026, ePrint 2026/1591), which
makes a structurally similar claim — polynomial-time quantum algorithm whose
consequence is poly-time LWE — and whose acknowledgements include Vidick. The
prior it supplies cuts both ways: such claims usually fail, and they usually
fail *fast and legibly*, which is a reason to record the claim and wait rather
than to either dismiss or amplify it.

## Relevance to this program
Governs how the program should hold KN-LIT-e204ab and any successor claim:
record it, state its status honestly, do not restate it as fact, and do not
re-plan GOAL-MLKEM-* / GOAL-MLDSA-* threat models on an unverified preprint.
See KN-OPEN-8a5965.

## Not verified here
Paper not read. The claim, the Step 9 bug, the attributions to Hongxun Wu and
Thomas Vidick, and the withdrawal are relayed from search results retrieved
2026-08-06 (the ePrint listing, the author's own posted note as quoted in
secondary coverage, and contemporaneous reporting). The primary ePrint page was
not fetched directly and the retraction wording is not quoted verbatim here.
Confidence `reported`.

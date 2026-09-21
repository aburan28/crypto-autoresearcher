---
id: KN-OPEN-010
type: open_problem
title: Can the leading spectrum of a coarse-grained transfer operator of the translation-by-P walk localize k into an interval shrinkable below sqrt(n) total cost, or does character orthogonality force localization O(1)?
tags: [transfer-operator, koopman, spectral, translation-walk, character-orthogonality, birthday, ecdlp, open]
confidence: reported
status: open
source_refs: [KN-LIT-040, KN-TECH-017]
added: 2026-07-22
superseded_by: null
---

## Statement
Coarse-grain the translation-by-P map on E(F_p) into a finite CxC Markov
operator, estimate its leading spectrum from sub-birthday trajectory samples
(total length S = o(sqrt(n))), and map eigenvalue phases to a k-interval. Does
the localization factor L grow super-constantly (L >= n^delta at S <= n^{0.3}),
shrinking the residual BSGS search below sqrt(n) total cost -- or is L = O(1)
because coarse-graining destroys the character phase that encodes k?

## Current state (as reported)
Transfer/Koopman spectral theory (KN-LIT-040, KN-TECH-017) is pure dynamics; no
DLOG/ECDLP application was located. A translation is measure-preserving, so its
Koopman operator is unitary with characters as eigenfunctions and the character
phases ARE the logarithm data -- at full resolution (C ~ n) the spectrum recovers
k circularly, and at C << n coarse-graining is expected to mix exactly that
phase. The strong expectation (unproven as a theorem with measurements) is the
BARRIER L = O(1). The program's transfer-operator candidate (RQ-TRA-001,
EXP-TRA-001) is designed to measure L(S,C) directly.

## Why it matters here
Any L growing like n^delta at S = o(sqrt(n)) would be a genuinely non-generic
surprise and a promotion signal; the overwhelmingly likely outcome is a clean
character-orthogonality barrier, valuable as a PROVED negative with a fitted
L(S,C) law. It sharpens the boundary of KN-OPEN-001 for spectral/direct-solver
(no factor base) approaches. A positive-control at C = n (spectrum does recover k)
and a random-permutation negative control (no localization) are needed to
separate a real signal from estimator artifacts.

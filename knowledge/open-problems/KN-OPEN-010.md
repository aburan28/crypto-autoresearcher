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

## Reconciliation note, 2026-10-18 (appended; the entry above is unchanged)

Register status stays `open`. The transfer-operator result is a toy-scale scoped negative (n <= ~4200); this entry's strong expectation L = O(1) is stated as unproven.

Premise check: the request that prompted this note cited DEC-20260722-003..006 as the proving decisions. They are not: DEC-20260722-003 targets GOAL-MLKEM-001/IDEA-20260722-001, -004 and -005 target GOAL-ECDLP-001 BATCH-002 task handling, and no DEC-20260722-006 exists. The records that do bear on this problem are below.

- EV-TRA-001 (TRA-H-001, `weakens`, preliminary): S in {n^1/4, n^3/8}, C = 128, 6 seeds; the evidence record's scope note says C = 128 is not a full-resolution test.
- H-TRA-4344b7 is `proposed`. DEC-20260804-139a86 records "H-TRA-001 rejected_scoped (L=O(1))"; no separate decision with that disposition was located by hypothesis id.

Decision request: `coordination/remediation/DECISION-REQUEST-20261018-ic-integrity.md`, item R-3.

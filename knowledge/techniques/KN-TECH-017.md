---
id: KN-TECH-017
type: technique
title: Transfer operators and Koopman spectral methods
tags: [transfer-operator, koopman, spectral, markov, mixing, walk, dlog-channel, ecdlp]
confidence: reported
complexity: spectral estimation cost ~ S*C^2 for S samples and C cells; localization factor L expected O(1) by character orthogonality
applicability: spectral analysis of a coarse-grained Markov/Koopman operator of a dynamical map; here the translation-by-P walk
source_refs: [KN-LIT-040]
added: 2026-07-22
superseded_by: null
---

## Method
The transfer (Perron-Frobenius) operator pushes forward densities under a
dynamical map; its adjoint, the Koopman operator (KN-LIT-040), acts on
observables by composition. For a chaotic/expanding system the leading spectrum
(spectral gap, resonances) governs mixing and decay of correlations (Baladi). One
coarse-grains the state space into C cells, estimates the empirical CxC
transition matrix from sampled trajectories, and reads leading eigenpairs.

## Program usage
The mechanism of the program's transfer-operator candidate (RQ-TRA-001,
EXP-TRA-001): coarse-grain the translation-by-P walk on E(F_p), estimate the
leading spectrum from sub-birthday samples, and try to map eigenvalue phases to a
k-interval, finishing with BSGS (KN-OPEN-010). No factor base -- a direct-solver
probe.

## Applicability limits (expected barrier)
A group translation is measure-preserving, so its Koopman operator is UNITARY
with pure point spectrum whose eigenfunctions are characters -- and the character
phases *are* the logarithm data. At full resolution (C ~ n) the spectrum trivially
recovers k (circular); at C << n coarse-graining mixes exactly the phase that
encodes k, so the localization factor L is expected to be O(1) (no gain). Unlike
expanding systems, there is no spectral gap to exploit. The honest expected
deliverable is a BARRIER measurement (fitted L(S,C) law) plus a character-
orthogonality theorem, not a sub-sqrt(n) attack. Estimator artifacts must be
excluded with random-permutation negative controls.

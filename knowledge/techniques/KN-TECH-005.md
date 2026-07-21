---
id: KN-TECH-005
type: technique
title: Generic group model and the square-root discrete-log lower bound
tags: [generic-group-model, lower-bound, discrete-logarithm, baseline, birthday, ecdlp]
confidence: established
complexity: Omega(sqrt(p)) group operations for any generic DLP algorithm (p = largest prime factor of the group order); with S-bit preprocessing, S*T^2 = Omega~(n)
applicability: any lower-bound argument that treats group elements as opaque labels accessed only via the group-operation oracle
source_refs: [KN-LIT-011, KN-LIT-013]
added: 2026-07-21
superseded_by: null
---

## Method
Model an algorithm as *generic*: group elements are given as random, otherwise
structureless encodings, and the algorithm learns nothing except equalities and
results of the group operation, supplied by an oracle. In this model one proves
information-theoretic lower bounds by counting how many distinct linear
combinations of the inputs the algorithm can form before two collide.

## The bound (the program's bar)
- Any generic DLP algorithm needs Omega(sqrt(p)) group operations (Shoup,
  KN-LIT-011; precursor Nechaev 1994). This matches baby-step/giant-step and
  Pollard rho (KN-TECH-001), so those are optimal among generic methods.
- With preprocessing/advice (fixed curve), the tight generic tradeoff is
  S*T^2 = Omega~(n) (Corrigan-Gibbs-Kogan, KN-LIT-013), and it survives against
  non-uniform adversaries (Coretti-Dodis-Guo).

## Program usage
This is the formal content of the program's baseline convention ("B = rho 1/2",
"birthday bound", "charged exponent below 0.49/0.5"). A prime-field proposal that
claims to beat ~sqrt(n) is, by these theorems, asserting it is NON-GENERIC: it
must use curve/encoding structure the model excludes. The standard first screen
for a candidate (jets, elliptic nets, transfer operators, ...) is therefore
"is the augmented oracle simulable in the generic group model with O(1)
overhead?" -- if yes, the candidate is closed at exponent 1/2 (KN-OPEN-005). The
bound is a barrier, NOT a proof that no non-generic attack exists (KN-OPEN-001).

## Applicability limits
The bound is about the generic model; it says nothing about attacks exploiting
concrete structure (isogenies, pairings on low-embedding-degree curves,
anomalous curves with #E = p, summation-polynomial index calculus over extension
fields). Those live precisely in the model's blind spot.

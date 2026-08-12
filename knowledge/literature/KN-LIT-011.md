---
id: KN-LIT-011
type: literature
title: Lower Bounds for Discrete Logarithms and Related Problems
authors: [Shoup Victor]
year: 1997
venue: EUROCRYPT 1997, LNCS 1233, pp. 256-266
identifiers:
  eprint: null
  doi: 10.1007/3-540-69053-0_18
  url: https://link.springer.com/chapter/10.1007/3-540-69053-0_18
tags: [generic-group-model, lower-bound, discrete-logarithm, baseline, shoup, complexity, ecdlp]
confidence: established
citation_verified: web
added: 2026-07-21
superseded_by: null
---

## Contribution
Formalizes the *generic group model*: an algorithm sees group elements only as
opaque, randomly-encoded labels and interacts with the group solely through an
oracle for the group operation (and equality). Proves that any generic
algorithm solving the discrete logarithm problem must perform Omega(sqrt(p))
group operations, where p is the largest prime dividing the group order.
Companion generic lower bounds are given for Diffie-Hellman-type problems.

## Key claims (as reported)
- The Omega(sqrt(p)) bound is *proven within the model*, not heuristic; it
  matches baby-step/giant-step and Pollard rho (KN-LIT-008), so those generic
  methods are essentially optimal among generic algorithms.
- The independently-credited precursor is Nechaev, "Complexity of a determinate
  algorithm for the discrete logarithm," Mathematical Notes 55(2):165-172, 1994
  (doi:10.1007/BF02113297), which gives an earlier sqrt(p) bound for a
  restricted deterministic model.

## Relevance to this program
This is the exact statement of the generic square-root (exponent-1/2) barrier
that the program's baseline convention encodes ("B = rho 1/2", "birthday
bound", "charged exponent"). Any prime-field ECDLP proposal that claims to beat
~sqrt(n) is, by this theorem, claiming to be *non-generic* -- it must exploit
specific curve/encoding structure the model excludes. Directly grounds the
"is the augmented oracle simulable in the generic model?" test the program
applies to jet/dual-number and elliptic-net candidates (KN-OPEN-005), and the
central open question KN-OPEN-001.

## Not verified here
Full paper not re-read for this entry; the sqrt(p) bound and model definition
are standard, textbook-level, and reconstructible (hence confidence:
established). Bibliographic fields confirmed against publisher DOI / secondary
indices via search, not by fetching the primary page (session egress blocks
that host).

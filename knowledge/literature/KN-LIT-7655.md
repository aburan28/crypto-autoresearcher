---
id: KN-LIT-7655
type: literature
title: "Radical 3-isogenies for the ideal class group actions on (2, epsilon)-structures"
authors:
  - "Masaomi Shibata"
  - "Hiroshi Onuki"
  - "Tsuyoshi Takagi"
year: 2026
venue: "IACR Cryptology ePrint Archive, Report 2026/576"
identifiers:
  eprint: "iacr:2026/576"
  doi: null
  arxiv: null
  url: "https://eprint.iacr.org/2026/576"
tags: [class-group-action, group-action, radical-isogeny, isogeny, supersingular, oriented-curve, orientation, delfs-galbraith, sidh-csidh, q-curve, montgomery-curve, meet-in-the-middle, elliptic-curve]
confidence: reported
citation_verified: web
added: "2026-08-01"
superseded_by: null
---

## Contribution
Explicit **radical 3-isogeny formulas** for evaluating the ideal class group action on
supersingular **`(2, ε)`-structures** — pairs consisting of an elliptic curve over
`F_{p²}` and a degree-2 isogeny from the curve to its Galois conjugate, in the sense of
Chenu and Smith.

The authors show that any `(2, ε)`-structure can be represented as **a curve
coefficient plus a single sign**, under two representations: reductions of degree-2
`Q`-curves, and Montgomery curves. From these they derive radical 3-isogenies
implementing the action of the class of a prime ideal above 3, and give an explicit
**meet-in-the-middle** algorithm as an application.

## Key claims (as reported)
- Compact representation of `(2, ε)`-structures: coefficient + one sign, in both
  representations.
- Explicit radical 3-isogenies for the action of a prime ideal above 3.
- An explicit meet-in-the-middle algorithm follows.
- Context (relayed from the abstract): Chenu–Smith's **generalized Delfs–Galbraith**
  algorithm for the supersingular isogeny problem is expected to beat the original by a
  **constant factor**. Constant factor — the abstract says so, and this entry does not
  upgrade it.

## Relevance to this program
Directly in the program's isogeny cost-model thread. Delfs–Galbraith is the standard
classical algorithm for the supersingular isogeny path-finding problem that
[[KN-TECH-050]] and [[KN-TECH-057]] price under full-cost accounting, and this paper
supplies the arithmetic that makes the *generalized* variant executable: without an
efficient way to evaluate the class-group action on `(2, ε)`-structures, the constant
factor is unrealizable.

Two notes on how to read it:

- **`(2, ε)`-structures are an object-level variation**, not an algorithmic trick: they
  change what a "vertex" is, and thereby what counts as a terminal. Compare
  [[KN-LIT-7580]] (`iacr:2026/1516`), which enlarges the recognizable terminal set of
  the same subfield search with precomputed CM vertices. Two independent 2026 attacks
  on the same bottleneck — Delfs–Galbraith's subfield-search stage — by two different
  routes to "reach a terminal sooner." Worth tracking as a converging line rather than
  as isolated papers.
- **Radical isogenies** are the standard tool for iterating a class-group action
  without recomputing kernel points, so this is also a datapoint on how far radical
  formulas extend beyond the CSIDH setting.

**Does not bear on the prime-field ECDLP**, and moves no exponent: the claimed gain in
the underlying algorithm is a constant factor on a `Õ(p^{1/2})` classical baseline.

## Not verified here
Full paper not read. Claims relayed from the ePrint abstract page for report 2026/576,
retrieved 2026-08-01 (hence `confidence: reported`). Citation checked against the
ePrint record: title, three authors (Shibata, Onuki, Takagi), report number, year 2026.

NOT verified here: the radical 3-isogeny formulas; the coefficient-plus-sign
representation; the meet-in-the-middle algorithm or its cost; the attribution to Chenu
and Smith; and the expected constant-factor improvement of generalized Delfs–Galbraith,
which is relayed from this abstract and not checked against the Chenu–Smith source.
**No revision to `KN-TECH-050` or `KN-TECH-057` is asserted.**

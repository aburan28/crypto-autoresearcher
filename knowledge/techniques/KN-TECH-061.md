---
id: KN-TECH-061
type: technique
title: Honda–Tate classification of abelian varieties over finite fields
tags: [honda-tate, abelian-variety, isogeny, weil-number, frobenius, endomorphism, finite-field, foundational, number-theory, algebraic-geometry]
confidence: established
complexity: classification theorem — enumerative, not an attack algorithm
applicability: abelian varieties (including elliptic curves) over finite fields, up to isogeny; endomorphism-ring refinements via Waterhouse
source_refs: [KN-LIT-7624, KN-LIT-7625, KN-LIT-7626, KN-LIT-075, KN-TECH-028]
added: 2026-07-31
superseded_by: null
---

## Method
For a finite field F_q, simple abelian varieties up to F_q-isogeny are in
bijection with conjugacy classes of Weil q-numbers (algebraic integers all of
whose conjugates have complex absolute value √q):

- **Weil** supplies the Weil-number property of Frobenius.
- **Tate (1966)** (KN-LIT-7624) shows injectivity: Hom is determined by the
  Tate-module / Frobenius action, so equal characteristic polynomials ⇒
  isogenous.
- **Honda (1968)** (KN-LIT-7625) shows surjectivity: every Weil q-number
  arises.
- **Waterhouse (1969)** (KN-LIT-7626) refines the picture to endomorphism
  rings and isomorphism types inside an isogeny class; the elliptic
  supersingular/ordinary dictionary is Deuring (KN-LIT-075).

## Why it matters for this program
This is the existence and uniqueness spine behind:

- which ordinary CM discriminants and supersingular isogeny classes can occur;
- endomorphism-ring algorithms and the Deuring correspondence (KN-TECH-028);
- any claim that a Weil polynomial “should correspond to a curve.”

It is **not** an ECDLP method. Proposals that rediscover “Frobenius
determines the isogeny class” are duplicates of this technique.

## Applicability limits
Classification is up to isogeny over the given finite field. Isomorphism
types, principal polarizations, and efficient construction of a curve with a
prescribed Weil polynomial are separate algorithmic problems. Nothing here
moves the discrete-log exponent on a fixed cryptographic group.

## Verified vs reported
The bijection is textbook arithmetic geometry (`confidence: established` as
a named theorem). Individual paper proofs were not re-derived; see the
`Not verified here` sections of KN-LIT-7624–7626.

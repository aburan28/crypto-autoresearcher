---
id: KN-LIT-5983
type: literature
title: "Proving Resistance against Invariant Attacks: How to Choose the Round Constants"
authors:
  - "Christof Beierle"
  - "Anne Canteaut"
  - "Gregor Leander"
  - "Yann Rotella"
year: null
venue: null
identifiers:
  eprint: null
  doi: null
  arxiv: null
  url: null
tags: [mov-fr, symmetric]
confidence: reported
citation_verified: read
added: "2026-07-24"
superseded_by: null
---

## Contribution
Many lightweight block ciphers apply a very simple key schedule in which the round keys only differ by addition of a roundspecific constant. Generally, there is not much theory on how to choose appropriate constants.

## Key claims (as reported)
- In fact, several of those schemes were recently broken using invariant attacks, i.e., invariant subspace or nonlinear invariant attacks.
- This work analyzes the resistance of such ciphers against invariant attacks and reveals the precise mathematical properties that render those attacks applicable.
- As a first practical consequence, we prove that some ciphers including Prince, Skinny-64 and Mantis7 are not vulnerable to invariant attacks.
- Also, we show that the invariant factors of the linear layer have a major impact on the resistance against those attacks.

## Relevance to this program
Relevant to pairing-based reductions and endomorphism speedups (MOV/Frey-Rück special cases, GLV/GLS) that bound which curve classes are safe baselines.

## Not verified here
Entry generated during the 2026-07-24 bulk seeding pass from the local PDF's first two pages. Title/authors/year/venue were parsed heuristically and may be incomplete or mis-segmented; claims are relayed from the paper's abstract without independent verification. Upgrade to a fully verified entry after a careful read.

## Local copies
- `downloads/10401273 (1).pdf`
- `downloads/10401273.pdf`

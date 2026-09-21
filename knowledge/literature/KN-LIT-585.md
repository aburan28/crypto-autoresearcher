---
id: KN-LIT-585
type: literature
title: "A note on the security of CSIDH"
authors: []
year: 2018
venue: "arXiv preprint"
identifiers:
  eprint: null
  doi: null
  arxiv: "1806.03656"
  url: "https://arxiv.org/abs/1806.03656"
tags: [class-group, elliptic-curve, endomorphism, finite-field, isogeny, number-theory, protocol, quantum, sidh-csidh, signature, supersingular]
confidence: reported
citation_verified: read
added: "2026-07-24"
superseded_by: null
---

## Contribution
We propose an algorithm for computing an isogeny between two elliptic curves E1 , E2 defined over a finite field such that there is an imaginary quadratic order O satisfying O ≃ End(Ei ) for i = 1, 2. This concerns ordinary curves and supersingular curves defined over Fp (the latter used in the recent CSIDH proposal).

## Key claims (as reported)
- Our algorithm has heuris√  O tic asymptotic run time e √ O log(|∆|) and requires polynomial quantum log(|∆|) memory and e classical memory, where ∆ is the discriminant of O.
- This asymptotic complexity outperforms all other available method for computing isogenies.
- We√ also show that a variant of our method has asymptotic run time  Õ log(|∆|) while requesting only polynomial memory (both quantum e and classical).

## Relevance to this program
Relevant to the isogeny cluster: bears on supersingular/isogeny-based constructions and the isogeny-path problems that compete with and inform ECDLP work. Relevant to pairing-based reductions and endomorphism speedups (MOV/Frey-Rück special cases, GLV/GLS) that bound which curve classes are safe baselines.

## Not verified here
Entry generated during the 2026-07-24 bulk seeding pass from the local PDF's first two pages. Title/authors/year/venue were parsed heuristically and may be incomplete or mis-segmented; claims are relayed from the paper's abstract without independent verification. Upgrade to a fully verified entry after a careful read.

## Local copies
- `downloads/1806.03656v4.pdf`

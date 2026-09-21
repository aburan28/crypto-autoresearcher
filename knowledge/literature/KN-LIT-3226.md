---
id: KN-LIT-3226
type: literature
title: "Cryptanalysis of CLT13 Multilinear Maps with Independent Slots"
authors:
  - "Jean-Sébastien Coron"
  - "Luca Notarnicola"
year: null
venue: null
identifiers:
  eprint: null
  doi: null
  arxiv: null
  url: null
tags: [cryptanalysis, fhe, glv-gls, lattice, protocol, provable-security, quantum]
confidence: reported
citation_verified: read
added: "2026-07-24"
superseded_by: null
---

## Contribution
Many constructions based on multilinear maps require independent slots in the plaintext, so that multiple computations can be performed in parallel over the slots. Such constructions are usually based on CLT13 multilinear maps, since CLT13 inherently provides a composLn ite encoding space, with a plaintext ring i=1 Z/gi Z for small primes gi ’s.

## Key claims (as reported)
- However, a vulnerability was identified at Crypto 2014 by Gentry, Lewko and Waters, with a lattice-based attack in dimension 2, and the authors have suggested a simple countermeasure.
- In this paper, we identify an attack based on higher dimension lattice reduction that breaks the author’s countermeasure for a wide range of parameters.
- Combined with the Cheon et al. attack from Eurocrypt 2015, this leads to the recovery of all the secret parameters of CLT13, assuming that low-level encodings of almost zero plaintexts are available.
- We show how to apply our attack against various constructions based on composite-order CLT13.

## Relevance to this program
Relevant to pairing-based reductions and endomorphism speedups (MOV/Frey-Rück special cases, GLV/GLS) that bound which curve classes are safe baselines.

## Not verified here
Entry generated during the 2026-07-24 bulk seeding pass from the local PDF's first two pages. Title/authors/year/venue were parsed heuristically and may be incomplete or mis-segmented; claims are relayed from the paper's abstract without independent verification. Upgrade to a fully verified entry after a careful read.

## Local copies
- `downloads/119210133 (1).pdf`
- `downloads/119210133.pdf`

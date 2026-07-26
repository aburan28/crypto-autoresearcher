---
id: KN-LIT-6287
type: literature
title: "Ring-LWE in Polynomial Rings"
authors:
  - "Dépt. Informatique"
  - "rue d’Ulm"
year: null
venue: null
identifiers:
  eprint: null
  doi: null
  arxiv: null
  url: null
tags: [fhe, lattice, mpc, pairing, provable-security, signature]
confidence: reported
citation_verified: read
added: "2026-07-24"
superseded_by: null
---

## Contribution
The Ring-LWE problem, introduced by Lyubashevsky, Peikert, and Regev (Eurocrypt 2010), has been steadily finding many uses in numerous cryptographic applications. Still, the Ring-LWE problem defined in [LPR10] involves the fractional ideal R∨ , the dual of the ring R, which is the source of many theoretical and implementation technicalities.

## Key claims (as reported)
- Until now, getting rid of R∨ , required some relatively complex transformation that substantially increase the magnitude of the error polynomial and the practical complexity to sample it.
- It is only for rings R = Z[X]/(X n + 1) where n a power of 2, that this transformation is simple and benign.
- In this work we show that by applying a different, and much simpler transformation, one can transfer the results from [LPR10] into an “easyto-use” Ring-LWE setting (i.e. without the dual ring R∨ ), with only a very slight increase in the magnitude of the noise coefficients.
- Additionally, we show that creating the correct noise distribution can also be simplified by generating a Gaussian distribution over a particular extension ring of R, and then performing a reduction modulo f (X).

## Relevance to this program
Relevant to pairing-based reductions and endomorphism speedups (MOV/Frey-Rück special cases, GLV/GLS) that bound which curve classes are safe baselines.

## Not verified here
Entry generated during the 2026-07-24 bulk seeding pass from the local PDF's first two pages. Title/authors/year/venue were parsed heuristically and may be incomplete or mis-segmented; claims are relayed from the paper's abstract without independent verification. Upgrade to a fully verified entry after a careful read.

## Local copies
- `downloads/72930037 (1).pdf`
- `downloads/72930037 (2).pdf`
- `downloads/72930037 (3).pdf`
- `downloads/72930037.pdf`

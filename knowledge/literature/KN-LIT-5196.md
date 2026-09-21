---
id: KN-LIT-5196
type: literature
title: "Non-Interactive Verifiable Computing: Outsourcing Computation to Untrusted Workers"
authors:
  - "Rosario Gennaro"
  - "Craig Gentry"
  - "Bryan Parno"
year: null
venue: null
identifiers:
  eprint: null
  doi: null
  arxiv: null
  url: null
tags: [lattice, pairing]
confidence: reported
citation_verified: read
added: "2026-07-24"
superseded_by: null
---

## Contribution
We introduce and formalize the notion of Verifiable Computation, which enables a computationally weak client to “outsource” the computation of a function F on various dynamically-chosen inputs x1 , ..., xk to one or more workers. The workers return the result of the function evaluation, e.g., yi = F(xi ), as well as a proof that the computation of F was carried out correctly on the given value xi .

## Key claims (as reported)
- The primary constraint is that the verification of the proof should require substantially less computational effort than computing F(xi ) from scratch.
- We present a protocol that allows the worker to return a computationally-sound, non-interactive proof that can be verified in O(m · poly(λ)) time, where m is the bit-length of the output of F, and λ is a security parameter.
- The protocol requires a one-time pre-processing stage by the client which takes O(|C| · poly(λ)) time, where C is the smallest known Boolean circuit computing F.
- Unlike previous work in this area, our scheme also provides (at no additional cost) input and output privacy for the client, meaning that the workers do not learn any information about the xi or yi values.

## Relevance to this program
Relevant to pairing-based reductions and endomorphism speedups (MOV/Frey-Rück special cases, GLV/GLS) that bound which curve classes are safe baselines.

## Not verified here
Entry generated during the 2026-07-24 bulk seeding pass from the local PDF's first two pages. Title/authors/year/venue were parsed heuristically and may be incomplete or mis-segmented; claims are relayed from the paper's abstract without independent verification. Upgrade to a fully verified entry after a careful read.

## Local copies
- `downloads/62230459 (1).pdf`
- `downloads/62230459 (2).pdf`
- `downloads/62230459 (3).pdf`
- `downloads/62230459.pdf`

---
id: KN-LIT-6480
type: literature
title: "Securing Computation Against Continuous Leakage"
authors:
  - "Shafi Goldwasser"
  - "Guy N. Rothblum"
year: null
venue: null
identifiers:
  eprint: null
  doi: null
  arxiv: null
  url: null
tags: [pairing, side-channel, signature, symmetric]
confidence: reported
citation_verified: read
added: "2026-07-24"
superseded_by: null
---

## Contribution
We present a general method to compile any cryptographic algorithm into one which resists side channel attacks of the only computation leaks information variety for an unbounded number of executions. Our method uses as a building block a semantically secure subsidiary bit encryption scheme with the following additional operations: key refreshing, oblivious generation of cipher texts, leakage resilience re-generation, and blinded homomorphic evaluation of one single complete gate (e.g.

## Key claims (as reported)
- Furthermore, the security properties of the subsidiary encryption scheme should withstand bounded leakage incurred while performing each of the above operations.
- We show how to implement such a subsidiary encryption scheme under the DDH intractability assumption and the existence of a simple secure hardware component.
- The hardware component is independent of the encryption scheme secret key.
- The subsidiary encryption scheme resists leakage attacks where the leakage is computable in polynomial time and of length bounded by a constant fraction of the security parameter.

## Relevance to this program
Relevant to pairing-based reductions and endomorphism speedups (MOV/Frey-Rück special cases, GLV/GLS) that bound which curve classes are safe baselines.

## Not verified here
Entry generated during the 2026-07-24 bulk seeding pass from the local PDF's first two pages. Title/authors/year/venue were parsed heuristically and may be incomplete or mis-segmented; claims are relayed from the paper's abstract without independent verification. Upgrade to a fully verified entry after a careful read.

## Local copies
- `downloads/62230059 (1).pdf`
- `downloads/62230059 (2).pdf`
- `downloads/62230059 (3).pdf`
- `downloads/62230059.pdf`

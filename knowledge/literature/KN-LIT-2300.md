---
id: KN-LIT-2300
type: literature
title: "Accelerating HE Operations from Key Decomposition Technique"
authors:
  - "Miran Kim"
  - "Dongwon Lee"
year: null
venue: null
identifiers:
  eprint: null
  doi: null
  arxiv: null
  url: null
tags: [fhe, lattice, pairing, quantum, survey]
confidence: reported
citation_verified: read
added: "2026-07-24"
superseded_by: null
---

## Contribution
Lattice-based homomorphic encryption (HE) schemes are based on the noisy encryption technique, where plaintexts are masked with some random noise for security. Recent advanced HE schemes rely on a decomposition technique to manage the growth of noise, which involves a conversion of a ciphertext entry into a short vector followed by multiplication with an evaluation key.

## Key claims (as reported)
- Prior to this work, the decomposition procedure turns out to be the most time-consuming part, as it requires discrete Fourier transforms (DFTs) over the base ring for efficient polynomial arithmetic.
- In this paper, an expensive decomposition operation over a large modulus is replaced with relatively cheap operations over a ring of integers with a small bound.
- Notably, the cost of DFTs is reduced from quadratic to linear with the level of a ciphertext without any extra noise growth.
- We demonstrate the implication of our approach by applying it to the key-switching procedure.

## Relevance to this program
Relevant to pairing-based reductions and endomorphism speedups (MOV/Frey-Rück special cases, GLV/GLS) that bound which curve classes are safe baselines.

## Not verified here
Entry generated during the 2026-07-24 bulk seeding pass from the local PDF's first two pages. Title/authors/year/venue were parsed heuristically and may be incomplete or mis-segmented; claims are relayed from the paper's abstract without independent verification. Upgrade to a fully verified entry after a careful read.

## Local copies
- `downloads/140850257 (1).pdf`
- `downloads/140850257.pdf`

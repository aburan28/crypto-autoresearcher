---
id: KN-LIT-3413
type: literature
title: "Differential and invertibility properties of BLAKE"
authors:
  - "Jean-Philippe Aumasson"
  - "Jian Guo"
  - "Simon Knellwolf"
year: null
venue: null
identifiers:
  eprint: null
  doi: null
  arxiv: null
  url: null
tags: [cryptanalysis, hash, pairing, symmetric]
confidence: reported
citation_verified: read
added: "2026-07-24"
superseded_by: null
---

## Contribution
BLAKE is a hash function selected by NIST as one of the 14 second round candidates for the SHA-3 Competition. In this paper, we follow a bottom-up approach to exhibit properties of BLAKE and of its building blocks: based on differential properties of the internal function G, we show that a round of BLAKE is a permutation on the message space, and present an efficient inversion algorithm.

## Key claims (as reported)
- For 1.5 rounds we present an algorithm that finds preimages faster than in previous attacks.
- Discovered properties lead us to describe large classes of impossible differentials for two rounds of BLAKE’s internal permutation, and particular impossible differentials for five and six rounds, respectively for BLAKE-32 and BLAKE-64.
- Then, using a linear and rotation-free model, we describe near-collisions for four rounds of the compression function.

## Relevance to this program
Relevant to pairing-based reductions and endomorphism speedups (MOV/Frey-Rück special cases, GLV/GLS) that bound which curve classes are safe baselines.

## Not verified here
Entry generated during the 2026-07-24 bulk seeding pass from the local PDF's first two pages. Title/authors/year/venue were parsed heuristically and may be incomplete or mis-segmented; claims are relayed from the paper's abstract without independent verification. Upgrade to a fully verified entry after a careful read.

## Local copies
- `downloads/61470324 (1).pdf`
- `downloads/61470324 (2).pdf`
- `downloads/61470324 (3).pdf`
- `downloads/61470324.pdf`

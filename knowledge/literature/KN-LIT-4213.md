---
id: KN-LIT-4213
type: literature
title: "Higher-Order Differential Meet-in-The-Middle Preimage Attacks on SHA-1 and BLAKE"
authors:
  - "Thomas Espitau"
  - "Pierre-Alain Fouque"
  - "Pierre Karpman"
year: null
venue: null
identifiers:
  eprint: null
  doi: null
  arxiv: null
  url: null
tags: [cryptanalysis, hash, pairing]
confidence: reported
citation_verified: read
added: "2026-07-24"
superseded_by: null
---

## Contribution
At CRYPTO 2012, Knellwolf and Khovratovich presented a differential formulation of advanced meet-in-the-middle techniques for preimage attacks on hash functions. They demonstrated the usefulness of their approach by significantly improving the previously best known attacks on SHA-1 from CRYPTO 2009, increasing the number of attacked rounds from a 48-round one-block pseudo-preimage without padding and a 48-round two-block preimage without padding to a 57-round one-block preimage without padding and a 57-round two-block preimage with padding, out of 80 rounds for the full function.

## Key claims (as reported)
- In this work, we exploit further the differential view of meet-in-the-middle techniques and generalize it to higher-order differentials.
- Despite being an important technique dating from the mid-90’s, this is the first time higher-order differentials have been applied to meet-in-the-middle preimages.
- We show that doing so may lead to significant improvements to preimage attacks on hash functions with a simple linear message expansion.
- We extend the number of attacked rounds on SHA-1 to give a 62-round one-block preimage without padding, a 56-round one-block preimage with padding, and a 62-round two-block preimage with padding.

## Relevance to this program
Relevant to pairing-based reductions and endomorphism speedups (MOV/Frey-Rück special cases, GLV/GLS) that bound which curve classes are safe baselines.

## Not verified here
Entry generated during the 2026-07-24 bulk seeding pass from the local PDF's first two pages. Title/authors/year/venue were parsed heuristically and may be incomplete or mis-segmented; claims are relayed from the paper's abstract without independent verification. Upgrade to a fully verified entry after a careful read.

## Local copies
- `downloads/92160170 (1).pdf`
- `downloads/92160170 (2).pdf`
- `downloads/92160170.pdf`

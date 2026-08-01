---
id: KN-LIT-673
type: literature
title: "Extended Truncated-differential Distinguishers on Round-reduced AES"
authors:
  - "Zhenzhen Bao"
  - "Jian Guo"
  - "Eik List"
year: 2019
venue: "IACR Cryptology ePrint Archive"
identifiers:
  eprint: "iacr:2019/622"
  doi: null
  arxiv: null
  url: "https://eprint.iacr.org/2019/622"
tags: [cryptanalysis, pairing, survey, symmetric]
confidence: reported
citation_verified: read
added: "2026-07-24"
superseded_by: null
---

## Contribution
Distinguishers on round-reduced AES have attracted considerable attention in the recent years. While the number of rounds covered in key-recovery attacks did not increase, subspace, yoyo, mixture-differential, and multiple-of-n cryptanalysis advanced the understanding of the properties of the cipher.

## Key claims (as reported)
- For substitution-permutation networks, integral attacks are a suitable target for extension since they usually end after a linear layer sums several subcomponents.
- Based on results by Patarin, Chen et al. already observed that the expected number of collisions for a sum of permutations differs slightly from that for a random primitive.
- Though, their target remained lightweight primitives.
- The present work illustrates how the well-known integral distinguisher on three-round AES resembles a sum of PRPs and can be extended to truncated-differential distinguishers over 4 and 5 rounds.

## Relevance to this program
Relevant to pairing-based reductions and endomorphism speedups (MOV/Frey-Rück special cases, GLV/GLS) that bound which curve classes are safe baselines.

## Not verified here
Entry generated during the 2026-07-24 bulk seeding pass from the local PDF's first two pages. Title/authors/year/venue were parsed heuristically and may be incomplete or mis-segmented; claims are relayed from the paper's abstract without independent verification. Upgrade to a fully verified entry after a careful read.

## Local copies
- `downloads/2019-622.pdf`

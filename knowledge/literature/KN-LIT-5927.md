---
id: KN-LIT-5927
type: literature
title: "Producing Collisions for Panama, Instantaneously"
authors:
  - "Joan Daemen"
  - "Gilles Van Assche"
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
We present a practical attack on the Panama hash function that generates a collision in 26 evaluations of the state updating function. Our attack improves that of Rijmen and coworkers that had a complexity 282 , too high to produce a collision in practice.

## Key claims (as reported)
- This improvement comes mainly from the use of techniques to transfer conditions on the state to message words instead of trying many message pairs and using the ones for which the conditions are satisfied.
- Our attack works for any arbitrary prefix message, followed by a pair of suffix messages with a given difference.
- We give an example of a collision and make the collisiongenerating program available.
- Our attack does not affect the Panama stream cipher, that is still unbroken to the best of our knowledge.

## Relevance to this program
Relevant to pairing-based reductions and endomorphism speedups (MOV/Frey-Rück special cases, GLV/GLS) that bound which curve classes are safe baselines.

## Not verified here
Entry generated during the 2026-07-24 bulk seeding pass from the local PDF's first two pages. Title/authors/year/venue were parsed heuristically and may be incomplete or mis-segmented; claims are relayed from the paper's abstract without independent verification. Upgrade to a fully verified entry after a careful read.

## Local copies
- `downloads/45930001 (1).pdf`
- `downloads/45930001 (2).pdf`
- `downloads/45930001 (3).pdf`
- `downloads/45930001.pdf`

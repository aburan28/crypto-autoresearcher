---
id: KN-LIT-5725
type: literature
title: "Parameter-Hiding Order-Revealing Encryption without Pairings Cong Peng1[0000−0002−9958−3255] , Rongmao Chen2B[0000−0002−5113−387X]"
authors:
  - "Yi Wang"
  - "Debiao HeB"
year: null
venue: null
identifiers:
  eprint: null
  doi: null
  arxiv: null
  url: null
tags: [lattice, pairing, signature]
confidence: reported
citation_verified: read
added: "2026-07-24"
superseded_by: null
---

## Contribution
Order-Revealing Encryption (ORE) provides a practical solution for conducting range queries over encrypted data. Achieving a desirable privacy-efficiency tradeoff in designing ORE schemes has posed a significant challenge.

## Key claims (as reported)
- At Asiacrypt 2018, Cash et al. proposed Parameterhiding ORE (pORE), which specifically targets scenarios where the data distribution shape is known, but the underlying parameters (such as mean and variance) need to be protected.
- However, existing pORE constructions rely on impractical bilinear maps, limiting their real-world applicability.
- In this work, we propose an alternative and efficient method for constructing pORE using identification schemes.
- By leveraging the map-invariance property of identification schemes, we eliminate the need for pairing computations during ciphertext comparison.

## Relevance to this program
Relevant to pairing-based reductions and endomorphism speedups (MOV/Frey-Rück special cases, GLV/GLS) that bound which curve classes are safe baselines.

## Not verified here
Entry generated during the 2026-07-24 bulk seeding pass from the local PDF's first two pages. Title/authors/year/venue were parsed heuristically and may be incomplete or mis-segmented; claims are relayed from the paper's abstract without independent verification. Upgrade to a fully verified entry after a careful read.

## Local copies
- `downloads/14602096 (1).pdf`
- `downloads/14602096.pdf`

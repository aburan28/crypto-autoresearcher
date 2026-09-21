---
id: KN-LIT-3637
type: literature
title: "Efficient Techniques for High-Speed Elliptic Curve Cryptography"
authors:
  - "Patrick Longa"
  - "Catherine Gebotys"
year: null
venue: null
identifiers:
  eprint: null
  doi: null
  arxiv: null
  url: null
tags: [curve-arithmetic, elliptic-curve, endomorphism, extension-field, glv-gls, implementation, jacobian, pairing, prime-field, provable-security, quantum, survey]
confidence: reported
citation_verified: read
added: "2026-07-24"
superseded_by: null
---

## Contribution
In this paper, a thorough bottom-up optimization process (field, point and scalar arithmetic) is used to speed up the computation of elliptic curve point multiplication and report new speed records on modern x86-64 based processors. Our different implementations include elliptic curves using Jacobian coordinates, extended Twisted Edwards coordinates and the recently proposed Galbraith-Lin-Scott (GLS) method.

## Key claims (as reported)
- Compared to state-of-the-art implementations on identical platforms the proposed techniques provide up to 30% speed improvements.
- Additionally, compared to the best previous published results on similar platforms improvements up to 31% are observed.
- This research is crucial for advancing high speed cryptography on new emerging processor architectures.

## Relevance to this program
Relevant to pairing-based reductions and endomorphism speedups (MOV/Frey-Rück special cases, GLV/GLS) that bound which curve classes are safe baselines.

## Not verified here
Entry generated during the 2026-07-24 bulk seeding pass from the local PDF's first two pages. Title/authors/year/venue were parsed heuristically and may be incomplete or mis-segmented; claims are relayed from the paper's abstract without independent verification. Upgrade to a fully verified entry after a careful read.

## Local copies
- `downloads/62250075 (1).pdf`
- `downloads/62250075 (2).pdf`
- `downloads/62250075 (3).pdf`
- `downloads/62250075.pdf`

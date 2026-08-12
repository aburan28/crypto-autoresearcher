---
id: KN-LIT-7361
type: literature
title: "Understanding binary-Goppa decoding"
authors:
  - "Daniel J. Bernstein"
year: null
venue: null
identifiers:
  eprint: null
  doi: null
  arxiv: null
  url: null
tags: [implementation, pairing, pqc, side-channel, survey]
confidence: reported
citation_verified: read
added: "2026-07-24"
superseded_by: null
---

## Contribution
This paper reviews, from bottom to top, a polynomial-time algorithm to correct t errors in classical binary Goppa codes defined by squarefree degree-t polynomials. The proof is factored through a proof of a simple Reed–Solomon decoder, and the algorithm is simpler than Patterson’s algorithm.

## Key claims (as reported)
- All algorithm layers are expressed as Sage scripts backed by test scripts.
- All theorems are formally verified.
- The paper also covers the use of decoding inside the Classic McEliece cryptosystem, including reliable recognition of valid inputs.

## Relevance to this program
Relevant to pairing-based reductions and endomorphism speedups (MOV/Frey-Rück special cases, GLV/GLS) that bound which curve classes are safe baselines.

## Not verified here
Entry generated during the 2026-07-24 bulk seeding pass from the local PDF's first two pages. Title/authors/year/venue were parsed heuristically and may be incomplete or mis-segmented; claims are relayed from the paper's abstract without independent verification. Upgrade to a fully verified entry after a careful read.

## Local copies
- `downloads/goppadecoding-20220320.pdf`
- `downloads/goppadecoding-20220816.pdf`
- `downloads/goppadecoding-20230818.pdf`
- `downloads/goppadecoding-20240412.pdf`
- `downloads/goppadecoding-20240702.pdf`

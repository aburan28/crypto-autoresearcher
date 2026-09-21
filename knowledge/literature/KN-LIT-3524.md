---
id: KN-LIT-3524
type: literature
title: "Efficient and Round-Optimal Oblivious Transfer and Commitment with Adaptive Security?"
authors:
  - "Ran Canetti"
  - "Pratik Sarkar"
  - "Xiao Wang"
year: null
venue: null
identifiers:
  eprint: null
  doi: null
  arxiv: null
  url: null
tags: [lattice, mpc, pairing, provable-security, survey]
confidence: reported
citation_verified: read
added: "2026-07-24"
superseded_by: null
---

## Contribution
We construct the most efficient two-round adaptively secure bit-OT in the Common Random String (CRS) model. The scheme is UC secure under the Decisional Diffie-Hellman (DDH) assumption.

## Key claims (as reported)
- It incurs O(1) exponentiations and sends O(1) group elements, whereas the state of the art requires O(κ2 ) exponentiations and communicates poly(κ) bits, where κ is the computational security parameter.
- Along the way, we obtain several other efficient UC-secure OT protocols under DDH : – The most efficient yet two-round adaptive string-OT protocol assuming global programmable random oracle.
- Furthermore, the protocol can be made non-interactive in the simultaneous message setting, assuming random inputs for the sender. – The first two-round string-OT with amortized constant exponentiations and communication overhead which is secure in the global observable random oracle model. – The first two-round receiver equivocal string-OT in the CRS model that incurs constant computation and communication overhead.
- We also obtain the first non-interactive adaptive string UC-commitment in the CRS model which incurs a sublinear communication overhead in the security parameter.

## Relevance to this program
Relevant to pairing-based reductions and endomorphism speedups (MOV/Frey-Rück special cases, GLV/GLS) that bound which curve classes are safe baselines.

## Not verified here
Entry generated during the 2026-07-24 bulk seeding pass from the local PDF's first two pages. Title/authors/year/venue were parsed heuristically and may be incomplete or mis-segmented; claims are relayed from the paper's abstract without independent verification. Upgrade to a fully verified entry after a careful read.

## Local copies
- `downloads/12491404 (1).pdf`
- `downloads/12491404.pdf`

---
id: KN-LIT-7463
type: literature
title: "Verifiable Rotation of Homomorphic Encryptions"
authors:
  - "Sebastiaan de Hoogh"
  - "Berry Schoenmakers"
  - "Boris Škorić"
  - "José Villegas"
year: null
venue: null
identifiers:
  eprint: null
  doi: null
  arxiv: null
  url: null
tags: [fhe, mpc, pairing, zk-proof]
confidence: reported
citation_verified: read
added: "2026-07-24"
superseded_by: null
---

## Contribution
Similar to verifiable shuffling (mixing), we consider the problem of verifiable rotating a given list of homomorphic encryptions. The offset by which the list is rotated (cyclic shift) should remain hidden.

## Key claims (as reported)
- Basically, we will present zero-knowledge proofs of knowledge of a rotation offset and re-encryption exponents, which define how the input list is transformed into the output list.
- We also briefly address various applications of verifiable rotation, ranging from ‘fragile mixing’ as introduced by Reiter and Wang at CCS’04 to applications in protocols for secure multiparty computation and voting.
- We present two new, efficient protocols.
- Our first protocol is quite elegant and involves the use of the Discrete Fourier Transform (as well as the Fast Fourier Transform algorithm), and works under some reasonable conditions.

## Relevance to this program
Relevant to pairing-based reductions and endomorphism speedups (MOV/Frey-Rück special cases, GLV/GLS) that bound which curve classes are safe baselines.

## Not verified here
Entry generated during the 2026-07-24 bulk seeding pass from the local PDF's first two pages. Title/authors/year/venue were parsed heuristically and may be incomplete or mis-segmented; claims are relayed from the paper's abstract without independent verification. Upgrade to a fully verified entry after a careful read.

## Local copies
- `downloads/54430397 (1).pdf`
- `downloads/54430397 (2).pdf`
- `downloads/54430397 (3).pdf`
- `downloads/54430397.pdf`

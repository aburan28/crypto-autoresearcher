---
id: KN-LIT-4938
type: literature
title: "Mitigating Multi-Target Attacks in Hash-based Signatures"
authors:
  - "Andreas Hülsing"
  - "Joost Rijneveld"
  - "Fang Song"
year: null
venue: null
identifiers:
  eprint: null
  doi: null
  arxiv: null
  url: null
tags: [ecdsa, hash, pairing, pqc, provable-security, rsa, signature]
confidence: reported
citation_verified: read
added: "2026-07-24"
superseded_by: null
---

## Contribution
This work introduces XMSS-T, a new stateful hash-based signature scheme with tight security. Previous hash-based signatures are facing a loss of security, linear in performance parameters such as the total tree height.

## Key claims (as reported)
- Our new scheme can achieve the same security level but using hash functions with a smaller output length, which immediately leads to a smaller signature size.
- The same techniques also apply directly to the recent stateless hash-based signature scheme SPHINCS (Eurocrypt 2015), and the signature size is reduced as well.
- Being a little more specific and technical, the tight security stems from new multi-target notions of hash-function properties which we define and analyze.
- We show precise complexity for breaking these security properties under both classical and quantum generic attacks, thus establishing a reliable estimate for the quantum security of XMSS-T.

## Relevance to this program
Relevant to pairing-based reductions and endomorphism speedups (MOV/Frey-Rück special cases, GLV/GLS) that bound which curve classes are safe baselines.

## Not verified here
Entry generated during the 2026-07-24 bulk seeding pass from the local PDF's first two pages. Title/authors/year/venue were parsed heuristically and may be incomplete or mis-segmented; claims are relayed from the paper's abstract without independent verification. Upgrade to a fully verified entry after a careful read.

## Local copies
- `downloads/96140179 (1).pdf`
- `downloads/96140179 (2).pdf`
- `downloads/96140179 (3).pdf`
- `downloads/96140179 (4).pdf`
- `downloads/96140179.pdf`

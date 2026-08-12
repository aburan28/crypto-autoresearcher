---
id: KN-LIT-3609
type: literature
title: "Efficient Private Matching and Set Intersection"
authors:
  - "Michael J. Freedman"
  - "Kobbi Nissim"
  - "Benny Pinkas"
year: null
venue: null
identifiers:
  eprint: null
  doi: null
  arxiv: null
  url: null
tags: [complexity-theory, fhe, mpc, provable-security]
confidence: reported
citation_verified: read
added: "2026-07-24"
superseded_by: null
---

## Contribution
We consider the problem of computing the intersection of private datasets of two parties, where the datasets contain lists of elements taken from a large domain. This problem has many applications for online collaboration.

## Key claims (as reported)
- We present protocols, based on the use of homomorphic encryption and balanced hashing, for both semi-honest and malicious environments.
- For lists of length k, we obtain O(k) communication overhead and O(k ln ln k) computation.
- The protocol for the semihonest environment is secure in the standard model, while the protocol for the malicious environment is secure in the random oracle model.
- We also consider the problem of approximating the size of the intersection, show a linear lower-bound for the communication overhead of solving this problem, and provide a suitable secure protocol.

## Relevance to this program
Recorded for completeness of the local cryptography library. Peripheral to the ECDLP index-calculus program; cite in novelty checks for the tagged areas only.

## Not verified here
Entry generated during the 2026-07-24 bulk seeding pass from the local PDF's first two pages. Title/authors/year/venue were parsed heuristically and may be incomplete or mis-segmented; claims are relayed from the paper's abstract without independent verification. Upgrade to a fully verified entry after a careful read.

## Local copies
- `downloads/pm-eurocrypt04-lncs (1).pdf`
- `downloads/pm-eurocrypt04-lncs (2).pdf`
- `downloads/pm-eurocrypt04-lncs.pdf`

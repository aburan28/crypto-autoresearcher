---
id: KN-LIT-6712
type: literature
title: "SMILE: Set Membership from Ideal Lattices with Applications to Ring Signatures and Confidential Transactions"
authors:
  - "Vadim Lyubashevsky"
  - "Ngoc Khanh Nguyen"
  - "Gregor Seiler"
year: null
venue: null
identifiers:
  eprint: null
  doi: null
  arxiv: null
  url: null
tags: [dlp, elliptic-curve, lattice, pairing, quantum, signature, zk-proof]
confidence: reported
citation_verified: read
added: "2026-07-24"
superseded_by: null
---

## Contribution
In a set membership proof, the public information consists of a set of elements and a commitment. The prover then produces a zero-knowledge proof showing that the commitment is indeed to some element from the set.

## Key claims (as reported)
- This primitive is closely related to concepts like ring signatures and “one-out-of-many” proofs that underlie many anonymity and privacy protocols.
- The main result of this work is a new succinct lattice-based set membership proof whose size is logarithmic in the size of the set.
- We also give a transformation of our set membership proof to a ring signature scheme.
- The ring signature size is also logarithmic in the size of the public key set and has size 16 KB for a set of 25 elements, and 22 KB for a set of size 225 .

## Relevance to this program
Relevant to pairing-based reductions and endomorphism speedups (MOV/Frey-Rück special cases, GLV/GLS) that bound which curve classes are safe baselines.

## Not verified here
Entry generated during the 2026-07-24 bulk seeding pass from the local PDF's first two pages. Title/authors/year/venue were parsed heuristically and may be incomplete or mis-segmented; claims are relayed from the paper's abstract without independent verification. Upgrade to a fully verified entry after a careful read.

## Local copies
- `downloads/12826384 (1).pdf`
- `downloads/12826384.pdf`

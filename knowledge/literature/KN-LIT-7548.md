---
id: KN-LIT-7548
type: literature
title: "Zero-Knowledge Arguments for Matrix-Vector"
authors:
  - "Lattice-Based Group Encryption"
year: null
venue: null
identifiers:
  eprint: null
  doi: null
  arxiv: null
  url: null
tags: [dlp, lattice, pairing, quantum, signature, zk-proof]
confidence: reported
citation_verified: read
added: "2026-07-24"
superseded_by: null
---

## Contribution
Group encryption (GE) is the natural encryption analogue of group signatures in that it allows verifiably encrypting messages for some anonymous member of a group while providing evidence that the receiver is a properly certified group member. Should the need arise, an opening authority is capable of identifying the receiver of any ciphertext.

## Key claims (as reported)
- As introduced by Kiayias, Tsiounis and Yung (Asiacrypt’07), GE is motivated by applications in the context of oblivious retriever storage systems, anonymous third parties and hierarchical group signatures.
- This paper provides the first realization of group encryption under lattice assumptions.
- Our construction is proved secure in the standard model (assuming interaction in the proving phase) under the Learning-With-Errors (LWE) and Short-Integer-Solution (SIS) assumptions.
- As a crucial component of our system, we describe a new zero-knowledge argument system allowing to demonstrate that a given ciphertext is a valid encryption under some hidden but certified public key, which incurs to prove quadratic statements about LWE relations.

## Relevance to this program
Relevant to pairing-based reductions and endomorphism speedups (MOV/Frey-Rück special cases, GLV/GLS) that bound which curve classes are safe baselines.

## Not verified here
Entry generated during the 2026-07-24 bulk seeding pass from the local PDF's first two pages. Title/authors/year/venue were parsed heuristically and may be incomplete or mis-segmented; claims are relayed from the paper's abstract without independent verification. Upgrade to a fully verified entry after a careful read.

## Local copies
- `downloads/10031288 (1).pdf`
- `downloads/10031288.pdf`

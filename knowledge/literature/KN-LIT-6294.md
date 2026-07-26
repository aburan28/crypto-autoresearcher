---
id: KN-LIT-6294
type: literature
title: "Robust Multiparty Computation with Linear Communication Complexity"
authors:
  - "Martin Hirt"
  - "Jesper Buus Nielsen"
year: null
venue: null
identifiers:
  eprint: null
  doi: null
  arxiv: null
  url: null
tags: [fhe, mpc, pairing]
confidence: reported
citation_verified: read
added: "2026-07-24"
superseded_by: null
---

## Contribution
We present a robust multiparty computation protocol. The protocol is for the cryptographic model with open channels and a polytime adversary, and allows n parties to actively securely evaluate any poly-sized circuit with resilience t < n/2.

## Key claims (as reported)
- The total communication complexity in bits over the point-to-point channels is O(Snκ + n BC), where S is the size of the circuit being securely evaluated, κ is the security parameter and BC is the communication complexity of one broadcast of a κ-bit value.
- This means the average number of bits sent and received by a single party is O(Sκ + BC), which is almost independent of the number of participating parties.
- This is the first robust multiparty computation protocol with this property.

## Relevance to this program
Relevant to pairing-based reductions and endomorphism speedups (MOV/Frey-Rück special cases, GLV/GLS) that bound which curve classes are safe baselines.

## Not verified here
Entry generated during the 2026-07-24 bulk seeding pass from the local PDF's first two pages. Title/authors/year/venue were parsed heuristically and may be incomplete or mis-segmented; claims are relayed from the paper's abstract without independent verification. Upgrade to a fully verified entry after a careful read.

## Local copies
- `downloads/41170458 (1).pdf`
- `downloads/41170458 (2).pdf`
- `downloads/41170458 (3).pdf`
- `downloads/41170458.pdf`

---
id: KN-LIT-7454
type: literature
title: "Verifiable Oblivious Storage"
authors:
  - "Daniel Apon"
  - "Jonathan Katz"
  - "Elaine Shi"
  - "Aishwarya Thiruvengadam"
year: null
venue: null
identifiers:
  eprint: null
  doi: null
  arxiv: null
  url: null
tags: [complexity-theory, fhe, hash, lattice, mpc, pairing, zk-proof]
confidence: reported
citation_verified: read
added: "2026-07-24"
superseded_by: null
---

## Contribution
We formalize the notion of Verifiable Oblivious Storage (VOS), where a client outsources the storage of data to a server while ensuring data confidentiality, access pattern privacy, and integrity and freshness of data accesses. VOS generalizes the notion of Oblivious RAM (ORAM) in that it allows the server to perform computation, and also explicitly considers data integrity and freshness.

## Key claims (as reported)
- We show that allowing server-side computation enables us to construct asymptotically more efficient VOS schemes whose bandwidth overhead cannot be matched by any ORAM scheme, due to a known lower bound by Goldreich and Ostrovsky.
- Specifically, for large block sizes we can construct a VOS scheme with constant bandwidth per query; further, answering queries requires only poly-logarithmic server computation.
- We describe applications of VOS to Dynamic Proofs of Retrievability, and RAM-model secure multi-party computation.

## Relevance to this program
Relevant to pairing-based reductions and endomorphism speedups (MOV/Frey-Rück special cases, GLV/GLS) that bound which curve classes are safe baselines.

## Not verified here
Entry generated during the 2026-07-24 bulk seeding pass from the local PDF's first two pages. Title/authors/year/venue were parsed heuristically and may be incomplete or mis-segmented; claims are relayed from the paper's abstract without independent verification. Upgrade to a fully verified entry after a careful read.

## Local copies
- `downloads/83830206 (1).pdf`
- `downloads/83830206 (2).pdf`
- `downloads/83830206 (3).pdf`
- `downloads/83830206 (4).pdf`
- `downloads/83830206 (5).pdf`
- `downloads/83830206.pdf`

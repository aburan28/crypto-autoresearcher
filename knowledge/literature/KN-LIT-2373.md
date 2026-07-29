---
id: KN-LIT-2373
type: literature
title: "Aggregatable Distributed Key Generation Kobi Gurkan ? , Philipp Jovanovic ?? , Mary Maller ? ? ? , Sarah Meiklejohn"
authors:
  - "Gilad Stern"
  - "Alin Tomescu"
year: null
venue: null
identifiers:
  eprint: null
  doi: null
  arxiv: null
  url: null
tags: [mov-fr, mpc, pairing, provable-security, signature]
confidence: reported
citation_verified: read
added: "2026-07-24"
superseded_by: null
---

## Contribution
In this paper, we introduce a distributed key generation (DKG) protocol with aggregatable and publicly-verifiable transcripts. Compared with prior publicly-verifiable approaches, our DKG reduces the size of the final transcript and the time to verify it from O(n2 ) to O(n log n), where n denotes the number of parties.

## Key claims (as reported)
- As compared with prior non-publicly-verifiable approaches, our DKG leverages gossip rather than all-to-all communication to reduce verification and communication complexity.
- We also revisit existing DKG security definitions, which are quite strong, and propose new and natural relaxations.
- As a result, we can prove the security of our aggregatable DKG as well as that of several existing DKGs, including the popular Pedersen variant.
- We show that, under these new definitions, these existing DKGs can be used to yield secure threshold variants of popular cryptosystems such as El-Gamal encryption and BLS signatures.

## Relevance to this program
Relevant to pairing-based reductions and endomorphism speedups (MOV/Frey-Rück special cases, GLV/GLS) that bound which curve classes are safe baselines.

## Not verified here
Entry generated during the 2026-07-24 bulk seeding pass from the local PDF's first two pages. Title/authors/year/venue were parsed heuristically and may be incomplete or mis-segmented; claims are relayed from the paper's abstract without independent verification. Upgrade to a fully verified entry after a careful read.

## Local copies
- `downloads/126960109 (1).pdf`
- `downloads/126960109.pdf`

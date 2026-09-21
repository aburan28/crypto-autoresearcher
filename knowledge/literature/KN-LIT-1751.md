---
id: KN-LIT-1751
type: literature
title: "Multi-key Fully Homomorphic Encryption with Non-Interactive Setup in the Plain Model"
authors:
  - "Seonhong Min"
  - "Jeongeun Park"
  - "Yongsoo Song"
year: 2026
venue: "IACR Cryptology ePrint Archive"
identifiers:
  eprint: "iacr:2026/322"
  doi: null
  arxiv: null
  url: "https://eprint.iacr.org/2026/322"
tags: [fhe, lattice, mov-fr, mpc]
confidence: reported
citation_verified: read
added: "2026-07-24"
superseded_by: null
---

## Contribution
Multi-key fully homomorphic encryption (MKFHE) enables computation over encrypted data under multiple different keys. Constructing MKFHE without any trusted or interactive setup remains an open problem.

## Key claims (as reported)
- In the context of MKFHE, a trusted setup is often assumed to mean the use of a common random string (CRS).
- In this paper, we present the first MKFHE scheme in the plain model (i.e., without any trusted or interactive setup) based on the RLWE assumption.
- Specifically, we construct a multi-key somewhat homomorphic encryption based on the RLWE assumption and extend it to a multi-key variant of the Gentry-Sahai-Waters (GSW) scheme with a circular security assumption.
- Our design yields a 2-round multi-party computation (MPC) in the plain model against semi-malicious adversaries.

## Relevance to this program
Relevant to pairing-based reductions and endomorphism speedups (MOV/Frey-Rück special cases, GLV/GLS) that bound which curve classes are safe baselines.

## Not verified here
Entry generated during the 2026-07-24 bulk seeding pass from the local PDF's first two pages. Title/authors/year/venue were parsed heuristically and may be incomplete or mis-segmented; claims are relayed from the paper's abstract without independent verification. Upgrade to a fully verified entry after a careful read.

## Local copies
- `downloads/2026-322.pdf`

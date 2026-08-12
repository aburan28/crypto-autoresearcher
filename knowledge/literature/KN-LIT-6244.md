---
id: KN-LIT-6244
type: literature
title: "Reusable Two-Round MPC from DDH"
authors:
  - "James Bartusek"
  - "Sanjam Garg"
  - "Daniel Masny"
  - "Pratyay Mukherjee"
year: null
venue: null
identifiers:
  eprint: null
  doi: null
  arxiv: null
  url: null
tags: [glv-gls, lattice, mpc, provable-security, quantum]
confidence: reported
citation_verified: read
added: "2026-07-24"
superseded_by: null
---

## Contribution
We present a reusable two-round multi-party computation (MPC) protocol from the Decisional Diffie Hellman assumption (DDH). In particular, we show how to upgrade any secure two-round MPC protocol to allow reusability of its first message across multiple computations, using Homomorphic Secret Sharing (HSS) and pseudorandom functions in N C 1 — each of which can be instantiated from DDH.

## Key claims (as reported)
- In our construction, if the underlying two-round MPC protocol is secure against semi-honest adversaries (in the plain model) then so is our reusable two-round MPC protocol.
- Similarly, if the underlying two-round MPC protocol is secure against malicious adversaries (in the common random/reference string model) then so is our reusable two-round MPC protocol.
- Previously, such reusable two-round MPC protocols were only known under assumptions on lattices.
- At a technical level, we show how to upgrade any two-round MPC protocol to a first message succinct two-round MPC protocol, where the first message of the protocol is generated independently of the computed circuit (though it is not reusable).

## Relevance to this program
Relevant to pairing-based reductions and endomorphism speedups (MOV/Frey-Rück special cases, GLV/GLS) that bound which curve classes are safe baselines.

## Not verified here
Entry generated during the 2026-07-24 bulk seeding pass from the local PDF's first two pages. Title/authors/year/venue were parsed heuristically and may be incomplete or mis-segmented; claims are relayed from the paper's abstract without independent verification. Upgrade to a fully verified entry after a careful read.

## Local copies
- `downloads/12550196 (1).pdf`
- `downloads/12550196.pdf`

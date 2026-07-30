---
id: KN-LIT-5805
type: literature
title: "Post-Quantum Multi-Party Computation"
authors:
  - "Amit Agarwal∗"
  - "James Bartusek"
  - "Vipul Goyal"
  - "Dakshita Khurana"
year: null
venue: null
identifiers:
  eprint: null
  doi: null
  arxiv: null
  url: null
tags: [dlp, fhe, lattice, mpc, pairing, pqc, provable-security, zk-proof]
confidence: reported
citation_verified: read
added: "2026-07-24"
superseded_by: null
---

## Contribution
We initiate the study of multi-party computation for classical functionalities in the plain model, with security against malicious quantum adversaries. We observe that existing techniques readily give a polynomial-round protocol, but our main result is a construction of constant-round post-quantum multi-party computation.

## Key claims (as reported)
- We assume mildly super-polynomial quantum hardness of learning with errors (LWE), and quantum polynomial hardness of an LWE-based circular security assumption.
- Along the way, we develop the following cryptographic primitives that may be of independent interest: – A spooky encryption scheme for relations computable by quantum circuits, from the quantum hardness of (a circular variant of) the LWE problem.
- This immediately yields the first quantum multi-key fully-homomorphic encryption scheme with classical keys. – A constant-round post-quantum non-malleable commitment scheme, from the mildly super-polynomial quantum hardness of LWE.
- To prove the security of our protocol, we develop a new straight-line non-black-box simulation technique against parallel sessions that does not clone the adversary’s state.

## Relevance to this program
Relevant to pairing-based reductions and endomorphism speedups (MOV/Frey-Rück special cases, GLV/GLS) that bound which curve classes are safe baselines.

## Not verified here
Entry generated during the 2026-07-24 bulk seeding pass from the local PDF's first two pages. Title/authors/year/venue were parsed heuristically and may be incomplete or mis-segmented; claims are relayed from the paper's abstract without independent verification. Upgrade to a fully verified entry after a careful read.

## Local copies
- `downloads/126960101 (1).pdf`
- `downloads/126960101.pdf`

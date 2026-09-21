---
id: KN-LIT-4757
type: literature
title: "Linear-Size Constant-Query IOPs for Delegating Computation"
authors:
  - "Eli Ben-Sasson"
  - "Alessandro Chiesa"
  - "Lior Goldberg"
  - "Tom Gur"
  - "Michael Riabzev"
year: null
venue: null
identifiers:
  eprint: null
  doi: null
  arxiv: null
  url: null
tags: [complexity-theory, pairing, survey, zk-proof]
confidence: reported
citation_verified: read
added: "2026-07-24"
superseded_by: null
---

## Contribution
We study the problem of delegating computations via interactive proofs that can be probabilistically checked. Known as interactive oracle proofs (IOPs), these proofs extend probabilistically checkable proofs (PCPs) to multi-round protocols, and have received much attention due to their application to constructing cryptographic proofs (such as succinct non-interactive arguments).

## Key claims (as reported)
- The relevant complexity measures for IOPs in this context are prover and verifier time, and query complexity.
- We construct highly efficient IOPs for a rich class of nondeterministic algebraic computations, which includes succinct versions of arithmetic circuit satisfiability and rank-one constraint system (R1CS) satisfiability.
- For a time-T computation, we obtain prover arithmetic complexity O(T log T ) and verifier complexity polylog(T ).
- These IOPs are the first to simultaneously achieve the state of the art in prover complexity, due to [14], and in verifier complexity, due to [7].

## Relevance to this program
Relevant to pairing-based reductions and endomorphism speedups (MOV/Frey-Rück special cases, GLV/GLS) that bound which curve classes are safe baselines.

## Not verified here
Entry generated during the 2026-07-24 bulk seeding pass from the local PDF's first two pages. Title/authors/year/venue were parsed heuristically and may be incomplete or mis-segmented; claims are relayed from the paper's abstract without independent verification. Upgrade to a fully verified entry after a careful read.

## Local copies
- `downloads/11891149 (1).pdf`
- `downloads/11891149.pdf`

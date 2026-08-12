---
id: KN-LIT-5916
type: literature
title: "Private Polynomial Commitments and Applications to MPC"
authors:
  - "Rishabh Bhadauria"
  - "Carmit Hazay"
year: null
venue: null
identifiers:
  eprint: null
  doi: null
  arxiv: null
  url: null
tags: [fhe, mpc, pairing, zk-proof]
confidence: reported
citation_verified: read
added: "2026-07-24"
superseded_by: null
---

## Contribution
Polynomial commitment schemes allow a prover to commit to a polynomial and later reveal the evaluation of the polynomial on an arbitrary point along with proof of validity. This object is central in the design of many cryptographic schemes such as zero-knowledge proofs and verifiable secret sharing.

## Key claims (as reported)
- In the standard definition, the polynomial is known to the prover whereas the evaluation points are not private.
- In this paper, we put forward the notion of private polynomial commitments that capture additional privacy guarantees, where the evaluation points are hidden from the verifier while the polynomial is hidden from both.
- We provide concretely efficient constructions that allow simultaneously batch the verification of many evaluations with a small additive overhead.
- As an application, we design a new concretely efficient multi-party private set-intersection with malicious security and improved asymptotic communication and space complexities.

## Relevance to this program
Relevant to pairing-based reductions and endomorphism speedups (MOV/Frey-Rück special cases, GLV/GLS) that bound which curve classes are safe baselines.

## Not verified here
Entry generated during the 2026-07-24 bulk seeding pass from the local PDF's first two pages. Title/authors/year/venue were parsed heuristically and may be incomplete or mis-segmented; claims are relayed from the paper's abstract without independent verification. Upgrade to a fully verified entry after a careful read.

## Local copies
- `downloads/13940130 (1).pdf`
- `downloads/13940130.pdf`

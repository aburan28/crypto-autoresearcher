---
id: KN-LIT-6629
type: literature
title: "Sigma protocols for MQ, PKP and SIS, and fishy signature schemes"
authors:
  - "Ward Beullens"
year: null
venue: null
identifiers:
  eprint: null
  doi: null
  arxiv: null
  url: null
tags: [finite-field, lattice, mov-fr, pairing, pqc, signature, zk-proof]
confidence: reported
citation_verified: read
added: "2026-07-24"
superseded_by: null
---

## Contribution
This work presents sigma protocols to prove knowledge of: – a solution to a system of quadratic polynomials, – a solution to an instance of the Permuted Kernel Problem and – a witness for a variety of lattice statements (including SIS). Our sigma protocols have soundness error 1/q 0 , where q 0 is any number bounded by the size of the underlying finite field.

## Key claims (as reported)
- This is much better than existing proofs, which have soundness error 2/3 or (q 0 + 1)/2q 0 .
- The prover and verifier time our proofs are O(q 0 ).
- We achieve this by first constructing so-called sigma protocols with helper, which are sigma protocols where the prover and the verifier are assisted by a trusted third party, and then eliminating the helper from the proof with a “cut-and-choose” protocol.
- We apply the Fiat-Shamir transform to obtain signature schemes with security proof in the QROM.

## Relevance to this program
Relevant to pairing-based reductions and endomorphism speedups (MOV/Frey-Rück special cases, GLV/GLS) that bound which curve classes are safe baselines.

## Not verified here
Entry generated during the 2026-07-24 bulk seeding pass from the local PDF's first two pages. Title/authors/year/venue were parsed heuristically and may be incomplete or mis-segmented; claims are relayed from the paper's abstract without independent verification. Upgrade to a fully verified entry after a careful read.

## Local copies
- `downloads/12105262 (1).pdf`
- `downloads/12105262.pdf`

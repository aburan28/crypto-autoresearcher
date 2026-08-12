---
id: KN-LIT-6449
type: literature
title: "Secure Multiparty Computation with Free Branching"
authors:
  - "Aarushi Goel"
  - "Mathias Hall-Andersen"
  - "Aditya Hegde"
  - "Abhishek Jain"
year: null
venue: null
identifiers:
  eprint: null
  doi: null
  arxiv: null
  url: null
tags: [fhe, mpc, pairing, survey]
confidence: reported
citation_verified: read
added: "2026-07-24"
superseded_by: null
---

## Contribution
We study secure multi-party computation (MPC) protocols for branching circuits that contain multiple sub-circuits (i.e., branches) and the output of the circuit is that of single “active” branch. Crucially, the identity of the active branch must remain hidden from the protocol participants.

## Key claims (as reported)
- While such circuits can be securely computed by evaluating each branch and then multiplexing the output, such an approach incurs a communication cost linear in the size of the entire circuit.
- To alleviate this, a series of recent works have investigated the problem of reducing the communication cost of branching executions inside MPC (without relying on fully homomorphic encryption).
- Most notably, the stacked garbling paradigm [Heath and Kolesnikov, CRYPTO’20] yields garbled circuits for branching circuits whose size only depends on the size of the largest branch.
- Presently, however, it is not known how to obtain similar communication improvements for secure computation involving more than two parties.

## Relevance to this program
Relevant to pairing-based reductions and endomorphism speedups (MOV/Frey-Rück special cases, GLV/GLS) that bound which curve classes are safe baselines.

## Not verified here
Entry generated during the 2026-07-24 bulk seeding pass from the local PDF's first two pages. Title/authors/year/venue were parsed heuristically and may be incomplete or mis-segmented; claims are relayed from the paper's abstract without independent verification. Upgrade to a fully verified entry after a careful read.

## Local copies
- `downloads/132760348 (1).pdf`
- `downloads/132760348.pdf`

---
id: KN-LIT-3207
type: literature
title: "Crowd Verifiable Zero-Knowledge and End-to-end Verifiable Multiparty Computation"
authors:
  - "Foteini Baldimtsi"
  - "Aggelos Kiayias"
  - "Thomas Zacharias"
year: null
venue: null
identifiers:
  eprint: null
  doi: null
  arxiv: null
  url: null
tags: [lattice, mov-fr, mpc, pairing, provable-security, zk-proof]
confidence: reported
citation_verified: read
added: "2026-07-24"
superseded_by: null
---

## Contribution
Auditing a secure multiparty computation (MPC) protocol entails the validation of the protocol transcript by a third party that is otherwise untrusted. In this work, we introduce the concept of end-to-end verifiable MPC (VMPC), that requires the validation to provide a correctness guarantee even in the setting that all servers, trusted setup primitives and all the client systems utilized by the input-providing users of the MPC protocol are subverted by an adversary.

## Key claims (as reported)
- To instantiate VMPC, we introduce a new concept in the setting of zero-knowlegde protocols that we term crowd verifiable zero-knowledge (CVZK).
- A CVZK protocol enables a prover to convince a set of verifiers about a certain statement, even though each one individually contributes a small amount of entropy for verification and some of them are adversarially controlled.
- Given CVZK, we present a VMPC protocol that is based on discretelogarithm related assumptions.
- At the high level of adversity that VMPC is meant to withstand, it is infeasible to ensure perfect correctness, thus we investigate the classes of functions and verifiability relations that are feasible in our framework, and present a number of possible applications the underlying functions of which can be implemented via VMPC.

## Relevance to this program
Relevant to pairing-based reductions and endomorphism speedups (MOV/Frey-Rück special cases, GLV/GLS) that bound which curve classes are safe baselines.

## Not verified here
Entry generated during the 2026-07-24 bulk seeding pass from the local PDF's first two pages. Title/authors/year/venue were parsed heuristically and may be incomplete or mis-segmented; claims are relayed from the paper's abstract without independent verification. Upgrade to a fully verified entry after a careful read.

## Local copies
- `downloads/12491295 (1).pdf`
- `downloads/12491295.pdf`

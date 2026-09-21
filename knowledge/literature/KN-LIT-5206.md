---
id: KN-LIT-5206
type: literature
title: "Non-Interactive Zero-Knowledge Proofs to Multiple Verifiers"
authors:
  - "Kang Yang"
  - "Xiao Wang"
year: null
venue: null
identifiers:
  eprint: null
  doi: null
  arxiv: null
  url: null
tags: [pairing, provable-security, quantum, zk-proof]
confidence: reported
citation_verified: read
added: "2026-07-24"
superseded_by: null
---

## Contribution
In this paper, we study zero-knowledge (ZK) proofs for circuit satisfiability that can prove to n verifiers at a time efficiently. The proofs are secure against the collusion of a prover and a subset of t verifiers.

## Key claims (as reported)
- We refer to such ZK proofs as multi-verifier zero-knowledge (MVZK) proofs and focus on the case that a majority of verifiers are honest (i.e., t < n/2).
- We construct efficient MVZK protocols in the random oracle model where the prover sends one message to each verifier, while the verifiers only exchange one round of messages.
- When the threshold of corrupted verifiers t < n/2, the prover sends 1/2 + o(1) field elements per multiplication gate to every verifier; when t < n(1/2 − ) for some constant 0 <  < 1/2, we can further reduce the communication to O(1/n) field elements per multiplication gate per verifier.
- Our MVZK protocols demonstrate particularly high scalability: the proofs are streamable and only require a memory proportional to what is needed to evaluate the circuit in the clear.

## Relevance to this program
Relevant to pairing-based reductions and endomorphism speedups (MOV/Frey-Rück special cases, GLV/GLS) that bound which curve classes are safe baselines.

## Not verified here
Entry generated during the 2026-07-24 bulk seeding pass from the local PDF's first two pages. Title/authors/year/venue were parsed heuristically and may be incomplete or mis-segmented; claims are relayed from the paper's abstract without independent verification. Upgrade to a fully verified entry after a careful read.

## Local copies
- `downloads/137910246 (1).pdf`
- `downloads/137910246.pdf`

---
id: KN-LIT-5282
type: literature
title: "Oblivious Transfer from Zero-Knowledge Proofs"
authors:
  - "Or How to Achieve Round-Optimal Quantum Oblivious"
year: null
venue: null
identifiers:
  eprint: null
  doi: null
  arxiv: null
  url: null
tags: [complexity-theory, elliptic-curve, glv-gls, lattice, mpc, pairing, pqc, provable-security, rsa, zk-proof]
confidence: reported
citation_verified: read
added: "2026-07-24"
superseded_by: null
---

## Contribution
We provide a generic construction to turn any classical ZeroKnowledge (ZK) protocol into a composable (quantum) oblivious transfer (OT) protocol, mostly lifting the round-complexity properties and security guarantees (plain-model/statistical security/unstructured functions. . . ) of the ZK protocol to the resulting OT protocol. Such a construction is unlikely to exist classically as Cryptomania is believed to be different from Minicrypt.

## Key claims (as reported)
- In particular, by instantiating our construction using Non-Interactive ZK (NIZK), we provide the first round-optimal (2-message) quantum OT protocol secure in the random oracle model, and round-optimal extensions to string and k-out-of-n OT.
- At the heart of our construction lies a new method that allows us to prove properties on a received quantum state without revealing additional information on it, even in a non-interactive way and/or with statistical guarantees when using an appropriate classical ZK protocol.
- We can notably prove that a state has been partially measured (with arbitrary constraints on the set of measured qubits), without revealing any additional information on this set.
- This notion can be seen as an analog of ZK to quantum states, and we expect it to be of independent interest as it extends complexity theory to quantum languages, as illustrated by the two new complexity classes we introduce, ZKstatesQIP and ZKstatesQMA.

## Relevance to this program
Relevant to pairing-based reductions and endomorphism speedups (MOV/Frey-Rück special cases, GLV/GLS) that bound which curve classes are safe baselines.

## Not verified here
Entry generated during the 2026-07-24 bulk seeding pass from the local PDF's first two pages. Title/authors/year/venue were parsed heuristically and may be incomplete or mis-segmented; claims are relayed from the paper's abstract without independent verification. Upgrade to a fully verified entry after a careful read.

## Local copies
- `downloads/14438378 (1).pdf`
- `downloads/14438378.pdf`

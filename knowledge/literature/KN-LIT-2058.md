---
id: KN-LIT-2058
type: literature
title: "A Framework for Statistically Sender Private OT with Optimal Rate"
authors:
  - "Pedro Branco Nico Döttling"
  - "Akshayaram Srinivasan"
year: null
venue: null
identifiers:
  eprint: null
  doi: null
  arxiv: null
  url: null
tags: [complexity-theory, hash, lattice, mpc, provable-security, zk-proof]
confidence: reported
citation_verified: read
added: "2026-07-24"
superseded_by: null
---

## Contribution
Statistical sender privacy (SSP) is the strongest achievable security notion for two-message oblivious transfer (OT) in the standard model, providing statistical security against malicious receivers and computational security against semi-honest senders. In this work we provide a novel construction of SSP OT from the Decisional Diffie-Hellman (DDH) and the Learning Parity with Noise (LPN) assumptions achieving (asymptotically) optimal amortized communication complexity, i.e. it achieves rate 1.

## Key claims (as reported)
- Concretely, the total communication complexity for k OT instances is 2k(1 + o(1)), which (asymptotically) approaches the information-theoretic lower bound.
- Previously, it was only known how to realize this primitive using heavy rate-1 FHE techniques [Brakerski et al., Gentry and Halevi TCC’19].
- At the heart of our construction is a primitive called statistical co-PIR, essentially a a public key encryption scheme which statistically erases bits of the message in a few hidden locations.
- Our scheme achieves nearly optimal ciphertext size and provides statistical security against malicious receivers.

## Relevance to this program
Recorded for completeness of the local cryptography library. Peripheral to the ECDLP index-calculus program; cite in novelty checks for the tagged areas only.

## Not verified here
Entry generated during the 2026-07-24 bulk seeding pass from the local PDF's first two pages. Title/authors/year/venue were parsed heuristically and may be incomplete or mis-segmented; claims are relayed from the paper's abstract without independent verification. Upgrade to a fully verified entry after a careful read.

## Local copies
- `downloads/140850388 (1).pdf`
- `downloads/140850388.pdf`

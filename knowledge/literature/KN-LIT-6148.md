---
id: KN-LIT-6148
type: literature
title: "Rate-1 Quantum Fully Homomorphic Encryption"
authors:
  - "Orestis Chardouvelis∗"
  - "Nico Döttling"
  - "Giulio Malavolta"
year: null
venue: null
identifiers:
  eprint: null
  doi: null
  arxiv: null
  url: null
tags: [fhe, lattice, pairing, provable-security]
confidence: reported
citation_verified: read
added: "2026-07-24"
superseded_by: null
---

## Contribution
Secure function evaluation (SFE) allows Alice to publish an encrypted version of her input m such that Bob (holding a circuit C) can send a single message that reveals C(m) to Alice, and nothing more. Security is required to hold against malicious parties, that may behave arbitrarily.

## Key claims (as reported)
- In this work we study the notion of SFE in the quantum setting, where Alice outputs an encrypted quantum state |ψi and learns C(|ψi) after receiving Bob’s message.
- We show that, assuming the quantum hardness of the learning with errors problem (LWE), there exists an SFE protocol for quantum computation with communication complexity (| |ψi | + |C(|ψi)|) · (1 + o(1)) which is nearly optimal.
- This result is obtained by two main technical steps, which might be of independent interest.
- Specifically, we show (i) a construction of a rate-1 quantum fully-homomorphic encryption and (ii) a generic transformation to achieve malicious circuit privacy in the quantum setting.

## Relevance to this program
Relevant to pairing-based reductions and endomorphism speedups (MOV/Frey-Rück special cases, GLV/GLS) that bound which curve classes are safe baselines.

## Not verified here
Entry generated during the 2026-07-24 bulk seeding pass from the local PDF's first two pages. Title/authors/year/venue were parsed heuristically and may be incomplete or mis-segmented; claims are relayed from the paper's abstract without independent verification. Upgrade to a fully verified entry after a careful read.

## Local copies
- `downloads/130420209 (1).pdf`
- `downloads/130420209.pdf`

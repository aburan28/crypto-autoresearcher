---
id: KN-LIT-6078
type: literature
title: "Quantum Authentication and Encryption with Key Recycling Or: How to Re-use a One-Time Pad Even if P = NP — Safely & Feasibly"
authors:
  - "Serge Fehr"
  - "Louis Salvail"
year: null
venue: null
identifiers:
  eprint: null
  doi: null
  arxiv: null
  url: null
tags: [hash, lattice, mov-fr, pairing]
confidence: reported
citation_verified: read
added: "2026-07-24"
superseded_by: null
---

## Contribution
We propose an information-theoretically secure encryption scheme for classical messages with quantum ciphertexts that offers detection of eavesdropping attacks, and re-usability of the key in case no eavesdropping took place: the entire key can be securely re-used for encrypting new messages as long as no attack is detected. This is known to be impossible for fully classical schemes, where there is no way to detect plain eavesdropping attacks.

## Key claims (as reported)
- This particular application of quantum techniques to cryptography was originally proposed by Bennett, Brassard and Breidbart in 1982, even before proposing quantum-key-distribution, and a simple candidate scheme was suggested but no rigorous security analysis was given.
- The idea was picked up again in 2005, when Damgård, Pedersen and Salvail suggested a new scheme for the same task, but now with a rigorous security analysis.
- However, their scheme is much more demanding in terms of quantum capabilities: it requires the users to have a quantum computer.
- In contrast, and like the original scheme by Bennett et al., our new scheme requires from the honest users merely to prepare and measure single BB84 qubits.

## Relevance to this program
Relevant to pairing-based reductions and endomorphism speedups (MOV/Frey-Rück special cases, GLV/GLS) that bound which curve classes are safe baselines.

## Not verified here
Entry generated during the 2026-07-24 bulk seeding pass from the local PDF's first two pages. Title/authors/year/venue were parsed heuristically and may be incomplete or mis-segmented; claims are relayed from the paper's abstract without independent verification. Upgrade to a fully verified entry after a careful read.

## Local copies
- `downloads/10210108 (1).pdf`
- `downloads/10210108.pdf`

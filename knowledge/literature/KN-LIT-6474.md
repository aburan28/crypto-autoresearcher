---
id: KN-LIT-6474
type: literature
title: "Secure Two-Party Quantum Evaluation of Unitaries Against Specious Adversaries"
authors: []
year: null
venue: null
identifiers:
  eprint: null
  doi: null
  arxiv: null
  url: null
tags: [mpc, pairing, provable-security, quantum]
confidence: reported
citation_verified: read
added: "2026-07-24"
superseded_by: null
---

## Contribution
We describe how any two-party quantum computation, specified by a unitary which simultaneously acts on the registers of both parties, can be privately implemented against a quantum version of classical semi-honest adversaries that we call specious. Our construction requires two ideal functionalities to garantee privacy: a private SWAP between registers held by the two parties and a classical private AND-box equivalent to oblivious transfer.

## Key claims (as reported)
- If the unitary to be evaluated is in the Clifford group then only one call to SWAP is required for privacy.
- On the other hand, any unitary not in the Clifford requires one call to an AND-box per R-gate in the circuit.
- Since SWAP is itself in the Clifford group, this functionality is universal for the private evaluation of any unitary in that group.
- SWAP can be built from a classical bit commitment scheme or an AND-box but an AND-box cannot be constructed from SWAP.

## Relevance to this program
Relevant to pairing-based reductions and endomorphism speedups (MOV/Frey-Rück special cases, GLV/GLS) that bound which curve classes are safe baselines.

## Not verified here
Entry generated during the 2026-07-24 bulk seeding pass from the local PDF's first two pages. Title/authors/year/venue were parsed heuristically and may be incomplete or mis-segmented; claims are relayed from the paper's abstract without independent verification. Upgrade to a fully verified entry after a careful read.

## Local copies
- `downloads/62230682 (1).pdf`
- `downloads/62230682 (2).pdf`
- `downloads/62230682 (3).pdf`
- `downloads/62230682.pdf`

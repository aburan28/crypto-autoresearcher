---
id: KN-LIT-2148
type: literature
title: "A New Framework for Quantum Oblivious Transfer"
authors:
  - "Amit Agarwal⋆"
  - "James Bartusek⋆⋆"
  - "Dakshita Khurana⋆ ⋆ ⋆"
year: null
venue: null
identifiers:
  eprint: null
  doi: null
  arxiv: null
  url: null
tags: [hash, mpc, pairing, provable-security]
confidence: reported
citation_verified: read
added: "2026-07-24"
superseded_by: null
---

## Contribution
We present a new template for building oblivious transfer from quantum information that we call the “fixed basis” framework. Our framework departs from prior work (eg., Crepeau and Kilian, FOCS ’88) by fixing the correct choice of measurement basis used by each player, except for some hidden trap qubits that are intentionally measured in a conjugate basis.

## Key claims (as reported)
- We instantiate this template in the quantum random oracle model (QROM) to obtain simple protocols that implement, with security against malicious adversaries: – Non-interactive random-input bit OT in a model where parties share EPR pairs a priori. – Two-round random-input bit OT without setup, obtained by showing that the protocol above remains secure even if the (potentially malicious) OT receiver sets up the EPR pairs. – Three-round chosen-input string OT from BB84 states without entanglement or setup.
- This improves upon natural variations of the CK88 template that require at least five rounds.
- Along the way, we develop technical tools that may be of independent interest.
- We prove that natural functions like XOR enable seedless randomness extraction from certain quantum sources of entropy.

## Relevance to this program
Relevant to pairing-based reductions and endomorphism speedups (MOV/Frey-Rück special cases, GLV/GLS) that bound which curve classes are safe baselines.

## Not verified here
Entry generated during the 2026-07-24 bulk seeding pass from the local PDF's first two pages. Title/authors/year/venue were parsed heuristically and may be incomplete or mis-segmented; claims are relayed from the paper's abstract without independent verification. Upgrade to a fully verified entry after a careful read.

## Local copies
- `downloads/14004214 (1).pdf`
- `downloads/14004214.pdf`

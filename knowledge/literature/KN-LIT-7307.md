---
id: KN-LIT-7307
type: literature
title: "Two-Round Adaptively Secure MPC from Indistinguishability Obfuscation"
authors:
  - "Sanjam Garg"
  - "Antigoni Polychroniadou"
year: null
venue: null
identifiers:
  eprint: null
  doi: null
  arxiv: null
  url: null
tags: [mpc, pairing, provable-security]
confidence: reported
citation_verified: read
added: "2026-07-24"
superseded_by: null
---

## Contribution
Adaptively secure Multi-Party Computation (MPC) first studied by Canetti, Feige, Goldreich, and Naor in 1996, is a fundamental notion in cryptography. Adaptive security is particularly hard to achieve in settings where arbitrary number of parties can be corrupted and honest parties are not trusted to properly erase their internal state.

## Key claims (as reported)
- We did not know how to realize constant round protocols for this task even if we were to restrict ourselves to semi-honest adversaries and to the simpler two-party setting.
- Specifically the round complexity of known protocols grows with the depth of the circuit the parties are trying to compute.
- In this work, using indistinguishability obfuscation, we construct a UC two-round Multi-Party computation protocol secure against any active, adaptive adversary corrupting an arbitrary number of parties.

## Relevance to this program
Relevant to pairing-based reductions and endomorphism speedups (MOV/Frey-Rück special cases, GLV/GLS) that bound which curve classes are safe baselines.

## Not verified here
Entry generated during the 2026-07-24 bulk seeding pass from the local PDF's first two pages. Title/authors/year/venue were parsed heuristically and may be incomplete or mis-segmented; claims are relayed from the paper's abstract without independent verification. Upgrade to a fully verified entry after a careful read.

## Local copies
- `downloads/90150614 (1).pdf`
- `downloads/90150614.pdf`

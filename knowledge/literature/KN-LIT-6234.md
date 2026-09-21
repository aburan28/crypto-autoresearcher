---
id: KN-LIT-6234
type: literature
title: "Resource-Restricted Cryptography: Revisiting MPC Bounds in the Proof-of-Work Era 1"
authors:
  - "Juan Garay"
  - "Aggelos Kiayias"
  - "Rafail M. Ostrovsky"
  - "Giorgos Panagiotakos"
year: null
venue: null
identifiers:
  eprint: null
  doi: null
  arxiv: null
  url: null
tags: [complexity-theory, mov-fr, mpc, pairing, provable-security]
confidence: reported
citation_verified: read
added: "2026-07-24"
superseded_by: null
---

## Contribution
the core properties that the resource-restricting paradigm oers by means of a functionality wrapper, in the UC frame- work, which when applied to a standard point-to-point network restricts the ability (of the adversary) to send new messages. We show that such a wrapped network can be implemented using the resource-restricting paradigmconcretely, using PoWs and honest majority of computing powerand that the traditional t < n/3 impossibility results fail when the parties have access to such a network.

## Key claims (as reported)
- Our construction is in the fresh Common Reference String (CRS) modeli.e., it assumes a CRS which becomes available to the parties at the same time as to the adversary.
- We then present constructions for BA and MPC, which given access to such a network tolerate t < n/2 corruptions without assuming a private correlated randomness setup.
- We also show how to remove the freshness assumption from the CRS by leveraging the power of a random oracle.
- Our MPC protocol achieves the standard notion of MPC security, where parties might have dedicated roles, as is for example the case in Oblivious Transfer protocols.

## Relevance to this program
Relevant to pairing-based reductions and endomorphism speedups (MOV/Frey-Rück special cases, GLV/GLS) that bound which curve classes are safe baselines.

## Not verified here
Entry generated during the 2026-07-24 bulk seeding pass from the local PDF's first two pages. Title/authors/year/venue were parsed heuristically and may be incomplete or mis-segmented; claims are relayed from the paper's abstract without independent verification. Upgrade to a fully verified entry after a careful read.

## Local copies
- `downloads/12105413 (1).pdf`
- `downloads/12105413.pdf`

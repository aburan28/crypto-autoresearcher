---
id: KN-LIT-4788
type: literature
title: "Low Cost Constant Round MPC"
authors:
  - "Combining BMR"
  - "Oblivious Transfer"
year: null
venue: null
identifiers:
  eprint: null
  doi: null
  arxiv: null
  url: null
tags: [fhe, hash, mpc, provable-security, symmetric, zk-proof]
confidence: reported
citation_verified: read
added: "2026-07-24"
superseded_by: null
---

## Contribution
In this work, we present two new universally composable, actively secure, constant round multi-party protocols for generating BMR garbled circuits with free-XOR and reduced costs. Our first protocol takes a generic approach using any secret-sharing based MPC protocol for binary circuits, and a correlated oblivious transfer functionality.

## Key claims (as reported)
- Our specialized protocol uses secret-sharing based MPC with informationtheoretic MACs.
- This approach is less general, but requires no additional correlated OTs to compute the garbled circuit.
- In both approaches, the underlying secret-sharing based protocol is only used for one secure F2 multiplication per AND gate.
- An interesting consequence of this is that, with current techniques, constant round MPC for binary circuits is not much more expensive than practical, non-constant round protocols.

## Relevance to this program
Recorded for completeness of the local cryptography library. Peripheral to the ECDLP index-calculus program; cite in novelty checks for the tagged areas only.

## Not verified here
Entry generated during the 2026-07-24 bulk seeding pass from the local PDF's first two pages. Title/authors/year/venue were parsed heuristically and may be incomplete or mis-segmented; claims are relayed from the paper's abstract without independent verification. Upgrade to a fully verified entry after a careful read.

## Local copies
- `downloads/106240250 (1).pdf`
- `downloads/106240250.pdf`

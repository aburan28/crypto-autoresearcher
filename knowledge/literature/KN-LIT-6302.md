---
id: KN-LIT-6302
type: literature
title: "Robustness for Free in Unconditional Multi-Party Computation"
authors:
  - "Martin Hirt"
  - "Ueli Maurer"
year: null
venue: null
identifiers:
  eprint: null
  doi: null
  arxiv: null
  url: null
tags: [finite-field, mpc, provable-security]
confidence: reported
citation_verified: read
added: "2026-07-24"
superseded_by: null
---

## Contribution
We present a very efficient multi-party computation protocol unconditionally secure against an active adversary. The security is maximal, i.e., active corruption of up to t < n/3 of the n players is tolerated.

## Key claims (as reported)
- The communication complexity for securely evaluating a circuit with m multiplication gates over a finite field is O(mn2 ) field elements, including the communication required for simulating broadcast, but excluding some overhead costs (independent of m) for sharing the inputs and reconstructing the outputs.
- This corresponds to the complexity of the best known protocols for the passive model, where the corrupted players are guaranteed not to deviate from the protocol.
- The complexity of our protocol may well be optimal.
- The constant overhead factor for robustness is small and the protocol is practical.

## Relevance to this program
Recorded for completeness of the local cryptography library. Peripheral to the ECDLP index-calculus program; cite in novelty checks for the tagged areas only.

## Not verified here
Entry generated during the 2026-07-24 bulk seeding pass from the local PDF's first two pages. Title/authors/year/venue were parsed heuristically and may be incomplete or mis-segmented; claims are relayed from the paper's abstract without independent verification. Upgrade to a fully verified entry after a careful read.

## Local copies
- `downloads/21390100 (1).pdf`
- `downloads/21390100 (2).pdf`
- `downloads/21390100 (3).pdf`
- `downloads/21390100.pdf`

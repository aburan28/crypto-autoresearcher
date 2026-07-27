---
id: KN-LIT-7302
type: literature
title: "Two-Party Computing with Encrypted Data"
authors:
  - "Seung Geol Choi"
  - "Ariel Elbaz"
  - "Ari Juels"
  - "Tal Malkin"
  - "Moti Yung"
year: null
venue: null
identifiers:
  eprint: null
  doi: null
  arxiv: null
  url: null
tags: [fhe, mpc, provable-security, rsa]
confidence: reported
citation_verified: read
added: "2026-07-24"
superseded_by: null
---

## Contribution
We consider a new model for online secure computation on encrypted inputs in the presence of malicious adversaries. The inputs are independent of the circuit computed in the sense that they can be contributed by separate third parties.

## Key claims (as reported)
- The model attempts to emulate as closely as possible the model of “Computing with Encrypted Data” that was put forth in 1978 by Rivest, Adleman and Dertouzos which involved a single online message.
- In our model, two parties publish their public keys in an offline stage, after which any party (i.e., any of the two and any third party) can publish encryption of their local inputs.
- Then in an on-line stage, given any common input circuit C and its set of inputs from among the published encryptions, the first party sends a single message to the second party, who completes the computation.

## Relevance to this program
Recorded for completeness of the local cryptography library. Peripheral to the ECDLP index-calculus program; cite in novelty checks for the tagged areas only.

## Not verified here
Entry generated during the 2026-07-24 bulk seeding pass from the local PDF's first two pages. Title/authors/year/venue were parsed heuristically and may be incomplete or mis-segmented; claims are relayed from the paper's abstract without independent verification. Upgrade to a fully verified entry after a careful read.

## Local copies
- `downloads/48330299 (1).pdf`
- `downloads/48330299 (2).pdf`
- `downloads/48330299 (3).pdf`
- `downloads/48330299.pdf`

---
id: KN-LIT-7419
type: literature
title: "Untagging Tor: A Formal Treatment of Onion Encryption"
authors:
  - "Jean Paul Degabriele"
  - "Martijn Stam"
year: null
venue: null
identifiers:
  eprint: null
  doi: null
  arxiv: null
  url: null
tags: [protocol, provable-security]
confidence: reported
citation_verified: read
added: "2026-07-24"
superseded_by: null
---

## Contribution
Tor is a primary tool for maintaining anonymity online. It provides a low-latency, circuit-based, bidirectional secure channel between two parties through a network of onion routers, with the aim of obscuring exactly who is talking to whom, even to adversaries controlling part of the network.

## Key claims (as reported)
- Tor relies heavily on cryptographic techniques, yet its onion encryption scheme is susceptible to tagging attacks (Fu and Ling, 2009), which allow an active adversary controlling the first and last node of a circuit to deanonymize with near-certainty.
- This contrasts with less active traffic correlation attacks, where the same adversary can at best deanonymize with high probability.
- The Tor project has been actively looking to defend against tagging attacks and its most concrete alternative is proposal 261, which specifies a new onion encryption scheme based on a variable-input-length tweakable cipher.
- We provide a formal treatment of low-latency, circuit-based onion encryption, relaxed to the unidirectional setting, by expanding existing secure channel notions to the new setting and introducing circuit hiding to capture the anonymity aspect of Tor.

## Relevance to this program
Recorded for completeness of the local cryptography library. Peripheral to the ECDLP index-calculus program; cite in novelty checks for the tagged areas only.

## Not verified here
Entry generated during the 2026-07-24 bulk seeding pass from the local PDF's first two pages. Title/authors/year/venue were parsed heuristically and may be incomplete or mis-segmented; claims are relayed from the paper's abstract without independent verification. Upgrade to a fully verified entry after a careful read.

## Local copies
- `downloads/10822314 (1).pdf`
- `downloads/10822314.pdf`

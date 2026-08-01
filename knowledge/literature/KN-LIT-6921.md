---
id: KN-LIT-6921
type: literature
title: "Synchronous Consensus with Optimal Asynchronous Fallback Guarantees"
authors:
  - "Erica Blum"
  - "Jonathan Katz"
  - "Julian Loss"
year: null
venue: null
identifiers:
  eprint: null
  doi: null
  arxiv: null
  url: null
tags: [mpc]
confidence: reported
citation_verified: read
added: "2026-07-24"
superseded_by: null
---

## Contribution
Typically, protocols for Byzantine agreement (BA) are designed to run in either a synchronous network (where all messages are guaranteed to be delivered within some known time ∆ from when they are sent) or an asynchronous network (where messages may be arbitrarily delayed). Protocols designed for synchronous networks are generally insecure if the network in which they run does not ensure synchrony; protocols designed for asynchronous networks are (of course) secure in a synchronous setting as well, but in that case tolerate a lower fraction of faults than would have been possible if synchrony had been assumed from the start.

## Key claims (as reported)
- Fix some number of parties n, and 0 < ta < n/3 ≤ ts < n/2.
- We ask whether it is possible (given a public-key infrastructure) to design a BA protocol that is resilient to (1) ts corruptions when run in a synchronous network and (2) ta faults even if the network happens to be asynchronous.
- We show matching feasibility and infeasibility results demonstrating that this is possible if and only if ta + 2 · ts < n.

## Relevance to this program
Recorded for completeness of the local cryptography library. Peripheral to the ECDLP index-calculus program; cite in novelty checks for the tagged areas only.

## Not verified here
Entry generated during the 2026-07-24 bulk seeding pass from the local PDF's first two pages. Title/authors/year/venue were parsed heuristically and may be incomplete or mis-segmented; claims are relayed from the paper's abstract without independent verification. Upgrade to a fully verified entry after a careful read.

## Local copies
- `downloads/11891182 (1).pdf`
- `downloads/11891182.pdf`

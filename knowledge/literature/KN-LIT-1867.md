---
id: KN-LIT-1867
type: literature
title: "Security Analysis of Bitcoin’s V2 Transport Protocol: Exploiting Design Implications for"
authors:
  - "Sustained Eclipse"
  - "Downgrade Attacks"
year: 2026
venue: "arXiv preprint"
identifiers:
  eprint: null
  doi: "10.4230/LIPIcs...1"
  arxiv: "2605.19715"
  url: "https://arxiv.org/abs/2605.19715"
tags: [lattice, pairing, quantum]
confidence: reported
citation_verified: read
added: "2026-07-24"
superseded_by: null
---

## Contribution
Bitcoin recently introduced a new protocol for the encryption of peer-to-peer (P2P) communication. The protocol, known as V2 P2P transport, represents a big step towards securing the overlay network against various previously-known attack vectors.

## Key claims (as reported)
- Based on an analysis of V2 P2P transport, this work examines the current viability of said attacks and concludes that while they are now remediated, alternative attacks and paths to similar objectives exist.
- The identified shortcomings are conceptual (and not implementation bugs) and even applicable to other P2P networks.
- We show how a network-level attacker can identify application messages using the length of TCP payloads, can eclipse a target node by taking advantage of how encrypted communication channels work and can downgrade all of a node’s connections to the unencrypted protocol by using the mechanisms designed for compatibility.
- We validate our contributions using a combination of network measurements, emulations and simulations.

## Relevance to this program
Relevant to pairing-based reductions and endomorphism speedups (MOV/Frey-Rück special cases, GLV/GLS) that bound which curve classes are safe baselines.

## Not verified here
Entry generated during the 2026-07-24 bulk seeding pass from the local PDF's first two pages. Title/authors/year/venue were parsed heuristically and may be incomplete or mis-segmented; claims are relayed from the paper's abstract without independent verification. Upgrade to a fully verified entry after a careful read.

## Local copies
- `downloads/2605.19715v1.pdf`

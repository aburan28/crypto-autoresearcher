---
id: KN-LIT-3593
type: literature
title: "Efficient Network Coding Signatures in the Standard Model"
authors:
  - "Dario Catalano"
  - "Dario Fiore"
  - "Bogdan Warinschi"
year: null
venue: null
identifiers:
  eprint: null
  doi: null
  arxiv: null
  url: null
tags: [hash, provable-security, signature]
confidence: reported
citation_verified: read
added: "2026-07-24"
superseded_by: null
---

## Contribution
Network Coding is a routing technique where each node may actively modify the received packets before transmitting them. While this departure from passive networks improves throughput and resilience to packet loss it renders transmission susceptible to pollution attacks where nodes can misbehave and change in a malicious way the messages transmitted.

## Key claims (as reported)
- Nodes cannot use standard signature schemes to authenticate the modified packets: this would require knowledge of the original sender’s signing key.
- Network coding signature schemes offer a cryptographic solution to this problem.
- Very roughly, such signatures allow signing vector spaces (or rather bases of such spaces), and these signatures are homomorphic: given signatures on a set of vectors it is possible to create signatures for any linear combination of these vectors.
- Designing such schemes is a difficult task, and the few existent constructions either rely on random oracles or are rather inefficient.

## Relevance to this program
Recorded for completeness of the local cryptography library. Peripheral to the ECDLP index-calculus program; cite in novelty checks for the tagged areas only.

## Not verified here
Entry generated during the 2026-07-24 bulk seeding pass from the local PDF's first two pages. Title/authors/year/venue were parsed heuristically and may be incomplete or mis-segmented; claims are relayed from the paper's abstract without independent verification. Upgrade to a fully verified entry after a careful read.

## Local copies
- `downloads/72930680 (1).pdf`
- `downloads/72930680 (2).pdf`
- `downloads/72930680 (3).pdf`
- `downloads/72930680.pdf`

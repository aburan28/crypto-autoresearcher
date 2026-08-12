---
id: KN-LIT-5785
type: literature
title: "Poly Onions: Achieving Anonymity in the Presence of Churn"
authors:
  - "Megumi Ando"
  - "Miranda Christ"
  - "Anna Lysyanskaya"
  - "Tal Malkin"
year: null
venue: null
identifiers:
  eprint: null
  doi: null
  arxiv: null
  url: null
tags: [provable-security]
confidence: reported
citation_verified: read
added: "2026-07-24"
superseded_by: null
---

## Contribution
Onion routing is a popular approach towards anonymous communication. Practical implementations are widely used (for example, Tor has millions of users daily), but are vulnerable to various traffic correlation attacks, and the theoretical foundations, despite recent progress, still lag behind.

## Key claims (as reported)
- In particular, all works that model onion routing protocols and prove their security only address a single run, where each party sends and receives a single message of fixed length, once.
- Moreover, they all assume a static network setting, where the parties are stable throughout the lifetime of the protocol.
- In contrast, real networks have a high rate of churn (nodes joining and exiting the network), real users want to send multiple messages, and realistic adversaries may observe multiple runs of the protocol.
- We initiate a formal treatment of onion routing in a setting with multiple runs over a dynamic network with churn.

## Relevance to this program
Recorded for completeness of the local cryptography library. Peripheral to the ECDLP index-calculus program; cite in novelty checks for the tagged areas only.

## Not verified here
Entry generated during the 2026-07-24 bulk seeding pass from the local PDF's first two pages. Title/authors/year/venue were parsed heuristically and may be incomplete or mis-segmented; claims are relayed from the paper's abstract without independent verification. Upgrade to a fully verified entry after a careful read.

## Local copies
- `downloads/137470111 (1).pdf`
- `downloads/137470111.pdf`

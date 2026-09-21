---
id: KN-LIT-4341
type: literature
title: "Identity-Based Encryption Secure"
authors:
  - "Jian Weng"
  - "Yunlei Zhao"
year: null
venue: null
identifiers:
  eprint: null
  doi: null
  arxiv: null
  url: null
tags: [hash, lattice, mpc, provable-security]
confidence: reported
citation_verified: read
added: "2026-07-24"
superseded_by: null
---

## Contribution
Security against selective opening attack (SOA) requires that in a multi-user setting, even if an adversary has access to all ciphertexts from users, and adaptively corrupts some fraction of the users by exposing not only their messages but also the random coins, the remaining unopened messages retain their privacy. Recently, Bellare, Waters and Yilek considered SOA-security in the identity-based setting, and presented the first identity-based encryption (IBE) schemes that are proven secure against selective opening chosen plaintext attack (SO-CPA).

## Key claims (as reported)
- However, how to achieve SO-CCA security for IBE is still open.
- In this paper, we introduce a new primitive called extractable IBE and define its IND-ID-CCA security notion.
- We present a generic construction of SO-CCA secure IBE from an IND-ID-CCA secure extractable IBE with “One-Sided Public Openability”(1SPO), a collision-resistant hash function and a strengthened cross-authentication code.
- Finally, we propose two concrete constructions of extractable 1SPO-IBE schemes, resulting in the first simulation-based SO-CCA secure IBE schemes without random oracles.

## Relevance to this program
Recorded for completeness of the local cryptography library. Peripheral to the ECDLP index-calculus program; cite in novelty checks for the tagged areas only.

## Not verified here
Entry generated during the 2026-07-24 bulk seeding pass from the local PDF's first two pages. Title/authors/year/venue were parsed heuristically and may be incomplete or mis-segmented; claims are relayed from the paper's abstract without independent verification. Upgrade to a fully verified entry after a careful read.

## Local copies
- `downloads/84410219 (1).pdf`
- `downloads/84410219 (2).pdf`
- `downloads/84410219 (3).pdf`
- `downloads/84410219.pdf`

---
id: KN-LIT-4795
type: literature
title: "Low-Communication Multiparty Triple Generation for SPDZ from Ring-LPN?"
authors:
  - "Damiano Abram"
  - "Peter Scholl"
year: null
venue: null
identifiers:
  eprint: null
  doi: null
  arxiv: null
  url: null
tags: [fhe, mpc, prime-field, provable-security, quantum, zk-proof]
confidence: reported
citation_verified: read
added: "2026-07-24"
superseded_by: null
---

## Contribution
The SPDZ protocol for multi-party computation relies on a correlated randomness setup consisting of authenticated, multiplication triples. A recent line of work by Boyle et al.

## Key claims (as reported)
- (Crypto 2019, Crypto 2020) has investigated the possibility of producing this correlated randomness in a silent preprocessing phase, which involves a “small” setup protocol with less communication than the total size of the triples being produced.
- These works do this using a tool called a pseudorandom correlation generator (PCG), which allows a large batch of correlated randomness to be compressed into a set of smaller, correlated seeds.
- However, existing methods for compressing SPDZ triples only apply to the 2-party setting.
- In this work, we construct a PCG for producing SPDZ triples over large prime fields in the multi-party setting.

## Relevance to this program
Recorded for completeness of the local cryptography library. Peripheral to the ECDLP index-calculus program; cite in novelty checks for the tagged areas only.

## Not verified here
Entry generated during the 2026-07-24 bulk seeding pass from the local PDF's first two pages. Title/authors/year/venue were parsed heuristically and may be incomplete or mis-segmented; claims are relayed from the paper's abstract without independent verification. Upgrade to a fully verified entry after a careful read.

## Local copies
- `downloads/131770119 (1).pdf`
- `downloads/131770119.pdf`

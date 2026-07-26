---
id: KN-LIT-7050
type: literature
title: "The Rebound Attack: Cryptanalysis of Reduced Whirlpool and Grøstl"
authors:
  - "Florian Mendel"
  - "Christian Rechberger"
  - "Martin Schläffer and"
year: null
venue: null
identifiers:
  eprint: null
  doi: null
  arxiv: null
  url: null
tags: [cryptanalysis, hash, symmetric]
confidence: reported
citation_verified: read
added: "2026-07-24"
superseded_by: null
---

## Contribution
In this work, we propose the rebound attack, a new tool for the cryptanalysis of hash functions. The idea of the rebound attack is to use the available degrees of freedom in a collision attack to efficiently bypass the low probability parts of a differential trail.

## Key claims (as reported)
- The rebound attack consists of an inbound phase with a match-in-the-middle part to exploit the available degrees of freedom, and a subsequent probabilistic outbound phase.
- Especially on AES based hash functions, the rebound attack leads to new attacks for a surprisingly high number of rounds.
- We use the rebound attack to construct collisions for 4.5 rounds of the 512-bit hash function Whirlpool with a complexity of 2120 compression function evaluations and negligible memory requirements.
- The attack can be extended to a near-collision on 7.5 rounds of the compression function of Whirlpool and 8.5 rounds of the similar hash function Maelstrom.

## Relevance to this program
Recorded for completeness of the local cryptography library. Peripheral to the ECDLP index-calculus program; cite in novelty checks for the tagged areas only.

## Not verified here
Entry generated during the 2026-07-24 bulk seeding pass from the local PDF's first two pages. Title/authors/year/venue were parsed heuristically and may be incomplete or mis-segmented; claims are relayed from the paper's abstract without independent verification. Upgrade to a fully verified entry after a careful read.

## Local copies
- `downloads/56650270 (1).pdf`
- `downloads/56650270 (2).pdf`
- `downloads/56650270 (3).pdf`
- `downloads/56650270.pdf`

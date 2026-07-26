---
id: KN-LIT-2940
type: literature
title: "Collision Attacks against the Knudsen-Preneel Compression Functions"
authors:
  - "Onur Özen"
  - "Martijn Stam"
year: null
venue: "IACR Cryptology ePrint Archive"
identifiers:
  eprint: null
  doi: null
  arxiv: null
  url: null
tags: [complexity-theory, hash, symmetric]
confidence: reported
citation_verified: read
added: "2026-07-24"
superseded_by: null
---

## Contribution
Knudsen and Preneel (Asiacrypt’96 and Crypto’97) introduced a hash function design in which a linear error-correcting code is used to build a wide-pipe compression function from underlying blockciphers operating in Davies-Meyer mode. Their main design goal was to deliver compression functions with collision resistance up to, and even beyond, the block size of the underlying blockciphers.

## Key claims (as reported)
- In this paper, we present new collision-finding attacks against these compression functions using the ideas of an unpublished work of Watanabe and the preimage attack of Özen, Shrimpton, and Stam (FSE’10).
- In brief, our best attack has a time complexity strictly smaller than the block-size for all but two of the parameter sets.
- Consequently, the time complexity lower bound proven by Knudsen and Preneel is incorrect and the compression functions do not achieve the security level they were designed for.

## Relevance to this program
Recorded for completeness of the local cryptography library. Peripheral to the ECDLP index-calculus program; cite in novelty checks for the tagged areas only.

## Not verified here
Entry generated during the 2026-07-24 bulk seeding pass from the local PDF's first two pages. Title/authors/year/venue were parsed heuristically and may be incomplete or mis-segmented; claims are relayed from the paper's abstract without independent verification. Upgrade to a fully verified entry after a careful read.

## Local copies
- `downloads/6477076 (1).pdf`
- `downloads/6477076 (2).pdf`
- `downloads/6477076 (3).pdf`
- `downloads/6477076.pdf`

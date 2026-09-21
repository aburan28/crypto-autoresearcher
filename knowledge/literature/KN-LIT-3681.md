---
id: KN-LIT-3681
type: literature
title: End-to-end Design of a PUF-based Privacy Preserving Authentication Protocol
authors:
- Aydin Aysu
- Ege Gulcan
- Daisuke Moriyama
- Patrick Schaumont
year: null
venue: null
identifiers:
  eprint: null
  doi: null
  arxiv: null
  url: null
tags:
- puf
- authentication
- privacy
- implementation
confidence: reported
citation_verified: read
added: '2026-07-24'
superseded_by: null
---

## Contribution
We demonstrate a prototype implementation of a provably secure protocol that supports privacy-preserving mutual authentication between a server and a constrained device. Our proposed protocol is based on a physically unclonable function (PUF) and it is optimized for resource-constrained platforms.

## Key claims (as reported)
- The reported results include a full protocol analysis, the design of its building blocks, their integration into a constrained device, and finally its performance evaluation.
- We show how to obtain efficient implementations for each of the building blocks of the protocol, including a fuzzy extractor with a novel helper-data construction technique, a truly random number generator (TRNG), and a pseudo-random function (PRF).
- The prototype is implemented on a SASEBO-GII board, using the on-board SRAM as the source of entropy for the PUF and the TRNG.
- We present three different implementations.

## Relevance to this program
Recorded for completeness of the local cryptography library. Peripheral to the ECDLP index-calculus program; cite in novelty checks for the tagged areas only.

## Not verified here
Entry generated during the 2026-07-24 bulk seeding pass from the local PDF's first two pages. Title/authors/year/venue were parsed heuristically and may be incomplete or mis-segmented; claims are relayed from the paper's abstract without independent verification. Upgrade to a fully verified entry after a careful read.

## Local copies
- `downloads/92930538 (1).pdf`
- `downloads/92930538.pdf`

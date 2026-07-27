---
id: KN-LIT-7096
type: literature
title: "Thinking Outside the Superbox"
authors:
  - "Nicolas Bordes"
  - "Joan Daemen"
  - "Daniël Kuijsters"
  - "Gilles Van Assche"
year: null
venue: "IACR Cryptology ePrint Archive"
identifiers:
  eprint: null
  doi: null
  arxiv: null
  url: null
tags: [hash, symmetric]
confidence: reported
citation_verified: read
added: "2026-07-24"
superseded_by: null
---

## Contribution
Designing a block cipher or cryptographic permutation can be approached in many different ways. One such approach, popularized by AES, consists in grouping the bits along the S-box boundaries, e.g., in bytes, and in consistently processing them in these groups.

## Key claims (as reported)
- This aligned approach leads to hierarchical structures like superboxes that make it possible to reason about the differential and linear propagation properties using combinatorial arguments.
- In contrast, an unaligned approach avoids any such grouping in the design of transformations.
- However, without hierarchical structure, sophisticated computer programs are required to investigate the differential and linear propagation properties of the primitive.
- In this paper, we formalize this notion of alignment and study four primitives that are exponents of different design strategies.

## Relevance to this program
Recorded for completeness of the local cryptography library. Peripheral to the ECDLP index-calculus program; cite in novelty checks for the tagged areas only.

## Not verified here
Entry generated during the 2026-07-24 bulk seeding pass from the local PDF's first two pages. Title/authors/year/venue were parsed heuristically and may be incomplete or mis-segmented; claims are relayed from the paper's abstract without independent verification. Upgrade to a fully verified entry after a careful read.

## Local copies
- `downloads/12826323 (1).pdf`
- `downloads/12826323.pdf`

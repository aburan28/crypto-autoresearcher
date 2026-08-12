---
id: KN-LIT-5887
type: literature
title: "PRESENT Runs Fast:"
authors:
  - "Secure Implementation in Software"
year: null
venue: null
identifiers:
  eprint: null
  doi: null
  arxiv: null
  url: null
tags: [implementation, side-channel, symmetric]
confidence: reported
citation_verified: read
added: "2026-07-24"
superseded_by: null
---

## Contribution
The PRESENT block cipher was one of the first hardwareoriented proposals for implementation in extremely resource-constrained environments. Its design is based on 4-bit S-boxes and a 64-bit permutation, a far from optimal choice to achieve good performance in software.

## Key claims (as reported)
- As a result, most software implementations require large lookup tables in order to meet efficiency goals.
- In this paper, we describe a new portable and efficient software implementation of PRESENT, fully protected against timing attacks.
- Our implementation uses a novel decomposition of the permutation layer, and bitsliced computation of the S-boxes using optimized Boolean formulas, not requiring lookup tables.
- The implementations are evaluated in embedded ARM CPUs ranging from microcontrollers to full-featured processors equipped with vector instructions.

## Relevance to this program
Recorded for completeness of the local cryptography library. Peripheral to the ECDLP index-calculus program; cite in novelty checks for the tagged areas only.

## Not verified here
Entry generated during the 2026-07-24 bulk seeding pass from the local PDF's first two pages. Title/authors/year/venue were parsed heuristically and may be incomplete or mis-segmented; claims are relayed from the paper's abstract without independent verification. Upgrade to a fully verified entry after a careful read.

## Local copies
- `downloads/10529185 (1).pdf`
- `downloads/10529185.pdf`

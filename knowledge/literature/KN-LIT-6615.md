---
id: KN-LIT-6615
type: literature
title: "Side-Channel Analysis of Multiplications in GF(2128 ) Application to AES-GCM"
authors:
  - "Sonia Belaı̈d"
  - "Pierre-Alain Fouque"
  - "Benoı̂t Gérard"
year: null
venue: null
identifiers:
  eprint: null
  doi: null
  arxiv: null
  url: null
tags: [cryptanalysis, hash, implementation, quantum, side-channel, symmetric]
confidence: reported
citation_verified: read
added: "2026-07-24"
superseded_by: null
---

## Contribution
In this paper, we study the side-channel security of the field multiplication in GF(2n ). We particularly focus on GF(2128 ) multiplication which is the one used in the authentication part of AES-GCM but the proposed attack also applies to other binary extensions.

## Key claims (as reported)
- In a hardware implementation using a 128-bit multiplier, the full 128-bit secret is manipulated at once.
- In this context, classical DPA attacks based on the divide and conquer strategy cannot be applied.
- In this work, the algebraic structure of the multiplication is leveraged to recover bits of information about the secret multiplicand without having to perform any key-guess.
- To do so, the leakage corresponding to the writing of the multiplication output into a register is considered.

## Relevance to this program
Recorded for completeness of the local cryptography library. Peripheral to the ECDLP index-calculus program; cite in novelty checks for the tagged areas only.

## Not verified here
Entry generated during the 2026-07-24 bulk seeding pass from the local PDF's first two pages. Title/authors/year/venue were parsed heuristically and may be incomplete or mis-segmented; claims are relayed from the paper's abstract without independent verification. Upgrade to a fully verified entry after a careful read.

## Local copies
- `downloads/88730275 (1).pdf`
- `downloads/88730275 (2).pdf`
- `downloads/88730275 (3).pdf`
- `downloads/88730275.pdf`

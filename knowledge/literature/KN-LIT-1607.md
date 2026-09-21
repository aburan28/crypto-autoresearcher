---
id: KN-LIT-1607
type: literature
title: "Cryptanalysis of the Subfield Bilinear Collision Problem"
authors:
  - "Pierre Briaud"
  - "Romaric Neveu"
year: 2026
venue: "IACR Cryptology ePrint Archive"
identifiers:
  eprint: "iacr:2026/916"
  doi: null
  arxiv: null
  url: "https://eprint.iacr.org/2026/916"
tags: [cryptanalysis, dlp, finite-field, index-calculus, provable-security, signature]
confidence: reported
citation_verified: read
added: "2026-07-24"
superseded_by: null
---

## Contribution
The Subfield Bilinear Collision (SBC) problem was introduced at Crypto 2024 by Huth and Joux to build an MPC-in-the-Head signature scheme. The problem has later proven to be even more efficient when used within the VOLE-in-the-Head framework (Asiacrypt 2025).

## Key claims (as reported)
- In this note, we improve the original cryptanalysis of SBC in several ways.
- First, we describe a link between the SBC problem and the rank decoding problem, strengthening its theoretical hardness and expanding the range of attacks on the SBC problem.
- Second, we analyze Gröbner basis algorithms to solve the SBC bilinear system and obtain conjectures on the behavior of this system.
- Finally, we describe another algebraic modeling of SBC using the Plücker relations between the maximal minors of a matrix.

## Relevance to this program
Directly relevant to the ECDLP algebraic-attack line (index calculus / summation polynomials / Gröbner methods). Novelty checks for decomposition-based proposals must cite this before claiming new mechanisms.

## Not verified here
Entry generated during the 2026-07-24 bulk seeding pass from the local PDF's first two pages. Title/authors/year/venue were parsed heuristically and may be incomplete or mis-segmented; claims are relayed from the paper's abstract without independent verification. Upgrade to a fully verified entry after a careful read.

## Local copies
- `downloads/2026-916.pdf`

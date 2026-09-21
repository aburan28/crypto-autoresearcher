---
id: KN-LIT-1059
type: literature
title: "A New Linear Distinguisher for Four-Round AES"
authors:
  - "Tomer Ashur"
  - "Erik Takke"
year: 2023
venue: "IACR Cryptology ePrint Archive"
identifiers:
  eprint: "iacr:2023/398"
  doi: null
  arxiv: null
  url: "https://eprint.iacr.org/2023/398"
tags: [cryptanalysis, finite-field, hash, symmetric]
confidence: reported
citation_verified: read
added: "2026-07-24"
superseded_by: null
---

## Contribution
In SAC’14, Biham and Carmeli presented a novel attack on DES, involving a variation of Partitioning Cryptanalysis. This was further extended in ToSC’18 by Biham and Perle into the Conditional Linear Cryptanalysis in the context of Feistel ciphers.

## Key claims (as reported)
- In this work, we formalize this cryptanalytic technique for SubstitutionPermutation Networks and derive several properties.
- A conditional approximation is then used to approximate the inv : GF (28 ) → GF (28 ) : x 7→ x254 function which forms the only source of non-linearity in the AES.
- By extending the approximation to encompass the full AES round function, a linear distinguisher for 4-round AES using 2125.72 known-plaintexts is constructed; the existence of which is often understood to be impossible.
- We furthermore demonstrate how to recover 32 key bits directly from this distinguisher with no data or time overhead.

## Relevance to this program
Recorded for completeness of the local cryptography library. Peripheral to the ECDLP index-calculus program; cite in novelty checks for the tagged areas only.

## Not verified here
Entry generated during the 2026-07-24 bulk seeding pass from the local PDF's first two pages. Title/authors/year/venue were parsed heuristically and may be incomplete or mis-segmented; claims are relayed from the paper's abstract without independent verification. Upgrade to a fully verified entry after a careful read.

## Local copies
- `downloads/2023-398.pdf`

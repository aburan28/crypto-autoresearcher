---
id: KN-LIT-4060
type: literature
title: "GCM, GHASH and Weak Keys"
authors:
  - "Markku-Juhani O. Saarinen"
year: null
venue: null
identifiers:
  eprint: null
  doi: null
  arxiv: null
  url: null
tags: [cryptanalysis, finite-field, protocol, symmetric]
confidence: reported
citation_verified: read
added: "2026-07-24"
superseded_by: null
---

## Contribution
The Galois/Counter Mode (GCM) of operation has been standardized by NIST to provide single-pass authenticated encryption. The GHASH authentication component of GCM belongs to a class of Wegman-Carter polynomial universal hashes that operate in the field GF (2128 ).

## Key claims (as reported)
- GCM uses the same block cipher key K to both encrypt data and to derive the generator H of the authentication polynomial.
- In present literature, only the trivial weak key H = 0 has been considered.
- In this note we show that GHASH has much wider classes of weak keys in its 512 multiplicative subgroups, analyze some of their properties, and give experimental results when GCM is used with the AES algorithm.

## Relevance to this program
Recorded for completeness of the local cryptography library. Peripheral to the ECDLP index-calculus program; cite in novelty checks for the tagged areas only.

## Not verified here
Entry generated during the 2026-07-24 bulk seeding pass from the local PDF's first two pages. Title/authors/year/venue were parsed heuristically and may be incomplete or mis-segmented; claims are relayed from the paper's abstract without independent verification. Upgrade to a fully verified entry after a careful read.

## Local copies
- `downloads/75490220 (1).pdf`
- `downloads/75490220 (2).pdf`
- `downloads/75490220 (3).pdf`
- `downloads/75490220.pdf`

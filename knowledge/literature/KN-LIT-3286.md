---
id: KN-LIT-3286
type: literature
title: "Cryptanalysis of WIDEA"
authors:
  - "Gaëtan Leurent"
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
WIDEA is a family of block ciphers designed by Junod and Macchetti in 2009 as an extension of IDEA to larger block sizes (256 and 512 bits for the main instances WIDEA-4 and WIDEA-8) and larger key sizes (512 and 1024 bits, respectively). WIDEA-w is composed of w parallel copies of the IDEA block cipher, with an MDS matrix to provide diffusion between them.

## Key claims (as reported)
- An important motivation was to use WIDEA to design a hash function.
- In this paper we present low complexity attacks on WIDEA based on truncated differentials.
- We show a distinguisher for the full WIDEA with complexity only 265 , and we use the distinguisher in a key-recovery attack with complexity w · 268 .
- We also show a collision attack on WIDEA-8 if it is used to build a hash function using the Merkle-Damgård mode of operation.

## Relevance to this program
Recorded for completeness of the local cryptography library. Peripheral to the ECDLP index-calculus program; cite in novelty checks for the tagged areas only.

## Not verified here
Entry generated during the 2026-07-24 bulk seeding pass from the local PDF's first two pages. Title/authors/year/venue were parsed heuristically and may be incomplete or mis-segmented; claims are relayed from the paper's abstract without independent verification. Upgrade to a fully verified entry after a careful read.

## Local copies
- `downloads/84240037 (1).pdf`
- `downloads/84240037 (2).pdf`
- `downloads/84240037 (3).pdf`
- `downloads/84240037.pdf`

---
id: KN-LIT-3222
type: literature
title: "Cryptanalysis of ARMADILLO2"
authors:
  - "Marion Videau"
  - "Erik Zenner"
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
ARMADILLO2 is the recommended variant of a multi-purpose cryptographic primitive dedicated to hardware which has been proposed by Badel et al. in [1]. In this paper, we describe a meet-in-themiddle technique relying on the parallel matching algorithm that allows us to invert the ARMADILLO2 function.

## Key claims (as reported)
- This makes it possible to perform a key recovery attack when used as a FIL-MAC.
- A variant of this attack can also be applied to the stream cipher derived from the PRNG mode.
- Finally we propose a (second) preimage attack when used as a hash function.
- We have validated our attacks by implementing cryptanalysis on scaled variants.

## Relevance to this program
Recorded for completeness of the local cryptography library. Peripheral to the ECDLP index-calculus program; cite in novelty checks for the tagged areas only.

## Not verified here
Entry generated during the 2026-07-24 bulk seeding pass from the local PDF's first two pages. Title/authors/year/venue were parsed heuristically and may be incomplete or mis-segmented; claims are relayed from the paper's abstract without independent verification. Upgrade to a fully verified entry after a careful read.

## Local copies
- `downloads/70730305 (1).pdf`
- `downloads/70730305 (2).pdf`
- `downloads/70730305 (3).pdf`
- `downloads/70730305.pdf`

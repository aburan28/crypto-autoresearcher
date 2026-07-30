---
id: KN-LIT-5834
type: literature
title: "Practical Cryptanalysis of ARMADILLO2"
authors: []
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
The ARMADILLO2 primitive is a very innovative hardwareoriented multi-purpose design published at CHES 2010 and based on data-dependent bit transpositions. In this paper, we first show a very unpleasant property of the internal permutation that allows for example to obtain a cheap distinguisher on ARMADILLO2 when instantiated as a stream-cipher.

## Key claims (as reported)
- Then, we exploit the very weak diffusion properties of the internal permutation when the attacker can control the Hamming weight of the input values, leading to a practical free-start collision attack on the ARMADILLO2 compression function.
- Moreover, we describe a new attack so-called local-linearization that seems to be very efficient on datadependent bit transpositions designs and we obtain a practical semifree-start collision attack on the ARMADILLO2 hash function.
- Finally, we provide a related-key recovery attack when ARMADILLO2 is instantiated as a stream cipher.
- All collision attacks have been verified experimentally, they require negligible memory and a very small number of computations (less than one second on an average computer), even for the high security versions of the scheme.

## Relevance to this program
Recorded for completeness of the local cryptography library. Peripheral to the ECDLP index-calculus program; cite in novelty checks for the tagged areas only.

## Not verified here
Entry generated during the 2026-07-24 bulk seeding pass from the local PDF's first two pages. Title/authors/year/venue were parsed heuristically and may be incomplete or mis-segmented; claims are relayed from the paper's abstract without independent verification. Upgrade to a fully verified entry after a careful read.

## Local copies
- `downloads/75490147 (1).pdf`
- `downloads/75490147 (2).pdf`
- `downloads/75490147 (3).pdf`
- `downloads/75490147.pdf`

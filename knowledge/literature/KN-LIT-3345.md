---
id: KN-LIT-3345
type: literature
title: "Cube Testers and Key Recovery Attacks"
authors:
  - "On Reduced-Round MD"
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
CRYPTO 2008 saw the introduction of the hash function MD6 and of cube attacks, a type of algebraic attack applicable to cryptographic functions having a low-degree algebraic normal form over GF(2). This paper applies cube attacks to reduced round MD6, finding the full 128-bit key of a 14-round MD6 with complexity 222 (which takes less than a minute on a single PC).

## Key claims (as reported)
- This is the best key recovery attack announced so far for MD6.
- We then introduce a new class of attacks called cube testers, based on efficient property-testing algorithms, and apply them to MD6 and to the stream cipher Trivium.
- Unlike the standard cube attacks, cube testers detect nonrandom behavior rather than performing key extraction, but they can also attack cryptographic schemes described by nonrandom polynomials of relatively high degree.
- Applied to MD6, cube testers detect nonrandomness over 18 rounds in 217 complexity; applied to a slightly modified version of the MD6 compression function, they can distinguish 66 rounds from random in 224 complexity.

## Relevance to this program
Recorded for completeness of the local cryptography library. Peripheral to the ECDLP index-calculus program; cite in novelty checks for the tagged areas only.

## Not verified here
Entry generated during the 2026-07-24 bulk seeding pass from the local PDF's first two pages. Title/authors/year/venue were parsed heuristically and may be incomplete or mis-segmented; claims are relayed from the paper's abstract without independent verification. Upgrade to a fully verified entry after a careful read.

## Local copies
- `downloads/56650001 (1).pdf`
- `downloads/56650001 (2).pdf`
- `downloads/56650001 (3).pdf`
- `downloads/56650001.pdf`

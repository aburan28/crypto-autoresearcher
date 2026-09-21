---
id: KN-LIT-7102
type: literature
title: "Threshold and Multi-Signature Schemes from Linear Hash Functions"
authors:
  - "Stefano Tessaro"
year: null
venue: null
identifiers:
  eprint: null
  doi: null
  arxiv: null
  url: null
tags: [dlp, factoring, hash, mov-fr, pairing, provable-security, rsa, signature]
confidence: reported
citation_verified: read
added: "2026-07-24"
superseded_by: null
---

## Contribution
This paper gives new constructions of two-round multi-signatures and threshold signatures for which security relies solely on either the hardness of the (plain) discrete logarithm problem or the hardness of RSA, in addition to assuming random oracles. Their signing protocol is partially non-interactive, i.e., the first round of the signing protocol is independent of the message being signed.

## Key claims (as reported)
- We obtain our constructions by generalizing the most efficient discretelogarithm based schemes, MuSig2 (Nick, Ruffing, and Seurin, CRYPTO ’21) and FROST (Komlo and Goldberg, SAC ’20), to work with suitably defined linear hash functions.
- While the original schemes rely on the stronger and more controversial one-more discrete logarithm assumption, we show that suitable instantiations of the hash functions enable security to be based on either the plain discrete logarithm assumption or on RSA.
- The signatures produced by our schemes are equivalent to those obtained from Okamoto’s identification schemes (CRYPTO ’92).
- More abstractly, our results suggest a general framework to transform schemes secure under OMDL into ones secure under the plain DL assumption and, with some restrictions, under RSA.

## Relevance to this program
Relevant to pairing-based reductions and endomorphism speedups (MOV/Frey-Rück special cases, GLV/GLS) that bound which curve classes are safe baselines.

## Not verified here
Entry generated during the 2026-07-24 bulk seeding pass from the local PDF's first two pages. Title/authors/year/venue were parsed heuristically and may be incomplete or mis-segmented; claims are relayed from the paper's abstract without independent verification. Upgrade to a fully verified entry after a careful read.

## Local copies
- `downloads/14004293 (1).pdf`
- `downloads/14004293.pdf`

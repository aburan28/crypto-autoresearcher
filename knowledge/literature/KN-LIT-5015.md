---
id: KN-LIT-5015
type: literature
title: "Multi-property-preserving Hash Domain Extension and the EMD Transform"
authors:
  - "Mihir Bellare"
  - "Thomas Ristenpart"
year: null
venue: null
identifiers:
  eprint: null
  doi: null
  arxiv: null
  url: null
tags: [hash, protocol, provable-security, rsa]
confidence: reported
citation_verified: read
added: "2026-07-24"
superseded_by: null
---

## Contribution
We point out that the seemingly strong pseudorandom oracle preserving (PRO-Pr) property of hash function domain-extension transforms defined and implemented by Coron et. al. [1] can actually weaken our guarantees on the hash function, in particular producing a hash function that fails to be even collision-resistant (CR) even though the compression function to which the transform is applied is CR.

## Key claims (as reported)
- Not only is this true in general, but we show that all the transforms presented in [1] have this weakness.
- We suggest that the appropriate goal of a domain extension transform for the next generation of hash functions is to be multi-property preserving, namely that one should have a single transform that is simultaneously at least collision-resistance preserving, pseudorandom function preserving and PRO-Pr.
- We present an efficient new transform that is proven to be multi-property preserving in this sense.

## Relevance to this program
Recorded for completeness of the local cryptography library. Peripheral to the ECDLP index-calculus program; cite in novelty checks for the tagged areas only.

## Not verified here
Entry generated during the 2026-07-24 bulk seeding pass from the local PDF's first two pages. Title/authors/year/venue were parsed heuristically and may be incomplete or mis-segmented; claims are relayed from the paper's abstract without independent verification. Upgrade to a fully verified entry after a careful read.

## Local copies
- `downloads/42840301 (1).pdf`
- `downloads/42840301 (2).pdf`
- `downloads/42840301 (3).pdf`
- `downloads/42840301.pdf`

---
id: KN-LIT-2825
type: literature
title: "CacheBleed: A Timing Attack on OpenSSL Constant Time RSA"
authors:
  - "Yuval Yarom"
  - "Daniel Genkin"
  - "Nadia Heninger"
year: null
venue: null
identifiers:
  eprint: null
  doi: null
  arxiv: null
  url: null
tags: [cryptanalysis, implementation, pairing, rsa, side-channel, signature]
confidence: reported
citation_verified: read
added: "2026-07-24"
superseded_by: null
---

## Contribution
The scatter-gather technique is a commonly implemented approach to prevent cache-based timing attacks. In this paper we show that scatter-gather is not constant time.

## Key claims (as reported)
- We implement a cache timing attack against the scatter-gather implementation used in the modular exponentiation routine in OpenSSL version 1.0.2f.
- Our attack exploits cache-bank conflicts on the Sandy Bridge microarchitecture.
- We have tested the attack on an Intel Xeon E5-2430 processor.
- For 4096-bit RSA our attack can fully recover the private key after observing 16,000 decryptions.

## Relevance to this program
Relevant to pairing-based reductions and endomorphism speedups (MOV/Frey-Rück special cases, GLV/GLS) that bound which curve classes are safe baselines.

## Not verified here
Entry generated during the 2026-07-24 bulk seeding pass from the local PDF's first two pages. Title/authors/year/venue were parsed heuristically and may be incomplete or mis-segmented; claims are relayed from the paper's abstract without independent verification. Upgrade to a fully verified entry after a careful read.

## Local copies
- `downloads/98130130 (1).pdf`
- `downloads/98130130.pdf`

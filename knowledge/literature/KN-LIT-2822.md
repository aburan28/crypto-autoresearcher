---
id: KN-LIT-2822
type: literature
title: "Cache-Collision Timing Attacks Against AES"
authors:
  - "Joseph Bonneau"
  - "Ilya Mironov"
year: null
venue: null
identifiers:
  eprint: null
  doi: null
  arxiv: null
  url: null
tags: [cryptanalysis, implementation, pairing, side-channel, symmetric]
confidence: reported
citation_verified: read
added: "2026-07-24"
superseded_by: null
---

## Contribution
This paper describes several novel timing attacks against the common table-driven software implementation of the AES cipher. We define a general attack strategy using a simplified model of the cache to predict timing variation due to cache-collisions in the sequence of lookups performed by the encryption.

## Key claims (as reported)
- The attacks presented should be applicable to most high-speed software AES implementations and computing platforms, we have implemented them against OpenSSL v.
- 0.9.8.(a) running on Pentium III, Pentium IV Xeon, and UltraSPARC III+ machines.
- The most powerful attack has been shown under optimal conditions to reliably recover a full 128-bit AES key with 213 timing samples, an improvement of almost four orders of magnitude over the best previously published attacks of this type [Ber05].
- While the task of defending AES against all timing attacks is challenging, a small patch can significantly reduce the vulnerability to these specific attacks with no performance penalty.

## Relevance to this program
Relevant to pairing-based reductions and endomorphism speedups (MOV/Frey-Rück special cases, GLV/GLS) that bound which curve classes are safe baselines.

## Not verified here
Entry generated during the 2026-07-24 bulk seeding pass from the local PDF's first two pages. Title/authors/year/venue were parsed heuristically and may be incomplete or mis-segmented; claims are relayed from the paper's abstract without independent verification. Upgrade to a fully verified entry after a careful read.

## Local copies
- `downloads/16 (1).pdf`
- `downloads/16 (2).pdf`
- `downloads/16 (3).pdf`
- `downloads/16.pdf`

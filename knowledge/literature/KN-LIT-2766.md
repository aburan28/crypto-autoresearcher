---
id: KN-LIT-2766
type: literature
title: "Boosting Merkle-Damgård Hashing for Message Authentication"
authors:
  - "Kan Yasuda"
year: null
venue: null
identifiers:
  eprint: null
  doi: null
  arxiv: null
  url: null
tags: [cryptanalysis, hash, mov-fr, provable-security, symmetric]
confidence: reported
citation_verified: read
added: "2026-07-24"
superseded_by: null
---

## Contribution
This paper presents a novel mode of operation of compression functions, intended for dedicated use as a message authentication code (MAC.) The new approach is faster than the well-known MerkleDamgård iteration; more precisely, it is (1 + c/b)-times as fast as the classical Merkle-Damgård hashing when applied to a compression function h : {0, 1}c+b → {0, 1}c . Our construction provides a single-key MAC with provable security; we show that the proposed scheme yields a PRF(pseudo-random function)-based MAC on the assumption that the underlying compression function h satisfies certain PRF properties.

## Key claims (as reported)
- Thus our method offers a way to process data more efficiently than the conventional HMAC without losing formal proofs of security.
- Our design also takes into account usage with prospective compression functions; that is, those compression functions h with relatively weighty load and relatively large c (i.e., “wide-pipe”) greatly benefit from the improved performance by our mode of operation.

## Relevance to this program
Relevant to pairing-based reductions and endomorphism speedups (MOV/Frey-Rück special cases, GLV/GLS) that bound which curve classes are safe baselines.

## Not verified here
Entry generated during the 2026-07-24 bulk seeding pass from the local PDF's first two pages. Title/authors/year/venue were parsed heuristically and may be incomplete or mis-segmented; claims are relayed from the paper's abstract without independent verification. Upgrade to a fully verified entry after a careful read.

## Local copies
- `downloads/48330214 (1).pdf`
- `downloads/48330214 (2).pdf`
- `downloads/48330214 (3).pdf`
- `downloads/48330214.pdf`

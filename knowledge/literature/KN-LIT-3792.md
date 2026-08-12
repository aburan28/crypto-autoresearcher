---
id: KN-LIT-3792
type: literature
title: "Fast Correlation Attack Revisited Cryptanalysis on Full Grain-128a, Grain-128, and Grain-v1"
authors:
  - "Kazumaro Aoki"
  - "Bin Zhang"
year: null
venue: null
identifiers:
  eprint: null
  doi: null
  arxiv: null
  url: null
tags: [cryptanalysis, finite-field, mov-fr, pairing, symmetric]
confidence: reported
citation_verified: read
added: "2026-07-24"
superseded_by: null
---

## Contribution
A fast correlation attack (FCA) is a well-known cryptanalysis technique for LFSR-based stream ciphers. The correlation between the initial state of an LFSR and corresponding key stream is exploited, and the goal is to recover the initial state of the LFSR.

## Key claims (as reported)
- In this paper, we revisit the FCA from a new point of view based on a finite field, and it brings a new property for the FCA when there are multiple linear approximations.
- Moreover, we propose a novel algorithm based on the new property, which enables us to reduce both time and data complexities.
- We finally apply this technique to the Grain family, which is a well-analyzed class of stream ciphers.
- There are three stream ciphers, Grain-128a, Grain-128, and Grain-v1 in the Grain family, and Grain-v1 is in the eSTREAM portfolio and Grain-128a is standardized by ISO/IEC.

## Relevance to this program
Relevant to pairing-based reductions and endomorphism speedups (MOV/Frey-Rück special cases, GLV/GLS) that bound which curve classes are safe baselines.

## Not verified here
Entry generated during the 2026-07-24 bulk seeding pass from the local PDF's first two pages. Title/authors/year/venue were parsed heuristically and may be incomplete or mis-segmented; claims are relayed from the paper's abstract without independent verification. Upgrade to a fully verified entry after a careful read.

## Local copies
- `downloads/10993232 (1).pdf`
- `downloads/10993232.pdf`

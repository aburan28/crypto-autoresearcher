---
id: KN-LIT-6310
type: literature
title: "Rotational Differential-Linear Distinguishers of ARX Ciphers with Arbitrary Output Linear Masks"
authors:
  - "Zhongfeng Niu"
  - "Siwei Sun"
  - "Yunwen Liu"
  - "Chao Li"
year: null
venue: null
identifiers:
  eprint: null
  doi: null
  arxiv: null
  url: null
tags: [cryptanalysis, hash, implementation, pairing, protocol, side-channel, survey, symmetric]
confidence: reported
citation_verified: read
added: "2026-07-24"
superseded_by: null
---

## Contribution
The rotational differential-linear attacks, proposed at EUROCRYPT 2021, is a generalization of differential-linear attacks by replacing the differential part of the attacks with rotational differentials. At EUROCRYPT 2021, Liu et al. presented a method based on Morawiecki et al.’s technique (FSE 2013) for evaluating the rotational differential-linear correlations for the special cases where the output linear masks are unit vectors.

## Key claims (as reported)
- With this method, some powerful (rotational) differential-linear distinguishers with output linear masks being unit vectors against FRIET, Xoodoo, and Alzette were discovered.
- However, how to compute the rotational differential-linear correlations for arbitrary output masks was left open.
- In this work, we partially solve this open problem by presenting an efficient algorithm for computing the (rotational) differential-linear correlation of modulo additions for arbitrary output linear masks, based on which a technique for evaluating the (rotational) differential-linear correlation of ARX ciphers is derived.
- We apply the technique to Alzette, SipHash, ChaCha, and SPECK.

## Relevance to this program
Relevant to pairing-based reductions and endomorphism speedups (MOV/Frey-Rück special cases, GLV/GLS) that bound which curve classes are safe baselines.

## Not verified here
Entry generated during the 2026-07-24 bulk seeding pass from the local PDF's first two pages. Title/authors/year/venue were parsed heuristically and may be incomplete or mis-segmented; claims are relayed from the paper's abstract without independent verification. Upgrade to a fully verified entry after a careful read.

## Local copies
- `downloads/135070144 (1).pdf`
- `downloads/135070144.pdf`

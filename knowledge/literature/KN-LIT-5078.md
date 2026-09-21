---
id: KN-LIT-5078
type: literature
title: "New algorithms for the Deuring correspondence"
authors:
  - "Towards practical"
  - "secure SQISign signatures"
year: null
venue: null
identifiers:
  eprint: null
  doi: null
  arxiv: null
  url: null
tags: [cryptanalysis, elliptic-curve, isogeny, pairing, pqc, protocol, sidh-csidh, signature, supersingular, survey]
confidence: reported
citation_verified: read
added: "2026-07-24"
superseded_by: null
---

## Contribution
The Deuring correspondence defines a bijection between isogenies of supersingular elliptic curves and ideals of maximal orders in a quaternion algebra. We present a new algorithm to translate ideals of prime-power norm to their corresponding isogenies — a central task of the effective Deuring correspondence.

## Key claims (as reported)
- The new method improves upon the algorithm introduced in 2021 by De Feo, Kohel, Leroux, Petit and Wesolowski as a building-block of the SQISign signature scheme.
- SQISign is the most compact post-quantum signature scheme currently known, but is several orders of magnitude slower than competitors, the main bottleneck of the computation being the ideal-to-isogeny translation.
- We implement the new algorithm and apply it to SQISign, achieving a more than two-fold speedup in key generation and signing with a new choice of parameter.
- Moreover, after adapting the state-of-the-art Fp2 multiplication algorithms by Longa to implement SQISign’s underlying extension field arithmetic and adding various improvements, we push the total speedups to over three times for signing and four times for verification.

## Relevance to this program
Relevant to the isogeny cluster: bears on supersingular/isogeny-based constructions and the isogeny-path problems that compete with and inform ECDLP work. Relevant to pairing-based reductions and endomorphism speedups (MOV/Frey-Rück special cases, GLV/GLS) that bound which curve classes are safe baselines.

## Not verified here
Entry generated during the 2026-07-24 bulk seeding pass from the local PDF's first two pages. Title/authors/year/venue were parsed heuristically and may be incomplete or mis-segmented; claims are relayed from the paper's abstract without independent verification. Upgrade to a fully verified entry after a careful read.

## Local copies
- `downloads/14004105 (1).pdf`
- `downloads/14004105.pdf`

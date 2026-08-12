---
id: KN-LIT-3092
type: literature
title: "Conditional Differential Cryptanalysis of NLFSR-based Cryptosystems"
authors:
  - "Simon Knellwolf⋆"
  - "Willi Meier"
  - "Marı́a Naya-Plasencia⋆⋆"
year: null
venue: null
identifiers:
  eprint: null
  doi: null
  arxiv: null
  url: null
tags: [cryptanalysis, hash, implementation, pairing, symmetric]
confidence: reported
citation_verified: read
added: "2026-07-24"
superseded_by: null
---

## Contribution
Non-linear feedback shift registers are widely used in lightweight cryptographic primitives. For such constructions we propose a general analysis technique based on differential cryptanalysis.

## Key claims (as reported)
- The essential idea is to identify conditions on the internal state to obtain a deterministic differential characteristic for a large number of rounds.
- Depending on whether these conditions involve public variables only, or also key variables, we derive distinguishing and partial key recovery attacks.
- We apply these methods to analyse the security of the eSTREAM finalist Grain v1 as well as the block cipher family KATAN/KTANTAN.
- This allows us to distinguish Grain v1 reduced to 104 of its 160 rounds and to recover some information on the key.

## Relevance to this program
Relevant to pairing-based reductions and endomorphism speedups (MOV/Frey-Rück special cases, GLV/GLS) that bound which curve classes are safe baselines.

## Not verified here
Entry generated during the 2026-07-24 bulk seeding pass from the local PDF's first two pages. Title/authors/year/venue were parsed heuristically and may be incomplete or mis-segmented; claims are relayed from the paper's abstract without independent verification. Upgrade to a fully verified entry after a careful read.

## Local copies
- `downloads/6477130 (1).pdf`
- `downloads/6477130 (2).pdf`
- `downloads/6477130 (3).pdf`
- `downloads/6477130.pdf`

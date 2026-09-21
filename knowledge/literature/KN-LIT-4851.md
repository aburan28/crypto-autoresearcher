---
id: KN-LIT-4851
type: literature
title: "Marlin: Preprocessing zkSNARKs with Universal and Updatable SRS"
authors:
  - "Alessandro Chiesa"
  - "Yuncong Hu"
  - "Mary Maller"
  - "Pratyush Mishra"
year: null
venue: null
identifiers:
  eprint: null
  doi: null
  arxiv: null
  url: null
tags: [lattice, pairing, quantum, survey, zk-proof]
confidence: reported
citation_verified: read
added: "2026-07-24"
superseded_by: null
---

## Contribution
We present a methodology to construct preprocessing zkSNARKs where the structured reference string (SRS) is universal and updatable. This exploits a novel use of holography [Babai et al., STOC 1991], where fast verification is achieved provided the statement being checked is given in encoded form.

## Key claims (as reported)
- We use our methodology to obtain a preprocessing zkSNARK where the SRS has linear size and arguments have constant size.
- Our construction improves on Sonic [Maller et al., CCS 2019], the prior state of the art in this setting, in all efficiency parameters: proving is an order of magnitude faster and verification is thrice as fast, even with smaller SRS size and argument size.
- Our construction is most efficient when instantiated in the algebraic group model (also used by Sonic), but we also demonstrate how to realize it under concrete knowledge assumptions.
- We implement and evaluate our construction.

## Relevance to this program
Relevant to pairing-based reductions and endomorphism speedups (MOV/Frey-Rück special cases, GLV/GLS) that bound which curve classes are safe baselines.

## Not verified here
Entry generated during the 2026-07-24 bulk seeding pass from the local PDF's first two pages. Title/authors/year/venue were parsed heuristically and may be incomplete or mis-segmented; claims are relayed from the paper's abstract without independent verification. Upgrade to a fully verified entry after a careful read.

## Local copies
- `downloads/12105185 (1).pdf`
- `downloads/12105185.pdf`

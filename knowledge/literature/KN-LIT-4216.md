---
id: KN-LIT-4216
type: literature
title: "Higher-Order Masking Schemes for S-Boxes"
authors:
  - "Claude Carlet"
  - "Louis Goubin"
  - "Emmanuel Prouff"
  - "Michael Quisquater"
year: null
venue: null
identifiers:
  eprint: null
  doi: null
  arxiv: null
  url: null
tags: [cryptanalysis, mpc, pairing, side-channel, symmetric]
confidence: reported
citation_verified: read
added: "2026-07-24"
superseded_by: null
---

## Contribution
Masking is a common countermeasure against side-channel attacks. The principle is to randomly split every sensitive intermediate variable occurring in the computation into d + 1 shares, where d is called the masking order and plays the role of a security parameter.

## Key claims (as reported)
- The main issue while applying masking to protect a block cipher implementation is to design an efficient scheme for the s-box computations.
- Actually, masking schemes with arbitrary order only exist for Boolean circuits and for the AES s-box.
- Although any s-box can be represented as a Boolean circuit, applying such a strategy leads to inefficient implementation in software.
- The design of an efficient and generic higher-order masking scheme was hence until now an open problem.

## Relevance to this program
Relevant to pairing-based reductions and endomorphism speedups (MOV/Frey-Rück special cases, GLV/GLS) that bound which curve classes are safe baselines.

## Not verified here
Entry generated during the 2026-07-24 bulk seeding pass from the local PDF's first two pages. Title/authors/year/venue were parsed heuristically and may be incomplete or mis-segmented; claims are relayed from the paper's abstract without independent verification. Upgrade to a fully verified entry after a careful read.

## Local copies
- `downloads/75490370 (1).pdf`
- `downloads/75490370 (2).pdf`
- `downloads/75490370 (3).pdf`
- `downloads/75490370.pdf`

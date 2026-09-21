---
id: KN-LIT-5540
type: literature
title: "On the Power of Fault Sensitivity Analysis and Collision"
authors:
  - "Yang Li"
  - "Kazuo Ohta"
  - "Kazuo Sakiyama"
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
At CHES 2010 two powerful new attacks were presented, namely the Fault Sensitivity Analysis and the Correlation Collision Attack. This paper shows how these ideas can be combined to create even stronger attacks.

## Key claims (as reported)
- Two solutions are presented; both extract leakage information by the fault sensitivity analysis method while each one applies a slightly different collision attack to deduce the secret information without the need of any hypothetical leakage model.
- Having a similar fault injection method, one attack utilizes the non-uniform distribution of faulty ciphertext bytes while the other one exploits the data-dependent timing characteristics of the target combination circuit.
- The results when attacking several AES ASIC cores of the SASEBO LSI chips in different process technologies are presented.
- Successfully breaking the cores protected against DPA attacks using either gate-level countermeasures or logic styles indicates the strength of the attacks.

## Relevance to this program
Relevant to pairing-based reductions and endomorphism speedups (MOV/Frey-Rück special cases, GLV/GLS) that bound which curve classes are safe baselines.

## Not verified here
Entry generated during the 2026-07-24 bulk seeding pass from the local PDF's first two pages. Title/authors/year/venue were parsed heuristically and may be incomplete or mis-segmented; claims are relayed from the paper's abstract without independent verification. Upgrade to a fully verified entry after a careful read.

## Local copies
- `downloads/69170291 (1).pdf`
- `downloads/69170291 (2).pdf`
- `downloads/69170291 (3).pdf`
- `downloads/69170291.pdf`

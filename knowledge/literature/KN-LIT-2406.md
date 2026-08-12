---
id: KN-LIT-2406
type: literature
title: "Algebraic Side-Channel Attacks Beyond the Hamming Weight Leakage Model"
authors:
  - "Yossef Oren"
  - "Mathieu Renauld"
  - "François-Xavier Standaert"
  - "Avishai Wool"
year: null
venue: null
identifiers:
  eprint: null
  doi: null
  arxiv: null
  url: null
tags: [cryptanalysis, pairing, side-channel, symmetric]
confidence: reported
citation_verified: read
added: "2026-07-24"
superseded_by: null
---

## Contribution
Algebraic side-channel attacks (ASCA) are a method of cryptanalysis which allow performing key recoveries with very low data complexity. In an ASCA, the side-channel leaks of a device under test (DUT) are represented as a system of equations, and a machine solver is used to find a key which satisfies these equations.

## Key claims (as reported)
- A primary limitation of the ASCA method is the way it tolerates errors.
- If the correct key is excluded from the system of equations due to noise in the measurements, the attack will fail.
- On the other hand, if the DUT is described in a more robust manner to better tolerate errors, the loss of information may make computation time intractable.
- In this paper, we first show how this robustness-information tradeoff can be simplified by using an optimizer, which exploits the probability data output by a side-channel decoder, instead of a standard SAT solver.

## Relevance to this program
Relevant to pairing-based reductions and endomorphism speedups (MOV/Frey-Rück special cases, GLV/GLS) that bound which curve classes are safe baselines.

## Not verified here
Entry generated during the 2026-07-24 bulk seeding pass from the local PDF's first two pages. Title/authors/year/venue were parsed heuristically and may be incomplete or mis-segmented; claims are relayed from the paper's abstract without independent verification. Upgrade to a fully verified entry after a careful read.

## Local copies
- `downloads/74280138 (1).pdf`
- `downloads/74280138 (2).pdf`
- `downloads/74280138 (3).pdf`
- `downloads/74280138.pdf`

---
id: KN-LIT-4920
type: literature
title: "MILP-Based Automatic Search Algorithms for Differential and Linear Trails for Speck"
authors:
  - "Kai Fu"
  - "Meiqin Wang"
  - "Yinghua Guo"
  - "Siwei Sun"
  - "Lei Hu"
year: null
venue: null
identifiers:
  eprint: null
  doi: null
  arxiv: null
  url: null
tags: [cryptanalysis, pairing, provable-security, symmetric]
confidence: reported
citation_verified: read
added: "2026-07-24"
superseded_by: null
---

## Contribution
In recent years, Mixed Integer Linear Programming (MILP) has been successfully applied in searching for differential characteristics and linear approximations in block ciphers and has produced the significant results for some ciphers such as SIMON (a family of lightweight and hardware-optimized block ciphers designed by NSA) etc. However, in the literature, the MILP-based automatic search algorithm for differential characteristics and linear approximations is still infeasible for block ciphers such as ARX constructions.

## Key claims (as reported)
- In this paper, we propose an MILP-based method for automatic search for differential characteristics and linear approximations in ARX ciphers.
- By researching the properties of differential characteristic and linear approximation of modular addition in ARX ciphers, we present a method to describe the differential characteristic and linear approximation with linear inequalities under the assumptions of independent inputs to the modular addition and independent rounds.
- We use this representation as an input to the publicly available MILP optimizer Gurobi to search for differential characteristics and linear approximations for ARX ciphers.
- As an illustration, we apply our method to Speck, a family of lightweight and software-optimized block ciphers designed by NSA, which results in the improved differential characteristics and linear approximations compared with the existing ones.

## Relevance to this program
Relevant to pairing-based reductions and endomorphism speedups (MOV/Frey-Rück special cases, GLV/GLS) that bound which curve classes are safe baselines.

## Not verified here
Entry generated during the 2026-07-24 bulk seeding pass from the local PDF's first two pages. Title/authors/year/venue were parsed heuristically and may be incomplete or mis-segmented; claims are relayed from the paper's abstract without independent verification. Upgrade to a fully verified entry after a careful read.

## Local copies
- `downloads/97830255 (1).pdf`
- `downloads/97830255.pdf`

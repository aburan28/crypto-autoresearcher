---
id: KN-LIT-385
type: literature
title: "Automatic Security Evaluation and (Related-key) Differential Characteristic Search: Application to SIMON, PRESENT, LBlock"
authors:
  - "Siwei Sun"
  - "Lei Hu"
  - "Peng Wang"
  - "Kexin Qiao"
  - "Xiaoshuang Ma"
year: 2013
venue: "IACR Cryptology ePrint Archive"
identifiers:
  eprint: "iacr:2013/676"
  doi: null
  arxiv: null
  url: "https://eprint.iacr.org/2013/676"
tags: [cryptanalysis, pairing, quantum, symmetric]
confidence: reported
citation_verified: read
added: "2026-07-24"
superseded_by: null
---

## Contribution
We propose two systematic methods to describe the differential property of an S-box with linear inequalities based on logical condition modelling and computational geometry respectively. In one method, inequalities are generated according to some conditional differential properties of the S-box; in the other method, inequalities are extracted from the H-representation of the convex hull of all possible differential patterns of the S-box.

## Key claims (as reported)
- For the second method, we develop a greedy algorithm for selecting a given number of inequalities from the convex hull.
- Using these inequalities combined with Mixed-integer Linear Programming (MILP) technique, we propose an automatic method for evaluating the security of bit-oriented block ciphers against the (related-key) differential attack with several techniques for obtaining tighter security bounds, and a new tool for finding (related-key) differential characteristics automatically for bit-oriented block ciphers.

## Relevance to this program
Relevant to pairing-based reductions and endomorphism speedups (MOV/Frey-Rück special cases, GLV/GLS) that bound which curve classes are safe baselines.

## Not verified here
Entry generated during the 2026-07-24 bulk seeding pass from the local PDF's first two pages. Title/authors/year/venue were parsed heuristically and may be incomplete or mis-segmented; claims are relayed from the paper's abstract without independent verification. Upgrade to a fully verified entry after a careful read.

## Local copies
- `downloads/88730115 (1).pdf`
- `downloads/88730115 (2).pdf`
- `downloads/88730115 (3).pdf`
- `downloads/88730115.pdf`

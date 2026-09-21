---
id: KN-LIT-4666
type: literature
title: "Layout Graphs, Random Walks and the t-wise Independence of SPN Block Ciphers"
authors:
  - "Tianren Liu"
  - "Angelos Pelecanos"
  - "Stefano Tessaro"
year: null
venue: null
identifiers:
  eprint: null
  doi: null
  arxiv: null
  url: null
tags: [cryptanalysis, mov-fr, provable-security, symmetric]
confidence: reported
citation_verified: read
added: "2026-07-24"
superseded_by: null
---

## Contribution
We continue the study of t-wise independence of substitutionpermutation networks (SPNs) initiated by the recent work of Liu, Tessaro, and Vaikuntanathan (CRYPTO 2021). Our key technical result shows that when the S-boxes are randomly and independently chosen and kept secret, an r-round SPN with input length n = b·k is 2−Θ(n) -close to t-wise independent within r = O(min{k, log t}) rounds for any t almost as large as 2b/2 .

## Key claims (as reported)
- Here, b is the input length of the S-box and we assume that the underlying mixing achieves maximum branch number.
- We also analyze the special case of AES parameters (with random S-boxes), and show it is 2−128 -close to pairwise independent in 7 rounds.
- Central to our result is the analysis of a random walk on what we call the layout graph, a combinatorial abstraction that captures equality and inequality constraints among multiple SPN evaluations.
- We use our technical result to show concrete security bounds for SPNs with actual block cipher parameters and small-input S-boxes.

## Relevance to this program
Relevant to pairing-based reductions and endomorphism speedups (MOV/Frey-Rück special cases, GLV/GLS) that bound which curve classes are safe baselines.

## Not verified here
Entry generated during the 2026-07-24 bulk seeding pass from the local PDF's first two pages. Title/authors/year/venue were parsed heuristically and may be incomplete or mis-segmented; claims are relayed from the paper's abstract without independent verification. Upgrade to a fully verified entry after a careful read.

## Local copies
- `downloads/140850418 (1).pdf`
- `downloads/140850418.pdf`

---
id: KN-LIT-1004
type: literature
title: "Mind the TWEAKEY Schedule: Cryptanalysis on SKINNYe-64-256"
authors:
  - "Lingyue Qin"
  - "Xiaoyang Dong"
  - "Anyu Wang"
year: 2022
venue: "IACR Cryptology ePrint Archive"
identifiers:
  eprint: "iacr:2022/789"
  doi: null
  arxiv: null
  url: "https://eprint.iacr.org/2022/789"
tags: [cryptanalysis, fhe, finite-field, implementation, pairing, side-channel, symmetric, zk-proof]
confidence: reported
citation_verified: read
added: "2026-07-24"
superseded_by: null
---

## Contribution
Designing symmetric ciphers for particular applications becomes a hot topic. At EUROCRYPT 2020, Naito, Sasaki and Sugawara invented the threshold implementation friendly cipher SKINNYe-64-256 to meet the requirement of the authenticated encryption PFB_Plus.

## Key claims (as reported)
- Soon, Thomas Peyrin pointed out that SKINNYe-64-256 may lose the security expectation due the new tweakey schedule.
- Although the security issue of SKINNYe-64-256 is still unclear, Naito et al. decided to introduce SKINNYe-64-256 v2 as a response.
- In this paper, we give a formal cryptanalysis on the new tweakey schedule of SKINNYe-64-256 and discover unexpected differential cancellations in the tweakey schedule.
- For example, we find the number of cancellations can be up to 8 within 30 consecutive rounds, which is significantly larger than the expected 3 cancellations.

## Relevance to this program
Relevant to pairing-based reductions and endomorphism speedups (MOV/Frey-Rück special cases, GLV/GLS) that bound which curve classes are safe baselines.

## Not verified here
Entry generated during the 2026-07-24 bulk seeding pass from the local PDF's first two pages. Title/authors/year/venue were parsed heuristically and may be incomplete or mis-segmented; claims are relayed from the paper's abstract without independent verification. Upgrade to a fully verified entry after a careful read.

## Local copies
- `downloads/137910052 (1).pdf`
- `downloads/137910052.pdf`

---
id: KN-LIT-1425
type: literature
title: "New Techniques for Analyzing Differentials with Application to AES"
authors:
  - "Itai Dinur"
year: 2025
venue: "IACR Cryptology ePrint Archive"
identifiers:
  eprint: "iacr:2025/1326"
  doi: null
  arxiv: null
  url: "https://eprint.iacr.org/2025/1326"
tags: [cryptanalysis, provable-security, quantum, symmetric]
confidence: reported
citation_verified: read
added: "2026-07-24"
superseded_by: null
---

## Contribution
We propose new techniques for estimating the probability that an input difference leads to an output difference in a block cipher (i.e., the probability of a differential) under the assumption of independent round-keys. We apply our techniques to AES, and show that the probability of 1 from the every non-trivial differential in 8-round AES is within an additive factor of 2−128 · 50 1 expected value of 2128 −1 .

## Key claims (as reported)
- We further apply our techniques to prove that 40-round AES is at most 2−135 -close to a pairwise independent permutation.
- This improves upon the work of Liu, Tessaro and Vaikuntanathan [CRYPTO 2021], who proved a similar bound for 9000-round AES.
- To obtain our results, we develop and adapt a variety of techniques for analyzing differentials using functional analysis.
- We expect these techniques to be useful for analyzing differentials in additional block ciphers besides the AES.

## Relevance to this program
Recorded for completeness of the local cryptography library. Peripheral to the ECDLP index-calculus program; cite in novelty checks for the tagged areas only.

## Not verified here
Entry generated during the 2026-07-24 bulk seeding pass from the local PDF's first two pages. Title/authors/year/venue were parsed heuristically and may be incomplete or mis-segmented; claims are relayed from the paper's abstract without independent verification. Upgrade to a fully verified entry after a careful read.

## Local copies
- `downloads/2025-1326 (1).pdf`
- `downloads/2025-1326.pdf`

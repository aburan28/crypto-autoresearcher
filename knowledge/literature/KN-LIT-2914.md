---
id: KN-LIT-2914
type: literature
title: "Classical and Quantum Full Plaintext Recovery for Low-Round Feistel-Type Designs"
authors:
  - "Tingting Guo"
  - "Peng Wang(B)"
  - "Jiwu Jing"
  - "Shuping Mao"
year: null
venue: null
identifiers:
  eprint: null
  doi: null
  arxiv: null
  url: null
tags: [cryptanalysis, provable-security, symmetric]
confidence: reported
citation_verified: read
added: "2026-07-24"
superseded_by: null
---

## Contribution
The Feistel (Luby-Rackoff) structure underlies numerous block-cipher and mode-of-operation designs, whose security is traditionally assessed via indistinguishability. For low-round Feistel constructions, a variety of classical and quantum distinguishing attacks are known.

## Key claims (as reported)
- In this work, we show that such distinguishing attacks can be systematically upgraded to full plaintext recovery with essentially the same query complexity.
- We establish classical recovery attacks on the 2-round Feistel under CPA and the 3-round Feistel under CCA using only three queries, and introduce quantum-assisted forward/backward extension techniques based on Simons algorithm that yield recovery attacks on the 3-round Feistel under qCPA and the 4-round Feistel under qCCA.
- We further prove that the attacks extend to the Unified Feistel-Lai-Massey (UFLM) framework and therefore apply to a broad class of two-branch constructions.
- As a consequence, we obtain plaintext-recovery attacks on 4/5/6round Feistel-FK and on several practical enciphering schemes, including AEZ-core, FMix, OleF, double-decker, and docked-double-decker.

## Relevance to this program
Recorded for completeness of the local cryptography library. Peripheral to the ECDLP index-calculus program; cite in novelty checks for the tagged areas only.

## Not verified here
Entry generated during the 2026-07-24 bulk seeding pass from the local PDF's first two pages. Title/authors/year/venue were parsed heuristically and may be incomplete or mis-segmented; claims are relayed from the paper's abstract without independent verification. Upgrade to a fully verified entry after a careful read.

## Local copies
- `downloads/2026-1040 (1).pdf`
- `downloads/2026-1040.pdf`

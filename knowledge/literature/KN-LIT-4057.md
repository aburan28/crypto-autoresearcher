---
id: KN-LIT-4057
type: literature
title: "Gate-Level Masking Under a Path-Based Leakage Metric"
authors:
  - "Andrew J. Leiserson"
  - "Mark E. Marson"
  - "Megan A. Wachs"
year: null
venue: null
identifiers:
  eprint: null
  doi: null
  arxiv: null
  url: null
tags: [implementation, side-channel, symmetric]
confidence: reported
citation_verified: read
added: "2026-07-24"
superseded_by: null
---

## Contribution
Masking is a popular countermeasure against differential power analysis (DPA) and other side-channel attacks. When designing integrated circuits to resist DPA, masking at the logic gate level has the benefit that it can be implemented without consideration of the highlevel function of the circuit.

## Key claims (as reported)
- However, the phenomena of glitches and early propagation reduce the effectiveness of many gate-level masking schemes.
- In this paper we present a new technique for gate-level masking that is free of glitches and early propagation, yet requires only cell-level “don’t touch” constraints.
- Our technique, which we call LUT-Masked Dual-rail with Precharge Logic (LMDPL), can therefore be implemented in a typical FPGA or standard cell ASIC design flow.
- LMDPL does not require routing constraints, nor sequencing of the evaluation of individual gates with enables, registers, or latches.

## Relevance to this program
Recorded for completeness of the local cryptography library. Peripheral to the ECDLP index-calculus program; cite in novelty checks for the tagged areas only.

## Not verified here
Entry generated during the 2026-07-24 bulk seeding pass from the local PDF's first two pages. Title/authors/year/venue were parsed heuristically and may be incomplete or mis-segmented; claims are relayed from the paper's abstract without independent verification. Upgrade to a fully verified entry after a careful read.

## Local copies
- `downloads/87310197 (1).pdf`
- `downloads/87310197 (2).pdf`
- `downloads/87310197 (3).pdf`
- `downloads/87310197.pdf`

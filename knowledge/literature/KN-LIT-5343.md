---
id: KN-LIT-5343
type: literature
title: "On Expected Constant-Round Protocols for Byzantine Agreement"
authors:
  - "Jonathan Katz"
  - "Chiu-Yuen Koo"
year: null
venue: null
identifiers:
  eprint: null
  doi: null
  arxiv: null
  url: null
tags: [signature, survey]
confidence: reported
citation_verified: read
added: "2026-07-24"
superseded_by: null
---

## Contribution
In a seminal paper, Feldman and Micali (STOC ’88) show an n-party Byzantine agreement protocol tolerating t < n/3 malicious parties that runs in expected constant rounds. Here, we show an expected constant-round protocol for authenticated Byzantine agreement assuming honest majority (i.e., t < n/2), and relying only on the existence of a secure signature scheme and a public-key infrastructure (PKI).

## Key claims (as reported)
- Combined with existing results, this gives the first expected constant-round protocol for secure computation with honest majority in a point-to-point network assuming only one-way functions and a PKI.
- Our key technical tool — a new primitive we introduce called moderated VSS — also yields a simpler proof of the Feldman-Micali result.
- We also show a simple technique for sequential composition of protocols without simultaneous termination (something that is inherent for Byzantine agreement protocols using o(n) rounds) for the case of t < n/2.

## Relevance to this program
Recorded for completeness of the local cryptography library. Peripheral to the ECDLP index-calculus program; cite in novelty checks for the tagged areas only.

## Not verified here
Entry generated during the 2026-07-24 bulk seeding pass from the local PDF's first two pages. Title/authors/year/venue were parsed heuristically and may be incomplete or mis-segmented; claims are relayed from the paper's abstract without independent verification. Upgrade to a fully verified entry after a careful read.

## Local copies
- `downloads/41170440 (1).pdf`
- `downloads/41170440 (2).pdf`
- `downloads/41170440 (3).pdf`
- `downloads/41170440.pdf`

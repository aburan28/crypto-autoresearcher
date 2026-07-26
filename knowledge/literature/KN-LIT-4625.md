---
id: KN-LIT-4625
type: literature
title: "Languages with Efficient Zero-Knowledge PCPs are in SZK"
authors:
  - "Mohammad Mahmoody"
  - "David Xiao"
year: null
venue: null
identifiers:
  eprint: null
  doi: null
  arxiv: null
  url: null
tags: [provable-security, quantum, zk-proof]
confidence: reported
citation_verified: read
added: "2026-07-24"
superseded_by: null
---

## Contribution
A Zero-Knowledge PCP (ZK-PCP) is a randomized PCP such that the view of any (perhaps cheating) efficient verifier can be efficiently simulated up to small statistical distance. Kilian, Petrank, and Tardos (STOC ’97) constructed ZK-PCPs for all languages in NEXP.

## Key claims (as reported)
- Ishai, Mahmoody, and Sahai (TCC ’12), motivated by cryptographic applications, revisited the possibility of efficient ZK-PCPs for all of NP where the PCP is encoded as a polynomial-size circuit that given a query i returns the ith symbol of the PCP.
- Ishai et al. showed that there is no efficient ZK-PCP for NP with a non-adaptive verifier, that prepares all of its PCP queries before seeing any answers, unless NP ⊆ coAM and the polynomial-time hierarchy collapses.
- The question of whether adaptive verification can lead to efficient ZK-PCPs for NP remained open.
- In this work, we resolve this question and show that any language or promise problem with efficient ZK-PCPs must be in SZK (the class of promise problems with a statistical zero-knowledge single prover proof system).

## Relevance to this program
Recorded for completeness of the local cryptography library. Peripheral to the ECDLP index-calculus program; cite in novelty checks for the tagged areas only.

## Not verified here
Entry generated during the 2026-07-24 bulk seeding pass from the local PDF's first two pages. Title/authors/year/venue were parsed heuristically and may be incomplete or mis-segmented; claims are relayed from the paper's abstract without independent verification. Upgrade to a fully verified entry after a careful read.

## Local copies
- `downloads/77850295 (1).pdf`
- `downloads/77850295 (2).pdf`
- `downloads/77850295 (3).pdf`
- `downloads/77850295.pdf`

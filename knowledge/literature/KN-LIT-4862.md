---
id: KN-LIT-4862
type: literature
title: "Masking vs. Multiparty Computation: How Large is the Gap for AES?"
authors:
  - "Vincent Grosso"
  - "François-Xavier Standaert"
  - "Sebastian Faust"
year: null
venue: null
identifiers:
  eprint: null
  doi: null
  arxiv: null
  url: null
tags: [extension-field, mpc, pairing, side-channel, survey, symmetric]
confidence: reported
citation_verified: read
added: "2026-07-24"
superseded_by: null
---

## Contribution
In this paper, we evaluate the performances of state-of-theart higher-order masking schemes for the AES. Doing so, we pay a particular attention to the comparison between specialized solutions introduced exclusively as countermeasures against side-channel analysis, and a recent proposal by Roche and Prouff exploiting MultiParty Computation (MPC) techniques.

## Key claims (as reported)
- We show that the additional security features this latter scheme provides (e.g. its glitch-freeness) comes at the cost of large performance overheads.
- We then study how exploiting standard optimization techniques from the MPC literature can be used to reduce this gap.
- In particular, we show that “packed secret sharing” based on a modified multiplication algorithm can speed up MPC-based masking when the order of the masking scheme increases.
- Eventually, we discuss the randomness requirements of masked implementations.

## Relevance to this program
Relevant to pairing-based reductions and endomorphism speedups (MOV/Frey-Rück special cases, GLV/GLS) that bound which curve classes are safe baselines.

## Not verified here
Entry generated during the 2026-07-24 bulk seeding pass from the local PDF's first two pages. Title/authors/year/venue were parsed heuristically and may be incomplete or mis-segmented; claims are relayed from the paper's abstract without independent verification. Upgrade to a fully verified entry after a careful read.

## Local copies
- `downloads/80860155 (1).pdf`
- `downloads/80860155 (2).pdf`
- `downloads/80860155 (3).pdf`
- `downloads/80860155.pdf`

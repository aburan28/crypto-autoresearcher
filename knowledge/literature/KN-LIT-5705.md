---
id: KN-LIT-5705
type: literature
title: "PAC Privacy: Automatic Privacy Measurement and Control of Data Processing"
authors:
  - "Hanshen Xiao"
  - "Srinivas Devadas"
year: null
venue: null
identifiers:
  eprint: null
  doi: null
  arxiv: null
  url: null
tags: [complexity-theory, provable-security, side-channel]
confidence: reported
citation_verified: read
added: "2026-07-24"
superseded_by: null
---

## Contribution
We propose and study a new privacy definition, termed Probably Approximately Correct (PAC) Privacy. PAC Privacy characterizes the information-theoretic hardness to recover sensitive data given arbitrary information disclosure/leakage during/after any processing.

## Key claims (as reported)
- Unlike the classic cryptographic definition and Differential Privacy (DP), which consider the adversarial (input-independent) worst case, PAC Privacy is a simulatable metric that quantifies the instance-based impossibility of inference.
- A fully automatic analysis and proof generation framework is proposed: security parameters can be produced with arbitrarily high confidence via Monte-Carlo simulation for any black-box data processing oracle.
- This appealing automation property enables analysis of complicated data processing, where the worst-case proof in the classic privacy regime could be loose or even intractable.
- Moreover, we show that the produced PAC Privacy guarantees enjoy simple composition bounds and the automatic analysis framework can be implemented in an online fashion to analyze the composite PAC Privacy loss even under correlated randomness.

## Relevance to this program
Recorded for completeness of the local cryptography library. Peripheral to the ECDLP index-calculus program; cite in novelty checks for the tagged areas only.

## Not verified here
Entry generated during the 2026-07-24 bulk seeding pass from the local PDF's first two pages. Title/authors/year/venue were parsed heuristically and may be incomplete or mis-segmented; claims are relayed from the paper's abstract without independent verification. Upgrade to a fully verified entry after a careful read.

## Local copies
- `downloads/140850060 (1).pdf`
- `downloads/140850060.pdf`

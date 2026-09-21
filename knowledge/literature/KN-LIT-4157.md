---
id: KN-LIT-4157
type: literature
title: "Hardness of Non-Interactive Differential Privacy from One-Way Functions"
authors:
  - "Lucas Kowalczyk"
  - "Tal Malkin"
  - "Jonathan Ullman"
  - "Daniel Wichs"
year: null
venue: null
identifiers:
  eprint: null
  doi: null
  arxiv: null
  url: null
tags: [provable-security, survey]
confidence: reported
citation_verified: read
added: "2026-07-24"
superseded_by: null
---

## Contribution
A central challenge in differential privacy is to design computationally efficient non-interactive algorithms that can answer large numbers of statistical queries on a sensitive dataset. That is, we would like to design a differentially private algorithm that takes a dataset D ∈ X n consisting of some small number of elements n from some large data universe X, and efficiently outputs a summary that allows a user to efficiently obtain an answer to any query in some large family Q.

## Key claims (as reported)
- Ignoring computational constraints, this problem can be solved even when X and Q are exponentially large and n is just a small polynomial; however, all algorithms with remotely similar guarantees run in exponential time.
- There have been several results showing that, under the strong assumption of indistinguishability obfuscation, no efficient differentially private algorithm exists when X and Q can be exponentially large.
- However, there are no strong separations between informationtheoretic and computationally efficient differentially private algorithms under any standard complexity assumption.
- In this work we show that, if one-way functions exist, there is no general purpose differentially private algorithm that works when X and Q are exponentially large, and n is an arbitrary polynomial.

## Relevance to this program
Recorded for completeness of the local cryptography library. Peripheral to the ECDLP index-calculus program; cite in novelty checks for the tagged areas only.

## Not verified here
Entry generated during the 2026-07-24 bulk seeding pass from the local PDF's first two pages. Title/authors/year/venue were parsed heuristically and may be incomplete or mis-segmented; claims are relayed from the paper's abstract without independent verification. Upgrade to a fully verified entry after a careful read.

## Local copies
- `downloads/10993262 (1).pdf`
- `downloads/10993262.pdf`

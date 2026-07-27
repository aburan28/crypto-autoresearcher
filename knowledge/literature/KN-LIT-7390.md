---
id: KN-LIT-7390
type: literature
title: "Universal Reductions: Reductions Relative to Stateful Oracles"
authors:
  - "Benjamin Chan"
  - "Cody Freitag"
year: null
venue: null
identifiers:
  eprint: null
  doi: null
  arxiv: null
  url: null
tags: [complexity-theory, pairing, provable-security]
confidence: reported
citation_verified: read
added: "2026-07-24"
superseded_by: null
---

## Contribution
We define a framework for analyzing the security of cryptographic protocols that makes minimal assumptions about what a “realistic model of computation is”. In particular, whereas classical models assume that the attacker is a (perhaps non-uniform) probabilistic polynomial-time algorithm, and more recent definitional approaches also consider quantum polynomial-time algorithms, we consider an approach that is more agnostic to what computational model is physically realizable.

## Key claims (as reported)
- Our notion of universal reductions models attackers as PPT algorithms having access to some arbitrary unbounded stateful Nature that cannot be rewound or restarted when queried multiple times.
- We also consider a more relaxed notion of universal reductions w.r.t. time-evolving, kwindow, Natures that makes restrictions on Nature—roughly speaking, Nature’s behavior may depend on number of messages it has received and the content of the last k(λ)-messages (but not on “older” messages).
- We present both impossibility results and general feasibility results for our notions, indicating to what extent the extended Church-Turing hypotheses are needed for a well-founded theory of Cryptography.

## Relevance to this program
Relevant to pairing-based reductions and endomorphism speedups (MOV/Frey-Rück special cases, GLV/GLS) that bound which curve classes are safe baselines.

## Not verified here
Entry generated during the 2026-07-24 bulk seeding pass from the local PDF's first two pages. Title/authors/year/venue were parsed heuristically and may be incomplete or mis-segmented; claims are relayed from the paper's abstract without independent verification. Upgrade to a fully verified entry after a careful read.

## Local copies
- `downloads/137470109 (1).pdf`
- `downloads/137470109.pdf`

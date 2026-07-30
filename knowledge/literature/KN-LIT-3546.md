---
id: KN-LIT-3546
type: literature
title: "Efficient Constructions of Composable"
authors:
  - "Zero-Knowledge Proofs"
year: null
venue: null
identifiers:
  eprint: null
  doi: null
  arxiv: null
  url: null
tags: [pairing, provable-security, zk-proof]
confidence: reported
citation_verified: read
added: "2026-07-24"
superseded_by: null
---

## Contribution
[7] recently proposed a new framework — termed Generalized Universal Composability (GUC) — for properly analyzing concurrent execution of cryptographic protocols in the presence of a global setup, and constructed the first known GUC-secure implementations of commitment (GUCC) and zero-knowledge (GUC ZK), which suffice to implement any two-party or multi-party functionality under several natural and relatively mild setup assumptions. Unfortunately, the feasibility results of [7] used rather inefficient constructions.

## Key claims (as reported)
- In this paper, we dramatically improve the efficiency of (adaptivelysecure) GUCC and GUC ZK assuming data erasures are allowed.
- Namely, using the same minimal setup assumptions as those used by [7], we build – a direct and efficient constant-round GUC ZK for R from any “dense” Ω-protocol [21] for R.
- As a corollary, we get a semi-efficient construction from any Σ-protocol for R (without doing the Cook-Levin reduction), and a very efficient GUC ZK for proving knowledge of a discrete log representation. – the first constant-rate (and constant-round) GUCC scheme.
- Additionally, we show how to properly model a random oracle in the GUC framework without losing deniability, which is one of the attractive features of the GUC framework.

## Relevance to this program
Relevant to pairing-based reductions and endomorphism speedups (MOV/Frey-Rück special cases, GLV/GLS) that bound which curve classes are safe baselines.

## Not verified here
Entry generated during the 2026-07-24 bulk seeding pass from the local PDF's first two pages. Title/authors/year/venue were parsed heuristically and may be incomplete or mis-segmented; claims are relayed from the paper's abstract without independent verification. Upgrade to a fully verified entry after a careful read.

## Local copies
- `downloads/51570518 (1).pdf`
- `downloads/51570518 (2).pdf`
- `downloads/51570518 (3).pdf`
- `downloads/51570518.pdf`
- `downloads/gucc.pdf`

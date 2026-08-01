---
id: KN-LIT-5944
type: literature
title: "Proof-Carrying Data without Succinct Arguments ?"
authors:
  - "Benedikt Bünz"
year: null
venue: null
identifiers:
  eprint: null
  doi: null
  arxiv: null
  url: null
tags: [dlp, hash, pairing, provable-security, survey, zk-proof]
confidence: reported
citation_verified: read
added: "2026-07-24"
superseded_by: null
---

## Contribution
Proof-carrying data (PCD) is a powerful cryptographic primitive that enables mutually distrustful parties to perform distributed computations that run indefinitely. Known approaches to construct PCD are based on succinct noninteractive arguments of knowledge (SNARKs) that have a succinct verifier or a succinct accumulation scheme.

## Key claims (as reported)
- In this paper we show how to obtain PCD without relying on SNARKs.
- We construct a PCD scheme given any non-interactive argument of knowledge (e.g., with linear-size arguments) that has a split accumulation scheme, which is a weak form of accumulation that we introduce.
- Moreover, we construct a transparent non-interactive argument of knowledge for R1CS whose split accumulation is verifiable via a (small) constant number of group and field operations.
- Our construction is proved secure in the random oracle model based on the hardness of discrete logarithms, and it leads, via the random oracle heuristic and our result above, to concrete efficiency improvements for PCD.

## Relevance to this program
Relevant to pairing-based reductions and endomorphism speedups (MOV/Frey-Rück special cases, GLV/GLS) that bound which curve classes are safe baselines.

## Not verified here
Entry generated during the 2026-07-24 bulk seeding pass from the local PDF's first two pages. Title/authors/year/venue were parsed heuristically and may be incomplete or mis-segmented; claims are relayed from the paper's abstract without independent verification. Upgrade to a fully verified entry after a careful read.

## Local copies
- `downloads/12826020 (1).pdf`
- `downloads/12826020.pdf`

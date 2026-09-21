---
id: KN-LIT-2665
type: literature
title: "Batch Verification for Statistical Zero Knowledge Proofs?"
authors:
  - "Inbar Kaslasi"
  - "Guy N. Rothblum"
  - "Ron D. Rothblum"
  - "Adam Sealfon"
year: null
venue: null
identifiers:
  eprint: null
  doi: null
  arxiv: null
  url: null
tags: [complexity-theory, dlp, lattice, pairing, provable-security, signature, zk-proof]
confidence: reported
citation_verified: read
added: "2026-07-24"
superseded_by: null
---

## Contribution
A statistical zero-knowledge proof (SZK) for a problem Π enables a computationally unbounded prover to convince a polynomialtime verifier that x ∈ Π without revealing any additional information about x to the verifier, in a strong information-theoretic sense. Suppose, however, that the prover wishes to convince the verifier that k separate inputs x1 , . . . , xk all belong to Π (without revealing anything else).

## Key claims (as reported)
- A naive way of doing so is to simply run the SZK protocol separately for each input.
- In this work we ask whether one can do better – that is, is efficient batch verification possible for SZK?
- We give a partial positive answer to this question by constructing a batch verification protocol for a natural and important subclass of SZK – all problems Π that have a non-interactive SZK protocol (in the common random string model).
- More specifically, we show that, for every such problem Π, there exists an honest-verifier SZK protocol for batch verification of k instances, with communication complexity poly(n) + k · poly(log n, log k), where poly refers to a fixed polynomial that depends only on Π (and not on k).

## Relevance to this program
Relevant to pairing-based reductions and endomorphism speedups (MOV/Frey-Rück special cases, GLV/GLS) that bound which curve classes are safe baselines.

## Not verified here
Entry generated during the 2026-07-24 bulk seeding pass from the local PDF's first two pages. Title/authors/year/venue were parsed heuristically and may be incomplete or mis-segmented; claims are relayed from the paper's abstract without independent verification. Upgrade to a fully verified entry after a careful read.

## Local copies
- `downloads/12550147 (1).pdf`
- `downloads/12550147.pdf`

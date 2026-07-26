---
id: KN-LIT-6458
type: literature
title: "Secure Physical Computation using Disposable Circuits"
authors:
  - "Ben A. Fisch"
  - "Daniel Freund"
  - "Moni Naor"
year: null
venue: null
identifiers:
  eprint: null
  doi: null
  arxiv: null
  url: null
tags: [mpc, zk-proof]
confidence: reported
citation_verified: read
added: "2026-07-24"
superseded_by: null
---

## Contribution
In a secure physical computation, a set of parties each have physical inputs and jointly compute a function of their inputs in a way that reveals no information to any party except for the output of the function. Recent work in CRYPTO’14 presented examples of physical zero-knowledge proofs of physical properties, a special case of secure physical two-party computation in which one party has a physical input and the second party verifies a boolean function of that input.

## Key claims (as reported)
- While the work suggested a general framework for modeling and analyzing physical zero-knowledge protocols, it did not provide a general theory of how to prove any physical property with zero-knowledge.
- This paper takes an orthogonal approach using disposable circuits (DC)—cheap hardware tokens that can be completely destroyed after a computation—an extension of the familiar tamper-proof token model.
- In the DC model, we demonstrate that two parties can compute any function of their physical inputs in a way that leaks at most 1 bit of additional information to either party.
- Moreover, our result generalizes to any multi-party physical computation.

## Relevance to this program
Recorded for completeness of the local cryptography library. Peripheral to the ECDLP index-calculus program; cite in novelty checks for the tagged areas only.

## Not verified here
Entry generated during the 2026-07-24 bulk seeding pass from the local PDF's first two pages. Title/authors/year/venue were parsed heuristically and may be incomplete or mis-segmented; claims are relayed from the paper's abstract without independent verification. Upgrade to a fully verified entry after a careful read.

## Local copies
- `downloads/90140183 (1).pdf`
- `downloads/90140183.pdf`

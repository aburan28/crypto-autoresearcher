---
id: KN-LIT-5006
type: literature
title: "Multi-Party Computation of Polynomials and Branching Programs without Simultaneous Interaction"
authors:
  - "S. Dov Gordon⋆"
  - "Tal Malkin ⋆⋆"
  - "Mike Rosulek⋆ ⋆ ⋆"
  - "Hoeteck Wee"
year: null
venue: null
identifiers:
  eprint: null
  doi: null
  arxiv: null
  url: null
tags: [factoring, mpc, rsa]
confidence: reported
citation_verified: read
added: "2026-07-24"
superseded_by: null
---

## Contribution
Halevi, Lindell, and Pinkas (CRYPTO 2011) recently proposed a model for secure computation that captures communication patterns that arise in many practical settings, such as secure computation on the web. In their model, each party interacts only once, with a single centralized server.

## Key claims (as reported)
- Parties do not interact with each other; in fact, the parties need not even be online simultaneously.
- In this work we present a suite of new, simple and efficient protocols for secure computation in this “one-pass” model.
- We give protocols that obtain optimal privacy for the following general tasks: – Evaluating any multivariate polynomial F (x1 , . . . , xn ) (modulo a large RSA modulus N ), where the parties each hold an input xi . – Evaluating any read once branching program over the parties’ inputs.
- As a special case, these function classes include all previous functions for which an optimally private, one-pass computation was known, as well as many new functions, including variance and other statistical functions, string matching, second-price auctions, classification algorithms and some classes of finite automata and decision trees.

## Relevance to this program
Recorded for completeness of the local cryptography library. Peripheral to the ECDLP index-calculus program; cite in novelty checks for the tagged areas only.

## Not verified here
Entry generated during the 2026-07-24 bulk seeding pass from the local PDF's first two pages. Title/authors/year/venue were parsed heuristically and may be incomplete or mis-segmented; claims are relayed from the paper's abstract without independent verification. Upgrade to a fully verified entry after a careful read.

## Local copies
- `downloads/78810572 (1).pdf`
- `downloads/78810572 (2).pdf`
- `downloads/78810572 (3).pdf`
- `downloads/78810572.pdf`

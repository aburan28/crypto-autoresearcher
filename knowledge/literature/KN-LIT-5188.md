---
id: KN-LIT-5188
type: literature
title: "Non-Interactive Proofs for Integer Multiplication"
authors:
  - "Ivan Damgård"
  - "Rune Thorbek"
year: null
venue: null
identifiers:
  eprint: null
  doi: null
  arxiv: null
  url: null
tags: [mov-fr, mpc, provable-security, zk-proof]
confidence: reported
citation_verified: read
added: "2026-07-24"
superseded_by: null
---

## Contribution
We present two universally composable and practical protocols by which a dealer can, verifiably and non-interactively, secret-share an integer among a set of players. Moreover, at small extra cost and using a distributed verifier proof, it can be shown in zero-knowledge that three shared integers a, b, c satisfy ab = c.

## Key claims (as reported)
- This implies by known reductions non-interactive zero-knowledge proofs that a shared integer is in a given interval, or that one secret integer is larger than another.
- Such primitives are useful, e.g., for supplying inputs to a multiparty computation protocol, such as an auction or an election.
- The protocols use various set-up assumptions, but do not require the random oracle model.

## Relevance to this program
Relevant to pairing-based reductions and endomorphism speedups (MOV/Frey-Rück special cases, GLV/GLS) that bound which curve classes are safe baselines.

## Not verified here
Entry generated during the 2026-07-24 bulk seeding pass from the local PDF's first two pages. Title/authors/year/venue were parsed heuristically and may be incomplete or mis-segmented; claims are relayed from the paper's abstract without independent verification. Upgrade to a fully verified entry after a careful read.

## Local copies
- `downloads/45150412 (1).pdf`
- `downloads/45150412 (2).pdf`
- `downloads/45150412 (3).pdf`
- `downloads/45150412.pdf`

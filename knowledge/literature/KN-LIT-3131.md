---
id: KN-LIT-3131
type: literature
title: "Constraint-Hiding Constrained PRFs for NC1 from LWE"
authors:
  - "Ran Canetti"
  - "Yilei Chen"
year: null
venue: null
identifiers:
  eprint: null
  doi: null
  arxiv: null
  url: null
tags: [lattice, mpc, provable-security]
confidence: reported
citation_verified: read
added: "2026-07-24"
superseded_by: null
---

## Contribution
Constraint-hiding constrained PRFs (CHCPRFs), initially studied by Boneh, Lewi and Wu [PKC 2017], are constrained PRFs where the constrained key hides the description of the constraint. Envisioned with powerful applications such as searchable encryption, privatedetectable watermarking and symmetric deniable encryption, the only known candidates of CHCPRFs are based on indistinguishability obfuscation or multilinear maps with strong security properties.

## Key claims (as reported)
- In this paper we construct CHCPRFs for all NC1 circuits from the Learning with Errors assumption.
- The construction draws heavily from the graph-induced multilinear maps by Gentry, Gorbunov and Halevi [TCC 2015], as well as the existing lattice-based PRFs.
- In fact, our construction can be viewed as an instance of the GGH15 approach where security can be reduced to LWE.
- We also show how to build from CHCPRFs reusable garbled circuits (RGC), or equivalently private-key function-hiding functional encryptions with 1-key security.

## Relevance to this program
Recorded for completeness of the local cryptography library. Peripheral to the ECDLP index-calculus program; cite in novelty checks for the tagged areas only.

## Not verified here
Entry generated during the 2026-07-24 bulk seeding pass from the local PDF's first two pages. Title/authors/year/venue were parsed heuristically and may be incomplete or mis-segmented; claims are relayed from the paper's abstract without independent verification. Upgrade to a fully verified entry after a careful read.

## Local copies
- `downloads/10210302 (1).pdf`
- `downloads/10210302.pdf`

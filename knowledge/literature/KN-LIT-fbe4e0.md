---
id: KN-LIT-fbe4e0
type: literature
title: "Two grumpy giants and a baby"
authors:
  - "Daniel J. Bernstein"
  - "Tanja Lange"
year: 2013
venue: "ANTS X, Open Book Series 1:87-111 (2013); ePrint 2012/294"
identifiers:
  eprint: "iacr:2012/294"
  arxiv: null
  doi: "10.2140/obs.2013.1.87"
  url: null
tags: [pollard-rho, bsgs, grumpy-giants, generic-algorithms, ecdlp]
confidence: reported
citation_verified: web
added: "2026-09-26"
superseded_by: null
---

## Contribution

Shows rho is further from optimal than believed, for two reasons. "Higher-degree local anti-collisions" make adding walks less random than the Brent-Pollard heuristic. A truly random walk also suffers global anti-collisions. The paper proposes the two-grumpy-giants-and-a-baby BSGS variant, which beats both.

## Key claims (as reported)

- After (1.5+o(1))sqrt(l) additions (no negation): success probability 0.5625 (BSGS), 0.6753... (truly random walk), 0.71875 (two grumpy giants and a baby).

## Relevance to this program

Two grumpy giants and a baby: better average-case generic DLP than rho/BSGS for a given number of operations (1.25-type constants). This program's cryptanalysis library measures S = 1.18 whole-group (docs/BENCHMARKS.md) — a replication, not a novelty.

## Not verified here

Only the bibliographic record and the abstract or summary page were read, fetched from IACR ePrint, arXiv, Crossref or the publisher on 2026-09-26. The full text was not read, so claims are relayed and not re-derived. Where the summary says "standard statement" or "metadata only", treat the claim as recalled until someone reads the paper.

## Provenance

Created 2026-09-26 from the verified bibliography behind `docs/ecdlp-literature-review-20260926.md`. Every identifier above was seen on a fetched page or index record during that sweep; none is from memory.
Supersedes KN-LIT-7291 (bulk stub or misattributed entry; see that file's `superseded_by`).

---
id: KN-LIT-3811
type: literature
title: "Fast Pseudorandom Functions Based on Expander Graphs?"
authors:
  - "Benny Applebaum"
  - "Pavel Raykov"
year: null
venue: null
identifiers:
  eprint: null
  doi: null
  arxiv: null
  url: null
tags: [complexity-theory, hash, provable-security]
confidence: reported
citation_verified: read
added: "2026-07-24"
superseded_by: null
---

## Contribution
We present direct constructions of pseudorandom function (PRF) families based on Goldreich’s one-way function. Roughly speaking, we assume that non-trivial local mappings f : {0, 1}n → {0, 1}m whose input-output dependencies graph form an expander are hard to invert.

## Key claims (as reported)
- We show that this one-wayness assumption yields PRFs with relatively low complexity.
- This includes weak PRFs which can be computed in linear time of O(n) on a RAM machine with O(log n) word size, or by a depth-3 circuit with unbounded fan-in AND and OR gates (AC0 circuit), and standard PRFs that can be computed by a quasilinear size circuit or by a constant-depth circuit with unbounded fan-in AND, OR and Majority gates (TC0).
- Our proofs are based on a new search-to-decision reduction for expanderbased functions.
- This extends a previous reduction of the first author (STOC 2012) which was applicable for the special case of random local functions.

## Relevance to this program
Recorded for completeness of the local cryptography library. Peripheral to the ECDLP index-calculus program; cite in novelty checks for the tagged areas only.

## Not verified here
Entry generated during the 2026-07-24 bulk seeding pass from the local PDF's first two pages. Title/authors/year/venue were parsed heuristically and may be incomplete or mis-segmented; claims are relayed from the paper's abstract without independent verification. Upgrade to a fully verified entry after a careful read.

## Local copies
- `downloads/99850107 (1).pdf`
- `downloads/99850107.pdf`

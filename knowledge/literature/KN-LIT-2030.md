---
id: KN-LIT-2030
type: literature
title: A Dichotomy for Local Small-Bias Generators
authors:
- Benny Applebaum
- Andrej Bogdanov
- Alon Rosen
year: null
venue: null
identifiers:
  eprint: null
  doi: null
  arxiv: null
  url: null
tags:
- pseudorandom-generator
- small-bias
- complexity-theory
- foundations
confidence: reported
citation_verified: read
added: '2026-07-24'
superseded_by: null
---

## Contribution
We consider pseudorandom generators in which each output bit depends on a constant number of input bits. Such generators have appealingly simple structure: they can be described by a sparse inputoutput dependency graph G and a small predicate P that is applied at each output.

## Key claims (as reported)
- Following the works of Cryan and Miltersen (MFCS ’01) and by Mossel et al (FOCS ’03), we ask: which graphs and predicates yield “small-bias” generators (that fool linear distinguishers)?
- We identify an explicit class of degenerate predicates and prove the following.
- For most graphs, all non-degenerate predicates yield small-bias generators, f : {0, 1}n → {0, 1}m , with output length m = n1+ for some constant  > 0.
- Conversely, we show that for most graphs, degenerate predicates are not secure against linear distinguishers, even when the output length is linear m = n + Ω(n).

## Relevance to this program
Recorded for completeness of the local cryptography library. Peripheral to the ECDLP index-calculus program; cite in novelty checks for the tagged areas only.

## Not verified here
Entry generated during the 2026-07-24 bulk seeding pass from the local PDF's first two pages. Title/authors/year/venue were parsed heuristically and may be incomplete or mis-segmented; claims are relayed from the paper's abstract without independent verification. Upgrade to a fully verified entry after a careful read.

## Local copies
- `downloads/71940191 (1).pdf`
- `downloads/71940191 (2).pdf`
- `downloads/71940191 (3).pdf`
- `downloads/71940191.pdf`

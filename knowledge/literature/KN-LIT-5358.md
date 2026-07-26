---
id: KN-LIT-5358
type: literature
title: "On Instantiating the Algebraic Group Model from Falsifiable Assumptions"
authors:
  - "Thomas Agrikola"
  - "Dennis Hofheinz"
  - "Julia Kastner"
year: null
venue: null
identifiers:
  eprint: null
  doi: null
  arxiv: null
  url: null
tags: [complexity-theory, dlp, provable-security, signature]
confidence: reported
citation_verified: read
added: "2026-07-24"
superseded_by: null
---

## Contribution
We provide a standard-model implementation (of a relaxation) of the algebraic group model (AGM, [Fuchsbauer, Kiltz, Loss, CRYPTO 2018]). Specifically, we show that every algorithm that uses our group is algebraic, and hence “must know” a representation of its output group elements in terms of its input group elements.

## Key claims (as reported)
- Here, “must know” means that a suitable extractor can extract such a representation efficiently.
- We stress that our implementation relies only on falsifiable assumptions in the standard model, and in particular does not use any knowledge assumptions.
- As a consequence, our group allows to transport a number of results obtained in the AGM into the standard model, under falsifiable assumptions.
- For instance, we show that in our group, several Diffie-Hellman-like assumptions (including computational Diffie-Hellman) are equivalent to the discrete logarithm assumption.

## Relevance to this program
Recorded for completeness of the local cryptography library. Peripheral to the ECDLP index-calculus program; cite in novelty checks for the tagged areas only.

## Not verified here
Entry generated during the 2026-07-24 bulk seeding pass from the local PDF's first two pages. Title/authors/year/venue were parsed heuristically and may be incomplete or mis-segmented; claims are relayed from the paper's abstract without independent verification. Upgrade to a fully verified entry after a careful read.

## Local copies
- `downloads/12105281 (1).pdf`
- `downloads/12105281.pdf`

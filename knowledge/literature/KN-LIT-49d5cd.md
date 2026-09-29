---
id: KN-LIT-49d5cd
type: literature
title: "Speeding up Pollard's rho method for computing discrete logarithms"
authors:
  - "Edlyn Teske"
year: 1998
venue: "ANTS-III, pp. 541-554"
identifiers:
  eprint: null
  arxiv: null
  doi: "10.1007/BFb0054891"
  url: null
tags: [pollard-rho, r-adding-walk, random-walk, iteration-function, baseline, ecdlp]
confidence: reported
citation_verified: web
added: "2026-09-26"
superseded_by: null
---

## Contribution

Proposes r-adding walks (x -> x + M_i, i = hash(x) mod r) as rho iteration functions that behave much more like random mappings than Pollard's original 3-way walk; the additive walk is the one used for elliptic curves in practice.

## Key claims (as reported)

- r-adding walks with r around 20 recommended (secondary knowledge; not re-read in this session).

## Relevance to this program

Origin of the r-adding walk used by every modern rho implementation, including this program's GPU/CPU clients. A proposal to 'use additive walks with r table entries' is known; what remains open is the exact constant for a given r on a given group (see Teske 2001, Bos–Dudeanu–Jetchev 2014, and the Bernstein–Lange anti-collision analysis).

## Not verified here

Only the bibliographic record and the abstract or summary page were read, fetched from IACR ePrint, arXiv, Crossref or the publisher on 2026-09-26. The full text was not read, so claims are relayed and not re-derived. Where the summary says "standard statement" or "metadata only", treat the claim as recalled until someone reads the paper.

## Provenance

Created 2026-09-26 from the verified bibliography behind `docs/ecdlp-literature-review-20260926.md`. Every identifier above was seen on a fetched page or index record during that sweep; none is from memory.

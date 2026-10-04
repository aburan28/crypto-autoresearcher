---
id: KN-LIT-c137bd
type: literature
title: "A Variant of the F4 Algorithm"
authors:
  - "Antoine Joux"
  - "Vanessa Vitse"
year: 2011
venue: "LNCS (2011), pp. 356-375; ePrint 2010/158"
identifiers:
  eprint: "iacr:2010/158"
  arxiv: null
  doi: "10.1007/978-3-642-19074-2_23"
  url: null
tags: [index-calculus, f4, groebner, decomposition, implementation, ecdlp]
confidence: reported
citation_verified: web
added: "2026-09-26"
superseded_by: null
---

## Contribution

F4 variant for computing Groebner bases of many polynomial systems with the same shape: a first run records which reductions are useful, and later systems replay it. This avoids all reductions to zero while keeping F4's simplicity (competitive with F5). It is exactly the workload of bulk point decomposition and was a key ingredient of the E(F_{p^5}) relation search.

## Key claims (as reported)

- Avoids all reductions to zero (speed-up figures in paper, not re-extracted).

## Relevance to this program

F4 variant that reuses a traced computation across many similar systems — the 'trace once, replay' idea behind CERTBIN's failed P-GPU premise (EV-CERTBIN-6c3e0a) and the precomputation-solver-reuse suite. Replaying an F4 trace across decomposition targets is known.

## Not verified here

Only the bibliographic record and the abstract or summary page were read, fetched from IACR ePrint, arXiv, Crossref or the publisher on 2026-09-26. The full text was not read, so claims are relayed and not re-derived. Where the summary says "standard statement" or "metadata only", treat the claim as recalled until someone reads the paper.

## Provenance

Created 2026-09-26 from the verified bibliography behind `docs/ecdlp-literature-review-20260926.md`. Every identifier above was seen on a fetched page or index record during that sweep; none is from memory.
Supersedes KN-LIT-275 (bulk stub or misattributed entry; see that file's `superseded_by`).

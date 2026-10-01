---
id: KN-LIT-93696f
type: literature
title: "Speeding Up the Pollard Rho Method on Prime Fields"
authors:
  - "Jung Hee Cheon"
  - "Jin Hong"
  - "Minkyu Kim"
year: 2008
venue: "ASIACRYPT 2008, pp. 471-488"
identifiers:
  eprint: null
  arxiv: null
  doi: "10.1007/978-3-540-89255-7_29"
  url: null
tags: [pollard-rho, tag-tracing, prime-field, iteration-function, table-walk, ecdlp]
confidence: reported
citation_verified: web
added: "2026-09-26"
superseded_by: null
---

## Contribution

"Tag tracing": in multiplicative groups of finite fields most rho steps are done on a cheap partial product (a tag) and the full product is only formed occasionally, cutting the cost per iteration well below one field multiplication. The technique targets F_p^*/F_{p^m}^* rather than elliptic curves, but it is the model for "do less than a full group operation per step" ideas. Related: Kim-Cheon-Hong, subset-restricted random walks on F_{p^m}, PKC 2009, doi:10.1007/978-3-642-00468-1_4; Mukhopadhyay-Sarkar, eprint 2021/043.

Also published as: journal version: Accelerating Pollard's Rho Algorithm on Finite Fields, J. Cryptology 25:195-242, doi:10.1007/s00145-010-9093-7.

## Key claims (as reported)

- Speed-up factors not re-extracted in this session.

## Relevance to this program

Tag tracing: precomputed tables let most rho steps avoid full multiplications (finite-field DLP). The crypto repo's step-table experiments cite it; table-driven walk shortcuts are this line of work.

## Not verified here

Only the bibliographic record and the abstract or summary page were read, fetched from IACR ePrint, arXiv, Crossref or the publisher on 2026-09-26. The full text was not read, so claims are relayed and not re-derived. Where the summary says "standard statement" or "metadata only", treat the claim as recalled until someone reads the paper.

## Provenance

Created 2026-09-26 from the verified bibliography behind `docs/ecdlp-literature-review-20260926.md`. Every identifier above was seen on a fetched page or index record during that sweep; none is from memory.
Supersedes KN-LIT-6767 (bulk stub or misattributed entry; see that file's `superseded_by`).

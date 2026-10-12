---
id: KN-LIT-41fe5c
type: literature
title: "On the Static Diffie-Hellman Problem on Elliptic Curves over Extension Fields"
authors:
  - "Robert Granger"
year: 2010
venue: "ASIACRYPT 2010, LNCS 6477, pp. 283-302; ePrint 2010/177"
identifiers:
  eprint: "iacr:2010/177"
  arxiv: null
  doi: "10.1007/978-3-642-17373-8_17"
  url: null
tags: [index-calculus, static-dh, extension-field, oracle-assisted, ecdlp]
confidence: reported
citation_verified: web
added: "2026-09-26"
superseded_by: null
---

## Contribution

With a static-DH oracle and a decomposition-based index calculus on E(F_{q^n}), any later static-DH instance can be solved heuristically faster than the DLP. The same applies to delayed-target DHP/DLP and one-more DHP/DLP. Shows that for index-calculus-amenable groups these oracle problems are always easier than the DLP.

## Key claims (as reported)

- O(q^{1-1/(n+1)}) oracle queries in a learning phase, then any Static DHP instance in heuristic O~(q^{1-1/(n+1)}) (fixed n > 1, q -> infinity).

## Relevance to this program

Oracle-assisted static Diffie–Hellman over extension fields. Required reading for the ecGFp5 OA-SDH estimate (GOAL-GFPN-380702).

## Not verified here

Only the bibliographic record and the abstract or summary page were read, fetched from IACR ePrint, arXiv, Crossref or the publisher on 2026-09-26. The full text was not read, so claims are relayed and not re-derived. Where the summary says "standard statement" or "metadata only", treat the claim as recalled until someone reads the paper.

## Provenance

Created 2026-09-26 from the verified bibliography behind `docs/ecdlp-literature-review-20260926.md`. Every identifier above was seen on a fetched page or index record during that sweep; none is from memory.
Supersedes KN-LIT-5597 (bulk stub or misattributed entry; see that file's `superseded_by`).

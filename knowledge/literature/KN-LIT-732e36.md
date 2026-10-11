---
id: KN-LIT-732e36
type: literature
title: "Computing Elliptic Curve Discrete Logarithms with Improved Baby-step Giant-step Algorithm"
authors:
  - "Steven D. Galbraith"
  - "Ping Wang"
  - "Fangguo Zhang"
year: 2015
venue: "IACR ePrint 2015/605 (Advances in Mathematics of Communications 2017; journal id not verified here)"
identifiers:
  eprint: "iacr:2015/605"
  arxiv: null
  doi: null
  url: null
tags: [pollard-rho, bsgs, grumpy-giants, interval-dlp, negation-map, ecdlp]
confidence: reported
citation_verified: web
added: "2026-09-26"
superseded_by: null
---

## Contribution

Exploits the fact that computing X+Y in affine coordinates yields X-Y almost for free (same inversion). Combined with negation and Montgomery simultaneous inversion, this speeds up BSGS and gives the average-case analysis of grumpy giants with and without fast inversion. It is the same "cheap second point" idea that RetiredCoder's community SOTA+ kangaroo applies (claimed K about 1.02).

## Key claims (as reported)

- In the fully optimised setting, interleaved BSGS and grumpy-giants have better average-case running time than rho; for interval DLP, interleaved BSGS is "considerably faster" than kangaroo or Gaudry-Schost (memory permitting).

## Relevance to this program

Uses the nearly free X−Y alongside X+Y (shared inversion) to speed BSGS/grumpy-giants and interval search. The community 'SOTA+' kangaroo trick is this idea; a proposal to 'compute P−Q for free with P+Q' is known.

## Not verified here

Only the bibliographic record and the abstract or summary page were read, fetched from IACR ePrint, arXiv, Crossref or the publisher on 2026-09-26. The full text was not read, so claims are relayed and not re-derived. Where the summary says "standard statement" or "metadata only", treat the claim as recalled until someone reads the paper.

## Provenance

Created 2026-09-26 from the verified bibliography behind `docs/ecdlp-literature-review-20260926.md`. Every identifier above was seen on a fetched page or index record during that sweep; none is from memory.

---
id: KN-LIT-92b022
type: literature
title: "A SAT-Based Approach for Index Calculus on Binary Elliptic Curves"
authors:
  - "Monika Trimoska"
  - "Sorina Ionica"
  - "Gilles Dequen"
year: 2020
venue: "AFRICACRYPT 2020, pp. 214-235; ePrint 2019/313"
identifiers:
  eprint: "iacr:2019/313"
  arxiv: null
  doi: "10.1007/978-3-030-51938-4_11"
  url: null
tags: [index-calculus, sat, binary-field, point-decomposition, cryptominisat, xor, ecdlp]
confidence: reported
citation_verified: web
added: "2026-09-26"
superseded_by: null
---

## Contribution

Solves the point-decomposition step for prime-degree F_{2^n} with the dedicated XOR-aware SAT solver WDSat, adding a symmetry-breaking technique that removes an m! factor for S_{m+1}. Asymptotically exponential in the factor-base dimension l, but much faster than Groebner bases in practice.

## Key claims (as reported)

- Up to 300x faster than Magma's F4 on the PDP for the (l, n) tested, with the gap growing in l and n; m! symmetry-breaking gain for S_{m+1}.

## Relevance to this program

SAT-based PDP for binary curves (AFRICACRYPT 2020; up to 300× faster than Magma F4 on the PDP step). With WDSat (KN-LIT-102cdb) the SAT baseline for EV-ICPERF-390707 (branching-order confound) and the pdp-scaling slopes. Frozen inputs: inputs/SATIC-TRIMOSKA-2019.

## Not verified here

Only the bibliographic record and the abstract or summary page were read, fetched from IACR ePrint, arXiv, Crossref or the publisher on 2026-09-26. The full text was not read, so claims are relayed and not re-derived. Where the summary says "standard statement" or "metadata only", treat the claim as recalled until someone reads the paper.

## Provenance

Created 2026-09-26 from the verified bibliography behind `docs/ecdlp-literature-review-20260926.md`. Every identifier above was seen on a fetched page or index record during that sweep; none is from memory.

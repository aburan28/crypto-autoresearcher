---
id: KN-LIT-7cc07f
type: literature
title: "Computing Small Discrete Logarithms Faster"
authors:
  - "Daniel J. Bernstein"
  - "Tanja Lange"
year: 2012
venue: "INDOCRYPT 2012, LNCS 7668, pp. 317-338; ePrint 2012/458"
identifiers:
  eprint: "iacr:2012/458"
  arxiv: null
  doi: "10.1007/978-3-642-34931-7_19"
  url: null
tags: [pollard-rho, precomputation, distinguished-points, multi-target, small-dlp, ecdlp]
confidence: reported
citation_verified: web
added: "2026-09-26"
superseded_by: null
---

## Contribution

Rho/kangaroo with a group-specific precomputed table of distinguished points: online cost drops to about l^{1/3} for a table of size l^{1/3} built with about l^{2/3} work. Directly applicable to repeated ECDLPs on a fixed curve and to decryption in EC-ElGamal-style additively homomorphic schemes.

## Key claims (as reported)

- Interval of order l: 1.93*l^{1/3} multiplications online with table size l^{1/3} (precomputation 1.21*l^{2/3}); whole group of order l: 1.77*l^{1/3} (precomputation 1.24*l^{2/3}).

## Relevance to this program

Precomputed distinguished-point tables: online ~1.77·l^{1/3} after ~1.2·l^{2/3} precomputation with a table of l^{1/3} DPs; table selection by walk usefulness. The basin-size/oracle-ceiling analysis of H-ECDLP-3550b8 (EV-ECDLP-31e91c/60e266/f6b3f5) is measured against this paper's Table 4.1 and rule.

## Not verified here

Only the bibliographic record and the abstract or summary page were read, fetched from IACR ePrint, arXiv, Crossref or the publisher on 2026-09-26. The full text was not read, so claims are relayed and not re-derived. Where the summary says "standard statement" or "metadata only", treat the claim as recalled until someone reads the paper.

## Provenance

Created 2026-09-26 from the verified bibliography behind `docs/ecdlp-literature-review-20260926.md`. Every identifier above was seen on a fetched page or index record during that sweep; none is from memory.
Supersedes KN-LIT-3060 (bulk stub or misattributed entry; see that file's `superseded_by`).

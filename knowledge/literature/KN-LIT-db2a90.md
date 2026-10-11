---
id: KN-LIT-db2a90
type: literature
title: "Speeding up the Discrete Log Computation on Curves with Automorphisms"
authors:
  - "I. Duursma"
  - "P. Gaudry"
  - "F. Morain"
year: 1999
venue: "ASIACRYPT 1999, pp. 103-121"
identifiers:
  eprint: null
  arxiv: null
  doi: "10.1007/978-3-540-48000-6_10"
  url: null
tags: [pollard-rho, automorphism, equivalence-classes, negation-map, cm-curves, ecdlp]
confidence: reported
citation_verified: web
added: "2026-09-26"
superseded_by: null
---

## Contribution

General framework: if a group automorphism of order m is cheap to evaluate, rho can walk on orbits and gain sqrt(m). Covers hyperelliptic curves and elliptic curves with extra automorphisms; for j-invariant 0 curves such as secp256k1 or BN curves the order-6 automorphism group gives sqrt(6).

## Key claims (as reported)

- sqrt(m) speed-up for an automorphism group of order m (e.g. sqrt(6) for j=0 curves; measured 0.790*sqrt(6) on BN254 by Bos-Costello-Miele 2014).

## Relevance to this program

General √m speed-up from an automorphism group of order m (j = 0, 1728 curves; Koblitz curves). Any 'use the endomorphism to shrink the rho search space' proposal is this paper plus GLV/Wiener–Zuccherato; the gain is a constant √m, never an exponent change.

## Not verified here

Only the bibliographic record and the abstract or summary page were read, fetched from IACR ePrint, arXiv, Crossref or the publisher on 2026-09-26. The full text was not read, so claims are relayed and not re-derived. Where the summary says "standard statement" or "metadata only", treat the claim as recalled until someone reads the paper.

## Provenance

Created 2026-09-26 from the verified bibliography behind `docs/ecdlp-literature-review-20260926.md`. Every identifier above was seen on a fetched page or index record during that sweep; none is from memory.

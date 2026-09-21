---
id: KN-LIT-047
type: literature
title: Lattice basis reduction - Improved practical algorithms and solving subset sum problems (BKZ)
authors: [Schnorr Claus-Peter, Euchner M.]
year: 1994
venue: Mathematical Programming, 66(2):181-199
identifiers:
  eprint: null
  doi: 10.1007/BF01581144
  url: https://link.springer.com/article/10.1007/BF01581144
tags: [lattice-reduction, bkz, enumeration, korkine-zolotarev, block-size, security-estimate, cryptanalysis]
confidence: established
citation_verified: web
added: 2026-07-23
superseded_by: null
---

## Contribution
Introduces the block Korkine-Zolotarev (BKZ) reduction algorithm and the
Schnorr-Euchner enumeration for short/closest vectors. BKZ gives a tunable
time/quality tradeoff parameterized by block size beta, interpolating between LLL
(beta = 2, KN-LIT-046) and full HKZ reduction (beta = full dimension).

## Key claims (as reported)
- Stronger reduction than LLL at higher cost, controlled by beta; the practical
  workhorse for lattice cryptanalysis.
- Concrete-estimate refinements: Chen-Nguyen, "BKZ 2.0: Better Lattice Security
  Estimates," ASIACRYPT 2011, LNCS 7073:1-20 (doi:10.1007/978-3-642-25385-0_1) --
  pruned enumeration, preprocessing, and a simulator predicting output quality.
  Prediction model: Gama-Nguyen, "Predicting Lattice Reduction," EUROCRYPT 2008,
  LNCS 4965:31-51 (doi:10.1007/978-3-540-78967-3_3) -- the root-Hermite-factor
  delta as the quality predictor.

## Relevance to this program
BKZ (and its cost model via block size / root Hermite factor) is the reduction
used to turn a lattice attack into a concrete feasibility/cost call -- for both
lattice-crypto security estimates AND the (EC)DSA/HNP and Coppersmith attacks the
corpus records (KN-TECH-019, KN-TECH-020). The delta predictor decides whether a
given nonce-leakage instance is breakable.

## Not verified here
Full paper not read; BKZ is textbook-level in lattice cryptanalysis (hence
confidence: established). Euchner's given name is rendered only as initial "M."
in the sources (not expanded, to avoid fabrication). Fields (incl. BKZ 2.0,
Gama-Nguyen) confirmed against Springer/IACR records via search, not by fetching
the primary pages.

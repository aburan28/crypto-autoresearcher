---
id: KN-LIT-084
type: literature
title: Reducing elliptic curve logarithms to logarithms in a finite field
authors: [Menezes Alfred J., Okamoto Tatsuaki, Vanstone Scott A.]
year: 1993
venue: IEEE Transactions on Information Theory, 39(5):1639-1646
identifiers:
  eprint: null
  doi: 10.1109/18.259647
  url: https://doi.org/10.1109/18.259647
tags: [mov, pairing, weil-pairing, embedding-degree, supersingular, transfer, subexponential, special-curves, ecdlp, hygiene]
confidence: established
citation_verified: web
added: 2026-07-24
superseded_by: null
---

## Contribution
The MOV attack: uses the Weil pairing to embed a prime-order subgroup of
E(F_q) into the multiplicative group of an extension field F_{q^k}, where k is
the embedding degree (the least k with l | q^k - 1). The ECDLP is thereby
transferred to a finite-field DLP, where index calculus is subexponential. For
supersingular curves the reduction is probabilistic polynomial time, because
k <= 6 always.

## Key claims (as reported)
- The elliptic curve logarithm problem reduces to the logarithm problem in
  F_{q^k}^* via the Weil pairing (proven).
- For supersingular elliptic curves the embedding degree satisfies k <= 6, so
  the reduction runs in probabilistic polynomial time and yields a
  subexponential ECDLP algorithm for that class.
- Consequently supersingular curves, and more generally any curve of small
  embedding degree, must be excluded when choosing ECC parameters.

## Relevance to this program
MOV is the canonical example of a *structure transfer*: it does not beat rho
generically, it identifies a curve class where the problem is not generic at
all. Two consequences for this program. (1) Novelty screening: any proposal to
"map the ECDLP into a field DLP" is `known` unless it works at large embedding
degree, which is the generic case (KN-LIT-086). (2) Scope discipline: an
advantage measured on a small-embedding-degree curve says nothing about
ordinary large-prime-order E(F_p), which is the program's declared target. The
companion transfer via the Tate pairing is KN-LIT-085; the genericity bound is
KN-LIT-086; the synthesis is KN-TECH-032.

## Not verified here
Full paper not fetched. Authors, title, venue (IEEE Trans. Inform. Theory
39(5):1639-1646, September 1993) and DOI were confirmed against IEEE Xplore and
the publisher DOI record, and the claims above are taken from the published
abstract. The k <= 6 bound for supersingular curves is textbook standard
(hence confidence: established) but the proof was not re-derived here.

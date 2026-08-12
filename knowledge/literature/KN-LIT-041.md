---
id: KN-LIT-041
type: literature
title: Faster Point Multiplication on Elliptic Curves with Efficient Endomorphisms (GLV)
authors: [Gallant Robert P., Lambert Robert J., Vanstone Scott A.]
year: 2001
venue: CRYPTO 2001, LNCS 2139, pp. 190-200
identifiers:
  eprint: null
  doi: 10.1007/3-540-44647-8_11
  url: https://doi.org/10.1007/3-540-44647-8_11
tags: [glv, gls, endomorphism, scalar-multiplication, equivalence-class, rho-speedup, baseline]
confidence: established
citation_verified: web
added: 2026-07-22
superseded_by: null
---

## Contribution
The GLV method: on curves with an efficiently computable endomorphism phi of
known eigenvalue lambda, decompose a scalar k = k1 + k2*lambda (mod n) with
k1,k2 about half-length, and compute kP = k1*P + k2*phi(P) as a multi-
exponentiation -- roughly halving the doublings.

## Key claims (as reported)
- ~2x faster scalar multiplication on curves admitting a fast endomorphism
  (conditional on the curve having one and a short decomposition).
- Broadened to a large curve class over F_{p^2}: Galbraith-Lin-Scott (GLS),
  EUROCRYPT 2009, LNCS 5479:518-535 (doi:10.1007/978-3-642-01001-9_30,
  iacr:2008/194; J. Cryptology 24(3):446-469, 2011,
  doi:10.1007/s00145-010-9065-y), using a Frobenius-derived endomorphism so
  small-discriminant CM is not required.

## Relevance to this program
The endomorphism phi induces equivalence classes (orbits under phi) on the
curve; the SAME map underlies faster equivalence-class Pollard rho, contributing
a sqrt(|<phi>|) factor to the automorphism-adjusted rho constant that the program
charges its baseline against (KN-TECH-006, KN-TECH-018). GLS matters because it
shows such exploitable endomorphisms exist for a LARGE class of curves, not just
special CM curves -- so the automorphism discount applies broadly. (These are
scalar-multiplication / structure results, NOT ECDLP attacks.)

## Not verified here
Full paper not read; the GLV decomposition is textbook-level in ECC (hence
confidence: established). Fields (incl. GLS conference + journal) confirmed
against Springer/IACR DOI records via search, not by fetching the primary pages.

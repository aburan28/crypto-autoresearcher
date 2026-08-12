---
id: KN-LIT-386
type: literature
title: "Classification of Elliptic/Hyperelliptic Curves with Weak Coverings against the GHS Attack under an Isogeny Condition"
authors:
  - "Tsutomu Iijima ∗"
year: 2013
venue: "IACR Cryptology ePrint Archive"
identifiers:
  eprint: "iacr:2013/487"
  doi: null
  arxiv: null
  url: "https://eprint.iacr.org/2013/487"
tags: [dlp, elliptic-curve, finite-field, hyperelliptic, index-calculus, isogeny, jacobian, number-theory, weil-descent]
confidence: reported
citation_verified: read
added: "2026-07-24"
superseded_by: null
---

## Contribution
The GHS attack is known to map the discrete logarithm problem(DLP) in the Jacobian of a curve C0 defined over the d degree extension kd of a finite field k to the DLP in the Jacobian of a new curve C over k which is a covering curve of C0 , then solve the DLP of curves C/k by variations of index calculus algorithms. It is therefore important to know which curve C0 /kd is subjected to the GHS attack, especially those whose covering C/k have the smallest genus g(C) = dg(C0 ), which we called satisfying the isogeny condition.

## Key claims (as reported)
- Until now, 4 classes of such curves were found by Thériault in [35] and 6 classes by Diem in [3][5].
- In this paper, we present a classification i.e. a complete list of all elliptic curves and hyperelliptic curves C0 /kd of genus 2, 3 which possess (2, ..., 2) covering C/k of P1 under the isogeny condition (i.e. g(C) = d · g(C0 )) in odd characteristic case.
- In particular, classification of the Galois representation of Gal(kd /k) acting on the covering group cov(C/P1 ) is used together with analysis of ramification points of these coverings.
- Besides, a general existential condition of a model of C over k is also obtained.

## Relevance to this program
Directly relevant to the ECDLP algebraic-attack line (index calculus / summation polynomials / Gröbner methods). Novelty checks for decomposition-based proposals must cite this before claiming new mechanisms. Relevant to the isogeny cluster: bears on supersingular/isogeny-based constructions and the isogeny-path problems that compete with and inform ECDLP work.

## Not verified here
Entry generated during the 2026-07-24 bulk seeding pass from the local PDF's first two pages. Title/authors/year/venue were parsed heuristically and may be incomplete or mis-segmented; claims are relayed from the paper's abstract without independent verification. Upgrade to a fully verified entry after a careful read.

## Local copies
- `downloads/2013-487.pdf`

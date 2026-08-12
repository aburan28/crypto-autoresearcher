---
id: KN-LIT-449
type: literature
title: "A classification of elliptic curves with respect to the GHS attack in odd characteristic"
authors:
  - "Tsutomu Iijima ∗"
year: 2015
venue: "IACR Cryptology ePrint Archive"
identifiers:
  eprint: "iacr:2015/805"
  doi: null
  arxiv: null
  url: "https://eprint.iacr.org/2015/805"
tags: [binary-field, complexity-theory, dlp, ecdlp, elliptic-curve, glv-gls, hyperelliptic, index-calculus, isogeny, jacobian, number-theory, pollard-rho, semaev, summation-polynomial, weil-descent]
confidence: reported
citation_verified: read
added: "2026-07-24"
superseded_by: null
---

## Contribution
The GHS attack is known to solve discrete logarithm problems (DLP) in the Jacobian of a curve C0 defined over the d degree extension field kd of k := Fq by mapping it to the DLP in the Jacobian of a covering curve C of C0 over k. Recently, classifications for all elliptic curves and hyperelliptic curves C0 /kd of genus 2,3 which possess (2, ..., 2)-covering C/k of P1 were shown under an isogeny condition (i.e. when g(C) = d · g(C0 )).

## Key claims (as reported)
- This paper presents a systematic classification procedure for hyperelliptic curves in the odd characteristic case.
- In particular, we show a complete classification of elliptic curves C0 over kd which have (2, ..., 2)-covering C/k of P1 for d = 2, 3, 5, 7.
- It has been reported by Diem[6] that the GHS attack fails for elliptic curves C0 over odd characteristic definition field kd with prime extension degree d greater than or equal to 11 since g(C) become very large.
- Therefore, for elliptic curves over kd with prime extension degree d, it is sufficient to analyze cases of d = 2, 3, 5, 7.

## Relevance to this program
Directly relevant to the ECDLP algebraic-attack line (index calculus / summation polynomials / Gröbner methods). Novelty checks for decomposition-based proposals must cite this before claiming new mechanisms. Relevant to the isogeny cluster: bears on supersingular/isogeny-based constructions and the isogeny-path problems that compete with and inform ECDLP work. Relevant to pairing-based reductions and endomorphism speedups (MOV/Frey-Rück special cases, GLV/GLS) that bound which curve classes are safe baselines. Bears on the generic baseline (Pollard rho / generic-group lower bounds) against which every candidate algorithm in this program is benchmarked.

## Not verified here
Entry generated during the 2026-07-24 bulk seeding pass from the local PDF's first two pages. Title/authors/year/venue were parsed heuristically and may be incomplete or mis-segmented; claims are relayed from the paper's abstract without independent verification. Upgrade to a fully verified entry after a careful read.

## Local copies
- `downloads/2015-805.pdf`

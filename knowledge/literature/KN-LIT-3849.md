---
id: KN-LIT-3849
type: literature
title: "Faster Scalar Multiplication on Koblitz Curves combining Point Halving with the Frobenius Endomorphism"
authors:
  - "Roberto Maria Avanzi ⋆"
  - "Mathieu Ciet ⋆"
  - "Francesco Sica ⋆"
year: null
venue: null
identifiers:
  eprint: null
  doi: null
  arxiv: null
  url: null
tags: [binary-field, curve-arithmetic, dlp, elliptic-curve, endomorphism, finite-field]
confidence: reported
citation_verified: read
added: "2026-07-24"
superseded_by: null
---

## Contribution
Let E be an elliptic curve defined over F2n . The inverse operation of point doubling, called point halving, can be done up to three times as fast as doubling.

## Key claims (as reported)
- Some authors have therefore proposed to perform a scalar multiplication by an “halve-and-add” algorithm, which is faster than the classical double-and-add method.
- If the coefficients of the equation defining the curve lie in a small subfield of F2n , one can use the Frobenius endomorphism τ of the field extension to replace doublings.
- Since the cost of τ is negligible if normal bases are used, the scalar multiplication is written in “base τ ” and the resulting “τ -and-add” algorithm gives very good performance.
- For elliptic Koblitz curves, this work combines the two ideas for the first time to achieve a novel decomposition of the scalar.

## Relevance to this program
Relevant to pairing-based reductions and endomorphism speedups (MOV/Frey-Rück special cases, GLV/GLS) that bound which curve classes are safe baselines.

## Not verified here
Entry generated during the 2026-07-24 bulk seeding pass from the local PDF's first two pages. Title/authors/year/venue were parsed heuristically and may be incomplete or mis-segmented; claims are relayed from the paper's abstract without independent verification. Upgrade to a fully verified entry after a careful read.

## Local copies
- `downloads/29470028 (1).pdf`
- `downloads/29470028 (2).pdf`
- `downloads/29470028.pdf`

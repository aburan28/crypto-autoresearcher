---
id: KN-LIT-4380
type: literature
title: "Improved Algorithms for Efficient Arithmetic on Elliptic Curves Using Fast Endomorphisms"
authors:
  - "Mathieu Ciet"
  - "Tanja Lange"
  - "Francesco Sica"
year: null
venue: null
identifiers:
  eprint: null
  doi: null
  arxiv: null
  url: null
tags: [binary-field, curve-arithmetic, elliptic-curve, endomorphism, finite-field, glv-gls, prime-field, quantum]
confidence: reported
citation_verified: read
added: "2026-07-24"
superseded_by: null
---

## Contribution
In most algorithms involving elliptic curves, the most expensive part consists in computing multiples of points. This paper investigates how to extend the τ -adic expansion from Koblitz curves to a larger class of curves defined over a prime field having an efficiently-computable endomorphism φ in order to perform an efficient point multiplication with efficiency similar to Solinas’ approach presented at CRYPTO ’97.

## Key claims (as reported)
- Furthermore, many elliptic curve cryptosystems require the computation of k0 P +k1 Q.
- Following the work of Solinas on the Joint Sparse Form, we introduce the notion of φ-Joint Sparse Form which combines the advantages of a φ-expansion with the additional speedup of the Joint Sparse Form.
- We also present an efficient algorithm to obtain the φ-Joint Sparse Form.
- Then, the double exponentiation can be done using the φ endomorphism instead of doubling, resulting in an average of l applications of φ and l/2 additions, where l is the size of the ki ’s.

## Relevance to this program
Relevant to pairing-based reductions and endomorphism speedups (MOV/Frey-Rück special cases, GLV/GLS) that bound which curve classes are safe baselines.

## Not verified here
Entry generated during the 2026-07-24 bulk seeding pass from the local PDF's first two pages. Title/authors/year/venue were parsed heuristically and may be incomplete or mis-segmented; claims are relayed from the paper's abstract without independent verification. Upgrade to a fully verified entry after a careful read.

## Local copies
- `downloads/26560388 (1).pdf`
- `downloads/26560388 (2).pdf`
- `downloads/26560388.pdf`

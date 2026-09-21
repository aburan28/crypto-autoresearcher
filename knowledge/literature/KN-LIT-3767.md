---
id: KN-LIT-3767
type: literature
title: "Factoring pq 2 with Quadratic Forms: Nice Cryptanalyses"
authors:
  - "Guilhem Castagnos"
  - "Antoine Joux"
  - "Fabien Laguillaumie"
year: null
venue: null
identifiers:
  eprint: null
  doi: null
  arxiv: null
  url: null
tags: [cryptanalysis, factoring, fhe, lattice, number-theory, protocol, provable-security, rsa, survey]
confidence: reported
citation_verified: read
added: "2026-07-24"
superseded_by: null
---

## Contribution
We present a new algorithm based on binary quadratic forms to factor integers of the form N = pq 2 . Its heuristic running time is exponential in the general case, but becomes polynomial when special (arithmetic) hints are available, which is exactly the case for the so-called NICE family of public-key cryptosystems based on quadratic fields introduced in the late 90s.

## Key claims (as reported)
- Such cryptosystems come in two flavours, depending on whether the quadratic field is imaginary or real.
- Our factoring algorithm yields a general key-recovery polynomial-time attack on NICE, which works for both versions: Castagnos and Laguillaumie recently obtained a total break of imaginary-NICE, but their attack could not apply to real-NICE.
- Our algorithm is rather different from classical factoring algorithms: it combines Lagrange’s reduction of quadratic forms with a provable variant of Coppersmith’s lattice-based root finding algorithm for homogeneous polynomials.
- It is very efficient given either of the following arithmetic hints: the public key of imaginary-NICE, which provides an alternative to the CL attack; or the knowledge that the regulator of the √ quadratic field Q( p) is unusually small, just like in real-NICE.

## Relevance to this program
Recorded for completeness of the local cryptography library. Peripheral to the ECDLP index-calculus program; cite in novelty checks for the tagged areas only.

## Not verified here
Entry generated during the 2026-07-24 bulk seeding pass from the local PDF's first two pages. Title/authors/year/venue were parsed heuristically and may be incomplete or mis-segmented; claims are relayed from the paper's abstract without independent verification. Upgrade to a fully verified entry after a careful read.

## Local copies
- `downloads/59120468 (1).pdf`
- `downloads/59120468 (2).pdf`
- `downloads/59120468 (3).pdf`
- `downloads/59120468.pdf`

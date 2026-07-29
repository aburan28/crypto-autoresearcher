---
id: KN-LIT-990
type: literature
title: "Horizontal racewalking using radical isogenies"
authors:
  - "Wouter Castryck"
  - "Thomas Decru"
  - "Marc Houben"
year: 2022
venue: "IACR Cryptology ePrint Archive"
identifiers:
  eprint: "iacr:2022/1259"
  doi: null
  arxiv: null
  url: "https://eprint.iacr.org/2022/1259"
tags: [curve-arithmetic, elliptic-curve, endomorphism, finite-field, isogeny, mpc, pairing, pqc, prime-field, protocol, sidh-csidh, signature, supersingular]
confidence: reported
citation_verified: read
added: "2026-07-24"
superseded_by: null
---

## Contribution
We address three main open problems concerning the use of radical isogenies, as presented by Castryck, Decru and Vercauteren at Asiacrypt 2020, in the computation of long chains of isogenies of fixed, small degree between elliptic curves over finite fields. Firstly, we present an interpolation method for finding radical isogeny formulae in a given degree N , which by-passes the need for factoring division polynomials over large function fields.

## Key claims (as reported)
- Using this method, we are able to push the range for which we have formulae at our disposal from N ≤ 13 to N ≤ 37 (where in the range 18 ≤ N ≤ 37 we have restricted our attention to prime powers).
- Secondly, using a combination of known techniques and ad-hoc manipulations, we derive optimized versions of these formulae for N ≤ 19, with some instances performing more than twice as fast as their counterparts from 2020.
- Thirdly, we solve the problem of understanding the correct choice of radical when walking along the surface between supersingular elliptic curves over Fp with p ≡ 7 mod 8; this is non-trivial for even N and was settled for N = 2 and N = 4 only, in the latter case by Onuki and Moriya at PKC 2022.
- We give a conjectural statement for all even N and prove it for N ≤ 14.

## Relevance to this program
Relevant to the isogeny cluster: bears on supersingular/isogeny-based constructions and the isogeny-path problems that compete with and inform ECDLP work. Relevant to pairing-based reductions and endomorphism speedups (MOV/Frey-Rück special cases, GLV/GLS) that bound which curve classes are safe baselines.

## Not verified here
Entry generated during the 2026-07-24 bulk seeding pass from the local PDF's first two pages. Title/authors/year/venue were parsed heuristically and may be incomplete or mis-segmented; claims are relayed from the paper's abstract without independent verification. Upgrade to a fully verified entry after a careful read.

## Local copies
- `downloads/137910358 (1).pdf`
- `downloads/137910358.pdf`
- `downloads/2022-1259.pdf`

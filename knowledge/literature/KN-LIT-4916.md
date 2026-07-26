---
id: KN-LIT-4916
type: literature
title: "Middle-Product Learning With Errors"
authors:
  - "Miruna Roşca"
  - "Amin Sakzad"
  - "Damien Stehlé"
  - "Ron Steinfeld"
year: null
venue: null
identifiers:
  eprint: null
  doi: null
  arxiv: null
  url: null
tags: [lattice, number-theory, provable-security, quantum]
confidence: reported
citation_verified: read
added: "2026-07-24"
superseded_by: null
---

## Contribution
We introduce a new variant MP-LWE of the Learning With Errors problem (LWE) making use of the Middle Product between polynomials modulo an integer q. We exhibit a reduction from the PolynomialLWE problem (PLWE) parametrized by a polynomial f , to MP-LWE which is defined independently of any such f .

## Key claims (as reported)
- The reduction only requires f to be monic with constant coefficient coprime with q.
- It incurs a noise growth proportional to the so-called expansion factor of f .
- We also describe a public-key encryption scheme with quasi-optimal asymptotic efficiency (the bit-sizes of the keys and the run-times of all involved algorithms are quasi-linear in the security parameter), which is secure against chosen plaintext attacks under the MP-LWE hardness assumption.
- The scheme is hence secure under the assumption that PLWE is hard for at least one polynomial f of degree n among a family of f ’s which is exponential in n.

## Relevance to this program
Recorded for completeness of the local cryptography library. Peripheral to the ECDLP index-calculus program; cite in novelty checks for the tagged areas only.

## Not verified here
Entry generated during the 2026-07-24 bulk seeding pass from the local PDF's first two pages. Title/authors/year/venue were parsed heuristically and may be incomplete or mis-segmented; claims are relayed from the paper's abstract without independent verification. Upgrade to a fully verified entry after a careful read.

## Local copies
- `downloads/10401269 (1).pdf`
- `downloads/10401269.pdf`

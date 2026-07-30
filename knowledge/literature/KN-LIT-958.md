---
id: KN-LIT-958
type: literature
title: "Breaking a fully Balanced ASIC Coprocessor Implementing Complete Addition Formulas on Weierstrass Elliptic Curves"
authors:
  - "Ievgen Kabin"
  - "Zoya Dyka"
  - "Dan Klann"
  - "Nele Mentens"
  - "Lejla Batina"
  - "Peter Langendoerfer"
year: 2022
venue: "arXiv preprint"
identifiers:
  eprint: null
  doi: null
  arxiv: "2201.01158"
  url: "https://arxiv.org/abs/2201.01158"
tags: [binary-field, curve-arithmetic, ecdsa, elliptic-curve, finite-field, prime-field, provable-security, quantum, rsa, side-channel, signature]
confidence: reported
citation_verified: read
added: "2026-07-24"
superseded_by: null
---

## Contribution
In this paper we report on the results of selected horizontal SCA attacks against two open-source designs that implement hardware accelerators for elliptic curve cryptography. Both designs use the complete addition formula to make the point addition and point doubling operations indistinguishable.

## Key claims (as reported)
- One of the designs uses in addition means to randomize the operation sequence as a countermeasure.
- We used the comparison to the mean and an automated SPA to attack both designs.
- Despite all these countermeasures, we were able to extract the keys processed with a correctness of 100%.

## Relevance to this program
Elliptic-curve/abelian-variety mathematics background for the program; relevant to curve arithmetic, point counting, and structural results underlying ECDLP instances.

## Not verified here
Entry generated during the 2026-07-24 bulk seeding pass from the local PDF's first two pages. Title/authors/year/venue were parsed heuristically and may be incomplete or mis-segmented; claims are relayed from the paper's abstract without independent verification. Upgrade to a fully verified entry after a careful read.

## Local copies
- `downloads/2201.01158v1.pdf`

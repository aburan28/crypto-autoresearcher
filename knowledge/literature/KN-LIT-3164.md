---
id: KN-LIT-3164
type: literature
title: "Converting Pairing-Based Cryptosystems from Composite-Order Groups to Prime-Order Groups"
authors:
  - "David Mandell Freeman"
year: null
venue: null
identifiers:
  eprint: null
  doi: null
  arxiv: null
  url: null
tags: [abelian-variety, dlp, elliptic-curve, finite-field, pairing, quantum, zk-proof]
confidence: reported
citation_verified: read
added: "2026-07-24"
superseded_by: null
---

## Contribution
We develop an abstract framework that encompasses the key properties of bilinear groups of composite order that are required to construct secure pairing-based cryptosystems, and we show how to use prime-order elliptic curve groups to construct bilinear groups with the same properties. In particular, we define a generalized version of the subgroup decision problem and give explicit constructions of bilinear groups in which the generalized subgroup decision assumption follows from the decision Diffie-Hellman assumption, the decision linear assumption, and/or related assumptions in prime-order groups.

## Key claims (as reported)
- We apply our framework and our prime-order group constructions to create more efficient versions of cryptosystems that originally required composite-order groups.
- Specifically, we consider the Boneh-Goh-Nissim encryption scheme, the Boneh-Sahai-Waters traitor tracing system, and the Katz-Sahai-Waters attribute-based encryption scheme.
- We give a security theorem for the prime-order group instantiation of each system, using assumptions of comparable complexity to those used in the composite-order setting.
- Our conversion of the last two systems to primeorder groups answers a problem posed by Groth and Sahai.

## Relevance to this program
Relevant to pairing-based reductions and endomorphism speedups (MOV/Frey-Rück special cases, GLV/GLS) that bound which curve classes are safe baselines.

## Not verified here
Entry generated during the 2026-07-24 bulk seeding pass from the local PDF's first two pages. Title/authors/year/venue were parsed heuristically and may be incomplete or mis-segmented; claims are relayed from the paper's abstract without independent verification. Upgrade to a fully verified entry after a careful read.

## Local copies
- `downloads/66320233 (1).pdf`
- `downloads/66320233 (2).pdf`
- `downloads/66320233 (3).pdf`
- `downloads/66320233.pdf`

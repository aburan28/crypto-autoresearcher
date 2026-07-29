---
id: KN-LIT-3868
type: literature
title: "FHE Circuit Privacy Almost For Free"
authors:
  - "Florian Bourse ∗"
  - "Rafaël Del Pino"
  - "Michele Minelli"
  - "Hoeteck Wee"
year: null
venue: null
identifiers:
  eprint: null
  doi: null
  arxiv: null
  url: null
tags: [fhe, lattice, mpc, pairing]
confidence: reported
citation_verified: read
added: "2026-07-24"
superseded_by: null
---

## Contribution
Circuit privacy is an important property for many applications of fully homomorphic encryption. Prior approaches for achieving circuit privacy rely on superpolynomial noise flooding or on bootstrapping.

## Key claims (as reported)
- In this work, we present a conceptually different approach to circuit privacy based on a novel characterization of the noise growth amidst homomorphic evaluation.
- In particular, we show that a variant of the GSW FHE for branching programs already achieves circuit privacy; this immediately yields a circuit-private FHE for NC1 circuits under the standard LWE assumption with polynomial modulus-to-noise ratio.
- Our analysis relies on a variant of the discrete Gaussian leftover hash lemma which states that e| G−1 (v) + small noise does not depend on v.
- We believe that this result is of independent interest.

## Relevance to this program
Relevant to pairing-based reductions and endomorphism speedups (MOV/Frey-Rück special cases, GLV/GLS) that bound which curve classes are safe baselines.

## Not verified here
Entry generated during the 2026-07-24 bulk seeding pass from the local PDF's first two pages. Title/authors/year/venue were parsed heuristically and may be incomplete or mis-segmented; claims are relayed from the paper's abstract without independent verification. Upgrade to a fully verified entry after a careful read.

## Local copies
- `downloads/98150061 (1).pdf`
- `downloads/98150061.pdf`

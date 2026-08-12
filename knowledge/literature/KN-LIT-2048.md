---
id: KN-LIT-2048
type: literature
title: "A formula for disaster: a unified approach to elliptic curve special-point-based attacks"
authors:
  - "Vladimir Sedlacek"
year: null
venue: null
identifiers:
  eprint: null
  doi: null
  arxiv: null
  url: null
tags: [cryptanalysis, curve-arithmetic, ecdsa, elliptic-curve, extension-field, finite-field, implementation, pairing, quantum, side-channel, signature]
confidence: reported
citation_verified: read
added: "2026-07-24"
superseded_by: null
---

## Contribution
The Refined Power Analysis, Zero-Value Point, and Exceptional Procedure attacks introduced side-channel techniques against specific cases of elliptic curve cryptography. The three attacks recover bits of a static ECDH key adaptively, collecting information on whether a certain multiple of the input point was computed.

## Key claims (as reported)
- We unify and generalize these attacks in a common framework, and solve the corresponding problem for a broader class of inputs.
- We also introduce a version of the attack against windowed scalar multiplication methods, recovering the full scalar instead of just a part of it.
- Finally, we systematically analyze elliptic curve point addition formulas from the Explicit-Formulas Database, classify all non-trivial exceptional points, and find them in new formulas.
- These results indicate the usefulness of our tooling, which we released publicly, for unrolling formulas and finding special points, and potentially for independent future work.

## Relevance to this program
Relevant to pairing-based reductions and endomorphism speedups (MOV/Frey-Rück special cases, GLV/GLS) that bound which curve classes are safe baselines.

## Not verified here
Entry generated during the 2026-07-24 bulk seeding pass from the local PDF's first two pages. Title/authors/year/venue were parsed heuristically and may be incomplete or mis-segmented; claims are relayed from the paper's abstract without independent verification. Upgrade to a fully verified entry after a careful read.

## Local copies
- `downloads/130900095 (1).pdf`
- `downloads/130900095.pdf`

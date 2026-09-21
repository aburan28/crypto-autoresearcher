---
id: KN-LIT-5962
type: literature
title: "Protostar: Generic Efficient Accumulation/Folding for Special-sound Protocols"
authors:
  - "Benedikt Bünz"
year: null
venue: null
identifiers:
  eprint: null
  doi: null
  arxiv: null
  url: null
tags: [curve-arithmetic, dlp, elliptic-curve, mov-fr, pairing, provable-security, zk-proof]
confidence: reported
citation_verified: read
added: "2026-07-24"
superseded_by: null
---

## Contribution
Accumulation is a simple yet powerful primitive that enables incrementally verifiable computation (IVC) without the need for recursive SNARKs. We provide a generic, efficient accumulation (or folding) scheme for any (2k − 1)-move special-sound protocol with a verifier that checks l degree-d equations.

## Key claims (as reported)
- The accumulation verifier only performs k+2 elliptic curve multiplications and k+d+O(1) field/hash operations.
- Using the compiler from BCLMS21 (Crypto 21), this enables building efficient IVC schemes where the recursive circuit only depends on the number of rounds and the verifier degree of the underlying special-sound protocol but not the proof size or the verifier time.
- We use our generic accumulation compiler to build Protostar.
- Protostar is a non-uniform IVC scheme for Plonk that supports high-degree gates and (vector) lookups.

## Relevance to this program
Relevant to pairing-based reductions and endomorphism speedups (MOV/Frey-Rück special cases, GLV/GLS) that bound which curve classes are safe baselines.

## Not verified here
Entry generated during the 2026-07-24 bulk seeding pass from the local PDF's first two pages. Title/authors/year/venue were parsed heuristically and may be incomplete or mis-segmented; claims are relayed from the paper's abstract without independent verification. Upgrade to a fully verified entry after a careful read.

## Local copies
- `downloads/14438084 (1).pdf`
- `downloads/14438084.pdf`

---
id: KN-LIT-3141
type: literature
title: "Constructing Verifiable Random Functions with Large Input Spaces"
authors:
  - "Susan Hohenberger"
  - "Brent Waters"
year: null
venue: null
identifiers:
  eprint: null
  doi: null
  arxiv: null
  url: null
tags: [hash, mov-fr, provable-security, zk-proof]
confidence: reported
citation_verified: read
added: "2026-07-24"
superseded_by: null
---

## Contribution
We present a family of verifiable random functions which are provably secure for exponentially-large input spaces under a noninteractive complexity assumption. Prior constructions required either an interactive complexity assumption or one that could tolerate a factor 2n security loss for n-bit inputs.

## Key claims (as reported)
- Our construction is practical and inspired by the pseudorandom functions of Naor and Reingold and the verifiable random functions of Lysyanskaya.
- Set in a bilinear group, where the Decisional Diffie-Hellman problem is easy to solve, we require the `Decisional Diffie-Hellman Exponent assumption in the standard model, without a common reference string.
- Our core idea is to apply a simulation technique where the large space of VRF inputs is collapsed into a small (polynomial-size) input in the view of the reduction algorithm.
- This view, however, is information-theoretically hidden from the attacker.

## Relevance to this program
Relevant to pairing-based reductions and endomorphism speedups (MOV/Frey-Rück special cases, GLV/GLS) that bound which curve classes are safe baselines.

## Not verified here
Entry generated during the 2026-07-24 bulk seeding pass from the local PDF's first two pages. Title/authors/year/venue were parsed heuristically and may be incomplete or mis-segmented; claims are relayed from the paper's abstract without independent verification. Upgrade to a fully verified entry after a careful read.

## Local copies
- `downloads/66320201 (1).pdf`
- `downloads/66320201 (2).pdf`
- `downloads/66320201 (3).pdf`
- `downloads/66320201.pdf`

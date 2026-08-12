---
id: KN-LIT-316
type: literature
title: "IDENTIFYING SUPERSINGULAR ELLIPTIC CURVES"
authors:
  - "ANDREW V. SUTHERLAND"
year: 2011
venue: "arXiv preprint"
identifiers:
  eprint: null
  doi: null
  arxiv: "1107.1140"
  url: "https://arxiv.org/abs/1107.1140"
tags: [curve-arithmetic, dlp, elliptic-curve, endomorphism, finite-field, isogeny, pairing, supersingular]
confidence: reported
citation_verified: read
added: "2026-07-24"
superseded_by: null
---

## Contribution
Given an elliptic curve E over a field of positive characteristic p, we consider how to efficiently determine whether E is ordinary or supersingular. We analyze the complexity of several existing algorithms and then present a new approach that exploits structural differences between ordinary and supersingular isogeny graphs.

## Key claims (as reported)
- This yields a simple algorithm that, given E and a suitable non-residue in Fp2 , determines the supersingularity of E in O(n3 log2n) time and O(n) space, where n = O(log p).
- Both these complexity bounds are significant improvements over existing methods, as we demonstrate with some practical computations.

## Relevance to this program
Relevant to the isogeny cluster: bears on supersingular/isogeny-based constructions and the isogeny-path problems that compete with and inform ECDLP work. Relevant to pairing-based reductions and endomorphism speedups (MOV/Frey-Rück special cases, GLV/GLS) that bound which curve classes are safe baselines.

## Not verified here
Entry generated during the 2026-07-24 bulk seeding pass from the local PDF's first two pages. Title/authors/year/venue were parsed heuristically and may be incomplete or mis-segmented; claims are relayed from the paper's abstract without independent verification. Upgrade to a fully verified entry after a careful read.

## Local copies
- `downloads/1107.1140v4.pdf`
- `downloads/AMS2012.pdf`

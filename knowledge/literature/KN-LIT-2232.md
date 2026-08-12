---
id: KN-LIT-2232
type: literature
title: "A Simple Obfuscation Scheme for Pattern-Matching with Wildcards"
authors:
  - "Allison Bishop"
  - "Lucas Kowalczyk"
  - "Tal Malkin"
  - "Valerio Pastro"
year: null
venue: null
identifiers:
  eprint: null
  doi: null
  arxiv: null
  url: null
tags: [complexity-theory, lattice, pairing, provable-security, side-channel]
confidence: reported
citation_verified: read
added: "2026-07-24"
superseded_by: null
---

## Contribution
We give a simple and efficient method for obfuscating pattern matching with wildcards. In other words, we construct a way to check an input against a secret pattern, which is described in terms of prescribed values interspersed with unconstrained “wildcard” slots.

## Key claims (as reported)
- As long as the support of the pattern is sufficiently sparse and the pattern itself is chosen from an appropriate distribution, we prove that a polynomialtime adversary cannot find a matching input, except with negligible probability.
- We rely upon the generic group heuristic (in a regular group, with no multilinearity).
- Previous work [9, 10, 32] provided less efficient constructions based on multilinear maps or LWE.

## Relevance to this program
Relevant to pairing-based reductions and endomorphism speedups (MOV/Frey-Rück special cases, GLV/GLS) that bound which curve classes are safe baselines.

## Not verified here
Entry generated during the 2026-07-24 bulk seeding pass from the local PDF's first two pages. Title/authors/year/venue were parsed heuristically and may be incomplete or mis-segmented; claims are relayed from the paper's abstract without independent verification. Upgrade to a fully verified entry after a careful read.

## Local copies
- `downloads/10993373 (1).pdf`
- `downloads/10993373.pdf`

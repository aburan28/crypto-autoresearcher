---
id: KN-LIT-1869
type: literature
title: "Semantics-Based Verification of an Implemented Shor Oracle for ECDLP in Qrisp"
authors:
  - "Lei Zhang"
year: 2026
venue: "arXiv preprint"
identifiers:
  eprint: null
  doi: null
  arxiv: "2605.01008"
  url: "https://arxiv.org/abs/2605.01008"
tags: [curve-arithmetic, dlp, ecdlp, elliptic-curve, factoring, pairing, quantum, rsa]
confidence: reported
citation_verified: read
added: "2026-07-24"
superseded_by: null
---

## Contribution
Shor-style quantum algorithms for the elliptic-curve discrete logarithm problem (ECDLP) are highly sensitive to the exact semantics of their group-operation oracles. Consequently, minor implementation choices can invalidate the intended mathematical model and lead to misleading conclusions.

## Key claims (as reported)
- This paper introduces a semantics-first verification perspective for an end-to-end, compilable ECDLP implementation built on Qrisp.
- We specify the implemented oracle at the level of program semantics, derive refinement-style verification obligations for its key components, and provide a high-level complexity argument for the resulting oracle family.
- A small case study highlights that (i) the core point-update primitive agrees with a classical reference on well-formed inputs, yet (ii) controlled execution may violate the expected control law under the evaluated toolchain, despite a passing trivial control sanity check.
- These results position semantic auditing as a practical prerequisite for trustworthy ECDLP-oriented quantum software.

## Relevance to this program
Directly relevant to the ECDLP algebraic-attack line (index calculus / summation polynomials / Gröbner methods). Novelty checks for decomposition-based proposals must cite this before claiming new mechanisms. Relevant to pairing-based reductions and endomorphism speedups (MOV/Frey-Rück special cases, GLV/GLS) that bound which curve classes are safe baselines.

## Not verified here
Entry generated during the 2026-07-24 bulk seeding pass from the local PDF's first two pages. Title/authors/year/venue were parsed heuristically and may be incomplete or mis-segmented; claims are relayed from the paper's abstract without independent verification. Upgrade to a fully verified entry after a careful read.

## Local copies
- `downloads/2605.01008v1.pdf`

---
id: KN-LIT-6276
type: literature
title: "Rewriting Variables: the Complexity of Fast Algebraic Attacks on Stream Ciphers"
authors:
  - "Philip Hawkes"
  - "Gregory G. Rose"
year: null
venue: null
identifiers:
  eprint: null
  doi: null
  arxiv: null
  url: null
tags: [cryptanalysis, factoring, pairing, symmetric]
confidence: reported
citation_verified: read
added: "2026-07-24"
superseded_by: null
---

## Contribution
Recently proposed algebraic attacks [2, 6] and fast algebraic attacks [1, 5] have provided the best analyses against some deployed LFSR-based ciphers. The process complexity is exponential in the degree of the equations.

## Key claims (as reported)
- Fast algebraic attacks were introduced [5] as a way of reducing run-time complexity by reducing the degree of the system of equations.
- Previous reports on fast algebraic attacks [1, 5] have underestimated the complexity of substituting the keystream into the system of equations, which in some cases dominates the attack.
- We also show how the Fast Fourier Transform (FFT) [4] can be applied to decrease the complexity of the substitution step.
- Finally, it is shown that all functions of degree d satisfy a common, function-independent linear combination that may be used in the pre-computation step of the fast algebraic attack.

## Relevance to this program
Relevant to pairing-based reductions and endomorphism speedups (MOV/Frey-Rück special cases, GLV/GLS) that bound which curve classes are safe baselines.

## Not verified here
Entry generated during the 2026-07-24 bulk seeding pass from the local PDF's first two pages. Title/authors/year/venue were parsed heuristically and may be incomplete or mis-segmented; claims are relayed from the paper's abstract without independent verification. Upgrade to a fully verified entry after a careful read.

## Local copies
- `downloads/Hawkes_Rose_FINAL_VERSION (1).pdf`
- `downloads/Hawkes_Rose_FINAL_VERSION (2).pdf`
- `downloads/Hawkes_Rose_FINAL_VERSION.pdf`
